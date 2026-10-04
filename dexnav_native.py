"""Source-reviewed native ORAS DexNav encounters absent from the CSV snapshot.

Native targets can be searched after obtaining the species. They do not need
the foreign-species unlock after Groudon/Kyogre. Fishing targets are searched
as water encounters, so approaching them requires Surf rather than a rod.
"""

# Each forest is a different daily map; preserve its roster instead of merging
# all eight maps into a misleading generic Mirage Forest encounter.
MIRAGE_ACCESS = ('soar using the Eon Flute from Steven after defeating or capturing '
                 'Groudon/Kyogre; this specific daily Mirage spot must be present, '
                 'with additional spots possible through StreetPass')
MIRAGE_FORESTS = (
    ('west of Route 105', (205, 440)),
    ('south of Route 109', (191, 531)),
    ('north of Route 111', (402, 636)),
    ('west of Route 114', (114, 191, 432, 548)),
    ('north of Lilycove City', (114, 191, 421, 432)),
    ('north of Route 124', (37, 114, 191, 432)),
    ('east of Mossdeep City', (114, 191, 431, 572)),
    ('south of Route 132', (191, 531, 548)),
)

MIRAGE_ISLANDS = (
    ('west of Route 104', (49, 178, 523, 555)),
    ('west of Dewford Town', (49, 114, 178, 523)),
    ('north of Route 113', (555, 636)),
    ('north of Route 124', (49, 53, 178, 523)),
    ('north of Route 125', (137, 432)),
    ('south of Pacifidlog Town', (178, 531)),
    ('south of Route 132', (132, 517)),
    ('south of Route 134', (49, 178, 523, 556)),
)
MIRAGE_MOUNTAINS = (
    ('west of Route 104', (205, 232, 234, 402)),
    ('north of Lilycove City', (205, 232, 402, 627)),
    ('north of Route 125', (114, 440, 531)),
    ('northeast of Route 125', (205, 232, 402, 629)),
    ('east of Route 125', (240, 555)),
    ('southeast of Route 129', (137, 178, 517)),
    ('south of Route 129', (239, 523)),
    ('south of Route 131', (203, 205, 232, 402)),
)

NATIVE_LOCATIONS = tuple({
    'location': 'Mirage Forest',
    'species': roster,
    'terrain': place + ' grass',
    'requirements': MIRAGE_ACCESS + (
        '; Cherrim is encountered in Overcast Forme' if 421 in roster else ''),
    'source': 'https://bulbapedia.bulbagarden.net/wiki/Mirage_Forest_('
              + place.replace(' ', '_') + ')#Pokémon',
} for place, roster in MIRAGE_FORESTS) + tuple({
    'location': location,
    'species': roster,
    'terrain': place + ' grass',
    'requirements': MIRAGE_ACCESS + (
        '; Darmanitan is encountered in Standard Mode' if 555 in roster else ''),
    'source': 'https://bulbapedia.bulbagarden.net/wiki/'
              + location.replace(' ', '_') + '_('
              + place.replace(' ', '_') + ')#Pokémon',
} for location, maps in (('Mirage Island', MIRAGE_ISLANDS),
                         ('Mirage Mountain', MIRAGE_MOUNTAINS))
  for place, roster in maps) + (
    {
        'location': 'Mirage Cave',
        'species': (563, 599),
        'terrain': 'north of Route 124 cave floor',
        'requirements': 'soar using the Eon Flute from Steven after defeating or capturing Groudon/Kyogre; this specific daily Mirage spot must be present, with additional spots possible through StreetPass',
        'source': 'https://bulbapedia.bulbagarden.net/wiki/Mirage_Cave_(north_of_Route_124)#Pokémon',
    },
    {
        'location': 'Mirage Cave',
        'species': (95, 602),
        'terrain': 'southeast of Route 129 cave floor',
        'requirements': 'soar using the Eon Flute from Steven after defeating or capturing Groudon/Kyogre; this specific daily Mirage spot must be present, with additional spots possible through StreetPass',
        'source': 'https://bulbapedia.bulbagarden.net/wiki/Mirage_Cave_(southeast_of_Route_129)#Pokémon',
    },
    {
        'location': 'Mirage Cave',
        'species': (79, 563, 602),
        'terrain': 'south of Route 131 cave floor',
        'requirements': 'soar using the Eon Flute from Steven after defeating or capturing Groudon/Kyogre; this specific daily Mirage spot must be present, with additional spots possible through StreetPass',
        'source': 'https://bulbapedia.bulbagarden.net/wiki/Mirage_Cave_(south_of_Route_131)#Pokémon',
    },
    {
        'location': 'Mirage Cave',
        'species': (132, 530, 602),
        'terrain': 'north of Route 132 cave floor',
        'requirements': 'soar using the Eon Flute from Steven after defeating or capturing Groudon/Kyogre; this specific daily Mirage spot must be present, with additional spots possible through StreetPass',
        'source': 'https://bulbapedia.bulbagarden.net/wiki/Mirage_Cave_(north_of_Route_132)#Pokémon',
    },
    {
        'location': 'Mirage Cave',
        'species': (201,),
        'terrain': 'south of Route 107 cave floor',
        'requirements': 'soar using the Eon Flute from Steven after defeating or capturing Groudon/Kyogre; this specific daily Mirage spot must be present, with additional spots possible through StreetPass',
        'source': 'https://bulbapedia.bulbagarden.net/wiki/Mirage_Cave_(south_of_Route_107)#Pokémon',
    },
    {
        'location': 'Mirage Cave',
        'species': (79, 602),
        'terrain': 'north of Fallarbor Town cave floor',
        'requirements': 'soar using the Eon Flute from Steven after defeating or capturing Groudon/Kyogre; this specific daily Mirage spot must be present, with additional spots possible through StreetPass',
        'source': 'https://bulbapedia.bulbagarden.net/wiki/Mirage_Cave_(north_of_Fallarbor_Town)#Pokémon',
    },
    {
        'location': 'Mirage Cave',
        'species': (599, 602),
        'terrain': 'west of Route 115 cave floor',
        'requirements': 'soar using the Eon Flute from Steven after defeating or capturing Groudon/Kyogre; this specific daily Mirage spot must be present, with additional spots possible through StreetPass',
        'source': 'https://bulbapedia.bulbagarden.net/wiki/Mirage_Cave_(west_of_Route_115)#Pokémon',
    },
    {
        'location': 'Mirage Cave',
        'species': (95, 530, 599, 602),
        'terrain': 'north of Fortree City cave floor',
        'requirements': 'soar using the Eon Flute from Steven after defeating or capturing Groudon/Kyogre; this specific daily Mirage spot must be present, with additional spots possible through StreetPass',
        'source': 'https://bulbapedia.bulbagarden.net/wiki/Mirage_Cave_(north_of_Fortree_City)#Pokémon',
    },
    {
        'location': 'Victory Road',
        'species': (42, 72, 73, 129, 320, 370),
        'terrain': 'entrance, 1F and B1F water',
        'requirements': 'initially reach Ever Grande with Surf and Waterfall after the Rain Badge; Surf required for searches and Strength for deeper traversal',
        'source': 'https://bulbapedia.bulbagarden.net/wiki/Victory_Road_(Hoenn)#Generation_VI',
    },
    {
        'location': 'Victory Road',
        'species': (42, 118, 129, 339),
        'terrain': '2F water',
        'requirements': 'initially reach Ever Grande with Surf and Waterfall after the Rain Badge; Surf and Strength required to traverse to 2F; Waterfall accesses upper pools',
        'source': 'https://bulbapedia.bulbagarden.net/wiki/Victory_Road_(Hoenn)#Generation_VI',
    },
    {
        'location': 'Sea Mauville',
        'species': (72, 278, 279, 129, 320),
        'terrain': 'exterior water',
        'requirements': 'Surf required from Route 108; Dive through the facility is needed for the northern exterior',
        'source': 'https://bulbapedia.bulbagarden.net/wiki/Sea_Mauville#Outside_2',
    },
    {
        'location': 'Sea Mauville',
        'species': (72, 129, 320),
        'terrain': 'interior surface water',
        'requirements': 'Surf required from Route 108 and to approach searched Pokémon; Dive opens the submerged section and northern exterior',
        'source': 'https://bulbapedia.bulbagarden.net/wiki/Sea_Mauville#Inside_2',
    },
    {
        'location': 'Sealed Chamber',
        'species': (41, 42, 72, 129, 320, 116),
        'terrain': 'entrance water',
        'requirements': 'Surf through the Route 134 currents, Dive at the entrance and surface at the lit area; Dig and the Relicanth/Wailord party puzzle unlock the deeper chamber and legendary caves rather than these water encounters',
        'source': 'https://bulbapedia.bulbagarden.net/wiki/Sealed_Chamber#Generation_VI',
    },
    {
        'location': 'Team Aqua Hideout',
        'species': (),
        'alphaSapphireSpecies': (72, 129, 320, 120),
        'terrain': 'interior water',
        'requirements': 'Alpha Sapphire only; Surf required; the interior opens after Team Aqua steals the submarine in Slateport',
        'source': 'https://bulbapedia.bulbagarden.net/wiki/Aqua_Hideout#Generation_VI',
    },
    {
        'location': 'Team Magma Hideout',
        'species': (),
        'omegaRubySpecies': (72, 129, 320, 120),
        'terrain': 'Lilycove interior water',
        'requirements': 'Omega Ruby only; Surf required; the interior opens after Team Magma steals the submarine in Slateport',
        'source': 'https://bulbapedia.bulbagarden.net/wiki/Magma_Hideout_(Lilycove_City)#Generation_VI',
    },
    {
        'location': 'Seafloor Cavern',
        'species': (42, 73, 72, 129, 320),
        'terrain': 'entrance water',
        'requirements': 'Surf and Dive required to reach the entrance from Route 128',
        'source': 'https://bulbapedia.bulbagarden.net/wiki/Seafloor_Cavern#Generation_VI',
    },
    {
        'location': 'Seafloor Cavern',
        'species': (42, 73, 72, 129, 320),
        'terrain': 'rooms 5 and 6 water',
        'requirements': 'Surf and Dive required to enter; Strength required for interior navigation; Rock Smash is optional in ORAS',
        'source': 'https://bulbapedia.bulbagarden.net/wiki/Seafloor_Cavern#Generation_VI',
    },
    {
        'location': 'Seafloor Cavern',
        'species': (42, 41),
        'terrain': 'rooms 1-9 cave floors, including searching native horde species Zubat',
        'requirements': 'Surf and Dive required to enter; Strength required for interior navigation; Rock Smash is optional in ORAS',
        'source': 'https://bulbapedia.bulbagarden.net/wiki/Seafloor_Cavern#Generation_VI',
    },
    {
        'location': 'Jagged Pass',
        'species': (66, 322, 325),
        'terrain': 'native grass',
        'requirements': 'defeat Maxie in Omega Ruby or Archie in Alpha Sapphire on Mt. Chimney; Acro Bike enables uphill ledge traversal',
        'source': 'https://bulbapedia.bulbagarden.net/wiki/Jagged_Pass#Generation_VI',
    },
    {
        'location': 'Scorched Slab',
        'species': (42,),
        'terrain': '1F cave floor',
        'requirements': 'Surf across the Route 120 lake to enter',
        'source': 'https://bulbapedia.bulbagarden.net/wiki/Scorched_Slab#Generation_VI',
    },
    {
        'location': 'Scorched Slab',
        'species': (41, 42),
        'terrain': 'B1F-B3F cave floors, including searching the native horde species Zubat',
        'requirements': 'Surf across the Route 120 lake to enter; Flash illuminates dark floors; Strength creates an optional shortcut',
        'source': 'https://bulbapedia.bulbagarden.net/wiki/Scorched_Slab#Generation_VI',
    },
    {
        'location': 'Scorched Slab',
        'species': (41, 42, 118, 129, 339),
        'terrain': '1F and B1F water',
        'requirements': 'Surf required to enter and approach searched Pokémon',
        'source': 'https://bulbapedia.bulbagarden.net/wiki/Scorched_Slab#Generation_VI',
    },
    {
        'location': 'Cave of Origin',
        'species': (41, 42),
        'omegaRubySpecies': (303,),
        'alphaSapphireSpecies': (302,),
        'terrain': 'native cave floors, including searching the native horde species Zubat',
        'requirements': 'story access in Sootopolis after the Seafloor Cavern confrontation; reach Sootopolis through Route 126 using Surf and Dive or return by Fly',
        'source': 'https://bulbapedia.bulbagarden.net/wiki/Cave_of_Origin#Generation_VI',
    },
    {
        'location': 'Route 126',
        'species': (72, 73, 279, 129, 320),
        'terrain': 'surface water',
        'requirements': 'Surf required to approach searched Pokémon; Dive is needed only for underwater passages and isolated surface pockets',
        'source': 'https://bulbapedia.bulbagarden.net/wiki/Hoenn_Route_126#Generation_VI',
    },
    {
        'location': 'Route 127',
        'species': (72, 73, 279, 129, 320),
        'terrain': 'surface water',
        'requirements': 'Surf required to approach searched Pokémon; accessed south of Mossdeep City',
        'source': 'https://bulbapedia.bulbagarden.net/wiki/Hoenn_Route_127#Generation_VI',
    },
    {
        'location': 'Route 128',
        'species': (72, 73, 279, 129, 320, 222, 370),
        'terrain': 'surface water',
        'requirements': 'Surf required to approach searched Pokémon; Dive is needed for Seafloor Cavern rather than the surface searches',
        'source': 'https://bulbapedia.bulbagarden.net/wiki/Hoenn_Route_128#Generation_VI',
    },
    {
        'location': 'Route 129',
        'species': (72, 73, 279, 129, 320),
        'terrain': 'surface water',
        'requirements': 'Surf required to approach searched Pokémon; Dive is needed only for underwater passages',
        'source': 'https://bulbapedia.bulbagarden.net/wiki/Hoenn_Route_129#Generation_VI',
    },
    {
        'location': 'Route 131',
        'species': (72, 73, 279, 129, 320, 116, 117),
        'terrain': 'surface water',
        'requirements': 'Surf required to approach searched Pokémon; the Delta Episode seal restricts Sky Pillar entry, not Route 131 water',
        'source': 'https://bulbapedia.bulbagarden.net/wiki/Hoenn_Route_131#Generation_VI',
    },
    {
        'location': 'Route 132',
        'species': (72, 73, 279, 129, 320, 116, 117),
        'terrain': 'calm surface water',
        'requirements': 'Surf required; start from Pacifidlog and use calm water pockets because currents flow east to west',
        'source': 'https://bulbapedia.bulbagarden.net/wiki/Hoenn_Route_132#Generation_VI',
    },
    {
        'location': 'Route 133',
        'species': (72, 73, 279, 129, 320, 116, 117),
        'terrain': 'calm surface water',
        'requirements': 'Surf required; use calm water pockets along the east-to-west currents from Route 132',
        'source': 'https://bulbapedia.bulbagarden.net/wiki/Hoenn_Route_133#Generation_VI',
    },
    {
        'location': 'Route 134',
        'species': (72, 278, 279, 129, 320, 116, 117),
        'terrain': 'calm surface water',
        'requirements': 'Surf required; use calm water pockets along the east-to-west currents from Route 133',
        'source': 'https://bulbapedia.bulbagarden.net/wiki/Hoenn_Route_134#Generation_VI',
    },
    {
        'location': 'Route 122',
        'species': (72, 278, 279, 129, 320),
        'terrain': 'surface water',
        'requirements': 'Surf required to approach searched Pokémon',
        'source': 'https://bulbapedia.bulbagarden.net/wiki/Hoenn_Route_122#Generation_VI',
    },
    {
        'location': 'Route 123',
        'species': (44, 264, 279, 352, 353, 278),
        'terrain': 'long grass, including searching native horde species',
        'requirements': '',
        'source': 'https://bulbapedia.bulbagarden.net/wiki/Hoenn_Route_123#Generation_VI',
    },
    {
        'location': 'Route 123',
        'species': (183, 184, 283, 284, 118, 129, 341, 342),
        'terrain': 'ponds',
        'requirements': 'Surf required to approach searched Pokémon',
        'source': 'https://bulbapedia.bulbagarden.net/wiki/Hoenn_Route_123#Generation_VI',
    },
    {
        'location': 'Route 124',
        'species': (72, 73, 279, 129, 320),
        'terrain': 'surface water',
        'requirements': 'Surf required; defeat Team Magma in Omega Ruby or Team Aqua in Alpha Sapphire at the Lilycove hideout to open the eastern sea route',
        'source': 'https://bulbapedia.bulbagarden.net/wiki/Hoenn_Route_124#Generation_VI',
    },
    {
        'location': 'Route 125',
        'species': (72, 73, 279, 129, 320),
        'terrain': 'surface water',
        'requirements': 'Surf required to approach searched Pokémon; accessed north of Mossdeep City',
        'source': 'https://bulbapedia.bulbagarden.net/wiki/Hoenn_Route_125#Generation_VI',
    },
    {
        'location': 'Route 110',
        'species': (72, 278, 279, 129, 320),
        'terrain': 'water beneath the Cycling Road',
        'requirements': 'Surf required to approach searched Pokémon',
        'source': 'https://bulbapedia.bulbagarden.net/wiki/Hoenn_Route_110#Generation_VI',
    },
    {
        'location': 'Route 119',
        'species': (44, 264, 352, 357, 43),
        'terrain': 'long grass, including searching the native horde species Oddish',
        'requirements': 'cross the Route 118 inlet using Surf to reach Route 119 from Mauville',
        'source': 'https://bulbapedia.bulbagarden.net/wiki/Hoenn_Route_119#Generation_VI',
    },
    {
        'location': 'Route 119',
        'species': (72, 278, 279, 129, 318, 319),
        'terrain': 'river water',
        'requirements': 'Surf required to approach searched Pokémon; Waterfall is needed only for the upper water beyond the falls',
        'source': 'https://bulbapedia.bulbagarden.net/wiki/Hoenn_Route_119#Generation_VI',
    },
    {
        'location': 'Route 120',
        'species': (44, 264, 352, 357, 359, 43, 183),
        'terrain': 'western long grass near Ancient Tomb, including searching native horde species',
        'requirements': '',
        'source': 'https://bulbapedia.bulbagarden.net/wiki/Hoenn_Route_120#Generation_VI',
    },
    {
        'location': 'Route 120',
        'species': (184, 283, 284, 72, 129, 339),
        'terrain': 'eastern ponds',
        'requirements': 'Surf required to approach searched Pokémon',
        'source': 'https://bulbapedia.bulbagarden.net/wiki/Hoenn_Route_120#Generation_VI',
    },
    {
        'location': 'Route 120',
        'species': (184, 283, 284, 118, 129, 339),
        'terrain': 'western pond near Ancient Tomb',
        'requirements': 'Surf required to approach searched Pokémon',
        'source': 'https://bulbapedia.bulbagarden.net/wiki/Hoenn_Route_120#Generation_VI',
    },
    {
        'location': 'Route 121',
        'species': (44, 264, 279, 352, 353, 278),
        'terrain': 'grass and long grass, including searching native horde species',
        'requirements': '',
        'source': 'https://bulbapedia.bulbagarden.net/wiki/Hoenn_Route_121#Generation_VI',
    },
    {
        'location': 'Pacifidlog Town',
        'species': (72, 73, 129, 279, 320),
        'terrain': 'surrounding sea',
        'requirements': 'Surf required to approach searched Pokémon',
        'source': 'https://bulbapedia.bulbagarden.net/wiki/Pacifidlog_Town#Generation_VI',
    },
    {
        'location': 'Mossdeep City',
        'species': (72, 73, 129, 279, 320),
        'terrain': 'coastal water',
        'requirements': 'Surf required to approach searched Pokémon',
        'source': 'https://bulbapedia.bulbagarden.net/wiki/Mossdeep_City#Generation_VI',
    },
    {
        'location': 'Ever Grande City',
        'species': (72, 73, 129, 222, 279, 320, 370),
        'terrain': 'coastal water',
        'requirements': 'Surf required to approach searched Pokémon; Waterfall is needed to climb to the Pokémon Center and Victory Road entrance, rather than to search the sea below the waterfall',
        'source': 'https://bulbapedia.bulbagarden.net/wiki/Ever_Grande_City#Generation_VI',
    },
    {
        'location': 'Route 102',
        'species': (261, 263, 265, 280, 283),
        'omegaRubySpecies': (273,),
        'alphaSapphireSpecies': (270,),
        'terrain': 'tall grass',
        'requirements': '',
        'source': 'https://bulbapedia.bulbagarden.net/wiki/Hoenn_Route_102#Generation_VI',
    },
    {
        'location': 'Route 102',
        'species': (118, 129, 183, 184, 283, 284, 341),
        'terrain': 'pond',
        'requirements': 'Surf required to approach searched Pokémon',
        'source': 'https://bulbapedia.bulbagarden.net/wiki/Hoenn_Route_102#Generation_VI',
    },
)


def add_locations(result, games):
    """Merge only reviewed terrain/version assignments into the route inventory."""
    for game in games:
        version_key = 'omegaRubySpecies' if game.endswith('Omega Ruby') else 'alphaSapphireSpecies'
        for record in NATIVE_LOCATIONS:
            label = record['location'] + ' · ' + record['terrain']
            if record['requirements']:
                label += ' · ' + record['requirements']
            for species in record['species'] + record.get(version_key, ()):
                result[(species, game)].add(label)


def source_references(locations):
    """Retain the reviewed location source for every matching native assignment."""
    references = list(dict.fromkeys(
        record['source'] for record in NATIVE_LOCATIONS
        if any(label.startswith(record['location'] + ' · ' + record['terrain']) for label in locations)
    ))
    if any('Eon Flute' in label for label in locations):
        references.append('https://bulbapedia.bulbagarden.net/wiki/Eon_Flute#Acquisition')
    return references
