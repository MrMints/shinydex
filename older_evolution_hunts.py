"""Render simple Ultra Sun/Ultra Moon level requirements from the pinned table."""
import json
from pathlib import Path
from form_mapping import catalog_forms
ROOT=Path(__file__).parent
GAME='Pokémon Ultra Sun / Ultra Moon'
ITEM_TYPES={'UseItem','UseItemMale','UseItemFemale','UseItemWormhole','TradeHeldItem','LevelUpHeldItemDay','LevelUpHeldItemNight'}
CONDITION_TYPES={'LevelUpFriendship','LevelUpFriendshipMorning','LevelUpFriendshipNight','LevelUpAffection50MoveType'}
GENDER_TIME_TYPES={'LevelUpMale','LevelUpFemale','LevelUpMorning','LevelUpNight'}
PARTY_STAT_TYPES={'LevelUpATK','LevelUpDEF','LevelUpAeqD','LevelUpWithTeammate','LevelUpMoveType'}
SPECIAL_REQUIREMENTS={
 'LevelUpECl5':'level up at level 7 or higher with the hidden encryption constant selecting Silcoon; this branch is fixed for each Wurmple and cannot be changed by resetting, time of day or gender',
 'LevelUpECgeq5':'level up at level 7 or higher with the hidden encryption constant selecting Cascoon; this branch is fixed for each Wurmple and cannot be changed by resetting, time of day or gender',
 'LevelUpNinjask':'level up Nincada at level 20 or higher',
 'LevelUpShedinja':'evolve shiny Nincada at level 20 or higher with an empty party slot and a regular Poké Ball in the bag; shiny Shedinja appears alongside Ninjask',
 'LevelUpBeauty':'level up with Beauty at least 170; raise Beauty in a compatible earlier Contest game such as Omega Ruby or Alpha Sapphire, then transfer Feebas through Pokémon Bank; Ultra Sun and Ultra Moon cannot raise Beauty themselves',
 'LevelUpInverted':'level up at level 30 or higher while holding the Nintendo 3DS upside down',
 'LevelUpWeather':'level up at level 50 or higher during natural overworld rain or fog; Rain Dance or an Ability that creates rain only in battle does not satisfy this requirement',
 'LevelUpVersionDay':'level up regular Rockruff without Own Tempo at level 25 or higher during the in-game day in Pokémon Ultra Sun to obtain Midday Form; this evolution cannot be performed in Ultra Moon',
}
LOCATION_REQUIREMENTS={
 'LevelUpElectric':('level up in the special magnetic field at Blush Mountain or Vast Poni Canyon',['Blush_Mountain','Vast_Poni_Canyon']),
 'LevelUpForest':('level up near the Moss Rock in Lush Jungle',['Lush_Jungle']),
 'LevelUpCold':('level up near the Ice Rock inside the cave on Mount Lanakila',['Mount_Lanakila']),
 'LevelUpSummit':('level up on Mount Lanakila; the accessible mountain base also works in Ultra Sun and Ultra Moon',['Mount_Lanakila']),
 'LevelUpWormhole':('level up at level 28 or higher in Ultra Space to obtain the Kantonian form',['Marowak_(Pok%C3%A9mon)']),
}
def merge(records,catalog):
 forms=catalog_forms(catalog);names={p['key']:p['displayName'] for p in catalog};sources={p['key']:p['source'] for p in catalog};added=[];excluded=[]
 items=(ROOT/'reference/pkhex/PKHeX.Core/Resources/text/items/text_Items_en.txt').read_text(encoding='utf-8-sig').splitlines()
 moves=(ROOT/'reference/pkhex/PKHeX.Core/Resources/text/other/en/text_Moves_en.txt').read_text(encoding='utf-8-sig').splitlines()
 for edge in json.loads((ROOT/'audit/older-evolution-encounters.json').read_text()):
  parent=forms.get((edge['sourceSpecies'],edge['sourceForm']));child=forms.get((edge['destinationSpecies'],edge['destinationForm']))
  reason='untracked-form' if parent is None or child is None else 'shiny-locked-parent-or-child' if records[str(parent)]['locked'] or records[str(child)]['locked'] else 'unsupported-condition' if edge['evolutionType'] not in {'LevelUp','Trade','TradeShelmetKarrablast','LevelUpKnowMove'}|ITEM_TYPES|CONDITION_TYPES|GENDER_TIME_TYPES|PARTY_STAT_TYPES|set(LOCATION_REQUIREMENTS)|set(SPECIAL_REQUIREMENTS) else None
  if reason:
   excluded.append(dict(edge,reason=reason));continue
  kind=edge['evolutionType']
  if kind=='LevelUp':
   assert 1<=edge['level']<=100
   requirement='level up at level '+str(edge['level'])+' or higher'
  elif kind in SPECIAL_REQUIREMENTS:
   requirement=SPECIAL_REQUIREMENTS[kind]
  elif kind in PARTY_STAT_TYPES:
   if kind=='LevelUpWithTeammate':
    assert edge['argument']==223
    requirement='level up with Remoraid in your party; Remoraid does not need to be shiny'
   elif kind=='LevelUpMoveType':
    assert edge['sourceSpecies']==674 and edge['level']==32
    requirement='level up at level 32 or higher with a Dark-type Pokémon in your party; the party partner does not need to be shiny'
   else:
    assert edge['sourceSpecies']==236 and edge['level']==20
    comparison={'LevelUpATK':'higher than','LevelUpDEF':'lower than','LevelUpAeqD':'equal to'}[kind]
    requirement='level up at level 20 or higher with Attack '+comparison+' Defense after gaining the level; compare actual stats, not base stats'
  elif kind in LOCATION_REQUIREMENTS:
   requirement=LOCATION_REQUIREMENTS[kind][0]
  elif kind in GENDER_TIME_TYPES:
   assert 1<=edge['level']<=100
   requirement='level up at level '+str(edge['level'])+' or higher'
   if kind.endswith('Male'):requirement+=' as a male Pokémon'
   if kind.endswith('Female'):requirement+=' as a female Pokémon'
   if kind.endswith('Morning'):requirement+=' during the in-game day'
   if kind.endswith('Night'):requirement+=' during the in-game night'
   if edge['sourceSpecies']==104:requirement+=' in Alola, outside Ultra Space, to obtain the Alolan form'
   if edge['sourceSpecies']==412 and edge['destinationSpecies']==413:requirement+=' while wearing the Plant Cloak'
  elif kind in CONDITION_TYPES:
   if kind=='LevelUpAffection50MoveType':
    requirement='level up while knowing a Fairy-type move with at least two affection hearts in Pokémon Refresh; affection is separate from friendship; stay away from the Moss Rock and Ice Rock'
   else:
    requirement='level up with at least 220 friendship'
    if kind.endswith('Morning'):requirement+=' during the in-game day'
    if kind.endswith('Night'):requirement+=' during the in-game night'
    if edge['sourceSpecies']==133:requirement+='; forget Fairy-type moves to prevent Sylveon and stay away from the Moss Rock and Ice Rock'
  elif kind=='LevelUpKnowMove':
   move=moves[edge['argument']];assert move.strip()
   requirement='level up while knowing '+move
  elif kind=='TradeShelmetKarrablast':requirement='trade specifically for '+('Shelmet' if edge['sourceSpecies']==588 else 'Karrablast')+'; neither Pokémon may hold an Everstone; arrange a trade back to keep your shiny'
  elif kind in ITEM_TYPES:
   item=items[edge['argument']];assert item.strip()
   if kind.startswith('UseItem'):
    requirement='use '+item
    if kind=='UseItemMale':requirement+=' on a male Pokémon'
    if kind=='UseItemFemale':requirement+=' on a female Pokémon'
    if kind=='UseItemWormhole':requirement+=' in Ultra Space to obtain the Kantonian form'
    elif edge['sourceSpecies'] in {25,102}:requirement+=' in Alola, outside Ultra Space, to obtain the Alolan form'
   elif kind=='TradeHeldItem':requirement='trade while holding '+item+'; arrange a trade back to keep your shiny'
   else:requirement='level up while holding '+item+(' during the day' if kind.endswith('Day') else ' at night')
  else:requirement='trade with another player without holding an Everstone; arrange a trade back to keep your shiny'
  method='Obtain shiny '+names[parent]+'; '+requirement+' to evolve into '+names[child]+'; the shiny parent may require a compatible trade or Bank transfer'
  references=[edge['source'],sources[child]+'#Evolution_data']
  if kind in LOCATION_REQUIREMENTS:references.extend('https://bulbapedia.bulbagarden.net/wiki/'+page for page in LOCATION_REQUIREMENTS[kind][1])
  if kind in CONDITION_TYPES:references.append('https://bulbapedia.bulbagarden.net/wiki/'+('Affection' if kind=='LevelUpAffection50MoveType' else 'Friendship_Evolution'))
  records[str(child)]['entries'].append(dict(game=GAME,method=method,status='Huntable',locations=[],source=edge['source'],sourceReferences=references,olderEvolutionKind='level-only' if kind=='LevelUp' else 'special' if kind in SPECIAL_REQUIREMENTS else 'party-stat' if kind in PARTY_STAT_TYPES else 'location' if kind in LOCATION_REQUIREMENTS else 'gender-time' if kind in GENDER_TIME_TYPES else 'condition' if kind in CONDITION_TYPES else 'move' if kind=='LevelUpKnowMove' else 'item' if kind in ITEM_TYPES else 'trade',olderEvolutionType=kind,evolutionParent=parent,evolutionLevel=edge['level'],evolutionArgument=edge['argument'],gameFormId=edge['destinationForm'],verification='Evolution requirement decoded from pinned Ultra Sun/Ultra Moon table; shiny parent acquisition remains under audit'))
  if kind=='LevelUpVersionDay':records[str(child)]['entries'][-1]['game']='Pokémon Ultra Sun'
  added.append(dict(key=child,parent=parent,level=edge['level'],form=edge['destinationForm'],type=kind))
 (ROOT/'audit/older-evolution-route-audit.json').write_text(json.dumps({'routes':added,'routeCount':len(added),'excludedBranches':excluded,'decodedBranchCount':len(added)+len(excluded),'fullHuntingAuditComplete':False},indent=2),encoding='utf-8')
 return len(added)
