import json
from pathlib import Path
root=Path(__file__).parent;h=json.loads((root/'hunts.json').read_text());edges=json.loads((root/'gen-three-evolution-encounters.json').read_text())
rows=[(int(k),e) for k,g in h.items() for e in g['entries'] if e.get('olderEvolutionKind','').startswith('orre-')]
assert len(rows)==24
for key,e in rows:
 assert e['game'] in {'Pokémon Colosseum','Pokémon XD: Gale of Darkness'}
 assert any(x['destinationSpecies']==key and x['sourceSpecies']==e['evolutionParent'] and x['level']==e['evolutionLevel'] and x['evolutionType']==e['olderEvolutionType'] for x in edges)
 assert 'purify it before leveling' in e['method'] and 'XD Shadow Pokémon are shiny locked' in e['method']
 if e['olderEvolutionType']=='LevelUp':assert 'level '+str(e['evolutionLevel'])+' or higher' in e['method']
 else:assert '220 friendship' in e['method']
 assert not any(x['game']==e['game'] and x['method'].startswith('Catch shiny ') and x['method'].endswith(' and evolve it') for x in h[str(key)]['entries'])
print('Verified 24 Orre precise evolution replacements; parent acquisition remains under audit')
