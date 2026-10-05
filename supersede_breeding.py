"""Replace generic direct-species breeding instructions with precise egg routes."""
import json
from pathlib import Path
from supersede_evolutions import GAME_FAMILIES
DIRECT_EGG_KINDS={'direct-egg','gen-two-dv-egg'}
COMBINED_GAMES={
 'Pokémon Black / White / Black 2 / White 2':('Pokémon Black / White','Pokémon Black 2 / White 2'),
 'Pokémon Sun / Moon / Ultra Sun / Ultra Moon':('Pokémon Sun / Moon','Pokémon Ultra Sun / Ultra Moon'),
}

def supersede(records):
 removed=[]
 def egg_chain(key,game,seen=()):
  if key in seen:return None
  entries=records[str(key)]['entries']
  for e in entries:
   if e.get('breedingKind') in DIRECT_EGG_KINDS and game in GAME_FAMILIES.get(e['game'],{e['game']}):return [key]
  for e in entries:
   if (e.get('evolutionKind') or e.get('olderEvolutionKind')) and game in GAME_FAMILIES.get(e['game'],{e['game']}):
    chain=egg_chain(e['evolutionParent'],game,seen+(key,))
    if chain:return chain+[key]
  return None
 for key,guide in records.items():
  specific={e['game'] for e in guide['entries'] if e.get('breedingKind') in DIRECT_EGG_KINDS}
  covered=set().union(*(GAME_FAMILIES.get(g,{g}) for g in specific)) if specific else set()
  kept=[]
  for entry in guide['entries']:
   generic=entry['method'].startswith(('Breed a shiny in this evolutionary line','Breed shiny starter eggs','Breed shiny Alola starter eggs','Breed shiny Galar starter eggs')) and not entry.get('breedingKind')
   game_chains={game:egg_chain(int(key),game) for game in COMBINED_GAMES.get(entry['game'],())} if generic else {}
   if game_chains and all(game_chains.values()):
    removed.append({'key':int(key),'replacedEntry':entry,'replacementGames':list(game_chains),'replacementGameChains':game_chains})
   elif generic and entry['game'] in covered:
    removed.append({'key':int(key),'replacedEntry':entry,'replacementGames':sorted(specific)})
   elif generic and 'evolve' in entry['method'].lower() and (chain:=egg_chain(int(key),entry['game'])):
    removed.append({'key':int(key),'replacedEntry':entry,'replacementGames':[entry['game']],'replacementEggEvolutionChain':chain})
   else:kept.append(entry)
  guide['entries']=kept
 Path('audit/superseded-breeding-audit.json').write_text(json.dumps({'removedCount':len(removed),'records':removed,'fullHuntingAuditComplete':False},indent=2),encoding='utf-8')
 return len(removed)
