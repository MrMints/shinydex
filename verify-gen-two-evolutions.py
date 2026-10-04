import json
from pathlib import Path
root=Path(__file__).parent
h=json.loads((root/'hunts.json').read_text());edges=json.loads((root/'gen-two-evolution-encounters.json').read_text())
expected={(e['destinationSpecies'],e['sourceSpecies'],e['level'],e['argument']) for e in edges if e['evolutionType']=='LevelUp' and e['level'] and not e['sourceForm'] and not e['destinationForm']}
for game in ['Pokémon Gold','Pokémon Silver','Pokémon Crystal']:
 rows=[(int(k),e) for k,g in h.items() for e in g['entries'] if e.get('olderEvolutionKind')=='gen-two-level' and e['game']==game]
 assert len(rows)==len(expected)
 assert {(key,e['evolutionParent'],e['evolutionLevel'],e['evolutionArgument']) for key,e in rows}==expected
 assert all(key<=251 and e['evolutionParent']<=251 and 'evos_g2.pkl' in e['source'] for key,e in rows)
 assert all('Generation III and later cannot transfer Pokémon back' in e['method'] for key,e in rows)
 assert any(key==6 and e['evolutionParent']==5 and e['evolutionLevel']==36 for key,e in rows)
 assert any(key==149 and e['evolutionParent']==148 and e['evolutionLevel']==55 for key,e in rows)
assert not any(key in {196,197,700} for key,parent,level,arg in expected)
print('Verified',len(expected)*3,'Generation II level routes in Gold, Silver and Crystal; conditional evolutions and acquisitions remain under audit')
from gen_two_evolution_hunts import FRIENDSHIP
zero={(e['sourceSpecies'],e['destinationSpecies']) for e in edges if e['evolutionType']=='LevelUp' and not e['level']}
assert zero==FRIENDSHIP
for game in ['Pokémon Gold','Pokémon Silver','Pokémon Crystal']:
 rows=[(int(k),e) for k,g in h.items() for e in g['entries'] if e.get('olderEvolutionKind')=='gen-two-friendship' and e['game']==game]
 assert len(rows)==8 and {(e['evolutionParent'],k) for k,e in rows}==FRIENDSHIP
 assert all('220 friendship' in e['method'] and 'level 0' not in e['method'] and 'Friendship_Evolution' in ' '.join(e['sourceReferences']) for k,e in rows)
 assert any(k==196 and '4:00 AM–5:59 PM' in e['method'] for k,e in rows)
 assert any(k==197 and '6:00 PM–3:59 AM' in e['method'] for k,e in rows)
print('Verified 24 Generation II friendship routes, including its distinct Espeon/Umbreon clock windows')
other={(e['destinationSpecies'],e['sourceSpecies'],e['evolutionType'],e['argument']) for e in edges if e['evolutionType'] in {'UseItem','Trade'}}
for game in ['Pokémon Gold','Pokémon Silver','Pokémon Crystal']:
 rows=[(int(k),e) for k,g in h.items() for e in g['entries'] if e.get('olderEvolutionKind') in {'gen-two-item','gen-two-trade'} and e['game']==game]
 assert len(rows)==28 and {(k,e['evolutionParent'],e['olderEvolutionType'],e['evolutionArgument']) for k,e in rows}==other
 for key,text in [(26,'Thunder Stone'),(182,'Sun Stone'),(186,"King's Rock"),(199,"King's Rock"),(208,'Metal Coat'),(212,'Metal Coat'),(230,'Dragon Scale'),(233,'Up-Grade')]:assert any(k==key and text in e['method'] for k,e in rows)
 assert all('trade back' in e['method'] for k,e in rows if e['olderEvolutionType']=='Trade')
print('Verified 84 Generation II stone/trade routes, with held-item requirements restored from gameplay references')
for game in ['Pokémon Gold','Pokémon Silver','Pokémon Crystal']:
 rows=[(int(k),e) for k,g in h.items() for e in g['entries'] if e.get('olderEvolutionKind')=='gen-two-stat' and e['game']==game]
 assert len(rows)==3
 for key,text in [(106,'higher than'),(107,'lower than'),(237,'equal to')]:assert any(k==key and e['evolutionParent']==236 and e['evolutionLevel']==20 and 'Attack '+text+' Defense' in e['method'] and 'Tyrogue#Evolution_data' in e['source'] for k,e in rows)
print('Verified 9 Generation II Tyrogue stat branches omitted by the source legality tree')
