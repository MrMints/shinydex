"""Read public Bulbagarden Archives metadata; download consistent HOME art.
No sprite or other-site fallback: normal and shiny must use the same artwork family.
"""
import json, urllib.request, urllib.parse, time, hashlib, concurrent.futures, io
from PIL import Image
from pathlib import Path
ROOT=Path(__file__).parent
UA='ShinyDex/1.0 (personal Pokedex image audit)'
def fetch(url):
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':UA}),timeout=30) as r:
  return r.read()
def metadata():
 files=[]; continuation={}
 while True:
  params={'action':'query','format':'json','list':'allimages','aiprefix':'HOME','ailimit':500,'aiprop':'url|size|mime',**continuation}
  obj=json.loads(fetch('https://archives.bulbagarden.net/w/api.php?'+urllib.parse.urlencode(params)))
  files.extend(obj['query']['allimages']); print('Metadata files:',len(files),flush=True)
  if 'continue' not in obj: break
  continuation=obj['continue'];time.sleep(.3)
 (ROOT/'archives-images.json').write_text(json.dumps(files,separators=(',',':')))
 return files
def download(file):
 path=ROOT/'assets'/'pokemon'/file['name']
 if path.exists():
  try:
   with Image.open(path) as image: image.verify()
   return {'file':file['name'],'ok':True,'cached':True}
  except Exception: pass
 source=file['url'];thumb=source.replace('/media/upload/','/media/upload/thumb/')+'/200px-'+source.split('/')[-1]
 errors=[]
 for url in [thumb,source]:
  try:
   payload=fetch(url)
   with Image.open(io.BytesIO(payload)) as image:
    image.verify()
   path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(payload)
   return {'file':file['name'],'ok':True,'source':url,'sha256':hashlib.sha256(payload).hexdigest()}
  except Exception as e: errors.append(str(e))
 return {'file':file['name'],'ok':False,'errors':errors}
if __name__=='__main__':
 files=json.loads((ROOT/'archives-images.json').read_text()) if (ROOT/'archives-images.json').exists() else metadata()
 registry={f['name']:f for f in files}
 data=json.loads((ROOT/'data.json').read_text())
 missing=[];valid=[]
 for p in data:
  for mode,suffix in [('normal',''),('shiny','_s')]:
   filename=p.get(mode+'File',f'HOME{p["id"]:04}{suffix}.png');file=registry.get(filename)
   if not file: missing.append({'id':p['id'],'name':p['name'],'mode':mode,'requested':filename,'candidates':[f['name'] for f in files if f['name'].startswith(f'HOME{p["id"]:04}')]})
   else: valid.append({'id':p['id'],'name':p['name'],'mode':mode,**file})
 report={'verifiedAt':'2026-10-03','species':len(data),'expectedImages':len(data)*2,'verifiedFiles':len(valid),'missing':missing,'dimensions':sorted(set((f['width'],f['height']) for f in valid))}
 (ROOT/'image-audit.json').write_text(json.dumps(report,indent=2))
 print(json.dumps({'verifiedFiles':len(valid),'missing':missing,'dimensions':report['dimensions']},indent=2),flush=True)
 import sys
 if '--download' in sys.argv:
  unique={f['name']:f for f in valid}; results=[]
  with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
   for i,r in enumerate(pool.map(download,unique.values()),1):
    results.append(r)
    if i%50==0: print('Downloaded:',i,'/',len(unique),'Failed:',sum(not x['ok'] for x in results),flush=True)
  report['downloads']=results;report['loadedImages']=sum(x['ok'] for x in results);report['failedDownloads']=[r for r in results if not r['ok']]
  (ROOT/'image-audit.json').write_text(json.dumps(report,indent=2))
  print('Finished:',report['loadedImages'],'loaded;',len(report['failedDownloads']),'failed',flush=True)
