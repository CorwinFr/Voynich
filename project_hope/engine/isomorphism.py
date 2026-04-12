"""
VOYNICH ENGINE — Structural Isomorphism Attack

Graph matching between VMS folio co-occurrence and corpus ingredient co-occurrence.
No ingredient decoding required — pure structural comparison.

Usage:
    python -m project_hope.engine.isomorphism
"""
import json, sys, io, os, random, math
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.dirname(os.path.dirname(__file__))
VMS_PATH = os.path.join(BASE, 'vms', 'vms_structured.json')
REG_PATH = os.path.join(BASE, 'hypothesis_registry.json')
RECIPE_DIR = os.path.join(os.path.dirname(BASE), 'attacks', 'RECIPE_DATASET')
MACER_PATH = os.path.join(BASE, 'session_14', 'macer_complete.json')
RESULTS = os.path.join(BASE, 'engine')

# ================================================================
# LOAD DATA
# ================================================================
print('Loading data...')
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
# STEP 1: BUILD VMS GRAPH
# ================================================================
print('\n' + '='*70)
print('STEP 1 — VMS co-occurrence graph')
print('='*70)

# Extract non-functional roots per herbal folio
folio_roots = {}
folio_list = []

for fid, folio in sorted(vms['folios'].items()):
    sec = folio['metadata']['section']
    if 'herbal' not in sec:
        continue

    roots = set()
    for block in folio['blocks']:
        for line in block['lines']:
            for w in line['words']:
                eva = w['eva_primary']
                if eva in LOGOS:
                    continue
                root = (w.get('morphology') or {}).get('root', '')
                if root and len(root) >= 3 and root not in FUNCTIONAL and root not in NOISE:
                    roots.add(root)

    if len(roots) >= 3:
        folio_roots[fid] = roots
        folio_list.append(fid)

N_FOLIOS = len(folio_list)
fid_to_idx = {fid: i for i, fid in enumerate(folio_list)}

# Build adjacency matrix
vms_adj = [[0]*N_FOLIOS for _ in range(N_FOLIOS)]

for i in range(N_FOLIOS):
    for j in range(i+1, N_FOLIOS):
        shared = len(folio_roots[folio_list[i]] & folio_roots[folio_list[j]])
        vms_adj[i][j] = shared
        vms_adj[j][i] = shared

# Stats
edges = sum(1 for i in range(N_FOLIOS) for j in range(i+1, N_FOLIOS) if vms_adj[i][j] > 0)
avg_weight = sum(vms_adj[i][j] for i in range(N_FOLIOS) for j in range(i+1, N_FOLIOS)) / max(edges, 1)
print(f'  Folios: {N_FOLIOS}')
print(f'  Edges (shared roots > 0): {edges}')
print(f'  Avg shared roots per edge: {avg_weight:.1f}')


# ================================================================
# STEP 2: BUILD MACER GRAPH (from parsed chapters)
# ================================================================
print(f'\n{"="*70}')
print('STEP 2 — Macer ingredient co-occurrence graph')
print('='*70)

import re

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
    'crocus': r'\bcroc\w*\b', 'papaver': r'\bpapav\w*\b',
}

chapter_ingrs = {}
chapter_list = []

for ch in macer_data['chapters']:
    name = ch['name']
    text = ch['text'].lower()

    ingrs = set()
    for ingr_name, pattern in INGR_PATTERNS.items():
        if re.search(pattern, text):
            ingrs.add(ingr_name)

    if len(ingrs) >= 2:
        chapter_ingrs[name] = ingrs
        chapter_list.append(name)

N_CHAPTERS = len(chapter_list)
ch_to_idx = {name: i for i, name in enumerate(chapter_list)}

# Build adjacency matrix
macer_adj = [[0]*N_CHAPTERS for _ in range(N_CHAPTERS)]

for i in range(N_CHAPTERS):
    for j in range(i+1, N_CHAPTERS):
        shared = len(chapter_ingrs[chapter_list[i]] & chapter_ingrs[chapter_list[j]])
        macer_adj[i][j] = shared
        macer_adj[j][i] = shared

m_edges = sum(1 for i in range(N_CHAPTERS) for j in range(i+1, N_CHAPTERS) if macer_adj[i][j] > 0)
m_avg = sum(macer_adj[i][j] for i in range(N_CHAPTERS) for j in range(i+1, N_CHAPTERS)) / max(m_edges, 1)
print(f'  Chapters: {N_CHAPTERS}')
print(f'  Edges: {m_edges}')
print(f'  Avg shared ingredients per edge: {m_avg:.1f}')


# ================================================================
# STEP 3: FIXED ANCHORS (Sherwood → Macer)
# ================================================================
SHERWOOD_MACER = {
    'f48v':'Ruta','f9v':'Violae','f44v':'Apium','f51v':'Salvia',
    'f29r':'Lactuca','f41r':'Origanum','f37r':'Mentha',
    'f41v':'Coriandrum','f22r':'Verbena','f28r':'Aristolochia',
    'f5v':'Malva','f45r':'Atriplex','f66v':'Satureia',
    'f65v':'Centaurea','f3v':'Elleborus','f95v1':'Althaea',
}

fixed = {}  # folio_idx → chapter_idx
for fid, ch_name in SHERWOOD_MACER.items():
    if fid in fid_to_idx and ch_name in ch_to_idx:
        fixed[fid_to_idx[fid]] = ch_to_idx[ch_name]

print(f'\n  Fixed anchors: {len(fixed)}')


# ================================================================
# STEP 4: SIMULATED ANNEALING
# ================================================================
print(f'\n{"="*70}')
print('STEP 4 — Simulated Annealing')
print('='*70)

# Initialize: random assignment for non-fixed folios
assignment = [0] * N_FOLIOS
for i in range(N_FOLIOS):
    if i in fixed:
        assignment[i] = fixed[i]
    else:
        assignment[i] = random.randint(0, N_CHAPTERS - 1)

def compute_score(assign):
    """Compute global structural matching score."""
    score = 0
    for i in range(N_FOLIOS):
        for j in range(i+1, N_FOLIOS):
            if vms_adj[i][j] > 0:
                ci = assign[i]
                cj = assign[j]
                if ci < N_CHAPTERS and cj < N_CHAPTERS:
                    score += vms_adj[i][j] * macer_adj[ci][cj]
    return score

# SA parameters
T_START = 1000.0
T_END = 0.1
COOLING = 0.9995
MAX_ITER = 200000

current_score = compute_score(assignment)
best_score = current_score
best_assignment = assignment[:]

T = T_START
n_accepted = 0
n_rejected = 0

for iteration in range(MAX_ITER):
    # Pick a random non-fixed folio
    i = random.randint(0, N_FOLIOS - 1)
    while i in fixed:
        i = random.randint(0, N_FOLIOS - 1)

    # Try a new chapter assignment
    old_ch = assignment[i]
    new_ch = random.randint(0, N_CHAPTERS - 1)
    if new_ch == old_ch:
        continue

    # Compute score delta (efficient: only affected edges)
    delta = 0
    for j in range(N_FOLIOS):
        if j == i or vms_adj[i][j] == 0:
            continue
        cj = assignment[j]
        if cj < N_CHAPTERS:
            old_contrib = vms_adj[i][j] * macer_adj[old_ch][cj]
            new_contrib = vms_adj[i][j] * macer_adj[new_ch][cj]
            delta += new_contrib - old_contrib

    # Accept or reject
    if delta > 0 or random.random() < math.exp(delta / max(T, 0.001)):
        assignment[i] = new_ch
        current_score += delta
        n_accepted += 1

        if current_score > best_score:
            best_score = current_score
            best_assignment = assignment[:]
    else:
        n_rejected += 1

    T *= COOLING

    if iteration % 20000 == 0:
        print(f'  Iter {iteration:>7d}  T={T:.1f}  score={current_score:.0f}  '
              f'best={best_score:.0f}  acc={n_accepted}  rej={n_rejected}')

assignment = best_assignment
final_score = best_score
print(f'\n  FINAL: score={final_score:.0f}  (accepted={n_accepted}, rejected={n_rejected})')


# ================================================================
# STEP 5: RESULTS — Folio assignments
# ================================================================
print(f'\n{"="*70}')
print('STEP 5 — ASSIGNMENTS')
print('='*70)

# Validation against extended Sherwood
SHERWOOD_EXTRA = {
    'f11r':'rosmarinus','f16r':'cannabis','f39r':'crocus',
    'f44r':'mandragora','f50v':'gentiana','f29v':'nigella',
    'f33v':'tanacetum','f49r':'nymphaea',
}

correct_top1 = 0
tested = 0

for fid, true_plant in SHERWOOD_EXTRA.items():
    if fid not in fid_to_idx:
        continue
    idx = fid_to_idx[fid]
    pred_ch = chapter_list[assignment[idx]]
    tested += 1
    match = true_plant[:4].lower() in pred_ch.lower() or pred_ch[:4].lower() in true_plant.lower()
    if match:
        correct_top1 += 1
        status = '✓'
    else:
        status = '✗'
    print(f'  {status} {fid:>8s} true={true_plant:>15s}  pred={pred_ch:>15s}')

if tested:
    print(f'\n  Accuracy: {correct_top1}/{tested} ({correct_top1*100//tested}%)')

# Show assignment distribution
ch_counts = Counter(chapter_list[a] for a in assignment)
print(f'\n  Chapter assignment distribution (top 15):')
for ch, n in ch_counts.most_common(15):
    print(f'    {ch:>15s}: {n} folios')


# ================================================================
# STEP 6: EXTRACT ROOT→INGREDIENT MAPPINGS
# ================================================================
print(f'\n{"="*70}')
print('STEP 6 — Root→Ingredient extraction')
print('='*70)

# For each non-functional root, find which ingredients it could be
# based on the folio assignments
root_candidates = defaultdict(Counter)

for i, fid in enumerate(folio_list):
    ch_idx = assignment[i]
    ch_name = chapter_list[ch_idx]
    ch_ingrs = chapter_ingrs[ch_name]

    # Roots in this folio
    for root in folio_roots[fid]:
        # This root could be any ingredient in this chapter
        for ingr in ch_ingrs:
            root_candidates[root][ingr] += 1

# For each root, what ingredient is most consistently assigned?
print(f'\n  Root→Ingredient (assigned in 5+ folios, dominant > 50%):')
print(f'  {"Root":>12s} {"BestIngr":>12s} {"Count":>6s} {"Total":>6s} {"Pct":>5s} {"Alternatives"}')
print('  ' + '-' * 70)

stable_mappings = []

for root, candidates in sorted(root_candidates.items(), key=lambda x: -sum(x[1].values())):
    total = sum(candidates.values())
    if total < 5:
        continue

    best_ingr, best_count = candidates.most_common(1)[0]
    pct = best_count * 100 // total

    if pct >= 40:
        alternatives = [(i, c) for i, c in candidates.most_common(3)[1:] if c > 1]
        alt_str = ', '.join(f'{i}({c})' for i, c in alternatives[:2])

        stable_mappings.append({
            'root': root,
            'ingredient': best_ingr,
            'count': best_count,
            'total': total,
            'pct': pct,
        })

        if pct >= 50 and total >= 8:
            print(f'  {root:>12s} {best_ingr:>12s} {best_count:>6d} {total:>6d} {pct:>4d}% {alt_str}')

print(f'\n  Stable mappings (>= 40%): {len(stable_mappings)}')


# ================================================================
# SAVE
# ================================================================
output = {
    'n_folios': N_FOLIOS,
    'n_chapters': N_CHAPTERS,
    'final_score': final_score,
    'n_fixed': len(fixed),
    'validation_accuracy': correct_top1 / max(tested, 1),
    'validation_tested': tested,
    'assignments': {folio_list[i]: chapter_list[assignment[i]] for i in range(N_FOLIOS)},
    'stable_mappings': stable_mappings[:50],
    'chapter_distribution': dict(ch_counts.most_common(20)),
}

with open(os.path.join(RESULTS, 'isomorphism_results.json'), 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f'\nSaved isomorphism_results.json')
