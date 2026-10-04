"""Sun/Moon evolution routes explicitly checked against location references."""
import json,struct
from pathlib import Path
from form_mapping import catalog_forms
GAME='Pokémon Sun / Moon'
ROUTES=[
 (82,462,'level up in the special magnetic field at Vast Poni Canyon','Vast_Poni_Canyon'),
 (299,476,'level up in the special magnetic field at Vast Poni Canyon','Vast_Poni_Canyon'),
 (737,738,'level up in the special magnetic field at Vast Poni Canyon','Vast_Poni_Canyon'),
 (133,470,'level up near the Moss Rock in Lush Jungle','Lush_Jungle'),
 (133,471,'level up near the Ice Rock inside the cave on Mount Lanakila; access requires defeating Lusamine in the story','Mount_Lanakila'),
 (739,740,'level up on Mount Lanakila; access requires defeating Lusamine in the story','Mount_Lanakila'),
]
def merge(records,catalog):
 names={p['id']:p['displayName'] for p in catalog if not p.get('region')}
 forms=catalog_forms(catalog);pairs={key:pair for pair,key in forms.items()}
 root=Path(__file__).parent;ref=root/'reference/pkhex'
 raw=(ref/'PKHeX.Core/Resources/byte/personal/personal_sm').read_bytes()
 sha=json.loads((ref/'tree.json').read_text())['sha']
 reader='https://github.com/kwsch/PKHeX/blob/'+sha+'/PKHeX.Core/Legality/Evolutions/EvolutionTree.cs'
 personal_source='https://github.com/kwsch/PKHeX/blob/'+sha+'/PKHeX.Core/Resources/byte/personal/personal_sm'
 def supported(sid,form):
  if sid>802:return False
  row=raw[sid*84:(sid+1)*84]
  return len(row)==84 and (form==0 or (struct.unpack_from('<H',row,28)[0]>0 and form<row[32]))
 count=0
 for key,guide in records.items():
  for entry in list(guide['entries']):
   if entry.get('olderEvolutionKind') not in {'level-only','trade','item','move','condition','gender-time','party-stat','special'}:continue
   if entry['olderEvolutionType'] in {'UseItemWormhole','LevelUpVersionDay'}:continue
   parent=entry['evolutionParent'];child=int(key)
   if parent not in pairs or child not in pairs or not supported(*pairs[parent]) or not supported(*pairs[child]):continue
   kind=entry['olderEvolutionKind']
   method=entry['method'].replace('in Alola, outside Ultra Space','in Alola').replace('Ultra Sun and Ultra Moon cannot raise Beauty themselves','Sun and Moon cannot raise Beauty themselves')
   copied=dict(entry,game=GAME,method=method,olderEvolutionKind='sun-moon-level' if kind=='level-only' else 'sun-moon-'+kind,sourceReferences=entry['sourceReferences']+[reader,personal_source],verification='Shared Generation VII evolution requirement plus Sun/Moon species/form support checked; Ultra Space branches excluded and parent acquisition remains under audit')
   guide['entries'].append(copied);count+=1
 for parent,child,requirement,page in ROUTES:
  source='https://bulbapedia.bulbagarden.net/wiki/'+page
  records[str(child)]['entries'].append(dict(game=GAME,method='Obtain shiny '+names[parent]+'; '+requirement+' to evolve into '+names[child]+'; the parent may require a compatible trade or Pokémon Bank transfer',status='Huntable',locations=[],source=source,sourceReferences=[source],olderEvolutionKind='sun-moon-location',evolutionParent=parent,verification='Sun/Moon location requirement verified from Bulbapedia; parent acquisition remains under audit'))
 source='https://bulbapedia.bulbagarden.net/wiki/Lycanroc#Evolution_data'
 records['745']['entries'].append(dict(game='Pokémon Sun',method='Obtain shiny Rockruff; level up at level 25 or higher during the in-game day in Pokémon Sun to evolve into Midday Form Lycanroc; this evolution cannot be performed in Pokémon Moon',status='Huntable',locations=[],source=source,olderEvolutionKind='sun-moon-version',evolutionParent=744,verification='Version and time requirement checked against Bulbapedia; shiny parent acquisition remains under audit'))
 return count+len(ROUTES)+1
