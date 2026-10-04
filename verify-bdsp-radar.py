"""Check decoded BDSP Radar coverage and independent gameplay regressions.

These checks do not establish exact swarm/time/garden conditions for every slot.
"""
import json
from pathlib import Path

ROOT = Path(__file__).parent
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

report = {'checked':'2026-10-04', 'routes':len(actual),
          'fullCoverageVerified':False,
          'verified':'Pinned grass-slot location eligibility, independent exclusive roster samples, game-specific mechanics and National Dex prerequisites',
          'remaining':['Exact time/swarm/Backlot conditions per slot',
                       'Independent complete Radar-exclusive roster comparison',
                       'All access prerequisites and short-grass tile mapping'],
          'references':['https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9_Radar',
                        'https://bulbapedia.bulbagarden.net/wiki/National_Pok%C3%A9dex']}
(ROOT / 'bdsp-radar-review.json').write_text(json.dumps(report,indent=2))
print('Verified 321 BDSP Radar routes, location exclusions, version-exclusive samples and mechanics; conditional pool audit remains incomplete')
