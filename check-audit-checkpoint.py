"""Detect checkpoint drift; this does not certify the audit's correctness."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
checkpoint = json.loads((root / 'audit-checkpoint.json').read_text(encoding='utf-8'))
changed = []
missing = []
for section in ('inputs', 'evidenceReports'):
    for relative, expected in checkpoint[section].items():
        target = root / relative
        if not target.is_file():
            missing.append(relative)
        elif hashlib.sha256(target.read_bytes()).hexdigest() != expected:
            changed.append(relative)
print('Audit complete:', checkpoint['auditComplete'])
print('Checkpoint date:', checkpoint['checkpointDate'])
print('Changed checkpoint files:', len(changed))
for relative in changed:
    print('  changed:', relative)
for relative in missing:
    print('  missing:', relative)
print('Unchanged hashes do not prove correctness or exhaustive coverage.')
raise SystemExit(1 if changed or missing else 0)
