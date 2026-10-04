"""Require each removed generic route to have a retained same-game replacement."""
import json
from pathlib import Path
from supersede_evolutions import GAME_FAMILIES
root=Path(__file__).parent
hunts=json.loads((root/'hunts.json').read_text())
audit=json.loads((root/'superseded-evolution-audit.json').read_text())
assert audit['removedCount']==len(audit['records'])
for row in audit['records']:
 old=row['replacedEntry'];entries=hunts[str(row['key'])]['entries']
 specific=[e for e in entries if e.get('evolutionKind') or e.get('olderEvolutionKind')]
 assert any(old['game'] in GAME_FAMILIES.get(e['game'],{e['game']}) for e in specific),row
 assert old not in entries
lycan=next(e for e in hunts['745']['entries'] if e.get('olderEvolutionType')=='LevelUpVersionDay')
assert lycan['game']=='Pokémon Ultra Sun'
assert 'Pokémon Ultra Moon' not in GAME_FAMILIES.get(lycan['game'],{lycan['game']})
print('Verified',len(audit['records']),'removed generic routes have retained same-game replacements; version-exclusive route remains Ultra Sun only')
