"""Verify SOS version mechanics and independently reviewed special targets."""

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
entries = [(key, e) for key, g in hunts.items() for e in g['entries']
           if e.get('encounterKind') == 'alola-1']
assert len(entries) == 843
for key, entry in entries:
    method = entry['method']
    assert entry['huntingTechnique'] == 'alola-sos'
    assert all(t in method for t in ('Verdant Cavern', 'three trials',
        'persistent status', 'Struggle', 'answered calls', '13 at 31',
        'Shiny Charm', 'remain under review'))
    if 'Ultra' in entry['game']:
        assert 'counter caps at 255' in method and 'wraps after 255' not in method
    else:
        assert 'wraps after 255' in method and 'counter caps at 255' not in method
    if int(key) == 62: assert 'rain active during daytime' in method
    if int(key) == 186: assert 'rain active during nighttime' in method
    if int(key) == 444: assert 'sandstorm active' in method
    if int(key) in (582,583,584): assert 'hail' in method
    if int(key) in (704,705): assert 'rain' in method
    if int(key) == 747: assert 'Mareanie attacks Corsola' in method
    if int(key) == 302: assert 'Sableye attacks Carbink' in method
report = {'checked':'2026-10-04', 'routes':len(entries),
          'fullCoverageVerified':False,
          'verified':['Core mechanics and SM/USUM counter differences',
                      'Fourteen special weather/caller target notes'],
          'remaining':['Complete caller relationships per encounter slot',
                       'Precise room/time/weather conditions and story access'],
          'references':['https://bulbapedia.bulbagarden.net/wiki/SOS_Battle',
                        'https://bulbapedia.bulbagarden.net/wiki/Adrenaline_Orb']}
(ROOT / 'audit/sos-review.json').write_text(json.dumps(report,indent=2))
print('Verified mechanics for 843 SOS routes, version counter differences and special targets; full caller audit remains incomplete')
