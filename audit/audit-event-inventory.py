"""Rebuild research candidates; this inventory does not certify event coverage."""

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

ROOT=Path(__file__).resolve().parent.parent
report_path=ROOT/'audit/pending-event-review.json'
previous=json.loads(report_path.read_text(encoding='utf-8'))
hunts=json.loads((ROOT/'hunts.json').read_text(encoding='utf-8'))
candidates=[]
groups={}
for key,record in hunts.items():
 for entry in record['entries']:
  method=entry['method']
  historical=method.startswith('Historical ')
  vague=method=='Shiny event distribution'
  undated=entry['status'].startswith(('Past event','Event rotation')) and not any(str(year) in method for year in range(1996,2027))
  if not (historical or vague or undated):continue
  kind=('max-raid' if 'Max Raid' in method else 'outbreak' if 'outbreak' in method else 'tera-raid' if 'Tera Raid' in method else 'gift-or-go')
  row=dict(key=key,game=entry['game'],method=method,status=entry['status'],source=entry.get('source'),kind=kind,needsAnnouncementReview=True)
  for field in ('raidKind','eventIndices','gameFormId','hostVersions','raidStars','gigantamax','sourceReferences'):
   if field in entry:row[field]=entry[field]
  if 'Verified historical example:' in method:
   row['partialAnnouncementReview']='2024 summer example verified; other merged events remain open.'
  candidates.append(row)
  identity=(kind,row['source'],tuple(row.get('eventIndices',[])))
  group=groups.setdefault(identity,dict(kind=kind,source=row['source'],eventIndices=row.get('eventIndices',[]),routeCount=0,catalogKeys=set(),games=set(),needsAnnouncementReview=True))
  group['routeCount']+=1
  group['catalogKeys'].add(key)
  group['games'].add(entry['game'])
for group in groups.values():
 group['catalogKeys']=sorted(group['catalogKeys'],key=int)
 group['games']=sorted(group['games'])
report=dict(checked='2026-10-04',fullEventAuditComplete=False,candidateCount=len(candidates),countsByKind=dict(Counter(row['kind'] for row in candidates)),limitations=previous['limitations'],candidates=candidates,reviewedHistoricalWindows=previous.get('reviewedHistoricalWindows',[]),sourceGroupCount=len(groups),sourceGroups=list(groups.values()))
assert sum(group['routeCount'] for group in groups.values())==len(candidates)
report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'{len(candidates)} current candidates in {len(groups)} source/index research groups; event coverage remains incomplete.')
