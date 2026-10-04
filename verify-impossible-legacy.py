import json
from pathlib import Path
root=Path(__file__).parent;h=json.loads((root/'hunts.json').read_text());a=json.loads((root/'impossible-legacy-audit.json').read_text())
species={str(p['key']):p['id'] for p in json.loads((root/'data.json').read_text())}
assert len(a['records'])==a['removedCount']
for r in a['records']:assert r['entry'] not in h[str(r['key'])]['entries'] and r['reason']
for key,g in h.items():
 for e in g['entries']:
  if e['game'] in {"Pokémon Let's Go, Pikachu!","Pokémon Let's Go, Eevee!"}:assert species[key]<=151 or species[key] in {808,809} or e['status']=='Shiny Locked'
  if int(key) in {900,902,903,904}:assert e['game'] not in {'Pokémon Sword','Pokémon Shield','Pokémon The Isle Of Armor Sword','Pokémon The Isle Of Armor Shield','Pokémon The Crown Tundra Sword','Pokémon The Crown Tundra Shield'}
  generic=e['method'].startswith('Catch shiny ') and e['method'].endswith(' and evolve it')
  if generic and int(key) in {26,103,105}:assert e['game'] not in {'Pokémon Sun','Pokémon Moon'}
  if generic and int(key) in {110,122}:assert e['game'] not in {'Pokémon Sword','Pokémon Shield','Pokémon The Isle Of Armor Sword','Pokémon The Isle Of Armor Shield','Pokémon The Crown Tundra Sword','Pokémon The Crown Tundra Shield'}
assert any(e.get('breedingKind')=='direct-egg' and e['game']=='Pokémon Sword / Shield' for e in h['122']['entries']), 'Kanto Mr. Mime direct eggs without Odd Incense remain valid'
for key in [10100,10114,10115]:assert any(e.get('olderEvolutionKind') and e['game']=='Pokémon Sun / Moon' for e in h[str(key)]['entries'])
for key in [10167,10168]:assert any(e.get('evolutionKind') and e['game']=='Pokémon Sword / Shield' for e in h[str(key)]['entries'])
assert all(not h[str(k)]['locked'] for k in {169,196,197,900,902,903,904})
print('Verified',a['removedCount'],'impossible evolution claims removed without falsely applying global shiny locks')
