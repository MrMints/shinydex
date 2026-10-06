"""Inventory form candidates without mistaking decoded rows for reviewed scope."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'reference/pokeapi/living-dex'


def rows(name):
    with (INPUT / name).open(encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle))


def main():
    manifest = json.loads((INPUT / 'manifest.json').read_text(encoding='utf-8'))
    for item in manifest['files']:
        actual = hashlib.sha256((INPUT / item['name']).read_bytes()).hexdigest()
        if actual != item['sha256']:
            raise ValueError(f"Reference drift: {item['name']}")
    pokemon = {int(r['id']): r for r in rows('pokemon.csv')}
    species = {int(r['id']): r for r in rows('pokemon_species.csv')}
    names = {int(r['pokemon_form_id']): r for r in rows('pokemon_form_names.csv') if r['local_language_id'] == '9'}
    catalog = json.loads((ROOT / 'data.json').read_text(encoding='utf-8'))
    existing = {p['key']: p for p in catalog}
    entries = []
    for form in rows('pokemon_forms.csv'):
        pid, fid = int(form['pokemon_id']), int(form['id'])
        sid = int(pokemon[pid]['species_id'])
        if sid > 1025:
            continue
        label = names.get(fid, {}).get('form_name') or form['form_identifier'].replace('-', ' ').title() or 'Standard'
        entry = {
            'speciesId': sid, 'pokemonId': pid, 'formId': fid,
            'identifier': form['identifier'], 'label': label,
            'isDefault': form['is_default'] == '1',
            'battleOnly': form['is_battle_only'] == '1', 'mega': form['is_mega'] == '1',
            'genderDifferences': species[sid]['has_gender_differences'] == '1',
            'genderRate': int(species[sid]['gender_rate']),
            'existingKey': pid if pid in existing and existing[pid]['id'] == sid and form['is_default'] == '1' else None,
            'reviewStatus': 'candidate',
        }
        entries.append(entry)
    counts = Counter('battle' if p['battleOnly'] or p['mega'] else 'persistentCandidate' for p in entries)
    report = {
        'schemaVersion': 1, 'auditComplete': False, 'inventoryOnly': True,
        'referenceCommit': manifest['commit'],
        'scopeSource': 'https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_with_form_differences',
        'limits': [
            'Reference flags do not prove HOME storage, transfer availability, shiny eligibility, or complete coverage.',
            'Species-level gender difference flags need per-form review, particularly regional forms.',
            'Missing upstream forms/artwork require independent reconciliation; nothing is silently dropped.',
            'Existing ownership can be form-unspecified; artwork defaults do not prove which form the user caught.',
        ],
        'counts': dict(counts),
        'genderDifferenceSpecies': [sid for sid, p in species.items() if sid <= 1025 and p['has_gender_differences'] == '1'],
        'forms': entries,
    }
    (ROOT / 'audit/living-dex-inventory.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    assert len([p for p in entries if p['pokemonId'] == 869 and not p['battleOnly']]) == 63
    assert len({p['formId'] for p in entries}) == len(entries)
    print(f"Inventoried {len(entries)} form records; {counts}; 63 Alcremie combinations retained.")


if __name__ == '__main__':
    main()
