"""Encounter-specific exceptions not representable by generic gift matching."""
def resolve(p,entry,ref,sha,facts):
 sid=p['id'];game=entry['game'];method=entry['method']
 def cite(path,needle):
  lines=(ref/path).read_text(encoding='utf-8-sig').splitlines()
  line=next(i+1 for i,text in enumerate(lines) if needle in text)
  return 'https://github.com/kwsch/PKHeX/blob/'+sha+'/'+path+'#L'+str(line)
 prefix='PKHeX.Core/Legality/Encounters/'
 result=None
 if sid==25 and game in {'Pokémon Omega Ruby','Pokémon Alpha Sapphire'} and method=='Cosplay Pikachu contest gift':
  result=('Shiny Locked',method,cite(prefix+'Data/Gen6/Encounters6AO.cs','Shiny = Shiny.Never,'))
 elif sid==175 and game=='Pokémon XD: Gale of Darkness':
  result=('Shiny Locked','Shadow Togepi gift from Hordel',cite(prefix+'Templates/Gen3/XD/EncounterShadow3XD.cs','public Shiny Shiny => Shiny.Never'))
 elif sid in {196,197} and game=='Pokémon Colosseum':
  result=('Shiny Locked','Starter Pokémon',cite(prefix+'Templates/Gen3/Colo/EncounterStarter3Colo.cs','public Shiny Shiny => Shiny.Never'))
 elif sid==250 and game=='Pokémon Colosseum':
  matches=[f for f in facts if f['species']==250 and f['type']=='EncounterGift3Colo']
  assert matches and all(f['shiny']=='Never' for f in matches)
  result=('Shiny Locked','Mt. Battle completion reward',matches[0]['source'])
 elif sid==385 and method in {'Colosseum Bonus Disc Us','Pokemon Channel Pal'}:
  ot='WISHMKR' if method=='Colosseum Bonus Disc Us' else 'CHANNEL'
  path=prefix+'Data/Gen3/EncountersWC3.cs'
  line=next(l for l in (ref/path).read_text(encoding='utf-8-sig').splitlines() if 'OriginalTrainerName = "'+ot+'"' in l)
  assert 'Shiny = Random' in line
  result=('Huntable','US Colosseum Bonus Disc · receive and check WISHMKR Jirachi' if ot=='WISHMKR' else 'PAL Pokémon Channel · receive and check CHANNEL Jirachi',cite(path,'OriginalTrainerName = "'+ot+'"'))
 elif sid==490 and method=='Pokemon Ranger':
  result=('Huntable','Pokémon Ranger Manaphy Egg · trade the unhatched egg to another Generation IV save before hatching; shininess depends on the hatching trainer','https://bulbapedia.bulbagarden.net/wiki/Manaphy_(Pok%C3%A9mon)#Trivia')
 if result:
  state,label,source=result
  return dict(status=state,method=label,source=source,verification='Verified encounter-specific gift exception against linked reference')
