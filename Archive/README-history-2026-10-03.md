# ShinyDex

Current audit status: hunting coverage remains incomplete. The guide contains 4,169 direct egg routes across Generations III–IX plus 348 Generation II DV-based egg routes. Generation II includes 375 detailed evolution routes; Generation III includes 736; Generation IV includes 738; Let's Go includes 160. These counts establish reference-table and requirement coverage, not complete parent acquisition or event availability. Generic breeding/evolution shortcuts have been replaced by detailed routes, including Midday Lycanroc trade detours from Moon/Ultra Moon. Legends: Z-A Feebas Beauty evolution remains unresolved; the Prism Scale trade route is included. See evolution-pending-audit.json and evolution-review-evidence.json for the conflicting evidence. Run `python verify-gen-two-breeding.py`, `python verify-gen-three-evolutions.py`, `python verify-gen-four-evolutions.py`, `python verify-breeding.py`, `python verify-legacy-form-corrections.py` and `python audit-evolution-pending.py` after rebuilding.

Run `node server.cjs`, then open http://localhost:5173.

Run `python check-project.py` to run every checked-in verifier and write project-checks.json. A passing run verifies the checks' stated scope; it does not certify exhaustive hunting coverage. Rebuild hunting data with `python build-hunts.py` first after changing a hunting-data generator.

Includes National Pokédex species #0001–#1025 plus 58 regional entries, Gen 4 inspired scrolling, normal/shiny images from Bulbapedia's Bulbagarden Archives, generation and captured filters, and 37 fixed HOME boxes of 30 slots (6 columns × 5 rows). Regional forms follow their base species, in Alola / Galar / Hisui / Paldea order. Other alternate forms are not extra entries. This is a suggested living-dex organization; HOME does not mandate a box arrangement.

Captured is left of Shiny captured. Checking Shiny also checks Captured; clearing Captured clears Shiny. Every check and uncheck immediately saves to localStorage, shared by all views and restored on reload. Progress belongs to this browser and URL; clearing browser storage removes it. The save status reports storage failures. Export backup downloads JSON.

HOME follows actual collection state: uncaptured Pokémon are silhouettes, regular captures show normal art, and shiny captures show shiny art. Filters keep slots fixed; hover names and row/column labels identify positions. The separate Shiny collection tab lists captured shinies.

All 2,166 normal/shiny images are local files from the same HOME artwork family. All passed decoding and archive caption identity checks. Two Galarian Moltres source captions incorrectly use #0145; the correct #0146 filenames, species captions and both images were visually verified. See image-audit.json and caption-audit.json.

Data from PokéAPI. Artwork hosted by Bulbagarden Archives, owned by the respective Pokémon rights holders. Unofficial fan project.

The hunting panel provides game names, methods, recorded locations, breeding/evolution options, event/reward availability, sources and game-specific shiny locks. Confirmed locks say **Shiny Locked**. Missing records are not proof of a lock. Every species and regional form has a recorded method or lock status.

**The exhaustive hunting audit is unfinished.** Record coverage does not establish full accuracy or completeness. All 555 previously uncertain gift records now have source-backed encounter-specific classifications. Decoded and explicit reference tables add 9,535 wild, Alpha, gift and static routes/restrictions across Sun/Moon/Ultra Sun/Ultra Moon, Sword/Shield, Legends: Arceus, Brilliant Diamond/Shining Pearl, Scarlet/Violet and Legends: Z-A, including DLC and 50 regional forms with wild routes. All 180,291 tracked-form slot/location records in these decoded tables passed coverage verification. Gameplay prerequisites, encounter conditions, exact breeding/evolution availability, other game tables and remaining distributions, GO and historical events still need fuller verification. References were checked October 3, 2026. Use linked Bulbapedia sources before starting a hunt. data-audit.json records the audit status; modern-decode-audit.json and modern-coverage-audit.json record source-table validation and the remaining scope.

Fixed wild Tera spawns are recorded separately from raids, with 382 additional game/form routes decoded from 977 source encounters.

Historical event mass outbreaks add 132 game/form routes from 12,636 source encounters. All 52,070 tracked-form location records map to the guide. Downloaded event availability, dates and event-specific shiny odds still need announcement-level verification; these records are not a current event calendar.

Raid tables additionally provide 3,201 form-specific routes covering Max Raid dens, historical raid distributions, Dynamax Adventures, Tera Raids and Mightiest Mark events. All 14,684 tracked-form raid records passed mapping checks for Pokémon, form, location, shiny status, host version, stars and event identifiers. Historical distributions depend on retained event data and are not presented as currently running events. Dynamax Adventures checks shininess at the results screen. See raid-decode-audit.json and raid-coverage-audit.json. Event dates and gameplay prerequisites still need verification.

Direct egg hunting adds 845 routes for Sword/Shield, BDSP and Scarlet/Violet, matched to each game's species presence and parent egg groups. Babies name their breedable parent, regional parents include Everstone instructions, and incense babies distinguish pre-Scarlet/Violet requirements. Breeding Manaphy produces Phione eggs; neither Manaphy nor Ditto is listed as hatchable. Parent acquisition, older games, exact evolutions and additional form exceptions remain under audit. See breeding-audit.json; run `python verify-breeding.py` after rebuilding.

Evolution snapshots decode 1,418 branches across Sword/Shield, BDSP, Scarlet/Violet, Legends: Arceus and Legends: Z-A. The guide includes 789 level-only routes, 242 item-based routes 168 friendship/move/gender/time/stat/party/weather/branch/location routes 27 trade routes and 27 special action routes with exact item names, gender restrictions, held-item trades and day/night conditions, restricted to forms present in that game. Matched trades specify Shelmet/Karrablast partners and the Everstone restriction. Arceus includes both trading and Linking Cord alternatives where supported. Arceus day/night item IDs are decoded separately from mainline tower IDs. Tyrogue branches specify Attack/Defense comparisons at level 20. Action routes include 1,000 Let’s Go steps, Union Circle at level 38, 999 Gimmighoul Coins and 20 Rage Fist uses. Party routes require Remoraid for Mantyke, and a Dark-type Pokémon at level 32 for Pancham. Hisuian routes include agile Psyshield Bash, strong Barb Barrage, 294 recoil HP without fainting, and Peat Block during a full moon. White-Striped Basculin eggs do not require an Everstone in Scarlet/Violet. Battle routes name critical-hit counts, eligible damage and arch locations, and Bisharp opponents holding Leader’s Crest. Nincada branches include level 20 and Shedinja’s empty party slot and regular Poké Ball requirements. Known-move routes name the required move. Friendship branches include day/night restrictions where needed; Arceus specifies manual evolution. Other evolution conditions and shiny parent acquisition/transfer prerequisites remain unfinished. Refresh with `python decode-evolutions.py` before rebuilding; run `python verify-evolutions.py` afterward. See evolution-decode-audit.json and evolution-route-audit.json.

Gift restrictions are additionally cross-checked against public PKHeX encounter definitions pinned to commit 542111fc8584ff29c9d1455553b8acd0e1f8a59a. The reference sources and GNU GPL v3 license are retained in reference/pkhex; no upstream code is executed. See THIRD_PARTY_NOTICES.md for source and artwork attribution. Rebuilding the hunting guide preserves this verification through audit_gifts.py. Game-specific locked methods display **Shiny Locked**; missing or unverified encounter records are not automatically classified as locked.

Rebuild hunting data with `python build-hunts.py` using the checked-in CSV and reference snapshots. To refresh the derived modern reference tables, run `python decode-modern.py`, `python decode-raids.py` and `python parse-static.py` first; verify tracked-form source coverage with `python verify-modern.py` and `python verify-raids.py`. Rebuild catalog with `python build-catalog.py`; validate ordering, assets and guide records with `node verify-data.cjs`. The interface uses modern browser standards; no browser extension is required. Autosave check/uncheck, reload recovery, independent regional tracking, shiny collection, fixed HOME positions and shiny image selection passed in the in-app browser. Chrome and Firefox have not been separately exercised.

Inkay’s Sword/Shield and Scarlet/Violet evolution routes specify level 30, upside-down handheld play, attached Joy-Con controllers and disconnection of other controllers. Legends: Z-A manual evolution timing remains under review. Run `python audit-evolution-pending.py` to refresh the outstanding evolution branch inventory.

Goodra routes specify level 50 and natural overworld rain, excluding battle-only weather abilities and moves. Legends entries specify manual evolution from the party menu.

Wurmple evolves from level 7 into the branch fixed by its hidden encryption constant. BDSP and Arceus guides explain that resetting, time of day and gender cannot select the other evolution.

Modern Sylveon evolution entries require high friendship and a known Fairy-type move; they do not reuse the older Pokémon-Amie/Refresh affection requirement.

Amped Toxtricity routes list all 13 eligible original natures and level 30; Mints do not alter the evolution branch.

Location evolutions for Leafeon and Glaceon distinguish BDSP’s Eterna Forest/Route 217 from Arceus’s Heartwood/Icepeak Cavern, including manual evolution in Arceus.

Magnezone and Probopass location routes name Mount Coronet in BDSP and the Coronet Highlands in Arceus, with manual evolution in Arceus.

Dudunsparce’s Two-Segment evolution route requires Hyper Drill and the fixed hidden form branch; resetting does not reroll the form.

Maushold’s Family of Three evolution route requires battle experience from level 25 and its fixed hidden form branch. The guide explains silent evolution, candy limitations and why level-100 Tandemaus cannot evolve.

Overqwil’s Z-A route requires landing 20 Barb Barrage hits with Hisuian Qwilfish, followed by manual evolution; Arceus’s strong-style requirement is not applied to Z-A.

Alcremie routes specify a held Sweet and a clockwise daytime spin shorter than five seconds for Vanilla Cream. Strawberry Sweet matches the pictured decoration.

Feebas Beauty evolution routes require at least 170 Beauty: dry Poffins in BDSP, or preparation in a compatible Contest game before transfer to Sword/Shield or Scarlet/Violet. Z-A’s preserved source-table Beauty branch is not published as a working route while its gameplay support remains unverified.

Retained Crabominable summit branches in modern evolution tables are excluded: Mount Lanakila applies to Alola games, while Scarlet/Violet and Z-A use Ice Stones. Source-backed exclusions are recorded in evolution-exceptions.json.

Espeon/Umbreon routes explain removing Fairy-type moves where Sylveon is available and avoiding evolution rocks where applicable. legacy-method-review.json inventories generic breeding/evolution instructions requiring game-specific review; regenerate with python audit-legacy-methods.py.

Rebuilding supersedes 872 vague modern evolution rows with existing exact same-game requirements. superseded-evolution-audit.json preserves the replaced records and their replacement game families. This does not establish complete hunting coverage.

Rebuilding also supersedes 833 generic breeding rows where a direct egg route for that same catalog entry and game already supplies parent, language, incense and form instructions. Removed records are retained in superseded-breeding-audit.json; evolved-species breeding routes remain under review.

Added 18 optional-incense egg routes for supported Sword/Shield and BDSP forms: without the relevant incense, eggs hatch Marill, Wobbuffet, Roselia, Chimecho, Sudowoodo, Mr. Mime, Chansey, Snorlax or Mantine instead of their babies. These direct evolved-species egg routes are excluded from Scarlet/Violet, where the baby offspring are automatic.

Modern Nidoran and Volbeat/Illumise egg routes include both counterpart-parent options and explain that eggs can hatch either species. Nidorina and Nidoqueen are explicitly excluded as breeding parents.

Tauros egg routes require Ditto and a parent of the intended breed. Kantonian Tauros breeding in Paldea requires an Everstone to avoid Combat Breed offspring; Kantonian parents do not yield Blaze or Aqua Breed. Area-specific Paldean breed inheritance remains under review.

Johtonian Wooper’s Scarlet/Violet egg route specifies an Everstone on the Johtonian Wooper/Quagsire parent when breeding in Paldea; otherwise the offspring is Paldean Wooper.

Direct egg routes distinguish male-only/gender-unknown parents requiring Ditto from female parents paired with compatible males sharing an Egg Group. Paired-species exceptions remain separately described.

All direct egg routes describe ordinary egg hunting, different-language Masuda breeding and the Shiny Charm modifier. Scarlet/Violet entries distinguish Egg Power’s egg-production benefit from Sparkling Power, which does not improve egg shiny odds.

Detailed evolution rows link both the pinned evolution-table source and the species’ Bulbapedia Evolution data section. The hunting panel displays supporting references and omits duplicate or non-HTTP links.

Ultra Sun/Ultra Moon evolution references are separately decoded into 410 branches. The guide now includes 264 simple level-based routes; special conditions and shiny parent acquisition remain under review. Refresh with python decode-older-evolutions.py and verify with python verify-older-evolutions.py.

Ultra Sun/Ultra Moon additionally includes 11 trade routes, with exact Shelmet/Karrablast partners, Everstone restrictions, trade-back guidance and Alolan Graveler.

Ultra Sun/Ultra Moon includes 62 additional item evolution routes with exact item names, gender restrictions, held-item time requirements, and Ultra Space versus Alola conditions for Raichu and Exeggutor.

Ultra Sun/Ultra Moon also includes nine known-move evolution routes, with explicit Rollout, Ancient Power, Double Hit, Mimic, Stomp or Dragon Pulse requirements.

Ultra Sun/Ultra Moon includes 18 friendship evolution routes requiring at least 220 friendship, with day/night conditions where applicable, and a separate Sylveon route requiring two affection hearts in Pokémon Refresh and a Fairy-type move. Eevee routes explain competing evolution conditions. Eleven further gender/time routes cover female-only Salazzle and Vespiquen, Plant Cloak Wormadam, and nighttime Alolan evolutions. These bring the older evolution subset to 376 routes; shiny parent acquisition and the remaining special conditions are still under audit.

Seven location routes raise the Ultra Sun/Ultra Moon subset to 383: magnetic fields at Blush Mountain or Vast Poni Canyon, the Lush Jungle Moss Rock, Mount Lanakila's Ice Rock and Crabrawler evolution area, and Kantonian Marowak evolution in Ultra Space. Each links the relevant Bulbapedia location reference. Parent acquisition and other special evolutions remain under audit.

Five stat/party routes bring the subset to 388: Tyrogue's three Attack/Defense comparisons at level 20 or higher, Mantyke with Remoraid in the party, and Pancham at level 32 or higher with a Dark-type party member. These requirements preserve the shiny parent; party partners need not be shiny.

Seven further special routes bring this subset to 395: fixed Wurmple branches, Ninjask and Shedinja, Feebas with Beauty prepared in an earlier compatible Contest game, Inkay with an inverted Nintendo 3DS, and Sliggoo during natural overworld rain or fog. Full hunting and parent acquisition coverage remains unfinished.

Midday Lycanroc adds a version-specific Ultra Sun route (regular Rockruff without Own Tempo, level 25 or higher during the day). The older evolution audit now accounts for all 410 decoded branches: 396 rendered routes, 11 forms outside this catalog, and three branches with shiny-locked parents or children. This accounts for the evolution table, not exhaustive shiny acquisition or game availability.

Specific older evolution requirements now supersede generic advice in matching Ultra Sun/Ultra Moon guides. Across the audited game subsets, 1,201 generic evolution rows have retained same-game replacements; `python verify-superseded-evolutions.py` checks each replacement. Midday Lycanroc's evolution entry is labeled Ultra Sun only and cannot supersede Ultra Moon advice.

Legends: Z-A Inkay now has its manual party-menu evolution route, supported by a gameplay guide with screenshots: reach level 30, hold the console upside down in handheld mode, select Inkay and Evolve even without an evolution arrow. Modern rendered evolution routes total 1,254. The preserved Z-A Feebas Beauty branch remains withheld pending evidence that the game implements it.

The pending evolution audit checks actual guide entries against decoded parent, destination form, game, method type, argument and level rather than assuming a supported method was rendered. Its current result is 1,254 matching routes and one pending branch (Z-A Feebas Beauty). The separate legacy inventory still contains 7,683 generic breeding/evolution records across 689 entries needing review; these counts do not establish complete hunting coverage. Refresh both reports with `python audit-evolution-pending.py` and `python audit-legacy-methods.py`.

Direct egg routes now total 1,206, including 361 Ultra Sun/Ultra Moon routes with incense, original Alola form inheritance and Paniola Ranch Nursery requirements. Older routes name compatible trades or Pokémon Bank rather than HOME as the parent source: HOME cannot send Pokémon back to Nintendo 3DS games. Generic breeding advice has 2,518 verified replacements, including 1,329 complete same-game egg/evolution chains; check with `python verify-superseded-breeding.py`. Acquisition prerequisites still need full review.

Sun/Moon now adds 361 direct egg routes, six explicit location evolution routes and 261 simple level routes. The pinned EvolutionTree reader uses the shared `uu` table for Generation VII; simple routes are additionally filtered through Sun/Moon's own personal table. Ultra-specific location/form conditions are separately reviewed. Verify with `python verify-sun-moon-evolutions.py`. Current totals: 1,567 direct egg routes, 1,374 superseded generic evolution records, and 2,904 superseded breeding records (1,450 complete egg/evolution chains). The legacy review has 7,124 records across 633 entries; exhaustive coverage remains unfinished.

Sun/Moon's evolution subset now contains 392 routes: 264 simple levels (including regional forms), 60 items, 19 friendship/affection, 11 trades, eight known moves, 23 gender/party/stat/special conditions, six location requirements and one Sun-only Midday Lycanroc route. Ultra Space evolutions and Ultra-only species are excluded. Full acquisition coverage remains under audit.

## Attribution and archived work

See [ATTRIBUTIONS.txt](ATTRIBUTIONS.txt) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for artwork, data, upstream programs and runtime credits. PKHeX reference material retains its GPLv3 license in `reference/pkhex/LICENSE`. Individual hunting records link to their sources. This project is an unofficial fan app; Pokémon artwork and characters belong to Nintendo, Creatures and GAME FREAK and their respective rights holders.

Historical previews and the unused earlier app are preserved in [Archive](Archive/README.md). Release cleanup and the exhaustive hunting audit remain in progress.

Upstream license copies: [PokéAPI BSD-3-Clause](licenses/PokeAPI-BSD-3-Clause.txt), [Prettier MIT](licenses/Prettier-MIT.txt), and [PKHeX GPLv3](reference/pkhex/LICENSE). Copyright notices and conditions are retained in these files; artwork rights are credited separately in ATTRIBUTIONS.txt.
