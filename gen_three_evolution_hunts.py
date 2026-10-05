"""Generation III ordinary level requirements from its own evolution table."""
import json
from pathlib import Path
ROOT=Path(__file__).parent
GAMES=[('rs','Pokémon Ruby / Sapphire'),('e','Pokémon Emerald'),('fr','Pokémon FireRed'),('lg','Pokémon LeafGreen')]
CONDITIONS={'LevelUpFriendship','LevelUpATK','LevelUpDEF','LevelUpAeqD'}
TIMED={'LevelUpFriendshipMorning','LevelUpFriendshipNight'}
SPECIAL={
 'LevelUpECl5':('level up at level 7 or higher with the hidden personality value selecting Silcoon; the branch is fixed for this Wurmple and resetting cannot change it','Personality_value'),
 'LevelUpECgeq5':('level up at level 7 or higher with the hidden personality value selecting Cascoon; the branch is fixed for this Wurmple and resetting cannot change it','Personality_value'),
 'LevelUpNinjask':('level up Nincada at level 20 or higher','Nincada'),
 'LevelUpShedinja':('evolve shiny Nincada at level 20 or higher with an empty party slot; shiny Shedinja appears alongside Ninjask; a spare Poké Ball is not required in Generation III','Shedinja'),
 'LevelUpBeauty':('level up with Beauty at least 170; raise Beauty using dry-flavored Pokéblocks in Ruby, Sapphire or Emerald before reaching the sheen limit','Feebas'),
}
def merge(records,catalog):
 names={p['id']:p['displayName'] for p in catalog if not p.get('region')};count=0
 items=(ROOT/'reference/pkhex/PKHeX.Core/Resources/text/items/gen3/text_ItemsG3_en.txt').read_text(encoding='utf-16').splitlines()
 for code,game in GAMES:
  raw=(ROOT/('reference/pkhex/PKHeX.Core/Resources/byte/personal/personal_'+code)).read_bytes()
  for edge in json.loads((ROOT/'audit/gen-three-evolution-encounters.json').read_text()):
   kind=edge['evolutionType']
   if kind not in {'LevelUp','UseItem','Trade','TradeHeldItem'}|CONDITIONS|TIMED|set(SPECIAL) or edge['sourceForm'] or edge['destinationForm']:continue
   parent=edge['sourceSpecies'];child=edge['destinationSpecies'];level=edge['level']
   assert 1<=parent<=386 and 1<=child<=386 and 0<=level<=100
   assert len(raw[parent*28:(parent+1)*28])==28 and len(raw[child*28:(child+1)*28])==28
   restriction='; in FireRed/LeafGreen, evolutions into species outside the original Kanto Pokédex require the National Pokédex' if code in {'fr','lg'} and child>151 else ''
   if kind in SPECIAL:
    requirement=SPECIAL[kind][0];category='special'
    if kind=='LevelUpBeauty' and code in {'fr','lg'}:requirement='prepare Feebas with Beauty at least 170 using dry-flavored Pokéblocks in Ruby, Sapphire or Emerald before reaching the sheen limit, then trade it here and level up; FireRed and LeafGreen cannot raise Beauty locally'
   elif kind in TIMED:
    period='12:00 PM–11:59 PM' if kind=='LevelUpFriendshipMorning' else '12:00 AM–11:59 AM'
    requirement='level up with at least 220 friendship during '+period+' on the Hoenn game clock'
    if code in {'fr','lg'}:requirement='trade shiny Eevee to Ruby, Sapphire or Emerald; rebuild friendship to at least 220 after the trade and '+requirement+' there, then trade the evolved shiny back; FireRed and LeafGreen have no day/night clock and cannot perform this evolution locally'
    category='time'
   elif kind in CONDITIONS:
    if kind=='LevelUpFriendship':requirement='level up with at least 220 friendship'
    else:
     comparison={'LevelUpATK':'higher than','LevelUpDEF':'lower than','LevelUpAeqD':'equal to'}[kind]
     requirement='level up at level '+str(level)+' or higher with Attack '+comparison+' Defense after gaining the level; compare actual stats, not base stats'
    category='condition'
   elif kind=='LevelUp':
    assert level>=1
    requirement='level up at level '+str(level)+' or higher';category='level'
   elif kind=='Trade':requirement='trade, then arrange a trade back to keep your shiny';category='trade'
   else:
    item=items[edge['argument']];assert item and not item.startswith('(')
    requirement='use '+item if kind=='UseItem' else 'trade while holding '+item+'; arrange a trade back to keep your shiny';category='item'
   method='Obtain shiny '+names[parent]+'; '+requirement+' to evolve into '+names[child]+restriction+'; the parent may require a compatible Generation III trade; later generations cannot transfer Pokémon back into Generation III'
   refs=[edge['source'],'https://bulbapedia.bulbagarden.net/wiki/Evolution#In_the_core_series_games']+(['https://bulbapedia.bulbagarden.net/wiki/Evolution_prevention'] if restriction else [])
   if kind=='LevelUpFriendship':refs.append('https://bulbapedia.bulbagarden.net/wiki/Friendship_Evolution')
   if kind in TIMED:refs.extend(['https://bulbapedia.bulbagarden.net/wiki/Time#Generation_III','https://bulbapedia.bulbagarden.net/wiki/Espeon#Evolution_data','https://bulbapedia.bulbagarden.net/wiki/Friendship'])
   if kind in SPECIAL:refs.append('https://bulbapedia.bulbagarden.net/wiki/'+SPECIAL[kind][1])
   records[str(child)]['entries'].append(dict(game=game,method=method,status='Huntable',locations=[],source=edge['source'],sourceReferences=refs,olderEvolutionKind='gen-three-'+category,olderEvolutionType=kind,evolutionParent=parent,evolutionLevel=level,evolutionArgument=edge['argument'],gameFormId=0,verification='Generation III evolution requirement and species table checked; parent acquisition remains under audit'))
   count+=1
 return count
