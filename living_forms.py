"""Extend the catalog only with explicit reviewed living-form definitions."""
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def extend_catalog(catalog):
    # Generic old records remain unspecified rather than implying a cream/sweet.
    base = next(p for p in catalog if p['key'] == 869)
    base['formLabel'] = 'Form unspecified'
    base['displayName'] = base['speciesName'] + ' · Form unspecified'
    base['formUnspecified'] = True
    manifest = json.loads((ROOT / 'reference/pokeapi/living-dex/alcremie-artwork-map.json').read_text(encoding='utf-8'))
    for definition in manifest['forms']:
        p = copy.deepcopy(base)
        p.pop('formUnspecified', None)
        p.update(key=definition['key'], name=definition['identity'], formLabel=definition['formLabel'],
                 displayName=base['speciesName']+' · '+definition['formLabel'], livingForm=True, legacyKey=869)
        for mode in ('normal','shiny'):
            file = definition[mode+'File']
            assert (ROOT / 'assets/pokemon' / file).is_file(), file
            p[mode+'File'] = file
            p[mode+'Source'] = definition[mode+'Source']
            p[mode] = './assets/pokemon/'+file
        catalog.append(p)
    manifest = json.loads((ROOT / 'reference/pokeapi/living-dex/gender-artwork-map.json').read_text(encoding='utf-8'))
    by_key = {p['key']:p for p in catalog}
    for definition in manifest['forms']:
        base = by_key[definition['legacyKey']]
        if not base.get('formUnspecified'):
            base['formLabel'] = (base.get('formLabel','')+' · ' if base.get('region') else '')+'Gender unspecified'
            base['displayName'] = base['speciesName']+' · '+base['formLabel']
            base['formUnspecified'] = True
        p = copy.deepcopy(base)
        p.pop('formUnspecified', None)
        p.update(key=definition['key'], name=definition['identity'], formLabel=definition['formLabel'],
                 displayName=base['speciesName']+' · '+definition['formLabel'], livingForm=True,
                 legacyKey=definition['legacyKey'], gender=definition['gender'])
        for mode in ('normal','shiny'):
            p[mode+'File'] = definition[mode+'File']
            p[mode+'Source'] = definition[mode+'Source']
            p[mode] = './assets/pokemon/'+definition[mode+'File']
        catalog.append(p)
    manifest = json.loads((ROOT / 'reference/pokeapi/living-dex/unown-artwork-map.json').read_text(encoding='utf-8'))
    base = by_key[201]
    base.update(formLabel='Form unspecified', displayName=base['speciesName']+' · Form unspecified', formUnspecified=True)
    for definition in manifest['forms']:
        p = copy.deepcopy(base)
        p.pop('formUnspecified', None)
        p.update(key=definition['key'], name=definition['identity'], formLabel=definition['formLabel'],
                 displayName=base['speciesName']+' · '+definition['formLabel'], livingForm=True, legacyKey=201)
        for mode in ('normal','shiny'):
            p[mode+'File'] = definition[mode+'File']
            p[mode+'Source'] = definition[mode+'Source']
            p[mode] = './assets/pokemon/'+definition[mode+'File']
        catalog.append(p)
    definitions = []
    for batch in ('persistent', 'alternate', 'type', 'latent', 'cap', 'technical', 'special'):
        definitions.extend(json.loads((ROOT / f'reference/pokeapi/living-dex/{batch}-artwork-map.json').read_text(encoding='utf-8'))['forms'])
    home_scope = json.loads((ROOT / 'reference/pokeapi/living-dex/home-storage-scope.json').read_text(encoding='utf-8'))
    excluded = set(home_scope['excludedIdentities'])
    for definition in definitions:
        if definition['identity'] in excluded:
            continue
        base = by_key[definition['legacyKey']]
        base.update(formLabel='Form unspecified', displayName=base['speciesName']+' · Form unspecified', formUnspecified=True)
        p = copy.deepcopy(base)
        p.pop('formUnspecified', None)
        p.update(key=definition['key'], name=definition['identity'], formLabel=definition['formLabel'],
                 displayName=base['speciesName']+' · '+definition['formLabel'], livingForm=True,
                 legacyKey=definition['legacyKey'], types=definition['types'],
                 height=definition['height'], weight=definition['weight'])
        if definition.get('artworkView'):
            p['artworkView'] = definition['artworkView']
        if 'shinyArtworkAvailable' in definition:
            p['shinyArtworkAvailable'] = definition['shinyArtworkAvailable']
        for field in ('shinyLocked', 'shinyLockSource', 'gender'):
            if field in definition: p[field] = definition[field]
        for mode in ('normal', 'shiny'):
            p[mode+'File'] = definition[mode+'File']
            p[mode+'Source'] = definition[mode+'Source']
            p[mode] = './assets/pokemon/'+definition[mode+'File']
        catalog.append(p)
    assert len({p['key'] for p in catalog}) == len(catalog)
    return catalog
