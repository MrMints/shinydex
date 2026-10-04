"""Read the pinned public Friend Safari roster without executing upstream code."""
import re
from pathlib import Path
REFERENCE=Path('reference/pkhex/PKHeX.Core/Legality/Encounters/Templates/Gen6/EncounterArea6XY.cs')
SOURCE='https://github.com/kwsch/PKHeX/blob/542111fc8584ff29c9d1455553b8acd0e1f8a59a/PKHeX.Core/Legality/Encounters/Templates/Gen6/EncounterArea6XY.cs'
VERIFIED_SLOTS={species:('Normal',slot) for slot,species_list in {
 1:[216,190,206,506],2:[294,352,531,572],3:[113,132,133,235],
}.items() for species in species_list}
for safari_type,slots in {
 'Grass':{1:[43,114,191,511],2:[2,541,548,586],3:[556,651,673]},
 'Poison':{1:[14,44,268,336],2:[49,168,317,569],3:[89,452,454,544]},
 'Electric':{1:[101,417,587,702],2:[25,125,618,694],3:[310,404,523,596]},
 'Ground':{1:[27,194,231,328],2:[51,105,290,323],3:[423,536,660]},
 'Psychic':{1:[63,96,326,517],2:[202,561,677],3:[178,203,575,578]},
 'Rock':{1:[299,525,557],2:[95,219,222,247],3:[112,213,689]},
 'Ice':{1:[225,361,363,459],2:[215,614,712],3:[87,91,131,221]},
 'Fire':{1:[58,77,126,513],2:[5,218,636,668],3:[38,654,662]},
 'Fighting':{1:[56,67,307,619],2:[538,539,674],3:[236,286,297,447]},
 'Water':{1:[98,224,400,515],2:[8,130,195,419],3:[61,184,657]},
}.items():
 for slot,species_list in slots.items():
  for species in species_list:
   assert species not in VERIFIED_SLOTS
   VERIFIED_SLOTS[species]=(safari_type,slot)
FLYING_SLOTS={species:slot for slot,species_list in {
 1:[16,21,83,84],2:[163,520,527,581],3:[357,627,662,701],
}.items() for species in species_list}
EXTRA_SAFARIS={
 'Dark':{1:[262,274,624,629],2:[215,332,342,551],3:[302,359,510,686]},
 'Steel':{1:[82,303,597],2:[205,227,375,600],3:[437,530,707]},
 'Fairy':{1:[175,209,281,702],2:[39,303,682,684],3:[35,670]},
 'Bug':{1:[12,46,165,415],2:[267,284,313,314],3:[49,127,214,666]},
 'Dragon':{1:[444,611],2:[148,372,714],3:[621,705]},
 'Ghost':{1:[353,608],2:[708,710],3:[356,426,442,623]},
}
def roster():
 text=REFERENCE.read_text(encoding='utf-8-sig')
 match=re.search(r'AllFriendSafariSpecies\s*=>\s*\[([^]]+)\]',text)
 assert match
 species={int(s) for s in re.findall(r'\b\d+\b',match[1])}
 assert 'Species.Floette' in text and 'Species.Vivillon' in text
 return species|{666,670}
def merge(records):
 count=0
 for species in sorted(roster()):
  assert str(species) in records and not records[str(species)]['locked']
  for game in ('Pokémon X','Pokémon Y'):
   records[str(species)]['entries'].append({'game':game,'method':'Friend Safari shiny hunting · level 30 encounters with improved shiny odds; Shiny Charm applies. Reach the Hall of Fame to access Kiloude City, then use a registered friend’s Safari containing this species. First two slots are available immediately; third-slot species require that friend to have entered the Hall of Fame and been recognized while playing together. Previously unlocked third slots remain usable; after the 3DS online-service shutdown, unlocking new third slots requires local play together.','status':'Huntable','locations':['Kiloude City · Friend Safari · species depends on registered friend’s Safari'],'huntingTechnique':'xy-friend-safari','source':SOURCE,'sourceReferences':['https://bulbapedia.bulbagarden.net/wiki/Friend_Safari']})
   count+=1
   if species in VERIFIED_SLOTS:
    safari_type,slot=VERIFIED_SLOTS[species]
    entry=records[str(species)]['entries'][-1]
    entry['friendSafariType']=safari_type
    entry['friendSafariSlot']=slot
    entry['locations']=[f'Kiloude City · {safari_type}-type Friend Safari · Slot {slot}']
    entry['method']+=f' This species occupies Slot {slot} of a {safari_type}-type Safari. '+('The third-slot unlock is required for this species.' if slot==3 else 'This species is available before the third slot is unlocked.')
   entry=records[str(species)]['entries'][-1]
   assignments=[]
   if species in VERIFIED_SLOTS:assignments.append(VERIFIED_SLOTS[species])
   if species in FLYING_SLOTS:assignments.append(('Flying',FLYING_SLOTS[species]))
   for kind,slots in EXTRA_SAFARIS.items():
    for slot,species_list in slots.items():
     if species in species_list:
      assignments.append((kind,slot))
      entry['method']+=f' This species occupies Slot {slot} of a {kind}-type Safari. '+('The third-slot unlock is required for this Safari route.' if slot==3 else 'This Safari route is available before the third slot is unlocked.')
   if assignments:
    entry['friendSafariAssignments']=[{'type':kind,'slot':slot} for kind,slot in assignments]
    entry['locations']=[f'Kiloude City · {kind}-type Friend Safari · Slot {slot}' for kind,slot in assignments]
   if species in FLYING_SLOTS:
    slot=FLYING_SLOTS[species]
    entry['method']+=f' This species occupies Slot {slot} of a Flying-type Safari. '+('The third-slot unlock is required for this species.' if slot==3 else 'This species is available before the third slot is unlocked.')
   if species==666:entry['method']+=' Vivillon uses the hunting player’s own location data for its pattern, rather than the Safari owner’s location.'
   if species==670:entry['method']+=' Friend Safari Floette has Red, Yellow or Blue flowers; the Safari owner determines the flower color. Orange and White flowers are unavailable here.'
   if species==423:entry['method']+=' Friend Safari Gastrodon is West Sea form only.'
   if species==586:entry['method']+=' Friend Safari Sawsbuck is Spring Form only.'
   if species==710:entry['method']+=' Friend Safari Pumpkaboo is Average Size.'
 return count
