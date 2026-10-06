// Verify a concrete newer-catalog -> older-catalog -> newer-catalog round trip.
const assert = require('node:assert/strict');
async function main() {
  const {decodeCollection, encodeCollection, assignCapture} = await import('../collection-codec.js');
  const newer = {version:2, captured:[1,200025], shinies:[200025]};
  const oldView = decodeCollection(newer, new Set([1,2]));
  assert.deepEqual([...oldView.captured], [1]);
  assert.equal(oldView.shinies.size, 0, 'Unknown forms must not inflate visible counters');
  oldView.captured.delete(1);
  oldView.captured.add(2);
  const portable = JSON.parse(JSON.stringify(encodeCollection(oldView)));
  assert.deepEqual(portable, {version:2,captured:[2,200025],shinies:[200025]});
  const restored = decodeCollection(portable, new Set([1,2,200025]));
  assert.ok(restored.captured.has(200025));
  assert.ok(restored.shinies.has(200025));
  assert.equal(restored.futureCaptured.size, 0);
  assert.deepEqual(encodeCollection(decodeCollection({version:2,captured:[],shinies:[200025]},new Set())),
    {version:2,captured:[200025],shinies:[200025]});
  for (const bad of [null, {version:3,captured:[],shinies:[]}, {version:2,captured:[1],shinies:null}]) {
    assert.throws(() => decodeCollection(bad, new Set([1])));
  }
  assert.deepEqual(encodeCollection(decodeCollection({version:2,captured:[0,-1,1000001,'1',1],shinies:[]}, new Set([1]))),
    {version:2,captured:[1],shinies:[]});
  console.log('Verified unknown-form round trip, visible totals, shiny implication, version and malformed-record handling.');
  const old={version:2,captured:[25,999999],shinies:[25,999999]};
  const assigned=assignCapture(old,25,300051);
  assert.deepEqual(assigned,{version:2,captured:[300051,999999],shinies:[300051,999999]});
  assert.deepEqual(old,{version:2,captured:[25,999999],shinies:[25,999999]},'Assignment must not mutate backup');
  assert.throws(()=>assignCapture(old,26,300051));
  assert.throws(()=>assignCapture(old,25,25));
  console.log('Verified explicit assignment preserves backup and unknown IDs, moves shiny ownership and rejects missing captures.');
}
main().catch(error => { console.error(error); process.exitCode = 1; });
