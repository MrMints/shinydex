const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs/promises');
const os=require('node:os');
const path=require('node:path');
const {CollectionStore,validate}=require('./storage.cjs');
test('queued saves retain future catalog IDs and backups wait for writes',async t=>{
 const dir=await fs.mkdtemp(path.join(os.tmpdir(),'shinydex-store-'));t.after(()=>fs.rm(dir,{recursive:true,force:true}));
 const store=new CollectionStore(dir,[1,2]);assert.equal(await store.load(),null);
 await store.save({version:2,captured:[1,99999],shinies:[99999]});
 const first=store.save({version:2,captured:[2],shinies:[]});
 const second=store.save({version:2,captured:[1],shinies:[1]});
 const backup=store.backup();await Promise.all([first,second]);
 const expected={version:2,captured:[1,99999],shinies:[1,99999]};
 assert.deepEqual(JSON.parse(await store.load()),expected);
 assert.deepEqual(JSON.parse(await fs.readFile(await backup,'utf8')),expected);
});
test('malformed existing saves are preserved',async t=>{
 const dir=await fs.mkdtemp(path.join(os.tmpdir(),'shinydex-store-'));t.after(()=>fs.rm(dir,{recursive:true,force:true}));
 const store=new CollectionStore(dir,[1]);await fs.writeFile(store.file,'broken');
 await assert.rejects(store.save({version:2,captured:[1],shinies:[]}));
 assert.equal(await fs.readFile(store.file,'utf8'),'broken');
 assert.throws(()=>validate({version:2,captured:[NaN],shinies:[]}));
 assert.deepEqual(validate({version:2,captured:[],shinies:[1,1]}),{version:2,captured:[1],shinies:[1]});
});
