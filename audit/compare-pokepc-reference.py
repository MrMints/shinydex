"""Compare reference family coverage and retain unverified identity details."""
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def normalize(text):
    return re.sub(r'[^a-z0-9♀♂]', '', unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode().lower())

def form_name(text):
    if text in ('!', '?'): return text
    text = re.sub(r'\b(forme?|size|pattern|type)\b', '', text, flags=re.I)
    return normalize(text)

catalog = json.loads((ROOT / 'data.json').read_text(encoding='utf-8'))
reference = json.loads((ROOT / 'audit/pokepc-living-dex-reference.json').read_text(encoding='utf-8'))
species = {p['id']: p['speciesName'] for p in catalog}
names = sorted(((normalize(name), sid) for sid, name in species.items()), reverse=True, key=lambda item: len(item[0]))
groups = defaultdict(set)
unmapped = []
for slot in reference['slots']:
    label = slot.split(', ', 1)[1]
    text = normalize(label)
    if text in ('heatrotom', 'washrotom', 'frostrotom', 'fanrotom', 'mowrotom'):
        sid = 479
    elif label.startswith('Nidoran'):
        sid = 29 if '♀' in label else 32
    else:
        sid = next((sid for name, sid in names if text.startswith(name)), None)
    if sid is None: unmapped.append(label)
    else: groups[sid].add(label)
rows = []
unmatched_forms = []
# Reviewed naming aliases; these do not infer ownership or transfer eligibility.
aliases = {
    'Raticate (Alolan Form)': 210194,
    'Marowak (Alolan Form)': 210217,
    'Sneasel (Hisuian Form)': 320470,
    'Sneasel (Female Hisuian Form)': 320471,
    'Basculin (White-Striped Form)': 10247,
    'Xerneas (Neutral Mode)': 716,
    'Hoopa Unbound': 210188,
}
for sid, labels in sorted(groups.items()):
    forms = [p for p in catalog if p['id'] == sid and not p.get('formUnspecified')]
    matches = []
    for label in sorted(labels):
        suffix = label[len(species[sid]):].strip(' ()') if label.startswith(species[sid]) else label
        if not suffix:
            candidates = [p for p in forms if p.get('gender') == 'Male' and not p.get('region')]
            if not candidates: candidates = [p for p in forms if p['key'] == sid or p['key'] == 200000 + sid]
            if not candidates and len(forms) == 1: candidates = forms
        else:
            candidates = [p for p in forms if form_name(p.get('formLabel', 'Standard')) == form_name(suffix)]
        if label in aliases:
            candidates = [p for p in forms if p['key'] == aliases[label]]
        if len(candidates) == 1:
            p = candidates[0]
            assert isinstance(p['position'], int) and p['position'] >= 0
            matches.append({'referenceLabel': label, 'catalogKey': p['key'], 'catalogLabel': p.get('formLabel', 'Standard'),
                            'homePosition': p['position'], 'matchVerified': True})
        else:
            matches.append({'referenceLabel': label, 'matchVerified': False})
            unmatched_forms.append({'speciesId': sid, 'referenceLabel': label, 'catalogLabels': [p.get('formLabel', 'Standard') for p in forms]})
    rows.append({'speciesId': sid, 'species': species[sid], 'referenceLabels': sorted(labels),
                 'catalogForms': [{'key': p['key'], 'label': p.get('formLabel', 'Standard')} for p in forms],
                 'referenceCount': len(labels), 'catalogCount': len(forms),
                 'countCoverage': len(forms) >= len(labels),
                 'independentTransferVerification': False,
                 'formMatches': matches,
                 'limitation': 'Reference identity matches do not independently verify transfer, eligibility, artwork or hunting routes.'})
matched_keys = {m['catalogKey'] for r in rows for m in r['formMatches'] if m['matchVerified']}
additional = [{'key': p['key'], 'speciesId': p['id'], 'species': p['speciesName'],
               'form': p.get('formLabel', 'Standard'), 'homePosition': p['position'],
               'verificationStatus': 'Not present in the saved working reference; HOME storage identity remains unverified.'}
              for p in catalog if not p.get('formUnspecified') and p['key'] not in matched_keys]
report = {'source': reference['source'], 'speciesNumberReference': 'https://pokepc.net/pokemon',
          'speciesNumberReferenceReviewedDate': '2026-10-05',
          'speciesNumberReferenceScope': 'Species names and National Dex numbers; includes temporary transformations excluded from this app.',
          'additionalCatalogForms': additional, 'auditComplete': False, 'userAuthorizedWorkingReference': True,
          'unmappedLabels': unmapped, 'familiesBelowReferenceCount': [r['speciesId'] for r in rows if not r['countCoverage']],
          'unmatchedForms': unmatched_forms, 'families': rows}
(ROOT / 'audit/pokepc-living-dex-comparison.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print(json.dumps({'referenceFamilies': len(rows), 'unmapped': unmapped, 'belowReferenceCount': report['familiesBelowReferenceCount'], 'unmatchedForms': unmatched_forms}))
