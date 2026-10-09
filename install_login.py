"""Run once in your project root: py install_login.py"""
from pathlib import Path
import shutil
import sys

root = Path(__file__).resolve().parent
app_path = root / 'app.py'
if not app_path.exists():
    sys.exit('app.py가 없습니다. install_login.py를 프로젝트 폴더에 넣어주세요.')
code = app_path.read_text(encoding='utf-8')
if 'install_auth(app)' in code:
    print('이미 로그인 기능이 연결되어 있습니다.')
    sys.exit(0)
import re
pattern = r'(?m)^(app\s*=\s*Flask\([^\n]*\)\s*)$'
match = re.search(pattern, code)
if not match:
    sys.exit('Flask 앱 생성 위치를 찾지 못했습니다. app.py를 보내주세요. 원본은 수정하지 않았습니다.')
shutil.copy2(app_path, root / 'app_before_login.py.bak')
code = code[:match.end()] + '\nfrom auth import install_auth\ninstall_auth(app)\n' + code[match.end():]
app_path.write_text(code, encoding='utf-8')
# Add a visible logout button without replacing the existing page designs.
templates = root / 'templates'
for page in templates.glob('*.html'):
    if page.name in ('login.html', 'register.html'):
        continue
    html = page.read_text(encoding='utf-8')
    if "url_for('logout')" in html:
        continue
    logout_form = """<form method="post" action="{{ url_for('logout') }}" style="margin:16px 10px;">
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
<button type="submit" style="width:100%;padding:11px;border:1px solid #e3e5ec;border-radius:9px;background:white;color:#626977;cursor:pointer;">로그아웃</button>
</form>"""
    import re as _re
    if _re.search(r'</nav\s*>', html, _re.I):
        html = _re.sub(r'</nav\s*>', lambda m: logout_form + '\n' + m.group(0), html, count=1, flags=_re.I)
    elif _re.search(r'</aside\s*>', html, _re.I):
        html = _re.sub(r'</aside\s*>', lambda m: logout_form + '\n' + m.group(0), html, count=1, flags=_re.I)
    else:
        continue
    shutil.copy2(page, page.with_suffix('.html.bak'))
    page.write_text(html, encoding='utf-8')
print('app.py 연결 완료. 백업: app_before_login.py.bak')
print('기존 템플릿에 로그아웃 버튼을 추가했습니다. 원본 백업: *.html.bak')
