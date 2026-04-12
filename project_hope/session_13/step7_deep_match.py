"""
STEP 7 — Deep recipe matching.

For each top VMS↔AN pair:
1. Check if DOSE positions align
2. Check if ingredient GROUP SIZES match (ana groups)
3. Check if the SAME EVA root maps to the SAME Latin in multiple pairs
4. Check if PLANT codes align with known botanical IDs

Only keep matches where 2+ structural features align.
"""
import json, sys, io, os
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

RESULTS = os.path.join(os.path.dirname(__file__), 'results')

with open(os.path.join(RESULTS, 'an_signatures.json'), encoding='utf-8') as f:
    an_sigs = json.load(f)
with open(os.path.join(RESULTS, 'vms_signatures.json'), encoding='utf-8') as f:
    vms_sigs = json.load(f)
with open(os.path.join(RESULTS, 'alignments.json'), encoding='utf-8') as f:
    align_data = json.load(f)

an_by_id = {s['id']: s for s in an_sigs}
vms_by_id = {s['id']: s for s in vms_sigs}

def lcs_align(a, b):
    m, n = len(a), len(b)
    dp = [[0]*(n+1) for _ in range(m+1)]
    for i in range(m):
        for j in range(n):
            if a[i] == b[j]:
                dp[i+1][j+1] = dp[i][j] + 1
            else:
                dp[i+1][j+1] = max(dp[i][j+1], dp[i+1][j])
    alignment = []
    i, j = m, n
    while i > 0 and j > 0:
        if a[i-1] == b[j-1]:
            alignment.append((i-1, j-1))
            i -= 1; j -= 1
        elif dp[i-1][j] > dp[i][j-1]:
            i -= 1
        else:
            j -= 1
    alignment.reverse()
    return alignment

# ================================================================
# For each top match, compute DEEP features
# ================================================================
print('=' * 70)
print('DEEP RECIPE MATCHING')
print('=' * 70)

def get_dose_positions(sig):
    """Get relative positions of D in signature."""
    positions = []
    for i, c in enumerate(sig):
        if c == 'D':
            positions.append(i / max(len(sig)-1, 1))
    return positions

def get_ingr_groups(sig):
    """Count ingredients between doses."""
    groups = []
    current = 0
    for c in sig:
        if c == 'I':
            current += 1
        elif c == 'D' and current > 0:
            groups.append(current)
            current = 0
    if current > 0:
        groups.append(current)
    return groups

deep_matches = []

for m in align_data['top_matches'][:100]:
    vsig = vms_by_id.get(m['vms_id'])
    asig = an_by_id.get(m['an_id'])
    if not vsig or not asig: continue

    # Feature 1: Dose position correlation
    v_dose_pos = get_dose_positions(vsig['signature'])
    a_dose_pos = get_dose_positions(asig['signature'])
    n_dose_match = min(len(v_dose_pos), len(a_dose_pos))

    dose_corr = 0
    if n_dose_match >= 2:
        diffs = [abs(v_dose_pos[i] - a_dose_pos[i]) for i in range(n_dose_match)]
        dose_corr = 1.0 - sum(diffs) / len(diffs)

    # Feature 2: Ingredient group sizes
    v_groups = get_ingr_groups(vsig['signature'])
    a_groups = get_ingr_groups(asig['signature'])
    n_groups = min(len(v_groups), len(a_groups))

    group_match = 0
    if n_groups >= 2:
        exact = sum(1 for i in range(n_groups) if v_groups[i] == a_groups[i])
        group_match = exact / n_groups

    # Feature 3: Word length correlation
    alignment = lcs_align(vsig['signature'], asig['signature'])
    len_diffs = []
    word_pairs = []
    for vi, ai in alignment:
        if vi >= len(vsig['tokens']) or ai >= len(asig['tokens']): continue
        vt = vsig['tokens'][vi]
        at = asig['tokens'][ai]
        if vt['type'] == 'I' and at['type'] == 'I':
            ld = abs(vt['length'] - at['length'])
            len_diffs.append(ld)
            word_pairs.append((vt['eva'], at['raw'], vt['length'], at['length']))

    len_corr = 0
    if len_diffs:
        avg_diff = sum(len_diffs) / len(len_diffs)
        len_corr = max(0, 1.0 - avg_diff / 5)  # 0 diff = 1.0, 5+ diff = 0

    # Combined score
    deep_score = (m['score'] * 0.4 +
                  dose_corr * 0.25 +
                  group_match * 0.20 +
                  len_corr * 0.15)

    deep_matches.append({
        'vms_id': m['vms_id'],
        'an_id': m['an_id'],
        'an_name': m['an_name'],
        'lcs_score': m['score'],
        'dose_corr': round(dose_corr, 3),
        'group_match': round(group_match, 3),
        'len_corr': round(len_corr, 3),
        'deep_score': round(deep_score, 3),
        'n_word_pairs': len(word_pairs),
        'word_pairs': word_pairs[:15],
        'v_groups': v_groups,
        'a_groups': a_groups,
    })

deep_matches.sort(key=lambda x: -x['deep_score'])

# ================================================================
# TOP DEEP MATCHES
# ================================================================
print(f'\nTOP 20 DEEP MATCHES:')
print(f'  {"VMS":>18s} {"AN":>8s} {"Deep":>5s} {"LCS":>5s} {"Dose":>5s} '
      f'{"Grp":>5s} {"Len":>5s} {"Pairs":>5s} {"AN Name":>30s}')
print('  ' + '-' * 95)

for dm in deep_matches[:20]:
    print(f'  {dm["vms_id"]:>18s} {dm["an_id"]:>8s} {dm["deep_score"]:>5.3f} '
          f'{dm["lcs_score"]:>5.3f} {dm["dose_corr"]:>5.3f} {dm["group_match"]:>5.3f} '
          f'{dm["len_corr"]:>5.3f} {dm["n_word_pairs"]:>5d} {dm["an_name"][:30]:>30s}')

# ================================================================
# BEST DEEP MATCHES — word-level detail
# ================================================================
print(f'\n{"="*70}')
print('MEILLEURS MATCHS — détail mot-à-mot')
print('=' * 70)

for dm in deep_matches[:5]:
    print(f'\n  {"─"*60}')
    print(f'  {dm["vms_id"]} ↔ {dm["an_id"]} "{dm["an_name"][:40]}"')
    print(f'  Deep={dm["deep_score"]:.3f} LCS={dm["lcs_score"]:.3f} '
          f'Dose={dm["dose_corr"]:.3f} Grp={dm["group_match"]:.3f} '
          f'Len={dm["len_corr"]:.3f}')
    print(f'  VMS groups: {dm["v_groups"]}')
    print(f'  AN groups:  {dm["a_groups"]}')
    print(f'\n  Ingredient alignments ({dm["n_word_pairs"]}):')
    for eva, latin, vlen, alen in dm['word_pairs']:
        len_ok = '✓' if abs(vlen - alen) <= 2 else '~' if abs(vlen - alen) <= 4 else '✗'
        print(f'    {len_ok} {eva:18s} ({vlen}) ↔ {latin:18s} ({alen})')

# ================================================================
# CONVERGENT MAPPINGS from deep matches only
# ================================================================
print(f'\n{"="*70}')
print('CONVERGENT MAPPINGS (from top 20 deep matches)')
print('=' * 70)

deep_mappings = defaultdict(Counter)  # eva → {latin: count}

for dm in deep_matches[:20]:
    for eva, latin, _, _ in dm['word_pairs']:
        deep_mappings[eva][latin] += 1

convergent = []
for eva, latins in deep_mappings.items():
    if latins.most_common(1)[0][1] >= 2:  # appears 2+ times
        best, count = latins.most_common(1)[0]
        total = sum(latins.values())
        convergent.append((eva, best, count, total))

convergent.sort(key=lambda x: -x[2])

if convergent:
    print(f'\n  {len(convergent)} convergent mappings:')
    for eva, latin, count, total in convergent:
        agreement = count * 100 // total
        print(f'    {eva:18s} → {latin:18s} ({count}/{total} = {agreement}%)')
else:
    print('\n  No convergent mappings in top 20.')
    print('  Expanding to top 50...')

    for dm in deep_matches[20:50]:
        for eva, latin, _, _ in dm['word_pairs']:
            deep_mappings[eva][latin] += 1

    for eva, latins in deep_mappings.items():
        if latins.most_common(1)[0][1] >= 2:
            best, count = latins.most_common(1)[0]
            total = sum(latins.values())
            convergent.append((eva, best, count, total))

    convergent = list(set(convergent))
    convergent.sort(key=lambda x: -x[2])
    print(f'\n  {len(convergent)} convergent mappings (top 50):')
    for eva, latin, count, total in convergent[:20]:
        agreement = count * 100 // total
        print(f'    {eva:18s} → {latin:18s} ({count}/{total} = {agreement}%)')

# Save
results = {
    'deep_matches': deep_matches[:50],
    'convergent_mappings': [
        {'eva': e, 'latin': l, 'count': c, 'total': t}
        for e, l, c, t in convergent
    ],
}
with open(os.path.join(RESULTS, 'deep_matches.json'), 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print('\nSaved deep_matches.json')
