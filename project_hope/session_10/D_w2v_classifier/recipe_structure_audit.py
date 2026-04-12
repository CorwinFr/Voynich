"""
RECIPE STRUCTURE AUDIT — Which f103r recipes follow the expected
VERB → INGR → DOSE → TEMPORAL pattern, and which DON'T?

Expected pharma recipe structure:
  [VERB] [INGR]+ [DOSE] [TEMPORAL]?  (repeat)

Score each recipe on:
1. V→I transitions (verb followed by ingredient)
2. I→D transitions (ingredient followed by dose)
3. VERB presence (at least 1 verb)
4. INGR presence (at least 2 ingredients)
5. DOSE presence (at least 1 dose)
6. Alternation regularity (not all same type in a row)
"""
import json, sys, io, os
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.dirname(__file__)
CLASSIFIER_PATH = os.path.join(BASE, 'results', 'w2v_classifier.json')
RESULTS = os.path.join(BASE, 'results')

with open(CLASSIFIER_PATH, encoding='utf-8') as f:
    data = json.load(f)

SYM = {
    'LOGO': 'L', 'DOSE_MORPH': 'D', 'INGR_XREF': '★',
    'VERB': 'V', 'GRAM': 'G', 'INGR': 'I',
    'DOSE': 'Q', 'TEMPORAL': 'T', 'PREP_FORM': 'P', '?': '·',
}

# Functional groups for transition analysis
def role_group(role):
    """Collapse roles into functional groups."""
    if role in ('VERB', 'LOGO'):
        return 'V'
    elif role in ('INGR', 'INGR_XREF'):
        return 'I'
    elif role in ('DOSE', 'DOSE_MORPH'):
        return 'D'
    elif role == 'TEMPORAL':
        return 'T'
    elif role == 'GRAM':
        return 'G'
    elif role == 'PREP_FORM':
        return 'P'
    return '·'

print('=' * 70)
print('RECIPE STRUCTURE AUDIT — f103r')
print('=' * 70)

recipe_scores = []

for recipe in data['f103r_recipes']:
    rid = recipe['id']
    n = recipe['n_words']
    tagged = recipe['tagged']

    # Build role sequence
    roles = [tw['role'] for tw in tagged]
    groups = [role_group(r) for r in roles]
    pattern = ''.join(groups)

    # Detailed pattern with symbols
    detail = ''.join(SYM.get(r, '?') for r in roles)

    # ── Metrics ──
    # Count functional roles
    n_verb = sum(1 for g in groups if g == 'V')
    n_ingr = sum(1 for g in groups if g == 'I')
    n_dose = sum(1 for g in groups if g == 'D')
    n_temp = sum(1 for g in groups if g == 'T')
    n_gram = sum(1 for g in groups if g == 'G')
    n_unk = sum(1 for g in groups if g == '·')

    # Transitions
    transitions = Counter()
    for i in range(len(groups) - 1):
        transitions[groups[i] + '→' + groups[i+1]] += 1

    vi = transitions.get('V→I', 0)  # verb → ingredient
    id_ = transitions.get('I→D', 0)  # ingredient → dose
    di = transitions.get('D→I', 0)  # dose → ingredient (new ingredient after dose)
    dv = transitions.get('D→V', 0)  # dose → verb (new instruction)
    iv = transitions.get('I→V', 0)  # ingredient → verb
    vd = transitions.get('V→D', 0)  # verb → dose (dose right after verb, unusual)
    it = transitions.get('I→T', 0)  # ingredient → temporal
    dt = transitions.get('D→T', 0)  # dose → temporal
    tv = transitions.get('T→V', 0)  # temporal → verb (new step)

    # Good transitions: V→I, I→D, D→I, D→T, T→V
    good = vi + id_ + di + dt + tv
    # Neutral: I→I (multiple ingredients), D→D (multiple doses), G→anything
    neutral = transitions.get('I→I', 0) + transitions.get('D→D', 0)
    # Bad: V→V (consecutive verbs), V→D (verb then dose, no ingredient)
    bad = transitions.get('V→V', 0) + vd

    total_transitions = sum(transitions.values())
    good_pct = good * 100 // max(total_transitions, 1)

    # Run detection: longest run of same group
    max_run = 1
    current_run = 1
    max_run_type = groups[0] if groups else ''
    for i in range(1, len(groups)):
        if groups[i] == groups[i-1]:
            current_run += 1
            if current_run > max_run:
                max_run = current_run
                max_run_type = groups[i]
        else:
            current_run = 1

    # First word role
    first_role = groups[0] if groups else '?'
    # Last word role
    last_role = groups[-1] if groups else '?'

    # ── RECIPE SCORE ──
    # Higher = more recipe-like
    score = 0
    score += min(n_verb, 3) * 10       # verbs present (max 30)
    score += min(n_ingr, 5) * 8        # ingredients present (max 40)
    score += min(n_dose, 3) * 5        # doses present (max 15)
    score += vi * 15                    # V→I transitions
    score += id_ * 10                   # I→D transitions
    score += di * 5                     # D→I transitions
    score += dt * 5                     # D→T transitions
    score -= bad * 10                   # penalty for bad transitions
    score -= max(max_run - 3, 0) * 5   # penalty for long runs
    score -= max(n_unk - 3, 0) * 3     # penalty for unknowns

    recipe_scores.append({
        'id': rid,
        'n_words': n,
        'score': score,
        'pattern': pattern,
        'detail': detail,
        'n_verb': n_verb,
        'n_ingr': n_ingr,
        'n_dose': n_dose,
        'n_temp': n_temp,
        'n_gram': n_gram,
        'n_unk': n_unk,
        'good_transitions': good,
        'good_pct': good_pct,
        'bad_transitions': bad,
        'max_run': max_run,
        'max_run_type': max_run_type,
        'first_role': first_role,
        'last_role': last_role,
        'transitions': dict(transitions),
    })

# Sort by score
recipe_scores.sort(key=lambda x: -x['score'])

# ================================================================
# DISPLAY: GOOD recipes first, then BAD
# ================================================================
print('\n' + '─' * 70)
print('RANKED BY RECIPE-LIKENESS (high = good structure)')
print('─' * 70)

for i, r in enumerate(recipe_scores):
    verdict = '✓ RECIPE' if r['score'] >= 50 else '? WEAK' if r['score'] >= 25 else '✗ ANOMALY'
    print(f'\n  #{i+1} {r["id"]} — score={r["score"]:3d} {verdict}')
    print(f'     {r["n_words"]}w: {r["n_verb"]}V {r["n_ingr"]}I {r["n_dose"]}D '
          f'{r["n_temp"]}T {r["n_gram"]}G {r["n_unk"]}·')
    print(f'     Good transitions: {r["good_transitions"]} ({r["good_pct"]}%) '
          f'| Bad: {r["bad_transitions"]} | Max run: {r["max_run"]}{r["max_run_type"]}')
    print(f'     {r["detail"]}')

# ================================================================
# ANOMALIES: recipes that DON'T follow the pattern
# ================================================================
print('\n' + '=' * 70)
print('ANOMALIES — Recipes that DON\'T look like recipes')
print('=' * 70)

anomalies = [r for r in recipe_scores if r['score'] < 25]
weak = [r for r in recipe_scores if 25 <= r['score'] < 50]
good = [r for r in recipe_scores if r['score'] >= 50]

print(f'\n  ✓ RECIPE-LIKE: {len(good)} blocks')
print(f'  ? WEAK:        {len(weak)} blocks')
print(f'  ✗ ANOMALY:     {len(anomalies)} blocks')

for r in anomalies:
    print(f'\n  ──── {r["id"]} (score={r["score"]}) ────')
    print(f'  Pattern: {r["detail"]}')
    print(f'  Roles: {r["n_verb"]}V {r["n_ingr"]}I {r["n_dose"]}D '
          f'{r["n_temp"]}T {r["n_gram"]}G {r["n_unk"]}·')

    # What's WRONG?
    problems = []
    if r['n_verb'] == 0:
        problems.append('NO VERBS')
    if r['n_ingr'] <= 1:
        problems.append(f'ONLY {r["n_ingr"]} INGREDIENT(S)')
    if r['n_dose'] == 0:
        problems.append('NO DOSES')
    if r['max_run'] >= 4:
        problems.append(f'LONG RUN of {r["max_run"]} consecutive {r["max_run_type"]}')
    if r['n_unk'] > r['n_words'] // 3:
        problems.append(f'{r["n_unk"]}/{r["n_words"]} UNKNOWN')
    if r['good_transitions'] == 0:
        problems.append('ZERO good transitions')

    print(f'  PROBLEMS: {"; ".join(problems)}')

    # What COULD it be instead of a recipe?
    hypotheses = []
    if r['n_dose'] > r['n_words'] * 0.4:
        hypotheses.append('DOSE TABLE (list of quantities)')
    if r['n_temp'] > r['n_words'] * 0.3:
        hypotheses.append('INSTRUCTIONS (temporal/procedural text)')
    if r['n_gram'] > r['n_words'] * 0.3:
        hypotheses.append('PROSE (narrative/descriptive text)')
    if r['n_ingr'] > r['n_words'] * 0.4:
        hypotheses.append('INGREDIENT LIST (simple enumeration)')
    if not hypotheses:
        hypotheses.append('UNCLEAR — mixed content')

    print(f'  HYPOTHESIS: {" / ".join(hypotheses)}')

# ================================================================
# TRANSITION MATRIX: aggregate across all recipes
# ================================================================
print('\n' + '=' * 70)
print('AGGREGATE TRANSITION MATRIX')
print('=' * 70)

agg_trans = Counter()
for r in recipe_scores:
    for t, c in r['transitions'].items():
        agg_trans[t] += c

# Build matrix
roles_order = ['V', 'I', 'D', 'T', 'G', 'P', '·']
print(f'\n{"":>6s}', end='')
for to_r in roles_order:
    print(f'{to_r:>6s}', end='')
print()

for from_r in roles_order:
    print(f'{from_r:>6s}', end='')
    for to_r in roles_order:
        n = agg_trans.get(f'{from_r}→{to_r}', 0)
        if n > 0:
            print(f'{n:6d}', end='')
        else:
            print(f'{"·":>6s}', end='')
    print()

# Highlight pharma-relevant transitions
print('\nPHARMA transitions (expected in recipes):')
for trans, label in [('V→I', 'verb→ingredient'), ('I→D', 'ingredient→dose'),
                     ('D→I', 'dose→ingredient'), ('D→T', 'dose→temporal'),
                     ('T→V', 'temporal→verb'), ('I→I', 'ingredient list')]:
    n = agg_trans.get(trans, 0)
    print(f'  {trans} ({label}): {n}')

print('\nANOMALOUS transitions:')
for trans, label in [('V→V', 'consecutive verbs'), ('V→D', 'verb→dose (no ingr)'),
                     ('D→D', 'consecutive doses'), ('·→·', 'consecutive unknowns')]:
    n = agg_trans.get(trans, 0)
    if n > 0:
        print(f'  {trans} ({label}): {n}')

# Save
results = {
    'recipe_scores': recipe_scores,
    'n_good': len(good),
    'n_weak': len(weak),
    'n_anomaly': len(anomalies),
    'anomaly_ids': [r['id'] for r in anomalies],
    'aggregate_transitions': dict(agg_trans),
}
with open(os.path.join(RESULTS, 'recipe_structure_audit.json'), 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print('\nSaved recipe_structure_audit.json')
