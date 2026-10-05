"""Generation V level requirements from its own evolution table."""
import json
from pathlib import Path
from gen_six_evolution_hunts import ITEM_TYPES,CONDITION_TYPES
ROOT=Path(__file__).parent
GAMES=[('bw','Pokémon Black / White',60),('b2w2','Pokémon Black 2 / White 2',76)]
SPECIAL={
 'LevelUpElectric':('level up in the special magnetic field at Chargestone Cave','Chargestone_Cave'),
 'LevelUpForest':('level up near the Moss Rock in Pinwheel Forest','Pinwheel_Forest'),
 'LevelUpCold':('level up near the Ice Rock on the lowest floor of Twist Mountain','Twist_Mountain'),
 'LevelUpECl5':('level up at level 7 or higher with the hidden personality value selecting Silcoon; this branch is fixed for each Wurmple and cannot be changed by resetting, time of day or gender','Personality_value'),
 'LevelUpECgeq5':('level up at level 7 or higher with the hidden personality value selecting Cascoon; this branch is fixed for each Wurmple and cannot be changed by resetting, time of day or gender','Personality_value'),
 'LevelUpNinjask':('level up Nincada at level 20 or higher','Nincada'),
 'LevelUpShedinja':('evolve shiny Nincada at level 20 or higher with an empty party slot and a regular Poké Ball in the bag; shiny Shedinja appears alongside Ninjask','Shedinja'),
 'LevelUpBeauty':('level up with Beauty at least 170; prepare Beauty in a compatible Generation IV or earlier Contest game, then use one-way Poké Transfer to bring Feebas here; Generation V games cannot raise Beauty themselves','Beautiful_(condition)'),
}
def merge(records,catalog):
 names={p['id']:p['displayName'] for p in catalog if not p.get('region')};count=0
 for code,game,size in GAMES:
  raw=(ROOT/('reference/pkhex/PKHeX.Core/Resources/byte/personal/personal_'+code)).read_bytes()
  for edge in json.loads((ROOT/'audit/gen-five-evolution-encounters.json').read_text()):
   kind=edge['evolutionType']
   if kind not in {'LevelUp','Trade','TradeShelmetKarrablast','LevelUpKnowMove'}|ITEM_TYPES|CONDITION_TYPES|set(SPECIAL) or edge['sourceForm'] or edge['destinationForm']:continue
   parent=edge['sourceSpecies'];child=edge['destinationSpecies'];level=edge['level']
   if records[str(parent)]['locked'] or records[str(child)]['locked']:continue
   assert parent<=649 and child<=649
   assert len(raw[parent*size:(parent+1)*size])==size and len(raw[child*size:(child+1)*size])==size
   if kind!='LevelUp':
    if kind in SPECIAL:
     requirement,page=SPECIAL[kind]
     source='https://bulbapedia.bulbagarden.net/wiki/'+page
     records[str(child)]['entries'].append(dict(game=game,method='Obtain shiny '+names[parent]+'; '+requirement+' to evolve into '+names[child]+'; the parent may require a compatible Generation V trade or one-way Poké Transfer from Generation IV',status='Huntable',locations=[],source=edge['source'],sourceReferences=[edge['source'],source],olderEvolutionKind='gen-five-special',olderEvolutionType=kind,evolutionParent=parent,evolutionLevel=level,evolutionArgument=edge['argument'],gameFormId=0,verification='Gen V requirement and supporting gameplay reference checked; acquisition remains under audit'))
     count+=1;continue
    template=next(e for e in records[str(child)]['entries'] if e.get('olderEvolutionKind') in {'gen-six-item','gen-six-trade','gen-six-move','gen-six-condition'} and e['evolutionParent']==parent and e['olderEvolutionType']==kind and e['evolutionArgument']==edge['argument'] and e['evolutionLevel']==level)
    requirement=template['method'].split('; ',1)[1].split(' to evolve into ',1)[0].replace('forget Fairy-type moves to prevent Sylveon and ','')
    method='Obtain shiny '+names[parent]+'; '+requirement+' to evolve into '+names[child]+'; the parent may require a compatible Generation V trade or one-way Poké Transfer from Generation IV'
    records[str(child)]['entries'].append(dict(template,game=game,method=method,source=edge['source'],sourceReferences=[edge['source']]+template['sourceReferences'][1:],olderEvolutionKind=template['olderEvolutionKind'].replace('gen-six-','gen-five-'),verification='Generation V table requirements checked; parent acquisition remains under audit'))
    count+=1;continue
   assert 1<=level<=100
   records[str(child)]['entries'].append(dict(game=game,method='Obtain shiny '+names[parent]+'; level up at level '+str(level)+' or higher to evolve into '+names[child]+'; the parent may require a compatible Generation V trade or one-way Poké Transfer from Generation IV',status='Huntable',locations=[],source=edge['source'],olderEvolutionKind='gen-five-level',evolutionParent=parent,evolutionLevel=level,gameFormId=0,verification='Gen V level requirement and game-specific species data checked; parent acquisition remains under audit'))
   count+=1
 return count
