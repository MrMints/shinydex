# ShinyDex

An unofficial browser Pokédex and collection tracker with a scrolling National Dex, separate captured and shiny ownership, fixed HOME-style boxes, and a game-specific shiny hunting guide.

**Development status:** the exhaustive hunting and final release audits are incomplete. The project is published at [MrMints/shinydex](https://github.com/MrMints/shinydex). Passing the verifiers establishes their stated checks, not complete game, event, location, form, or prerequisite coverage.

## Run locally

Install Node.js, then run `npm start` from this directory and open http://localhost:5173. You can also run `node server.cjs` directly. The browser app has no npm runtime dependencies. Keep the local server running while using the app.

## Collection

- Captured and Shiny captured are separate checkboxes, with Captured on the left. Marking shiny also marks captured; clearing captured clears shiny.
- Every change autosaves in this browser and origin under `shinydex-collection-v2`. Base species and regional forms have independent keys. The earlier shiny-only format migrates automatically, and changes synchronize between tabs.
- HOME boxes retain National Dex positions when filtered: six columns, five rows, 30 slots. Unowned entries use silhouettes; owned shinies use shiny art. Hover labels give the name and position.
- The Shiny collection tab shows owned shinies. Export backup saves a JSON copy of collection ownership. Collection storage is local to the browser; changing browser, device, host, or port creates a different storage context.

The current catalog contains 1,025 species and 58 regional-form entries, spanning 37 boxes. These counts are checks of the current catalog and do not independently establish exhaustive correctness.

## Files

`index.html`, `main.js`, and `style.css` implement the browser interface. `server.cjs` serves the project on the loopback address. `data.json` contains catalog and artwork references; `hunts.json` contains form-specific acquisition records. `assets/pokemon/` holds 2,166 normal/shiny HOME artwork PNGs sourced from Bulbagarden Archives.

The Python builders and checked-in reference snapshots support reproducible data generation. `python build-hunts.py` rebuilds the guide; `python build-catalog.py` rebuilds the catalog. Python tooling requires Pillow for image decoding. Preserve the CSVs and `reference/` when rebuilding. PKHeX resources are pinned to commit `542111fc8584ff29c9d1455553b8acd0e1f8a59a`; the decoders read these resources without executing upstream C# code.

`Archive/` preserves obsolete app code, historical previews, and accumulated development notes. These files are not browser runtime dependencies.

## Verification and remaining work

Run `python check-project.py` to execute the checked-in `verify-*.py` and `verify-*.cjs` checks and refresh `project-checks.json`. Run `python audit-dexnav-coverage.py` to refresh the unresolved DexNav location/form inventory. Run `python audit-upstream-images.py --fresh` for a new network comparison of every artwork file. Run `python build-image-review.py` to recreate the visual-review sheets. Run `python audit-captions.py` to compare every image identity with cached Archives captions; missing captions are fetched from the Archives API.

Audit evidence includes:

- `data-audit.json` and `regional-form-audit.json`: catalog order, regional mapping, guide presence, and current scope limitations.
- `image-audit.json`, `caption-audit.json`, and `local-image-audit.json`: Archives metadata, caption identity checks, and full local PNG decoding with SHA-256 hashes. Caption exceptions are documented. `upstream-image-audit.json` records fresh source-file fetches matching all 2,166 local SHA-256 hashes. `visual-image-audit.json` records visual inspection of every normal/shiny pair across 16 labeled contact sheets, with resolution limits stated.
- `runtime-qa.json`: observed browser behavior and limitations. In-app browser testing includes regional ownership, reload persistence, bidirectional cross-tab synchronization, silhouettes, owned shiny images, collection filtering, all HOME position/hover labels, malformed JSON/null/partial-record rejection, invalid-key filtering and recovery, plus isolated simulated quota/denial failures and generated emergency-backup contents. Chrome and Firefox remain unverified.
- `hunting-technique-review.json`, `dexnav-coverage-gaps.json`, and the encounter/evolution/raid/breeding audit files: completed source checks and unresolved coverage.

All 32 Mirage variants now retain individually reviewed retail floor/grass rosters and source links. The normalized ORAS inventory has eight raw cross-version hideout candidates, all retained with reviewed gameplay exclusions; zero unreviewed normalized candidates does not certify full room, form or prerequisite coverage.

Unown DexNav guidance now distinguishes species search from the approaching form silhouette and documents the chain consequence of skipping a detected form. `bdsp-radar-review.json` records 321 BDSP Radar routes and reviewed location exclusions, acquisition and version-specific mechanics. `sos-review.json` records mechanics for 843 SOS routes and reviewed special caller/weather targets. Both retain explicit limits on conditional encounter coverage. Desktop (1280×900), mobile (390×844) and mobile six-column HOME layouts were visually reviewed in the in-app browser; evidence is recorded in `runtime-qa.json`.

Remaining work includes the full DexNav room/form/prerequisite review; remaining radar and SOS conditional encounter coverage and other hunting techniques; exact access and transfer prerequisites; announcement-level historical event and Pokémon GO verification; shiny-lock review; Chrome/Firefox and real quota exhaustion and native-download completion; final code, attribution, and cleanup audits. A missing method or source record must not be treated as proof of a shiny lock.

## Attribution and rights

This is an unofficial fan project, unaffiliated with Nintendo, Creatures, GAME FREAK, The Pokémon Company, Bulbapedia, PokéAPI, or PKHeX. Pokémon characters and artwork belong to their respective rights holders. Artwork is sourced from [Bulbagarden Archives](https://archives.bulbagarden.net/), with per-image source pages retained in `data.json`. Hunting mechanics and location reviews link to [Bulbapedia](https://bulbapedia.bulbagarden.net/).

Encounter and Pokédex CSV snapshots originate from [PokéAPI](https://github.com/PokeAPI/pokeapi), credited to Paul Hallett and PokéAPI contributors under BSD-3-Clause. Pinned encounter, evolution, and personal reference resources originate from [PKHeX](https://github.com/kwsch/PKHeX), under GNU GPLv3. Prettier 3.6.2, by James Long and contributors, was used during development under MIT; it is not a browser runtime dependency. Node.js is supplied separately by the user and is not bundled. Pillow supports the Python image audit and is not bundled in the browser app.

See [ATTRIBUTIONS.txt](ATTRIBUTIONS.txt), [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md), `licenses/`, and `reference/pkhex/LICENSE` for retained notices and provenance. No blanket MIT license is asserted over this project, Pokémon artwork, or bundled reference material. Third-party rights and licenses remain separate. Complete attribution review is still part of the publication audit.
