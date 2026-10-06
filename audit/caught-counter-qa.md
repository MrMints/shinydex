# Pokémon caught counter — 2026-10-05

Added the captured ownership total immediately left of the shiny total. Both use the full catalog denominator and count regional forms separately. Save format and ownership rules are unchanged.

Verification performed:
- `python audit/check-audit-checkpoint.py` before editing: zero changed/missing baseline files; exhaustive audit remains incomplete.
- `node --check main.js` and `node --check desktop/smoke.cjs`: passed.
- In-app browser on isolated QA origin `http://localhost:5189`: empty 0/0 totals; captured checkbox produced 1/0; shiny checkbox produced 1/1; reload retained 1/1 after renderer initialization; clearing captured produced 0/0; search filtering left global totals unchanged.
- Visually reviewed normal browser layout and 390×844 viewport. Mobile DOM bounds confirmed captured total left of shiny total, same row, and within viewport. Temporary viewport override reset.
- Native source smoke attempted with `SHINYDEX_DESKTOP_QA=1` and isolated `audit/artifacts/caught-counter-qa` profile. Electron failed before renderer initialization because Windows sandbox ACLs deny access to its local installation. Shell exit code 0 did not establish a pass. Native assertions added for counters and 1280/420 widths remain unexecuted.

No installer build, release, or real user collection used for QA. Existing browser collection on port 5173 was only viewed; interactions used the separate empty QA origin.

## Follow-up: separate boxes

Split captured and shiny summaries into separate bordered boxes, captured on the left. Each has its own progress bar and completion percentage underneath. Browser interaction on the isolated QA origin confirmed a normal capture shows 1/1,083 and 0.1% captured complete while the shiny box remains 0/1,083 and 0.0%. Clearing restores both to zero. Visually reviewed both boxes at desktop size and 390×844; both completion lines remain visible on mobile. `node --check main.js` and `git diff --check` passed. Checkpoint drift before this follow-up was the expected prior counter changes in main.js and style.css; hashes were not refreshed.
