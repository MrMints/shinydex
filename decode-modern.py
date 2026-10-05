"""Decode reference encounter bytes following PKHeX's documented readers.
The .pkl resources are binary tables, never Python pickle objects.
"""
import json,struct
from pathlib import Path
ROOT=Path(__file__).parent
REF=ROOT/'reference/pkhex'
SHA=json.loads((REF/'tree.json').read_text())['sha']
def linked(path,width=4):
 data=path.read_bytes();count=struct.unpack_from('<H',data,2)[0]
 offsets=struct.unpack_from('<'+('I' if width==4 else 'H')*(count+1),data,4)
 assert offsets[0]>=4+width*(count+1) and offsets[-1]==len(data)
 assert all(a<=b for a,b in zip(offsets,offsets[1:]))
 return [data[a:b] for a,b in zip(offsets,offsets[1:])]
def source(path):return 'https://github.com/kwsch/PKHeX/blob/'+SHA+'/'+path.relative_to(REF).as_posix()
records=[];audits=[]
path=REF/'PKHeX.Core/Resources/legality/wild/Gen9/encounter_fixed_paldea.pkl'
data=path.read_bytes()
assert len(data)%20==0
locations=(REF/'PKHeX.Core/Resources/text/locations/gen9/text_sv_00000_en.txt').read_text(encoding='utf-8-sig').splitlines()
for offset in range(0,len(data),20):
 block=data[offset:offset+20]
 species=struct.unpack_from('<H',block)[0];form=block[2];level=block[3]
 assert 1<=species<=1025 and 1<=level<=100
 for location in sorted(set(block[16:20])-{0}):
  assert location<len(locations)
  records.append(dict(species=species,form=form,game='Pokémon Scarlet / Violet',location=locations[location].strip() or 'Encounter location #'+str(location),locationId=location,levelMin=level,levelMax=level,shiny='Random',kind='sv-fixed',alpha=False,source=source(path)))
audits.append(dict(file=path.name,serializedRecords=len(data)//20,slots=len(records)))
path=REF/'PKHeX.Core/Resources/legality/wild/Gen9/encounter_outbreak_paldea.pkl'
data=path.read_bytes();start=len(records)
assert len(data)%28==0
for offset in range(0,len(data),28):
 block=data[offset:offset+28]
 species=struct.unpack_from('<H',block)[0];form=block[2];low=block[4];high=block[5]
 assert 1<=species<=1025 and 1<=low<=high<=100 and block[11] in {0,1}
 base=block[12];flags=int.from_bytes(block[12:28],'little')>>8
 assert flags
 for bit in range(120):
  if not flags&(1<<bit):continue
  location=base+bit
  assert location<len(locations)
  records.append(dict(species=species,form=form,game='Pokémon Scarlet / Violet',location=locations[location].strip() or 'Encounter location #'+str(location),locationId=location,levelMin=low,levelMax=high,shiny='Always' if block[11] else 'Random',kind='sv-event-outbreak',alpha=False,source=source(path)))
audits.append(dict(file=path.name,serializedRecords=len(data)//28,slots=len(records)-start))
for filename,game,locset,width,kind in [
 ('encounter_wild_paldea.pkl','Pokémon Scarlet / Violet','gen9/text_sv',4,'sv'),
 ('encounter_za.pkl','Pokémon Legends: Z-A','gen9a/text_za',2,'za'),
 ('encounter_hyperspace_za.pkl','Pokémon Legends: Z-A · Mega Dimension','gen9a/text_za',2,'hyperspace'),
]:
 path=REF/'PKHeX.Core/Resources/legality/wild/Gen9'/filename
 locations=(REF/('PKHeX.Core/Resources/text/locations/'+locset+'_00000_en.txt')).read_text(encoding='utf-8-sig').splitlines()
 blocks=linked(path,width);start=len(records)
 for block in blocks:
  assert len(block)>=4 and (len(block)-4)%8==0
  location=(block[2] or block[0]) if kind=='sv' else struct.unpack_from('<H',block)[0]
  assert location<len(locations),(filename,location)
  location_name=locations[location].strip() or 'Encounter location #'+str(location)
  for offset in range(4,len(block),8):
   species,form,gender,low,high,extra,flag=struct.unpack_from('<H6B',block,offset)
   assert 1<=species<=1025 and 1<=low<=high<=100
   shiny='Random' if kind=='sv' else {0:'Random',1:'Never',2:'Always',3:'AlwaysStar',4:'AlwaysSquare'}[flag]
   records.append(dict(species=species,form=form,game=game,location=location_name,locationId=location,levelMin=low,levelMax=high,shiny=shiny,kind=kind,alpha=kind!='sv' and extra==1,source=source(path)))
 audits.append(dict(file=filename,areas=len(blocks),slots=len(records)-start))
path=REF/'PKHeX.Core/Resources/legality/wild/Gen8/encounter_la.pkl'
locations=(REF/'PKHeX.Core/Resources/text/locations/gen8a/text_la_00000_en.txt').read_text(encoding='utf-8-sig').splitlines()
blocks=linked(path);start=len(records)
for block in blocks:
 location_count=block[0];location_ids=list(block[1:1+location_count]);align=location_count+1;align+=align&1
 kind,count=block[align:align+2];slot_end=align+2+count*8
 assert kind<=4 and len(block)-slot_end in {0,2} and not any(block[slot_end:])
 for offset in range(align+2,slot_end,8):
  species,form,alpha,low,high,gender,flawless=struct.unpack_from('<H6B',block,offset)
  assert 1<=species<=905 and 1<=low<=high<=100 and alpha<=2
  for location in location_ids:
   assert location<len(locations)
   records.append(dict(species=species,form=form,game='Pokémon Legends: Arceus',location=locations[location].strip() or 'Encounter location #'+str(location),displayLocation=locations[location_ids[0]].strip() or 'Encounter location #'+str(location_ids[0]),locationId=location,levelMin=low,levelMax=high,shiny='Random',kind='la-'+str(kind),alpha=alpha,source=source(path)))
audits.append(dict(file=path.name,areas=len(blocks),slots=len(records)-start))
for code,game in [('bd','Pokémon Brilliant Diamond'),('sp','Pokémon Shining Pearl')]:
 for underground in [False,True]:
  filename='encounter_'+code+('_underground' if underground else '')+'.pkl'
  path=REF/'PKHeX.Core/Resources/legality/wild/Gen8'/filename
  locations=(REF/'PKHeX.Core/Resources/text/locations/gen8b/text_bdsp_00000_en.txt').read_text(encoding='utf-8-sig').splitlines()
  blocks=linked(path);start=len(records)
  for block in blocks:
   location=struct.unpack_from('<H',block)[0];kind=block[2]
   assert kind<=8 and len(block)>=4 and (len(block)-4)%4==0
   assert location<len(locations)
   for offset in range(4,len(block),4):
    packed,low,high=struct.unpack_from('<H2B',block,offset);species=packed&0x3ff;form=packed>>11
    assert 1<=species<=493 and 1<=low<=high<=100
    records.append(dict(species=species,form=form,game=game,location=locations[location].strip() or 'Encounter location #'+str(location),locationId=location,levelMin=low,levelMax=high,shiny='Random',kind='bdsp-'+('underground' if underground else str(kind)),alpha=False,source=source(path)))
  audits.append(dict(file=filename,areas=len(blocks),slots=len(records)-start))
for code,game in [('sn','Sun'),('mn','Moon'),('us','Ultra Sun'),('um','Ultra Moon')]:
 path=REF/('PKHeX.Core/Resources/legality/wild/Gen7/encounter_'+code+'.pkl')
 locations=(REF/'PKHeX.Core/Resources/text/locations/gen7/text_sm_00000_en.txt').read_text(encoding='utf-8-sig').splitlines()
 blocks=linked(path);start=len(records)
 for block in blocks:
  location=struct.unpack_from('<H',block)[0];kind=block[2]
  assert kind<=1 and len(block)>=4 and (len(block)-4)%4==0
  location_name='Poké Pelago · Isle Abeens' if location==30016 else locations[location].strip() if location<len(locations) else 'Encounter location #'+str(location)
  for offset in range(4,len(block),4):
   packed,low,high=struct.unpack_from('<H2B',block,offset);species=packed&0x3ff;form=packed>>11
   assert 0<=species<=807 and 1<=low<=high<=100
   if species==0:
    assert packed==0
    continue # Empty encounter slot: species 0 is not a Pokémon.
   records.append(dict(species=species,form=form,game='Pokémon '+game,location=location_name or 'Encounter location #'+str(location),locationId=location,levelMin=low,levelMax=high,shiny='Random',kind='pelago' if location==30016 else 'alola-'+str(kind),alpha=False,source=source(path)))
 audits.append(dict(file=path.name,areas=len(blocks),slots=len(records)-start))
weather_names=['Clear','Overcast','Rain','Thunderstorm','Intense sun','Snow','Snowstorm','Sandstorm','Fog']
for code,game in [('sw','Sword'),('sh','Shield')]:
 for table in ['symbol','hidden']:
  path=REF/('PKHeX.Core/Resources/legality/wild/Gen8/encounter_'+code+'_'+table+'.pkl')
  locations=(REF/'PKHeX.Core/Resources/text/locations/gen8/text_swsh_00000_en.txt').read_text(encoding='utf-8-sig').splitlines()
  blocks=linked(path);start=len(records)
  for block in blocks:
   location,total=block[:2];offset=2;seen=0
   assert location<len(locations)
   while seen<total:
    flags,low,high,count,slot_type=struct.unpack_from('<H4B',block,offset);offset+=6
    assert count and 1<=low<=high<=100 and slot_type<=13
    kind='swsh-'+str(slot_type)
    if flags&1024 or slot_type==12:kind='swsh-fishing'
    elif flags&512:kind='swsh-tree'
    weather=[name for i,name in enumerate(weather_names) if flags&(1<<i)]
    locname=locations[location].strip() or 'Encounter location #'+str(location)
    if weather and flags&511!=511:locname+=' · '+', '.join(weather)
    for _ in range(count):
     packed=struct.unpack_from('<H',block,offset)[0];offset+=2;seen+=1
     species=packed&0x3ff;form=packed>>11
     assert 1<=species<=898
     records.append(dict(species=species,form=form,game='Pokémon '+game,location=locname,locationId=location,levelMin=low,levelMax=high,shiny='Random',kind=kind,alpha=False,source=source(path)))
    assert seen<=total
   assert len(block)-offset in {0,2} and not any(block[offset:])
  audits.append(dict(file=path.name,areas=len(blocks),slots=len(records)-start))
(ROOT/'audit/modern-wild.json').write_text(json.dumps(records,separators=(',',':')))
(ROOT/'audit/modern-decode-audit.json').write_text(json.dumps(audits,indent=2))
print('Decoded modern wild records:',len(records),audits)
