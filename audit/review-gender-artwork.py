"""Capture explicit female artwork captions and retain immutable source evidence."""
import hashlib
import json
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]


def fetch(url):
    with urlopen(Request(url,headers={'User-Agent':'ShinyDex-form-review'}),timeout=60) as response:
        return response.read()


def main():
    registry={r['name']:r for r in json.loads((ROOT/'audit/archives-images.json').read_text(encoding='utf-8'))}
    catalog=json.loads((ROOT/'data.json').read_text(encoding='utf-8'))
    bases={p['id']:p for p in catalog if not p.get('region') and not p.get('livingForm')}
    filenames=sorted(name for name in registry if re.fullmatch(r'HOME\d{4}(?:H)?_f(?:_s)?\.png',name))
    captions={}
    for start in range(0,len(filenames),40):
        query=urlencode({'action':'query','format':'json','titles':'|'.join('File:'+f for f in filenames[start:start+40]),'prop':'revisions','rvprop':'content','rvslots':'main'})
        payload=json.loads(fetch('https://archives.bulbagarden.net/w/api.php?'+query))
        for page in payload['query']['pages'].values():
            text=page['revisions'][0]['slots']['main']['*']
            captions[page['title'][5:].replace(' ','_')]={'wikitext':text,'sha256':hashlib.sha256(text.encode()).hexdigest()}
    def download(name):
        content=fetch(registry[name]['url'])
        target=ROOT/'assets/pokemon'/name
        if not target.exists():target.write_bytes(content)
        image=Image.open(target);image.load();assert image.format=='PNG'
        return {'file':name,'source':registry[name]['descriptionurl'],'sourceSha256':hashlib.sha256(content).hexdigest(),'localSha256':hashlib.sha256(target.read_bytes()).hexdigest()}
    with ThreadPoolExecutor(max_workers=6) as pool:
        downloads=list(pool.map(download,filenames))
    species=sorted({int(name[4:8]) for name in filenames})
    destination=ROOT/'audit/artifacts/living-dex';destination.mkdir(parents=True,exist_ok=True)
    sheets=[]
    for start in range(0,len(species),24):
        subset=species[start:start+24]
        sheet=Image.new('RGB',(1200,6*180),'white');draw=ImageDraw.Draw(sheet)
        for index,sid in enumerate(subset):
            x=(index%4)*300;y=(index//4)*180
            files=[bases[sid]['normalFile'],f'HOME{sid:04}_f.png']
            for column,file in enumerate(files):
                im=Image.open(ROOT/'assets/pokemon'/file).convert('RGBA');im.thumbnail((125,125))
                sheet.paste(im,(x+column*145,y),im)
                draw.text((x+column*145,y+126),file,fill='black')
            draw.text((x,y+145),f'{sid}: '+bases[sid]['speciesName'].encode('ascii','replace').decode(),fill='black')
        name=f'gender-{start//24+1}.png';sheet.save(destination/name);sheets.append('audit/artifacts/living-dex/'+name)
    (ROOT/'audit/gender-artwork-review.json').write_text(json.dumps({'auditComplete':False,'visualReviewComplete':False,'captions':captions,'downloads':downloads,'sheets':sheets,'limits':['Torchic rear-only dimorphism requires separate mapping review.','Regional forms do not automatically inherit a base species gender difference.','Source captions and visual pairs require review before catalog inclusion.']},indent=2)+'\n',encoding='utf-8')
    print(f'Captured {len(captions)} captions and downloaded {len(downloads)} images for {len(species)} base species; {len(sheets)} contact sheets.')


if __name__=='__main__':main()
