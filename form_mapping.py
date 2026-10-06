"""Map the tracked regional forms to game form IDs.
Indices verified against PKHeX FormConverter at the pinned reference commit.
"""
import json
from pathlib import Path
ROOT=Path(__file__).parent
def catalog_forms(catalog):
 """Return the legacy encounter decoder's species/regional key mapping.

 Living-dex gender and cosmetic identities have independent ownership keys,
 but do not share this decoder's one-key-per-game-form representation. Their
 hunting routes require separate reviewed mappings rather than overwriting
 legacy routes with the last matching appearance.
 """
 result={};audit=[]
 for p in catalog:
  if p.get('livingForm'):continue
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
 (ROOT/'audit/regional-form-audit.json').write_text(json.dumps(dict(source='https://github.com/kwsch/PKHeX/blob/'+sha+'/PKHeX.Core/PKM/Util/Conversion/FormConverter.cs',forms=audit),indent=2))
 return result
