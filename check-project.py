"""Run checked-in verifiers; passing checks do not certify exhaustive hunting coverage."""
import json
import os
import subprocess
import sys
from datetime import datetime,timezone
from pathlib import Path

root=Path(__file__).resolve().parent
# Children emit UTF-8 to match the capture decoder. Keep diagnostics printable
# even when the Windows console cannot represent a Pokémon name or traceback.
sys.stdout.reconfigure(errors='backslashreplace')
verifier_env={**os.environ,'PYTHONIOENCODING':'utf-8'}
results=[]
for path in sorted([*root.glob('verify-*.py'),*root.glob('verify-*.cjs')]):
 command=[sys.executable if path.suffix=='.py' else 'node',str(path)]
 try:
  run=subprocess.run(command,cwd=root,env=verifier_env,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=120)
  result={'check':path.name,'passed':run.returncode==0,'exitCode':run.returncode,'output':run.stdout.strip(),'errors':run.stderr.strip()}
 except (OSError,subprocess.TimeoutExpired) as error:
  result={'check':path.name,'passed':False,'errors':str(error)}
 results.append(result)
 print(('PASS ' if result['passed'] else 'FAIL ')+path.name,flush=True)
 if not result['passed']:print(result.get('errors') or result.get('output'),flush=True)
report={'checkedAt':datetime.now(timezone.utc).isoformat(),'passed':all(r['passed'] for r in results),'checkCount':len(results),'fullHuntingAuditComplete':False,'limitations':['Checks cover their stated reference snapshots and regressions; they do not prove all games, hunting techniques, events or acquisition prerequisites are complete.','Browser interaction checks are recorded separately in runtime-qa.json.'],'results':results}
(root/'project-checks.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
print(f"{sum(r['passed'] for r in results)}/{len(results)} checks passed; exhaustive hunting audit remains incomplete.")
sys.exit(0 if report['passed'] else 1)
