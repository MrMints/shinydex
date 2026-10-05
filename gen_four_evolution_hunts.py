"""Generation IV ordinary level evolutions, decoded from its own table."""
import json
from pathlib import Path
from gen_six_evolution_hunts import ITEM_TYPES,CONDITION_TYPES
ROOT=Path(__file__).parent
GAMES=[('dp','Pokémon Diamond / Pearl'),('pt','Pokémon Platinum'),('hgss','Pokémon HeartGold / SoulSilver')]
SPECIAL={
 'LevelUpECl5':('level up at level 7 or higher with the hidden personality value selecting Silcoon; this branch is fixed for each Wurmple','Personality_value'),
 'LevelUpECgeq5':('level up at level 7 or higher with the hidden personality value selecting Cascoon; this branch is fixed for each Wurmple','Personality_value'),
 'LevelUpNinjask':('level up Nincada at level 20 or higher','Nincada'),
 'LevelUpShedinja':('evolve shiny Nincada at level 20 or higher with an empty party slot and a regular Poké Ball in the bag; shiny Shedinja appears alongside Ninjask','Shedinja'),
 'LevelUpElectric':('level up in the special magnetic field at Mount Coronet','Mount_Coronet'),
 'LevelUpForest':('level up near the Moss Rock in Eterna Forest','Eterna_Forest'),
 'LevelUpCold':('level up near the Ice Rock on Sinnoh Route 217','Sinnoh_Route_217'),
 'LevelUpBeauty':('level up with Beauty at least 170; raise Beauty with dry Poffins, taking the limited sheen capacity into account','Beautiful_(condition)'),
}
def merge(records,catalog):
 names={p['id']:p['displayName'] for p in catalog if not p.get('region')};count=0
 for code,game in GAMES:
  raw=(ROOT/('reference/pkhex/PKHeX.Core/Resources/byte/personal/personal_'+code)).read_bytes()
  for edge in json.loads((ROOT/'audit/gen-four-evolution-encounters.json').read_text()):
   kind=edge['evolutionType']
   if kind not in {'LevelUp','Trade','LevelUpKnowMove'}|ITEM_TYPES|CONDITION_TYPES|set(SPECIAL) or edge['sourceForm'] or edge['destinationForm']:continue
   parent=edge['sourceSpecies'];child=edge['destinationSpecies'];level=edge['level']
   if records[str(parent)]['locked'] or records[str(child)]['locked']:continue
   assert 1<=parent<=493 and 1<=child<=493 and 0<=level<=100
   if kind=='LevelUp':assert level>=1
   assert len(raw[parent*44:(parent+1)*44])==44 and len(raw[child*44:(child+1)*44])==44
   if kind in SPECIAL:
    requirement,page=SPECIAL[kind]
    if code=='hgss' and kind=='LevelUpBeauty':requirement='level up with Beauty at least 170; raise the hidden Beauty condition through grooming by Daisy Oak in Pallet Town or the haircut brothers in Goldenrod, taking the limited sheen capacity into account; alternatively prepare Beauty in Diamond, Pearl or Platinum and trade Feebas here'
    if code=='hgss' and kind in {'LevelUpElectric','LevelUpForest','LevelUpCold'}:requirement='trade the shiny parent to Diamond, Pearl or Platinum, then '+requirement+' there and trade the evolved shiny back; HeartGold and SoulSilver have no corresponding evolution location'
    records[str(child)]['entries'].append(dict(game=game,method='Obtain shiny '+names[parent]+'; '+requirement+' to obtain '+names[child]+'; the parent may require a compatible Generation IV trade or one-way Pal Park transfer from Generation III',status='Huntable',locations=[],source=edge['source'],sourceReferences=[edge['source'],'https://bulbapedia.bulbagarden.net/wiki/'+page],olderEvolutionKind='gen-four-special',olderEvolutionType=kind,evolutionParent=parent,evolutionLevel=level,evolutionArgument=edge['argument'],gameFormId=0,verification='Generation IV special requirement and game-specific gameplay references checked; parent acquisition remains under audit'))
    count+=1;continue
   if kind!='LevelUp':
    template=next(e for e in records[str(child)]['entries'] if e.get('olderEvolutionKind') in {'gen-five-item','gen-five-trade','gen-five-move','gen-five-condition'} and e['evolutionParent']==parent and e['olderEvolutionType']==kind and e['evolutionArgument']==edge['argument'] and e['evolutionLevel']==level)
    requirement=template['method'].split('; ',1)[1].split(' to evolve into ',1)[0]
    if code=='hgss':requirement=requirement.replace('; stay away from the Moss Rock and Ice Rock','')
    records[str(child)]['entries'].append(dict(template,game=game,method='Obtain shiny '+names[parent]+'; '+requirement+' to evolve into '+names[child]+'; the parent may require a compatible Generation IV trade or one-way Pal Park transfer from Generation III',source=edge['source'],sourceReferences=[edge['source']]+template['sourceReferences'][1:],olderEvolutionKind=template['olderEvolutionKind'].replace('gen-five-','gen-four-'),verification='Generation IV evolution requirement checked against its own table; parent acquisition remains under audit'))
    count+=1;continue
   records[str(child)]['entries'].append(dict(game=game,method='Obtain shiny '+names[parent]+'; level up at level '+str(level)+' or higher to evolve into '+names[child]+'; the parent may require a compatible Generation IV trade or one-way Pal Park transfer from Generation III',status='Huntable',locations=[],source=edge['source'],olderEvolutionKind='gen-four-level',olderEvolutionType='LevelUp',evolutionParent=parent,evolutionLevel=level,evolutionArgument=edge['argument'],gameFormId=0,verification='Generation IV level requirement and game-specific species data checked; parent acquisition remains under audit'))
   count+=1
 return count
