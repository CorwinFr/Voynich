"""
STEP 3 — Align VMS and AN signatures.

Use LCS (Longest Common Subsequence) on type signatures.
Then word-level alignment on top matches.
"""
import json, sys, io, os
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

RESULTS = os.path.join(os.path.dirname(__file__), 'results')

with open(os.path.join(RESULTS, 'an_signatures.json'), encoding='utf-8') as f:
    an_sigs = json.load(f)
with open(os.path.join(RESULTS, 'vms_signatures.json'), encoding='utf-8') as f:
    vms_sigs = json.load(f)

def lcs_length(a, b):
    """Fast LCS length computation."""
    m, n = len(a), len(b)
    if m > n:
        a, b = b, a
        m, n = n, m
    prev = [0] * (n + 1)
    for i in range(m):
        curr = [0] * (n + 1)
        for j in range(n):
            if a[i] == b[j]:
                curr[j+1] = prev[j] + 1
            else:
                curr[j+1] = max(curr[j], prev[j+1])
        prev = curr
    return prev[n]

def lcs_align(a, b):
    """Full LCS with backtracking to get alignment."""
    m, n = len(a), len(b)
    dp = [[0]*(n+1) for _ in range(m+1)]
    for i in range(m):
        for j in range(n):
            if a[i] == b[j]:
                dp[i+1][j+1] = dp[i][j] + 1
            else:
                dp[i+1][j+1] = max(dp[i][j+1], dp[i+1][j])

    # Backtrack
    alignment = []
    i, j = m, n
    while i > 0 and j > 0:
        if a[i-1] == b[j-1]:
            alignment.append((i-1, j-1))
            i -= 1
            j -= 1
        elif dp[i-1][j] > dp[i][j-1]:
            i -= 1
        else:
            j -= 1
    alignment.reverse()
    return alignment

# ================================================================
# ALIGN ALL PAIRS
# ================================================================
print('Aligning VMS vs AN signatures...')
print(f'  {len(vms_sigs)} VMS × {len(an_sigs)} AN = {len(vms_sigs)*len(an_sigs)} pairs')

all_matches = []

for vi, vsig in enumerate(vms_sigs):
    v_sig = vsig['signature']
    v_len = len(v_sig)
    if v_len < 5:
        continue

    best_for_block = []

    for ai, asig in enumerate(an_sigs):
        a_sig = asig['signature']
        a_len = len(a_sig)

        # Pre-filter: size ratio
        if max(v_len, a_len) > 3 * min(v_len, a_len):
            continue

        # LCS
        lcs = lcs_length(v_sig, a_sig)
        score = lcs / max(v_len, a_len)

        if score > 0.35:
            best_for_block.append({
                'vms_id': vsig['id'],
                'an_id': asig['id'],
                'an_name': asig['name'],
                'score': round(score, 3),
                'lcs': lcs,
                'v_len': v_len,
                'a_len': a_len,
            })

    best_for_block.sort(key=lambda x: -x['score'])
    all_matches.extend(best_for_block[:5])  # top 5 per VMS block

    if (vi + 1) % 50 == 0:
        print(f'  {vi+1}/{len(vms_sigs)} done...')

all_matches.sort(key=lambda x: -x['score'])

# ================================================================
# TOP MATCHES
# ================================================================
print(f'\n{"="*70}')
print(f'TOP 30 MATCHES (score > 0.35)')
print('=' * 70)

for m in all_matches[:30]:
    print(f'  {m["score"]:.3f} {m["vms_id"]:20s} ↔ {m["an_id"]:8s} '
          f'"{m["an_name"][:35]}" (LCS={m["lcs"]}, V={m["v_len"]}, A={m["a_len"]})')

# ================================================================
# DETAILED ALIGNMENT for top 10
# ================================================================
print(f'\n{"="*70}')
print('ALIGNEMENTS DÉTAILLÉS (top 10)')
print('=' * 70)

top10 = all_matches[:10]

detailed = []
for m in top10:
    # Find the original signatures
    vsig = next(s for s in vms_sigs if s['id'] == m['vms_id'])
    asig = next(s for s in an_sigs if s['id'] == m['an_id'])

    # Full alignment
    alignment = lcs_align(vsig['signature'], asig['signature'])

    print(f'\n  {m["vms_id"]} ↔ {m["an_id"]} (score={m["score"]:.3f})')
    print(f'  VMS sig: {vsig["signature"][:60]}...')
    print(f'  AN sig:  {asig["signature"][:60]}...')
    print(f'  Aligned {len(alignment)} positions')

    # Word-level alignment
    word_pairs = []
    for vi, ai in alignment:
        if vi < len(vsig['tokens']) and ai < len(asig['tokens']):
            vt = vsig['tokens'][vi]
            at = asig['tokens'][ai]
            if vt['type'] == 'I' and at['type'] == 'I':
                word_pairs.append({
                    'vms_eva': vt['eva'],
                    'vms_code': vt['code'],
                    'an_raw': at['raw'],
                    'an_ref': at.get('ref', ''),
                    'vms_len': vt['length'],
                    'an_len': at['length'],
                })

    if word_pairs:
        print(f'  Ingredient pairs ({len(word_pairs)}):')
        for wp in word_pairs[:10]:
            len_match = '✓' if abs(wp['vms_len'] - wp['an_len']) <= 2 else ' '
            print(f'    {len_match} {wp["vms_eva"]:18s} ↔ {wp["an_raw"]:18s} '
                  f'({wp["vms_len"]}↔{wp["an_len"]} chars) [{wp["an_ref"]}]')

    detailed.append({
        'vms_id': m['vms_id'],
        'an_id': m['an_id'],
        'score': m['score'],
        'word_pairs': word_pairs,
    })

# ================================================================
# CONVERGENCE: which EVA→Latin mappings appear in multiple pairs?
# ================================================================
print(f'\n{"="*70}')
print('CONVERGENCE — mappings qui apparaissent dans 2+ paires')
print('=' * 70)

mapping_counts = Counter()
mapping_details = {}

for d in detailed:
    for wp in d['word_pairs']:
        key = (wp['vms_eva'], wp['an_raw'])
        mapping_counts[key] += 1
        if key not in mapping_details:
            mapping_details[key] = []
        mapping_details[key].append(d['vms_id'] + '↔' + d['an_id'])

convergent = [(k, c) for k, c in mapping_counts.items() if c >= 2]
convergent.sort(key=lambda x: -x[1])

if convergent:
    print(f'\n  {len(convergent)} mappings convergents:')
    for (eva, latin), count in convergent[:20]:
        sources = mapping_details[(eva, latin)]
        print(f'    {eva:18s} → {latin:18s} ({count}x) from {", ".join(sources[:3])}')
else:
    print(f'\n  Aucun mapping convergent (top 10 seulement)')
    print(f'  Élargissons aux top 50...')

    # Redo with all matches
    all_detailed_pairs = []
    for m in all_matches[:50]:
        vsig = next(s for s in vms_sigs if s['id'] == m['vms_id'])
        asig = next(s for s in an_sigs if s['id'] == m['an_id'])
        alignment = lcs_align(vsig['signature'], asig['signature'])
        for vi, ai in alignment:
            if vi < len(vsig['tokens']) and ai < len(asig['tokens']):
                vt = vsig['tokens'][vi]
                at = asig['tokens'][ai]
                if vt['type'] == 'I' and at['type'] == 'I':
                    key = (vt['eva'], at['raw'])
                    mapping_counts[key] += 1
                    if key not in mapping_details:
                        mapping_details[key] = []
                    mapping_details[key].append(m['vms_id'])

    convergent = [(k, c) for k, c in mapping_counts.items() if c >= 2]
    convergent.sort(key=lambda x: -x[1])
    print(f'\n  {len(convergent)} mappings convergents (top 50 matchs):')
    for (eva, latin), count in convergent[:30]:
        print(f'    {eva:18s} → {latin:18s} ({count}x)')

# Save
results = {
    'n_matches': len(all_matches),
    'top_matches': all_matches[:50],
    'detailed_alignments': detailed,
    'convergent_mappings': [
        {'eva': eva, 'latin': latin, 'count': count}
        for (eva, latin), count in convergent[:50]
    ],
}

with open(os.path.join(RESULTS, 'alignments.json'), 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f'\nTotal matches (score>0.35): {len(all_matches)}')
print('Saved alignments.json')
