"""Verify DexNav merges, with independent Shoal Cave tide regressions."""

# Audit tools resolve shared inputs from the repository, regardless of launch directory.
import os as _audit_os
import sys as _audit_sys
from pathlib import Path as _AuditPath
_audit_root = _AuditPath(__file__).resolve().parents[1]
_audit_sys.path.insert(0, str(_audit_root))
_audit_os.chdir(_audit_root)

import json
from pathlib import Path
from dexnav_hunts import routes,GAMES
h=json.loads(Path('hunts.json').read_text())
actual={}
for key,guide in h.items():
 for e in guide['entries']:
  if e.get('huntingTechnique')=='oras-dexnav':
   pair=(int(key),e['game']);assert pair not in actual
   actual[pair]=e
assert set(actual)==set(routes())
for game in GAMES.values():
 for species in (41,42,363,364,361,72,73,129,320,87,225,613):
  e=actual[(species,game)]
  loc=[s for s in e['locations'] if s.startswith('Shoal Cave')]
  assert len(loc)==1
  if species==361:assert 'low tide only' in loc[0] and 'outside ice room' in loc[0]
  if species in (72,73,129,320):assert 'high tide' in loc[0] and 'Surf required' in loc[0]
  if species in (87,225,613):assert 'after defeating or capturing Groudon/Kyogre' in loc[0]
  assert 'https://bulbapedia.bulbagarden.net/wiki/Shoal_Cave#Generation_VI' in e['sourceReferences']
print('Verified',len(actual),'DexNav routes, including 24 species/game Shoal Cave location assignments')

# Independently recorded Bulbapedia hidden-only rosters, both games.
for route,species_list in {101:[506,540,570],102:[506,535,574],103:[422,441,506],104:[441,519,540]}.items():
 for game in GAMES.values():
  for species in species_list:
   e=actual[(species,game)]
   assert any(l.startswith(f'Route {route} ') and 'after defeating or capturing Groudon/Kyogre' in l for l in e['locations'])
   assert f'https://bulbapedia.bulbagarden.net/wiki/Hoenn_Route_{route}#Generation_VI' in e['sourceReferences']
for game,form in [(GAMES['25'],'West Sea form'),(GAMES['26'],'East Sea form')]:
 assert any('Route 103 ' in l and form in l for l in actual[(422,game)]['locations'])
print('Verified hidden-only Route 101-104 rosters and version-specific Shellos forms')

for route,species_list in {112:[77,236],113:[559,626,707],116:[133,519,595]}.items():
 for game in GAMES.values():
  for species in species_list+([538 if game==GAMES['25'] else 539] if route==112 else []):
   e=actual[(species,game)]
   assert any(l.startswith(f'Route {route} ') and 'after defeating or capturing Groudon/Kyogre' in l for l in e['locations'])
   assert f'https://bulbapedia.bulbagarden.net/wiki/Hoenn_Route_{route}#Generation_VI' in e['sourceReferences']
for species,game in [(538,GAMES['26']),(539,GAMES['25'])]:
 assert not any(l.startswith('Route 112 ') for l in actual.get((species,game),{}).get('locations',[]))
print('Verified Routes 112, 113, 116, including Throh/Sawk version exclusivity')

for route,species_list in {111:[443,551,557],117:[19,535,585],118:[20,190,404]}.items():
 for game in GAMES.values():
  for species in species_list:
   e=actual[(species,game)]
   loc=[l for l in e['locations'] if l.startswith(f'Route {route} ')][0]
   assert 'after defeating or capturing Groudon/Kyogre' in loc
   assert f'https://bulbapedia.bulbagarden.net/wiki/Hoenn_Route_{route}#Generation_VI' in e['sourceReferences']
   if route==111:assert 'deep-sand' in loc and 'Go-Goggles required' in loc
   if route==118:assert 'long-grass' in loc
   if species==585:assert 'Spring Form only' in loc
print('Verified Routes 111, 117, 118, desert access and Deerling form')

for route,species_list in {114:[200,451,535],115:[35,200,519],121:[97,190,605]}.items():
 for game in GAMES.values():
  for species in species_list:
   e=actual[(species,game)]
   loc=[l for l in e['locations'] if l.startswith(f'Route {route} ')][0]
   assert 'after defeating or capturing Groudon/Kyogre' in loc
   assert f'https://bulbapedia.bulbagarden.net/wiki/Hoenn_Route_{route}#Generation_VI' in e['sourceReferences']
   if route==121:assert 'long-grass' in loc
print('Verified hidden-only rosters on Routes 114, 115 and 121')

for area,species_list in {'Petalburg Woods':[46,546,708],'Granite Cave':[95,532,610]}.items():
 for game in GAMES.values():
  for species in species_list:
   entry=actual[(species,game)]
   loc=[l for l in entry['locations'] if l.startswith(area+' ·')][0]
   assert 'hidden-only after defeating or capturing Groudon/Kyogre' in loc
   assert 'https://bulbapedia.bulbagarden.net/wiki/'+area.replace(' ','_')+'#Generation_VI' in entry['sourceReferences']
   if area=='Granite Cave':assert '1F, B1F and B2F' in loc
print('Verified hidden-only Petalburg Woods and Granite Cave rosters')

for area,species_list in {'Fiery Path':[50,236,524],'Jagged Pass':[56,77,236],'Mt. Pyre':[58,436,605]}.items():
 for game in GAMES.values():
  for species in species_list:
   entry=actual[(species,game)]
   loc=[l for l in entry['locations'] if l.startswith(area+' ·')][0]
   assert 'hidden-only after defeating or capturing Groudon/Kyogre' in loc
   assert 'https://bulbapedia.bulbagarden.net/wiki/'+area.replace(' ','_')+'#Generation_VI' in entry['sourceReferences']
   if area=='Mt. Pyre':assert 'exterior and summit grass' in loc
print('Verified Fiery Path, Jagged Pass and exterior/summit Mt. Pyre hidden rosters')

for game in GAMES.values():
 for species in (35,621,633):
  entry=actual[(species,game)]
  assert any(l.startswith('Meteor Falls · 1F 1R cave floor') and 'after defeating or capturing Groudon/Kyogre' in l for l in entry['locations'])
  assert 'https://bulbapedia.bulbagarden.net/wiki/Meteor_Falls#Generation_VI' in entry['sourceReferences']
 for species in (98,592,690 if game==GAMES['25'] else 692):
  entry=actual[(species,game)]
  assert any(l.startswith('Route 105 · hidden-only water') and 'Surf required' in l for l in entry['locations'])
  assert 'https://bulbapedia.bulbagarden.net/wiki/Hoenn_Route_105#Generation_VI' in entry['sourceReferences']
for species,game in [(690,GAMES['26']),(692,GAMES['25'])]:
 assert not any(l.startswith('Route 105 ') for l in actual.get((species,game),{}).get('locations',[]))
print('Verified Meteor Falls first room and Route 105 water/version restrictions')

for route in (106,107,108,109):
 for game in GAMES.values():
  for species in (98,592,690 if game==GAMES['25'] else 692):
   entry=actual[(species,game)]
   assert any(l.startswith(f'Route {route} · hidden-only water') and 'Surf required' in l and 'after defeating or capturing Groudon/Kyogre' in l for l in entry['locations'])
   assert f'https://bulbapedia.bulbagarden.net/wiki/Hoenn_Route_{route}#Generation_VI' in entry['sourceReferences']
 for species,game in [(690,GAMES['26']),(692,GAMES['25'])]:
  assert not any(l.startswith(f'Route {route} ') for l in actual.get((species,game),{}).get('locations',[]))
print('Verified water and version restrictions on Routes 106-109')

for route,species_list in {110:[422,568,441],125:[86,456,592]}.items():
 for game in GAMES.values():
  for species in species_list:
   e=actual[(species,game)]
   loc=[l for l in e['locations'] if l.startswith(f'Route {route} ')][0]
   assert 'after defeating or capturing Groudon/Kyogre' in loc
   assert f'https://bulbapedia.bulbagarden.net/wiki/Hoenn_Route_{route}#Generation_VI' in e['sourceReferences']
   if route==125:assert 'water encounters' in loc and 'Surf required' in loc
   if species==422:assert ('West Sea form' if game==GAMES['25'] else 'East Sea form') in loc
print('Verified Route 110 Shellos forms and Route 125 water hunts')

for game in GAMES.values():
 for species in (456,592,594):
  entry=actual[(species,game)]
  assert any(l.startswith('Route 122 · hidden-only water') and 'Surf required' in l and 'after defeating or capturing Groudon/Kyogre' in l for l in entry['locations'])
  assert 'https://bulbapedia.bulbagarden.net/wiki/Hoenn_Route_122#Generation_VI' in entry['sourceReferences']
print('Verified Route 122 hidden Finneon, Frillish and Alomomola hunts')

for route in (124,126,127,128,129,130,131,132,133,134):
 for game in GAMES.values():
  for species in (456,592,594):
   entry=actual[(species,game)]
   assert any(l.startswith(f'Route {route} · hidden-only water') and 'Surf required' in l and 'after defeating or capturing Groudon/Kyogre' in l for l in entry['locations'])
   assert f'https://bulbapedia.bulbagarden.net/wiki/Hoenn_Route_{route}#Generation_VI' in entry['sourceReferences']
print('Verified hidden-water rosters on Routes 124 and 126-134')

# Independent underwater rosters from the Generation VI route tables.
for route,species_list in {107:[170,171,366,369],124:[170,171,366,369],126:[170,171,366,369],128:[170,171,222,366,369],129:[170,171,366,369],130:[170,171,366,369]}.items():
 for game in GAMES.values():
  for species in species_list:
   entry=actual[(species,game)]
   location=f'Route {route} · underwater seaweed · Surf and Dive required'
   assert location in entry['locations']
   assert 'https://bulbapedia.bulbagarden.net/wiki/Hoenn_Route_'+str(route)+'#Generation_VI' in entry['sourceReferences']
   assert 'after defeating' not in location
print('Verified six underwater seaweed route rosters and Dive requirements')

for game in GAMES.values():
 for species,area,terrain,access in (
  (25,1,'tall grass',''),(203,1,'long grass','Acro Bike and Surf'),
  (178,2,'tall grass',''),(202,2,'long grass','Mach Bike'),
  (111,3,'tall grass','Mach Bike'),(214,3,'long grass','Acro Bike'),
  (232,4,'tall grass','Acro Bike'),(127,4,'long grass','Mach Bike and Surf'),
 ):
  entry=actual[(species,game)]
  loc=[l for l in entry['locations'] if l.startswith(f'Safari Zone · Area {area} · {terrain}')]
  assert len(loc)==1 and access in loc[0]
  assert 'https://bulbapedia.bulbagarden.net/wiki/Hoenn_Safari_Zone#Generation_VI' in entry['sourceReferences']
 for species in (14,17,427):
  locations=[l for l in actual[(species,game)]['locations'] if l.startswith('Safari Zone ·')]
  assert len(locations)==4
  assert all('after defeating or capturing Groudon/Kyogre' in l for l in locations)
 for species in (118,119,129):
  assert all('Surf required' in l for l in actual[(species,game)]['locations'] if l.startswith('Safari Zone ·'))
print('Verified Safari Zone grass restrictions, bike access, story unlock and water searches')

for game in GAMES.values():
 for area,location,species_list in (
  ('Fiery Path','Fiery Path · cave floor',(66,88,109,218,322,324)),
  ('Granite Cave','Granite Cave · 1F cave floor',(41,63,74,296)),
  ('Petalburg Woods','Petalburg Woods · tall grass',(263,265,266,268,276,285,287)),
 ):
  for species in species_list:
   entry=actual[(species,game)]
   assert location in entry['locations']
   assert 'https://bulbapedia.bulbagarden.net/wiki/'+area.replace(' ','_')+'#Generation_VI' in entry['sourceReferences']
print('Verified native Fiery Path, Granite Cave 1F and Petalburg Woods rosters')

for game in GAMES.values():
 for species in (27,328,331,343):
  assert 'Route 111 · desert deep sand · Go-Goggles required' in actual[(species,game)]['locations']
 for species in (183,184,283,284,118,129,339):
  entry=actual[(species,game)]
  assert 'Route 111 · southern pond · Surf required to approach searched Pokémon' in entry['locations']
  assert 'https://bulbapedia.bulbagarden.net/wiki/Hoenn_Route_111#Generation_VI' in entry['sourceReferences']
print('Verified Route 111 native desert and southern pond hunts')

for game in GAMES.values():
 for species in (313,314):
  assert 'Route 117 · tall grass' in actual[(species,game)]['locations']
 for species in (341,342):
  assert 'Route 117 · pond · Surf required to approach searched Pokémon' in actual[(species,game)]['locations']
 assert 'Route 110 · tall grass' in actual[(316,game)]['locations']
 assert 'Route 115 · northern tall grass · Surf required to reach grass' in actual[(39,game)]['locations']
 assert 'Route 115 · water · Surf required to approach searched Pokémon' in actual[(279,game)]['locations']
print('Verified Route 117 bugs/pond species, Route 110 Gulpin and Route 115 access')

for game in GAMES.values():
 for species in (35,200,519):
  locations=[l for l in actual[(species,game)]['locations'] if l.startswith('Route 115 · hidden-only')]
  assert len(locations)==1 and 'Surf required to reach grass' in locations[0]
for entry in actual.values():
 assert len(entry['sourceReferences'])==len(set(entry['sourceReferences']))
print('Verified Route 115 hidden-only access and deduplicated references')

for game in GAMES.values():
 for species in (274 if game==GAMES['25'] else 271,335 if game==GAMES['25'] else 336):
  assert 'Route 114 · tall grass' in actual[(species,game)]['locations']
 for species in (271 if game==GAMES['25'] else 274,336 if game==GAMES['25'] else 335):
  assert not any(l.startswith('Route 114 ·') for l in actual.get((species,game),{}).get('locations',[]))
 assert 'Mt. Pyre · interior 1F-4F · Surf required to reach mountain entrance' in actual[(355,game)]['locations']
 assert 'Mt. Pyre · summit grass · Surf required to reach mountain entrance' in actual[(358,game)]['locations']
 assert not any(l.startswith('Mt. Pyre · interior') for l in actual[(358,game)]['locations'])
print('Verified Route 114 version exclusives and Mt. Pyre Duskull/Chimecho locations')

for game in GAMES.values():
 for species in (318,319):
  assert 'Route 118 · inlet water · Surf required to approach searched Pokémon' in actual[(species,game)]['locations']
 for species in (116,117):
  assert 'Route 130 · surface water · Surf required to approach searched Pokémon' in actual[(species,game)]['locations']
 assert 'Route 118 · eastern tall grass · Surf required to cross inlet' in actual[(264,game)]['locations']
 locations=[l for l in actual[(130,game)]['locations'] if l.startswith('Sootopolis City · lake')]
 assert len(locations)==1 and 'Surf required' in locations[0] and 'Dive on Route 126' in locations[0]
 assert 'https://bulbapedia.bulbagarden.net/wiki/Sootopolis_City#Generation_VI' in actual[(130,game)]['sourceReferences']
print('Verified Route 118, Route 130 and Sootopolis water hunts and access')

for game in GAMES.values():
 for species in (72,73,129,223,224,226,279,458):
  entry=actual[(species,game)]
  locations=[l for l in entry['locations'] if l.startswith('Battle Resort · water')]
  assert len(locations)==1
  assert all(word in locations[0] for word in ('Surf required','Delta Episode','S.S. Ticket','Norman','S.S. Tidal'))
  assert 'https://bulbapedia.bulbagarden.net/wiki/Battle_Resort#Pok%C3%A9mon' in entry['sourceReferences']
print('Verified all eight Battle Resort water species and postgame access')

for game in GAMES.values():
 for species in (72,278,279,129,320,120):
  entry=actual[(species,game)]
  assert 'Lilycove City · coastal water · Surf required to approach searched Pokémon' in entry['locations']
  assert 'https://bulbapedia.bulbagarden.net/wiki/Lilycove_City#Generation_VI' in entry['sourceReferences']
print('Verified Lilycove coastal roster including Staryu searching')

for game in GAMES.values():
 for species in (42,168,333,344,303 if game==GAMES['25'] else 302):
  entry=actual[(species,game)]
  locations=[l for l in entry['locations'] if l.startswith('Sky Pillar ·')]
  assert len(locations)==1 and all(s in locations[0] for s in ('1F-5F','Delta Episode','Wallace','defeat him'))
  assert 'https://bulbapedia.bulbagarden.net/wiki/Sky_Pillar#Generation_VI' in entry['sourceReferences']
 excluded=302 if game==GAMES['25'] else 303
 assert not any(l.startswith('Sky Pillar ·') for l in actual.get((excluded,game),{}).get('locations',[]))
 assert not any(l.startswith('Sky Pillar') for l in actual.get((384,game),{}).get('locations',[]))
print('Verified Sky Pillar ordinary searches, version exclusivity and story access')

for game in GAMES.values():
 for species in (42,294,297,305,308,303 if game==GAMES['25'] else 302):
  entry=actual[(species,game)]
  locations=[l for l in entry['locations'] if l.startswith('Victory Road · entrance, 1F and B1F cave floors')]
  assert len(locations)==1 and 'Waterfall' in locations[0] and 'Strength' in locations[0]
  assert 'https://bulbapedia.bulbagarden.net/wiki/Victory_Road_(Hoenn)#Generation_VI' in entry['sourceReferences']
print('Verified Victory Road native cave roster and traversal requirements')

for game in GAMES.values():
 star=338 if game==GAMES['25'] else 337
 assert 'Meteor Falls · 1F 1R cave floor' in actual[(star,game)]['locations']
 wrong=337 if game==GAMES['25'] else 338
 assert not any(l.startswith('Meteor Falls ·') for l in actual.get((wrong,game),{}).get('locations',[]))
 assert any(l.startswith('Meteor Falls · 1F 2R and B1F 1R water') and 'Waterfall required' in l for l in actual[(340,game)]['locations'])
 for species in (357,359):assert 'Route 120 · eastern long grass' in actual[(species,game)]['locations']
 feebas=[l for l in actual[(349,game)]['locations'] if l.startswith('Route 119 · river water')]
 assert len(feebas)==1 and 'first own Feebas' in feebas[0] and 'daytime' in feebas[0] and 'nighttime' in feebas[0]
 assert any(l.startswith('Route 128 · surface water · Surf required') for l in actual[(370,game)]['locations'])
print('Verified remaining Meteor Falls, Route 120, Feebas and Luvdisc candidates')

for game in GAMES.values():
 for species in (261,263,265):
  assert any(l.startswith('Route 101 · tall grass') and 'receive DexNav' in l for l in actual[(species,game)]['locations'])
 for species in (261,263,278):assert 'Route 103 · western tall grass' in actual[(species,game)]['locations']
 for species in (72,278,279,129,320):
  assert 'Route 103 · river water · Surf required to approach searched Pokémon' in actual[(species,game)]['locations']
print('Verified Route 101 DexNav access and Route 103 native grass/water rosters')

for game in GAMES.values():
 for section in ('north','south'):
  for species in (263,265,276,278):
   assert f'Route 104 · {section} section tall grass' in actual[(species,game)]['locations']
  for species in (278,279,129):
   assert f'Route 104 · {section} section water · Surf required to approach searched Pokémon' in actual[(species,game)]['locations']
  for species in (441,519,540):
   assert f'Route 104 · {section} section tall grass · hidden-only after defeating or capturing Groudon/Kyogre' in actual[(species,game)]['locations']
print('Verified both Route 104 sections, water access and hidden-only rosters')

for game in GAMES.values():
 for species in (72,278,279,129,320):
  entry=actual[(species,game)]
  assert 'Route 105 · surface water · Surf required to approach searched Pokémon' in entry['locations']
  assert 'https://bulbapedia.bulbagarden.net/wiki/Hoenn_Route_105#Generation_VI' in entry['sourceReferences']
print('Verified Route 105 native water searches and Surf requirement')

for game in GAMES.values():
 for route in (106,107,108,109):
  for species in (72,278,279,129,320):
   entry=actual[(species,game)]
   assert f'Route {route} · surface water · Surf required to approach searched Pokémon' in entry['locations']
   assert f'https://bulbapedia.bulbagarden.net/wiki/Hoenn_Route_{route}#Generation_VI' in entry['sourceReferences']
print('Verified Route 106-109 native surface searches separately from underwater targets')

# Independent expected native rosters from Bulbapedia's Generation VI tables.
# Keep these separate from the post-Groudon/Kyogre foreign-species unlock.
for game in GAMES.values():
 for route,roster,terrain in ((113,(27,227,327),'ash-covered grass'),(116,(263,276,290,293,300),'tall grass')):
  for species in roster:
   entry=actual[(species,game)]
   assert f'Route {route} · {terrain}' in entry['locations']
   assert f'https://bulbapedia.bulbagarden.net/wiki/Hoenn_Route_{route}#Generation_VI' in entry['sourceReferences']
  # Emerald's Abra/Poochyena grass roster must not leak into ORAS Route 116.
 for species in (63,261):
  assert not any(l.startswith('Route 116 · tall grass') for l in actual.get((species,game),{}).get('locations',[]))
print('Verified Route 113 and 116 native rosters separately from hidden-only encounters')

for game in GAMES.values():
 for city in ('Dewford Town','Slateport City'):
  for species in (72,278,279,129,320):
   entry=actual[(species,game)]
   assert f'{city} · coastal water · Surf required to approach searched Pokémon' in entry['locations']
   assert 'https://bulbapedia.bulbagarden.net/wiki/'+city.replace(' ','_')+'#Generation_VI' in entry['sourceReferences']
 for species in (183,184,283,284,118,129,341):
  entry=actual[(species,game)]
  locations=[l for l in entry['locations'] if l.startswith('Petalburg City · ponds')]
  assert len(locations)==1 and all(s in locations[0] for s in ('Surf required','HM03','Norman','Balance Badge'))
  assert 'https://bulbapedia.bulbagarden.net/wiki/Petalburg_City#Generation_VI' in entry['sourceReferences']
print('Verified Dewford, Slateport and Petalburg native water searches and Surf access')

# Source-reviewed native city and Route 102 rosters. Expectations are separate
# from the builder, including exclusions that catch version/generation leaks.
for game in GAMES.values():
 for city,roster,terrain in (
  ('Pacifidlog Town',(72,73,129,279,320),'surrounding sea'),
  ('Mossdeep City',(72,73,129,279,320),'coastal water'),
  ('Ever Grande City',(72,73,129,222,279,320,370),'coastal water'),
 ):
  for species in roster:
   entry=actual[(species,game)]
   labels=[l for l in entry['locations'] if l.startswith(city+' · '+terrain)]
   assert len(labels)==1 and 'Surf required' in labels[0]
   assert 'https://bulbapedia.bulbagarden.net/wiki/'+city.replace(' ','_')+'#Generation_VI' in entry['sourceReferences']
 for species in (261,263,265,280,283,273 if game==GAMES['25'] else 270):
  entry=actual[(species,game)]
  assert 'Route 102 · tall grass' in entry['locations']
  assert 'https://bulbapedia.bulbagarden.net/wiki/Hoenn_Route_102#Generation_VI' in entry['sourceReferences']
 excluded=270 if game==GAMES['25'] else 273
 assert not any(l.startswith('Route 102 · tall grass') for l in actual.get((excluded,game),{}).get('locations',[]))
 for species in (118,129,183,184,283,284,341):
  assert 'Route 102 · pond · Surf required to approach searched Pokémon' in actual[(species,game)]['locations']
 # Corsola in Pacifidlog is an NPC trade, not a wild DexNav search.
 assert not any(l.startswith('Pacifidlog Town ·') for l in actual[(222,game)]['locations'])
print('Verified Pacifidlog, Mossdeep, Ever Grande and version-specific Route 102 searches')

for game in GAMES.values():
 for route,roster,terrain in (
  (110,(72,278,279,129,320),'water beneath the Cycling Road'),
  (119,(44,264,352,357,43),'long grass'),
  (119,(72,278,279,129,318,319),'river water'),
  (120,(44,264,352,357,359,43,183),'western long grass'),
  (120,(184,283,284,72,129,339),'eastern ponds'),
  (120,(184,283,284,118,129,339),'western pond'),
  (121,(44,264,279,352,353,278),'grass and long grass'),
 ):
  for species in roster:
   entry=actual[(species,game)]
   labels=[l for l in entry['locations'] if l.startswith(f'Route {route} · {terrain}')]
   assert len(labels)==1
   if route in (110,119) or terrain in ('eastern ponds','western pond'):
    assert 'Surf' in labels[0]
   assert f'https://bulbapedia.bulbagarden.net/wiki/Hoenn_Route_{route}#Generation_VI' in entry['sourceReferences']
 # Route 120 has different fishing species east/west; do not flatten them.
 assert not any(l.startswith('Route 120 · eastern ponds') for l in actual[(118,game)]['locations'])
 assert not any(l.startswith('Route 120 · western pond') for l in actual[(72,game)]['locations'])
print('Verified Routes 110 and 119-121 including distinct Route 120 pond rosters')

for game in GAMES.values():
 for route,roster,terrain in (
  (122,(72,278,279,129,320),'surface water'),
  (123,(44,264,279,352,353,278),'long grass'),
  (123,(183,184,283,284,118,129,341,342),'ponds'),
  (124,(72,73,279,129,320),'surface water'),
  (125,(72,73,279,129,320),'surface water'),
 ):
  for species in roster:
   entry=actual[(species,game)]
   labels=[l for l in entry['locations'] if l.startswith(f'Route {route} · {terrain}')]
   assert len(labels)==1
   if terrain!='long grass':
    assert 'Surf required' in labels[0]
   if route==124:
    assert 'Lilycove hideout' in labels[0]
   assert f'https://bulbapedia.bulbagarden.net/wiki/Hoenn_Route_{route}#Generation_VI' in entry['sourceReferences']
 # Sharpedo's Generation III fishing encounter is absent from these ORAS routes.
 for route in (122,124,125):
  assert not any(l.startswith(f'Route {route} · surface water') for l in actual[(319,game)]['locations'])
print('Verified Routes 122-125 native terrain rosters and Lilycove hideout access')

for game in GAMES.values():
 for route,roster,terrain in (
  (126,(72,73,279,129,320),'surface water'),
  (127,(72,73,279,129,320),'surface water'),
  (128,(72,73,279,129,320,222,370),'surface water'),
  (129,(72,73,279,129,320),'surface water'),
  (131,(72,73,279,129,320,116,117),'surface water'),
  (132,(72,73,279,129,320,116,117),'calm surface water'),
  (133,(72,73,279,129,320,116,117),'calm surface water'),
  (134,(72,278,279,129,320,116,117),'calm surface water'),
 ):
  for species in roster:
   entry=actual[(species,game)]
   labels=[l for l in entry['locations'] if l.startswith(f'Route {route} · {terrain}')]
   assert len(labels)==1 and 'Surf required' in labels[0]
   if route in (132,133,134):
    assert 'east-to-west' in labels[0] or 'east to west' in labels[0]
   assert f'https://bulbapedia.bulbagarden.net/wiki/Hoenn_Route_{route}#Generation_VI' in entry['sourceReferences']
  assert not any(l.startswith(f'Route {route} · {terrain}') for l in actual[(319,game)]['locations'])
 assert not any(l.startswith('Route 129 · surface water') for l in actual.get((321,game),{}).get('locations',[]))
 assert not any(l.startswith('Route 134 · calm surface water') for l in actual[(73,game)]['locations'])
print('Verified Routes 126-129 and 131-134 native water rosters and current/access distinctions')

for game in GAMES.values():
 for location,roster,terrain in (
  ('Jagged Pass',(66,322,325),'native grass'),
  ('Scorched Slab',(42,),'1F cave floor'),
  ('Scorched Slab',(41,42),'B1F-B3F cave floors'),
  ('Scorched Slab',(41,42,118,129,339),'1F and B1F water'),
  ('Cave of Origin',(41,42,303 if game==GAMES['25'] else 302),'native cave floors'),
 ):
  for species in roster:
   entry=actual[(species,game)]
   labels=[l for l in entry['locations'] if l.startswith(location+' · '+terrain)]
   assert len(labels)==1
   assert 'https://bulbapedia.bulbagarden.net/wiki/'+location.replace(' ','_')+'#Generation_VI' in entry['sourceReferences']
   if location=='Scorched Slab':
    assert 'Surf' in labels[0]
   if location=='Cave of Origin':
    assert 'Seafloor Cavern' in labels[0]
 excluded=302 if game==GAMES['25'] else 303
 assert not any(l.startswith('Cave of Origin ·') for l in actual.get((excluded,game),{}).get('locations',[]))
 for species in (118,129,339):
  assert not any(l.startswith('Scorched Slab · B1F-B3F cave floors') for l in actual[(species,game)]['locations'])
print('Verified Jagged Pass, Scorched Slab floor/water and Cave of Origin version assignments')

for game in GAMES.values():
 hideout='Team Magma Hideout' if game==GAMES['25'] else 'Team Aqua Hideout'
 wrong='Team Aqua Hideout' if game==GAMES['25'] else 'Team Magma Hideout'
 source='Magma_Hideout_(Lilycove_City)' if game==GAMES['25'] else 'Aqua_Hideout'
 for species in (72,129,320,120):
  entry=actual[(species,game)]
  labels=[l for l in entry['locations'] if l.startswith(hideout+' ·')]
  assert len(labels)==1 and 'Surf required' in labels[0] and 'submarine in Slateport' in labels[0]
  assert 'https://bulbapedia.bulbagarden.net/wiki/'+source+'#Generation_VI' in entry['sourceReferences']
  assert not any(l.startswith(wrong+' ·') for l in entry['locations'])
 for terrain,roster in (
  ('entrance water',(42,73,72,129,320)),
  ('rooms 5 and 6 water',(42,73,72,129,320)),
  ('rooms 1-9 cave floors',(42,41)),
 ):
  for species in roster:
   entry=actual[(species,game)]
   labels=[l for l in entry['locations'] if l.startswith('Seafloor Cavern · '+terrain)]
   assert len(labels)==1 and 'Surf and Dive' in labels[0]
   if terrain.startswith('rooms'):
    assert 'Strength required' in labels[0] and 'Rock Smash is optional' in labels[0]
   assert 'https://bulbapedia.bulbagarden.net/wiki/Seafloor_Cavern#Generation_VI' in entry['sourceReferences']
 # Graveler's Rock Smash encounter must not become a cave-floor DexNav search.
 assert not any(l.startswith('Seafloor Cavern ·') for l in actual.get((75,game),{}).get('locations',[]))
print('Verified version-specific Lilycove hideouts and Seafloor Cavern floor/water searches')

for game in GAMES.values():
 for location,roster,terrain,source in (
  ('Sea Mauville',(72,278,279,129,320),'exterior water','Sea_Mauville#Outside_2'),
  ('Sea Mauville',(72,129,320),'interior surface water','Sea_Mauville#Inside_2'),
  ('Sealed Chamber',(41,42,72,129,320,116),'entrance water','Sealed_Chamber#Generation_VI'),
 ):
  for species in roster:
   entry=actual[(species,game)]
   labels=[l for l in entry['locations'] if l.startswith(location+' · '+terrain)]
   assert len(labels)==1 and 'Surf' in labels[0] and 'Dive' in labels[0]
   assert 'https://bulbapedia.bulbagarden.net/wiki/'+source in entry['sourceReferences']
 for species in (278,279):
  assert not any(l.startswith('Sea Mauville · interior') for l in actual[(species,game)]['locations'])
 assert not any(l.startswith('Sealed Chamber ·') for l in actual[(117,game)]['locations'])
print('Verified Sea Mauville exterior/interior rosters and Sealed Chamber water access')

for game in GAMES.values():
 for terrain,roster in (
  ('entrance, 1F and B1F water',(42,72,73,129,320,370)),
  ('2F water',(42,118,129,339)),
 ):
  for species in roster:
   entry=actual[(species,game)]
   labels=[l for l in entry['locations'] if l.startswith('Victory Road · '+terrain)]
   assert len(labels)==1 and all(t in labels[0] for t in ('Surf','Waterfall','Rain Badge','Strength'))
   assert 'https://bulbapedia.bulbagarden.net/wiki/Victory_Road_(Hoenn)#Generation_VI' in entry['sourceReferences']
 for species in (118,339):
  assert not any(l.startswith('Victory Road · entrance, 1F and B1F water') for l in actual[(species,game)]['locations'])
 for species in (72,73,320,370):
  assert not any(l.startswith('Victory Road · 2F water') for l in actual[(species,game)]['locations'])
print('Verified Victory Road separate lower-floor and 2F water rosters')

for game in GAMES.values():
 for place,roster in (
  ('south of Route 107',(201,)),
  ('north of Fallarbor Town',(79,602)),
  ('west of Route 115',(599,602)),
  ('north of Fortree City',(95,530,599,602)),
  ('north of Route 124',(563,599)),
  ('southeast of Route 129',(95,602)),
  ('south of Route 131',(79,563,602)),
  ('north of Route 132',(132,530,602)),
 ):
  for species in roster:
   entry=actual[(species,game)]
   labels=[l for l in entry['locations'] if l.startswith('Mirage Cave · '+place+' cave floor')]
   assert len(labels)==1 and all(t in labels[0] for t in ('Eon Flute','Steven','Groudon/Kyogre','daily Mirage spot','StreetPass'))
   assert 'https://bulbapedia.bulbagarden.net/wiki/Mirage_Cave_('+place.replace(' ','_')+')#Pokémon' in entry['sourceReferences']
   assert 'https://bulbapedia.bulbagarden.net/wiki/Eon_Flute#Acquisition' in entry['sourceReferences']
 # Demo-only Loudred and Rock Smash-only Graveler are not floor searches.
 for species in (294,75):
  assert not any(l.startswith('Mirage Cave · north of Fallarbor Town') or l.startswith('Mirage Cave · west of Route 115') for l in actual.get((species,game),{}).get('locations',[]))
print('Verified eight distinct Mirage Cave floor rosters, daily access and demo/Rock Smash exclusions')

# Independently reviewed retail forest rosters. Demo and Rock Smash tables
# must not leak into searchable grass targets; matching a base name is insufficient.
for game in GAMES.values():
 for place, roster in (
  ('west of Route 105', (205,440)),
  ('south of Route 109', (191,531)),
  ('north of Route 111', (402,636)),
  ('west of Route 114', (114,191,432,548)),
  ('north of Lilycove City', (114,191,421,432)),
  ('north of Route 124', (37,114,191,432)),
  ('east of Mossdeep City', (114,191,431,572)),
  ('south of Route 132', (191,531,548)),
 ):
  prefix='Mirage Forest · '+place+' grass'
  observed={species for (species,g),entry in actual.items()
            if g==game and any(label.startswith(prefix) for label in entry['locations'])}
  assert observed==set(roster), (game,place,observed,set(roster))
  for species in roster:
   entry=actual[(species,game)]
   labels=[label for label in entry['locations'] if label.startswith(prefix)]
   assert len(labels)==1 and all(t in labels[0] for t in ('Eon Flute','Steven','Groudon/Kyogre','daily Mirage spot','StreetPass'))
   assert 'https://bulbapedia.bulbagarden.net/wiki/Mirage_Forest_('+place.replace(' ','_')+')#Pokémon' in entry['sourceReferences']
 assert any('Overcast Forme' in label for label in actual[(421,game)]['locations'] if label.startswith('Mirage Forest · north of Lilycove City'))
print('Verified eight retail Mirage Forest rosters, Cherrim form and exact demo/Rock Smash exclusions')

for game in GAMES.values():
 for location,place,roster in (
  ('Mirage Island','west of Route 104',(49,178,523,555)),
  ('Mirage Island','west of Dewford Town',(49,114,178,523)),
  ('Mirage Island','north of Route 113',(555,636)),
  ('Mirage Island','north of Route 124',(49,53,178,523)),
  ('Mirage Island','north of Route 125',(137,432)),
  ('Mirage Island','south of Pacifidlog Town',(178,531)),
  ('Mirage Island','south of Route 132',(132,517)),
  ('Mirage Island','south of Route 134',(49,178,523,556)),
  ('Mirage Mountain','west of Route 104',(205,232,234,402)),
  ('Mirage Mountain','north of Lilycove City',(205,232,402,627)),
  ('Mirage Mountain','north of Route 125',(114,440,531)),
  ('Mirage Mountain','northeast of Route 125',(205,232,402,629)),
  ('Mirage Mountain','east of Route 125',(240,555)),
  ('Mirage Mountain','southeast of Route 129',(137,178,517)),
  ('Mirage Mountain','south of Route 129',(239,523)),
  ('Mirage Mountain','south of Route 131',(203,205,232,402)),
 ):
  prefix=location+' · '+place+' grass'
  observed={species for (species,g),entry in actual.items()
            if g==game and any(label.startswith(prefix) for label in entry['locations'])}
  assert observed==set(roster), (game,place,observed,set(roster))
  for species in roster:
   entry=actual[(species,game)]
   labels=[label for label in entry['locations'] if label.startswith(prefix)]
   assert len(labels)==1 and all(t in labels[0] for t in ('Eon Flute','Steven','Groudon/Kyogre','daily Mirage spot','StreetPass'))
   assert 'https://bulbapedia.bulbagarden.net/wiki/'+location.replace(' ','_')+'_('+place.replace(' ','_')+')#Pokémon' in entry['sourceReferences']
   if species==555: assert 'Standard Mode' in labels[0]
print('Verified eight Mirage Island and eight Mirage Mountain retail grass rosters, forms and exclusions')

# Neither Rock Smash species is searchable on any Mirage Cave floor.
for game in GAMES.values():
 entry=actual[(201,game)]
 assert all(text in entry['method'] for text in ('equal encounter rates','form silhouette','guarantee a particular letter','disappear breaks the chain'))

for game in GAMES.values():
 for species in (75,525):
  assert not any(l.startswith('Mirage Cave ·') for l in actual.get((species,game),{}).get('locations',[]))
