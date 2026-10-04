"""Report evolution branches still awaiting rendered requirement verification."""
import json
from collections import Counter
from pathlib import Path
from form_mapping import catalog_forms
from evolution_hunts import GAMES
root=Path(__file__).parent
forms=catalog_forms(json.loads((root/'data.json').read_text()))
hunts=json.loads((root/'hunts.json').read_text())
counts=Counter();pending=[]
exceptions=json.loads((root/'evolution-exceptions.json').read_text())['exceptions']
reviews=json.loads((root/'evolution-review-evidence.json').read_text())['reviews']
for edge in json.loads((root/'evolution-encounters.json').read_text()):
 parent=forms.get((edge['sourceSpecies'],edge['sourceForm']))
 child=forms.get((edge['destinationSpecies'],edge['destinationForm']))
 if not edge['sourcePresent'] or not edge['destinationPresent']:counts['absent game form']+=1
 elif parent is None or child is None:counts['untracked alternate form']+=1
 elif hunts[str(parent)]['locked'] or hunts[str(child)]['locked']:counts['globally shiny locked']+=1
 elif any(edge['gameTable']==x['gameTable'] and edge['sourceSpecies']==x['sourceSpecies'] and edge['evolutionType']==x['evolutionType'] for x in exceptions):counts['verified non-working legacy branch']+=1
 elif any(entry.get('evolutionKind') and entry['game']==GAMES[edge['gameTable']] and entry.get('evolutionParent')==parent and entry.get('evolutionType')==edge['evolutionType'] and entry.get('evolutionArgument')==edge['argument'] and entry.get('evolutionLevel')==edge['level'] and entry.get('gameFormId')==edge['destinationForm'] for entry in hunts[str(child)]['entries']):counts['rendered requirement']+=1
 else:
  counts['pending requirement']+=1
  pending.append(edge)
for edge in pending:
 edge['reviewEvidence']=[review for review in reviews if all(edge[field]==review[field] for field in ('gameTable','sourceSpecies','evolutionType'))]
report={'exhaustiveHuntingAuditComplete':False,'classificationCounts':dict(counts),'pendingTypes':dict(Counter(e['evolutionType'] for e in pending)),'pendingBranches':pending,'limitation':'Rendered requirements do not verify shiny parent acquisition, transfers, older games, event availability or complete hunting coverage.'}
(root/'evolution-pending-audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='pendingBranches'},indent=2))
