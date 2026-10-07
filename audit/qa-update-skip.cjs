const {app,BrowserWindow}=require('electron');
const fs=require('node:fs/promises');
const path=require('node:path');
const assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const profile=path.join(root,'audit/artifacts/update-skip-qa');
app.setPath('userData',profile);
app.whenReady().then(async()=>{
 const win=new BrowserWindow({width:700,height:650,show:true,webPreferences:{sandbox:true,contextIsolation:true,nodeIntegration:false}});
 const js=async s=>{try{return await win.webContents.executeJavaScript(s);}catch(e){throw Error(s.slice(0,180)+": "+e.message);}};
 const wait=async s=>{for(let i=0;i<100;i++){if(await js(s))return;await new Promise(r=>setTimeout(r,100));}throw Error('Timed out: '+s);};
 const source=await fs.readFile(path.join(root,'updater.js'),'utf8');
 async function load(tag,clear=false){
  await win.loadFile(path.join(root,'audit/artifacts/update-skip-fixture.html'));
  await js(`document.body.innerHTML='<div class="header-right"></div>';${clear?'localStorage.clear();':''}window.fixture={currentVersion:'v1.1.1',latestVersion:${JSON.stringify(tag)},updateAvailable:true,releases:[{tag:'v1.1.1'},{tag:${JSON.stringify(tag)}}],status:'available',progress:0};window.shinydexDesktop={updateStatus:async()=>fixture,checkUpdates:async()=>fixture};void 0;`);
  await js(source+";void 0;"); await wait('!!document.querySelector("#update-open")');
 }
 try{
  await load('v1.1.2',true);
  assert.equal(await js('document.querySelector("#update-dialog").open'),true);
  await js('document.querySelector("#update-later").click()');
  await load('v1.1.2');
  assert.equal(await js('document.querySelector("#update-dialog").open'),true);
  await js('document.querySelector("#update-skip").click()');
  await new Promise(r=>setTimeout(r,500));
  try { await fs.writeFile(path.join(profile,'skip-dialog.png'),(await win.webContents.capturePage()).toPNG()); } catch(e) { console.log('Screenshot unavailable: '+e.message); }
  await js('document.querySelector("#update-later").click()');
  assert.equal(await js('document.querySelector("#update-open").textContent'),'Update');
  await load('v1.1.2');
  assert.equal(await js('document.querySelector("#update-dialog").open'),false);
  await js('document.querySelector("#update-open").click()');
  assert.equal(await js('document.querySelector("#update-dialog").open'),true);
  assert.equal(await js('document.querySelector("#update-skip").checked'),true);
  await js('document.querySelector("#update-skip").click();document.querySelector("#update-later").click()');
  await load('v1.1.2');
  assert.equal(await js('document.querySelector("#update-dialog").open'),true);
  await js('document.querySelector("#update-skip").click();document.querySelector("#update-later").click()');
  await load('v1.1.3');
  assert.equal(await js('document.querySelector("#update-dialog").open'),true);
  assert.equal(await js('document.querySelector("#update-open").textContent'),'Update Available');
  assert.equal(await js('document.querySelector("#update-skip").checked'),false);
  await fs.writeFile(path.join(profile,'result.json'),JSON.stringify({passed:true,scope:'Real Electron renderer with controlled release bridge: Later without skip, persisted skip across reload, manual reopen, unskip, different version prompt and button',version:'1.1.1'},null,2));
  app.exit(0);
 }catch(e){console.error(e);app.exit(1);}
});





