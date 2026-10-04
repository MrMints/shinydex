import json
from pathlib import Path
root=Path(__file__).parent;h=json.loads((root/'hunts.json').read_text())
counts=[]
for code,game in [('gs','Pokémon Gold'),('gs','Pokémon Silver'),('c','Pokémon Crystal')]:
 raw=(root/('reference/pkhex/PKHeX.Core/Resources/byte/personal/personal_'+code)).read_bytes()
 rows=[(int(k),e) for k,g in h.items() for e in g['entries'] if e.get('breedingKind')=='gen-two-dv-egg' and e['game']==game]
 counts.append(len(rows));assert rows
 for key,e in rows:
  assert key<=251 and key!=132 and e['gameFormId']==0
  byte=raw[e['breedingParent']*32+23];assert 15 not in {byte&15,byte>>4}
  assert 'Defense DV 10 and Special DV 2 or 10' in e['method'] and '1/64' in e['method']
  assert 'two shiny parents cannot breed' in e['method'] and 'no Masuda method or Shiny Charm' in e['method'] and 'Johto Route 34' in e['method']
 for key,parent in [(172,25),(173,35),(174,39),(175,176),(236,106),(238,124),(239,125),(240,126)]:assert any(k==key and e['breedingParent']==parent for k,e in rows)
 assert any(k==1 and 'only males can be shiny' in e['method'] for k,e in rows)
assert len(set(counts))==1
print('Verified',sum(counts),'Generation II DV egg routes and parent groups; parent acquisition remains under audit')
