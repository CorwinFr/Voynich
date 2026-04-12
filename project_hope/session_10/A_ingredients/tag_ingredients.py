"""
ATTACK A — Identify ingredients in f103r recipes.

For each word in each of the 18 f103r recipes:
1. Is it a LOGOGRAM? (single glyph in table) → tag [LOGO:latin]
2. Is it a DOSE candidate? (has -ain/-aiin suffix) → tag [DOSE:i_count]
3. Does its ROOT match a herbal plant identifier? → tag [INGR:root:folio]
4. Otherwise → tag [?:word]

Also enriched with word2vec distributional type from Attack B.

Output: annotated recipes + statistics.
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
# 1. Load data
# ================================================================
with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)

with open(CROSSREF_PATH, encoding='utf-8') as f:
    crossref = json.load(f)

# Build herbal root → folio mapping
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

print(f'Loaded {len(herbal_roots)} herbal roots that appear in pharma')

# Load w2v results if available
w2v_nn = {}
if os.path.exists(W2V_PATH):
    with open(W2V_PATH, encoding='utf-8') as f:
        w2v = json.load(f)
    w2v_nn = w2v.get('nn_results', {})
    print(f'Loaded w2v neighbors for {len(w2v_nn)} words')

# ================================================================
# 2. Tag each word in f103r
# ================================================================
f103r = vms['folios']['f103r']
all_recipes = []
tag_counts = Counter()
ingredient_registry = defaultdict(list)  # root → [(recipe, position)]

print('\n' + '=' * 70)
print('f103r — 18 RECIPES ANNOTATED')
print('=' * 70)

for b in f103r['blocks']:
    recipe_id = b['block_id']
    words = []
    for line in b['lines']:
        for w in line['words']:
            words.append(w)

    print(f'\n{"─"*70}')
    print(f'RECIPE {recipe_id} ({len(words)} words)')
    print(f'{"─"*70}')

    tagged_words = []
    recipe_line = []

    for i, w in enumerate(words):
        eva = w['eva_primary']
        morph = w.get('morphology', {})
        root = morph.get('root', '')
        suffix = morph.get('suffix', '')
        ic = morph.get('i_count')

        # Classification
        if eva in LOGOGRAMS:
            tag = 'LOGO'
            label = f'[LOGO:{LOGOGRAMS[eva]}]'
            tag_counts['LOGO'] += 1
        elif ic is not None:
            tag = 'DOSE'
            label = f'[DOSE:i{ic}]'
            tag_counts['DOSE'] += 1
        elif root in herbal_roots:
            tag = 'INGR'
            hr = herbal_roots[root]
            label = f'[INGR:{root}→{hr["folio"]}]'
            tag_counts['INGR'] += 1
            ingredient_registry[root].append({
                'recipe': recipe_id,
                'position': i,
                'eva': eva,
                'suffix': suffix,
                'herbal_folio': hr['folio'],
            })
        else:
            # Check if root is a known functional word from w2v
            w2v_info = ''
            if eva in w2v_nn:
                top = w2v_nn[eva]['neighbors'][0]
                w2v_info = f' w2v→{top["latin"]}({top["cosine"]:.2f})'

            tag = 'UNK'
            label = f'[?:{eva}]'
            tag_counts['UNK'] += 1

        tagged_words.append({
            'pos': i,
            'eva': eva,
            'root': root,
            'suffix': suffix,
            'i_count': ic,
            'tag': tag,
            'label': label,
        })
        recipe_line.append(label)

    # Print recipe on 2 lines: EVA then tags
    eva_line = ' '.join(w['eva_primary'] for w in words)
    tag_line = ' '.join(tw['label'] for tw in tagged_words)

    # Print in chunks of ~8 words for readability
    chunk_size = 6
    for start in range(0, len(tagged_words), chunk_size):
        chunk = tagged_words[start:start+chunk_size]
        eva_chunk = ' '.join(f'{tw["eva"]:15s}' for tw in chunk)
        tag_chunk = ' '.join(f'{tw["label"]:15s}' for tw in chunk)
        print(f'  {eva_chunk}')
        print(f'  {tag_chunk}')
        print()

    # Summary
    n_ingr = sum(1 for tw in tagged_words if tw['tag'] == 'INGR')
    n_dose = sum(1 for tw in tagged_words if tw['tag'] == 'DOSE')
    n_logo = sum(1 for tw in tagged_words if tw['tag'] == 'LOGO')
    n_unk = sum(1 for tw in tagged_words if tw['tag'] == 'UNK')
    unique_ingr = len(set(tw['root'] for tw in tagged_words if tw['tag'] == 'INGR'))

    print(f'  SUMMARY: {n_ingr} INGR ({unique_ingr} unique), {n_dose} DOSE, '
          f'{n_logo} LOGO, {n_unk} UNK')

    all_recipes.append({
        'id': recipe_id,
        'n_words': len(words),
        'tagged': tagged_words,
        'counts': {'INGR': n_ingr, 'DOSE': n_dose, 'LOGO': n_logo, 'UNK': n_unk},
        'unique_ingredients': unique_ingr,
    })

# ================================================================
# 3. Global statistics
# ================================================================
print('\n' + '=' * 70)
print('GLOBAL STATISTICS')
print('=' * 70)

total_words = sum(r['n_words'] for r in all_recipes)
print(f'\nTotal words in f103r: {total_words}')
for tag, count in tag_counts.most_common():
    print(f'  {tag:6s}: {count:4d} ({count*100//total_words}%)')

print(f'\nIngredient coverage: {tag_counts["INGR"]}/{total_words} = '
      f'{tag_counts["INGR"]*100//total_words}%')

# ================================================================
# 4. Ingredient registry: which roots appear most?
# ================================================================
print('\n' + '=' * 70)
print('INGREDIENT REGISTRY (roots found in f103r)')
print('=' * 70)

for root in sorted(ingredient_registry.keys(),
                   key=lambda r: -len(ingredient_registry[r])):
    entries = ingredient_registry[root]
    hr = herbal_roots[root]
    recipes = set(e['recipe'] for e in entries)
    suffixes = Counter(e['suffix'] for e in entries)
    suf_str = ', '.join(f'{s or "(none)"}x{c}' for s, c in suffixes.most_common(3))

    print(f'\n  {root:12s} (herbal {hr["folio"]}, pharma x{hr["pharma_count"]})')
    print(f'    In {len(recipes)} recipes, {len(entries)} occurrences')
    print(f'    Suffixes: {suf_str}')
    print(f'    EVA forms: {", ".join(set(e["eva"] for e in entries))}')

# ================================================================
# 5. Recipe patterns: INGR-DOSE alternation
# ================================================================
print('\n' + '=' * 70)
print('RECIPE STRUCTURE PATTERNS')
print('=' * 70)

for r in all_recipes:
    pattern = ''.join({'INGR': 'I', 'DOSE': 'D', 'LOGO': 'L', 'UNK': '.'}[tw['tag']]
                      for tw in r['tagged'])
    n_id_pairs = sum(1 for i in range(len(pattern)-1) if pattern[i:i+2] == 'ID')
    print(f'  {r["id"]}: {pattern}')
    print(f'    {r["counts"]["INGR"]}I {r["counts"]["DOSE"]}D {r["counts"]["LOGO"]}L '
          f'{r["counts"]["UNK"]}? | I→D pairs: {n_id_pairs}')

# ================================================================
# 6. Cross-reference with w2v: what do UNK words distribute as?
# ================================================================
if w2v_nn:
    print('\n' + '=' * 70)
    print('UNK WORDS: W2V DISTRIBUTIONAL HINTS')
    print('=' * 70)

    unk_words = set()
    for r in all_recipes:
        for tw in r['tagged']:
            if tw['tag'] == 'UNK':
                unk_words.add(tw['eva'])

    for eva in sorted(unk_words, key=lambda w: -sum(1 for r in all_recipes
                      for tw in r['tagged'] if tw['eva'] == w)):
        if eva not in w2v_nn:
            continue
        nn = w2v_nn[eva]
        top3 = nn['neighbors'][:3]
        nn_str = ', '.join(f'{n["latin"]}({n["cosine"]:.2f})' for n in top3)
        count = sum(1 for r in all_recipes for tw in r['tagged'] if tw['eva'] == eva)
        print(f'  {eva:18s} (x{count:2d}) → {nn_str}')

# ================================================================
# Save
# ================================================================
results = {
    'total_words': total_words,
    'tag_distribution': dict(tag_counts),
    'recipes': all_recipes,
    'ingredient_registry': {
        root: {
            'herbal_folio': herbal_roots[root]['folio'],
            'pharma_count': herbal_roots[root]['pharma_count'],
            'occurrences': entries,
        }
        for root, entries in ingredient_registry.items()
    },
}

with open(os.path.join(RESULTS, 'f103r_ingredients.json'), 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print('\nSaved f103r_ingredients.json')
