
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
edges=json.loads((root/'audit/gen-five-evolution-encounters.json').read_text())
expected={(e['destinationSpecies'],e['sourceSpecies'],e['level']) for e in edges if e['evolutionType']=='LevelUp' and not e['sourceForm'] and not e['destinationForm'] and not h[str(e['sourceSpecies'])]['locked'] and not h[str(e['destinationSpecies'])]['locked']}
for game in ['Pokémon Black / White','Pokémon Black 2 / White 2']:
 rows=[(int(k),e) for k,g in h.items() for e in g['entries'] if e.get('olderEvolutionKind')=='gen-five-level' and e['game']==game]
 assert {(key,e['evolutionParent'],e['evolutionLevel']) for key,e in rows}==expected
 assert all(key<=649 and e['evolutionParent']<=649 and 'evos_g5.pkl' in e['source'] for key,e in rows)
 assert all('one-way Poké Transfer from Generation IV' in e['method'] and 'HOME' not in e['method'] for key,e in rows)
assert (6,5,36) in expected and (149,148,55) in expected
assert not any(key in {196,197,700} for key,parent,level in expected)
print('Verified',len(expected)*2,'Generation V level requirements against every eligible decoded branch in both game pairs')
from gen_six_evolution_hunts import ITEM_TYPES
expected_special={(e['destinationSpecies'],e['sourceSpecies'],e['evolutionType'],e['argument'],e['level']) for e in edges if e['evolutionType'] in {'Trade','TradeShelmetKarrablast','LevelUpKnowMove'}|ITEM_TYPES and not e['sourceForm'] and not e['destinationForm'] and not h[str(e['sourceSpecies'])]['locked'] and not h[str(e['destinationSpecies'])]['locked']}
for game in ['Pokémon Black / White','Pokémon Black 2 / White 2']:
 rows=[(int(k),e) for k,g in h.items() for e in g['entries'] if e.get('olderEvolutionKind') in {'gen-five-item','gen-five-trade','gen-five-move'} and e['game']==game]
 assert {(key,e['evolutionParent'],e['olderEvolutionType'],e['evolutionArgument'],e['evolutionLevel']) for key,e in rows}==expected_special
 assert all('Generation IV' in e['method'] and 'Bank transfer' not in e['method'] for key,e in rows)
 for sid,text in [(475,'male Pokémon'),(478,'female Pokémon'),(589,'Shelmet'),(617,'Karrablast'),(463,'Rollout')]:assert any(key==sid and text in e['method'] for key,e in rows)
print('Verified',len(expected_special)*2,'Generation V item, trade and known-move routes against decoded requirements')
from gen_six_evolution_hunts import CONDITION_TYPES
expected_conditions={(e['destinationSpecies'],e['sourceSpecies'],e['evolutionType'],e['argument'],e['level']) for e in edges if e['evolutionType'] in CONDITION_TYPES and not e['sourceForm'] and not e['destinationForm'] and not h[str(e['sourceSpecies'])]['locked'] and not h[str(e['destinationSpecies'])]['locked']}
for game in ['Pokémon Black / White','Pokémon Black 2 / White 2']:
 rows=[(int(k),e) for k,g in h.items() for e in g['entries'] if e.get('olderEvolutionKind')=='gen-five-condition' and e['game']==game]
 assert {(key,e['evolutionParent'],e['olderEvolutionType'],e['evolutionArgument'],e['evolutionLevel']) for key,e in rows}==expected_conditions
 assert not any('Fairy' in e['method'] or 'Sylveon' in e['method'] or 'Amie' in e['method'] for key,e in rows)
 for sid,text in [(196,'220 friendship'),(197,'in-game night'),(416,'female Pokémon'),(237,'equal to Defense'),(226,'Remoraid')]:assert any(key==sid and text in e['method'] for key,e in rows)
print('Verified',len(expected_conditions)*2,'Generation V friendship, gender, time, stat and party routes; later-generation Eevee requirements excluded')
from gen_five_evolution_hunts import SPECIAL
expected_remaining={(e['destinationSpecies'],e['sourceSpecies'],e['evolutionType'],e['argument'],e['level']) for e in edges if e['evolutionType'] in SPECIAL and not e['sourceForm'] and not e['destinationForm']}
for game in ['Pokémon Black / White','Pokémon Black 2 / White 2']:
 rows=[(int(k),e) for k,g in h.items() for e in g['entries'] if e.get('olderEvolutionKind')=='gen-five-special' and e['game']==game]
 assert {(key,e['evolutionParent'],e['olderEvolutionType'],e['evolutionArgument'],e['evolutionLevel']) for key,e in rows}==expected_remaining
 for sid,text in [(462,'Chargestone Cave'),(476,'Chargestone Cave'),(470,'Pinwheel Forest'),(471,'Twist Mountain'),(292,'empty party slot'),(350,'Generation IV or earlier')]:assert any(key==sid and text in e['method'] for key,e in rows)
 assert all('personality value' in e['method'] and 'encryption constant' not in e['method'] for key,e in rows if key in {266,268})
print('Verified 18 remaining Gen V special/location routes, including Wurmple PID and pre-Gen V Beauty preparation')
