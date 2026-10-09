"""Optional: after creating your account, run `py claim_legacy.py your_username`."""
import sys
from database import connect, init_db

if len(sys.argv) != 2:
    sys.exit('사용법: py claim_legacy.py 내아이디')
init_db()
with connect() as conn:
    username = sys.argv[1]
    user = conn.execute('SELECT id FROM users WHERE username=?', (username,)).fetchone()
    if not user:
        sys.exit('먼저 웹사이트에서 해당 아이디로 회원가입해 주세요.')
    legacy = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='legacy_subjects'").fetchone()
    if not legacy:
        sys.exit('옮길 기존 공용 데이터가 없습니다.')
    if conn.execute("SELECT value FROM metadata WHERE key='legacy_claimed_by'").fetchone():
        sys.exit('기존 데이터가 이미 이전되었습니다. 중복 이전하지 않습니다.')
    old_count = conn.execute('SELECT COUNT(*) AS c FROM legacy_wrong_notes').fetchone()['c']
    print(f'기존 공용 오답 {old_count}개를 {username} 계정으로 복사합니다.')
    if input('본인 데이터가 맞습니까? YES 입력: ').strip() != 'YES':
        sys.exit('취소되었습니다.')
    old_subjects = conn.execute('SELECT id,name FROM legacy_subjects ORDER BY id').fetchall()
    for s in old_subjects:
        conn.execute('INSERT OR IGNORE INTO subjects(user_id,name) VALUES (?,?)', (user['id'],s['name']))
        sid = conn.execute('SELECT id FROM subjects WHERE user_id=? AND name=?', (user['id'],s['name'])).fetchone()['id']
        for n in conn.execute('SELECT question,answer FROM legacy_wrong_notes WHERE subject_id=? ORDER BY id', (s['id'],)).fetchall():
            conn.execute('INSERT INTO wrong_notes(subject_id,question,answer) VALUES (?,?,?)', (sid,n['question'],n['answer']))
    conn.execute("INSERT INTO metadata(key,value) VALUES ('legacy_claimed_by',?)", (username,))
print('기존 데이터 이전 완료. legacy_* 원본 테이블은 보존됩니다.')
