
# Audit tools resolve shared inputs from the repository, regardless of launch directory.
import os as _audit_os
import sys as _audit_sys
from pathlib import Path as _AuditPath
_audit_root = _AuditPath(__file__).resolve().parents[1]
_audit_sys.path.insert(0, str(_audit_root))
_audit_os.chdir(_audit_root)

import json
from pathlib import Path
root=Path(__file__).resolve().parent.parent
h=json.loads((root/'hunts.json').read_text())
edges=json.loads((root/'audit/gen-six-evolution-encounters.json').read_text())
expected={(e['destinationSpecies'],e['sourceSpecies'],e['level']) for e in edges if e['evolutionType']=='LevelUp' and e['sourceSpecies']!=705 and not e['sourceForm'] and not e['destinationForm'] and e['sourceSpecies']<=721 and e['destinationSpecies']<=721 and not h[str(e['sourceSpecies'])]['locked'] and not h[str(e['destinationSpecies'])]['locked']}
count=0
for game in ['Pokémon X / Y','Pokémon Omega Ruby / Alpha Sapphire']:
 rows=[(int(k),e) for k,g in h.items() for e in g['entries'] if e.get('olderEvolutionKind')=='gen-six-level' and e['game']==game]
 assert {(key,e['evolutionParent'],e['evolutionLevel']) for key,e in rows}==expected
 assert all('evos_g6.pkl' in e['source'] and 'HOME' not in e['method'] for key,e in rows)
 count+=len(rows)
assert (6,5,36) in expected and (149,148,55) in expected
assert not any(key in {196,197,700} for key,parent,level in expected)
print('Verified',count,'Gen VI level routes against every eligible decoded branch in both game pairs')
from gen_six_evolution_hunts import SUPPORTED
expected_special={(e['destinationSpecies'],e['sourceSpecies'],e['evolutionType'],e['argument'],e['level']) for e in edges if e['evolutionType'] in SUPPORTED-{'LevelUp'} and not e['sourceForm'] and not e['destinationForm'] and not h[str(e['sourceSpecies'])]['locked'] and not h[str(e['destinationSpecies'])]['locked']}
for game in ['Pokémon X / Y','Pokémon Omega Ruby / Alpha Sapphire']:
 rows=[(int(k),e) for k,g in h.items() for e in g['entries'] if e.get('olderEvolutionKind') in {'gen-six-item','gen-six-trade','gen-six-move'} and e['game']==game]
 assert {(key,e['evolutionParent'],e['olderEvolutionType'],e['evolutionArgument'],e['evolutionLevel']) for key,e in rows}==expected_special
 for sid,text in [(475,'male Pokémon'),(478,'female Pokémon'),(463,'Rollout'),(424,'Double Hit'),(589,'specifically for Shelmet'),(617,'specifically for Karrablast')]:assert any(key==sid and text in e['method'] for key,e in rows)
 assert not any('Ultra Space' in e['method'] or 'HOME' in e['method'] for key,e in rows)
 assert all('Evolution_data' in e['sourceReferences'][1] for key,e in rows)
print('Verified',len(expected_special)*2,'Gen VI item, trade and known-move routes, including gender and paired-trade conditions')
from gen_six_evolution_hunts import CONDITION_TYPES
expected_conditions={(e['destinationSpecies'],e['sourceSpecies'],e['evolutionType'],e['argument'],e['level']) for e in edges if e['evolutionType'] in CONDITION_TYPES and not e['sourceForm'] and not e['destinationForm'] and not h[str(e['sourceSpecies'])]['locked'] and not h[str(e['destinationSpecies'])]['locked']}
for game in ['Pokémon X / Y','Pokémon Omega Ruby / Alpha Sapphire']:
 rows=[(int(k),e) for k,g in h.items() for e in g['entries'] if e.get('olderEvolutionKind')=='gen-six-condition' and e['game']==game]
 assert {(key,e['evolutionParent'],e['olderEvolutionType'],e['evolutionArgument'],e['evolutionLevel']) for key,e in rows}==expected_conditions
 assert not any('Pokémon Refresh' in e['method'] for key,e in rows)
 assert any(key==700 and 'two affection hearts in Pokémon-Amie' in e['method'] and 'Fairy-type move' in e['method'] for key,e in rows)
 for sid,text in [(196,'220 friendship'),(197,'in-game night'),(416,'female Pokémon'),(237,'equal to Defense'),(226,'Remoraid'),(675,'Dark-type')]:assert any(key==sid and text in e['method'] for key,e in rows)
print('Verified',len(expected_conditions)*2,'Gen VI conditional routes, including Pokémon-Amie affection and friendship/time/party/stat requirements')
for game in ['Pokémon X / Y','Pokémon Omega Ruby / Alpha Sapphire']:
 rows=[(int(k),e) for k,g in h.items() for e in g['entries'] if e.get('olderEvolutionKind')=='gen-six-special' and e['game']==game]
 assert len(rows)==7
 assert any(key==706 and 'natural overworld rain' in e['method'] and 'fog does not satisfy' in e['method'] for key,e in rows)
 assert any(key==687 and 'Nintendo 3DS upside down' in e['method'] for key,e in rows)
 assert any(key==292 and 'empty party slot' in e['method'] and 'regular Poké Ball' in e['method'] for key,e in rows)
 for sid in [266,268]:assert any(key==sid and 'cannot be changed by resetting' in e['method'] for key,e in rows)
 assert any(key==350 and 'Beauty at least 170' in e['method'] and ('blue Pokéblocks' if game=='Pokémon Omega Ruby / Alpha Sapphire' else 'X/Y cannot raise Beauty themselves') in e['method'] for key,e in rows)
print('Verified 14 Gen VI special routes, including Goodra rain omitted by the reference table and game-specific Beauty preparation')
for game,magnetic,moss,ice in [('Pokémon X / Y','Kalos Route 13','Kalos Route 20','Frost Cavern'),('Pokémon Omega Ruby / Alpha Sapphire','New Mauville','Petalburg Woods','Shoal Cave')]:
 rows=[(int(k),e) for k,g in h.items() for e in g['entries'] if e.get('olderEvolutionKind')=='gen-six-location' and e['game']==game]
 assert len(rows)==4
 for sid in [462,476]:assert any(key==sid and magnetic in e['method'] for key,e in rows)
 assert any(key==470 and moss in e['method'] for key,e in rows)
 assert any(key==471 and ice in e['method'] for key,e in rows)
 if game=='Pokémon Omega Ruby / Alpha Sapphire':assert any(key==471 and 'low tide' in e['method'] for key,e in rows)
 assert all(len(e['sourceReferences'])>=3 for key,e in rows)
print('Verified eight Gen VI location routes with separate Kalos/Hoenn locations and Shoal Cave low tide')
