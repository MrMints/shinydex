"""Verify rendered level-only branches against the decoded source."""
import json
from pathlib import Path
from form_mapping import catalog_forms
from evolution_hunts import GAMES,ITEM_TYPES,CONDITION_TYPES,TRADE_TYPES,ACTION_TYPES
ROOT=Path(__file__).parent
forms=catalog_forms(json.loads((ROOT/'data.json').read_text()))
edges=json.loads((ROOT/'evolution-encounters.json').read_text());h=json.loads((ROOT/'hunts.json').read_text())
expected=set()
for e in edges:
 parent=forms.get((e['sourceSpecies'],e['sourceForm']));child=forms.get((e['destinationSpecies'],e['destinationForm']))
 if e['evolutionType']!='LevelUp' or not e['sourcePresent'] or not e['destinationPresent'] or parent is None or child is None:continue
 if h[str(parent)]['locked'] or h[str(child)]['locked']:continue
 expected.add((child,parent,GAMES[e['gameTable']],e['level'],e['destinationForm']))
actual={(int(k),e['evolutionParent'],e['game'],e['evolutionLevel'],e['gameFormId']) for k,g in h.items() for e in g['entries'] if e.get('evolutionKind')=='level-only'}
assert actual==expected
assert (2,1,'Pokémon Scarlet / Violet',16,0) in actual
assert (6,5,'Pokémon Sword / Shield',36,0) in actual
assert not any(child in {899,902,904} for child,parent,game,level,form in actual),'Action-based evolutions must not be level-only'
print('Verified',len(actual),'level-only routes with source/destination forms and game presence')
expected_items=set()
for e in edges:
 parent=forms.get((e['sourceSpecies'],e['sourceForm']));child=forms.get((e['destinationSpecies'],e['destinationForm']))
 if e['evolutionType'] not in ITEM_TYPES or not e['sourcePresent'] or not e['destinationPresent'] or parent is None or child is None:continue
 if h[str(parent)]['locked'] or h[str(child)]['locked']:continue
 expected_items.add((child,parent,GAMES[e['gameTable']],e['evolutionType'],e['argument'],e['level'],e['destinationForm']))
actual_items={(int(k),e['evolutionParent'],e['game'],e['evolutionType'],e['evolutionArgument'],e['evolutionLevel'],e['gameFormId']) for k,g in h.items() for e in g['entries'] if e.get('evolutionKind')=='item'}
assert actual_items==expected_items
gallade=[e for e in h['475']['entries'] if e.get('evolutionKind')=='item']
assert gallade and all('Dawn Stone' in e['method'] and 'male Pokémon' in e['method'] for e in gallade)
froslass=[e for e in h['478']['entries'] if e.get('evolutionKind')=='item']
assert froslass and all('Dawn Stone' in e['method'] and 'female Pokémon' in e['method'] for e in froslass)
assert any(e.get('evolutionType')=='TradeHeldItem' and 'Metal Coat' in e['method'] for e in h['212']['entries'])
assert any(e.get('evolutionType')=='LevelUpHeldItemNight' and 'Razor Claw' in e['method'] and 'at night' in e['method'] for e in h['461']['entries'])
print('Verified',len(actual_items),'item-based routes and gender/held-item regressions')
expected_conditions=set()
for e in edges:
 parent=forms.get((e['sourceSpecies'],e['sourceForm']));child=forms.get((e['destinationSpecies'],e['destinationForm']))
 if e['evolutionType'] not in CONDITION_TYPES or not e['sourcePresent'] or not e['destinationPresent'] or parent is None or child is None:continue
 if h[str(parent)]['locked'] or h[str(child)]['locked']:continue
 if e['evolutionType']=='LevelUpBeauty' and e['gameTable']=='za':continue
 expected_conditions.add((child,parent,GAMES[e['gameTable']],e['evolutionType'],e['argument'],e['level'],e['destinationForm']))
actual_conditions={(int(k),e['evolutionParent'],e['game'],e['evolutionType'],e['evolutionArgument'],e['evolutionLevel'],e['gameFormId']) for k,g in h.items() for e in g['entries'] if e.get('evolutionKind')=='condition'}
assert actual_conditions==expected_conditions
for sid,time in [('196','during the day'),('197','at night')]:
 rows=[e for e in h[sid]['entries'] if e.get('evolutionKind')=='condition']
 assert rows and all('high friendship' in e['method'] and time in e['method'] for e in rows)
rows=[e for e in h['473']['entries'] if e.get('evolutionKind')=='condition']
assert rows and all('Ancient Power' in e['method'] for e in rows)
assert any('party menu' in e['method'] for e in rows if e['game']=='Pokémon Legends: Arceus')
assert any('female Pokémon' in e['method'] for e in h['416']['entries'] if e.get('evolutionKind')=='condition')
print('Verified',len(actual_conditions),'friendship/move/gender/time routes and representative regressions')
expected_trades=set()
for e in edges:
 parent=forms.get((e['sourceSpecies'],e['sourceForm']));child=forms.get((e['destinationSpecies'],e['destinationForm']))
 if e['evolutionType'] not in TRADE_TYPES or not e['sourcePresent'] or not e['destinationPresent'] or parent is None or child is None:continue
 if h[str(parent)]['locked'] or h[str(child)]['locked']:continue
 expected_trades.add((child,parent,GAMES[e['gameTable']],e['evolutionType'],e['destinationForm']))
actual_trades={(int(k),e['evolutionParent'],e['game'],e['evolutionType'],e['gameFormId']) for k,g in h.items() for e in g['entries'] if e.get('evolutionKind')=='trade'}
assert actual_trades==expected_trades
for sid,partner in [('589','Shelmet'),('617','Karrablast')]:
 rows=[e for e in h[sid]['entries'] if e.get('evolutionKind')=='trade']
 assert rows and all('specifically for '+partner in e['method'] and 'Everstone' in e['method'] for e in rows)
assert any(e.get('evolutionKind')=='item' and 'Linking Cord' in e['method'] for e in h['65']['entries'] if e['game']=='Pokémon Legends: Arceus')
print('Verified',len(actual_trades),'trade routes, matched trade partners and Arceus Linking Cord alternative')
for sid,item,time in [('472','Razor Fang','at night'),('461','Razor Claw','at night'),('903','Razor Claw','during the day'),('113','Oval Stone','during the day')]:
 rows=[e for e in h[sid]['entries'] if e.get('evolutionKind')=='item' and e['game']=='Pokémon Legends: Arceus']
 assert rows and any(item in e['method'] and time in e['method'] and e['evolutionType'].startswith('UseItem') for e in rows)
print('Verified Arceus day/night evolution ID remapping')
for sid,condition in [('106','Attack greater than Defense'),('107','Defense greater than Attack'),('237','Attack equal to Defense')]:
 rows=[e for e in h[sid]['entries'] if e.get('evolutionKind')=='condition']
 assert rows and all(condition in e['method'] and e['evolutionLevel']==20 for e in rows)
print('Verified Tyrogue level/stat branch requirements')
expected_actions=set()
for e in edges:
 parent=forms.get((e['sourceSpecies'],e['sourceForm']));child=forms.get((e['destinationSpecies'],e['destinationForm']))
 if e['evolutionType'] not in ACTION_TYPES or not e['sourcePresent'] or not e['destinationPresent'] or parent is None or child is None:continue
 if h[str(parent)]['locked'] or h[str(child)]['locked']:continue
 expected_actions.add((child,parent,GAMES[e['gameTable']],e['evolutionType'],e['argument'],e['level'],e['destinationForm']))
actual_actions={(int(k),e['evolutionParent'],e['game'],e['evolutionType'],e['evolutionArgument'],e['evolutionLevel'],e['gameFormId']) for k,g in h.items() for e in g['entries'] if e.get('evolutionKind')=='action'}
assert actual_actions==expected_actions
for sid in ['923','947','954']:
 assert any('1000 steps' in e['method'] for e in h[sid]['entries'] if e.get('evolutionKind')=='action')
assert any('Union Circle' in e['method'] and e['evolutionLevel']==38 for e in h['964']['entries'] if e.get('evolutionKind')=='action')
assert any('Rage Fist 20 times' in e['method'] for e in h['979']['entries'] if e.get('evolutionKind')=='action')
assert any('999 Gimmighoul Coins' in e['method'] for e in h['1000']['entries'] if e.get('evolutionKind')=='action')
print('Verified',len(actual_actions),'walking, multiplayer, coin and move-use evolution routes')
rows=[e for e in h['226']['entries'] if e.get('evolutionType')=='LevelUpWithTeammate']
assert len(rows)==3 and all('Remoraid in the party' in e['method'] for e in rows)
assert any('party menu' in e['method'] for e in rows if e['game']=='Pokémon Legends: Arceus')
rows=[e for e in h['675']['entries'] if e.get('evolutionType')=='LevelUpMoveType']
assert len(rows)==2 and all('Dark-type Pokémon in the party' in e['method'] and e['evolutionLevel']==32 for e in rows)
print('Verified five party-dependent evolution routes')
for sid,text in [('899','Psyshield Bash in agile style 20 times'),('904','Barb Barrage in strong style 20 times')]:
 assert any(text in e['method'] for e in h[sid]['entries'] if e.get('evolutionKind')=='action')
assert any('Peat Block during a full moon' in e['method'] for e in h['901']['entries'] if e.get('evolutionType')=='UseItemFullMoon')
rows=[e for e in h['902']['entries'] if e.get('evolutionKind')=='action']
assert len(rows)==2 and all('294 HP of recoil damage without fainting' in e['method'] and 'White-Striped' in e['method'] for e in rows)
print('Verified Hisuian move-style, recoil and full-moon requirements')
rows=[e for e in h['865']['entries'] if e.get('evolutionType')=='CriticalHitsInBattle']
assert len(rows)==2 and all('three critical hits in one battle' in e['method'] for e in rows)
rows=[e for e in h['867']['entries'] if e.get('evolutionType')=='HitPointsLostInBattle']
assert len(rows)==2 and all('49 HP' in e['method'] and 'without fainting' in e['method'] for e in rows)
assert any('Dusty Bowl' in e['method'] for e in rows if e['game']=='Pokémon Sword / Shield')
assert any('Coulant Waterway' in e['method'] for e in rows if e['game']=='Pokémon Legends: Z-A')
assert any('three wild Bisharp holding a Leader’s Crest' in e['method'] and 'finishing blows' in e['method'] for e in h['983']['entries'] if e.get('evolutionType')=='LevelUpDefeatEquals')
print('Verified critical-hit, damage/location and opponent-item evolution routes')

for sid,kind in [('291','LevelUpNinjask'),('292','LevelUpShedinja')]:
 rows=[e for e in h[sid]['entries'] if e.get('evolutionType')==kind]
 assert len(rows)==2 and all(e['evolutionParent']==290 and e['evolutionLevel']==20 for e in rows)
 if sid=='292':assert all('empty party slot' in e['method'] and 'regular Poké Ball in the bag' in e['method'] for e in rows)
print('Verified Nincada branches and Shedinja party/Poké Ball requirements')

rows=[e for e in h['687']['entries'] if e.get('evolutionType')=='LevelUpInverted']
assert len(rows)==3 and all('handheld mode' in e['method'] and e['evolutionLevel']==30 for e in rows)
assert all('no other controllers connected' in e['method'] for e in rows if e['game']!='Pokémon Legends: Z-A')
assert any(e['game']=='Pokémon Legends: Z-A' and 'select Inkay, then Evolve' in e['method'] and 'no evolution arrow' in e['method'] for e in rows)
print('Verified upside-down evolution conditions, including Legends: Z-A manual party-menu evolution')

rows=[e for g in h.values() for e in g['entries'] if e.get('evolutionType')=='LevelUpWeather']
assert len(rows)==6 and all(e['evolutionLevel']==50 and 'natural rain in the overworld' in e['method'] and 'battle-only rain' in e['method'] for e in rows)
assert all('party menu' in e['method'] for e in rows if e['game'] in {'Pokémon Legends: Arceus','Pokémon Legends: Z-A'})
print('Verified six Goodra weather evolution routes, including regional forms')

for sid,kind in [('266','LevelUpECl5'),('268','LevelUpECgeq5')]:
 rows=[e for e in h[sid]['entries'] if e.get('evolutionType')==kind]
 assert len(rows)==2 and all(e['evolutionLevel']==7 and e['evolutionParent']==265 and 'branch is fixed' in e['method'] for e in rows)
 assert all('party menu' in e['method'] for e in rows if e['game']=='Pokémon Legends: Arceus')
print('Verified four fixed Wurmple evolution branches')

rows=[e for e in h['700']['entries'] if e.get('evolutionType')=='LevelUpAffection50MoveType']
assert len(rows)==4 and all('high friendship while knowing a Fairy-type move' in e['method'] and e['evolutionParent']==133 for e in rows)
assert all('party menu' in e['method'] for e in rows if e['game'] in {'Pokémon Legends: Arceus','Pokémon Legends: Z-A'})
print('Verified four modern Sylveon friendship/Fairy move requirements')

rows=[e for e in h['849']['entries'] if e.get('evolutionType')=='LevelUpNatureAmped']
assert len(rows)==3 and all(e['evolutionLevel']==30 and e['gameFormId']==0 and 'Mints do not change' in e['method'] for e in rows)
for nature in ['Hardy','Brave','Adamant','Naughty','Docile','Impish','Lax','Hasty','Jolly','Naive','Rash','Sassy','Quirky']:
 assert all(nature in e['method'] for e in rows)
print('Verified three Amped Toxtricity routes and original-nature requirement')

for sid,kind,places in [('470','LevelUpForest',['Eterna Forest','The Heartwood']),('471','LevelUpCold',['Route 217','Icepeak Cavern'])]:
 rows=[e for e in h[sid]['entries'] if e.get('evolutionType')==kind]
 assert len(rows)==2 and all(any(place in e['method'] for e in rows) for place in places)
 assert all('party menu' in e['method'] for e in rows if e['game']=='Pokémon Legends: Arceus')
print('Verified four Eevee rock evolution routes and game-specific locations')

for sid,parent in [('462',82),('476',299)]:
 rows=[e for e in h[sid]['entries'] if e.get('evolutionType')=='LevelUpElectric']
 assert len(rows)==2 and all(e['evolutionParent']==parent for e in rows)
 assert any('Mount Coronet' in e['method'] for e in rows if e['game']=='Pokémon Brilliant Diamond / Shining Pearl')
 assert any('Coronet Highlands' in e['method'] and 'party menu' in e['method'] for e in rows if e['game']=='Pokémon Legends: Arceus')
print('Verified four magnetic-field evolution routes and game-specific locations')

rows=[e for e in h['982']['entries'] if e.get('evolutionType')=='LevelUpKnowMoveECElse']
assert len(rows)==1 and rows[0]['evolutionParent']==206 and rows[0]['evolutionArgument']==887
assert 'Hyper Drill' in rows[0]['method'] and 'Two-Segment Form' in rows[0]['method'] and 'resetting cannot change' in rows[0]['method']
print('Verified Dudunsparce move and fixed form branch')

rows=[e for e in h['925']['entries'] if e.get('evolutionType')=='LevelUpInBattleEC100']
assert len(rows)==1 and rows[0]['evolutionParent']==924 and rows[0]['evolutionLevel']==25
assert all(text in rows[0]['method'] for text in ['battle experience','Family of Three','without an animation','candies alone','level-100'])
print('Verified Maushold battle experience, fixed branch and level-100 limitation')

rows=[e for e in h['904']['entries'] if e.get('evolutionType')=='UseMoveBarbBarrage']
assert len(rows)==1 and rows[0]['evolutionArgument']==20 and rows[0]['game']=='Pokémon Legends: Z-A'
assert 'land 20 hits' in rows[0]['method'] and 'Hisuian Qwilfish' in rows[0]['method'] and 'strong style is not required' in rows[0]['method']
print('Verified Z-A Overqwil hit count and distinction from Arceus strong style')

rows=[e for e in h['869']['entries'] if e.get('evolutionType')=='Spin']
assert len(rows)==2 and all(e['evolutionParent']==868 and e['gameFormId']==0 for e in rows)
assert all(all(text in e['method'] for text in ['clockwise','less than 5 seconds','during the day','Vanilla Cream','Strawberry Sweet']) for e in rows)
print('Verified two Vanilla Cream Alcremie spin and Sweet routes')

rows=[e for e in h['350']['entries'] if e.get('evolutionType')=='LevelUpBeauty']
assert len(rows)==3 and all('Beauty at least 170' in e['method'] for e in rows)
assert all('dry Poffins' in e['method'] if e['game']=='Pokémon Brilliant Diamond / Shining Pearl' else 'cannot raise Beauty itself' in e['method'] for e in rows)
print('Verified three Feebas Beauty routes and preparation/transfer requirements')

assert not any(e.get('evolutionType')=='LevelUpSummit' for e in h['740']['entries'])
for game in ['Pokémon Scarlet / Violet','Pokémon Legends: Z-A']:
 assert any(e['game']==game and e.get('evolutionKind')=='item' and 'Ice Stone' in e['method'] for e in h['740']['entries'])
print('Verified Crabominable Ice Stone routes and exclusion of unavailable summit branches')

for sid in ['196','197']:
 rows=[e for e in h[sid]['entries'] if e.get('evolutionKind')=='condition']
 assert all('without a Fairy-type move' in e['method'] for e in rows if e['game']!='Pokémon Brilliant Diamond / Shining Pearl')
 assert all('away from the Moss Rock and Ice Rock' in e['method'] for e in rows if e['game'] in {'Pokémon Brilliant Diamond / Shining Pearl','Pokémon Legends: Arceus'})
print('Verified competing Eevee evolution conditions')
