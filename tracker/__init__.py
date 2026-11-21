"""Study tracker: a local Flask application with server-enforced ownership."""
from datetime import date
from pathlib import Path
import os
import secrets
import sqlite3

from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
from flask_login import LoginManager, UserMixin, current_user, login_required, login_user, logout_user
from flask_wtf.csrf import CSRFError, CSRFProtect
from werkzeug.security import check_password_hash, generate_password_hash

from .storage import StudyRepository, get_db, initialize
from .rules import validate_study


class User(UserMixin):
    def __init__(self, row):
        self.id = row['id']
        self.display_name = row['display_name']


def create_app(config=None):
    app = Flask(__name__, instance_relative_config=True)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    key = os.environ.get('TRACKER_SECRET_KEY')
    if not key:
        # Exclusive creation avoids two processes choosing different persistent keys.
        key_file = Path(app.instance_path) / 'secret.key'
        try:
            with key_file.open('x') as file:
                os.chmod(key_file, 0o600)
                file.write(secrets.token_hex(32))
        except FileExistsError:
            pass
        key = key_file.read_text().strip()
    app.config.update(
        SECRET_KEY=key, DATABASE=str(Path(app.instance_path) / 'tracker.sqlite3'),
        SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax',
        MAX_CONTENT_LENGTH=16 * 1024,
    )
    if config:
        app.config.update(config)
    from .storage import close_db
    app.teardown_appcontext(close_db)
    CSRFProtect(app)
    manager = LoginManager(app)
    manager.login_view = 'login'

    @manager.user_loader
    def load_user(user_id):
        row = get_db().execute('SELECT id, display_name FROM users WHERE id = ?', (user_id,)).fetchone()
        return User(row) if row else None

    @app.after_request
    def response_headers(response):
        response.headers['Cache-Control'] = 'no-store'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Content-Security-Policy'] = "default-src 'self'; style-src 'self'; form-action 'self'; frame-ancestors 'none'; base-uri 'self'"
        return response

    @app.errorhandler(CSRFError)
    def csrf_error(error):
        return render_template('error.html', title='Form expired', message='Your form could not be verified. Reload the page and try again.'), 400

    @app.errorhandler(404)
    def missing(error):
        return render_template('error.html', title='Not found', message='That record is not available.'), 404

    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return render_template('welcome.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        error = None
        if request.method == 'POST':
            username = request.form.get('username', '').strip().lower()
            name = request.form.get('display_name', '').strip()
            password = request.form.get('password', '')
            if not (3 <= len(username) <= 40 and username.isascii() and all(c.isalnum() or c == '_' for c in username)):
                error = 'Use 3–40 letters, numbers, or underscores for your username.'
            elif not 1 <= len(name) <= 80:
                error = 'Enter a display name of 1–80 characters.'
            elif not 12 <= len(password) <= 128:
                error = 'Use a password of 12–128 characters.'
            elif password != request.form.get('confirm_password', ''):
                error = 'Passwords do not match.'
            else:
                db = get_db()
                try:
                    db.execute('INSERT INTO users (username, display_name, password_hash) VALUES (?, ?, ?)',
                               (username, name, generate_password_hash(password)))
                    db.commit()
                except sqlite3.IntegrityError:
                    db.rollback()
                    error = 'That username is unavailable. Choose another.'
                if not error:
                    flash('Account created. Sign in to start recording sessions.')
                    return redirect(url_for('login'))
        return render_template('auth.html', mode='register', error=error), 400 if error else 200

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        error = None
        if request.method == 'POST':
            row = get_db().execute('SELECT * FROM users WHERE username = ?',
                                   (request.form.get('username', '').strip().lower(),)).fetchone()
            if row and check_password_hash(row['password_hash'], request.form.get('password', '')):
                session.clear()
                login_user(User(row))
                # Ignore arbitrary next URLs rather than allow an external redirect.
                return redirect(url_for('dashboard'))
            error = 'Username or password is incorrect.'
        return render_template('auth.html', mode='login', error=error), 400 if error else 200

    @app.post('/logout')
    @login_required
    def logout():
        logout_user()
        session.clear()
        return redirect(url_for('index'))

    @app.get('/dashboard')
    @login_required
    def dashboard():
        rows = StudyRepository(get_db()).recent(current_user.id)
        return render_template('dashboard.html', rows=rows, total=sum(r['duration_minutes'] for r in rows))

    @app.route('/sessions/new', methods=['GET', 'POST'])
    @login_required
    def new_study():
        error = None
        if request.method == 'POST':
            try:
                values = validate_study(request.form, today=date.today())
            except ValueError as exc:
                error = str(exc)
            else:
                try:
                    record_id = StudyRepository(get_db()).add(current_user.id, values)
                except sqlite3.Error:
                    get_db().rollback()
                    error = 'The session could not be saved. No success was recorded. Try again.'
                else:
                    flash('Study session saved.')
                    return redirect(url_for('study_detail', record_id=record_id))
        return render_template('new.html', error=error, today=date.today().isoformat()), 400 if error else 200

    @app.get('/sessions/<int:record_id>')
    @login_required
    def study_detail(record_id):
        row = StudyRepository(get_db()).get_owned(record_id, current_user.id)
        if row is None:
            abort(404)
        return render_template('detail.html', row=row)

    with app.app_context():
        initialize()
    return app
