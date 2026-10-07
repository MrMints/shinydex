from pathlib import Path
import urllib.request,hashlib,json
q=Path('audit/artifacts/release-1.1.1-compatibility');q.mkdir(exist_ok=True)
f=q/'ShinyDex-1.1.0.exe'
if not f.exists():
 urllib.request.urlretrieve('https://github.com/MrMints/shinydex/releases/download/v1.1.0/ShinyDex.exe',f)
r=json.loads(Path('audit/release-1.1.0-ready.json').read_text())
assert hashlib.sha256(f.read_bytes()).hexdigest()==next(a['sha256'] for a in r['package']['assets'] if a['name']=='ShinyDex.exe')
assert hashlib.sha256(Path('audit/artifacts/release-1.1.0/previous-runtime/app.asar').read_bytes()).hexdigest()==r['priorRelease']['sourceAsarSha256']
print('Verified published 1.1.0 installer and retained 1.0.0 runtime hashes.')
