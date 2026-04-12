"""
SESSION 17 — DECISIVE ATTACK: Constraint solving on 31 Macer-bridged recipes

For each recipe where we know the plant:
1. Get the Macer chapter → list of expected ingredients
2. Extract all NON-functional, NON-noise roots from the recipe
3. These unknown roots MUST BE one of the Macer ingredients
4. If a root appears in multiple recipes for DIFFERENT plants,
   it must be an ingredient shared by those Macer chapters
5. Cross-validate: the same root→ingredient must be consistent everywhere

This is the most constrained attack possible.
"""
import json, sys, io, os
from collections import Counter, defaultdict
from math import comb

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.dirname(__file__)
VMS_PATH = os.path.join(BASE, '..', 'vms', 'vms_structured.json')
REG_PATH = os.path.join(BASE, '..', 'hypothesis_registry.json')
MACER_PATH = os.path.join(BASE, '..', 'session_14', 'macer_complete.json')
ATK2_PATH = os.path.join(BASE, 'attack2_results.json')
RESULTS = BASE

with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)
with open(REG_PATH, encoding='utf-8') as f:
    registry = json.load(f)
with open(MACER_PATH, encoding='utf-8') as f:
    macer = json.load(f)
with open(ATK2_PATH, encoding='utf-8') as f:
    atk2 = json.load(f)

LOGOS = {'o','l','d','r','v','x','k','m','f','t','y','c','s','sh','p','ch','air','h'}

# Functional roots (>20% of folios) — NOT ingredients
FUNCTIONAL = set(registry.get('functional_words', {}).keys())

# Noise roots (< 10% standalone from Attack 1)
NOISE = {'ke', 'ko', 'po', 'do'}

# Already known ingredients
KNOWN = {}
for root, data in registry['confirmed_ingredients'].items():
    KNOWN[root] = data['latin']
for root, data in registry.get('probable_ingredients', {}).items():
    if data.get('status') == 'ELIMINATED':
        continue
    if data.get('confidence', 0) >= 0.65:
        KNOWN[root] = data['latin'].replace('i_', '')

# Macer chapters
MACER_BY_NAME = {}
for ch in macer['chapters']:
    MACER_BY_NAME[ch['name'].lower()] = ch
if 'violae' in MACER_BY_NAME:
    MACER_BY_NAME['viola'] = MACER_BY_NAME['violae']

# Sherwood mapping for plants we identified in recipes
PLANT_TO_MACER = {
    'ruta': 'ruta', 'lens': 'plantago', 'aristolochia': 'aristolochia',
    'apium': 'apium', 'lactuca': 'lactuca', 'viola': 'violae',
    'scorzonera': None, 'valeriana': None, 'sonchus': None,
    'erigeron': None, 'veronica': None, 'mentha': 'mentha',
    'origanum': 'origanum', 'verbena': 'verbena', 'malva': 'malva',
    'atriplex': 'atriplex', 'satureia': 'satureia', 'centaurea': 'centaurea',
    'elleborus': 'elleborus', 'salvia': 'salvia', 'coriandrum': 'coriandrum',
    'nigella': None, 'rosmarinus': None, 'rhododendron': None,
}

print(f'Known ingredients: {len(KNOWN)}')
print(f'Functional roots: {len(FUNCTIONAL)}')
print(f'Noise roots: {NOISE}')

# ================================================================
# STEP 1: For each bridged recipe, extract candidate roots
# ================================================================
print(f'\n{"="*70}')
print('STEP 1 — EXTRACT CANDIDATE ROOTS FROM BRIDGED RECIPES')
print('='*70)

# Group matched recipes by plant
plant_recipes = defaultdict(list)
for r in atk2['matched_recipes']:
    plant_recipes[r['plant_latin']].append(r)

# For each recipe, extract roots that are:
# - NOT functional (not in top 62)
# - NOT noise (not ke, ko, po, do)
# - NOT already known
# - >= 3 chars (to avoid false positives)
# These are CANDIDATE ingredient roots

recipe_candidates = {}  # bid → list of candidate roots

for plant, recipes in plant_recipes.items():
    # Get Macer chapter if available
    macer_name = PLANT_TO_MACER.get(plant)
    if not macer_name:
        # Try direct lookup
        for mn, ch in MACER_BY_NAME.items():
            if plant.replace('plant_of_', '') in mn or mn in plant:
                macer_name = mn
                break

    macer_ch = MACER_BY_NAME.get(macer_name) if macer_name else None
    macer_ingrs = set()
    if macer_ch:
        macer_ingrs = set(i.replace('I_', '').replace('P_', '') for i in macer_ch['ingredients'])

    for r in recipes:
        bid = r['bid']
        fid = r['fid']

        # Get all words in this block
        candidates = Counter()
        total_words = 0
        known_found = set()

        for block in vms['folios'][fid]['blocks']:
            if block.get('block_id') != bid:
                continue
            for line in block['lines']:
                for w in line['words']:
                    eva = w['eva_primary']
                    root = (w.get('morphology') or {}).get('root', '')
                    total_words += 1

                    if eva in LOGOS:
                        continue
                    if not root or len(root) < 3:
                        continue
                    if root in FUNCTIONAL:
                        continue
                    if root in NOISE:
                        continue

                    # Already known?
                    if root in KNOWN:
                        known_found.add(KNOWN[root])
                        continue

                    # This is a candidate
                    candidates[root] += 1

        recipe_candidates[bid] = {
            'plant': plant,
            'macer_chapter': macer_name,
            'macer_ingredients': sorted(macer_ingrs),
            'known_found': sorted(known_found),
            'candidate_roots': dict(candidates),
            'total_words': total_words,
        }

# ================================================================
# STEP 2: Cross-recipe analysis — which unknown roots appear in
# multiple recipes for the SAME Macer ingredient set?
# ================================================================
print(f'\n{"="*70}')
print('STEP 2 — CROSS-RECIPE ROOT ANALYSIS')
print('='*70)

# For each unknown root, collect which recipes (and Macer chapters) it appears in
root_recipes = defaultdict(list)  # root → list of (bid, plant, macer_ingrs)

for bid, data in recipe_candidates.items():
    for root in data['candidate_roots']:
        root_recipes[root].append({
            'bid': bid,
            'plant': data['plant'],
            'macer_ingrs': set(data['macer_ingredients']),
        })

# For each root, find the INTERSECTION of Macer ingredients across all recipes
print(f'\n  Roots appearing in 2+ Macer-bridged recipes:')
print(f'  {"Root":>12s} {"#Rec":>5s} {"Intersection of Macer ingredients"}')
print('  ' + '-' * 70)

constraint_solutions = []

for root, recipe_list in sorted(root_recipes.items(), key=lambda x: -len(x[1])):
    # Only recipes with Macer chapters
    macer_recipes = [r for r in recipe_list if r['macer_ingrs']]

    if len(macer_recipes) < 2:
        continue

    # Intersection of all Macer ingredient sets
    intersection = None
    plants = set()
    for r in macer_recipes:
        plants.add(r['plant'])
        if intersection is None:
            intersection = r['macer_ingrs'].copy()
        else:
            intersection &= r['macer_ingrs']

    # Remove already-known ingredients
    if intersection:
        intersection -= set(KNOWN.values())

    if intersection and len(intersection) <= 5:
        constraint_solutions.append({
            'root': root,
            'n_recipes': len(macer_recipes),
            'n_plants': len(plants),
            'possible_ingredients': sorted(intersection),
            'plants': sorted(plants),
            'bids': [r['bid'] for r in macer_recipes[:5]],
        })

        print(f'  {root:>12s} {len(macer_recipes):>5d}  '
              f'plants={sorted(plants)[:3]}  '
              f'→ MUST BE: {sorted(intersection)}')

# Also check roots in 1 recipe (weaker but still constrained)
single_recipe_candidates = []
for root, recipe_list in root_recipes.items():
    macer_recipes = [r for r in recipe_list if r['macer_ingrs']]
    if len(macer_recipes) != 1:
        continue
    r = macer_recipes[0]
    remaining = r['macer_ingrs'] - set(KNOWN.values())
    if remaining and len(remaining) <= 3:
        single_recipe_candidates.append({
            'root': root,
            'plant': r['plant'],
            'bid': r['bid'],
            'possible_ingredients': sorted(remaining),
        })

print(f'\n  Roots in 1 Macer-bridged recipe with <=3 possible ingredients: {len(single_recipe_candidates)}')
for sc in sorted(single_recipe_candidates, key=lambda x: len(x['possible_ingredients']))[:15]:
    print(f'    {sc["root"]:>12s} in {sc["plant"]:>12s} → {sc["possible_ingredients"]}')


# ================================================================
# STEP 3: UNIQUE SOLUTIONS (root maps to exactly 1 ingredient)
# ================================================================
print(f'\n\n{"="*70}')
print('STEP 3 — UNIQUE SOLUTIONS')
print('='*70)

unique_solutions = []

for cs in constraint_solutions:
    if len(cs['possible_ingredients']) == 1:
        unique_solutions.append({
            'root': cs['root'],
            'ingredient': cs['possible_ingredients'][0],
            'n_recipes': cs['n_recipes'],
            'n_plants': cs['n_plants'],
            'confidence': min(0.85, 0.6 + 0.05 * cs['n_recipes'] + 0.1 * cs['n_plants']),
            'method': 'macer_constraint_intersection',
            'plants': cs['plants'],
        })

if unique_solutions:
    print(f'\n  ★★★ UNIQUE CONSTRAINT SOLUTIONS ★★★')
    print(f'  {"Root":>12s} {"Ingredient":>15s} {"Conf":>5s} {"#Rec":>5s} {"#Pl":>4s} {"Plants"}')
    print('  ' + '-' * 65)
    for us in unique_solutions:
        print(f'  {us["root"]:>12s} {us["ingredient"]:>15s} {us["confidence"]:>5.2f} '
              f'{us["n_recipes"]:>5d} {us["n_plants"]:>4d} {us["plants"][:3]}')
else:
    print(f'  No unique solutions found (intersection always > 1)')

# Narrow solutions (2-3 possibilities)
narrow = [cs for cs in constraint_solutions if 1 < len(cs['possible_ingredients']) <= 3]
if narrow:
    print(f'\n  NARROW SOLUTIONS (2-3 possibilities):')
    for ns in narrow:
        print(f'  {ns["root"]:>12s} ({ns["n_recipes"]} rec, {ns["n_plants"]} plants) '
              f'→ {ns["possible_ingredients"]}')


# ================================================================
# STEP 4: Show best decoded recipes with new knowledge
# ================================================================
print(f'\n\n{"="*70}')
print('STEP 4 — BEST RECIPES WITH CONSTRAINT KNOWLEDGE')
print('='*70)

# Add new solutions to vocabulary
new_vocab = {}
for us in unique_solutions:
    new_vocab[us['root']] = us['ingredient']

all_vocab = {}
all_vocab.update(KNOWN)
all_vocab.update(new_vocab)
sorted_all = sorted(all_vocab.keys(), key=len, reverse=True)

# Decode the Macer-bridged recipes with augmented vocabulary
best_decodings = []

for bridge in atk2['macer_bridge']:
    plant = bridge['plant']
    macer_ch = bridge['macer_chapter']
    macer_ingrs = set(bridge['macer_ingredients'])

    for bid in bridge['recipe_bids']:
        # Decode
        words = []
        for fid_check, folio in vms['folios'].items():
            for block in folio['blocks']:
                if block.get('block_id') != bid:
                    continue
                for line in block['lines']:
                    for w in line['words']:
                        eva = w['eva_primary']
                        root = (w.get('morphology') or {}).get('root', '')

                        if eva in LOGOS:
                            words.append(('LOGO', eva, f'[{eva}]', 1.0))
                        elif root in all_vocab:
                            ingr = all_vocab[root]
                            conf = 0.9 if root in KNOWN else 0.75
                            is_new = root in new_vocab
                            marker = '★' if is_new else ''
                            words.append(('INGR', eva, f'{ingr.upper()}{marker}', conf))
                        elif root in FUNCTIONAL or root in NOISE:
                            words.append(('FUNC', eva, f'~{root}~', 0.3))
                        else:
                            words.append(('UNK', eva, f'({eva})', 0.0))

        n_total = len(words)
        n_ingr = sum(1 for t, _, _, _ in words if t == 'INGR')
        n_func = sum(1 for t, _, _, _ in words if t == 'FUNC')
        n_logo = sum(1 for t, _, _, _ in words if t == 'LOGO')
        n_unk = sum(1 for t, _, _, _ in words if t == 'UNK')

        ingrs_found = set(latin for t, _, latin, _ in words if t == 'INGR')
        ingrs_in_macer = set(i.upper() for i in macer_ingrs) & set(i.replace('★','') for i in ingrs_found)

        reading = ' '.join(latin for _, _, latin, _ in words)

        best_decodings.append({
            'bid': bid,
            'plant': plant,
            'macer': macer_ch,
            'n_total': n_total,
            'n_ingr': n_ingr,
            'n_func': n_func,
            'n_logo': n_logo,
            'n_unk': n_unk,
            'ingrs_found': sorted(ingrs_found),
            'in_macer': len(ingrs_in_macer),
            'reading': reading,
        })

best_decodings.sort(key=lambda x: (-x['n_ingr'], -x['in_macer']))

print(f'\n  TOP 10 DECODED RECIPES:')
print(f'  {"Block":>12s} {"Plant":>12s} {"Tot":>4s} {"Ingr":>5s} {"Func":>5s} '
      f'{"Logo":>5s} {"Unk":>4s} {"InM":>4s}')
print('  ' + '-' * 60)

for bd in best_decodings[:10]:
    print(f'  {bd["bid"]:>12s} {bd["plant"]:>12s} {bd["n_total"]:>4d} '
          f'{bd["n_ingr"]:>5d} {bd["n_func"]:>5d} {bd["n_logo"]:>5d} '
          f'{bd["n_unk"]:>4d} {bd["in_macer"]:>4d}')
    # Show the reading
    print(f'    {bd["reading"][:100]}')
    if bd['ingrs_found']:
        print(f'    Ingredients: {", ".join(bd["ingrs_found"][:8])}')
    print()


# ================================================================
# SAVE
# ================================================================
output = {
    'n_bridged_recipes': len(recipe_candidates),
    'n_constraint_solutions': len(constraint_solutions),
    'n_unique_solutions': len(unique_solutions),
    'n_narrow_solutions': len(narrow),
    'unique_solutions': unique_solutions,
    'narrow_solutions': [{
        'root': ns['root'],
        'possible': ns['possible_ingredients'],
        'n_recipes': ns['n_recipes'],
    } for ns in narrow],
    'constraint_solutions': constraint_solutions,
    'best_decodings': best_decodings[:10],
}

with open(os.path.join(RESULTS, 'attack_decisive_results.json'), 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f'\n{"="*70}')
print(f'DECISIVE ATTACK SUMMARY')
print(f'  Bridged recipes analyzed: {len(recipe_candidates)}')
print(f'  Constraint solutions (2+ recipes): {len(constraint_solutions)}')
print(f'  UNIQUE solutions: {len(unique_solutions)}')
print(f'  Narrow solutions (2-3 options): {len(narrow)}')
print(f'{"="*70}')
print(f'\nSaved attack_decisive_results.json')
