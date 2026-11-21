from datetime import date
import re
import sqlite3

import pytest
from werkzeug.security import check_password_hash

from tracker import create_app
from tracker.rules import validate_study
from tracker.storage import StudyRepository, get_db
from pattern_experiment import simple_get_owned

PASSWORD = 'Synthetic-Study-123!'


@pytest.fixture
def app(tmp_path):
    return create_app({'TESTING': True, 'SECRET_KEY': 'test-only-key',
                       'DATABASE': str(tmp_path / 'test.sqlite3')})


def token(client, path):
    response = client.get(path)
    match = re.search(r'name="csrf_token" value="([^"]+)"', response.text)
    assert match, (path, response.status_code)
    return match.group(1)


def register(client, username='student_a', **changes):
    data = {'username': username, 'display_name': 'Student', 'password': PASSWORD,
            'confirm_password': PASSWORD}
    data.update(changes)
    return client.post('/register', data={**data, 'csrf_token': token(client, '/register')})


def login(client, username='student_a', password=PASSWORD):
    return client.post('/login', data={'username': username, 'password': password,
                                      'csrf_token': token(client, '/login')})


def logout(client):
    return client.post('/logout', data={'csrf_token': token(client, '/dashboard')})


def save(client, **changes):
    data = {'subject': 'IS218', 'session_date': '2026-01-15',
            'duration_minutes': '45', 'note': 'Reviewed functions'}
    data.update(changes)
    return client.post('/sessions/new', data={**data, 'csrf_token': token(client, '/sessions/new')})


def test_complete_slice_and_reopen_after_restart(app):
    client = app.test_client()
    assert register(client).status_code == 302
    assert login(client).status_code == 302
    saved = save(client)
    location = saved.headers['Location']
    assert saved.status_code == 302
    page = client.get(location)
    assert 'IS218' in page.text and '45 minutes' in page.text
    assert logout(client).status_code == 302
    assert client.get(location).status_code == 302
    restarted = create_app({'TESTING': True, 'SECRET_KEY': 'test-only-key',
                            'DATABASE': app.config['DATABASE']})
    returned = restarted.test_client()
    assert login(returned).status_code == 302
    assert 'Reviewed functions' in returned.get(location).text
    assert '45 minutes across 1 saved session' in returned.get('/dashboard').text


def test_password_is_hashed_and_wrong_login_rejected(app):
    client = app.test_client()
    register(client)
    with app.app_context():
        row = get_db().execute('SELECT password_hash FROM users').fetchone()
        assert row['password_hash'] != PASSWORD
        assert check_password_hash(row['password_hash'], PASSWORD)
    assert login(client, password='wrong').status_code == 400
    assert client.get('/dashboard').status_code == 302


def test_duplicate_username_case_insensitive(app):
    a, b = app.test_client(), app.test_client()
    register(a, 'STUDENT_A')
    response = register(b, 'student_a')
    assert response.status_code == 400
    assert 'unavailable' in response.text
    with app.app_context():
        assert get_db().execute('SELECT COUNT(*) FROM users').fetchone()[0] == 1


@pytest.mark.parametrize('changes', [
    {'username': ''}, {'username': 'ab'}, {'username': 'has space'},
    {'username': 'a' * 41}, {'display_name': ' '}, {'display_name': 'a' * 81},
    {'password': 'short'}, {'password': 'a' * 129}, {'confirm_password': 'mismatch'},
])
def test_invalid_registration_leaves_no_account(app, changes):
    client = app.test_client()
    assert register(client, **changes).status_code == 400
    with app.app_context():
        assert get_db().execute('SELECT COUNT(*) FROM users').fetchone()[0] == 0


def test_another_user_cannot_read_record_or_dashboard(app):
    a, b = app.test_client(), app.test_client()
    register(a)
    login(a)
    url = save(a, subject='PRIVATE-ALGEBRA').headers['Location']
    register(b, 'student_b')
    login(b, 'student_b')
    assert b.get(url).status_code == 404
    assert 'PRIVATE-ALGEBRA' not in b.get('/dashboard').text
    assert 'No sessions yet.' in b.get('/dashboard').text


def test_submitted_owner_is_ignored(app):
    a, b = app.test_client(), app.test_client()
    register(a)
    register(b, 'student_b')
    login(a)
    url = save(a, user_id='2').headers['Location']
    assert a.get(url).status_code == 200
    login(b, 'student_b')
    assert b.get(url).status_code == 404


@pytest.mark.parametrize('path', ['/dashboard', '/sessions/new', '/sessions/1'])
def test_signed_out_private_pages_are_blocked(app, path):
    response = app.test_client().get(path)
    assert response.status_code == 302 and '/login' in response.headers['Location']


def test_csrf_required_even_on_login_and_save(app):
    client = app.test_client()
    assert client.post('/register', data={'username': 'abc'}).status_code == 400
    assert client.post('/login', data={}).status_code == 400
    register(client)
    login(client)
    assert client.post('/sessions/new', data={'subject': 'Test'}).status_code == 400
    assert client.post('/logout').status_code == 400


def test_logout_is_post_only_and_external_next_ignored(app):
    client = app.test_client()
    register(client)
    csrf = token(client, '/login')
    response = client.post('/login?next=https://example.org', data={
        'username': 'student_a', 'password': PASSWORD, 'csrf_token': csrf})
    assert response.headers['Location'] == '/dashboard'
    assert client.get('/logout').status_code == 405


@pytest.mark.parametrize('changes', [
    {'subject': ' '}, {'subject': 'a' * 81}, {'duration_minutes': '0'},
    {'duration_minutes': '-1'}, {'duration_minutes': '1441'},
    {'duration_minutes': '1.5'}, {'duration_minutes': 'abc'},
    {'duration_minutes': '９'}, {'duration_minutes': '9' * 500},
    {'session_date': 'not-a-date'}, {'session_date': '2026-02-30'},
    {'session_date': '2099-01-01'}, {'note': 'a' * 241},
])
def test_invalid_session_creates_no_record(app, changes):
    client = app.test_client()
    register(client)
    login(client)
    assert save(client, **changes).status_code == 400
    with app.app_context():
        assert get_db().execute('SELECT COUNT(*) FROM study_sessions').fetchone()[0] == 0


@pytest.mark.parametrize('minutes', ['1', '1440'])
def test_valid_rules_boundaries(minutes):
    result = validate_study({'subject': 'a' * 80, 'session_date': '2026-01-15',
                             'duration_minutes': minutes, 'note': 'x' * 240}, today=date(2026, 1, 15))
    assert result == ('a' * 80, '2026-01-15', int(minutes), 'x' * 240)


def test_text_is_escaped_and_sql_input_is_data(app):
    client = app.test_client()
    register(client)
    login(client)
    url = save(client, subject='<script>alert(1)</script>', note="x'); DROP TABLE users;--").headers['Location']
    page = client.get(url).text
    assert '&lt;script&gt;' in page and '<script>alert(1)</script>' not in page
    with app.app_context():
        assert get_db().execute('SELECT COUNT(*) FROM users').fetchone()[0] == 1


def test_failed_write_has_no_success_or_partial_record(app, monkeypatch):
    client = app.test_client()
    register(client)
    login(client)
    def fail(self, user_id, values):
        self.db.execute('''INSERT INTO study_sessions
            (user_id, subject, session_date, duration_minutes, note) VALUES (?, ?, ?, ?, ?)''', (user_id, *values))
        raise sqlite3.OperationalError('simulated write failure')
    monkeypatch.setattr(StudyRepository, 'add', fail)
    page = save(client)
    assert page.status_code == 400
    assert 'could not be saved' in page.text
    assert 'Study session saved.' not in page.text
    with app.app_context():
        assert get_db().execute('SELECT COUNT(*) FROM study_sessions').fetchone()[0] == 0


def test_repository_and_simpler_alternative_match_independent_expectations(app):
    client = app.test_client()
    register(client)
    login(client)
    save(client)
    with app.app_context():
        db = get_db()
        repo = StudyRepository(db)
        record_id = repo.recent(1)[0]['id']
        for lookup in [repo.get_owned, lambda rid, uid: simple_get_owned(db, rid, uid)]:
            row = lookup(record_id, 1)
            assert row['subject'] == 'IS218'
            assert row['duration_minutes'] == 45
            assert lookup(record_id, 2) is None
            assert lookup(999999, 1) is None


def test_no_private_page_cache(app):
    client = app.test_client()
    register(client)
    login(client)
    page = client.get('/dashboard')
    assert page.headers['Cache-Control'] == 'no-store'
