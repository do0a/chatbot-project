from database import connect, init_db, current_user_id


def load_subjects():
    init_db()
    uid = current_user_id()
    with connect() as conn:
        return [row['name'] for row in conn.execute(
            'SELECT name FROM subjects WHERE user_id=? ORDER BY id', (uid,))]


def add_subject(subject):
    init_db()
    uid = current_user_id()
    subject = subject.strip()
    if not subject or len(subject) > 100:
        return False
    with connect() as conn:
        cur = conn.execute('INSERT OR IGNORE INTO subjects(user_id,name) VALUES (?,?)', (uid, subject))
        return cur.rowcount > 0


def delete_subject(subject):
    init_db()
    uid = current_user_id()
    with connect() as conn:
        cur = conn.execute('DELETE FROM subjects WHERE user_id=? AND name=?', (uid, subject))
        return cur.rowcount > 0
