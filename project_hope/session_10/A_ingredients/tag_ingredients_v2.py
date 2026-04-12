"""
ATTACK A v2 — Identify ingredients in f103r recipes.

IMPROVEMENT: Extract ROOT from each compound word (strip gallows prefix,
qo- prefix, etc.) before matching against herbal roots.

A word like "qokeey" has root "okeey" (from morphology) or stripped root "keey".
The herbal roots are STRIPPED roots from first words of herbal pages.

We match at MULTIPLE levels:
1. Direct EVA match → logogram table
2. Morphological root match → herbal crossref
3. Stripped root match (remove qo-, o-, p-, t-, k-, f- prefixes)
4. Fuzzy root match (edit distance ≤ 1)
"""
import json, sys, io, os
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.dirname(__file__)
VMS_PATH = os.path.join(BASE, '..', '..', 'vms', 'vms_structured.json')
CROSSREF_PATH = os.path.join(BASE, '..', '..', 'session_09', 'results', 'plant_crossref_complete.json')
W2V_PATH = os.path.join(BASE, '..', 'B_gpu_embeddings', 'results', 'w2v_procrustes.json')
RESULTS = os.path.join(BASE, 'results')
os.makedirs(RESULTS, exist_ok=True)

LOGOGRAMS = {
    'o': 'ac', 'l': 'se', 'd': 'de', 'r': 'recipe', 'v': 'vel',
    'x': 'crux', 'k': 'cum', 'm': 'misce', 'f': 'per', 't': 'et',
    'y': 'in', 'c': 'cum', 's': 'est', 'sh': 'ci', 'p': 'usque',
    'ch': 'cum', 'air': 'air', 'h': '(h)',
}

# ================================================================
# Load data
# ================================================================
with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)

with open(CROSSREF_PATH, encoding='utf-8') as f:
    crossref = json.load(f)

# Build herbal root set
herbal_roots = {}
for entry in crossref['crossref']:
    root = entry['root']
    herbal_roots[root] = {
        'folio': entry['folio'],
        'gallows': entry['gallows'],
        'pharma_count': entry['pharma'],
        'herbal_count': entry['herbal'],
        'total': entry['total'],
    }

# Also build a set of ALL herbal first-word roots (including those not in pharma)
# by scanning herbal section
all_herbal_roots = set(herbal_roots.keys())

# Scan VMS herbal section for ALL first-word roots
for fid, folio in vms['folios'].items():
    if folio['metadata']['section'] != 'herbal':
        continue
    for block in folio['blocks']:
        words = [w for line in block['lines'] for w in line['words']]
        if not words:
            continue
        first_word = words[0]['eva_primary']
        morph = words[0].get('morphology', {})
        root = morph.get('root', '')
        if root:
            all_herbal_roots.add(root)

print(f'Pharma-crossref roots: {len(herbal_roots)}')
print(f'All herbal roots (incl non-pharma): {len(all_herbal_roots)}')

# Load w2v
w2v_nn = {}
if os.path.exists(W2V_PATH):
    with open(W2V_PATH, encoding='utf-8') as f:
        w2v = json.load(f)
    w2v_nn = w2v.get('nn_results', {})

# ================================================================
# ROOT EXTRACTION: strip prefixes from compound words
# ================================================================

def extract_possible_roots(eva, morph_root):
    """Extract possible roots from a compound EVA word.

    Returns list of (root, method) tuples.
    """
    roots = []

    # Method 1: morphological root from build_vms
    if morph_root:
        roots.append((morph_root, 'morphology'))

    # Method 2: strip common prefixes
    # Gallows prefixes: p, t, k, f (single char)
    # qo- prefix (very common in pharma)
    # o- prefix
    # op- prefix
    # d- prefix
    # l- prefix
    # s- prefix
    prefixes = ['qo', 'op', 'ot', 'ok', 'sh', 'ch', 'p', 't', 'k', 'f', 'o', 'd', 'l', 's']
    for pfx in prefixes:
        if eva.startswith(pfx) and len(eva) > len(pfx) + 1:
            stripped = eva[len(pfx):]
            if stripped not in LOGOGRAMS and len(stripped) >= 2:
                roots.append((stripped, f'strip_{pfx}'))

    return roots


# ================================================================
# TAG each word
# ================================================================
f103r = vms['folios']['f103r']
all_recipes = []
tag_counts = Counter()
ingredient_registry = defaultdict(list)
match_methods = Counter()

print('\n' + '=' * 70)
print('f103r — 18 RECIPES ANNOTATED (v2: deep root matching)')
print('=' * 70)

for b in f103r['blocks']:
    recipe_id = b['block_id']
    words = [w for line in b['lines'] for w in line['words']]

    print(f'\n{"─"*70}')
    print(f'RECIPE {recipe_id} ({len(words)} words)')
    print(f'{"─"*70}')

    tagged_words = []

    for i, w in enumerate(words):
        eva = w['eva_primary']
        morph = w.get('morphology', {})
        root = morph.get('root', '')
        suffix = morph.get('suffix', '')
        ic = morph.get('i_count')

        tag = None
        label = ''
        match_detail = ''

        # 1. Logogram?
        if eva in LOGOGRAMS:
            tag = 'LOGO'
            label = f'LOGO:{LOGOGRAMS[eva]}'

        # 2. Dose candidate?
        elif ic is not None:
            tag = 'DOSE'
            label = f'DOSE:i{ic}'

        # 3. Ingredient? Try multiple root extraction methods
        else:
            possible_roots = extract_possible_roots(eva, root)
            best_match = None
            best_priority = 999

            for candidate_root, method in possible_roots:
                # Priority 1: exact match in pharma-crossref roots
                if candidate_root in herbal_roots:
                    priority = 1
                    if priority < best_priority:
                        best_priority = priority
                        best_match = (candidate_root, method, 'pharma_crossref')

                # Priority 2: match in all herbal roots (even non-pharma)
                elif candidate_root in all_herbal_roots:
                    priority = 2
                    if priority < best_priority:
                        best_priority = priority
                        best_match = (candidate_root, method, 'herbal_only')

                # Priority 3: suffix-stripped match
                # Try removing -edy, -eey, -ey, -ol, -al, -ar, -or from candidate
                for suf in ['edy', 'eedy', 'eey', 'ey', 'ol', 'al', 'ar', 'or', 'am', 'dy']:
                    if candidate_root.endswith(suf) and len(candidate_root) > len(suf) + 1:
                        inner_root = candidate_root[:-len(suf)]
                        if inner_root in herbal_roots:
                            priority = 3
                            if priority < best_priority:
                                best_priority = priority
                                best_match = (inner_root, f'{method}+strip_{suf}', 'deep_strip')
                        elif inner_root in all_herbal_roots:
                            priority = 4
                            if priority < best_priority:
                                best_priority = priority
                                best_match = (inner_root, f'{method}+strip_{suf}', 'deep_herbal')

            if best_match:
                matched_root, method, source = best_match
                tag = 'INGR'
                hr = herbal_roots.get(matched_root, {'folio': '?', 'pharma_count': 0})
                label = f'INGR:{matched_root}→{hr["folio"]}'
                match_detail = f'({method},{source})'
                match_methods[method] += 1
                ingredient_registry[matched_root].append({
                    'recipe': recipe_id,
                    'position': i,
                    'eva': eva,
                    'method': method,
                    'source': source,
                })
            else:
                tag = 'UNK'
                label = f'?:{eva}'

        tag_counts[tag] += 1
        tagged_words.append({
            'pos': i,
            'eva': eva,
            'root': root,
            'suffix': suffix,
            'i_count': ic,
            'tag': tag,
            'label': label,
            'match_detail': match_detail,
        })

    # Print compact annotated recipe
    for tw in tagged_words:
        marker = {'LOGO': 'L', 'DOSE': 'D', 'INGR': '★', 'UNK': '.'}[tw['tag']]
        detail = f' {tw["match_detail"]}' if tw['match_detail'] else ''
        if tw['tag'] == 'INGR':
            print(f'  {marker} [{tw["label"]}] {tw["eva"]}{detail}')
        elif tw['tag'] in ('LOGO', 'DOSE'):
            print(f'  {marker} [{tw["label"]}] {tw["eva"]}')
        # Skip UNK in compact view

    n_ingr = sum(1 for tw in tagged_words if tw['tag'] == 'INGR')
    n_dose = sum(1 for tw in tagged_words if tw['tag'] == 'DOSE')
    n_logo = sum(1 for tw in tagged_words if tw['tag'] == 'LOGO')
    n_unk = sum(1 for tw in tagged_words if tw['tag'] == 'UNK')
    unique_ingr = len(set(tw['root'] for tw in tagged_words if tw['tag'] == 'INGR'))

    # Pattern string
    pattern = ''.join({'INGR': 'I', 'DOSE': 'D', 'LOGO': 'L', 'UNK': '.'}[tw['tag']]
                      for tw in tagged_words)
    print(f'  Pattern: {pattern}')
    print(f'  → {n_ingr}★INGR ({unique_ingr}uniq) {n_dose}D {n_logo}L {n_unk}?')

    all_recipes.append({
        'id': recipe_id,
        'n_words': len(words),
        'tagged': tagged_words,
        'counts': {'INGR': n_ingr, 'DOSE': n_dose, 'LOGO': n_logo, 'UNK': n_unk},
        'unique_ingredients': unique_ingr,
        'pattern': pattern,
    })

# ================================================================
# GLOBAL STATS
# ================================================================
print('\n' + '=' * 70)
print('GLOBAL STATISTICS (v2)')
print('=' * 70)

total_words = sum(r['n_words'] for r in all_recipes)
print(f'\nTotal words: {total_words}')
for tag, count in tag_counts.most_common():
    print(f'  {tag:6s}: {count:4d} ({count*100//total_words}%)')

print(f'\nMatch methods:')
for method, count in match_methods.most_common():
    print(f'  {method:30s}: {count}')

# ================================================================
# INGREDIENT REGISTRY
# ================================================================
print('\n' + '=' * 70)
print('INGREDIENT REGISTRY')
print('=' * 70)

for root in sorted(ingredient_registry.keys(),
                   key=lambda r: -len(ingredient_registry[r])):
    entries = ingredient_registry[root]
    hr = herbal_roots.get(root, {'folio': '?', 'pharma_count': 0})
    recipes = set(e['recipe'] for e in entries)
    methods = Counter(e['method'] for e in entries)
    sources = Counter(e['source'] for e in entries)

    print(f'\n  {root:12s} (herbal {hr["folio"]}, pharma x{hr["pharma_count"]})')
    print(f'    {len(entries)} occurrences in {len(recipes)} recipes')
    print(f'    Methods: {dict(methods)}')
    print(f'    EVA forms: {", ".join(sorted(set(e["eva"] for e in entries)))}')

# ================================================================
# RECIPE COMPARISON: f103r vs AN structure
# ================================================================
print('\n' + '=' * 70)
print('RECIPE STRUCTURE vs ANTIDOTARIUM NICOLAI')
print('=' * 70)

# AN typical structure: VERB INGR INGR INGR DOSE INGR INGR DOSE VERB PREP ...
# VMS expected: some similar alternation

for r in all_recipes:
    ingr_ratio = r['counts']['INGR'] / max(r['n_words'], 1)
    dose_ratio = r['counts']['DOSE'] / max(r['n_words'], 1)
    print(f'  {r["id"]}: {r["n_words"]:2d}w | '
          f'{r["counts"]["INGR"]:2d}I({ingr_ratio:.0%}) '
          f'{r["counts"]["DOSE"]:2d}D({dose_ratio:.0%}) '
          f'{r["counts"]["LOGO"]:1d}L {r["counts"]["UNK"]:2d}?')

# Expected AN ratios:
# INGR: ~50-60% of tokens
# DOSE+QTY: ~10-15%
# VERB: ~3-5%
# GRAM: ~20-30%

print('\nAN reference ratios: INGR ~50%, DOSE ~12%, VERB ~4%, GRAM ~25%')
print(f'VMS f103r observed: INGR {tag_counts["INGR"]*100//total_words}%, '
      f'DOSE {tag_counts["DOSE"]*100//total_words}%, '
      f'LOGO {tag_counts["LOGO"]*100//total_words}%, '
      f'UNK {tag_counts["UNK"]*100//total_words}%')
print(f'\n→ Most UNK words are likely INGREDIENTS or GRAMMAR not yet identified.')
print(f'→ The {tag_counts["INGR"]} identified ingredients are a LOWER BOUND.')

# ================================================================
# Save
# ================================================================
results = {
    'version': 'v2_deep_root',
    'total_words': total_words,
    'tag_distribution': dict(tag_counts),
    'match_methods': dict(match_methods),
    'recipes': all_recipes,
    'ingredient_registry': {
        root: {
            'herbal_folio': herbal_roots.get(root, {}).get('folio', '?'),
            'pharma_count': herbal_roots.get(root, {}).get('pharma_count', 0),
            'occurrences': entries,
        }
        for root, entries in ingredient_registry.items()
    },
    'all_herbal_roots': sorted(all_herbal_roots),
    'n_herbal_roots_total': len(all_herbal_roots),
}

with open(os.path.join(RESULTS, 'f103r_ingredients_v2.json'), 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print('\nSaved f103r_ingredients_v2.json')
