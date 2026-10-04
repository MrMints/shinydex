"""Let's Go level routes restricted to its playable Kanto species and catalog forms."""
import json
from pathlib import Path
from form_mapping import catalog_forms
ROOT=Path(__file__).parent
GAMES=["Pokémon Let's Go, Pikachu!","Pokémon Let's Go, Eevee!"]
def merge(records,catalog):
 forms=catalog_forms(catalog);names={p['key']:p['displayName'] for p in catalog};count=0
 items=(ROOT/'reference/pkhex/PKHeX.Core/Resources/text/items/text_Items_en.txt').read_text(encoding='utf-8-sig').splitlines()
 for edge in json.loads((ROOT/'lets-go-evolution-encounters.json').read_text()):
  parent=edge['sourceSpecies'];child=edge['destinationSpecies']
  kind=edge['evolutionType']
  if kind not in {'LevelUp','UseItem','Trade'} or not (1<=parent<=151 and 1<=child<=151):continue
  pk=forms.get((parent,edge['sourceForm']));ck=forms.get((child,edge['destinationForm']))
  if pk is None or ck is None:continue
  level=edge['level'];assert 0<=level<=100
  if kind=='LevelUp':
   assert level>=1
   requirement='level up at level '+str(level)+' or higher';category='level'
  elif kind=='UseItem':requirement='use '+items[edge['argument']];category='item'
  else:requirement='trade with another Let’s Go player; arrange a trade back to keep your shiny';category='trade'
  if parent in {25,133}:requirement+='; use a regular caught or transferred Pokémon, since the partner Pikachu and Eevee cannot evolve'
  acquisition='; shiny Alolan parents may require repeatable Alolan NPC trades or a compatible GO transfer' if edge['sourceForm'] else ''
  for game in GAMES:
   records[str(ck)]['entries'].append(dict(game=game,method='Obtain shiny '+names[pk]+'; '+requirement+' to evolve into '+names[ck]+acquisition+'; these games have no breeding',status='Huntable',locations=[],source=edge['source'],sourceReferences=[edge['source'],'https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9mon:_Let%27s_Go,_Pikachu!_and_Let%27s_Go,_Eevee!'],olderEvolutionKind='lets-go-'+category,olderEvolutionType=kind,evolutionParent=pk,evolutionLevel=level,evolutionArgument=edge['argument'],gameFormId=edge['destinationForm'],verification='Playable Kanto species and exact evolution requirements checked; parent acquisition remains under audit'))
   count+=1
 return count
