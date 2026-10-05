"""Inventory ORAS source encounters missing from DexNav coverage; no eligibility inference."""

# Audit tools resolve shared inputs from the repository, regardless of launch directory.
import os as _audit_os
import sys as _audit_sys
from pathlib import Path as _AuditPath
_audit_root = _AuditPath(__file__).resolve().parents[1]
_audit_sys.path.insert(0, str(_audit_root))
_audit_os.chdir(_audit_root)

import hashlib,json,struct
from pathlib import Path
from dexnav_hunts import routes
root=Path('reference/pkhex/PKHeX.Core')
labels=(root/'Resources/text/locations/gen6/text_xy_00000_en.txt').read_text(encoding='utf-8-sig').splitlines()
covered=routes();missing=[];sources=[];location_candidates={}

def location_key(name):
 """Compare location names only; this does not verify rooms or encounter terrain."""
 name=name.casefold().removeprefix('hoenn ')
 return ''.join(character for character in name if character.isalnum())
for code,game in [('or','Pok\u00e9mon Omega Ruby'),('as','Pok\u00e9mon Alpha Sapphire')]:
 path=root/('Resources/legality/wild/Gen6/encounter_'+code+'.pkl');b=path.read_bytes();sources.append({'path':str(path),'sha256':hashlib.sha256(b).hexdigest()})
 n=struct.unpack_from('<H',b,2)[0];offsets=struct.unpack_from('<'+str(n+1)+'I',b,4);seen={}
 assert offsets[-1]==len(b)
 for start,end in zip(offsets,offsets[1:]):
  block=b[start:end];loc=struct.unpack_from('<H',block)[0];kind=block[2]
  assert kind in (0,6,7) and (len(block)-4)%4==0
  if kind==6:continue
  for pos in range(4,len(block),4):
   raw,lo,hi=struct.unpack_from('<HBB',block,pos);species=raw&1023;form=raw>>11
   if species==0:continue
   label=labels[loc] if loc<len(labels) else None
   locations=covered.get((species,game),set())
   # Preserve location gaps even when the species has a hunt elsewhere.
   # A matching base name is only an inventory match, not gameplay verification.
   if label and not any(location_key(label)==location_key(location.split(' ·')[0]) for location in locations):
    key=(species,game,loc,form)
    location_candidates[key]={'species':species,'game':game,'locationId':loc,'location':label,'form':form,'eligibilityVerified':False}
   if (species,game) in covered:continue
   item={'locationId':loc,'location':labels[loc] if loc<len(labels) else None,'slotType':kind,'form':form,'minLevel':lo,'maxLevel':hi}
   if item not in seen.setdefault(species,[]):seen[species].append(item)
 for species,encounters in sorted(seen.items()):missing.append({'species':species,'game':game,'encounters':encounters,'eligibilityVerified':False})
report={'fullCoverageVerified':False,'purpose':'Candidate species/game gaps from pinned ORAS wild tables. Standard slot type does not distinguish hidden-only, fishing, water or ice-room restrictions. Each candidate needs gameplay eligibility and prerequisites verified before publication.','scopeLimit':'Zero missing species/game pairs means each recorded species has at least one route. It does not prove every encounter location, form, prerequisite or hunting method is included. Location matches compare only normalized base names, not rooms or terrain; reported location candidates require manual review.','sources':sources,'missingSpeciesGamePairs':len(missing),'candidates':missing,'missingLocationFormCandidates':len(location_candidates),'locationCandidates':list(location_candidates.values())}
# The legality snapshot retains both hideout location IDs in both versions.
# Keep those raw candidates visible, with reviewed gameplay exclusions, rather
# than silently promoting an inaccessible map or deleting evidence.
exclusions=[]
for candidate in report['locationCandidates']:
 wrong_hideout=((candidate['game'].endswith('Omega Ruby') and candidate['location']=='Team Aqua Hideout')
                or (candidate['game'].endswith('Alpha Sapphire') and candidate['location']=='Team Magma Hideout'))
 if wrong_hideout:
  exclusions.append({**candidate, 'eligibilityVerified':True, 'eligible':False,
                     'reason':'This hideout is replaced by the other team hideout in this game.',
                     'source':'https://bulbapedia.bulbagarden.net/wiki/Aqua_Hideout#In_the_games'})
report['reviewedExclusions']=exclusions
report['unreviewedLocationFormCandidates']=len(location_candidates)-len(exclusions)
report['scopeLimit']+=' Reviewed exclusions preserve cross-version source records; zero unreviewed normalized candidates still does not certify exhaustive floor, form or prerequisite coverage.'
Path('audit/dexnav-coverage-gaps.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('Recorded',len(missing),'candidate species/game gaps; none promoted without eligibility verification.')
print('Recorded',len(location_candidates),'location/form candidates needing review.')
print('Reviewed',len(exclusions),'inaccessible cross-version hideout records;',report['unreviewedLocationFormCandidates'],'unreviewed normalized candidates remain.')
