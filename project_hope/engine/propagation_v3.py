"""
VOYNICH ENGINE — Propagation v3 with COMPLETE Macer parsing

Key fix: add PLANT CROSS-REFERENCES as ingredients.
If Ruta chapter mentions "piper", then piper is in Ruta's ingredient list.
If Absinthium chapter mentions "ruta", then RUTA is in Absinthium's list.

This gives us discriminant power from PLANT NAMES (which we know 23 of).
"""
import json, sys, io, os, re
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.dirname(os.path.dirname(__file__))
VMS_PATH = os.path.join(BASE, 'vms', 'vms_structured.json')
REG_PATH = os.path.join(BASE, 'hypothesis_registry.json')
MACER_PATH = os.path.join(BASE, 'session_14', 'macer_complete.json')
RESULTS = os.path.join(BASE, 'engine')

with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)
with open(REG_PATH, encoding='utf-8') as f:
    registry = json.load(f)
with open(MACER_PATH, encoding='utf-8') as f:
    macer_data = json.load(f)

LOGOS = {'o','l','d','r','v','x','k','m','f','t','y','c','s','sh','p','ch','air','h'}
FUNCTIONAL = set(registry.get('functional_words', {}).keys())
NOISE = {'ke', 'ko', 'po', 'do'}

# ================================================================
# BUILD COMPLETE MACER INGREDIENT MATRIX
# ================================================================
print('Building COMPLETE Macer ingredient matrix...')

# Standard ingredients
INGR_PATTERNS = {
    'acetum': r'\bacet\w*\b', 'aqua': r'\baqua\w*\b|\bamne\b',
    'mel': r'\bmel\b|\bmell\w*\b|\bmulsa\b', 'piper': r'\bpiper\w*\b',
    'oleum': r'\boleu\w*\b|\boleo\b', 'sal': r'\bsal[ei]?\b|\bsale\b|\bsalque\b',
    'vinum': r'\bvin\w*\b|\bmero\b|\bmust\w*\b', 'succus': r'\bsucc\w*\b',
    'lac': r'\blac\b|\blact[ei]\w*\b', 'ovum': r'\bov[uoia]\w*\b',
    'nitrum': r'\bnitr\w*\b', 'myrrha': r'\bmyrrh\w*\b',
    'lens': r'\blen[st]\w*\b', 'nardus': r'\bnard\w*\b',
    'rosa': r'\bros[aisae]\w*\b', 'faba': r'\bfab[ae]\w*\b',
    'feniculum': r'\bfenic\w*\b', 'vesica': r'\bvesic\w*\b',
    'adeps': r'\badep\w*\b|\baxungi\w*\b',
}

# Plant cross-references (plant name used AS ingredient in another chapter)
PLANT_PATTERNS = {}
plant_names = set()
for ch in macer_data['chapters']:
    pname = ch['name'].lower()
    plant_names.add(pname)
    if len(pname) >= 4:
        PLANT_PATTERNS[pname] = r'\b' + re.escape(pname[:4]) + r'\w*\b'

chapter_ingrs = {}
for ch in macer_data['chapters']:
    name = ch['name']
    text = ch['text'].lower()
    ingrs = set()

    # Standard ingredients
    for ingr_name, pattern in INGR_PATTERNS.items():
        if re.search(pattern, text):
            ingrs.add(ingr_name)

    # Plant cross-references (other plants mentioned in this chapter)
    for pname, pattern in PLANT_PATTERNS.items():
        if pname == name.lower():
            continue  # skip self-reference
        if re.search(pattern, text):
            ingrs.add(pname)  # plant name as "ingredient"

    chapter_ingrs[name] = ingrs

n_chapters = len(chapter_ingrs)
total_ingrs = set()
for ingrs in chapter_ingrs.values():
    total_ingrs.update(ingrs)

print(f'Chapters: {n_chapters}, Total unique items: {len(total_ingrs)}')

# Show rarity
rarity = Counter()
for ch, ingrs in chapter_ingrs.items():
    for i in ingrs:
        rarity[i] += 1

print(f'\nRARE items (in <=3 chapters):')
rare_items = {i for i, c in rarity.items() if c <= 3}
for item, count in sorted(rarity.items(), key=lambda x: x[1]):
    if count <= 5:
        print(f'  {item:>15s}: {count} chapters')

# ================================================================
# BUILD KNOWN ROOTS (ingredients + plant names)
# ================================================================
known_roots = {}

# Confirmed ingredients
for root, data in registry['confirmed_ingredients'].items():
    if len(root) >= 3:
        known_roots[root] = data['latin']
known_roots.update({
    'ypch': 'aqua', 'ykeed': 'nitrum', 'seees': 'lens',
    'kald': 'ovum', 'otoly': 'sal', 'shocthy': 'mastix', 'shotch': 'nigella',
})

# Validated death match ingredients
for root, data in registry.get('death_match_vocabulary', {}).items():
    if data.get('type') == 'INGR' and data.get('status') != 'ELIMINATED' and data.get('status') != 'CONFLICTED':
        if len(root) >= 3:
            known_roots[root] = data['latin']

# PLANT NAMES as roots (this is the KEY addition!)
for root, data in registry['plant_names'].items():
    if len(root) >= 4:  # only longer plant roots (avoid short FP)
        latin = data['latin'].lower()
        if latin in plant_names:  # only if the plant exists in Macer
            known_roots[root] = latin

# Build folio roots
folio_roots = {}
for fid, folio in sorted(vms['folios'].items()):
    if 'herbal' not in folio['metadata']['section']:
        continue
    roots = set()
    for block in folio['blocks']:
        for line in block['lines']:
            for w in line['words']:
                eva = w['eva_primary']
                if eva in LOGOS: continue
                root = (w.get('morphology') or {}).get('root', '')
                if root and len(root) >= 3 and root not in FUNCTIONAL and root not in NOISE:
                    roots.add(root)
    if roots:
        folio_roots[fid] = roots

print(f'\nKnown roots (ingredients + plants): {len(known_roots)}')
ingr_count = sum(1 for r, l in known_roots.items() if l not in plant_names)
plant_count = sum(1 for r, l in known_roots.items() if l in plant_names)
print(f'  Ingredients: {ingr_count}, Plant names: {plant_count}')

# Show which plant names we can use
print(f'\n  Plant roots usable as anchors:')
for root, latin in sorted(known_roots.items(), key=lambda x: x[1]):
    if latin in plant_names:
        n_as_ingr = rarity.get(latin, 0)
        print(f'    {root:>10s} = {latin:>15s}  (mentioned in {n_as_ingr} other chapters)')

# ================================================================
# FIXED ASSIGNMENTS
# ================================================================
assigned = {
    'f48v':'Ruta','f9v':'Violae','f44v':'Apium','f51v':'Salvia',
    'f29r':'Lactuca','f41r':'Origanum','f37r':'Mentha',
    'f41v':'Coriandrum','f22r':'Verbena','f28r':'Aristolochia',
    'f5v':'Malva','f45r':'Atriplex','f66v':'Satureia',
    'f65v':'Centaurea','f3v':'Elleborus','f95v1':'Althaea',
}

# ================================================================
# SCORING (rarity-weighted)
# ================================================================
def score(fid, ch_name):
    if ch_name not in chapter_ingrs or fid not in folio_roots:
        return -999, set(), set()
    ch_ingrs_set = chapter_ingrs[ch_name]
    roots = folio_roots[fid]
    sc = 0
    matched = set()
    mismatched = set()
    for root in roots:
        if root not in known_roots:
            continue
        item = known_roots[root]
        weight = max(1, n_chapters - rarity.get(item, 0))
        if item in ch_ingrs_set:
            sc += weight
            matched.add((root, item))
        else:
            sc -= weight * 0.3
            mismatched.add((root, item))
    return sc, matched, mismatched

# ================================================================
# PROPAGATION
# ================================================================
print(f'\n{"="*70}')
print('PROPAGATION v3 (with plant cross-references)')
print('='*70)

history = []
iteration = 0

while iteration < 200:
    iteration += 1
    candidates = []
    for fid in folio_roots:
        if fid in assigned:
            continue
        for ch_name in chapter_ingrs:
            sc, matched, mis = score(fid, ch_name)
            if len(matched) >= 2:
                candidates.append({
                    'fid': fid, 'chapter': ch_name,
                    'score': sc, 'matched': matched, 'n_matched': len(matched),
                })

    if not candidates:
        print(f'\n  No candidates')
        break

    candidates.sort(key=lambda x: -x['score'])
    best = candidates[0]

    # Margin
    second = 0
    for c in candidates[1:]:
        if c['fid'] == best['fid'] and c['chapter'] != best['chapter']:
            second = c['score']
            break
    margin = best['score'] - second

    if best['score'] < 10 or margin < 5:
        print(f'\n  Below threshold (score={best["score"]:.0f}, margin={margin:.0f})')
        break

    assigned[best['fid']] = best['chapter']
    matched_str = ', '.join(f'{r}={i}' for r, i in sorted(best['matched'])[:5])
    print(f'  [{iteration:>3d}] {best["fid"]:>8s} → {best["chapter"]:>15s}  '
          f'score={best["score"]:>5.0f}  margin={margin:>4.0f}  '
          f'match={best["n_matched"]}  [{matched_str}]')

    history.append({
        'iteration': iteration, 'folio': best['fid'],
        'chapter': best['chapter'], 'score': best['score'],
        'margin': margin, 'n_matched': best['n_matched'],
        'matched': sorted((r, i) for r, i in best['matched']),
    })

# ================================================================
# VALIDATION
# ================================================================
print(f'\n{"="*70}')
print('VALIDATION')
print('='*70)

SHERWOOD_EXTRA = {
    'f11r':'rosmarinus','f16r':'cannabis','f39r':'crocus',
    'f44r':'mandragora','f50v':'gentiana','f29v':'nigella',
    'f33v':'tanacetum','f49r':'nymphaea',
}

correct = 0
tested = 0
for fid, true in SHERWOOD_EXTRA.items():
    if fid not in assigned:
        continue
    pred = assigned[fid]
    tested += 1
    match = true[:4].lower() in pred.lower() or pred[:4].lower() in true.lower()
    if match: correct += 1
    print(f'  {"✓" if match else "✗"} {fid:>8s} true={true:>15s}  pred={pred:>15s}')

if tested:
    print(f'\n  Accuracy: {correct}/{tested} ({correct*100//tested}%)')

# All assignments
print(f'\n  NEW ASSIGNMENTS ({len(assigned)-16}):')
for fid, ch in sorted(assigned.items()):
    if fid in {'f48v','f9v','f44v','f51v','f29r','f41r','f37r','f41v',
               'f22r','f28r','f5v','f45r','f66v','f65v','f3v','f95v1'}:
        continue
    for h in history:
        if h['folio'] == fid:
            print(f'    {fid:>8s} → {ch:>15s}  score={h["score"]:.0f}  margin={h["margin"]:.0f}  '
                  f'matched={h["matched"][:4]}')

ch_counts = Counter(assigned.values())
print(f'\n  Distribution: {dict(ch_counts.most_common(10))}')

# Save
output = {
    'iterations': iteration,
    'n_assigned': len(assigned),
    'n_new': len(assigned) - 16,
    'n_known_roots': len(known_roots),
    'history': history,
    'assigned': assigned,
    'validation_correct': correct,
    'validation_tested': tested,
}

with open(os.path.join(RESULTS, 'propagation_v3_results.json'), 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f'\nSaved propagation_v3_results.json')
