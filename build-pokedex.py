"""Build offline, game/form-labeled descriptive entries from pinned/cached sources."""
import csv
import hashlib
import html
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REF = ROOT / 'reference' / 'pokeapi-pokedex'

def templates(text):
    depth, start = 0, 0
    for match in re.finditer(r'\{\{|\}\}', text):
        if match[0] == '{{':
            if depth == 0:
                start = match.start()
            depth += 1
        elif depth:
            depth -= 1
            if depth == 0:
                yield text[start:match.end()]

def parts(text):
    chunks, start, braces, links = [], 0, 0, 0
    for match in re.finditer(r'\{\{|\}\}|\[\[|\]\]|\|', text):
        token = match[0]
        if token == '{{': braces += 1
        elif token == '}}': braces -= 1
        elif token == '[[': links += 1
        elif token == ']]': links -= 1
        elif braces == 0 and links == 0:
            chunks.append(text[start:match.start()])
            start = match.end()
    return chunks + [text[start:]]

def plain(text, unresolved):
    for template in list(templates(text)):
        args = parts(template[2:-2])
        name = args[0].strip().lower()
        if name == 'scpkmn': value = 'Pokémon'
        elif name == 'scball': value = 'Poké Ball'
        elif name == 'berries': value = 'Berries'
        elif name == 'sic': value = '[sic]'
        elif name in ('tt', 'obp', 'pkmn2'):
            value = args[1] if len(args) > 1 else ''
        elif name.startswith('sup/3'):
            value = {'R': '[Ruby]', 'S': '[Sapphire]', 'E': '[Emerald]'}.get(args[-1], args[-1])
        elif name.startswith('sup/4'):
            value = {'HG': '[HeartGold]', 'SS': '[SoulSilver]'}.get(args[-1], args[-1])
        elif name in ('p', 'pkmn', 'a', 'm', 't', 'type', 'dl', 'color2', 'color', 'ga', 'g', 'wp', 'w', 'sm', 'sup', 'sub', 'small', 'status', 'game'):
            value = args[-1] if len(args) > 1 else ''
        else:
            unresolved.add(template)
            value = template
        if value != template:
            value = plain(value, unresolved)
        text = text.replace(template, value)
    text = re.sub(r'\[\[([^\[\]]+)\]\]', lambda m: m[1].split('|')[-1], text)
    text = re.sub(r'<br\s*/?>', ' / ', text, flags=re.I)
    text = re.sub(r'<ref\b[^>]*>.*?</ref>|<ref\b[^>]*/>', '', text, flags=re.S)
    text = re.sub(r'<[^>]+>', '', text)
    return ' '.join(html.unescape(text).replace("'''", '').replace("''", '').split())

def game_id(label):
    aliases = {"Let's Go Pikachu": 'lets-go-pikachu', "Let's Go Eevee": 'lets-go-eevee',
               'Legends: Z-A': 'legends-za', 'XD': 'xd'}
    return aliases.get(label, re.sub(r'[^a-z0-9]+', '-', label.lower()).strip('-'))

def build():
    catalog = json.loads((ROOT / 'data.json').read_text(encoding='utf-8'))
    species_ids = sorted({p['id'] for p in catalog})
    entries = defaultdict(list)
    games = {}
    unresolved = set()
    no_entry_statements = {}
    missing = []
    hashes = {}
    # Bulbapedia preserves form labels and fills the modern-game gaps in PokéAPI.
    for sid in species_ids:
        file = ROOT / 'reference' / 'bulbapedia-pokedex' / f'{sid}.json'
        if not file.exists():
            missing.append(sid)
            continue
        snapshot = json.loads(file.read_text(encoding='utf-8'))
        hashes[str(sid)] = hashlib.sha256(file.read_bytes()).hexdigest()
        form = None
        statements = []
        for template in templates(snapshot['wikitext']):
            args = parts(template[2:-2])
            name = args[0].strip()
            params = dict(a.split('=', 1) for a in args[1:] if '=' in a)
            if name.startswith('Dex/Gen/'):
                form = None
            elif name == 'Dex/Form':
                form = plain(args[1], unresolved) if len(args) > 1 else None
            elif name in ('Dex/NE', 'Dex/NA'):
                statements.append({'template': name, 'statement': plain('|'.join(args[1:]), set()), 'formLabel': form})
            elif re.fullmatch(r'Dex/Entry[1-4]', name) and 'entry' in params:
                text = plain(params['entry'], unresolved)
                for field in ('v', 'v2', 'v3', 'v4'):
                    if field not in params: continue
                    label = params[field].strip()
                    gid = game_id(label)
                    games[gid] = {'id': gid, 'name': 'Pokémon ' + label}
                    row = {'gameId': gid, 'formLabel': form, 'text': text,
                           'source': snapshot['source'], 'revisionId': snapshot['revisionId'],
                           'scope': 'source-labeled-form' if form else 'species-default-entry'}
                    if row not in entries[str(sid)]: entries[str(sid)].append(row)
        if statements: no_entry_statements[str(sid)] = statements
    # Keep every English PokéAPI row as fallback, without treating it as form-specific.
    versions = {r['id']: r['identifier'] for r in csv.DictReader((REF / 'versions.csv').open(encoding='utf-8'))}
    names = {r['version_id']: r['name'] for r in csv.DictReader((REF / 'version_names.csv').open(encoding='utf-8')) if r['local_language_id'] == '9'}
    for vid, gid in versions.items():
        label = names.get(vid, gid)
        if gid.endswith('-japan'): label += ' Japan'
        if gid == 'xd': label = 'XD: Gale of Darkness'
        if gid == 'mega-dimension': label = 'Legends: Z-A · Mega Dimension'
        games.setdefault(gid, {'id': gid, 'name': 'Pokémon ' + label})
    pin = json.loads((REF / 'source.json').read_text(encoding='utf-8'))
    fallback = 0
    fallback_rows = []
    for row in csv.DictReader((REF / 'pokemon_species_flavor_text.csv').open(encoding='utf-8')):
        if row['language_id'] != '9' or int(row['species_id']) not in species_ids: continue
        sid, gid = row['species_id'], versions[row['version_id']]
        if any(e['gameId'] == gid and e['formLabel'] is None for e in entries[sid]): continue
        games.setdefault(gid, {'id': gid, 'name': 'Pokémon ' + names[row['version_id']]})
        entries[sid].append({'gameId': gid, 'formLabel': None, 'text': ' '.join(row['flavor_text'].split()),
                             'scope': 'species-default-entry', 'source': f"https://github.com/PokeAPI/pokeapi/blob/{pin['commit']}/data/v2/csv/pokemon_species_flavor_text.csv"})
        fallback += 1
        fallback_rows.append({'speciesId': int(sid), 'gameId': gid})
    for key in entries: entries[key].sort(key=lambda e: (e['gameId'], e['formLabel'] or '', e['text']))
    result = {'schemaVersion': 1, 'language': 'en', 'coverageComplete': False,
              'games': dict(sorted(games.items())), 'species': dict(sorted(entries.items(), key=lambda e: int(e[0])))}
    counts = Counter(e['gameId'] for rows in entries.values() for e in rows)
    for gid, game in games.items():
        game['descriptionCount'] = counts[gid]
        game['descriptionStatus'] = 'recorded' if counts[gid] else 'not-recorded'
    # Write after attaching game-level coverage status.
    (ROOT / 'pokedex-entries.json').write_text(json.dumps(result, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
    report = {'auditComplete': False, 'speciesCount': len(entries), 'entryCount': sum(counts.values()),
              'gameCount': len(games), 'entriesByGame': dict(sorted(counts.items())),
              'missingSpeciesSnapshots': missing, 'unresolvedTemplates': sorted(unresolved),
              'pokeapiFallbackCount': fallback, 'pokeapiFallbackRows': fallback_rows, 'snapshotSha256': hashes,
              'inputSha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(REF.glob('*')) if p.is_file()},
              'sourceNoEntryStatements': no_entry_statements,
              'limitations': ['English descriptive text only; no game-specific Dex numbers.',
                 'Source coverage is not independently verified against every game cartridge or localization.',
                 'Default species text must not be presented as an independently verified entry for every form.',
                 'No-entry source declarations and unavailable games are not shiny locks or encounter evidence.',
                 'DLC descriptions may be recorded under the parent game by the source; do not invent distinct DLC text.',
                 'This is the 1,025-species application catalog, not an exhaustive inventory of all spin-off games.']}
    (ROOT / 'audit' / 'pokedex-entries-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    species_names = {p['id']: p.get('speciesName', p['name']) for p in catalog}
    export = ROOT / 'audit' / 'artifacts' / 'pokedex-entries.csv'
    export.parent.mkdir(parents=True, exist_ok=True)
    with export.open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(['species_id', 'pokemon', 'game_id', 'game', 'form_label', 'description', 'source', 'revision_id'])
        for sid, rows in result['species'].items():
            for entry in rows:
                writer.writerow([sid, species_names[int(sid)], entry['gameId'], games[entry['gameId']]['name'], entry['formLabel'] or '', entry['text'], entry['source'], entry.get('revisionId', '')])
    print(f'{len(entries)} species; {sum(counts.values())} entries; {len(games)} games; {len(missing)} missing snapshots; {len(unresolved)} unresolved templates')

if __name__ == '__main__': build()
