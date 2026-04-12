"""
SESSION 17 — EM GLOBAL OPTIMIZATION

Expectation-Maximization to jointly solve:
  1. Which plant is each herbal folio?
  2. Which ingredient is each VMS root?

Uses ALL corpora to build a mega plant×ingredient matrix.
Fixes confirmed mappings. Iterates until convergence.

E-step: Given root→ingredient, find best plant for each folio
M-step: Given folio→plant, find best ingredient for each root
"""
import json, sys, io, os, re
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.dirname(__file__)
VMS_PATH = os.path.join(BASE, '..', 'vms', 'vms_structured.json')
REG_PATH = os.path.join(BASE, '..', 'hypothesis_registry.json')
RECIPE_DIR = os.path.join(BASE, '..', '..', 'attacks', 'RECIPE_DATASET')
RESULTS = BASE

with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)
with open(REG_PATH, encoding='utf-8') as f:
    registry = json.load(f)

LOGOS = {'o','l','d','r','v','x','k','m','f','t','y','c','s','sh','p','ch','air','h'}
FUNCTIONAL = set(registry.get('functional_words', {}).keys())
NOISE = {'ke', 'ko', 'po', 'do'}

# ================================================================
# STEP 1: Build MEGA plant×ingredient matrix from ALL corpora
# ================================================================
print('='*70)
print('STEP 1 — Build mega plant×ingredient matrix')
print('='*70)

corpus_files = [
    ('S05_MACER.json', 'name'),
    ('S08_AVICENNA.json', 'name'),
    ('S09_COLLECTIO.json', 'title'),
    ('S10_ALPHITA.json', 'name'),
    ('S11_BALNEA.json', 'name'),
    ('S12_TACUINUM.json', 'name'),
    ('S15_ABENGUEFIT.json', 'name'),
    ('S16_RHAZES.json', 'name'),
]

# Normalize plant names to simple form
def normalize_plant(name):
    """Extract the core plant name from a corpus entry title."""
    name = name.lower().strip()
    # Remove common prefixes
    for prefix in ['de ', 'ad ', 'contra ', 'pro ', 'capitulum ']:
        if name.startswith(prefix):
            name = name[len(prefix):]
    # Take first word if it's a known plant-like word
    words = name.split()
    if words:
        first = words[0].strip('.,;:()')
        if len(first) >= 4 and first.isalpha():
            return first
    return name[:20]

# Build matrix
plant_ingredients = defaultdict(Counter)  # plant → {ingredient: count}
all_ingredients = set()

for corpus_file, name_field in corpus_files:
    path = os.path.join(RECIPE_DIR, corpus_file)
    if not os.path.exists(path):
        continue

    with open(path, encoding='utf-8') as f:
        data = json.load(f)

    for entry in data.get('entries', []):
        raw_name = entry.get(name_field, entry.get('name', entry.get('title', '')))
        plant = normalize_plant(raw_name)
        if not plant or len(plant) < 3:
            continue

        for tok in entry.get('tokens', []):
            if tok.get('type') == 'INGR':
                ref = tok.get('ref', tok.get('raw', '')).lower().strip('.,;: ').replace('i_', '')
                if len(ref) >= 3:
                    plant_ingredients[plant][ref] += 1
                    all_ingredients.add(ref)

# Filter: keep plants with 3+ ingredients
plant_matrix = {}
for plant, ingrs in plant_ingredients.items():
    if len(ingrs) >= 3:
        plant_matrix[plant] = set(ingrs.keys())

print(f'  Plants with 3+ ingredients: {len(plant_matrix)}')
print(f'  Total unique ingredients: {len(all_ingredients)}')

# Top 20 plants by ingredient count
top_plants = sorted(plant_matrix.items(), key=lambda x: -len(x[1]))[:20]
print(f'\n  Top 20 plants:')
for p, ingrs in top_plants:
    print(f'    {p:>20s}: {len(ingrs)} ingredients')


# ================================================================
# STEP 2: Build VMS folio×root matrix
# ================================================================
print(f'\n{"="*70}')
print('STEP 2 — Build VMS folio×root matrix')
print('='*70)

# Only use roots that are: non-functional, non-noise, non-logo, >= 3 chars
folio_roots = {}  # fid → set of roots

for fid, folio in vms['folios'].items():
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
                if not root or len(root) < 3:
                    continue
                if root in FUNCTIONAL or root in NOISE:
                    continue
                roots.add(root)

    if roots:
        folio_roots[fid] = roots

# All unique candidate roots
all_roots = set()
for roots in folio_roots.values():
    all_roots.update(roots)

print(f'  Herbal folios with roots: {len(folio_roots)}')
print(f'  Total unique candidate roots: {len(all_roots)}')


# ================================================================
# STEP 3: Fixed constraints (confirmed mappings)
# ================================================================
CONFIRMED = {}
REAL_SHORT = {'chk', 'cht', 'yk', 'dsh'}
for root, data in registry['confirmed_ingredients'].items():
    if len(root) >= 3 or root in REAL_SHORT:
        CONFIRMED[root] = data['latin']
CONFIRMED['ypch'] = 'aqua'
CONFIRMED['ykeed'] = 'nitrum'
CONFIRMED['seees'] = 'lens'
CONFIRMED['kald'] = 'ovum'
CONFIRMED['otoly'] = 'sal'

# Sherwood (fixed folio→plant where known)
SHERWOOD = {
    'f48v':'ruta','f9v':'viola','f44v':'apium','f51v':'salvia',
    'f29r':'lactuca','f41r':'origanum','f37r':'mentha',
    'f41v':'coriandrum','f22r':'verbena','f28r':'aristolochia',
    'f5v':'malva','f45r':'atriplex','f66v':'satureia',
    'f65v':'centaurea','f3v':'elleborus','f95v1':'althaea',
}

print(f'  Confirmed root→ingredient: {len(CONFIRMED)}')
print(f'  Fixed folio→plant (Sherwood): {len(SHERWOOD)}')


# ================================================================
# STEP 4: EM OPTIMIZATION
# ================================================================
print(f'\n{"="*70}')
print('STEP 4 — EM OPTIMIZATION')
print('='*70)

# Initialize:
# - root→ingredient: start with confirmed, rest = None
# - folio→plant: start with Sherwood, rest = None

root_to_ingr = dict(CONFIRMED)  # current mapping
folio_to_plant = dict(SHERWOOD)  # current assignment

# Helper: compute score of folio F being plant P given current root mappings
def score_folio_plant(fid, plant_name):
    if plant_name not in plant_matrix:
        return -1
    plant_ingrs = plant_matrix[plant_name]
    folio_root_set = folio_roots.get(fid, set())

    score = 0
    for root in folio_root_set:
        if root in root_to_ingr:
            ingr = root_to_ingr[root]
            if ingr in plant_ingrs:
                score += 1  # ingredient matches plant
            else:
                score -= 0.5  # mismatch penalty
    return score

# Helper: compute score of root R being ingredient I given current folio assignments
def score_root_ingr(root, ingr):
    score = 0
    for fid, roots in folio_roots.items():
        if root not in roots:
            continue
        plant = folio_to_plant.get(fid)
        if not plant or plant not in plant_matrix:
            continue
        plant_ingrs = plant_matrix[plant]
        if ingr in plant_ingrs:
            score += 1
        else:
            score -= 0.5
    return score

N_ITERATIONS = 8
plants_list = list(plant_matrix.keys())
ingredients_list = sorted(all_ingredients)

for iteration in range(N_ITERATIONS):
    changes = 0

    # E-STEP: For each unassigned folio, find best plant
    for fid in folio_roots:
        if fid in SHERWOOD:
            continue  # fixed

        best_plant = None
        best_score = -999
        for plant in plants_list:
            s = score_folio_plant(fid, plant)
            if s > best_score:
                best_score = s
                best_plant = plant

        if best_plant and best_plant != folio_to_plant.get(fid):
            folio_to_plant[fid] = best_plant
            changes += 1

    # M-STEP: For each unassigned root, find best ingredient
    for root in sorted(all_roots):
        if root in CONFIRMED:
            continue  # fixed

        # Only consider roots that appear in 2+ assigned folios
        n_assigned = sum(1 for fid in folio_roots if root in folio_roots[fid] and fid in folio_to_plant)
        if n_assigned < 2:
            continue

        best_ingr = None
        best_score = 0  # threshold: must be positive
        for ingr in ingredients_list:
            s = score_root_ingr(root, ingr)
            if s > best_score:
                best_score = s
                best_ingr = ingr

        if best_ingr and best_ingr != root_to_ingr.get(root):
            root_to_ingr[root] = best_ingr
            changes += 1

    # Compute global score
    total_score = 0
    for fid in folio_roots:
        plant = folio_to_plant.get(fid)
        if plant:
            total_score += score_folio_plant(fid, plant)

    n_mapped_roots = len([r for r in root_to_ingr if r not in CONFIRMED])
    n_mapped_folios = len([f for f in folio_to_plant if f not in SHERWOOD])

    print(f'  Iter {iteration+1}: changes={changes}  '
          f'global_score={total_score:.0f}  '
          f'mapped_roots={n_mapped_roots}  mapped_folios={n_mapped_folios}')

    if changes == 0:
        print(f'  CONVERGED at iteration {iteration+1}')
        break


# ================================================================
# STEP 5: RESULTS
# ================================================================
print(f'\n{"="*70}')
print('RESULTS — NEW ROOT MAPPINGS')
print('='*70)

new_mappings = {}
for root, ingr in sorted(root_to_ingr.items()):
    if root in CONFIRMED:
        continue
    # Count evidence
    n_folios = sum(1 for fid in folio_roots if root in folio_roots[fid])
    n_consistent = 0
    for fid in folio_roots:
        if root not in folio_roots[fid]:
            continue
        plant = folio_to_plant.get(fid)
        if plant and plant in plant_matrix:
            if ingr in plant_matrix[plant]:
                n_consistent += 1

    confidence = n_consistent / max(n_folios, 1)
    new_mappings[root] = {
        'ingredient': ingr,
        'n_folios': n_folios,
        'n_consistent': n_consistent,
        'confidence': round(confidence, 2),
    }

# Sort by confidence × frequency
ranked = sorted(new_mappings.items(),
                key=lambda x: (-x[1]['confidence'], -x[1]['n_consistent']))

print(f'\n  {"Root":>12s} {"Ingredient":>15s} {"Folios":>7s} {"Consist":>8s} {"Conf":>5s}')
print('  ' + '-' * 55)
for root, data in ranked[:40]:
    if data['confidence'] >= 0.5:
        print(f'  {root:>12s} {data["ingredient"]:>15s} {data["n_folios"]:>7d} '
              f'{data["n_consistent"]:>8d} {data["confidence"]:>5.2f}')


# ================================================================
# STEP 6: VALIDATION — folio→plant assignments
# ================================================================
print(f'\n{"="*70}')
print('VALIDATION — Folio→Plant assignments')
print('='*70)

SHERWOOD_ALL = {
    'f48v':'ruta','f9v':'viola','f44v':'apium','f51v':'salvia',
    'f29r':'lactuca','f41r':'origanum','f37r':'mentha',
    'f41v':'coriandrum','f22r':'verbena','f28r':'aristolochia',
    'f5v':'malva','f45r':'atriplex','f66v':'satureia',
    'f65v':'centaurea','f3v':'elleborus','f95v1':'althaea',
    'f11r':'rosmarinus','f16r':'cannabis','f39r':'crocus',
    'f44r':'mandragora','f50v':'gentiana','f29v':'nigella',
}

correct = 0
tested = 0
for fid, true_plant in SHERWOOD_ALL.items():
    if fid in SHERWOOD:
        continue  # was fixed, not a test
    predicted = folio_to_plant.get(fid, '?')
    tested += 1
    match = true_plant[:4] in predicted or predicted[:4] in true_plant
    if match:
        correct += 1
        status = '✓'
    else:
        status = '✗'
    print(f'  {status} {fid:>8s} true={true_plant:>15s}  pred={predicted:>15s}')

if tested:
    print(f'\n  Accuracy (unfixed Sherwood): {correct}/{tested} ({correct*100//tested}%)')

# Show top new assignments
print(f'\n  NEW FOLIO ASSIGNMENTS (not in Sherwood):')
for fid in sorted(folio_to_plant.keys()):
    if fid in SHERWOOD_ALL:
        continue
    plant = folio_to_plant[fid]
    score = score_folio_plant(fid, plant)
    if score >= 3:
        print(f'    {fid:>8s} → {plant:>15s}  score={score:.1f}')


# Save
output = {
    'n_iterations': iteration + 1,
    'global_score': total_score,
    'n_new_root_mappings': len(new_mappings),
    'n_folio_assignments': len(folio_to_plant) - len(SHERWOOD),
    'top_root_mappings': [{
        'root': r,
        'ingredient': d['ingredient'],
        'confidence': d['confidence'],
        'n_folios': d['n_folios'],
    } for r, d in ranked[:30] if d['confidence'] >= 0.4],
    'folio_assignments': {fid: plant for fid, plant in folio_to_plant.items()
                          if fid not in SHERWOOD},
}

with open(os.path.join(RESULTS, 'attack_em_results.json'), 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f'\nSaved attack_em_results.json')
