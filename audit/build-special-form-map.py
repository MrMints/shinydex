"""Finalize visually reviewed non-HOME art with explicit availability metadata."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
inventory = json.loads((ROOT / 'audit/living-dex-inventory.json').read_text(encoding='utf-8'))
review_path = ROOT / 'audit/special-artwork-review.json'
review = json.loads(review_path.read_text(encoding='utf-8'))
catalog = json.loads((ROOT / 'data.json').read_text(encoding='utf-8'))
pokemon = {int(p['id']): p for p in csv.DictReader((ROOT / 'reference/pokeapi/living-dex/pokemon.csv').open(encoding='utf-8'))}
mapping = {'pikachu-cosplay': '0025Pikachu-Cosplay.png', 'pikachu-rock-star': '0025Pikachu-Rock_Star.png',
           'pikachu-belle': '0025Pikachu-Belle.png', 'pikachu-pop-star': '0025Pikachu-Pop_Star.png',
           'pikachu-phd': '0025Pikachu-PhD.png', 'pikachu-libre': '0025Pikachu-Libre.png',
           'floette-eternal': '0670Floette-Eternal.png'}
forms = []
for identity, file in mapping.items():
    form = next(p for p in inventory['forms'] if p['identifier'] == identity)
    base = next(p for p in catalog if p['key'] == form['speciesId'])
    art = next(p for p in review['records'] if p['file'] == file)
    assert hashlib.sha256((ROOT / 'assets/pokemon' / file).read_bytes()).hexdigest() == art['localSha256']
    metrics = pokemon[form['pokemonId']]
    definition = {'identity': identity, 'key': 200000 + form['formId'], 'legacyKey': form['speciesId'],
                  'speciesId': form['speciesId'], 'pokemonId': form['pokemonId'], 'formLabel': form['label'],
                  'height': int(metrics['height']), 'weight': int(metrics['weight']), 'types': base['types'],
                  'normalFile': file, 'shinyFile': file, 'normalSource': art['source'], 'shinySource': art['source'],
                  'shinyArtworkAvailable': False}
    if form['speciesId'] == 25:
        definition.update(gender='Female', shinyLocked=True, shinyLockSource='https://bulbapedia.bulbagarden.net/wiki/Cosplay_Pikachu')
    forms.append(definition)
base = next(p for p in catalog if p['key'] == 172)
standard = {'identity': 'pichu', 'key': 200172, 'legacyKey': 172, 'speciesId': 172,
            'pokemonId': 172, 'formLabel': 'Standard', 'height': base['height'], 'weight': base['weight'], 'types': base['types']}
for mode in ('normal', 'shiny'):
    standard[mode+'File'] = base[mode+'File']; standard[mode+'Source'] = base[mode+'Source']
forms.append(standard)
(ROOT / 'reference/pokeapi/living-dex/special-artwork-map.json').write_text(json.dumps({'schemaVersion': 1, 'forms': forms, 'reviewEvidence': 'audit/special-artwork-review.json'}, indent=2) + '\n', encoding='utf-8')
review.update(reviewComplete=True, visualReviewScope='First seven images inspected on special.png; Spiky-eared Pichu APNG inspected separately with its HGSS sprite caption. Five costume illustrations, uncostumed Cosplay game render, Eternal Flower illustration and Pichu sprite match source-page references. No shiny render is asserted.')
review_path.write_text(json.dumps(review, indent=2) + '\n', encoding='utf-8')
print('Finalized seven special form mappings and standard Pichu; six forms explicitly shiny-locked. Spiky-eared Pichu excluded by user scope.')
