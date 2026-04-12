"""
SESSION 16 — FRAPPE 6: Functional words (grammatical roots)

Roots appearing in >20% of folios are probably functional words
(prepositions, conjunctions, verbs, etc.), NOT ingredients.

Method:
1. Identify all high-frequency roots (>20% of folios)
2. Compare their distributional profiles to known logograms
3. Classify: connector, preposition, verb, determiner, etc.
4. Mark as FUNCTIONAL in registry (not to be decoded as ingredients)

This prevents future false positives from frequency-based methods.
"""
import json, sys, io, os
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.dirname(__file__)
VMS_PATH = os.path.join(BASE, '..', 'vms', 'vms_structured.json')
RESULTS = BASE

with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)

LOGOS = {
    'o': 'ac', 'l': 'se', 'd': 'de', 'r': 'recipe', 'v': 'vel',
    'x': 'crux', 'k': 'cum', 'm': 'misce', 'f': 'per', 't': 'et',
    'y': 'in', 'c': 'cum', 's': 'est', 'sh': 'ci', 'p': 'usque',
    'ch': 'cum',
}

# ================================================================
# STEP 1: Root frequency across all folios
# ================================================================
print('='*70)
print('FRAPPE 6 — FUNCTIONAL WORDS')
print('='*70)

total_folios = len(vms['folios'])
root_in_folios = defaultdict(set)     # root → set of folio IDs
root_in_sections = defaultdict(Counter)  # root → {section: count}
root_total = Counter()                 # root → total occurrences
root_positions = defaultdict(list)     # root → list of (relative word pos in line)

for fid, folio in vms['folios'].items():
    section = folio['metadata']['section']
    for block in folio['blocks']:
        for line in block['lines']:
            n_words = len(line['words'])
            for wi, w in enumerate(line['words']):
                eva = w['eva_primary']
                root = (w.get('morphology') or {}).get('root', '')
                if root and len(root) >= 2:
                    root_in_folios[root].add(fid)
                    root_in_sections[root][section] += 1
                    root_total[root] += 1
                    if n_words > 1:
                        root_positions[root].append(wi / (n_words - 1))

# Compute profiles
print(f'\n  Total folios: {total_folios}')
print(f'  Total unique roots (2+ chars): {len(root_in_folios)}')

# ================================================================
# STEP 2: High-frequency roots (>20% of folios)
# ================================================================
threshold = total_folios * 0.20
high_freq = []

for root in root_in_folios:
    n_folios = len(root_in_folios[root])
    if n_folios >= threshold:
        sections = root_in_sections[root]
        total = root_total[root]
        positions = root_positions.get(root, [])
        mean_pos = sum(positions) / len(positions) if positions else 0.5

        # Position entropy: how spread out in lines?
        # Split into 3 bins: start (0-0.33), mid (0.33-0.67), end (0.67-1.0)
        pos_bins = Counter()
        for p in positions:
            if p < 0.33:
                pos_bins['start'] += 1
            elif p < 0.67:
                pos_bins['mid'] += 1
            else:
                pos_bins['end'] += 1

        # Section distribution
        herbal_pct = sections.get('herbal', 0) * 100 // max(total, 1)
        pharma_pct = sections.get('pharma', 0) * 100 // max(total, 1)
        balnea_pct = sections.get('balnea', 0) * 100 // max(total, 1)
        other_pct = 100 - herbal_pct - pharma_pct - balnea_pct

        high_freq.append({
            'root': root,
            'n_folios': n_folios,
            'folio_pct': n_folios * 100 // total_folios,
            'total': total,
            'mean_pos': mean_pos,
            'pos_start': pos_bins.get('start', 0),
            'pos_mid': pos_bins.get('mid', 0),
            'pos_end': pos_bins.get('end', 0),
            'herbal_pct': herbal_pct,
            'pharma_pct': pharma_pct,
            'balnea_pct': balnea_pct,
            'other_pct': other_pct,
        })

high_freq.sort(key=lambda x: -x['n_folios'])

print(f'\n  Roots in 20%+ of folios: {len(high_freq)}')
print(f'\n  {"Root":>10s} {"Folios":>7s} {"Total":>6s} {"MeanPos":>8s} '
      f'{"Start":>6s} {"Mid":>5s} {"End":>5s} '
      f'{"Herb%":>6s} {"Phar%":>6s} {"Baln%":>6s}')
print('  ' + '-' * 80)

for hf in high_freq:
    print(f'  {hf["root"]:>10s} {hf["folio_pct"]:>6d}% {hf["total"]:>6d} '
          f'{hf["mean_pos"]:>8.2f} '
          f'{hf["pos_start"]:>6d} {hf["pos_mid"]:>5d} {hf["pos_end"]:>5d} '
          f'{hf["herbal_pct"]:>5d}% {hf["pharma_pct"]:>5d}% {hf["balnea_pct"]:>5d}%')


# ================================================================
# STEP 3: Compare with logogram profiles
# ================================================================
print(f'\n\n{"="*70}')
print('STEP 3 — LOGOGRAM REFERENCE PROFILES')
print('='*70)

# Get logogram profiles for comparison
logo_profiles = {}
for logo, latin in LOGOS.items():
    if logo in root_in_folios:
        n_folios = len(root_in_folios[logo])
        total = root_total[logo]
        positions = root_positions.get(logo, [])
        mean_pos = sum(positions) / len(positions) if positions else 0.5

        logo_profiles[logo] = {
            'latin': latin,
            'n_folios': n_folios,
            'total': total,
            'mean_pos': mean_pos,
        }

        print(f'  {logo:>5s} = {latin:>8s}  folios={n_folios:>3d} ({n_folios*100//total_folios}%)  '
              f'total={total:>5d}  pos={mean_pos:.2f}')


# ================================================================
# STEP 4: Classify functional words
# ================================================================
print(f'\n\n{"="*70}')
print('STEP 4 — FUNCTIONAL WORD CLASSIFICATION')
print('='*70)

# Classification heuristics:
# - Start-heavy (pos_start >> pos_end) → determiner/preposition
# - End-heavy (pos_end >> pos_start) → terminator/case marker
# - Uniform position → conjunction/connector
# - Mostly herbal → plant modifier
# - Mostly pharma → recipe verb
# - All sections → universal connector

classified = []

for hf in high_freq:
    root = hf['root']
    total_pos = hf['pos_start'] + hf['pos_mid'] + hf['pos_end']
    if total_pos == 0:
        continue

    start_frac = hf['pos_start'] / total_pos
    mid_frac = hf['pos_mid'] / total_pos
    end_frac = hf['pos_end'] / total_pos

    # Position pattern
    if start_frac > 0.5:
        pos_type = 'START-HEAVY'
    elif end_frac > 0.5:
        pos_type = 'END-HEAVY'
    else:
        pos_type = 'UNIFORM'

    # Section pattern
    if hf['herbal_pct'] > 60:
        sec_type = 'HERBAL-ONLY'
    elif hf['pharma_pct'] > 60:
        sec_type = 'PHARMA-ONLY'
    elif hf['balnea_pct'] > 30:
        sec_type = 'BALNEA-HEAVY'
    else:
        sec_type = 'UNIVERSAL'

    # Classification
    if pos_type == 'END-HEAVY' and sec_type == 'UNIVERSAL':
        category = 'TERMINATOR'
        hypothesis = 'sentence/clause ender (cf. -am)'
    elif pos_type == 'START-HEAVY' and sec_type == 'UNIVERSAL':
        category = 'OPENER'
        hypothesis = 'preposition or connector'
    elif pos_type == 'UNIFORM' and sec_type == 'UNIVERSAL':
        category = 'CONNECTOR'
        hypothesis = 'conjunction (et/vel/cum) or preposition'
    elif sec_type == 'HERBAL-ONLY':
        category = 'HERBAL-FUNC'
        hypothesis = 'botanical modifier or structural'
    elif sec_type == 'PHARMA-ONLY':
        category = 'PHARMA-FUNC'
        hypothesis = 'recipe verb or quantity word'
    else:
        category = 'FUNCTIONAL'
        hypothesis = 'grammatical word'

    classified.append({
        'root': root,
        'category': category,
        'hypothesis': hypothesis,
        'pos_type': pos_type,
        'sec_type': sec_type,
        'folio_pct': hf['folio_pct'],
        'total': hf['total'],
        'mean_pos': hf['mean_pos'],
    })

print(f'\n  {"Root":>10s} {"Cat":>15s} {"Pos":>12s} {"Sec":>14s} '
      f'{"Folios":>7s} {"Total":>6s} {"Hypothesis"}')
print('  ' + '-' * 90)

for c in classified:
    print(f'  {c["root"]:>10s} {c["category"]:>15s} {c["pos_type"]:>12s} '
          f'{c["sec_type"]:>14s} {c["folio_pct"]:>6d}% {c["total"]:>6d}  '
          f'{c["hypothesis"]}')


# ================================================================
# STEP 5: Summary — functional word registry
# ================================================================
print(f'\n\n{"="*70}')
print('FUNCTIONAL WORD SUMMARY')
print('='*70)

cats = Counter(c['category'] for c in classified)
for cat, n in cats.most_common():
    print(f'  {cat:>15s}: {n}')
    for c in classified:
        if c['category'] == cat:
            print(f'    {c["root"]:>10s} ({c["folio_pct"]}% folios, {c["total"]} occ)')

# ================================================================
# SAVE
# ================================================================
output = {
    'n_high_freq': len(high_freq),
    'threshold_pct': 20,
    'high_freq_roots': high_freq,
    'classified': classified,
    'category_counts': dict(cats),
}

with open(os.path.join(RESULTS, 'frappe6_results.json'), 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f'\nSaved frappe6_results.json')
