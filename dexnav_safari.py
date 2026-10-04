"""ORAS Safari Zone DexNav locations, reviewed against Bulbapedia's Gen VI tables.

Keep tall grass, long grass and water separate: their access requirements differ.
The Safari Game fee and Safari Balls belong to Gen III, not these remakes.
"""

SOURCE = 'https://bulbapedia.bulbagarden.net/wiki/Hoenn_Safari_Zone#Generation_VI'

# Each area's two uncommon species are restricted to their respective grass type.
GRASS = {
    1: ([25, 44, 54, 84], [44, 54, 84, 203], '', 'Acro Bike and Surf required'),
    2: ([44, 54, 84, 178], [44, 54, 84, 202], '', 'Mach Bike required'),
    3: ([44, 54, 84, 111], [44, 54, 84, 214], 'Mach Bike required', 'Acro Bike required'),
    4: ([44, 54, 84, 232], [44, 54, 84, 127], 'Acro Bike required', 'Mach Bike and Surf required'),
}


def add_locations(result, games):
    """Append verified locations to the existing species/game collection."""
    for game in games:
        for area, (tall, long, tall_access, long_access) in GRASS.items():
            for terrain, species_list, access in (
                ('tall grass', tall, tall_access),
                ('long grass', long, long_access),
            ):
                location = f'Safari Zone · Area {area} · {terrain}'
                if access:
                    location += ' · ' + access
                for species in species_list:
                    result[(species, game)].add(location)

            # These species require the story unlock for foreign hidden encounters.
            # Northern areas require a bike; exact reachable patches vary by bike.
            for species in (14, 17, 427):
                location = f'Safari Zone · Area {area} · tall grass · hidden-only after defeating or capturing Groudon/Kyogre'
                if tall_access:
                    location += ' · ' + tall_access
                result[(species, game)].add(location)

            for species in (54, 118, 119, 129):
                result[(species, game)].add(
                    f'Safari Zone · Area {area} · water · Surf required to approach searched Pokémon'
                    + (' · bike required to reach northern area' if area in (3, 4) else '')
                )

