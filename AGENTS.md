# ShinyDex project rules

Established 2026-10-05 from the current source, README, audit checkpoint, and regression checks. Applies throughout this repository. Follow explicit current user instructions when they change task scope. This file is a working change-control policy, not a claim that the application or exhaustive audit is complete.

## Before changing anything

- Canonical audit location: `audit/`. Read `audit/README.md` for the directory map and current commands. All new audit reports, inventories, evidence snapshots, QA artifacts and audit/verifier tooling belong there. Do not recreate their former root/Archive/windows locations from stale chat history. Keep runtime files and shared data-generation inputs in their documented source locations; update audit producers/consumers together.

- Read `README.md`, `audit/AUDIT-CHECKPOINT.md`, `audit/REMAINING-AUDIT.md`, and affected audit reports. For area work also read the relevant entries in `audit/REMAINING-AREAS-AUDIT.md` and its JSON ledger; distinguish confirmed remaining scopes from investigation candidates.
- Inspect Git status and preserve existing work. The existing remaining-area ledger is included in the user-authorized audit-folder migration; preserve its findings and distinguish its confirmed scopes from investigation candidates.
- Identify the affected runtime, data producers, consumers, save format, evidence, and package contents before editing. Check for additional scoped AGENTS.md files as the project grows.
- Run `python audit/check-audit-checkpoint.py` before relying on checkpoint evidence. Drift calls for review of the affected scope; do not refresh hashes merely to hide changes.
- Keep changes limited to the authorized task. Repository descriptions of outstanding publication work do not alone authorize a new release or an exhaustive audit in every chat.

## Architecture and dependencies

- Current product: Electron desktop app in `desktop/`; shared renderer in `index.html`, `main.js`, `style.css`, and `updater.js`. Desktop runs through `shiny://app` without a localhost server or TCP port.
- `server.cjs` is browser development only. `windows/` and `Archive/` preserve historical browser previews and are excluded from the desktop package. Do not substitute their launcher for Electron.
- `package.json` and `pnpm-lock.yaml` define dependencies together. Current pins: Electron 44.5.1, electron-builder 26.15.3, electron-updater 6.8.9. Treat dependency upgrades as explicit changes requiring relevant runtime/build verification; avoid incidental upgrades or another package manager's lockfile.
- Python data tools depend on checked-in CSV/JSON/reference snapshots; image tooling needs Pillow. PKHeX resources are pinned to `542111fc8584ff29c9d1455553b8acd0e1f8a59a`. Preserve provenance and snapshots; decoders read resources without executing upstream C#.

## Collection and interface invariants

- Keep stable species/form `key` values, separate form ownership, and version-2 collections. Shiny ownership implies captured ownership; clearing captured clears shiny.
- Preserve `%APPDATA%\ShinyDexDesktop\collection-v2.json`, serialized atomic writes, validation, backups before import/update, and unknown newer IDs during desktop rollback saves. Never use real user collections for QA.
- Browser storage uses `shinydex-collection-v2` with legacy shiny migration and cross-tab synchronization. Browser and desktop profiles are separate; do not silently merge them.
- Preserve autosave error feedback, portable export/import, malformed-save protection, and recovery behavior. A schema/key/profile change requires an explicit compatibility and migration plan plus tests.
- HOME uses catalog positions: six columns, five rows, 30 slots. Filtering must not compact positions. Preserve silhouettes, owned shiny artwork, labels, separate captured/shiny controls, and the owned-shiny collection view.
- Current catalog baseline: 1,025 base species, 58 regional entries, 1,083 unique keys, 37 boxes, 2,166 normal/shiny images. Intentional catalog expansion must update affected checks and evidence; these counts are not permanent ceilings.

## Data generation and evidence

- Change hunting rules in `build-hunts.py` or the responsible imported module, then regenerate `hunts.json`. Change catalog generation in `build-catalog.py`, then regenerate `data.json`. Inspect generated diffs for unrelated removals and changes; preserve pipeline ordering and form mappings.
- Trace catalog changes through ownership, HOME positions, form-specific hunting records, artwork, audits, and verifier assumptions. Trace hunting changes through encounter/evolution/breeding producers, exception/supersession rules, and source-link rendering.
- Encounter presence, missing methods, inventory counts, and passing tests do not establish shiny eligibility, shiny locks, complete coverage, or actual gameplay. Do not replace unresolved evidence with assumptions.
- Verify game/version, form, room/terrain, time/weather, story access, parent acquisition/transfers, and method prerequisites where affected. Retain precise reviewed details and documented uncertainties.
- For event changes, verify authoritative announcements and distinguish announcement, distribution, redemption, and acquisition windows, regions, time zones, and ended versus usable historical content. Check current external facts when the task depends on them.
- Preserve source URLs, input hashes, reviewed exclusions, evidence scope, and unresolved work. Update affected reports/checkpoint only after review. Keep `auditComplete` false while full-goal requirements remain unresolved.

## Desktop security and releases

- Preserve sandboxing, context isolation, disabled renderer Node integration, narrow preload IPC, sender authorization, protocol file allowlist, CSP, navigation restrictions, and denied permission requests. New resources/links may require coordinated protocol, package, and external-domain allowlist changes.
- Bundle runtime artwork and data for offline use. Keep package contents explicit; exclude reference tooling, historical launchers, secrets, and user saves.
- Preserve app ID, product/profile identity, uninstall save retention, and compatible rollback behavior.
- Release discovery accepts compatible public exact `vX.Y.Z` tags starting at 1.0.0, trusted repository asset URLs, and immutable per-release feeds. Retain version verification, manifest SHA-512 verification via electron-updater, GitHub SHA-256 digest verification, backup-before-install, and usable offline/failure behavior.
- For an authorized release: increment the package version consistently with the lockfile, build/verify Windows x64 NSIS output, and publish the exact tag with `ShinyDex.exe`, `latest.yml`, blockmap, and SHA-256 checksum. Do not replace existing release assets. Distinguish checked-in source from the exact installer version/hash containing it.
- Preserve attribution, per-image sources, `THIRD_PARTY_NOTICES.md`, `ATTRIBUTIONS.txt`, bundled notices, and reference licenses. No blanket MIT license applies to the project or third-party material.

## Verification by change scope

- Desktop save/updater changes: `pnpm test:desktop`. If sandbox process spawning returns EPERM, use `node --test --test-isolation=none desktop/storage.test.cjs desktop/updates.test.cjs` on a supporting Node runtime; report the execution limitation accurately.
- Renderer changes: affected source checks plus browser/desktop interaction and visual review for the changed behavior, including relevant filters, ownership, persistence, and responsive HOME layout.
- Catalog/artwork changes: affected data/form/image checks. Fresh upstream comparison or visual identity review is required when source artwork changes, not for unrelated edits.
- Hunting changes: relevant `verify-*.py` checks and source-rendering checks. `python audit/check-project.py` runs all checked-in verifiers and refreshes `audit/project-checks.json`; individual verifiers can also write reports, so inspect their resulting diffs.
- Packaged desktop/runtime changes: build and smoke test using `SHINYDEX_DESKTOP_QA=1` and an explicitly isolated `SHINYDEX_DESKTOP_QA_DIR`. Unit tests do not prove real NSIS installation, update, downgrade, restart, or clean-machine behavior.
- Recheck completed work only when changes affect it. Record commands, results, limitations, and failures; do not claim historical report results as tests just run.

## Baseline and known uncertainty

- On 2026-10-05, checkpoint comparison reported zero changed/missing baseline files. The existing project report records 33/33 passing checks; the exhaustive hunting audit remains incomplete.
- Six desktop storage/updater tests passed during policy creation with test isolation disabled. Default test-runner process spawning was blocked by sandbox EPERM.
- Installer evidence reconciled on 2026-10-05: `audit/desktop-qa.json` records historical 1.0.0 installation/installed-app smoke/uninstall checks. The later audit build has win-unpacked smoke evidence only. Its refreshed NSIS installer and real public update/downgrade/restart/save-persistence cycle remain unverified; controlled fixtures do not establish those results.
- Outstanding scope includes historical events/GO/locks, room/form/access and conditional encounter coverage, breeding/evolution acquisition/transfers, browser/native runtime gaps, and final attribution/code review. Follow the remaining-work ledgers rather than restarting completed audits.
