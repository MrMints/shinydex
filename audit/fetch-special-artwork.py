"""Capture source captions and seven official-art candidates before integration."""
import hashlib
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
files = ['0025Pikachu-Cosplay.png', '0025Pikachu-Rock_Star.png', '0025Pikachu-Belle.png',
         '0025Pikachu-Pop_Star.png', '0025Pikachu-PhD.png', '0025Pikachu-Libre.png',
         '0670Floette-Eternal.png', 'Spr_4h_172S.png']
known = {name for page in json.loads((ROOT / 'audit/special-artwork-candidates.json').read_text(encoding='utf-8')) for name in page['images']}
assert set(files) <= known
def fetch(url):
    with urlopen(Request(url, headers={'User-Agent': 'ShinyDex-form-review'}), timeout=60) as response:
        return response.read()
url = 'https://archives.bulbagarden.net/w/api.php?' + urlencode({'action': 'query', 'format': 'json',
      'titles': '|'.join('File:' + file for file in files), 'prop': 'imageinfo|revisions',
      'iiprop': 'url', 'rvprop': 'content', 'rvslots': 'main'})
pages = json.loads(fetch(url))['query']['pages'].values()
records = []
for page in pages:
    file = page['title'][5:].replace(' ', '_')
    info = page['imageinfo'][0]
    content = fetch(info['url'])
    target = ROOT / 'assets/pokemon' / file
    if not target.exists(): target.write_bytes(content)
    im = Image.open(target); im.load(); assert im.format == 'PNG'
    records.append({'file': file, 'source': info['descriptionurl'], 'url': info['url'],
                    'sourceSha256': hashlib.sha256(content).hexdigest(),
                    'localSha256': hashlib.sha256(target.read_bytes()).hexdigest(),
                    'caption': page['revisions'][0]['slots']['main']['*']})
sheet = Image.new('RGB', (1200, 600), 'white'); draw = ImageDraw.Draw(sheet)
for i, record in enumerate(sorted(records, key=lambda p: p['file'])):
    x = (i % 4) * 300; y = (i // 4) * 300
    im = Image.open(ROOT / 'assets/pokemon' / record['file']).convert('RGBA'); im.thumbnail((260, 250))
    sheet.paste(im, (x, y), im); draw.text((x, y + 260), record['file'], fill='black')
destination = ROOT / 'audit/artifacts/living-dex/special.png'
sheet.save(destination)
(ROOT / 'audit/special-artwork-review.json').write_text(json.dumps({'auditComplete': False, 'reviewComplete': False, 'records': records, 'contactSheet': 'audit/artifacts/living-dex/special.png'}, indent=2) + '\n', encoding='utf-8')
print(f'Captured and decoded {len(records)} special-form art candidates; visual/caption review required.')
