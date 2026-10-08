# Pinned PokéAPI descriptive-entry fallback

`source.json` records the upstream commit. The CSV files were downloaded from
`https://raw.githubusercontent.com/PokeAPI/pokeapi/COMMIT/data/v2/csv/FILE`.
The complete multilingual flavor-text snapshot is retained; the runtime build
selects English language ID 9. Version tables supply identifiers and names only.
No game-specific Pokédex numbers are compiled.

PokéAPI is credited to Paul Hallett and PokéAPI contributors under BSD-3-Clause;
see `licenses/PokeAPI-BSD-3-Clause.txt`. Underlying Pokémon text rights remain
separate. Input hashes and the exact fallback species/game pairs are in
`audit/pokedex-entries-report.json`.
