"""Map reviewed persistent technical forms to shared artwork and exact metrics."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
inventory = json.loads((ROOT / 'audit/living-dex-inventory.json').read_text(encoding='utf-8'))
catalog = json.loads((ROOT / 'data.json').read_text(encoding='utf-8'))
pokemon = {int(p['id']): p for p in csv.DictReader((ROOT / 'reference/pokeapi/living-dex/pokemon.csv').open(encoding='utf-8'))}
selected = [p for p in inventory['forms'] if not p['battleOnly'] and
            ('totem' in p['identifier'] or p['identifier'] in
             ('zygarde-10-power-construct', 'zygarde-50-power-construct'))]
forms = []
for form in selected:
    sid = form['speciesId']
    if form['identifier'] == 'raticate-totem-alola':
        base = next(p for p in catalog if p['name'] == 'raticate-alola')
    elif form['identifier'] == 'marowak-totem':
        base = next(p for p in catalog if p['name'] == 'marowak-alola')
    elif sid == 718:
        base = next(p for p in catalog if p['name'] == ('zygarde-10' if '-10-' in form['identifier'] else 'zygarde-50'))
    else:
        base = next(p for p in catalog if p['key'] == sid)
    metrics = pokemon[form['pokemonId']]
    label = form['label'] + ' · Power Construct' if sid == 718 else 'Totem-like' + (' · Alolan' if base.get('region') == 'alola' else '')
    definition = {'identity': form['identifier'], 'key': 200000 + form['formId'],
                  'legacyKey': sid if sid == 718 else base['key'], 'speciesId': sid, 'pokemonId': form['pokemonId'],
                  'formLabel': label, 'height': int(metrics['height']), 'weight': int(metrics['weight']),
                  'types': base['types']}
    for mode in ('normal', 'shiny'):
        definition[mode + 'File'] = base[mode + 'File']
        definition[mode + 'Source'] = base[mode + 'Source']
    forms.append(definition)
    if sid != 718:
        ordinary = next(p for p in inventory['forms'] if p.get('existingKey') == base['key'] and not p['battleOnly'] and not p['mega'])
        standard = dict(definition)
        standard.update(identity=ordinary['identifier'], key=200000 + ordinary['formId'],
                        pokemonId=ordinary['pokemonId'], formLabel=ordinary['label'] if base.get('region') != 'alola' else 'Alolan · Standard size',
                        height=base['height'], weight=base['weight'])
        forms.append(standard)
assert len(forms) == 24
manifest = {'schemaVersion': 1, 'forms': forms,
            'scopeSource': 'https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_with_form_differences#Totem_Pok%C3%A9mon',
            'notes': 'Eleven obtainable Totem-like technical forms persist outside battle but do not retain size in HOME. Shared artwork is intentional; pinned dimensions distinguish them. Two Power Construct Zygarde identities retain separate ownership. Shiny eligibility remains separately unresolved.'}
(ROOT / 'reference/pokeapi/living-dex/technical-artwork-map.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
print('Mapped 11 Totem-like, 11 standard-size and two Power Construct Zygarde forms.')
