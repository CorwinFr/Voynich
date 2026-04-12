"""
SESSION 17 PREP — Volvelle re-analysis + Hot/Cold new approach

Part A: Re-analyze volvelle f57v with current knowledge
  - Ring labels: are they plant names? ingredient codes?
  - The alphabet lines: does the ordering mean anything?

Part B: Hot/Cold — NEW approach
  Instead of looking for a specific word, look at:
  1. Character-level frequencies (which EVA chars are more common in hot vs cold?)
  2. The BASE ELEMENT of the first root (ch- vs sh- vs ot- etc.)
  3. Total vocabulary overlap between hot and cold folios
  4. Maybe hot/cold is encoded in the SUFFIX of the plant name, not a separate word
"""
import json, sys, io, os
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.dirname(__file__)
VMS_PATH = os.path.join(BASE, '..', '..', 'vms', 'vms_structured.json')
REG_PATH = os.path.join(BASE, '..', '..', 'hypothesis_registry.json')
RESULTS = os.path.dirname(__file__)

with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)
with open(REG_PATH, encoding='utf-8') as f:
    registry = json.load(f)

STANDARD_QUALITIES = {
    'ruta': 'hot', 'viola': 'cold', 'apium': 'hot', 'salvia': 'hot',
    'lactuca': 'cold', 'origanum': 'hot', 'mentha': 'hot',
    'coriandrum': 'cold', 'verbena': 'cold', 'aristolochia': 'hot',
    'malva': 'cold', 'atriplex': 'cold', 'satureia': 'hot',
    'centaurea': 'hot', 'elleborus': 'hot', 'althaea': 'wet',
    'rosmarinus': 'hot', 'cannabis': 'cold', 'crocus': 'hot',
    'mandragora': 'cold', 'gentiana': 'hot', 'nigella': 'hot',
    'ribes': 'cold', 'pulmonaria': 'cold', 'achillea': 'hot',
    'scorzonera': 'hot', 'anagallis': 'cold', 'spinacia': 'cold',
    'tanacetum': 'hot', 'nymphaea': 'cold',
}

ALL_SHERWOOD = {
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
}

# ================================================================
# PART A: VOLVELLE RE-ANALYSIS
# ================================================================
print('='*70)
print('PART A — VOLVELLE f57v RE-ANALYSIS')
print('='*70)

f57v = vms['folios']['f57v']
print(f'\nAll lines:')
for line in f57v['blocks'][0]['lines']:
    words = [w['eva_primary'] for w in line['words']]
    print(f'  {line["line_id"]:>10s}: {" ".join(words)}')

# Lines 2-3 and 5: the alphabet
# Line 3: o l d r v x k m f @169v t r @170 @171 y
# Line 5: o v l r m aiin d @170 c f s y l k x
print(f'\n  Alphabet line 3: o l d r v x k m f [@169v] t r [@170] [@171] y')
print(f'  Alphabet line 5: o v l r m [aiin] d [@170] c f s y l k x')

# Ring labels (single-word lines 6-12)
ring_labels = []
for line in f57v['blocks'][0]['lines']:
    words = [w['eva_primary'] for w in line['words']]
    if len(words) == 1 and len(words[0]) > 2:
        ring_labels.append(words[0])

print(f'\n  Ring labels: {ring_labels}')

# Check if ring labels contain plant roots
plant_roots = set(registry['plant_names'].keys())
for label in ring_labels:
    matches = []
    for pr in sorted(plant_roots, key=len, reverse=True):
        if pr in label and len(pr) >= 3:
            matches.append(pr)
    if matches:
        print(f'    {label} → contains {matches[0]} ({registry["plant_names"][matches[0]]["latin"]})')
    else:
        # Decompose: what parts do we recognize?
        parts = []
        remaining = label
        from itertools import combinations
        # Simple: check known logograms
        LOGOS = {'o':'ac','l':'se','d':'de','r':'recipe','v':'vel','k':'cum',
                 'm':'misce','f':'per','t':'et','y':'in','c':'cum','s':'est'}
        decomp = []
        for i, ch in enumerate(label):
            if ch in LOGOS:
                decomp.append(f'{ch}({LOGOS[ch]})')
            else:
                decomp.append(ch)
        print(f'    {label} → {"·".join(decomp)}')


# ================================================================
# PART B: HOT/COLD — APPROACH 1: Plant name suffix
# ================================================================
print(f'\n\n{"="*70}')
print('PART B1 — HOT/COLD: Plant name SUFFIX')
print('='*70)

# Hypothesis: the suffix of the plant name (first word of herbal folio)
# might encode the quality. E.g. -ody = hot, -aiin = cold?

hot_suffixes = Counter()
cold_suffixes = Counter()

for fid, plant in ALL_SHERWOOD.items():
    if fid not in vms['folios']:
        continue
    qual = STANDARD_QUALITIES.get(plant)
    if not qual:
        continue
    is_cold = qual in ('cold', 'wet')

    # Get first word and its suffix
    folio = vms['folios'][fid]
    first_word = None
    first_suffix = ''
    for block in folio['blocks']:
        for line in block['lines']:
            if line['words']:
                w = line['words'][0]
                first_word = w['eva_primary']
                first_suffix = (w.get('morphology') or {}).get('suffix', '')
                break
        if first_word:
            break

    if not first_word:
        continue

    # Also extract last 2-3 chars as suffix
    last2 = first_word[-2:] if len(first_word) >= 2 else first_word
    last3 = first_word[-3:] if len(first_word) >= 3 else first_word

    if is_cold:
        cold_suffixes[last3] += 1
    else:
        hot_suffixes[last3] += 1

    label = 'COLD' if is_cold else 'HOT'
    sfx_str = first_suffix or ''
    print(f'  {fid:>8s} {plant:>15s} [{label:>4s}]  word={first_word:>15s}  '
          f'morph_sfx={sfx_str:>6s}  last3={last3}')

# Any suffix distinctly hot or cold?
all_sfx = set(hot_suffixes.keys()) | set(cold_suffixes.keys())
print(f'\n  Suffix analysis (last 3 chars of plant name):')
print(f'  {"Suffix":>8s} {"Hot":>4s} {"Cold":>5s} {"Ratio":>6s}')
for sfx in sorted(all_sfx, key=lambda s: -(hot_suffixes.get(s,0) + cold_suffixes.get(s,0))):
    h = hot_suffixes.get(sfx, 0)
    c = cold_suffixes.get(sfx, 0)
    if (h + c) >= 2:
        ratio = h / max(c, 0.1)
        print(f'  {sfx:>8s} {h:>4d} {c:>5d} {ratio:>6.1f}')


# ================================================================
# PART B2: HOT/COLD — Character frequency in entire folio
# ================================================================
print(f'\n\n{"="*70}')
print('PART B2 — HOT/COLD: Character frequency in folio')
print('='*70)

# For each EVA character, is it more frequent in hot or cold folios?
hot_chars = Counter()
cold_chars = Counter()
hot_total = 0
cold_total = 0

for fid, plant in ALL_SHERWOOD.items():
    if fid not in vms['folios']:
        continue
    qual = STANDARD_QUALITIES.get(plant)
    if not qual:
        continue
    is_cold = qual in ('cold', 'wet')

    folio = vms['folios'][fid]
    for block in folio['blocks']:
        for line in block['lines']:
            for w in line['words']:
                for c in w['eva_primary']:
                    if is_cold:
                        cold_chars[c] += 1
                        cold_total += 1
                    else:
                        hot_chars[c] += 1
                        hot_total += 1

print(f'\n  Hot total chars: {hot_total}, Cold total chars: {cold_total}')
print(f'\n  {"Char":>5s} {"Hot%":>6s} {"Cold%":>7s} {"Diff":>6s} {"Direction"}')
print('  ' + '-' * 40)

all_chars = set(hot_chars.keys()) | set(cold_chars.keys())
char_diffs = []
for c in sorted(all_chars):
    h_pct = hot_chars.get(c, 0) * 1000 // max(hot_total, 1)
    c_pct = cold_chars.get(c, 0) * 1000 // max(cold_total, 1)
    diff = h_pct - c_pct
    char_diffs.append((c, h_pct, c_pct, diff))

char_diffs.sort(key=lambda x: -abs(x[3]))
for c, h, co, diff in char_diffs[:15]:
    direction = 'HOT' if diff > 0 else 'COLD'
    print(f'  {c:>5s} {h/10:>5.1f}% {co/10:>6.1f}% {diff/10:>+5.1f}% {direction}')


# ================================================================
# PART B3: HOT/COLD — Line 2 specific words
# ================================================================
print(f'\n\n{"="*70}')
print('PART B3 — HOT/COLD: Line 2 words (quality declaration zone)')
print('='*70)

# In Macer, quality is often in the 2nd-4th line.
# Maybe the SECOND LINE of VMS herbal folios contains the quality info.

hot_line2_roots = Counter()
cold_line2_roots = Counter()

for fid, plant in ALL_SHERWOOD.items():
    if fid not in vms['folios']:
        continue
    qual = STANDARD_QUALITIES.get(plant)
    if not qual:
        continue
    is_cold = qual in ('cold', 'wet')

    folio = vms['folios'][fid]
    line_count = 0
    for block in folio['blocks']:
        for line in block['lines']:
            line_count += 1
            if line_count == 2:
                for w in line['words']:
                    root = (w.get('morphology') or {}).get('root', '')
                    if root and len(root) >= 3:
                        if is_cold:
                            cold_line2_roots[root] += 1
                        else:
                            hot_line2_roots[root] += 1
                break
        if line_count >= 2:
            break

# Find roots that distinguish hot from cold
all_l2_roots = set(hot_line2_roots.keys()) | set(cold_line2_roots.keys())
discriminants = []

for root in all_l2_roots:
    h = hot_line2_roots.get(root, 0)
    c = cold_line2_roots.get(root, 0)
    if (h + c) >= 3:
        total = h + c
        hot_rate = h / total
        discriminants.append((root, h, c, hot_rate))

discriminants.sort(key=lambda x: -x[3])

print(f'\n  Roots in LINE 2 (3+ occurrences):')
print(f'  {"Root":>10s} {"Hot":>4s} {"Cold":>5s} {"Hot%":>6s}')
print('  ' + '-' * 30)
for root, h, c, hr in discriminants:
    direction = '← HOT' if hr > 0.7 else '← COLD' if hr < 0.3 else ''
    print(f'  {root:>10s} {h:>4d} {c:>5d} {hr:>5.0%} {direction}')


# ================================================================
# PART B4: HOT/COLD — Composition pattern of plant name
# ================================================================
print(f'\n\n{"="*70}')
print('PART B4 — HOT/COLD: Plant name BASE element')
print('='*70)

# The plant name = base + modification
# Does the BASE (ch, sh, ot, etc.) correlate with hot/cold?

hot_bases = Counter()
cold_bases = Counter()

for fid, plant in ALL_SHERWOOD.items():
    if fid not in vms['folios']:
        continue
    qual = STANDARD_QUALITIES.get(plant)
    if not qual:
        continue
    is_cold = qual in ('cold', 'wet')

    folio = vms['folios'][fid]
    first_root = ''
    for block in folio['blocks']:
        for line in block['lines']:
            if line['words']:
                first_root = (line['words'][0].get('morphology') or {}).get('root', '')
                break
        if first_root:
            break

    if not first_root or len(first_root) < 2:
        continue

    # Extract base: first 2-3 characters (the Tironian base element)
    base2 = first_root[:2]
    base3 = first_root[:3] if len(first_root) >= 3 else first_root

    if is_cold:
        cold_bases[base2] += 1
    else:
        hot_bases[base2] += 1

    label = 'COLD' if is_cold else 'HOT'
    print(f'  {fid:>8s} {plant:>15s} [{label:>4s}]  root={first_root:>10s}  base={base2}')

all_bases = set(hot_bases.keys()) | set(cold_bases.keys())
print(f'\n  Base (first 2 chars of root) vs quality:')
print(f'  {"Base":>6s} {"Hot":>4s} {"Cold":>5s}')
for base in sorted(all_bases, key=lambda b: -(hot_bases.get(b,0)+cold_bases.get(b,0))):
    h = hot_bases.get(base, 0)
    c = cold_bases.get(base, 0)
    if (h + c) >= 2:
        direction = '← HOT' if h > c * 2 else '← COLD' if c > h * 2 else ''
        print(f'  {base:>6s} {h:>4d} {c:>5d} {direction}')


# Save
output = {
    'volvelle_ring_labels': ring_labels,
    'plant_name_suffixes_hot': dict(hot_suffixes),
    'plant_name_suffixes_cold': dict(cold_suffixes),
    'char_enrichment': [(c, h, co, d) for c, h, co, d in char_diffs[:10]],
    'line2_discriminants': [(r, h, c, hr) for r, h, c, hr in discriminants],
}

with open(os.path.join(RESULTS, 'volvelle_hotcold.json'), 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f'\nSaved volvelle_hotcold.json')
