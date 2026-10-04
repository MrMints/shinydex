"""Verify simple older evolution routes against decoded branches and regressions."""
import json
from pathlib import Path
from form_mapping import catalog_forms
root=Path(__file__).parent
h=json.loads((root/'hunts.json').read_text());forms=catalog_forms(json.loads((root/'data.json').read_text()))
expected=set()
for edge in json.loads((root/'older-evolution-encounters.json').read_text()):
 if edge['evolutionType']!='LevelUp':continue
 parent=forms.get((edge['sourceSpecies'],edge['sourceForm']));child=forms.get((edge['destinationSpecies'],edge['destinationForm']))
 if parent is None or child is None or h[str(parent)]['locked'] or h[str(child)]['locked']:continue
 expected.add((child,parent,edge['level'],edge['destinationForm']))
actual={(int(key),entry['evolutionParent'],entry['evolutionLevel'],entry['gameFormId']) for key,guide in h.items() for entry in guide['entries'] if entry.get('olderEvolutionKind')=='level-only'}
assert actual==expected
assert (2,1,16,0) in actual and (6,5,36,0) in actual
assert (130,129,20,0) in actual and (149,148,55,0) in actual
assert not any(child in {196,197,700,740} for child,parent,level,form in actual)
assert len(actual)==sum(r['type']=='LevelUp' for r in json.loads((root/'older-evolution-route-audit.json').read_text())['routes'])
print('Verified',len(actual),'Ultra Sun/Ultra Moon level requirements; special-condition evolutions excluded')

trades=[(int(key),entry) for key,guide in h.items() for entry in guide['entries'] if entry.get('olderEvolutionKind')=='trade']
assert len(trades)==11
for sid,partner in [(589,'Shelmet'),(617,'Karrablast')]:
 entry=next(e for key,e in trades if key==sid)
 assert 'specifically for '+partner in entry['method'] and 'neither Pokémon may hold an Everstone' in entry['method']
assert any(key>1025 and 'Alolan' in entry['method'] for key,entry in trades)
print('Verified 11 older trade routes, paired partners and Alolan Graveler')

expected_trades=set()
for edge in json.loads((root/'older-evolution-encounters.json').read_text()):
 if edge['evolutionType'] not in {'Trade','TradeShelmetKarrablast'}:continue
 parent=forms.get((edge['sourceSpecies'],edge['sourceForm']));child=forms.get((edge['destinationSpecies'],edge['destinationForm']))
 if parent is None or child is None or h[str(parent)]['locked'] or h[str(child)]['locked']:continue
 expected_trades.add((child,parent,edge['destinationForm'],edge['evolutionType']))
assert {(key,e['evolutionParent'],e['gameFormId'],e['olderEvolutionType']) for key,e in trades}==expected_trades

from older_evolution_hunts import ITEM_TYPES
expected_items=set()
for edge in json.loads((root/'older-evolution-encounters.json').read_text()):
 if edge['evolutionType'] not in ITEM_TYPES:continue
 parent=forms.get((edge['sourceSpecies'],edge['sourceForm']));child=forms.get((edge['destinationSpecies'],edge['destinationForm']))
 if parent is None or child is None or h[str(parent)]['locked'] or h[str(child)]['locked']:continue
 expected_items.add((child,parent,edge['destinationForm'],edge['evolutionType'],edge['argument']))
items=[(int(key),e) for key,g in h.items() for e in g['entries'] if e.get('olderEvolutionKind')=='item']
assert {(key,e['evolutionParent'],e['gameFormId'],e['olderEvolutionType'],e['evolutionArgument']) for key,e in items}==expected_items
for sid,text in [(475,'male Pokémon'),(478,'female Pokémon')]:
 assert any(key==sid and 'Dawn Stone' in e['method'] and text in e['method'] for key,e in items)
for sid in [26,103]:assert any(key==sid and 'in Ultra Space' in e['method'] for key,e in items)
assert any(key>1025 and 'outside Ultra Space' in e['method'] for key,e in items)
print('Verified',len(items),'older item routes, gender restrictions and Ultra Space form conditions')

expected_moves=set()
for edge in json.loads((root/'older-evolution-encounters.json').read_text()):
 if edge['evolutionType']!='LevelUpKnowMove':continue
 parent=forms.get((edge['sourceSpecies'],edge['sourceForm']));child=forms.get((edge['destinationSpecies'],edge['destinationForm']))
 if parent is None or child is None or h[str(parent)]['locked'] or h[str(child)]['locked']:continue
 expected_moves.add((child,parent,edge['argument']))
move_rows=[(int(key),e) for key,g in h.items() for e in g['entries'] if e.get('olderEvolutionKind')=='move']
assert {(key,e['evolutionParent'],e['evolutionArgument']) for key,e in move_rows}==expected_moves
for sid,move in [(463,'Rollout'),(465,'Ancient Power'),(424,'Double Hit'),(473,'Ancient Power'),(185,'Mimic'),(763,'Stomp'),(804,'Dragon Pulse')]:
 assert any(key==sid and 'knowing '+move in e['method'] for key,e in move_rows)
print('Verified',len(move_rows),'older known-move evolution routes')

from older_evolution_hunts import CONDITION_TYPES
expected_conditions=set()
for edge in json.loads((root/'older-evolution-encounters.json').read_text()):
 if edge['evolutionType'] not in CONDITION_TYPES:continue
 parent=forms.get((edge['sourceSpecies'],edge['sourceForm']));child=forms.get((edge['destinationSpecies'],edge['destinationForm']))
 if parent is None or child is None or h[str(parent)]['locked'] or h[str(child)]['locked']:continue
 expected_conditions.add((child,parent,edge['evolutionType']))
conditions=[(int(key),e) for key,g in h.items() for e in g['entries'] if e.get('olderEvolutionKind')=='condition']
assert {(key,e['evolutionParent'],e['olderEvolutionType']) for key,e in conditions}==expected_conditions
assert len(conditions)==19
for key,e in conditions:
 if key==700:
  assert 'two affection hearts in Pokémon Refresh' in e['method'] and 'knowing a Fairy-type move' in e['method']
  assert '220 friendship' not in e['method']
 else:assert 'at least 220 friendship' in e['method']
for sid,time in [(196,'day'),(197,'night'),(315,'day'),(358,'night'),(448,'day')]:
 assert any(key==sid and 'in-game '+time in e['method'] for key,e in conditions)
for sid in [196,197]:
 assert any(key==sid and 'forget Fairy-type moves' in e['method'] and 'Moss Rock and Ice Rock' in e['method'] for key,e in conditions)
assert any(key>1025 and 'Alolan' in e['method'] for key,e in conditions)
print('Verified 18 friendship routes and Sylveon affection, time and competing-branch requirements')

from older_evolution_hunts import GENDER_TIME_TYPES
expected_gender_time=set()
for edge in json.loads((root/'older-evolution-encounters.json').read_text()):
 if edge['evolutionType'] not in GENDER_TIME_TYPES:continue
 parent=forms.get((edge['sourceSpecies'],edge['sourceForm']));child=forms.get((edge['destinationSpecies'],edge['destinationForm']))
 if parent is None or child is None or h[str(parent)]['locked'] or h[str(child)]['locked']:continue
 expected_gender_time.add((child,parent,edge['evolutionType'],edge['level']))
gender_time=[(int(key),e) for key,g in h.items() for e in g['entries'] if e.get('olderEvolutionKind')=='gender-time']
assert {(key,e['evolutionParent'],e['olderEvolutionType'],e['evolutionLevel']) for key,e in gender_time}==expected_gender_time
assert len(gender_time)==11
for sid,level,condition in [(413,20,'female'),(414,20,'male'),(416,21,'female'),(678,25,'male'),(697,39,'in-game day'),(699,39,'in-game night'),(735,20,'in-game day'),(754,34,'in-game day'),(758,33,'female')]:
 assert any(key==sid and 'level '+str(level)+' or higher' in e['method'] and condition in e['method'] for key,e in gender_time)
assert any(key==413 and 'Plant Cloak' in e['method'] for key,e in gender_time)
assert any(e['evolutionParent']==104 and 'outside Ultra Space' in e['method'] and 'in-game night' in e['method'] for key,e in gender_time)
assert any(key==forms[(20,1)] and e['evolutionParent']==forms[(19,1)] and e['evolutionLevel']==20 and 'in-game night' in e['method'] for key,e in gender_time)
print('Verified 11 gender/time routes, female-only evolutions, Plant Cloak and Alolan form conditions')

from older_evolution_hunts import LOCATION_REQUIREMENTS
expected_locations=set()
for edge in json.loads((root/'older-evolution-encounters.json').read_text()):
 if edge['evolutionType'] not in LOCATION_REQUIREMENTS:continue
 parent=forms.get((edge['sourceSpecies'],edge['sourceForm']));child=forms.get((edge['destinationSpecies'],edge['destinationForm']))
 if parent is None or child is None or h[str(parent)]['locked'] or h[str(child)]['locked']:continue
 expected_locations.add((child,parent,edge['evolutionType']))
locations=[(int(key),e) for key,g in h.items() for e in g['entries'] if e.get('olderEvolutionKind')=='location']
assert {(key,e['evolutionParent'],e['olderEvolutionType']) for key,e in locations}==expected_locations
assert len(locations)==7
for sid in [462,476,738]:
 assert any(key==sid and 'Blush Mountain or Vast Poni Canyon' in e['method'] for key,e in locations)
for sid,text in [(470,'Moss Rock in Lush Jungle'),(471,'Ice Rock inside the cave on Mount Lanakila'),(740,'mountain base'),(105,'level 28 or higher in Ultra Space')]:
 assert any(key==sid and text in e['method'] for key,e in locations)
assert all(len(e['sourceReferences'])>=3 for key,e in locations)
print('Verified seven location routes, magnetic fields, evolution rocks and Ultra Space form selection')

party_stats=[(int(key),e) for key,g in h.items() for e in g['entries'] if e.get('olderEvolutionKind')=='party-stat']
assert len(party_stats)==5
for sid,comparison in [(106,'higher than'),(107,'lower than'),(237,'equal to')]:
 assert any(key==sid and e['evolutionParent']==236 and e['evolutionLevel']==20 and 'Attack '+comparison+' Defense after gaining the level' in e['method'] for key,e in party_stats)
assert any(key==226 and e['evolutionParent']==458 and e['evolutionArgument']==223 and 'Remoraid in your party' in e['method'] for key,e in party_stats)
assert any(key==675 and e['evolutionParent']==674 and e['evolutionLevel']==32 and 'Dark-type Pokémon in your party' in e['method'] for key,e in party_stats)
print('Verified five stat/party routes: three Tyrogue branches, Remoraid and Dark-type party requirements')

special=[(int(key),e) for key,g in h.items() for e in g['entries'] if e.get('olderEvolutionKind')=='special']
assert len(special)==8
for sid,level,text in [(266,7,'selecting Silcoon'),(268,7,'selecting Cascoon'),(291,20,'level 20 or higher'),(292,20,'regular Poké Ball'),(687,30,'Nintendo 3DS upside down'),(706,50,'overworld rain or fog')]:
 assert any(key==sid and e['evolutionLevel']==level and text in e['method'] for key,e in special)
assert any(key==292 and 'empty party slot' in e['method'] and 'shiny Shedinja' in e['method'] for key,e in special)
assert any(key==350 and e['evolutionArgument']==170 and 'Omega Ruby or Alpha Sapphire' in e['method'] and 'Pokémon Bank' in e['method'] for key,e in special)
assert all('cannot be changed by resetting' in e['method'] for key,e in special if key in {266,268})
assert any(key==745 and e['evolutionParent']==744 and 'without Own Tempo' in e['method'] and 'cannot be performed in Ultra Moon' in e['method'] for key,e in special)
print('Verified eight special routes, including version-specific Midday Lycanroc')
audit=json.loads((root/'older-evolution-route-audit.json').read_text())
assert audit['decodedBranchCount']==410==audit['routeCount']+len(audit['excludedBranches'])
assert audit['routeCount']==396
assert not any(e['reason']=='unsupported-condition' for e in audit['excludedBranches'])
for edge in audit['excludedBranches']:
 parent=forms.get((edge['sourceSpecies'],edge['sourceForm']));child=forms.get((edge['destinationSpecies'],edge['destinationForm']))
 if edge['reason']=='untracked-form':assert parent is None or child is None
 else:assert edge['reason']=='shiny-locked-parent-or-child' and (h[str(parent)]['locked'] or h[str(child)]['locked'])
print('Accounted for all 410 branches: 396 rendered, 11 untracked forms and three shiny-locked branches; acquisition audit remains incomplete')
