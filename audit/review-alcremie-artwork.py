"""Capture caption evidence for every Alcremie cream/sweet artwork mapping."""
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
CREAMS = {'vanilla-cream':'', 'ruby-cream':'RuC', 'matcha-cream':'MaC', 'mint-cream':'MiC', 'lemon-cream':'LeC', 'salted-cream':'SaC', 'ruby-swirl':'RuS', 'caramel-swirl':'CaS', 'rainbow-swirl':'RaS'}
SWEETS = {'strawberry-sweet':'', 'berry-sweet':'B', 'love-sweet':'L', 'star-sweet':'S', 'clover-sweet':'C', 'flower-sweet':'F', 'ribbon-sweet':'R'}


def main():
    inventory = json.loads((ROOT / 'audit/living-dex-inventory.json').read_text(encoding='utf-8'))
    registry = {x['name']:x for x in json.loads((ROOT / 'audit/archives-images.json').read_text(encoding='utf-8'))}
    mappings = []
    for cream, code in CREAMS.items():
        for sweet, suffix in SWEETS.items():
            identifier = 'alcremie-' + cream + '-' + sweet
            form = next(x for x in inventory['forms'] if x['identifier'] == identifier)
            normal = 'HOME0869' + code + suffix + '.png'
            shiny = 'HOME0869' + suffix + '_s.png'
            assert normal in registry and shiny in registry
            mappings.append({'formId':form['formId'], 'identifier':identifier, 'cream':cream, 'sweet':sweet, 'normalFile':normal, 'shinyFile':shiny})
    files = sorted({m[k] for m in mappings for k in ('normalFile','shinyFile')})
    pages = []
    for offset in range(0, len(files), 40):
        query = urlencode({'action':'query', 'format':'json', 'titles':'|'.join('File:'+f for f in files[offset:offset+40]), 'prop':'imageinfo|revisions', 'iiprop':'url|extmetadata', 'rvprop':'content', 'rvslots':'main'})
        url = 'https://archives.bulbagarden.net/w/api.php?' + query
        with urlopen(Request(url, headers={'User-Agent':'ShinyDex-form-review'}), timeout=60) as response:
            payload = json.load(response)
        pages.extend(payload['query']['pages'].values())
    captions = {}
    for page in pages:
        if 'imageinfo' not in page:
            raise ValueError('Missing caption: ' + page['title'])
        info = page['imageinfo'][0]
        content = page.get('revisions',[{}])[0].get('slots',{}).get('main',{}).get('*','')
        captions[page['title'].removeprefix('File:').replace(' ', '_')] = {'source':info['descriptionurl'], 'url':info['url'], 'description':info.get('extmetadata',{}).get('ImageDescription',{}).get('value',''), 'wikitext':content, 'wikitextSha256':hashlib.sha256(content.encode()).hexdigest()}
    result = {'auditComplete':False, 'scope':'Alcremie 63 cream/sweet combinations; caption capture awaiting independent mapping review', 'mappings':mappings, 'captions':captions}
    (ROOT / 'audit/alcremie-artwork-review.json').write_text(json.dumps(result,indent=2)+'\n', encoding='utf-8')
    print(f'Captured {len(captions)} artwork captions for {len(mappings)} Alcremie forms.')
    for file in ['HOME0869.png','HOME0869CaSR.png','HOME0869R_s.png']:
        print(file, re.sub('<[^>]*>','',captions[file]['wikitext'])[:300])


if __name__ == '__main__':
    main()
