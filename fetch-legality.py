"""Download public encounter source/data for audit only; do not execute upstream code."""
import json,urllib.request,sys,concurrent.futures
from pathlib import Path
ROOT=Path(__file__).parent/'reference'/'pkhex'
ROOT.mkdir(parents=True,exist_ok=True)
def fetch(url):
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'ShinyDex encounter audit'}),timeout=40) as response:return response.read()
tree=json.loads((ROOT/'tree.json').read_text()) if (ROOT/'tree.json').exists() else json.loads(fetch('https://api.github.com/repos/kwsch/PKHeX/git/trees/master?recursive=1'))
(ROOT/'tree.json').write_text(json.dumps(tree))
paths=[e['path'] for e in tree['tree'] if e['type']=='blob' and ('Legality/Encounters/Data/' in e['path'] or '/Resources/legality/wild/' in e['path'] or 'EncounterArea' in e['path'] or 'EncounterSlot' in e['path'])]
(ROOT/'paths.json').write_text(json.dumps(paths,indent=2))
print('Commit:',tree['sha'],'files:',len(paths))
if '--remaining' in sys.argv:
 paths+= [e['path'] for e in tree['tree'] if e['type']=='blob' and (('Encounters/Templates/' in e['path'] and any(n in e['path'] for n in ['EncounterStatic','EncounterTrade','EncounterGift','SlotType','AreaWeather','Shiny.cs'])) or 'BinLinkerAccessor' in e['path'] or ('Resources/text/locations/' in e['path'] and e['path'].endswith('_en.txt')) or ('Resources/byte/personal/' in e['path'] and e['path'].endswith(('personal_sv','personal_bdsp','personal_la','personal_swsh','personal_za'))) or e['path']=='LICENSE')]
else: paths=[p for p in paths if 'Legality/Encounters/Data/' in p]
paths+=['PKHeX.Core/Game/Locations/Locations.cs']
paths+=['PKHeX.Core/PKM/Util/Conversion/FormConverter.cs','PKHeX.Core/Legality/Tables/FormInfo.cs']
paths += [e['path'] for e in tree['tree'] if e['type']=='blob' and 'Encounters/Templates/Gen9/' in e['path'] and any(n in e['path'] for n in ['EncounterDist9.cs','EncounterFixed9.cs','EncounterMight9.cs','EncounterOutbreak9.cs','EncounterTera9.cs'])]
paths += [e['path'] for e in tree['tree'] if e['type']=='blob' and 'Encounters/Templates/' in e['path'] and any(n in e['path'] for n in ['EncounterStarter3Colo.cs','EncounterShadow3XD.cs'])]
def download(path):
 target=ROOT/path;target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists():return
 target.write_bytes(fetch('https://raw.githubusercontent.com/kwsch/PKHeX/'+tree['sha']+'/'+path))
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(download,paths))
print('Downloaded encounter definitions')
