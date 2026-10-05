"""Inventory generic hunting instructions that still need exact game-specific review."""

# Audit tools resolve shared inputs from the repository, regardless of launch directory.
import os as _audit_os
import sys as _audit_sys
from pathlib import Path as _AuditPath
_audit_root = _AuditPath(__file__).resolve().parents[1]
_audit_sys.path.insert(0, str(_audit_root))
_audit_os.chdir(_audit_root)

import json
from collections import Counter
from pathlib import Path
root=Path(__file__).resolve().parent.parent
hunts=json.loads((root/'hunts.json').read_text())
phrases=('Breed a shiny in this evolutionary line','Catch shiny ','Catch a shiny in this evolutionary line','Breed shiny starter eggs','Breed shiny Alola starter eggs','Breed shiny Galar starter eggs')
rows=[]
for key,guide in hunts.items():
 for entry in guide['entries']:
  if entry.get('evolutionKind') or entry.get('olderEvolutionKind') or entry.get('breedingKind'):continue
  method=entry['method']
  if method.startswith(phrases) and ('evolve' in method.lower() or 'Breed' in method):
   rows.append({'key':int(key),'game':entry['game'],'method':method,'status':entry['status'],'reviewReason':'Verify parent availability, hatchable species/form, exact evolution requirements and transfer prerequisites.'})
report={'exhaustiveHuntingAuditComplete':False,'recordCount':len(rows),'affectedEntries':len({r['key'] for r in rows}),'recordsByGame':dict(Counter(r['game'] for r in rows)),'records':rows}
(root/'audit/legacy-method-review.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('Generic breeding/evolution records requiring review:',len(rows),'across',report['affectedEntries'],'catalog entries')
