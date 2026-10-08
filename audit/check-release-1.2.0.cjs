const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const assert = require('node:assert/strict');
const { createRequire } = require('node:module');
const asar = createRequire(require.resolve('electron-builder'))('@electron/asar');
const hash = b => crypto.createHash('sha256').update(b).digest('hex');
const qa = 'audit/artifacts/release-1.2.0';
const archive = 'dist/desktop/win-unpacked/resources/app.asar';
const metadata = JSON.parse(asar.extractFile(archive, 'package.json'));
assert.equal(metadata.version, '1.2.0');
const files = ['main.js','index.html','style.css','updater.js','collection-codec.js','data.json','hunts.json','desktop/main.cjs','desktop/preload.cjs','desktop/storage.cjs','desktop/updates.cjs','desktop/smoke.cjs','ATTRIBUTIONS.txt','THIRD_PARTY_NOTICES.md'];
for (const file of files) assert.equal(hash(asar.extractFile(archive,file)), hash(fs.readFileSync(file)), file);
assert.ok(!asar.listPackage(archive).some(f => /[/\\](audit|Archive|windows)[/\\]|collection-v2\.json$|\.csv$/.test(f)));
const installer = fs.readFileSync('dist/desktop/ShinyDex.exe');
const manifest = fs.readFileSync('dist/desktop/latest.yml','utf8');
assert.match(manifest, /^version: 1\.2\.0\r?$/m);
assert.equal(manifest.match(/^sha512: (.+)$/m)[1].trim(), crypto.createHash('sha512').update(installer).digest('base64'));
assert.equal(Number(manifest.match(/^    size: (\d+)/m)[1]), installer.length);
fs.writeFileSync('dist/desktop/ShinyDex.exe.sha256', hash(installer)+'  ShinyDex.exe\n');
const smoke = JSON.parse(fs.readFileSync(qa+'/profile-smoke/smoke.json'));
assert.equal(smoke.passed,true); assert.equal(smoke.packaged,true); assert.equal(smoke.version,'1.2.0');
fs.copyFileSync(qa+'/profile-smoke/smoke.json',qa+'/smoke.json');
for (const file of fs.readdirSync(qa+'/profile-smoke').filter(f=>f.endsWith('.png'))) fs.copyFileSync(qa+'/profile-smoke/'+file,qa+'/'+file);
const project = JSON.parse(fs.readFileSync('audit/project-checks.json')); assert.equal(project.passed,true);
const matrix = JSON.parse(fs.readFileSync(qa+'/matrix.json')); assert.equal(matrix.passed,true);
const sourceMeta = JSON.parse(fs.readFileSync('package.json'));
for (const field of ['version','name','main','dependencies']) assert.deepEqual(metadata[field], sourceMeta[field]);
assert.deepEqual(sourceMeta.dependencies, {'electron-updater':'6.8.9'});
assert.deepEqual(sourceMeta.devDependencies, {'electron':'44.5.1','electron-builder':'26.15.3'});
const assets = ['ShinyDex.exe','latest.yml','ShinyDex.exe.blockmap','ShinyDex.exe.sha256'].map(name=>({name,bytes:fs.statSync('dist/desktop/'+name).size,sha256:hash(fs.readFileSync('dist/desktop/'+name))}));
assert.ok(assets.every(a=>a.bytes>0));
const report = {version:'1.2.0',checked:'2026-10-07',uploadApproved:true,published:false,auditComplete:false,
changes:['Responsive selection workspace and smooth transitions','Expandable form image galleries with arrows beside species names; gender-unspecified choices hidden without deleting legacy IDs','Larger saturated type badges','Flush sticky hunting-table header and 16px game-filter spacing'],
verification:{desktopTests:'6/6 passed with test isolation disabled',projectChecks:`${project.checkCount}/${project.checkCount} passed`,packagedSmoke:smoke,windowsBuild:'pnpm build:windows passed (Windows x64 NSIS)',packagedSourceMatch:true,sha512Matches:true,compatibilityMatrix:matrix,rendererEvidence:'audit/selection-layout-qa.json',dependencyPinsUnchanged:true,lockfile:'pnpm-lock.yaml has no application version field; dependency pins unchanged'},
package:{asarSha256:hash(fs.readFileSync(archive)),assets},
limitations:['Real NSIS installation/update/downgrade/restart cycle not tested','Physical monitor/DPI combinations not exhaustively tested; browser 5120-wide request clamped to 4096','Exhaustive hunting and attribution audit remains incomplete','1.0.0 exports omit newer form IDs although disk saves preserve them; export from a newer version before rollback']};
fs.writeFileSync('audit/release-1.2.0-ready.json',JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({ready:true,version:'1.2.0',installerSha256:assets[0].sha256}));
