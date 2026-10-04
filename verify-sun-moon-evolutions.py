import json
from form_mapping import catalog_forms
from pathlib import Path
root=Path(__file__).parent
h=json.loads((root/'hunts.json').read_text())
pairs={key:pair for pair,key in catalog_forms(json.loads((root/'data.json').read_text())).items()}
rows=[(int(k),e) for k,g in h.items() for e in g['entries'] if e.get('olderEvolutionKind')=='sun-moon-location']
assert len(rows)==6
for key,e in rows:
 assert e['game']=='Pokémon Sun / Moon' and 'Blush Mountain' not in e['method']
 assert 'Ultra Space' not in e['method'] and 'HOME transfer' not in e['method']
 if key in {462,476,738}:assert 'Vast Poni Canyon' in e['method']
 if key in {471,740}:assert 'defeating Lusamine' in e['method']
assert any(key==470 and 'Moss Rock in Lush Jungle' in e['method'] for key,e in rows)
assert any(key==471 and 'Ice Rock inside the cave' in e['method'] for key,e in rows)
print('Verified six Sun/Moon location routes with original-game locations and story access requirements')
levels=[(int(k),e) for k,g in h.items() for e in g['entries'] if e.get('olderEvolutionKind')=='sun-moon-level']
assert levels
for key,e in levels:
 assert pairs[key][0]<=802 and pairs[e['evolutionParent']][0]<=802 and e['olderEvolutionType']=='LevelUp'
 assert e['game']=='Pokémon Sun / Moon' and 1<=e['evolutionLevel']<=100
 assert any('EvolutionTree.cs' in s for s in e['sourceReferences'])
 assert any('personal_sm' in s for s in e['sourceReferences'])
 assert any(old.get('olderEvolutionKind')=='level-only' and old['evolutionParent']==e['evolutionParent'] and old['evolutionLevel']==e['evolutionLevel'] for old in h[str(key)]['entries'])
for sid,parent,level in [(2,1,16),(6,5,36),(130,129,20),(149,148,55)]:assert any(key==sid and e['evolutionParent']==parent and e['evolutionLevel']==level for key,e in levels)
print('Verified',len(levels),'Sun/Moon simple level routes using the shared Gen VII reader and Sun/Moon species support')
from collections import Counter
shared=[(int(k),e) for k,g in h.items() for e in g['entries'] if e.get('olderEvolutionKind') in {'sun-moon-item','sun-moon-condition','sun-moon-trade','sun-moon-move'}]
assert Counter(e['olderEvolutionKind'] for key,e in shared)=={'sun-moon-item':60,'sun-moon-condition':19,'sun-moon-trade':11,'sun-moon-move':8}
for key,e in shared:
 assert pairs[key][0]<=802 and pairs[e['evolutionParent']][0]<=802
 assert e['olderEvolutionType']!='UseItemWormhole' and 'Ultra Space' not in e['method']
 assert e['game']=='Pokémon Sun / Moon' and any('personal_sm' in s for s in e['sourceReferences'])
 assert any(old.get('olderEvolutionKind') in {'item','condition','trade','move'} and old['olderEvolutionType']==e['olderEvolutionType'] and old['evolutionParent']==e['evolutionParent'] and old['evolutionArgument']==e['evolutionArgument'] for old in h[str(key)]['entries'])
assert not any(key==804 for key,e in shared)
assert any(key==700 and 'two affection hearts in Pokémon Refresh' in e['method'] for key,e in shared)
print('Verified 98 shared Sun/Moon item, friendship/affection, trade and known-move routes; Ultra Space and Poipole excluded')
extra=[(int(k),e) for k,g in h.items() for e in g['entries'] if e.get('olderEvolutionKind') in {'sun-moon-gender-time','sun-moon-party-stat','sun-moon-special'}]
assert Counter(e['olderEvolutionKind'] for key,e in extra)=={'sun-moon-gender-time':11,'sun-moon-party-stat':5,'sun-moon-special':7}
for key,e in extra:
 assert e['game']=='Pokémon Sun / Moon'
 assert 'Ultra Space' not in e['method'] and 'Ultra Sun' not in e['method']
 assert e['olderEvolutionType']!='LevelUpVersionDay'
for sid,text in [(758,'female'),(416,'female'),(237,'equal to Defense'),(226,'Remoraid'),(675,'Dark-type'),(292,'empty party slot'),(687,'Nintendo 3DS upside down'),(706,'rain or fog'),(350,'Sun and Moon cannot raise Beauty themselves')]:
 assert any(key==sid and text in e['method'] for key,e in extra)
print('Verified 23 additional gender, party, stat and special Sun/Moon evolutions')
version=next(e for e in h['745']['entries'] if e.get('olderEvolutionKind')=='sun-moon-version')
assert version['game']=='Pokémon Sun' and 'level 25 or higher' in version['method'] and 'in-game day' in version['method']
assert 'cannot be performed in Pokémon Moon' in version['method']
print('Verified Midday Lycanroc is explicitly Sun-only')
