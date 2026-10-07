# Standard-only form dropdown — 2026-10-07

Pokédex rows omit the form selector when their only catalog option has the label Standard (including the existing fallback label). Multiple-form selectors and any single named-form selector remain available. Ownership controls and collection persistence are unchanged. Existing flex layout lets the species button use the freed space.

Validation: JavaScript syntax checks passed for main.js and desktop/smoke.cjs. Executed the actual list-rendering function in a Node VM with the checked-in catalog and isolated UI stubs: 806 Standard-only selectors omitted, 219 selectors retained; Bulbasaur has no selector and Pikachu retains its selector. Native smoke expectations were updated. Interaction and visual checks remain unverified because the prior Electron launch was blocked by Windows sandbox ACL permissions; no new native pass is claimed.

Checkpoint drift and pre-existing work were preserved. No catalog, save schema, package version or release changes.
