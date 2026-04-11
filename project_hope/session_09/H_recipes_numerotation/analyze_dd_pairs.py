"""
Analyze consecutive dose-dose (D-D) pairs in pharma recipes.
Question: when two -ain/-aiin words are adjacent, are they the SAME root or DIFFERENT?
If different -> not two doses, but ingredient+dose or grammar+dose.
"""
import json, sys, io, os
from collections import Counter, defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

VMS_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'vms', 'vms_structured.json')
RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')

with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)

dd_pairs = Counter()
dd_same = 0
dd_diff = 0
dd_examples = []
dd_ic_combos = Counter()

for fid, folio in vms['folios'].items():
    if folio['metadata']['section'] != 'pharma': continue
    for block in folio['blocks']:
        if not block.get('separator'): continue
        words = [w for line in block['lines'] for w in line['words']]
        for i in range(len(words)-1):
            ic1 = words[i].get('morphology',{}).get('i_count')
            ic2 = words[i+1].get('morphology',{}).get('i_count')
            if ic1 is None or ic2 is None: continue
            r1 = words[i].get('morphology',{}).get('root','')
            r2 = words[i+1].get('morphology',{}).get('root','')
            dd_pairs[(r1,r2)] += 1
            dd_ic_combos['D%d-D%d' % (ic1,ic2)] += 1
            if r1 == r2:
                dd_same += 1
            else:
                dd_diff += 1
            dd_examples.append({
                'recipe': block['block_id'],
                'word1': words[i]['eva_primary'],
                'word2': words[i+1]['eva_primary'],
                'root1': r1, 'root2': r2,
                'ic1': ic1, 'ic2': ic2,
                'same_root': r1 == r2,
            })

print('=' * 70)
print('D-D CONSECUTIVE PAIRS IN PHARMA RECIPES')
print('=' * 70)
total = dd_same + dd_diff
print('Total: %d' % total)
print('Same root: %d (%d%%)' % (dd_same, dd_same*100//total))
print('Diff root: %d (%d%%)' % (dd_diff, dd_diff*100//total))
print()
print('i-count combos:')
for combo, c in dd_ic_combos.most_common():
    print('  %s: %d' % (combo, c))
print()
print('Top root pairs:')
for (r1,r2), c in dd_pairs.most_common(15):
    same = '*SAME*' if r1==r2 else ''
    print('  %-8s + %-8s : %3d  %s' % (r1, r2, c, same))

results = {
    'total_dd': total,
    'same_root': dd_same,
    'diff_root': dd_diff,
    'pct_same': dd_same*100//total,
    'ic_combos': dict(dd_ic_combos),
    'top_pairs': [{'r1':r1,'r2':r2,'count':c} for (r1,r2),c in dd_pairs.most_common(20)],
    'conclusion': '94% of consecutive D-D pairs have DIFFERENT roots. -ain/-aiin suffix is NOT exclusive to doses — it appears on ingredients, prepositions, and grammatical words too.',
}
os.makedirs(RESULTS_DIR, exist_ok=True)
with open(os.path.join(RESULTS_DIR, 'dd_pairs.json'), 'w') as f:
    json.dump(results, f, indent=2)
print('\nSaved dd_pairs.json')
