import json
from pathlib import Path
root=Path(__file__).parent
h=json.loads((root/'hunts.json').read_text())
edges=json.loads((root/'gen-four-evolution-encounters.json').read_text())
expected={(e['destinationSpecies'],e['sourceSpecies'],e['level'],e['argument']) for e in edges if e['evolutionType']=='LevelUp' and not e['sourceForm'] and not e['destinationForm'] and not h[str(e['sourceSpecies'])]['locked'] and not h[str(e['destinationSpecies'])]['locked']}
for game in ['Pokémon Diamond / Pearl','Pokémon Platinum','Pokémon HeartGold / SoulSilver']:
 rows=[(int(k),e) for k,g in h.items() for e in g['entries'] if e.get('olderEvolutionKind')=='gen-four-level' and e['game']==game]
 assert len(rows)==len(expected)
 assert {(key,e['evolutionParent'],e['evolutionLevel'],e['evolutionArgument']) for key,e in rows}==expected
 assert all(key<=493 and e['evolutionParent']<=493 and 'evos_g4.pkl' in e['source'] for key,e in rows)
 assert all('one-way Pal Park transfer from Generation III' in e['method'] and 'HOME' not in e['method'] for key,e in rows)
assert any(child==6 and parent==5 and level==36 for child,parent,level,arg in expected)
assert any(child==149 and parent==148 and level==55 for child,parent,level,arg in expected)
assert not any(child in {196,197,700} for child,parent,level,arg in expected)
print('Verified',len(expected)*3,'Generation IV ordinary level routes across all three game groups')
from gen_six_evolution_hunts import ITEM_TYPES
expected_special={(e['destinationSpecies'],e['sourceSpecies'],e['evolutionType'],e['argument'],e['level']) for e in edges if e['evolutionType'] in {'Trade','LevelUpKnowMove'}|ITEM_TYPES and not e['sourceForm'] and not e['destinationForm'] and not h[str(e['sourceSpecies'])]['locked'] and not h[str(e['destinationSpecies'])]['locked']}
for game in ['Pokémon Diamond / Pearl','Pokémon Platinum','Pokémon HeartGold / SoulSilver']:
 rows=[(int(k),e) for k,g in h.items() for e in g['entries'] if e.get('olderEvolutionKind') in {'gen-four-item','gen-four-trade','gen-four-move'} and e['game']==game]
 assert len(rows)==len(expected_special)
 assert {(key,e['evolutionParent'],e['olderEvolutionType'],e['evolutionArgument'],e['evolutionLevel']) for key,e in rows}==expected_special
 assert all('evos_g4.pkl' in e['source'] and 'one-way Pal Park transfer from Generation III' in e['method'] for key,e in rows)
 for sid,text in [(475,'male Pokémon'),(478,'female Pokémon'),(463,'Rollout'),(464,'Protector'),(466,'Electirizer'),(467,'Magmarizer')]:
  assert any(key==sid and text in e['method'] for key,e in rows)
print('Verified',len(expected_special)*3,'Generation IV item, trade and known-move routes')
from gen_six_evolution_hunts import CONDITION_TYPES
conditions={(e['destinationSpecies'],e['sourceSpecies'],e['evolutionType'],e['argument'],e['level']) for e in edges if e['evolutionType'] in CONDITION_TYPES and not e['sourceForm'] and not e['destinationForm']}
for game in ['Pokémon Diamond / Pearl','Pokémon Platinum','Pokémon HeartGold / SoulSilver']:
 rows=[(int(k),e) for k,g in h.items() for e in g['entries'] if e.get('olderEvolutionKind')=='gen-four-condition' and e['game']==game]
 assert len(rows)==len(conditions)
 assert {(key,e['evolutionParent'],e['olderEvolutionType'],e['evolutionArgument'],e['evolutionLevel']) for key,e in rows}==conditions
 for sid,text in [(106,'Attack higher than Defense'),(107,'Attack lower than Defense'),(237,'Attack equal to Defense'),(196,'220 friendship during the in-game day'),(197,'220 friendship during the in-game night'),(416,'female Pokémon'),(226,'Remoraid in your party')]:
  assert any(key==sid and text in e['method'] for key,e in rows)
 if game=='Pokémon HeartGold / SoulSilver':assert all('Moss Rock' not in e['method'] and 'Ice Rock' not in e['method'] for key,e in rows)
print('Verified',len(conditions)*3,'Generation IV friendship, time, gender, stat and party requirements')
from gen_four_evolution_hunts import SPECIAL
special={(e['destinationSpecies'],e['sourceSpecies'],e['evolutionType'],e['argument'],e['level']) for e in edges if e['evolutionType'] in SPECIAL and not e['sourceForm'] and not e['destinationForm']}
for game in ['Pokémon Diamond / Pearl','Pokémon Platinum','Pokémon HeartGold / SoulSilver']:
 rows=[(int(k),e) for k,g in h.items() for e in g['entries'] if e.get('olderEvolutionKind')=='gen-four-special' and e['game']==game]
 assert len(rows)==len(special)
 assert {(key,e['evolutionParent'],e['olderEvolutionType'],e['evolutionArgument'],e['evolutionLevel']) for key,e in rows}==special
 assert any(key==292 and 'regular Poké Ball' in e['method'] and 'empty party slot' in e['method'] and 'shiny Shedinja' in e['method'] for key,e in rows)
 assert all('personality value' in e['method'] and 'fixed' in e['method'] and 'encryption constant' not in e['method'] for key,e in rows if key in {266,268})
 beauty=next(e for key,e in rows if key==350)
 assert 'Beauty at least 170' in beauty['method'] and 'sheen' in beauty['method']
 if game=='Pokémon HeartGold / SoulSilver':
  assert 'Daisy Oak' in beauty['method'] and 'haircut brothers' in beauty['method'] and 'Poffins' not in beauty['method']
  assert all('trade the shiny parent to Diamond, Pearl or Platinum' in e['method'] and 'trade the evolved shiny back' in e['method'] for key,e in rows if key in {462,470,471,476})
 else:
  assert 'dry Poffins' in beauty['method']
  for key,text in [(462,'Mount Coronet'),(476,'Mount Coronet'),(470,'Eterna Forest'),(471,'Sinnoh Route 217')]:assert any(k==key and text in e['method'] for k,e in rows)
print('Verified',len(special)*3,'Generation IV special routes, including HGSS grooming and Sinnoh trade detours')
for game in ['Pokémon Diamond / Pearl','Pokémon Platinum','Pokémon HeartGold / SoulSilver']:
 actual={(int(k),e['evolutionParent'],e['olderEvolutionType'],e['evolutionArgument'],e['evolutionLevel']) for k,g in h.items() for e in g['entries'] if e.get('olderEvolutionKind','').startswith('gen-four-') and e['game']==game}
 assert actual=={(e['destinationSpecies'],e['sourceSpecies'],e['evolutionType'],e['argument'],e['level']) for e in edges if not e['sourceForm'] and not e['destinationForm']}
print('All 246 decoded Generation IV branches accounted for in each game group; full hunting acquisition coverage remains incomplete')
