// Resolve runtime inputs relative to the repository, not the launch directory.
process.chdir(require('node:path').resolve(__dirname,'..'));
const fs=require('node:fs');
const code=fs.readFileSync('main.js','utf8');
const start=code.indexOf('function methodSources('),end=code.indexOf('function huntEntries(',start);
const render=new Function('URL','esc',code.slice(start,end)+';return methodSources;')(URL,s=>String(s).replaceAll('&','&amp;').replaceAll('"','&quot;').replaceAll('<','&lt;').replaceAll('>','&gt;'));
const hunts=JSON.parse(fs.readFileSync('hunts.json','utf8'));
let count=0;
for(const guide of Object.values(hunts))for(const entry of guide.entries){
 if(!entry.sourceReferences)continue;
 const result=render(entry),expected=[...new Set([entry.source,...entry.sourceReferences].filter(Boolean))];
 if((result.match(/<a /g)||[]).length!==expected.length)throw Error('Reference missing');
 count++;
}
if(render({source:'javascript:alert(1)'}))throw Error('Unsafe source accepted');
if((render({source:'https://example.com',sourceReferences:['https://example.com']}).match(/<a /g)||[]).length!==1)throw Error('Duplicate reference');
console.log('Verified supporting references render for '+count+' hunting routes; duplicate and unsafe links excluded');
