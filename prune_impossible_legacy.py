"""Remove generic evolution guesses contradicted by game species/form support."""
import json
from pathlib import Path
def prune(records):
 removed=[]
 for key,guide in records.items():
  kept=[]
  for e in guide['entries']:
   reason=None
   generic=e['method'].startswith('Catch shiny ') and e['method'].endswith(' and evolve it')
   swsh=e['game'] in {'Pokémon Sword','Pokémon Shield','Pokémon The Isle Of Armor Sword','Pokémon The Isle Of Armor Shield','Pokémon The Crown Tundra Sword','Pokémon The Crown Tundra Shield'}
   if generic and e['game'] in {"Pokémon Let's Go, Pikachu!","Pokémon Let's Go, Eevee!"} and int(key)>151:
    reason='These games support Kanto species plus Meltan/Melmetal, not later evolutionary relatives of Kanto Pokémon.'
   if generic and int(key) in {900,902,903,904} and e['game'] in {'Pokémon Sword','Pokémon Shield','Pokémon The Isle Of Armor Sword','Pokémon The Isle Of Armor Shield','Pokémon The Crown Tundra Sword','Pokémon The Crown Tundra Shield'}:
    reason='This Hisuian evolution is not supported in Sword/Shield or its DLC; a shared ancestor does not establish a hunting route.'
   if generic and int(key) in {26,103,105} and e['game'] in {'Pokémon Sun','Pokémon Moon'}:
    reason='In Sun/Moon this evolution produces the Alolan form, not the pictured Kanto form. Ultra Space exceptions apply only in Ultra Sun/Ultra Moon.'
   if swsh and ((generic and int(key) in {110,122}) or (int(key)==110 and e['method'].startswith('Breed a shiny in this evolutionary line'))):
    reason='Koffing and Mime Jr. evolve into Galarian forms in Sword/Shield, not the pictured Kanto form. A transfer or direct egg exception needs its own verified route.'
   if reason:removed.append(dict(key=int(key),entry=e,reason=reason))
   else:kept.append(e)
  guide['entries']=kept
 Path('audit/impossible-legacy-audit.json').write_text(json.dumps(dict(removedCount=len(removed),records=removed,fullHuntingAuditComplete=False),indent=2),encoding='utf-8')
 return len(removed)
