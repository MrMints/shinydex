import json
from pathlib import Path
root=Path(__file__).parent
h=json.loads((root/'hunts.json').read_text())
edges=json.loads((root/'gen-three-evolution-encounters.json').read_text())
expected={(e['destinationSpecies'],e['sourceSpecies'],e['level'],e['argument']) for e in edges if e['evolutionType']=='LevelUp' and not e['sourceForm'] and not e['destinationForm']}
for game in ['Pokémon Ruby / Sapphire','Pokémon Emerald','Pokémon FireRed','Pokémon LeafGreen']:
 rows=[(int(k),e) for k,g in h.items() for e in g['entries'] if e.get('olderEvolutionKind')=='gen-three-level' and e['game']==game]
 assert len(rows)==len(expected)
 assert {(key,e['evolutionParent'],e['evolutionLevel'],e['evolutionArgument']) for key,e in rows}==expected
 assert all(key<=386 and e['evolutionParent']<=386 and 'evos_g3.pkl' in e['source'] for key,e in rows)
 assert all('later generations cannot transfer Pokémon back' in e['method'] for key,e in rows)
 if game in {'Pokémon FireRed','Pokémon LeafGreen'}:assert all('National Pokédex' in e['method'] for key,e in rows if key>151)
 assert any(key==6 and e['evolutionParent']==5 and e['evolutionLevel']==36 for key,e in rows)
 assert any(key==149 and e['evolutionParent']==148 and e['evolutionLevel']==55 for key,e in rows)
assert not any(key in {196,197,350} for key,parent,level,arg in expected)
print('Verified',len(expected)*4,'Generation III ordinary level routes across Ruby/Sapphire, Emerald, FireRed and LeafGreen')
expected_items={(e['destinationSpecies'],e['sourceSpecies'],e['evolutionType'],e['argument'],e['level']) for e in edges if e['evolutionType'] in {'UseItem','Trade','TradeHeldItem'} and not e['sourceForm'] and not e['destinationForm']}
for game in ['Pokémon Ruby / Sapphire','Pokémon Emerald','Pokémon FireRed','Pokémon LeafGreen']:
 rows=[(int(k),e) for k,g in h.items() for e in g['entries'] if e.get('olderEvolutionKind') in {'gen-three-item','gen-three-trade'} and e['game']==game]
 assert len(rows)==len(expected_items)
 assert {(key,e['evolutionParent'],e['olderEvolutionType'],e['evolutionArgument'],e['evolutionLevel']) for key,e in rows}==expected_items
 for key,text in [(26,'Thunder Stone'),(182,'Sun Stone'),(186,"King's Rock"),(208,'Metal Coat'),(230,'Dragon Scale'),(233,'Up-Grade'),(367,'DeepSeaTooth'),(368,'DeepSeaScale')]:
  assert any(k==key and text in e['method'] for k,e in rows),(game,key,text)
 assert all('trade back' in e['method'] for key,e in rows if e['olderEvolutionType'] in {'Trade','TradeHeldItem'})
 if game in {'Pokémon FireRed','Pokémon LeafGreen'}:assert all('National Pokédex' in e['method'] for key,e in rows if key>151)
print('Verified',len(expected_items)*4,'Generation III stone and trade routes against generation-specific item IDs')
from gen_three_evolution_hunts import CONDITIONS
conditions={(e['destinationSpecies'],e['sourceSpecies'],e['evolutionType'],e['argument'],e['level']) for e in edges if e['evolutionType'] in CONDITIONS and not e['sourceForm'] and not e['destinationForm']}
for game in ['Pokémon Ruby / Sapphire','Pokémon Emerald','Pokémon FireRed','Pokémon LeafGreen']:
 rows=[(int(k),e) for k,g in h.items() for e in g['entries'] if e.get('olderEvolutionKind')=='gen-three-condition' and e['game']==game]
 assert len(rows)==len(conditions)
 assert {(key,e['evolutionParent'],e['olderEvolutionType'],e['evolutionArgument'],e['evolutionLevel']) for key,e in rows}==conditions
 assert all('220 friendship' in e['method'] for key,e in rows if e['olderEvolutionType']=='LevelUpFriendship')
 for key,text in [(106,'Attack higher than Defense'),(107,'Attack lower than Defense'),(237,'Attack equal to Defense')]:
  assert any(k==key and text in e['method'] and 'level 20' in e['method'] for k,e in rows)
 if game in {'Pokémon FireRed','Pokémon LeafGreen'}:assert all('National Pokédex' in e['method'] for key,e in rows if key>151)
print('Verified',len(conditions)*4,'Generation III friendship and Tyrogue stat routes')
for game in ['Pokémon Ruby / Sapphire','Pokémon Emerald','Pokémon FireRed','Pokémon LeafGreen']:
 rows=[(int(k),e) for k,g in h.items() for e in g['entries'] if e.get('olderEvolutionKind')=='gen-three-time' and e['game']==game]
 assert len(rows)==2
 assert any(key==196 and e['evolutionParent']==133 and '12:00 PM–11:59 PM' in e['method'] for key,e in rows)
 assert any(key==197 and e['evolutionParent']==133 and '12:00 AM–11:59 AM' in e['method'] for key,e in rows)
 assert all('220 friendship' in e['method'] and 'Hoenn game clock' in e['method'] for key,e in rows)
 if game in {'Pokémon FireRed','Pokémon LeafGreen'}:
  assert all('trade shiny Eevee to Ruby, Sapphire or Emerald' in e['method'] and 'rebuild friendship' in e['method'] and 'trade the evolved shiny back' in e['method'] and 'cannot perform this evolution locally' in e['method'] for key,e in rows)
 else:assert all('cannot perform this evolution locally' not in e['method'] for key,e in rows)
print('Verified 8 Generation III Espeon/Umbreon routes with exact Hoenn times and FRLG trade detours')
from gen_three_evolution_hunts import SPECIAL
special={(e['destinationSpecies'],e['sourceSpecies'],e['evolutionType'],e['argument'],e['level']) for e in edges if e['evolutionType'] in SPECIAL and not e['sourceForm'] and not e['destinationForm']}
for game in ['Pokémon Ruby / Sapphire','Pokémon Emerald','Pokémon FireRed','Pokémon LeafGreen']:
 rows=[(int(k),e) for k,g in h.items() for e in g['entries'] if e.get('olderEvolutionKind')=='gen-three-special' and e['game']==game]
 assert len(rows)==len(special)
 assert {(key,e['evolutionParent'],e['olderEvolutionType'],e['evolutionArgument'],e['evolutionLevel']) for key,e in rows}==special
 assert all('personality value' in e['method'] and 'fixed' in e['method'] and 'encryption constant' not in e['method'] for key,e in rows if key in {266,268})
 assert any(key==292 and 'empty party slot' in e['method'] and 'spare Poké Ball is not required' in e['method'] and 'shiny Shedinja' in e['method'] for key,e in rows)
 beauty=next(e for key,e in rows if key==350)
 assert 'Beauty at least 170' in beauty['method'] and 'Pokéblocks' in beauty['method'] and 'sheen limit' in beauty['method']
 if game in {'Pokémon FireRed','Pokémon LeafGreen'}:assert 'trade it here and level up' in beauty['method'] and 'cannot raise Beauty locally' in beauty['method']
 actual={(int(k),e['evolutionParent'],e['olderEvolutionType'],e['evolutionArgument'],e['evolutionLevel']) for k,g in h.items() for e in g['entries'] if e.get('olderEvolutionKind','').startswith('gen-three-') and e['game']==game}
 assert actual=={(e['destinationSpecies'],e['sourceSpecies'],e['evolutionType'],e['argument'],e['level']) for e in edges if not e['sourceForm'] and not e['destinationForm']}
print('Verified 20 Generation III special routes; all 184 decoded branches represented in each game group, acquisition audit still incomplete')
