#!/usr/bin/env python3
"""
Parse VMS IVTFF transcription, extract H (composite/best) transcription,
segment by VMS section, compute word frequencies.
Save everything to OPERATION_HOPE/data/ and OPERATION_HOPE/results/
"""

import re, json, os
from collections import Counter, defaultdict

IVTFF = "/sessions/laughing-jolly-bell/mnt/Voynich FINAL/OPERATION_HOPE/data/LSI_ivtff_0d.txt"
DATADIR = "/sessions/laughing-jolly-bell/mnt/Voynich FINAL/OPERATION_HOPE/data"
RESDIR = "/sessions/laughing-jolly-bell/mnt/Voynich FINAL/OPERATION_HOPE/results"

# ========================================================================
# Section classification
# ========================================================================
def get_section(folio):
    m = re.match(r'f(\d+)', folio)
    if not m:
        return 'other'
    num = int(m.group(1))
    if 1 <= num <= 56:
        return 'herbal_a'  # Herbal A (quires 1-8)
    elif 57 <= num <= 66:
        return 'herbal_b'  # Herbal B (quires 9-11)
    elif 67 <= num <= 73:
        return 'astro'     # Astronomical/astrological
    elif 75 <= num <= 84:
        return 'balnea'    # Bathing/biological
    elif 85 <= num <= 86:
        return 'bio'       # Biological (rosettes)
    elif 87 <= num <= 102:
        return 'pharma_a'  # Pharmaceutical A (text-heavy)
    elif 103 <= num <= 116:
        return 'pharma_b'  # Pharmaceutical B (stars pages)
    return 'other'

# ========================================================================
# Parse IVTFF - extract H transcription (or best available)
# ========================================================================
print("=" * 60)
print("PARSING VMS IVTFF TRANSCRIPTION")
print("=" * 60)

lines_by_locus = defaultdict(dict)  # locus -> {transcriber: text}
folio_order = []
seen_loci = set()

with open(IVTFF, encoding='latin-1') as f:
    for line in f:
        line = line.rstrip('\n')
        if not line or line.startswith('#'):
            continue

        # Match: <f1r.1,@P0;H>  text
        # Or: <f1r.1,+P0;H>  text
        # Or: <f1r.1,=Pt;H>  text
        # Or: <f1r>  (folio header)
        m = re.match(r'<(f\d+\w?\d?)\.(\d+),[^;]*;(\w)>\s*(.*)', line)
        if m:
            folio = m.group(1)
            line_num = m.group(2)
            transcriber = m.group(3)
            text = m.group(4).strip()

            locus = f"{folio}.{line_num}"
            if locus not in seen_loci:
                seen_loci.add(locus)
                folio_order.append((folio, locus))

            lines_by_locus[locus][transcriber] = text

# Choose best transcription per locus (prefer H > T > C > N > F > any)
priority = ['H', 'T', 'C', 'N', 'F', 'U', 'X', 'V', 'D', 'L', 'B']
best_lines = []
for folio, locus in folio_order:
    versions = lines_by_locus[locus]
    text = None
    for p in priority:
        if p in versions:
            text = versions[p]
            break
    if text is None and versions:
        text = list(versions.values())[0]
    if text:
        best_lines.append((folio, locus, text))

print(f"Total loci parsed: {len(best_lines)}")

# ========================================================================
# Clean EVA text and extract words
# ========================================================================
def clean_eva(text):
    """Clean EVA text: remove markup, keep word separators."""
    # Remove inline comments {...}
    text = re.sub(r'\{[^}]*\}', '', text)
    # Remove uncertain/alternate markers
    text = re.sub(r'<[^>]*>', '', text)
    # Remove special chars but keep dots (word sep) and letters
    text = re.sub(r'[!\?\*]', '', text)  # unknown/uncertain chars
    text = re.sub(r"['\"]", '', text)
    # Normalize spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Segment by section
section_data = defaultdict(list)  # section -> [(folio, locus, words)]
section_text = defaultdict(list)
all_words = []

for folio, locus, raw_text in best_lines:
    section = get_section(folio)
    cleaned = clean_eva(raw_text)

    # Split on dots (EVA word separator)
    words = [w.strip() for w in cleaned.split('.') if w.strip() and len(w.strip()) > 0]
    # Also split on spaces (some lines use spaces)
    expanded = []
    for w in words:
        parts = w.split()
        expanded.extend([p for p in parts if p])
    words = expanded

    # Remove pure markup artifacts
    words = [w for w in words if re.match(r'^[a-zA-Z]+$', w)]

    if words:
        section_data[section].append((folio, locus, words))
        section_text[section].extend(words)
        all_words.extend(words)

# ========================================================================
# Report
# ========================================================================
print("\nSECTION BREAKDOWN:")
print(f"{'Section':12s} {'Lines':>6s} {'Words':>7s} {'Unique':>7s}")
print("-" * 40)
total_lines = 0
total_words = 0
for section in ['herbal_a', 'herbal_b', 'astro', 'balnea', 'bio', 'pharma_a', 'pharma_b', 'other']:
    words = section_text.get(section, [])
    lines = len(section_data.get(section, []))
    unique = len(set(words))
    print(f"  {section:12s} {lines:6d} {len(words):7d} {unique:7d}")
    total_lines += lines
    total_words += len(words)

print(f"  {'TOTAL':12s} {total_lines:6d} {total_words:7d} {len(set(all_words)):7d}")

# ========================================================================
# Save word lists and frequencies
# ========================================================================

# Combine pharma sections
pharma_words = section_text.get('pharma_a', []) + section_text.get('pharma_b', [])
herbal_words = section_text.get('herbal_a', []) + section_text.get('herbal_b', [])

freq_all = Counter(all_words)
freq_pharma = Counter(pharma_words)
freq_herbal = Counter(herbal_words)
freq_astro = Counter(section_text.get('astro', []))
freq_balnea = Counter(section_text.get('balnea', []))

# Save frequencies
for name, freq in [('all', freq_all), ('pharma', freq_pharma),
                    ('herbal', freq_herbal), ('astro', freq_astro),
                    ('balnea', freq_balnea)]:
    with open(f"{RESDIR}/freq_{name}.json", 'w') as f:
        json.dump(dict(freq.most_common()), f, indent=2)

# Save raw word lists
for name, words in [('all', all_words), ('pharma', pharma_words),
                     ('herbal', herbal_words)]:
    with open(f"{DATADIR}/vms_{name}_words.json", 'w') as f:
        json.dump(words, f)

# ========================================================================
# Top words per section
# ========================================================================
print("\n" + "=" * 60)
print("TOP 30 WORDS - ALL SECTIONS")
print("=" * 60)
for w, c in freq_all.most_common(30):
    # Show per-section breakdown
    p = freq_pharma.get(w, 0)
    h = freq_herbal.get(w, 0)
    a = freq_astro.get(w, 0)
    b = freq_balnea.get(w, 0)
    ratio_p = p / max(c, 1) * 100
    print(f"  {w:18s} {c:5d}  pharma={p:4d}({ratio_p:4.0f}%)  herbal={h:4d}  astro={a:4d}  balnea={b:4d}")

print("\n" + "=" * 60)
print("TOP 30 WORDS - PHARMA ONLY")
print("=" * 60)
for w, c in freq_pharma.most_common(30):
    h = freq_herbal.get(w, 0)
    # Pharma/herbal ratio
    if h > 0:
        ratio = c / h
    else:
        ratio = float('inf')
    marker = " ***" if ratio > 3 else " **" if ratio > 2 else ""
    print(f"  {w:18s} {c:5d}  (herbal={h:4d}, ratio={ratio:5.1f}){marker}")

# ========================================================================
# EVA character analysis
# ========================================================================
print("\n" + "=" * 60)
print("EVA CHARACTER FREQUENCIES")
print("=" * 60)

char_all = Counter()
char_pharma = Counter()
char_herbal = Counter()

for w in all_words:
    for c in w:
        char_all[c] += 1
for w in pharma_words:
    for c in w:
        char_pharma[c] += 1
for w in herbal_words:
    for c in w:
        char_herbal[c] += 1

print(f"{'Char':6s} {'All':>6s} {'Pharma':>7s} {'Herbal':>7s} {'P/H ratio':>10s}")
for c, n in char_all.most_common():
    p = char_pharma.get(c, 0)
    h = char_herbal.get(c, 0)
    ratio = p / h if h > 0 else 0
    print(f"  {c:4s} {n:6d} {p:7d} {h:7d} {ratio:10.2f}")

# ========================================================================
# Gallows analysis (H1)
# ========================================================================
print("\n" + "=" * 60)
print("H1: GALLOWS CHARACTER ANALYSIS")
print("=" * 60)

# EVA gallows: t, k, p, f (single gallows)
# EVA bench gallows: cth, ckh, cph, cfh
gallows_single = {'t', 'k', 'p', 'f'}
gallows_bench_patterns = ['cth', 'ckh', 'cph', 'cfh']

def count_gallows(words):
    """Count gallows characters in word list."""
    single = Counter()
    bench = Counter()
    total_chars = 0
    gallows_words = []

    for w in words:
        total_chars += len(w)
        has_gallows = False

        # Count bench gallows first (they contain single gallows chars)
        for bg in gallows_bench_patterns:
            count = w.count(bg)
            if count:
                bench[bg] += count
                has_gallows = True

        # Count single gallows (exclude those in bench patterns)
        w_no_bench = w
        for bg in gallows_bench_patterns:
            w_no_bench = w_no_bench.replace(bg, '___')

        for g in gallows_single:
            count = w_no_bench.count(g)
            if count:
                single[g] += count
                has_gallows = True

        if has_gallows:
            gallows_words.append(w)

    return single, bench, total_chars, gallows_words

for name, words in [('ALL', all_words), ('PHARMA', pharma_words),
                     ('HERBAL', herbal_words), ('ASTRO', section_text.get('astro', [])),
                     ('BALNEA', section_text.get('balnea', []))]:
    single, bench, total_chars, gw = count_gallows(words)
    total_g = sum(single.values()) + sum(bench.values())
    pct = 100 * total_g / total_chars if total_chars else 0

    print(f"\n  {name}: {len(words)} words, {total_chars} chars")
    print(f"    Single gallows: {dict(single)} = {sum(single.values())}")
    print(f"    Bench gallows:  {dict(bench)} = {sum(bench.values())}")
    print(f"    Total gallows:  {total_g} ({pct:.1f}% of chars)")
    print(f"    Words with gallows: {len(gw)} ({100*len(gw)/max(len(words),1):.1f}% of words)")

# ========================================================================
# Word length distribution (potential number encoding)
# ========================================================================
print("\n" + "=" * 60)
print("WORD LENGTH DISTRIBUTION")
print("=" * 60)

for name, words in [('ALL', all_words), ('PHARMA', pharma_words), ('HERBAL', herbal_words)]:
    lengths = Counter(len(w) for w in words)
    print(f"\n  {name}:")
    for l in sorted(lengths.keys()):
        bar = '#' * (lengths[l] // 50)
        print(f"    len={l:2d}: {lengths[l]:5d} {bar}")

print("\nDone. Results saved to OPERATION_HOPE/results/")
