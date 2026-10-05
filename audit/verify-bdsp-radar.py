"""Check decoded BDSP Radar coverage and independent gameplay regressions.

Trophy Garden introductions are independently checked; remaining conditions
outside that reviewed location are not established by these checks.
"""

# Audit tools resolve shared inputs from the repository, regardless of launch directory.
import os as _audit_os
import sys as _audit_sys
from pathlib import Path as _AuditPath
_audit_root = _AuditPath(__file__).resolve().parents[1]
_audit_sys.path.insert(0, str(_audit_root))
_audit_os.chdir(_audit_root)

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
hunts = json.loads((ROOT / 'hunts.json').read_text())
actual = {(int(key), entry['game']): entry
          for key, guide in hunts.items() for entry in guide['entries']
          if entry.get('huntingTechnique') == 'bdsp-radar'}
BD, SP = 'Pokémon Brilliant Diamond', 'Pokémon Shining Pearl'
assert len(actual) == 321

# Locations independently reviewed in the pinned reader: interiors, Marsh,
# honey trees, water and Underground must not become grass Radar hunts.
for entry in actual.values():
    ids = set(entry['radarLocationIds'])
    assert not ids.intersection({195, 196, 203, 208, 244, 252, 255, 260,
                                 286, 292, 294, 296, 299, 306, 368})
    assert not any(219 <= loc <= 243 for loc in ids)
    assert all(text in entry['method'] for text in
               ('Manaphy is excluded', '50 steps', '1/99',
                'Shiny Charm does not', 'Hidden Ability', 'randomly',
                'conditional pools', '1.1.3'))

# Bulbapedia's BDSP-exclusive roster checks, including version distinctions.
for game in (BD, SP):
    for sid, ids in {29:{354}, 32:{354}, 128:{367,373}, 241:{367,373},
                     132:{400}, 175:{489}, 294:{206,207}}.items():
        assert ids <= set(actual[(sid,game)]['radarLocationIds'])
    assert 259 in actual[(324,game)]['radarLocationIds']
assert 375 in actual[(352,BD)]['radarLocationIds'] and (352,SP) not in actual
assert 375 in actual[(371,SP)]['radarLocationIds'] and (371,BD) not in actual
assert (246,BD) in actual and (246,SP) not in actual
assert (234,SP) in actual and (234,BD) not in actual

# Complete independently published Radar-exclusive roster (43 species).
# Compare every species/version pair and the union of named locations, rather
# than certifying only the earlier seven samples. Split-map version details
# still require individual encounter-table review.
exclusive_locations={
 29:{'Route 201'},30:{'Valor Lakefront','Route 221'},32:{'Route 201'},
 33:{'Valor Lakefront','Route 221'},48:{'Route 229'},49:{'Route 229'},
 56:{'Route 225','Route 226'},57:{'Route 225','Route 226'},79:{'Route 205'},
 88:{'Route 212'},128:{'Route 209','Route 210'},132:{'Route 218'},
 161:{'Route 202'},175:{'Route 230'},179:{'Valley Windworks'},180:{'Route 222'},
 187:{'Route 205','Fuego Ironworks'},188:{'Route 205','Fuego Ironworks'},
 191:{'Route 204'},202:{'Lake Verity','Lake Valor','Lake Acuity'},
 229:{'Route 214','Route 215'},234:{'Route 207'},235:{'Route 212'},
 236:{'Route 208','Route 211'},241:{'Route 209','Route 210'},246:{'Route 207'},
 262:{'Route 214','Route 215'},277:{'Route 213'},280:{'Route 203','Route 204'},
 281:{'Route 203','Route 204'},290:{'Eterna Forest'},294:{'Mount Coronet'},
 304:{'Fuego Ironworks'},324:{'Route 227','Stark Mountain'},328:{'Route 228'},
 329:{'Route 228'},333:{'Route 211'},343:{'Route 206'},352:{'Route 210'},
 355:{'Route 224'},356:{'Route 224'},361:{'Route 216','Route 217','Acuity Lakefront'},
 371:{'Route 210'}}
only_bd={246,262,304,352};only_sp={79,229,234,371}
exclusive_pairs=[]
for sid,expected_locations in exclusive_locations.items():
    found_locations=set()
    for game in (BD,SP):
        expected=not (game==BD and sid in only_sp or game==SP and sid in only_bd)
        assert ((sid,game) in actual)==expected,(sid,game)
        if expected:
            exclusive_pairs.append((sid,game))
            found_locations.update(label.split(' ·')[0] for label in actual[(sid,game)]['locations'])
    assert found_locations==expected_locations,(sid,found_locations,expected_locations)
assert len(exclusive_locations)==43 and len(exclusive_pairs)==78

# Independently read the actual BDSP tables for both Route 205 sections and
# Fuego Ironworks, including negative version/location checks.
for game,expected in ((BD,{187:{359,361},188:{361},304:{201}}),
                      (SP,{187:{359,201},188:{201},79:{361}})):
    for sid,locations in expected.items():
        row=actual[(sid,game)]
        assert set(row['radarLocationIds'])==locations,(sid,game)
        assert any('/pokearth/sinnoh/' in source for source in row['sourceReferences'])
        assert 'This version’s Radar encounters' in row['method']

# Independent BDSP Garden roster from its Generation VIII encounter table.
garden_special = (35,39,52,113,133,137,173,174,183,298,311,312,351,438,439,440)
for game in (BD,SP):
    garden_rows = {sid: row for (sid,g),row in actual.items()
                   if g==game and row.get('gardenConditionVerified')}
    assert set(garden_rows)==set(garden_special)
    for order,sid in enumerate(garden_special,1):
        row=garden_rows[sid]
        assert row['gardenIntroductionOrder']==order and 297 in row['radarLocationIds']
        assert all(word in row['method'] for word in
                   ('midnight','fixed 16-species','two most recent','does not reroll'))
        assert any('Trophy_Garden' in source for source in row['sourceReferences'])
        assert any('Backlot must' in label for label in row['locations'])
    for sid in (25,172,315,397,402):
        assert not actual[(sid,game)].get('gardenConditionVerified')

# All 28 rows of the independent BDSP outbreak table, in both versions.
swarm_ids={16:420,81:201,83:404,84:354,96:394,98:487,100:400,104:356,
           108:327,177:411,206:365,209:367,220:397,222:489,225:395,231:364,
           238:330,263:355,283:323,287:200,296:412,299:362,300:407,309:197,
           325:392,327:414,359:385,374:416}
for game in (BD,SP):
    swarm_rows={sid:row for (sid,g),row in actual.items()
                if g==game and row.get('swarmConditionVerified')}
    assert set(swarm_rows)==set(swarm_ids)
    for sid,location in swarm_ids.items():
        row=swarm_rows[sid]
        assert location in row['radarLocationIds']
        assert all(word in row['method'] for word in
                   ('only while its daily swarm','pause-menu','cannot be directly'))
        assert any('active daily swarm' in label for label in row['locations'])
        assert any('Mass_outbreak' in source for source in row['sourceReferences'])
    assert not actual[(29,game)].get('swarmConditionVerified')

ordinary_conditions={(int(key),row['game']):row for key,guide in hunts.items()
                     for row in guide['entries'] if row.get('conditionalAvailabilityVerified')}
assert len(ordinary_conditions)==88
for game in (BD,SP):
    for sid in garden_special:
        row=ordinary_conditions[(sid,game)]
        assert row['encounterKind']=='bdsp-1' and row['conditionalAvailabilityVerified']=='garden'
        assert 'fixed 16-species' in row['method']
    for sid in swarm_ids:
        row=ordinary_conditions[(sid,game)]
        assert row['encounterKind']=='bdsp-1' and row['conditionalAvailabilityVerified']=='swarm'
        assert 'only while its daily swarm' in row['method']

report = {'checked':'2026-10-04', 'routes':len(actual),
          'fullCoverageVerified':False,
          'verified':'Pinned grass-slot location eligibility; complete 43-species Radar-exclusive roster comparison, all eight version exclusions and combined named locations; game-specific mechanics and National Dex prerequisites; all 16 Trophy Garden introductions and 28 daily swarms in both games with exact introduction/swarm conditions',
          'exclusiveSpeciesVerified':43,'exclusiveSpeciesGamePairsVerified':78,
          'gardenConditionalRoutesVerified':32,
          'swarmConditionalRoutesVerified':56,
          'ordinaryGrassConditionalRoutesVerified':88,
          'remaining':['Time conditions for unmapped sections and other interior encounters',
                       'Individual grass sections outside reviewed Route 205 and Fuego Ironworks',
                       'All access prerequisites and short-grass tile mapping'],
          'references':['https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9_Radar',
                        'https://bulbapedia.bulbagarden.net/wiki/National_Pok%C3%A9dex',
                        'https://bulbapedia.bulbagarden.net/wiki/Trophy_Garden',
                        'https://bulbapedia.bulbagarden.net/wiki/Mass_outbreak']}
report['references'].append('https://www.serebii.net/brilliantdiamondshiningpearl/pokeradar.shtml')
report['splitMapSpeciesGamePairsVerified']=6
report['references'].extend(['https://www.serebii.net/pokearth/sinnoh/route205.shtml',
                             'https://www.serebii.net/pokearth/sinnoh/fuegoironworks.shtml'])
# The independent source inventory remains evidence for manual review, rather
# than a second automatically generated guide. Check its known conditional
# cases so a parser regression cannot silently erase time/section distinctions.
inventory=json.loads((ROOT/'audit/bdsp-independent-tables.json').read_text(encoding='utf-8'))
assert inventory['fullCoverageVerified'] is False
assert len(inventory['sources'])==39 and not inventory['failures']
assert not inventory['unmatchedGuideLocations']
assert inventory['unmappedLocationIds']==[]
assert '\ufffd' not in json.dumps(inventory,ensure_ascii=False)
for game in (BD,SP):
    # Legacy-encoded page headings must retain Radar pools, never inherit
    # ordinary encounter times from a preceding table.
    wobbuffet=[row for row in inventory['rows'] if row['species']==202
               and row['game']==game and row['location']=='Lake Verity']
    assert len(wobbuffet)==2
    assert all(row['pool']=='PokéRadar' and row['times']==[] for row in wobbuffet)
    for sid,period in ((401,'morning'),(41,'night')):
        reviewed=[row for row in hunts[str(sid)]['entries'] if row['game']==game
                  and (row.get('encounterKind')=='bdsp-1' or row.get('huntingTechnique')=='bdsp-radar')]
        assert len(reviewed)==2
        assert all(f'Route 206 · {period} only' in row['locations'] for row in reviewed)
        assert all(next(item for item in row['reviewedTimeConditions'] if item['locationId']==362)['times']==[period] for row in reviewed)
assert all(len(source['sha256'])==64 and source['parsedRows']>0 for source in inventory['sources'])
time_rows={(row['species'],row['game'],row['locationId']):set(row['times'])
           for row in inventory['timeRestrictedCandidates']}
for game in (BD,SP):
    assert time_rows[(401,game,362)]=={'morning'}
    assert time_rows[(166,game,420)]=={'morning'}
    assert time_rows[(168,game,420)]=={'night'}
assert time_rows[(198,BD,200)]=={'night'}
assert time_rows[(200,SP,200)]=={'night'}
# Independent expectations from the reviewed published tables. Check both
# guide methods and keep version exclusives out of the opposite game's review.
expected_reviews={(401,362):{'morning'},(41,362):{'night'},
                  (166,420):{'morning'},(168,420):{'night'},
                  (441,407):{'morning','day'},(441,411):{'morning','day'}}
expected_reviews.update({(401,loc):{'morning','night'} for loc in (355,356,357,358,364)})
expected_reviews.update({(41,loc):{'night'} for loc in (356,357,358,364,367)})
expected_reviews[(92,367)]={'night'}
for sid,locs in {42:[259,414],164:[263,327,330,351,375,378,395,397],
                 354:[259,412,414,487],41:[351,365,377,378,395,397],163:[375,377]}.items():
    expected_reviews.update({(sid,loc):{'night'} for loc in locs})
expected_reviews.update({(307,loc):{'morning','day'} for loc in (351,397)})
expected_reviews.update({(sid,loc):{'night'} for sid in (42,164) for loc in (206,207)})
expected={(sid,game,loc):times for (sid,loc),times in expected_reviews.items() for game in (BD,SP)}
expected.update({(198,BD,200):{'night'},(200,SP,200):{'night'}})
reviewed={(int(key),row['game'],condition['locationId']):set(condition['times'])
          for key,guide in hunts.items() for row in guide['entries']
          if row.get('huntingTechnique')=='bdsp-radar'
          for condition in row.get('reviewedTimeConditions',[])}
assert reviewed==expected
assert len(reviewed)==92
assert inventory['reviewedTimeRestrictedCombinations']==92
assert not inventory['unreviewedTimeCandidates']
for key,times in expected.items():
    assert time_rows[key]==times
    sid,game,loc=key
    ordinary=[row for row in hunts[str(sid)]['entries']
              if row['game']==game and row.get('encounterKind')=='bdsp-1']
    assert len(ordinary)==1
    condition=next(item for item in ordinary[0]['reviewedTimeConditions'] if item['locationId']==loc)
    assert set(condition['times'])==times
    label=condition['location']+(' · '+condition['section'] if condition.get('section') else '')+' · '+' or '.join(condition['times'])+' only'
    assert label in ordinary[0]['locations'] and label in actual[(sid,game)]['locations']
assert not actual.get((198,SP),{}).get('reviewedTimeConditions')
assert not actual.get((200,BD),{}).get('reviewedTimeConditions')
for game in (BD,SP):
    for sid in (41,92):
        ordinary=next(row for row in hunts[str(sid)]['entries']
                      if row['game']==game and row.get('encounterKind')=='bdsp-1')
        assert all(f'Route 209 · Lost Tower {floor}F' in ordinary['locations'] for floor in range(1,6))
        assert 'Route 209 · night only' in ordinary['locations']
        assert 'https://www.serebii.net/pokearth/sinnoh/losttower.shtml' in ordinary['sourceReferences']
    assert all('Lost Tower' not in label for (sid,g),row in actual.items()
               if g==game for label in row['locations'])
    golbat=next(row for row in hunts['42']['entries'] if row['game']==game and row.get('encounterKind')=='bdsp-1')
    assert 'Stark Mountain · cave interior' in golbat['locations']
    assert 'Stark Mountain · exterior grass · night only' in golbat['locations']
    assert 'Mount Coronet · cave interior' in golbat['locations']
    assert all('cave interior' not in label for (sid,g),row in actual.items() if g==game for label in row['locations'])
wild=json.loads((ROOT/'audit/modern-wild.json').read_text(encoding='utf-8'))
for game,exclusive in ((BD,198),(SP,200)):
    ordinary=next(row for row in hunts[str(exclusive)]['entries'] if row['game']==game and row.get('encounterKind')=='bdsp-1')
    interior={c['locationId']:c for c in ordinary['reviewedTimeConditions'] if 368<=c['locationId']<=372}
    assert set(interior)==set(range(368,373))
    assert 'start its Radar chain' not in ordinary['method']
    for floor in range(1,6):
        loc=367+floor
        label=f'Route 209 · Lost Tower {floor}F · night only'
        assert label in ordinary['locations'] and interior[loc]['times']==['night']
        slots=[s for s in wild if s['game']==game and s['kind']=='bdsp-1' and s['locationId']==loc]
        expected_roster={41,92,exclusive}|({42} if floor>=3 else set())
        assert {s['species'] for s in slots}==expected_roster
        exclusive_slots=[s for s in slots if s['species']==exclusive]
        assert len(exclusive_slots)==1
        assert exclusive_slots[0]['levelMin']==exclusive_slots[0]['levelMax']==16+floor
    golbat=next(row for row in hunts['42']['entries'] if row['game']==game and row.get('encounterKind')=='bdsp-1')
    assert {label for label in golbat['locations'] if 'Lost Tower' in label}=={f'Route 209 · Lost Tower {floor}F' for floor in (3,4,5)}
report['lostTowerReview']={'floors':5,'nightRestrictedSpeciesGameFloorCombinations':10,
                         'rostersAndVersionExclusivesVerified':True,
                         'source':'https://www.serebii.net/pokearth/sinnoh/losttower.shtml'}
for game in (BD,SP):
    garden_inventory={row['species'] for row in inventory['rows']
                      if row['location']=='Trophy Garden' and row['game']==game
                      and row['section']=='Daily Pokemon'}
    assert garden_inventory==set(garden_special)
sections=json.loads((ROOT/'audit/bdsp-section-review.json').read_text(encoding='utf-8'))
assert {r['locationId']:(r['mapFile'],r['publishedSection']) for r in sections['sections']}=={
    206:('D05R0104','Snow Area'),207:('D05R0105','Top'),
    323:('D27R0101','Before Galactic'),324:('D27R0102','After Galactic')}
for game in (BD,SP):
    for sid in (35,67,294,308,433,437,459,460):
        row=actual[(sid,game)]
        assert 'Mount Coronet · snow area exterior' in row['locations']
        assert 'Mount Coronet · summit exterior' in row['locations']
        assert 'https://luminescent.team/rom-hacking/dictionary/zones' in row['sourceReferences']
    for sid in (202,396,399):
        row=actual[(sid,game)]
        assert 'Lake Verity · before Galactic incident' in row['locations']
        assert 'Lake Verity · after Galactic incident' in row['locations']
    swarm=actual[(283,game)]
    assert any('before Galactic incident; this species must be the active daily swarm' in label for label in swarm['locations'])
    assert any('after Galactic incident; this species must be the active daily swarm' in label for label in swarm['locations'])
report['sectionMappingReview']={'resolvedLocationIds':[206,207,323,324],
                               'fullCoverageVerified':False,'sources':sections['sources']}
report['independentTableInventory']={'pages':39,'unmappedLocationIds':[],
                                    'timeRestrictedCandidates':len(time_rows),
                                    'guideConditionsPromoted':True,
                                    'reviewedTimeRestrictedCombinations':len(reviewed),
                                    'remainingTimeRestrictedCandidates':len(time_rows)-len(reviewed)}
(ROOT / 'audit/bdsp-radar-review.json').write_text(json.dumps(report,indent=2))
print(f'Verified 321 BDSP Radar routes, 32 Garden introductions, 56 swarm conditions and {len(reviewed)} reviewed time combinations; remaining ordinary time slots and access audit incomplete')
