"""Verify artwork identities against the Archives' own HOME template captions."""

# Audit tools resolve shared inputs from the repository, regardless of launch directory.
import os as _audit_os
import sys as _audit_sys
from pathlib import Path as _AuditPath
_audit_root = _AuditPath(__file__).resolve().parents[1]
_audit_sys.path.insert(0, str(_audit_root))
_audit_os.chdir(_audit_root)

import json,re,urllib.parse,urllib.request,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
data=json.loads((ROOT/'data.json').read_text())
cachepath=ROOT/'audit/image-captions.json'
cache=json.loads(cachepath.read_text()) if cachepath.exists() else {}
files=[p[m+'File'] for p in data for m in ['normal','shiny']]
missing=[f for f in files if f not in cache]
for i in range(0,len(missing),50):
 params={'action':'query','format':'json','prop':'revisions','rvprop':'content','titles':'|'.join('File:'+f for f in missing[i:i+50])}
 url='https://archives.bulbagarden.net/w/api.php?'+urllib.parse.urlencode(params)
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'ShinyDex/1.0 (personal Pokedex image audit)'}),timeout=30) as response: obj=json.load(response)
 for page in obj['query']['pages'].values():
  if page.get('revisions'): cache[page['title'].removeprefix('File:').replace(' ','_')]=page['revisions'][0]['*']
 cachepath.write_text(json.dumps(cache,separators=(',',':')))
 print('Captions:',len(cache),'/',len(files),flush=True)
 time.sleep(.2)
problems=[];exceptions=[]
for p in data:
 for mode in ['normal','shiny']:
  filename=p[mode+'File']; caption=cache.get(filename,''); template=re.search(r'\{\{HOME\|0*(\d+)\|([^|}]+)(?:\|([^}]*))?',caption,re.I)
  if template and p['id']==146 and p.get('region')=='galar' and int(template[1])==145 and template[2]=='Moltres':
   exceptions.append({'file':filename,'issue':'Archives caption incorrectly numbers Moltres as 0145; filename, species name and both images visually verified as Galarian Moltres'})
  elif not template or int(template[1])!=p['id']: problems.append({'file':filename,'issue':'Missing or mismatching HOME species caption'})
  elif ('shiny' in (template[3] or '').lower())!=(mode=='shiny'): problems.append({'file':filename,'issue':'Normal/shiny caption mismatch'})
  if p.get('region') and template:
   expected={'alola':'alolan','galar':'galarian','hisui':'hisuian','paldea':'paldean'}[p['region']]
   if p['id']==550: expected='white-striped'
   if expected not in (template[3] or '').lower(): problems.append({'file':filename,'issue':'Regional caption mismatch','caption':template[0]})
(ROOT/'audit/caption-audit.json').write_text(json.dumps({'checkedImages':len(files),'issues':problems,'sourceCaptionExceptions':exceptions},indent=2))
print('Identity audit:',len(files),'images;',len(problems),'issues',flush=True)
