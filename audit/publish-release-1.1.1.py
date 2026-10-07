"""Publish approved, hash-verified release assets using the Git credential helper."""
import hashlib
import http.client
import json
import os
import subprocess
from pathlib import Path
from urllib.parse import urlsplit, quote

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'audit/release-1.1.1-ready.json'
report = json.loads(REPORT.read_text(encoding='utf-8'))
assert report['uploadApproved'] and report['version'] == '1.1.1'
assert subprocess.check_output(['git', 'config', '--get', 'remote.origin.url'], text=True).strip() == 'https://github.com/MrMints/shinydex.git'
commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
credential = subprocess.run(['git', 'credential', 'fill'], input='protocol=https\nhost=github.com\n\n', text=True, capture_output=True, check=True)
fields = dict(line.split('=', 1) for line in credential.stdout.splitlines() if '=' in line)
token = fields['password']
headers = {'Authorization': 'Bearer ' + token, 'Accept': 'application/vnd.github+json', 'User-Agent': 'ShinyDex-approved-release', 'X-GitHub-Api-Version': '2022-11-28'}

def request(method, route, value=None):
    connection = http.client.HTTPSConnection('api.github.com', timeout=60)
    payload = json.dumps(value).encode() if value is not None else None
    connection.request(method, route, payload, {**headers, 'Content-Type': 'application/json'})
    response = connection.getresponse()
    data = response.read()
    connection.close()
    if response.status == 404:
        return None
    if not 200 <= response.status < 300:
        raise RuntimeError(f'GitHub returned {response.status}: {data.decode()[:300]}')
    return json.loads(data) if data else None

repo = '/repos/MrMints/shinydex'
existing = request('GET', repo + '/releases/tags/v1.1.1')
assert existing is None, 'Release already exists; never replace existing assets'
for asset in report['package']['assets']:
    payload = (ROOT / 'dist/desktop' / asset['name']).read_bytes()
    assert hashlib.sha256(payload).hexdigest() == asset['sha256'], 'Candidate asset changed'
notes = (ROOT / 'audit/RELEASE-1.1.1-NOTES.md').read_text(encoding='utf-8')
body = notes.split('## Release description\n', 1)[1].split('\n## Upload contents', 1)[0].strip()
release = request('POST', repo + '/releases', {'tag_name': 'v1.1.1', 'target_commitish': commit, 'name': 'ShinyDex 1.1.1', 'body': body, 'draft': True, 'prerelease': False})
print('Created draft release ' + str(release['id']), flush=True)
uploaded = []
for asset in report['package']['assets']:
    file = ROOT / 'dist/desktop' / asset['name']
    target = urlsplit(release['upload_url'].split('{', 1)[0] + '?name=' + quote(asset['name']))
    assert target.hostname == 'uploads.github.com'
    connection = http.client.HTTPSConnection(target.hostname, timeout=240)
    connection.putrequest('POST', target.path + '?' + target.query)
    for key, value in {**headers, 'Content-Type': 'application/octet-stream', 'Content-Length': str(file.stat().st_size)}.items():
        connection.putheader(key, value)
    connection.endheaders()
    with file.open('rb') as stream:
        while block := stream.read(1024 * 1024):
            connection.send(block)
    response = connection.getresponse()
    data = response.read()
    connection.close()
    if response.status != 201:
        raise RuntimeError(f'Asset upload failed: HTTP {response.status}')
    saved = json.loads(data)
    assert saved['name'] == asset['name'] and saved['size'] == asset['bytes']
    assert saved['digest'] == 'sha256:' + asset['sha256'], 'GitHub asset digest mismatch'
    uploaded.append({'name': saved['name'], 'sha256': asset['sha256'], 'url': saved['browser_download_url']})
    print('Uploaded and verified ' + asset['name'], flush=True)
published = request('PATCH', repo + '/releases/' + str(release['id']), {'draft': False, 'make_latest': 'true'})
confirmed = request('GET', repo + '/releases/tags/v1.1.1')
assert confirmed and not confirmed['draft'] and len(confirmed['assets']) == 4
for asset in confirmed['assets']:
    expected = next(a for a in report['package']['assets'] if a['name'] == asset['name'])
    assert asset['digest'] == 'sha256:' + expected['sha256']
published_assets = [{'name': asset['name'], 'sha256': asset['digest'].split(':', 1)[1],
                     'url': asset['browser_download_url']} for asset in confirmed['assets']]
report.update(published=True, releaseUrl=confirmed['html_url'], sourceCommit=commit, publishedAt=confirmed['published_at'], publishedAssets=published_assets)
REPORT.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print('Published and verified ' + confirmed['html_url'], flush=True)
