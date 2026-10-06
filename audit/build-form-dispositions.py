"""Record reviewed state aliases without adding duplicate ownership slots."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
catalog = json.loads((ROOT / 'data.json').read_text(encoding='utf-8'))
inventory = json.loads((ROOT / 'audit/living-dex-inventory.json').read_text(encoding='utf-8'))
records = []
for form in inventory['forms']:
    if form['speciesId'] == 774 and form['identifier'].endswith('-meteor'):
        target = form['identifier'].removesuffix('-meteor')
        record = next(p for p in catalog if p['name'] == target)
        records.append({'identifier': form['identifier'], 'disposition': 'represented-state',
                        'catalogKey': record['key'],
                        'reason': 'Meteor shell and exposed core are Shields Down states of the same fixed-color individual; ownership is represented by its core-color slot.',
                        'source': 'https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_with_form_differences#Minior'})
    elif form['speciesId'] in (1007, 1008) and form['pokemonId'] != form['speciesId']:
        records.append({'identifier': form['identifier'], 'disposition': 'represented-state',
                        'catalogKey': form['speciesId'],
                        'reason': 'Traversal/power state of the same partner, represented by its species ownership slot rather than another captured individual.',
                        'source': 'https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_with_form_differences#Koraidon_and_Miraidon'})
    elif form['identifier'] in ('arceus-unknown', 'eternatus-eternamax'):
        records.append({'identifier': form['identifier'], 'disposition': 'excluded-unobtainable',
                        'reason': 'Unused unobtainable type' if form['identifier'] == 'arceus-unknown' else 'Unobtainable boss/move-animation form',
                        'source': 'https://bulbapedia.bulbagarden.net/wiki/' + ('Arceus' if form['speciesId'] == 493 else 'Eternatus') + '_(Pok%C3%A9mon)#Form_data'})
    elif form['identifier'] == 'pichu-spiky-eared':
        records.append({'identifier': form['identifier'], 'disposition': 'excluded-user-scope',
                        'reason': 'User explicitly excludes Spiky-eared Pichu: confined to HeartGold/SoulSilver and cannot transfer to HOME.',
                        'source': 'https://bulbapedia.bulbagarden.net/wiki/Spiky-eared_Pichu'})
assert len(records) == 18
(ROOT / 'reference/pokeapi/living-dex/form-dispositions.json').write_text(json.dumps({'schemaVersion': 1, 'records': records}, indent=2) + '\n', encoding='utf-8')
print('Recorded 15 represented states, two unobtainable exclusions and one user-directed HOME exclusion.')
