"""Guard the audit workspace boundary, migrated references, and artwork evidence."""
import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AUDIT = ROOT / 'audit'
migration = json.loads((AUDIT / 'migration-baseline.json').read_text(encoding='utf-8'))
for old, new in migration['moves'].items():
    assert not (ROOT / old).exists(), f'Stale audit file recreated: {old}'
    assert (ROOT / new).is_file(), f'Migrated audit file missing: {new}'
    if Path(new).suffix in {'.png', '.jpg'}:
        assert hashlib.sha256((ROOT / new).read_bytes()).hexdigest() == migration['beforeSha256'][old], new

assert {p.name for p in ROOT.glob('*.json')} == {'package.json', 'data.json', 'hunts.json'}, 'Keep audit JSON in audit/'
assert not any(ROOT.glob('verify-*')), 'Keep verification scripts in audit/'
assert not any(ROOT.glob('audit-*')), 'Keep audit scripts and reports in audit/'
for p in [*ROOT.glob('*.py'), *AUDIT.glob('*.py'), *(AUDIT / 'windows').glob('*.py')]:
    ast.parse(p.read_text(encoding='utf-8'), filename=str(p))

# Statically check literal audit paths used by producers and consumers.
moved_names = {Path(old).name for old in migration['moves'] if '/' not in old}
for p in [*ROOT.glob('*.py'), *AUDIT.glob('*.py')]:
    if p.resolve() == Path(__file__).resolve():
        continue
    tree = ast.parse(p.read_text(encoding='utf-8'))
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if node.value in moved_names:
                raise AssertionError(f'{p.name}:{node.lineno} uses former audit path {node.value}')
            if node.value.startswith('audit/') and node.value.endswith('.json'):
                assert (ROOT / node.value).is_file(), f'Missing referenced audit JSON: {node.value}'

visual = json.loads((AUDIT / 'visual-image-audit.json').read_text(encoding='utf-8'))
for sheet in visual['sheets']:
    path = ROOT / sheet['file']
    assert path.is_file(), f'Missing reviewed sheet: {sheet["file"]}'
    assert hashlib.sha256(path.read_bytes()).hexdigest() == sheet['sha256']
print(f'Verified {len(migration["moves"])} audit relocations, canonical paths and unchanged reviewed artwork')
