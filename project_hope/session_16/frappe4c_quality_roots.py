"""
SESSION 16 — FRAPPE 4c: Find the quality-encoding root

If the pharmacist encoded hot/cold, there must be a root (or set of roots)
that DIFFERENTIATES hot-plant folios from cold-plant folios.

Method:
1. Split anchor folios into HOT vs COLD groups (using standard medieval qualities)
2. For each root, compute Fisher enrichment: is it significantly more present
   in one group?
3. Look especially at lines 1-3 (where Macer states the quality)
4. Also check: could it be a SUFFIX pattern, not a root?
"""
import json, sys, io, os
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.dirname(__file__)
VMS_PATH = os.path.join(BASE, '..', 'vms', 'vms_structured.json')
RESULTS = BASE

with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)

LOGOS = {'o','l','d','r','v','x','k','m','f','t','y','c','s','sh','p','ch','air','h'}

STANDARD_QUALITIES = {
    'artemisia': 'hot', 'abrotanum': 'hot', 'absinthium': 'hot',
    'urtica': 'hot', 'allium': 'hot', 'plantago': 'cold',
    'ruta': 'hot', 'apium': 'hot', 'althaea': 'wet',
    'anethum': 'hot', 'betonica': 'hot', 'sabina': 'hot',
    'chamomilla': 'hot', 'nepeta': 'hot', 'pulegium': 'hot',
    'feniculum': 'hot', 'portulaca': 'cold', 'lactuca': 'cold',
    'rosa': 'cold', 'lilium': 'hot', 'satureia': 'hot',
    'salvia': 'hot', 'origanum': 'hot', 'mentha': 'hot',
    'coriandrum': 'cold', 'eruca': 'hot', 'papaver': 'cold',
    'viola': 'cold', 'aristolochia': 'hot', 'verbena': 'cold',
    'malva': 'cold', 'atriplex': 'cold', 'centaurea': 'hot',
    'elleborus': 'hot', 'rosmarinus': 'hot', 'cannabis': 'cold',
    'crocus': 'hot', 'mandragora': 'cold', 'gentiana': 'hot',
    'nigella': 'hot',
}

ALL_SHERWOOD = {
    'f48v':'ruta','f9v':'viola','f44v':'apium','f51v':'salvia',
    'f29r':'lactuca','f41r':'origanum','f37r':'mentha',
    'f41v':'coriandrum','f22r':'verbena','f28r':'aristolochia',
    'f5v':'malva','f45r':'atriplex','f66v':'satureia',
    'f65v':'centaurea','f3v':'elleborus','f95v1':'althaea',
    'f11r':'rosmarinus','f16r':'cannabis','f39r':'crocus',
    'f44r':'mandragora','f50v':'gentiana','f29v':'nigella',
}

# Split into hot (hot/dry) vs cold (cold/wet)
hot_folios = []
cold_folios = []
for fid, plant in ALL_SHERWOOD.items():
    if fid not in vms['folios']:
        continue
    qual = STANDARD_QUALITIES.get(plant)
    if qual in ('hot', 'dry'):
        hot_folios.append(fid)
    elif qual in ('cold', 'wet'):
        cold_folios.append(fid)

print(f'HOT/DRY folios: {len(hot_folios)}')
print(f'COLD/WET folios: {len(cold_folios)}')

# ================================================================
# TEST A: Root enrichment across ENTIRE folio
# ================================================================
print(f'\n{"="*70}')
print('TEST A — ROOT ENRICHMENT (entire folio)')
print('='*70)

def get_roots(fid):
    roots = Counter()
    for block in vms['folios'][fid]['blocks']:
        for line in block['lines']:
            for w in line['words']:
                eva = w['eva_primary']
                if eva in LOGOS or len(eva) < 2:
                    continue
                root = (w.get('morphology') or {}).get('root', eva)
                if root and len(root) >= 2:
                    roots[root] += 1
    return roots

# Collect roots per group
hot_roots = Counter()     # root → count in hot folios
cold_roots = Counter()
hot_presence = defaultdict(int)   # root → number of hot folios containing it
cold_presence = defaultdict(int)

for fid in hot_folios:
    roots = get_roots(fid)
    for root, count in roots.items():
        hot_roots[root] += count
        hot_presence[root] += 1

for fid in cold_folios:
    roots = get_roots(fid)
    for root, count in roots.items():
        cold_roots[root] += count
        cold_presence[root] += 1

# Find enriched roots
all_roots_set = set(hot_roots.keys()) | set(cold_roots.keys())

enriched = []
for root in all_roots_set:
    hp = hot_presence.get(root, 0)
    cp = cold_presence.get(root, 0)
    hn = len(hot_folios)
    cn = len(cold_folios)

    # Enrichment ratio
    hot_rate = hp / max(hn, 1)
    cold_rate = cp / max(cn, 1)

    # Only consider roots present in 3+ folios total
    if (hp + cp) < 3:
        continue

    if hot_rate > 0 and cold_rate > 0:
        ratio = hot_rate / cold_rate
    elif hot_rate > 0:
        ratio = 99.0  # only in hot
    elif cold_rate > 0:
        ratio = 0.01  # only in cold
    else:
        continue

    enriched.append({
        'root': root,
        'hot_present': hp,
        'cold_present': cp,
        'hot_rate': hot_rate,
        'cold_rate': cold_rate,
        'ratio': ratio,
        'hot_count': hot_roots.get(root, 0),
        'cold_count': cold_roots.get(root, 0),
    })

# Sort by most enriched in hot
enriched.sort(key=lambda x: -x['ratio'])

print(f'\n  TOP 15 HOT-ENRICHED roots:')
print(f'  {"Root":>12s} {"Hot":>4s}/{hn:d}  {"Cold":>4s}/{cn:d}  {"Ratio":>6s} {"HotCnt":>7s} {"ColdCnt":>7s}')
print('  ' + '-' * 55)
for e in enriched[:15]:
    print(f'  {e["root"]:>12s} {e["hot_present"]:>4d}   {e["cold_present"]:>4d}   '
          f'{e["ratio"]:>6.1f} {e["hot_count"]:>7d} {e["cold_count"]:>7d}')

print(f'\n  TOP 15 COLD-ENRICHED roots:')
enriched.sort(key=lambda x: x['ratio'])
for e in enriched[:15]:
    print(f'  {e["root"]:>12s} {e["hot_present"]:>4d}   {e["cold_present"]:>4d}   '
          f'{e["ratio"]:>6.1f} {e["hot_count"]:>7d} {e["cold_count"]:>7d}')


# ================================================================
# TEST B: Root enrichment in FIRST 3 LINES only
# ================================================================
print(f'\n\n{"="*70}')
print('TEST B — ROOT ENRICHMENT (first 3 lines only)')
print('='*70)

def get_roots_first_n_lines(fid, n=3):
    roots = Counter()
    line_count = 0
    for block in vms['folios'][fid]['blocks']:
        for line in block['lines']:
            line_count += 1
            if line_count > n:
                return roots
            for w in line['words']:
                eva = w['eva_primary']
                if eva in LOGOS or len(eva) < 2:
                    continue
                root = (w.get('morphology') or {}).get('root', eva)
                if root and len(root) >= 2:
                    roots[root] += 1
    return roots

hot_roots3 = Counter()
cold_roots3 = Counter()
hot_pres3 = defaultdict(int)
cold_pres3 = defaultdict(int)

for fid in hot_folios:
    roots = get_roots_first_n_lines(fid, 3)
    for root, count in roots.items():
        hot_roots3[root] += count
        hot_pres3[root] += 1

for fid in cold_folios:
    roots = get_roots_first_n_lines(fid, 3)
    for root, count in roots.items():
        cold_roots3[root] += count
        cold_pres3[root] += 1

enriched3 = []
for root in set(hot_roots3.keys()) | set(cold_roots3.keys()):
    hp = hot_pres3.get(root, 0)
    cp = cold_pres3.get(root, 0)
    if (hp + cp) < 3:
        continue

    hot_rate = hp / max(len(hot_folios), 1)
    cold_rate = cp / max(len(cold_folios), 1)

    if hot_rate > 0 and cold_rate > 0:
        ratio = hot_rate / cold_rate
    elif hot_rate > 0:
        ratio = 99.0
    elif cold_rate > 0:
        ratio = 0.01
    else:
        continue

    enriched3.append({
        'root': root,
        'hot_present': hp,
        'cold_present': cp,
        'ratio': ratio,
    })

enriched3.sort(key=lambda x: -x['ratio'])

print(f'\n  HOT-ENRICHED in first 3 lines:')
print(f'  {"Root":>12s} {"Hot":>4s}/{len(hot_folios)}  {"Cold":>4s}/{len(cold_folios)}  {"Ratio":>6s}')
print('  ' + '-' * 40)
for e in enriched3[:10]:
    print(f'  {e["root"]:>12s} {e["hot_present"]:>4d}   {e["cold_present"]:>4d}   {e["ratio"]:>6.1f}')

enriched3.sort(key=lambda x: x['ratio'])
print(f'\n  COLD-ENRICHED in first 3 lines:')
for e in enriched3[:10]:
    print(f'  {e["root"]:>12s} {e["hot_present"]:>4d}   {e["cold_present"]:>4d}   {e["ratio"]:>6.1f}')


# ================================================================
# TEST C: SUFFIX patterns (hot vs cold)
# ================================================================
print(f'\n\n{"="*70}')
print('TEST C — SUFFIX ENRICHMENT')
print('='*70)

def get_suffixes(fid):
    suffixes = Counter()
    for block in vms['folios'][fid]['blocks']:
        for line in block['lines']:
            for w in line['words']:
                sfx = (w.get('morphology') or {}).get('suffix', '')
                if sfx and len(sfx) >= 2:
                    suffixes[sfx] += 1
    return suffixes

hot_sfx = Counter()
cold_sfx = Counter()
hot_sfx_pres = defaultdict(int)
cold_sfx_pres = defaultdict(int)

for fid in hot_folios:
    sfx = get_suffixes(fid)
    for s, c in sfx.items():
        hot_sfx[s] += c
        hot_sfx_pres[s] += 1

for fid in cold_folios:
    sfx = get_suffixes(fid)
    for s, c in sfx.items():
        cold_sfx[s] += c
        cold_sfx_pres[s] += 1

sfx_enriched = []
for sfx in set(hot_sfx.keys()) | set(cold_sfx.keys()):
    hp = hot_sfx_pres.get(sfx, 0)
    cp = cold_sfx_pres.get(sfx, 0)
    if (hp + cp) < 3:
        continue

    hot_rate = hp / max(len(hot_folios), 1)
    cold_rate = cp / max(len(cold_folios), 1)

    if hot_rate > 0 and cold_rate > 0:
        ratio = hot_rate / cold_rate
    elif hot_rate > 0:
        ratio = 99.0
    elif cold_rate > 0:
        ratio = 0.01
    else:
        continue

    sfx_enriched.append({
        'suffix': sfx,
        'hot_present': hp,
        'cold_present': cp,
        'ratio': ratio,
        'hot_count': hot_sfx.get(sfx, 0),
        'cold_count': cold_sfx.get(sfx, 0),
    })

sfx_enriched.sort(key=lambda x: -x['ratio'])
print(f'\n  HOT-ENRICHED suffixes:')
print(f'  {"Suffix":>12s} {"Hot":>4s}/{len(hot_folios)}  {"Cold":>4s}/{len(cold_folios)}  '
      f'{"Ratio":>6s} {"HotCnt":>7s} {"ColdCnt":>7s}')
print('  ' + '-' * 55)
for e in sfx_enriched[:10]:
    print(f'  {e["suffix"]:>12s} {e["hot_present"]:>4d}   {e["cold_present"]:>4d}   '
          f'{e["ratio"]:>6.1f} {e["hot_count"]:>7d} {e["cold_count"]:>7d}')

sfx_enriched.sort(key=lambda x: x['ratio'])
print(f'\n  COLD-ENRICHED suffixes:')
for e in sfx_enriched[:10]:
    print(f'  {e["suffix"]:>12s} {e["hot_present"]:>4d}   {e["cold_present"]:>4d}   '
          f'{e["ratio"]:>6.1f} {e["hot_count"]:>7d} {e["cold_count"]:>7d}')


# ================================================================
# TEST D: WORD-LEVEL patterns (specific EVA words)
# ================================================================
print(f'\n\n{"="*70}')
print('TEST D — SPECIFIC EVA WORDS in lines 1-3')
print('='*70)

hot_words3 = Counter()
cold_words3 = Counter()
hot_wpres3 = defaultdict(int)
cold_wpres3 = defaultdict(int)

for fid in hot_folios:
    line_count = 0
    seen = set()
    for block in vms['folios'][fid]['blocks']:
        for line in block['lines']:
            line_count += 1
            if line_count > 3:
                break
            for w in line['words']:
                eva = w['eva_primary']
                if len(eva) >= 3:
                    hot_words3[eva] += 1
                    if eva not in seen:
                        hot_wpres3[eva] += 1
                        seen.add(eva)
        if line_count > 3:
            break

for fid in cold_folios:
    line_count = 0
    seen = set()
    for block in vms['folios'][fid]['blocks']:
        for line in block['lines']:
            line_count += 1
            if line_count > 3:
                break
            for w in line['words']:
                eva = w['eva_primary']
                if len(eva) >= 3:
                    cold_words3[eva] += 1
                    if eva not in seen:
                        cold_wpres3[eva] += 1
                        seen.add(eva)
        if line_count > 3:
            break

# Find words only in hot or mostly in hot
hot_only = []
for word in set(hot_wpres3.keys()) | set(cold_wpres3.keys()):
    hp = hot_wpres3.get(word, 0)
    cp = cold_wpres3.get(word, 0)
    if (hp + cp) < 3:
        continue
    hot_rate = hp / max(len(hot_folios), 1)
    cold_rate = cp / max(len(cold_folios), 1)
    if cold_rate > 0:
        ratio = hot_rate / cold_rate
    elif hot_rate > 0:
        ratio = 99.0
    else:
        continue

    hot_only.append({
        'word': word,
        'hot': hp,
        'cold': cp,
        'ratio': ratio,
    })

hot_only.sort(key=lambda x: -x['ratio'])
print(f'\n  Words in lines 1-3 enriched in HOT:')
for e in hot_only[:10]:
    print(f'    {e["word"]:>15s}  hot={e["hot"]:d}/{len(hot_folios)}  cold={e["cold"]:d}/{len(cold_folios)}  ratio={e["ratio"]:.1f}')

hot_only.sort(key=lambda x: x['ratio'])
print(f'\n  Words in lines 1-3 enriched in COLD:')
for e in hot_only[:10]:
    print(f'    {e["word"]:>15s}  hot={e["hot"]:d}/{len(hot_folios)}  cold={e["cold"]:d}/{len(cold_folios)}  ratio={e["ratio"]:.1f}')


# ================================================================
# TEST E: SECOND WORD ONLY (position after plant name)
# ================================================================
print(f'\n\n{"="*70}')
print('TEST E — SECOND WORD (right after plant name)')
print('='*70)

# In Macer, quality appears right after the plant name
# Maybe the SECOND word of each VMS folio encodes the quality?

hot_second = Counter()
cold_second = Counter()

for fid in hot_folios:
    words_so_far = 0
    for block in vms['folios'][fid]['blocks']:
        for line in block['lines']:
            for w in line['words']:
                words_so_far += 1
                if words_so_far == 2:
                    eva = w['eva_primary']
                    root = (w.get('morphology') or {}).get('root', eva)
                    hot_second[root] += 1
                    break
            if words_so_far >= 2:
                break
        if words_so_far >= 2:
            break

for fid in cold_folios:
    words_so_far = 0
    for block in vms['folios'][fid]['blocks']:
        for line in block['lines']:
            for w in line['words']:
                words_so_far += 1
                if words_so_far == 2:
                    eva = w['eva_primary']
                    root = (w.get('morphology') or {}).get('root', eva)
                    cold_second[root] += 1
                    break
            if words_so_far >= 2:
                break
        if words_so_far >= 2:
            break

print(f'\n  HOT second-word roots: {dict(hot_second.most_common(10))}')
print(f'  COLD second-word roots: {dict(cold_second.most_common(10))}')

# Check overlap
all_seconds = set(hot_second.keys()) | set(cold_second.keys())
print(f'\n  {"SecondRoot":>12s} {"Hot":>4s} {"Cold":>5s}')
print('  ' + '-' * 25)
for root in sorted(all_seconds, key=lambda r: hot_second.get(r,0)+cold_second.get(r,0), reverse=True)[:15]:
    h = hot_second.get(root, 0)
    c = cold_second.get(root, 0)
    marker = ''
    if h > 0 and c == 0:
        marker = ' ← HOT only'
    elif c > 0 and h == 0:
        marker = ' ← COLD only'
    print(f'  {root:>12s} {h:>4d} {c:>5d}{marker}')

# Save
output = {
    'n_hot': len(hot_folios),
    'n_cold': len(cold_folios),
    'hot_enriched_roots_top5': [{'root': e['root'], 'ratio': e['ratio'],
                                  'hot': e['hot_present'], 'cold': e['cold_present']}
                                 for e in sorted(enriched, key=lambda x: -x['ratio'])[:5]],
    'cold_enriched_roots_top5': [{'root': e['root'], 'ratio': e['ratio'],
                                   'hot': e['hot_present'], 'cold': e['cold_present']}
                                  for e in sorted(enriched, key=lambda x: x['ratio'])[:5]],
}

with open(os.path.join(RESULTS, 'frappe4c_results.json'), 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f'\nSaved frappe4c_results.json')
