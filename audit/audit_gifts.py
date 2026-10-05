"""Cross-check uncertain gift records against pinned encounter definitions."""

# Audit tools resolve shared inputs from the repository, regardless of launch directory.
import os as _audit_os
import sys as _audit_sys
from pathlib import Path as _AuditPath
_audit_root = _AuditPath(__file__).resolve().parents[1]
_audit_sys.path.insert(0, str(_audit_root))
_audit_os.chdir(_audit_root)

import json,struct
from gift_exceptions import resolve
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
def verify(records,catalog):
 facts=json.loads((ROOT/'audit/static-index.json').read_text())
 ref=ROOT/'reference/pkhex';sha=json.loads((ref/'tree.json').read_text())['sha']
 pelago={}
 for code,game in [('sn','Sun'),('mn','Moon'),('us','Ultra Sun'),('um','Ultra Moon')]:
  path=ref/('PKHeX.Core/Resources/legality/wild/Gen7/encounter_'+code+'.pkl');blob=path.read_bytes()
  count=struct.unpack_from('<H',blob,2)[0];offsets=struct.unpack_from('<'+'I'*(count+1),blob,4)
  members=set()
  for start,end in zip(offsets,offsets[1:]):
   if struct.unpack_from('<H',blob,start)[0]!=30016:continue
   assert (end-start-4)%4==0
   for offset in range(start+4,end,4):
    packed=struct.unpack_from('<H',blob,offset)[0]
    if packed>>11==0:members.add(packed&0x3ff)
  pelago['Pokémon '+game]=(members,'https://github.com/kwsch/PKHeX/blob/'+sha+'/'+path.relative_to(ref).as_posix())
 resolved=[];unresolved=[]
 states={'Random':'Huntable','Never':'Shiny Locked','Always':'Guaranteed shiny','AlwaysStar':'Guaranteed shiny','AlwaysSquare':'Guaranteed shiny'}
 for p in catalog:
  for entry in records[str(p['key'])]['entries']:
   if entry['status']!='Check gift/event shiny restrictions':continue
   if entry['locations']==['Poke Pelago'] and entry['game'] in pelago and p['id'] in pelago[entry['game']][0]:
    entry.update(status='Huntable',method='Poké Pelago · befriend a shiny Pokémon visiting Isle Abeens',source=pelago[entry['game']][1],verification='Species present in Poké Pelago encounter table; EncounterSlot7 permits random shininess')
    resolved.append({'name':p['displayName'],'game':entry['game'],'status':entry['status'],'source':entry['source']});continue
   if entry['locations']==['Heahea Beach']:
    totems=[f for f in facts if f['species']==p['id'] and entry['game'] in f['games'] and f['location']==202 and f['form']>0 and f['gift']]
    if totems and all(f['shiny']=='Never' for f in totems):
     entry.update(status='Shiny Locked',method='Totem-sized Pokémon gift from Samson Oak',source=totems[0]['source'],verification='Matched species, game and Heahea Beach Totem gift')
     resolved.append({'name':p['displayName'],'game':entry['game'],'status':entry['status'],'source':entry['source']});continue
   candidates=[f for f in facts if f['species']==p['id'] and entry['game'] in f['games'] and f['form']==0 and (not f['type'].startswith('EncounterTrade') or f['gift'])]
   if entry['method']=='Gift egg':candidates=[f for f in candidates if f['egg']]
   elif entry['method']=='Gift Pokémon / soft reset':
    direct=[f for f in candidates if not f['egg']]
    if direct:candidates=direct
    elif candidates and all(f['egg'] for f in candidates):entry['method']='Gift egg · hatch and check for shininess'
   if 'Colosseum Bonus Disc Jpn'==entry['method']:
    candidates=[f for f in facts if f['species']==p['id'] and f['type']=='EncounterGift3Colo']
   if entry['locations']==['Pallet Town'] and p['id'] in {25,133} and "Let's Go" in entry['game']:
    candidates=[f for f in facts if f['species']==p['id'] and entry['game'] in f['games'] and f['gift'] and f['form']>0]
    entry['method']='Partner starter gift'
   if entry['game'] in {'Pokémon Omega Ruby','Pokémon Alpha Sapphire'} and p['id']==25:
    candidates=[f for f in facts if f['species']==25 and entry['game'] in f['games'] and f['gift'] and f['form']>0]
    entry['method']='Cosplay Pikachu contest gift'
   # In Gen II every static uses Poké Balls, without a separate Gift flag.
   candidates=[f for f in candidates if f['gift'] or f['egg'] or f['type']=='EncounterStatic2']
   statuses={f['shiny'] for f in candidates}
   exception=resolve(p,entry,ref,sha,facts)
   if exception:
    entry.update(exception)
    resolved.append({'name':p['displayName'],'game':entry['game'],'status':entry['status'],'source':entry['source']});continue
   if entry['method']=='Gift egg' and entry['game']=='Pokémon Crystal' and statuses=={'Always','Never'}:
    entry.update(status='Huntable',method='Odd Egg from the Day-Care Man · hatch and check for shininess',source=candidates[0]['source'],verification='Odd Egg table contains both shiny and non-shiny outcomes')
    resolved.append({'name':p['displayName'],'game':entry['game'],'status':entry['status'],'source':entry['source']});continue
   if len(statuses)==1 and next(iter(statuses)) in states:
    entry['status']=states[next(iter(statuses))]
    entry['source']=candidates[0]['source']
    entry['verification']='Matched game, species and gift/egg category against explicit encounter shiny specification'
    resolved.append({'name':p['displayName'],'game':entry['game'],'status':entry['status'],'source':entry['source']})
   else:unresolved.append({'name':p['displayName'],'id':p['id'],'game':entry['game'],'method':entry['method'],'locations':entry['locations'],'candidateStatuses':sorted(statuses)})
 (ROOT/'audit/gift-audit.json').write_text(json.dumps({'resolved':resolved,'unresolved':unresolved},indent=2))
 return len(resolved),len(unresolved)
if __name__=='__main__':
 records=json.loads((ROOT/'hunts.json').read_text());catalog=json.loads((ROOT/'data.json').read_text());print('Gift audit:',verify(records,catalog));
 (ROOT/'hunts.json').write_text(json.dumps(records,separators=(',',':')))
