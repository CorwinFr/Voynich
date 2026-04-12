"""
SESSION 17 — ATTACK 4: Validate oty=COLD on herbal_b (32 folios)

Session 16 found: oty in lines 1-3 = cold plant marker (p=0.023, 22 plants).
Now test on an INDEPENDENT set: herbal_b (32 folios).

If oty correlates with cold in herbal_b too → combined p <<< 0.01.

We need botanical identifications for herbal_b plants. Use Sherwood
and any other available identifications.
"""
import json, sys, io, os
from collections import Counter, defaultdict
from math import comb

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.dirname(__file__)
VMS_PATH = os.path.join(BASE, '..', 'vms', 'vms_structured.json')
RESULTS = BASE

with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)

STANDARD_QUALITIES = {
    'artemisia': 'hot', 'abrotanum': 'hot', 'absinthium': 'hot',
    'urtica': 'hot', 'allium': 'hot', 'plantago': 'cold',
    'ruta': 'hot', 'apium': 'hot', 'althaea': 'wet',
    'anethum': 'hot', 'betonica': 'hot', 'sabina': 'hot',
    'chamomilla': 'hot', 'nepeta': 'hot', 'pulegium': 'hot',
    'feniculum': 'hot', 'portulaca': 'cold', 'lactuca': 'cold',
    'rosa': 'cold', 'lilium': 'hot', 'satureia': 'hot',
    'salvia': 'hot', 'origanum': 'hot', 'mentha': 'hot',
    'coriandrum': 'cold', 'eruca': 'hot', 'papaver': 'cold',
    'viola': 'cold', 'aristolochia': 'hot', 'verbena': 'cold',
    'malva': 'cold', 'atriplex': 'cold', 'centaurea': 'hot',
    'elleborus': 'hot', 'rosmarinus': 'hot', 'cannabis': 'cold',
    'crocus': 'hot', 'mandragora': 'cold', 'gentiana': 'hot',
    'nigella': 'hot', 'achillea': 'hot', 'nymphaea': 'cold',
    'spinacia': 'cold', 'tanacetum': 'hot', 'ribes': 'cold',
    'pulmonaria': 'cold', 'anagallis': 'cold', 'inula': 'hot',
    'valeriana': 'hot', 'erigeron': 'cold', 'drosera': 'cold',
    'lonicera': 'hot', 'arnica': 'hot', 'symphytum': 'hot',
    'dictamnus': 'hot', 'scorzonera': 'hot', 'veronica': 'cold',
    'rhododendron': 'cold', 'sonchus': 'cold',
}

# ALL Sherwood identifications including herbal_b
ALL_SHERWOOD = {
    # herbal_a
    'f48v':'ruta','f9v':'viola','f44v':'apium','f51v':'salvia',
    'f29r':'lactuca','f41r':'origanum','f37r':'mentha',
    'f41v':'coriandrum','f22r':'verbena','f28r':'aristolochia',
    'f5v':'malva','f45r':'atriplex','f66v':'satureia',
    'f65v':'centaurea','f3v':'elleborus','f95v1':'althaea',
    'f11r':'rosmarinus','f16r':'cannabis','f39r':'crocus',
    'f44r':'mandragora','f50v':'gentiana','f29v':'nigella',
    'f35v':'ribes','f47v':'pulmonaria','f53r':'achillea',
    'f14r':'scorzonera','f21r':'anagallis','f27r':'spinacia',
    'f33v':'tanacetum','f49r':'nymphaea',
    # herbal_b (some identified by Sherwood/Scott)
    'f87r':'satureia','f90r':'papaver','f90v':'eruca',
}

# ================================================================
# Identify herbal_b folios
# ================================================================
herbal_b_folios = []
herbal_a_folios = []

for fid, folio in sorted(vms['folios'].items()):
    sec = folio['metadata']['section']
    if sec == 'herbal_b':
        herbal_b_folios.append(fid)
    elif sec == 'herbal_a':
        herbal_a_folios.append(fid)

print(f'herbal_a folios: {len(herbal_a_folios)}')
print(f'herbal_b folios: {len(herbal_b_folios)}')
print(f'herbal_b: {herbal_b_folios}')

# ================================================================
# Check which herbal_b folios have plant identifications
# ================================================================
def has_oty_in_first_n_lines(fid, n=3):
    folio = vms['folios'][fid]
    line_count = 0
    for block in folio['blocks']:
        for line in block['lines']:
            line_count += 1
            if line_count > n:
                return False
            for w in line['words']:
                root = (w.get('morphology') or {}).get('root', '')
                if root == 'oty' or w['eva_primary'] == 'oty':
                    return True
    return False

print(f'\n{"="*70}')
print('HERBAL_B — OTY IN LINES 1-3')
print('='*70)

# First: which herbal_b folios have Sherwood identifications?
b_identified = {}
for fid in herbal_b_folios:
    if fid in ALL_SHERWOOD:
        plant = ALL_SHERWOOD[fid]
        qual = STANDARD_QUALITIES.get(plant, 'unknown')
        b_identified[fid] = {'plant': plant, 'quality': qual}

print(f'\n  herbal_b with Sherwood ID: {len(b_identified)}/{len(herbal_b_folios)}')

# Check oty for all herbal_b folios (even unidentified)
b_with_oty = []
b_without_oty = []

for fid in herbal_b_folios:
    has_oty = has_oty_in_first_n_lines(fid, 3)
    plant = ALL_SHERWOOD.get(fid, '?')
    qual = STANDARD_QUALITIES.get(plant, '?')

    if has_oty:
        b_with_oty.append((fid, plant, qual))
    else:
        b_without_oty.append((fid, plant, qual))

print(f'  herbal_b with oty in L1-3: {len(b_with_oty)}')
print(f'  herbal_b without oty in L1-3: {len(b_without_oty)}')

print(f'\n  WITH oty:')
for fid, plant, qual in b_with_oty:
    marker = f'  ← {qual.upper()}' if qual != '?' else ''
    print(f'    {fid:>8s} {plant:>15s} {qual:>8s}{marker}')

print(f'\n  WITHOUT oty:')
for fid, plant, qual in b_without_oty:
    marker = f'  ← {qual.upper()}' if qual != '?' else ''
    print(f'    {fid:>8s} {plant:>15s} {qual:>8s}{marker}')

# ================================================================
# COMBINED TEST: herbal_a + herbal_b
# ================================================================
print(f'\n\n{"="*70}')
print('COMBINED TEST — ALL HERBAL FOLIOS')
print('='*70)

# Herbal_a data from session 16 (22 plants with identifications)
# Re-compute for completeness
all_hot_oty = 0
all_hot_no_oty = 0
all_cold_oty = 0
all_cold_no_oty = 0

for fid in herbal_a_folios + herbal_b_folios:
    plant = ALL_SHERWOOD.get(fid, None)
    if not plant:
        continue
    qual = STANDARD_QUALITIES.get(plant, None)
    if not qual:
        continue

    is_cold = qual in ('cold', 'wet')
    has_oty = has_oty_in_first_n_lines(fid, 3)

    if is_cold and has_oty:
        all_cold_oty += 1
    elif is_cold:
        all_cold_no_oty += 1
    elif has_oty:
        all_hot_oty += 1
    else:
        all_hot_no_oty += 1

n_total = all_hot_oty + all_hot_no_oty + all_cold_oty + all_cold_no_oty
n_oty = all_hot_oty + all_cold_oty
n_hot = all_hot_oty + all_hot_no_oty
n_cold = all_cold_oty + all_cold_no_oty

print(f'\n  Contingency table (all herbal with quality info):')
print(f'  {"":>10s} {"oty":>6s} {"no-oty":>7s} {"Total":>6s}')
print(f'  {"HOT/DRY":>10s} {all_hot_oty:>6d} {all_hot_no_oty:>7d} {n_hot:>6d}')
print(f'  {"COLD/WET":>10s} {all_cold_oty:>6d} {all_cold_no_oty:>7d} {n_cold:>6d}')
print(f'  {"Total":>10s} {n_oty:>6d} {n_total-n_oty:>7d} {n_total:>6d}')

# Fisher exact test
if n_total > 0 and n_hot > 0 and n_cold > 0:
    total_comb = comb(n_total, n_hot)
    p_value = 0
    # One-tailed: hot has FEWER oty than expected
    for x in range(0, all_hot_oty + 1):
        p_value += comb(n_oty, x) * comb(n_total - n_oty, n_hot - x) / total_comb

    cold_rate = all_cold_oty / max(n_cold, 1)
    hot_rate = all_hot_oty / max(n_hot, 1)

    print(f'\n  Cold with oty: {all_cold_oty}/{n_cold} = {cold_rate:.1%}')
    print(f'  Hot with oty:  {all_hot_oty}/{n_hot} = {hot_rate:.1%}')
    if hot_rate > 0:
        print(f'  Enrichment: {cold_rate/hot_rate:.1f}x in cold vs hot')
    print(f'  Fisher exact test (one-tailed): p = {p_value:.4f}')

    if p_value < 0.01:
        print(f'\n  ★★★ CONFIRMED at p < 0.01 ★★★')
    elif p_value < 0.05:
        print(f'\n  ★★ Significant at p < 0.05 ★★')
    else:
        print(f'\n  Not significant (p >= 0.05)')

# ================================================================
# ALSO: test oty position across ALL herbal folios (even unidentified)
# ================================================================
print(f'\n\n{"="*70}')
print('OTY PREVALENCE ACROSS ALL SECTIONS')
print('='*70)

section_oty = defaultdict(lambda: {'with': 0, 'without': 0})
for fid, folio in vms['folios'].items():
    sec = folio['metadata']['section']
    has = has_oty_in_first_n_lines(fid, 3)
    if has:
        section_oty[sec]['with'] += 1
    else:
        section_oty[sec]['without'] += 1

for sec in sorted(section_oty.keys()):
    w = section_oty[sec]['with']
    wo = section_oty[sec]['without']
    total = w + wo
    pct = w * 100 // max(total, 1)
    print(f'  {sec:>12s}: {w:>3d}/{total:>3d} = {pct:>2d}% have oty in L1-3')

# ================================================================
# SAVE
# ================================================================
output = {
    'herbal_b_folios': len(herbal_b_folios),
    'herbal_b_identified': len(b_identified),
    'herbal_b_with_oty': [(f, p, q) for f, p, q in b_with_oty],
    'combined_test': {
        'hot_oty': all_hot_oty,
        'hot_no_oty': all_hot_no_oty,
        'cold_oty': all_cold_oty,
        'cold_no_oty': all_cold_no_oty,
        'p_value': p_value if n_total > 0 else None,
    },
}

with open(os.path.join(RESULTS, 'attack4_results.json'), 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f'\nSaved attack4_results.json')
