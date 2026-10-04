"""Compare complete encounter identities for every condition-bearing tracked row."""
import csv,hashlib,json
from pathlib import Path
def rows(path):
 with open(path,encoding='utf-8-sig') as f:return list(csv.DictReader(f))
local={r['id']:r for r in rows('encounters.csv')}
remote={r['id']:r for r in rows('reference/pokeapi-encounters-current.csv')}
condition_ids={r['encounter_id'] for r in rows('encounter_condition_value_map.csv')}
matched=condition_ids&local.keys()
mismatches=[key for key in matched if remote.get(key)!=local[key]]
report={'conditionBearingLocalRows':len(matched),'mismatchCount':len(mismatches),'mismatchIds':sorted(mismatches,key=int),'localEncounterSha256':hashlib.sha256(Path('encounters.csv').read_bytes()).hexdigest(),'comparisonEncounterSha256':hashlib.sha256(Path('reference/pokeapi-encounters-current.csv').read_bytes()).hexdigest(),'comparisonSource':'https://raw.githubusercontent.com/PokeAPI/pokeapi/master/data/v2/csv/encounters.csv','fullHuntingAuditComplete':False}
Path('condition-compatibility-audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
assert not mismatches,report
assert matched
print('Verified complete encounter identities for',len(matched),'condition-bearing local rows against the current source snapshot')
