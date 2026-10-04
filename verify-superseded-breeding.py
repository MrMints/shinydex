"""Verify retained egg and evolution chains for every removed breeding instruction."""
import json
from pathlib import Path
from supersede_evolutions import GAME_FAMILIES
from supersede_breeding import DIRECT_EGG_KINDS, COMBINED_GAMES
root=Path(__file__).parent
h=json.loads((root/'hunts.json').read_text())
a=json.loads((root/'superseded-breeding-audit.json').read_text())
assert a['removedCount']==len(a['records'])
chains=0
for row in a['records']:
 game=row['replacedEntry']['game']
 game_chains=row.get('replacementGameChains')
 if game_chains is not None:
  assert set(game_chains)==set(COMBINED_GAMES[game])==set(row['replacementGames'])
 else:game_chains={game:row.get('replacementEggEvolutionChain',[row['key']])}
 for replacement_game,chain in game_chains.items():
  assert chain[-1]==row['key'] and len(chain)==len(set(chain))
  assert any(e.get('breedingKind') in DIRECT_EGG_KINDS and replacement_game in GAME_FAMILIES.get(e['game'],{e['game']}) for e in h[str(chain[0])]['entries'])
  for parent,child in zip(chain,chain[1:]):
   assert any((e.get('evolutionKind') or e.get('olderEvolutionKind')) and e['evolutionParent']==parent and replacement_game in GAME_FAMILIES.get(e['game'],{e['game']}) for e in h[str(child)]['entries'])
  chains+=len(chain)>1
 assert row['replacedEntry'] not in h[str(row['key'])]['entries']
print('Verified',len(a['records']),'replacements, including',chains,'complete same-game egg/evolution chains')
