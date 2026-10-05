# ShinyDex audit workspace

All audit reports, checkpoints, remaining-work inventories, audit/reference JSON snapshots, audit and verification scripts, and QA artifacts live in `audit/`. This is the canonical location in the GitHub repository and shared checkout. Read the root [project rules](../AGENTS.md) before resuming work from another chat.

- [Continuation checkpoint](AUDIT-CHECKPOINT.md) and [machine-readable baseline](audit-checkpoint.json).
- [Remaining audit scope](REMAINING-AUDIT.md) and [remaining area ledger](REMAINING-AREAS-AUDIT.md).
- Reports and source snapshots: JSON files in this folder. Paths recorded in JSON are repository-relative unless their report explicitly specifies another base.
- Contact sheets, screenshots, reviewed Radar maps and browser QA fixtures: `artifacts/`; independent audit-only CSV comparisons: `inputs/`; historical browser-launcher QA: `windows/`. Contact-sheet manifest filenames are relative to their `artifacts/image-review/` directory.
- [Migration baseline](migration-baseline.json) preserves old-to-new paths and hashes before the 2026-10-05 move. A location change does not establish new scientific or gameplay findings.

Run from the repository root:

```powershell
python audit/check-audit-checkpoint.py
python audit/check-project.py
python audit/audit-dexnav-coverage.py
python audit/audit-event-inventory.py
python audit/build-image-review.py
```

Individual Python/CJS audit tools also resolve shared inputs from the repository root when launched from another directory. `check-project.py` discovers the moved `audit/verify-*` checks; historical launcher verifiers remain separate and require the old launcher build.

Runtime `data.json`, `hunts.json`, artwork, desktop/browser code, package files and collection saves remain outside this folder. Runtime-data builders and their shared Python modules, CSVs and pinned `reference/` resources retain their existing source locations; their audit JSON reads/writes point here. Rebuild with `python build-hunts.py` or `python build-catalog.py` from the repository root.

Create new audit material here; do not recreate root-level reports or use stale commands from older chat history. Update producers, consumers, report links, and checkpoint paths together. Preserve existing findings and their limits. Only refresh affected checkpoint hashes after reviewing resulting changes. The exhaustive audit remains incomplete.
