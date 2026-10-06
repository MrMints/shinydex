"""Finalize gender mappings with explicit legacy identity and caption evidence."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    review=json.loads((ROOT/'audit/gender-artwork-review.json').read_text(encoding='utf-8'))
    inventory=json.loads((ROOT/'audit/living-dex-inventory.json').read_text(encoding='utf-8'))
    catalog=json.loads((ROOT/'data.json').read_text(encoding='utf-8'))
    registry={r['name']:r for r in json.loads((ROOT/'audit/archives-images.json').read_text(encoding='utf-8'))}
    bases=[next(p for p in catalog if p['key']==sid) for sid in inventory['genderDifferenceSpecies']]
    bases.append(next(p for p in catalog if p['name']=='sneasel-hisui'))
    definitions=[]
    for base in bases:
        for gender,offset in [('Male',0),('Female',1)]:
            p={'identity':base['name']+'-'+gender.lower(),'key':300000+base['key']*2+offset,'legacyKey':base['key'],'speciesId':base['id'],'gender':gender,'formLabel':(base.get('formLabel','')+' · ' if base.get('region') else '')+gender}
            for mode in ['normal','shiny']:
                original=base[mode+'File']
                file=original if gender=='Male' or base['id']==255 else original.replace('_s.png','_f_s.png') if mode=='shiny' else original.replace('.png','_f.png')
                assert file in registry and (ROOT/'assets/pokemon'/file).is_file(),file
                if gender=='Female' and base['id']!=255:
                    caption=review['captions'][file]['wikitext']
                    assert 'female' in caption.lower(),file
                    assert ('shiny' in caption.lower())==(mode=='shiny'),file
                p[mode+'File']=file;p[mode+'Source']=registry[file]['descriptionurl']
            definitions.append(p)
    assert len(definitions)==206 and len({p['key'] for p in definitions})==206
    manifest={'schemaVersion':1,'forms':definitions,'scopeSource':'https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_with_gender_differences','exceptions':{'255':'Torchic gender distinction is a rear black spot; front artwork shared between sexes. Ownership is separate.','regional':'Only Hisuian Sneasel has a reviewed separate regional gender image pair here; other regional forms are not inferred from species flags.'}}
    (ROOT/'reference/pokeapi/living-dex/gender-artwork-map.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    review['normalPairVisualReviewComplete']=True
    review['visualReviewScope']='101 base species normal Male/Female pairs inspected across five labeled sheets; source female and shiny captions checked. Subtle rear features and shiny colors are not certified by these normal-front sheets. Hisuian Sneasel pair needs separate visual review.'
    (ROOT/'audit/gender-artwork-review.json').write_text(json.dumps(review,indent=2)+'\n',encoding='utf-8')
    print('Finalized 206 gender ownership/artwork mappings for 102 base species and Hisuian Sneasel.')


if __name__=='__main__':main()
