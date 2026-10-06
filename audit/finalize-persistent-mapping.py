"""Finalize the 91 mappings inspected on the four persistent-form sheets."""
import csv
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main(batch='persistent', expected=91):
    path = ROOT / f'audit/{batch}-artwork-review.json'
    review = json.loads(path.read_text(encoding='utf-8'))
    names = ['', 'normal', 'fighting', 'flying', 'poison', 'ground', 'rock', 'bug',
             'ghost', 'steel', 'fire', 'water', 'grass', 'electric', 'psychic',
             'ice', 'dragon', 'dark', 'fairy']
    types = {}
    with (ROOT / 'types.csv').open(encoding='utf-8-sig') as source:
        for row in csv.DictReader(source):
            types.setdefault(int(row['pokemon_id']), []).append(names[int(row['type_id'])])
    downloads = {row['file']: row for row in review['downloads']}
    for form in review['mappings']:
        form['types'] = types[form['pokemonId']]
        if form['speciesId'] in (493, 773):
            form['types'] = [form['identity'].rsplit('-', 1)[1]]
        for mode in ('normal', 'shiny'):
            file = form[mode + 'File']
            caption = review['captions'][file]['wikitext']
            template = re.search(r'\{\{HOME\|[^}]*\}\}', caption, re.I)
            assert template, file
            assert ('shiny' in template.group().lower()) == (mode == 'shiny' and batch != 'cap'), file
            assert hashlib.sha256((ROOT / 'assets/pokemon' / file).read_bytes()).hexdigest() == downloads[file]['localSha256'], file
    assert len(review['mappings']) == expected
    manifest = {
        'schemaVersion': 1, 'forms': review['mappings'],
        'reviewEvidence': f'audit/{batch}-artwork-review.json',
        'typeInputSha256': hashlib.sha256((ROOT / 'types.csv').read_bytes()).hexdigest(),
        'captionLimitations': 'Default forms often omit their label. Flower captions omit color; all five colors were visually inspected. Plant/trash cloaks and west/spring defaults were checked visually. Size captions identify the size; resized thumbnails do not establish physical scale.',
    }
    if batch == 'alternate':
        manifest['captionLimitations'] = 'Default captions omit some form labels. Minior cores share one shiny appearance; all seven ownership identities remain separate. Artwork does not establish shiny eligibility or transfer/storage compatibility.'
    if batch == 'type':
        manifest['captionLimitations'] = 'All 58 pairs visually inspected on type-1 through type-3 and captions matched. Default captions can omit labels. Tea forms use rear artwork to expose authenticity marks. Arceus and Silvally types follow their explicit type identity; PokeAPI pokemon IDs can share a Normal-type record. Artwork does not establish shiny eligibility or HOME transfer compatibility.'
        for form in manifest['forms']:
            if form['speciesId'] in (854, 855, 1012, 1013):
                form['artworkView'] = 'back'
    if batch == 'cap':
        manifest['captionLimitations'] = 'Eight normal cap images reviewed against source captions and cap-1 sheet. No separate shiny render exists in the captured registry; normal artwork is displayed with an explicit unavailable-shiny-art indication. Artwork availability does not establish shiny eligibility.'
        for form in manifest['forms']:
            form['shinyArtworkAvailable'] = False
    (ROOT / f'reference/pokeapi/living-dex/{batch}-artwork-map.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    scope = 'All 91 normal/shiny pairs inspected on persistent-1 through persistent-4 sheets. Identity, color, appliance, cloak, season, pattern and visible family/segment counts checked. Size identity supported by captions and pinned height/weight, not thumbnail scale.' if batch == 'persistent' else 'All 55 normal/shiny pairs inspected on alternate-1 through alternate-3 sheets, with HOME source captions. Seven Minior colors share the reviewed black shiny core. Appearance does not prove shiny eligibility.'
    if batch in ('type', 'cap'):
        scope = manifest['captionLimitations']
    review.update(reviewComplete=True, visualReviewScope=scope, unresolved=['Eternal Flower Floette has no paired HOME artwork in this registry and remains outside this batch.'] if batch == 'persistent' else [])
    path.write_text(json.dumps(review, indent=2) + '\n', encoding='utf-8')
    print(f'Finalized {expected} {batch} forms with form-specific types and dimensions.')


if __name__ == '__main__':
    main()
