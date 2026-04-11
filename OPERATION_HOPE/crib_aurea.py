#!/usr/bin/env python3
"""
OPERATION HOPE - CRIB AUREA ATTACK

Strategy:
1. Extract TYPE sequences from AN recipes (VERB, INGR, DOSE, QTY, UNIT...)
2. Identify the STRUCTURAL SIGNATURE of a pharmaceutical recipe:
   - Where do DOSE/QTY/UNIT tokens appear relative to INGR tokens?
   - What's the ratio of dose tokens to total tokens?
   - What's the typical INGR-DOSE gap?
3. Classify VMS pharma words by suffix into candidate TYPE categories
4. Test: Do VMS pharma sequences match the structural signature of AN recipes?
5. Critical test: Do positions of -ain/-aiin in VMS align with DOSE positions in AN?
"""

import json, re, math
from collections import Counter, defaultdict

AN_PATH = "/sessions/laughing-jolly-bell/mnt/Voynich FINAL/RECIPE_DATASET/S01_AN.json"
IVTFF = "/sessions/laughing-jolly-bell/mnt/Voynich FINAL/OPERATION_HOPE/data/LSI_ivtff_0d.txt"

# ========================================================================
# 1. AN STRUCTURAL ANALYSIS
# ========================================================================
print("=" * 70)
print("1. STRUCTURE DES RECETTES AN")
print("=" * 70)

with open(AN_PATH) as f:
    an_data = json.load(f)

# For each recipe: compute dose density and inter-dose interval
dose_types = {'DOSE', 'QTY', 'UNIT'}
ingr_types = {'INGR'}

recipe_stats = []
for entry in an_data['entries']:
    tokens = entry['tokens']
    n = len(tokens)
    types = [t.get('type', '?') for t in tokens]

    # Positions of DOSE/QTY/UNIT
    dose_pos = [i for i, t in enumerate(types) if t in dose_types]
    ingr_pos = [i for i, t in enumerate(types) if t in ingr_types]

    dose_density = len(dose_pos) / n if n > 0 else 0
    ingr_density = len(ingr_pos) / n if n > 0 else 0

    # Inter-DOSE intervals
    if len(dose_pos) > 1:
        intervals = [dose_pos[i+1] - dose_pos[i] for i in range(len(dose_pos)-1)]
        mean_interval = sum(intervals) / len(intervals)
    else:
        mean_interval = 0

    # INGR-to-DOSE distance: for each DOSE, how far back is nearest INGR?
    ingr_dose_gaps = []
    for dp in dose_pos:
        # Find nearest INGR before this DOSE
        nearest = [ip for ip in ingr_pos if ip < dp]
        if nearest:
            ingr_dose_gaps.append(dp - nearest[-1])

    # Pattern: INGR runs between DOSEs
    # Count consecutive INGR tokens
    ingr_runs = []
    current_run = 0
    for t in types:
        if t in ingr_types:
            current_run += 1
        else:
            if current_run > 0:
                ingr_runs.append(current_run)
            current_run = 0
    if current_run > 0:
        ingr_runs.append(current_run)

    recipe_stats.append({
        'id': entry['id'], 'n': n,
        'dose_density': dose_density,
        'ingr_density': ingr_density,
        'n_dose': len(dose_pos),
        'n_ingr': len(ingr_pos),
        'mean_interval': mean_interval,
        'ingr_dose_gaps': ingr_dose_gaps,
        'ingr_runs': ingr_runs,
    })

# Aggregate stats
print(f"\nAN ({len(recipe_stats)} recipes):")
print(f"  Dose density: {sum(r['dose_density'] for r in recipe_stats)/len(recipe_stats):.3f}")
print(f"  Ingr density: {sum(r['ingr_density'] for r in recipe_stats)/len(recipe_stats):.3f}")
print(f"  Mean tokens/recipe: {sum(r['n'] for r in recipe_stats)/len(recipe_stats):.1f}")
print(f"  Mean DOSE tokens/recipe: {sum(r['n_dose'] for r in recipe_stats)/len(recipe_stats):.1f}")
print(f"  Mean INGR tokens/recipe: {sum(r['n_ingr'] for r in recipe_stats)/len(recipe_stats):.1f}")

all_gaps = [g for r in recipe_stats for g in r['ingr_dose_gaps']]
if all_gaps:
    print(f"\n  INGR-to-DOSE gap distribution:")
    gap_dist = Counter(all_gaps)
    for g in sorted(gap_dist.keys())[:10]:
        bar = "#" * (gap_dist[g] // 2)
        print(f"    gap={g}: {gap_dist[g]:4d} {bar}")

all_runs = [r for s in recipe_stats for r in s['ingr_runs']]
if all_runs:
    print(f"\n  INGR run-length distribution:")
    run_dist = Counter(all_runs)
    for r in sorted(run_dist.keys())[:10]:
        bar = "#" * (run_dist[r] // 2)
        print(f"    run={r}: {run_dist[r]:4d} {bar}")

# KEY PATTERN: The AN "recipe fingerprint"
# Typical sequence: VERB [INGR]+ DOSE [INGR]+ DOSE ... VERB [INGR]+ PREP
# Simplified: INGR-run of 2-8, then DOSE cluster of 1-4, repeat
print(f"\n  AN Recipe Fingerprint:")
print(f"    INGR run: median={sorted(all_runs)[len(all_runs)//2]}, mean={sum(all_runs)/len(all_runs):.1f}")
print(f"    INGR-DOSE gap: median={sorted(all_gaps)[len(all_gaps)//2]}, mean={sum(all_gaps)/len(all_gaps):.1f}")

# ========================================================================
# 2. VMS WORD CLASSIFICATION BY SUFFIX
# ========================================================================
print("\n" + "=" * 70)
print("2. CLASSIFICATION DES MOTS VMS PAR SUFFIXE")
print("=" * 70)

def get_section(folio):
    m = re.match(r'f(\d+)', folio)
    if not m: return 'other'
    num = int(m.group(1))
    if 87 <= num <= 116: return 'pharma'
    elif 1 <= num <= 66: return 'herbal'
    elif 75 <= num <= 84: return 'balnea'
    return 'other'

def classify_vms_word(w):
    """Classify a VMS word into candidate TYPE based on suffix/features."""
    # DOSE candidates: words containing a[i+]n pattern
    if re.search(r'a[i]+n$', w):
        return 'DOSE_CAND'  # -ain, -aiin, -aiiin
    # UNIT candidates: -eey, -eedy (pharma-specific suffixes)
    if re.search(r'ee+y$', w):
        return 'UNIT_CAND'  # -eey, -eeey
    # Possible ingredient: -edy (pharma-associated)
    if w.endswith('edy') and len(w) >= 4:
        return 'INGR_CAND_A'
    # Possible ingredient: -eol
    if w.endswith('eol') and len(w) >= 4:
        return 'INGR_CAND_B'
    # Short function words (1-2 chars)
    if len(w) <= 2:
        return 'FUNC'
    # Herbal-associated suffixes
    if w.endswith('chy') or w.endswith('hor'):
        return 'HERB_ASSOC'
    # Long words (>= 7 chars) - likely content words
    if len(w) >= 7:
        return 'LONG'
    return 'OTHER'

# Parse VMS pharma
pharma_lines = defaultdict(list)  # folio -> [list of (word, class)]
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
        text = re.sub(r'\{[^}]*\}', '', text)
        text = re.sub(r'<[^>]*>', '', text)
        text = re.sub(r'[!\?\*\'"]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        words = [w.strip() for w in text.split('.') if w.strip()]
        expanded = []
        for w in words:
            parts = w.split()
            expanded.extend([p for p in parts if p and re.match(r'^[a-zA-Z]+$', p)])

        classified = [(w, classify_vms_word(w)) for w in expanded]
        pharma_lines[folio].extend(classified)

# Global classification stats
all_pharma_classified = [(w, c) for folio in pharma_lines for w, c in pharma_lines[folio]]
class_dist = Counter(c for _, c in all_pharma_classified)
total = len(all_pharma_classified)
print(f"\nVMS Pharma word classification (n={total}):")
for cls, count in class_dist.most_common():
    pct = 100 * count / total
    print(f"  {cls:15s}: {count:5d} ({pct:5.1f}%)")

# ========================================================================
# 3. STRUCTURAL COMPARISON: AN vs VMS
# ========================================================================
print("\n" + "=" * 70)
print("3. CRIB STRUCTURAL: DOSE density dans VMS vs AN")
print("=" * 70)

# VMS "dose density" = fraction of DOSE_CAND words
# Compare with AN dose density
vms_dose_density_by_folio = {}
for folio in sorted(pharma_lines.keys()):
    words = pharma_lines[folio]
    n = len(words)
    if n < 10:
        continue
    dose_count = sum(1 for _, c in words if c == 'DOSE_CAND')
    unit_count = sum(1 for _, c in words if c == 'UNIT_CAND')
    dose_density = dose_count / n
    unit_density = unit_count / n
    combined = (dose_count + unit_count) / n
    vms_dose_density_by_folio[folio] = {
        'dose_d': dose_density, 'unit_d': unit_density,
        'combined': combined, 'n': n,
        'dose_n': dose_count, 'unit_n': unit_count
    }

# AN average dose density
an_dose_avg = sum(r['dose_density'] for r in recipe_stats) / len(recipe_stats)
an_ingr_avg = sum(r['ingr_density'] for r in recipe_stats) / len(recipe_stats)

print(f"\nAN dose density (DOSE+QTY+UNIT / total): {an_dose_avg:.3f}")
print(f"AN ingredient density (INGR / total): {an_ingr_avg:.3f}")

vms_dose_vals = [v['dose_d'] for v in vms_dose_density_by_folio.values()]
vms_combined = [v['combined'] for v in vms_dose_density_by_folio.values()]
print(f"\nVMS pharma DOSE_CAND density: mean={sum(vms_dose_vals)/len(vms_dose_vals):.3f}, "
      f"range={min(vms_dose_vals):.3f}-{max(vms_dose_vals):.3f}")
print(f"VMS pharma DOSE+UNIT density: mean={sum(vms_combined)/len(vms_combined):.3f}, "
      f"range={min(vms_combined):.3f}-{max(vms_combined):.3f}")

print(f"\n{'Folio':10s} {'Words':>6s} {'DOSE':>5s} {'UNIT':>5s} {'D_dens':>7s} {'D+U':>7s}")
print("-" * 48)
for folio in sorted(vms_dose_density_by_folio.keys()):
    v = vms_dose_density_by_folio[folio]
    print(f"  {folio:8s} {v['n']:6d} {v['dose_n']:5d} {v['unit_n']:5d} {v['dose_d']:7.3f} {v['combined']:7.3f}")

# ========================================================================
# 4. CRITICAL TEST: DOSE-INGR ALTERNATION PATTERN
# ========================================================================
print("\n" + "=" * 70)
print("4. TEST CLE: Pattern INGR-DOSE alternation")
print("=" * 70)

# In AN, the pattern is: [INGR]+ [DOSE]+ [INGR]+ [DOSE]+
# If VMS follows the same pattern, DOSE_CAND should alternate with non-DOSE runs

# For VMS pharma: compute run lengths of DOSE_CAND vs non-DOSE
def get_runs(classified_words, target_classes):
    """Get alternating run lengths of target vs non-target."""
    target_runs = []
    non_target_runs = []
    current_target = 0
    current_non = 0

    for _, cls in classified_words:
        if cls in target_classes:
            if current_non > 0:
                non_target_runs.append(current_non)
                current_non = 0
            current_target += 1
        else:
            if current_target > 0:
                target_runs.append(current_target)
                current_target = 0
            current_non += 1

    if current_target > 0:
        target_runs.append(current_target)
    if current_non > 0:
        non_target_runs.append(current_non)

    return target_runs, non_target_runs

# VMS pharma runs
all_pharma = [(w, c) for folio in sorted(pharma_lines.keys()) for w, c in pharma_lines[folio]]
vms_dose_runs, vms_nondose_runs = get_runs(all_pharma, {'DOSE_CAND'})

print(f"\nVMS Pharma DOSE_CAND runs:")
dose_run_dist = Counter(vms_dose_runs)
for r in sorted(dose_run_dist.keys())[:8]:
    print(f"  run={r}: {dose_run_dist[r]:4d}")

print(f"\nVMS Pharma non-DOSE runs between DOSEs:")
nondose_run_dist = Counter(vms_nondose_runs)
for r in sorted(nondose_run_dist.keys())[:12]:
    bar = "#" * (nondose_run_dist[r] // 3)
    print(f"  gap={r}: {nondose_run_dist[r]:4d} {bar}")

# AN: same analysis
print(f"\nAN DOSE runs:")
an_dose_runs_all = []
an_nondose_runs_all = []
for entry in an_data['entries']:
    types = [t.get('type', '?') for t in entry['tokens']]
    classified_an = [(t, 'DOSE' if t in dose_types else 'OTHER') for t in types]
    d_runs, nd_runs = get_runs(classified_an, {'DOSE'})
    an_dose_runs_all.extend(d_runs)
    an_nondose_runs_all.extend(nd_runs)

an_d_dist = Counter(an_dose_runs_all)
for r in sorted(an_d_dist.keys())[:8]:
    print(f"  run={r}: {an_d_dist[r]:4d}")

print(f"\nAN non-DOSE runs between DOSEs:")
an_nd_dist = Counter(an_nondose_runs_all)
for r in sorted(an_nd_dist.keys())[:12]:
    bar = "#" * (an_nd_dist[r] // 3)
    print(f"  gap={r}: {an_nd_dist[r]:4d} {bar}")

# ========================================================================
# 5. THE ULTIMATE TEST: DOSE position relative to long words
# ========================================================================
print("\n" + "=" * 70)
print("5. TEST ULTIME: Position DOSE relative aux mots longs")
print("=" * 70)

# In AN: DOSE usually follows 1-8 INGR tokens
# If VMS -ain/-aiin are doses, they should follow runs of "ingredient-like" words

# For each DOSE_CAND in VMS pharma, count how many non-DOSE words precede it
# (since last DOSE_CAND or start of folio)
vms_gaps_before_dose = []
for folio in sorted(pharma_lines.keys()):
    words = pharma_lines[folio]
    gap = 0
    for w, cls in words:
        if cls == 'DOSE_CAND':
            if gap > 0:
                vms_gaps_before_dose.append(gap)
            gap = 0
        else:
            gap += 1

# In AN: same
an_gaps_before_dose = []
for entry in an_data['entries']:
    types = [t.get('type', '?') for t in entry['tokens']]
    gap = 0
    for t in types:
        if t in dose_types:
            if gap > 0:
                an_gaps_before_dose.append(gap)
            gap = 0
        else:
            gap += 1

print(f"\nGap (non-DOSE words) before each DOSE token:")
print(f"{'Gap':>4s} {'VMS':>6s} {'VMS%':>6s} {'AN':>6s} {'AN%':>6s}")
print("-" * 35)
for g in range(1, 15):
    v = sum(1 for x in vms_gaps_before_dose if x == g)
    a = sum(1 for x in an_gaps_before_dose if x == g)
    vp = 100 * v / max(len(vms_gaps_before_dose), 1)
    ap = 100 * a / max(len(an_gaps_before_dose), 1)
    print(f"  {g:2d} {v:6d} {vp:5.1f}% {a:6d} {ap:5.1f}%")

vms_mean = sum(vms_gaps_before_dose) / max(len(vms_gaps_before_dose), 1)
an_mean = sum(an_gaps_before_dose) / max(len(an_gaps_before_dose), 1)
print(f"\n  VMS mean gap: {vms_mean:.2f}")
print(f"  AN mean gap:  {an_mean:.2f}")

# ========================================================================
# 6. BIGRAM TYPE PATTERNS
# ========================================================================
print("\n" + "=" * 70)
print("6. BIGRAM TYPE PATTERNS: VMS vs AN")
print("=" * 70)

# VMS bigrams
vms_bigrams = Counter()
for folio in pharma_lines:
    words = pharma_lines[folio]
    for i in range(len(words) - 1):
        bg = f"{words[i][1]} -> {words[i+1][1]}"
        vms_bigrams[bg] += 1

print("\nVMS Pharma type bigrams (top 20):")
total_bg = sum(vms_bigrams.values())
for bg, c in vms_bigrams.most_common(20):
    print(f"  {bg:35s} {c:5d} ({100*c/total_bg:4.1f}%)")

# AN bigrams using simplified categories
def simplify_an_type(t):
    if t in ('DOSE', 'QTY', 'UNIT'):
        return 'DOSE_CAND'
    elif t == 'INGR':
        return 'INGR'
    elif t in ('CONJ', 'COP', 'GRAM'):
        return 'FUNC'
    elif t == 'VERB':
        return 'VERB'
    return 'OTHER'

an_bigrams = Counter()
for entry in an_data['entries']:
    types = [simplify_an_type(t.get('type', '?')) for t in entry['tokens']]
    for i in range(len(types) - 1):
        bg = f"{types[i]} -> {types[i+1]}"
        an_bigrams[bg] += 1

print("\nAN type bigrams (simplified, top 20):")
total_an_bg = sum(an_bigrams.values())
for bg, c in an_bigrams.most_common(20):
    print(f"  {bg:35s} {c:5d} ({100*c/total_an_bg:4.1f}%)")

# KEY COMPARISON: What follows DOSE in both?
print("\n--- Que suit un DOSE ? ---")
print(f"{'Next type':20s} {'VMS%':>6s} {'AN%':>6s} {'Diff':>6s}")
print("-" * 40)
vms_after_dose = {k.split(' -> ')[1]: v for k, v in vms_bigrams.items() if k.startswith('DOSE_CAND -> ')}
an_after_dose = {k.split(' -> ')[1]: v for k, v in an_bigrams.items() if k.startswith('DOSE_CAND -> ')}
total_vms_ad = sum(vms_after_dose.values())
total_an_ad = sum(an_after_dose.values())
all_next = set(list(vms_after_dose.keys()) + list(an_after_dose.keys()))
for next_t in sorted(all_next, key=lambda x: -(vms_after_dose.get(x, 0) + an_after_dose.get(x, 0))):
    vp = 100 * vms_after_dose.get(next_t, 0) / max(total_vms_ad, 1)
    ap = 100 * an_after_dose.get(next_t, 0) / max(total_an_ad, 1)
    print(f"  {next_t:18s} {vp:5.1f}% {ap:5.1f}% {abs(vp-ap):5.1f}%")

print("\n--- Que precede un DOSE ? ---")
print(f"{'Prev type':20s} {'VMS%':>6s} {'AN%':>6s} {'Diff':>6s}")
print("-" * 40)
vms_before_dose = {k.split(' -> ')[0]: v for k, v in vms_bigrams.items() if k.endswith(' -> DOSE_CAND')}
an_before_dose = {k.split(' -> ')[0]: v for k, v in an_bigrams.items() if k.endswith(' -> DOSE_CAND')}
total_vms_bd = sum(vms_before_dose.values())
total_an_bd = sum(an_before_dose.values())
all_prev = set(list(vms_before_dose.keys()) + list(an_before_dose.keys()))
for prev_t in sorted(all_prev, key=lambda x: -(vms_before_dose.get(x, 0) + an_before_dose.get(x, 0))):
    vp = 100 * vms_before_dose.get(prev_t, 0) / max(total_vms_bd, 1)
    ap = 100 * an_before_dose.get(prev_t, 0) / max(total_an_bd, 1)
    print(f"  {prev_t:18s} {vp:5.1f}% {ap:5.1f}% {abs(vp-ap):5.1f}%")

# ========================================================================
# 7. THE SMOKING GUN TEST: DOSE-DOSE adjacency
# ========================================================================
print("\n" + "=" * 70)
print("7. SMOKING GUN: DOSE-DOSE adjacency rate")
print("=" * 70)

# In AN, DOSE tokens often cluster (ana .ii. et grana .vi. = 5 consecutive DOSE tokens)
# If VMS -ain/-aiin are doses, they should also cluster

vms_dd = vms_bigrams.get('DOSE_CAND -> DOSE_CAND', 0)
vms_dd_pct = 100 * vms_dd / max(total_vms_ad, 1)
an_dd = an_bigrams.get('DOSE_CAND -> DOSE_CAND', 0)
an_dd_pct = 100 * an_dd / max(total_an_ad, 1)

print(f"\n  VMS: DOSE -> DOSE = {vms_dd} ({vms_dd_pct:.1f}% of post-DOSE transitions)")
print(f"  AN:  DOSE -> DOSE = {an_dd} ({an_dd_pct:.1f}% of post-DOSE transitions)")
print(f"\n  In AN, doses cluster because 'ana .ii. et grana .vi.' = 5+ DOSE tokens")
print(f"  If VMS has similar clustering, -ain/-aiin words should be adjacent frequently")

print("\n" + "=" * 70)
print("CRIB AUREA ANALYSIS COMPLETE")
print("=" * 70)
