"""Add source-reviewed SOS mechanics without inventing caller relationships.

The decoded SOS tables identify possible allies, not always their caller or
weather/time gates. Explicit notes below cover reviewed special targets.
"""
SOURCE = 'https://bulbapedia.bulbagarden.net/wiki/SOS_Battle'
ORB = 'https://bulbapedia.bulbagarden.net/wiki/Adrenaline_Orb'
NOTES = {
    62: 'Use a caller in Malie Garden with rain active during daytime for Poliwrath.',
    186: 'Use a caller in Malie Garden with rain active during nighttime for Politoed.',
    351: 'Castform is a weather ally: use rain, hail or sandstorm in the listed weather-enabled areas. Weather can be set by a move or Ability; Cloud Nine and Air Lock suppress weather allies.',
    444: 'Use a caller in Haina Desert with sandstorm active for Gabite.',
    582: 'Use hail at Tapu Village; Ultra Sun/Ultra Moon also allow Vanillite at the base of Mount Lanakila.',
    583: 'Use hail on Mount Lanakila outside the base and icy cave for Vanillish.',
    584: 'In Ultra Sun/Ultra Moon, use hail on Mount Lanakila outside the base and icy cave for Vanilluxe.',
    704: 'Use rain with a caller in Lush Jungle or Route 17 for Goomy.',
    705: 'Use rain with a caller on Exeggutor Island for Sliggoo.',
    747: 'Corsola can call Mareanie. Mareanie attacks Corsola, so protect or replace the caller before it faints.',
    302: 'Carbink can call Sableye in caves. Sableye attacks Carbink, so protect or replace the caller before it faints.',
    94: 'Haunter can call Gengar; keep a caller alive rather than expecting Gengar to call more allies.',
    115: 'Cubone can call Kangaskhan.',
    373: 'Bagon can call Salamence.',
}


def merge(records, catalog):
    species = {str(p['key']): p['id'] for p in catalog}
    count = 0
    for key, guide in records.items():
        for entry in guide['entries']:
            if entry.get('encounterKind') != 'alola-1':
                continue
            ultra = entry['game'] in ('Pokémon Ultra Sun', 'Pokémon Ultra Moon')
            entry['method'] = (
                'SOS shiny hunting: clear Ilima’s Verdant Cavern trial. '
                'Start a regular wild battle with an eligible caller in the '
                'listed area; an SOS-table target may be an ally of a different '
                'species rather than a suitable caller itself. Lower the '
                'caller’s HP and use an Adrenaline Orb from the Bag. Orbs are '
                'sold at Poké Marts after three trials; earlier field pickups '
                'also exist. Keep a caller alive and defeat unwanted allies; '
                'avoid paralysis, sleep or other persistent status on the '
                'caller because status prevents calls. Manage PP so the '
                'caller does not faint from Struggle. When the shiny arrives, '
                'remove the other wild Pokémon before throwing a Poké Ball. '
                'Shiny bonuses count answered calls: 5 total rolls at 11, '
                '9 at 21, and 13 at 31; Shiny Charm adds its extra rolls. '
            )
            entry['method'] += (
                'Ultra Sun/Ultra Moon require the Orb for repeated calls; '
                'the counter caps at 255 and retains its bonuses. '
                if ultra else
                'Sun/Moon’s counter wraps after 255 called Pokémon, resetting '
                'the bonuses before they build again. '
            )
            note = NOTES.get(species[key])
            if note:
                entry['method'] += note + ' '
            entry['method'] += 'Caller, time and weather requirements for all other table entries remain under review; use the linked SOS ally table for the target.'
            entry['sourceReferences'] = sorted(set(entry.get('sourceReferences', []) + [entry['source'], SOURCE, ORB]))
            entry['huntingTechnique'] = 'alola-sos'
            count += 1
    return count
