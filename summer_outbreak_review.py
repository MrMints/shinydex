"""Add announcement-backed examples without dating all decoded outbreak rows."""
SOURCE='https://sv-news.pokemon.co.jp/en/page/235.html'

def merge(records,catalog):
 groups=[
  ('July 12–25, 2024',None,[(172,None,'Paldea'),(25,None,'Kitakami'),(778,None,'Kitakami'),(26,None,'Blueberry Academy'),(26,'alola','Blueberry Academy')]),
  ('July 26–August 8, 2024',None,[(978,None,'Paldea')]),
  ('August 9–22, 2024','Pumped-Up',[(940,None,'Paldea'),(447,None,'Kitakami'),(764,None,'Blueberry Academy')]),
  ('August 23–September 1, 2024','Charismatic',[(246,None,'Paldea'),(371,None,'Paldea'),(704,None,'Kitakami'),(705,'hisui','Kitakami'),(374,None,'Blueberry Academy')]),
 ]
 count=0
 for dates,mark,targets in groups:
  for sid,region,area in targets:
   pokemon=next(p for p in catalog if p['id']==sid and p.get('region')==region)
   game='Pokémon Scarlet / Violet'+(' · The Teal Mask' if area=='Kitakami' else ' · The Indigo Disk' if area=='Blueberry Academy' else '')
   for entry in records[str(pokemon['key'])]['entries']:
    if entry.get('encounterKind')!='sv-event-outbreak' or entry['game']!=game:continue
    note=f' Verified historical example: {dates}, from 00:00 UTC on the first date through 23:59 UTC on the last, in {area}; increased shiny availability.'
    if sid==978:note+=' This example is Curly Form Tatsugiri only.'
    if mark:note+=f' Increased {mark} Mark availability also applied.'
    entry['method']+=note+' Download the game update and applicable Poké Portal News; receiving news does not require paid Nintendo Switch Online. Other events represented by this decoded row still require review.'
    entry.setdefault('sourceReferences',[]).append(SOURCE)
    count+=1
 return count
