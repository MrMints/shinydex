
# Audit tools resolve shared inputs from the repository, regardless of launch directory.
import os as _audit_os
import sys as _audit_sys
from pathlib import Path as _AuditPath
_audit_root = _AuditPath(__file__).resolve().parents[1]
_audit_sys.path.insert(0, str(_audit_root))
_audit_os.chdir(_audit_root)

import json
from pathlib import Path
from form_mapping import catalog_forms
root=Path(__file__).resolve().parent.parent
catalog=json.loads((root/'data.json').read_text());forms=catalog_forms(catalog)
h=json.loads((root/'hunts.json').read_text());edges=json.loads((root/'audit/lets-go-evolution-encounters.json').read_text())
expected={(forms[(e['destinationSpecies'],e['destinationForm'])],forms[(e['sourceSpecies'],e['sourceForm'])],e['level']) for e in edges if e['evolutionType']=='LevelUp' and 1<=e['sourceSpecies']<=151 and 1<=e['destinationSpecies']<=151 and (e['sourceSpecies'],e['sourceForm']) in forms and (e['destinationSpecies'],e['destinationForm']) in forms}
for game in ["Pokémon Let's Go, Pikachu!","Pokémon Let's Go, Eevee!"]:
 rows=[(int(k),e) for k,g in h.items() for e in g['entries'] if e.get('olderEvolutionKind')=='lets-go-level' and e['game']==game]
 assert len(rows)==len(expected)
 assert {(k,e['evolutionParent'],e['evolutionLevel']) for k,e in rows}==expected
 assert all('these games have no breeding' in e['method'] and 'evos_gg.pkl' in e['source'] for k,e in rows)
 assert (6,5,36) in expected and (149,148,55) in expected
 assert not any(k in {196,197,700,809} for k,p,l in expected)
print('Verified',len(expected)*2,'Let’s Go level routes, including independent Alolan parent forms; remaining evolution methods under audit')
expected_other={(forms[(e['destinationSpecies'],e['destinationForm'])],forms[(e['sourceSpecies'],e['sourceForm'])],e['evolutionType'],e['argument']) for e in edges if e['evolutionType'] in {'UseItem','Trade'} and 1<=e['sourceSpecies']<=151 and 1<=e['destinationSpecies']<=151 and (e['sourceSpecies'],e['sourceForm']) in forms and (e['destinationSpecies'],e['destinationForm']) in forms}
for game in ["Pokémon Let's Go, Pikachu!","Pokémon Let's Go, Eevee!"]:
 rows=[(int(k),e) for k,g in h.items() for e in g['entries'] if e.get('olderEvolutionKind') in {'lets-go-item','lets-go-trade'} and e['game']==game]
 assert len(rows)==len(expected_other)
 assert {(k,e['evolutionParent'],e['olderEvolutionType'],e['evolutionArgument']) for k,e in rows}==expected_other
 for sid,text in [(26,'Thunder Stone'),(31,'Moon Stone'),(38,'Fire Stone'),(45,'Leaf Stone'),(62,'Water Stone')]:assert any(k==sid and text in e['method'] for k,e in rows)
 assert all('partner Pikachu and Eevee cannot evolve' in e['method'] for k,e in rows if e['evolutionParent'] in {25,133})
 assert all('trade back' in e['method'] and 'Let’s Go player' in e['method'] for k,e in rows if e['olderEvolutionType']=='Trade')
 for p in catalog:
  if p['id'] in {28,38} and p.get('region')=='alola':assert any(k==p['key'] and 'Ice Stone' in e['method'] for k,e in rows)
 actual={(int(k),e['evolutionParent'],e['olderEvolutionType'],e['evolutionArgument']) for k,g in h.items() for e in g['entries'] if e.get('olderEvolutionKind','').startswith('lets-go-') and e['game']==game}
 assert len(actual)==len(expected)+len(expected_other)
print('Verified',len(expected_other)*2,'Let’s Go stone and trade routes, Alolan Ice Stones and partner exceptions')
