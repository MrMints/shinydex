// Run real release renderer/storage code against one isolated fixture profile.
// Electron: <this file> <app.asar> <phase> <fixture directory> <report directory>
const fs=require('node:fs');
const fsp=require('node:fs/promises');
const path=require('node:path');
const assert=require('node:assert/strict');
const {app}=require('electron');
const [rootArg,phase,profileArg,reportsArg]=process.argv.slice(2);
const root=path.resolve(rootArg),profile=path.resolve(profileArg),reports=path.resolve(reportsArg);
const workspace=path.resolve(__dirname,'..');
assert.ok(profile.startsWith(path.join(workspace,'audit','artifacts')+path.sep),'QA profile must stay in audit/artifacts');
process.env.SHINYDEX_DESKTOP_QA='1';
process.env.SHINYDEX_DESKTOP_QA_DIR=profile;
app.setAppPath(root);
const sourceVersion=JSON.parse(fs.readFileSync(path.join(root,'package.json'),'utf8')).version;
const sourceCatalog=JSON.parse(fs.readFileSync(path.join(root,'data.json'),'utf8'));
const expectedNew=[1,300050,300051];
async function run({window,store}){
 const errors=[];
 window.webContents.on('console-message',event=>{if(event.level==='error')errors.push(event.message);});
 const evaluate=source=>window.webContents.executeJavaScript(source);
 const wait=async predicate=>{for(let i=0;i<200;i++){if(await evaluate(predicate))return;await new Promise(r=>setTimeout(r,100));}throw Error('Renderer timed out');};
 const click=selector=>evaluate(`document.querySelector(${JSON.stringify(selector)}).click()`);
 const load=async()=>{await window.loadURL('shiny://app/');await wait('!!document.querySelector("input[data-catch]") && !!document.querySelector("#update-open")');};
 const record=async()=>JSON.parse(await store.load());
 const waitSaved=async key=>{for(let i=0;i<200;i++){if((await record()).captured.includes(key))return;await new Promise(r=>setTimeout(r,100));}throw Error("Autosave timed out");};
 const choose=async(name,key)=>{
  await evaluate(`(()=>{const s=document.querySelector('#search');s.value=${JSON.stringify(name)};s.dispatchEvent(new Event('input',{bubbles:true}));const f=document.querySelector('.form-select');f.value=${JSON.stringify(String(key))};f.dispatchEvent(new Event('change',{bubbles:true}));})()`);
 };
 const exportRecord=async()=>{
  await evaluate("(()=>{const OriginalBlob=Blob;window.Blob=class extends OriginalBlob{constructor(parts,options){super(parts,options);window.qaExport=parts.join('');}};HTMLAnchorElement.prototype.click=function(){};})()");
  await click('#export');
  return JSON.parse(await evaluate('window.qaExport'));
 };
 try{
  await wait('!!document.querySelector("input[data-catch]") && !!document.querySelector("#update-open")');
  assert.equal(await evaluate('typeof require'),'undefined');
  const checks=[];
  if(phase==='old-seed'){
   assert.equal(sourceVersion,'1.0.0');assert.equal(await store.load(),null);
   await store.save({version:2,captured:[1,25,999999],shinies:[25,999999]});
   await load();
   assert.equal(await evaluate('document.querySelector(\'input[data-catch="25"][data-kind=shiny]\').checked'),true);
   checks.push('Original release loads legacy ownership; fixture includes a future ID');
  }else if(phase==='new-upgrade'){
   assert.ok(['1.1.0','1.1.1','1.1.2'].includes(sourceVersion));
   assert.deepEqual(await record(),{version:2,captured:[1,25,999999],shinies:[25,999999]});
   assert.equal(sourceCatalog.find(p=>p.key===25).formUnspecified,true);
   await choose('Pikachu',300050);
   await click('#assign-form');await wait("document.querySelector('#save').textContent.includes('Form assigned')");
   const backups=await fsp.readdir(path.join(profile,'backups'));assert.ok(backups.length>0);
   const backup=JSON.parse(await fsp.readFile(path.join(profile,'backups',backups[0]),'utf8'));
   assert.deepEqual(backup,{version:2,captured:[1,25,999999],shinies:[25,999999]});
   await choose('Pikachu',300051);await click('input[data-catch="300051"][data-kind=shiny]');
   await waitSaved(300051);
   const alcremie=sourceCatalog.find(p=>p.id===869&&!p.formUnspecified);
   await choose('Alcremie',alcremie.key);await click(`input[data-catch="${alcremie.key}"][data-kind=shiny]`);
   await waitSaved(alcremie.key);
   const expected={version:2,captured:[...expectedNew,alcremie.key,999999].sort((a,b)=>a-b),shinies:[300050,300051,alcremie.key,999999].sort((a,b)=>a-b)};
   assert.deepEqual(await record(),expected);
   await load();assert.deepEqual(await record(),expected);
   const portable=await exportRecord();assert.deepEqual(portable.captured,expected.captured);assert.deepEqual(portable.shinies,expected.shinies);
   await fsp.writeFile(path.join(reports,'new-expected.json'),JSON.stringify(expected,null,2));
   checks.push('Legacy capture not guessed; explicit form assignment backs up before moving shiny ownership','Male/female Pikachu and Alcremie persisted independently','New export retains all form and future IDs');
  }else if(phase==='old-downgrade'){
   assert.equal(sourceVersion,'1.0.0');
   const expected=JSON.parse(await fsp.readFile(path.join(reports,'new-expected.json'),'utf8'));
   assert.deepEqual(await record(),expected);
   await click('input[data-catch="2"][data-kind=captured]');
   await wait("document.querySelector('#save').textContent.includes('Saved')");
   expected.captured.push(2);expected.captured.sort((a,b)=>a-b);
   assert.deepEqual(await record(),expected);
   await load();assert.deepEqual(await record(),expected);
   const portable=await exportRecord();assert.deepEqual(portable.captured.sort((a,b)=>a-b),[1,2]);assert.deepEqual(portable.shinies,[]);
   await fsp.writeFile(path.join(reports,'return-expected.json'),JSON.stringify(expected,null,2));
   checks.push('Original release autosave and restart preserve unknown form IDs','Older export confirmed to omit unrecognized IDs; limitation recorded');
  }else if(phase==='new-return'){
   assert.ok(['1.1.0','1.1.1','1.1.2'].includes(sourceVersion));
   const expected=JSON.parse(await fsp.readFile(path.join(reports,'return-expected.json'),'utf8'));
   assert.deepEqual(await record(),expected);
   await choose('Pikachu',300050);assert.equal(await evaluate('document.querySelector(\'input[data-catch="300050"][data-kind=shiny]\').checked'),true);
   await choose('Pikachu',300051);assert.equal(await evaluate('document.querySelector(\'input[data-catch="300051"][data-kind=shiny]\').checked'),true);
   const portable=await exportRecord();assert.deepEqual(portable.captured,expected.captured);assert.deepEqual(portable.shinies,expected.shinies);
   await store.backup();await store.save(portable);await load();assert.deepEqual(await record(),expected);
   checks.push('Re-upgrade restores all new forms, shiny ownership and older-version edits','Portable current-version export re-imported through disk store without loss');
  }else throw Error('Unknown phase');
  assert.deepEqual(errors,[]);
  await fsp.writeFile(path.join(reports,`${phase}.json`),JSON.stringify({passed:true,phase,sourceVersion,sourceAsar:root,checks,collection:await record(),errors},null,2));
  app.exit(0);
 }catch(error){await fsp.writeFile(path.join(reports,`${phase}.json`),JSON.stringify({passed:false,phase,sourceVersion,error:error.stack,errors},null,2));app.exit(1);}
}
const smokePath=require.resolve(path.join(root,'desktop','smoke.cjs'));
require.cache[smokePath]={id:smokePath,filename:smokePath,loaded:true,exports:{run}};
require(path.join(root,'desktop','main.cjs'));
