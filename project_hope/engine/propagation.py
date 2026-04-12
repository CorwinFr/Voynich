"""
VOYNICH ENGINE — Constraint Propagation (Sudoku approach)

1. Start with 14 fixed folio→chapter (Sherwood) + 10 known root→ingredient
2. Pick the MOST CONSTRAINED unassigned folio (highest score against a chapter)
3. Assign it → roots unique to this folio+chapter become NEW known ingredients
4. Propagate: these new knowns constrain ALL remaining folios
5. Repeat until no more confident assignments possible
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
# BUILD DATA
# ================================================================
print('Building data structures...')

# VMS folio roots
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

# Macer chapter ingredients (from full text)
INGR_PATTERNS = {
    'acetum': r'\bacet\w*\b', 'aqua': r'\baqua\w*\b|\bamne\b',
    'mel': r'\bmel\b|\bmell\w*\b|\bmulsa\b', 'piper': r'\bpiper\w*\b',
    'oleum': r'\boleu\w*\b|\boleo\b', 'sal': r'\bsal[ei]?\b|\bsale\b',
    'vinum': r'\bvin\w*\b|\bmero\b|\bmust\w*\b', 'succus': r'\bsucc\w*\b',
    'lac': r'\blac\b|\blact\w*\b', 'ovum': r'\bov[uoia]\w*\b',
    'nitrum': r'\bnitr\w*\b', 'myrrha': r'\bmyrrh\w*\b',
    'lens': r'\blen[st]\w*\b', 'nardus': r'\bnard\w*\b',
    'rosa': r'\bros[ai]\w*\b', 'faba': r'\bfab\w*\b',
    'linum': r'\blin[uoi]\w*\b', 'feniculum': r'\bfenic\w*\b',
    'vesica': r'\bvesic\w*\b', 'cera': r'\bcer[ae]\w*\b',
    'thus': r'\bthus\b|\bthur\w*\b', 'sulphur': r'\bsulph\w*\b',
    'origanum': r'\borigan\w*\b', 'anethum': r'\baneth\w*\b',
    'ruta': r'\brut[ae]\w*\b', 'coriandrum': r'\bcoriand\w*\b',
    'plantago': r'\bplantag\w*\b', 'mentha': r'\bment[ha]\w*\b',
    'aristolochia': r'\baristoloch\w*\b', 'salvia': r'\bsalvi\w*\b',
    'verbena': r'\bverben\w*\b', 'chamomilla': r'\bchamom\w*\b',
    'betonica': r'\bbetonic\w*\b', 'urtica': r'\burtic\w*\b',
    'crocus': r'\bcroc\w*\b',
}

chapter_ingrs = {}
for ch in macer_data['chapters']:
    name = ch['name']
    text = ch['text'].lower()
    ingrs = set()
    for ingr_name, pattern in INGR_PATTERNS.items():
        if re.search(pattern, text):
            ingrs.add(ingr_name)
    if ingrs:
        chapter_ingrs[name] = ingrs

print(f'Folios: {len(folio_roots)}, Chapters: {len(chapter_ingrs)}')

# ================================================================
# INITIAL KNOWN STATE
# ================================================================
known_roots = {}  # root → ingredient
for root, data in registry['confirmed_ingredients'].items():
    if len(root) >= 3:
        known_roots[root] = data['latin']
known_roots['ypch'] = 'aqua'
known_roots['ykeed'] = 'nitrum'
known_roots['seees'] = 'lens'
known_roots['kald'] = 'ovum'
known_roots['otoly'] = 'sal'
known_roots['shocthy'] = 'mastix'
known_roots['shotch'] = 'nigella'

assigned_folios = {
    'f48v':'Ruta','f9v':'Violae','f44v':'Apium','f51v':'Salvia',
    'f29r':'Lactuca','f41r':'Origanum','f37r':'Mentha',
    'f41v':'Coriandrum','f22r':'Verbena','f28r':'Aristolochia',
    'f5v':'Malva','f45r':'Atriplex','f66v':'Satureia',
    'f65v':'Centaurea','f3v':'Elleborus','f95v1':'Althaea',
}

print(f'Initial known roots: {len(known_roots)}')
print(f'Initial assigned folios: {len(assigned_folios)}')

# ================================================================
# CONSTRAINT PROPAGATION LOOP
# ================================================================
print(f'\n{"="*70}')
print('CONSTRAINT PROPAGATION')
print('='*70)

iteration = 0
history = []

while True:
    iteration += 1

    # SCORE every unassigned folio against every chapter
    best_fid = None
    best_chapter = None
    best_score = 0
    best_matched = set()
    best_unmatched_roots = set()

    for fid, roots in folio_roots.items():
        if fid in assigned_folios:
            continue

        for ch_name, ch_ingrs in chapter_ingrs.items():
            score = 0
            matched = set()
            mismatched = set()

            for root in roots:
                if root in known_roots:
                    ingr = known_roots[root]
                    if ingr in ch_ingrs:
                        score += 3  # known root matches chapter
                        matched.add((root, ingr))
                    else:
                        score -= 2  # known root contradicts chapter
                        mismatched.add((root, ingr))

            # Need at least 2 positive matches to be credible
            if score > best_score and len(matched) >= 2:
                best_score = score
                best_fid = fid
                best_chapter = ch_name
                best_matched = matched
                best_unmatched_roots = roots - set(r for r, _ in matched) - set(r for r, _ in mismatched)

    if best_fid is None or best_score < 4:
        print(f'\n  No more confident assignments (best_score={best_score})')
        break

    # ASSIGN
    assigned_folios[best_fid] = best_chapter
    ch_ingrs = chapter_ingrs[best_chapter]

    # PROPAGATE: roots in this folio that are NOT yet known
    # and the chapter has fewer unknown ingredients than unknown roots
    known_ingrs_here = set(ingr for _, ingr in best_matched)
    unknown_ch_ingrs = ch_ingrs - known_ingrs_here - set(known_roots.values())
    unknown_roots_here = best_unmatched_roots

    new_mappings = []
    # If only 1 unknown ingredient and 1 dominant unknown root → map it
    if len(unknown_ch_ingrs) == 1 and len(unknown_roots_here) >= 1:
        # The most frequent unknown root in this folio is probably this ingredient
        ingr = list(unknown_ch_ingrs)[0]
        # Pick the root that appears in the MOST folios (most useful to fix)
        best_root = max(unknown_roots_here,
                       key=lambda r: sum(1 for f in folio_roots.values() if r in f))
        known_roots[best_root] = ingr
        new_mappings.append((best_root, ingr))

    # Log
    matched_str = ', '.join(f'{r}={i}' for r, i in sorted(best_matched)[:4])
    new_str = ', '.join(f'{r}={i}' for r, i in new_mappings) if new_mappings else 'none'

    print(f'  [{iteration:>3d}] {best_fid:>8s} → {best_chapter:>15s}  '
          f'score={best_score:>3d}  matched={len(best_matched)}  '
          f'new_maps: {new_str}')

    history.append({
        'iteration': iteration,
        'folio': best_fid,
        'chapter': best_chapter,
        'score': best_score,
        'n_matched': len(best_matched),
        'matched': sorted((r, i) for r, i in best_matched),
        'new_mappings': new_mappings,
    })

    if iteration >= 100:
        print(f'  Max iterations reached')
        break

# ================================================================
# RESULTS
# ================================================================
print(f'\n{"="*70}')
print('RESULTS')
print('='*70)

print(f'\n  Iterations: {iteration}')
print(f'  Assigned folios: {len(assigned_folios)} (was 16)')
print(f'  Known roots: {len(known_roots)} (was ~10)')

# New root→ingredient mappings
initial_roots = {'cth', 'cht', 'chk', 'otoly', 'ypch', 'ykeed', 'seees', 'kald', 'shocthy', 'shotch'}
new_roots = {r: i for r, i in known_roots.items() if r not in initial_roots}
if new_roots:
    print(f'\n  NEW ROOT MAPPINGS:')
    for r, i in sorted(new_roots.items()):
        n_folios = sum(1 for f in folio_roots.values() if r in f)
        print(f'    {r:>12s} = {i:>12s}  (appears in {n_folios} folios)')

# Validation
SHERWOOD_EXTRA = {
    'f11r':'rosmarinus','f16r':'cannabis','f39r':'crocus',
    'f44r':'mandragora','f50v':'gentiana','f29v':'nigella',
    'f33v':'tanacetum','f49r':'nymphaea',
}

print(f'\n  VALIDATION (unfix Sherwood):')
correct = 0
tested = 0
for fid, true_plant in SHERWOOD_EXTRA.items():
    if fid not in assigned_folios:
        continue
    pred = assigned_folios[fid]
    tested += 1
    match = true_plant[:4].lower() in pred.lower() or pred[:4].lower() in true_plant.lower()
    if match:
        correct += 1
    status = '✓' if match else '✗'
    print(f'    {status} {fid:>8s} true={true_plant:>15s}  pred={pred:>15s}')

if tested:
    print(f'\n  Accuracy: {correct}/{tested}')

# Assignment list
print(f'\n  ALL NEW ASSIGNMENTS:')
for fid, ch in sorted(assigned_folios.items()):
    if fid in {'f48v','f9v','f44v','f51v','f29r','f41r','f37r','f41v',
               'f22r','f28r','f5v','f45r','f66v','f65v','f3v','f95v1'}:
        continue  # skip fixed Sherwood
    score = 0
    for h in history:
        if h['folio'] == fid:
            score = h['score']
    print(f'    {fid:>8s} → {ch:>15s}  score={score}')

# Save
output = {
    'iterations': iteration,
    'n_assigned': len(assigned_folios),
    'n_known_roots': len(known_roots),
    'history': history,
    'known_roots': known_roots,
    'assigned_folios': assigned_folios,
    'new_root_mappings': new_roots,
}

with open(os.path.join(RESULTS, 'propagation_results.json'), 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f'\nSaved propagation_results.json')
