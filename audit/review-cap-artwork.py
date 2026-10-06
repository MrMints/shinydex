"""Capture cap artwork; absent shiny renders must never be fabricated."""
import runpy
from pathlib import Path

main = runpy.run_path(str(Path(__file__).with_name('review-persistent-artwork.py')))['main']
GROUPS = {25: [('original-cap', ('O', 'O')), ('hoenn-cap', ('H', 'H')),
              ('sinnoh-cap', ('S', 'S')), ('unova-cap', ('U', 'U')),
              ('kalos-cap', ('K', 'K')), ('alola-cap', ('A', 'A')),
              ('partner-cap', ('P', 'P')), ('world-cap', ('W', 'W'))]}

if __name__ == '__main__':
    main(GROUPS, 'cap')
