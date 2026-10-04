"""Verify coverage of every tracked-form wild slot in the decoded sources.
This does not establish exhaustive game/event coverage or gameplay prerequisites.
"""
import json
from pathlib import Path
from collections import Counter
from form_mapping import catalog_forms
from modern_hunts import dlc_game,STATES
ROOT=Path(__file__).parent
catalog=json.loads((ROOT/'data.json').read_text());forms=catalog_forms(catalog)
hunts=json.loads((ROOT/'hunts.json').read_text());wild=json.loads((ROOT/'modern-wild.json').read_text())
index={};mapped=0;excluded=Counter();games=Counter();regional=set()
for key,guide in hunts.items():
 for entry in guide['entries']:
  if 'encounterKind' not in entry:continue
  identity=(int(key),entry['game'],entry['encounterKind'],entry['alphaEncounter'],entry['status'],entry['source'])
  assert identity not in index,identity
  index[identity]=entry
for slot in wild:
 key=forms.get((slot['species'],slot['form']))
 if key is None:
  excluded[(slot['species'],slot['form'])]+=1;continue
 identity=(key,dlc_game(slot['game'],slot['locationId']),slot['kind'],slot['alpha'],STATES[slot['shiny']],slot['source'])
 assert identity in index,identity
 entry=index[identity]
 assert entry['gameFormId']==slot['form'] and slot.get('displayLocation',slot['location']) in entry['locations'],identity
 mapped+=1;games[slot['game']]+=1
 if key>1025:regional.add(key)
report=dict(decodedSlotLocationRecords=len(wild),mappedTrackedFormRecords=mapped,verifiedRoutes=len(index),regionalFormsWithDecodedRoutes=len(regional),recordsByGame=dict(games),excludedUntrackedForms=[dict(species=s,form=f,records=n) for (s,f),n in sorted(excluded.items())],fullHuntingAuditComplete=False,remaining=['Other game tables and raid formats','Gameplay prerequisites and encounter conditions','Breeding availability and exact evolution requirements','GO shiny releases and historical event coverage'])
(ROOT/'modern-coverage-audit.json').write_text(json.dumps(report,indent=2))
print('Verified decoded source coverage:',mapped,'tracked-form slot/location records;',len(index),'routes;',len(regional),'regional forms')
