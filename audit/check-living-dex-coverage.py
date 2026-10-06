"""Enumerate uncovered candidates without treating snapshot flags as scope proof."""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
inventory = json.loads((ROOT / 'audit/living-dex-inventory.json').read_text(encoding='utf-8'))
catalog = json.loads((ROOT / 'data.json').read_text(encoding='utf-8'))
identities = {p['name'] for p in catalog if p.get('livingForm') or p.get('region')}
family_ids = {p['id'] for p in catalog if p.get('livingForm')}
by_key = {p['key']: p for p in catalog}
gender_legacy = {p['legacyKey'] for p in catalog if p.get('gender')}
dispositions = {p['identifier']: p for p in json.loads((ROOT / 'reference/pokeapi/living-dex/form-dispositions.json').read_text(encoding='utf-8'))['records']}
home_scope = json.loads((ROOT / 'reference/pokeapi/living-dex/home-storage-scope.json').read_text(encoding='utf-8'))
records = []
for form in inventory['forms']:
    # Ordinary singleton species are already catalogued. Alternate families need
    # every candidate disposition reviewed; default labels can differ from names.
    sid = form['speciesId']
    siblings = [f for f in inventory['forms'] if f['speciesId'] == sid]
    if len(siblings) == 1 and sid not in family_ids:
        continue
    concrete_key = 200000 + form['formId']
    legacy = by_key.get(form.get('existingKey'))
    evidence = None
    if concrete_key in by_key and by_key[concrete_key].get('livingForm'):
        status, evidence = 'integrated', {'catalogKey': concrete_key}
    elif form['identifier'] in identities:
        status, evidence = 'integrated', {'identity': form['identifier']}
    elif legacy and not legacy.get('formUnspecified'):
        status, evidence = 'integrated-standard', {'catalogKey': legacy['key']}
    elif form.get('existingKey') in gender_legacy:
        status, evidence = 'integrated-gender-pair', {'legacyKey': form['existingKey'], 'catalogKeys': [p['key'] for p in catalog if p.get('gender') and p.get('legacyKey') == form['existingKey']]}
    else:
        status = 'temporary-candidate' if form['battleOnly'] or form['mega'] else 'needs-scope-review'
    if form['identifier'] in dispositions:
        disposition = dispositions[form['identifier']]
        if 'catalogKey' in disposition: assert disposition['catalogKey'] in by_key
        status, evidence = disposition['disposition'], disposition
    if form['identifier'] in home_scope['excludedIdentities']:
        status, evidence = 'excluded-home-storage', {'source': home_scope['source'], 'reason': 'Outside user-authorized HOME storage scope'}
    records.append({**form, 'coverageStatus': status, 'catalogEvidence': evidence})
report = {
    'auditComplete': False,
    'limitation': 'PokeAPI battleOnly and mega flags are candidate classification, not proof of storage scope or user eligibility. Technical duplicates, default names, spin-offs and latent forms still need explicit reviewed dispositions.',
    'catalogRecords': len(catalog),
    'counts': dict(Counter(p['coverageStatus'] for p in records)),
    'records': records,
}
(ROOT / 'audit/living-dex-coverage.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'catalogRecords': len(catalog), 'candidateCounts': report['counts']}))
