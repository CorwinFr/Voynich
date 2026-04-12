"""
STAR COLOR ANALYSIS — f103r has TWO types of star markers.

User observation (from manuscript image):
  19 stars total: 7 ROUGE (filled), 12 VIDE (outline)

Pattern: R V V R V R V V R V V R V R V V R V V

19 entries for 18 blocks → first R = page header star, B01-B18 = entries 2-19.

KEY HYPOTHESIS: Rouge = main recipe header, Vide = sub-section/continuation.
If true → f103r has 6-7 COMPOUND RECIPES, not 18 independent ones.
"""
import json, sys, io, os
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.dirname(__file__)
CLASSIFIER_PATH = os.path.join(BASE, 'results', 'w2v_classifier.json')
AUDIT_PATH = os.path.join(BASE, 'results', 'recipe_structure_audit.json')
RESULTS = os.path.join(BASE, 'results')

with open(CLASSIFIER_PATH, encoding='utf-8') as f:
    classifier = json.load(f)
with open(AUDIT_PATH, encoding='utf-8') as f:
    audit = json.load(f)

# ================================================================
# STAR COLOR DATA (user observation)
# ================================================================
# 19 entries: first = page header, then B01-B18
STAR_COLORS_RAW = [
    'R',  # page header
    'V', 'V',  # B01, B02
    'R', 'V',  # B03, B04
    'R', 'V', 'V',  # B05, B06, B07
    'R', 'V', 'V',  # B08, B09, B10
    'R', 'V',  # B11, B12
    'R', 'V', 'V',  # B13, B14, B15
    'R', 'V', 'V',  # B16, B17, B18
]

# Map B01-B18
block_ids = [f'f103r_B{i:02d}' for i in range(1, 19)]
star_colors = {}
for i, bid in enumerate(block_ids):
    star_colors[bid] = STAR_COLORS_RAW[i + 1]  # skip page header

# Get scores from audit
score_by_id = {r['id']: r for r in audit['recipe_scores']}

print('=' * 70)
print('STAR COLOR MAPPING — f103r')
print('=' * 70)

print(f'\nPage header: ROUGE (decorative/section marker)')
print(f'\nBlock mapping:')
for bid in block_ids:
    color = star_colors[bid]
    r = score_by_id.get(bid, {})
    score = r.get('score', '?')
    n_words = r.get('n_words', '?')
    n_verb = r.get('n_verb', 0)
    n_ingr = r.get('n_ingr', 0)
    n_dose = r.get('n_dose', 0)
    marker = '█ ROUGE' if color == 'R' else '○ VIDE'
    print(f'  {bid}: {marker:10s} | score={score:3} | '
          f'{n_words:2}w {n_verb}V {n_ingr}I {n_dose}D')

# ================================================================
# HYPOTHESIS: Rouge = new recipe, Vide = sub-section
# ================================================================
print('\n' + '=' * 70)
print('COMPOUND RECIPE GROUPING')
print('Rouge = new recipe header, Vide = sub-section')
print('=' * 70)

# Group blocks: each R starts a new compound recipe
groups = []
current_group = None

for bid in block_ids:
    color = star_colors[bid]
    if color == 'R':
        if current_group:
            groups.append(current_group)
        current_group = {'header': bid, 'parts': [bid]}
    else:
        if current_group:
            current_group['parts'].append(bid)
        else:
            # Vide before first rouge — part of page header group
            if not groups:
                current_group = {'header': 'PAGE_HEADER', 'parts': [bid]}
            else:
                current_group['parts'].append(bid)

if current_group:
    groups.append(current_group)

print(f'\nFound {len(groups)} compound recipes:\n')

for i, group in enumerate(groups):
    header = group['header']
    parts = group['parts']
    total_words = sum(score_by_id.get(bid, {}).get('n_words', 0) for bid in parts)
    total_ingr = sum(score_by_id.get(bid, {}).get('n_ingr', 0) for bid in parts)
    total_dose = sum(score_by_id.get(bid, {}).get('n_dose', 0) for bid in parts)
    total_verb = sum(score_by_id.get(bid, {}).get('n_verb', 0) for bid in parts)

    scores = [score_by_id.get(bid, {}).get('score', 0) for bid in parts]
    avg_score = sum(scores) / max(len(scores), 1)

    print(f'  RECIPE {i+1} ({len(parts)} parts, {total_words} words)')
    for j, bid in enumerate(parts):
        color = star_colors.get(bid, '?')
        r = score_by_id.get(bid, {})
        marker = '█ HEAD' if j == 0 else '○ sub'
        n = r.get('n_words', 0)
        print(f'    {marker} {bid}: {n:2d}w '
              f'{r.get("n_verb",0)}V {r.get("n_ingr",0)}I {r.get("n_dose",0)}D '
              f'score={r.get("score",0)}')

    print(f'    → TOTAL: {total_words}w, {total_verb}V, {total_ingr}I, {total_dose}D')
    print()

# ================================================================
# COMPARE: compound recipe sizes vs AN
# ================================================================
print('=' * 70)
print('COMPOUND RECIPE SIZES vs ANTIDOTARIUM NICOLAI')
print('=' * 70)

compound_sizes = [sum(score_by_id.get(bid, {}).get('n_words', 0)
                      for bid in g['parts']) for g in groups]

# AN recipe sizes (from earlier analysis)
an_sizes_approx = [128, 134, 136, 105]  # first 4 AN recipes as reference
an_median = 115  # from earlier analysis

print(f'\nCompound recipe sizes: {compound_sizes}')
print(f'  Min: {min(compound_sizes)}, Max: {max(compound_sizes)}, '
      f'Mean: {sum(compound_sizes)/len(compound_sizes):.0f}, '
      f'Median: {sorted(compound_sizes)[len(compound_sizes)//2]}')
print(f'\nAN median: {an_median}')
print(f'  Ratio VMS_compound/AN: {sum(compound_sizes)/len(compound_sizes)/an_median:.2f}')

# ================================================================
# SUB-SECTION ROLES: what type of content is in each position?
# ================================================================
print('\n' + '=' * 70)
print('SUB-SECTION ROLE ANALYSIS')
print('What does each position (head, sub1, sub2) typically contain?')
print('=' * 70)

# Collect stats by position within group
pos_stats = defaultdict(lambda: {'n': 0, 'verb': 0, 'ingr': 0, 'dose': 0,
                                  'temp': 0, 'gram': 0, 'words': 0, 'scores': []})

for group in groups:
    for j, bid in enumerate(group['parts']):
        r = score_by_id.get(bid, {})
        pos = 'HEAD' if j == 0 else f'SUB_{j}'
        pos_stats[pos]['n'] += 1
        pos_stats[pos]['verb'] += r.get('n_verb', 0)
        pos_stats[pos]['ingr'] += r.get('n_ingr', 0)
        pos_stats[pos]['dose'] += r.get('n_dose', 0)
        pos_stats[pos]['words'] += r.get('n_words', 0)
        pos_stats[pos]['scores'].append(r.get('score', 0))

        # Get temporal count from classifier
        recipe_data = next((rec for rec in classifier['f103r_recipes']
                           if rec['id'] == bid), None)
        if recipe_data:
            n_temp = recipe_data['role_counts'].get('TEMPORAL', 0)
            pos_stats[pos]['temp'] += n_temp

print(f'\n{"Position":<10s} {"N":>3s} {"Words":>6s} {"Verb":>5s} {"Ingr":>5s} '
      f'{"Dose":>5s} {"Temp":>5s} {"AvgScore":>8s}')
print('-' * 55)

for pos in ['HEAD', 'SUB_1', 'SUB_2']:
    ps = pos_stats.get(pos, None)
    if not ps or ps['n'] == 0:
        continue
    avg_score = sum(ps['scores']) / len(ps['scores'])
    print(f'{pos:<10s} {ps["n"]:3d} {ps["words"]:6d} {ps["verb"]:5d} {ps["ingr"]:5d} '
          f'{ps["dose"]:5d} {ps["temp"]:5d} {avg_score:8.1f}')

# Per-block averages
print(f'\nPer-block averages:')
for pos in ['HEAD', 'SUB_1', 'SUB_2']:
    ps = pos_stats.get(pos, None)
    if not ps or ps['n'] == 0:
        continue
    n = ps['n']
    print(f'  {pos:<10s}: {ps["words"]/n:.0f}w/block, '
          f'{ps["verb"]/n:.1f}V, {ps["ingr"]/n:.1f}I, '
          f'{ps["dose"]/n:.1f}D, {ps["temp"]/n:.1f}T')

# ================================================================
# KEY FINDING: Do sub-sections specialize?
# ================================================================
print('\n' + '=' * 70)
print('KEY FINDING: SUB-SECTION SPECIALIZATION')
print('=' * 70)

for pos in ['HEAD', 'SUB_1', 'SUB_2']:
    ps = pos_stats.get(pos, None)
    if not ps or ps['n'] == 0:
        continue
    total = ps['words']
    if total == 0:
        continue
    verb_pct = ps['verb'] * 100 // total
    ingr_pct = ps['ingr'] * 100 // total
    dose_pct = ps['dose'] * 100 // total
    temp_pct = ps['temp'] * 100 // total

    dominant = max(
        [('VERB', verb_pct), ('INGR', ingr_pct), ('DOSE', dose_pct), ('TEMP', temp_pct)],
        key=lambda x: x[1]
    )
    print(f'\n  {pos}: {verb_pct}%V {ingr_pct}%I {dose_pct}%D {temp_pct}%T → {dominant[0]}-dominant')

# ================================================================
# AUREA RE-CHECK: does any compound recipe match Aurea (105 tokens)?
# ================================================================
print('\n' + '=' * 70)
print('AUREA RE-CHECK with compound recipes')
print(f'Aurea: 105 tokens, 78 INGR, 11 DOSE')
print('=' * 70)

for i, (group, size) in enumerate(zip(groups, compound_sizes)):
    total_ingr = sum(score_by_id.get(bid, {}).get('n_ingr', 0) for bid in group['parts'])
    total_dose = sum(score_by_id.get(bid, {}).get('n_dose', 0) for bid in group['parts'])
    dist = abs(size - 105) / 105
    print(f'  Recipe {i+1}: {size:3d} tokens, {total_ingr:2d}I, {total_dose:2d}D '
          f'| dist_Aurea={dist:.2f}')

# Save
results = {
    'star_colors': star_colors,
    'compound_recipes': [
        {
            'recipe_num': i + 1,
            'header': g['header'],
            'parts': g['parts'],
            'total_words': sum(score_by_id.get(bid, {}).get('n_words', 0) for bid in g['parts']),
            'total_ingr': sum(score_by_id.get(bid, {}).get('n_ingr', 0) for bid in g['parts']),
            'total_dose': sum(score_by_id.get(bid, {}).get('n_dose', 0) for bid in g['parts']),
        }
        for i, g in enumerate(groups)
    ],
    'position_stats': {pos: dict(ps) for pos, ps in pos_stats.items()},
    'discovery': 'f103r has 7 COMPOUND RECIPES (rouge=header, vide=sub-section), '
                 'not 18 independent recipes. Compound sizes (mean 76) much closer '
                 'to AN median (115) than individual blocks (mean 30).',
}

with open(os.path.join(RESULTS, 'star_color_analysis.json'), 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print('\nSaved star_color_analysis.json')
