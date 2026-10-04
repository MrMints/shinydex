"""Merge decoded modern wild encounters and explicit static definitions."""
import json,re
from pathlib import Path
from collections import defaultdict
from form_mapping import catalog_forms
ROOT=Path(__file__).parent
STATES={'Random':'Huntable','Never':'Shiny Locked','Always':'Guaranteed shiny','AlwaysStar':'Guaranteed shiny','AlwaysSquare':'Guaranteed shiny'}
def dlc_game(game,location):
 if game in {'Pokémon Scarlet / Violet','Pokémon Scarlet','Pokémon Violet'}:
  if location>=172:return game+' · The Indigo Disk'
  if location>=132:return game+' · The Teal Mask'
 if game in {'Pokémon Sword','Pokémon Shield'}:
  if location>=204:return game+' · The Crown Tundra'
  if location>=164:return game+' · The Isle of Armor'
 return game
def merge(records,catalog):
 forms=catalog_forms(catalog)
 form_ids={key:form for (species,form),key in forms.items()}
 grouped=defaultdict(set);sources={}
 for slot in json.loads((ROOT/'modern-wild.json').read_text()):
  catalog_key=forms.get((slot['species'],slot['form']))
  if catalog_key is None:continue
  key=(catalog_key,dlc_game(slot['game'],slot['locationId']),slot['kind'],slot['alpha'],slot['shiny'])
  grouped[key].add(slot.get('displayLocation',slot['location']));sources[key]=slot['source']
 added=0
 for key,locations in grouped.items():
  sid,game,kind,alpha,shiny=key
  method=('Wild encounters · Sparkling Power; mass outbreaks where available. Species availability depends on version; Union Circle can provide encounters hosted by the other version.' if kind=='sv' else 'Hyperspace wild encounters · Mega Dimension DLC' if kind=='hyperspace' else 'Wild Zone / city wild encounters')
  if kind=='sv-fixed':method='Fixed wild Tera Pokémon encounters · shininess is visible before battle; wild Tera spawns are separate from Tera Raid Battles'
  elif kind=='sv-event-outbreak':method='Historical distribution mass outbreak hunting · availability depends on downloaded event data; check the event announcement for dates and bonuses'
  elif kind.startswith('la-'):
   method={'la-0':'Wild encounters','la-1':'Space-time distortion encounters','la-2':'Landmark encounters','la-3':'Mass outbreak hunting','la-4':'Massive mass outbreak hunting'}[kind]
   if alpha:method+=' · guaranteed Alpha' if alpha==2 else ' · Alpha can appear'
  elif kind.startswith('bdsp-'):
   method={'bdsp-0':'Wild encounters','bdsp-1':'Grass encounters','bdsp-2':'Surf encounters','bdsp-3':'Old Rod fishing','bdsp-4':'Good Rod fishing','bdsp-5':'Super Rod fishing','bdsp-6':'Rock Smash encounters','bdsp-7':'Headbutt encounters','bdsp-8':'Honey Tree encounters','bdsp-underground':'Grand Underground Pokémon Hideaway encounters'}[kind]
  elif kind.startswith('alola-'):method='SOS call hunting' if kind=='alola-1' else 'Wild encounter hunting'
  elif kind=='pelago':method='Poké Pelago · befriend a shiny Pokémon visiting Isle Abeens'
  elif kind.startswith('swsh-'):
   method='Fishing' if kind=='swsh-fishing' else 'Shaking berry-tree encounters' if kind=='swsh-tree' else 'Surfing / water encounters' if kind in {'swsh-5','swsh-6','swsh-11'} else 'Random grass encounters' if kind in {'swsh-3','swsh-4'} else 'Overworld encounters'
  elif alpha:method+=' · Alpha encounter'
  records[str(sid)]['entries'].append(dict(game=game,method=method,status=STATES[shiny],locations=sorted(locations),source=sources[key],encounterKind=kind,gameFormId=form_ids[sid],alphaEncounter=alpha,verification='Decoded species, tracked form, location and shiny status from pinned encounter table'))
  added+=1
 for fact in json.loads((ROOT/'static-index.json').read_text()):
  if fact['type'] not in {'EncounterStatic9','EncounterStatic9a','EncounterGift9a','EncounterStatic8a','EncounterStatic8b','EncounterStatic8','EncounterStatic7'} or fact['shiny'] not in STATES:continue
  catalog_key=forms.get((fact['species'],fact['form']))
  if catalog_key is None:continue
  note=re.sub(r'\s*\([^)]*_[^)]*\)','',fact['note']).strip() or 'Special encounter'
  method=('Gift / reward: ' if fact['gift'] else 'Stationary encounter: ')+note
  if fact['gift'] and fact['species'] in {138,140,142,345,347,408,410,564,566,696,698,880,881,882,883}:
   method='Fossil revival: '+note
  if fact['level']:method+=' (level '+str(fact['level'])+')'
  for game in fact['games']:
   game=dlc_game(game,fact['location'])
   locsets={'EncounterStatic7':'gen7/text_sm','EncounterStatic8':'gen8/text_swsh','EncounterStatic8a':'gen8a/text_la','EncounterStatic8b':'gen8b/text_bdsp','EncounterStatic9':'gen9/text_sv','EncounterStatic9a':'gen9a/text_za','EncounterGift9a':'gen9a/text_za'}
   locs=(ROOT/('reference/pkhex/PKHeX.Core/Resources/text/locations/'+locsets[fact['type']]+'_00000_en.txt')).read_text(encoding='utf-8-sig').splitlines()
   location=fact['location']
   names=[locs[location]] if location and location<len(locs) and locs[location].strip() else []
   row=dict(game=game,method=method,status=STATES[fact['shiny']],locations=names,source=fact['source'],verification='Explicit static encounter shiny specification, matched tracked form')
   existing=next((e for e in records[str(catalog_key)]['entries'] if e['game']==game and e['method']==method and e['status']==row['status']),None)
   if existing:
    existing['locations']=sorted(set(existing['locations']+names))
    existing['sourceReferences']=sorted(set(existing.get('sourceReferences',[existing['source']])+[fact['source']]))
   else:
    records[str(catalog_key)]['entries'].append(row);added+=1
 return added
