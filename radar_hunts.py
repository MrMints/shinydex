"""Record explicitly radar-enabled encounters; ordinary grass coverage is separate."""
import csv
from collections import defaultdict
VERIFIED_GRASS_ROUTES={
 'Mt Coronet':'https://bulbapedia.bulbagarden.net/wiki/Mt_Coronet#Generation_IV',
 'Stark Mountain':'https://bulbapedia.bulbagarden.net/wiki/Stark_Mountain#Generation_IV',
 'Lake Verity':'https://bulbapedia.bulbagarden.net/wiki/Lake_Verity#Generation_IV',
 'Lake Valor':'https://bulbapedia.bulbagarden.net/wiki/Lake_Valor#Generation_IV',
 'Lake Acuity':'https://bulbapedia.bulbagarden.net/wiki/Lake_Acuity#Generation_IV',
 'Valor Lakefront':'https://bulbapedia.bulbagarden.net/wiki/Valor_Lakefront#Generation_IV',
 'Acuity Lakefront':'https://bulbapedia.bulbagarden.net/wiki/Acuity_Lakefront#Generation_IV',
 'Sendoff Spring':'https://bulbapedia.bulbagarden.net/wiki/Sendoff_Spring#Generation_IV',
 'Trophy Garden':'https://bulbapedia.bulbagarden.net/wiki/Trophy_Garden#Generation_IV',
 'Fuego Ironworks':'https://bulbapedia.bulbagarden.net/wiki/Fuego_Ironworks#Generation_IV',
 'Eterna Forest':'https://bulbapedia.bulbagarden.net/wiki/Eterna_Forest#Generation_IV',
 'Valley Windworks':'https://bulbapedia.bulbagarden.net/wiki/Valley_Windworks#Generation_IV',
 'Sinnoh Route 201':'https://bulbapedia.bulbagarden.net/wiki/Sinnoh_Route_201#Generation_IV',
 'Sinnoh Route 202':'https://bulbapedia.bulbagarden.net/wiki/Sinnoh_Route_202#Generation_IV',
 'Sinnoh Route 203':'https://bulbapedia.bulbagarden.net/wiki/Sinnoh_Route_203#Generation_IV',
 'Sinnoh Route 204':'https://bulbapedia.bulbagarden.net/wiki/Sinnoh_Route_204#Generation_IV',
 'Sinnoh Route 205':'https://bulbapedia.bulbagarden.net/wiki/Sinnoh_Route_205#Generation_IV',
 'Sinnoh Route 206':'https://bulbapedia.bulbagarden.net/wiki/Sinnoh_Route_206#Generation_IV',
 'Sinnoh Route 207':'https://bulbapedia.bulbagarden.net/wiki/Sinnoh_Route_207#Generation_IV',
 'Sinnoh Route 208':'https://bulbapedia.bulbagarden.net/wiki/Sinnoh_Route_208#Generation_IV',
 'Sinnoh Route 209':'https://bulbapedia.bulbagarden.net/wiki/Sinnoh_Route_209#Generation_IV',
 'Sinnoh Route 211':'https://bulbapedia.bulbagarden.net/wiki/Sinnoh_Route_211#Generation_IV',
 'Sinnoh Route 212':'https://bulbapedia.bulbagarden.net/wiki/Sinnoh_Route_212#Generation_IV',
 'Sinnoh Route 213':'https://bulbapedia.bulbagarden.net/wiki/Sinnoh_Route_213#Generation_IV',
 'Sinnoh Route 214':'https://bulbapedia.bulbagarden.net/wiki/Sinnoh_Route_214#Generation_IV',
 'Sinnoh Route 215':'https://bulbapedia.bulbagarden.net/wiki/Sinnoh_Route_215#Generation_IV',
 'Sinnoh Route 216':'https://bulbapedia.bulbagarden.net/wiki/Sinnoh_Route_216#Generation_IV',
 'Sinnoh Route 217':'https://bulbapedia.bulbagarden.net/wiki/Sinnoh_Route_217#Generation_IV',
 'Sinnoh Route 218':'https://bulbapedia.bulbagarden.net/wiki/Sinnoh_Route_218#Generation_IV',
 'Sinnoh Route 221':'https://bulbapedia.bulbagarden.net/wiki/Sinnoh_Route_221#Generation_IV',
 'Sinnoh Route 222':'https://bulbapedia.bulbagarden.net/wiki/Sinnoh_Route_222#Generation_IV',
 'Sinnoh Route 224':'https://bulbapedia.bulbagarden.net/wiki/Sinnoh_Route_224#Generation_IV',
 'Sinnoh Route 225':'https://bulbapedia.bulbagarden.net/wiki/Sinnoh_Route_225#Generation_IV',
 'Sinnoh Route 226':'https://bulbapedia.bulbagarden.net/wiki/Sinnoh_Route_226#Generation_IV',
 'Sinnoh Route 227':'https://bulbapedia.bulbagarden.net/wiki/Sinnoh_Route_227#Generation_IV',
 'Sinnoh Route 228':'https://bulbapedia.bulbagarden.net/wiki/Sinnoh_Route_228#Generation_IV',
 'Sinnoh Route 229':'https://bulbapedia.bulbagarden.net/wiki/Sinnoh_Route_229#Generation_IV',
 'Sinnoh Route 230':'https://bulbapedia.bulbagarden.net/wiki/Sinnoh_Route_230#Generation_IV',
}
def routes(ordinary=False):
 def rows(name):
  with open(name+'.csv',encoding='utf-8-sig') as f:return list(csv.DictReader(f))
 conditions={r['id']:r['identifier'] for r in rows('encounter_condition_values')}
 encounter_conditions=defaultdict(set)
 for condition in rows('encounter_condition_value_map'):
  encounter_conditions[condition['encounter_id']].add(conditions[condition['encounter_condition_value_id']])
 radar={r['encounter_id'] for r in rows('encounter_condition_value_map') if conditions[r['encounter_condition_value_id']]=='radar-on'}
 pokemon={r['id']:r for r in rows('pokemon')};areas={r['id']:r['location_id'] for r in rows('location_areas')};locations={r['id']:r['identifier'] for r in rows('locations')}
 area_names={r['id']:r['identifier'] for r in rows('location_areas')}
 slots={r['id']:r['encounter_method_id'] for r in rows('encounter_slots')}
 games={'12':'Pokémon Diamond','13':'Pokémon Pearl','14':'Pokémon Platinum'}
 result=defaultdict(set)
 for r in rows('encounters'):
  p=pokemon[r['pokemon_id']]
  loc=locations[areas[r['location_area_id']]]
  eligible=(r['id'] in radar) if not ordinary else (r['id'] not in radar and slots[r['encounter_slot_id']]=='1' and (loc.startswith(('sinnoh-route-','sinnoh-sea-route-')) or (loc=='mt-coronet' and area_names[r['location_area_id']] in {'exterior-snowfall','exterior-blizzard'}) or (loc=='stark-mountain' and area_names[r['location_area_id']]=='') or loc in {'eterna-forest','valley-windworks','fuego-ironworks','trophy-garden','sendoff-spring','valor-lakefront','acuity-lakefront','lake-verity','lake-valor','lake-acuity'}))
  if eligible and r['version_id'] in games and p['is_default']=='1':
   label=(loc.replace('sinnoh-sea-route-','sinnoh-route-') if ordinary else loc).replace('-',' ').title()
   area=area_names[r['location_area_id']]
   if area:label+=' · '+area.replace('-',' ').title()
   if ordinary:
    requirements=sorted(c for c in encounter_conditions[r['id']] if c not in {'radar-off','swarm-no','slot2-none'})
    if requirements:label+=' · Encounter conditions: '+', '.join(c.replace('-',' ') for c in requirements)
   result[(int(p['species_id']),games[r['version_id']])].add(label)
 return result
def merge(records):
 for (species,game),locations in routes().items():
  records[str(species)]['entries'].append({'game':game,'method':'Poké Radar exclusive encounter / shiny chaining; obtain the Poké Radar after receiving the National Pokédex. Use it in eligible tall grass; capture or defeat the same species in shaking patches to build a chain, and look for a sparkling shiny patch. Recharge by walking 50 steps to reroll patches without entering one. Repels help avoid ordinary encounters; fleeing or encountering a different species breaks the chain. Chains can also break randomly.','status':'Huntable','locations':sorted(locations),'huntingTechnique':'sinnoh-radar-exclusive','source':'https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9_Radar','sourceReferences':['https://github.com/PokeAPI/pokeapi/blob/master/data/v2/csv/encounter_condition_value_map.csv']})
 return len(routes())

def merge_ordinary(records):
 for (species,game),locations in routes(ordinary=True).items():
  records[str(species)]['entries'].append({'game':game,'method':'Poké Radar chaining of ordinary route grass encounters; obtain the radar with the National Pokédex and use eligible short grass on these routes. Species availability can depend on time, swarms or an inserted Generation III cartridge; check the location encounter conditions. Capture or defeat the same species to continue the chain; recharge with 50 steps to reroll patches and seek a sparkling shiny patch. Repels prevent ordinary encounters; fleeing, a different species or leaving the area breaks the chain. Do not use water, cave encounters or long grass for this route.','status':'Huntable','locations':sorted(locations),'huntingTechnique':'sinnoh-radar-route-grass','source':'https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9_Radar'})
  entry=records[str(species)]['entries'][-1]
  entry['status']='Area eligibility needs verification'
  entry['method']='Candidate radar route; exact short-grass eligibility is still being verified. '+entry['method']
  verified=[location for location in entry['locations'] if location.split(' · ')[0] in VERIFIED_GRASS_ROUTES]
  if verified:
   approved=dict(entry,locations=verified,status='Huntable',huntingTechnique='sinnoh-radar-verified-route-grass')
   approved['method']=entry['method'].split('being verified. ',1)[1]
   if any(location.startswith('Trophy Garden') for location in verified):
    approved['method']+=' For Backlot encounter conditions, speak to Mr. Backlot after obtaining the National Pokédex and confirm the target is one of the last two Pokémon he introduced to the garden; ordinary resident species do not require his introduction.'
   approved['sourceReferences']=sorted({VERIFIED_GRASS_ROUTES[location.split(' · ')[0]] for location in verified})
   entry['locations']=[location for location in entry['locations'] if location not in verified]
   if not entry['locations']:records[str(species)]['entries'].remove(entry)
   records[str(species)]['entries'].append(approved)
  if entry['locations'] and any(location.startswith('Sinnoh Route 210') for location in entry['locations']):
   entry['method']+=' Route 210 contains extra-tall grass where the radar cannot be used. Radar-exclusive encounters confirm usable grass exists in both encounter sections, but the exact ordinary encounter patch assignments still need map verification.'
   entry['sourceReferences']=['https://bulbapedia.bulbagarden.net/wiki/Sinnoh_Route_210#Generation_IV','https://bulbapedia.bulbagarden.net/wiki/Tall_grass#Long_grass']
 return len(routes(ordinary=True))
