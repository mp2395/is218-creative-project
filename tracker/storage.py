"""Small repository boundary; all record reads include the authenticated owner."""
import sqlite3
from flask import current_app, g


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
        g.db.execute('PRAGMA foreign_keys = ON')
    return g.db


def close_db(error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def initialize():
    get_db().executescript('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL UNIQUE,
        display_name TEXT NOT NULL,
        password_hash TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS study_sessions (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id),
        subject TEXT NOT NULL,
        session_date TEXT NOT NULL,
        duration_minutes INTEGER NOT NULL CHECK(duration_minutes BETWEEN 1 AND 1440),
        note TEXT NOT NULL DEFAULT '',
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    ''')


class StudyRepository:
    def __init__(self, connection):
        self.db = connection

    def add(self, user_id, values):
        cursor = self.db.execute('''INSERT INTO study_sessions
            (user_id, subject, session_date, duration_minutes, note)
            VALUES (?, ?, ?, ?, ?)''', (user_id, *values))
        self.db.commit()
        return cursor.lastrowid

    def recent(self, user_id):
        return self.db.execute('''SELECT * FROM study_sessions WHERE user_id = ?
            ORDER BY session_date DESC, id DESC''', (user_id,)).fetchall()

    def get_owned(self, record_id, user_id):
        return self.db.execute('SELECT * FROM study_sessions WHERE id = ? AND user_id = ?',
                               (record_id, user_id)).fetchone()
