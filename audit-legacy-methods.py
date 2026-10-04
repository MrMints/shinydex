"""Inventory generic hunting instructions that still need exact game-specific review."""
import json
from collections import Counter
from pathlib import Path
root=Path(__file__).parent
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
(root/'legacy-method-review.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('Generic breeding/evolution records requiring review:',len(rows),'across',report['affectedEntries'],'catalog entries')
