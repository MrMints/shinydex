# Descriptive-entry source snapshots

The numbered JSON files retain only the Dex template section of each of the 1,025
species pages in the application catalog. Each records the original page URL,
MediaWiki revision ID, UTC retrieval time and SHA-256 of the API response.
`collect-pokedex.py` resumes missing snapshots without overwriting existing ones.
Remove a specifically reviewed snapshot before intentionally refreshing it.

Bulbapedia contributors supply the transcription, structure and form labels.
Source: https://bulbapedia.bulbagarden.net/ . History for each snapshot is available
at `https://bulbapedia.bulbagarden.net/w/index.php?oldid=REVISION_ID`.
Source-derived material is attributed to Bulbapedia and its contributors under
CC BY-NC-SA 2.5, subject to the separate underlying Pokémon rights. See
https://bulbapedia.bulbagarden.net/wiki/Bulbapedia:Copyrights and
https://creativecommons.org/licenses/by-nc-sa/2.5/ . Whitespace, wiki markup and
shared-version templates are transformed by `build-pokedex.py`; descriptions
are not independently verified against game cartridges.

`template-recycled-rg.json` records why Japanese Red/Green English descriptions
are not silently synthesized: the source marks them untranslated until recycled
in FireRed. This explanatory template is not a descriptive entry.
