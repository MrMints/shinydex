"""Capture image references from source pages for non-HOME forms."""
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
results = []
for title in ('Cosplay Pikachu', 'Spiky-eared Pichu', 'Floette', 'Pichu'):
    url = 'https://bulbapedia.bulbagarden.net/w/api.php?' + urlencode({'action': 'parse', 'page': title, 'prop': 'images', 'redirects': 1, 'format': 'json'})
    with urlopen(Request(url, headers={'User-Agent': 'ShinyDex-form-review'}), timeout=60) as response:
        payload = json.load(response)
    assert 'parse' in payload, payload
    images = [name for name in payload['parse']['images'] if any(word in name.lower() for word in ('pikachu', 'pichu', 'floette')) or (title == 'Pichu' and '172' in name)]
    results.append({'page': title, 'source': url, 'images': images})
(ROOT / 'audit/special-artwork-candidates.json').write_text(json.dumps(results, indent=2) + '\n', encoding='utf-8')
for result in results:
    print(result['page'] + ': ' + ', '.join(result['images']))
