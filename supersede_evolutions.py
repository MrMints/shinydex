"""Supersede vague evolution rows only when an exact same-game route exists."""
import json
from pathlib import Path
GAME_FAMILIES={
 'Pokémon Ruby / Sapphire':{'Pokémon Ruby','Pokémon Sapphire','Pokémon Ruby / Sapphire'},
 'Pokémon Scarlet / Violet':{'Pokémon Scarlet','Pokémon Violet','Pokémon Scarlet / Violet'},
 'Pokémon Sword / Shield':{'Pokémon Sword','Pokémon Shield','Pokémon Sword / Shield','Pokémon The Isle Of Armor Sword','Pokémon The Isle Of Armor Shield','Pokémon The Crown Tundra Sword','Pokémon The Crown Tundra Shield'},
 'Pokémon Brilliant Diamond / Shining Pearl':{'Pokémon Brilliant Diamond','Pokémon Shining Pearl','Pokémon Brilliant Diamond / Shining Pearl'},
 'Pokémon Legends: Arceus':{'Pokémon Legends: Arceus'},
 'Pokémon Legends: Z-A':{'Pokémon Legends: Z-A'},
 'Pokémon Ultra Sun / Ultra Moon':{'Pokémon Ultra Sun','Pokémon Ultra Moon','Pokémon Ultra Sun / Ultra Moon'},
 'Pokémon Sun / Moon':{'Pokémon Sun','Pokémon Moon','Pokémon Sun / Moon'},
 'Pokémon X / Y':{'Pokémon X','Pokémon Y','Pokémon X / Y'},
 'Pokémon Omega Ruby / Alpha Sapphire':{'Pokémon Omega Ruby','Pokémon Alpha Sapphire','Pokémon Omega Ruby / Alpha Sapphire'},
 'Pokémon Black / White':{'Pokémon Black','Pokémon White','Pokémon Black / White'},
 'Pokémon Black 2 / White 2':{'Pokémon Black 2','Pokémon White 2','Pokémon Black 2 / White 2'},
 'Pokémon Diamond / Pearl':{'Pokémon Diamond','Pokémon Pearl','Pokémon Diamond / Pearl'},
 'Pokémon Platinum':{'Pokémon Platinum'},
 'Pokémon HeartGold / SoulSilver':{'Pokémon HeartGold','Pokémon SoulSilver','Pokémon HeartGold / SoulSilver'},
}
def supersede(records):
 removed=[]
 for key,guide in records.items():
  specific={e['game'] for e in guide['entries'] if e.get('evolutionKind') or e.get('olderEvolutionKind')}
  covered=set().union(*(GAME_FAMILIES.get(g,{g}) for g in specific)) if specific else set()
  kept=[]
  for entry in guide['entries']:
   method=entry['method']
   generic=(method.startswith('Catch shiny ') and method.endswith(' and evolve it')) or method=='Catch a shiny in this evolutionary line and evolve it'
   if generic and entry['game'] in covered:
    removed.append({'key':int(key),'replacedEntry':entry,'replacementGames':sorted(specific)})
   else:kept.append(entry)
  guide['entries']=kept
 Path('superseded-evolution-audit.json').write_text(json.dumps({'removedCount':len(removed),'records':removed,'fullHuntingAuditComplete':False},indent=2),encoding='utf-8')
 return len(removed)
