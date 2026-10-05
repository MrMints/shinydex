"""BDSP Radar routes from pinned grass slots and explicit location exclusions.

Legality slots include conditional encounters. Preserve their location IDs and
warn about time, swarm and garden pools instead of implying constant availability.
"""
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent
SOURCE = 'https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9_Radar'
GARDEN_SOURCE = 'https://bulbapedia.bulbagarden.net/wiki/Trophy_Garden'
# Separately reviewed BDSP introduction roster, in National Dex rotation order.
GARDEN_INTRODUCTIONS = (35, 39, 52, 113, 133, 137, 173, 174,
                        183, 298, 311, 312, 351, 438, 439, 440)
SWARM_SOURCE = 'https://bulbapedia.bulbagarden.net/wiki/Mass_outbreak#Pok%C3%A9mon_Brilliant_Diamond_and_Shining_Pearl'
# The independent BDSP outbreak roster, not inferred from legality slots.
SWARMS = {16:'Route 229',81:'Fuego Ironworks',83:'Route 221',84:'Route 201',
          96:'Route 215',98:'Route 226',100:'Route 218',104:'Route 203',
          108:'Lake Valor',177:'Route 224',206:'Route 208',209:'Route 209',
          220:'Route 217',222:'Route 230',225:'Route 216',231:'Route 207',
          238:'Lake Acuity',263:'Route 202',283:'Lake Verity',287:'Eterna Forest',
          296:'Route 225',299:'Route 206',300:'Route 222',309:'Valley Windworks',
          325:'Route 214',327:'Route 227',359:'Route 213',374:'Route 228'}
READER = 'PKHeX.Core/Legality/Encounters/Templates/Gen8b/EncounterSlot8b.cs'
SECTION_SOURCES = {
    206:'https://www.serebii.net/pokearth/sinnoh/mt.coronet.shtml',
    207:'https://www.serebii.net/pokearth/sinnoh/mt.coronet.shtml',
    323:'https://www.serebii.net/pokearth/sinnoh/lakeverity.shtml',
    324:'https://www.serebii.net/pokearth/sinnoh/lakeverity.shtml',
    359:'https://www.serebii.net/pokearth/sinnoh/route205.shtml',
    361:'https://www.serebii.net/pokearth/sinnoh/route205.shtml',
    201:'https://www.serebii.net/pokearth/sinnoh/fuegoironworks.shtml'}

# CanUseRadarOverworld exclusions in the pinned reader, plus the Great Marsh.
EXCLUDED = ({195, 196, 203, 204, 205, 208, 209, 210, 211, 212, 213, 214,
             215, 252, 255, 256, 260, 261, 262, 292, 293, 294, 295, 296}
            | set(range(219, 244)) | set(range(244, 250))
            | set(range(264, 285)) | set(range(286, 292))
            | set(range(299, 315)) | set(range(368, 373)))
DETAILS = {206: 'snow area exterior', 207: 'summit exterior',
           323: 'before Galactic incident', 324: 'after Galactic incident',
           259: 'exterior grass', 373: 'south section; eligible short grass only',
           375: 'north section', 357: 'south section', 358: 'north section',
           359: 'south section', 361: 'north section',
           377: 'west section', 378: 'east section',
           379: 'north section', 383: 'south section'}

def merge_reviewed_times(records):
    """Apply explicit source reviews, never promote parsed inventory candidates."""
    conditions = json.loads((ROOT / 'bdsp-time-review.json').read_text(encoding='utf-8'))['conditions']
    count = 0
    for condition in conditions:
        species, location, source = condition['species'], condition['location'], condition['source']
        period = ' or '.join(condition['times'])
        section = condition.get('section')
        target = location + (' · ' + section if section else '')
        time_label = target + f' · {period} only'
        for row in records[str(species)]['entries']:
            if row['game'] not in condition['games']:
                continue
            if row.get('encounterKind') != 'bdsp-1' and row.get('huntingTechnique') != 'bdsp-radar':
                continue
            if not any(label.split(' · ')[0] == location for label in row['locations']):
                continue
            if row.get('huntingTechnique') == 'bdsp-radar':
                assert condition['locationId'] in row['radarLocationIds']
            radar_note = '; start its Radar chain there during that period' if row.get('huntingTechnique') == 'bdsp-radar' else ''
            note = f' On {target}, this species is available in wild encounters only during {period}{radar_note}. Other listed locations have separate encounter conditions.'
            if note not in row['method']:
                row['method'] += note
            row['locations'] = [time_label if label in (location,target) else label for label in row['locations']]
            # Ordinary routes collapse floor/section IDs into one base name.
            # Once the generic label is replaced, retain each reviewed section.
            if time_label not in row['locations']:
                row['locations'].append(time_label)
            row['locations'] = sorted(set(row['locations']))
            row['sourceReferences'] = sorted({row['source'], *row.get('sourceReferences', []), source})
            existing = {item['locationId']:item for item in row.get('reviewedTimeConditions', [])}
            existing[condition['locationId']] = {field:condition[field] for field in ('locationId','location','times','source')}
            if section:
                existing[condition['locationId']]['section'] = section
            row['reviewedTimeConditions'] = [existing[key] for key in sorted(existing)]
            count += 1
    clock_note = ' BDSP uses the Nintendo Switch system clock: morning 04:00–09:59, day 10:00–19:59, and night 20:00–03:59.'
    for guide in records.values():
        for row in guide['entries']:
            if row.get('reviewedTimeConditions'):
                if clock_note not in row['method']:
                    row['method'] += clock_note
                row['sourceReferences'] = sorted({*row['sourceReferences'], 'https://bulbapedia.bulbagarden.net/wiki/Time#Pokémon_Brilliant_Diamond_and_Shining_Pearl'})
    return count


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
            if location == 297 and species in GARDEN_INTRODUCTIONS:
                detail = 'Mr. Backlot must have introduced this species most recently or on his previous introduction'
            if SWARMS.get(species) == slot['location']:
                detail = (detail + '; ' if detail else '') + 'this species must be the active daily swarm'
            labels.append(slot['location'] + (' · ' + detail if detail else ''))
        garden = 297 in slots and species in GARDEN_INTRODUCTIONS
        swarm = species in SWARMS
        conditional_note = ''
        if swarm:
            assert {slot['location'] for slot in slots.values()} == {SWARMS[species]}
            conditional_note = (
                ' Start this species’ chain only while its daily swarm is '
                'active at ' + SWARMS[species] + '. Check the pause-menu '
                'outbreak notice or ask Lucas/Dawn’s little sister in '
                'Sandgem Town for the active species and location. The '
                'visible Pokémon popping out of grass cannot be directly '
                'caught; encounter the species through the grass or Radar.'
            )
        if garden:
            conditional_note = (
                ' For Trophy Garden, speak to Mr. Backlot after obtaining the '
                'National Pokédex. His introduction can advance once per day '
                'after midnight and follows a fixed 16-species National Dex '
                'rotation, from Clefairy through Happiny. This species must '
                'be one of his two most recent introductions; those two '
                'remain until replaced by further introductions. Resetting '
                'before the conversation does not reroll the species as it '
                'can in the original Diamond/Pearl games.'
            )
        if species in (187,188,79,304):
            sections=[]
            if 359 in slots:
                sections.append('Route 205 south of Eterna Forest')
            if 361 in slots:
                sections.append('Route 205 north of Eterna Forest, beside Eterna City')
            if 201 in slots:
                sections.append('Fuego Ironworks exterior grass')
            if sections:
                method += ' This version’s Radar encounters for this species are in ' + '; '.join(sections) + '.'
        method += conditional_note
        # The ordinary grass route has the same availability gates. Leaving
        # it generic would contradict the more precise Radar route beside it.
        if conditional_note:
            for ordinary in records[str(species)]['entries']:
                if ordinary['game'] != game or ordinary.get('encounterKind') != 'bdsp-1':
                    continue
                ordinary['method'] += conditional_note
                ordinary['sourceReferences'] = sorted({ordinary['source'],
                    *ordinary.get('sourceReferences', []), GARDEN_SOURCE if garden else SWARM_SOURCE})
                ordinary['conditionalAvailabilityVerified'] = 'garden' if garden else 'swarm'
        records[str(species)]['entries'].append({
            'game': game, 'method': method, 'status': 'Huntable',
            'locations': sorted(set(labels)), 'radarLocationIds': sorted(slots),
            'huntingTechnique': 'bdsp-radar', 'source': SOURCE,
            'sourceReferences': sorted({reader, 'https://bulbapedia.bulbagarden.net/wiki/National_Pok%C3%A9dex', *([GARDEN_SOURCE] if garden else []), *([SWARM_SOURCE] if swarm else []), *[SECTION_SOURCES[loc] for loc in slots if loc in SECTION_SOURCES], *[s['source'] for s in slots.values()], *(['https://luminescent.team/rom-hacking/dictionary/zones', 'https://bulbapedia.bulbagarden.net/wiki/List_of_locations_by_index_number_(Brilliant_Diamond_%26_Shining_Pearl)'] if set(slots)&{206,207,323,324} else [])}),
            **({'gardenIntroductionOrder': GARDEN_INTRODUCTIONS.index(species) + 1,
                'gardenConditionVerified': True} if garden else {}),
            **({'swarmLocation':SWARMS[species], 'swarmConditionVerified':True} if swarm else {}),
            'verification': 'Pinned grass slots and explicit Radar location eligibility; individual conditional pools remain under review',
        })
    merge_reviewed_times(records)
    return len(routes())
