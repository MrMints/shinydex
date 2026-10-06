"""Map persistent Scatterbug/Spewpa identities to their shared appearances."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
inventory = json.loads((ROOT / 'audit/living-dex-inventory.json').read_text(encoding='utf-8'))
catalog = json.loads((ROOT / 'data.json').read_text(encoding='utf-8'))
forms = []
hashes = {}
for sid in (664, 665, 658, 744, 414):
    base = next(p for p in catalog if p['key'] == sid)
    patterns = [p for p in inventory['forms'] if p['speciesId'] == sid and not p['battleOnly'] and not p['mega']]
    assert len(patterns) == (20 if sid in (664, 665) else 3 if sid == 414 else 2)
    for pattern in patterns:
        definition = {'identity': pattern['identifier'], 'key': 200000 + pattern['formId'],
                      'legacyKey': sid, 'speciesId': sid, 'pokemonId': pattern['pokemonId'],
                      'formLabel': pattern['label'] + ' · Vivillon pattern' if sid in (664, 665) else pattern['label'] + ' · Burmy origin' if sid == 414 else pattern['label'],
                      'height': base['height'], 'weight': base['weight'], 'types': base['types']}
        for mode in ('normal', 'shiny'):
            file = base[mode + 'File']
            assert (ROOT / 'assets/pokemon' / file).is_file()
            hashes[file] = hashlib.sha256((ROOT / 'assets/pokemon' / file).read_bytes()).hexdigest()
            definition[mode + 'File'] = file
            definition[mode + 'Source'] = base[mode + 'Source']
        forms.append(definition)
manifest = {'schemaVersion': 1, 'forms': forms, 'sharedAppearance': True,
            'scopeSource': 'https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_with_form_differences#Scatterbug_and_Spewpa',
            'reviewNote': 'Source confirms 20 latent evolution-pattern forms in Scatterbug/Spewpa, Battle Bond Greninja and Own Tempo Rockruff as separate persistent technical forms. Shared normal/shiny appearance is intentional; old generic ownership does not identify a pattern or ability. Artwork does not establish shiny eligibility.',
            'imageHashes': hashes}
(ROOT / 'reference/pokeapi/living-dex/latent-artwork-map.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
print(f'Mapped {len(forms)} latent pattern, origin and ability identities with existing shared artwork.')
