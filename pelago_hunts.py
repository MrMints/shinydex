"""Add independently reviewed story gates to decoded Isle Abeens encounters.

The legality tables establish species and shiny eligibility. Gameplay access
and recruitment come from the separate Pelago reference; do not infer shiny
odds or reset behavior from legality records.
"""
SOURCE = 'https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9_Pelago'
SM = (
    (21, 41, 64, 81, 90, 92, 198, 278, 426, 703, 731),
    (60, 120, 127, 661, 709, 771),
    (227, 375, 707),
    (123, 131, 429, 587),
)
USUM = (
    (41, 79, 86, 120, 122, 124, 180, 222, 278, 731, 742),
    (127, 163, 177, 701, 764, 771),
    (131, 200, 354),
    (209, 357, 430, 667),
)
GATES = ('initial Isle Abeens access', 'reaching Ula\u2019ula Island',
         'reaching Poni Island', 'becoming Champion')


def reviewed_rosters():
    """Return earliest story gate for every visitor in each retail version."""
    result = {}
    for title, stages, exclusive, stage in (
        ('Sun', SM, 627, 0), ('Moon', SM, 629, 0),
        ('Ultra Sun', USUM, 228, 2), ('Ultra Moon', USUM, 309, 2),
    ):
        roster = {sid: gate for gate, group in enumerate(stages) for sid in group}
        assert exclusive not in roster
        roster[exclusive] = stage
        result['Pok\u00e9mon ' + title] = roster
    return result


def merge(records):
    rosters = reviewed_rosters()
    observed = {game: set() for game in rosters}
    count = 0
    for key, guide in records.items():
        for entry in guide['entries']:
            if entry.get('encounterKind') != 'pelago':
                continue
            game, sid = entry['game'], int(key)
            assert game in rosters and sid in rosters[game], (game, sid)
            assert entry['gameFormId'] == 0 and entry['status'] == 'Huntable'
            observed[game].add(sid)
            gate = rosters[game][sid]
            unlock = ('Register Charizard Glide after Kiawe\u2019s trial'
                      if game in ('Pok\u00e9mon Sun', 'Pok\u00e9mon Moon') else
                      'After Kiawe\u2019s trial, meet Mohn on Route 7')
            entry['method'] = (
                'Pok\u00e9 Pelago \u00b7 befriend a shiny Isle Abeens visitor. '
                + unlock + '; keep at least one Pok\u00e9mon in your PC Boxes '
                'for the first visit. This species joins the visitor pool at '
                + GATES[gate] + '. Visitors are selected every 24 hours; '
                'Pok\u00e9 Beans in the crate make that timer run twice as fast. '
                'Tap a visitor; if it stays and displays a heart at a later '
                'selection, tap it again to recruit it into your party or PC.'
            )
            entry['locations'] = ['Pok\u00e9 Pelago \u00b7 Isle Abeens']
            entry['pelagoUnlockStage'] = gate
            entry['sourceReferences'] = sorted({entry['source'], SOURCE})
            entry['verification'] += '; visitor roster and earliest story gate separately source-reviewed'
            count += 1
    assert all(observed[g] == set(rosters[g]) for g in rosters), observed
    assert count == 100, count
    return count
