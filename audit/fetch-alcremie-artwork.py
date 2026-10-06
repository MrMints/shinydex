"""Download source artwork with decoding and immutable evidence hashes."""
import hashlib
import io
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.request import Request, urlopen
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]


def main():
    report = json.loads((ROOT / 'audit/alcremie-artwork-review.json').read_text(encoding='utf-8'))
    def fetch(item):
        name, evidence = item
        with urlopen(Request(evidence['url'], headers={'User-Agent':'ShinyDex-form-review'}), timeout=60) as response:
            content = response.read()
        image = Image.open(io.BytesIO(content))
        image.load()
        assert image.format == 'PNG'
        target = ROOT / 'assets/pokemon' / name
        if target.exists():
            # Existing catalog art is resized; retain it and record both hashes.
            local = Image.open(target)
            local.load()
        else:
            target.write_bytes(content)
        return {'file':name, 'sourceSha256':hashlib.sha256(content).hexdigest(), 'localSha256':hashlib.sha256(target.read_bytes()).hexdigest(), 'source':evidence['source'], 'downloadUrl':evidence['url'], 'sourceSize':list(image.size)}
    with ThreadPoolExecutor(max_workers=6) as pool:
        downloads = list(pool.map(fetch, report['captions'].items()))
    output = ROOT / 'audit/artifacts/living-dex'
    output.mkdir(parents=True, exist_ok=True)
    sheet = Image.new('RGB',(9*150,8*180),'white')
    draw = ImageDraw.Draw(sheet)
    for index, mapping in enumerate(report['mappings']):
        # Rows are sweets; columns are creams, with a separate final shiny row.
        x, y = (index//7)*150, (index%7)*180
        image = Image.open(ROOT / 'assets/pokemon' / mapping['normalFile']).convert('RGBA')
        image.thumbnail((125,125))
        sheet.paste(image,(x+(150-image.width)//2,y),image)
        draw.text((x+3,y+126),mapping['cream'].replace('-',' '),fill='black')
        draw.text((x+3,y+142),mapping['sweet'].replace('-',' '),fill='black')
    for index, mapping in enumerate(report['mappings'][:7]):
        image = Image.open(ROOT / 'assets/pokemon' / mapping['shinyFile']).convert('RGBA')
        image.thumbnail((125,125))
        sheet.paste(image,(index*150,7*180),image)
        draw.text((index*150+3,7*180+126),mapping['sweet'].replace('-',' '),fill='black')
        draw.text((index*150+3,7*180+142),'Shiny',fill='black')
    sheet.save(output / 'alcremie.png')
    (ROOT / 'audit/alcremie-artwork-download.json').write_text(json.dumps({'auditComplete':False,'downloadedAndDecoded':downloads,'visualReviewComplete':False,'contactSheet':'audit/artifacts/living-dex/alcremie.png'},indent=2)+'\n',encoding='utf-8')
    print(f'Downloaded and decoded {len(downloads)} source images; contact sheet ready for visual review.')


if __name__ == '__main__':
    main()
