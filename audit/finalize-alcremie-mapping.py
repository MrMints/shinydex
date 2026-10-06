"""Publish the caption-checked, visually reviewed 63-form generation input."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    review = json.loads((ROOT / 'audit/alcremie-artwork-review.json').read_text(encoding='utf-8'))
    downloaded = json.loads((ROOT / 'audit/alcremie-artwork-download.json').read_text(encoding='utf-8'))
    hashes = {r['file']:r for r in downloaded['downloadedAndDecoded']}
    output = []
    for mapping in review['mappings']:
        cream = mapping['cream'].replace('-', ' ').title()
        sweet = mapping['sweet'].replace('-', ' ').title()
        normal_caption = review['captions'][mapping['normalFile']]['wikitext']
        shiny_caption = review['captions'][mapping['shinyFile']]['wikitext']
        if mapping['normalFile'] != 'HOME0869.png':
            assert cream in normal_caption and sweet in normal_caption
        assert 'Shiny' in shiny_caption
        if mapping['shinyFile'] not in {'HOME0869_s.png', 'HOME0869S_s.png'}:
            assert sweet in shiny_caption
        output.append({
            'identity':mapping['identifier'], 'key':200000+mapping['formId'],
            'speciesId':869, 'formId':mapping['formId'], 'formLabel':cream+' · '+sweet,
            'normalFile':mapping['normalFile'], 'shinyFile':mapping['shinyFile'],
            'normalSource':hashes[mapping['normalFile']]['source'],
            'shinySource':hashes[mapping['shinyFile']]['source'],
        })
    assert len(output) == len({r['identity'] for r in output}) == len({r['key'] for r in output}) == 63
    manifest = {'schemaVersion':1, 'scope':'Alcremie persistent cream/sweet forms', 'forms':output,
                'evidence':'audit/alcremie-artwork-review.json',
                'captionExceptions':{'HOME0869.png':'Source omits default Vanilla Cream/Strawberry Sweet; visual review confirms both.', 'HOME0869_s.png':'Source omits Strawberry Sweet; visual review confirms strawberries.', 'HOME0869S_s.png':'Source omits Star Sweet; visual review confirms yellow stars.'}}
    (ROOT / 'reference/pokeapi/living-dex/alcremie-artwork-map.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    downloaded['visualReviewComplete'] = True
    downloaded['visualReview'] = {'date':'2026-10-05', 'scope':'All 63 normal combinations and seven shiny sweet appearances inspected on labeled 9-column/8-row contact sheet.', 'observations':'Cream colors and swirl appearances match columns; strawberry, berry, heart, star, clover, flower and ribbon ornaments match rows. Shiny row has the matching seven ornaments. Small-image review does not certify pixel-perfect fidelity.', 'captionExceptions':manifest['captionExceptions']}
    (ROOT / 'audit/alcremie-artwork-download.json').write_text(json.dumps(downloaded,indent=2)+'\n',encoding='utf-8')
    print('Finalized 63 unique form identities and artwork mappings; original key 869 remains unspecified.')


if __name__ == '__main__':
    main()
