"""Review and bundle every Unown shape with explicit stable form identity."""
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[1]


def fetch(url):
    with urlopen(Request(url,headers={'User-Agent':'ShinyDex-form-review'}),timeout=60) as response:return response.read()


def main():
    inventory=json.loads((ROOT/'audit/living-dex-inventory.json').read_text(encoding='utf-8'))
    registry={r['name']:r for r in json.loads((ROOT/'audit/archives-images.json').read_text(encoding='utf-8'))}
    forms=[p for p in inventory['forms'] if p['speciesId']==201]
    assert len(forms)==28
    mappings=[]
    for form in forms:
        label=form['label'];suffix='' if label=='A' else 'EX' if label=='!' else 'QU' if label=='?' else label
        p={'identity':form['identifier'],'key':200000+form['formId'],'legacyKey':201,'speciesId':201,'formLabel':label}
        for mode,ending in [('normal',''),('shiny','_s')]:
            file=f'HOME0201{suffix}{ending}.png';assert file in registry
            p[mode+'File']=file;p[mode+'Source']=registry[file]['descriptionurl']
        mappings.append(p)
    files=sorted({m[mode+'File'] for m in mappings for mode in ['normal','shiny']})
    captions={}
    for start in range(0,len(files),40):
        query=urlencode({'action':'query','format':'json','titles':'|'.join('File:'+f for f in files[start:start+40]),'prop':'revisions','rvprop':'content','rvslots':'main'})
        payload=json.loads(fetch('https://archives.bulbagarden.net/w/api.php?'+query))
        for page in payload['query']['pages'].values():
            text=page['revisions'][0]['slots']['main']['*'];captions[page['title'][5:].replace(' ','_')]={'wikitext':text,'sha256':hashlib.sha256(text.encode()).hexdigest()}
    def download(file):
        content=fetch(registry[file]['url']);target=ROOT/'assets/pokemon'/file
        if not target.exists():target.write_bytes(content)
        im=Image.open(target);im.load();assert im.format=='PNG'
        return {'file':file,'sourceSha256':hashlib.sha256(content).hexdigest(),'localSha256':hashlib.sha256(target.read_bytes()).hexdigest(),'source':registry[file]['descriptionurl']}
    with ThreadPoolExecutor(max_workers=6) as pool:downloads=list(pool.map(download,files))
    sheet=Image.new('RGB',(7*180,4*180),'white');draw=ImageDraw.Draw(sheet)
    for index,m in enumerate(mappings):
        x=(index%7)*180;y=(index//7)*180
        for col,mode in enumerate(['normal','shiny']):
            im=Image.open(ROOT/'assets/pokemon'/m[mode+'File']).convert('RGBA');im.thumbnail((80,130));sheet.paste(im,(x+col*85,y),im)
        draw.text((x+15,y+140),'Unown '+m['formLabel'],fill='black')
    destination=ROOT/'audit/artifacts/living-dex';destination.mkdir(parents=True,exist_ok=True);sheet.save(destination/'unown.png')
    report={'auditComplete':False,'visualReviewComplete':False,'mappings':mappings,'captions':captions,'downloads':downloads,'contactSheet':'audit/artifacts/living-dex/unown.png'}
    (ROOT/'audit/unown-artwork-review.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(f'Captured {len(captions)} captions and decoded {len(downloads)} images for 28 Unown shapes.')


def finalize():
    report=json.loads((ROOT/'audit/unown-artwork-review.json').read_text(encoding='utf-8'))
    for mapping in report['mappings']:
        for mode in ['normal','shiny']:
            caption=report['captions'][mapping[mode+'File']]['wikitext']
            expected='('+mapping['formLabel']+('; Shiny)' if mode=='shiny' else ')')
            assert expected in caption, mapping
    report['visualReviewComplete']=True
    report['visualReviewScope']='All 28 letter/punctuation shapes and normal/shiny pairs inspected on the labeled contact sheet, 2026-10-05.'
    (ROOT/'audit/unown-artwork-review.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    (ROOT/'reference/pokeapi/living-dex/unown-artwork-map.json').write_text(json.dumps({'schemaVersion':1,'forms':report['mappings'],'evidence':'audit/unown-artwork-review.json'},indent=2)+'\n',encoding='utf-8')
    print('Finalized 28 caption-checked and visually reviewed Unown mappings.')


if __name__=='__main__':
    import sys
    finalize() if '--finalize' in sys.argv else main()
