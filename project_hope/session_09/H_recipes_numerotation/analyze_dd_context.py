"""
List ALL consecutive D-D pairs with their FULL context (5 words before, 5 after).
Focus on understanding WHAT these adjacent dose-like words actually are.
"""
import json, sys, io, os
from collections import Counter, defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

VMS_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'vms', 'vms_structured.json')
RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')
LOGOGRAMS = {'o','l','d','r','v','x','k','m','f','t','y','c','s','sh','p','air'}

with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)

# Collect ALL D-D pairs with full context
all_dd = []

for fid, folio in vms['folios'].items():
    if folio['metadata']['section'] != 'pharma': continue
    for block in folio['blocks']:
        if not block.get('separator'): continue
        words = [w for line in block['lines'] for w in line['words']]

        for i in range(len(words) - 1):
            ic1 = words[i].get('morphology', {}).get('i_count')
            ic2 = words[i+1].get('morphology', {}).get('i_count')
            if ic1 is None or ic2 is None:
                continue

            w1 = words[i]
            w2 = words[i+1]
            r1 = w1.get('morphology', {}).get('root', '')
            r2 = w2.get('morphology', {}).get('root', '')

            # Context: 5 before, 5 after
            before = []
            for j in range(max(0, i-5), i):
                eva = words[j]['eva_primary']
                if eva in LOGOGRAMS:
                    before.append('{%s}' % eva)
                elif words[j].get('morphology', {}).get('i_count') is not None:
                    before.append('[D%d:%s]' % (words[j]['morphology']['i_count'], eva))
                else:
                    before.append(eva)

            after = []
            for j in range(i+2, min(len(words), i+7)):
                eva = words[j]['eva_primary']
                if eva in LOGOGRAMS:
                    after.append('{%s}' % eva)
                elif words[j].get('morphology', {}).get('i_count') is not None:
                    after.append('[D%d:%s]' % (words[j]['morphology']['i_count'], eva))
                else:
                    after.append(eva)

            all_dd.append({
                'recipe': block['block_id'],
                'pos': i,
                'w1': w1['eva_primary'],
                'w2': w2['eva_primary'],
                'r1': r1,
                'r2': r2,
                'ic1': ic1,
                'ic2': ic2,
                'same_root': r1 == r2,
                'before': before,
                'after': after,
            })

# ================================================================
# Display ALL pairs grouped by type
# ================================================================

# Type 1: SAME root, different i-count (D1+D2 or D2+D1)
same_diff_ic = [dd for dd in all_dd if dd['same_root'] and dd['ic1'] != dd['ic2']]
# Type 2: SAME root, same i-count (D1+D1 or D2+D2)
same_same_ic = [dd for dd in all_dd if dd['same_root'] and dd['ic1'] == dd['ic2']]
# Type 3: DIFFERENT root, same i-count
diff_same_ic = [dd for dd in all_dd if not dd['same_root'] and dd['ic1'] == dd['ic2']]
# Type 4: DIFFERENT root, different i-count
diff_diff_ic = [dd for dd in all_dd if not dd['same_root'] and dd['ic1'] != dd['ic2']]

print('=' * 70)
print('TOUTES LES PAIRES D-D CONSECUTIVES (%d total)' % len(all_dd))
print('=' * 70)

print('\nType 1: MEME racine, i-count DIFFERENT (%d cas)' % len(same_diff_ic))
print('  = le MEME mot avec une DOSE differente?')
print('-' * 70)
for dd in same_diff_ic:
    ctx_before = ' '.join(dd['before'][-3:])
    ctx_after = ' '.join(dd['after'][:3])
    print('  %s  ...%s [**D%d:%s**] [**D%d:%s**] %s...' % (
        dd['recipe'], ctx_before, dd['ic1'], dd['w1'], dd['ic2'], dd['w2'], ctx_after))

print('\n\nType 2: MEME racine, MEME i-count (%d cas)' % len(same_same_ic))
print('  = repetition? erreur? emphase?')
print('-' * 70)
for dd in same_same_ic:
    ctx_before = ' '.join(dd['before'][-3:])
    ctx_after = ' '.join(dd['after'][:3])
    print('  %s  ...%s [D%d:%s] [D%d:%s] %s...' % (
        dd['recipe'], ctx_before, dd['ic1'], dd['w1'], dd['ic2'], dd['w2'], ctx_after))

print('\n\nType 3: DIFF racine, MEME i-count — D1+D1 (%d cas)' %
      sum(1 for dd in diff_same_ic if dd['ic1'] == 1))
print('  = deux mots differents avec le meme suffixe')
print('-' * 70)
for dd in diff_same_ic:
    if dd['ic1'] != 1: continue
    ctx_before = ' '.join(dd['before'][-3:])
    ctx_after = ' '.join(dd['after'][:3])
    print('  %s  ...%s [D1:%s(%s)] [D1:%s(%s)] %s...' % (
        dd['recipe'], ctx_before, dd['w1'], dd['r1'], dd['w2'], dd['r2'], ctx_after))

print('\n\nType 3b: DIFF racine, MEME i-count — D2+D2 (%d cas)' %
      sum(1 for dd in diff_same_ic if dd['ic1'] == 2))
print('-' * 70)
count = 0
for dd in diff_same_ic:
    if dd['ic1'] != 2: continue
    ctx_before = ' '.join(dd['before'][-3:])
    ctx_after = ' '.join(dd['after'][:3])
    print('  %s  ...%s [D2:%s(%s)] [D2:%s(%s)] %s...' % (
        dd['recipe'], ctx_before, dd['w1'], dd['r1'], dd['w2'], dd['r2'], ctx_after))
    count += 1
    if count >= 30:
        print('  ... (%d more)' % (sum(1 for dd in diff_same_ic if dd['ic1']==2) - 30))
        break

# ================================================================
# FREQUENCY of root combinations
# ================================================================
print('\n\n' + '=' * 70)
print('RACINES LES PLUS FREQUENTES DANS LES PAIRES D-D')
print('=' * 70)

r1_freq = Counter(dd['r1'] for dd in all_dd)
r2_freq = Counter(dd['r2'] for dd in all_dd)
both_freq = Counter()
for dd in all_dd:
    both_freq[dd['r1']] += 1
    both_freq[dd['r2']] += 1

print('\nRacines qui apparaissent le PLUS dans les paires D-D:')
print('%-10s %5s %5s %5s' % ('Root', 'as W1', 'as W2', 'Total'))
for root, total in both_freq.most_common(15):
    print('%-10s %5d %5d %5d' % (root, r1_freq[root], r2_freq[root], total))

# ================================================================
# KEY QUESTION: are ok/qok/ot always in the SAME position (W1 or W2)?
# ================================================================
print('\n\n' + '=' * 70)
print('POSITION DES RACINES: toujours W1 ou toujours W2?')
print('=' * 70)

for root in ['ok', 'qok', 'ot', 'd', 'r', 's', 'k', 'lk', 'ch', 'sh']:
    as_w1 = r1_freq.get(root, 0)
    as_w2 = r2_freq.get(root, 0)
    total = as_w1 + as_w2
    if total < 3: continue
    pct_w1 = as_w1 * 100 // max(total, 1)
    bias = 'W1-biased' if pct_w1 > 65 else ('W2-biased' if pct_w1 < 35 else 'BALANCED')
    print('  %-8s W1=%3d W2=%3d (%d%% W1)  %s' % (root, as_w1, as_w2, pct_w1, bias))

# Save
results = {
    'total_dd': len(all_dd),
    'type1_same_root_diff_ic': len(same_diff_ic),
    'type2_same_root_same_ic': len(same_same_ic),
    'type3_diff_root_same_ic': len(diff_same_ic),
    'type4_diff_root_diff_ic': len(diff_diff_ic),
    'root_position_bias': {root: {'w1': r1_freq.get(root,0), 'w2': r2_freq.get(root,0)}
                           for root in both_freq if both_freq[root] >= 3},
    'all_pairs': all_dd,
}
with open(os.path.join(RESULTS_DIR, 'dd_context.json'), 'w') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print('\nSaved dd_context.json')
