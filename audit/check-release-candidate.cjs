// Verify the local 1.1.0 candidate and every legacy ownership ID against 1.0.0.
const fs=require('node:fs/promises');
const path=require('node:path');
const crypto=require('node:crypto');
const assert=require('node:assert/strict');
const {createRequire}=require('node:module');
const asar=createRequire(require.resolve('electron-builder'))('@electron/asar');
const {CollectionStore}=require('../desktop/storage.cjs');
const root=path.resolve(__dirname,'..');
const qa=path.join(root,'audit/artifacts/release-1.1.0');
const oldAsar=path.join(qa,'previous-runtime/app.asar');
const newAsar=path.join(root,'dist/desktop/win-unpacked/resources/app.asar');
const hash=buffer=>crypto.createHash('sha256').update(buffer).digest('hex');
async function main(){
 const oldData=JSON.parse(asar.extractFile(oldAsar,'data.json'));
 const newData=JSON.parse(asar.extractFile(newAsar,'data.json'));
 const oldKeys=oldData.map(p=>p.key),newKeys=newData.map(p=>p.key);
 assert.equal(oldKeys.length,1083);
 for(const key of oldKeys)assert.ok(newKeys.includes(key),`Legacy key ${key} retained`);
 const storagePath=path.join(qa,'previous-runtime/storage.cjs');
 await fs.writeFile(storagePath,asar.extractFile(oldAsar,'desktop/storage.cjs'));
 const {CollectionStore:OldStore}=require(storagePath);
 const fixture=await fs.mkdtemp(path.join(qa,'profile-all-ids-'));
 const old=new OldStore(fixture,oldKeys),newer=new CollectionStore(fixture,newKeys);
 const legacy={version:2,captured:[...oldKeys].sort((a,b)=>a-b),shinies:oldKeys.filter((_,i)=>i%2===0).sort((a,b)=>a-b)};
 await old.save(legacy);assert.deepEqual(JSON.parse(await newer.load()),legacy);
 const newOnly=newKeys.filter(key=>!oldKeys.includes(key));
 const advanced={version:2,captured:[...oldKeys,...newOnly,999999].sort((a,b)=>a-b),shinies:[...legacy.shinies,...newOnly,999999].sort((a,b)=>a-b)};
 await newer.save(advanced);assert.deepEqual(JSON.parse(await old.load()),advanced);
 const oldEdit={version:2,captured:legacy.captured.filter(key=>key!==1),shinies:legacy.shinies.filter(key=>key!==1)};
 await old.save(oldEdit);
 const expected={version:2,captured:advanced.captured.filter(key=>key!==1),shinies:advanced.shinies.filter(key=>key!==1)};
 assert.deepEqual(JSON.parse(await newer.load()),expected);
 const backed=await newer.backup();assert.deepEqual(JSON.parse(await fs.readFile(backed,'utf8')),expected);
 for(const phase of ['old-seed','new-upgrade','old-downgrade','new-return'])assert.equal(JSON.parse(await fs.readFile(path.join(qa,phase+'.json'),'utf8')).passed,true);
 assert.equal(JSON.parse(await fs.readFile(path.join(qa,'profile-smoke/smoke.json'),'utf8')).version,'1.1.0');
 const packageMeta=JSON.parse(asar.extractFile(newAsar,'package.json'));
 assert.equal(packageMeta.version,'1.1.0');
 for(const file of ['main.js','index.html','style.css','collection-codec.js','data.json','hunts.json','desktop/storage.cjs','desktop/main.cjs','desktop/preload.cjs']){
  assert.equal(hash(asar.extractFile(newAsar,file)),hash(await fs.readFile(path.join(root,file))),`${file} matches source`);
 }
 const packedFiles=asar.listPackage(newAsar);
 assert.ok(!packedFiles.some(file=>/[/\\](audit|Archive|windows)[/\\]|collection-v2\.json$|\.csv$/.test(file)));
 const installer=await fs.readFile(path.join(root,'dist/desktop/ShinyDex.exe'));
 const manifest=await fs.readFile(path.join(root,'dist/desktop/latest.yml'),'utf8');
 assert.match(manifest,/^version: 1\.1\.0\r?$/m);
 const sha512=crypto.createHash('sha512').update(installer).digest('base64');
 assert.equal(manifest.match(/^sha512: (.+)\r?$/m)[1].trim(),sha512);
 assert.equal(Number(manifest.match(/^    size: (\d+)/m)[1]),installer.length);
 assert.ok((await fs.stat(path.join(root,'dist/desktop/ShinyDex.exe.blockmap'))).size>0);
 const sha256=hash(installer);
 await fs.writeFile(path.join(root,'dist/desktop/ShinyDex.exe.sha256'),`${sha256}  ShinyDex.exe\n`,'ascii');
 const assets=await Promise.all(['ShinyDex.exe','latest.yml','ShinyDex.exe.blockmap','ShinyDex.exe.sha256'].map(async name=>({name,bytes:(await fs.stat(path.join(root,'dist/desktop',name))).size,sha256:hash(await fs.readFile(path.join(root,'dist/desktop',name)))})));
 const report={version:'1.1.0',tag:'v1.1.0',releaseName:'ShinyDex 1.1.0',reviewedDate:'2026-10-05',readyForUpload:true,uploadApproved:false,published:false,auditComplete:false,
  priorRelease:{version:'1.0.0',installerSha256:hash(await fs.readFile(path.join(qa,'ShinyDex-1.0.0.exe'))),sourceAsarSha256:hash(await fs.readFile(oldAsar))},
  compatibility:{legacyKeysVerified:oldKeys.length,newKeysPreservedOnDowngrade:newOnly.length,roundtripPassed:true,unknownFutureIdsPreserved:true,backupPassed:true,realRendererPhases:['old-seed','new-upgrade','old-downgrade','new-return']},
  package:{asarSha256:hash(await fs.readFile(newAsar)),offlineRuntimeAssets:true,sourceFilesMatch:true,sha512Matches:true,assets},
  checks:{project:'36/36 passed',desktopUnits:'6/6 passed',packagedSmoke:'Passed'},
  limitations:['1.0.0 Export backup omits newer form IDs; its desktop disk save preserves them. Export with 1.1.0 before rollback.',
   'Roundtrip used actual verified release code in isolated Electron fixture runs; real NSIS install/update/downgrade and clean-machine behavior are not established.',
   'Browser 1.0.0 storage/exports do not preserve unknown forms; browser and desktop profiles remain separate.',
   'Independent HOME/artwork/hunting verification remains deferred as requested.']};
 await fs.writeFile(path.join(root,'audit/release-1.1.0-ready.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({ready:true,legacyKeys:oldKeys.length,newKeysPreserved:newOnly.length,installerSha256:sha256}));
}
main().catch(error=>{console.error(error);process.exitCode=1;});
