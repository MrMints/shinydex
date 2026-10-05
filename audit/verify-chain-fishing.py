"""Match chain-fishing routes to each Gen VI rod encounter in the CSV snapshot."""

# Audit tools resolve shared inputs from the repository, regardless of launch directory.
import os as _audit_os
import sys as _audit_sys
from pathlib import Path as _AuditPath
_audit_root = _AuditPath(__file__).resolve().parents[1]
_audit_sys.path.insert(0, str(_audit_root))
_audit_os.chdir(_audit_root)

import csv,json
from pathlib import Path
def read(name):
 with open(name+'.csv',encoding='utf-8-sig') as f:return list(csv.DictReader(f))
pokemon={r['id']:r for r in read('pokemon')}
slots={r['id']:r['encounter_method_id'] for r in read('encounter_slots')}
methods={r['id']:r['identifier'] for r in read('encounter_methods')}
games={'23':'Pokémon X','24':'Pokémon Y','25':'Pokémon Omega Ruby','26':'Pokémon Alpha Sapphire'}
expected=set()
for row in read('encounters'):
 p=pokemon[row['pokemon_id']];method=methods[slots[row['encounter_slot_id']]]
 if row['version_id'] in games and p['is_default']=='1' and method in {'old-rod','good-rod','super-rod'}:
  expected.add((int(p['species_id']),games[row['version_id']],method))
h=json.loads(Path('hunts.json').read_text())
actual=[]
for key,guide in h.items():
 for entry in guide['entries']:
  if entry.get('huntingTechnique')!='gen-six-chain-fishing':continue
  actual.append((int(key),entry['game'],entry['rodMethod']))
  assert entry['status']=='Huntable' and entry['locations']
  assert 'streak of 20' in entry['method'] and 'Shiny Charm' in entry['method']
  assert 'fleeing' in entry['method'] and 'failed reel' in entry['method']
  assert entry['source']=='https://bulbapedia.bulbagarden.net/wiki/Fishing#Generation_VI'
assert set(actual)==expected and len(actual)==len(expected)
print('Verified',len(actual),'chain-fishing species/game/rod routes against recorded Generation VI encounters')
