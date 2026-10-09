from database import connect, init_db, current_user_id


def _subject_id(conn, uid, subject):
    row = conn.execute('SELECT id FROM subjects WHERE user_id=? AND name=?', (uid, subject)).fetchone()
    return row['id'] if row else None


def save_note(subject, question, answer):
    init_db()
    uid = current_user_id()
    with connect() as conn:
        sid = _subject_id(conn, uid, subject)
        if sid is None or not question.strip() or not answer.strip():
            return False
        conn.execute('INSERT INTO wrong_notes(subject_id,question,answer) VALUES (?,?,?)',
                     (sid, question.strip(), answer.strip()))
        return True


def load_notes(subject):
    init_db()
    uid = current_user_id()
    with connect() as conn:
        rows = conn.execute('''SELECT n.question, n.answer FROM wrong_notes n
            JOIN subjects s ON s.id=n.subject_id
            WHERE s.user_id=? AND s.name=? ORDER BY n.id''', (uid, subject)).fetchall()
        return [{'question': row['question'], 'answer': row['answer']} for row in rows]


def rewrite_notes(subject, notes):
    init_db()
    uid = current_user_id()
    with connect() as conn:
        sid = _subject_id(conn, uid, subject)
        if sid is None:
            return False
        conn.execute('DELETE FROM wrong_notes WHERE subject_id=?', (sid,))
        for note in notes:
            conn.execute('INSERT INTO wrong_notes(subject_id,question,answer) VALUES (?,?,?)',
                         (sid, note['question'].strip(), note['answer'].strip()))
        return True


def _note_id(conn, uid, subject, index):
    if not isinstance(index, int) or index < 0:
        return None
    rows = conn.execute('''SELECT n.id FROM wrong_notes n JOIN subjects s ON s.id=n.subject_id
        WHERE s.user_id=? AND s.name=? ORDER BY n.id''', (uid, subject)).fetchall()
    return rows[index]['id'] if index < len(rows) else None


def update_note(subject, index, question, answer):
    init_db()
    uid = current_user_id()
    with connect() as conn:
        nid = _note_id(conn, uid, subject, index)
        if nid is None or not question.strip() or not answer.strip():
            return False
        conn.execute('UPDATE wrong_notes SET question=?, answer=? WHERE id=?',
                     (question.strip(), answer.strip(), nid))
        return True


def delete_note(subject, index):
    init_db()
    uid = current_user_id()
    with connect() as conn:
        nid = _note_id(conn, uid, subject, index)
        if nid is None:
            return False
        conn.execute('DELETE FROM wrong_notes WHERE id=?', (nid,))
        return True
