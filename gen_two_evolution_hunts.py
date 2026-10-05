"""Generation II level routes decoded from its own table."""
import json
from pathlib import Path
ROOT=Path(__file__).parent
GAMES=[('gs','Pokémon Gold'),('gs','Pokémon Silver'),('c','Pokémon Crystal')]
FRIENDSHIP={(42,169),(113,242),(133,196),(133,197),(172,25),(173,35),(174,39),(175,176)}
HELD={186:"King's Rock",199:"King's Rock",208:'Metal Coat',212:'Metal Coat',230:'Dragon Scale',233:'Up-Grade'}
def merge(records,catalog):
 names={p['id']:p['displayName'] for p in catalog if not p.get('region')};count=0
 itembytes=(ROOT/'reference/pkhex/PKHeX.Core/Resources/text/items/gen2/text_ItemsG2_en.txt').read_bytes()
 items=itembytes.decode('utf-16' if itembytes[:2]==b'\xff\xfe' else 'utf-8-sig').splitlines()
 for code,game in GAMES:
  raw=(ROOT/('reference/pkhex/PKHeX.Core/Resources/byte/personal/personal_'+code)).read_bytes()
  for edge in json.loads((ROOT/'audit/gen-two-evolution-encounters.json').read_text()):
   kind=edge['evolutionType']
   if kind not in {'LevelUp','UseItem','Trade'} or edge['sourceForm'] or edge['destinationForm']:continue
   parent=edge['sourceSpecies'];child=edge['destinationSpecies'];level=edge['level']
   assert 1<=parent<=251 and 1<=child<=251 and 0<=level<=100
   assert len(raw[parent*32:(parent+1)*32])==32 and len(raw[child*32:(child+1)*32])==32
   refs=[edge['source']]
   if kind=='UseItem':requirement='use '+items[edge['argument']];category='item'
   elif kind=='Trade':
    requirement='trade'+(' while holding '+HELD[child] if child in HELD else '')+'; arrange a trade back to keep your shiny';category='trade'
    refs.append('https://bulbapedia.bulbagarden.net/wiki/Trade_Evolution')
   elif level:requirement='level up at level '+str(level)+' or higher';category='level'
   else:
    assert (parent,child) in FRIENDSHIP
    requirement='level up with at least 220 friendship';category='friendship'
    if child==196:requirement+=' during morning or day (4:00 AM–5:59 PM) on the in-game clock'
    if child==197:requirement+=' at night (6:00 PM–3:59 AM) on the in-game clock'
    refs.extend(['https://bulbapedia.bulbagarden.net/wiki/Friendship_Evolution','https://bulbapedia.bulbagarden.net/wiki/Time#Generation_II'])
   records[str(child)]['entries'].append(dict(game=game,method='Obtain shiny '+names[parent]+'; '+requirement+' to evolve into '+names[child]+'; the parent may require a compatible Generation II trade or a Generation I Time Capsule transfer; Generation III and later cannot transfer Pokémon back to these games',status='Huntable',locations=[],source=edge['source'],sourceReferences=refs,olderEvolutionKind='gen-two-'+category,olderEvolutionType=kind,evolutionParent=parent,evolutionLevel=level,evolutionArgument=edge['argument'],gameFormId=0,verification='Generation II source branch and gameplay requirement checked; parent acquisition remains under audit'))
   count+=1
  # The legality tree omits Tyrogue's stat-dependent branches; gameplay still supports all three.
  for child,comparison in [(106,'higher than'),(107,'lower than'),(237,'equal to')]:
   source='https://bulbapedia.bulbagarden.net/wiki/Tyrogue#Evolution_data'
   records[str(child)]['entries'].append(dict(game=game,method='Obtain shiny Tyrogue; level up at level 20 or higher with Attack '+comparison+' Defense after gaining the level; compare actual stats, not base stats, to evolve into '+names[child],status='Huntable',locations=[],source=source,sourceReferences=[source],olderEvolutionKind='gen-two-stat',olderEvolutionType='GameplayStatBranch',evolutionParent=236,evolutionLevel=20,evolutionArgument=0,gameFormId=0,verification='Generation II gameplay branch omitted from legality tree; parent acquisition remains under audit'))
   count+=1
 return count
