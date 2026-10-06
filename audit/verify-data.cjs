// Resolve runtime inputs relative to the repository, not the launch directory.
process.chdir(require('node:path').resolve(__dirname,'..'));
const assert=require('node:assert/strict'),fs=require('node:fs');
const data=JSON.parse(fs.readFileSync('data.json')),hunts=JSON.parse(fs.readFileSync('hunts.json'));
const legacy=data.filter(p=>!p.livingForm);
assert.equal(legacy.length,1083,'Preserve the legacy species/regional catalog');
assert.equal(new Set(data.map(p=>p.key)).size,data.length,'Form keys must be unique');
assert.deepEqual(legacy.filter(p=>!p.region).map(p=>p.id),Array.from({length:1025},(_,i)=>i+1));
assert.equal(legacy.filter(p=>p.region).length,58);
const home=data.filter(p=>!p.formUnspecified),pendingFormGuides=[];
let position=0;
const needsReview=[];
for(const [i,p] of data.entries()){
 assert.equal(p.position,p.formUnspecified?null:position++,'Concrete box positions must be consecutive; unspecified legacy forms have no slot');
 if(i)assert.ok(p.id>=data[i-1].id,'National order must remain fixed');
 for(const mode of ['normal','shiny']){
  assert.ok(fs.existsSync(p[mode]),`Missing ${mode} image for ${p.displayName}`);
  assert.ok(p[mode+'Source'].startsWith('https://archives.bulbagarden.net/'));
 }
 const h=hunts[p.key];
 if(p.livingForm&&!h){pendingFormGuides.push({key:p.key,name:p.displayName});continue;}
 assert.ok(h,`Missing legacy form-specific guide: ${p.displayName}`);
 assert.ok(h.locked||h.entries.length,`No hunting or lock record: ${p.displayName}`);
 for(const e of h.entries){assert.ok(e.game&&e.method&&e.status&&e.source);}
 const uncertain=h.entries.filter(e=>e.status==='Check gift/event shiny restrictions');
 if(uncertain.length)needsReview.push({key:p.key,name:p.displayName,games:[...new Set(uncertain.map(e=>e.game))]});
}
const captions=JSON.parse(fs.readFileSync('audit/caption-audit.json'));
assert.equal(captions.issues.length,0,'Artwork identity audit must pass');
const report={entries:data.length,legacyEntries:legacy.length,species:1025,regionalForms:58,boxes:Math.ceil(home.length/30),homeSlots:home.length,imageFiles:new Set(data.flatMap(p=>[p.normal,p.shiny])).size,globallyLocked:data.filter(p=>hunts[p.key]?.locked).map(p=>p.displayName),unverifiedGiftSpecies:needsReview.length,needsReview,pendingFormGuides,exhaustiveHuntingAuditComplete:false};
fs.writeFileSync('audit/data-audit.json',JSON.stringify(report,null,2));
console.log(`Verified ${data.length} ordered catalog records, ${home.length} HOME slots and local artwork; preserved ${legacy.length} legacy hunting/lock records. ${pendingFormGuides.length} new form guides and ${needsReview.length} gift restrictions remain unreviewed; exhaustive game coverage remains incomplete.`);
