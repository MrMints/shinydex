"""Capture evidence for the next persistent-form families; finalize after review."""
import csv
import hashlib
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[1]
# Explicit candidate mappings, reconciled against source captions before inclusion.
GROUPS={
386:[('normal',''),('attack','A'),('defense','D'),('speed','S')],
412:[('plant',''),('sandy','G'),('trash','S')],413:[('plant',''),('sandy','G'),('trash','S')],
422:[('west',''),('east','E')],423:[('west',''),('east','E')],
479:[('',''),('heat','O'),('wash','W'),('frost','R'),('fan','F'),('mow','L')],
585:[('spring',''),('summer','S'),('autumn','A'),('winter','W')],586:[('spring',''),('summer','S'),('autumn','A'),('winter','W')],
666:[('meadow',''),('icy-snow','Icy'),('polar','Pol'),('tundra','Tun'),('continental','Con'),('garden','Gar'),('elegant','Ele'),('modern','Mod'),('marine','Mar'),('archipelago','Arc'),('high-plains','Hig'),('sandstorm','San'),('river','Riv'),('monsoon','Mon'),('savanna','Sav'),('sun','Sun'),('ocean','Oce'),('jungle','Jun'),('fancy','Fan'),('poke-ball','Pok')],
669:[('red',''),('yellow','Y'),('orange','O'),('blue','B'),('white','W')],
670:[('red',''),('yellow','Y'),('orange','O'),('blue','B'),('white','W')],
671:[('red',''),('yellow','Y'),('orange','O'),('blue','B'),('white','W')],
710:[('average',''),('small','Sm'),('large','La'),('super','Su')],711:[('average',''),('small','Sm'),('large','La'),('super','Su')],
741:[('baile',''),('pom-pom','Po'),('pau','Pa'),('sensu','Se')],745:[('midday',''),('midnight','Mn'),('dusk','D')],
849:[('amped',''),('low-key','L')],925:[('family-of-four',''),('family-of-three','T')],
931:[('green-plumage',''),('blue-plumage','B'),('yellow-plumage','Y'),('white-plumage','W')],
978:[('curly',''),('droopy','D'),('stretchy','S')],982:[('two-segment',''),('three-segment','Th')],
}


def fetch(url):
    with urlopen(Request(url,headers={'User-Agent':'ShinyDex-form-review'}),timeout=60) as response:return response.read()


def main(groups=GROUPS, batch='persistent'):
    inventory=json.loads((ROOT/'audit/living-dex-inventory.json').read_text(encoding='utf-8'))
    registry={r['name']:r for r in json.loads((ROOT/'audit/archives-images.json').read_text(encoding='utf-8'))}
    catalog=json.loads((ROOT/'data.json').read_text(encoding='utf-8'))
    names={p['id']:p['name'] for p in catalog if p['key']==p['id']}
    pokemon={int(p['id']):p for p in csv.DictReader((ROOT/'reference/pokeapi/living-dex/pokemon.csv').open(encoding='utf-8'))}
    mappings=[]
    for sid,forms in groups.items():
        for label,suffix in forms:
            identifier=names[sid].split('-')[0]+'-'+label if label else names[sid]
            candidates=[p for p in inventory['forms'] if p['speciesId']==sid and p['identifier']==identifier]
            assert len(candidates)==1,(sid,identifier)
            form=candidates[0];record=pokemon[form['pokemonId']]
            p={'identity':identifier,'key':200000+form['formId'],'legacyKey':sid,'speciesId':sid,'formLabel':form['label'],'pokemonId':form['pokemonId'],'height':int(record['height']),'weight':int(record['weight'])}
            for mode,ending in [('normal',''),('shiny','_s')]:
                mode_suffix = suffix[0 if mode == 'normal' else 1] if isinstance(suffix, tuple) else suffix
                file=f'HOME{sid:04}{mode_suffix}{ending}.png'
                if batch == 'cap' and mode == 'shiny': file=f'HOME{sid:04}{mode_suffix}.png'
                assert file in registry,file
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
    destination=ROOT/'audit/artifacts/living-dex';destination.mkdir(parents=True,exist_ok=True)
    sheets=[]
    for start in range(0,len(mappings),24):
        sheet=Image.new('RGB',(1200,6*180),'white');draw=ImageDraw.Draw(sheet)
        for index,m in enumerate(mappings[start:start+24]):
            x=(index%4)*300;y=(index//4)*180
            for col,mode in enumerate(['normal','shiny']):
                im=Image.open(ROOT/'assets/pokemon'/m[mode+'File']).convert('RGBA');im.thumbnail((130,130));sheet.paste(im,(x+col*145,y),im)
            draw.text((x+3,y+140),m['identity'].encode('ascii','replace').decode(),fill='black')
        file=f'{batch}-{start//24+1}.png';sheet.save(destination/file);sheets.append('audit/artifacts/living-dex/'+file)
    report={'auditComplete':False,'reviewComplete':False,'mappings':mappings,'captions':captions,'downloads':downloads,'contactSheets':sheets}
    (ROOT/f'audit/{batch}-artwork-review.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(f'Captured {len(captions)} captions and decoded {len(downloads)} images for {len(mappings)} candidate forms; {len(sheets)} review sheets.')


if __name__=='__main__':main()
