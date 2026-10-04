"""Check that independently fetched artwork evidence still covers local assets."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
catalog = json.loads((ROOT / 'data.json').read_text(encoding='utf-8'))
report = json.loads((ROOT / 'upstream-image-audit.json').read_text(encoding='utf-8'))
expected = {p[mode + 'File'] for p in catalog for mode in ('normal', 'shiny')}
rows = {row['file']: row for row in report['files']}
assert len(rows) == len(report['files']), 'Duplicate upstream evidence'
assert set(rows) == expected, 'Upstream evidence does not cover the catalog'
assert report['complete'] and not report['issues']
for filename, row in rows.items():
    actual = hashlib.sha256((ROOT / 'assets' / 'pokemon' / filename).read_bytes()).hexdigest()
    assert row['matches'] and actual == row['localSha256'] == row['upstreamSha256'], filename
    assert row['source'].startswith('https://archives.bulbagarden.net/media/upload/'), filename
    assert row['upstreamBytes'] > 0 and row['checkedAt'], filename
print(f'All {len(rows)} local artwork files match independently fetched upstream hashes')
