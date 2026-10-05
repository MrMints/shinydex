"""Independently match radar-enabled encounter rows to rendered species/game locations."""

# Audit tools resolve shared inputs from the repository, regardless of launch directory.
import os as _audit_os
import sys as _audit_sys
from pathlib import Path as _AuditPath
_audit_root = _AuditPath(__file__).resolve().parents[1]
_audit_sys.path.insert(0, str(_audit_root))
_audit_os.chdir(_audit_root)

import csv,hashlib,json
from collections import defaultdict
from pathlib import Path
def rows(name):
 with open(name+'.csv',encoding='utf-8-sig') as f:return list(csv.DictReader(f))
conditions={r['id']:r['identifier'] for r in rows('encounter_condition_values')}
enabled={r['encounter_id'] for r in rows('encounter_condition_value_map') if conditions[r['encounter_condition_value_id']]=='radar-on'}
pokemon={r['id']:r for r in rows('pokemon')};slots={r['id']:r['encounter_method_id'] for r in rows('encounter_slots')}
areas={r['id']:r['location_id'] for r in rows('location_areas')};locations={r['id']:r['identifier'] for r in rows('locations')}
area_names={r['id']:r['identifier'] for r in rows('location_areas')}
games={'12':'Pokémon Diamond','13':'Pokémon Pearl','14':'Pokémon Platinum'}
expected=defaultdict(set)
for r in rows('encounters'):
 if r['id'] not in enabled or r['version_id'] not in games:continue
 p=pokemon[r['pokemon_id']]
 if p['is_default']!='1':continue
 assert slots[r['encounter_slot_id']]=='1',r # Walk encounter, not fishing/gift/static.
 label=locations[areas[r['location_area_id']]].replace('-',' ').title()
 area=area_names[r['location_area_id']]
 if area:label+=' · '+area.replace('-',' ').title()
 expected[(int(p['species_id']),games[r['version_id']])].add(label)
actual={}
for key,g in json.loads(Path('hunts.json').read_text()).items():
 for e in g['entries']:
  if e.get('huntingTechnique')!='sinnoh-radar-exclusive':continue
  pair=(int(key),e['game']);assert pair not in actual
  actual[pair]=set(e['locations'])
  assert e['status']=='Huntable' and '50 steps' in e['method'] and 'National Pokédex' in e['method']
assert actual==expected
for species in (128,241):
 for game in games.values():
  assert any('South Towards Solaceon Town' in loc for loc in actual[(species,game)] if loc.startswith('Sinnoh Route 210')), (species,game)
for species in (352,371):
 assert any('West Towards Celestic Town' in loc for pair,locs in actual.items() if pair[0]==species for loc in locs if loc.startswith('Sinnoh Route 210')),species
approved=[]
approved_locations={}
approved_route_numbers=[*range(201,210),*range(211,219),221,222,*range(224,231)]
mapped_conditions=defaultdict(set)
for condition in rows('encounter_condition_value_map'):
 mapped_conditions[condition['encounter_id']].add(conditions[condition['encounter_condition_value_id']])
expected_ordinary=defaultdict(set)
for encounter in rows('encounters'):
 if encounter['version_id'] not in games or encounter['id'] in enabled:continue
 if slots[encounter['encounter_slot_id']]!='1':continue
 route=locations[areas[encounter['location_area_id']]].replace('sinnoh-sea-route-','sinnoh-route-')
 if not (route=='mt-coronet' and area_names[encounter['location_area_id']] in {'exterior-snowfall','exterior-blizzard'}) and not (route=='stark-mountain' and area_names[encounter['location_area_id']]=='') and route not in {'sinnoh-route-'+str(number) for number in approved_route_numbers}|{'eterna-forest','valley-windworks','fuego-ironworks','trophy-garden','sendoff-spring','valor-lakefront','acuity-lakefront','lake-verity','lake-valor','lake-acuity'}:continue
 p=pokemon[encounter['pokemon_id']]
 if p['is_default']!='1':continue
 label=route.replace('-',' ').title()
 area=area_names[encounter['location_area_id']]
 if area:label+=' · '+area.replace('-',' ').title()
 required=sorted(mapped_conditions[encounter['id']]-{'radar-off','swarm-no','slot2-none'})
 if required:label+=' · Encounter conditions: '+', '.join(value.replace('-',' ') for value in required)
 expected_ordinary[(int(p['species_id']),games[encounter['version_id']])].add(label)
route201=[]
for key,g in json.loads(Path('hunts.json').read_text()).items():
 for e in g['entries']:
  if e.get('huntingTechnique')!='sinnoh-radar-verified-route-grass':continue
  assert e['status']=='Huntable'
  pair=(int(key),e['game'])
  assert pair not in approved_locations,('duplicate ordinary radar entry',pair)
  approved_locations[pair]=set(e['locations'])
  assert len(e['locations'])==len(approved_locations[pair]),('duplicate location',pair)
  expected_sources={'https://bulbapedia.bulbagarden.net/wiki/'+loc.split(' · ')[0].replace(' ','_')+'#Generation_IV' for loc in e['locations']}
  assert set(e['sourceReferences'])==expected_sources,('incorrect route references',pair)
  assert all(loc.split(' · ')[0] in ({'Sinnoh Route '+str(number) for number in approved_route_numbers}|{'Eterna Forest','Valley Windworks','Fuego Ironworks','Trophy Garden','Sendoff Spring','Valor Lakefront','Acuity Lakefront','Lake Verity','Lake Valor','Lake Acuity','Stark Mountain','Mt Coronet'}) for loc in e['locations'])
  loc201=[loc for loc in e['locations'] if loc.split(' · ')[0]=='Sinnoh Route 201']
  if loc201:
   assert int(key) in {84,58,396,399,401},(key,e)
   if int(key)==401:assert e['game']=='Pokémon Platinum'
   if int(key)==84:assert all('swarm yes' in loc for loc in loc201)
   if int(key)==58:assert all('slot2 firered' in loc for loc in loc201)
   route201.append((int(key),e['game']))
  approved.append((int(key),e['game']))
assert len(route201)==13,route201
assert approved_locations==expected_ordinary,'Approved radar species, games, areas or encounter conditions differ from the encounter snapshot'
for name,count in [('Valor Lakefront',17),('Acuity Lakefront',21)]:
 assert sum(any(loc.startswith(name) for loc in locs) for locs in approved_locations.values())==count,(name,count)
for guide in json.loads(Path('hunts.json').read_text()).values():
 for entry in guide['entries']:
  if entry.get('huntingTechnique')=='sinnoh-radar-verified-route-grass':
   assert 'exact ordinary encounter patch assignments still need' not in entry['method']
mountain_locations={location for locations in approved_locations.values() for location in locations if location.startswith('Mt Coronet')}
assert mountain_locations,'Mt. Coronet exterior coverage is missing'
assert all(location.split(' · ')[1] in {'Exterior Snowfall','Exterior Blizzard'} for location in mountain_locations),mountain_locations
stark_locations={location for locations in approved_locations.values() for location in locations if location.startswith('Stark Mountain')}
assert stark_locations,'Stark Mountain exterior coverage is missing'
assert all('Entrance' not in location and 'Inside' not in location and 'Heatran' not in location for location in stark_locations),stark_locations
for excluded in ['Great Marsh','Old Chateau','Turnback Cave','Iron Island','Lost Tower','Snowpoint Temple','Oreburgh Mine','Oreburgh Gate','Wayward Cave','Solaceon Ruins','Ravaged Path']:
 assert not any(location.startswith(excluded) for locations in approved_locations.values() for location in locations),excluded
assert any('Sinnoh_Route_205' in reference for g in json.loads(Path('hunts.json').read_text()).values() for e in g['entries'] if e.get('huntingTechnique')=='sinnoh-radar-verified-route-grass' for reference in e['sourceReferences'])
print('Verified',len(approved),'ordinary-grass species/game routes on',len(approved_route_numbers),'approved routes; cave and water locations excluded')
snapshot=json.loads(Path('audit/encounter-condition-provenance.json').read_text())
for item in snapshot['files']:
 assert hashlib.sha256(Path(item['file']).read_bytes()).hexdigest()==item['sha256']
print('Verified',len(actual),'explicit radar species/game routes, locations, walk methods and snapshot hashes; ordinary-grass coverage remains incomplete')
