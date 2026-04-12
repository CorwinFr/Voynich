"""
SESSION 17 — ATTACK 1: Clean false positives

Problem: 23 roots are 2-3 chars. They match inside longer words by chance.
This inflates decode rates from ~5% real to 42% apparent.

Solution: Compute TWO decode rates per folio:
  - STRICT: only roots >= 4 chars + logograms + confirmed 3-char in context
  - LENIENT: all roots (current method, for comparison)

Also identify which short roots are REAL (appear standalone or in confirmed
compounds) vs NOISE (only appear as substrings of unknown words).
"""
import json, sys, io, os
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.dirname(__file__)
VMS_PATH = os.path.join(BASE, '..', 'vms', 'vms_structured.json')
REG_PATH = os.path.join(BASE, '..', 'hypothesis_registry.json')
RESULTS = BASE

with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)
with open(REG_PATH, encoding='utf-8') as f:
    registry = json.load(f)

LOGOS = {'o': 'ac', 'l': 'se', 'd': 'de', 'r': 'recipe', 'v': 'vel',
         'x': 'crux', 'k': 'cum', 'm': 'misce', 'f': 'per', 't': 'et',
         'y': 'in', 'c': 'cum', 's': 'est', 'sh': 'ci', 'p': 'usque', 'ch': 'cum'}
LOGO_SET = set(LOGOS.keys())

# Build root dictionaries by confidence tier
TIER1 = {}  # confirmed >= 0.8
TIER2 = {}  # probable >= 0.7
TIER3 = {}  # rest

for root, data in registry['confirmed_ingredients'].items():
    conf = data.get('confidence', 0.9)
    if conf >= 0.8:
        TIER1[root] = data['latin']
    else:
        TIER2[root] = data['latin']

for root, data in registry.get('probable_ingredients', {}).items():
    if data.get('status') == 'ELIMINATED':
        continue
    conf = data.get('confidence', 0.5)
    if conf >= 0.7:
        TIER2[root] = data['latin']
    else:
        TIER3[root] = data['latin']

for root, data in registry['plant_names'].items():
    TIER3[root] = data['latin']

print(f'Vocabulary tiers:')
print(f'  TIER1 (conf >= 0.8): {len(TIER1)} roots: {list(TIER1.keys())}')
print(f'  TIER2 (conf >= 0.7): {len(TIER2)} roots')
print(f'  TIER3 (conf < 0.7):  {len(TIER3)} roots')

# ================================================================
# Compute STRICT vs LENIENT decode rates
# ================================================================
STRICT_MIN_LEN = 4  # roots must be >= 4 chars for strict mode

all_tiers = {}
all_tiers.update(TIER3)
all_tiers.update(TIER2)
all_tiers.update(TIER1)

strict_roots = {r: l for r, l in all_tiers.items() if len(r) >= STRICT_MIN_LEN}
lenient_roots = all_tiers

sorted_strict = sorted(strict_roots.keys(), key=len, reverse=True)
sorted_lenient = sorted(lenient_roots.keys(), key=len, reverse=True)

def find_root_in(eva, root_list):
    for root in root_list:
        if len(root) < 2:
            continue
        if root in eva:
            return root
    return None

# Per-section stats
section_stats = defaultdict(lambda: {'strict_dec': 0, 'lenient_dec': 0,
                                      'logo': 0, 'total': 0})
folio_stats = []

for fid, folio in sorted(vms['folios'].items()):
    sec = folio['metadata']['section']
    strict_dec = 0
    lenient_dec = 0
    logo_dec = 0
    total = 0

    for block in folio['blocks']:
        for line in block['lines']:
            for w in line['words']:
                eva = w['eva_primary']
                total += 1

                if eva in LOGO_SET:
                    logo_dec += 1
                    continue

                if find_root_in(eva, sorted_strict):
                    strict_dec += 1
                if find_root_in(eva, sorted_lenient):
                    lenient_dec += 1

    section_stats[sec]['strict_dec'] += strict_dec
    section_stats[sec]['lenient_dec'] += lenient_dec
    section_stats[sec]['logo'] += logo_dec
    section_stats[sec]['total'] += total

    if total > 0:
        folio_stats.append({
            'fid': fid,
            'section': sec,
            'total': total,
            'logo': logo_dec,
            'strict': strict_dec,
            'lenient': lenient_dec,
            'strict_pct': (logo_dec + strict_dec) * 100 // total,
            'lenient_pct': (logo_dec + lenient_dec) * 100 // total,
        })

# ================================================================
# RESULTS
# ================================================================
print(f'\n{"="*70}')
print('DECODE RATES BY SECTION')
print('='*70)

total_all = sum(s['total'] for s in section_stats.values())
total_logo = sum(s['logo'] for s in section_stats.values())
total_strict = sum(s['strict_dec'] for s in section_stats.values())
total_lenient = sum(s['lenient_dec'] for s in section_stats.values())

print(f'\n  {"Section":>12s} {"Total":>6s} {"Logo":>5s} {"Strict":>7s} {"Lenient":>8s} '
      f'{"Strict%":>8s} {"Lenient%":>9s} {"Inflation":>10s}')
print('  ' + '-' * 75)

for sec in sorted(section_stats.keys()):
    s = section_stats[sec]
    t = max(s['total'], 1)
    sp = (s['logo'] + s['strict_dec']) * 100 // t
    lp = (s['logo'] + s['lenient_dec']) * 100 // t
    inf = lp - sp
    print(f'  {sec:>12s} {s["total"]:>6d} {s["logo"]:>5d} {s["strict_dec"]:>7d} '
          f'{s["lenient_dec"]:>8d} {sp:>7d}% {lp:>8d}% {inf:>+9d}pp')

sp_all = (total_logo + total_strict) * 100 // total_all
lp_all = (total_logo + total_lenient) * 100 // total_all
print(f'  {"TOTAL":>12s} {total_all:>6d} {total_logo:>5d} {total_strict:>7d} '
      f'{total_lenient:>8d} {sp_all:>7d}% {lp_all:>8d}% {lp_all-sp_all:>+9d}pp')

# ================================================================
# TOP 10 folios by STRICT decode rate
# ================================================================
print(f'\n{"="*70}')
print('TOP 20 FOLIOS BY STRICT DECODE RATE')
print('='*70)

folio_stats.sort(key=lambda x: -x['strict_pct'])

print(f'\n  {"Folio":>8s} {"Section":>12s} {"Total":>5s} {"Strict%":>8s} {"Lenient%":>9s} {"Inflation":>10s}')
print('  ' + '-' * 60)

for fs in folio_stats[:20]:
    inf = fs['lenient_pct'] - fs['strict_pct']
    print(f'  {fs["fid"]:>8s} {fs["section"]:>12s} {fs["total"]:>5d} '
          f'{fs["strict_pct"]:>7d}% {fs["lenient_pct"]:>8d}% {inf:>+9d}pp')

# ================================================================
# ANALYSIS: Which short roots are REAL vs NOISE?
# ================================================================
print(f'\n{"="*70}')
print('SHORT ROOT ANALYSIS (2-3 chars)')
print('='*70)

short_roots = {r: l for r, l in all_tiers.items() if len(r) <= 3}

for root, latin in sorted(short_roots.items(), key=lambda x: x[0]):
    # Count: standalone occurrences vs substring-only
    standalone = 0
    as_substring = 0
    as_prefix_of_known = 0

    for fid, folio in vms['folios'].items():
        for block in folio['blocks']:
            for line in block['lines']:
                for w in line['words']:
                    eva = w['eva_primary']
                    morph_root = (w.get('morphology') or {}).get('root', '')
                    if morph_root == root:
                        standalone += 1
                    elif root in eva and morph_root != root:
                        as_substring += 1

    total_occ = standalone + as_substring
    standalone_pct = standalone * 100 // max(total_occ, 1)

    status = 'REAL' if standalone_pct >= 30 else 'NOISE' if standalone_pct < 10 else 'MIXED'
    tier = 'T1' if root in TIER1 else 'T2' if root in TIER2 else 'T3'

    print(f'  {root:>5s} = {latin:>15s} [{tier}]  '
          f'standalone={standalone:>4d} substr={as_substring:>5d} '
          f'({standalone_pct:>2d}% standalone) → {status}')

# ================================================================
# SAVE
# ================================================================
output = {
    'strict_total_pct': sp_all,
    'lenient_total_pct': lp_all,
    'inflation': lp_all - sp_all,
    'section_stats': {sec: dict(s) for sec, s in section_stats.items()},
    'top20_strict': [{'fid': fs['fid'], 'section': fs['section'],
                      'strict_pct': fs['strict_pct'], 'lenient_pct': fs['lenient_pct']}
                     for fs in folio_stats[:20]],
    'strict_roots_count': len(strict_roots),
    'lenient_roots_count': len(lenient_roots),
}

with open(os.path.join(RESULTS, 'attack1_results.json'), 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f'\nSaved attack1_results.json')
