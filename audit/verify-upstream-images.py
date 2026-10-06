"""Check that independently fetched artwork evidence still covers local assets."""

# Audit tools resolve shared inputs from the repository, regardless of launch directory.
import os as _audit_os
import sys as _audit_sys
from pathlib import Path as _AuditPath
_audit_root = _AuditPath(__file__).resolve().parents[1]
_audit_sys.path.insert(0, str(_audit_root))
_audit_os.chdir(_audit_root)

import hashlib
import json
from pathlib import Path
from artwork_evidence import living_artwork_evidence

ROOT = Path(__file__).resolve().parent.parent
catalog = json.loads((ROOT / 'data.json').read_text(encoding='utf-8'))
report = json.loads((ROOT / 'audit/upstream-image-audit.json').read_text(encoding='utf-8'))
expected = {p[mode + 'File'] for p in catalog for mode in ('normal', 'shiny')}
rows = {row['file']: row for row in report['files']}
assert len(rows) == len(report['files']), 'Duplicate upstream evidence'
_, form_downloads = living_artwork_evidence()
assert expected <= set(rows) | set(form_downloads), 'Upstream evidence does not cover the catalog'
assert report['complete'] and not report['issues']
baseline_files = expected & set(rows)
for filename in baseline_files:
    row = rows[filename]
    actual = hashlib.sha256((ROOT / 'assets' / 'pokemon' / filename).read_bytes()).hexdigest()
    assert row['matches'] and actual == row['localSha256'] == row['upstreamSha256'], filename
    assert row['source'].startswith('https://archives.bulbagarden.net/media/upload/'), filename
    assert row['upstreamBytes'] > 0 and row['checkedAt'], filename
for filename in expected - set(rows):
    row = form_downloads[filename]
    actual = hashlib.sha256((ROOT / 'assets/pokemon' / filename).read_bytes()).hexdigest()
    assert actual == row['localSha256'], filename
    assert len(row['sourceSha256']) == 64 and row['source'].startswith('https://archives.bulbagarden.net/wiki/File:'), filename
print(f'{len(baseline_files)} runtime artwork files match baseline upstream hashes; {len(expected-set(rows))} additional files retain their recorded download/local hashes. Recorded transformed payloads are not asserted byte-identical to upstream; visual review has separate scope.')
