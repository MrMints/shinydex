"""Exercise the built EXE over HTTP with an isolated extraction cache and test port."""
import concurrent.futures
import hashlib
import http.client
import os
from pathlib import Path
import socket
import subprocess
import tempfile
import time
import zipfile

root = Path(__file__).resolve().parent.parent
exe = root / 'dist' / 'ShinyDex.exe'
assert exe.exists(), 'Build windows/build-windows.ps1 first.'
with socket.socket() as available:
    available.bind(('127.0.0.1', 0))
    port = available.getsockname()[1]

def request(path, method='GET', host=None):
    connection = http.client.HTTPConnection('127.0.0.1', port, timeout=15)
    connection.request(method, path, headers={'Host': host or f'localhost:{port}'})
    response = connection.getresponse()
    result = response.status, response.getheader('Content-Type'), response.read()
    connection.close()
    return result

with tempfile.TemporaryDirectory(prefix='shinydex-launcher-') as cache:
    environment = dict(os.environ, LOCALAPPDATA=cache)
    process = subprocess.Popen([str(exe), '--verify', str(port)], env=environment, stderr=subprocess.PIPE)
    try:
        for attempt in range(200):
            if process.poll() is not None:
                raise AssertionError(f'Launcher exited: {process.returncode}; {process.stderr.read().decode(errors="replace")}')
            try:
                if request('/__shinydex_launcher')[0] == 200:
                    break
            except OSError:
                time.sleep(0.1)
        else:
            raise AssertionError('Launcher did not become ready.')
        for name in ('index.html', 'main.js', 'style.css', 'data.json', 'hunts.json'):
            status, mime, body = request('/' + name)
            assert status == 200 and body == (root / name).read_bytes(), name
        assert request('/')[2] == (root / 'index.html').read_bytes()
        assert request('/main.js')[1].startswith('application/javascript')
        assert request('/hunts.json', 'HEAD')[2] == b''
        for path in ('/../README.md', '/%2e%2e/README.md', '/assets/pokemon/../../data.json', '/.git/config', '/server.cjs', '/assets/pokemon/..%5c..%5cREADME.md'):
            assert request(path)[0] == 403, path
        assert request('/%ZZ')[0] == 400
        assert request('/', 'POST')[0] == 405
        assert request('/', host='attacker.example')[0] == 403
        assert request('/assets/pokemon/missing.png')[0] == 404
        duplicate = subprocess.run([str(exe), '--verify', str(port)], env=environment, timeout=10)
        assert duplicate.returncode == 0 and request('/')[0] == 200
        images = sorted((root / 'assets' / 'pokemon').glob('*.png'))
        def check_image(image):
            status, mime, body = request('/' + image.relative_to(root).as_posix())
            assert status == 200 and mime == 'image/png'
            assert hashlib.sha256(body).digest() == hashlib.sha256(image.read_bytes()).digest(), image
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as workers:
            list(workers.map(check_image, images))
        with zipfile.ZipFile(root / 'dist' / 'web.zip') as bundle:
            assert len([name for name in bundle.namelist() if name.endswith('.png')]) == 2166
            assert 'reference/pkhex/LICENSE' in bundle.namelist()
        print(f'PASS: EXE startup, duplicate launch, HTTP methods, host/path boundaries, exact runtime files, {len(images)} served image hashes, bundled notices.')
    finally:
        process.terminate()
        process.wait(timeout=10)
