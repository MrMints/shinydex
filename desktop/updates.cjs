// Public releases plus immutable per-release NSIS update manifests.
const crypto = require('node:crypto');
const fs = require('node:fs');
const {pipeline} = require('node:stream/promises');
const {Writable} = require('node:stream');

const repository = 'https://api.github.com/repos/MrMints/shinydex';
function version(tag) {
  const match = /^v?(\d+)\.(\d+)\.(\d+)$/.exec(tag || '');
  return match ? match.slice(1).map(Number) : null;
}
function compare(a,b) {
  const x=version(a),y=version(b);
  if(!x||!y) return 0;
  for(let i=0;i<3;i++) if(x[i]!==y[i]) return x[i]-y[i];
  return 0;
}
function releasesFrom(rows) {
  return rows.flatMap(row=>{
    const number=version(row.tag_name);
    if(row.draft||row.prerelease||!/^v\d+\.\d+\.\d+$/.test(row.tag_name||'')||!number||compare(row.tag_name,'v1.0.0')<0) return [];
    const expected=`https://github.com/MrMints/shinydex/releases/download/${row.tag_name}/ShinyDex.exe`;
    const asset=(row.assets||[]).find(item=>item.name==='ShinyDex.exe'&&item.browser_download_url===expected&&/^sha256:[a-f0-9]{64}$/.test(item.digest||''));
    const manifest=(row.assets||[]).find(item=>item.name==='latest.yml'&&item.browser_download_url===`https://github.com/MrMints/shinydex/releases/download/${row.tag_name}/latest.yml`);
    if(!asset||!manifest) return [];
    return [{tag:row.tag_name,name:row.name||row.tag_name,size:asset.size,hash:asset.digest.slice(7)}];
  }).sort((a,b)=>compare(b.tag,a.tag));
}
async function sha256(file) {
  const hash=crypto.createHash('sha256');
  await pipeline(fs.createReadStream(file),new Writable({write(chunk,encoding,done){hash.update(chunk);done();}}));
  return hash.digest('hex');
}
class Updates {
  constructor({currentVersion,updater,fetch,store,packaged}) {
    this.currentVersion='v'+currentVersion;
    this.updater=updater;this.fetch=fetch;this.store=store;this.packaged=packaged;
    this.releases=[];this.latestVersion=null;this.status='idle';this.progress=0;this.error=null;
    updater.autoDownload=false;updater.autoInstallOnAppQuit=false;
    updater.allowDowngrade=true;
    updater.on('download-progress',event=>{this.progress=Math.round(event.percent);});
    updater.on('error',()=>{}); // Errors are reported through the explicit transaction below.
  }
  snapshot(){ return {currentVersion:this.currentVersion,latestVersion:this.latestVersion,updateAvailable:compare(this.latestVersion,this.currentVersion)>0,releases:this.releases.map(({hash,...release})=>release),status:this.status,progress:this.progress,error:this.error}; }
  async check() {
    if(['checking','downloading','restarting'].includes(this.status)) return this.snapshot();
    this.status='checking';this.error=null;
    try {
      const get=async url=>{
        const response=await this.fetch(url,{headers:{'User-Agent':'ShinyDex-Desktop','Accept':'application/vnd.github+json'},signal:AbortSignal.timeout(30000)});
        if(!response.ok) throw Error('Release service unavailable');
        return response.json();
      };
      const latest=await get(repository+'/releases/latest');
      const rows=[];
      for(let page=1;page<=10;page++) {
        const batch=await get(repository+`/releases?per_page=100&page=${page}`);
        if(!Array.isArray(batch)) throw Error('Invalid release list');
        rows.push(...batch);if(batch.length<100) break;
      }
      this.releases=releasesFrom(rows);
      this.latestVersion=this.releases.some(item=>item.tag===latest.tag_name)?latest.tag_name:null;
      this.status='ready';
    }catch{this.status='error';this.error='Could not check for updates. The installed app still works; try again later.';}
    return this.snapshot();
  }
  install(tag) {
    const release=this.releases.find(item=>item.tag===tag);
    if(!this.packaged) throw Error('Updates are installed from the packaged desktop app.');
    if(!release||tag===this.currentVersion||['checking','downloading','restarting'].includes(this.status)) throw Error('Choose another available desktop version.');
    this.status='downloading';this.progress=0;this.error=null;
    this.transaction=this.apply(release);
    return this.snapshot();
  }
  async apply(release) {
    try {
      await this.store.backup();
      this.updater.setFeedURL({provider:'generic',url:`https://github.com/MrMints/shinydex/releases/download/${release.tag}/`});
      const result=await this.updater.checkForUpdates();
      if(!result||result.updateInfo.version!==release.tag.slice(1)) throw Error('Release version mismatch');
      const files=await this.updater.downloadUpdate();
      if(!files?.length||await sha256(files[0])!==release.hash) throw Error('Release checksum mismatch');
      this.progress=100;this.status='restarting';
      this.updater.quitAndInstall(true,true);
    }catch{this.status='error';this.progress=0;this.error='The update could not be installed or verified. The current app and saved collection are unchanged.';}
  }
}
module.exports={Updates,version,compare,releasesFrom,sha256};
