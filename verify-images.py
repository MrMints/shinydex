"""Decode every local artwork file and retain reproducible integrity evidence.

Archives captions establish identity; this independent check establishes that
the actual local payloads decode and that each normal/shiny pair is distinct.
Neither check alone is a visual review of every image.
"""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

root = Path(__file__).resolve().parent
catalog = json.loads((root / 'data.json').read_text(encoding='utf-8'))
captions = json.loads((root / 'image-captions.json').read_text(encoding='utf-8'))
registry = {item['name']: item for item in json.loads(
    (root / 'archives-images.json').read_text(encoding='utf-8'))}
results = []
issues = []
for pokemon in catalog:
    pair = []
    for mode in ('normal', 'shiny'):
        filename = pokemon[mode + 'File']
        path = root / pokemon[mode]
        try:
            payload = path.read_bytes()
            with Image.open(path) as artwork:
                assert artwork.format == 'PNG', 'Artwork must be PNG'
                artwork.verify()
            with Image.open(path) as artwork:
                artwork.load()  # Decode all pixels, beyond header/CRC validation.
                width, height = artwork.size
                assert width > 0 and height > 0
                assert artwork.convert('RGBA').getbbox(), 'Empty artwork'
            assert filename in registry, 'Missing Archives metadata'
            assert filename in captions, 'Missing Archives identity caption'
            assert path.name == filename, 'Catalog filename/path mismatch'
            assert pokemon[mode + 'Source'] == registry[filename]['descriptionurl'], 'Source page mismatch'
            digest = hashlib.sha256(payload).hexdigest()
            pair.append(digest)
            results.append({'key': pokemon['key'], 'mode': mode, 'file': filename,
                            'sha256': digest, 'bytes': len(payload),
                            'width': width, 'height': height})
        except Exception as error:
            issues.append({'key': pokemon['key'], 'mode': mode, 'file': filename,
                           'error': str(error)})
    if len(pair) == 2 and pair[0] == pair[1]:
        issues.append({'key': pokemon['key'], 'error': 'Identical normal/shiny payloads'})

report = {'checkedAt': datetime.now(timezone.utc).isoformat(),
          'expectedFiles': len(catalog) * 2, 'decodedFiles': len(results),
          'issues': issues, 'files': results,
          'limitations': ['Pixel decoding and caption matching do not replace visual review.',
                          'Hashes identify local payloads, not an independently fetched upstream copy.']}
(root / 'local-image-audit.json').write_text(
    json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print(f"Decoded {len(results)}/{len(catalog) * 2} local images; {len(issues)} issues")
assert not issues, f"See local-image-audit.json for {len(issues)} issues"
