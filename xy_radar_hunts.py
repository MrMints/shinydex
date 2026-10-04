"""X/Y flower-bed radar routes from explicit encounter methods."""
import csv
from collections import defaultdict

VERIFIED_GRASS = {
 'kalos-route-20':'https://bulbapedia.bulbagarden.net/wiki/Kalos_Route_20',
 'kalos-route-22':'https://bulbapedia.bulbagarden.net/wiki/Kalos_Route_22',

 'kalos-route-14':'https://bulbapedia.bulbagarden.net/wiki/Kalos_Route_14',
 'kalos-route-15':'https://bulbapedia.bulbagarden.net/wiki/Kalos_Route_15',
 'kalos-route-18':'https://bulbapedia.bulbagarden.net/wiki/Kalos_Route_18',

 'kalos-route-11':'https://bulbapedia.bulbagarden.net/wiki/Kalos_Route_11',
 'kalos-route-12':'https://bulbapedia.bulbagarden.net/wiki/Kalos_Route_12',

 'kalos-route-5':'https://bulbapedia.bulbagarden.net/wiki/Kalos_Route_5',
 'kalos-route-7':'https://bulbapedia.bulbagarden.net/wiki/Kalos_Route_7',
 'kalos-route-8':'https://bulbapedia.bulbagarden.net/wiki/Kalos_Route_8',
 'kalos-route-10':'https://bulbapedia.bulbagarden.net/wiki/Kalos_Route_10',

 'azure-bay':'https://bulbapedia.bulbagarden.net/wiki/Azure_Bay',
 'kalos-route-2':'https://bulbapedia.bulbagarden.net/wiki/Kalos_Route_2',
 'kalos-route-3':'https://bulbapedia.bulbagarden.net/wiki/Kalos_Route_3',
 'santalune-forest':'https://bulbapedia.bulbagarden.net/wiki/Santalune_Forest',
}
def merge(records,grass=False):
 def rows(name):
  with open(name+'.csv',encoding='utf-8-sig') as f:return list(csv.DictReader(f))
 slots={r['id']:r['encounter_method_id'] for r in rows('encounter_slots')}
 methods={r['id']:r['identifier'] for r in rows('encounter_methods')}
 areas={r['id']:r['location_id'] for r in rows('location_areas')}
 locations={r['id']:r['identifier'] for r in rows('locations')}
 pokemon={r['id']:r for r in rows('pokemon')}
 games={'23':'Pokémon X','24':'Pokémon Y'}
 routes=defaultdict(set)
 for encounter in rows('encounters'):
  method=methods[slots[encounter['encounter_slot_id']]]
  if encounter['version_id'] not in games:continue
  if grass:
   if method!='walk' or locations[areas[encounter['location_area_id']]] not in VERIFIED_GRASS:continue
  elif method not in {'yellow-flowers','red-flowers','purple-flowers'}:continue
  p=pokemon[encounter['pokemon_id']]
  if p['is_default']!='1':continue
  location=locations[areas[encounter['location_area_id']]].replace('-',' ').title()
  routes[(int(p['species_id']),games[encounter['version_id']])].add(location+' · '+method.replace('-',' ').title())
 for (species,game),locations in routes.items():
  records[str(species)]['entries'].append({'game':game,'method':'Poké Radar chaining in the listed flower beds. Receive the radar from the scientist on 2F of Sycamore Pokémon Lab after entering the Hall of Fame. Walk with the D-pad; Bicycle and Roller Skates break the chain. Capture or defeat the same species in shaking patches, then recharge with 50 steps to reroll patches and seek a sparkling shiny patch. Avoid weakly shaking empty patches, fleeing, different species, hordes, Sweet Scent and leaving the area. Catching improves continuation chances. Flower color determines the encounter table. Long grass and Friend Safari are ineligible.','status':'Huntable','locations':sorted(locations),'huntingTechnique':'xy-radar-flower-beds','source':'https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9_Radar'})
  if grass:
   entry=records[str(species)]['entries'][-1]
   entry['huntingTechnique']='xy-radar-verified-grass'
   entry['method']=entry['method'].replace('listed flower beds','listed ordinary grass patches').replace('Flower color determines the encounter table. ','')
   entry['sourceReferences']=sorted({VERIFIED_GRASS[place.split(' · ')[0].lower().replace(' ','-')] for place in locations})
   if species==16 and any(place.startswith('Kalos Route 2 ·') for place in locations):
    entry['method']+=' The scripted first Pidgey encounter on Route 2 is Shiny Locked; these radar hunts use the ordinary encounter table after obtaining the radar.'
  records[str(species)]['entries'][-1]['method']+=' The sparkling-patch rate reaches 1/100 at a chain of 40. Catching a shiny normally resets that rate to 1/8100 without ending the chain; the alternate Poké Radar Chain! music temporarily gives 1/100 and preserves the chain rate when catching a shiny. Patch animations can be disguised, so appearance alone does not guarantee continuation. Honey, field moves, Trainer battles, fishing, Dowsing Machine, picking up items, hatching an Egg, story events, exiting or reloading the game, or walking until all shaking patches leave the screen also end the chain.'
 return len(routes)
