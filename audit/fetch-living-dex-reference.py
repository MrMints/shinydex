"""Snapshot public form inputs at one immutable PokeAPI commit.

These are shared catalog-generation inputs, kept under reference/pokeapi.
Inventory and review output belongs in audit/.
"""
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'reference' / 'pokeapi' / 'living-dex'
FILES = ('pokemon_forms.csv', 'pokemon_form_names.csv', 'pokemon.csv', 'pokemon_species.csv')


def fetch(url):
    with urlopen(Request(url, headers={'User-Agent': 'ShinyDex-form-review'}), timeout=45) as response:
        return response.read()


def main():
    revision = json.loads(fetch('https://api.github.com/repos/PokeAPI/pokeapi/commits/master'))['sha']
    DEST.mkdir(parents=True, exist_ok=True)
    manifest = {'repository': 'https://github.com/PokeAPI/pokeapi', 'commit': revision, 'files': []}
    for name in FILES:
        url = f'https://raw.githubusercontent.com/PokeAPI/pokeapi/{revision}/data/v2/csv/{name}'
        content = fetch(url)
        (DEST / name).write_bytes(content)
        manifest['files'].append({'name': name, 'url': url, 'sha256': hashlib.sha256(content).hexdigest()})
    (DEST / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(f'Snapshotted {len(FILES)} tables at {revision}')


if __name__ == '__main__':
    main()
