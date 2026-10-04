"""Add ORAS DexNav searches with separately sourced Shoal Cave tide restrictions."""
import csv
from collections import defaultdict
METHODS={'walk','surf','old-rod','good-rod','super-rod','horde','seaweed','feebas-tile-fishing'}
GAMES={'25':'Pokémon Omega Ruby','26':'Pokémon Alpha Sapphire'}
SHOAL={
 41:'Shoal Cave · main cave, outside ice room · high or low tide · search horde species',
 42:'Shoal Cave · main cave, outside ice room · high or low tide',
 363:'Shoal Cave · main cave, outside ice room · high or low tide',
 364:'Shoal Cave · main cave, outside ice room · high or low tide',
 361:'Shoal Cave · main cave, outside ice room · low tide only',
 72:'Shoal Cave · water · high tide · Surf required',
 73:'Shoal Cave · water · high tide · Surf required',
 129:'Shoal Cave · water · high tide · Surf required to approach searched fishing species',
 320:'Shoal Cave · water · high tide · Surf required to approach searched fishing species',
 87:'Shoal Cave · main cave, outside ice room · high or low tide · hidden-only after defeating or capturing Groudon/Kyogre',
 225:'Shoal Cave · main cave, outside ice room · high or low tide · hidden-only after defeating or capturing Groudon/Kyogre',
 613:'Shoal Cave · main cave, outside ice room · high or low tide · hidden-only after defeating or capturing Groudon/Kyogre',
}
VERIFIED_HIDDEN_ROUTES={101:[506,540,570],102:[506,535,574],103:[422,441,506],104:[441,519,540],112:[77,236],113:[559,626,707],116:[133,519,595],111:[443,551,557],117:[19,535,585],118:[20,190,404],114:[200,451,535],115:[35,200,519],121:[97,190,605],110:[422,568,441],125:[86,456,592],122:[456,592,594],124:[456,592,594],126:[456,592,594],127:[456,592,594],128:[456,592,594],129:[456,592,594],130:[456,592,594],131:[456,592,594],132:[456,592,594],133:[456,592,594],134:[456,592,594]}

VERIFIED_HIDDEN_AREAS={'Petalburg Woods':([46,546,708],'grass'),'Granite Cave':([95,532,610],'1F, B1F and B2F cave floors'),'Fiery Path':([50,236,524],'cave'),'Jagged Pass':([56,77,236],'grass'),'Mt. Pyre':([58,436,605],'exterior and summit grass'),'Meteor Falls':([35,621,633],'1F 1R cave floor')}

def routes():
 def rows(name):
  with open(name+'.csv',encoding='utf-8-sig') as f:return list(csv.DictReader(f))
 pokemon={r['id']:r for r in rows('pokemon')}
 slots={r['id']:r['encounter_method_id'] for r in rows('encounter_slots')}
 methods={r['id']:r['identifier'] for r in rows('encounter_methods')}
 areas={r['id']:r for r in rows('location_areas')}
 locations={r['id']:r['identifier'] for r in rows('locations')}
 result=defaultdict(set)
 for row in rows('encounters'):
  p=pokemon[row['pokemon_id']];area=areas[row['location_area_id']]
  if row['version_id'] not in GAMES or p['is_default']!='1' or methods[slots[row['encounter_slot_id']]] not in METHODS:continue
  loc=locations[area['location_id']]
  if loc=='shoal-cave':continue # Ice-room searching is unavailable; area mapping still needs review.
  result[(int(p['species_id']),GAMES[row['version_id']])].add(loc.replace('-',' ').title())
 for game in GAMES.values():
  for species,location in SHOAL.items():result[(species,game)].add(location)
 for game in GAMES.values():
  for route,species_list in VERIFIED_HIDDEN_ROUTES.items():
   if route==104:continue # North/south assignments are added separately below.
   for species in species_list+([538 if game==GAMES['25'] else 539] if route==112 else []):
    detail=f'Route {route} · hidden-only grass encounters after defeating or capturing Groudon/Kyogre'
    if route in (122,124,125,126,127,128,129,130,131,132,133,134):detail=detail.replace('grass encounters','water encounters')+' · Surf required'
    if route==111:detail=detail.replace('grass encounters','deep-sand encounters')+' · desert · Go-Goggles required'
    if route in (118,121):detail=detail.replace('grass encounters','grass and long-grass encounters')
    if route==115:detail+=' · northern grass · Surf required to reach grass'
    if route==118:detail+=' · eastern grass · Surf required to cross inlet'
    if species==585:detail+=' · Spring Form only'
    if species==422:detail+=' · '+('West Sea form' if game==GAMES['25'] else 'East Sea form')
    result[(species,game)].add(detail)
 for game in GAMES.values():
  for area,(species_list,terrain) in VERIFIED_HIDDEN_AREAS.items():
   for species in species_list:
    location=f'{area} · {terrain} · hidden-only after defeating or capturing Groudon/Kyogre'
    if area=='Mt. Pyre':location+=' · Surf required to reach mountain entrance'
    result[(species,game)].add(location)
 for game in GAMES.values():
  for route in (105,106,107,108,109):
   for species in (98,592,690 if game==GAMES['25'] else 692):
    result[(species,game)].add(f'Route {route} · hidden-only water encounters after defeating or capturing Groudon/Kyogre · Surf required')
 # Seaweed targets are stationary hidden encounters, distinct from surface water.
 # These native species do not require the post-Groudon/Kyogre foreign-species unlock.
 for game in GAMES.values():
  for route,species_list in {107:[170,171,366,369],124:[170,171,366,369],126:[170,171,366,369],128:[170,171,222,366,369],129:[170,171,366,369],130:[170,171,366,369]}.items():
   for species in species_list:
    result[(species,game)].add(f'Route {route} · underwater seaweed · Surf and Dive required')
 from dexnav_safari import add_locations
 add_locations(result,GAMES.values())
 # Native encounters omitted by the source CSV's limited ORAS snapshot.
 # These do not need the later foreign-species story unlock.
 for game in GAMES.values():
  for species in (261,263,265):
   result[(species,game)].add('Route 101 · tall grass · receive DexNav from Brendan/May after returning to the lab following the Route 103 rival battle')
  for species in (261,263,278):
   result[(species,game)].add('Route 103 · western tall grass')
  for species in (72,278,279,129,320):
   result[(species,game)].add('Route 103 · river water · Surf required to approach searched Pokémon')
  for section in ('north','south'):
   for species in (263,265,276,278):
    result[(species,game)].add(f'Route 104 · {section} section tall grass')
   for species in (278,279,129):
    result[(species,game)].add(f'Route 104 · {section} section water · Surf required to approach searched Pokémon')
   for species in (441,519,540):
    result[(species,game)].add(f'Route 104 · {section} section tall grass · hidden-only after defeating or capturing Groudon/Kyogre')
  for species in (66,88,109,218,322,324):
   result[(species,game)].add('Fiery Path · cave floor')
  for species in (41,63,74,296):
   result[(species,game)].add('Granite Cave · 1F cave floor')
  for species in (263,265,266,268,276,285,287):
   result[(species,game)].add('Petalburg Woods · tall grass')
  for species in (27,328,331,343):
   result[(species,game)].add('Route 111 · desert deep sand · Go-Goggles required')
  for species in (183,184,283,284,118,129,339):
   result[(species,game)].add('Route 111 · southern pond · Surf required to approach searched Pokémon')
  for species in (43,183,263,283,313,314,315):
   result[(species,game)].add('Route 117 · tall grass')
  for species in (183,184,283,284,118,129,341,342):
   result[(species,game)].add('Route 117 · pond · Surf required to approach searched Pokémon')
  for species in (43,263,278,309,316,100):
   result[(species,game)].add('Route 110 · tall grass')
  for species in (39,276,278,333):
   result[(species,game)].add('Route 115 · northern tall grass · Surf required to reach grass')
  for species in (72,278,279,129,320):
   result[(species,game)].add('Route 115 · water · Surf required to approach searched Pokémon')
  for species in (283,333,274 if game==GAMES['25'] else 271,335 if game==GAMES['25'] else 336):
   result[(species,game)].add('Route 114 · tall grass')
  for species in (183,184,283,284,118,129,339):
   result[(species,game)].add('Route 114 · pond · Surf required to approach searched Pokémon')
  for species in (353,355):
   result[(species,game)].add('Mt. Pyre · interior 1F-4F · Surf required to reach mountain entrance')
  for species in (37,278,307,353):
   result[(species,game)].add('Mt. Pyre · exterior grass · Surf required to reach mountain entrance')
  for species in (37,307,353,358):
   result[(species,game)].add('Mt. Pyre · summit grass · Surf required to reach mountain entrance')
  for species in (264,278,309,352):
   result[(species,game)].add('Route 118 · eastern tall grass · Surf required to cross inlet')
  for species in (264,279,309,352):
   result[(species,game)].add('Route 118 · eastern long grass · Surf required to cross inlet')
  for species in (72,278,279,129,318,319):
   result[(species,game)].add('Route 118 · inlet water · Surf required to approach searched Pokémon')
  for species in (72,73,279,129,320,116,117):
   result[(species,game)].add('Route 130 · surface water · Surf required to approach searched Pokémon')
  for species in (129,130):
   result[(species,game)].add('Sootopolis City · lake · Surf required to approach searched Pokémon · initially enter city using Dive on Route 126, or use Fly/Soar after visiting')
  # Resort access follows the Delta Episode, independently of DexNav Search Level.
  for species in (72,73,129,223,224,226,279,458):
   result[(species,game)].add('Battle Resort · water · Surf required to approach searched Pokémon · complete the Delta Episode, receive S.S. Ticket from Norman, then take S.S. Tidal from Slateport or Lilycove')
  for species in (72,278,279,129,320,120):
   result[(species,game)].add('Lilycove City · coastal water · Surf required to approach searched Pokémon')
  # Sky Pillar's ordinary floors support searching; the scripted apex encounter
  # is a separate shiny-locked Rayquaza encounter and must not enter this roster.
  for species in (42,168,333,344,303 if game==GAMES['25'] else 302):
   result[(species,game)].add('Sky Pillar · 1F-5F · during the Delta Episode, ask Wallace for help at the Sootopolis great tree, then defeat him at the entrance to open the seal · Surf to Route 131 or Fly/Soar after visiting')
  for species in (42,294,297,305,308,303 if game==GAMES['25'] else 302):
   result[(species,game)].add('Victory Road · entrance, 1F and B1F cave floors · initially reach Ever Grande using Surf and Waterfall; Surf and Strength needed for deeper traversal')
  for species in (41,338 if game==GAMES['25'] else 337):
   result[(species,game)].add('Meteor Falls · 1F 1R cave floor')
  for species in (41,42,118,129,339,338 if game==GAMES['25'] else 337):
   result[(species,game)].add('Meteor Falls · 1F 1R water · Surf required to approach searched Pokémon')
  for species in (42,118,129,339,340,338 if game==GAMES['25'] else 337):
   result[(species,game)].add('Meteor Falls · 1F 2R and B1F 1R water · Surf and Waterfall required to reach deeper rooms and approach searched Pokémon')
  for species in (44,264,352,357,359):
   result[(species,game)].add('Route 120 · eastern long grass')
  result[(349,game)].add('Route 119 · river water · Surf required to approach searched Feebas; first own Feebas to use DexNav Search. Any rod can catch the initial Feebas; daytime fishing below the Weather Institute bridge or nighttime fishing near the stone northwest of Pokémon Ranger Catherine guarantees Feebas encounters')
  # Native surface and fishing species can be searched on the water after
  # owning the species; the foreign hidden-only roster has a separate unlock.
  for route in (105,106,107,108,109):
   for species in (72,278,279,129,320):
    result[(species,game)].add(f'Route {route} · surface water · Surf required to approach searched Pokémon')
  # Native rosters checked against the Generation VI location tables, rather
  # than inferred from the incomplete encounter CSV or foreign-species list.
  for species in (27,227,327):
   result[(species,game)].add('Route 113 · ash-covered grass')
  for species in (263,276,290,293,300):
   result[(species,game)].add('Route 116 · tall grass')
  for city in ('Dewford Town','Slateport City'):
   for species in (72,278,279,129,320):
    result[(species,game)].add(f'{city} · coastal water · Surf required to approach searched Pokémon')
  for species in (183,184,283,284,118,129,341):
   result[(species,game)].add('Petalburg City · ponds · Surf required to approach searched Pokémon; receive HM03 from Wally’s father after defeating Norman and earning the Balance Badge')
 from dexnav_native import add_locations
 add_locations(result,GAMES.values())
 return result
def merge(records):
 count=0
 for (species,game),locations in routes().items():
  if records[str(species)]['locked']:continue
  records[str(species)]['entries'].append({'game':game,'method':'DexNav hidden Pokémon searching / chaining; own the species to use Search, then sneak toward the detected Pokémon. Higher species Search Level improves shiny chances, with additional chain bonuses at 50 and 100 encounters; Shiny Charm applies. Capture or defeat hidden Pokémon to continue the chain; fleeing or letting a detected Pokémon disappear breaks it. Fishing- and horde-only species can be searched as individual hidden encounters; water targets require Surf. Shoal Cave’s ice room does not support DexNav searching.','status':'Huntable','locations':sorted(locations),'huntingTechnique':'oras-dexnav','source':'https://bulbapedia.bulbagarden.net/wiki/DexNav'})
  entry=records[str(species)]['entries'][-1]
  if species==201:
   # Search chooses a species; the approaching silhouette previews its form.
   # Do not promise a letter-selection control that the sources do not establish.
   entry['method']+=' Unown: Mirage Cave south of Route 107 has equal encounter rates for its forms. Search for Unown, then approach carefully to inspect the form silhouette before battling. Search is documented as selecting the species, so do not rely on it to guarantee a particular letter. Letting an unwanted detected form disappear breaks the chain; battle and capture or defeat it to preserve the chain.'
  refs=entry.setdefault('sourceReferences',[])
  from dexnav_native import source_references
  refs.extend(source_references(locations))
  for route in (101,103,104,105,106,107,108,109,110,113,114,115,116,117,118,119,120,128,130):
   if any(l.startswith(f'Route {route} ·') for l in locations):
    refs.append(f'https://bulbapedia.bulbagarden.net/wiki/Hoenn_Route_{route}#Generation_VI')
  if any(l.startswith('Sootopolis City · lake') for l in locations):
   refs.append('https://bulbapedia.bulbagarden.net/wiki/Sootopolis_City#Generation_VI')
  if any(l.startswith('Battle Resort · water') for l in locations):
   refs.append('https://bulbapedia.bulbagarden.net/wiki/Battle_Resort#Pok%C3%A9mon')
  if any(l.startswith('Lilycove City · coastal water') for l in locations):
   refs.append('https://bulbapedia.bulbagarden.net/wiki/Lilycove_City#Generation_VI')
  for city in ('Dewford Town','Slateport City','Petalburg City'):
   if any(l.startswith(city+' ·') for l in locations):
    refs.append('https://bulbapedia.bulbagarden.net/wiki/'+city.replace(' ','_')+'#Generation_VI')
  if any(l.startswith('Sky Pillar ·') for l in locations):
   refs.append('https://bulbapedia.bulbagarden.net/wiki/Sky_Pillar#Generation_VI')
  if any(l.startswith('Victory Road ·') for l in locations):
   refs.append('https://bulbapedia.bulbagarden.net/wiki/Victory_Road_(Hoenn)#Generation_VI')
  if any(l.startswith('Route 111 · desert deep sand') or l.startswith('Route 111 · southern pond') for l in locations):
   refs.append('https://bulbapedia.bulbagarden.net/wiki/Hoenn_Route_111#Generation_VI')
  if any(l.startswith('Safari Zone ·') for l in locations):
   from dexnav_safari import SOURCE
   refs.append(SOURCE)
  for route in VERIFIED_HIDDEN_ROUTES:
   if any(l.startswith(f'Route {route} · hidden-only') for l in locations):refs.append(f'https://bulbapedia.bulbagarden.net/wiki/Hoenn_Route_{route}#Generation_VI')
  for route in (105,106,107,108,109):
   if any(l.startswith(f'Route {route} · hidden-only') for l in locations):refs.append(f'https://bulbapedia.bulbagarden.net/wiki/Hoenn_Route_{route}#Generation_VI')
  for route in (107,124,126,128,129,130):
   if any(l.startswith(f'Route {route} · underwater seaweed') for l in locations):
    url=f'https://bulbapedia.bulbagarden.net/wiki/Hoenn_Route_{route}#Generation_VI'
    if url not in refs:refs.append(url)
  for area in VERIFIED_HIDDEN_AREAS:
   if any(l.startswith(area+' ·') for l in locations):refs.append('https://bulbapedia.bulbagarden.net/wiki/'+area.replace(' ','_')+'#Generation_VI')
  count+=1
  if any(location.startswith('Shoal Cave') for location in locations):
   records[str(species)]['entries'][-1]['sourceReferences'].append('https://bulbapedia.bulbagarden.net/wiki/Shoal_Cave#Generation_VI')
  entry['sourceReferences']=list(dict.fromkeys(entry['sourceReferences']))
 return count
