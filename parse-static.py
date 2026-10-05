"""Extract explicit public encounter definitions, preserving pinned source lines.
This reads C# as reference text. It does not compile or execute upstream code.
"""
import json,re
from pathlib import Path
ROOT=Path(__file__).parent
REF=ROOT/'reference'/'pkhex';sha=json.loads((REF/'tree.json').read_text())['sha']
games={
 'GSC':['Gold','Silver','Crystal'],'GS':['Gold','Silver'],'GD':['Gold'],'SI':['Silver'],'C':['Crystal'],
 'HGSS':['HeartGold','SoulSilver'],'HG':['HeartGold'],'SS':['SoulSilver'],
 'DPPt':['Diamond','Pearl','Platinum'],'DP':['Diamond','Pearl'],'D':['Diamond'],'P':['Pearl'],'Pt':['Platinum'],
 'RSE':['Ruby','Sapphire','Emerald'],'RS':['Ruby','Sapphire'],'R':['Ruby'],'S':['Sapphire'],'E':['Emerald'],
 'FRLG':['FireRed','LeafGreen'],'FR':['FireRed'],'LG':['LeafGreen'],
 'BW':['Black','White'],'B':['Black'],'W':['White'],'B2W2':['Black 2','White 2'],'B2':['Black 2'],'W2':['White 2'],
 'XY':['X','Y'],'X':['X'],'Y':['Y'],'AO':['Omega Ruby','Alpha Sapphire'],'ORAS':['Omega Ruby','Alpha Sapphire'],'OR':['Omega Ruby'],'AS':['Alpha Sapphire'],
 'SM':['Sun','Moon'],'SN':['Sun'],'MN':['Moon'],'USUM':['Ultra Sun','Ultra Moon'],'US':['Ultra Sun'],'UM':['Ultra Moon'],
 'GG':["Let's Go, Pikachu!","Let's Go, Eevee!"],'GP':["Let's Go, Pikachu!"],'GE':["Let's Go, Eevee!"],
 'SWSH':['Sword','Shield'],'SW':['Sword'],'SH':['Shield'],'BDSP':['Brilliant Diamond','Shining Pearl'],'BD':['Brilliant Diamond'],'SP':['Shining Pearl'],
 'PLA':['Legends: Arceus'],'SV':['Scarlet','Violet'],'SL':['Scarlet'],'VL':['Violet'],'ZA':['Legends: Z-A'],'XD':['XD: Gale of Darkness'],'CXD':['Colosseum'],
}
records=[];report=[]
for file in sorted((REF/'PKHeX.Core'/'Legality'/'Encounters'/'Data').rglob('*.cs')):
 text=file.read_text(encoding='utf-8-sig')
 for array in re.finditer(r'(?:internal|private|public)\s+static\s+readonly\s+(Encounter(?:Static|Trade|Gift|Starter|Shadow)\w*)\[\]\s+(\w+)\s*=\s*(?://[^\n]*\n\s*)?\[(.*?)\n\s*\];',text,re.S):
  typ,table,body=array.groups();defaults=[]
  for tf in (REF/'PKHeX.Core'/'Legality'/'Encounters'/'Templates').rglob(typ+'.cs'):
   template=tf.read_text(encoding='utf-8-sig')
   match=re.search(r'public Shiny Shiny\s*(?:=>\s*Shiny\.(\w+)|\{[^}]+\}\s*=\s*Shiny\.(\w+))',template)
   defaults.append(next(x for x in match.groups() if x) if match else 'Random')
  parsed=0
  for match in re.finditer(r'(?m)^\s*new\(([^\n]*?)\)(?:\s*//[^\n]*\n)?\s*(?:\{([^{}]+)\})?',body,re.S):
   args,properties=match.groups();properties=properties or '';spec=re.search(r'\bSpecies\s*=\s*(\d+)',properties)
   nums=[int(n) for n in re.findall(r'(?<![\w.])\b\d+\b',args)]
   if not spec and (typ.startswith('EncounterStatic') or typ.startswith('EncounterGift')) and nums: sid=nums[0]
   elif not spec and typ in {'EncounterTrade2','EncounterTrade4PID'} and len(nums)>1:sid=nums[1]
   elif spec: sid=int(spec[1])
   else:continue
   tokens=re.findall(r'\b[A-Z][A-Za-z0-9]*\b',args);game=next((g for g in tokens if g in games),None)
   if not game and typ in {'EncounterStatic8','EncounterTrade8'}:game='SWSH'
   if not game and typ=='EncounterStatic8a':game='PLA'
   if not game and typ=='EncounterStatic3XD':game='XD'
   if not game and typ=='EncounterTrade2':game='GSC'
   if not game and typ in {'EncounterStatic9a','EncounterGift9a','EncounterTrade9a'}:game='ZA'
   if not game:continue
   def val(field,default=0):
    found=re.search(r'\b'+field+r'\s*=\s*(\d+)',properties);return int(found[1]) if found else default
   shiny=re.search(r'\bShiny\s*=\s*(?:Shiny\.)?(\w+)',properties)
   shiny=shiny[1] if shiny else defaults[0] if defaults else 'Unknown'
   if typ=='EncounterTrade4PID' and shiny=='FixedValue':
    pid=re.search(r'0x([0-9A-Fa-f]+)',args)
    if pid:
     pid=int(pid[1],16);shiny='Always' if (val('TID16')^val('SID16')^(pid&65535)^(pid>>16))<8 else 'Never'
   end=array.start(3)+match.end();tail=text[end:text.find('\n',end)]
   note=tail.split('//',1)[1].strip() if '//' in tail else ''
   start=array.start(3)+match.start();line=text[:start].count('\n')+1
   form=val('Form',nums[1] if typ in {'EncounterStatic8a','EncounterStatic9a','EncounterGift9a'} and len(nums)>1 else 0)
   records.append({**({'roaming':True} if re.search(r'\bIsRoaming\s*=\s*true',properties) else {}),'species':sid,'form':form,'games':['Pokémon '+g for g in games[game]],'shiny':shiny,'gift':('Gift = true' in properties or 'FixedBall = Ball.Poke' in properties or typ.startswith('EncounterGift') or typ=='EncounterStatic3XD' or typ=='EncounterTrade2' and nums[0] in {9,10} or typ=='EncounterTrade4PID' and nums[0] in {10,11}),'egg':val('EggLocation',1 if 'IsEgg = true' in properties else 0),'location':val('Location'),'level':val('Level',nums[2] if typ in {'EncounterStatic8a','EncounterStatic9a','EncounterGift9a'} and len(nums)>2 else nums[1] if typ in {'EncounterStatic3','EncounterStatic2'} and len(nums)>1 else 0),'table':table,'type':typ,'note':note,'line':line,'file':file.relative_to(REF).as_posix(),'source':'https://github.com/kwsch/PKHeX/blob/'+sha+'/'+file.relative_to(REF).as_posix()+'#L'+str(line)})
   parsed+=1
  if 'EncounterStatic' in typ or 'EncounterTrade' in typ: report.append({'file':file.name,'table':table,'type':typ,'constructors':len(re.findall(r'(?m)^\s*new\(',body)),'parsed':parsed})
(ROOT/'audit/static-index.json').write_text(json.dumps(records,separators=(',',':')))
(ROOT/'audit/static-parse-audit.json').write_text(json.dumps(report,indent=2))
print('Parsed',len(records),'explicit encounters; unparsed tables:',[(r['file'],r['table'],r['constructors']-r['parsed']) for r in report if r['constructors']!=r['parsed']])
