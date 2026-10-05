// Local custom protocol renders the app inside Chromium without HTTP sockets.
const {app,BrowserWindow,protocol,net,ipcMain,dialog,shell,Menu}=require('electron');
const path=require('node:path');
const fs=require('node:fs');
const fsp=require('node:fs/promises');
const {pathToFileURL}=require('node:url');
const {CollectionStore,validate}=require('./storage.cjs');
const {Updates}=require('./updates.cjs');
const {autoUpdater}=require('electron-updater');
const origin='shiny://app';
protocol.registerSchemesAsPrivileged([{scheme:'shiny',privileges:{standard:true,secure:true,supportFetchAPI:true}}]);

// Keep this profile name stable across every installer and rollback.
const qa=process.env.SHINYDEX_DESKTOP_QA==='1';
const profile=qa?process.env.SHINYDEX_DESKTOP_QA_DIR:path.join(app.getPath('appData'),'ShinyDexDesktop');
if(!profile) throw Error('Missing test profile');
fs.mkdirSync(profile,{recursive:true});
app.setPath('userData',profile);
let window,store,updates;
if(!app.requestSingleInstanceLock()){app.quit();}
else{
  app.on('second-instance',()=>{if(window){if(window.isMinimized())window.restore();window.show();window.focus();}});
  app.whenReady().then(start).catch(error=>{dialog.showErrorBox('ShinyDex could not start',error.message);app.quit();});
}
app.on('window-all-closed',()=>app.quit());

function authorized(event) {
  if(!window||event.sender!==window.webContents||!event.senderFrame?.url.startsWith(origin+'/')) throw Error('Untrusted app frame');
}
async function start(){
  const root=app.getAppPath();
  const keys=JSON.parse(await fsp.readFile(path.join(root,'data.json'),'utf8')).map(p=>p.key);
  store=new CollectionStore(profile,keys);
  updates=new Updates({currentVersion:app.getVersion(),updater:autoUpdater,fetch:net.fetch.bind(net),store,packaged:app.isPackaged});
  protocol.handle('shiny',async request=>{
    const url=new URL(request.url);
    if(url.hostname!=='app'||request.method!=='GET')return new Response('Forbidden',{status:403});
    let pathname;
    try{pathname=decodeURIComponent(url.pathname);}catch{return new Response('Invalid path',{status:400});}
    const relative=pathname==='/'?'index.html':pathname.slice(1);
    const allowed=['index.html','main.js','style.css','updater.js','data.json','hunts.json','ATTRIBUTIONS.txt','THIRD_PARTY_NOTICES.md'].includes(relative)||/^assets\/pokemon\/[a-zA-Z0-9_.-]+\.png$/.test(relative);
    if(!allowed)return new Response('Forbidden',{status:403});
    try{
      const response=await net.fetch(pathToFileURL(path.join(root,relative)).href);
      const headers=new Headers(response.headers);
      headers.set('Cache-Control','no-store');
      headers.set('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'");
      return new Response(response.body,{status:response.status,headers});
    }catch{return new Response('Not found',{status:404});}
  });
  const handle=(channel,callback)=>ipcMain.handle(channel,(event,...args)=>{authorized(event);return callback(...args);});
  handle('collection:load',()=>store.load());
  handle('collection:save',record=>store.save(record));
  handle('collection:import',async()=>{
    const choice=await dialog.showOpenDialog(window,{title:'Import ShinyDex backup',properties:['openFile'],filters:[{name:'ShinyDex JSON backup',extensions:['json']}]});
    if(choice.canceled)return null;
    const file=choice.filePaths[0];
    if((await fsp.stat(file)).size>1000000)throw Error('Backup file is too large');
    const record=validate(JSON.parse(await fsp.readFile(file,'utf8')));
    await store.backup();await store.save(record);
    return record;
  });
  handle('updates:status',()=>updates.snapshot());
  handle('updates:check',()=>updates.check());
  handle('updates:install',tag=>updates.install(tag));
  window=new BrowserWindow({width:1280,height:900,minWidth:420,minHeight:600,title:'ShinyDex',backgroundColor:'#ad3946',show:false,webPreferences:{preload:path.join(__dirname,'preload.cjs'),nodeIntegration:false,contextIsolation:true,sandbox:true}});
  const external=url=>{
    try{const target=new URL(url);if(target.protocol==='https:'&&['bulbapedia.bulbagarden.net','archives.bulbagarden.net','pokeapi.co','github.com','www.serebii.net','luminescent.team','www.pokemon.com','home.pokemon.com','pokemongo.com','swordshield.pokemon.com','www.pokemon.co.jp'].includes(target.hostname))shell.openExternal(target.href);}catch{}
  };
  window.webContents.setWindowOpenHandler(({url})=>{external(url);return {action:'deny'};});
  window.webContents.on('will-navigate',(event,url)=>{if(!url.startsWith(origin+'/')){event.preventDefault();external(url);}});
  window.webContents.session.setPermissionRequestHandler((contents,permission,callback)=>callback(false));
  Menu.setApplicationMenu(Menu.buildFromTemplate([{label:'ShinyDex',submenu:[{label:'Quit',role:'quit'}]},{label:'View',submenu:[{role:'reload'},{role:'resetZoom'},{role:'zoomIn'},{role:'zoomOut'}]}]));
  window.once('ready-to-show',()=>window.show());
  await window.loadURL(origin+'/');
  if(qa)await require('./smoke.cjs').run({window,store,profile,app});
}
