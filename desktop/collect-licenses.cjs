// Preserve upstream production dependency license texts in the distribution.
const fs=require('node:fs');const path=require('node:path');const {createRequire}=require('node:module');
const seen=new Set();const sections=[];
function visit(directory){
 directory=fs.realpathSync(directory);if(seen.has(directory))return;seen.add(directory);
 const pkg=JSON.parse(fs.readFileSync(path.join(directory,'package.json'),'utf8'));
 const licenses=fs.readdirSync(directory).filter(name=>/^(license|licence|copying)(\.|$)/i.test(name)&&fs.statSync(path.join(directory,name)).isFile());
 const fallback=path.resolve(`licenses/${pkg.name}-MIT.txt`);
 if(!licenses.length&&!fs.existsSync(fallback))throw Error(`Missing license: ${pkg.name}`);
 sections.push(`${pkg.name} ${pkg.version} (${pkg.license})\n${licenses.length?licenses.map(name=>fs.readFileSync(path.join(directory,name),'utf8')).join('\n'):fs.readFileSync(fallback,'utf8')}`);
 const resolve=createRequire(path.join(directory,'package.json'));
 for(const name of Object.keys(pkg.dependencies||{})){
  let file=resolve.resolve(name);let parent=path.dirname(file);
  while(!fs.existsSync(path.join(parent,'package.json')))parent=path.dirname(parent);
  visit(parent);
 }
}
visit(path.resolve('node_modules/electron-updater'));
fs.writeFileSync('licenses/Desktop-runtime-dependencies.txt',sections.join('\n\n'+'='.repeat(80)+'\n\n'));
fs.copyFileSync('node_modules/electron/dist/LICENSE','licenses/Electron-MIT.txt');
console.log(`Retained licenses for ${seen.size} production packages plus Electron; Chromium notices ship beside the executable.`);
