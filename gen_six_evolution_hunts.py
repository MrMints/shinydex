"""Render Gen VI simple level requirements from its pinned evolution table."""
import json
from pathlib import Path
ROOT=Path(__file__).parent
ITEM_TYPES={'UseItem','UseItemMale','UseItemFemale','TradeHeldItem','LevelUpHeldItemDay','LevelUpHeldItemNight'}
SUPPORTED={'LevelUp','Trade','TradeShelmetKarrablast','LevelUpKnowMove'}|ITEM_TYPES
CONDITION_TYPES={'LevelUpFriendship','LevelUpFriendshipMorning','LevelUpFriendshipNight','LevelUpAffection50MoveType','LevelUpMale','LevelUpFemale','LevelUpMorning','LevelUpNight','LevelUpATK','LevelUpDEF','LevelUpAeqD','LevelUpWithTeammate','LevelUpMoveType'}
SPECIAL_TYPES={'LevelUpECl5','LevelUpECgeq5','LevelUpNinjask','LevelUpShedinja','LevelUpBeauty','LevelUpInverted'}
LOCATIONS={
 ('xy','LevelUpElectric'):('level up in the special magnetic field on Kalos Route 13','Magnetic_field'),
 ('ao','LevelUpElectric'):('level up in the special magnetic field at New Mauville','Magnetic_field'),
 ('xy','LevelUpForest'):('level up near the Moss Rock on Kalos Route 20','Moss_Rock'),
 ('ao','LevelUpForest'):('level up near the Moss Rock in Petalburg Woods','Moss_Rock'),
 ('xy','LevelUpCold'):('level up near the Ice Rock in Frost Cavern','Ice_Rock'),
 ('ao','LevelUpCold'):('level up near the Ice Rock in the lowest icy room of Shoal Cave, accessible at low tide','Shoal_Cave'),
}
def merge(records,catalog):
 names={p['id']:p['displayName'] for p in catalog if not p.get('region')}
 items=(ROOT/'reference/pkhex/PKHeX.Core/Resources/text/items/text_Items_en.txt').read_text(encoding='utf-8-sig').splitlines()
 moves=(ROOT/'reference/pkhex/PKHeX.Core/Resources/text/other/en/text_Moves_en.txt').read_text(encoding='utf-8-sig').splitlines()
 count=0
 for code,game,size in [('xy','Pokémon X / Y',64),('ao','Pokémon Omega Ruby / Alpha Sapphire',80)]:
  raw=(ROOT/('reference/pkhex/PKHeX.Core/Resources/byte/personal/personal_'+code)).read_bytes()
  for edge in json.loads((ROOT/'audit/gen-six-evolution-encounters.json').read_text()):
   kind=edge['evolutionType']
   if kind not in SUPPORTED|CONDITION_TYPES|SPECIAL_TYPES|{'LevelUpElectric','LevelUpForest','LevelUpCold'} or edge['sourceForm'] or edge['destinationForm']:continue
   parent=edge['sourceSpecies'];child=edge['destinationSpecies']
   if parent not in names or child not in names or parent>721 or child>721:continue
   if records[str(parent)]['locked'] or records[str(child)]['locked']:continue
   assert len(raw[parent*size:(parent+1)*size])==size and len(raw[child*size:(child+1)*size])==size
   level=edge['level']
   if (code,kind) in LOCATIONS:
    requirement=LOCATIONS[(code,kind)][0];category='location'
   elif parent==705 and child==706:
    requirement='level up at level 50 or higher during natural overworld rain; Rain Dance, Drizzle and Primordial Sea do not count; fog does not satisfy this requirement in Generation VI';category='special'
   elif kind in SPECIAL_TYPES:
    category='special'
    if kind=='LevelUpBeauty':requirement='level up with Beauty at least 170; '+('raise Beauty using blue Pokéblocks before leveling up' if code=='ao' else 'prepare Beauty in a compatible earlier Contest game or Omega Ruby/Alpha Sapphire and transfer Feebas here before leveling up; X/Y cannot raise Beauty themselves')
    else:
     match=next(e for e in records[str(child)]['entries'] if e.get('olderEvolutionKind')=='special' and e.get('olderEvolutionType')==kind and e['evolutionParent']==parent and e['evolutionLevel']==level)
     requirement=match['method'].split('; ',1)[1].split(' to evolve into ',1)[0]
   elif kind in CONDITION_TYPES:
    match=next(e for e in records[str(child)]['entries'] if e.get('olderEvolutionKind') in {'condition','gender-time','party-stat'} and e.get('olderEvolutionType')==kind and e['evolutionParent']==parent and e['evolutionLevel']==level)
    assert edge['argument']==match['evolutionArgument'] or (kind in {'LevelUpMale','LevelUpFemale','LevelUpMorning','LevelUpNight','LevelUpATK','LevelUpDEF','LevelUpAeqD','LevelUpMoveType'} and edge['argument']==level)
    requirement=match['method'].split('; ',1)[1].split(' to evolve into ',1)[0].replace('Pokémon Refresh','Pokémon-Amie');category='condition'
   elif kind=='LevelUp':
    assert 1<=level<=100
    requirement='level up at level '+str(level)+' or higher';category='level'
   elif kind=='LevelUpKnowMove':requirement='level up while knowing '+moves[edge['argument']];category='move'
   elif kind in {'Trade','TradeShelmetKarrablast'}:
    requirement=('trade specifically for '+('Shelmet' if parent==588 else 'Karrablast')+'; neither Pokémon may hold an Everstone' if kind=='TradeShelmetKarrablast' else 'trade with another player without holding an Everstone')+'; arrange a trade back to keep your shiny';category='trade'
   else:
    item=items[edge['argument']];assert item.strip();category='item'
    if kind.startswith('UseItem'):
     requirement='use '+item
     if kind=='UseItemMale':requirement+=' on a male Pokémon'
     if kind=='UseItemFemale':requirement+=' on a female Pokémon'
    elif kind=='TradeHeldItem':requirement='trade while holding '+item+'; arrange a trade back to keep your shiny'
    else:requirement='level up while holding '+item+(' during the day' if kind.endswith('Day') else ' at night')
   records[str(child)]['entries'].append(dict(game=game,method='Obtain shiny '+names[parent]+'; '+requirement+' to evolve into '+names[child]+'; the parent may require a compatible trade or Pokémon Bank transfer from Generation VI or earlier origins',status='Huntable',locations=[],source=edge['source'],sourceReferences=[edge['source'],next(p['source'] for p in catalog if p['key']==child)+'#Evolution_data'],olderEvolutionKind='gen-six-'+category,olderEvolutionType=kind,evolutionParent=parent,evolutionLevel=level,evolutionArgument=edge['argument'],gameFormId=0,verification='Gen VI evolution requirement and game-specific species data checked; parent acquisition remains under audit'))
   if parent==705 and child==706:records[str(child)]['entries'][-1]['sourceReferences'].append('https://bulbapedia.bulbagarden.net/wiki/Sliggoo#Evolution_data')
   if (code,kind) in LOCATIONS:records[str(child)]['entries'][-1]['sourceReferences'].append('https://bulbapedia.bulbagarden.net/wiki/'+LOCATIONS[(code,kind)][1])
   if kind=='LevelUpBeauty':records[str(child)]['entries'][-1]['sourceReferences'].extend(['https://bulbapedia.bulbagarden.net/wiki/Beautiful_(condition)','https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9block'])
   count+=1
 return count
