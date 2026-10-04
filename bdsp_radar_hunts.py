"""BDSP Radar routes from pinned grass slots and explicit location exclusions.

Legality slots include conditional encounters. Preserve their location IDs and
warn about time, swarm and garden pools instead of implying constant availability.
"""
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent
SOURCE = 'https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9_Radar'
READER = 'PKHeX.Core/Legality/Encounters/Templates/Gen8b/EncounterSlot8b.cs'

# CanUseRadarOverworld exclusions in the pinned reader, plus the Great Marsh.
EXCLUDED = ({195, 196, 203, 204, 205, 208, 209, 210, 211, 212, 213, 214,
             215, 252, 255, 256, 260, 261, 262, 292, 293, 294, 295, 296}
            | set(range(219, 244)) | set(range(244, 250))
            | set(range(264, 285)) | set(range(286, 292))
            | set(range(299, 315)) | set(range(368, 373)))
DETAILS = {206: 'exterior grass', 207: 'exterior grass',
           259: 'exterior grass', 373: 'south section; eligible short grass only',
           375: 'north section', 357: 'south section', 358: 'north section',
           359: 'south section', 361: 'north section',
           377: 'west section', 378: 'east section',
           379: 'north section', 383: 'south section'}


def routes():
    grouped = defaultdict(dict)
    for slot in json.loads((ROOT / 'modern-wild.json').read_text()):
        if (slot['kind'] != 'bdsp-1' or slot['form'] != 0
                or slot['locationId'] in EXCLUDED):
            continue
        grouped[(slot['species'], slot['game'])][slot['locationId']] = slot
    return grouped


def merge(records):
    sha = json.loads((ROOT / 'reference/pkhex/tree.json').read_text())['sha']
    reader = 'https://github.com/kwsch/PKHeX/blob/' + sha + '/' + READER
    for (species, game), slots in routes().items():
        method = (
            'Poké Radar shiny chaining (BDSP, version 1.1.3 or later). '
            'Receive the Radar from Rowan in Sandgem Town after Oak upgrades '
            'your Pokédex to the National Pokédex: reach Eterna City and see '
            'all 150 required Sinnoh species (Manaphy is excluded), then '
            'visit Rowan’s lab. Use eligible tall grass on '
            'foot; use Repels to avoid ordinary battles. Capture or defeat '
            'the chained species in shaking patches. Choose distant patches '
            'and capture to improve continuation, but chains can still break '
            'randomly. Recharge with 50 steps and reuse the Radar to reroll '
            'patches without entering one. At chain 40 or higher, each patch '
            'has a 1/99 shiny-patch chance; a sparkling patch guarantees a '
            'shiny. The Shiny Charm does not improve Radar odds. Vigorous '
            'shaking indicates Hidden Ability, not a shiny. Leaving the area, '
            'an ordinary battle or ending a battle without catching/defeating '
            'breaks the chain. Encounter availability may require a swarm, '
            'time of day or Mr. Backlot’s current/previous Trophy Garden '
            'introduction; these tables combine conditional pools. Version '
            '1.1.3 permits ordinary species whose slots were otherwise '
            'overwritten by Radar-exclusive encounters.'
        )
        labels = []
        for location, slot in sorted(slots.items()):
            detail = DETAILS.get(location)
            labels.append(slot['location'] + (' · ' + detail if detail else ''))
        records[str(species)]['entries'].append({
            'game': game, 'method': method, 'status': 'Huntable',
            'locations': sorted(set(labels)), 'radarLocationIds': sorted(slots),
            'huntingTechnique': 'bdsp-radar', 'source': SOURCE,
            'sourceReferences': sorted({reader, 'https://bulbapedia.bulbagarden.net/wiki/National_Pok%C3%A9dex', *[s['source'] for s in slots.values()]}),
            'verification': 'Pinned grass slots and explicit Radar location eligibility; individual conditional pools remain under review',
        })
    return len(routes())
