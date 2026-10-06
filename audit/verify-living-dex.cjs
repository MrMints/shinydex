// Integration coverage grows with reviewed form families; passing is not full coverage.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const root=path.resolve(__dirname,'..');
async function main(){
 const data=JSON.parse(fs.readFileSync(path.join(root,'data.json')));
 const definitions=JSON.parse(fs.readFileSync(path.join(root,'reference/pokeapi/living-dex/alcremie-artwork-map.json'))).forms;
 const keys=new Set(data.map(p=>p.key));
 const excluded=new Set(JSON.parse(fs.readFileSync(path.join(root,'reference/pokeapi/living-dex/home-storage-scope.json'))).excludedIdentities);
 for(const identity of excluded)assert.ok(!data.some(p=>p.name===identity),`HOME excludes ${identity}`);
 assert.equal(keys.size,data.length);
 assert.equal(data.filter(p=>!p.livingForm).length,1083,'Preserve all legacy records');
 const forms=data.filter(p=>p.livingForm&&p.id===869);
 assert.equal(forms.length,63);
 const persistentDefinitions=JSON.parse(fs.readFileSync(path.join(root,'reference/pokeapi/living-dex/persistent-artwork-map.json'))).forms;
 assert.equal(persistentDefinitions.length,91);
 const alternateDefinitions=JSON.parse(fs.readFileSync(path.join(root,'reference/pokeapi/living-dex/alternate-artwork-map.json'))).forms;
 assert.equal(alternateDefinitions.length,55);
 const typeDefinitions=JSON.parse(fs.readFileSync(path.join(root,'reference/pokeapi/living-dex/type-artwork-map.json'))).forms;
 assert.equal(typeDefinitions.length,58);
 const latentDefinitions=JSON.parse(fs.readFileSync(path.join(root,'reference/pokeapi/living-dex/latent-artwork-map.json'))).forms;
 assert.equal(latentDefinitions.length,47);
 assert.equal(latentDefinitions.filter(p=>p.speciesId===414).length,3);
 const capDefinitions=JSON.parse(fs.readFileSync(path.join(root,'reference/pokeapi/living-dex/cap-artwork-map.json'))).forms;
 assert.equal(capDefinitions.length,8);
 const technicalDefinitions=JSON.parse(fs.readFileSync(path.join(root,'reference/pokeapi/living-dex/technical-artwork-map.json'))).forms;
 assert.equal(technicalDefinitions.length,24);
 const specialDefinitions=JSON.parse(fs.readFileSync(path.join(root,'reference/pokeapi/living-dex/special-artwork-map.json'))).forms;
 assert.equal(specialDefinitions.length,8);
 assert.ok(!data.some(p=>p.name==='pichu-spiky-eared'),'Exclude Spiky-eared Pichu from the living dex');
 for(const p of specialDefinitions){
  if(excluded.has(p.identity))continue;
  const record=data.find(f=>f.key===p.key);
  if(p.identity!=='pichu')assert.equal(record.shinyArtworkAvailable,false);
  if(p.speciesId===25){assert.equal(record.shinyLocked,true);assert.equal(record.gender,'Female');}
 }
 assert.equal(technicalDefinitions.filter(p=>p.identity.includes('totem')).length,11);
 for(const p of capDefinitions){
  assert.equal(data.find(f=>f.key===p.key).shinyArtworkAvailable,false);
  assert.equal(p.normalFile,p.shinyFile);
 }
 for(const sid of [658,744]){
  const abilities=latentDefinitions.filter(p=>p.speciesId===sid);
  assert.equal(abilities.length,2);
  assert.equal(new Set(abilities.map(p=>p.key)).size,2);
  assert.equal(new Set(abilities.map(p=>p.normalFile)).size,1);
 }
 for(const sid of [664,665]){
  const patterns=latentDefinitions.filter(p=>p.speciesId===sid);
  assert.equal(patterns.length,20);
  assert.equal(new Set(patterns.map(p=>p.formLabel)).size,20);
  assert.equal(new Set(patterns.map(p=>p.normalFile)).size,1);
 }
 for(const definition of [...persistentDefinitions,...alternateDefinitions,...typeDefinitions,...latentDefinitions,...capDefinitions,...technicalDefinitions,...specialDefinitions]){
  if(excluded.has(definition.identity))continue;
  const p=data.find(p=>p.key===definition.key);
  assert.equal(p.name,definition.identity);
  assert.equal(p.formLabel,definition.formLabel);
  assert.equal(p.legacyKey,definition.legacyKey);
  assert.deepEqual(p.types,definition.types);
  assert.equal(p.height,definition.height);
  assert.equal(p.weight,definition.weight);
  for(const mode of ['normal','shiny']){
   assert.equal(p[mode+'File'],definition[mode+'File']);
   assert.equal(p[mode+'Source'],definition[mode+'Source']);
   assert.ok(fs.existsSync(path.resolve(root,p[mode])));
  }
 }
 assert.deepEqual(data.find(p=>p.name==='rotom-wash').types,['electric','water']);
 assert.equal(persistentDefinitions.filter(p=>p.speciesId===666).length,20);
 assert.deepEqual(data.find(p=>p.name==='urshifu-rapid-strike').types,['fighting','water']);
 const minior=alternateDefinitions.filter(p=>p.speciesId===774);
 assert.equal(minior.length,7);
 assert.equal(new Set(minior.map(p=>p.normalFile)).size,7);
 assert.equal(new Set(minior.map(p=>p.shinyFile)).size,1);
 for(const sid of [493,773]){
  const typeForms=typeDefinitions.filter(p=>p.speciesId===sid);
  assert.equal(typeForms.length,18);
  assert.equal(new Set(typeForms.map(p=>p.types[0])).size,18);
  for(const p of typeForms)assert.equal(p.types[0],p.identity.split('-').pop());
 }
 const unownDefinitions=JSON.parse(fs.readFileSync(path.join(root,'reference/pokeapi/living-dex/unown-artwork-map.json'))).forms;
 assert.equal(unownDefinitions.length,28);
 assert.deepEqual(new Set(unownDefinitions.map(p=>p.formLabel)),new Set([...'ABCDEFGHIJKLMNOPQRSTUVWXYZ','!','?']));
 for(const definition of unownDefinitions){
  const p=data.find(p=>p.key===definition.key);
  assert.equal(p.formLabel,definition.formLabel);
  assert.equal(p.legacyKey,201);
  for(const mode of ['normal','shiny'])assert.equal(p[mode+'File'],definition[mode+'File']);
 }
 const genderDefinitions=JSON.parse(fs.readFileSync(path.join(root,'reference/pokeapi/living-dex/gender-artwork-map.json'))).forms;
 assert.equal(genderDefinitions.length,206);
 for(const definition of genderDefinitions){
  const p=data.find(p=>p.key===definition.key);
  assert.equal(p.gender,definition.gender);
  assert.equal(p.legacyKey,definition.legacyKey);
  assert.ok(data.find(p=>p.key===definition.legacyKey).formUnspecified);
  for(const mode of ['normal','shiny']){
   assert.equal(p[mode+'File'],definition[mode+'File']);
   assert.ok(fs.existsSync(path.resolve(root,p[mode])));
  }
 }
 assert.ok(data.find(p=>p.key===869).formUnspecified,'Generic saves must not imply a cream/sweet');
 let slot=0;
 for(const [index,p] of data.entries()){
  if(p.formUnspecified)assert.equal(p.position,null);
  else assert.equal(p.position,slot++);
  if(index)assert.ok(p.id>=data[index-1].id);
 }
 for(const definition of definitions){
  const p=forms.find(p=>p.key===definition.key);
  assert.equal(p.name,definition.identity);
  for(const mode of ['normal','shiny']){
   assert.equal(p[mode+'File'],definition[mode+'File']);
   assert.ok(fs.existsSync(path.resolve(root,p[mode])));
   assert.equal(p[mode+'Source'],definition[mode+'Source']);
  }
 }
 const {decodeCollection,encodeCollection}=await import('../collection-codec.js');
 const state=decodeCollection({version:2,captured:[869],shinies:[869]},keys);
 state.captured.add(forms[0].key);
 state.shinies.add(forms[1].key);
 const restored=decodeCollection(encodeCollection(state),keys);
 assert.ok(restored.captured.has(869));
 assert.ok(restored.captured.has(forms[0].key));
 assert.ok(!restored.shinies.has(forms[0].key));
 assert.ok(restored.captured.has(forms[1].key));
 assert.ok(restored.shinies.has(forms[1].key));
 assert.ok(!restored.captured.has(forms[2].key));
 const pikachu=decodeCollection({version:2,captured:[25,300050],shinies:[300051]},keys);
 assert.ok(pikachu.captured.has(25));
 assert.ok(pikachu.captured.has(300050)&&!pikachu.shinies.has(300050));
 assert.ok(pikachu.captured.has(300051)&&pikachu.shinies.has(300051));
 console.log(`Verified ${data.length} catalog records, concrete HOME positions, preserved legacy IDs and independent ownership across the reviewed form manifests. Candidate scope review remains incomplete.`);
}
main().catch(error=>{console.error(error);process.exitCode=1;});
