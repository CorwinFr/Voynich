"""
SESSION 16 — FRAPPE 2: Pharma best-decoded recipes (fill gaps)

For each well-decoded recipe (65%+), the 2-3 remaining unknown words
should be identifiable by pharmaceutical context:
1. If a recipe has mel+piper+acetum+UNK, what's the UNK?
2. Search medieval recipe corpora for recipes with exactly those ingredients
3. The missing ingredient IS the unknown word

This is constraint solving: given partial decode, what completes it?
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

LOGOS = {'o': 'ac', 'l': 'se', 'd': 'de', 'r': 'recipe', 'v': 'vel',
         'x': 'crux', 'k': 'cum', 'm': 'misce', 'f': 'per', 't': 'et',
         'y': 'in', 'c': 'cum', 's': 'est', 'sh': 'ci', 'p': 'usque', 'ch': 'cum'}
LOGO_SET = set(LOGOS.keys())

# Build vocabulary
all_roots = {}
for root, data in registry['confirmed_ingredients'].items():
    all_roots[root] = data['latin']
for root, data in registry.get('probable_ingredients', {}).items():
    if root not in all_roots and data.get('status') != 'ELIMINATED':
        all_roots[root] = data['latin']

sorted_roots = sorted(all_roots.keys(), key=len, reverse=True)

def find_root(eva):
    for root in sorted_roots:
        if len(root) < 2:
            continue
        idx = eva.find(root)
        if idx >= 0:
            prefix = eva[:idx]
            suffix = eva[idx+len(root):]
            if len(prefix) <= 4 and len(suffix) <= 5:
                return root, all_roots[root]
    return None, None

# ================================================================
# Load corpora for recipe matching
# ================================================================
corpus_recipes = []  # list of (source, name, ingredient_set)

for corpus_file, corpus_name in [
    ('S01_AN.json', 'AN'),
    ('S05_MACER.json', 'MACER'),
    ('S09_COLLECTIO.json', 'COLLECTIO'),
    ('S08_AVICENNA.json', 'AVICENNA'),
]:
    path = os.path.join(RECIPE_DIR, corpus_file)
    if not os.path.exists(path):
        continue
    with open(path, encoding='utf-8') as f:
        data = json.load(f)

    for entry in data.get('entries', []):
        ingrs = set()
        for tok in entry.get('tokens', []):
            if tok.get('type') == 'INGR':
                ref = tok.get('ref', tok.get('raw', '')).lower().strip('.,;: ')
                if len(ref) >= 3:
                    ingrs.add(ref)
        if len(ingrs) >= 2:
            corpus_recipes.append((corpus_name, entry.get('name', ''), ingrs))

print(f'Loaded {len(corpus_recipes)} corpus recipes with 2+ ingredients')

# ================================================================
# Decode pharma recipes
# ================================================================
print(f'\n{"="*70}')
print('FRAPPE 2 — PHARMA RECIPE GAP-FILLING')
print('='*70)

recipe_data = []

for fid, folio in vms['folios'].items():
    if folio['metadata']['section'] != 'pharma':
        continue
    for block in folio['blocks']:
        bid = block.get('block_id', '')
        words = []
        known_ingrs = set()
        unknown_roots = []

        for line in block['lines']:
            for w in line['words']:
                eva = w['eva_primary']
                morph = w.get('morphology') or {}
                ic = morph.get('i_count')
                root_m = morph.get('root', '')

                if eva in LOGO_SET:
                    words.append({'eva': eva, 'type': 'LOGO', 'latin': LOGOS[eva]})
                elif ic is not None:
                    words.append({'eva': eva, 'type': 'DOSE', 'latin': f'({ic})'})
                elif len(eva) < 3:
                    words.append({'eva': eva, 'type': 'SHORT', 'latin': '?'})
                else:
                    root, latin = find_root(eva)
                    if root:
                        words.append({'eva': eva, 'type': 'INGR', 'latin': latin, 'root': root})
                        known_ingrs.add(latin.replace('i_', ''))
                    else:
                        words.append({'eva': eva, 'type': 'UNK', 'root': root_m})
                        if root_m and len(root_m) >= 2:
                            unknown_roots.append(root_m)

        n_total = len(words)
        n_decoded = sum(1 for w in words if w['type'] != 'UNK')
        pct = n_decoded * 100 // max(n_total, 1)

        if pct >= 60 and n_total >= 5 and len(known_ingrs) >= 2:
            recipe_data.append({
                'bid': bid,
                'fid': fid,
                'words': words,
                'n_total': n_total,
                'pct': pct,
                'known_ingrs': known_ingrs,
                'unknown_roots': Counter(unknown_roots),
            })

recipe_data.sort(key=lambda x: (-x['pct'], -len(x['known_ingrs'])))

print(f'\n  Well-decoded recipes with 2+ known ingredients: {len(recipe_data)}')

# ================================================================
# For each recipe, search corpora for matching recipes
# ================================================================
print(f'\n{"="*70}')
print('RECIPE-BY-RECIPE GAP FILLING')
print('='*70)

all_gap_fills = []

for r in recipe_data[:30]:
    known = r['known_ingrs']
    unk = r['unknown_roots']

    if not unk:
        continue

    # Search corpus recipes that contain ALL our known ingredients
    matches = []
    for source, name, corpus_ingrs in corpus_recipes:
        # How many of our known ingredients are in this corpus recipe?
        overlap = sum(1 for k in known if any(k in ci for ci in corpus_ingrs))
        if overlap >= 2:
            # What extra ingredients does this recipe have that we don't?
            extras = set()
            for ci in corpus_ingrs:
                if not any(k in ci for k in known):
                    extras.add(ci)
            if extras:
                matches.append((source, name, overlap, extras))

    if not matches:
        continue

    matches.sort(key=lambda x: -x[2])
    best_matches = matches[:5]

    # Count which extra ingredients appear most often across matches
    extra_counts = Counter()
    for _, _, _, extras in best_matches:
        for e in extras:
            extra_counts[e] += 1

    # The most common extra ingredient is likely what the unknown root means
    top_extras = extra_counts.most_common(5)

    if top_extras:
        print(f'\n  {r["bid"]} ({r["pct"]}% decoded, {len(known)} known ingr):')
        print(f'    Known: {", ".join(sorted(known))}')
        print(f'    Unknown roots: {dict(unk.most_common(5))}')
        print(f'    {len(matches)} corpus matches found. Top missing ingredients:')
        for extra, count in top_extras:
            print(f'      {extra:>20s} ({count}/{len(best_matches)} matches)')

        # Try to assign: most frequent unknown root → most frequent extra
        if len(unk) >= 1 and len(top_extras) >= 1:
            unk_root = unk.most_common(1)[0][0]
            extra_ingr = top_extras[0][0]
            confidence = top_extras[0][1] / max(len(best_matches), 1)

            all_gap_fills.append({
                'bid': r['bid'],
                'root': unk_root,
                'ingredient': extra_ingr,
                'confidence': round(confidence, 2),
                'known_context': sorted(known),
                'n_corpus_matches': len(matches),
            })

            print(f'    → HYPOTHESIS: {unk_root} = {extra_ingr} (conf={confidence:.2f})')


# ================================================================
# CONSOLIDATE: which root→ingredient appears across multiple recipes?
# ================================================================
print(f'\n\n{"="*70}')
print('CONSOLIDATION — Root mappings across recipes')
print('='*70)

root_assignments = defaultdict(list)
for gf in all_gap_fills:
    root_assignments[gf['root']].append(gf)

print(f'\n  {"Root":>12s} {"#Recipes":>9s} {"Ingredients (by frequency)"}')
print('  ' + '-' * 60)

consolidated = []
for root, assignments in sorted(root_assignments.items(), key=lambda x: -len(x[1])):
    ingr_counts = Counter(a['ingredient'] for a in assignments)
    top_ingr = ingr_counts.most_common(3)
    n_recipes = len(assignments)

    ingr_str = ', '.join(f'{ingr}({n})' for ingr, n in top_ingr)
    print(f'  {root:>12s} {n_recipes:>9d}  {ingr_str}')

    if n_recipes >= 2:
        best_ingr = top_ingr[0][0]
        best_count = top_ingr[0][1]
        confidence = min(0.7, 0.4 + 0.1 * best_count)
        consolidated.append({
            'root': root,
            'ingredient': best_ingr,
            'n_recipes': n_recipes,
            'n_agreement': best_count,
            'confidence': confidence,
        })

print(f'\n  Consolidated (2+ recipes): {len(consolidated)}')
for c in consolidated:
    print(f'    {c["root"]:>12s} = {c["ingredient"]:>15s} '
          f'({c["n_recipes"]} recipes, {c["n_agreement"]} agree, conf={c["confidence"]:.2f})')


# ================================================================
# SAVE
# ================================================================
output = {
    'n_good_recipes': len(recipe_data),
    'n_gap_fills': len(all_gap_fills),
    'gap_fills': all_gap_fills,
    'consolidated': consolidated,
}

with open(os.path.join(RESULTS, 'frappe2_results.json'), 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f'\nSaved frappe2_results.json')
