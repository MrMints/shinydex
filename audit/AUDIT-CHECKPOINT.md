# Audit continuation checkpoint

Checkpoint: 2026-10-04. The exhaustive audit remains incomplete.

Release update, 2026-10-07: [ShinyDex 1.3.0](https://github.com/MrMints/shinydex/releases/tag/v1.3.0) publishes the offline game-specific Pokédex description card and linked hunting filters from source commit `87fb9ef`. [Release evidence](release-1.3.0-ready.json) records Windows x64 NSIS build, packaged smoke, 37/37 project checks, six desktop tests, unchanged save/schema/catalog/hunting inputs, all four public asset digests and verified public update metadata. Real NSIS installation/update/restart cycles and exhaustive hunting review remain unverified. Existing checkpoint hashes remain preserved.

Release update, 2026-10-07: [ShinyDex 1.2.0](https://github.com/MrMints/shinydex/releases/tag/v1.2.0) publishes the responsive selection workspace, form-image galleries, type badges and hunting-header fixes from source commit `4c67c1d`. [Release evidence](release-1.2.0-ready.json) records all four public asset digests, Windows x64 NSIS build, packaged smoke, 36/36 project checks, six desktop tests and twelve directed packaged-storage compatibility pairs. Renderer checks cover common monitor sizes and mobile stacking. Real NSIS installation/update/restart cycles and exhaustive hunting review remain unverified. Existing checkpoint hashes remain preserved.

Release update, 2026-10-07: [ShinyDex 1.1.2](https://github.com/MrMints/shinydex/releases/tag/v1.1.2) publishes the save-status and Standard-only selector cleanup. [Release evidence](release-1.1.2-ready.json) records verified installer assets, packaged smoke and twelve directed save-compatibility pairs across 1.0.0�1.1.2, plus actual renderer upgrade/rollback/reload/export fixtures. 1.0.0 exports still omit unknown form IDs; export from a newer version before rollback. Real NSIS update/restart cycles remain unverified. Existing checkpoint hashes remain preserved.

Release update, 2026-10-05: user-approved [ShinyDex 1.1.0](https://github.com/MrMints/shinydex/releases/tag/v1.1.0) publishes the living-dex source at `8e6809dcd4633c923fb7f2e5f8d89d2eca011163`. [Release evidence](release-1.1.0-ready.json) records the exact installer SHA-256, public asset/feed verification, packaged smoke pass and isolated 1.0.0 → 1.1.0 → 1.0.0 → 1.1.0 save checks. Older desktop autosaves retain newer form IDs, but 1.0.0 exports omit them; export in 1.1.0 before rollback. Real NSIS update/downgrade cycles remain unverified. Independent HOME/artwork/hunting review remains deferred under the user's working-reference instruction. The earlier audit hash baseline remains preserved and reports source drift; this release does not certify exhaustive audit completion.

Location migration: 2026-10-05. Audit data, tooling and QA artifacts now live in `audit/`; read [the directory guide](README.md) before resuming from older chat instructions. `migration-baseline.json` preserves former paths and hashes. Checkpoint hashes were refreshed only for reviewed path changes and regenerated local verification evidence; no new hunting coverage or installer verification is asserted.

Run `python audit/check-audit-checkpoint.py` to detect changed or missing baseline files. It reports drift only and never certifies completion.

Use `audit/audit-checkpoint.json` to identify the source baseline, input hashes, evidence reports, and installer scope. Git history identifies the commit containing each checkpoint. Use `audit/REMAINING-AUDIT.md` for unfinished requirements. Do not infer completion from a passing verifier, a dated route, or an inventory count.

## Where work stopped

The overworld interaction review added missing Drifloon, Spiritomb and Rotom triggers to six BDSP routes. The Mesprit/Cresselia decoder defect is now corrected: both are roaming hunts with release-site and pre-release reset guidance. See `audit/bdsp-roaming-review.json`; KO/Champion respawn behavior remains unverified. See `audit/bdsp-interaction-review.json` for this and retained timing/NPC gaps.

The official BDSP Unown review corrected both game routes to cave room encounters and documented letter targeting plus the 26-letter punctuation chamber prerequisite. See `audit/bdsp-unown-review.json`; exact rates/levels and older-game form requirements remain open.

Ramanas Park now has access, slate prices and room instructions for all 26 catchable stationary routes. The minimum Ho-Oh unlock condition still conflicts between secondary sources; direct gameplay reset/targeting verification remains open. See `audit/bdsp-ramanas-review.json`.

The latest pass added officially documented North American historical shiny gifts from the 2017–2019 and 2021 archives, including region-specific Zacian/Zamazenta windows and Toxtricity's Wild Area prerequisite. Follow `audit/north-america-gift-review.json` for original campaign prerequisites still requiring review. These official archives are incomplete: the 2016 page lists only Magearna, and the 2020 page omits the independently verified shiny Zeraora reward.

The latest archive pass also found a confirmed official source conflict: the 2025 summary uses Wo-Chien raid dates for the gift period. The detailed result announcement confirms the existing August 8–September 30 UTC gift dates. See `audit/scarlet-violet-event-review.json` before using year archives for future updates. The 2024 archive does not cover all championship rewards; those announcements still require direct review.

The source and later local win-unpacked executable passed the native runtime smoke check. Failed updater transactions were tested with the real save store. Historical 1.0.0 evidence in `audit/desktop-qa.json` records installer exit code 0, an installed-app smoke pass, and test uninstall exit code 0; update/downgrade calls used controlled fixtures. That earlier result does not verify the refreshed audit build's NSIS installer. Real public update/downgrade, restart and collection persistence across that cycle, and clean-machine Windows/SmartScreen prompts remain unverified. A refreshed public installer remains outstanding.

Documentation reconciliation, 2026-10-05: the earlier installation evidence was recorded in Git commits `009f6d0` and `5286502`; the later win-unpacked smoke scope was recorded in `518c3dc`. No new installation test was performed for this reconciliation.

Historical Max Raid, Tera Raid, outbreak, GO and gift evidence remains unfinished. `audit/pending-event-review.json` is a reproducible research inventory; its decoded indices are not unique official event identifiers. BDSP, ORAS, SOS, Pelago, older Radar, parent acquisition/transfer, and Z-A Feebas edge cases retain the gaps documented in their reports and remaining-work checklist.

## Resume after a new game or update

1. Read this checkpoint, the remaining scope, and the affected evidence reports. Compare current input hashes and Git changes with the checkpoint before relying on old findings.
2. Record the new game, patch, catalog revision, official announcement dates, regions, and distribution/redeem windows. Distinguish announced, active, ended, and acquired research that remains usable.
3. Review changed species, forms, locks, encounters, access prerequisites, evolution, breeding, transfers and event bonuses against independent evidence. Treat decoded encounter presence as insufficient proof of shiny eligibility or working gameplay.
4. Preserve stable ownership keys and unknown newer IDs. Test changed save behavior across the relevant version pair. Review bundled artwork and HOME ordering only where the catalog or assets changed.
5. Run checks whose scope covers the changes. Record commands, results, limitations and source references. Separately record source publication and the exact downloadable installer version/hash.
6. Update the checkpoint hashes and reports after review. Retain unresolved findings and prior evidence in Git. Only set `auditComplete` true after every full-goal requirement is independently established; leave a dated baseline and explicit next-update triggers even then.

An unchanged hash proves only that a file is unchanged. It does not establish that its content was correct or that an external event is still available.
