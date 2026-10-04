"""Bundle runtime files and rights notices; omit audit snapshots and user data."""
import os
from pathlib import Path
import zipfile

root = Path(os.environ['SHINYDEX_BUILD_ROOT'])
files = [root / name for name in ('index.html', 'main.js', 'style.css', 'updater.js', 'data.json', 'hunts.json', 'ATTRIBUTIONS.txt', 'THIRD_PARTY_NOTICES.md')]
files += sorted((root / 'assets' / 'pokemon').rglob('*.png'))
files += sorted((root / 'licenses').glob('*.txt'))
files.append(root / 'reference' / 'pkhex' / 'LICENSE')
with zipfile.ZipFile(root / 'dist' / 'web.zip', 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
    for path in files:
        # Fixed timestamps and ordering make unchanged payloads reproducible.
        info = zipfile.ZipInfo(path.relative_to(root).as_posix(), (2026, 1, 1, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        bundle.writestr(info, path.read_bytes(), compresslevel=9)
print(f'Bundled {len(files)} runtime and notice files.')
