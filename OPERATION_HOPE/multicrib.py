#!/usr/bin/env python3
"""
OPERATION HOPE - MULTI-CRIB ATTACK
Segment ALL pharma folios by star markers (<$>) into individual recipes.
Compare each VMS recipe's signature with AN recipe signatures.
"""

import json, re, math
from collections import Counter, defaultdict

IVTFF = "/sessions/laughing-jolly-bell/mnt/Voynich FINAL/OPERATION_HOPE/data/LSI_ivtff_0d.txt"
AN_PATH = "/sessions/laughing-jolly-bell/mnt/Voynich FINAL/RECIPE_DATASET/S01_AN.json"
RESDIR = "/sessions/laughing-jolly-bell/mnt/Voynich FINAL/OPERATION_HOPE/results"

def get_section(folio):
    m = re.match(r'f(\d+)', folio)
    if not m: return 'other'
    num = int(m.group(1))
    if 87 <= num <= 116: return 'pharma'
    return 'other'

def classify_word(w):
    """Classify VMS word into functional category."""
    if re.search(r'ai+n$', w) and len(w) > 3:
        return 'DOSE'
    if re.search(r'ee+y$', w) and len(w) > 3:
        return 'UNIT'
    if w.endswith('edy') and len(w) >= 5:
        return 'INGR_A'
    if w.endswith('eol') and len(w) >= 5:
        return 'INGR_B'
    if len(w) <= 2:
        return 'FUNC'
    if len(w) >= 7:
        return 'LONG'
    return 'MID'

# ========================================================================
# 1. SEGMENTATION VMS PHARMA BY STAR MARKERS
# ========================================================================
print("=" * 70)
print("1. SEGMENTATION VMS PHARMA PAR ETOILES")
print("=" * 70)

# Parse all H-transcriber pharma lines, segment by <$>
all_recipes = []  # list of {folio, recipe_num, words, classes}
current_words = []
current_folio = None
recipe_count_per_folio = Counter()

with open(IVTFF, encoding='latin-1') as f:
    for line in f:
        line = line.rstrip('\n')
        if not line or line.startswith('#'):
            continue
        m = re.match(r'<(f\d+\w?\d?)\.(\d+),[^;]*;H>\s*(.*)', line)
        if not m:
            continue
        folio = m.group(1)
        if get_section(folio) != 'pharma':
            continue

        text = m.group(3).strip()
        has_star = '<$>' in text

        # Clean
        text = re.sub(r'<[^>]*>', '', text)
        text = re.sub(r'\{[^}]*\}', '', text)
        text = re.sub(r'[!\?\*\'"]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()

        words = [w.strip() for w in text.split('.') if w.strip()]
        expanded = []
        for w in words:
            parts = w.split()
            expanded.extend([p for p in parts if p and re.match(r'^[a-zA-Z]+$', p)])

        if current_folio and current_folio != folio and current_words:
            # New folio boundary = also recipe boundary
            classes = [classify_word(w) for w in current_words]
            recipe_count_per_folio[current_folio] += 1
            all_recipes.append({
                'folio': current_folio,
                'recipe_num': recipe_count_per_folio[current_folio],
                'words': current_words,
                'classes': classes
            })
            current_words = []

        current_folio = folio
        current_words.extend(expanded)

        if has_star and current_words:
            # Star = recipe boundary
            classes = [classify_word(w) for w in current_words]
            recipe_count_per_folio[folio] += 1
            all_recipes.append({
                'folio': folio,
                'recipe_num': recipe_count_per_folio[folio],
                'words': current_words,
                'classes': classes
            })
            current_words = []

# Don't forget last recipe
if current_words:
    classes = [classify_word(w) for w in current_words]
    recipe_count_per_folio[current_folio] += 1
    all_recipes.append({
        'folio': current_folio,
        'recipe_num': recipe_count_per_folio[current_folio],
        'words': current_words,
        'classes': classes
    })

print(f"\nTotal VMS pharma recipes (star-segmented): {len(all_recipes)}")
print(f"\nRecipes per folio:")
for folio in sorted(recipe_count_per_folio.keys()):
    print(f"  {folio}: {recipe_count_per_folio[folio]} recipes")

# Recipe statistics
lens = [len(r['words']) for r in all_recipes]
doses = [sum(1 for c in r['classes'] if c == 'DOSE') for r in all_recipes]
units = [sum(1 for c in r['classes'] if c == 'UNIT') for r in all_recipes]

print(f"\nVMS Recipe statistics:")
print(f"  Tokens/recipe: min={min(lens)}, max={max(lens)}, "
      f"mean={sum(lens)/len(lens):.1f}, median={sorted(lens)[len(lens)//2]}")
print(f"  DOSE/recipe:   min={min(doses)}, max={max(doses)}, "
      f"mean={sum(doses)/len(doses):.1f}")
print(f"  UNIT/recipe:   min={min(units)}, max={max(units)}, "
      f"mean={sum(units)/len(units):.1f}")
print(f"  DOSE+UNIT/recipe: mean={sum(d+u for d,u in zip(doses,units))/len(doses):.1f}")

# ========================================================================
# 2. AN RECIPE SIGNATURES
# ========================================================================
print("\n" + "=" * 70)
print("2. SIGNATURES AN")
print("=" * 70)

with open(AN_PATH) as f:
    an_data = json.load(f)

dose_types = {'DOSE', 'QTY', 'UNIT'}

an_sigs = []
for entry in an_data['entries']:
    tokens = entry['tokens']
    n = len(tokens)
    types = [t.get('type', '?') for t in tokens]
    n_dose = sum(1 for t in types if t in dose_types)
    n_ingr = sum(1 for t in types if t == 'INGR')
    n_verb = sum(1 for t in types if t == 'VERB')
    n_func = sum(1 for t in types if t in ('CONJ', 'COP', 'GRAM'))

    an_sigs.append({
        'id': entry['id'], 'name': entry['name'],
        'n': n, 'n_dose': n_dose, 'n_ingr': n_ingr,
        'dose_density': n_dose / n if n else 0,
        'ingr_density': n_ingr / n if n else 0,
    })

an_lens = [s['n'] for s in an_sigs]
an_doses = [s['n_dose'] for s in an_sigs]
print(f"\nAN ({len(an_sigs)} recipes):")
print(f"  Tokens/recipe: min={min(an_lens)}, max={max(an_lens)}, "
      f"mean={sum(an_lens)/len(an_lens):.1f}, median={sorted(an_lens)[len(an_lens)//2]}")
print(f"  DOSE/recipe:   min={min(an_doses)}, max={max(an_doses)}, "
      f"mean={sum(an_doses)/len(an_doses):.1f}")

# ========================================================================
# 3. DISTRIBUTION COMPARISON
# ========================================================================
print("\n" + "=" * 70)
print("3. DISTRIBUTION TOKENS/RECETTE : VMS vs AN")
print("=" * 70)

print(f"\n{'Range':>12s} {'VMS':>6s} {'AN':>6s}")
print("-" * 30)
for lo, hi in [(1,5), (6,10), (11,15), (16,20), (21,25), (26,30), (31,40),
               (41,50), (51,70), (71,100), (101,150), (151,200)]:
    v = sum(1 for l in lens if lo <= l <= hi)
    a = sum(1 for l in an_lens if lo <= l <= hi)
    if v + a > 0:
        print(f"  {lo:3d}-{hi:3d}    {v:6d} {a:6d}")

# ========================================================================
# 4. DOSE/RECIPE DISTRIBUTION
# ========================================================================
print("\n" + "=" * 70)
print("4. DISTRIBUTION DOSES/RECETTE : VMS vs AN")
print("=" * 70)

print(f"\n{'Doses':>6s} {'VMS':>6s} {'VMS%':>6s} {'AN':>6s} {'AN%':>6s}")
print("-" * 35)
for d in range(0, 25):
    v = sum(1 for x in doses if x == d)
    a = sum(1 for x in an_doses if x == d)
    vp = 100 * v / len(doses) if v else 0
    ap = 100 * a / len(an_doses) if a else 0
    if v + a > 0:
        print(f"  {d:4d} {v:6d} {vp:5.1f}% {a:6d} {ap:5.1f}%")

# ========================================================================
# 5. DOSE DENSITY COMPARISON
# ========================================================================
print("\n" + "=" * 70)
print("5. DOSE DENSITY (doses/tokens) PAR RECETTE")
print("=" * 70)

vms_densities = [d / l if l > 0 else 0 for d, l in zip(doses, lens)]
an_densities = [s['dose_density'] for s in an_sigs]

print(f"\n  VMS dose density: mean={sum(vms_densities)/len(vms_densities):.3f}, "
      f"median={sorted(vms_densities)[len(vms_densities)//2]:.3f}")
print(f"  AN dose density:  mean={sum(an_densities)/len(an_densities):.3f}, "
      f"median={sorted(an_densities)[len(an_densities)//2]:.3f}")

# Histogram
print(f"\n{'Density':>8s} {'VMS':>6s} {'AN':>6s}")
print("-" * 25)
for lo, hi in [(0, 0.05), (0.05, 0.10), (0.10, 0.15), (0.15, 0.20),
               (0.20, 0.25), (0.25, 0.30), (0.30, 0.40), (0.40, 0.50)]:
    v = sum(1 for x in vms_densities if lo <= x < hi)
    a = sum(1 for x in an_densities if lo <= x < hi)
    if v + a > 0:
        print(f"  {lo:.2f}-{hi:.2f} {v:6d} {a:6d}")

# ========================================================================
# 6. SIGNATURE MATCHING: Find VMS recipes closest to AN recipes
# ========================================================================
print("\n" + "=" * 70)
print("6. SIGNATURE MATCHING: VMS <-> AN")
print("=" * 70)

def recipe_distance(vms_r, an_s):
    """Distance between VMS recipe and AN signature based on structure."""
    # Normalize by recipe length
    vms_n = len(vms_r['words'])
    an_n = an_s['n']
    vms_dose_d = sum(1 for c in vms_r['classes'] if c == 'DOSE') / max(vms_n, 1)
    an_dose_d = an_s['dose_density']

    # Length similarity (log ratio)
    len_dist = abs(math.log(vms_n / max(an_n, 1)))
    # Dose density difference
    dose_dist = abs(vms_dose_d - an_dose_d)

    return len_dist + dose_dist * 5  # weight dose density more

# For each VMS recipe, find top 3 AN matches
print(f"\nTop VMS-AN matches (by structure similarity):")
print(f"{'VMS Recipe':25s} {'n':>4s} {'dose':>5s} {'Best AN match':25s} {'n':>4s} {'dose':>5s} {'dist':>6s}")
print("-" * 80)

matches = []
for vr in all_recipes:
    vms_n = len(vr['words'])
    if vms_n < 5:
        continue
    vms_d = sum(1 for c in vr['classes'] if c == 'DOSE')

    best = min(an_sigs, key=lambda s: recipe_distance(vr, s))
    dist = recipe_distance(vr, best)
    matches.append((vr, best, dist))

matches.sort(key=lambda x: x[2])

for vr, best_an, dist in matches[:25]:
    vms_label = f"{vr['folio']}_R{vr['recipe_num']:02d}"
    vms_n = len(vr['words'])
    vms_d = sum(1 for c in vr['classes'] if c == 'DOSE')
    an_label = f"{best_an['id']}"
    print(f"  {vms_label:23s} {vms_n:4d} {vms_d:5d}   {an_label:23s} {best_an['n']:4d} {best_an['n_dose']:5d} {dist:6.3f}")

# ========================================================================
# 7. AGGREGATE METRICS
# ========================================================================
print("\n" + "=" * 70)
print("7. METRIQUES GLOBALES")
print("=" * 70)

total_recipes = len(all_recipes)
total_tokens = sum(lens)
total_doses = sum(doses)
total_units = sum(units)

print(f"\n  Total recettes VMS pharma: {total_recipes}")
print(f"  Total tokens:              {total_tokens}")
print(f"  Total DOSE markers:        {total_doses}")
print(f"  Total UNIT markers:        {total_units}")
print(f"  Tokens/recette:            {total_tokens/total_recipes:.1f}")
print(f"  DOSE/recette:              {total_doses/total_recipes:.1f}")
print(f"  DOSE density:              {total_doses/total_tokens:.3f}")
print(f"")
print(f"  AN reference:")
print(f"    150 recipes, 107.9 tokens/recipe, 12.7 DOSE/recipe")
print(f"    DOSE density: 0.121")

# ========================================================================
# 8. PER-FOLIO SUMMARY
# ========================================================================
print("\n" + "=" * 70)
print("8. RECETTES PAR FOLIO (resume)")
print("=" * 70)

folio_summary = defaultdict(lambda: {'recipes': 0, 'tokens': 0, 'doses': 0})
for r in all_recipes:
    f = r['folio']
    folio_summary[f]['recipes'] += 1
    folio_summary[f]['tokens'] += len(r['words'])
    folio_summary[f]['doses'] += sum(1 for c in r['classes'] if c == 'DOSE')

print(f"\n{'Folio':10s} {'Recettes':>9s} {'Tokens':>7s} {'Doses':>6s} {'Tok/Rec':>8s} {'Dose/Rec':>9s}")
print("-" * 55)
for folio in sorted(folio_summary.keys()):
    s = folio_summary[folio]
    tpr = s['tokens'] / s['recipes'] if s['recipes'] else 0
    dpr = s['doses'] / s['recipes'] if s['recipes'] else 0
    print(f"  {folio:8s} {s['recipes']:9d} {s['tokens']:7d} {s['doses']:6d} {tpr:8.1f} {dpr:9.1f}")

# Save recipes for future use
output = []
for r in all_recipes:
    output.append({
        'folio': r['folio'],
        'recipe_num': r['recipe_num'],
        'n_tokens': len(r['words']),
        'n_dose': sum(1 for c in r['classes'] if c == 'DOSE'),
        'n_unit': sum(1 for c in r['classes'] if c == 'UNIT'),
        'words': r['words'],
        'classes': r['classes']
    })

with open(f"{RESDIR}/vms_recipes_segmented.json", 'w') as f:
    json.dump(output, f, indent=2)
print(f"\nSaved {len(output)} recipes to results/vms_recipes_segmented.json")

print("\n" + "=" * 70)
print("MULTI-CRIB ANALYSIS COMPLETE")
print("=" * 70)
