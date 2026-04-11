#!/usr/bin/env python3
"""
OPERATION HOPE - Test i-count hypothesis
If a[i*]n encodes numbers: a-i-n=1, a-ii-n=2, a-iii-n=3

Predictions to test:
1. Benford-like distribution (decreasing with i-count)
2. Prefix x i-count profiles differ
3. AN dose distribution correlates with VMS i-count
4. Same pattern in e-count (-ey/-eey/-eeey) for second unit?
5. Folio-level variation consistent with recipe variation
"""

import re, json, math
from collections import Counter, defaultdict

IVTFF = "/sessions/laughing-jolly-bell/mnt/Voynich FINAL/OPERATION_HOPE/data/LSI_ivtff_0d.txt"
AN_PATH = "/sessions/laughing-jolly-bell/mnt/Voynich FINAL/RECIPE_DATASET/S01_AN.json"

def get_section(folio):
    m = re.match(r'f(\d+)', folio)
    if not m:
        return 'other'
    num = int(m.group(1))
    if 1 <= num <= 56: return 'herbal_a'
    elif 57 <= num <= 66: return 'herbal_b'
    elif 67 <= num <= 73: return 'astro'
    elif 75 <= num <= 84: return 'balnea'
    elif 85 <= num <= 86: return 'bio'
    elif 87 <= num <= 116: return 'pharma'
    return 'other'

# Parse IVTFF
all_seq = []
with open(IVTFF, encoding='latin-1') as f:
    for line in f:
        line = line.rstrip('\n')
        if not line or line.startswith('#'):
            continue
        m = re.match(r'<(f\d+\w?\d?)\.(\d+),[^;]*;H>\s*(.*)', line)
        if not m:
            continue
        folio = m.group(1)
        section = get_section(folio)
        text = m.group(3).strip()
        text = re.sub(r'\{[^}]*\}', '', text)
        text = re.sub(r'<[^>]*>', '', text)
        text = re.sub(r'[!\?\*\'"]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        words = [w.strip() for w in text.split('.') if w.strip()]
        expanded = []
        for w in words:
            parts = w.split()
            expanded.extend([p for p in parts if p and re.match(r'^[a-zA-Z]+$', p)])
        for i, w in enumerate(expanded):
            all_seq.append({
                'word': w, 'folio': folio, 'section': section,
                'pos': i, 'total': len(expanded)
            })

# ========================================================================
# EXTRACTION : decompose each word containing 'a[i]+n' pattern
# ========================================================================
print("=" * 70)
print("DECOMPOSITION a[i*]n - EXTRACTION SYSTEMATIQUE")
print("=" * 70)

# Match pattern: prefix + a + i{1,} + n (+ optional suffix)
# The 'n' must be at end or followed by non-i characters
ain_pattern = re.compile(r'^(.+?)a(i+)n(.*)$')

# Also try: pattern where 'a' is start of the suffix
# i.e., word = PREFIX + a + i{n} + n
# More conservative: require prefix to be at least 1 char

entries = []
for entry in all_seq:
    w = entry['word']
    m = ain_pattern.match(w)
    if m:
        prefix = m.group(1)
        i_count = len(m.group(2))
        remainder = m.group(3)
        entries.append({
            'word': w, 'prefix': prefix, 'i_count': i_count,
            'remainder': remainder, 'section': entry['section'],
            'folio': entry['folio'], 'pos': entry['pos'],
            'total': entry['total']
        })

print(f"\nTotal words matching *a[i+]n*: {len(entries)}")

# ========================================================================
# TEST 1: BENFORD - Distribution of i-count
# ========================================================================
print("\n" + "=" * 70)
print("TEST 1: DISTRIBUTION DE i-count (Benford-like?)")
print("=" * 70)

# Global
icount_global = Counter(e['i_count'] for e in entries)
total = sum(icount_global.values())
print(f"\nGlobal (n={total}):")
for ic in sorted(icount_global.keys()):
    c = icount_global[ic]
    bar = "#" * int(c * 100 / total)
    print(f"  i x {ic}: {c:5d} ({100*c/total:5.1f}%) {bar}")

# By section
for sec in ['pharma', 'herbal_a', 'herbal_b', 'balnea', 'astro', 'bio']:
    sec_entries = [e for e in entries if e['section'] == sec]
    if len(sec_entries) < 20:
        continue
    icount_sec = Counter(e['i_count'] for e in sec_entries)
    total_sec = sum(icount_sec.values())
    print(f"\n{sec} (n={total_sec}):")
    for ic in sorted(icount_sec.keys()):
        c = icount_sec[ic]
        bar = "#" * int(c * 100 / total_sec)
        print(f"  i x {ic}: {c:5d} ({100*c/total_sec:5.1f}%) {bar}")

# Compare with AN dose distribution
print("\n--- Comparaison AN ---")
with open(AN_PATH) as f:
    an_data = json.load(f)

an_doses = Counter()
for entry in an_data['entries']:
    for tok in entry['tokens']:
        raw = tok.get('raw', '').lower().strip('.')
        if re.match(r'^[ivx]+$', raw):
            # Roman numeral
            val = 0
            for ch in raw:
                if ch == 'i': val += 1
                elif ch == 'v': val += 5
                elif ch == 'x': val += 10
            if 1 <= val <= 20:
                an_doses[val] += 1

# Also count "ana" separately
ana_count = 0
for entry in an_data['entries']:
    for tok in entry['tokens']:
        if tok.get('raw', '').lower() in ('ana', 'an.', 'ana.'):
            ana_count += 1

total_an = sum(an_doses.values())
print(f"\nAN doses (roman numerals, n={total_an}, + ana={ana_count}):")
for val in sorted(an_doses.keys()):
    c = an_doses[val]
    bar = "#" * int(c * 100 / max(total_an, 1))
    print(f"  {val:3d}: {c:5d} ({100*c/total_an:5.1f}%) {bar}")

# Ratio comparison
print(f"\n--- Ratio Comparison ---")
print(f"  VMS i=1 / i=2 = {icount_global.get(1,0)} / {icount_global.get(2,0)} = {icount_global.get(1,0)/max(icount_global.get(2,0),1):.2f}")
print(f"  AN  .i. / .ii. = {an_doses.get(1,0)} / {an_doses.get(2,0)} = {an_doses.get(1,0)/max(an_doses.get(2,0),1):.2f}")
print(f"  VMS i=2 / i=3 = {icount_global.get(2,0)} / {icount_global.get(3,0)} = {icount_global.get(2,0)/max(icount_global.get(3,0),1):.2f}")
print(f"  AN  .ii. / .iii. = {an_doses.get(2,0)} / {an_doses.get(3,0)} = {an_doses.get(2,0)/max(an_doses.get(3,0),1):.2f}")

# ========================================================================
# TEST 2: PREFIX x i-count
# ========================================================================
print("\n" + "=" * 70)
print("TEST 2: PREFIXE x i-count")
print("=" * 70)

prefix_icount = defaultdict(Counter)
for e in entries:
    prefix_icount[e['prefix']][e['i_count']] += 1

top_prefixes = sorted(prefix_icount.keys(), key=lambda p: -sum(prefix_icount[p].values()))

print(f"\n{'Prefix':12s} {'i=1':>6s} {'i=2':>6s} {'i=3':>6s} {'i=4':>6s} {'Total':>6s} {'ratio 2/1':>10s} {'mean_i':>7s}")
print("-" * 65)
for prefix in top_prefixes[:25]:
    ic = prefix_icount[prefix]
    total = sum(ic.values())
    i1 = ic.get(1, 0)
    i2 = ic.get(2, 0)
    i3 = ic.get(3, 0)
    i4 = ic.get(4, 0)
    ratio = i2 / max(i1, 1)
    mean_i = sum(k * v for k, v in ic.items()) / max(total, 1)
    if total >= 10:
        print(f"  {prefix:10s} {i1:6d} {i2:6d} {i3:6d} {i4:6d} {total:6d} {ratio:10.2f} {mean_i:7.2f}")

# ========================================================================
# TEST 2b: PREFIX x i-count PER SECTION (pharma vs herbal vs balnea)
# ========================================================================
print("\n" + "=" * 70)
print("TEST 2b: PREFIXE x i-count PAR SECTION")
print("=" * 70)

for prefix in ['d', 'qok', 'ok', 'ot', 's', 'qot', 'k', 'r']:
    prefix_entries = [e for e in entries if e['prefix'] == prefix]
    if len(prefix_entries) < 20:
        continue
    print(f"\n  Prefix '{prefix}' (n={len(prefix_entries)}):")
    for sec in ['pharma', 'herbal_a', 'balnea']:
        sec_entries = [e for e in prefix_entries if e['section'] == sec]
        if len(sec_entries) < 5:
            continue
        ic = Counter(e['i_count'] for e in sec_entries)
        total = sum(ic.values())
        i1 = ic.get(1, 0)
        i2 = ic.get(2, 0)
        i3 = ic.get(3, 0)
        ratio = i2 / max(i1, 1)
        mean_i = sum(k * v for k, v in ic.items()) / max(total, 1)
        print(f"    {sec:12s}: i=1:{i1:4d} i=2:{i2:4d} i=3:{i3:4d} ratio={ratio:.2f} mean={mean_i:.2f}")

# ========================================================================
# TEST 3: SAME PATTERN IN e-count ? (-ey/-eey/-eeey)
# ========================================================================
print("\n" + "=" * 70)
print("TEST 3: e-count DANS LES SUFFIXES -e*y")
print("=" * 70)

# Pattern: prefix + e{1,} + y
ey_pattern = re.compile(r'^(.+?)(e+)y$')

ey_entries = []
for entry in all_seq:
    w = entry['word']
    m = ey_pattern.match(w)
    if m and len(m.group(1)) >= 1:
        prefix = m.group(1)
        e_count = len(m.group(2))
        ey_entries.append({
            'word': w, 'prefix': prefix, 'e_count': e_count,
            'section': entry['section'], 'folio': entry['folio']
        })

print(f"\nTotal words matching *[e+]y: {len(ey_entries)}")

ecount_global = Counter(e['e_count'] for e in ey_entries)
total_ey = sum(ecount_global.values())
print(f"\nGlobal e-count distribution:")
for ec in sorted(ecount_global.keys()):
    c = ecount_global[ec]
    bar = "#" * int(c * 100 / total_ey)
    print(f"  e x {ec}: {c:5d} ({100*c/total_ey:5.1f}%) {bar}")

for sec in ['pharma', 'herbal_a', 'balnea']:
    sec_ey = [e for e in ey_entries if e['section'] == sec]
    if len(sec_ey) < 20:
        continue
    ec_sec = Counter(e['e_count'] for e in sec_ey)
    total_s = sum(ec_sec.values())
    e1 = ec_sec.get(1, 0)
    e2 = ec_sec.get(2, 0)
    e3 = ec_sec.get(3, 0)
    ratio = e2 / max(e1, 1)
    print(f"\n  {sec}: e=1:{e1} e=2:{e2} e=3:{e3} ratio e2/e1={ratio:.2f}")

# e-count by prefix
ey_prefix_ecount = defaultdict(Counter)
for e in ey_entries:
    ey_prefix_ecount[e['prefix']][e['e_count']] += 1

top_ey_prefixes = sorted(ey_prefix_ecount.keys(), key=lambda p: -sum(ey_prefix_ecount[p].values()))

print(f"\n{'Prefix':12s} {'e=1':>6s} {'e=2':>6s} {'e=3':>6s} {'e=4':>6s} {'Total':>6s} {'ratio 2/1':>10s}")
print("-" * 58)
for prefix in top_ey_prefixes[:20]:
    ec = ey_prefix_ecount[prefix]
    total = sum(ec.values())
    e1 = ec.get(1, 0)
    e2 = ec.get(2, 0)
    e3 = ec.get(3, 0)
    e4 = ec.get(4, 0)
    ratio = e2 / max(e1, 1)
    if total >= 10:
        print(f"  {prefix:10s} {e1:6d} {e2:6d} {e3:6d} {e4:6d} {total:6d} {ratio:10.2f}")

# ========================================================================
# TEST 4: ALSO CHECK -e*d*y pattern (edy, eedy, eedy)
# ========================================================================
print("\n" + "=" * 70)
print("TEST 4: e-count DANS -e*dy")
print("=" * 70)

edy_pattern = re.compile(r'^(.+?)(e+)dy$')

edy_entries = []
for entry in all_seq:
    w = entry['word']
    m = edy_pattern.match(w)
    if m and len(m.group(1)) >= 1:
        edy_entries.append({
            'word': w, 'prefix': m.group(1), 'e_count': len(m.group(2)),
            'section': entry['section'], 'folio': entry['folio']
        })

ecount_edy = Counter(e['e_count'] for e in edy_entries)
total_edy = sum(ecount_edy.values())
print(f"\nGlobal e-count in -e*dy (n={total_edy}):")
for ec in sorted(ecount_edy.keys()):
    c = ecount_edy[ec]
    bar = "#" * int(c * 100 / total_edy)
    print(f"  e x {ec}: {c:5d} ({100*c/total_edy:5.1f}%) {bar}")

for sec in ['pharma', 'herbal_a', 'balnea']:
    sec_edy = [e for e in edy_entries if e['section'] == sec]
    if len(sec_edy) < 20:
        continue
    ec_sec = Counter(e['e_count'] for e in sec_edy)
    total_s = sum(ec_sec.values())
    e1 = ec_sec.get(1, 0)
    e2 = ec_sec.get(2, 0)
    e3 = ec_sec.get(3, 0)
    ratio = e2 / max(e1, 1)
    print(f"  {sec}: e=1:{e1} e=2:{e2} e=3:{e3} ratio e2/e1={ratio:.2f}")

# ========================================================================
# TEST 5: FOLIO-LEVEL i-count distribution (pharma only)
# ========================================================================
print("\n" + "=" * 70)
print("TEST 5: i-count PAR FOLIO (pharma)")
print("=" * 70)

pharma_entries = [e for e in entries if e['section'] == 'pharma']
folio_icount = defaultdict(Counter)
for e in pharma_entries:
    folio_icount[e['folio']][e['i_count']] += 1

print(f"\n{'Folio':10s} {'i=1':>5s} {'i=2':>5s} {'i=3':>5s} {'Total':>6s} {'ratio':>7s} {'mean_i':>7s}")
print("-" * 50)
for folio in sorted(folio_icount.keys()):
    ic = folio_icount[folio]
    total = sum(ic.values())
    if total < 5:
        continue
    i1 = ic.get(1, 0)
    i2 = ic.get(2, 0)
    i3 = ic.get(3, 0)
    ratio = i2 / max(i1, 1)
    mean_i = sum(k * v for k, v in ic.items()) / max(total, 1)
    print(f"  {folio:8s} {i1:5d} {i2:5d} {i3:5d} {total:6d} {ratio:7.2f} {mean_i:7.2f}")

# ========================================================================
# TEST 6: CORRELATION BETWEEN i-count AND e-count ON SAME FOLIO
# ========================================================================
print("\n" + "=" * 70)
print("TEST 6: i-count MOYEN vs e-count MOYEN par folio (pharma)")
print("=" * 70)

# If both encode quantities, they should correlate (same recipes need same numbers)
folio_ecount = defaultdict(Counter)
for e in ey_entries:
    if e['section'] == 'pharma':
        folio_ecount[e['folio']][e['e_count']] += 1

print(f"\n{'Folio':10s} {'mean_i':>7s} {'mean_e':>7s} {'n_ain':>6s} {'n_ey':>5s}")
print("-" * 40)
i_means = []
e_means = []
for folio in sorted(set(list(folio_icount.keys()) + list(folio_ecount.keys()))):
    ic = folio_icount.get(folio, {})
    ec = folio_ecount.get(folio, {})
    n_i = sum(ic.values())
    n_e = sum(ec.values())
    if n_i < 5 or n_e < 5:
        continue
    mean_i = sum(k * v for k, v in ic.items()) / n_i
    mean_e = sum(k * v for k, v in ec.items()) / n_e
    i_means.append(mean_i)
    e_means.append(mean_e)
    print(f"  {folio:8s} {mean_i:7.2f} {mean_e:7.2f} {n_i:6d} {n_e:5d}")

# Pearson correlation
if len(i_means) >= 5:
    n = len(i_means)
    mean_i_avg = sum(i_means) / n
    mean_e_avg = sum(e_means) / n
    cov = sum((i_means[j] - mean_i_avg) * (e_means[j] - mean_e_avg) for j in range(n))
    var_i = sum((i_means[j] - mean_i_avg)**2 for j in range(n))
    var_e = sum((e_means[j] - mean_e_avg)**2 for j in range(n))
    if var_i > 0 and var_e > 0:
        r = cov / (math.sqrt(var_i) * math.sqrt(var_e))
        print(f"\n  Pearson correlation (mean_i vs mean_e): r = {r:.3f} (n={n})")
        print(f"  Si r > 0.3: les deux systemes covarient (memes recettes)")
        print(f"  Si r ~ 0: independants")
    else:
        print("\n  Variance nulle, pas de correlation calculable")

print("\n" + "=" * 70)
print("TESTS i-count TERMINES")
print("=" * 70)
