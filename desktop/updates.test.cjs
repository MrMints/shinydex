const {test}=require('node:test');
const assert=require('node:assert/strict');
const {EventEmitter}=require('node:events');
const {Updates,releasesFrom,sha256}=require('./updates.cjs');
const fs=require('node:fs/promises');const os=require('node:os');const path=require('node:path');
test('release discovery rejects browser releases and untrusted manifests',()=>{
 const row={tag_name:'v1.0.1',assets:[{name:'ShinyDex.exe',browser_download_url:'https://github.com/MrMints/shinydex/releases/download/v1.0.1/ShinyDex.exe',digest:'sha256:'+'a'.repeat(64)},{name:'latest.yml',browser_download_url:'https://evil.invalid/latest.yml'}]};
 assert.equal(releasesFrom([row]).length,0);row.assets[1].browser_download_url='https://github.com/MrMints/shinydex/releases/download/v1.0.1/latest.yml';assert.equal(releasesFrom([row]).length,1);
 assert.equal(releasesFrom([{...row,tag_name:'v1.1.0-windows-preview'}]).length,0);
 const older={...row,tag_name:'v0.9.9',assets:row.assets.map(asset=>({...asset,browser_download_url:asset.browser_download_url.replace('v1.0.1','v0.9.9')}))};
 assert.equal(releasesFrom([older]).length,0);
});
test('offline discovery leaves installation usable',async()=>{
 const updates=new Updates({currentVersion:'1.0.0',updater:new EventEmitter(),fetch:async()=>{throw Error('offline');},store:{},packaged:true});
 assert.equal((await updates.check()).status,'error');assert.throws(()=>updates.install('v9.0.0'));
});
test('verified updates and rollback install; mismatches never install',async t=>{
 const dir=await fs.mkdtemp(path.join(os.tmpdir(),'shinydex-update-'));t.after(()=>fs.rm(dir,{recursive:true,force:true}));const file=path.join(dir,'installer');await fs.writeFile(file,'fixture');
 for(const mode of ['success','rollback','version','hash']){
  let installed=false,backed=false;const tag=mode==='rollback'?'v1.0.0':'v1.0.2';
  const updater=Object.assign(new EventEmitter(),{setFeedURL(feed){assert.ok(feed.url.endsWith(tag+'/'));},async checkForUpdates(){return {updateInfo:{version:mode==='version'?'9.0.0':tag.slice(1)}};},async downloadUpdate(){return [file];},quitAndInstall(){installed=true;}});
  const updates=new Updates({currentVersion:'1.0.1',updater,fetch:null,store:{async backup(){backed=true;}},packaged:true});updates.releases=[{tag,hash:mode==='hash'?'0'.repeat(64):await sha256(file)}];
  updates.install(tag);await updates.transaction;assert.ok(backed);assert.equal(installed,['success','rollback'].includes(mode));assert.equal(updates.status,installed?'restarting':'error');
 }
});

// Exercise the updater with the real disk store, including pending collection writes.
test('failed update transactions preserve collection and never launch installer', async t=>{
 const {CollectionStore}=require('./storage.cjs');
 const dir=await fs.mkdtemp(path.join(os.tmpdir(),'shinydex-update-save-'));
 t.after(()=>fs.rm(dir,{recursive:true,force:true}));
 for(const stage of ['backup','check','download','checksum']) {
  const store=new CollectionStore(path.join(dir,stage),[1,2]);
  await store.save({version:2,captured:[1],shinies:[1]});
  const pending=store.save({version:2,captured:[1,2],shinies:[2]});
  let installed=false,checked=false;
  const updater=Object.assign(new EventEmitter(),{
   setFeedURL(){},
   async checkForUpdates(){checked=true;if(stage==='check')throw Error('offline');return {updateInfo:{version:'1.0.2'}};},
   async downloadUpdate(){if(stage==='download')throw Error('interrupted');const file=path.join(dir,'invalid-installer');await fs.writeFile(file,'invalid');return [file];},
   quitAndInstall(){installed=true;}
  });
  const updateStore=stage==='backup'?{async backup(){throw Error('disk full');}}:store;
  const updates=new Updates({currentVersion:'1.0.1',updater,fetch:null,store:updateStore,packaged:true});
  updates.releases=[{tag:'v1.0.2',hash:'0'.repeat(64)}];
  updates.install('v1.0.2');
  assert.throws(()=>updates.install('v1.0.2'),'concurrent install is blocked');
  await Promise.all([pending,updates.transaction]);
  assert.equal(installed,false);assert.equal(updates.status,'error');
  assert.equal(checked,stage!=='backup');
  const expected={version:2,captured:[1,2],shinies:[2]};
  assert.deepEqual(JSON.parse(await store.load()),expected);
  if(stage!=='backup') {
   const backups=await fs.readdir(path.join(store.directory,'backups'));
   assert.equal(backups.length,1);
   assert.deepEqual(JSON.parse(await fs.readFile(path.join(store.directory,'backups',backups[0]),'utf8')),expected);
  }
 }
});
