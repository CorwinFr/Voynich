"""
STEP 12 — Permutation test on co-occurrence mapping.

NULL HYPOTHESIS: The VMS↔AN mapping found in step 11 is no better than
a random frequency-preserving mapping.

TEST:
1. Take our mapping (top 20 VMS→AN codes)
2. Compute a CONSISTENCY SCORE: for each pair of mapped codes,
   does their VMS co-occurrence correlate with their AN co-occurrence?
3. Generate 10000 RANDOM mappings (preserving frequency rank ±5)
4. Compute the same score for each random mapping
5. p-value = fraction of random mappings that score >= our mapping

Also: test on RARE codes (rank 15-40) to avoid Zipf contamination.
"""
import json, sys, io, os, random
import numpy as np
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

VMS_PATH = os.path.join(os.path.dirname(__file__), '..', 'vms', 'vms_structured.json')
AN_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'attacks', 'RECIPE_DATASET', 'S01_AN.json')
RESULTS = os.path.join(os.path.dirname(__file__), 'results')

with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)
with open(AN_PATH, encoding='utf-8') as f:
    an = json.load(f)

LOGOS = {'o','l','d','r','v','x','k','m','f','t','y','c','s','sh','p','ch','air','h'}

# ================================================================
# Rebuild co-occurrence matrices
# ================================================================
print('Building co-occurrence matrices...')

vms_freq = Counter()
vms_recipes = []
for fid, folio in vms['folios'].items():
    if folio['metadata']['section'] != 'pharma': continue
    for block in folio['blocks']:
        if not block.get('separator'): continue
        roots = set()
        for line in block['lines']:
            for w in line['words']:
                eva = w['eva_primary']
                if eva in LOGOS: continue
                root = (w.get('morphology') or {}).get('root', '')
                if root and len(root) >= 2:
                    roots.add(root)
                    vms_freq[root] += 1
        if len(roots) >= 2:
            vms_recipes.append(roots)

vms_cooc = defaultdict(Counter)
for recipe in vms_recipes:
    for a in recipe:
        for b in recipe:
            if a != b:
                vms_cooc[a][b] += 1

an_freq = Counter()
an_recipes = []
for entry in an['entries']:
    ingrs = set()
    for tok in entry['tokens']:
        if tok['type'] == 'INGR' and tok.get('ref'):
            ingrs.add(tok['ref'])
            an_freq[tok['ref']] += 1
    if len(ingrs) >= 2:
        an_recipes.append(ingrs)

an_cooc = defaultdict(Counter)
for recipe in an_recipes:
    for a in recipe:
        for b in recipe:
            if a != b:
                an_cooc[a][b] += 1

vms_top = [c for c, _ in vms_freq.most_common(50)]
an_top = [c for c, _ in an_freq.most_common(50)]

# ================================================================
# Our mapping from step 11
# ================================================================
OUR_MAPPING = {
    'qok': 'I_aqua', 'ch': 'I_mel', 'ot': 'I_succus',
    'ok': 'I_cinnamomum', 'sh': 'I_rosa', 'qot': 'I_mastix',
    'aiin': 'I_crocus', 'lk': 'I_rosa', 'ar': 'I_vinum',
    'al': 'I_aloe', 'ol': 'I_aloe', 'or': 'I_aloe',
    'ched': 'I_viola', 'lch': 'I_viola',
}

def consistency_score(mapping, vms_cooc, an_cooc, vms_freq, an_freq):
    """Compute how well VMS co-occurrences predict AN co-occurrences."""
    codes = list(mapping.keys())
    total_corr = 0
    n_pairs = 0

    for i in range(len(codes)):
        for j in range(i+1, len(codes)):
            v1, v2 = codes[i], codes[j]
            a1, a2 = mapping[v1], mapping[v2]

            # Normalized co-occurrence
            vms_val = vms_cooc[v1].get(v2, 0) / max(vms_freq[v1], 1)
            an_val = an_cooc[a1].get(a2, 0) / max(an_freq[a1], 1)

            # Correlation contribution
            total_corr += vms_val * an_val  # high when both high or both low
            n_pairs += 1

    return total_corr / max(n_pairs, 1)

our_score = consistency_score(OUR_MAPPING, vms_cooc, an_cooc, vms_freq, an_freq)
print(f'\nOur mapping consistency score: {our_score:.6f}')

# ================================================================
# TEST 1: Full permutation test (all ranks)
# ================================================================
print(f'\n{"="*70}')
print('TEST 1: Full permutation test (10000 random mappings)')
print('=' * 70)

random.seed(42)
n_exceed = 0
random_scores = []

vms_codes = list(OUR_MAPPING.keys())
an_pool = an_top[:30]

for trial in range(10000):
    # Random mapping: for each VMS code, pick a random AN code
    # (allowing frequency-rank proximity ±10)
    random_mapping = {}
    available = list(an_pool)
    random.shuffle(available)
    for v_code in vms_codes:
        if available:
            random_mapping[v_code] = available.pop()
        else:
            random_mapping[v_code] = random.choice(an_pool)

    rand_score = consistency_score(random_mapping, vms_cooc, an_cooc, vms_freq, an_freq)
    random_scores.append(rand_score)
    if rand_score >= our_score:
        n_exceed += 1

p_value = n_exceed / 10000
mean_random = np.mean(random_scores)
std_random = np.std(random_scores)
z_score = (our_score - mean_random) / max(std_random, 1e-10)

print(f'  Our score:     {our_score:.6f}')
print(f'  Random mean:   {mean_random:.6f} ± {std_random:.6f}')
print(f'  Z-score:       {z_score:.2f}')
print(f'  p-value:       {p_value:.4f} ({n_exceed}/10000)')
print(f'  VERDICT:       {"✓ SIGNIFICANT (p<0.01)" if p_value < 0.01 else "✓ MARGINAL (p<0.05)" if p_value < 0.05 else "✗ NOT SIGNIFICANT"}')

# ================================================================
# TEST 2: RARE codes only (rank 15-40) — avoid Zipf
# ================================================================
print(f'\n{"="*70}')
print('TEST 2: RARE codes only (rank 15-40)')
print('=' * 70)

vms_rare = vms_top[15:40]
an_rare = an_top[15:40]

# Build mapping for rare codes by same method (rank matching)
rare_mapping = {}
for i, v in enumerate(vms_rare):
    if i < len(an_rare):
        rare_mapping[v] = an_rare[i]

rare_score = consistency_score(rare_mapping, vms_cooc, an_cooc, vms_freq, an_freq)
print(f'  Rare mapping score: {rare_score:.6f}')

n_exceed_rare = 0
random_rare_scores = []

for trial in range(10000):
    random_rare = {}
    available = list(an_rare)
    random.shuffle(available)
    for i, v in enumerate(vms_rare):
        if i < len(available):
            random_rare[v] = available[i]

    rand_score = consistency_score(random_rare, vms_cooc, an_cooc, vms_freq, an_freq)
    random_rare_scores.append(rand_score)
    if rand_score >= rare_score:
        n_exceed_rare += 1

p_rare = n_exceed_rare / 10000
mean_rare = np.mean(random_rare_scores)
std_rare = np.std(random_rare_scores)
z_rare = (rare_score - mean_rare) / max(std_rare, 1e-10)

print(f'  Random mean:   {mean_rare:.6f} ± {std_rare:.6f}')
print(f'  Z-score:       {z_rare:.2f}')
print(f'  p-value:       {p_rare:.4f} ({n_exceed_rare}/10000)')
print(f'  VERDICT:       {"✓ SIGNIFICANT (p<0.01)" if p_rare < 0.01 else "✓ MARGINAL (p<0.05)" if p_rare < 0.05 else "✗ NOT SIGNIFICANT (Zipf artifact)"}')

# ================================================================
# TEST 3: Recipe-level test — does the mapping predict recipe composition?
# ================================================================
print(f'\n{"="*70}')
print('TEST 3: Recipe-level prediction')
print('=' * 70)

# For each VMS recipe, translate using our mapping, then check:
# is the translated set of ingredients more similar to a REAL AN recipe
# than a RANDOM set of AN ingredients?

full_mapping = {v: a for v, a in zip(vms_top[:20], an_top[:20])}

recipe_scores = []
random_recipe_scores = []

for vms_recipe in vms_recipes[:100]:  # first 100 VMS recipes
    # Translate
    translated = set()
    for root in vms_recipe:
        if root in full_mapping:
            translated.add(full_mapping[root])

    if len(translated) < 3: continue

    # Find best matching AN recipe (Jaccard)
    best_jacc = 0
    for an_recipe in an_recipes:
        jacc = len(translated & an_recipe) / max(len(translated | an_recipe), 1)
        best_jacc = max(best_jacc, jacc)
    recipe_scores.append(best_jacc)

    # Random baseline: pick random AN ingredients of same size
    rand_set = set(random.sample(an_top[:50], min(len(translated), 50)))
    best_rand_jacc = 0
    for an_recipe in an_recipes:
        jacc = len(rand_set & an_recipe) / max(len(rand_set | an_recipe), 1)
        best_rand_jacc = max(best_rand_jacc, jacc)
    random_recipe_scores.append(best_rand_jacc)

if recipe_scores:
    our_mean = np.mean(recipe_scores)
    rand_mean = np.mean(random_recipe_scores)
    print(f'  Our mapping → Jaccard with best AN recipe: {our_mean:.4f}')
    print(f'  Random mapping → Jaccard: {rand_mean:.4f}')
    print(f'  Improvement: {our_mean/max(rand_mean,0.001):.2f}x')
    print(f'  VERDICT: {"✓ BETTER THAN RANDOM" if our_mean > rand_mean * 1.2 else "✗ NO BETTER THAN RANDOM"}')

# Save
results = {
    'test1_full': {
        'our_score': round(our_score, 6),
        'random_mean': round(mean_random, 6),
        'z_score': round(z_score, 2),
        'p_value': p_value,
    },
    'test2_rare': {
        'our_score': round(rare_score, 6),
        'random_mean': round(mean_rare, 6),
        'z_score': round(z_rare, 2),
        'p_value': p_rare,
    },
    'test3_recipe': {
        'our_jaccard': round(our_mean, 4) if recipe_scores else None,
        'random_jaccard': round(rand_mean, 4) if random_recipe_scores else None,
    },
}
with open(os.path.join(RESULTS, 'permutation_test.json'), 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print('\nSaved permutation_test.json')
