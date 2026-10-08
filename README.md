# ShinyDex

An unofficial desktop Pokédex and collection tracker with a scrolling National Dex, separate captured and shiny ownership, fixed HOME-style boxes, and a game-specific shiny hunting guide.

## Download and start

Version 1.3.0 adds offline game-specific Pokédex descriptions above hunting methods, remembered game selection, form labels and source links. It preserves version-2 collections and older unspecified captures.

**[Download ShinyDex for Windows](https://github.com/MrMints/shinydex/releases/latest/download/ShinyDex.exe)** · [Release notes and checksums](https://github.com/MrMints/shinydex/releases/latest)

1. Download **ShinyDex.exe** and double-click it to install.
2. Open **ShinyDex** from the desktop shortcut or Windows Start menu.
3. Search by Pokémon name or number. Mark **Captured** or **Shiny captured**; changes save automatically.
4. Use **HOME boxes** to browse box positions and **Shiny collection** to see your shinies. Use **Export backup** to keep a separate copy of your collection.

The app opens its own desktop window and includes all artwork. It uses no localhost server or TCP port, so an occupied port 5173 does not affect it. Closing the window exits the app. Node.js, Python, a browser, and a terminal are not required.

## Requirements and installation notes

Windows 10/11, 64-bit (x64). The installer is unsigned, so Windows may show a publisher or SmartScreen prompt. Download only from this project's GitHub release page; the release includes a SHA-256 checksum. Internet access is needed for update checks and linked reference pages; the bundled Pokédex, artwork, and collection work offline.

This is a fresh desktop profile. The former browser preview launcher and its browser saves are separate; automatic migration from browser previews is not included.

## Updates and older versions

On startup, a newer desktop release offers **Update now** or **Later**. In version 1.1.1, check **Skip Version** before choosing **Later** to stop startup prompts for that exact release. A newer unskipped release shows **Update Available** on the update button. Skipped releases remain available for manual installation. The adjacent version dropdown selects a compatible published desktop version; reopen it with **Update**. Published native versions include 1.0.0, 1.1.0, 1.1.1, 1.1.2, and 1.2.0. **Versions older than 1.0.0 Release cannot be selected.** Native releases can be installed or rolled back as far as 1.0.0. The old browser previews are named 0.1 and 0.2 and are excluded.

The updater downloads the selected installer, verifies its manifest SHA-512 and GitHub SHA-256 digest, and installs and restarts automatically. An offline check or failed verification leaves the installed app usable.

Collection files remain in `%APPDATA%\ShinyDexDesktop\collection-v2.json` across desktop updates and rollbacks. Before installation the app writes a JSON backup in that profile's `backups` folder. Future catalog IDs are retained when an older desktop catalog saves. Collection contents are never uploaded to GitHub. **Export backup** saves a portable JSON file; **Import backup** restores a compatible version-2 collection after backing up the current one.

The 1.0.0 → 1.1.0 → 1.0.0 → 1.1.0 desktop save round trip was tested with the verified public 1.0.0 code and isolated fixtures. All 1,083 legacy IDs survive the upgrade; newer form ownership survives older desktop autosaves and reappears after upgrading again. **Export a backup in 1.1.0 before rolling back:** 1.0.0's Export backup button omits forms that it cannot recognize, although its on-disk desktop save retains them. Older browser previews do not provide the same unknown-form protection. These checks do not establish a real NSIS installation/update cycle; see [release preparation evidence](audit/release-1.1.0-ready.json).

Save compatibility for 1.0.0�1.1.2 passed all twelve directed version pairs with all catalog IDs and an unknown future ID. Actual renderer upgrade, rollback, reload, backup and export checks used isolated fixture profiles; real NSIS update/restart cycles remain unverified. See [1.1.2 release evidence](audit/release-1.1.2-ready.json).

## Collection

- Captured and Shiny captured are separate checkboxes, with Captured on the left. Marking shiny also marks captured; clearing captured clears shiny.
- Species with alternate forms have an arrow beside their name that expands a labeled image gallery. Select an image to choose a form. Each concrete form has independent captured and shiny ownership. The separate Pokémon caught and shinies caught boxes show their own totals and completion. Browser development has separate storage and synchronizes changes between browser tabs.
- HOME boxes retain National Dex positions when filtered: six columns, five rows, 30 slots. Unowned entries use silhouettes; owned shinies use shiny art. Hover labels give the name and position.
- The Shiny collection tab shows owned shinies. Export backup saves a JSON copy of collection ownership. Desktop storage is local to this Windows user. Export a backup before changing computers.

The current source catalog covers 1,025 species with 1,431 concrete living-dex slots across 48 HOME boxes. It also preserves 173 unspecified legacy ownership records, giving 1,604 stable records in total. Unspecified records have no HOME slot; use the form assignment control to choose their identity explicitly. Assignment backs up the collection first, and browser backups can be restored from the recovery panel. The published installer may predate these source changes.

The working completeness reference is [PokéPC’s living dex](https://pokepc.net/livingdex); [its National Pokédex](https://pokepc.net/pokemon) supplies species names and Dex numbers. Only HOME-storable forms are in scope, excluding temporary battle transformations and Spiky-eared Pichu. All named forms in the saved living-dex layout have a matching concrete slot. Independent transfer, artwork and hunting verification remains unfinished; [the comparison report](audit/pokepc-living-dex-comparison.json) marks that work and 43 additional catalog entries for later review.

## Data status

The exhaustive hunting, event, transfer-prerequisite, and final attribution audits remain incomplete. Passing the verifiers establishes their stated checks, not complete game, event, location, form, or prerequisite coverage. Use the linked references in the hunting guide when planning a hunt.

Future audits resume from [audit/AUDIT-CHECKPOINT.md](audit/AUDIT-CHECKPOINT.md) and the machine-readable [audit/audit-checkpoint.json](audit/audit-checkpoint.json). They record evidence scopes, unresolved work, source hashes, and installer limits so new games and updates can be reviewed without repeating unaffected completed work.

## Run from source

Install Node.js and pnpm, run `pnpm install`, then `pnpm start`. Build the Windows installer with `pnpm build:windows`; outputs are in `dist/desktop`. If dependency installation disables lifecycle scripts, run `node node_modules/electron/install.js` once to download Electron.

For browser development only, run `node server.cjs` and open http://localhost:5173. Browser development uses browser storage and does not install desktop updates.

## Files

`index.html`, `main.js`, and `style.css` implement the browser interface. `server.cjs` serves the project on the loopback address. `data.json` contains catalog and artwork references; `hunts.json` contains form-specific acquisition records. `assets/pokemon/` holds 2,166 normal/shiny HOME artwork PNGs sourced from Bulbagarden Archives.

The Python builders and checked-in reference snapshots support reproducible data generation. `python build-hunts.py` rebuilds the guide; `python build-catalog.py` rebuilds the catalog. Python tooling requires Pillow for image decoding. Preserve the CSVs and `reference/` when rebuilding. PKHeX resources are pinned to commit `542111fc8584ff29c9d1455553b8acd0e1f8a59a`; the decoders read these resources without executing upstream C# code.

`audit/` contains audit reports, checkpoints, evidence snapshots, inventories, verification tooling, and QA artifacts. See [audit/README.md](audit/README.md) for the directory map and current commands. Create new audit material there. Runtime files, CSV inputs, pinned `reference/` resources, and shared data builders retain their source locations.

`Archive/` preserves obsolete app code and historical development notes. Audit screenshots, contact sheets, and browser QA fixtures are now in `audit/artifacts/`. These files are not browser runtime dependencies.

`desktop/main.cjs` implements the local protocol and sandboxed window; `preload.cjs` exposes a narrow IPC bridge. `storage.cjs` validates and atomically saves collection records. `updates.cjs` discovers public desktop releases and installs immutable release feeds with electron-updater. Run `pnpm test:desktop` for storage and updater regression tests. `desktop/smoke.cjs` runs only with `SHINYDEX_DESKTOP_QA=1` and an explicit isolated `SHINYDEX_DESKTOP_QA_DIR`; it checks rendering, persistence, bridge isolation, update controls, and forbidden protocol paths.

`windows/` contains the historical browser-preview .NET browser launcher and its verifiers. It is excluded from desktop packages and should not be used to build the desktop app. Published browser-preview assets remain historical downloads. For a desktop release, increment `package.json`, build and verify the installer, and publish an exact `vX.Y.Z` tag with `ShinyDex.exe`, `latest.yml`, the blockmap, and SHA-256 checksum. Keep release assets immutable and the profile path stable.

Implementation references: [Electron protocol](https://www.electronjs.org/docs/latest/api/protocol), [context isolation](https://www.electronjs.org/docs/latest/tutorial/context-isolation), and [NSIS automatic updates](https://www.electron.build/docs/features/auto-update/).

## Verification and remaining work

Run `python audit/check-project.py` to execute the checked-in `verify-*.py` and `verify-*.cjs` checks and refresh `audit/project-checks.json`. Run `python audit/audit-dexnav-coverage.py` to refresh the unresolved DexNav location/form inventory. Run `python audit/audit-event-inventory.py` after rebuilding hunts to refresh vague historical event candidates and source/index research groups in `audit/pending-event-review.json`. These groups are not unique announcement identities and do not certify coverage. Run `python audit/audit-upstream-images.py --fresh` for a new network comparison of every artwork file. Run `python audit/build-image-review.py` to recreate the visual-review sheets. Run `python audit/audit-captions.py` to compare every image identity with cached Archives captions; missing captions are fetched from the Archives API.

Audit evidence includes:

- `audit/desktop-qa.json`: historical 1.0.0 packaged runtime and NSIS installation evidence, including installer exit code 0, an installed-app smoke pass, and test uninstall exit code 0. Update/downgrade calls used controlled fixtures. The later local audit build has source and win-unpacked smoke evidence in `audit/desktop-runtime-review.json`, but its refreshed NSIS installer has not been verified. Real public update/downgrade, restart and collection persistence across that cycle, and clean-machine Windows/SmartScreen prompts remain unverified.

- `audit/data-audit.json` and `audit/regional-form-audit.json`: catalog order, regional mapping, guide presence, and current scope limitations.
- `audit/image-audit.json`, `audit/caption-audit.json`, and `audit/local-image-audit.json`: Archives metadata, caption identity checks, and full local PNG decoding with SHA-256 hashes. Caption exceptions are documented. `audit/upstream-image-audit.json` records fresh source-file fetches matching all 2,166 local SHA-256 hashes. `audit/visual-image-audit.json` records visual inspection of every normal/shiny pair across 16 labeled contact sheets, with resolution limits stated.
- `audit/runtime-qa.json`: observed browser behavior and limitations. In-app browser testing includes regional ownership, reload persistence, bidirectional cross-tab synchronization, silhouettes, owned shiny images, collection filtering, all HOME position/hover labels, malformed JSON/null/partial-record rejection, invalid-key filtering and recovery, plus isolated simulated quota/denial failures and generated emergency-backup contents. Chrome and Firefox remain unverified.
- `audit/hunting-technique-review.json`, `audit/dexnav-coverage-gaps.json`, and the encounter/evolution/raid/breeding audit files: completed source checks and unresolved coverage.

All 32 Mirage variants now retain individually reviewed retail floor/grass rosters and source links. The normalized ORAS inventory has eight raw cross-version hideout candidates, all retained with reviewed gameplay exclusions; zero unreviewed normalized candidates does not certify full room, form or prerequisite coverage.

Unown DexNav guidance now distinguishes species search from the approaching form silhouette and documents the chain consequence of skipping a detected form. `audit/bdsp-radar-review.json` records 321 BDSP Radar routes and reviewed location exclusions, acquisition and version-specific mechanics. `audit/sos-review.json` records mechanics for 843 SOS routes and reviewed special caller/weather targets. Both retain explicit limits on conditional encounter coverage. Desktop (1280×900), mobile (390×844) and mobile six-column HOME layouts were visually reviewed in the in-app browser; evidence is recorded in `audit/runtime-qa.json`.

The local audit update adds exact BDSP availability conditions to 32 Trophy Garden and 56 swarm Radar routes, with the same requirements on 88 ordinary-grass routes. It also independently compares all 43 Radar-exclusive species, eight version exclusions, and their combined named locations. The published 1.0 installer predates these source data changes; they will ship with a subsequent installer release.

Route 205 and Fuego Ironworks now identify the reviewed version-specific Radar sections. `python audit/audit-bdsp-tables.py` inventories 39 independent encounter pages in `audit/bdsp-independent-tables.json`, retaining source URLs and hashes. It inventories 84 time-restricted species/game/location combinations. All 84 original time-restricted candidate combinations are now source-reviewed in audit/bdsp-time-review.json and applied to ordinary-grass and Radar entries. North/south and east/west sections retain separate annotations, and the guide gives BDSP system-clock periods. Lost Tower and Stark Mountain cave encounters are separated from their outdoor locations so exterior night restrictions do not apply to interior hunts. Lost Tower now has explicit 1F–5F labels: Murkrow (Brilliant Diamond) and Misdreavus (Shining Pearl) are night-only on each floor; Zubat and Gastly remain available across all five floors, and Golbat begins on 3F. These ten reviewed interior time restrictions are separate from the original 84 outdoor candidates. The four previously unmapped sections are now documented in audit/bdsp-section-review.json using explicit zone identities and matching map filenames: Mount Coronet snow area/summit and Lake Verity before/after the Galactic incident. This adds eight reviewed Mount Coronet night combinations, bringing the outdoor inventory to 92 with none unreviewed. Other interior conditions, access prerequisites, and tile eligibility remain unresolved. Legacy-encoded page headings are decoded without replacement characters so Radar pools remain distinct from ordinary time slots. Parsed records do not automatically change the guide or establish complete coverage.

Remaining work includes the full DexNav room/form/prerequisite review; remaining radar and SOS conditional encounter coverage and other hunting techniques; exact access and transfer prerequisites; announcement-level historical event and Pokémon GO verification; shiny-lock review; Chrome/Firefox and real quota exhaustion and native-download completion; final code, attribution, and cleanup audits. A missing method or source record must not be treated as proof of a shiny lock.

## Attribution and rights

This is an unofficial fan project, unaffiliated with Nintendo, Creatures, GAME FREAK, The Pokémon Company, Bulbapedia, Serebii, PokéAPI, or PKHeX. Pokémon characters and artwork belong to their respective rights holders. Artwork is sourced from [Bulbagarden Archives](https://archives.bulbagarden.net/), with per-image source pages retained in `data.json`. Hunting mechanics and location reviews link to [Bulbapedia](https://bulbapedia.bulbagarden.net/) and [Serebii Pokéarth](https://www.serebii.net/pokearth/).

Encounter and Pokédex CSV snapshots originate from [PokéAPI](https://github.com/PokeAPI/pokeapi), credited to Paul Hallett and PokéAPI contributors under BSD-3-Clause. Pinned encounter, evolution, and personal reference resources originate from [PKHeX](https://github.com/kwsch/PKHeX), under GNU GPLv3. Prettier 3.6.2, by James Long and contributors, was used during development under MIT; it is not a browser runtime dependency. The desktop app bundles Electron, Chromium, and Node.js; the renderer cannot access Node.js APIs. Electron notices and production dependency licenses ship with the app. Pillow supports the Python image audit and is not bundled in the browser app.

See [ATTRIBUTIONS.txt](ATTRIBUTIONS.txt), [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md), `licenses/`, and `reference/pkhex/LICENSE` for retained notices and provenance. No blanket MIT license is asserted over this project, Pokémon artwork, or bundled reference material. Third-party rights and licenses remain separate. Complete attribution review is still part of the publication audit.
