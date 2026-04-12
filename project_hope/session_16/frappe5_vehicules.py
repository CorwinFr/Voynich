"""
SESSION 16 — FRAPPE 5: Universal vehicles (aqua/succus/vinum)

Strategy: In the best-decoded pharma recipes, the REMAINING unknown
words must be vehicles (aqua, succus, vinum) or verbs (misce, recipe).
By elimination, the most frequent unknown roots in well-decoded
recipes ARE the vehicles.

Additional signals:
- Vehicle follows dose marker (you dose the liquid)
- Vehicle precedes ingredient list (dissolve IN liquid)
- Vehicle at end of recipe (final dilution)
- Distribution: aqua > vinum > succus in medieval pharmacy

Also cross-validate with Frappe 1 candidate: ypch = aqua
"""
import json, sys, io, os
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.dirname(__file__)
VMS_PATH = os.path.join(BASE, '..', 'vms', 'vms_structured.json')
REG_PATH = os.path.join(BASE, '..', 'hypothesis_registry.json')
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
for root, data in registry['plant_names'].items():
    if root not in all_roots:
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
# STEP 1: Analyze pharma recipes — find best-decoded ones
# ================================================================
print('='*70)
print('FRAPPE 5 — UNIVERSAL VEHICLES')
print('='*70)

recipe_data = []

for fid, folio in vms['folios'].items():
    if folio['metadata']['section'] != 'pharma':
        continue
    for block in folio['blocks']:
        bid = block.get('block_id', '')
        words = []
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
                    else:
                        words.append({'eva': eva, 'type': 'UNK', 'latin': '?', 'root': root_m})

        n_total = len(words)
        n_decoded = sum(1 for w in words if w['type'] != 'UNK')
        n_unk = n_total - n_decoded
        pct = n_decoded * 100 // max(n_total, 1)

        # Collect unknown roots
        unk_roots = Counter()
        for w in words:
            if w['type'] == 'UNK' and w.get('root'):
                unk_roots[w['root']] += 1

        recipe_data.append({
            'bid': bid,
            'fid': fid,
            'words': words,
            'n_total': n_total,
            'n_decoded': n_decoded,
            'pct': pct,
            'unk_roots': unk_roots,
        })

recipe_data.sort(key=lambda x: -x['pct'])

print(f'\n  Total pharma recipes: {len(recipe_data)}')
print(f'\n  TOP 20 best-decoded:')
print(f'  {"Block":>20s} {"Tot":>4s} {"Dec":>4s} {"Pct":>4s} {"Unknown roots (top 3)"}')
print('  ' + '-' * 65)

for r in recipe_data[:20]:
    unk_str = ', '.join(f'{root}({n})' for root, n in r['unk_roots'].most_common(3))
    print(f'  {r["bid"]:>20s} {r["n_total"]:>4d} {r["n_decoded"]:>4d} {r["pct"]:>3d}%  {unk_str}')


# ================================================================
# STEP 2: In well-decoded recipes (70%+), which unknown roots remain?
# ================================================================
print(f'\n\n{"="*70}')
print('STEP 2 — UNKNOWN ROOTS IN 70%+ DECODED RECIPES')
print('='*70)

# Count unknown roots across well-decoded recipes
unk_across_recipes = Counter()
unk_recipe_count = Counter()  # in how many recipes
unk_position_stats = defaultdict(list)  # position in recipe (0-1)

good_recipes = [r for r in recipe_data if r['pct'] >= 60 and r['n_total'] >= 5]
print(f'\n  Recipes at 60%+ decoded with 5+ words: {len(good_recipes)}')

for r in good_recipes:
    seen_in_recipe = set()
    for i, w in enumerate(r['words']):
        if w['type'] == 'UNK' and w.get('root'):
            root = w['root']
            unk_across_recipes[root] += 1
            norm_pos = i / max(len(r['words']), 1)
            unk_position_stats[root].append(norm_pos)
            if root not in seen_in_recipe:
                unk_recipe_count[root] += 1
                seen_in_recipe.add(root)

print(f'\n  Unknown roots ranked by frequency in good recipes:')
print(f'  {"Root":>12s} {"Count":>6s} {"Recipes":>8s} {"MeanPos":>8s} {"PosRange"}')
print('  ' + '-' * 55)

top_unknowns = unk_across_recipes.most_common(20)
for root, count in top_unknowns:
    n_rec = unk_recipe_count[root]
    positions = unk_position_stats[root]
    mean_pos = sum(positions) / len(positions)
    min_pos = min(positions)
    max_pos = max(positions)
    print(f'  {root:>12s} {count:>6d} {n_rec:>8d} {mean_pos:>8.2f} [{min_pos:.2f}-{max_pos:.2f}]')


# ================================================================
# STEP 3: Context analysis — what comes before/after unknowns?
# ================================================================
print(f'\n\n{"="*70}')
print('STEP 3 — CONTEXT ANALYSIS (what surrounds top unknowns?)')
print('='*70)

# For each top unknown root, what types of words come before/after?
for root, _ in top_unknowns[:10]:
    before_types = Counter()
    after_types = Counter()
    before_dose = 0
    after_dose = 0
    after_ingr = 0
    before_ingr = 0
    at_line_end = 0
    at_line_start = 0
    total_occ = 0

    for r in good_recipes:
        for i, w in enumerate(r['words']):
            if w['type'] == 'UNK' and w.get('root') == root:
                total_occ += 1
                if i > 0:
                    before_types[r['words'][i-1]['type']] += 1
                    if r['words'][i-1]['type'] == 'DOSE':
                        before_dose += 1
                    if r['words'][i-1]['type'] == 'INGR':
                        before_ingr += 1
                if i < len(r['words']) - 1:
                    after_types[r['words'][i+1]['type']] += 1
                    if r['words'][i+1]['type'] == 'DOSE':
                        after_dose += 1
                    if r['words'][i+1]['type'] == 'INGR':
                        after_ingr += 1

                # Position extremes
                norm = i / max(len(r['words']), 1)
                if norm < 0.1:
                    at_line_start += 1
                if norm > 0.85:
                    at_line_end += 1

    if total_occ == 0:
        continue

    print(f'\n  {root:>12s} ({total_occ} occurrences in good recipes):')
    print(f'    Before: {dict(before_types.most_common(4))}')
    print(f'    After:  {dict(after_types.most_common(4))}')
    print(f'    Before DOSE: {before_dose}/{total_occ} = {before_dose*100//total_occ}%')
    print(f'    After DOSE:  {after_dose}/{total_occ} = {after_dose*100//total_occ}%')
    print(f'    After INGR:  {after_ingr}/{total_occ} = {after_ingr*100//total_occ}%')
    print(f'    At start: {at_line_start}/{total_occ}  At end: {at_line_end}/{total_occ}')


# ================================================================
# STEP 4: Vehicle assignment by elimination
# ================================================================
print(f'\n\n{"="*70}')
print('STEP 4 — VEHICLE ASSIGNMENT')
print('='*70)

# Criteria for vehicles:
# 1. Must be in many recipes (>30% of good recipes)
# 2. Vehicles typically follow dose markers (you measure the liquid)
# 3. Aqua = most universal, often at end (final dilution)
# 4. Vinum = often with dose (measured wine)
# 5. Succus = often before ingredient (juice OF something)

print(f'\n  Scoring vehicle candidates:')
print(f'  {"Root":>12s} {"Recipes":>8s} {"BefDose":>8s} {"AftDose":>8s} {"AftIngr":>8s} '
      f'{"AtEnd":>6s} {"Score":>6s} {"Hypothesis"}')
print('  ' + '-' * 80)

n_good = max(len(good_recipes), 1)
vehicle_scores = []

for root, count in top_unknowns[:15]:
    n_rec = unk_recipe_count[root]
    rec_pct = n_rec * 100 // n_good
    positions = unk_position_stats[root]
    mean_pos = sum(positions) / len(positions)

    # Count contextual features
    total_occ = 0
    before_dose = 0
    after_dose = 0
    after_ingr = 0
    at_end = 0
    at_start = 0

    for r in good_recipes:
        for i, w in enumerate(r['words']):
            if w['type'] == 'UNK' and w.get('root') == root:
                total_occ += 1
                norm = i / max(len(r['words']), 1)
                if i > 0 and r['words'][i-1]['type'] == 'DOSE':
                    before_dose += 1
                if i < len(r['words'])-1 and r['words'][i+1]['type'] == 'DOSE':
                    after_dose += 1
                if i < len(r['words'])-1 and r['words'][i+1]['type'] == 'INGR':
                    after_ingr += 1
                if norm > 0.85:
                    at_end += 1
                if norm < 0.1:
                    at_start += 1

    if total_occ == 0:
        continue

    bd_pct = before_dose * 100 // total_occ
    ad_pct = after_dose * 100 // total_occ
    ai_pct = after_ingr * 100 // total_occ
    ae_pct = at_end * 100 // total_occ

    # Composite vehicle score
    score = rec_pct + bd_pct + ad_pct

    # Hypothesis based on profile
    if ae_pct >= 20 and rec_pct >= 30:
        hyp = 'aqua? (end position + universal)'
    elif bd_pct >= 20:
        hyp = 'vinum? (follows dose = measured)'
    elif ai_pct >= 20:
        hyp = 'succus? (before ingredient = juice OF)'
    elif rec_pct >= 20:
        hyp = 'vehicle? (frequent)'
    else:
        hyp = ''

    vehicle_scores.append({
        'root': root,
        'n_rec': n_rec,
        'rec_pct': rec_pct,
        'total_occ': total_occ,
        'before_dose_pct': bd_pct,
        'after_dose_pct': ad_pct,
        'after_ingr_pct': ai_pct,
        'at_end_pct': ae_pct,
        'score': score,
        'hypothesis': hyp,
    })

    print(f'  {root:>12s} {rec_pct:>7d}% {bd_pct:>7d}% {ad_pct:>7d}% {ai_pct:>7d}% '
          f'{ae_pct:>5d}% {score:>5d} {hyp}')


# ================================================================
# STEP 5: Cross-validate with herbal section
# ================================================================
print(f'\n\n{"="*70}')
print('STEP 5 — HERBAL CROSS-VALIDATION')
print('='*70)

# If a root is truly aqua/vinum/succus, it should also appear in herbal
# (these are universal ingredients in Macer)
print(f'\n  Checking vehicle candidates in herbal folios:')

for vs in vehicle_scores[:10]:
    root = vs['root']
    herbal_count = 0
    pharma_count = 0
    balnea_count = 0
    other_count = 0

    for fid, folio in vms['folios'].items():
        section = folio['metadata']['section']
        found = False
        for block in folio['blocks']:
            for line in block['lines']:
                for w in line['words']:
                    r = (w.get('morphology') or {}).get('root', '')
                    if r == root:
                        found = True
                        break
                if found: break
            if found: break

        if found:
            if section == 'herbal':
                herbal_count += 1
            elif section == 'pharma':
                pharma_count += 1
            elif section == 'balnea':
                balnea_count += 1
            else:
                other_count += 1

    total = herbal_count + pharma_count + balnea_count + other_count
    print(f'  {root:>12s}: herbal={herbal_count} pharma={pharma_count} '
          f'balnea={balnea_count} other={other_count} total={total}  '
          f'{vs["hypothesis"]}')


# ================================================================
# SAVE
# ================================================================
output = {
    'n_good_recipes': len(good_recipes),
    'top_unknowns': [{
        'root': root,
        'count': count,
        'n_recipes': unk_recipe_count[root],
    } for root, count in top_unknowns],
    'vehicle_candidates': vehicle_scores[:10],
}

with open(os.path.join(RESULTS, 'frappe5_results.json'), 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f'\nSaved frappe5_results.json')
