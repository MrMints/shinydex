"""Check published visitor guides retain story gates and version exclusions."""
import json
from pathlib import Path

guides = json.loads(Path('hunts.json').read_text())
rows = {(int(key), row['game']): row for key, guide in guides.items()
        for row in guide['entries'] if row.get('encounterKind') == 'pelago'}
assert len(rows) == 100
for (sid, game), row in rows.items():
    assert row['status'] == 'Huntable' and row['gameFormId'] == 0
    for required in ('PC Boxes', '24 hours', 'twice as fast', 'heart', 'recruit'):
        assert required in row['method'], (sid, game, required)
    assert any('Pok%C3%A9_Pelago' in ref for ref in row['sourceReferences'])
for title, exclusive, excluded in (
    ('Sun', 627, 629), ('Moon', 629, 627),
    ('Ultra Sun', 228, 309), ('Ultra Moon', 309, 228),
):
    game = 'Pokémon ' + title
    assert (exclusive, game) in rows and (excluded, game) not in rows
    assert sum(g == game for _, g in rows) == 25
    if title.startswith('Ultra'):
        assert 'Mohn on Route 7' in rows[exclusive, game]['method']
        assert rows[exclusive, game]['pelagoUnlockStage'] == 2
        assert rows[430, game]['pelagoUnlockStage'] == 3
        assert rows[120, game]['pelagoUnlockStage'] == 0
    else:
        assert 'Charizard Glide' in rows[exclusive, game]['method']
        assert rows[exclusive, game]['pelagoUnlockStage'] == 0
        assert rows[120, game]['pelagoUnlockStage'] == 1
        assert rows[227, game]['pelagoUnlockStage'] == 2
        assert rows[131, game]['pelagoUnlockStage'] == 3
print('Verified Pelago story gates, recruitment details and version exclusions; odds/reset audit remains pending.')
