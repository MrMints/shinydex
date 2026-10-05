"""Build game-specific encounter guide from public PokéAPI tables.
Shiny restrictions are curated separately: encounter presence does not imply shiny eligibility.
"""
import csv, json
from collections import defaultdict
from pathlib import Path
def rows(name): return list(csv.DictReader(open(name+'.csv',encoding='utf-8-sig')))
def lookup(name): return {int(r['id']):r for r in rows(name)}
catalog=json.loads(Path('data.json').read_text()); data=[p for p in catalog if not p.get('region')]; species=lookup('species'); versions=lookup('versions'); groups=lookup('version_groups'); slots=lookup('encounter_slots'); methods=lookup('encounter_methods'); areas=lookup('location_areas'); locations=lookup('locations')
pokemons=lookup('pokemon'); eggs=defaultdict(set)
for r in rows('egg_groups'): eggs[int(r['species_id'])].add(int(r['egg_group_id']))
enc=defaultdict(lambda:defaultdict(lambda:defaultdict(set)))
for r in rows('encounters'):
 p=pokemons[int(r['pokemon_id'])]
 if p['is_default']!='1': continue
 sid=int(p['species_id']); vid=int(r['version_id']); method=methods[int(slots[int(r['encounter_slot_id'])]['encounter_method_id'])]['identifier']
 area=areas[int(r['location_area_id'])]; loc=locations[int(area['location_id'])]['identifier']; enc[sid][vid][method].add(loc)
title=lambda s: s.replace('-',' ').title()
game_names={'firered':'FireRed','leafgreen':'LeafGreen','heartgold':'HeartGold','soulsilver':'SoulSilver','lets-go-pikachu':"Let's Go, Pikachu!",'lets-go-eevee':"Let's Go, Eevee!",'xd':'XD: Gale of Darkness','omega-ruby':'Omega Ruby','alpha-sapphire':'Alpha Sapphire'}
global_locked={494,720,789,790,801,802,891,892,893,896,897,898,1009,1010,1014,1015,1016,1017,1020,1021,1022,1023,1024,1025}
# Bulbapedia's unobtainable shiny list, checked 2026-10-03. Default species forms only.
def status(sid,v,m):
 if sid in global_locked: return 'Shiny Locked'
 if v in {'red','blue','yellow','red-japan','green-japan','blue-japan'}:
  return 'Shiny DV transfer route' if m in {'old-rod','good-rod','super-rod','gift','static','npc-trade'} else 'No shiny DV combination'
 if m=='hidden-grotto': return 'Shiny Locked'
 if m in {'snag','snag-rematch'} and v=='xd': return 'Shiny Locked'
 if m=='npc-trade' and v not in {'lets-go-pikachu','lets-go-eevee','xd'}: return 'Shiny Locked'
 if sid in {643,644} and v in {'black','white','black-2','white-2'}: return 'Shiny Locked'
 if sid in {382,383,384,386} and v in {'omega-ruby','alpha-sapphire'}: return 'Shiny Locked'
 if sid in {716,717,718} and v in {'x','y'}: return 'Shiny Locked'
 if sid in {144,145,146,150,143} and v in {'x','y'} and m in {'static','roaming'}: return 'Shiny Locked'
 if sid==448 and v in {'x','y'} and m=='gift': return 'Shiny Locked'
 if sid==571 and v in {'black','white'} and m=='static': return 'Shiny Locked'
 if sid==570 and v in {'black','white','black-2','white-2'} and m=='gift': return 'Shiny Locked'
 if sid in {133,585} and v in {'black-2','white-2'} and m=='gift': return 'Shiny Locked'
 if sid==718 and v in {'sun','moon','ultra-sun','ultra-moon'}: return 'Shiny Locked'
 if v in {'sword','shield','the-isle-of-armor-sword','the-isle-of-armor-shield','the-crown-tundra-sword','the-crown-tundra-shield'} and m=='gift':
  return 'Huntable' if sid in {880,881,882,883} else 'Shiny Locked'
 if sid in {785,786,787,788,791,792,800} and v in {'sun','moon','ultra-sun','ultra-moon'}: return 'Shiny Locked'
 if sid in {793,794,795,796,797,798,799} and v in {'sun','moon'}: return 'Shiny Locked'
 if sid in {888,889,890,772} and v in {'sword','shield','the-isle-of-armor-sword','the-isle-of-armor-shield','the-crown-tundra-sword','the-crown-tundra-shield'} and m!='dynamax-adventure': return 'Shiny Locked'
 if m in {'gift','gift-egg','pokemon-ranger','pokemon-battle-revolution','colosseum-bonus-disc-us','colosseum-bonus-disc-jpn','pokemon-channel-pal','new-york-pokecenter-wish-eggs'}: return 'Check gift/event shiny restrictions'
 return 'Huntable'
records={}
for p in data:
 sid=p['id']; entries=[]
 for vid,mm in enc[sid].items():
  v=versions[vid]['identifier']; gen=int(groups[int(versions[vid]['version_group_id'])]['generation_id'])
  game='Pokémon '+game_names.get(v,title(v))
  for method,locs in mm.items():
   label={'walk':'Wild encounters (grass / caves)','static':'Stationary encounter / soft reset','sos':'SOS encounters','horde':'Horde encounters','dynamax-adventure':'Dynamax Adventures','max-raid':'Max Raid Battles','gift':'Gift Pokémon / soft reset','gift-egg':'Gift egg','snag':'Shadow Pokémon snagging','snag-rematch':'Shadow Pokémon rematch'}.get(method,title(method))
   if status(sid,v,method)=='Shiny DV transfer route': label+=' · hunt shiny-compatible DVs, then transfer to Generation II or via Virtual Console Poké Transporter; no shiny appearance in Generation I'
   entries.append({'game':game,'method':label,'status':status(sid,v,method),'locations':sorted(title(l) for l in locs)})
   if v in {'lets-go-pikachu','lets-go-eevee'} and method.startswith('overworld'):
    entries.append({'game':game,'method':'Catch Combo shiny hunting; repeatedly catch this species. The combo shiny bonus peaks at 31 or more catches and applies only to the next spawn of the chained species after each catch; continue catching to reapply it. Lures and Shiny Charm improve overworld shiny odds. Catching a different species, a Pokémon fleeing from you, or closing the game breaks the combo; you may flee an encounter yourself without breaking it.','status':'Huntable','locations':sorted(title(l) for l in locs),'huntingTechnique':'lets-go-catch-combo','spawnMethod':method,'source':'https://bulbapedia.bulbagarden.net/wiki/Catch_Combo'})
   if gen==6 and method in {'old-rod','good-rod','super-rod'}:
    entries.append({'game':game,'method':'Consecutive fishing / chain fishing · '+title(method)+'; repeatedly reel in Pokémon in the same area without a failed reel or leaving the area; catching, defeating or fleeing the encounter preserves the streak. The shiny bonus reaches its maximum at a streak of 20; the Shiny Charm also applies. Lead with Suction Cups or Sticky Hold to improve bite reliability.','status':'Huntable','locations':sorted(title(l) for l in locs),'huntingTechnique':'gen-six-chain-fishing','rodMethod':method,'source':'https://bulbapedia.bulbagarden.net/wiki/Fishing#Generation_VI'})
  if eggs[sid] and 15 not in eggs[sid] and sid not in {132,490} and gen>=2 and v not in {'colosseum','xd','lets-go-pikachu','lets-go-eevee'}:
   entries.append({'game':game,'method':'Breed a shiny in this evolutionary line; evolve if needed'+(' · Masuda method' if gen>=4 else ''),'status':'Huntable','locations':[]})
 ancestor=species[sid]['evolves_from_species_id']
 if ancestor and sid not in global_locked:
  aid=int(ancestor)
  for vid,mm in enc[aid].items():
   v=versions[vid]['identifier']; gen=int(groups[int(versions[vid]['version_group_id'])]['generation_id'])
   if gen<p['generation'] or not any(status(aid,v,m)=='Huntable' for m in mm): continue
   ap=next(x for x in data if x['id']==aid)
   entries.append({'game':'Pokémon '+game_names.get(v,title(v)),'method':'Catch shiny '+title(ap['name'])+' and evolve it','status':'Huntable','locations':[]})
 if p['generation']==9 and sid not in global_locked:
  if sid in {999,1000}:
   entries.append({'game':'Pokémon Scarlet / Violet','method':'Shiny-enabled Gimmighoul event Tera Raids'+('; evolve with 999 Gimmighoul Coins' if sid==1000 else ''),'status':'Past event · availability varies','locations':[]})
  elif sid in {1001,1002,1003,1004,1007,1008}:
   entries.append({'game':'Pokémon Scarlet / Violet','method':'Stationary / story encounters','status':'Shiny Locked','locations':[]})
   entries.append({'game':'Pokémon Scarlet / Violet','method':'Shiny event distribution','status':'Past event · availability varies','locations':[]})
  elif 906<=sid<=914:
   entries.append({'game':'Pokémon Scarlet / Violet','method':'Breed shiny starter eggs (Masuda method); evolve if needed','status':'Huntable','locations':[]})
   if sid in {906,909,912}: entries.append({'game':'Pokémon Scarlet / Violet','method':'Starter gift','status':'Shiny Locked','locations':[]})
  else:
   if ancestor:
    entries.append({'game':'Pokémon Scarlet / Violet','method':'Catch a shiny in this evolutionary line and evolve it','status':'Huntable','locations':[]})
   else:
    entries.append({'game':'Pokémon Scarlet / Violet','method':'Wild encounters · Sparkling Power / outbreak hunting where available','status':'Huntable','locations':[]})
   if eggs[sid] and 15 not in eggs[sid]:
    entries.append({'game':'Pokémon Scarlet / Violet','method':'Breed a shiny in this evolutionary line (Masuda method); evolve if needed','status':'Huntable','locations':[]})
 records[str(sid)]={'locked':sid in global_locked,'entries':entries}
def add(ids,game,method,state='Huntable'):
 for sid in ids: records[str(sid)]['entries'].append({'game':game,'method':method,'status':state,'locations':[]})
for sid in (999,1000):
 for entry in records[str(sid)]['entries']:
  if entry['game']=='Pokémon Scarlet / Violet' and entry['method'].startswith('Shiny-enabled Gimmighoul event Tera Raids'):
   entry['method']='Chest Form Gimmighoul shiny hunting in 5-star event Tera Raids. Verified historical windows: June 21, 2023 at 15:00 UTC through July 2, 2023 at 23:59 UTC; August 9, 2024 at 00:00 UTC through August 22, 2024 at 23:59 UTC. Download the applicable Poké Portal News via Mystery Gift → Check Poké Portal News. Host 5-star raids after completing the main story or join another host; online multiplayer requires Nintendo Switch Online. Shiny encounters are possible, not guaranteed.'+('; evolve the shiny with 999 Gimmighoul Coins.' if sid==1000 else '')
   entry['source']='https://www.pokemon.com/us/news/chest-form-gimmighoul-is-coming-to-tera-raid-battles'
   entry['sourceReferences']=['https://www.pokemon.com/es/noticias-pokemon/enfrentate-a-gimmighoul-forma-cofre-en-las-teraincursiones','https://sv-news.pokemon.co.jp/es/page/235.html']
# Reviewed result announcements confirm these gifts were distributed, rather
# than merely promised if a community raid target was reached.
for sid,version in [(1007,'Violet'),(1008,'Scarlet')]:
 for entry in records[str(sid)]['entries']:
  if entry['game']=='Pokémon Scarlet / Violet' and entry['method']=='Shiny event distribution':
   entry['game']='Pokémon '+version
   entry['method']=f'2025 Japan shiny legendary code campaign: receive this gift in {version}. Code cards were distributed September 26–October 15, 2025 at participating Japanese game retailers, while supplies lasted; show a console HOME menu with a Scarlet or Violet software icon. One card per person carried separate codes for both gifts. Codes expired October 23, 2025; internet required, one use per code and one receipt of this gift per save. Other regional distributions require separate review.'
   entry['status']='Past event · codes expired'
   entry['source']='https://www.pokemon.co.jp/info/2025/09/250912_gm01.html'
for sid,event_name,start_date in [(1001,'wo-chien','August 8, 2025'),(1002,'chien-pao','August 22, 2025'),(1003,'ting-lu','September 5, 2025'),(1004,'chi-yu','September 19, 2025')]:
 for entry in records[str(sid)]['entries']:
  if entry['game']=='Pokémon Scarlet / Violet' and entry['method']=='Shiny event distribution':
   entry['method']=f'2025 shiny {title(event_name)} community-challenge reward: Mystery Gift → Get via Internet, from {start_date} at 00:00 UTC through September 30, 2025 at 23:59 UTC; save after redemption. The challenge raids could not be caught; the reward was a separate Mystery Gift.'
   entry['status']='Past event · distribution ended'
   entry['source']=f'https://www.pokemon.com/uk/news/announcing-the-total-victories-against-shiny-{event_name}-in-pokemon-scarlet-and-pokemon-violet'
   if sid==1003:
    entry['source']='https://www.pokemon.com/it/novita/annuncio-del-totale-di-vittorie-contro-ting-lu-cromatico-in-pokemon-scarlatto-e-pokemon-violetto'
   if sid==1004:
    entry['source']='https://sv-news.pokemon.co.jp/en/page/380.html'
    entry['method']+=' Requires internet and a Nintendo Account linked to the Switch user profile; Mystery Gift must be unlocked (approximately 1–1.5 hours of play).'
   entry['sourceReferences']=['https://www.pokemon.com/us/news/shiny-wo-chien-appears-in-5-star-tera-raid-battles-in-pokemon-scarlet-and-pokemon-violet']
add([409],'Pokémon Diamond / Platinum','Revive a shiny Cranidos from a Skull Fossil (soft reset), then evolve at level 30')
add([411],'Pokémon Pearl / Platinum','Revive a shiny Shieldon from an Armor Fossil (soft reset), then evolve at level 30')
add([474],'Pokémon Diamond / Pearl / Platinum','Breed a shiny Porygon; trade holding Up-Grade, then trade holding Dubious Disc')
add([489],'Pokémon Diamond / Pearl / Platinum','Breed Manaphy or Phione with Ditto; hatch shiny Phione eggs (Masuda method)')
add([490],'Pokémon Diamond / Pearl / Platinum / HeartGold / SoulSilver','Transfer Ranger Manaphy Egg; trade the unhatched egg to another save to allow shininess')
records['490']['entries'].append({
 'game':'Pokémon HOME',
 'method':'Complete the Brilliant Diamond / Shining Pearl Sinnoh Pokédex in Pokémon HOME, then confirm completion in the Games tab and claim shiny Manaphy through Mystery Gift. Requires a linked Nintendo Account; this gift can be received once per Nintendo Account. Previously completed HOME Pokédexes are eligible.',
 'status':'Reward · check requirements','locations':[],
 'source':'https://www.pokemon.com/uk/news/complete-pokedexes-to-earn-shiny-keldeo-and-shiny-meltan-in-pokemon-home'
})
add([496,499,502],'Pokémon Black / White / Black 2 / White 2','Breed shiny starter eggs (Masuda method); evolve to the middle stage')
add([723,724,726,727,729,730],'Pokémon Sun / Moon / Ultra Sun / Ultra Moon','Breed shiny Alola starter eggs (Masuda method); evolve to the desired stage')
add([811,812,814,815,817,818],'Pokémon Sword / Shield','Breed shiny Galar starter eggs (Masuda method); evolve to the desired stage')
add([810,813,816],'Pokémon Sword / Shield','Starter gift','Shiny Locked')
add([773],'Pokémon Sun / Moon / Ultra Sun / Ultra Moon','Soft reset the Type: Null gift; evolve with high friendship')
add([804],'Pokémon Ultra Sun / Ultra Moon','Soft reset the Poipole gift; evolve while knowing Dragon Pulse')
add([647],'Pokémon HOME','Complete the Sword / Shield Galar, Isle of Armor and Crown Tundra Pokédexes in HOME; claim shiny Keldeo','Reward · check requirements')
add([648],'Pokémon HOME','Complete Scarlet / Violet Paldea, Kitakami and Blueberry Pokédexes in HOME; claim shiny Meloetta','Reward · check requirements')
add([721],'Pokémon HOME','Complete the Legends: Z-A Lumiose, Hyperspace and Mega Evolution Pokédexes in HOME, then confirm completion in the Games tab. Redeem shiny Volcanion through Mystery Gifts in the mobile iOS/Android HOME app with a linked Nintendo Account; once per account. Previously completed Pokédexes remain eligible.','Reward · check requirements')
records['721']['entries'][-1]['source']='https://news.pokemon-home.com/en/page/757.html'
add([905],'Pokémon HOME','Complete the Legends: Arceus Hisui Pokédex in HOME; claim shiny Enamorus','Reward · check requirements')
add([647],'Pokémon Sword / Shield · Crown Tundra','Stationary Keldeo encounter','Shiny Locked')
add([648],'Pokémon Scarlet / Violet · Indigo Disk','Stationary Meloetta encounter','Shiny Locked')
add([905],'Pokémon Legends: Arceus','Mission Enamorus encounter','Shiny Locked')
records['649']['entries'].append({
 'game':'Pokémon GO',
 'method':'Shiny-enabled five-star Genesect raids. Verified historical window: Ultra Unlock Unova Week, August 14, 2020 at 20:00 UTC through August 21, 2020 at 20:00 UTC; shiny encounters were possible, not guaranteed. Later raid rotations require their own announcement checks.',
 'status':'Event rotation · availability varies','locations':[],
 'source':'https://pokemongo.com/news/aug2020-events'
})
add([719],'Pokémon Omega Ruby / Alpha Sapphire','Historical Japan shiny Diancie gift at Pokémon Centers and Pokémon Stores, December 12–31, 2015; distributed to Omega Ruby / Alpha Sapphire. These dates are corroborated by historical event records; the original official announcement is no longer available. The separate All-Stars Battle distribution requires further regional and redemption review.','Past event · distribution ended')
records['719']['entries'][-1]['source']='https://www.serebii.net/events/dex/719.shtml'
records['807']['entries'].append({
 'game':'Pokémon HOME',
 'method':'2020 shiny Zeraora reward: redeem Mystery Gift in mobile Pokémon HOME from June 30, 2020 at 00:00 UTC through July 6, 2020 at 23:59 UTC. Eligibility required depositing or withdrawing a Pokémon between Sword / Shield and Switch Pokémon HOME from June 17, 2020 at 15:00 UTC through July 6, 2020 at 23:59 UTC. The community raid target was achieved; Zeraora in those Max Raids could not be caught.',
 'status':'Past event · distribution ended','locations':[],
 'source':'https://swordshield.pokemon.com/en-us/expansionpass/mythical-zeraora/',
 'sourceReferences':['https://www.pokemon.co.jp/info/2020/06/200630_gm01.html']
})
records['808']['entries'].append({
 'game':'Pokémon GO',
 'method':"Obtain the Mystery Box by sending a Pokémon from GO to Pokémon HOME or Let's Go, Pikachu! / Eevee!, then use it during a shiny-enabled Meltan event. Verified windows: Let's GO, March 21, 2023 at 10:00 through March 29, 2023 at 20:00 local time; Steeled Resolve, April 28, 2026 at 10:00 through May 4, 2026 at 20:00 local time. Shiny encounters are possible, not guaranteed. These windows have ended; later availability requires an event announcement.",
 'status':'Event rotation · availability varies','locations':[],
 'source':'https://pokemongo.com/en/news/steeled-resolve-2026',
 'sourceReferences':['https://pokemongo.com/en/post/lets-go-event-team-go-rocket-takeover']
})
add([808],'Pokémon HOME',"Let's Go Pokédex-completion shiny Mystery Gift",'Reward · check requirements')
add([809],'Pokémon GO','Evolve shiny Meltan with 400 Meltan Candy','Huntable')
# HOME rewards use game-specific registration, rather than the in-game Dex.
for reward_id in (490,647,648,905,808):
 for reward in records[str(reward_id)]['entries']:
  if reward['game']=='Pokémon HOME' and reward['status']=='Reward · check requirements':
   if reward_id!=490:
    reward['method']+='; confirm completion in the Games tab and redeem Mystery Gift in the mobile HOME app. Requires a linked Nintendo Account; once per Nintendo Account.'
   else:
    reward['method']+=' Redeem in the mobile HOME app.'
   reward['method']+=' Register Pokémon originating in the corresponding games in HOME; importing Pokémon from other games does not satisfy the game-specific Pokédex.'
   reward['source']='https://www.pokemon.com/uk/news/complete-pokedexes-to-earn-shiny-keldeo-and-shiny-meltan-in-pokemon-home'
   reward['sourceReferences']=['https://home.pokemon.com/en-ca/features/']
records['647']['entries'].append({
 'game':'Pokémon GO',
 'method':'Final Justice paid Masterwork Research rewards shiny Keldeo. Ticket sales ran worldwide from November 25, 2025 at 10:00 to November 30, 2025 at 20:00 local time, for US$7.99 or the local equivalent plus applicable taxes and fees; PokéCoins could not be used. The acquired Masterwork Research does not expire. The separate seasonal Keldeo encounter is not this shiny reward.',
 'status':'Past ticket sale · acquired research does not expire','locations':[],
 'source':'https://pokemongo.com/news/final-justice-2025'
})
# Wyrdeer and Ursaluna use the decoded, detailed Legends: Arceus routes below.
add([647,648],'Pokémon Legends: Z-A · Mega Dimension','Special Hyperspace scan encounter','Shiny Locked')
add([380,381,638,639,640],'Pokémon Legends: Z-A · Mega Dimension','After defeating Rayquaza, earn 25,000 survey points and use Philippe’s special Hyperspace scan; repeat the corresponding legendary encounter')
regional_evolutions={
 ('alola',20):'Evolve shiny Alolan Rattata at level 20 at night',
 ('alola',26):'Catch or hatch shiny Pikachu; use a Thunder Stone in Alola (outside Ultra Space)',
 ('alola',28):'Use an Ice Stone on shiny Alolan Sandshrew',
 ('alola',38):'Use an Ice Stone on shiny Alolan Vulpix',
 ('alola',51):'Evolve shiny Alolan Diglett at level 26',
 ('alola',53):'Evolve shiny Alolan Meowth with high friendship',
 ('alola',75):'Evolve shiny Alolan Geodude at level 25',
 ('alola',76):'Trade shiny Alolan Graveler',
 ('alola',89):'Evolve shiny Alolan Grimer at level 38',
 ('alola',103):'Catch or hatch shiny Exeggcute; use a Leaf Stone in Alola (outside Ultra Space)',
 ('alola',105):'Evolve shiny Cubone at level 28 or higher at night in Alola (outside Ultra Space)',
 ('galar',78):'Evolve shiny Galarian Ponyta at level 40',
 ('galar',80):'Use a Galarica Cuff on shiny Galarian Slowpoke',
 ('galar',110):'Evolve shiny Koffing at level 35 or higher in Sword / Shield',
 ('galar',122):'Catch or hatch shiny Mime Jr.; level up knowing Mimic in Sword / Shield',
 ('galar',199):'Use a Galarica Wreath on shiny Galarian Slowpoke',
 ('galar',264):'Evolve shiny Galarian Zigzagoon at level 20',
 ('galar',555):'Use an Ice Stone on shiny Galarian Darumaka',
 ('hisui',59):'Use a Fire Stone on shiny Hisuian Growlithe',
 ('hisui',101):'Use a Leaf Stone on shiny Hisuian Voltorb',
 ('hisui',157):'Evolve shiny Quilava at level 36 or higher in Legends: Arceus; the starter gift is shiny locked, later wild encounters can be shiny',
 ('hisui',503):'Evolve shiny Dewott at level 36 or higher in Legends: Arceus; the starter gift is shiny locked, later wild encounters can be shiny',
 ('hisui',549):'Use a Sun Stone on shiny Petilil in Legends: Arceus',
 ('hisui',571):'Evolve shiny Hisuian Zorua at level 30',
 ('hisui',628):'Evolve shiny Rufflet at level 54 or higher in Legends: Arceus',
 ('hisui',705):'Evolve shiny Goomy at level 40 or higher in Legends: Arceus',
 ('hisui',706):'Evolve shiny Hisuian Sliggoo at level 50 or higher while raining',
 ('hisui',713):'Evolve shiny Bergmite at level 37 or higher in Legends: Arceus',
 ('hisui',724):'Evolve shiny Dartrix at level 34 or higher in Legends: Arceus; the starter gift is shiny locked, later wild encounters can be shiny',
}
for p in catalog:
 if not p.get('region'): continue
 region=p['region']; sid=p['id']; key=str(p['key']); records[key]={'locked':False,'entries':[]}
 def regional(game,method,state='Huntable',source=None):
  records[key]['entries'].append({'game':game,'method':method,'status':state,'locations':[],'source':source or p['source']+'#Game_locations'})
 evolution=regional_evolutions.get((region,sid))
 if region=='alola':
  regional('Pokémon Sun / Moon / Ultra Sun / Ultra Moon',evolution or 'Breed shiny '+p['displayName']+' eggs using the Masuda method; offspring in Alola have their Alolan form')
 elif region=='galar':
  if sid in {144,145,146}:
   regional('Pokémon Sword / Shield · Crown Tundra','Roaming Galarian legendary bird encounter','Shiny Locked')
   regional('Pokémon GO','Daily Adventure Incense: hunt the shiny Galarian bird',source='https://pokemongolive.com/post/galarian-expedition-2024')
   if sid==145:
    regional('Pokémon Sword / Shield','2022 International Challenge March shiny Galarian Zapdos reward: qualifying registered players had to participate in at least three battles, win or lose, from March 11, 2022 at 00:00 UTC through March 13, 2022 at 23:59 UTC. After the competition, redeem via Mystery Gift → Get a Mystery Gift → Get Battle Stadium Rewards. Entry and battles for this competition have ended.','Past competition · qualifying participants only',source='https://www.pokemon.com/uk/news/participate-in-the-2022-international-challenge-march-for-shiny-galarian-zapdos')
   else:
    month,registration,battles=('February','February 3, 2022 at 05:00 UTC through February 17, 2022 at 23:59 UTC','February 18–20, 2022 (ending 23:59 UTC)') if sid==144 else ('April','March 31, 2022 at 05:00 UTC through April 14, 2022 at 23:59 UTC','April 15–17, 2022 (ending 23:59 UTC)')
    regional('Pokémon Sword / Shield',f'2022 International Challenge {month} shiny Galarian bird reward. Registration: {registration}; battles: {battles}. Registered players needed three completed battles. Entry and battles have ended.', 'Past competition · qualifying participants only',source=f'https://www.serebii.net/swordshield/onlinecompetitions/2022internationalchallenge{month.lower()}.shtml')
  else:
   regional('Pokémon Sword / Shield'+(' · Isle of Armor' if sid in {79,80} else ' · Crown Tundra' if sid==199 else ''),evolution or 'Breed shiny '+p['displayName']+' eggs using the Masuda method; use an Everstone on the regional parent to retain its form',source=p['source']+'#Evolution')
 elif region=='hisui':
  regional('Pokémon Legends: Arceus',evolution or 'Wild encounters / mass outbreak hunting for '+p['displayName'])
 elif region=='paldea':
  version='Scarlet' if 'blaze' in p['name'] else 'Violet' if 'aqua' in p['name'] else 'Scarlet / Violet'
  regional('Pokémon '+version,'Wild encounter hunting for '+p['displayName']+'; Sparkling Power improves shiny odds')
  regional('Pokémon Scarlet / Violet','Masuda breeding with a parent of this form; use an Everstone to preserve regional form (Tauros breeds with Ditto)',source='https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9mon_breeding')
for p in catalog:
 record=records[str(p['key'])]
 for entry in record['entries']:
  entry.setdefault('source',p['source']+'#Game_locations')
from audit_gifts import verify
print('Gift verification:',verify(records,catalog))
# The CSV places these Totem rewards under the base species, but the rewards
# are Alolan forms. Keep their restrictions in the matching regional guide.
for sid in {20,105}:
 regional_key=next(p['key'] for p in catalog if p['id']==sid and p.get('region')=='alola')
 base=records[str(sid)]['entries']
 totems=[entry for entry in base if entry['method']=='Totem-sized Pokémon gift from Samson Oak']
 for entry in totems:
  entry['method']='Totem-sized Alolan Pokémon gift from Samson Oak'
  records[str(regional_key)]['entries'].append(entry)
 records[str(sid)]['entries']=[entry for entry in base if entry not in totems]
from modern_hunts import merge
print('Modern encounter routes:',merge(records,catalog))
from summer_outbreak_review import merge as merge_summer_outbreak_review
print('Reviewed 2024 summer outbreak examples:',merge_summer_outbreak_review(records,catalog))
from sos_hunts import merge as merge_sos
print('SOS mechanic and special-target reviews:',merge_sos(records,catalog))
from pelago_hunts import merge as merge_pelago
print('Source-reviewed Pelago access routes:',merge_pelago(records))
from raid_hunts import merge as merge_raids
print('Raid routes:',merge_raids(records,catalog))
from breeding_hunts import merge as merge_breeding
print('Direct egg routes:',merge_breeding(records,catalog))
from evolution_hunts import merge as merge_evolutions
print('Verified evolution requirement routes:',merge_evolutions(records,catalog))
from older_evolution_hunts import merge as merge_older_evolutions
print('Older evolution routes:',merge_older_evolutions(records,catalog))
from sun_moon_evolution_hunts import merge as merge_sun_moon_evolutions
print('Sun/Moon evolution routes:',merge_sun_moon_evolutions(records,catalog))
from gen_six_evolution_hunts import merge as merge_gen_six_evolutions
print('Gen VI evolution routes:',merge_gen_six_evolutions(records,catalog))
from gen_five_evolution_hunts import merge as merge_gen_five_evolutions
print('Gen V evolution routes:',merge_gen_five_evolutions(records,catalog))
from gen_four_evolution_hunts import merge as merge_gen_four_evolutions
print('Gen IV evolution routes:',merge_gen_four_evolutions(records,catalog))
from gen_three_evolution_hunts import merge as merge_gen_three_evolutions
print('Gen III evolution routes:',merge_gen_three_evolutions(records,catalog))
from lets_go_evolution_hunts import merge as merge_lets_go_evolutions
print('Let’s Go evolution routes:',merge_lets_go_evolutions(records,catalog))
from gen_two_evolution_hunts import merge as merge_gen_two_evolutions
print('Gen II evolution routes:',merge_gen_two_evolutions(records,catalog))
from gen_two_breeding_hunts import merge as merge_gen_two_breeding
print('Gen II DV egg routes:',merge_gen_two_breeding(records,catalog))
from orre_evolution_hunts import merge as merge_orre_evolutions
print('Orre precise evolution replacements:',merge_orre_evolutions(records,catalog))
# The catalog pictures Midday Lycanroc. Moon's own evolution cannot produce it.
for moon,sun in [('Pokémon Moon','Pokémon Sun'),('Pokémon Ultra Moon','Pokémon Ultra Sun')]:
 guide=records['745']
 shortcuts=[e for e in guide['entries'] if e['game']==moon and (e['method'].startswith('Breed a shiny in this evolutionary line') or e['method']=='Catch shiny Rockruff and evolve it')]
 assert len(shortcuts)==2, (moon,shortcuts)
 guide['entries']=[e for e in guide['entries'] if e not in shortcuts]
 guide['entries'].append({'game':moon,'method':f'Catch or hatch shiny Rockruff (ordinary ability); trade it to {sun}, level it up at level 25 or higher during daytime there to obtain Midday Lycanroc, then trade it back. In this game, evolving ordinary Rockruff instead produces Midnight Form at night.','status':'Huntable','locations':[],'formEvolutionKind':'midday-version-trade','source':'https://bulbapedia.bulbagarden.net/wiki/Lycanroc_(Pok%C3%A9mon)#Evolution'})
from prune_impossible_legacy import prune
from dexnav_hunts import merge as merge_dexnav
print('Recorded ORAS DexNav routes:',merge_dexnav(records))
from friend_safari_hunts import merge as merge_friend_safari
print('Friend Safari routes:',merge_friend_safari(records))
from radar_hunts import merge as merge_radar
print('Explicit Sinnoh radar encounter routes:',merge_radar(records))
from radar_hunts import merge_ordinary as merge_ordinary_radar
print('Sinnoh route-grass radar routes:',merge_ordinary_radar(records))
from xy_radar_hunts import merge as merge_xy_radar
print('X/Y flower-bed radar routes:',merge_xy_radar(records))
print('X/Y verified grass radar routes:',merge_xy_radar(records,grass=True))
from bdsp_radar_hunts import merge as merge_bdsp_radar
print('BDSP Radar routes:',merge_bdsp_radar(records))
print('Impossible generic evolution claims removed:',prune(records))
from supersede_evolutions import supersede
print('Generic evolution rows superseded by exact routes:',supersede(records))
from supersede_breeding import supersede as supersede_breeding
print('Generic breeding rows superseded by exact egg routes:',supersede_breeding(records))
Path('hunts.json').write_text(json.dumps(records,separators=(',',':')))
print(f'Built encounter guide for {len(records)} species, {sum(bool(r["entries"]) for r in records.values())} with game records')
