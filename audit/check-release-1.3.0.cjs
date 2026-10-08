const fs = require('node:fs');
const crypto = require('node:crypto');
const assert = require('node:assert/strict');
const { createRequire } = require('node:module');
const { execFileSync } = require('node:child_process');
const asar = createRequire(require.resolve('electron-builder'))('@electron/asar');
process.chdir(require('node:path').resolve(__dirname, '..'));
const hash = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const qa = 'audit/artifacts/release-1.3.0';
const archive = 'dist/release-1.3.0/win-unpacked/resources/app.asar';
const output = 'dist/release-1.3.0/';
const metadata = JSON.parse(asar.extractFile(archive, 'package.json'));
assert.equal(metadata.version, '1.3.0');
for (const file of ['main.js','index.html','style.css','updater.js','collection-codec.js','pokedex.js','pokedex-entries.json','data.json','hunts.json','desktop/main.cjs','desktop/preload.cjs','desktop/storage.cjs','desktop/updates.cjs','desktop/smoke.cjs','ATTRIBUTIONS.txt','THIRD_PARTY_NOTICES.md']) {
  assert.equal(hash(asar.extractFile(archive, file)), hash(fs.readFileSync(file)), file);
}
assert(!asar.listPackage(archive).some(file => /[/\\](audit|Archive|windows)[/\\]|collection-v2\.json$|\.csv$|build-pokedex|collect-pokedex|bulbapedia-pokedex/.test(file)));
// Existing save/schema evidence remains applicable only if its inputs are unchanged.
for (const file of ['desktop/storage.cjs','collection-codec.js','data.json','hunts.json']) {
  assert.equal(hash(fs.readFileSync(file)), hash(execFileSync('git',['show',`HEAD:${file}`],{maxBuffer:128*1024*1024})), `${file} unchanged from 1.2.0`);
}
const installer = fs.readFileSync(output+'ShinyDex.exe');
const manifest = fs.readFileSync(output+'latest.yml','utf8');
assert.match(manifest, /^version: 1\.3\.0\r?$/m);
assert.equal(manifest.match(/^sha512: (.+)$/m)[1].trim(), crypto.createHash('sha512').update(installer).digest('base64'));
assert.equal(Number(manifest.match(/^    size: (\d+)/m)[1]), installer.length);
fs.writeFileSync(output+'ShinyDex.exe.sha256', hash(installer)+'  ShinyDex.exe\n');
const smoke = JSON.parse(fs.readFileSync(qa+'/profile-smoke/smoke.json'));
assert.equal(smoke.passed,true); assert.equal(smoke.packaged,true); assert.equal(smoke.version,'1.3.0'); assert.deepEqual(smoke.errors,[]);
fs.copyFileSync(qa+'/profile-smoke/smoke.json', qa+'/smoke.json');
for (const file of fs.readdirSync(qa+'/profile-smoke').filter(file=>file.endsWith('.png'))) fs.copyFileSync(qa+'/profile-smoke/'+file,qa+'/'+file);
const project = JSON.parse(fs.readFileSync('audit/project-checks.json')); assert.equal(project.passed,true);
assert.deepEqual(metadata.dependencies, {'electron-updater':'6.8.9'});
const source = JSON.parse(fs.readFileSync('package.json'));
assert.deepEqual(source.devDependencies, {'electron':'44.5.1','electron-builder':'26.15.3'});
const assets = ['ShinyDex.exe','latest.yml','ShinyDex.exe.blockmap','ShinyDex.exe.sha256'].map(name=>({name,bytes:fs.statSync(output+name).size,sha256:hash(fs.readFileSync(output+name))}));
assert(assets.every(a=>a.bytes>0));
const report = {version:'1.3.0',checked:'2026-10-07',uploadApproved:true,published:false,auditComplete:false,
 changes:['Game-specific offline Pokédex descriptions above hunting methods','Remembered session game selection and optional all-game hunting','Explicit form labels, source links, missing-data messages and load retry'],
 verification:{desktopTests:'6/6 passed with test isolation disabled',projectChecks:`${project.checkCount}/${project.checkCount} passed`,packagedSmoke:smoke,windowsBuild:'Windows x64 NSIS build passed',packagedSourceMatch:true,sha512Matches:true,saveSchemaCatalogAndHuntsUnchanged:true,dependencyPinsUnchanged:true,lockfile:'pnpm-lock.yaml has no application version field; dependency pins unchanged',rendererEvidence:'audit/pokedex-ui-qa.json'},
 package:{outputDirectory:'dist/release-1.3.0',asarSha256:hash(fs.readFileSync(archive)),assets},
 limitations:['Real NSIS installation/update/restart cycle unverified','Every localization/spin-off/cartridge entry is not independently verified','Exhaustive hunting and attribution audit remains incomplete']};
fs.writeFileSync('audit/release-1.3.0-ready.json',JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({ready:true,version:'1.3.0',installerSha256:assets[0].sha256}));
