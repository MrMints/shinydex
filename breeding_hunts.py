"""Direct shiny egg routes from game-specific personal tables.
Evolution routes remain a separate audit: presence alone does not prove evolution.
"""
import csv,json,struct
from pathlib import Path
from form_mapping import catalog_forms
ROOT=Path(__file__).parent
REF=ROOT/'reference/pkhex'
INCENSE={298:'Sea Incense',360:'Lax Incense',406:'Rose Incense',433:'Pure Incense',438:'Rock Incense',439:'Odd Incense',440:'Luck Incense',446:'Full Incense',458:'Wave Incense'}
INCENSE_PARENTS={183:'Sea Incense',202:'Lax Incense',315:'Rose Incense',358:'Pure Incense',185:'Rock Incense',122:'Odd Incense',113:'Luck Incense',143:'Full Incense',226:'Wave Incense'}
GEN3={'rs','e','fr','lg'}
OLDER_CODES={'sm','uu','xy','ao','bw','b2w2','dp','pt','hgss'}|GEN3

def merge(records,catalog):
 species={int(r['id']):r for r in csv.DictReader((ROOT/'species.csv').open(encoding='utf-8-sig'))}
 names={p['id']:p['displayName'] for p in catalog if not p.get('region')}
 forms=catalog_forms(catalog);sha=json.loads((REF/'tree.json').read_text())['sha'];audit=[]
 for code,game,size,egg,index,count,present in [
  ('sv','Pokémon Scarlet / Violet',80,16,24,26,28),
  ('swsh','Pokémon Sword / Shield',176,22,30,32,33),
  ('bdsp','Pokémon Brilliant Diamond / Shining Pearl',68,22,30,32,33),
  ('uu','Pokémon Ultra Sun / Ultra Moon',84,22,28,32,None),
  ('sm','Pokémon Sun / Moon',84,22,28,32,None),
  ('xy','Pokémon X / Y',64,22,28,32,None),
  ('ao','Pokémon Omega Ruby / Alpha Sapphire',80,22,28,32,None),
  ('bw','Pokémon Black / White',60,22,28,32,None),
  ('b2w2','Pokémon Black 2 / White 2',76,22,28,32,None),
  ('dp','Pokémon Diamond / Pearl',44,20,42,41,None),
  ('pt','Pokémon Platinum',44,20,42,41,None),
  ('hgss','Pokémon HeartGold / SoulSilver',44,20,42,41,None),
  ('rs','Pokémon Ruby / Sapphire',28,20,None,None,None),
  ('e','Pokémon Emerald',28,20,None,None,None),
  ('fr','Pokémon FireRed',28,20,None,None,None),
  ('lg','Pokémon LeafGreen',28,20,None,None,None),
 ]:
  path=REF/'PKHeX.Core/Resources/byte/personal'/('personal_'+code);raw=path.read_bytes()
  assert len(raw)%size==0
  def personal(sid,form=0):
   if code in OLDER_CODES and sid>(386 if code in GEN3 else {'sm':802,'uu':807,'xy':721,'ao':721,'bw':649,'b2w2':649,'dp':493,'pt':493,'hgss':493}[code]):return None
   if (sid+1)*size>len(raw):return None
   base=raw[sid*size:(sid+1)*size]
   if form:
    first=struct.unpack_from('<H',base,index)[0]
    if not first or form>=base[count]:return None
    at=first+form-1;row=raw[at*size:(at+1)*size]
   else:row=base
   if len(row)!=size:return None
   available=True if code in OLDER_CODES else bool(row[present]) if code=='sv' else bool(row[present]&64)
   return row if available else None
  for p in catalog:
   if code in {'xy','ao','bw','b2w2','dp','pt','hgss'}|GEN3 and p.get('region'):continue
   sid=p['id'];form=next(f for (s,f),key in forms.items() if key==p['key'])
   info=personal(sid,form)
   if not info or sid in {132,490}:continue
   fact=species[sid]
   # Direct eggs hatch the unevolved species; babies need a breedable parent.
   has_parent=fact['evolves_from_species_id'] and not (code in GEN3 and int(fact['evolves_from_species_id'])>386)
   if has_parent and not (code!='sv' and sid in INCENSE_PARENTS):continue
   parent=sid
   if sid==489:parent=490
   elif info[egg]==15 or info[egg+1]==15:
    if fact['is_baby']!='1':continue
    parent=next((s for s,r in species.items() if r['evolves_from_species_id']==str(sid) and personal(s)),None)
    if parent is None:continue
   pi=personal(parent,form if parent==sid else 0)
   if not pi or 15 in {pi[egg],pi[egg+1]}:continue
   method='Hatch shiny '+p['displayName']+' eggs · normal egg hunting or Masuda method with parents from different language games; Shiny Charm improves egg shiny odds'
   if code in GEN3:method='Hatch shiny '+p['displayName']+' eggs · normal full-odds egg hunting; Generation III has neither the Masuda method nor the Shiny Charm'
   if code=='bw':method=method.replace('; Shiny Charm improves egg shiny odds','; Black and White do not have the Shiny Charm')
   if code in {'dp','pt','hgss'}:method=method.replace('; Shiny Charm improves egg shiny odds','; Generation IV games do not have the Shiny Charm')
   if sid in {29,32}:
    if code in {'dp','pt','hgss'}|GEN3:
     method+='; breed Nidoran♀ with a compatible partner; these eggs can hatch either Nidoran species, so the target is not guaranteed'
     if sid==32:method+='; alternatively breed Nidoran♂, Nidorino or Nidoking with Ditto, whose eggs always hatch Nidoran♂ in '+('Generation III' if code in GEN3 else 'Generation IV')
     else:method+='; Nidoran♂, Nidorino or Nidoking with Ditto cannot produce Nidoran♀ in '+('Generation III' if code in GEN3 else 'Generation IV')
    else:method+='; breed Nidoran♀ with a compatible partner or breed Nidoran♂, Nidorino or Nidoking with Ditto; eggs can hatch either Nidoran species, so the target is not guaranteed'
    method+='; Nidorina and Nidoqueen cannot breed'
   elif sid in {313,314}:
    if code in {'dp','pt','hgss'}|GEN3:
     method+='; breed Illumise with a compatible partner; these eggs can hatch either Volbeat or Illumise, so the target is not guaranteed'
     if sid==313:method+='; alternatively breed Volbeat with Ditto, whose eggs always hatch Volbeat in '+('Generation III' if code in GEN3 else 'Generation IV')
     else:method+='; Volbeat with Ditto cannot produce Illumise in '+('Generation III' if code in GEN3 else 'Generation IV')
    else:method+='; breed Illumise with a compatible partner or Volbeat with Ditto; eggs can hatch either Volbeat or Illumise, so the target is not guaranteed'
   elif sid==128:
    method+='; breed a Tauros of this exact form with Ditto (Tauros is male-only)'
    if code=='sv' and form==0:method+='; when breeding in Paldea, give Kantonian Tauros an Everstone or the eggs will hatch Combat Breed Paldean Tauros'
    elif code=='sv':method+='; use this exact Paldean breed as the parent; a Kantonian parent cannot produce Blaze or Aqua Breed'
   elif sid==489:method+='; breed Manaphy or Phione with Ditto (offspring are Phione)'
   else:
    if int(species[parent]['gender_rate']) in {-1,0}:method+='; breed '+names[parent]+' with Ditto; this male-only or gender-unknown parent requires Ditto'
    else:method+='; use a female '+names[parent]+' with a compatible male sharing an Egg Group, or '+names[parent]+' with Ditto'
    if p.get('region') and not (sid==550 and form==2):method+='; give the regional parent an Everstone to preserve its regional form'
   if sid==194 and form==0 and code=='sv':method+='; when breeding in Paldea, give the Johtonian Wooper or Quagsire parent an Everstone to preserve Johtonian Wooper; otherwise eggs hatch Paldean Wooper'
   if code in {'sm','uu'} and form==0 and sid in {19,27,37,50,52,74,88}:method+='; give the non-Alolan parent an Everstone to preserve its original form when breeding in Alola'
   if sid in INCENSE_PARENTS and code!='sv' and (code not in GEN3 or sid in {183,202}):method+='; neither parent may hold '+INCENSE_PARENTS[sid]+' or the egg will hatch the baby species instead'
   if sid in INCENSE and code!='sv':method+='; parent must hold '+INCENSE[sid]
   if code=='sv':method+='; Sparkling Power does not improve egg shiny odds'
   if code=='sv':method+='; collect eggs from the picnic basket (Egg Power speeds egg production)'
   elif code=='bdsp':method+='; collect eggs from the Pokémon Nursery in Solaceon Town'
   elif code in {'sm','uu'}:method+='; collect eggs from the Pokémon Nursery at Paniola Ranch; unavailable local parents require a compatible trade or Pokémon Bank transfer'
   elif code=='xy':method+='; collect eggs from the Pokémon Day Care on Route 7'
   elif code=='ao':method+='; collect eggs from the Pokémon Day Care on Route 117 or at the Battle Resort'
   elif code=='bw':method+='; collect eggs from the Pokémon Day Care on Unova Route 3; breeding unlocks after receiving the Bicycle in Nimbasa City, when the Day Care can accept two parents'
   elif code=='b2w2':method+='; collect eggs from the Pokémon Day Care on Unova Route 3; this is a postgame hunt: enter the Hall of Fame before Skyarrow Bridge and the Day Care become accessible'
   elif code in {'dp','pt'}:method+='; collect eggs from the Pokémon Day Care in Solaceon Town'
   elif code=='hgss':method+='; collect eggs from the Pokémon Day Care on Johto Route 34'
   elif code in {'rs','e'}:method+='; collect eggs from the Pokémon Day Care on Hoenn Route 117'
   elif code in {'fr','lg'}:method+='; collect eggs from the two-Pokémon Day Care on Four Island after unlocking the postgame Sevii Islands; the Route 5 Day Care cannot produce eggs'
   else:method+='; collect eggs from a Pokémon Nursery on Route 5 or in Bridge Field'
   if code not in OLDER_CODES:method+='; parents may require a trade or HOME transfer'
   elif code in {'xy','ao'}:method+='; unavailable local parents require a compatible trade or Pokémon Bank transfer from compatible Generation VI or earlier origins'
   elif code in {'bw','b2w2'}:method+='; unavailable local parents require a compatible Generation V trade or a one-way Poké Transfer from Generation IV; Pokémon Bank and HOME cannot send parents into these games'
   elif code in {'dp','pt','hgss'}:method+='; unavailable local parents require a compatible Generation IV trade or one-way Pal Park migration from Generation III; Pokémon Bank and HOME cannot send parents into these games'
   elif code in GEN3:method+='; unavailable local parents require a compatible Generation III trade; later generations cannot transfer parents back into these games'
   source='https://github.com/kwsch/PKHeX/blob/'+sha+'/'+path.relative_to(REF).as_posix()
   records[str(p['key'])]['entries'].append(dict(game=game,method=method,status='Huntable',locations=[],source=source,sourceReferences=[source,'https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9mon_breeding','https://bulbapedia.bulbagarden.net/wiki/Shiny_Charm'],breedingKind='direct-egg',gameFormId=form,breedingParent=parent,verification='Game-specific presence and parent egg groups checked; direct offspring only'))
   if sid in {29,32,313,314}:records[str(p['key'])]['entries'][-1]['sourceReferences'].append('https://bulbapedia.bulbagarden.net/wiki/Personality_value#Gender-counterpart_species')
   if code in {'bw','b2w2'}|GEN3:records[str(p['key'])]['entries'][-1]['sourceReferences'].append('https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9mon_Day_Care')
   if code in {'sm','uu'}:records[str(p['key'])]['entries'][-1]['sourceReferences'].extend(['https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9mon_Nursery','https://home.pokemon.com/en-gb/move/'])
   audit.append(dict(key=p['key'],game=game,form=form,parent=parent))
 (ROOT/'breeding-audit.json').write_text(json.dumps(dict(directEggRoutes=audit,routeCount=len(audit),fullHuntingAuditComplete=False,remaining=['Exact evolution requirements','Older game breeding availability','Form inheritance exceptions and parent acquisition prerequisites']),indent=2))
 return len(audit)
