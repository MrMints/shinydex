"""Check corrected Midday version routes and detailed Arceus replacements."""

# Audit tools resolve shared inputs from the repository, regardless of launch directory.
import os as _audit_os
import sys as _audit_sys
from pathlib import Path as _AuditPath
_audit_root = _AuditPath(__file__).resolve().parents[1]
_audit_sys.path.insert(0, str(_audit_root))
_audit_os.chdir(_audit_root)

import json
from pathlib import Path
h=json.loads(Path('hunts.json').read_text())
for moon,sun in [('Pokémon Moon','Pokémon Sun'),('Pokémon Ultra Moon','Pokémon Ultra Sun')]:
 entries=[e for e in h['745']['entries'] if e['game']==moon]
 exact=[e for e in entries if e.get('formEvolutionKind')=='midday-version-trade']
 assert len(exact)==1
 method=exact[0]['method']
 assert sun in method and '25 or higher' in method and 'daytime there' in method and 'trade it back' in method and 'ordinary ability' in method
 assert not any(e['method']=='Catch shiny Rockruff and evolve it' or e['method'].startswith('Breed a shiny in this evolutionary line') for e in entries)
for key,parent,requirement in [('899',234,'Psyshield Bash'),('901',217,'Peat Block')]:
 entries=[e for e in h[key]['entries'] if e['game']=='Pokémon Legends: Arceus' and e.get('evolutionKind') and e.get('evolutionParent')==parent]
 assert entries and any(requirement in e['method'] for e in entries)
 if key=='899':assert any('party menu' in e['method'] for e in entries)
 else:assert any('full moon' in e['method'].lower() for e in entries)
print('Verified Midday Lycanroc version trades and retained detailed Wyrdeer/Ursaluna routes')
