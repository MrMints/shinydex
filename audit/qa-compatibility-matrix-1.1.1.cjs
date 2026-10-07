const fs=require('node:fs/promises'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const {createRequire}=require('node:module');
const asar=createRequire(require.resolve('electron-builder'))('@electron/asar');
const root=path.resolve(__dirname,'..'),qa=path.join(root,'audit/artifacts/release-1.1.1-compatibility');
const sources={'1.0.0':path.join(root,'audit/artifacts/release-1.1.0/previous-runtime/app.asar'),'1.1.0':path.join(qa,'payload/resources/app.asar'),'1.1.1':path.join(root,'dist/desktop/win-unpacked/resources/app.asar')};
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
(async()=>{
 const stores={},keys={},hashes={};
 for(const [version,file] of Object.entries(sources)){
  assert.equal(JSON.parse(asar.extractFile(file,'package.json')).version,version);
  if(version==='1.1.0')assert.equal(hash(await fs.readFile(file)),JSON.parse(await fs.readFile(path.join(root,'audit/release-1.1.0-ready.json'))).package.asarSha256);
  hashes[version]=hash(await fs.readFile(file));
  keys[version]=JSON.parse(asar.extractFile(file,'data.json')).map(p=>p.key);
  const moduleFile=path.join(qa,`storage-${version}.cjs`);await fs.writeFile(moduleFile,asar.extractFile(file,'desktop/storage.cjs'));
  stores[version]=require(moduleFile).CollectionStore;
 }
 assert.deepEqual(keys['1.1.0'],keys['1.1.1']);
 const results=[];
 for(const from of Object.keys(stores))for(const to of Object.keys(stores)){
  if(from===to)continue;
  const profile=await fs.mkdtemp(path.join(qa,'profile-matrix-'));
  const a=new stores[from](profile,keys[from]),b=new stores[to](profile,keys[to]);
  const initial={version:2,captured:[...keys[from],999999].sort((a,b)=>a-b),shinies:[...keys[from].filter((_,i)=>i%2===0),999999].sort((a,b)=>a-b)};
  await a.save(initial);assert.deepEqual(JSON.parse(await b.load()),initial);
  const edited={version:2,captured:initial.captured.filter(id=>keys[to].includes(id)&&id!==1),shinies:initial.shinies.filter(id=>keys[to].includes(id)&&id!==1)};
  const expected={version:2,captured:initial.captured.filter(id=>id!==1),shinies:initial.shinies.filter(id=>id!==1)};
  await b.save(edited);
  assert.deepEqual(JSON.parse(await a.load()),expected);
  const restarted=new stores[to](profile,keys[to]);assert.deepEqual(JSON.parse(await restarted.load()),expected);
  const backup=await restarted.backup();assert.deepEqual(JSON.parse(await fs.readFile(backup)),expected);
  const imported=new stores[from](await fs.mkdtemp(path.join(qa,'profile-import-')),keys[from]);
  await imported.save(JSON.parse(await fs.readFile(backup)));assert.deepEqual(JSON.parse(await imported.load()),expected);
  results.push({from,to,passed:true,sourceKeys:keys[from].length,unknownIdsPreserved:initial.captured.filter(id=>!keys[to].includes(id)).length,checks:['load','autosave edit','fresh store reload','backup','restore backup on source version']});
 }
 const report={checked:'2026-10-07',passed:true,scope:'Actual packaged storage modules; all six directed version pairs with all catalog IDs plus unknown future ID',catalogCounts:Object.fromEntries(Object.entries(keys).map(([v,k])=>[v,k.length])),asarSha256:hashes,results,limitations:['Isolated collection stores; actual NSIS install/update cycle not exercised']};
 await fs.writeFile(path.join(qa,'matrix.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
})().catch(e=>{console.error(e);process.exitCode=1;});
