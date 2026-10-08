# Game descriptive-entry compilation

Scope: English descriptive text for the application's 1,025 species, including
source-labeled alternate forms. No game-specific Dex numbers, collection changes,
new hunting claims or publication were included in the compilation. The later
user-authorized UI trial is documented below.

`pokedex-entries.json` is the offline runtime-ready dataset. Its species keys are
National species IDs (`pokemon.id`), **not** collection/form keys (`pokemon.key`).
Each description records a stable game identifier, nullable source form label,
text, scope and source URL; Bulbapedia records also include revision IDs.
`games` includes source/PokéAPI game labels with explicit recorded/not-recorded
status. There are 18,838 descriptions, including 1,227 form-labeled descriptions,
across 41 games with text; 56 game records include games/DLC with no separate
recorded English description. `audit/artifacts/pokedex-entries.csv` is the readable
list. These are source inventory counts, not independent cartridge verification.

## Integration

Keep descriptions separate from `data.json` and `hunts.json` so catalog rebuilds
cannot erase them and ownership IDs remain stable. Load descriptions once on
demand when the future descriptive-entry feature is opened. The prepared module:

```javascript
import { createPokedexIndex } from './pokedex.js';
const descriptions = await read('./pokedex-entries.json');
const dex = createPokedexIndex(descriptions, hunts);
const gameRows = dex.forPokemon(selectedPokemon); // or a game ID such as 'scarlet'
```

Each row groups descriptions and the existing **exact selected-form** hunting
records by game. It preserves individual hunting methods, locations, statuses,
source links and DLC labels. Paired labels are expanded into their individual
games. Description text does not determine encounters or shiny eligibility.
Missing descriptions and hunting records have separate `not-recorded` statuses.

Render descriptions as text, alongside their form labels and source links.
`formLabel: null` means the source's default species entry; it does not establish
that the text applies to every form. The module deliberately returns the labeled
species descriptions together rather than guessing a correspondence between
wiki labels and living-dex ownership keys. A later form-specific UI can add a
reviewed mapping; it must not silently use base text for a regional form.

The UI trial now loads descriptions lazily into a card above the existing hunting
panel. Its remembered game selection filters paired-game and DLC hunting records;
the user can choose all hunting games instead. Source form labels remain visible.
Load failures offer a retry without disabling ownership or hunting. `pokedex.js`
and `pokedex-entries.json` are included in both the explicit package file list and
desktop protocol allowlist. Saves and collection keys remain unchanged. No release
version was incremented during the initial trial. The subsequent user-authorized
1.3.0 release preparation is recorded in `release-1.3.0-ready.json`.

UI validation is recorded in `audit/pokedex-ui-qa.json`. Source and Windows x64
unpacked smoke tests passed with isolated QA collections and no renderer errors.
Checks exercised game changes, remembered selection between species, all-game
hunting, missing Japanese-original descriptions, labeled Alolan entries, capture
persistence and six-column HOME behavior. Screenshots at 1280/1920 and 420 pixels
are under `audit/artifacts/pokedex-ui-packaged-qa/`. The new runtime files match
their packaged bytes, and reference snapshots/audit tooling remain excluded.
Six desktop regression tests and the Pokédex/source-link verifiers also passed.
Browser preview interaction confirmed Scarlet → Red → Scarlet descriptions and
hunting records. Initial sandbox launch/build failures were environmental ACL and
EPERM errors; reruns outside the command sandbox passed. No real NSIS cycle was
tested. Those preview runs reported 1.2.0; the 1.3.0 release has a separate
packaged smoke report under `audit/artifacts/release-1.3.0/`.

## Rebuild and verify

```powershell
python collect-pokedex.py       # network, resumable; only missing species pages
python build-pokedex.py         # entirely offline, deterministic for fixed inputs
node audit/verify-pokedex.cjs
```

All 1,025 species snapshots were fetched successfully. The builder expanded every
`Dex/Entry1`–`Dex/Entry4` record found in those sections and resolved all encountered
text templates. PokéAPI supplies 160 default species/game fallback rows where the
wiki only labeled particular forms or lacked a default record; the audit lists
every fallback. The verifier checks all compiled text, game IDs, species coverage,
all 83 hunting game labels, paired/DLC joins, retained Alolan text, exact-form
hunting joins and missing-data behavior. Rebuilding twice produced identical
runtime JSON, CSV and audit-report hashes.

## Limits and evidence

`pokedex-entries-report.json` contains input hashes, per-game counts, missing-page
and unresolved-template inventories, source no-entry/unavailable statements and
fallback rows. `pokedex-collection.json` records retrieval outcomes. No missing
description is filled with a different game's description. Source descriptions
introduced by DLC stay under their parent game when the source does so.

Japanese-only originals have no independently sourced English localization here.
The compilation does not claim every localization or every spin-off title; it
captures all descriptive templates in the catalog species source sections plus
the pinned English PokéAPI rows. Source transcription and every game/form pairing
have not been independently compared to cartridges. Existing hunting gaps and
`auditComplete: false` remain intact.

The pre-work checkpoint reported nine changed baseline files, consistent with
later source/release work documented in the checkpoint. Its hashes were preserved;
no old audit is treated as fresh verification. Existing area-ledger findings and
collection files were not changed.
