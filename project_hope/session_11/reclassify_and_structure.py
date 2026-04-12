"""
RECLASSIFY FUNC → INGR based on dose-adjacency signal.
Then analyze the REAL recipe structure that emerges.

Rule: if a FUNC code has >15% after_dose OR before_dose, it's probably INGR.
Also: if a FUNC code has specific suffixes (-ol, -ar, -or) it's content, not grammar.
"""
import json, sys, io, os
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DECODE_PATH = os.path.join(os.path.dirname(__file__), 'structural_decode.json')

with open(DECODE_PATH, encoding='utf-8') as f:
    data = json.load(f)

blocks = data['blocks']

# ================================================================
# 1. Compute dose-adjacency for each FUNC code
# ================================================================
func_dose = defaultdict(lambda: {'count': 0, 'after_dose': 0, 'before_dose': 0,
                                  'suffixes': Counter()})

for db in blocks:
    decoded = db['decoded']
    n = len(decoded)
    for i, dw in enumerate(decoded):
        if not dw['code'].startswith('FUNC_'): continue
        base = dw['code'].split('.')[0]
        func_dose[base]['count'] += 1
        if dw['suffix']:
            func_dose[base]['suffixes'][dw['suffix']] += 1
        if i > 0 and decoded[i-1]['type'] == 'DOSE':
            func_dose[base]['after_dose'] += 1
        if i < n-1 and decoded[i+1]['type'] == 'DOSE':
            func_dose[base]['before_dose'] += 1

# Reclassify
reclassified = {}
for code, info in func_dose.items():
    n = info['count']
    if n < 5: continue
    ad = info['after_dose'] * 100 // n
    bd = info['before_dose'] * 100 // n
    dose_adj = ad + bd

    # Content suffixes suggest ingredient
    content_suf = sum(info['suffixes'].get(s, 0) for s in ['ol','ar','or','air','eol'])
    content_pct = content_suf * 100 // max(n, 1)

    if dose_adj > 30 or (dose_adj > 15 and content_pct > 20):
        reclassified[code] = 'INGR*'
    elif dose_adj > 15:
        reclassified[code] = 'INGR?'

print(f'Reclassified {len(reclassified)} FUNC codes as INGR')
for code in sorted(reclassified.keys(), key=lambda c: -func_dose[c]['count']):
    info = func_dose[code]
    n = info['count']
    ad = info['after_dose'] * 100 // n
    bd = info['before_dose'] * 100 // n
    new_type = reclassified[code]
    print(f'  {code:10s} (n={n:4d}) ad={ad:2d}% bd={bd:2d}% → {new_type}')

# ================================================================
# 2. Rebuild blocks with reclassification
# ================================================================
type_counts_new = Counter()
for db in blocks:
    for dw in db['decoded']:
        base = dw['code'].split('.')[0]
        if base in reclassified:
            dw['type_v2'] = reclassified[base]
        else:
            dw['type_v2'] = dw['type']
        type_counts_new[dw['type_v2']] += 1

print(f'\n{"="*70}')
print('RECLASSIFIED TYPE DISTRIBUTION')
print('=' * 70)

total = sum(type_counts_new.values())
for t, n in type_counts_new.most_common():
    pct = n * 100 // total
    bar = '█' * (pct // 2)
    print(f'  {t:8s}: {n:5d} ({pct:2d}%) {bar}')

# ================================================================
# 3. RECIPE STRUCTURE with reclassification
# ================================================================
print(f'\n{"="*70}')
print('f103r — RECLASSIFIED RECIPE STRUCTURE')
print('=' * 70)

SYM = {'VERB': 'V', 'PLANT': 'P', 'INGR': 'I', 'INGR*': 'i', 'INGR?': '~',
       'DOSE': 'D', 'FUNC': 'F', 'LOGO': 'L', 'UNK': '·'}

for db in blocks:
    if db['folio'] != 'f103r': continue
    pattern = ''.join(SYM.get(dw['type_v2'], '?') for dw in db['decoded'])

    # Count
    tc = Counter(dw['type_v2'] for dw in db['decoded'])
    n_content = tc.get('INGR', 0) + tc.get('INGR*', 0) + tc.get('INGR?', 0) + tc.get('PLANT', 0)
    n_dose = tc.get('DOSE', 0)
    n_func = tc.get('FUNC', 0)

    print(f'\n  {db["block_id"]}: {pattern}')
    print(f'    {n_content} content(I+P) | {n_dose}D | {n_func}F | {tc.get("VERB",0)}V {tc.get("LOGO",0)}L')

# ================================================================
# 4. TRANSITION MATRIX (reclassified)
# ================================================================
print(f'\n{"="*70}')
print('TRANSITIONS (reclassified)')
print('=' * 70)

bi2 = Counter()
for db in blocks:
    types = [dw['type_v2'] for dw in db['decoded']]
    for i in range(len(types) - 1):
        # Collapse INGR variants
        a = 'INGR' if types[i].startswith('INGR') else types[i]
        b = 'INGR' if types[i+1].startswith('INGR') else types[i+1]
        bi2[(a, b)] += 1

total_bi = sum(bi2.values())
print(f'\n{"From→To":>20s} {"Count":>6s} {"Pct":>5s}')
print('-' * 35)
for (a, b), count in bi2.most_common(20):
    pct = count * 100 // total_bi
    print(f'{a:>8s}→{b:<8s} {count:>6d} {pct:>4d}%')

# ================================================================
# 5. RECIPE FORMULA — what's the typical structure?
# ================================================================
print(f'\n{"="*70}')
print('RECIPE FORMULA')
print('=' * 70)

# For each block, compute the CONTENT/DOSE/FUNC ratios
all_content_pct = []
all_dose_pct = []
all_func_pct = []

for db in blocks:
    n = len(db['decoded'])
    tc = Counter(dw['type_v2'] for dw in db['decoded'])
    content = tc.get('INGR', 0) + tc.get('INGR*', 0) + tc.get('INGR?', 0) + tc.get('PLANT', 0)
    dose = tc.get('DOSE', 0)
    func = tc.get('FUNC', 0)

    all_content_pct.append(content * 100 // max(n, 1))
    all_dose_pct.append(dose * 100 // max(n, 1))
    all_func_pct.append(func * 100 // max(n, 1))

def median(lst):
    s = sorted(lst)
    return s[len(s)//2]

print(f'  CONTENT (INGR+PLANT):  mean={sum(all_content_pct)//len(all_content_pct)}%  '
      f'median={median(all_content_pct)}%')
print(f'  DOSE:                  mean={sum(all_dose_pct)//len(all_dose_pct)}%  '
      f'median={median(all_dose_pct)}%')
print(f'  FUNC (pure grammar):   mean={sum(all_func_pct)//len(all_func_pct)}%  '
      f'median={median(all_func_pct)}%')

print(f'\n  AN reference: INGR ~50%, DOSE ~12%, GRAM ~25%, VERB ~4%')
print(f'  VMS reclassified: INGR+PLANT ~{sum(all_content_pct)//len(all_content_pct)}%, '
      f'DOSE ~{sum(all_dose_pct)//len(all_dose_pct)}%, '
      f'FUNC ~{sum(all_func_pct)//len(all_func_pct)}%')

# ================================================================
# 6. INGREDIENT SEQUENCES — typical list length between doses
# ================================================================
print(f'\n{"="*70}')
print('INGREDIENT SEQUENCES — combien d\'ingrédients entre 2 doses?')
print('=' * 70)

seq_lengths = []
for db in blocks:
    current_seq = 0
    for dw in db['decoded']:
        t = dw['type_v2']
        is_content = t in ('INGR', 'INGR*', 'INGR?', 'PLANT')
        if is_content:
            current_seq += 1
        elif t == 'DOSE' and current_seq > 0:
            seq_lengths.append(current_seq)
            current_seq = 0
        # FUNC doesn't break the sequence (it's grammar between ingredients)

if seq_lengths:
    sc = Counter(seq_lengths)
    print(f'  Total sequences: {len(seq_lengths)}')
    print(f'  Mean: {sum(seq_lengths)/len(seq_lengths):.1f}')
    print(f'  Median: {median(seq_lengths)}')
    print(f'  Distribution:')
    for length in sorted(sc.keys()):
        count = sc[length]
        bar = '█' * (count // 3)
        print(f'    {length:2d} ingrédients: {count:4d} ({count*100//len(seq_lengths):2d}%) {bar}')

    print(f'\n  AN reference: ANA groups of 2-4 ingredients are most common')

# Save
out = {
    'reclassified_codes': reclassified,
    'type_distribution_v2': dict(type_counts_new),
    'recipe_formula': {
        'content_pct_mean': sum(all_content_pct) // len(all_content_pct),
        'dose_pct_mean': sum(all_dose_pct) // len(all_dose_pct),
        'func_pct_mean': sum(all_func_pct) // len(all_func_pct),
    },
    'ingredient_seq_lengths': dict(Counter(seq_lengths)),
}
with open(os.path.join(os.path.dirname(__file__), 'reclassified_analysis.json'), 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=2, ensure_ascii=False)

print('\nSaved reclassified_analysis.json')
