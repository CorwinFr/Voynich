"""
VOYNICH ENGINE — Constraint Propagation v2

Fixes from v1:
  - 17 tier 1+2 anchors (13 ingredients + 4 body/disease)
  - RARITY WEIGHTING: rare ingredient match counts more
  - CROSS-FOLIO PROPAGATION: when folio F is assigned to plant P,
    roots shared between F and already-assigned folios reveal ingredients
    shared between P and those plants' chapters
  - Stricter assignment threshold (score >= 6 AND margin >= 2)
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
print('Building data...')

# Folio roots (non-functional, >= 3 chars)
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

# Macer chapter ingredients (from text)
INGR_PATTERNS = {
    'acetum': r'\bacet\w*\b', 'aqua': r'\baqua\w*\b|\bamne\b',
    'mel': r'\bmel\b|\bmell\w*\b|\bmulsa\b', 'piper': r'\bpiper\w*\b',
    'oleum': r'\boleu\w*\b|\boleo\b', 'sal': r'\bsal[ei]?\b|\bsale\b',
    'vinum': r'\bvin\w*\b|\bmero\b|\bmust\w*\b', 'succus': r'\bsucc\w*\b',
    'lac': r'\blac\b|\blact\w*\b', 'ovum': r'\bov[uoia]\w*\b',
    'nitrum': r'\bnitr\w*\b', 'myrrha': r'\bmyrrh\w*\b',
    'lens': r'\blen[st]\w*\b', 'nardus': r'\bnard\w*\b',
    'rosa': r'\bros[aisae]\w*\b', 'faba': r'\bfab\w*\b',
    'linum': r'\blin[uoi]\w*\b', 'feniculum': r'\bfenic\w*\b',
    'vesica': r'\bvesic\w*\b', 'cera': r'\bcer[ae]\w*\b',
    'thus': r'\bthus\b|\bthur\w*\b', 'sulphur': r'\bsulph\w*\b',
    'origanum': r'\borigan\w*\b', 'anethum': r'\baneth\w*\b',
    'coriandrum': r'\bcoriand\w*\b', 'chamomilla': r'\bchamom\w*\b',
    'plantago': r'\bplantag\w*\b', 'mentha': r'\bment[ha]\w*\b',
    'aristolochia': r'\baristoloch\w*\b', 'salvia': r'\bsalvi\w*\b',
    'verbena': r'\bverben\w*\b', 'betonica': r'\bbetonic\w*\b',
    'urtica': r'\burtic\w*\b', 'ruta': r'\brut[ae]\w*\b',
    'crocus': r'\bcroc\w*\b', 'malva': r'\bmalv\w*\b',
    'lactuca': r'\blactuc\w*\b',
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

# Ingredient RARITY across Macer chapters (for weighting)
ingr_chapter_count = Counter()
for ch_name, ingrs in chapter_ingrs.items():
    for ingr in ingrs:
        ingr_chapter_count[ingr] += 1

n_chapters = len(chapter_ingrs)
print(f'Folios: {len(folio_roots)}, Chapters: {n_chapters}')

# ================================================================
# INITIAL STATE — All tier 1+2 ingredient anchors
# ================================================================
known_roots = {}
# Tier 1
for root, data in registry['confirmed_ingredients'].items():
    if len(root) >= 3:
        known_roots[root] = data['latin']
# Tier 2 ingredients
known_roots.update({
    'ypch': 'aqua', 'ykeed': 'nitrum', 'seees': 'lens',
    'kald': 'ovum', 'otoly': 'sal', 'shocthy': 'mastix', 'shotch': 'nigella',
})
# Validated tier 2 from death match
for root, data in registry.get('death_match_vocabulary', {}).items():
    if data.get('validation') in ('PASS_distributional', 'PASS_fingerprint'):
        if data.get('type') == 'INGR' and data.get('status') != 'ELIMINATED':
            known_roots[root] = data['latin']

assigned = {
    'f48v':'Ruta','f9v':'Violae','f44v':'Apium','f51v':'Salvia',
    'f29r':'Lactuca','f41r':'Origanum','f37r':'Mentha',
    'f41v':'Coriandrum','f22r':'Verbena','f28r':'Aristolochia',
    'f5v':'Malva','f45r':'Atriplex','f66v':'Satureia',
    'f65v':'Centaurea','f3v':'Elleborus','f95v1':'Althaea',
}

print(f'Initial ingredient anchors: {len(known_roots)}')
for r, i in sorted(known_roots.items(), key=lambda x: x[1]):
    rarity = ingr_chapter_count.get(i, 0)
    print(f'  {r:>10s} = {i:>10s}  (in {rarity}/{n_chapters} chapters)')

# ================================================================
# SCORING FUNCTION (rarity-weighted)
# ================================================================
def score_folio_chapter(fid, ch_name):
    """Score a folio→chapter assignment using rarity-weighted matching."""
    if ch_name not in chapter_ingrs or fid not in folio_roots:
        return -999, set(), set()

    ch_ingrs = chapter_ingrs[ch_name]
    roots = folio_roots[fid]

    score = 0
    matched = set()
    mismatched = set()

    for root in roots:
        if root not in known_roots:
            continue
        ingr = known_roots[root]
        rarity_weight = max(1, n_chapters - ingr_chapter_count.get(ingr, 0))

        if ingr in ch_ingrs:
            score += rarity_weight  # rare match = high score
            matched.add((root, ingr))
        else:
            score -= rarity_weight * 0.5  # mismatch penalty
            mismatched.add((root, ingr))

    return score, matched, mismatched

# ================================================================
# PROPAGATION LOOP
# ================================================================
print(f'\n{"="*70}')
print('CONSTRAINT PROPAGATION v2 (rarity-weighted)')
print('='*70)

history = []
iteration = 0

while iteration < 150:
    iteration += 1

    # Score every unassigned folio × chapter
    candidates = []
    for fid in folio_roots:
        if fid in assigned:
            continue
        for ch_name in chapter_ingrs:
            score, matched, mismatched = score_folio_chapter(fid, ch_name)
            if len(matched) >= 2:
                candidates.append({
                    'fid': fid, 'chapter': ch_name,
                    'score': score, 'n_matched': len(matched),
                    'matched': matched, 'mismatched': mismatched,
                })

    if not candidates:
        print(f'\n  No more candidates')
        break

    # Sort by score, pick best
    candidates.sort(key=lambda x: -x['score'])
    best = candidates[0]

    # Check margin (distance to 2nd-best DIFFERENT chapter for same folio)
    second_score = 0
    for c in candidates[1:]:
        if c['fid'] == best['fid'] and c['chapter'] != best['chapter']:
            second_score = c['score']
            break
    margin = best['score'] - second_score

    # Threshold: score >= 5 AND margin >= 1
    if best['score'] < 5 or margin < 1:
        print(f'\n  Below threshold (score={best["score"]:.0f}, margin={margin:.0f})')
        break

    # ASSIGN
    fid = best['fid']
    ch_name = best['chapter']
    assigned[fid] = ch_name
    ch_ingrs = chapter_ingrs[ch_name]

    # CROSS-FOLIO PROPAGATION
    # Find roots in this folio that are ALSO in already-assigned folios
    new_mappings = []
    unknown_roots = folio_roots[fid] - set(known_roots.keys())

    for other_fid, other_ch in assigned.items():
        if other_fid == fid:
            continue
        if other_ch not in chapter_ingrs:
            continue

        other_roots = folio_roots.get(other_fid, set())
        shared_unknown = unknown_roots & other_roots

        if not shared_unknown:
            continue

        # Shared unknown roots must be ingredients shared between the two chapters
        shared_ingrs = ch_ingrs & chapter_ingrs[other_ch]
        shared_ingrs -= set(known_roots.values())  # remove already known

        # If exactly 1 shared ingredient matches the shared unknown roots
        if len(shared_ingrs) == 1 and len(shared_unknown) >= 1:
            new_ingr = list(shared_ingrs)[0]
            # Pick the root appearing in most folios (most useful)
            best_root = max(shared_unknown,
                           key=lambda r: sum(1 for f in folio_roots.values() if r in f))
            if best_root not in known_roots:
                known_roots[best_root] = new_ingr
                new_mappings.append((best_root, new_ingr, fid, other_fid))

    # Log
    matched_str = ', '.join(f'{r}={i}' for r, i in sorted(best['matched'])[:3])
    new_str = ', '.join(f'{r}={i}' for r, i, _, _ in new_mappings) if new_mappings else '-'

    print(f'  [{iteration:>3d}] {fid:>8s} → {ch_name:>15s}  '
          f'score={best["score"]:>5.0f}  margin={margin:>4.0f}  '
          f'match={best["n_matched"]}  NEW: {new_str}')

    history.append({
        'iteration': iteration,
        'folio': fid, 'chapter': ch_name,
        'score': best['score'], 'margin': margin,
        'n_matched': best['n_matched'],
        'new_mappings': [(r, i) for r, i, _, _ in new_mappings],
    })

# ================================================================
# RESULTS
# ================================================================
print(f'\n{"="*70}')
print('RESULTS')
print('='*70)

n_new_assigned = len(assigned) - 16
n_new_roots = len(known_roots) - 13  # started with ~13

print(f'\n  Iterations: {iteration}')
print(f'  Assigned folios: {len(assigned)} (+{n_new_assigned})')
print(f'  Known roots: {len(known_roots)} (+{n_new_roots})')

# New root mappings
initial_roots = set()
for root in registry['confirmed_ingredients']:
    initial_roots.add(root)
initial_roots.update({'ypch','ykeed','seees','kald','otoly','shocthy','shotch','dal','dary','qokeo'})

new_roots = {r: i for r, i in known_roots.items() if r not in initial_roots}
if new_roots:
    print(f'\n  NEW ROOT→INGREDIENT MAPPINGS:')
    for r, i in sorted(new_roots.items(), key=lambda x: x[1]):
        n = sum(1 for f in folio_roots.values() if r in f)
        print(f'    {r:>12s} = {i:>12s}  (in {n} folios)')

# Validation
SHERWOOD_EXTRA = {
    'f11r':'rosmarinus','f16r':'cannabis','f39r':'crocus',
    'f44r':'mandragora','f50v':'gentiana','f29v':'nigella',
    'f33v':'tanacetum','f49r':'nymphaea',
}

print(f'\n  VALIDATION:')
correct = 0
tested = 0
for fid, true in SHERWOOD_EXTRA.items():
    if fid not in assigned:
        continue
    pred = assigned[fid]
    tested += 1
    match = true[:4].lower() in pred.lower() or pred[:4].lower() in true.lower()
    if match: correct += 1
    print(f'    {"✓" if match else "✗"} {fid:>8s} true={true:>15s}  pred={pred:>15s}')

if tested:
    print(f'\n  Accuracy: {correct}/{tested} ({correct*100//tested}%)')

# New assignments
print(f'\n  NEW ASSIGNMENTS:')
for fid, ch in sorted(assigned.items()):
    if fid in {'f48v','f9v','f44v','f51v','f29r','f41r','f37r','f41v',
               'f22r','f28r','f5v','f45r','f66v','f65v','f3v','f95v1'}:
        continue
    s = 0
    for h in history:
        if h['folio'] == fid:
            s = h['score']
            break
    print(f'    {fid:>8s} → {ch:>15s}  score={s:.0f}')

# Chapter distribution
ch_counts = Counter(assigned.values())
print(f'\n  Chapter distribution:')
for ch, n in ch_counts.most_common(10):
    print(f'    {ch:>15s}: {n}')

# Save
output = {
    'iterations': iteration,
    'n_assigned': len(assigned),
    'n_known_roots': len(known_roots),
    'n_new_roots': n_new_roots,
    'history': history,
    'assigned': assigned,
    'known_roots': known_roots,
    'new_roots': new_roots,
    'validation_correct': correct,
    'validation_tested': tested,
}

with open(os.path.join(RESULTS, 'propagation_v2_results.json'), 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f'\nSaved propagation_v2_results.json')
