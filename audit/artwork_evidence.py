"""Read baseline and living-form evidence without replacing historical reports."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def living_artwork_evidence():
    captions, downloads = {}, {}
    for path in sorted((ROOT / 'audit').glob('*artwork-review.json')):
        report = json.loads(path.read_text(encoding='utf-8'))
        captions.update(report.get('captions', {}))
        for row in report.get('downloads', []) + report.get('records', []):
            downloads[row['file']] = {**row, 'evidenceReport': str(path.relative_to(ROOT))}
            if row.get('caption'):
                captions[row['file']] = {'wikitext': row['caption']}
    path = ROOT / 'audit/alcremie-artwork-download.json'
    for row in json.loads(path.read_text(encoding='utf-8'))['downloadedAndDecoded']:
        downloads[row['file']] = {**row, 'evidenceReport': str(path.relative_to(ROOT))}
    return captions, downloads
