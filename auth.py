import hmac
import os
import re
import secrets
from functools import wraps
from pathlib import Path
from urllib.parse import urlsplit

from flask import (g, redirect, render_template, request, session, url_for,
                   flash, abort)
from werkzeug.security import generate_password_hash, check_password_hash
from database import connect, init_db


def _secret_key():
    key = os.environ.get('FLASK_SECRET_KEY')
    if key:
        return key
    # Local-only stable secret. For deployment, set FLASK_SECRET_KEY explicitly.
    p = Path(__file__).resolve().parent / '.flask_secret'
    if not p.exists():
        try:
            with p.open('x', encoding='utf-8') as f:
                f.write(secrets.token_hex(32))
        except FileExistsError:
            pass
    return p.read_text(encoding='utf-8').strip()


def _csrf():
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_urlsafe(32)
    return session['csrf_token']


def _verify_csrf():
    expected = session.get('csrf_token', '')
    actual = request.form.get('csrf_token', '')
    if not expected or not hmac.compare_digest(expected, actual):
        abort(400, '잘못된 요청입니다. 페이지를 새로고침해 주세요.')


def _safe_next(target):
    if not target:
        return url_for('index')
    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc or not target.startswith('/') or target.startswith('//'):
        return url_for('index')
    return target


def install_auth(app):
    app.secret_key = _secret_key()
    app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax',
                      SESSION_COOKIE_SECURE=os.environ.get('FLASK_COOKIE_SECURE') == '1')
    init_db()
    app.jinja_env.globals['csrf_token'] = _csrf

    @app.before_request
    def authenticate_request():
        g.user_id = None
        g.username = None
        uid = session.get('user_id')
        if isinstance(uid, int):
            with connect() as conn:
                row = conn.execute('SELECT id,username FROM users WHERE id=?', (uid,)).fetchone()
            if row:
                g.user_id = row['id']
                g.username = row['username']
            else:
                session.clear()
        if request.endpoint in ('login', 'register', 'static'):
            return None
        if g.user_id is None:
            return redirect(url_for('login', next=request.path if request.method == 'GET' else '/'))
        return None

    @app.context_processor
    def inject_auth():
        return {'logged_in_username': g.get('username')}

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if g.user_id is not None:
            return redirect(url_for('index'))
        if request.method == 'POST':
            _verify_csrf()
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            confirm = request.form.get('confirm', '')
            if not re.fullmatch(r'[A-Za-z0-9_]{3,30}', username):
                flash('아이디는 영문, 숫자, 밑줄을 사용해 3~30자로 입력해 주세요.')
            elif len(password) < 10 or len(password) > 128:
                flash('비밀번호는 10~128자로 입력해 주세요.')
            elif password != confirm:
                flash('비밀번호 확인이 일치하지 않습니다.')
            else:
                try:
                    with connect() as conn:
                        cur = conn.execute('INSERT INTO users(username,password_hash) VALUES (?,?)',
                                           (username, generate_password_hash(password)))
                        uid = cur.lastrowid
                    session.clear()
                    session['user_id'] = uid
                    return redirect(url_for('index'))
                except __import__('sqlite3').IntegrityError:
                    flash('이미 사용 중인 아이디입니다.')
        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if g.user_id is not None:
            return redirect(url_for('index'))
        if request.method == 'POST':
            _verify_csrf()
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            with connect() as conn:
                row = conn.execute('SELECT id,password_hash FROM users WHERE username=?',
                                   (username,)).fetchone()
            if row and check_password_hash(row['password_hash'], password):
                session.clear()
                session['user_id'] = row['id']
                return redirect(_safe_next(request.form.get('next')))
            flash('아이디 또는 비밀번호가 올바르지 않습니다.')
        return render_template('login.html', next=_safe_next(request.args.get('next')))

    @app.route('/logout', methods=['POST'])
    def logout():
        _verify_csrf()
        session.clear()
        return redirect(url_for('login'))
