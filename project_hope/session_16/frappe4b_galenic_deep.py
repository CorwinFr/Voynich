"""
SESSION 16 — FRAPPE 4b: Deep galenic analysis

The pharmacist MUST have encoded hot/cold/dry/wet somewhere.
4 gallows (p,t,k,f) = 4 qualities (calidus, frigidus, siccus, humidus)?

Tests:
1. INITIAL GALLOWS — which gallows starts each herbal folio?
2. GALLOWS COUNT — does the NUMBER of each gallows encode the degree?
3. QUALITY WORD — is there a specific root at the start encoding quality?
4. Use standard medieval classifications (not just Macer's sparse data)
"""
import json, sys, io, os, re
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.dirname(__file__)
VMS_PATH = os.path.join(BASE, '..', 'vms', 'vms_structured.json')
MACER_PATH = os.path.join(BASE, '..', 'session_14', 'macer_complete.json')
RESULTS = BASE

with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)
with open(MACER_PATH, encoding='utf-8') as f:
    macer = json.load(f)

GALLOWS = {'p', 't', 'k', 'f'}

# ================================================================
# STANDARD MEDIEVAL GALENIC QUALITIES
# (from Dioscorides, Galen, standard medieval classifications)
# Degree 1-4, primary quality
# ================================================================
STANDARD_QUALITIES = {
    # From Macer + standard medieval sources
    'artemisia':    {'hot': 2, 'dry': 1},
    'abrotanum':    {'hot': 3, 'dry': 2},
    'absinthium':   {'hot': 1, 'dry': 2},
    'urtica':       {'hot': 3, 'dry': 1},
    'allium':       {'hot': 4, 'dry': 3},
    'plantago':     {'cold': 2, 'wet': 1},
    'ruta':         {'hot': 3, 'dry': 2},
    'apium':        {'hot': 2, 'dry': 1},
    'althaea':      {'hot': 1, 'wet': 2},
    'anethum':      {'hot': 2, 'dry': 1},
    'betonica':     {'hot': 2, 'dry': 1},
    'sabina':       {'hot': 3, 'dry': 3},
    'chamomilla':   {'hot': 1, 'dry': 2},
    'nepeta':       {'hot': 3, 'dry': 2},
    'pulegium':     {'hot': 3, 'dry': 2},
    'feniculum':    {'hot': 2, 'dry': 1},
    'portulaca':    {'cold': 3, 'wet': 2},
    'lactuca':      {'cold': 2, 'wet': 2},
    'rosa':         {'cold': 1, 'dry': 2},
    'lilium':       {'hot': 1, 'wet': 1},
    'satureia':     {'hot': 3, 'dry': 2},
    'salvia':       {'hot': 2, 'dry': 1},
    'origanum':     {'hot': 3, 'dry': 2},
    'mentha':       {'hot': 2, 'dry': 1},
    'coriandrum':   {'cold': 2, 'dry': 1},
    'eruca':        {'hot': 3, 'dry': 1},
    'papaver':      {'cold': 3, 'wet': 1},
    'viola':        {'cold': 1, 'wet': 1},
    'aristolochia': {'hot': 2, 'dry': 3},
    'verbena':      {'cold': 1, 'dry': 2},
    'malva':        {'cold': 1, 'wet': 2},
    'atriplex':     {'cold': 2, 'wet': 2},
    'centaurea':    {'hot': 1, 'dry': 1},
    'elleborus':    {'hot': 3, 'dry': 3},
    'rosmarinus':   {'hot': 2, 'dry': 1},
    'cannabis':     {'cold': 2, 'dry': 1},
    'crocus':       {'hot': 2, 'dry': 1},
    'mandragora':   {'cold': 3, 'wet': 1},
    'gentiana':     {'hot': 2, 'dry': 1},
    'nigella':      {'hot': 3, 'dry': 1},
}

# ================================================================
# ALL SHERWOOD ANCHORS (expanded beyond Macer-matched)
# ================================================================
ALL_SHERWOOD = {
    'f48v':'ruta','f9v':'viola','f44v':'apium','f51v':'salvia',
    'f29r':'lactuca','f41r':'origanum','f37r':'mentha',
    'f41v':'coriandrum','f22r':'verbena','f28r':'aristolochia',
    'f5v':'malva','f45r':'atriplex','f66v':'satureia',
    'f65v':'centaurea','f3v':'elleborus','f95v1':'althaea',
    'f11r':'rosmarinus','f16r':'cannabis','f39r':'crocus',
    'f44r':'mandragora','f50v':'gentiana','f29v':'nigella',
}

# ================================================================
# TEST 1: INITIAL GALLOWS per folio
# ================================================================
print('='*70)
print('TEST 1 — INITIAL GALLOWS = QUALITY?')
print('='*70)

def get_initial_gallows(fid):
    """Get the first gallows in a folio (first word starting with p/t/k/f)."""
    folio = vms['folios'].get(fid)
    if not folio:
        return None, None
    for block in folio['blocks']:
        for line in block['lines']:
            for w in line['words']:
                eva = w['eva_primary']
                # Check if word starts with a gallows
                for g in ['f', 'k', 'p', 't']:
                    if eva.startswith(g) and len(eva) > 1:
                        return g, eva
                # Also check single-char gallows
                if eva in GALLOWS:
                    return eva, eva
    return None, None

def get_primary_quality(plant):
    """Get the primary quality of a plant."""
    quals = STANDARD_QUALITIES.get(plant, {})
    if not quals:
        return None, None
    # Primary = highest degree
    best_qual = max(quals.items(), key=lambda x: x[1])
    return best_qual[0], best_qual[1]

print(f'\n  {"Folio":>8s} {"Plant":>15s} {"InitGall":>9s} {"Word":>15s} '
      f'{"Quality":>8s} {"Deg":>4s}')
print('  ' + '-' * 70)

gallows_quality_pairs = []

for fid, plant in sorted(ALL_SHERWOOD.items()):
    if fid not in vms['folios']:
        continue

    gall, gall_word = get_initial_gallows(fid)
    qual, degree = get_primary_quality(plant)

    if gall and qual:
        gallows_quality_pairs.append((gall, qual, degree, fid, plant))

    marker = ''
    if gall and qual:
        marker = f'  {gall}→{qual}'

    print(f'  {fid:>8s} {plant:>15s} {str(gall):>9s} {str(gall_word):>15s} '
          f'{str(qual):>8s} {str(degree):>4s}{marker}')

# ================================================================
# Analyze gallows→quality mapping
# ================================================================
print(f'\n\n  GALLOWS → QUALITY CONTINGENCY TABLE:')
print(f'  (Does each gallows map to a specific quality?)\n')

gallows_to_qual = defaultdict(Counter)
qual_to_gallows = defaultdict(Counter)

for gall, qual, deg, fid, plant in gallows_quality_pairs:
    gallows_to_qual[gall][qual] += 1
    qual_to_gallows[qual][gall] += 1

# Print contingency table
quals_list = ['hot', 'cold', 'dry', 'wet']
galls_list = ['p', 't', 'k', 'f']

print(f'  {"":>5s}', end='')
for q in quals_list:
    print(f' {q:>6s}', end='')
print(f' {"Total":>6s}')
print('  ' + '-' * 35)

for g in galls_list:
    print(f'  {g:>5s}', end='')
    row_total = 0
    for q in quals_list:
        count = gallows_to_qual[g][q]
        row_total += count
        print(f' {count:>6d}', end='')
    print(f' {row_total:>6d}')

print('  ' + '-' * 35)
print(f'  {"Total":>5s}', end='')
for q in quals_list:
    total = sum(gallows_to_qual[g][q] for g in galls_list)
    print(f' {total:>6d}', end='')
print()

# ================================================================
# TEST 2: ALL GALLOWS COUNTS per folio vs quality
# ================================================================
print(f'\n\n{"="*70}')
print('TEST 2 — GALLOWS COUNTS vs QUALITY')
print('='*70)

def get_gallows_counts(fid):
    """Count each gallows type in a folio."""
    folio = vms['folios'].get(fid)
    if not folio:
        return Counter()
    counts = Counter()
    for block in folio['blocks']:
        for line in block['lines']:
            for w in line['words']:
                eva = w['eva_primary']
                for g in GALLOWS:
                    if g in eva:
                        counts[g] += eva.count(g)
    return counts

print(f'\n  {"Folio":>8s} {"Plant":>15s} {"Qual":>5s} {"Deg":>4s} '
      f'{"p":>4s} {"t":>4s} {"k":>4s} {"f":>4s} {"Dominant":>9s}')
print('  ' + '-' * 65)

hot_dominant = Counter()
cold_dominant = Counter()

for fid, plant in sorted(ALL_SHERWOOD.items()):
    if fid not in vms['folios']:
        continue

    gc = get_gallows_counts(fid)
    qual, degree = get_primary_quality(plant)

    # Which gallows is dominant?
    if gc:
        dominant = gc.most_common(1)[0][0]
    else:
        dominant = '?'

    if qual in ('hot', 'dry'):
        hot_dominant[dominant] += 1
    elif qual in ('cold', 'wet'):
        cold_dominant[dominant] += 1

    print(f'  {fid:>8s} {plant:>15s} {str(qual):>5s} {str(degree):>4s} '
          f'{gc.get("p",0):>4d} {gc.get("t",0):>4d} '
          f'{gc.get("k",0):>4d} {gc.get("f",0):>4d} {dominant:>9s}')

print(f'\n  HOT/DRY plants → dominant gallows: {dict(hot_dominant)}')
print(f'  COLD/WET plants → dominant gallows: {dict(cold_dominant)}')


# ================================================================
# TEST 3: FIRST WORD pattern per quality group
# ================================================================
print(f'\n\n{"="*70}')
print('TEST 3 — FIRST WORD BY QUALITY GROUP')
print('='*70)

hot_first_words = []
cold_first_words = []

for fid, plant in sorted(ALL_SHERWOOD.items()):
    if fid not in vms['folios']:
        continue
    qual, _ = get_primary_quality(plant)
    if not qual:
        continue

    folio = vms['folios'][fid]
    first_word = None
    for block in folio['blocks']:
        for line in block['lines']:
            if line['words']:
                first_word = line['words'][0]['eva_primary']
                break
        if first_word:
            break

    if first_word:
        if qual in ('hot', 'dry'):
            hot_first_words.append((fid, plant, first_word, qual))
        else:
            cold_first_words.append((fid, plant, first_word, qual))

print(f'\n  HOT/DRY first words:')
for fid, plant, fw, qual in hot_first_words:
    # Get first character
    first_char = fw[0] if fw else '?'
    print(f'    {fid:>8s} {plant:>15s} [{qual:>4s}]  "{fw}"  starts={first_char}')

print(f'\n  COLD/WET first words:')
for fid, plant, fw, qual in cold_first_words:
    first_char = fw[0] if fw else '?'
    print(f'    {fid:>8s} {plant:>15s} [{qual:>4s}]  "{fw}"  starts={first_char}')

# Count initial characters
hot_starts = Counter(fw[0] for _, _, fw, _ in hot_first_words if fw)
cold_starts = Counter(fw[0] for _, _, fw, _ in cold_first_words if fw)
print(f'\n  HOT/DRY start with: {dict(hot_starts)}')
print(f'  COLD/WET start with: {dict(cold_starts)}')


# ================================================================
# TEST 4: SECOND LINE / SECOND WORD pattern
# ================================================================
print(f'\n\n{"="*70}')
print('TEST 4 — LINES 2-3 PATTERN (quality declaration?)')
print('='*70)

# In Macer, the quality is usually stated in the first few lines:
# "In primo calor esse gradu" (1st degree hot)
# Maybe the VMS has a similar pattern in lines 2-3?

for fid, plant in sorted(ALL_SHERWOOD.items()):
    if fid not in vms['folios']:
        continue
    qual, degree = get_primary_quality(plant)
    if not qual:
        continue

    folio = vms['folios'][fid]
    lines = []
    for block in folio['blocks']:
        for line in block['lines']:
            words = [w['eva_primary'] for w in line['words']]
            lines.append(' '.join(words))
            if len(lines) >= 3:
                break
        if len(lines) >= 3:
            break

    # Show first 3 lines
    qual_str = f'{qual}({degree})' if degree else qual
    print(f'\n  {fid} = {plant} [{qual_str}]:')
    for i, line in enumerate(lines[:3]):
        print(f'    L{i+1}: {line[:70]}')


# ================================================================
# TEST 5: GALLOWS RATIO (refined — initial position only)
# ================================================================
print(f'\n\n{"="*70}')
print('TEST 5 — INITIAL-POSITION GALLOWS ONLY')
print('='*70)

# Count only gallows that are block-initial (first word of a line)
def get_initial_gallows_counts(fid):
    folio = vms['folios'].get(fid)
    if not folio:
        return Counter()
    counts = Counter()
    for block in folio['blocks']:
        for line in block['lines']:
            if line['words']:
                first_eva = line['words'][0]['eva_primary']
                for g in GALLOWS:
                    if first_eva.startswith(g):
                        counts[g] += 1
                        break
    return counts

print(f'\n  {"Folio":>8s} {"Plant":>15s} {"Qual":>5s} '
      f'{"p0":>4s} {"t0":>4s} {"k0":>4s} {"f0":>4s} {"Dom0":>5s}')
print('  ' + '-' * 55)

hot_init = Counter()
cold_init = Counter()

for fid, plant in sorted(ALL_SHERWOOD.items()):
    if fid not in vms['folios']:
        continue

    igc = get_initial_gallows_counts(fid)
    qual, degree = get_primary_quality(plant)

    dominant = igc.most_common(1)[0][0] if igc else '?'

    if qual in ('hot', 'dry'):
        hot_init[dominant] += 1
    elif qual in ('cold', 'wet'):
        cold_init[dominant] += 1

    print(f'  {fid:>8s} {plant:>15s} {str(qual):>5s} '
          f'{igc.get("p",0):>4d} {igc.get("t",0):>4d} '
          f'{igc.get("k",0):>4d} {igc.get("f",0):>4d} {dominant:>5s}')

print(f'\n  HOT/DRY → initial gallows: {dict(hot_init)}')
print(f'  COLD/WET → initial gallows: {dict(cold_init)}')

# ================================================================
# FINAL VERDICT
# ================================================================
print(f'\n\n{"="*70}')
print('FINAL VERDICT — WHERE ARE GALENIC QUALITIES ENCODED?')
print('='*70)

# Check if any gallows consistently maps to hot or cold
all_gq = defaultdict(lambda: defaultdict(int))
for gall, qual, deg, fid, plant in gallows_quality_pairs:
    hc = 'HOT' if qual in ('hot', 'dry') else 'COLD'
    all_gq[gall][hc] += 1

for g in galls_list:
    hot_n = all_gq[g].get('HOT', 0)
    cold_n = all_gq[g].get('COLD', 0)
    total = hot_n + cold_n
    if total > 0:
        hot_pct = hot_n * 100 // total
        print(f'  Gallows {g}: HOT={hot_n} ({hot_pct}%)  COLD={cold_n} ({100-hot_pct}%)')

# Save results
output = {
    'gallows_quality_pairs': [(g, q, d, f, p) for g, q, d, f, p in gallows_quality_pairs],
    'contingency': {g: dict(gallows_to_qual[g]) for g in galls_list},
    'hot_dominant': dict(hot_dominant),
    'cold_dominant': dict(cold_dominant),
    'hot_initial': dict(hot_init),
    'cold_initial': dict(cold_init),
}

with open(os.path.join(RESULTS, 'frappe4b_results.json'), 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f'\nSaved frappe4b_results.json')
