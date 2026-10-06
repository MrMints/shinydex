# Living dex implementation — active

Requested outcome: every main-list Pokémon exposes independently captured/shiny form options, including gender differences and all 63 Alcremie combinations. Each tracked form receives a fixed National-order HOME position. Separate captured/shiny summary boxes remain.

## Evidence and scope

- User reference: https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_with_form_differences
- Immutable PokeAPI form/name/species inputs: `reference/pokeapi/living-dex/manifest.json`. Shared generation inputs stay in reference; review inventory/tooling stays in audit.
- `living-dex-inventory.json` is a candidate inventory, not an approved catalog or coverage certificate. It includes temporary/battle records so exclusions remain reviewable. Species-level gender differences need form-level reconciliation. The user selected forms kept outside battle; exclude temporary battle transformations from collection slots while retaining reviewed exclusions.
- Current data has 1,083 stable ownership keys. Existing 3,137 HOME-prefixed artwork metadata records include alternate forms but not every form's normal/shiny pair. Alcremie shiny images are shared across creams of the same sweet; this requires explicit mapping, not filename guessing.

## Compatibility design to implement and verify

1. Preserve version-2 numeric captured/shinies and all existing keys. Allocate new numeric keys from a reserved range with a checked-in immutable identity map; never derive identity from display names or mutable list positions.
2. An old generic capture does not establish gender, sweet, pattern, or other previously untracked form. Preserve it as form-unspecified ownership with a clear assignment action. Do not silently copy one old capture to every form or guess Male from the former picture. Define handling for existing regional forms separately where form identity was already exact.
3. Keep browser unknown valid numeric IDs in saves/exports, matching desktop rollback preservation. Validate complete records before changing state; test imports, reload, cross-tab sync, autosave errors, and older-catalog round trips.
4. Give all reviewed concrete forms independent ownership and deterministic HOME positions, six columns × five rows. Filtering leaves positions fixed. Main-list form selectors must target the same keys as HOME and shiny collection.
5. Keep form acquisition records distinct. Generic species hunting methods cannot be relabeled as verified alternate-form methods. Show reviewed form requirements and explicitly unresolved evidence until per-form hunting data is reviewed.

## Implementation and verification remaining

- Reconcile candidate forms against the supplied list, gender differences, HOME storage constraints, and current source coverage; record included/excluded identities and sources.
- Build immutable identity/artwork mappings, download and verify required artwork, retain per-image source URLs and attribution.
- Extend build-catalog.py through a responsible module; regenerate and inspect catalog diffs without unrelated removals. Coordinate hunting producers/consumers and verifier assumptions.
- Implement list selectors, ownership assignment, HOME slots, totals and collection behavior; retain the user's separate counter boxes.
- Verify compatibility and integration with isolated saves, real browser interactions, responsive visual review and source checks. Resolve local Electron sandbox installation ACL failure to enable native/package verification; do not disable sandboxing.
- Update documentation, package allowlists and affected evidence after review; do not refresh checkpoint hashes to hide ongoing drift. No release is authorized by this task alone.

The goal remains active and incomplete. Prior counter edits are preserved. Initial checkpoint drift is main.js/style.css from those counter changes; no baseline hash was refreshed.

## Completed foundation, 2026-10-05

- Pinned four public PokeAPI CSV inputs at `bc92d3b6029ef1abe9e7ad424c400b338f3c11fe`, with exact source URLs and SHA-256 hashes. Fetcher is `audit/fetch-living-dex-reference.py`.
- `python audit/inventory-living-dex.py` verifies input hashes and inventories 1,579 records: 1,422 persistent candidates and 157 battle/mega records. Flags are not final inclusion decisions; Gigantamax or technical forms require independent reconciliation. It asserts 63 Alcremie combinations and unique upstream form IDs.
- Added `collection-codec.js` and wired renderer load/import/storage-sync/save/export. Valid unknown version-2 IDs survive saves and exports without inflating visible counters. Complete decoding precedes replacing any collection state. Protocol and explicit package contents include the new module.
- `node audit/verify-collection-compatibility.cjs` passed newer/older/newer ownership round-trip, unknown shiny capture implication, visible counter isolation, invalid IDs, version rejection and malformed-record handling.
- Six desktop save/updater regression tests passed with `node --test --test-isolation=none desktop/storage.test.cjs desktop/updates.test.cjs`. JavaScript syntax checks passed. This is unit evidence, not native/package verification.
- In-app browser, isolated port 5189: shiny selection updated both counters, reload retained ownership, and clearing captured cleared shiny. Prior real collection was not used. Native launch still has the previously observed sandbox ACL limitation.

Next implementation: reviewed persistent-form identities and artwork mapping, then list selectors and fixed HOME layout. No new form ownership or slots are yet exposed in the runtime.

## Artwork progress, 2026-10-05

- Captured source-page wikitext and source URLs for all 70 Alcremie image files with `audit/review-alcremie-artwork.py`. The API normalizes underscores to spaces; the tool normalizes titles back to registry filenames.
- Downloaded and decoded 70 source PNGs, retaining existing default resized artwork. `audit/alcremie-artwork-download.json` distinguishes original source SHA-256 from local SHA-256; byte equality is not claimed for the pre-existing resized defaults.
- Visually inspected every normal cream/sweet pairing and all seven shared shiny sweet appearances in `audit/artifacts/living-dex/alcremie.png`. Source captions and visible colors/ornaments match the 63 mappings. Three source captions omit default cream/sweet details; the manifest records the visual evidence for those exceptions.
- `python audit/finalize-alcremie-mapping.py` checked caption agreement and wrote the shared generator input `reference/pokeapi/living-dex/alcremie-artwork-map.json`: 63 unique immutable identities/keys, explicit normal/shiny files, and per-image source URLs. Old generic ownership key 869 is not assigned to a guessed cream/sweet.
- New assets expand the artwork directory before catalog regeneration. Baseline image-count verifiers are intentionally not completion evidence for this in-progress state. Remaining form families, ownership assignment, renderer selectors and HOME catalog integration still require implementation and verification.

## First runtime form integration, 2026-10-05

- Added `living_forms.py`, called by `build-catalog.py`, to generate reviewed Alcremie forms from the shared identity/artwork manifest. Regenerated catalog has 1,146 entries, preserving all 1,083 prior keys and adding 63 concrete Alcremie keys. Generic 869 remains form-unspecified. This intermediate state has 39 HOME boxes.
- Every species row now exposes a form selector; selection changes the ownership checkboxes and detail/locate target to that exact key. Regional forms remain accessible through these selectors. Search/status filtering can select the matching form without compacting HOME slots. Main list groups species; HOME/shiny collection remain per-form.
- Browser QA on isolated port 5189 selected Caramel Swirl/Ribbon Sweet (210501), marked shiny, and observed its exact HOME label at Box 33, Row 5, Column 5 with HOME0869R_s.png. Reload and reselect retained its shiny checkbox. Clearing its capture removed its shiny ownership. Desktop-size list/detail visual review passed.
- New form hunting entries remain explicitly unresolved in the renderer. Hunting generation excludes living-form additions from the historical species/regional decoder pipeline so unreviewed species methods are not copied onto them.
- Remaining: other form families including gender variants, explicit assignment of old unspecified ownership, complete reviewed form hunting guidance, responsive/native/package checks, expanded verifier and documentation reconciliation. The requested goal remains incomplete.

## Gender variants, 2026-10-05

- Reviewed the public gender-difference list and captured 204 female image/source captions, normal and shiny, including Hisuian Sneasel. All source female captions explicitly identify female; shiny caption flags were checked separately.
- Downloaded and decoded the female source PNGs with source/local SHA-256 evidence. Visually inspected 101 base-species normal pairs on five labeled contact sheets, and Hisuian Sneasel separately (female shorter head feather). Tiny rear differences are not established by these front views; shiny colors still need a full visual review.
- Added explicit shared mappings and 206 independent gender keys: Male/Female for all 102 dimorphic base species and Hisuian Sneasel. Torchic has separate ownership but shares front art, because its difference is a rear black spot. Other regional forms are not automatically assigned base-species dimorphism.
- Regenerated catalog now has 1,352 records and 46 boxes, with prior keys preserved as gender-unspecified where necessary. Female Pikachu browser QA selected key 300051, persisted shiny ownership across reload, used HOME0025_f_s.png, and located Box 2, Row 2, Column 1. Clearing its capture removed its shiny; original generic/Male ownership is independent.
- `audit/verify-living-dex.cjs` now verifies all 206 gender mappings, image availability, legacy unspecified records and independent Pikachu ownership in addition to the Alcremie checks. Remaining families, assignment workflow, responsive/native/package checks and broader documentation/verifier reconciliation are still unfinished.

## Unown and explicit assignment, 2026-10-05

- Captured 56 source captions and downloaded/decoded normal/shiny artwork for all 28 Unown shapes. Visually inspected A–Z and both punctuation pairs; captions match every shape. Shared mappings preserve generic key 201 as form-unspecified. Catalog now has 1,380 records and 46 boxes.
- Added explicit assignment action in the selected concrete form's detail panel when its legacy unspecified capture exists. Before moving ownership, desktop writes a serialized profile backup; browser writes a uniquely named version-2 local backup. Backup/save failure leaves the in-memory original ownership intact. Shiny ownership moves with captured ownership; unrelated and unknown IDs are preserved. No automatic form guessing.
- Narrow preload method and sender-authorized collection:backup handler invoke the existing backup store. Renderer Node/security settings are unchanged.
- Browser QA, isolated port 5189: marked generic Unown shiny, selected ?, assigned it, observed only ? marked owned and the backup-saved status, confirmed Box 12/Row 1/Column 4, and retained shiny after reload/reselection. Then cleared the test capture. The final unique-backup-name change was syntax/source verified but not separately clicked again.
- Collection compatibility verifier checks assignment preserves its input backup and unknown IDs, moves captured/shiny ownership, and rejects missing captures/same-key assignment. Six desktop tests passed with isolation disabled. Living-dex verifier adds all 28 Unown identities and image mappings.
- Remaining: other persistent form families, per-form evidence/hunting guidance, unspecified-record presentation in HOME/totals, browser backup recovery UI, full responsive/native/package review, and verifier/documentation reconciliation. Goal still incomplete.

## Persistent-form batch, 2026-10-05

- User explicitly selected forms kept outside battle; temporary battle transformations remain excluded. Reviewed 91 concrete forms: Deoxys, Burmy/Wormadam cloaks, Shellos/Gastrodon seas, Rotom appliances, Deerling/Sawsbuck seasons, all 20 Vivillon patterns, five flower colors for Flabébé/Floette/Florges, Pumpkaboo/Gourgeist sizes, Oricorio styles, Lycanroc forms, Toxtricity forms, Maushold families, Squawkabilly colors, Tatsugiri shapes and Dudunsparce segments.
- Captured 182 source captions, downloaded/decoded their PNG pairs and visually inspected all four persistent-form contact sheets. Default labels, flower colors and cloak captions have documented limitations; physical size is supported by captions and pinned dimensions, not scaled thumbnails. Eternal Flower Floette remains unresolved because this registry lacks a paired HOME shiny image.
- `audit/finalize-persistent-mapping.py` verifies local hashes and shiny caption flags, attaches form-specific types from checked-in types.csv, and writes the shared persistent-artwork manifest. Catalog generation adds 91 independent keys, preserving all previous records, for 1,471 records and 50 boxes. Generic old captures remain unspecified.
- `node audit/verify-living-dex.cjs` and `node audit/verify-collection-compatibility.cjs` passed. Catalog regeneration produced the identical SHA-256. `git diff --check` passed with existing line-ending warnings.
- Browser QA on isolated port 5189: selected Wash Rotom, confirmed Electric/Water typing and Box 26/Row 2/Column 2; marked shiny and confirmed owned/shiny option indicators and detail after reload. Cleared it. Selected Vivillon Poké Ball Pattern, marked shiny, located its exact HOME slot at Box 34/Row 1/Column 2 beside Fancy Pattern, with separate ownership. Cleared it and observed both totals return to zero. One select-option attempt used the wrong indicator spacing, timed out, and succeeded after reading the actual option text.
- Updated HOME explanatory text for separate form slots. Broader remaining scope from the preceding sections still applies; this batch does not establish complete living-dex coverage, native/package verification or full hunting evidence. Goal remains active.

## Alternate-form batch, 2026-10-05

- Continued from authoritative current files; checkpoint comparison reports six changed baseline files in the authorized runtime/generation scope. Checkpoint hashes were not refreshed. Prior turn classified as progress: catalog, manifests, artwork evidence and browser checks changed authoritative state.
- Captured 104 source captions and decoded 104 PNGs for 55 candidate forms with `review-alternate-artwork.py`; visually inspected all three normal/shiny sheets and HOME captions. Includes Giratina, Shaymin, red/blue Basculin, Therian trio, Kyurem fusions, Keldeo, ten Furfrou appearances, Zygarde 10/50, Hoopa, seven Minior colors, Magearna, Urshifu styles, Zarude, Calyrex, Ursaluna, Gimmighoul and Ogerpon. Core colors share one shiny image, while ownership keys remain distinct. Artwork does not establish shiny eligibility or HOME transfer restrictions.
- Generalized the review/finalization tools to retain separate batch reports; finalized the shared alternate-form manifest with types/dimensions and local hash checks. Generated 1,526 records, preserving old keys, with 51 fixed HOME boxes. Living-dex verifier now checks all 55 mappings, Rapid Strike typing and distinct Minior normal/shared shiny files. Living-dex and save-compatibility verifiers pass; diff whitespace check passes.
- Fixed two tooling errors before capture: hyphenated Python filename import now uses runpy; Minior alternate colors explicitly select the shared shiny file instead of assuming nonexistent color-specific files.
- Added `check-living-dex-coverage.py` and its candidate report to enumerate snapshot coverage gaps. Classification is explicitly provisional; a PokeAPI flag or an image does not establish an exclusion. Remaining families and technical/default duplicates need reviewed inclusion/exclusion decisions. Browser interactions for this latest batch, broader renderer/native/package QA, legacy unspecified slot/totals presentation and documentation/verifier reconciliation remain outstanding. Goal remains active.

## Type and authenticity forms, 2026-10-05

- Captured 116 public HOME captions and decoded 116 images for 58 forms. Inspected all three type contact sheets: all 18 Arceus and 18 Silvally types, five Genesect drive appearances, Dialga/Palkia base/Origin, Necrozma base/Dusk Mane/Dawn Wings, Enamorus Incarnate/Therian, and both authenticity variants of Sinistea, Polteageist, Poltchageist and Sinistcha. Tea cards use the reviewed rear view to expose the authenticity stamp; `artworkView: back` is recorded.
- Finalization now checks the HOME caption template specifically. Initial finalization failed because a normal Antique Sinistea page mentions its shiny counterpart elsewhere in prose; this did not indicate a wrong image. The corrected template check passed. No catalog output was overwritten by the failed generation attempt.
- Arceus/Silvally type is explicitly derived from the form identity, because cosmetic PokeAPI forms can share the default Pokemon ID/type data. Checked-in type tables remain the input for other forms. The manifest documents this exception.
- Regenerated 1,584 records with prior numeric keys preserved and 53 HOME boxes. Expanded verifier checks 58 mappings, all 18 types for each type family, and Dawn Wings Psychic/Ghost typing. Living-dex and save compatibility verifiers passed; whitespace diff check passed with existing line-ending warnings. Candidate report regenerated: 352 need scope review, 367 exact integrated identities and 157 provisional temporary candidates. These counts include technical/default name mismatches and are not a count of missing physical forms.
- Browser review of the last two batches remains due, as do the prior remaining scopes. Pikachu caps/cosplay, Spiky-eared Pichu and Eternal Flower Floette require appropriate missing-art/shiny handling rather than fabricated image pairs. Goal remains active and full coverage unproven.

## Legacy unspecified presentation, 2026-10-05

- Catalog generation assigns positions only to concrete records. All 156 legacy unspecified IDs remain in the catalog/save decoder and species selectors with null positions; they no longer create duplicate HOME slots. Current concrete layout has 1,428 slots/48 boxes. Filters continue to preserve these catalog positions.
- Renderer HOME pagination and totals use concrete records. A visible pending-assignment message accounts for saved unspecified captures; their ownership/export is preserved, and shiny collection cards remain accessible with an assignment prompt instead of an invented position. Selecting unspecified detail removes the locate button and explains choosing a concrete form.
- Browser QA, isolated port 5189: marked Gender unspecified Pikachu shiny; observed one pending capture, zero concrete captured total, and explanatory detail without a HOME position. Selected Female and assigned; total became 1/1,428 and shiny moved to Female, Box 2/Row 1/Column 2. Cleared the test capture. Selected Fairy Arceus and confirmed Fairy typing with Box 24/Row 1/Column 4.
- `node --check main.js`, living-dex verifier, collection compatibility verifier and whitespace diff check passed. Verifier now asserts null legacy positions and consecutive concrete positions. This changes intermediate positions recorded in earlier QA sections; those older positions are historical evidence, not the current layout.
- Remaining coverage, backup recovery UI, responsive/native/package QA and affected baseline verifier reconciliation still need work. Goal remains active.

## New capture defaults, 2026-10-05

- Main list now defaults to a concrete form, while an owned unspecified record takes priority for assignment. Explicit user form selections still take priority over both defaults.
- Unchecked unspecified captured/shiny controls are disabled with a choose-concrete-form explanation. Existing unspecified ownership can still be cleared or assigned with backup preservation. This avoids introducing new ambiguous captures while keeping old saves accessible.
- Renderer syntax, living-dex mapping and save-compatibility checks passed. Browser interaction review for these latest default/disabled-control changes remains due. The previous goal turn made concrete progress in generation, presentation and browser assignment evidence; full goal remains unfinished.

## Coverage reconciliation and latent patterns, 2026-10-05

- Coverage now resolves stable generated form IDs, preserved standard keys and explicit gender pairs, instead of relying only on names. This reduced 352 apparent gaps to 90 review candidates; it did not establish exclusions or hide unimplemented forms. Catalog evidence is attached to each resolved record.
- Reviewed the supplied form-difference page's Scatterbug/Spewpa section: each has 20 persistent evolution-pattern identities. Added a reproducible shared-art manifest generator and 40 independent collection keys. Appearance is intentionally shared, with labels identifying the future Vivillon pattern. Generic old ownership is unspecified; no pattern is guessed.
- Regenerated 1,624 records and extended mapping verifier to cover the 40 labels/keys and shared images. Living-dex verifier passed. Current candidate ledger has 52 needs-scope-review records after the addition; temporary flags remain provisional. New latent slots, default-selector behavior and disabled unspecified controls still require browser review. Other outstanding scopes remain as previously recorded; full goal remains active.

## Ability variants and cap Pikachu, 2026-10-05

- Extended shared-art mappings to Standard/Battle Bond Greninja and Standard/Own Tempo Rockruff, based on the reviewed source's technical-form sections. Four independent keys preserve legacy generic ownership as unspecified; temporary Ash transformation is excluded from this addition.
- Captured eight cap Pikachu normal source captions/images. Visually inspected all eight hats against their caption identities. Added separate ownership keys for Original, Hoenn, Sinnoh, Unova, Kalos, Alola, Partner and World caps. The captured registry provides no separate shiny renders; manifest explicitly records unavailable shiny artwork, and renderer displays normal art with an unavailable-art explanation and accurate alt text. This is an artwork statement, not shiny-eligibility evidence.
- Catalog now has 1,636 preserved/concrete records; coverage report has 42 candidates needing scope review. Expanded mapping verifier covers all eight cap images and missing-art flags; renderer syntax and living-dex checks passed. Save compatibility checks passed before the cap renderer addition; broader runtime/browser checks remain due.
- Other remaining scopes persist, including cosplay/spiky-ear/Eternal Flower artwork, technical variants/dispositions, backup recovery, responsive/native/package QA and affected verifier/documentation reconciliation. Goal remains active.

## Totem-like and Power Construct forms, 2026-10-05

- Based on the reviewed technical-form sections, added eleven obtainable Totem-like identities and eleven corresponding standard-size identities, plus two persistent Power Construct Zygarde identities. New shared-art manifest is generated from pinned form/Pokemon snapshots, with exact Totem metrics. Alolan Raticate/Marowak use their regional artwork/types. Totem forms do not retain their size when transferred to HOME; slots are organizational collection records, not a claim that every form transfers unchanged.
- Preserve existing generic standard-size captures as unspecified instead of guessing that an old capture was a Totem. New concrete normal-size/Totem records have separate keys. Zygarde Power Construct variants assign from original generic species capture and do not modify already-selected shape keys.
- Generator and expanded mapping verifier passed; catalog now has 1,660 records. Candidate coverage report regenerated with 29 unresolved candidates. Shared-art appearances do not establish shiny eligibility; hunting restrictions remain unreviewed for the new technical entries.
- Browser testing for the recent batches, remaining non-HOME artwork, final scope dispositions, backup recovery UI and broader verification remain outstanding. Goal stays active.

## Mothim and Minior state reconciliation, 2026-10-05

- Reviewed the supplied source's technical Mothim and Minior sections. Added all three persistent Mothim Burmy-origin identities with intentionally shared existing artwork and independent keys. Old generic Mothim capture remains unspecified.
- Added reproducible disposition generation for seven Minior meteor states. Each resolves to its fixed core-color ownership slot; shell/core transitions do not create duplicate ownership records. The coverage report includes explicit target keys, reason and source for these represented states.
- Catalog generation/mapping verifier and save-compatibility checks passed; whitespace diff check passed. Catalog has 1,663 records. Candidate report now has 20 unresolved candidates, seven represented states and 157 still-provisional temporary candidates. No claim of full coverage is made from those counts.
- Recent additions still need browser review, and all previously documented remaining runtime/package/recovery/artwork scopes persist. Goal stays active.

## Non-HOME artwork discovery, 2026-10-05

### Pichu and disposition follow-up

- Reviewed source evidence for unused unobtainable ???-type Arceus and unobtainable Eternamax boss/animation form. Recorded explicit exclusions with source URLs. Eight Koraidon/Miraidon traversal/power states are represented by the same partner ownership slot; state aliases are distinct from exclusions and retain target keys/reasons.
- Discovered Spiky-eared Pichu's HGSS APNG from the actual Pichu article image inventory, captured source caption/hash and inspected its ear sprite separately. Added Spiky-eared and standard Pichu keys, preserving old generic key 172 as unspecified. Spiky-eared is female/shiny-locked based on reviewed source; normal artwork is explicitly used when shiny artwork is unavailable.
- Generator and expanded mapping verifier passed. Catalog now has 1,672 records; candidate ledger has two unresolved Let’s Go partner forms, 15 represented states and two reviewed unobtainable exclusions. Temporary-state flags still require final reconciliation, and browser/native/package/full coverage verification remain incomplete. Goal remains active.

### Integration follow-up

- Finalized seven mappings from the reviewed source captions/art sheet with local hash validation. Added six Cosplay Pikachu appearances (female) and Eternal Flower Floette to the runtime catalog and fixed HOME positions. Non-HOME images retain per-image source URLs and explicit unavailable-shiny-art metadata.
- Cosplay forms carry reviewed shiny-lock metadata and source. Renderer disables unchecked shiny controls for these forms, retains the ability to clear pre-existing imported shiny ownership, and rejects assignment from a shiny generic record to a locked target without modifying it. Existing unknown/save IDs remain preserved.
- Generator, renderer syntax, expanded living-dex verifier and save-compatibility verifier passed. Catalog has 1,670 records; coverage report has 13 unresolved scope candidates. Browser testing for the new lock controls and assignments remains due; full goal remains active.

- Captured source-page image inventories for Cosplay Pikachu, Spiky-eared Pichu and Floette. Following Floette's article redirect returned its actual form artwork references.
- Downloaded/decoded seven source-linked PNGs with source captions, URLs and SHA-256 evidence: six Cosplay appearances and Eternal Flower Floette. Visually reviewed special.png. Five costumes and Eternal Flower use official illustrations; uncostumed Cosplay uses an ORAS game render. Costume captions are generic; filenames, source-page placement and visual review support their mapping together.
- Assets are staged only; catalog mappings and eligibility handling remain due. Source states ORAS Cosplay is female and cannot be shiny. Spiky-eared Pichu still needs suitable game artwork/sprite. Full goal remains active.

## Browser recovery and default QA, 2026-10-05

- Added a browser-only recovery panel listing validated pre-assignment backups by timestamp/capture count. Restore validates the selected record, saves the current collection as a new backup, persists the restored version-2 record, then replaces in-memory ownership. Invalid records/storage failures leave ownership intact. The panel refreshes after assignment/restoration; desktop import ignores clicks while assignment is active.
- Browser QA on isolated port 5189 opened the recovery panel and restored its saved Pikachu legacy capture. Observed restore success, one pending assignment and retained ownership; reassigned Female Pikachu, observed one concrete capture, and cleared the fixture. The current collection was saved in another recovery backup before restore.
- QA found fresh Pikachu defaulting to Original Cap due numeric key ordering. Corrected concrete default preference to standard Male for gender-dimorphic base species. Reload verified Male selected by default; unowned Form unspecified capture control is disabled. Selected World Cap, marked shiny and verified explicit missing-shiny-art detail, then cleared it. No real user collection was used.
- Renderer syntax/save compatibility/whitespace checks passed before the final default preference adjustment. Browser interaction passed for that final adjustment. Broader runtime, responsive/native/package checks and catalog scope gaps remain unfinished. Recovery UI is now implemented and exercised; goal remains active.

### User-directed Spiky-eared Pichu exclusion

- User explicitly excluded Spiky-eared Pichu because it cannot transfer from HGSS to HOME. Removed its concrete catalog mapping and recorded excluded-user-scope in the reproducible disposition producer. Retained standard Pichu and legacy ownership compatibility.
- Regenerated catalog: 1,671 records. Living-dex and collection-compatibility checks passed. Existing checkpoint drift remains expected from the ongoing authorized implementation; no checkpoint hashes refreshed.


### HOME-only storage scope, user clarification

- User chose only forms HOME can store. Added reproducible home-storage-scope.json input and generator filtering. Removed six Cosplay Pikachu appearances, six fused Kyurem/Necrozma/Calyrex forms and eleven Totem-like entries; partner Pikachu/Eevee and Spiky-eared Pichu remain excluded. Totem transfer conversion reviewed against the referenced form-differences page. Standard-size counterparts remain.
- Retired concrete IDs remain preserved as unknown IDs by the version-2 collection codec; no ownership is silently assigned to another form. All 1,083 legacy catalog records remain. Current catalog has 1,648 records and 1,475 concrete HOME slots.
- Living-dex, data and compatibility checks passed. Data verifier now distinguishes reviewed legacy hunting records from 565 unresolved new-form guides instead of assuming every catalog expansion has verified hunting guidance. Transfer-reset/held-item reconciliation, browser/native/package verification and documentation remain due; goal and exhaustive audit remain incomplete.


### HOME transfer-reset reconciliation

- Reviewed HOME registration versus storage rules and held-item removal, plus Arceus/Origin resets and Ogerpon mask requirements. Reproducible producer audit/reconcile-home-transfer-resets.py excludes 44 reset appearances: 34 non-Normal Arceus/Silvally types, four Genesect Drives, three Origin forms and three Ogerpon masks. Artwork manifests retain historical reviewed mappings; generator applies the HOME-only scope before adding runtime forms.
- Current catalog: 1,604 records, 1,431 concrete HOME slots. Living-dex and data verifiers passed. Isolated browser QA on port 5189 confirmed Arceus only offers unspecified/Normal Type, Ogerpon unspecified/Teal Mask, Pichu unspecified/Standard; selected Normal Arceus shows Box 23, Row 4, Column 6. Saved screenshot audit/artifacts/home-only-arceus.jpg. No collection ownership changed.
- Remaining: broader scope reconciliation and runtime/package checks. HOME Pokédex recognition alone does not establish whether a latent identity is retained in storage; do not exclude those merely for lacking a separate Pokédex entry.


### PokéPC working completeness reference and deferred verification

- User supplied https://pokepc.net/livingdex and explicitly asked to use its list to save effort, marking unverified details for later. Saved all 1,394 occupied labels from Grouped by Regions (Optimized), with source HTML hash, in audit/pokepc-living-dex-reference.json. This reference is a working completeness baseline, not new independent gameplay evidence.
- audit/compare-pokepc-reference.py maps all labels to all 1,025 species; no family falls below the reference distinct-label count. audit/pokepc-living-dex-comparison.json records reference labels, concrete catalog slots and explicit unverified identity/transfer status per family. Exact identity matching remains required for interface completion; independent gameplay/transfer/artwork/hunting verification can be deferred under the user's instruction.
- Fixed legacy encounter mapper to exclude new living-form ownership records from its one-key-per-game-form mapping, preserving reviewed original route outputs. Artwork verifiers now read additional staged evidence, distinguish recorded local/source hashes from byte-identical baseline comparisons, and allow identical pairs only where separate shiny artwork is explicitly unavailable.
- python audit/check-project.py passed 36/36. Desktop storage/updater checks passed 6/6 with isolation disabled. Full audit remains incomplete; no release published.

### Interface completion and saved National Dex reference — 2026-10-05

- Saved the user's additional https://pokepc.net/pokemon reference for species names and National Dex numbers in the reproducible comparison report. That page also contains temporary transformations, which remain outside the requested HOME storage scope.
- Exact label matching now covers every named form in the saved PokéPC living-dex layout: 1,025 species families, no unmatched labels or missing reference forms. The report separately lists 43 concrete catalog entries absent from that layout with explicit pending HOME identity verification. All families retain independent transfer-verification limitations; reference matching is not gameplay evidence.
- Source interface now has a selector for each of 1,025 species, independent form ownership, 1,431 fixed HOME slots across 48 boxes, and separate captured/shiny counter boxes. All 1,083 legacy keys are retained; 173 unspecified records require explicit backed-up assignment rather than guessed ownership.
- Local Windows x64 NSIS build completed without publishing. Packaged isolated QA passed capture/shiny persistence, independent male/female Pikachu ownership, 1,025 selectors, counter ordering at 1280/420 widths, fixed filtered HOME positions, six-column/five-row layout, offline bundled artwork, narrow preload access and protocol file denial. Screenshots reviewed at both widths. The first smoke attempt failed because of a test-script quoting defect; corrected smoke passed with no renderer errors.
- Evidence and exact local build hashes: living-dex-completion-qa.json; native fixture output and screenshots: artifacts/living-dex-desktop-20261005-r2/. Living-dex verifier passed and desktop storage/updater tests passed 6/6. The earlier project pass remains 36/36. Checkpoint drift is preserved and reported rather than hidden by refreshing hashes.
- The requested living-dex interface work is complete against the user-authorized working reference. Independent HOME/artwork/hunting review remains marked for later, as requested. Exhaustive audit remains incomplete. No real installation/update cycle or public release is asserted.

