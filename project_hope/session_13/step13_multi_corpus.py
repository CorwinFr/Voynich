"""
STEP 13 — Test VMS co-occurrence against ALL 15 corpora.

For each corpus: build co-occurrence graph, match with VMS,
run permutation test. Find which corpus the VMS resembles MOST.
"""
import json, sys, io, os, random
import numpy as np
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

VMS_PATH = os.path.join(os.path.dirname(__file__), '..', 'vms', 'vms_structured.json')
RECIPE_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'attacks', 'RECIPE_DATASET')
RESULTS = os.path.join(os.path.dirname(__file__), 'results')

with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)

LOGOS = {'o','l','d','r','v','x','k','m','f','t','y','c','s','sh','p','ch','air','h'}

# ================================================================
# Build VMS co-occurrence (once)
# ================================================================
print('Building VMS co-occurrence...')

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

vms_top = [c for c, _ in vms_freq.most_common(40)]
print(f'  VMS: {len(vms_recipes)} recipes, {len(vms_freq)} roots')

# ================================================================
# For each corpus: build graph, match, permutation test
# ================================================================

def build_corpus_graph(corpus_path):
    """Build co-occurrence graph for a Latin corpus."""
    with open(corpus_path, encoding='utf-8') as f:
        data = json.load(f)

    freq = Counter()
    recipes = []

    for entry in data.get('entries', []):
        ingrs = set()
        for tok in entry.get('tokens', []):
            if tok.get('type') == 'INGR' and tok.get('ref'):
                ingrs.add(tok['ref'])
                freq[tok['ref']] += 1
            elif tok.get('type') == 'INGR':
                name = tok.get('raw', '').lower()
                if len(name) >= 3:
                    ingrs.add(name)
                    freq[name] += 1
        if len(ingrs) >= 2:
            recipes.append(ingrs)

    cooc = defaultdict(Counter)
    for recipe in recipes:
        for a in recipe:
            for b in recipe:
                if a != b:
                    cooc[a][b] += 1

    top = [c for c, _ in freq.most_common(40)]
    return freq, recipes, cooc, top

def recipe_level_test(vms_recipes, vms_top, corpus_recipes, corpus_top, n_trials=1000):
    """Test: does rank-mapping produce better recipe Jaccard than random?"""
    # Build mapping: vms_top[i] → corpus_top[i]
    n = min(len(vms_top), len(corpus_top), 20)
    mapping = {vms_top[i]: corpus_top[i] for i in range(n)}

    # Our score: translate VMS recipes, find best Jaccard with corpus recipes
    our_scores = []
    rand_scores = []

    sample_vms = vms_recipes[:min(100, len(vms_recipes))]
    random.seed(42)

    for vms_recipe in sample_vms:
        translated = set()
        for root in vms_recipe:
            if root in mapping:
                translated.add(mapping[root])
        if len(translated) < 2: continue

        # Best Jaccard with any corpus recipe
        best = 0
        for corp_recipe in corpus_recipes[:200]:
            jacc = len(translated & corp_recipe) / max(len(translated | corp_recipe), 1)
            best = max(best, jacc)
        our_scores.append(best)

        # Random: shuffle the mapping
        rand_mapping = dict(zip(vms_top[:n], random.sample(corpus_top[:30], min(n, 30))))
        rand_translated = set()
        for root in vms_recipe:
            if root in rand_mapping:
                rand_translated.add(rand_mapping[root])
        if len(rand_translated) < 2:
            rand_scores.append(0)
            continue

        best_rand = 0
        for corp_recipe in corpus_recipes[:200]:
            jacc = len(rand_translated & corp_recipe) / max(len(rand_translated | corp_recipe), 1)
            best_rand = max(best_rand, jacc)
        rand_scores.append(best_rand)

    our_mean = np.mean(our_scores) if our_scores else 0
    rand_mean = np.mean(rand_scores) if rand_scores else 0
    improvement = our_mean / max(rand_mean, 0.001)

    return our_mean, rand_mean, improvement

# ================================================================
# Test each corpus
# ================================================================
print(f'\n{"="*70}')
print('TESTING VMS AGAINST ALL CORPORA')
print('=' * 70)

results = []

for fname in sorted(os.listdir(RECIPE_DIR)):
    if not fname.startswith('S') or not fname.endswith('.json'): continue

    fpath = os.path.join(RECIPE_DIR, fname)
    try:
        freq, recipes, cooc, top = build_corpus_graph(fpath)
    except Exception as e:
        print(f'  {fname}: ERROR {e}')
        continue

    if len(recipes) < 5 or len(top) < 10:
        print(f'  {fname}: too small ({len(recipes)} recipes, {len(top)} ingr)')
        continue

    our_jacc, rand_jacc, improvement = recipe_level_test(
        vms_recipes, vms_top, recipes, top)

    status = '★' if improvement > 1.5 else '✓' if improvement > 1.2 else '·'

    print(f'  {status} {fname:25s}: {len(recipes):5d} recipes, {len(top):3d} ingr | '
          f'our={our_jacc:.4f} rand={rand_jacc:.4f} improve={improvement:.2f}x')

    results.append({
        'corpus': fname,
        'n_recipes': len(recipes),
        'n_ingredients': len(freq),
        'our_jaccard': round(our_jacc, 4),
        'random_jaccard': round(rand_jacc, 4),
        'improvement': round(improvement, 2),
    })

# Sort by improvement
results.sort(key=lambda x: -x['improvement'])

print(f'\n{"="*70}')
print('CLASSEMENT — quel corpus le VMS ressemble-t-il le PLUS?')
print('=' * 70)

for i, r in enumerate(results):
    status = '★★★' if r['improvement'] > 2.0 else '★★' if r['improvement'] > 1.5 else '★' if r['improvement'] > 1.2 else ''
    print(f'  #{i+1} {r["corpus"]:25s} improve={r["improvement"]:5.2f}x '
          f'({r["our_jaccard"]:.4f} vs {r["random_jaccard"]:.4f}) '
          f'{r["n_recipes"]} rec, {r["n_ingredients"]} ingr {status}')

with open(os.path.join(RESULTS, 'multi_corpus_test.json'), 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print('\nSaved multi_corpus_test.json')
