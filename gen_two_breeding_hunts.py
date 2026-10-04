"""Direct Generation II egg routes with DV inheritance requirements."""
import csv,json
from pathlib import Path
ROOT=Path(__file__).parent
def merge(records,catalog):
 species={int(r['id']):r for r in csv.DictReader((ROOT/'species.csv').open(encoding='utf-8-sig'))}
 names={p['id']:p['displayName'] for p in catalog if not p.get('region')};count=0
 for code,game in [('gs','Pokémon Gold'),('gs','Pokémon Silver'),('c','Pokémon Crystal')]:
  raw=(ROOT/('reference/pkhex/PKHeX.Core/Resources/byte/personal/personal_'+code)).read_bytes()
  def groups(sid):
   assert 1<=sid<=251
   value=raw[sid*32+23];return {value&15,value>>4}
  for sid in range(1,252):
   if sid==132:continue
   fact=species[sid];previous=fact['evolves_from_species_id']
   if previous and int(previous)<=251:continue
   parent=sid
   if 15 in groups(parent):
    if fact['is_baby']!='1':continue
    parent=next(s for s,f in species.items() if s<=251 and f['evolves_from_species_id']==str(sid) and 15 not in groups(s))
   method='Hatch shiny '+names[sid]+' eggs; breed '+names[parent]+' with a compatible Ditto at the Pokémon Day Care on Johto Route 34'
   method+='; use Ditto with Defense DV 10 and Special DV 2 or 10 (a shiny Ditto qualifies) for a 1/64 shiny chance per egg; a non-shiny Ditto can also have these DVs'
   method+='; the pair cannot breed if both parents have the same Defense DV and their Special DVs are equal or differ by 8; two shiny parents cannot breed'
   method+='; without Ditto, compatible opposite-gender parents pass DVs from the parent opposite the offspring’s gender, so shiny eligibility depends on that parent’s DVs; Generation II has no Masuda method or Shiny Charm'
   if sid in {29,32}:method+='; Nidoran eggs can hatch either species; Nidorina and Nidoqueen cannot breed'
   if int(fact['gender_rate'])==1:method+='; this species has a 7:1 male/female ratio, so only males can be shiny in Generation II'
   source='https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9mon_breeding#Generation_II'
   records[str(sid)]['entries'].append(dict(game=game,method=method,status='Huntable',locations=[],source=source,sourceReferences=[source,'https://bulbapedia.bulbagarden.net/wiki/Shiny_Pok%C3%A9mon','https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9mon_Day_Care'],breedingKind='gen-two-dv-egg',breedingParent=parent,gameFormId=0,verification='Generation II parent egg groups and DV gameplay rules checked; parent acquisition remains under audit'))
   count+=1
 return count
