"""Verify catch-combo routes match recorded Let's Go overworld encounters."""
import csv,json
from pathlib import Path
def rows(name):
 with open(name+'.csv',encoding='utf-8-sig') as f:return list(csv.DictReader(f))
p={r['id']:r for r in rows('pokemon')}
s={r['id']:r['encounter_method_id'] for r in rows('encounter_slots')}
m={r['id']:r['identifier'] for r in rows('encounter_methods')}
v={r['id']:r['identifier'] for r in rows('versions')}
games={'lets-go-pikachu':"Pokémon Let's Go, Pikachu!",'lets-go-eevee':"Pokémon Let's Go, Eevee!"}
expected=set()
for r in rows('encounters'):
 version=v[r['version_id']];method=m[s[r['encounter_slot_id']]];pokemon=p[r['pokemon_id']]
 if version in games and method.startswith('overworld') and pokemon['is_default']=='1':expected.add((int(pokemon['species_id']),games[version],method))
actual=[]
for key,g in json.loads(Path('hunts.json').read_text()).items():
 for e in g['entries']:
  if e.get('huntingTechnique')!='lets-go-catch-combo':continue
  actual.append((int(key),e['game'],e['spawnMethod']))
  assert 'only to the next spawn' in e['method'] and 'continue catching' in e['method'] and '31 or more' in e['method']
  assert e['status']=='Huntable' and e['locations'] and 'Lures' in e['method']
assert set(actual)==expected and len(actual)==len(expected)
assert not any(species in (808,809) for species,_,_ in actual)
print('Verified',len(actual),"Let's Go catch-combo species/game/spawn routes")
