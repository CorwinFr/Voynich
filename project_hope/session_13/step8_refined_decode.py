"""
STEP 8 — Refined structural decode with DOSE/UNIT separation.

New classification based on suffix → function:
  -aiin/-ain    = DOSE (quantity/number, i-count = the number)
  -eey          = UNIT (unit of measurement)
  -edy/-eedy    = INGR_A (ingredient class A)
  -eol          = INGR_B (ingredient class B)
  -ol/-ar/-al/-or = FUNC (connectors, prepositions)
  -am           = TERM (sentence terminator)
  -dy           = INSTR (instruction/temporal)
  -air          = QUAL (qualifier)
  gallows initial = VERB (recipe opener)
  logogram      = LOGO (function word)
  no suffix + compound = INGR_C (ingredient, class unknown)

Also: verify that the SAME prefix appears in MULTIPLE classes (zero multiclass).
And count unique PREFIXES = number of distinct CONCEPTS.
"""
import json, sys, io, os
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

VMS_PATH = os.path.join(os.path.dirname(__file__), '..', 'vms', 'vms_structured.json')
KB_PATH = os.path.join(os.path.dirname(__file__), '..', 'knowledge_base.json')
RESULTS = os.path.join(os.path.dirname(__file__), 'results')

with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)
with open(KB_PATH, encoding='utf-8') as f:
    kb = json.load(f)

LOGOS = set(kb['logograms'].keys())
LOGO_LATIN = {eva: data['latin'] for eva, data in kb['logograms'].items()}

# Suffix → class mapping (refined)
SUFFIX_CLASS = {
    'aiin': 'DOSE', 'ain': 'DOSE', 'aiiin': 'DOSE',
    'eey': 'UNIT', 'eeey': 'UNIT',
    'edy': 'INGR_A', 'eedy': 'INGR_A',
    'eol': 'INGR_B',
    'ol': 'FUNC', 'ar': 'FUNC', 'al': 'FUNC', 'or': 'FUNC',
    'am': 'TERM', 'om': 'TERM',
    'dy': 'INSTR',
    'ey': 'INGR_C', 'air': 'QUAL',
    'chy': 'INGR_C', 'shy': 'INGR_C',
}

# ================================================================
# 1. CLASSIFY EVERY WORD — refined
# ================================================================
print('=' * 70)
print('REFINED CLASSIFICATION')
print('=' * 70)

class_counts = Counter()
prefix_classes = defaultdict(set)  # prefix → set of classes
prefix_freq = Counter()
all_classified = []

for fid, folio in vms['folios'].items():
    section = folio['metadata']['section']
    for block in folio['blocks']:
        words = [w for line in block['lines'] for w in line['words']]
        for i, w in enumerate(words):
            eva = w['eva_primary']
            morph = w.get('morphology') or {}
            root = morph.get('root', '')
            suffix = morph.get('suffix', '') or ''
            ic = morph.get('i_count')

            if eva in LOGOS:
                wclass = 'LOGO'
            elif i == 0 and block.get('separator') and eva[0] in 'ptkf' and eva not in LOGOS:
                wclass = 'VERB'
            elif suffix in SUFFIX_CLASS:
                wclass = SUFFIX_CLASS[suffix]
            elif ic is not None:
                wclass = 'DOSE'
            elif len(eva) <= 2 and eva not in LOGOS:
                wclass = 'FUNC'
            elif '@' in eva:
                wclass = 'SPECIAL'
            else:
                wclass = 'UNK'

            class_counts[wclass] += 1
            if root and wclass not in ('LOGO', 'VERB', 'SPECIAL'):
                prefix_classes[root].add(wclass)
                prefix_freq[root] += 1

            all_classified.append({
                'folio': fid, 'section': section,
                'block': block.get('block_id', ''),
                'eva': eva, 'root': root, 'suffix': suffix,
                'class': wclass, 'i_count': ic,
            })

total = sum(class_counts.values())
print(f'\n  Total words: {total}')
print(f'\n  {"Class":>8s} {"Count":>6s} {"Pct":>5s}')
print('  ' + '-' * 25)
for cls, n in class_counts.most_common():
    print(f'  {cls:>8s} {n:>6d} {n*100//total:>4d}%')

# ================================================================
# 2. MULTICLASS CHECK — same prefix, different classes
# ================================================================
print(f'\n{"="*70}')
print('MULTICLASS CHECK — même préfixe, classes différentes')
print('=' * 70)

multiclass = [(pfx, classes) for pfx, classes in prefix_classes.items()
              if len(classes) > 1 and prefix_freq[pfx] >= 5]
multiclass.sort(key=lambda x: -prefix_freq[x[0]])

single_class = [(pfx, classes) for pfx, classes in prefix_classes.items()
                if len(classes) == 1 and prefix_freq[pfx] >= 5]

print(f'\n  Prefixes with 1 class only: {len(single_class)}')
print(f'  Prefixes with 2+ classes: {len(multiclass)}')
print(f'  → {len(multiclass)*100//(len(multiclass)+len(single_class))}% are multiclass')

print(f'\n  TOP 20 MULTICLASS prefixes:')
for pfx, classes in multiclass[:20]:
    freq = prefix_freq[pfx]
    cls_str = ', '.join(sorted(classes))
    print(f'    {pfx:12s} (x{freq:4d}): {cls_str}')

print(f'\n  TOP 10 SINGLE-CLASS prefixes:')
for pfx, classes in sorted(single_class, key=lambda x: -prefix_freq[x[0]])[:10]:
    freq = prefix_freq[pfx]
    cls = list(classes)[0]
    print(f'    {pfx:12s} (x{freq:4d}): {cls}')

# ================================================================
# 3. UNIQUE CONCEPTS — how many distinct prefixes?
# ================================================================
print(f'\n{"="*70}')
print('UNIQUE CONCEPTS (préfixes distincts)')
print('=' * 70)

n_total_prefixes = len(prefix_freq)
n_freq5 = sum(1 for f in prefix_freq.values() if f >= 5)
n_freq10 = sum(1 for f in prefix_freq.values() if f >= 10)
n_freq20 = sum(1 for f in prefix_freq.values() if f >= 20)

print(f'  Total prefixes: {n_total_prefixes}')
print(f'  With freq >= 5: {n_freq5}')
print(f'  With freq >= 10: {n_freq10}')
print(f'  With freq >= 20: {n_freq20}')
print(f'\n  AN has ~289 unique ingredients')
print(f'  VMS prefixes >= 5: {n_freq5} → {"COMPATIBLE" if 200 <= n_freq5 <= 500 else "HORS RANGE"}')

# ================================================================
# 4. PHARMA RECIPE STRUCTURE — refined
# ================================================================
print(f'\n{"="*70}')
print('PHARMA RECIPE STRUCTURE (refined)')
print('=' * 70)

# For pharma blocks, compute new class distributions
pharma_blocks = []
for block_data in all_classified:
    if block_data['section'] != 'pharma':
        continue

pharma_class = Counter()
pharma_block_classes = defaultdict(Counter)

for item in all_classified:
    if item['section'] == 'pharma':
        pharma_class[item['class']] += 1
        pharma_block_classes[item['block']][item['class']] += 1

total_pharma = sum(pharma_class.values())
print(f'\n  Pharma total: {total_pharma} words')
print(f'\n  {"Class":>8s} {"Count":>6s} {"Pct":>5s} {"Latin equivalent":>25s}')
print('  ' + '-' * 50)
CLASS_MEANING = {
    'DOSE': 'quantités (III, II, I)',
    'UNIT': 'unités (drachma, uncia)',
    'INGR_A': 'ingrédients type A (-edy)',
    'INGR_B': 'ingrédients type B (-eol)',
    'INGR_C': 'ingrédients type C (-ey)',
    'FUNC': 'connecteurs (et, ana, de)',
    'VERB': 'verbes (Recipe, Misce)',
    'LOGO': 'logograms',
    'TERM': 'terminateurs (-am)',
    'INSTR': 'instructions (-dy)',
    'QUAL': 'qualificatifs (-air)',
    'UNK': 'non classifié',
}
for cls, n in pharma_class.most_common():
    meaning = CLASS_MEANING.get(cls, '')
    print(f'  {cls:>8s} {n:>6d} {n*100//total_pharma:>4d}% {meaning:>25s}')

# Comparison with AN
print(f'\n  AN reference: INGR=25%, DOSE+QTY=9%, GRAM=40%, VERB=5%')
ingr_total = pharma_class.get('INGR_A',0) + pharma_class.get('INGR_B',0) + pharma_class.get('INGR_C',0)
dose_total = pharma_class.get('DOSE',0) + pharma_class.get('UNIT',0)
func_total = pharma_class.get('FUNC',0) + pharma_class.get('LOGO',0) + pharma_class.get('TERM',0)
print(f'  VMS refined: INGR={ingr_total*100//total_pharma}% '
      f'DOSE+UNIT={dose_total*100//total_pharma}% '
      f'FUNC+LOGO+TERM={func_total*100//total_pharma}% '
      f'VERB={pharma_class.get("VERB",0)*100//total_pharma}%')

# ================================================================
# 5. RECIPE FORMULA — what's a typical refined recipe?
# ================================================================
print(f'\n{"="*70}')
print('RECIPE FORMULA (refined)')
print('=' * 70)

SYM = {'DOSE':'D','UNIT':'U','INGR_A':'A','INGR_B':'B','INGR_C':'C',
       'FUNC':'F','VERB':'V','LOGO':'L','TERM':'T','INSTR':'I',
       'QUAL':'Q','UNK':'·','SPECIAL':'@'}

# Show f103r blocks
for bid in sorted(pharma_block_classes.keys()):
    if not bid.startswith('f103r'): continue
    items = [item for item in all_classified if item['block'] == bid]
    pattern = ''.join(SYM.get(item['class'], '?') for item in items)
    tc = pharma_block_classes[bid]
    print(f'\n  {bid}: {pattern}')
    summary = ' '.join(f'{SYM.get(c,"?")}:{n}' for c, n in tc.most_common() if n > 0)
    print(f'    {summary}')

# ================================================================
# 6. TRANSITION MATRIX (refined)
# ================================================================
print(f'\n{"="*70}')
print('TRANSITIONS (refined, pharma only)')
print('=' * 70)

transitions = Counter()
pharma_items = [item for item in all_classified if item['section'] == 'pharma']

for i in range(len(pharma_items) - 1):
    if pharma_items[i]['block'] != pharma_items[i+1]['block']:
        continue
    a = pharma_items[i]['class']
    b = pharma_items[i+1]['class']
    transitions[(a, b)] += 1

total_trans = sum(transitions.values())
print(f'\n  {"From→To":>20s} {"Count":>6s} {"Pct":>5s}')
print('  ' + '-' * 35)
for (a, b), n in transitions.most_common(25):
    print(f'  {a:>8s}→{b:<8s} {n:>6d} {n*100//total_trans:>4d}%')

# ================================================================
# 7. GALLOWS k/t RATIO PER HERBAL FOLIO
# ================================================================
print(f'\n{"="*70}')
print('GALLOWS k/t RATIO PAR FOLIO HERBAL')
print('=' * 70)

kt_ratio = {}
for fid, folio in vms['folios'].items():
    if 'herbal' not in folio['metadata']['section']: continue
    k_count = 0
    t_count = 0
    for block in folio['blocks']:
        for line in block['lines']:
            for w in line['words']:
                eva = w['eva_primary']
                if 'k' in eva and eva not in LOGOS: k_count += 1
                if 't' in eva and eva not in LOGOS: t_count += 1
    total_kt = k_count + t_count
    if total_kt >= 5:
        ratio = k_count / total_kt
        kt_ratio[fid] = (ratio, k_count, t_count)

ratios = [r for r, _, _ in kt_ratio.values()]
if ratios:
    import statistics
    mean_r = statistics.mean(ratios)
    std_r = statistics.stdev(ratios) if len(ratios) > 1 else 0
    print(f'\n  Mean k/(k+t): {mean_r:.3f} ± {std_r:.3f}')
    print(f'  Range: {min(ratios):.3f} — {max(ratios):.3f}')

    # Extremes
    sorted_kt = sorted(kt_ratio.items(), key=lambda x: x[1][0])
    print(f'\n  Most t-dominant (low k):')
    for fid, (r, kc, tc) in sorted_kt[:5]:
        print(f'    {fid:8s}: k/(k+t)={r:.2f} (k={kc}, t={tc})')
    print(f'\n  Most k-dominant (high k):')
    for fid, (r, kc, tc) in sorted_kt[-5:]:
        print(f'    {fid:8s}: k/(k+t)={r:.2f} (k={kc}, t={tc})')

# ================================================================
# Save
# ================================================================
results = {
    'class_counts': dict(class_counts),
    'n_prefixes': n_total_prefixes,
    'n_prefixes_freq5': n_freq5,
    'n_multiclass': len(multiclass),
    'n_singleclass': len(single_class),
    'pharma_classes': dict(pharma_class),
    'kt_mean': round(mean_r, 3) if ratios else None,
    'kt_std': round(std_r, 3) if ratios else None,
}

with open(os.path.join(RESULTS, 'refined_decode.json'), 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print('\nSaved refined_decode.json')
