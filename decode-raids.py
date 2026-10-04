"""Decode raid reference resources using their pinned C# reader layouts."""
import json,re,struct
from pathlib import Path
ROOT=Path(__file__).parent;REF=ROOT/'reference/pkhex'
SHA=json.loads((REF/'tree.json').read_text())['sha']
def source(path):return 'https://github.com/kwsch/PKHeX/blob/'+SHA+'/'+path.relative_to(REF).as_posix()
def chunks(path,size):
 data=path.read_bytes();assert len(data)%size==0,(path,len(data),size)
 return [data[i:i+size] for i in range(0,len(data),size)]
def shiny(flag):return {0:'Random',1:'Never',2:'Always'}[flag]
records=[];audit=[]
nest_source=REF/'PKHeX.Core/Legality/Encounters/Data/Gen8/Encounters8Nest.cs'
nest_body=re.search(r'GetNestLocations\(byte nestIndex\) => nestIndex switch\s*\{(.*?)\n\s*\};',nest_source.read_text(encoding='utf-8-sig'),re.S)[1]
den_locations={int(i):[int(v) for v in values.split(',') if v.strip()] for i,values in re.findall(r'(?m)^\s*(\d{3})\s*=>\s*\[([\d, ]*)\]',nest_body)}
names=(REF/'PKHeX.Core/Resources/text/locations/gen8/text_swsh_00000_en.txt').read_text(encoding='utf-8-sig').splitlines()
for code,game in [('sw','Pokémon Sword'),('sh','Pokémon Shield')]:
 for kind,size in [('nest',10),('dist',16)]:
  path=REF/('PKHeX.Core/Resources/legality/wild/Gen8/encounter_'+code+'_'+kind+'.pkl');rows=chunks(path,size)
  for raw in rows:
   species=struct.unpack_from('<H',raw)[0];form=raw[2];assert 1<=species<=898
   if kind=='nest':
    den,minrank,maxrank=raw[6:9];assert 0<=minrank<=maxrank<=4 and den in den_locations
    for location in den_locations[den]:
     assert location<len(names) and names[location].strip()
     records.append(dict(species=species,form=form,game=game,kind='max-raid',shiny='Random',den=den,stars=list(range(minrank+1,maxrank+2)),locationId=location,location=names[location],gigantamax=bool(raw[5]),source=source(path)))
   else:
    flag=raw[14]>>4;assert flag<=2 and 1<=raw[12]<=100
    records.append(dict(species=species,form=form,game=game,kind='max-raid-event',shiny=shiny(flag),eventIndex=raw[15],level=raw[12],locationId=0,location='Distributed Max Raid den',gigantamax=raw[13]>=128,source=source(path)))
  audit.append(dict(file=path.name,serializedEntries=len(rows),entrySize=size))
path=REF/'PKHeX.Core/Resources/legality/wild/Gen8/encounter_swsh_underground.pkl';rows=chunks(path,14)
for raw in rows:
 species=struct.unpack_from('<H',raw)[0];assert 1<=species<=898 and 1<=raw[3]<=100
 records.append(dict(species=species,form=raw[2],game='Pokémon Sword / Shield · The Crown Tundra',kind='dynamax-adventure',shiny='Random',level=raw[3],locationId=244,location='Max Lair',gigantamax=bool(raw[13]),source=source(path)))
audit.append(dict(file=path.name,serializedEntries=len(rows),entrySize=14))
for area,label in [('paldea','Paldea'),('kitakami','Kitakami · The Teal Mask'),('blueberry','Terarium · The Indigo Disk')]:
 path=REF/('PKHeX.Core/Resources/legality/wild/Gen9/encounter_gem_'+area+'.pkl');rows=chunks(path,24)
 for raw in rows:
  species=struct.unpack_from('<H',raw)[0];assert 1<=species<=1025 and raw[6]<=2 and 1<=raw[18]<=6
  scarlet,violet=struct.unpack_from('<hh',raw,20)
  assert scarlet>=-1 and violet>=-1 and (scarlet!=-1 or violet!=-1)
  records.append(dict(species=species,form=raw[2],game='Pokémon Scarlet / Violet',kind='tera-raid',shiny=shiny(raw[6]),stars=[raw[18]],hostVersions=[g for g,v in [('Scarlet',scarlet),('Violet',violet)] if v!=-1],locationId=0,location=label,source=source(path)))
 audit.append(dict(file=path.name,serializedEntries=len(rows),entrySize=24))
for table,kind in [('dist','tera-raid-event'),('might','tera-raid-mightiest')]:
 path=REF/('PKHeX.Core/Resources/legality/wild/Gen9/encounter_'+table+'_paldea.pkl');rows=chunks(path,62)
 for raw in rows:
  species=struct.unpack_from('<H',raw)[0];assert 1<=species<=1025 and raw[6]<=2 and 1<=raw[18]<=7
  totals=struct.unpack_from('<16H',raw,20)
  hosts=[g for i,g in [(2,'Scarlet'),(3,'Violet')] if any(totals[i+4*stage] for stage in range(4))]
  assert hosts
  records.append(dict(species=species,form=raw[2],game='Pokémon Scarlet / Violet',kind=kind,shiny=shiny(raw[6]),stars=[raw[18]],hostVersions=hosts,eventIndex=raw[17],locationId=0,location='Event Tera Raid crystal',source=source(path)))
 audit.append(dict(file=path.name,serializedEntries=len(rows),entrySize=62))
(ROOT/'raid-encounters.json').write_text(json.dumps(records,separators=(',',':')))
(ROOT/'raid-decode-audit.json').write_text(json.dumps(audit,indent=2))
print('Decoded raid records:',len(records),audit)
