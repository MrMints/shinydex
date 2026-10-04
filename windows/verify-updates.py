"""Verify native update transactions using local releases, including the real v1 EXE.

Run after building: python windows/verify-updates.py --old-exe PATH
The old binary is fetched explicitly for release QA, never automatically by this test.
"""
import argparse
import hashlib
import http.client
import json
import os
import re
from pathlib import Path
import signal
import socket
import subprocess
import tempfile
import time

root = Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser()
parser.add_argument('--old-exe', type=Path, required=True)
args = parser.parse_args()
assert hashlib.sha256(args.old_exe.read_bytes()).hexdigest() == 'fae256498734a21e19d8820e3d7ff2296b32df7e70da0fbc90a25add65e51df0', 'Use the original published v1.0.0 EXE.'
current = root / 'dist' / 'ShinyDex.exe'
compiler = Path(os.environ['WINDIR']) / 'Microsoft.NET/Framework64/v4.0.30319/csc.exe'

with socket.socket() as available:
    available.bind(('127.0.0.1', 0))
    port = available.getsockname()[1]

def request(path, method='GET', body=None, token=None, origin=None):
    connection = http.client.HTTPConnection('127.0.0.1', port, timeout=15)
    headers = {'Host': f'localhost:{port}'}
    if token is not None:
        headers['X-ShinyDex-Token'] = token
    if origin is not None:
        headers['Origin'] = origin
    if body is not None:
        body = json.dumps(body)
        headers['Content-Type'] = 'application/json'
    connection.request(method, path, body, headers)
    response = connection.getresponse()
    result = response.status, response.read()
    connection.close()
    return result

def status():
    code, body = request('/__updates/status')
    assert code == 200
    return json.loads(body)

def wait_for(predicate, timeout=40):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            value = status()
            if predicate(value):
                return value
        except OSError:
            pass
        time.sleep(0.1)
    raise AssertionError('Timed out waiting for update state: ' + str(status()))

with tempfile.TemporaryDirectory(prefix='shinydex-update-qa-') as temporary:
    cache = Path(temporary)
    future = cache / 'future.exe'
    sources = []
    for name in ('Launcher.cs', 'UpdateManager.cs'):
        path = cache / name
        path.write_text((root / 'windows' / name).read_text(encoding='utf-8').replace('1.1.0', '1.2.0'), encoding='utf-8')
        sources.append(str(path))
    subprocess.run([str(compiler), '/nologo', '/target:winexe', '/optimize+', '/platform:anycpu', f'/out:{future}', '/reference:System.Windows.Forms.dll', '/reference:System.Drawing.dll', '/reference:System.IO.Compression.dll', '/reference:System.IO.Compression.FileSystem.dll', '/reference:System.Web.Extensions.dll', f'/resource:{root / "dist/web.zip"},ShinyDex.Web.zip', f'/resource:{root / "updater.js"},ShinyDex.Updater.js', *sources], check=True)
    corrupt = cache / 'corrupt.exe'
    corrupt.write_bytes(b'not an executable' * 200)
    def release(tag, path, digest=None):
        return {'tag_name': tag, 'name': tag, 'draft': False, 'assets': [{'name': 'ShinyDex.exe', 'browser_download_url': path.as_uri(), 'size': path.stat().st_size, 'digest': 'sha256:' + (digest or hashlib.sha256(path.read_bytes()).hexdigest())}]}
    fixture = cache / 'releases.json'
    fixture.write_text(json.dumps({'latestTag': 'v1.2.0-windows-preview', 'releases': [release('v1.2.0-windows-preview', future), release('v1.1.0-windows-preview', current), release('v1.0.0-windows-preview', args.old_exe), release('v1.3.0-bad-checksum', corrupt, '0' * 64), release('v1.4.0-bad-bundle', corrupt), release('../invalid-tag', corrupt)]}))
    environment = dict(os.environ, LOCALAPPDATA=temporary, SHINYDEX_RELEASE_FIXTURE=str(fixture), SHINYDEX_VERIFY_LOG=str(cache / 'launcher.log'))
    process = subprocess.Popen([str(current), '--verify', str(port)], env=environment, stderr=subprocess.PIPE)
    processes = {process.pid}
    collection = json.dumps({'version': 2, 'captured': [1, 10001], 'shinies': [1]})
    def install(tag):
        snapshot = status()
        code, body = request('/__updates/install', 'POST', {'tag': tag, 'collection': collection}, snapshot['token'], f'http://localhost:{port}')
        assert code == 202, (code, body)
        return snapshot
    try:
        snapshot = wait_for(lambda state: state['status'] == 'ready')
        assert snapshot['currentVersion'] == 'v1.1.0-windows-preview'
        assert snapshot['updateAvailable'] and snapshot['latestVersion'] == 'v1.2.0-windows-preview'
        assert len(snapshot['releases']) == 5
        assert request('/__updates/install', 'POST', {'tag': 'v1.0.0-windows-preview'})[0] == 403
        assert request('/__updates/install', 'POST', {'tag': 'v1.0.0-windows-preview'}, snapshot['token'], 'http://attacker.example')[0] == 403
        assert request('/__updates/install', 'POST', {'tag': '../escape'}, snapshot['token'], f'http://localhost:{port}')[0] == 409
        assert request('/__updates/install', 'POST', {'tag': 'v1.0.0-windows-preview', 'collection': '{}'}, snapshot['token'], f'http://localhost:{port}')[0] == 409
        for failed in ('v1.3.0-bad-checksum', 'v1.4.0-bad-bundle'):
            install(failed)
            snapshot = wait_for(lambda state: state['status'] == 'error')
            assert snapshot['currentVersion'] == 'v1.1.0-windows-preview'
            assert request('/index.html')[1] == (root / 'index.html').read_bytes()
            assert not (cache / 'ShinyDex/installed.json').exists()
        install('v1.0.0-windows-preview')
        snapshot = wait_for(lambda state: state['status'] == 'installed')
        assert snapshot['currentVersion'] == 'v1.0.0-windows-preview'
        assert snapshot['launcherVersion'] == 'v1.1.0-windows-preview'
        assert b'src="/updater.js"' in request('/index.html')[1]
        assert request('/updater.js')[1] == (root / 'updater.js').read_bytes()
        backups = list((cache / 'ShinyDex/collections/backups').glob('*.json'))
        assert backups and all(json.loads(path.read_text(encoding='utf-8-sig')) == json.loads(collection) for path in backups)
        # A restart must remember the older selection while retaining the current updater.
        process.terminate(); process.wait(timeout=10)
        process = subprocess.Popen([str(current), '--verify', str(port)], env=environment)
        processes.add(process.pid)
        snapshot = wait_for(lambda state: state['status'] == 'ready')
        assert snapshot['currentVersion'] == 'v1.0.0-windows-preview'
        install('v1.1.0-windows-preview')
        snapshot = wait_for(lambda state: state['status'] == 'installed')
        assert snapshot['currentVersion'] == 'v1.1.0-windows-preview'
        install('v1.2.0-windows-preview')
        snapshot = wait_for(lambda state: state['launcherVersion'] == 'v1.2.0-windows-preview' and state['status'] == 'ready')
        processes.add(snapshot['processId'])
        assert snapshot['currentVersion'] == 'v1.2.0-windows-preview' and not snapshot['updateAvailable']
        process.wait(timeout=10)
        assert process.returncode == 0
        install('v1.0.0-windows-preview')
        snapshot = wait_for(lambda state: state['status'] == 'installed')
        assert snapshot['launcherVersion'] == 'v1.2.0-windows-preview' and snapshot['currentVersion'] == 'v1.0.0-windows-preview'
        # Opening the original EXE must route to the newer managed launcher.
        reopened = subprocess.run([str(current), '--verify', str(port)], env=environment, timeout=10)
        assert reopened.returncode == 0
        assert status()['processId'] == snapshot['processId']
        print('PASS: startup discovery, release filtering, request authorization, failed-download/bundle recovery, real v1 rollback, retained updater UI, collection disk backups, persisted selection, forward update, launcher restart, and old shortcut forwarding.')
    except Exception:
        if (cache / 'launcher.log').exists():
            print((cache / 'launcher.log').read_text())
        raise
    finally:
        if (cache / 'launcher.log').exists():
            processes.update(int(pid) for pid in re.findall(r'Started (?:replacement|redirect) (\d+)', (cache / 'launcher.log').read_text()))
        try:
            processes.add(status()['processId'])
        except OSError:
            pass
        for pid in processes:
            try:
                os.kill(pid, signal.SIGTERM)
            except (OSError, ProcessLookupError):
                pass
        time.sleep(0.5)
