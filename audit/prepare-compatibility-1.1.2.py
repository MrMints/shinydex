from pathlib import Path
import urllib.request,hashlib,json
q=Path('audit/artifacts/release-1.1.2');q.mkdir(exist_ok=True)
p=q/'ShinyDex-1.1.1.exe'
if not p.exists(): urllib.request.urlretrieve('https://github.com/MrMints/shinydex/releases/download/v1.1.1/ShinyDex.exe',p)
r=json.loads(Path('audit/release-1.1.1-ready.json').read_text())
assert hashlib.sha256(p.read_bytes()).hexdigest()==next(a['sha256'] for a in r['package']['assets'] if a['name']=='ShinyDex.exe')
print('Public 1.1.1 installer hash verified')
