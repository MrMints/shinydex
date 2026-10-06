import csv,json,re
from living_forms import extend_catalog
from pathlib import Path
from urllib.parse import quote
ROOT=Path(__file__).parent
def rows(file):return list(csv.DictReader(open(ROOT/file,encoding='utf-8-sig')))
old=json.loads((ROOT/'data.json').read_text());base={p['id']:p for p in old if not p.get('region') and not p.get('livingForm')}
names={int(r['pokemon_species_id']):r['name'] for r in rows('pokemon_species_names.csv') if r['local_language_id']=='9'}
registry={f['name']:f for f in json.loads((ROOT/'audit/archives-images.json').read_text())}
types={};tn=['','normal','fighting','flying','poison','ground','rock','bug','ghost','steel','fire','water','grass','electric','psychic','ice','dragon','dark','fairy']
for r in rows('types.csv'):types.setdefault(int(r['pokemon_id']),[]).append(tn[int(r['type_id'])])
result=[]
def finalize(p,suffix=''):
 p['key']=p.get('key',p['id']);p['speciesName']=names[p['id']];p['displayName']=p.get('displayName',names[p['id']]);p['source']='https://bulbapedia.bulbagarden.net/wiki/'+quote(names[p['id']].replace('’',"'")+'_(Pokémon)')
 for mode,s in [('normal',''),('shiny','_s')]:
  f=f'HOME{p["id"]:04}{suffix}{s}.png'
  if p['id']==774:f='HOME0774R'+s+'.png'
  if f not in registry:raise ValueError(f'Missing {f}')
  p[mode+'File']=f;p[mode+'Source']=registry[f]['descriptionurl'];p[mode]=f'./assets/pokemon/{f}'
  p.pop(mode+'Fallback',None)
 result.append(p)
for p in base.values():finalize(p)
regional=[]
for r in rows('pokemon.csv'):
 identifier=r['identifier']
 if re.search(r'-(alola|galar|hisui)$',identifier) or '-paldea-' in identifier or identifier=='wooper-paldea' or identifier=='darmanitan-galar-standard' or identifier=='basculin-white-striped':
  if 'totem' in identifier:continue
  regional.append(r)
for r in regional:
 sid=int(r['species_id']);pid=int(r['id']);identifier=r['identifier'];region=next((x for x in ['alola','galar','hisui','paldea'] if x in identifier),'hisui');label={'alola':'Alolan','galar':'Galarian','hisui':'Hisuian','paldea':'Paldean'}[region]
 suffix={'alola':'A','galar':'G','hisui':'H','paldea':'P'}[region]
 if sid==128:
  breed=next(x for x in ['combat','blaze','aqua'] if x in identifier);suffix='P'+{'combat':'C','blaze':'B','aqua':'A'}[breed];label+=f' · {breed.title()} Breed'
 if sid==550:suffix='W';label='White-Striped · Hisui'
 p={'id':sid,'key':pid,'name':identifier,'displayName':names[sid]+' · '+label,'region':region,'formLabel':label,'generation':7 if region=='alola' else 9 if region=='paldea' else 8,'sprite':pid,'height':int(r['height']),'weight':int(r['weight']),'types':types[pid]}
 finalize(p,suffix)
region_order={'':0,'alola':1,'galar':2,'hisui':3,'paldea':4}
result=extend_catalog(result)
result.sort(key=lambda p:(p['id'],region_order.get(p.get('region',''),0),p['key']))
slot=0
for p in result:
 if p.get('formUnspecified'):p['position']=None
 else:p['position']=slot;slot+=1
(ROOT/'data.json').write_text(json.dumps(result,separators=(',',':')),encoding='utf-8')
print('Catalog:',len(base),'species +',len(regional),'regional forms =',len(result),'entries')
