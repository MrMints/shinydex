"""Capture type/item and additional persistent-form artwork evidence."""
import runpy
from pathlib import Path

main = runpy.run_path(str(Path(__file__).with_name('review-persistent-artwork.py')))['main']
TYPES = ['normal', 'fighting', 'flying', 'poison', 'ground', 'rock', 'bug',
         'ghost', 'steel', 'fire', 'water', 'grass', 'electric', 'psychic',
         'ice', 'dragon', 'dark', 'fairy']
GROUPS = {
    493: [(name, '' if name == 'normal' else name.title()) for name in TYPES],
    773: [(name, '' if name == 'normal' else name.title()) for name in TYPES],
    649: [('', ''), ('douse', 'B'), ('shock', 'Y'), ('burn', 'R'), ('chill', 'W')],
    483: [('', ''), ('origin', 'O')],
    484: [('', ''), ('origin', 'O')],
    800: [('', ''), ('dusk', 'DM'), ('dawn', 'DW')],
    905: [('incarnate', ''), ('therian', 'T')],
    854: [('phony', '_b'), ('antique', 'A_b')],
    855: [('phony', '_b'), ('antique', 'A_b')],
    1012: [('counterfeit', '_b'), ('artisan', 'A_b')],
    1013: [('unremarkable', '_b'), ('masterpiece', 'M_b')],
}

if __name__ == '__main__':
    main(GROUPS, 'type')
