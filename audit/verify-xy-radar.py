"""Check every generated flower-bed route against the recorded encounter tables."""

# Audit tools resolve shared inputs from the repository, regardless of launch directory.
import os as _audit_os
import sys as _audit_sys
from pathlib import Path as _AuditPath
_audit_root = _AuditPath(__file__).resolve().parents[1]
_audit_sys.path.insert(0, str(_audit_root))
_audit_os.chdir(_audit_root)

import csv,json
from collections import defaultdict
from pathlib import Path
def rows(name):
 with open(name+'.csv',encoding='utf-8-sig') as f:return list(csv.DictReader(f))
slots={row['id']:row['encounter_method_id'] for row in rows('encounter_slots')}
methods={row['id']:row['identifier'] for row in rows('encounter_methods')}
areas={row['id']:row['location_id'] for row in rows('location_areas')}
locations={row['id']:row['identifier'] for row in rows('locations')}
pokemon={row['id']:row for row in rows('pokemon')}
games={'23':'Pokémon X','24':'Pokémon Y'}
expected=defaultdict(set)
for encounter in rows('encounters'):
 if encounter['version_id'] not in games:continue
 method=methods[slots[encounter['encounter_slot_id']]]
 if method not in {'yellow-flowers','red-flowers','purple-flowers'}:continue
 p=pokemon[encounter['pokemon_id']]
 if p['is_default']!='1':continue
 place=locations[areas[encounter['location_area_id']]]
 assert place!='friend-safari'
 expected[(int(p['species_id']),games[encounter['version_id']])].add(place.replace('-',' ').title()+' · '+method.replace('-',' ').title())
actual={}
for key,guide in json.loads(Path('hunts.json').read_text(encoding='utf-8')).items():
 for entry in guide['entries']:
  if entry.get('huntingTechnique')!='xy-radar-flower-beds':continue
  pair=(int(key),entry['game'])
  assert pair not in actual,pair
  actual[pair]=set(entry['locations'])
  assert len(actual[pair])==len(entry['locations'])
  assert entry['status']=='Huntable'
  assert all(text in entry['method'] for text in ['2F','Hall of Fame','D-pad','50 steps','hordes','Friend Safari','Flower color'])
  assert entry['source']=='https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9_Radar'
  assert all(text in entry['method'] for text in ['chain of 40','1/8100','Poké Radar Chain!','disguised','Honey','hatching an Egg','all shaking patches'])
assert actual==expected,'X/Y radar species, games, locations or flower colors differ from the encounter snapshot'
assert len(actual)==168,len(actual)
assert {location.split(' · ')[1] for locations in actual.values() for location in locations}=={'Yellow Flowers','Red Flowers','Purple Flowers'}
print('Verified 168 X/Y flower-bed radar species/game entries and every location/color; grass coverage remains incomplete')
grass={}
for key,guide in json.loads(Path('hunts.json').read_text(encoding='utf-8')).items():
 for entry in guide['entries']:
  if entry.get('huntingTechnique')!='xy-radar-verified-grass':continue
  pair=(int(key),entry['game'])
  assert pair not in grass,pair
  grass[pair]=set(entry['locations'])
  assert entry['status']=='Huntable'
  source_map={**{'Kalos Route '+str(n):'Kalos_Route_'+str(n) for n in [5,7,8,10,11,12,14,15,18,20,22]},'Azure Bay':'Azure_Bay','Kalos Route 2':'Kalos_Route_2','Kalos Route 3':'Kalos_Route_3','Santalune Forest':'Santalune_Forest'}
  assert entry['sourceReferences']==sorted({'https://bulbapedia.bulbagarden.net/wiki/'+source_map[place.split(' · ')[0]] for place in entry['locations']})
  if int(key)==16 and any(place.startswith('Kalos Route 2 ·') for place in entry['locations']):assert 'scripted first Pidgey encounter on Route 2 is Shiny Locked' in entry['method']
  assert 'ordinary grass patches' in entry['method'] and 'Flower color determines' not in entry['method']
  assert all(text in entry['method'] for text in ['chain of 40','1/8100','Poké Radar Chain!','disguised','Honey','hatching an Egg','all shaking patches'])
grass_expected=defaultdict(set)
for encounter in rows('encounters'):
 if encounter['version_id'] not in games:continue
 place=locations[areas[encounter['location_area_id']]]
 if place not in {'azure-bay','kalos-route-2','kalos-route-3','santalune-forest','kalos-route-5','kalos-route-7','kalos-route-8','kalos-route-10','kalos-route-11','kalos-route-12','kalos-route-14','kalos-route-15','kalos-route-18','kalos-route-20','kalos-route-22'} or methods[slots[encounter['encounter_slot_id']]]!='walk':continue
 p=pokemon[encounter['pokemon_id']]
 if p['is_default']!='1':continue
 grass_expected[(int(p['species_id']),games[encounter['version_id']])].add(place.replace('-',' ').title()+' · Walk')
assert grass==grass_expected
# Victory Road's walk snapshot is the cave table, not an outdoor grass table.
victory=defaultdict(set)
for encounter in rows('encounters'):
 if encounter['version_id'] not in games:continue
 if locations[areas[encounter['location_area_id']]]!='kalos-victory-road':continue
 if methods[slots[encounter['encounter_slot_id']]]!='walk':continue
 victory[encounter['version_id']].add(int(pokemon[encounter['pokemon_id']]['species_id']))
assert dict(victory)=={version:{75,93,108,533,621,634} for version in games}
assert not any('Victory Road' in place for places in grass.values() for place in places)
for cave,roster in {'connecting-cave':{41,293,307,610},'frost-cavern':{93,124,221,614,615,712},'glittering-cave':{66,95,104,111,115,303,337,338},'reflection-cave':{122,202,302,433,524,577,703},'lost-hotel':{82,101,607,624,707}}.items():
 observed=defaultdict(set)
 for encounter in rows('encounters'):
  if encounter['version_id'] not in games:continue
  if locations[areas[encounter['location_area_id']]]!=cave:continue
  if methods[slots[encounter['encounter_slot_id']]]!='walk':continue
  observed[encounter['version_id']].add(int(pokemon[encounter['pokemon_id']]['species_id']))
 assert dict(observed)=={version:roster for version in games},cave
 assert not any(cave.replace('-',' ').title() in place for places in grass.values() for place in places)
# Independently transcribed grass rosters, including version exclusives.
rosters={
 'Kalos Route 20':{game:{39,164,571,575,591,709} for game in games.values()},
 'Kalos Route 22':{game:{54,83,206,298,399,447,659,667} for game in games.values()},
 'Kalos Route 14':{game:{70,93,195,451,455,588,616,704} for game in games.values()},
 'Kalos Route 15':{games['23']:{262,451,505,590,624,707},games['24']:{451,505,510,590,624,707}},
 'Kalos Route 18':{games['23']:{28,75,305,324,533,631,632},games['24']:{28,75,247,324,533,631,632}},
 'Kalos Route 11':{games['23']:{30,33,297,397,433,434,539,702},games['24']:{30,33,297,397,433,434,538,702}},
 'Kalos Route 12':{games['23']:{79,102,127,128,241,417,441},games['24']:{79,102,128,214,241,417,441}},
 'Kalos Route 5':{games['23']:{63,84,311,316,659,672,674,676},games['24']:{63,84,312,316,659,672,674,676}},
 'Kalos Route 7':{games['23']:{235,313,314,315,453,580,669,684},games['24']:{235,313,314,315,453,580,669,682}},
 'Kalos Route 8':{games['23']:{325,335,359,371,425,619,686},games['24']:{325,336,359,371,425,619,686}},
 'Kalos Route 10':{games['23']:{133,209,228,561,587,622,701},games['24']:{133,209,309,561,587,622,701}},
 'Azure Bay':{game:{79,102,441,686} for game in games.values()},
 'Kalos Route 3':{game:{16,25,206,298,399,412,659,661} for game in games.values()},
 'Kalos Route 2':{'Pokémon X':{13,16,263,659,661,664},'Pokémon Y':{10,16,263,659,661,664}},
 'Santalune Forest':{'Pokémon X':{10,13,14,25,511,513,515,661,664},'Pokémon Y':{10,11,13,25,511,513,515,661,664}},
}
for place,versions in rosters.items():
 for game,roster in versions.items():
  assert {species for (species,version),places in grass.items() if version==game and place+' · Walk' in places}==roster,(place,game)
print(f'Verified {len(grass)} ordinary-grass radar species/game entries against encounter tables and fifteen Bulbapedia rosters')

terminus=defaultdict(set)
for encounter in rows('encounters'):
 if encounter['version_id'] not in games:continue
 if locations[areas[encounter['location_area_id']]]!='terminus-cave' or methods[slots[encounter['encounter_slot_id']]]!='walk':continue
 terminus[encounter['version_id']].add(int(pokemon[encounter['pokemon_id']]['species_id']))
assert dict(terminus)=={'23':{28,75,305,632},'24':{28,75,247,632}}
assert not any('Terminus Cave' in place for places in grass.values() for place in places)
