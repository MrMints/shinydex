"""Create labeled normal/shiny contact sheets for human artwork review.

These are audit derivatives only; runtime artwork stays untouched. Each pair
shows normal on the left and shiny on the right, in the exact catalog order.
"""
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'Archive' / 'image-review'
OUT.mkdir(parents=True, exist_ok=True)
catalog = json.loads((ROOT / 'data.json').read_text(encoding='utf-8'))
font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 13)
small = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 11)
pages = []
for start in range(0, len(catalog), 72):
    entries = catalog[start:start + 72]
    canvas = Image.new('RGB', (1440, 1270), '#f4f7fa')
    draw = ImageDraw.Draw(canvas)
    draw.text((12, 8), f'Catalog entries {start + 1}-{start + len(entries)} | NORMAL left / SHINY right', font=font, fill='#172b40')
    reviewed = []
    for index, pokemon in enumerate(entries):
        x, y = (index % 6) * 240, 35 + (index // 6) * 102
        draw.rectangle((x, y, x + 239, y + 101), outline='#b3c2cd')
        label = f"{pokemon['id']:04} {pokemon['displayName']}"
        draw.text((x + 5, y + 3), label, font=small, fill='#172b40')
        files = []
        for offset, mode in enumerate(('normal', 'shiny')):
            path = ROOT / pokemon[mode]
            with Image.open(path) as art:
                art = art.convert('RGBA')
                art.thumbnail((100, 80))
                canvas.paste(art, (x + 10 + offset * 120 + (100 - art.width) // 2, y + 18), art)
            files.append({'mode': mode, 'file': pokemon[mode + 'File'],
                          'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        reviewed.append({'key': pokemon['key'], 'name': pokemon['displayName'], 'files': files})
    filename = f'contact-{start // 72 + 1:02}.png'
    canvas.save(OUT / filename)
    pages.append({'sheet': filename, 'entries': reviewed})
(OUT / 'manifest.json').write_text(json.dumps({'normalLeftShinyRight': True, 'pages': pages}, indent=2, ensure_ascii=False), encoding='utf-8')
print(f'Created {len(pages)} sheets covering {len(catalog)} normal/shiny pairs')
