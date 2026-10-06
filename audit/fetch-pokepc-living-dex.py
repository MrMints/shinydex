"""Save the user-supplied public living-dex reference for deferred review."""
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
URL = 'https://pokepc.net/livingdex'

class Slots(HTMLParser):
    def __init__(self):
        super().__init__()
        self.labels = []
    def handle_starttag(self, tag, attrs):
        label = dict(attrs).get('aria-label', '')
        if ' slot ' in label and ', ' in label:
            self.labels.append(label)

with urlopen(Request(URL, headers={'User-Agent': 'ShinyDex-reference-review'}), timeout=60) as response:
    payload = response.read()
parser = Slots()
parser.feed(payload.decode('utf-8'))
assert len(parser.labels) > 1000, 'Incomplete reference capture'
report = {'source': URL, 'reviewedDate': '2026-10-05',
          'preset': 'Grouped by Regions (Optimized)', 'sourceSha256': hashlib.sha256(payload).hexdigest(),
          'userAuthorizedCompletenessReference': True,
          'limitation': 'Working list reference, not independent verification of transfer, eligibility, artwork or hunting routes.',
          'slots': parser.labels}
(ROOT / 'audit/pokepc-living-dex-reference.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print(f'Saved {len(parser.labels)} occupied reference slot labels.')
