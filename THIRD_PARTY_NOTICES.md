# Third-party sources

Pokémon artwork is sourced from Bulbapedia's Bulbagarden Archives. It is included in the original HOME artwork style, with normal and shiny variants. Image provenance and checks are recorded in image-audit.json, image-captions.json and caption-audit.json. Pokémon characters and artwork belong to their respective rights holders; they are not original app artwork.

Pokédex and encounter CSV snapshots originate from PokéAPI: https://github.com/PokeAPI/pokeapi. Bulbapedia references support hunting mechanics and game-specific restrictions. Individual hunting records retain source links.

PKHeX reference files are pinned to commit `542111fc8584ff29c9d1455553b8acd0e1f8a59a` at https://github.com/kwsch/PKHeX. They supply encounter definitions, personal tables and evolution data. The bundled license is GNU GPL version 3, retained in reference/pkhex/LICENSE. The build scripts read reference files as data; they do not execute upstream C# code. Derived hunting records link to the pinned source files.

The source licenses and artwork rights are separate from the app's own implementation. No blanket MIT license is asserted for this repository or its bundled reference material.

Source formatting uses [Prettier](https://prettier.io/) 3.6.2 by the Prettier contributors as a development tool. It is not bundled in the browser app. Runtime and development-tool credits are also recorded in ATTRIBUTIONS.txt.

License copies: PokéAPI by Paul Hallett and PokéAPI contributors: BSD-3-Clause, licenses/PokeAPI-BSD-3-Clause.txt (source: https://github.com/PokeAPI/pokeapi/blob/master/LICENSE.md). Prettier by James Long and contributors: MIT, licenses/Prettier-MIT.txt (source: https://github.com/prettier/prettier/blob/3.6.2/LICENSE). PKHeX: GNU GPLv3, reference/pkhex/LICENSE. These files retain the upstream copyright notices and license conditions.

Image audit and contact-sheet tooling: Pillow 9.0.0, the Python Imaging Library fork by Alex Clark and contributors, with original PIL copyrights retained for Secret Labs AB and Fredrik Lundh. Pillow is a separately installed development dependency, not browser runtime code. Its HPND license is retained in licenses/Pillow-HPND.txt; source: https://github.com/python-pillow/Pillow/blob/9.0.0/LICENSE.

Additional audit derivatives: Archive/image-review contact sheets use the same attributed Bulbagarden HOME artwork; reference/radar-maps contains Diamond/Pearl and Platinum Route 210 maps from Bulbagarden Archives, with source pages and hashes recorded in radar-area-review.json. The maps depict copyrighted game material and are not MIT artwork. Platinum radar implementation references point to pret/pokeplatinum commit c248fb3f8cc9934ded800e489567c5c0eeee92eb; no decompilation source code is bundled.

The current app uses locally available system fonts and downloads no web fonts. Contact-sheet labels were rendered with separately installed Arial; no font files are distributed. Artwork source-byte checks are in upstream-image-audit.json; visual-review evidence is in visual-image-audit.json.

The desktop v2 installer bundles Electron 44.5.1 (MIT), Chromium and its third-party components, and electron-updater 6.8.9 plus its production dependencies. `licenses/Electron-MIT.txt` and `licenses/Desktop-runtime-dependencies.txt` retain the distributed license texts; Electron's `LICENSE` and `LICENSES.chromium.html` ship beside the installed executable. lazy-val declares MIT but supplies no license file; its author, source, and standard MIT terms are retained separately without inventing an upstream copyright notice. Run `node desktop/collect-licenses.cjs` to refresh production dependency notices. The default Electron application icon is used.

The historical v1 launcher used the separately installed Windows .NET Framework. Its source and release binaries are retained for history and are not included in the desktop v2 installer. Pokémon artwork rights and other upstream licenses apply separately to both distributions.
