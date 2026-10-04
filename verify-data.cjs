const assert=require('node:assert/strict'),fs=require('node:fs');
const data=JSON.parse(fs.readFileSync('data.json')),hunts=JSON.parse(fs.readFileSync('hunts.json'));
assert.equal(data.length,1083);
assert.equal(new Set(data.map(p=>p.key)).size,data.length,'Form keys must be unique');
assert.deepEqual(data.filter(p=>!p.region).map(p=>p.id),Array.from({length:1025},(_,i)=>i+1));
assert.equal(data.filter(p=>p.region).length,58);
const needsReview=[];
for(const [i,p] of data.entries()){
 assert.equal(p.position,i,'Box positions must be consecutive');
 if(i)assert.ok(p.id>=data[i-1].id,'National order must remain fixed');
 for(const mode of ['normal','shiny']){
  assert.ok(fs.existsSync(p[mode]),`Missing ${mode} image for ${p.displayName}`);
  assert.ok(p[mode+'Source'].startsWith('https://archives.bulbagarden.net/'));
 }
 const h=hunts[p.key];assert.ok(h,`Missing form-specific guide: ${p.displayName}`);
 assert.ok(h.locked||h.entries.length,`No hunting or lock record: ${p.displayName}`);
 for(const e of h.entries){assert.ok(e.game&&e.method&&e.status&&e.source);}
 const uncertain=h.entries.filter(e=>e.status==='Check gift/event shiny restrictions');
 if(uncertain.length)needsReview.push({key:p.key,name:p.displayName,games:[...new Set(uncertain.map(e=>e.game))]});
}
const captions=JSON.parse(fs.readFileSync('caption-audit.json'));
assert.equal(captions.issues.length,0,'Artwork identity audit must pass');
const report={entries:data.length,species:1025,regionalForms:58,boxes:Math.ceil(data.length/30),imageFiles:data.length*2,globallyLocked:data.filter(p=>hunts[p.key].locked).map(p=>p.displayName),unverifiedGiftSpecies:needsReview.length,needsReview,exhaustiveHuntingAuditComplete:false};
fs.writeFileSync('data-audit.json',JSON.stringify(report,null,2));
console.log(`Verified ${data.length} ordered entries, 58 regional forms, 37 boxes, 2166 local images and hunting/lock records. ${needsReview.length} entries still have gift restrictions requiring review; exhaustive game coverage remains incomplete.`);
