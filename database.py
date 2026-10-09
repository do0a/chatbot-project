import os
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get('STUDY_DB_PATH', str(BASE_DIR / 'study.db')))


def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=20)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    conn.execute('PRAGMA busy_timeout = 20000')
    return conn


def init_db():
    """Keep pre-login data intact in legacy_* tables, never share it automatically."""
    with connect() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE COLLATE NOCASE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )''')
        cols = {row['name'] for row in conn.execute('PRAGMA table_info(subjects)')}
        if cols and 'user_id' not in cols:
            # Existing DB was shared. Archive rather than exposing it to new accounts.
            conn.execute('ALTER TABLE wrong_notes RENAME TO legacy_wrong_notes')
            conn.execute('ALTER TABLE subjects RENAME TO legacy_subjects')
        conn.execute('''CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            UNIQUE(user_id, name),
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )''')
        conn.execute('''CREATE TABLE IF NOT EXISTS wrong_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            FOREIGN KEY(subject_id) REFERENCES subjects(id) ON DELETE CASCADE
        )''')
        conn.execute('''CREATE TABLE IF NOT EXISTS metadata (
            key TEXT PRIMARY KEY, value TEXT NOT NULL
        )''')


def current_user_id():
    from flask import g
    uid = getattr(g, 'user_id', None)
    if uid is None:
        raise PermissionError('로그인이 필요합니다.')
    return uid
