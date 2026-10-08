const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
(async () => {
  const descriptions = JSON.parse(fs.readFileSync(path.join(root, 'pokedex-entries.json')));
  const catalog = JSON.parse(fs.readFileSync(path.join(root, 'data.json')));
  const hunts = JSON.parse(fs.readFileSync(path.join(root, 'hunts.json')));
  const code = fs.readFileSync(path.join(root, 'pokedex.js'), 'utf8');
  const { createPokedexIndex } = await import(`data:text/javascript;base64,${Buffer.from(code).toString('base64')}`);
  const index = createPokedexIndex(descriptions, hunts);
  const species = new Set(catalog.map(p => String(p.id)));
  assert.equal(Object.keys(descriptions.species).length, species.size);
  for (const [sid, entries] of Object.entries(descriptions.species)) {
    assert(species.has(sid));
    assert(entries.length);
    for (const e of entries) {
      assert(descriptions.games[e.gameId]);
      assert(e.text.trim());
      assert(!/\{\{|\}\}|\[\[|\]\]|<[^>]+>|\uFFFD/.test(e.text), `Unrendered text: ${sid}/${e.gameId}`);
      assert(new URL(e.source).protocol === 'https:');
    }
  }
  const labels = new Set(Object.values(hunts).flatMap(h => h.entries.map(e => e.game)));
  for (const label of labels) assert(index.gameIds(label).length, `Unmapped game: ${label}`);
  const bulbasaur = catalog.find(p => p.id === 1);
  assert(index.forPokemon(bulbasaur, 'scarlet')[0].descriptions.length);
  assert.deepEqual(index.gameIds('Pokémon Scarlet / Violet · The Indigo Disk'), ['scarlet', 'violet']);
  assert.deepEqual(index.gameIds('Pokémon Red Japan'), ['red-japan']);
  const raichu = descriptions.species['26'].filter(e => e.gameId === 'sun');
  assert(raichu.some(e => e.formLabel === 'Alolan Form'));
  assert(raichu.some(e => e.formLabel === null));
  const isolated = createPokedexIndex(descriptions, {'999999': {entries: [{game: 'Pokémon HOME', status: 'Reward', locations: []}]}});
  const home = isolated.forPokemon({id: 1, key: 999999}, 'home')[0];
  assert.equal(home.descriptionStatus, 'not-recorded');
  assert.equal(home.huntingRecords.length, 1);
  const empty = isolated.forPokemon({id: 1, key: 888888}, 'red')[0];
  assert.equal(empty.huntingStatus, 'not-recorded');
  assert(!('locked' in empty));
  console.log(`Verified descriptions for ${species.size} species and ${labels.size} hunting game labels; exact-form joins and missing-data behavior passed.`);
})().catch(error => { console.error(error); process.exitCode = 1; });
