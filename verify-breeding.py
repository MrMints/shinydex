"""Validate direct-egg routes and important offspring exceptions."""
import json
from pathlib import Path
ROOT=Path(__file__).parent
h=json.loads((ROOT/'hunts.json').read_text())
a=json.loads((ROOT/'breeding-audit.json').read_text())
routes={(int(k),e['game']):e for k,g in h.items() for e in g['entries'] if e.get('breedingKind')=='direct-egg'}
assert len(routes)==a['routeCount']
gen3_games={'Pokémon Ruby / Sapphire','Pokémon Emerald','Pokémon FireRed','Pokémon LeafGreen'}
for r in a['directEggRoutes']:
 e=routes[(r['key'],r['game'])]
 assert e['gameFormId']==r['form'] and e['breedingParent']==r['parent']
 assert e['status']=='Huntable'
 assert ('neither the Masuda method nor the Shiny Charm' in e['method']) if e['game'] in gen3_games else ('different language' in e['method'])
assert not any(k in {132,490} for k,g in routes), 'Ditto and Manaphy cannot hatch from eggs'
for game in ['Pokémon Scarlet / Violet','Pokémon Brilliant Diamond / Shining Pearl']:
 assert routes[(489,game)]['breedingParent']==490
 assert 'offspring are Phione' in routes[(489,game)]['method']
 assert routes[(172,game)]['breedingParent']==25
assert 'Sea Incense' in routes[(298,'Pokémon Brilliant Diamond / Shining Pearl')]['method']
assert 'Incense' not in routes[(298,'Pokémon Scarlet / Violet')]['method']
assert not any('Legends:' in game or "Let's Go" in game for key,game in routes)
print('Verified',len(routes),'direct egg routes and offspring/incense regressions; evolution audit remains incomplete')

for (key,game),entry in routes.items():
 if game=='Pokémon Brilliant Diamond / Shining Pearl':assert 'Nursery in Solaceon Town' in entry['method']
 elif game=='Pokémon Sword / Shield':assert 'Route 5 or in Bridge Field' in entry['method']
 elif game=='Pokémon Scarlet / Violet':assert 'picnic basket' in entry['method']
 elif game=='Pokémon Ultra Sun / Ultra Moon':assert 'Nursery at Paniola Ranch' in entry['method'] and 'Pokémon Bank transfer' in entry['method']
print('Verified game-specific egg collection facilities for all direct breeding routes')

older=[(key,e) for (key,game),e in routes.items() if game=='Pokémon Ultra Sun / Ultra Moon']
assert len(older)==361
assert all('HOME transfer' not in e['method'] for key,e in older)
assert all('https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9mon_Nursery' in e['sourceReferences'] for key,e in older)
for sid in [19,27,37,50,52,74,88]:assert 'non-Alolan parent an Everstone' in routes[(sid,'Pokémon Ultra Sun / Ultra Moon')]['method']
for sid,incense in [(298,'Sea Incense'),(360,'Lax Incense'),(406,'Rose Incense'),(433,'Pure Incense'),(438,'Rock Incense'),(439,'Odd Incense'),(440,'Luck Incense'),(446,'Full Incense'),(458,'Wave Incense')]:
 assert 'parent must hold '+incense in routes[(sid,'Pokémon Ultra Sun / Ultra Moon')]['method']
assert routes[(489,'Pokémon Ultra Sun / Ultra Moon')]['breedingParent']==490
assert not any(key in {132,490,803,804,807} for key,e in older)
print('Verified 361 older egg routes, Alola form preservation, incense babies and Phione parent')

# Check the emitted parents directly against the pinned Generation VII bytes.
import struct
catalog={p['key']:p for p in json.loads((ROOT/'data.json').read_text())}
raw=(ROOT/'reference/pkhex/PKHeX.Core/Resources/byte/personal/personal_uu').read_bytes()
def gen7_personal(sid,form):
 assert 1<=sid<=807
 base=raw[sid*84:(sid+1)*84]
 assert len(base)==84
 if not form:return base
 first=struct.unpack_from('<H',base,28)[0]
 assert first and form<base[32]
 row=raw[(first+form-1)*84:(first+form)*84]
 assert len(row)==84
 return row
for key,e in older:
 p=catalog[key]
 assert p['id']<=807 and not h[str(key)]['locked']
 assert not p.get('region') or p['region']=='alola'
 gen7_personal(p['id'],e['gameFormId'])
 parent=e['breedingParent']
 row=gen7_personal(parent,e['gameFormId'] if parent==p['id'] else 0)
 assert 15 not in {row[22],row[23]},(key,parent)
 assert 'Pokémon Bank transfer' in e['method']
print('Verified all older egg destinations and breedable parent groups directly against Generation VII personal bytes')

sm=[(key,e) for (key,game),e in routes.items() if game=='Pokémon Sun / Moon']
assert len(sm)==361
raw=(ROOT/'reference/pkhex/PKHeX.Core/Resources/byte/personal/personal_sm').read_bytes()
for key,e in sm:
 p=catalog[key];assert p['id']<=802 and not h[str(key)]['locked']
 assert not p.get('region') or p['region']=='alola'
 gen7_personal(p['id'],e['gameFormId'])
 parent=e['breedingParent'];row=gen7_personal(parent,e['gameFormId'] if parent==p['id'] else 0)
 assert 15 not in {row[22],row[23]}
 assert 'Nursery at Paniola Ranch' in e['method'] and 'HOME transfer' not in e['method']
assert not any(catalog[key]['id'] in {803,804,805,806,807} for key,e in sm)
print('Verified 361 Sun/Moon egg routes against their own personal table; Ultra-only species excluded')

for game,code,size,facility in [('Pokémon X / Y','xy',64,'Day Care on Route 7'),('Pokémon Omega Ruby / Alpha Sapphire','ao',80,'Route 117 or at the Battle Resort')]:
 gen6=[(key,e) for (key,g),e in routes.items() if g==game]
 assert len(gen6)==320
 data=(ROOT/('reference/pkhex/PKHeX.Core/Resources/byte/personal/personal_'+code)).read_bytes()
 for key,e in gen6:
  p=catalog[key];assert p['id']<=721 and not p.get('region') and not h[str(key)]['locked']
  assert e['gameFormId']==0 and facility in e['method'] and 'HOME transfer' not in e['method']
  sid=e['breedingParent'];assert sid<=721
  row=data[sid*size:(sid+1)*size]
  assert len(row)==size and 15 not in {row[22],row[23]}
  assert 'Generation VI or earlier origins' in e['method']
 for baby,incense in [(298,'Sea Incense'),(360,'Lax Incense'),(406,'Rose Incense'),(433,'Pure Incense'),(438,'Rock Incense'),(439,'Odd Incense'),(440,'Luck Incense'),(446,'Full Incense'),(458,'Wave Incense')]:assert 'parent must hold '+incense in routes[(baby,game)]['method']
 assert routes[(489,game)]['breedingParent']==490
print('Verified 640 Gen VI egg routes against game-specific parent groups, facilities, species limits and incense requirements')

for game,code,size in [('Pokémon Black / White','bw',60),('Pokémon Black 2 / White 2','b2w2',76)]:
 gen5=[(key,e) for (key,g),e in routes.items() if g==game];assert len(gen5)==289
 data=(ROOT/('reference/pkhex/PKHeX.Core/Resources/byte/personal/personal_'+code)).read_bytes()
 for key,e in gen5:
  p=catalog[key];assert p['id']<=649 and not p.get('region') and not h[str(key)]['locked']
  assert e['gameFormId']==0 and 'Day Care on Unova Route 3' in e['method']
  if code=='bw':assert 'after receiving the Bicycle in Nimbasa City' in e['method'] and 'postgame hunt' not in e['method']
  else:assert 'postgame hunt' in e['method'] and 'Hall of Fame' in e['method'] and 'Skyarrow Bridge' in e['method']
  assert 'https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9mon_Day_Care' in e['sourceReferences']
  sid=e['breedingParent'];assert sid<=649
  row=data[sid*size:(sid+1)*size];assert len(row)==size and 15 not in {row[22],row[23]}
  assert 'one-way Poké Transfer from Generation IV' in e['method']
  assert 'Bank and HOME cannot send parents' in e['method']
  assert ('do not have the Shiny Charm' if code=='bw' else 'Shiny Charm improves egg shiny odds') in e['method']
 for baby,incense in [(298,'Sea Incense'),(360,'Lax Incense'),(406,'Rose Incense'),(433,'Pure Incense'),(438,'Rock Incense'),(439,'Odd Incense'),(440,'Luck Incense'),(446,'Full Incense'),(458,'Wave Incense')]:assert 'parent must hold '+incense in routes[(baby,game)]['method']
 assert routes[(489,game)]['breedingParent']==490
print('Verified 578 Gen V egg routes, parent groups, incense, transfer direction and version-specific Shiny Charm availability')

for game,code,facility in [('Pokémon Diamond / Pearl','dp','Solaceon Town'),('Pokémon Platinum','pt','Solaceon Town'),('Pokémon HeartGold / SoulSilver','hgss','Johto Route 34')]:
 gen4=[(key,e) for (key,g),e in routes.items() if g==game];assert len(gen4)==220
 data=(ROOT/('reference/pkhex/PKHeX.Core/Resources/byte/personal/personal_'+code)).read_bytes()
 for key,e in gen4:
  p=catalog[key];assert p['id']<=493 and not p.get('region') and not h[str(key)]['locked']
  assert e['gameFormId']==0 and facility in e['method'] and 'Generation IV games do not have the Shiny Charm' in e['method']
  sid=e['breedingParent'];assert sid<=493
  row=data[sid*44:(sid+1)*44];assert len(row)==44 and 15 not in {row[20],row[21]}
  assert 'one-way Pal Park migration from Generation III' in e['method']
 for baby,incense in [(298,'Sea Incense'),(360,'Lax Incense'),(406,'Rose Incense'),(433,'Pure Incense'),(438,'Rock Incense'),(439,'Odd Incense'),(440,'Luck Incense'),(446,'Full Incense'),(458,'Wave Incense')]:assert 'parent must hold '+incense in routes[(baby,game)]['method']
 assert routes[(489,game)]['breedingParent']==490
print('Verified 660 Gen IV egg routes against parent groups, facilities, species limits, incense and transfer direction')

for sid,incense in [(183,'Sea Incense'),(202,'Lax Incense'),(315,'Rose Incense'),(358,'Pure Incense'),(185,'Rock Incense'),(122,'Odd Incense'),(113,'Luck Incense'),(143,'Full Incense'),(226,'Wave Incense')]:
 assert (sid,'Pokémon Brilliant Diamond / Shining Pearl') in routes
 assert 'neither parent may hold '+incense in routes[(sid,'Pokémon Brilliant Diamond / Shining Pearl')]['method']
 assert (sid,'Pokémon Scarlet / Violet') not in routes
print('Verified optional-incense evolved offspring and Scarlet/Violet baby-only behavior')

for (key,game),entry in routes.items():
 if key in {29,32}:
  assert 'either Nidoran species' in entry['method'] and 'Nidorina and Nidoqueen cannot breed' in entry['method']
 if key in {313,314}:
  assert 'either Volbeat or Illumise' in entry['method'] and 'not guaranteed' in entry['method']
print('Verified paired-species offspring and non-breedable Nidorina/Nidoqueen restrictions')
for game in ['Pokémon Diamond / Pearl','Pokémon Platinum','Pokémon HeartGold / SoulSilver']:
 assert 'cannot produce Nidoran♀ in Generation IV' in routes[(29,game)]['method']
 assert 'always hatch Nidoran♂ in Generation IV' in routes[(32,game)]['method']
 assert 'cannot produce Illumise in Generation IV' in routes[(314,game)]['method']
 assert 'always hatch Volbeat in Generation IV' in routes[(313,game)]['method']
 for sid in [29,32,313,314]:
  e=routes[(sid,game)]
  assert 'Personality_value#Gender-counterpart_species' in ' '.join(e['sourceReferences'])
  assert 'or breed Nidoran♂' not in e['method'] and 'or Volbeat with Ditto; eggs can hatch either' not in e['method']
for game in ['Pokémon Black / White','Pokémon Black 2 / White 2','Pokémon X / Y','Pokémon Omega Ruby / Alpha Sapphire']:
 assert 'or breed Nidoran♂, Nidorino or Nidoking with Ditto; eggs can hatch either Nidoran species' in routes[(29,game)]['method']
 assert 'or Volbeat with Ditto; eggs can hatch either Volbeat or Illumise' in routes[(314,game)]['method']
print('Verified Generation IV male-parent offspring restrictions and Generation V onward counterpart eligibility')

entry=routes[(128,'Pokémon Scarlet / Violet')]
assert 'Kantonian Tauros an Everstone' in entry['method'] and 'Combat Breed Paldean Tauros' in entry['method']
for key in [10250,10251,10252]:
 assert 'exact Paldean breed' in routes[(key,'Pokémon Scarlet / Violet')]['method']
print('Verified Tauros exact breed parents and Kantonian Everstone requirement in Paldea')

entry=routes[(194,'Pokémon Scarlet / Violet')]
assert 'Johtonian Wooper or Quagsire parent an Everstone' in entry['method'] and 'otherwise eggs hatch Paldean Wooper' in entry['method']
print('Verified Johtonian Wooper inheritance requirement when breeding in Paldea')

for sid in [81,100,120,137,479]:
 entries=[e for (key,game),e in routes.items() if key==sid]
 assert entries and all('requires Ditto' in e['method'] for e in entries)
entries=[e for (key,game),e in routes.items() if key==236]
assert entries and all('requires Ditto' in e['method'] for e in entries)
assert all('compatible male sharing an Egg Group' in e['method'] for (key,game),e in routes.items() if key==1)
print('Verified Ditto-only parents, Tyrogue parents and compatible female-parent instructions')

assert all('normal egg hunting or Masuda method' in entry['method'] and ('do not have the Shiny Charm' if game in {'Pokémon Black / White','Pokémon Diamond / Pearl','Pokémon Platinum','Pokémon HeartGold / SoulSilver'} else 'Shiny Charm improves egg shiny odds') in entry['method'] for (key,game),entry in routes.items() if game not in gen3_games)
assert all('Sparkling Power does not improve egg shiny odds' in entry['method'] for (key,game),entry in routes.items() if game=='Pokémon Scarlet / Violet')
print('Verified normal/Masuda egg options, Charm modifier and Sparkling Power exclusion')
for game,code in [('Pokémon Ruby / Sapphire','rs'),('Pokémon Emerald','e'),('Pokémon FireRed','fr'),('Pokémon LeafGreen','lg')]:
 data=(ROOT/('reference/pkhex/PKHeX.Core/Resources/byte/personal/personal_'+code)).read_bytes()
 rows=[(key,e) for (key,g),e in routes.items() if g==game]
 assert len(rows)==181
 for key,e in rows:
  assert key<=386 and not catalog[key].get('region') and e['gameFormId']==0
  row=data[e['breedingParent']*28:(e['breedingParent']+1)*28]
  assert len(row)==28 and 15 not in {row[20],row[21]}
  assert 'normal full-odds egg hunting' in e['method'] and 'neither the Masuda method nor the Shiny Charm' in e['method']
  assert 'later generations cannot transfer parents back' in e['method']
  assert ('Four Island' if code in {'fr','lg'} else 'Hoenn Route 117') in e['method']
 assert 'Sea Incense' in routes[(298,game)]['method'] and 'Lax Incense' in routes[(360,game)]['method']
 for sid in [315,358,185,122,113,143,226]:assert (sid,game) in routes and 'Incense' not in routes[(sid,game)]['method']
 assert 'cannot produce Nidoran♀ in Generation III' in routes[(29,game)]['method']
 assert 'cannot produce Illumise in Generation III' in routes[(314,game)]['method']
print('Verified 724 Generation III egg routes, parent groups, pre-baby offspring, facilities and shiny method restrictions')
