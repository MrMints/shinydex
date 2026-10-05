"""Fetch each catalog artwork independently and compare it with the local PNG.

This is an explicit network audit, separate from offline regression checks.
Checkpoints preserve successful evidence; --fresh discards previous results.
No local artwork is overwritten, including when upstream content has changed.
"""

# Audit tools resolve shared inputs from the repository, regardless of launch directory.
import os as _audit_os
import sys as _audit_sys
from pathlib import Path as _AuditPath
_audit_root = _AuditPath(__file__).resolve().parents[1]
_audit_sys.path.insert(0, str(_audit_root))
_audit_os.chdir(_audit_root)

import argparse
import concurrent.futures
import hashlib
import io
import json
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / 'audit/upstream-image-audit.json'
UA = 'ShinyDex/1.0 (independent artwork integrity audit)'


def now():
    return datetime.now(timezone.utc).isoformat()


def inspect(item):
    filename, source = item
    local = (ROOT / 'assets' / 'pokemon' / filename).read_bytes()
    result = {'file': filename, 'source': source,
              'localSha256': hashlib.sha256(local).hexdigest()}
    for attempt in range(3):
        try:
            request = urllib.request.Request(source, headers={
                'User-Agent': UA, 'Cache-Control': 'no-cache'})
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = response.read()
                result['resolvedSource'] = response.url
            with Image.open(io.BytesIO(payload)) as image:
                image.load()
                assert image.format == 'PNG', 'Upstream response is not PNG'
                result['upstreamDimensions'] = list(image.size)
            result.update(upstreamSha256=hashlib.sha256(payload).hexdigest(),
                          upstreamBytes=len(payload), checkedAt=now())
            result.pop('error', None)
            result['matches'] = result['upstreamSha256'] == result['localSha256']
            return result
        except Exception as error:
            result['error'] = str(error)
            if attempt < 2:
                time.sleep(1 + attempt)
    result.update(matches=False, checkedAt=now())
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fresh', action='store_true')
    parser.add_argument('--limit', type=int, help='Bound a diagnostic run')
    args = parser.parse_args()
    catalog = json.loads((ROOT / 'data.json').read_text(encoding='utf-8'))
    registry = {r['name']: r for r in json.loads(
        (ROOT / 'audit/archives-images.json').read_text(encoding='utf-8'))}
    downloads = {r['file']: r for r in json.loads(
        (ROOT / 'audit/image-audit.json').read_text(encoding='utf-8')).get('downloads', [])}
    sources = {}
    for pokemon in catalog:
        for mode in ('normal', 'shiny'):
            filename = pokemon[mode + 'File']
            original = registry[filename]['url']
            thumbnail = original.replace('/media/upload/', '/media/upload/thumb/')
            thumbnail += '/200px-' + original.rsplit('/', 1)[-1]
            source = downloads.get(filename, {}).get('source', thumbnail)
            # Constrain network requests to the catalog's recorded Archives art.
            assert source in (original, thumbnail), 'Unexpected artwork source'
            sources[filename] = source
    previous = json.loads(REPORT.read_text(encoding='utf-8')) if REPORT.exists() and not args.fresh else {}
    results = {r['file']: r for r in previous.get('files', []) if r.get('matches')}
    for filename in list(results):
        digest = hashlib.sha256((ROOT / 'assets' / 'pokemon' / filename).read_bytes()).hexdigest()
        if results[filename]['localSha256'] != digest:
            del results[filename]
    pending = [(f, u) for f, u in sources.items() if f not in results]
    if args.limit:
        pending = pending[:args.limit]

    def save():
        rows = [results[f] for f in sources if f in results]
        report = {'updatedAt': now(), 'expectedImages': len(sources),
                  'checkedImages': len(rows), 'matchedImages': sum(r['matches'] for r in rows),
                  'complete': len(rows) == len(sources) and all(r['matches'] for r in rows),
                  'issues': [r for r in rows if not r['matches']], 'files': rows,
                  'limitations': ['Byte identity establishes correspondence with the fetched Archives artwork; visual species/form review is a separate audit.']}
        temporary = REPORT.with_suffix('.json.tmp')
        temporary.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        temporary.replace(REPORT)

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for index, result in enumerate(pool.map(inspect, pending), 1):
            results[result['file']] = result
            if index % 25 == 0:
                save()
                print(f"Fetched {index}/{len(pending)}; matched {sum(r['matches'] for r in results.values())}/{len(sources)}", flush=True)
    save()
    print(f"Matched {sum(r['matches'] for r in results.values())}/{len(sources)} upstream files", flush=True)
    return 0 if len(results) == len(sources) and all(r['matches'] for r in results.values()) else 1


if __name__ == '__main__':
    raise SystemExit(main())
