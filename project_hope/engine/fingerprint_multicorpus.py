"""
VOYNICH ENGINE — Fingerprint with ALL corpora (not just Macer)

Fix: use ingredient lists from Macer + Avicenna + Collectio + Alphita + Galen + Abenguefit
to build the reference matrix. Many new plants (Atropa, Arnica, etc.) exist in these corpora.
"""
import json, sys, io, os, re
from collections import Counter, defaultdict
from math import comb

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.dirname(os.path.dirname(__file__))
VMS_PATH = os.path.join(BASE, 'vms', 'vms_structured.json')
REG_PATH = os.path.join(BASE, 'hypothesis_registry.json')
BOT_PATH = os.path.join(BASE, 'engine', 'botanical_ids_extended.json')
RECIPE_DIR = os.path.join(os.path.dirname(BASE), 'attacks', 'RECIPE_DATASET')
MACER_PATH = os.path.join(BASE, 'session_14', 'macer_complete.json')
RESULTS = os.path.join(BASE, 'engine')

with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)
with open(REG_PATH, encoding='utf-8') as f:
    registry = json.load(f)
with open(BOT_PATH, encoding='utf-8') as f:
    bot_ids = json.load(f)
with open(MACER_PATH, encoding='utf-8') as f:
    macer_data = json.load(f)

LOGOS = {'o','l','d','r','v','x','k','m','f','t','y','c','s','sh','p','ch','air','h'}
FUNCTIONAL = set(registry.get('functional_words', {}).keys())
NOISE = {'ke', 'ko', 'po', 'do'}

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

ALL_IDS = dict(SHERWOOD)
for fid, data in bot_ids.items():
    if fid not in ALL_IDS:
        ALL_IDS[fid] = data['primary'].split()[0].lower().rstrip('0123456789 ')

KNOWN_ROOTS = set(registry['confirmed_ingredients'].keys())
KNOWN_ROOTS.update({'ypch','ykeed','seees','kald','otoly','shocthy','shotch','dal','dary','qokeo'})

# ================================================================
# STEP 1: Build MEGA ingredient matrix from ALL corpora
# ================================================================
print('Building mega ingredient matrix from all corpora...')

# Macer (from text)
INGR_PATTERNS = {
    'acetum': r'\bacet\w*\b', 'aqua': r'\baqua\w*\b|\bamne\b',
    'mel': r'\bmel\b|\bmell\w*\b|\bmulsa\b', 'piper': r'\bpiper\w*\b',
    'oleum': r'\boleu\w*\b|\boleo\b', 'sal': r'\bsal[ei]?\b|\bsale\b',
    'vinum': r'\bvin\w*\b|\bmero\b|\bmust\w*\b', 'succus': r'\bsucc\w*\b',
    'lac': r'\blac\b|\blact[ei]\w*\b', 'ovum': r'\bov[uoia]\w*\b',
    'nitrum': r'\bnitr\w*\b', 'myrrha': r'\bmyrrh\w*\b',
    'rosa': r'\bros[aisae]\w*\b', 'faba': r'\bfab[ae]\w*\b',
    'feniculum': r'\bfenic\w*\b', 'adeps': r'\badep\w*\b|\baxungi\w*\b',
    'thus': r'\bthus\b|\bthur\w*\b', 'cera': r'\bcer[ae]\w*\b',
    'vesica': r'\bvesic\w*\b', 'lens': r'\blen[st]\w*\b',
    'nardus': r'\bnard\w*\b', 'linum': r'\blin[uoi]\w*\b',
}

# plant_genus → set of ingredients (from ALL sources)
plant_ingr_matrix = defaultdict(set)

# Macer
for ch in macer_data['chapters']:
    genus = ch['name'].lower()
    text = ch['text'].lower()
    for ingr, pattern in INGR_PATTERNS.items():
        if re.search(pattern, text):
            plant_ingr_matrix[genus].add(ingr)

# All structured corpora
for corpus_file, name_field in [
    ('S08_AVICENNA.json', 'name'), ('S09_COLLECTIO.json', 'title'),
    ('S10_ALPHITA.json', 'name'), ('S15_ABENGUEFIT.json', 'name'),
    ('S14_GALEN.json', 'name'), ('S12_TACUINUM.json', 'name'),
]:
    path = os.path.join(RECIPE_DIR, corpus_file)
    if not os.path.exists(path):
        continue
    with open(path, encoding='utf-8') as f:
        data = json.load(f)

    for entry in data.get('entries', []):
        raw_name = entry.get(name_field, entry.get('name', entry.get('title', ''))).lower()
        # Normalize: extract genus-like word
        words = re.findall(r'[a-z]{4,}', raw_name)
        if not words:
            continue

        for tok in entry.get('tokens', []):
            if tok.get('type') == 'INGR':
                ref = tok.get('ref', tok.get('raw', '')).lower().replace('i_', '').strip('.,;: ')
                if len(ref) >= 3:
                    # Map this ingredient to ALL genus-words in the name
                    for w in words[:2]:
                        plant_ingr_matrix[w].add(ref)

# Now map folio → plant genus → ingredients
fid_ingredients = {}
n_mapped = 0

for fid, plant in ALL_IDS.items():
    if fid not in vms['folios']:
        continue
    genus = plant.lower()[:4]

    # Find best matching plant in matrix
    best_plant = None
    best_ingrs = set()
    for plant_name, ingrs in plant_ingr_matrix.items():
        if genus in plant_name or plant_name[:4] == genus:
            if len(ingrs) > len(best_ingrs):
                best_plant = plant_name
                best_ingrs = ingrs

    if best_ingrs and len(best_ingrs) >= 2:
        fid_ingredients[fid] = best_ingrs
        n_mapped += 1

print(f'Folios mapped to ingredient lists: {n_mapped}/{len(ALL_IDS)}')

# Build ingredient expected folios
ingr_expected = defaultdict(set)
for fid, ingrs in fid_ingredients.items():
    for ingr in ingrs:
        ingr_expected[ingr].add(fid)

# Filter: only ingredients in 3-50% of mapped folios (discriminant)
n_mapped_total = len(fid_ingredients)
discriminant_ingrs = {}
for ingr, fids in ingr_expected.items():
    pct = len(fids) * 100 // n_mapped_total
    if 5 <= pct <= 60:
        discriminant_ingrs[ingr] = fids

print(f'Discriminant ingredients (5-60% of folios): {len(discriminant_ingrs)}')
for ingr, fids in sorted(discriminant_ingrs.items(), key=lambda x: len(x[1])):
    print(f'  {ingr:>15s}: {len(fids)} folios ({len(fids)*100//n_mapped_total}%)')

# ================================================================
# STEP 2: VMS root fingerprints
# ================================================================
root_actual = defaultdict(set)
for fid in fid_ingredients:
    folio = vms['folios'][fid]
    for block in folio['blocks']:
        for line in block['lines']:
            for w in line['words']:
                eva = w['eva_primary']
                if eva in LOGOS: continue
                root = (w.get('morphology') or {}).get('root', '')
                if root and len(root) >= 4 and root not in FUNCTIONAL and root not in NOISE:
                    if root not in KNOWN_ROOTS:
                        root_actual[root].add(fid)

print(f'\nUnknown roots (>= 4 chars): {len(root_actual)}')

# ================================================================
# STEP 3: Fingerprint matching with Fisher test
# ================================================================
print(f'\n{"="*70}')
print(f'FINGERPRINT MATCHING ({len(root_actual)} roots × {len(discriminant_ingrs)} ingredients)')
print('='*70)

results = []

for root, actual_fids in root_actual.items():
    if len(actual_fids) < 3:
        continue

    for ingr, expected_fids in discriminant_ingrs.items():
        common = set(fid_ingredients.keys())
        tp = len(actual_fids & expected_fids & common)
        fp = len((actual_fids - expected_fids) & common)
        fn = len((expected_fids - actual_fids) & common)
        tn = len(common) - tp - fp - fn

        if tp < 3:
            continue

        jaccard = tp / max(tp + fp + fn, 1)
        if jaccard < 0.20 or fp > 3:
            continue

        # Fisher exact test
        N = len(common)
        K = len(actual_fids & common)
        n = len(expected_fids & common)
        p_val = 0
        for x in range(tp, min(K, n) + 1):
            try:
                p_val += comb(K, x) * comb(N - K, n - x) / comb(N, n)
            except:
                pass

        results.append({
            'root': root, 'ingredient': ingr,
            'tp': tp, 'fp': fp, 'fn': fn,
            'jaccard': round(jaccard, 3),
            'p_value': round(p_val, 6),
            'n_root_folios': len(actual_fids),
        })

results.sort(key=lambda x: (x['p_value'], -x['jaccard']))

# Deduplicate: best per root
seen = set()
unique = []
for r in results:
    if r['root'] not in seen:
        unique.append(r)
        seen.add(r['root'])

print(f'\n  Total matches: {len(results)}')
print(f'  Unique roots: {len(unique)}')
print(f'  Significant (p < 0.05): {sum(1 for r in unique if r["p_value"] < 0.05)}')
print(f'  Highly sig (p < 0.01): {sum(1 for r in unique if r["p_value"] < 0.01)}')

print(f'\n  {"Root":>12s} {"Ingredient":>12s} {"TP":>3s} {"FP":>3s} {"FN":>3s} '
      f'{"J":>5s} {"p":>8s} {"#F":>3s}')
print('  ' + '-' * 55)

for r in unique[:30]:
    sig = '★★★' if r['p_value'] < 0.01 else '★★' if r['p_value'] < 0.05 else '★' if r['p_value'] < 0.1 else ''
    print(f'  {r["root"]:>12s} {r["ingredient"]:>12s} {r["tp"]:>3d} {r["fp"]:>3d} '
          f'{r["fn"]:>3d} {r["jaccard"]:>5.2f} {r["p_value"]:>8.4f} {r["n_root_folios"]:>3d} {sig}')

# Save
output = {
    'n_mapped_folios': n_mapped,
    'n_discriminant_ingrs': len(discriminant_ingrs),
    'n_roots_tested': len(root_actual),
    'n_significant': sum(1 for r in unique if r['p_value'] < 0.05),
    'results': unique[:50],
}

with open(os.path.join(RESULTS, 'fingerprint_multicorpus_results.json'), 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f'\nSaved fingerprint_multicorpus_results.json')
