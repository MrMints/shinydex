"""Render evolution requirements whose interpretation has been verified."""
import json
from pathlib import Path
from form_mapping import catalog_forms
ROOT=Path(__file__).parent
GAMES={'sv':'Pokémon Scarlet / Violet','ss':'Pokémon Sword / Shield','bs':'Pokémon Brilliant Diamond / Shining Pearl','la':'Pokémon Legends: Arceus','za':'Pokémon Legends: Z-A'}
ITEM_TYPES={'UseItem','UseItemMale','UseItemFemale','UseItemDay','UseItemNight','UseItemFullMoon','TradeHeldItem','LevelUpHeldItemDay','LevelUpHeldItemNight'}
CONDITION_TYPES={'LevelUpFriendship','LevelUpFriendshipMorning','LevelUpFriendshipNight','LevelUpKnowMove','LevelUpMale','LevelUpFemale','LevelUpMorning','LevelUpNight','LevelUpATK','LevelUpDEF','LevelUpAeqD','LevelUpWithTeammate','LevelUpMoveType','LevelUpWeather','LevelUpECl5','LevelUpECgeq5','LevelUpAffection50MoveType','LevelUpNatureAmped','LevelUpForest','LevelUpCold','LevelUpElectric','LevelUpKnowMoveECElse','LevelUpBeauty'}
TRADE_TYPES={'Trade','TradeShelmetKarrablast'}
ACTION_TYPES={'LevelUpWalkStepsWith','LevelUpUnionCircle','LevelUpCollect999','LevelUpUseMoveSpecial','UseMoveAgileStyle','UseMoveStrongStyle','LevelUpRecoilDamageMale','LevelUpRecoilDamageFemale','CriticalHitsInBattle','HitPointsLostInBattle','LevelUpDefeatEquals','LevelUpNinjask','LevelUpShedinja','LevelUpInverted','LevelUpInBattleEC100','UseMoveBarbBarrage','Spin'}
def merge(records,catalog):
 forms=catalog_forms(catalog);names={p['key']:p['displayName'] for p in catalog};sources={p['key']:p['source'] for p in catalog};added=[]
 items=(ROOT/'reference/pkhex/PKHeX.Core/Resources/text/items/text_Items_en.txt').read_text(encoding='utf-8-sig').splitlines()
 moves=(ROOT/'reference/pkhex/PKHeX.Core/Resources/text/other/en/text_Moves_en.txt').read_text(encoding='utf-8-sig').splitlines()
 for edge in json.loads((ROOT/'evolution-encounters.json').read_text()):
  kind=edge['evolutionType']
  if kind not in ITEM_TYPES|CONDITION_TYPES|TRADE_TYPES|ACTION_TYPES|{'LevelUp'} or not edge['sourcePresent'] or not edge['destinationPresent']:continue
  parent=forms.get((edge['sourceSpecies'],edge['sourceForm']));child=forms.get((edge['destinationSpecies'],edge['destinationForm']))
  if parent is None or child is None or records[str(parent)]['locked'] or records[str(child)]['locked']:continue
  if kind=='LevelUpBeauty' and edge['gameTable']=='za':continue # Gameplay support for this preserved table branch remains unverified.
  game=GAMES[edge['gameTable']]
  if kind=='LevelUp':
   requirement=('reach level ' if edge['gameTable']=='la' else 'level up at level ')+str(edge['level'])+' or higher'
   if edge['gameTable']=='la':requirement+='; select Evolve from the party menu'
  elif kind in ACTION_TYPES:
   if kind=='Spin':requirement='give Milcery a Sweet to hold, then spin the player clockwise for less than 5 seconds during the day and stop to produce Vanilla Cream Alcremie; use Strawberry Sweet to match the pictured decoration; the held Sweet determines its decoration and is consumed'
   elif kind=='UseMoveBarbBarrage':requirement='land 20 hits with Barb Barrage using this Hisuian Qwilfish, then select Evolve from the party menu; strong style is not required in Legends: Z-A'
   elif kind=='LevelUpInBattleEC100':requirement='gain a level from battle experience at level 25 or higher with the hidden encryption constant selecting Family of Three; the form branch is fixed and resetting cannot change it; evolution can occur without an animation if Tandemaus was not sent out; candies alone do not trigger it, and a level-100 Tandemaus cannot evolve'
   elif kind=='LevelUpInverted':requirement=('reach level 30 or higher, open the party menu and hold the console upside-down in handheld mode; select Inkay, then Evolve even if no evolution arrow appears' if edge['gameTable']=='za' else 'level up at level 30 or higher while holding the console upside-down in handheld mode, with attached Joy-Con controllers and no other controllers connected')
   elif kind=='LevelUpNinjask':requirement='level up Nincada at level 20 or higher'
   elif kind=='LevelUpShedinja':requirement='evolve shiny Nincada at level 20 or higher with an empty party slot and a regular Poké Ball in the bag; shiny Shedinja appears alongside Ninjask'
   elif kind=='CriticalHitsInBattle':requirement='land three critical hits in one battle without escaping or losing; '+('select Evolve from the party menu afterward' if edge['gameTable']=='za' else 'evolution triggers after the battle')
   elif kind=='HitPointsLostInBattle':requirement='take at least 49 HP of damage from opposing attacks without fainting, then stand under '+('a bridge over Coulant Waterway' if edge['gameTable']=='za' else 'the stone arch in Dusty Bowl')+'; self-inflicted or weather damage does not count'
   elif kind=='LevelUpDefeatEquals':requirement='defeat three wild Bisharp holding a Leader’s Crest with this Bisharp landing the finishing blows, then level up'
   elif kind in {'UseMoveAgileStyle','UseMoveStrongStyle'}:
    requirement=('use Psyshield Bash in agile style 20 times' if kind=='UseMoveAgileStyle' else 'use Barb Barrage in strong style 20 times')+'; select Evolve from the party menu'
   elif kind.startswith('LevelUpRecoilDamage'):
    requirement='accumulate at least 294 HP of recoil damage without fainting with a '+('male' if kind.endswith('Male') else 'female')+' White-Striped Basculin; then '+('select Evolve from the party menu' if edge['gameTable']=='la' else 'level up')
   elif kind=='LevelUpWalkStepsWith':requirement='walk '+str(edge['argument'])+' steps with this Pokémon out in Let’s Go mode, then level it up while it is out'
   elif kind=='LevelUpUnionCircle':requirement='level up at level '+str(edge['level'])+' or higher while connected to another player in Union Circle'
   elif kind=='LevelUpCollect999':requirement='collect '+str(edge['argument'])+' Gimmighoul Coins in your inventory, then '+('select Evolve from the party menu' if edge['gameTable']=='za' else 'level up')+'; evolution consumes the coins'
   else:requirement='use Rage Fist '+str(edge['argument'])+' times, then '+('select Evolve from the party menu' if edge['gameTable']=='za' else 'level up')
  elif kind in TRADE_TYPES:
   if kind=='TradeShelmetKarrablast':
    partner='Shelmet' if edge['sourceSpecies']==588 else 'Karrablast'
    requirement='trade specifically for '+partner+'; neither Pokémon may hold an Everstone; arrange a trade back to keep your shiny'
   else:requirement='trade with another player; arrange a trade back to keep your shiny'
  elif kind in CONDITION_TYPES:
   conditions=[]
   if edge['sourceSpecies']==133 and edge['destinationSpecies'] in {196,197}:
    if edge['gameTable']!='bs':conditions.append('without a Fairy-type move to avoid evolving into Sylveon')
    if edge['gameTable'] in {'bs','la'}:conditions.append('away from the Moss Rock and Ice Rock to avoid Leafeon or Glaceon')
   if kind in {'LevelUpECl5','LevelUpECgeq5'}:conditions.append('with the hidden encryption constant selecting '+('Silcoon' if kind=='LevelUpECl5' else 'Cascoon')+'; this branch is fixed for each Wurmple and cannot be changed by resetting, time of day or gender')
   if kind=='LevelUpWeather':conditions.append('during natural rain in the overworld; battle-only rain from Rain Dance, Drizzle or Primordial Sea does not count')
   if kind=='LevelUpBeauty':conditions.append('with Beauty at least 170; '+('raise Beauty using dry Poffins before leveling up' if edge['gameTable']=='bs' else 'prepare Beauty in a compatible Contest game such as BDSP and transfer Feebas here before leveling up; this game cannot raise Beauty itself'))
   if kind=='LevelUpElectric':conditions.append('in the special magnetic field of '+('Mount Coronet' if edge['gameTable']=='bs' else 'the Coronet Highlands'))
   if kind in {'LevelUpForest','LevelUpCold'}:
    location={('bs','LevelUpForest'):'the Moss Rock in Eterna Forest',('bs','LevelUpCold'):'the Ice Rock on Route 217',('la','LevelUpForest'):'the Moss Rock in The Heartwood, Obsidian Fieldlands',('la','LevelUpCold'):'the Ice Rock in Icepeak Cavern, Alabaster Icelands'}[(edge['gameTable'],kind)]
    conditions.append('near '+location)
   if kind=='LevelUpNatureAmped':
    assert edge['sourceSpecies']==848 and edge['destinationForm']==0,edge
    conditions.append('with an original Hardy, Brave, Adamant, Naughty, Docile, Impish, Lax, Hasty, Jolly, Naive, Rash, Sassy or Quirky nature for Amped Form; Mints do not change this evolution branch')
   if kind=='LevelUpAffection50MoveType':
    assert edge['sourceSpecies']==133 and edge['argument']==17,edge
    conditions.append('with high friendship while knowing a Fairy-type move')
   if 'Friendship' in kind:conditions.append('with high friendship')
   if kind.endswith('Morning'):conditions.append('during the day')
   if kind.endswith('Night'):conditions.append('at night')
   if kind=='LevelUpMale':conditions.append('with a male Pokémon')
   if kind=='LevelUpFemale':conditions.append('with a female Pokémon')
   if kind=='LevelUpWithTeammate':conditions.append('with '+names[forms[(edge['argument'],0)]]+' in the party')
   if kind=='LevelUpMoveType':
    assert edge['sourceSpecies']==674 and edge['argument']==0,edge
    conditions.append('with a Dark-type Pokémon in the party')
   if kind in {'LevelUpATK','LevelUpDEF','LevelUpAeqD'}:conditions.append({'LevelUpATK':'with Attack greater than Defense','LevelUpDEF':'with Defense greater than Attack','LevelUpAeqD':'with Attack equal to Defense'}[kind])
   if kind=='LevelUpKnowMoveECElse':
    assert edge['sourceSpecies']==206 and edge['argument']==887 and edge['destinationForm']==0,edge
    conditions.append('while knowing Hyper Drill, with the hidden encryption constant selecting Two-Segment Form; the branch is fixed for this Dunsparce and resetting cannot change it')
   if kind=='LevelUpKnowMove':
    move=moves[edge['argument']];assert move.strip(),edge
    conditions.append('while knowing '+move)
   requirement=('meet the conditions and select Evolve from the party menu' if edge['gameTable'] in {'la','za'} else 'level up')+' '+', '.join(conditions)
   if edge['level']:requirement+=' at level '+str(edge['level'])+' or higher'
  else:
   item=items[edge['argument']];assert item.strip(),edge
   if kind.startswith('UseItem'):
    requirement='use '+item
    if kind=='UseItemMale':requirement+=' on a male Pokémon'
    if kind=='UseItemFemale':requirement+=' on a female Pokémon'
    if kind=='UseItemDay':requirement+=' during the day'
    if kind=='UseItemNight':requirement+=' at night'
    if kind=='UseItemFullMoon':requirement+=' during a full moon'
   elif kind=='TradeHeldItem':requirement='trade while holding '+item+'; arrange a trade back to keep your shiny'
   else:
    requirement='level up while holding '+item+(' during the day' if kind.endswith('Day') else ' at night')
    if edge['level']:requirement+=' at level '+str(edge['level'])+' or higher'
  method='Obtain shiny '+names[parent]+'; '+requirement+' to evolve into '+names[child]
  method+=' · obtain the shiny pre-evolution through a hunting route or a compatible trade / HOME transfer'
  records[str(child)]['entries'].append(dict(game=game,method=method,status='Huntable',locations=[],source=edge['source'],sourceReferences=[edge['source'],sources[child]+'#Evolution_data'],evolutionKind='level-only' if kind=='LevelUp' else 'condition' if kind in CONDITION_TYPES else 'trade' if kind in TRADE_TYPES else 'action' if kind in ACTION_TYPES else 'item',evolutionType=kind,evolutionArgument=edge['argument'],evolutionParent=parent,evolutionLevel=edge['level'],gameFormId=edge['destinationForm'],verification='Evolution requirement and both forms present in game verified from pinned evolution/personal tables; acquisition prerequisites remain under audit'))
  if kind=='LevelUpInverted' and edge['gameTable']=='za':records[str(child)]['entries'][-1]['sourceReferences'].append('https://www.siliconera.com/how-to-evolve-inkay-in-pokemon-legends-z-a/')
  added.append(dict(key=child,parent=parent,game=game,level=edge['level'],type=kind,argument=edge['argument']))
 (ROOT/'evolution-route-audit.json').write_text(json.dumps(dict(routes=added,routeCount=len(added),fullHuntingAuditComplete=False,remaining=['Other evolution types and exact conditions','Shiny parent acquisition and transfer prerequisites']),indent=2))
 return len(added)
