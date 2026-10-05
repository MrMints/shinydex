"""Inventory independent BDSP grass-table time/section data for manual review.

This does not promote parsed rows into the guide or certify terrain/access.
Download caches live in TEMP; retained hashes identify the reviewed source bytes.
"""
import hashlib,html,json,os,re,urllib.request
from pathlib import Path
from bdsp_radar_hunts import GARDEN_INTRODUCTIONS, routes

ROOT=Path(__file__).parent
CACHE=Path(os.environ['TEMP'])/'shinydex-bdsp-source-tables'
CACHE.mkdir(exist_ok=True)
SPECIAL={'Mount Coronet':'mt.coronet','Trophy Garden':'trophygarden',
         'Sendoff Spring':'sendoffspring'}
def plain(value):
    return ' '.join(html.unescape(re.sub(r'<[^>]+>',' ',value)).split())

def decode_page(raw):
    # These source pages mix UTF-8 and legacy Windows-1252 across locations.
    # Replacement decoding would corrupt accented encounter headings and could
    # accidentally retain the preceding ordinary-encounter pool for Radar rows.
    try:
        return raw.decode('utf-8')
    except UnicodeDecodeError:
        return raw.decode('cp1252')
def parse(source):
    section='main';pool=None;found=[]
    # Encounter tables are flat in these pages. A heading embedded in the
    # first version's table also applies to the following second-version table.
    for match in re.finditer(r'<h([234])\b[^>]*>(.*?)</h\1>|<table\b[^>]*>.*?</table>',source,re.S|re.I):
        value=match.group()
        heading=re.search(r'<h([234])\b[^>]*>(.*?)</h\1>',value,re.S|re.I)
        if heading:
            title=plain(heading[2])
            if title.startswith('Random Encounter') or title in ('PokéRadar','Poké Radar','Swarm','Special Pokémon'):
                pool=title
            elif heading[1]=='2' and title not in ('Trainers','Items'):
                section=title
            elif title in ('Trainers','Items') or title.startswith(('Honey','Surf','Fishing')):
                pool=None
        if not value.lower().startswith('<table') or not pool:
            continue
        game=re.search(r'Pok(?:&eacute;|é)mon (Brilliant Diamond|Shining Pearl)',value)
        if not game:
            continue
        ids=re.findall(r'<img\b[^>]*src="/swordshield/pokemon/small/(\d+)(?:-[^"]*)?\.png"[^>]*class="wildsprite"',value)
        names=re.findall(r'<td\b[^>]*class="name"[^>]*>(.*?)</td>',value,re.S)
        if not ids:
            continue
        assert len(ids)==len(names),(pool,section,len(ids),len(names))
        times=([pool.rsplit(' - ',1)[1].lower()] if pool.startswith('Random Encounter - ') else
               ['morning','day','night'] if pool=='Random Encounter' else [])
        for sid,name in zip(ids,names):
            found.append({'species':int(sid),'name':plain(name),'game':'Pokémon '+game[1],
                          'section':section,'pool':pool,'times':times})
    assert found,'No recognized BDSP encounter rows'
    return found

rows=[];sources=[];failures=[]
for location in sorted({slot['location'] for grouped in routes().values() for slot in grouped.values()}):
    slug=SPECIAL.get(location,re.sub(r'[^a-z0-9]','',location.lower()))
    url='https://www.serebii.net/pokearth/sinnoh/'+slug+'.shtml'
    cached=CACHE/(slug+'.html')
    try:
        if not cached.exists():
            request=urllib.request.Request(url,headers={'User-Agent':'ShinyDex encounter audit'})
            cached.write_bytes(urllib.request.urlopen(request,timeout=30).read())
        raw=cached.read_bytes();decoded=decode_page(raw)
        title=plain(re.search(r'<h1\b[^>]*>(.*?)</h1>',decoded,re.S|re.I)[1])
        assert re.sub(r'[^a-z]','',title.lower().replace('mt.','mount'))==re.sub(r'[^a-z]','',location.lower()),(title,location)
        parsed=parse(decoded)
        rows.extend({**row,'location':location,'source':url} for row in parsed)
        sources.append({'location':location,'source':url,'sha256':hashlib.sha256(raw).hexdigest(),'parsedRows':len(parsed)})
        print('Parsed '+location+': '+str(len(parsed))+' rows',flush=True)
    except Exception as error:
        failures.append({'location':location,'source':url,'error':str(error)})
        print('Needs source review: '+location+': '+str(error),flush=True)
section_map={357:'South',358:'North',359:'South',361:'North',373:'South',375:'North',
             377:'West',378:'East',379:'North',383:'South',259:'Main Area',297:'Main Area'}
section_review=json.loads((ROOT/'bdsp-section-review.json').read_text(encoding='utf-8'))
section_map.update({row['locationId']:row['publishedSection'] for row in section_review['sections']})
unmapped=set()
time_candidates=[];unmatched=[]
for (species,game),locations in routes().items():
    for location,slot in locations.items():
        if location in unmapped:
            continue
        candidates=[row for row in rows if row['location']==slot['location']
                    and row['game']==game and row['species']==species
                    and row['section']==('Daily Pokemon' if location==297 and species in GARDEN_INTRODUCTIONS else section_map.get(location,
                        'Main Area' if slot['location'] in ('Fuego Ironworks','Lake Acuity','Lake Valor',
                                                          'Route 206','Valley Windworks') else 'main'))]
        times=sorted({time for row in candidates for time in row['times']})
        pools=sorted({row['pool'] for row in candidates})
        item={'species':species,'game':game,'locationId':location,'location':slot['location'],
              'requiresGardenIntroduction':location==297 and species in GARDEN_INTRODUCTIONS,
              'times':times,'pools':pools,'source':candidates[0]['source'] if candidates else None}
        if not candidates:
            unmatched.append(item)
        elif times and len(times)<3:
            time_candidates.append(item)
reviews=json.loads((ROOT/'bdsp-time-review.json').read_text(encoding='utf-8'))['conditions']
reviewed={(row['species'],game,row['locationId']):set(row['times']) for row in reviews for game in row['games']}
unreviewed=[]
for row in time_candidates:
    key=(row['species'],row['game'],row['locationId'])
    if key in reviewed:
        assert reviewed[key]==set(row['times']),('Review/source disagreement',key)
    else:
        unreviewed.append(row)
report={'fullCoverageVerified':False,'purpose':'Independent time and section inventory, cross-checked against explicit manual time reviews.',
        'limitations':['Parser inventories published encounter tables; it does not prove source accuracy, map-tile eligibility, story access, or Radar replacement behavior.',
                       'An unsuffixed random-encounter heading is inventoried as all three periods; independently verify unusual source headings before promotion.'],
        'sources':sources,'failures':failures,'unmappedLocationIds':sorted(unmapped),
        'timeRestrictedCandidates':time_candidates,'unreviewedTimeCandidates':unreviewed,
        'reviewedTimeRestrictedCombinations':len(time_candidates)-len(unreviewed),
        'unmatchedGuideLocations':unmatched,'rows':rows}
(ROOT/'bdsp-independent-tables.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'{len(sources)} pages parsed; {len(failures)} sources need review; no parsed rows automatically promoted.')
print(f'{len(time_candidates)} time-restricted candidates; {len(unreviewed)} still unreviewed; {len(unmatched)} unmatched guide-location rows; {len(unmapped)} unmapped section IDs.')
