"""Merge form-specific raid routes while preserving host and shiny restrictions."""
import json
from pathlib import Path
from collections import defaultdict
from form_mapping import catalog_forms
from modern_hunts import dlc_game,STATES
ROOT=Path(__file__).parent
def identity(raid,forms):
 key=forms.get((raid['species'],raid['form']))
 if key is None:return None
 game=dlc_game(raid['game'],raid['locationId'])
 if raid['kind']=='tera-raid':
  if 'Kitakami' in raid['location']:game+=' · The Teal Mask'
  elif 'Terarium' in raid['location']:game+=' · The Indigo Disk'
 return (key,game,raid['kind'],raid['shiny'],raid.get('gigantamax',False),tuple(raid.get('hostVersions',[])),raid['source'])
def merge(records,catalog):
 forms=catalog_forms(catalog);groups=defaultdict(list)
 for raid in json.loads((ROOT/'raid-encounters.json').read_text()):
  key=identity(raid,forms)
  if key:groups[key].append(raid)
 for key,raids in groups.items():
  catalog_key,game,kind,shiny,gmax,hosts,source=key
  stars=sorted({star for raid in raids for star in raid.get('stars',[])})
  method={
   'max-raid':'Max Raid Battle den hunting',
   'max-raid-event':'Historical event Max Raid Battles · availability depends on downloaded event data',
   'dynamax-adventure':'Dynamax Adventures · catch and check the summary at the results screen; shininess is rolled after the adventure (1/300, or 1/100 with Shiny Charm). Version-exclusive paths can be accessed by joining another host',
   'tera-raid':'Tera Raid Battle hunting · inspect the Pokémon during the raid',
   'tera-raid-event':'Historical event Tera Raid Battles · availability depends on downloaded event data',
   'tera-raid-mightiest':'Historical Mightiest Mark Tera Raid event · availability depends on downloaded event data',
  }[kind]
  if stars:method+=' · '+', '.join(map(str,stars))+'-star raids'
  if gmax:method+=' · Gigantamax-capable Pokémon'
  if hosts:method+=' · host in '+' / '.join(hosts)+'; joining a host is possible from either version'
  records[str(catalog_key)]['entries'].append(dict(game=game,method=method,status=STATES[shiny],locations=sorted({raid['location'] for raid in raids}),source=source,raidKind=kind,gameFormId=raids[0]['form'],gigantamax=gmax,hostVersions=list(hosts),raidStars=stars,eventIndices=sorted({r['eventIndex'] for r in raids if 'eventIndex' in r}),verification='Decoded tracked form, raid type, host version and shiny status from pinned raid tables'))
 return len(groups)
