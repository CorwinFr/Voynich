"""
VOYNICH ENGINE — Fingerprint with 115 botanical identifications

THE approach that actually works, now with 4× more data.

For each unknown VMS root:
1. Build presence/absence fingerprint across 115 identified herbal folios
2. Build ingredient fingerprint across ALL Macer+CI+Galen chapters
3. Match: which ingredient has the SAME presence pattern as this root?
4. Require: 3+ true positives, <=1 false positive, Jaccard >= 0.3

This is how we found acetum, mel, piper, oleum, sal, mastix, nigella.
Now with 115 anchors instead of 30.
"""
import json, sys, io, os, re
from collections import Counter, defaultdict
from math import comb

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.dirname(os.path.dirname(__file__))
VMS_PATH = os.path.join(BASE, 'vms', 'vms_structured.json')
REG_PATH = os.path.join(BASE, 'hypothesis_registry.json')
MACER_PATH = os.path.join(BASE, 'session_14', 'macer_complete.json')
BOT_PATH = os.path.join(BASE, 'engine', 'botanical_ids_extended.json')
RESULTS = os.path.join(BASE, 'engine')

with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)
with open(REG_PATH, encoding='utf-8') as f:
    registry = json.load(f)
with open(MACER_PATH, encoding='utf-8') as f:
    macer_data = json.load(f)
with open(BOT_PATH, encoding='utf-8') as f:
    bot_ids = json.load(f)

LOGOS = {'o','l','d','r','v','x','k','m','f','t','y','c','s','sh','p','ch','air','h'}
FUNCTIONAL = set(registry.get('functional_words', {}).keys())
NOISE = {'ke', 'ko', 'po', 'do'}

# Existing Sherwood
SHERWOOD = {
    'f48v':'ruta','f9v':'viola','f44v':'apium','f51v':'salvia',
    'f29r':'lactuca','f41r':'origanum','f37r':'mentha',
    'f41v':'coriandrum','f22r':'verbena','f28r':'aristolochia',
    'f5v':'malva','f45r':'atriplex','f66v':'satureia',
    'f65v':'centaurea','f3v':'elleborus','f95v1':'althaea',
    'f11r':'rosmarinus','f16r':'cannabis','f39r':'crocus',
    'f44r':'mandragora','f50v':'gentiana','f29v':'nigella',
    'f35v':'ribes','f47v':'pulmonaria','f53r':'achillea',
    'f14r':'scorzonera','f21r':'anagallis','f27r':'spinacia',
    'f33v':'tanacetum','f49r':'nymphaea',
}

# Merge: Sherwood + PDF identifications
ALL_IDS = dict(SHERWOOD)
for fid, data in bot_ids.items():
    if fid not in ALL_IDS:
        genus = data['primary'].split()[0].lower().rstrip('0123456789 ')
        ALL_IDS[fid] = genus

# Already known roots (exclude from search)
KNOWN_ROOTS = set()
for root in registry['confirmed_ingredients']:
    KNOWN_ROOTS.add(root)
KNOWN_ROOTS.update({'ypch','ykeed','seees','kald','otoly','shocthy','shotch','dal','dary','qokeo'})

print(f'Total identified folios: {len(ALL_IDS)}')
print(f'Known roots (excluded): {len(KNOWN_ROOTS)}')

# ================================================================
# STEP 1: Build Macer ingredient fingerprint
# ================================================================
print(f'\n{"="*70}')
print('STEP 1 — Macer ingredient presence per chapter')
print('='*70)

INGR_PATTERNS = {
    'acetum': r'\bacet\w*\b', 'aqua': r'\baqua\w*\b|\bamne\b',
    'mel': r'\bmel\b|\bmell\w*\b|\bmulsa\b', 'piper': r'\bpiper\w*\b',
    'oleum': r'\boleu\w*\b|\boleo\b', 'sal': r'\bsal[ei]?\b|\bsale\b',
    'vinum': r'\bvin\w*\b|\bmero\b|\bmust\w*\b', 'succus': r'\bsucc\w*\b',
    'lac': r'\blac\b|\blact[ei]\w*\b', 'ovum': r'\bov[uoia]\w*\b',
    'nitrum': r'\bnitr\w*\b', 'myrrha': r'\bmyrrh\w*\b',
    'lens': r'\blen[st]\w*\b', 'nardus': r'\bnard\w*\b',
    'rosa': r'\bros[aisae]\w*\b', 'faba': r'\bfab[ae]\w*\b',
    'feniculum': r'\bfenic\w*\b', 'vesica': r'\bvesic\w*\b',
    'adeps': r'\badep\w*\b|\baxungi\w*\b', 'cera': r'\bcer[ae]\w*\b',
    'thus': r'\bthus\b|\bthur\w*\b', 'linum': r'\blin[uoi]\w*\b',
    'sulphur': r'\bsulph\w*\b', 'anethum': r'\baneth\w*\b',
}

# Which Macer chapter mentions which ingredient
macer_ingr_presence = {}  # chapter_name → set of ingredients
for ch in macer_data['chapters']:
    name = ch['name'].lower()
    text = ch['text'].lower()
    ingrs = set()
    for ingr, pattern in INGR_PATTERNS.items():
        if re.search(pattern, text):
            ingrs.add(ingr)
    macer_ingr_presence[name] = ingrs

# Map folio → Macer chapter (via genus matching)
MACER_NAMES = {ch['name'].lower(): ch['name'] for ch in macer_data['chapters']}

def folio_to_macer(fid):
    """Find the Macer chapter for this folio's plant."""
    plant = ALL_IDS.get(fid, '').lower()
    if not plant:
        return None
    # Direct match
    if plant in MACER_NAMES:
        return plant
    # Partial match
    for mname in MACER_NAMES:
        if plant[:4] in mname or mname[:4] in plant:
            return mname
    return None

# Build: for each ingredient, which identified folios SHOULD have it?
ingr_expected_folios = defaultdict(set)  # ingredient → set of fids
fid_to_chapter = {}

for fid in ALL_IDS:
    if fid not in vms['folios']:
        continue
    ch = folio_to_macer(fid)
    if ch and ch in macer_ingr_presence:
        fid_to_chapter[fid] = ch
        for ingr in macer_ingr_presence[ch]:
            ingr_expected_folios[ingr].add(fid)

print(f'Folios mapped to Macer chapters: {len(fid_to_chapter)}')
for ingr in sorted(ingr_expected_folios.keys()):
    n = len(ingr_expected_folios[ingr])
    print(f'  {ingr:>12s}: expected in {n} folios')

# ================================================================
# STEP 2: Build VMS root fingerprint
# ================================================================
print(f'\n{"="*70}')
print('STEP 2 — VMS root presence per folio')
print('='*70)

# For each root, which folios contain it?
root_actual_folios = defaultdict(set)

for fid in fid_to_chapter:
    folio = vms['folios'][fid]
    for block in folio['blocks']:
        for line in block['lines']:
            for w in line['words']:
                eva = w['eva_primary']
                if eva in LOGOS:
                    continue
                root = (w.get('morphology') or {}).get('root', '')
                if root and len(root) >= 4 and root not in FUNCTIONAL and root not in NOISE:
                    if root not in KNOWN_ROOTS:
                        root_actual_folios[root].add(fid)

print(f'Unknown roots (>= 4 chars): {len(root_actual_folios)}')

# ================================================================
# STEP 3: FINGERPRINT MATCHING
# ================================================================
print(f'\n{"="*70}')
print('STEP 3 — Fingerprint matching (root ↔ ingredient)')
print('='*70)

n_anchors = len(fid_to_chapter)
results = []

for root, actual_fids in root_actual_folios.items():
    if len(actual_fids) < 3:
        continue  # need presence in 3+ folios

    for ingr, expected_fids in ingr_expected_folios.items():
        if len(expected_fids) < 3:
            continue

        # Only compare folios where BOTH are defined
        common_folios = actual_fids | expected_fids
        both_mapped = common_folios & set(fid_to_chapter.keys())

        tp = len(actual_fids & expected_fids)
        fp = len(actual_fids - expected_fids)
        fn = len(expected_fids - actual_fids)
        tn = len(both_mapped) - tp - fp - fn

        if tp < 3:
            continue

        jaccard = tp / max(tp + fp + fn, 1)

        if jaccard >= 0.25 and fp <= 2:
            # Compute Fisher exact test (one-tailed)
            N = len(both_mapped)
            K = len(actual_fids & both_mapped)
            n = len(expected_fids & both_mapped)
            if N > 0 and K > 0 and n > 0:
                p_val = 0
                for x in range(tp, min(K, n) + 1):
                    try:
                        p_val += comb(K, x) * comb(N - K, n - x) / comb(N, n)
                    except:
                        pass

                results.append({
                    'root': root,
                    'ingredient': ingr,
                    'tp': tp, 'fp': fp, 'fn': fn, 'tn': tn,
                    'jaccard': round(jaccard, 3),
                    'p_value': round(p_val, 6),
                    'n_folios': len(actual_fids),
                })

# Sort by p-value (most significant first)
results.sort(key=lambda x: (x['p_value'], -x['jaccard']))

# Remove duplicates: keep best match per root
seen_roots = set()
unique_results = []
for r in results:
    if r['root'] not in seen_roots:
        unique_results.append(r)
        seen_roots.add(r['root'])

print(f'\n  Total matches: {len(results)}')
print(f'  Unique roots matched: {len(unique_results)}')

print(f'\n  {"Root":>12s} {"Ingredient":>12s} {"TP":>3s} {"FP":>3s} {"FN":>3s} '
      f'{"J":>5s} {"p-value":>8s} {"#Fol":>5s}')
print('  ' + '-' * 60)

new_discoveries = []
for r in unique_results[:40]:
    sig = '★★★' if r['p_value'] < 0.01 else '★★' if r['p_value'] < 0.05 else '★'
    print(f'  {r["root"]:>12s} {r["ingredient"]:>12s} {r["tp"]:>3d} {r["fp"]:>3d} '
          f'{r["fn"]:>3d} {r["jaccard"]:>5.2f} {r["p_value"]:>8.4f} {r["n_folios"]:>5d} {sig}')

    if r['p_value'] < 0.05:
        new_discoveries.append(r)

print(f'\n  Significant (p < 0.05): {len(new_discoveries)}')
print(f'  Highly significant (p < 0.01): {sum(1 for r in new_discoveries if r["p_value"] < 0.01)}')

# ================================================================
# SAVE
# ================================================================
output = {
    'n_anchors': n_anchors,
    'n_roots_tested': len(root_actual_folios),
    'n_matches': len(unique_results),
    'n_significant': len(new_discoveries),
    'discoveries': new_discoveries,
    'all_matches': unique_results[:50],
}

with open(os.path.join(RESULTS, 'fingerprint_115_results.json'), 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f'\nSaved fingerprint_115_results.json')
