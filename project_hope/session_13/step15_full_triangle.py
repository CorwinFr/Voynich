"""
FULL TRIANGLE ATTACK — Use ALL 6 Sherwood↔Macer matches.

For each pair of folios/chapters:
  - What ingredients does the Macer say they SHARE?
  - What rare roots do the VMS folios SHARE?
  - By elimination: which root = which ingredient?

With 6 folios = 15 pairs = massive triangulation.
"""
import json, sys, io, os
from collections import Counter, defaultdict
from itertools import combinations

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

VMS_PATH = os.path.join(os.path.dirname(__file__), '..', 'vms', 'vms_structured.json')
MACER_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'attacks', 'RECIPE_DATASET', 'S05_MACER.json')
RESULTS = os.path.join(os.path.dirname(__file__), 'results')

with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)
with open(MACER_PATH, encoding='utf-8') as f:
    macer = json.load(f)

LOGOS = {'o','l','d','r','v','x','k','m','f','t','y','c','s','sh','p','ch','air','h'}

# ================================================================
# The 6 anchor pairs
# ================================================================
ANCHORS = {
    'f9v': 'Viola',
    'f29r': 'Lactuca',
    'f44v': 'Apium',
    'f48v': 'Ruta',
    'f51v': 'Salvia',
    'f95v': 'Althaea',  # f95v is actually f95v1 or f95v2
}

# Fix: f95v might be split
for fid_test in ['f95v', 'f95v1', 'f95v2']:
    if fid_test in vms['folios']:
        if 'f95v' in ANCHORS and fid_test != 'f95v':
            ANCHORS[fid_test] = ANCHORS.pop('f95v')
        break

# ================================================================
# Build root sets per folio
# ================================================================
def get_roots(fid):
    if fid not in vms['folios']: return Counter()
    folio = vms['folios'][fid]
    roots = Counter()
    for block in folio['blocks']:
        for line in block['lines']:
            for w in line['words']:
                eva = w['eva_primary']
                if eva in LOGOS: continue
                root = (w.get('morphology') or {}).get('root', '')
                if root and len(root) >= 2:
                    roots[root] += 1
    return roots

# Global root frequency
root_global = Counter()
for fid, folio in vms['folios'].items():
    for block in folio['blocks']:
        for line in block['lines']:
            for w in line['words']:
                eva = w['eva_primary']
                if eva in LOGOS: continue
                root = (w.get('morphology') or {}).get('root', '')
                if root and len(root) >= 2:
                    root_global[root] += 1

# Build Macer ingredient sets
macer_ingr = {}
for entry in macer['entries']:
    ingrs = set()
    for tok in entry['tokens']:
        if tok['type'] == 'INGR' and tok.get('ref'):
            ingrs.add(tok['ref'])
    macer_ingr[entry['name']] = ingrs

# Folio root sets
folio_roots = {fid: get_roots(fid) for fid in ANCHORS}

print(f'ANCHORS: {len(ANCHORS)} folio↔Macer pairs')
for fid, chapter in ANCHORS.items():
    n_roots = len(folio_roots.get(fid, {}))
    n_ingr = len(macer_ingr.get(chapter, set()))
    print(f'  {fid:8s} ↔ {chapter:15s} (VMS: {n_roots:3d} roots, Macer: {n_ingr:3d} ingredients)')

# ================================================================
# For EVERY pair of anchors, compute shared ingredients AND shared roots
# ================================================================
print(f'\n{"="*70}')
print('PAIRWISE ANALYSIS — 15 pairs')
print('=' * 70)

# Collect all evidence: root → set of possible ingredients
root_candidates = defaultdict(lambda: defaultdict(int))  # root → {ingredient: count}

for (fid1, chap1), (fid2, chap2) in combinations(ANCHORS.items(), 2):
    # Macer shared ingredients
    ingr1 = macer_ingr.get(chap1, set())
    ingr2 = macer_ingr.get(chap2, set())
    shared_ingr = ingr1 & ingr2

    # VMS shared roots (rare: global ≤ 50)
    roots1 = set(folio_roots.get(fid1, {}).keys())
    roots2 = set(folio_roots.get(fid2, {}).keys())
    shared_roots = roots1 & roots2
    rare_shared = {r for r in shared_roots if root_global[r] <= 50}

    # Exclusive shared: in these 2 folios but NOT in others of our 6
    other_roots = set()
    for fid3, _ in ANCHORS.items():
        if fid3 not in (fid1, fid2):
            other_roots.update(folio_roots.get(fid3, {}).keys())

    exclusive_shared = rare_shared - other_roots

    # Exclusive Macer ingredients
    other_ingr = set()
    for _, chap3 in ANCHORS.items():
        if chap3 not in (chap1, chap2):
            other_ingr.update(macer_ingr.get(chap3, set()))

    exclusive_ingr = shared_ingr - other_ingr

    if exclusive_shared and exclusive_ingr:
        print(f'\n  {fid1}({chap1}) + {fid2}({chap2})')
        print(f'    Shared ingredients: {len(shared_ingr)}, Exclusive: {len(exclusive_ingr)}')
        print(f'    Shared rare roots: {len(rare_shared)}, Exclusive: {len(exclusive_shared)}')

        if exclusive_ingr:
            print(f'    EXCLUSIVE ingredients: {sorted(exclusive_ingr)}')
        if exclusive_shared:
            print(f'    EXCLUSIVE roots: {sorted(exclusive_shared)[:10]}')

        if len(exclusive_ingr) == 1 and len(exclusive_shared) >= 1:
            ingr = list(exclusive_ingr)[0]
            print(f'    ★ SINGLE INGREDIENT: {ingr}')
            print(f'    ★ CANDIDATE ROOTS: {sorted(exclusive_shared)[:5]}')
            for r in exclusive_shared:
                root_candidates[r][ingr] += 1

        elif len(exclusive_shared) == 1 and len(exclusive_ingr) >= 1:
            root = list(exclusive_shared)[0]
            print(f'    ★ SINGLE ROOT: {root}')
            print(f'    ★ CANDIDATE INGREDIENTS: {sorted(exclusive_ingr)}')
            for ingr in exclusive_ingr:
                root_candidates[root][ingr] += 1

    # Also record non-exclusive but useful evidence
    for r in rare_shared:
        for ingr in shared_ingr:
            root_candidates[r][ingr] += 1

# ================================================================
# CONVERGENCE — which root→ingredient mappings are most constrained?
# ================================================================
print(f'\n{"="*70}')
print('CONVERGENCE — mappings les plus contraints')
print('=' * 70)

results = []
for root, candidates in root_candidates.items():
    total_evidence = sum(candidates.values())
    if total_evidence < 2: continue

    best_ingr = max(candidates, key=candidates.get)
    best_count = candidates[best_ingr]
    n_candidates = len(candidates)
    agreement = best_count / total_evidence

    results.append({
        'root': root,
        'best_ingr': best_ingr,
        'agreement': round(agreement, 2),
        'best_count': best_count,
        'total_evidence': total_evidence,
        'n_candidates': n_candidates,
        'all_candidates': dict(candidates),
        'global_freq': root_global[root],
    })

results.sort(key=lambda x: (-x['agreement'], -x['total_evidence']))

print(f'\n  {len(results)} roots with 2+ evidence points')
print(f'\n  {"Root":>12s} {"→ Ingredient":>25s} {"Agree":>6s} {"Evid":>5s} {"Cand":>5s} {"Global":>7s}')
print('  ' + '-' * 65)

for r in results[:30]:
    marker = '★' if r['agreement'] >= 0.5 and r['total_evidence'] >= 3 else ''
    print(f'  {r["root"]:>12s} → {r["best_ingr"]:>25s} {r["agreement"]:>5.0%} '
          f'{r["total_evidence"]:>5d} {r["n_candidates"]:>5d} {r["global_freq"]:>7d} {marker}')

    if r['n_candidates'] <= 3:
        for ingr, count in sorted(r['all_candidates'].items(), key=lambda x: -x[1]):
            print(f'    {"":>12s}   {ingr:>25s} ({count}x)')

# ================================================================
# STRONG CANDIDATES (agreement >= 50%, evidence >= 3)
# ================================================================
strong = [r for r in results if r['agreement'] >= 0.4 and r['total_evidence'] >= 3]

print(f'\n{"="*70}')
print(f'STRONG CANDIDATES ({len(strong)})')
print('=' * 70)

for r in strong:
    print(f'  {r["root"]:>12s} → {r["best_ingr"]:>20s} ({r["best_count"]}/{r["total_evidence"]} = {r["agreement"]:.0%})')

# Save
output = {
    'anchors': ANCHORS,
    'all_mappings': results,
    'strong_mappings': strong,
}
with open(os.path.join(RESULTS, 'full_triangle.json'), 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f'\nSaved full_triangle.json')
