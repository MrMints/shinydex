# Audit continuation checkpoint

Checkpoint: 2026-10-04. The exhaustive audit remains incomplete.

Run `python check-audit-checkpoint.py` to detect changed or missing baseline files. It reports drift only and never certifies completion.

Use `audit-checkpoint.json` to identify the source baseline, input hashes, evidence reports, and installer scope. Git history identifies the commit containing each checkpoint. Use `REMAINING-AUDIT.md` for unfinished requirements. Do not infer completion from a passing verifier, a dated route, or an inventory count.

## Where work stopped

Ramanas Park now has access, slate prices and room instructions for all 26 catchable stationary routes. The minimum Ho-Oh unlock condition still conflicts between secondary sources; direct gameplay reset/targeting verification remains open. See `bdsp-ramanas-review.json`.

The latest pass added officially documented North American historical shiny gifts from the 2017–2019 and 2021 archives, including region-specific Zacian/Zamazenta windows and Toxtricity's Wild Area prerequisite. Follow `north-america-gift-review.json` for original campaign prerequisites still requiring review. These official archives are incomplete: the 2016 page lists only Magearna, and the 2020 page omits the independently verified shiny Zeraora reward.

The latest archive pass also found a confirmed official source conflict: the 2025 summary uses Wo-Chien raid dates for the gift period. The detailed result announcement confirms the existing August 8–September 30 UTC gift dates. See `scarlet-violet-event-review.json` before using year archives for future updates. The 2024 archive does not cover all championship rewards; those announcements still require direct review.

The source and packaged executable passed the native runtime smoke check. Failed updater transactions were tested with the real save store. Actual NSIS installation, update, downgrade, restart, and save persistence remain unverified. A refreshed public installer remains outstanding.

Historical Max Raid, Tera Raid, outbreak, GO and gift evidence remains unfinished. `pending-event-review.json` is a reproducible research inventory; its decoded indices are not unique official event identifiers. BDSP, ORAS, SOS, Pelago, older Radar, parent acquisition/transfer, and Z-A Feebas edge cases retain the gaps documented in their reports and remaining-work checklist.

## Resume after a new game or update

1. Read this checkpoint, the remaining scope, and the affected evidence reports. Compare current input hashes and Git changes with the checkpoint before relying on old findings.
2. Record the new game, patch, catalog revision, official announcement dates, regions, and distribution/redeem windows. Distinguish announced, active, ended, and acquired research that remains usable.
3. Review changed species, forms, locks, encounters, access prerequisites, evolution, breeding, transfers and event bonuses against independent evidence. Treat decoded encounter presence as insufficient proof of shiny eligibility or working gameplay.
4. Preserve stable ownership keys and unknown newer IDs. Test changed save behavior across the relevant version pair. Review bundled artwork and HOME ordering only where the catalog or assets changed.
5. Run checks whose scope covers the changes. Record commands, results, limitations and source references. Separately record source publication and the exact downloadable installer version/hash.
6. Update the checkpoint hashes and reports after review. Retain unresolved findings and prior evidence in Git. Only set `auditComplete` true after every full-goal requirement is independently established; leave a dated baseline and explicit next-update triggers even then.

An unchanged hash proves only that a file is unchanged. It does not establish that its content was correct or that an external event is still available.
