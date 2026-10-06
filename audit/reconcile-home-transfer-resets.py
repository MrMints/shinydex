"""Record reviewed HOME transfer resets without rewriting artwork evidence."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / 'reference/pokeapi/living-dex/home-storage-scope.json'
scope = json.loads(path.read_text(encoding='utf-8'))
definitions = []
for batch in ('type', 'alternate'):
    definitions.extend(json.loads((ROOT / f'reference/pokeapi/living-dex/{batch}-artwork-map.json').read_text(encoding='utf-8'))['forms'])
reset = [p['identity'] for p in definitions
         if (p['speciesId'] in (493, 773) and not p['identity'].endswith('-normal'))
         or (p['speciesId'] == 649 and p['identity'] != 'genesect')
         or p['identity'] in ('dialga-origin', 'palkia-origin', 'giratina-origin')
         or (p['speciesId'] == 1017 and p['identity'] != 'ogerpon')]
assert len(reset) == 44, reset
scope['excludedIdentities'] = list(dict.fromkeys(scope['excludedIdentities'] + reset))
scope['transferResets'] = {
    'identities': reset,
    'sources': [
        'https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9dex_(HOME)#Registering_Pok%C3%A9mon_and_alternate_forms',
        'https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9mon_HOME#Limitations',
        'https://bulbapedia.bulbagarden.net/wiki/Ogerpon_(Pok%C3%A9mon)#Form_data'],
    'reason': 'Held-item forms lose their items on deposit; Arceus and the Origin forms also reset when deposited from Legends: Arceus. HOME Pokédex registration does not establish a separately storable form.'}
scope['reviewRemaining'] = 'Other transfer-specific forms and latent identities remain under review.'
path.write_text(json.dumps(scope, indent=2) + '\n', encoding='utf-8')
print(f'Recorded {len(reset)} transfer-reset appearances outside HOME living-dex storage scope.')
