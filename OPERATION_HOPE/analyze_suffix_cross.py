#!/usr/bin/env python3
"""
OPERATION HOPE - Tests discriminants
1. Decomposition prefixe x suffixe x section
2. Co-occurrence : quel mot PRECEDE -ain vs -aiin ?
3. Test balnea "ana" : ratio 1:1 = quantites egales ?
"""

import re, json
from collections import Counter, defaultdict

IVTFF = "/sessions/laughing-jolly-bell/mnt/Voynich FINAL/OPERATION_HOPE/data/LSI_ivtff_0d.txt"

def get_section(folio):
    m = re.match(r'f(\d+)', folio)
    if not m:
        return 'other'
    num = int(m.group(1))
    if 1 <= num <= 56:
        return 'herbal_a'
    elif 57 <= num <= 66:
        return 'herbal_b'
    elif 67 <= num <= 73:
        return 'astro'
    elif 75 <= num <= 84:
        return 'balnea'
    elif 85 <= num <= 86:
        return 'bio'
    elif 87 <= num <= 102:
        return 'pharma_a'
    elif 103 <= num <= 116:
        return 'pharma_b'
    return 'other'

# Parse IVTFF into sequential word list with metadata
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
        linenum = m.group(2)
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
                'word': w, 'folio': folio, 'line': linenum,
                'section': section, 'pos': i, 'total': len(expanded)
            })

print(f"Total words parsed: {len(all_seq)}")

# ========================================================================
# 1. DECOMPOSITION PREFIXE x SUFFIXE x SECTION
# ========================================================================
print("\n" + "=" * 70)
print("1. PREFIXE x SUFFIXE x SECTION")
print("=" * 70)

# Extract prefix for each -ain/-aiin/-aiiin word
suffix_data = defaultdict(lambda: defaultdict(Counter))
# suffix_data[suffix][section][prefix] = count

for entry in all_seq:
    w = entry['word']
    sec = entry['section']
    # Merge pharma sections
    if sec.startswith('pharma'):
        sec = 'pharma'
    elif sec.startswith('herbal'):
        sec = 'herbal'

    for suf in ['aiiin', 'aiin', 'ain']:
        if w.endswith(suf) and len(w) > len(suf):
            prefix = w[:-len(suf)]
            suffix_data[suf][sec][prefix] += 1
            break

# For top prefixes, show distribution across sections for each suffix
top_prefixes = ['d', 'qok', 'ok', 'ot', 's', 'qot', 'k', 'r', 'olk', 'lk',
                'od', 'ol', 'ch', 'sh', 'l']

print(f"\n{'Prefix':8s} {'Suffix':7s} {'pharma':>8s} {'herbal':>8s} {'balnea':>8s} {'astro':>7s} {'P/(P+H)':>8s}")
print("-" * 60)

for prefix in top_prefixes:
    for suf in ['ain', 'aiin', 'aiiin']:
        p = suffix_data[suf].get('pharma', {}).get(prefix, 0)
        h = suffix_data[suf].get('herbal', {}).get(prefix, 0)
        b = suffix_data[suf].get('balnea', {}).get(prefix, 0)
        a = suffix_data[suf].get('astro', {}).get(prefix, 0)
        total = p + h + b + a
        if total < 5:
            continue
        ph_ratio = p / (p + h) if (p + h) > 0 else 0
        print(f"  {prefix:6s} -{suf:5s} {p:8d} {h:8d} {b:8d} {a:7d} {ph_ratio:8.2f}")
    # blank line between prefixes
    any_printed = any(
        sum(suffix_data[suf].get(s, {}).get(prefix, 0) for s in ['pharma','herbal','balnea','astro']) >= 5
        for suf in ['ain', 'aiin', 'aiiin']
    )
    if any_printed:
        print()

# KEY: For each prefix, compute ratio -aiin/-ain PER SECTION
print("\n" + "=" * 70)
print("RATIO -aiin:-ain PAR PREFIXE ET PAR SECTION")
print("=" * 70)

print(f"\n{'Prefix':8s} {'Pharma':>12s} {'Herbal':>12s} {'Balnea':>12s}")
print(f"{'':8s} {'ain:aiin':>12s} {'ain:aiin':>12s} {'ain:aiin':>12s}")
print("-" * 50)

for prefix in top_prefixes:
    vals = {}
    for sec in ['pharma', 'herbal', 'balnea']:
        ain_c = suffix_data['ain'].get(sec, {}).get(prefix, 0)
        aiin_c = suffix_data['aiin'].get(sec, {}).get(prefix, 0)
        if ain_c + aiin_c >= 10:
            ratio = aiin_c / max(ain_c, 1)
            vals[sec] = f"{ain_c}:{aiin_c} ({ratio:.1f})"
        else:
            vals[sec] = "-"
    if any(v != "-" for v in vals.values()):
        print(f"  {prefix:6s} {vals.get('pharma','-'):>12s} {vals.get('herbal','-'):>12s} {vals.get('balnea','-'):>12s}")

# ========================================================================
# 2. CO-OCCURRENCE : Mot PRECEDENT different pour -ain vs -aiin ?
# ========================================================================
print("\n" + "=" * 70)
print("2. CO-OCCURRENCE : Mot precedent pour -ain vs -aiin en PHARMA")
print("=" * 70)

# For pharma: what long word (>= 5 chars) precedes -ain vs -aiin?
prev_for_ain = Counter()
prev_for_aiin = Counter()

for idx, entry in enumerate(all_seq):
    w = entry['word']
    sec = entry['section']
    if not sec.startswith('pharma'):
        continue

    if idx == 0:
        continue
    prev_entry = all_seq[idx - 1]
    prev_w = prev_entry['word']
    # Only consider if prev word is "long" (potential ingredient)
    if len(prev_w) < 5:
        continue
    # Must be same folio
    if prev_entry['folio'] != entry['folio']:
        continue

    for suf in ['aiiin', 'aiin', 'ain']:
        if w.endswith(suf) and len(w) > len(suf):
            if suf == 'ain':
                prev_for_ain[prev_w] += 1
            elif suf == 'aiin':
                prev_for_aiin[prev_w] += 1
            break

# Are the preceding words DIFFERENT for -ain vs -aiin?
print("\nTop 20 mots longs AVANT -ain (pharma):")
for w, c in prev_for_ain.most_common(20):
    also_before_aiin = prev_for_aiin.get(w, 0)
    exclusivity = c / (c + also_before_aiin) if (c + also_before_aiin) > 0 else 0
    marker = " *** EXCLUSIVE" if exclusivity > 0.75 and c >= 3 else ""
    print(f"  {w:20s} {c:4d}x avant -ain, {also_before_aiin:4d}x avant -aiin  (exc={exclusivity:.2f}){marker}")

print("\nTop 20 mots longs AVANT -aiin (pharma):")
for w, c in prev_for_aiin.most_common(20):
    also_before_ain = prev_for_ain.get(w, 0)
    exclusivity = c / (c + also_before_ain) if (c + also_before_ain) > 0 else 0
    marker = " *** EXCLUSIVE" if exclusivity > 0.75 and c >= 3 else ""
    print(f"  {w:20s} {c:4d}x avant -aiin, {also_before_ain:4d}x avant -ain  (exc={exclusivity:.2f}){marker}")

# Overlap analysis
ain_set = set(w for w, c in prev_for_ain.items() if c >= 2)
aiin_set = set(w for w, c in prev_for_aiin.items() if c >= 2)
both = ain_set & aiin_set
only_ain = ain_set - aiin_set
only_aiin = aiin_set - ain_set

print(f"\nOverlap (mots precedents avec >=2 occurrences):")
print(f"  Exclusifs a -ain:  {len(only_ain)}")
print(f"  Exclusifs a -aiin: {len(only_aiin)}")
print(f"  Communs:           {len(both)}")
print(f"  Jaccard similarity: {len(both) / max(len(both | ain_set | aiin_set), 1):.2f}")

# ========================================================================
# 3. TEST BALNEA : -ain/-aiin distribution par folio
# ========================================================================
print("\n" + "=" * 70)
print("3. BALNEA : Distribution -ain/-aiin par folio")
print("=" * 70)

balnea_folios = defaultdict(lambda: {'ain': 0, 'aiin': 0, 'aiiin': 0, 'total_words': 0})

for entry in all_seq:
    if entry['section'] != 'balnea':
        continue
    folio = entry['folio']
    balnea_folios[folio]['total_words'] += 1

    w = entry['word']
    for suf in ['aiiin', 'aiin', 'ain']:
        if w.endswith(suf) and len(w) > len(suf):
            balnea_folios[folio][suf] += 1
            break

print(f"\n{'Folio':10s} {'Words':>6s} {'-ain':>5s} {'-aiin':>6s} {'-aiiin':>7s} {'ratio':>8s}")
print("-" * 50)
for folio in sorted(balnea_folios.keys()):
    d = balnea_folios[folio]
    ain = d['ain']
    aiin = d['aiin']
    aiiin = d['aiiin']
    total = d['total_words']
    ratio = aiin / max(ain, 1) if ain + aiin > 0 else 0
    if total > 10:
        print(f"  {folio:8s} {total:6d} {ain:5d} {aiin:6d} {aiiin:7d} {ratio:8.1f}")

# ========================================================================
# 4. SUFFIX -eey vs -edy vs -ain : TRIPLE COMPARISON par section
# ========================================================================
print("\n" + "=" * 70)
print("4. TRIPLE SUFFIXE : -eey / -edy / -ain par section")
print("=" * 70)

# These are the 3 pharma-specific suffixes. Do they co-occur or alternate?
triple = defaultdict(lambda: Counter())  # section -> {suffix: count}

for entry in all_seq:
    w = entry['word']
    sec = entry['section']
    if sec.startswith('pharma'):
        sec = 'pharma'
    elif sec.startswith('herbal'):
        sec = 'herbal'

    for suf in ['eey', 'edy', 'ain']:
        if w.endswith(suf) and len(w) > len(suf):
            triple[sec][suf] += 1
            break  # only count once per word

print(f"\n{'Section':10s} {'-eey':>6s} {'-edy':>6s} {'-ain':>6s} {'eey/edy':>8s} {'eey/ain':>8s}")
print("-" * 55)
for sec in ['pharma', 'herbal', 'balnea', 'astro', 'bio']:
    eey = triple[sec].get('eey', 0)
    edy = triple[sec].get('edy', 0)
    ain = triple[sec].get('ain', 0)
    if eey + edy + ain < 10:
        continue
    r1 = eey / max(edy, 1)
    r2 = eey / max(ain, 1)
    print(f"  {sec:8s} {eey:6d} {edy:6d} {ain:6d} {r1:8.2f} {r2:8.2f}")

# ========================================================================
# 5. POSITION IN LINE : -ain vs -aiin vs -eey vs -edy
# ========================================================================
print("\n" + "=" * 70)
print("5. POSITION DANS LA LIGNE (pharma only) : ou tombent les suffixes ?")
print("=" * 70)

pos_data = defaultdict(lambda: Counter())  # suffix -> {position_bucket: count}

for entry in all_seq:
    sec = entry['section']
    if not sec.startswith('pharma'):
        continue
    w = entry['word']
    pos = entry['pos']
    total = entry['total']
    if total == 0:
        continue

    # Normalize position to 0-1
    norm_pos = pos / max(total - 1, 1)

    for suf in ['aiiin', 'aiin', 'ain', 'eey', 'edy', 'eol']:
        if w.endswith(suf) and len(w) > len(suf):
            # Bucket into quintiles
            if norm_pos < 0.2:
                bucket = "0-20%"
            elif norm_pos < 0.4:
                bucket = "20-40%"
            elif norm_pos < 0.6:
                bucket = "40-60%"
            elif norm_pos < 0.8:
                bucket = "60-80%"
            else:
                bucket = "80-100%"
            pos_data[suf][bucket] += 1
            break

print(f"\n{'Suffix':8s} {'0-20%':>7s} {'20-40%':>7s} {'40-60%':>7s} {'60-80%':>7s} {'80-100%':>8s} {'Total':>6s}")
print("-" * 55)
buckets = ["0-20%", "20-40%", "40-60%", "60-80%", "80-100%"]
for suf in ['ain', 'aiin', 'eey', 'edy', 'eol']:
    vals = [pos_data[suf].get(b, 0) for b in buckets]
    total = sum(vals)
    if total < 10:
        continue
    print(f"  -{suf:6s} {vals[0]:7d} {vals[1]:7d} {vals[2]:7d} {vals[3]:7d} {vals[4]:8d} {total:6d}")

# Normalize to percentages
print(f"\n{'Suffix':8s} {'0-20%':>7s} {'20-40%':>7s} {'40-60%':>7s} {'60-80%':>7s} {'80-100%':>8s}")
print("-" * 48)
for suf in ['ain', 'aiin', 'eey', 'edy', 'eol']:
    vals = [pos_data[suf].get(b, 0) for b in buckets]
    total = sum(vals)
    if total < 10:
        continue
    pcts = [100 * v / total for v in vals]
    print(f"  -{suf:6s} {pcts[0]:6.1f}% {pcts[1]:6.1f}% {pcts[2]:6.1f}% {pcts[3]:6.1f}% {pcts[4]:7.1f}%")

# ========================================================================
# 6. BIGRAM PATTERNS : -ain followed by X vs -aiin followed by X
# ========================================================================
print("\n" + "=" * 70)
print("6. QUE SUIT -ain vs -aiin en pharma ?")
print("=" * 70)

next_after_ain = Counter()
next_after_aiin = Counter()

for idx, entry in enumerate(all_seq):
    w = entry['word']
    sec = entry['section']
    if not sec.startswith('pharma'):
        continue
    if idx >= len(all_seq) - 1:
        continue
    next_entry = all_seq[idx + 1]
    if next_entry['folio'] != entry['folio']:
        continue
    next_w = next_entry['word']

    for suf in ['aiiin', 'aiin', 'ain']:
        if w.endswith(suf) and len(w) > len(suf):
            if suf == 'ain':
                next_after_ain[next_w] += 1
            elif suf == 'aiin':
                next_after_aiin[next_w] += 1
            break

print("\nApres -ain (pharma):")
for w, c in next_after_ain.most_common(15):
    print(f"  {w:20s} {c:4d}")

print("\nApres -aiin (pharma):")
for w, c in next_after_aiin.most_common(15):
    print(f"  {w:20s} {c:4d}")

# Chi-squared-like comparison: are the distributions different?
# Get union of top words
top_next = set(w for w, _ in next_after_ain.most_common(30)) | set(w for w, _ in next_after_aiin.most_common(30))
total_ain = sum(next_after_ain.values())
total_aiin = sum(next_after_aiin.values())

print(f"\nComparaison distributionnelle (top mots suivants):")
print(f"{'Word':18s} {'after -ain':>11s} {'after -aiin':>12s} {'diff':>8s}")
print("-" * 55)
for w in sorted(top_next, key=lambda x: -(next_after_ain.get(x, 0) + next_after_aiin.get(x, 0))):
    a1 = next_after_ain.get(w, 0)
    a2 = next_after_aiin.get(w, 0)
    p1 = 100 * a1 / max(total_ain, 1)
    p2 = 100 * a2 / max(total_aiin, 1)
    diff = abs(p1 - p2)
    if a1 + a2 >= 5:
        marker = " ***" if diff > 2.0 else ""
        print(f"  {w:16s} {a1:4d} ({p1:4.1f}%) {a2:4d} ({p2:4.1f}%) {diff:6.1f}%{marker}")

print("\n" + "=" * 70)
print("ANALYSE CROISEE TERMINEE")
print("=" * 70)
