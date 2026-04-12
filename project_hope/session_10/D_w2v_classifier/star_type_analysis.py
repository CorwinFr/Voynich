"""
STAR TYPE ANALYSIS — Do structural anomalies correlate across pharma?

User observation: f103r has two types of star markers:
  - RED/FILLED stars → recipe-like blocks
  - EMPTY/OUTLINE stars → anomalous blocks (B12, B15)

We can't distinguish star types from transcription, but we CAN:
1. Run the same structural audit on ALL pharma folios
2. Flag blocks that look anomalous (no verbs, no ingredients, dose-heavy)
3. Map their positions → are anomalous blocks clustered at folio edges?
4. Count how many total anomalies exist in all of pharma
"""
import json, sys, io, os
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.dirname(__file__)
VMS_PATH = os.path.join(BASE, '..', '..', 'vms', 'vms_structured.json')
CROSSREF_PATH = os.path.join(BASE, '..', '..', 'session_09', 'results', 'plant_crossref_complete.json')
RESULTS = os.path.join(BASE, 'results')

LOGOGRAMS = {'o','l','d','r','v','x','k','m','f','t','y','c','s','sh','p','air','ch','h'}

with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)

with open(CROSSREF_PATH, encoding='utf-8') as f:
    crossref = json.load(f)
herbal_roots = set(entry['root'] for entry in crossref['crossref'])

# Prefix stripping for ingredient detection
def has_herbal_root(eva, morph_root):
    """Check if word contains a herbal root (with prefix stripping)."""
    if morph_root in herbal_roots:
        return True
    prefixes = ['qo', 'op', 'ot', 'ok', 'sh', 'ch', 'p', 't', 'k', 'f', 'o', 'd', 'l', 's']
    for pfx in prefixes:
        if eva.startswith(pfx) and len(eva) > len(pfx) + 1:
            stripped = eva[len(pfx):]
            if stripped in herbal_roots:
                return True
            # Double strip (prefix + suffix)
            for suf in ['edy', 'eey', 'ey', 'ol', 'al', 'ar', 'or', 'dy']:
                if stripped.endswith(suf) and len(stripped) > len(suf) + 1:
                    inner = stripped[:-len(suf)]
                    if inner in herbal_roots:
                        return True
    return False

# ================================================================
# Audit ALL pharma blocks
# ================================================================
print('=' * 70)
print('STRUCTURAL AUDIT — ALL PHARMA BLOCKS')
print('=' * 70)

all_blocks = []

for fid, folio in sorted(vms['folios'].items()):
    if folio['metadata']['section'] != 'pharma':
        continue

    for b in folio['blocks']:
        if not b.get('separator'):
            continue

        words = [w for line in b['lines'] for w in line['words']]
        n = len(words)
        if n == 0:
            continue

        n_logo = sum(1 for w in words if w['eva_primary'] in LOGOGRAMS)
        n_dose = sum(1 for w in words
                     if w.get('morphology', {}).get('i_count') is not None)
        n_ingr = sum(1 for w in words
                     if has_herbal_root(w['eva_primary'],
                                       w.get('morphology', {}).get('root', '')))
        n_other = n - n_logo - n_dose - n_ingr

        # Structural flags
        has_verb_proxy = n_logo > 0  # logograms often = verbs
        has_ingredients = n_ingr >= 2
        has_doses = n_dose >= 1
        dose_heavy = n_dose > n * 0.4
        ingr_absent = n_ingr == 0

        # Score (simplified)
        score = 0
        score += min(n_logo, 2) * 10
        score += min(n_ingr, 5) * 8
        score += min(n_dose, 3) * 5
        score -= max(0, n_dose - n * 0.4) * 10  # penalty if dose-heavy

        is_anomaly = (n_ingr == 0 and n_logo == 0) or dose_heavy

        all_blocks.append({
            'folio': fid,
            'block': b['block_id'],
            'n_words': n,
            'n_logo': n_logo,
            'n_dose': n_dose,
            'n_ingr': n_ingr,
            'n_other': n_other,
            'score': score,
            'is_anomaly': is_anomaly,
            'dose_pct': n_dose * 100 // max(n, 1),
            'ingr_pct': n_ingr * 100 // max(n, 1),
        })

# ================================================================
# Summary
# ================================================================
total = len(all_blocks)
anomalies = [b for b in all_blocks if b['is_anomaly']]
normals = [b for b in all_blocks if not b['is_anomaly']]

print(f'\nTotal star-delimited blocks in pharma: {total}')
print(f'  Normal (recipe-like): {len(normals)}')
print(f'  ANOMALOUS: {len(anomalies)}')
print(f'  Anomaly rate: {len(anomalies)*100//total}%')

# ================================================================
# All anomalies — detailed
# ================================================================
print('\n' + '=' * 70)
print(f'ALL {len(anomalies)} ANOMALOUS BLOCKS')
print('=' * 70)

for b in anomalies:
    print(f'\n  {b["block"]:20s} ({b["folio"]})')
    print(f'    {b["n_words"]}w: {b["n_logo"]}logo {b["n_ingr"]}ingr '
          f'{b["n_dose"]}dose({b["dose_pct"]}%) {b["n_other"]}other')

    # Why anomalous?
    reasons = []
    if b['n_ingr'] == 0 and b['n_logo'] == 0:
        reasons.append('NO ingredients, NO logograms')
    if b['dose_pct'] > 40:
        reasons.append(f'DOSE-HEAVY ({b["dose_pct"]}%)')
    if b['n_words'] < 10:
        reasons.append(f'VERY SHORT ({b["n_words"]} words)')
    print(f'    Reason: {"; ".join(reasons)}')

# ================================================================
# Distribution by folio — which folios have anomalies?
# ================================================================
print('\n' + '=' * 70)
print('ANOMALY DISTRIBUTION BY FOLIO')
print('=' * 70)

folio_stats = defaultdict(lambda: {'total': 0, 'anomalies': 0, 'anomaly_ids': []})
for b in all_blocks:
    folio_stats[b['folio']]['total'] += 1
    if b['is_anomaly']:
        folio_stats[b['folio']]['anomalies'] += 1
        folio_stats[b['folio']]['anomaly_ids'].append(b['block'])

for fid in sorted(folio_stats.keys()):
    fs = folio_stats[fid]
    if fs['anomalies'] > 0:
        print(f'  {fid}: {fs["anomalies"]}/{fs["total"]} anomalous '
              f'→ {", ".join(fs["anomaly_ids"])}')

# ================================================================
# Position in folio — are anomalies at the END?
# ================================================================
print('\n' + '=' * 70)
print('POSITION OF ANOMALIES IN FOLIO')
print('=' * 70)

for fid in sorted(folio_stats.keys()):
    fs = folio_stats[fid]
    if fs['anomalies'] == 0:
        continue

    blocks_in_folio = [b for b in all_blocks if b['folio'] == fid]
    n_blocks = len(blocks_in_folio)

    for i, b in enumerate(blocks_in_folio):
        if b['is_anomaly']:
            rel_pos = (i + 1) / n_blocks
            pos_label = 'START' if rel_pos <= 0.25 else 'MIDDLE' if rel_pos <= 0.75 else 'END'
            print(f'  {b["block"]}: position {i+1}/{n_blocks} ({pos_label})')

# ================================================================
# Anomaly block sizes vs normal
# ================================================================
print('\n' + '=' * 70)
print('SIZE COMPARISON: ANOMALY vs NORMAL')
print('=' * 70)

anom_sizes = [b['n_words'] for b in anomalies]
norm_sizes = [b['n_words'] for b in normals]

if anom_sizes and norm_sizes:
    print(f'  Anomalous: n={len(anom_sizes)}, '
          f'min={min(anom_sizes)}, max={max(anom_sizes)}, '
          f'median={sorted(anom_sizes)[len(anom_sizes)//2]}, '
          f'mean={sum(anom_sizes)/len(anom_sizes):.1f}')
    print(f'  Normal:    n={len(norm_sizes)}, '
          f'min={min(norm_sizes)}, max={max(norm_sizes)}, '
          f'median={sorted(norm_sizes)[len(norm_sizes)//2]}, '
          f'mean={sum(norm_sizes)/len(norm_sizes):.1f}')

# Save
results = {
    'total_blocks': total,
    'n_normal': len(normals),
    'n_anomalous': len(anomalies),
    'anomaly_rate': len(anomalies) * 100 // total,
    'anomalies': anomalies,
    'folio_stats': {fid: dict(fs) for fid, fs in folio_stats.items()},
    'note': 'User observed: f103r anomalies (B12, B15) have EMPTY stars, '
            'normals have RED/FILLED stars. Not captured in ZL/LSI transcription.',
}
with open(os.path.join(RESULTS, 'star_type_analysis.json'), 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print('\nSaved star_type_analysis.json')
