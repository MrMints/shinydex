"""Verify all tracked raid records map to a source-backed guide entry."""
import json
from pathlib import Path
from collections import Counter
from form_mapping import catalog_forms
from raid_hunts import identity
from modern_hunts import STATES
ROOT=Path(__file__).parent
catalog=json.loads((ROOT/'data.json').read_text());forms=catalog_forms(catalog)
hunts=json.loads((ROOT/'hunts.json').read_text());raids=json.loads((ROOT/'raid-encounters.json').read_text())
index={};counts=Counter();excluded=Counter();checked=0
for key,guide in hunts.items():
 for entry in guide['entries']:
  if 'raidKind' not in entry:continue
  item=(int(key),entry['game'],entry['raidKind'],entry['status'],entry['gigantamax'],tuple(entry['hostVersions']),entry['source'])
  assert item not in index,item
  index[item]=entry
for raid in raids:
 item=identity(raid,forms)
 if item is None:
  excluded[(raid['species'],raid['form'])]+=1;continue
 key,game,kind,shiny,gmax,hosts,source=item
 target=(key,game,kind,STATES[shiny],gmax,hosts,source)
 assert target in index,target
 entry=index[target]
 assert entry['gameFormId']==raid['form'] and raid['location'] in entry['locations'],target
 assert set(raid.get('stars',[]))<=set(entry['raidStars']),target
 if 'eventIndex' in raid:assert raid['eventIndex'] in entry['eventIndices'],target
 checked+=1;counts[kind]+=1
assert any(e.get('raidKind')=='dynamax-adventure' and e['status']=='Huntable' for e in hunts['150']['entries'])
assert any(e.get('raidKind')=='tera-raid-mightiest' and e['status']=='Shiny Locked' for e in hunts['150']['entries'])
assert any(e['status']=='Huntable' and e['raidStars']==[5] for e in hunts['999']['entries'] if 'raidKind' in e)
assert any(e['status']=='Shiny Locked' and e['raidStars']==[1,2,3,4] for e in hunts['999']['entries'] if 'raidKind' in e)
report=dict(sourceRecords=len(raids),verifiedTrackedRecords=checked,guideRoutes=len(index),recordsByMethod=dict(counts),excludedUntrackedForms=[dict(species=s,form=f,records=n) for (s,f),n in sorted(excluded.items())],fullHuntingAuditComplete=False)
(ROOT/'raid-coverage-audit.json').write_text(json.dumps(report,indent=2))
print('Verified raid coverage:',checked,'tracked records;',len(index),'routes')
