# ShinyDex 1.1.0

Release tag: `v1.1.0`. Upload approved by the user on 2026-10-05.

## Release description

ShinyDex now supports a living dex with a form selector for each of the 1,025 species, independent captured/shiny ownership, and 1,431 fixed HOME slots across 48 boxes. The captured and shiny counters appear in separate boxes with their own totals. HOME filtering preserves each slot's position.

The catalog uses the saved PokéPC living-dex layout as its working completeness reference. Every named reference form has a matching app slot. Temporary battle transformations and HOME-excluded forms, including Spiky-eared Pichu, are excluded. The 43 additional catalog distinctions and unfinished independent transfer, artwork and hunting checks remain marked for later review.

Existing collections remain version 2. Legacy captures whose forms were unspecified are preserved and require an explicit form assignment, with a backup written before assignment. The upgrade/downgrade/re-upgrade checks preserved all 1,083 legacy IDs and all 521 added IDs; native renderer tests covered male/female Pikachu, Alcremie, shiny ownership and edits made in 1.0.0.

**Before rolling back, export a backup using 1.1.0.** The 1.0.0 desktop autosave retains newer forms, but its Export backup button omits unrecognized forms. New form ownership reappears when returning to 1.1.0 using the same desktop save. Browser and desktop profiles remain separate.

Validation: 36 project checks, six desktop storage/updater tests, packaged 1.1.0 smoke test, and isolated 1.0.0 → 1.1.0 → 1.0.0 → 1.1.0 renderer/storage round trip passed. The earlier BDSP roaming and encounter-condition source fixes are included. No claim is made about a real NSIS installation/update cycle or clean-machine behavior; the exhaustive hunting audit remains incomplete.

## Upload contents

- New exact tag `v1.1.0`, release title `ShinyDex 1.1.0`, using the approved source commit.
- `ShinyDex.exe`, `latest.yml`, `ShinyDex.exe.blockmap`, `ShinyDex.exe.sha256` from `dist/desktop/`.
- Verify hashes against `release-1.1.0-ready.json` before upload. Preserve all existing release assets.
- Publish only after explicit user confirmation. Update the README preparation status after publication.
