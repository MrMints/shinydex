"""Replace legacy Orre evolution shortcuts with explicit level/friendship requirements."""
import json
from pathlib import Path
ROOT=Path(__file__).parent
def merge(records,catalog):
 names={p['id']:p['displayName'] for p in catalog if not p.get('region')}
 edges=json.loads((ROOT/'audit/gen-three-evolution-encounters.json').read_text());count=0
 for key,guide in records.items():
  for e in list(guide['entries']):
   if e['game'] not in {'Pokémon Colosseum','Pokémon XD: Gale of Darkness'} or not (e['method'].startswith('Catch shiny ') and e['method'].endswith(' and evolve it')):continue
   edge=next(x for x in edges if x['destinationSpecies']==int(key) and not x['sourceForm'] and not x['destinationForm'])
   kind=edge['evolutionType'];assert kind in {'LevelUp','LevelUpFriendship'}
   requirement='level up at level '+str(edge['level'])+' or higher' if kind=='LevelUp' else 'level up with at least 220 friendship'
   parent=edge['sourceSpecies']
   method='Obtain shiny '+names[parent]+'; if it is a Shadow Pokémon, purify it before leveling; '+requirement+' to evolve into '+names[int(key)]+'; XD Shadow Pokémon are shiny locked, so XD shiny parents must come from an eligible non-Shadow encounter or compatible Generation III trade'
   guide['entries'].append(dict(e,method=method,source=edge['source'],sourceReferences=[edge['source'],'https://bulbapedia.bulbagarden.net/wiki/Shadow_Pok%C3%A9mon','https://bulbapedia.bulbagarden.net/wiki/Friendship_Evolution'],olderEvolutionKind='orre-'+('level' if kind=='LevelUp' else 'friendship'),olderEvolutionType=kind,evolutionParent=parent,evolutionLevel=edge['level'],evolutionArgument=edge['argument'],gameFormId=0,verification='Generation III level/friendship gameplay requirement checked; exact shiny parent acquisition remains under audit'))
   count+=1
 return count
