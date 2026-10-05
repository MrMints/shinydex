"""Verify every species in the pinned roster is represented in both X and Y."""

# Audit tools resolve shared inputs from the repository, regardless of launch directory.
import os as _audit_os
import sys as _audit_sys
from pathlib import Path as _AuditPath
_audit_root = _AuditPath(__file__).resolve().parents[1]
_audit_sys.path.insert(0, str(_audit_root))
_audit_os.chdir(_audit_root)

import json
from pathlib import Path
from friend_safari_hunts import roster
h=json.loads(Path('hunts.json').read_text())
actual=[]
for key,guide in h.items():
 for e in guide['entries']:
  if e.get('huntingTechnique')!='xy-friend-safari':continue
  actual.append((int(key),e['game']))
  assert e['status']=='Huntable' and 'local play' in e['method'] and 'third-slot' in e['method'] and 'Shiny Charm' in e['method']
  assert 'https://bulbapedia.bulbagarden.net/wiki/Friend_Safari' in e['sourceReferences']
  normal_slots={216:1,190:1,206:1,506:1,294:2,352:2,531:2,572:2,113:3,132:3,133:3,235:3}
  if int(key) in normal_slots:
   slot=normal_slots[int(key)]
   assert e['friendSafariType']=='Normal' and e['friendSafariSlot']==slot
   assert f'Kiloude City · Normal-type Friend Safari · Slot {slot}' in e['locations']
   assert ('The third-slot unlock is required' if slot==3 else 'available before the third slot') in e['method']
assert set(actual)=={(s,g) for s in roster() for g in ('Pokémon X','Pokémon Y')}
assert len(actual)==len(set(actual))
assert {666,670,132,113,651,654,657}<=roster()
print('Verified',len(actual),'Friend Safari species/game routes against the pinned roster, including Floette and Vivillon')
for safari_type,slots in {
 'Grass':{1:[43,114,191,511],2:[2,541,548,586],3:[556,651,673]},
 'Poison':{1:[14,44,268,336],2:[49,168,317,569],3:[89,452,454,544]},
 'Electric':{1:[101,417,587,702],2:[25,125,618,694],3:[310,404,523,596]},
 'Ground':{1:[27,194,231,328],2:[51,105,290,323],3:[423,536,660]},
 'Psychic':{1:[63,96,326,517],2:[202,561,677],3:[178,203,575,578]},
 'Rock':{1:[299,525,557],2:[95,219,222,247],3:[112,213,689]},
 'Ice':{1:[225,361,363,459],2:[215,614,712],3:[87,91,131,221]},
 'Fire':{1:[58,77,126,513],2:[5,218,636,668],3:[38,654,662]},
 'Fighting':{1:[56,67,307,619],2:[538,539,674],3:[236,286,297,447]},
 'Water':{1:[98,224,400,515],2:[8,130,195,419],3:[61,184,657]},
}.items():
 for slot,species_list in slots.items():
  for species in species_list:
   entries=[e for e in h[str(species)]['entries'] if e.get('huntingTechnique')=='xy-friend-safari']
   assert len(entries)==2
   for e in entries:
    assert e['friendSafariType']==safari_type and e['friendSafariSlot']==slot
    assert f'Kiloude City · {safari_type}-type Friend Safari · Slot {slot}' in e['locations']
    assert ('The third-slot unlock is required' if slot==3 else 'available before the third slot') in e['method']
print('Verified exact slots and type assignments for Normal, Fire, Fighting, Water, Grass, Poison, Electric, Ground, Psychic, Rock and Ice Safaris')
for slot,species_list in {1:[16,21,83,84],2:[163,520,527,581],3:[357,627,662,701]}.items():
 for species in species_list:
  for e in h[str(species)]['entries']:
   if e.get('huntingTechnique')!='xy-friend-safari':continue
   assert {'type':'Flying','slot':slot} in e['friendSafariAssignments']
   assert f'Kiloude City · Flying-type Friend Safari · Slot {slot}' in e['locations']
for e in h['662']['entries']:
 if e.get('huntingTechnique')=='xy-friend-safari':
  assert e['friendSafariAssignments']==[{'type':'Fire','slot':3},{'type':'Flying','slot':3}]
  assert len(e['locations'])==2
print('Verified Flying Safari slots and both Fire/Flying routes for Fletchinder')
for kind,slots in {
 'Dark':{1:[262,274,624,629],2:[215,332,342,551],3:[302,359,510,686]},
 'Steel':{1:[82,303,597],2:[205,227,375,600],3:[437,530,707]},
 'Fairy':{1:[175,209,281,702],2:[39,303,682,684],3:[35,670]},
 'Bug':{1:[12,46,165,415],2:[267,284,313,314],3:[49,127,214,666]},
 'Dragon':{1:[444,611],2:[148,372,714],3:[621,705]},
 'Ghost':{1:[353,608],2:[708,710],3:[356,426,442,623]},
}.items():
 for slot,species_list in slots.items():
  for species in species_list:
   for e in h[str(species)]['entries']:
    if e.get('huntingTechnique')!='xy-friend-safari':continue
    assert {'type':kind,'slot':slot} in e['friendSafariAssignments']
    assert f'Kiloude City · {kind}-type Friend Safari · Slot {slot}' in e['locations']
for species,text in [(666,'hunting player’s own location data'),(710,'Average Size'),(423,'West Sea form only'),(586,'Spring Form only'),(670,'Orange and White flowers are unavailable')]:
 assert all(text in e['method'] for e in h[str(species)]['entries'] if e.get('huntingTechnique')=='xy-friend-safari')
print('Verified Bug, Dragon and Ghost slots, Vivillon pattern and Pumpkaboo size requirements')

assert all(e.get('friendSafariAssignments') for guide in h.values() for e in guide['entries'] if e.get('huntingTechnique')=='xy-friend-safari')
for e in h['303']['entries']:
 if e.get('huntingTechnique')=='xy-friend-safari':assert e['friendSafariAssignments']==[{'type':'Steel','slot':1},{'type':'Fairy','slot':2}]
print('Verified all 18 Safari types have slot assignments for every roster species')
