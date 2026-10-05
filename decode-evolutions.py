"""Decode pinned evolution branches and resolve source/destination forms.
No reference C# is executed. Conditions remain raw until individually rendered.
"""
import json,re,struct
from pathlib import Path
ROOT=Path(__file__).parent;REF=ROOT/'reference/pkhex'
sha=json.loads((REF/'tree.json').read_text())['sha']
enum=(REF/'PKHeX.Core/Legality/Evolutions/Methods/EvolutionType.cs').read_text()
types={int(n):name for name,n in re.findall(r'^\s*(\w+)\s*=\s*(\d+)\s*,',enum,re.M)}
records=[];audit=[]
for code,personal,size,index,count,present,max_species in [
 ('sv','sv',80,24,26,28,1025),('ss','swsh',176,30,32,33,898),
 ('bs','bdsp',68,30,32,33,493),('la','la',176,30,32,33,905),('za','za',80,24,26,28,1025),
]:
 raw=(REF/('PKHeX.Core/Resources/byte/personal/personal_'+personal)).read_bytes()
 pairs={};presence={}
 for species in range(1,max_species+1):
  at=species*size;row=raw[at:at+size]
  if len(row)!=size:break
  pairs[species]=(species,0)
  presence[(species,0)]=bool(row[present]) if size==80 else bool(row[present]&64)
  first=struct.unpack_from('<H',row,index)[0]
  if not first:continue
  for form in range(1,row[count]):
   slot=first+form-1;r=raw[slot*size:(slot+1)*size]
   assert len(r)==size
   assert slot not in pairs,(code,slot)
   pairs[slot]=(species,form)
   presence[(species,form)]=bool(r[present]) if size==80 else bool(r[present]&64)
 path=REF/('PKHeX.Core/Resources/byte/evolve/evos_'+code+'.pkl');data=path.read_bytes()
 n=struct.unpack_from('<H',data,2)[0];offsets=struct.unpack_from('<'+'H'*(n+1),data,4)
 assert offsets[-1]==len(data) and offsets[0]>=4+2*(n+1)
 start=len(records)
 for slot,(a,b) in enumerate(zip(offsets,offsets[1:])):
  assert a<=b and (b-a)%8==0
  if a==b:continue
  assert slot in pairs,(code,slot)
  species,form=pairs[slot]
  for pos in range(a,b,8):
   block=data[pos:pos+8];kind=block[0];arg,dest=struct.unpack_from('<HH',block,2)
   assert kind in types and 1<=dest<=1025
   destform=form if block[6]==255 else block[6]
   method={48:'UseItemDay',49:'UseItemNight'}.get(kind,types[kind]) if code=='la' else types[kind]
   records.append(dict(gameTable=code,sourceSpecies=species,sourceForm=form,destinationSpecies=dest,destinationForm=destform,evolutionType=method,argument=arg,level=block[7],sourcePresent=presence.get((species,form),False),destinationPresent=presence.get((dest,destform),False),source='https://github.com/kwsch/PKHeX/blob/'+sha+'/'+path.relative_to(REF).as_posix()))
 audit.append(dict(table=code,entries=n,branches=len(records)-start))
(ROOT/'audit/evolution-encounters.json').write_text(json.dumps(records,indent=2))
(ROOT/'audit/evolution-decode-audit.json').write_text(json.dumps(dict(tables=audit,branches=len(records),fullHuntingAuditComplete=False,remaining=['Render and verify all evolution requirements','Validate source shiny acquisition routes','Replace unsupported generic evolution entries']),indent=2))
print('Decoded',len(records),'form-specific evolution branches:',audit)
