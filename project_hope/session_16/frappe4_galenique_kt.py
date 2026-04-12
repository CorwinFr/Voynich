"""
SESSION 16 — FRAPPE 4: Galenic k/t validation

Test whether the k/t ratio per folio correlates with hot/cold
galenic qualities from the Tacuinum Sanitatis and Macer Floridus.

For the 16 anchor folios where we know the plant identity:
1. Get the galenic qualities from Macer (calidus/frigidus/siccus/humidus)
2. Get the k/t ratio from the VMS folio
3. Test: does k correlate with cold, t with hot?

Also uses S12_TACUINUM.json if available.
"""
import json, sys, io, os
from collections import Counter
import math

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.dirname(__file__)
VMS_PATH = os.path.join(BASE, '..', 'vms', 'vms_structured.json')
MACER_PATH = os.path.join(BASE, '..', 'session_14', 'macer_complete.json')
TAC_PATH = os.path.join(BASE, '..', '..', 'attacks', 'RECIPE_DATASET', 'S12_TACUINUM.json')
RESULTS = BASE

with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)
with open(MACER_PATH, encoding='utf-8') as f:
    macer = json.load(f)

# ================================================================
# ANCHORS
# ================================================================
ANCHORS = {
    'f48v': 'ruta',      'f9v': 'viola',       'f44v': 'apium',
    'f51v': 'salvia',    'f29r': 'lactuca',    'f41r': 'origanum',
    'f37r': 'mentha',    'f41v': 'coriandrum', 'f22r': 'verbena',
    'f28r': 'aristolochia', 'f5v': 'malva',    'f45r': 'atriplex',
    'f66v': 'satureia',  'f65v': 'centaurea',  'f3v': 'elleborus',
    'f95v1': 'althaea',
}

# Match Macer chapters
MACER_BY_NAME = {}
for ch in macer['chapters']:
    MACER_BY_NAME[ch['name'].lower()] = ch
if 'violae' in MACER_BY_NAME:
    MACER_BY_NAME['viola'] = MACER_BY_NAME['violae']

# ================================================================
# GET k/t COUNTS PER FOLIO
# ================================================================
def get_kt_ratio(fid):
    """Count k and t occurrences in a folio."""
    folio = vms['folios'].get(fid)
    if not folio:
        return None, None, None
    k_count = 0
    t_count = 0
    for block in folio['blocks']:
        for line in block['lines']:
            for w in line['words']:
                eva = w['eva_primary']
                # Count gallows k and t
                k_count += eva.count('k')
                t_count += eva.count('t')
    total = k_count + t_count
    if total == 0:
        return 0, 0, 0.5
    ratio = k_count / total
    return k_count, t_count, ratio

# ================================================================
# GET MACER QUALITIES
# ================================================================
def get_qualities(plant_name):
    """Get galenic qualities from Macer chapter."""
    ch = MACER_BY_NAME.get(plant_name)
    if not ch:
        return {}
    quals = {}
    for q in ch.get('qualities', []):
        q_name = q.replace('Q_', '')
        quals[q_name] = True
    return quals

# ================================================================
# ANALYSIS
# ================================================================
print('='*70)
print('FRAPPE 4 — GALENIC k/t VALIDATION')
print('='*70)

data_points = []

print(f'\n  {"Folio":>8s} {"Plant":>15s} {"k":>4s} {"t":>4s} {"k/(k+t)":>8s} {"Qualities"}')
print('  ' + '-' * 65)

for fid, plant in sorted(ANCHORS.items()):
    if fid not in vms['folios']:
        continue

    k, t, ratio = get_kt_ratio(fid)
    quals = get_qualities(plant)
    qual_str = ', '.join(sorted(quals.keys())) if quals else '(none)'

    # Determine hot/cold score
    # hot = +1, cold = -1, neutral = 0
    hot_cold = 0
    if 'calidus' in quals:
        hot_cold += 1
    if 'frigidus' in quals:
        hot_cold -= 1

    data_points.append({
        'fid': fid,
        'plant': plant,
        'k': k,
        't': t,
        'ratio': ratio,
        'qualities': quals,
        'hot_cold': hot_cold,
    })

    marker = ''
    if hot_cold > 0:
        marker = ' ← HOT'
    elif hot_cold < 0:
        marker = ' ← COLD'

    print(f'  {fid:>8s} {plant:>15s} {k:>4d} {t:>4d} {ratio:>8.3f} {qual_str}{marker}')

# ================================================================
# CORRELATION TEST
# ================================================================
print(f'\n\n  CORRELATION ANALYSIS:')

# Separate into hot, cold, neutral
hot_ratios = [d['ratio'] for d in data_points if d['hot_cold'] > 0]
cold_ratios = [d['ratio'] for d in data_points if d['hot_cold'] < 0]
neutral_ratios = [d['ratio'] for d in data_points if d['hot_cold'] == 0]

if hot_ratios:
    print(f'\n  HOT plants ({len(hot_ratios)}): mean k/(k+t) = {sum(hot_ratios)/len(hot_ratios):.3f}')
    for d in data_points:
        if d['hot_cold'] > 0:
            print(f'    {d["fid"]:>8s} {d["plant"]:>15s}  k/(k+t)={d["ratio"]:.3f}')

if cold_ratios:
    print(f'\n  COLD plants ({len(cold_ratios)}): mean k/(k+t) = {sum(cold_ratios)/len(cold_ratios):.3f}')
    for d in data_points:
        if d['hot_cold'] < 0:
            print(f'    {d["fid"]:>8s} {d["plant"]:>15s}  k/(k+t)={d["ratio"]:.3f}')

if neutral_ratios:
    print(f'\n  NEUTRAL plants ({len(neutral_ratios)}): mean k/(k+t) = {sum(neutral_ratios)/len(neutral_ratios):.3f}')

# If hypothesis k=cold, t=hot:
# Then HOT plants should have LOW k/(k+t) = more t
# And COLD plants should have HIGH k/(k+t) = more k
if hot_ratios and cold_ratios:
    hot_mean = sum(hot_ratios) / len(hot_ratios)
    cold_mean = sum(cold_ratios) / len(cold_ratios)

    print(f'\n  HYPOTHESIS: k=cold, t=hot')
    print(f'  → HOT plants should have LOW k/(k+t):  {hot_mean:.3f}')
    print(f'  → COLD plants should have HIGH k/(k+t): {cold_mean:.3f}')

    if cold_mean > hot_mean:
        diff = cold_mean - hot_mean
        print(f'  → Direction CORRECT (cold-hot = +{diff:.3f})')
    else:
        diff = hot_mean - cold_mean
        print(f'  → Direction WRONG (hot-cold = +{diff:.3f})')

    # Mann-Whitney U test approximation (simple rank test)
    all_vals = [(r, 'hot') for r in hot_ratios] + [(r, 'cold') for r in cold_ratios]
    all_vals.sort(key=lambda x: x[0])
    hot_ranks = []
    cold_ranks = []
    for rank, (val, group) in enumerate(all_vals, 1):
        if group == 'hot':
            hot_ranks.append(rank)
        else:
            cold_ranks.append(rank)

    n1, n2 = len(hot_ratios), len(cold_ratios)
    R1 = sum(hot_ranks)
    U1 = R1 - n1 * (n1 + 1) / 2
    U2 = n1 * n2 - U1

    print(f'\n  Rank test: U_hot={U1:.0f}, U_cold={U2:.0f}')
    print(f'  n_hot={n1}, n_cold={n2}')
    print(f'  Expected U under null = {n1*n2/2:.0f}')

    # For small samples, compute exact significance is complex
    # Just report the direction and effect size
    effect_size = abs(U1 - n1*n2/2) / (n1*n2)
    print(f'  Effect size (|U-E|/n1n2) = {effect_size:.3f}')

# ================================================================
# TACUINUM ENRICHMENT (if available)
# ================================================================
if os.path.exists(TAC_PATH):
    print(f'\n\n{"="*70}')
    print('TACUINUM SANITATIS — Extended quality data')
    print('='*70)

    with open(TAC_PATH, encoding='utf-8') as f:
        tac = json.load(f)

    # Match plants to Tacuinum entries
    tac_quals = {}
    for entry in tac.get('entries', []):
        name = entry.get('name', '').lower().strip()
        quals = []
        for q in entry.get('qualities', []):
            q_name = q.replace('Q_', '').lower()
            quals.append(q_name)
        if name and quals:
            tac_quals[name] = quals

    print(f'  Tacuinum entries with qualities: {len(tac_quals)}')

    # Match our anchor plants
    matched = 0
    tac_hot = []
    tac_cold = []
    for fid, plant in sorted(ANCHORS.items()):
        if fid not in vms['folios']:
            continue
        # Try to find in Tacuinum
        tq = tac_quals.get(plant)
        if not tq:
            # Try partial match
            for tname, tqs in tac_quals.items():
                if plant[:4] in tname or tname[:4] in plant:
                    tq = tqs
                    break

        if tq:
            matched += 1
            k, t, ratio = get_kt_ratio(fid)
            is_hot = any('calid' in q or 'hot' in q or 'warm' in q for q in tq)
            is_cold = any('frigid' in q or 'cold' in q or 'cool' in q for q in tq)
            if is_hot:
                tac_hot.append(ratio)
            if is_cold:
                tac_cold.append(ratio)
            marker = 'HOT' if is_hot else ('COLD' if is_cold else '')
            print(f'  {fid:>8s} {plant:>15s}  k/(k+t)={ratio:.3f}  '
                  f'tac=[{", ".join(tq[:3])}]  {marker}')

    if tac_hot and tac_cold:
        print(f'\n  Tacuinum HOT mean k/(k+t) = {sum(tac_hot)/len(tac_hot):.3f} (n={len(tac_hot)})')
        print(f'  Tacuinum COLD mean k/(k+t) = {sum(tac_cold)/len(tac_cold):.3f} (n={len(tac_cold)})')

# ================================================================
# DRY/WET ANALYSIS
# ================================================================
print(f'\n\n{"="*70}')
print('DRY/WET ANALYSIS')
print('='*70)

dry_ratios = [d['ratio'] for d in data_points if 'siccus' in d['qualities']]
wet_ratios = [d['ratio'] for d in data_points if 'humidus' in d['qualities']]

if dry_ratios:
    print(f'\n  DRY plants ({len(dry_ratios)}): mean k/(k+t) = {sum(dry_ratios)/len(dry_ratios):.3f}')
if wet_ratios:
    print(f'\n  WET plants ({len(wet_ratios)}): mean k/(k+t) = {sum(wet_ratios)/len(wet_ratios):.3f}')

# ================================================================
# ALL HERBAL FOLIOS k/t distribution
# ================================================================
print(f'\n\n{"="*70}')
print('ALL HERBAL FOLIOS — k/t distribution')
print('='*70)

all_herbal_ratios = []
for fid, folio in sorted(vms['folios'].items()):
    if folio['metadata']['section'] != 'herbal':
        continue
    k, t, ratio = get_kt_ratio(fid)
    if k is not None and (k + t) >= 3:  # minimum 3 occurrences
        all_herbal_ratios.append((fid, k, t, ratio))

all_herbal_ratios.sort(key=lambda x: x[3])

# Show distribution in bins
bins = [0, 0.2, 0.4, 0.6, 0.8, 1.01]
for i in range(len(bins)-1):
    count = sum(1 for _, _, _, r in all_herbal_ratios if bins[i] <= r < bins[i+1])
    bar = '#' * count
    print(f'  k/(k+t) [{bins[i]:.1f}-{bins[i+1]:.1f}): {count:3d} {bar}')

print(f'\n  Total herbal folios with 3+ k/t: {len(all_herbal_ratios)}')
mean_all = sum(r for _, _, _, r in all_herbal_ratios) / max(len(all_herbal_ratios), 1)
print(f'  Mean k/(k+t) = {mean_all:.3f}')

# ================================================================
# SAVE
# ================================================================
output = {
    'anchor_data': [{
        'fid': d['fid'],
        'plant': d['plant'],
        'k': d['k'],
        't': d['t'],
        'ratio': d['ratio'],
        'qualities': list(d['qualities'].keys()),
        'hot_cold': d['hot_cold'],
    } for d in data_points],
    'hot_mean': sum(hot_ratios)/len(hot_ratios) if hot_ratios else None,
    'cold_mean': sum(cold_ratios)/len(cold_ratios) if cold_ratios else None,
    'direction_correct': (sum(cold_ratios)/len(cold_ratios) > sum(hot_ratios)/len(hot_ratios)) if (hot_ratios and cold_ratios) else None,
    'n_herbal_folios': len(all_herbal_ratios),
    'mean_all': mean_all,
}

with open(os.path.join(RESULTS, 'frappe4_results.json'), 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f'\nSaved frappe4_results.json')
