"""
STRUCTURAL ANALYSIS — What patterns emerge from structural decode?

Questions:
1. Which folios have unusual type distributions?
2. Are there recipe "templates" (recurring type sequences)?
3. Do PLANT codes cluster in specific recipes?
4. Which FUNC codes are actually verbs/prepositions vs content words?
5. Are there folios that don't look like recipes at all?
"""
import json, sys, io, os
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DECODE_PATH = os.path.join(os.path.dirname(__file__), 'structural_decode.json')

with open(DECODE_PATH, encoding='utf-8') as f:
    data = json.load(f)

blocks = data['blocks']
registry = data['registry']

# ================================================================
# 1. PER-FOLIO TYPE DISTRIBUTION
# ================================================================
print('=' * 70)
print('1. TYPE DISTRIBUTION PAR FOLIO')
print('=' * 70)

folio_stats = defaultdict(lambda: Counter())
folio_blocks = defaultdict(int)
folio_words = defaultdict(int)

for db in blocks:
    fid = db['folio']
    folio_blocks[fid] += 1
    for dw in db['decoded']:
        folio_stats[fid][dw['type']] += 1
        folio_words[fid] += 1

print(f'\n{"Folio":>8s} {"Blocs":>5s} {"Mots":>5s} '
      f'{"FUNC%":>6s} {"INGR%":>6s} {"DOSE%":>6s} {"PLANT%":>6s} '
      f'{"LOGO%":>6s} {"VERB%":>6s} {"UNK%":>5s} {"Signal":>15s}')
print('-' * 95)

anomalies = []
for fid in sorted(folio_stats.keys()):
    n = folio_words[fid]
    s = folio_stats[fid]
    func_pct = s['FUNC'] * 100 // max(n, 1)
    ingr_pct = s['INGR'] * 100 // max(n, 1)
    dose_pct = s['DOSE'] * 100 // max(n, 1)
    plant_pct = s['PLANT'] * 100 // max(n, 1)
    logo_pct = s['LOGO'] * 100 // max(n, 1)
    verb_pct = s['VERB'] * 100 // max(n, 1)
    unk_pct = s['UNK'] * 100 // max(n, 1)

    # Detect anomalies
    signal = ''
    if dose_pct < 5:
        signal = '! LOW DOSE'
    if dose_pct > 30:
        signal = '! HIGH DOSE'
    if plant_pct > 15:
        signal = '★ PLANT-RICH'
    if unk_pct > 20:
        signal = '? HIGH UNK'
    if verb_pct > 5:
        signal = '⚡ VERB-RICH'
    if logo_pct > 8:
        signal = '◆ LOGO-RICH'
    if func_pct > 55:
        signal = '~ FUNC-HEAVY'
    if ingr_pct > 35:
        signal = '▲ INGR-HEAVY'

    if signal:
        anomalies.append((fid, signal, n, s))

    print(f'{fid:>8s} {folio_blocks[fid]:>5d} {n:>5d} '
          f'{func_pct:>5d}% {ingr_pct:>5d}% {dose_pct:>5d}% {plant_pct:>5d}% '
          f'{logo_pct:>5d}% {verb_pct:>5d}% {unk_pct:>4d}% {signal:>15s}')

# ================================================================
# 2. ANOMALOUS FOLIOS
# ================================================================
print(f'\n{"="*70}')
print(f'2. FOLIOS REMARQUABLES ({len(anomalies)})')
print('=' * 70)

for fid, signal, n, s in anomalies:
    print(f'  {fid:8s} [{signal:15s}] {n:4d}w')

# ================================================================
# 3. RECIPE TEMPLATES — recurring type patterns
# ================================================================
print(f'\n{"="*70}')
print('3. RECIPE TEMPLATES — patterns de types récurrents')
print('=' * 70)

# For each block, create a type sequence (collapsed: FFFDD→F3D2)
def compress_pattern(decoded):
    """Compress type sequence: FUNC FUNC DOSE DOSE → F2 D2"""
    types = [dw['type'][0] for dw in decoded]  # first letter
    if not types:
        return ''
    compressed = []
    current = types[0]
    count = 1
    for t in types[1:]:
        if t == current:
            count += 1
        else:
            compressed.append(f'{current}{count}' if count > 1 else current)
            current = t
            count = 1
    compressed.append(f'{current}{count}' if count > 1 else current)
    return ''.join(compressed)

pattern_counts = Counter()
pattern_examples = defaultdict(list)

for db in blocks:
    pat = compress_pattern(db['decoded'])
    pattern_counts[pat] += 1
    if len(pattern_examples[pat]) < 2:
        pattern_examples[pat].append(db['block_id'])

print('\nTop 20 most common block patterns:')
for pat, count in pattern_counts.most_common(20):
    examples = ', '.join(pattern_examples[pat])
    print(f'  {count:3d}x  {pat[:60]:60s}  ({examples})')

# ================================================================
# 4. BIGRAMS — what follows what?
# ================================================================
print(f'\n{"="*70}')
print('4. TYPE BIGRAMS — transitions entre types')
print('=' * 70)

bigrams = Counter()
for db in blocks:
    types = [dw['type'] for dw in db['decoded']]
    for i in range(len(types) - 1):
        bigrams[(types[i], types[i+1])] += 1

total_bi = sum(bigrams.values())
print(f'\n{"From→To":>20s} {"Count":>6s} {"Pct":>5s}')
print('-' * 35)
for (a, b), count in bigrams.most_common(25):
    pct = count * 100 // total_bi
    print(f'{a:>8s}→{b:<8s} {count:>6d} {pct:>4d}%')

# ================================================================
# 5. PLANT CODE DISTRIBUTION — where do plants appear?
# ================================================================
print(f'\n{"="*70}')
print('5. PLANT CODES — distribution dans les recettes')
print('=' * 70)

plant_positions = defaultdict(list)  # plant_code → [relative positions]
plant_folios = defaultdict(Counter)  # plant_code → {folio: count}

for db in blocks:
    n = len(db['decoded'])
    for i, dw in enumerate(db['decoded']):
        if dw['type'] == 'PLANT':
            code = dw['code'].split('.')[0]  # strip suffix
            plant_positions[code].append(i / max(n - 1, 1))
            plant_folios[code][db['folio']] += 1

print(f'\n{"Plant":>15s} {"Total":>6s} {"Folios":>7s} {"AvgPos":>7s} {"StartBias":>10s}')
print('-' * 55)
for code in sorted(plant_positions.keys(), key=lambda c: -len(plant_positions[c])):
    positions = plant_positions[code]
    n_folios = len(plant_folios[code])
    avg_pos = sum(positions) / len(positions)
    start_bias = sum(1 for p in positions if p < 0.2) * 100 // len(positions)
    print(f'{code:>15s} {len(positions):>6d} {n_folios:>7d} {avg_pos:>7.2f} {start_bias:>9d}%')

# ================================================================
# 6. FUNC CODES — are they really functional?
# ================================================================
print(f'\n{"="*70}')
print('6. TOP FUNC CODES — que sont-ils vraiment?')
print('=' * 70)

func_info = defaultdict(lambda: {
    'count': 0, 'positions': [], 'after_dose': 0, 'before_dose': 0,
    'at_start': 0, 'suffixes': Counter(),
})

for db in blocks:
    n = len(db['decoded'])
    for i, dw in enumerate(db['decoded']):
        if not dw['code'].startswith('FUNC_'):
            continue
        base_code = dw['code'].split('.')[0]
        fi = func_info[base_code]
        fi['count'] += 1
        fi['positions'].append(i / max(n - 1, 1))
        if i < 2: fi['at_start'] += 1
        if dw['suffix']: fi['suffixes'][dw['suffix']] += 1

        # Context
        if i > 0 and db['decoded'][i-1]['type'] == 'DOSE':
            fi['after_dose'] += 1
        if i < n-1 and db['decoded'][i+1]['type'] == 'DOSE':
            fi['before_dose'] += 1

# Get root for each func code
func_roots = {}
for code, info in registry.get('functions', {}).items():
    func_roots[code] = info.get('root', '?')

print(f'\n{"Code":>10s} {"Root":>10s} {"Count":>6s} {"AvgPos":>7s} {"AfDose%":>8s} '
      f'{"BfDose%":>8s} {"Start%":>7s} {"TopSuffix":>15s}')
print('-' * 85)

for code in sorted(func_info.keys(), key=lambda c: -func_info[c]['count'])[:30]:
    fi = func_info[code]
    n = fi['count']
    avg_pos = sum(fi['positions']) / len(fi['positions'])
    ad = fi['after_dose'] * 100 // n
    bd = fi['before_dose'] * 100 // n
    st = fi['at_start'] * 100 // n
    root = func_roots.get(code, '?')
    top_suf = fi['suffixes'].most_common(1)
    suf_str = f'{top_suf[0][0]}({top_suf[0][1]})' if top_suf else '-'

    # Reclassify?
    role = ''
    if bd > 20: role = '→ pre-DOSE (INGREDIENT?)'
    if ad > 20: role = '→ post-DOSE (INGREDIENT?)'
    if st > 10: role = '→ OPENER'

    print(f'{code:>10s} {root:>10s} {n:>6d} {avg_pos:>7.2f} {ad:>7d}% '
          f'{bd:>7d}% {st:>6d}% {suf_str:>15s} {role}')

# ================================================================
# 7. BLOCK-LEVEL ANOMALIES — blocks that don't look like recipes
# ================================================================
print(f'\n{"="*70}')
print('7. BLOCKS NON-RECETTE (anomalies structurelles)')
print('=' * 70)

for db in blocks:
    n = len(db['decoded'])
    types = Counter(dw['type'] for dw in db['decoded'])

    dose_pct = types['DOSE'] * 100 // max(n, 1)
    plant_pct = types['PLANT'] * 100 // max(n, 1)
    verb_count = types['VERB']
    ingr_count = types['INGR']
    unk_pct = types['UNK'] * 100 // max(n, 1)

    anomaly = None
    if n < 5:
        anomaly = 'TRÈS COURT'
    elif dose_pct > 50:
        anomaly = 'TABLE DE DOSES'
    elif types['DOSE'] == 0 and types['PLANT'] == 0 and types['INGR'] < 2:
        anomaly = 'PAS DE CONTENU'
    elif unk_pct > 40:
        anomaly = 'TROP D\'INCONNUS'
    elif types['FUNC'] * 100 // n > 70:
        anomaly = 'PRESQUE TOUT FUNC'

    if anomaly:
        type_str = ' '.join(f'{t[0]}:{c}' for t, c in types.most_common())
        print(f'  {db["block_id"]:20s} ({db["folio"]}) {n:3d}w [{anomaly:20s}] {type_str}')

# ================================================================
# 8. SUMMARY STATS
# ================================================================
print(f'\n{"="*70}')
print('8. RÉSUMÉ')
print('=' * 70)

total_blocks = len(blocks)
total_words = sum(len(db['decoded']) for db in blocks)
folios = set(db['folio'] for db in blocks)

print(f'  Folios pharma:  {len(folios)}')
print(f'  Blocs:          {total_blocks}')
print(f'  Mots total:     {total_words}')
print(f'  Plants uniques: {len(plant_positions)}')
print(f'  INGR uniques:   {len(registry.get("ingredients", {}))}')
print(f'  FUNC uniques:   {len(registry.get("functions", {}))}')
print(f'  VERB uniques:   {len(registry.get("verbs", {}))}')

# Save summary
summary = {
    'folio_stats': {fid: dict(s) for fid, s in folio_stats.items()},
    'anomalous_folios': [(fid, sig) for fid, sig, _, _ in anomalies],
    'type_bigrams': {f'{a}→{b}': c for (a, b), c in bigrams.most_common(50)},
    'pattern_counts': dict(pattern_counts.most_common(30)),
}
out_path = os.path.join(os.path.dirname(__file__), 'structural_analysis.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)

print(f'\nSaved structural_analysis.json')
