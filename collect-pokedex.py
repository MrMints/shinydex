"""Cache public Bulbapedia Dex templates only; resumable, never fetches during builds."""
import concurrent.futures
import hashlib
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'reference' / 'bulbapedia-pokedex'
OUT.mkdir(parents=True, exist_ok=True)
catalog = json.loads((ROOT / 'data.json').read_text(encoding='utf-8'))
species = {p['id']: p for p in catalog}

def collect(item):
    sid, pokemon = item
    target = OUT / f'{sid}.json'
    if target.exists():
        return 'cached'
    title = urllib.parse.unquote(urllib.parse.urlparse(pokemon['source']).path.split('/wiki/')[1])
    query = urllib.parse.urlencode({'action': 'parse', 'page': title, 'prop': 'wikitext|revid', 'format': 'json', 'redirects': 1})
    url = 'https://bulbapedia.bulbagarden.net/w/api.php?' + query
    for attempt in range(4):
        try:
            request = urllib.request.Request(url, headers={'User-Agent': 'ShinyDex-data-research/1.0'})
            raw = urllib.request.urlopen(request, timeout=60).read()
            parsed = json.loads(raw)['parse']
            text = parsed['wikitext']['*']
            start = text.index('{{Dex/Header')
            end = text.index('{{Dex/Footer', start)
            end = text.index('}}', end) + 2
            record = {'speciesId': sid, 'title': parsed['title'], 'revisionId': parsed.get('revid'),
                      'source': pokemon['source'] + '#Pokédex_entries',
                      'retrievedAt': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                      'responseSha256': hashlib.sha256(raw).hexdigest(), 'wikitext': text[start:end]}
            target.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            time.sleep(.3)
            return 'fetched'
        except Exception as error:
            if attempt == 3:
                return {'speciesId': sid, 'error': str(error)}
            time.sleep(2 ** attempt)

if __name__ == '__main__':
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for i, result in enumerate(pool.map(collect, sorted(species.items())), 1):
            results.append(result)
            if i % 50 == 0:
                print(f'{i}/{len(species)} processed', flush=True)
    report = {'speciesCount': len(species), 'cached': results.count('cached'), 'fetched': results.count('fetched'),
              'failures': [r for r in results if isinstance(r, dict)]}
    (ROOT / 'audit' / 'pokedex-collection.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report), flush=True)
