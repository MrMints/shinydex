from pathlib import Path
p=Path('main.js')
s=p.read_text(encoding='utf-8')
prefix='${e.status==="Shiny Locked"?"<strong>Shiny Locked</strong><br>":""}'
s=s.replace(prefix,'').replace('${esc(e.method)}',prefix+'${esc(e.method)}')
s=s.replace('Game-specific encounter records and shiny restrictions. Gift and event restrictions requiring verification are labeled explicitly. Shiny locks refer to the selected form. Data checked October 3, 2026.', 'Game-specific encounters and shiny restrictions. Coverage is still being audited; this guide does not yet include every game or event. Unverified gift restrictions are labeled. Shiny locks apply to the selected form and game. References checked October 3, 2026.')
p.write_text(s,encoding='utf-8')
