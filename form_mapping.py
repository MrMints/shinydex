"""Map the tracked regional forms to game form IDs.
Indices verified against PKHeX FormConverter at the pinned reference commit.
"""
import json
from pathlib import Path
ROOT=Path(__file__).parent
def catalog_forms(catalog):
 result={};audit=[]
 for p in catalog:
  form=0
  if p.get('region'):
   form=1
   if p['name'] in {'meowth-galar','slowbro-galar','darmanitan-galar-standard','basculin-white-striped'}:form=2
   if p['id']==128:
    form=3 if 'aqua' in p['name'] else 2 if 'blaze' in p['name'] else 1
   audit.append(dict(key=p['key'],species=p['id'],name=p['displayName'],gameFormId=form))
  pair=(p['id'],form)
  assert pair not in result,pair
  result[pair]=p['key']
 assert len(audit)==58
 sha=json.loads((ROOT/'reference/pkhex/tree.json').read_text())['sha']
 (ROOT/'regional-form-audit.json').write_text(json.dumps(dict(source='https://github.com/kwsch/PKHeX/blob/'+sha+'/PKHeX.Core/PKM/Util/Conversion/FormConverter.cs',forms=audit),indent=2))
 return result
