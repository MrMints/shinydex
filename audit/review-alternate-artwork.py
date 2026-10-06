"""Review further persistent forms; identity/eligibility not inferred from images."""
import runpy
from pathlib import Path

main = runpy.run_path(str(Path(__file__).with_name('review-persistent-artwork.py')))['main']

GROUPS = {
    487: [('altered', ''), ('origin', 'O')],
    492: [('land', ''), ('sky', 'S')],
    550: [('red-striped', ''), ('blue-striped', 'B')],
    641: [('incarnate', ''), ('therian', 'T')],
    642: [('incarnate', ''), ('therian', 'T')],
    645: [('incarnate', ''), ('therian', 'T')],
    646: [('', ''), ('black', 'B'), ('white', 'W')],
    647: [('ordinary', ''), ('resolute', 'R')],
    676: [('natural', ''), ('heart', 'He'), ('star', 'St'), ('diamond', 'Di'),
          ('debutante', 'De'), ('matron', 'Ma'), ('dandy', 'Da'),
          ('la-reine', 'La'), ('kabuki', 'Ka'), ('pharaoh', 'Ph')],
    718: [('50', ''), ('10', 'T')],
    720: [('', ''), ('unbound', 'U')],
    774: [('red', ('R', 'R')), ('orange', ('O', 'R')), ('yellow', ('Y', 'R')), ('green', ('G', 'R')),
          ('blue', ('B', 'R')), ('indigo', ('I', 'R')), ('violet', ('V', 'R'))],
    801: [('', ''), ('original', 'O')],
    892: [('single-strike', ''), ('rapid-strike', 'R')],
    893: [('', ''), ('dada', 'D')],
    898: [('', ''), ('ice', 'I'), ('shadow', 'S')],
    901: [('', ''), ('bloodmoon', 'B')],
    999: [('chest', ''), ('roaming', 'R')],
    1017: [('', ''), ('wellspring-mask', 'W'), ('hearthflame-mask', 'H'),
           ('cornerstone-mask', 'C')],
}

if __name__ == '__main__':
    main(GROUPS, 'alternate')
