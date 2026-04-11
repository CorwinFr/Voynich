#!/usr/bin/env python3
"""
OPERATION HOPE - Deep hypothesis testing
H2: Repeated sequences (tally system)
H3: Short words as number candidates (section distribution)
H8: Bench gallows as operators
H9: Search for "ana" equivalent
H10: Structural comparison VMS pharma vs AN
"""

import json, re, os
from collections import Counter, defaultdict

DATADIR = "/sessions/laughing-jolly-bell/mnt/Voynich FINAL/OPERATION_HOPE/data"
RESDIR = "/sessions/laughing-jolly-bell/mnt/Voynich FINAL/OPERATION_HOPE/results"
IVTFF = f"{DATADIR}/LSI_ivtff_0d.txt"
AN_PATH = "/sessions/laughing-jolly-bell/mnt/Voynich FINAL/RECIPE_DATASET/S01_AN.json"

# Load pre-computed frequencies
with open(f"{RESDIR}/freq_all.json") as f:
    freq_all = json.load(f)
with open(f"{RESDIR}/freq_pharma.json") as f:
    freq_pharma = json.load(f)
with open(f"{RESDIR}/freq_herbal.json") as f:
    freq_herbal = json.load(f)
with open(f"{RESDIR}/freq_astro.json") as f:
    freq_astro = json.load(f)
with open(f"{RESDIR}/freq_balnea.json") as f:
    freq_balnea = json.load(f)

# ========================================================================
# H2: REPEATED CHARACTER SEQUENCES (tally/unary encoding)
# ========================================================================
print("=" * 70)
print("H2: REPEATED CHARACTER SEQUENCES")
print("=" * 70)

# Look for repeated chars within words: ii, iii, iiii, ee, eee, oo, ooo
def find_repeats(words):
    """Find repeated character sequences in words."""
    repeat_counts = defaultdict(Counter)  # char -> {repeat_len: count}
    repeat_words = defaultdict(list)  # pattern -> [word examples]

    for w in words:
        # Find runs of same character
        for m in re.finditer(r'(.)\1+', w):
            char = m.group(1)
            length = len(m.group(0))
            repeat_counts[char][length] += 1
            if len(repeat_words[f"{char}x{length}"]) < 5:
                repeat_words[f"{char}x{length}"].append(w)

    return repeat_counts, repeat_words

# Load word lists
with open(f"{DATADIR}/vms_all_words.json") as f:
    all_words = json.load(f)
with open(f"{DATADIR}/vms_pharma_words.json") as f:
    pharma_words = json.load(f)
with open(f"{DATADIR}/vms_herbal_words.json") as f:
    herbal_words = json.load(f)

print("\n--- All sections ---")
rc_all, rw_all = find_repeats(all_words)
for char in sorted(rc_all.keys()):
    if sum(rc_all[char].values()) > 20:
        lens = sorted(rc_all[char].items())
        detail = ", ".join(f"{char}x{l}={c}" for l, c in lens)
        print(f"  '{char}' repeats: {detail}")
        for l, c in lens:
            key = f"{char}x{l}"
            if rw_all[key]:
                print(f"       examples {key}: {rw_all[key][:5]}")

print("\n--- Pharma vs Herbal comparison ---")
rc_pharma, rw_pharma = find_repeats(pharma_words)
rc_herbal, rw_herbal = find_repeats(herbal_words)

print(f"{'Pattern':12s} {'Pharma':>7s} {'Herbal':>7s} {'P/H ratio':>10s} {'P/total':>8s}")
for char in ['i', 'e', 'o', 'a']:
    for length in range(2, 5):
        pc = rc_pharma.get(char, {}).get(length, 0)
        hc = rc_herbal.get(char, {}).get(length, 0)
        tc = rc_all.get(char, {}).get(length, 0)
        ratio = pc / hc if hc > 0 else float('inf')
        p_tot = pc / tc * 100 if tc > 0 else 0
        if tc > 5:
            print(f"  {char}x{length:d}      {pc:7d} {hc:7d} {ratio:10.2f} {p_tot:7.1f}%")

# ========================================================================
# H3: SHORT WORDS AS NUMBER CANDIDATES
# ========================================================================
print("\n" + "=" * 70)
print("H3: SHORT WORDS (len 1-3) - SECTION DISTRIBUTION")
print("=" * 70)

# For each short word, compute pharma concentration
short_words = [(w, int(freq_all[w])) for w in freq_all if len(w) <= 3 and int(freq_all[w]) >= 20]
short_words.sort(key=lambda x: -x[1])

print(f"\n{'Word':8s} {'All':>5s} {'Pharma':>7s} {'Herbal':>7s} {'Astro':>6s} {'Balnea':>7s} {'P%':>5s} {'P/H':>6s} {'Signal':>8s}")
print("-" * 70)

pharma_concentrated = []
for w, total in short_words[:50]:
    p = int(freq_pharma.get(w, 0))
    h = int(freq_herbal.get(w, 0))
    a = int(freq_astro.get(w, 0))
    b = int(freq_balnea.get(w, 0))
    pct = 100 * p / total if total else 0
    ratio = p / h if h > 0 else float('inf')

    # Signal: pharma-concentrated if P% > 40% or P/H > 3
    signal = ""
    if pct > 50:
        signal = "PHARMA++"
    elif pct > 40:
        signal = "PHARMA+"
    elif ratio > 3:
        signal = "RATIO++"

    print(f"  {w:6s} {total:5d} {p:7d} {h:7d} {a:6d} {b:7d} {pct:5.1f} {ratio:6.1f} {signal}")

    if signal:
        pharma_concentrated.append((w, total, p, pct, ratio))

print(f"\nPharma-concentrated short words (P% > 40% or P/H > 3):")
for w, total, p, pct, ratio in pharma_concentrated:
    print(f"  {w}: {total}x total, {p}x pharma ({pct:.0f}%), P/H={ratio:.1f}")

# ========================================================================
# H8: BENCH GALLOWS MAPPING
# ========================================================================
print("\n" + "=" * 70)
print("H8: BENCH GALLOWS - DETAILED POSITION ANALYSIS")
print("=" * 70)

bench_patterns = ['cth', 'ckh', 'cph', 'cfh']

def analyze_bench_positions(words, label):
    """Analyze where bench gallows appear in words."""
    positions = defaultdict(lambda: Counter())  # bg -> {position: count}
    contexts = defaultdict(list)  # bg -> [(word, pos_in_word)]
    word_lengths_with_bg = defaultdict(list)

    for w in words:
        for bg in bench_patterns:
            idx = w.find(bg)
            while idx >= 0:
                # Position categories
                if idx == 0:
                    pos = "start"
                elif idx + len(bg) == len(w):
                    pos = "end"
                else:
                    pos = "middle"
                positions[bg][pos] += 1
                word_lengths_with_bg[bg].append(len(w))
                if len(contexts[bg]) < 8:
                    contexts[bg].append(w)
                idx = w.find(bg, idx + 1)

    print(f"\n  {label}:")
    for bg in bench_patterns:
        total = sum(positions[bg].values())
        if total > 0:
            avg_len = sum(word_lengths_with_bg[bg]) / len(word_lengths_with_bg[bg])
            print(f"    {bg}: {total}x  start={positions[bg]['start']}  mid={positions[bg]['middle']}  end={positions[bg]['end']}  avg_wordlen={avg_len:.1f}")
            print(f"         examples: {contexts[bg][:8]}")

analyze_bench_positions(all_words, "ALL")
analyze_bench_positions(pharma_words, "PHARMA")
analyze_bench_positions(herbal_words, "HERBAL")

# Bench gallows as fraction of all gallows
print("\n  Bench gallows as % of all gallows:")
for label, words in [("ALL", all_words), ("PHARMA", pharma_words), ("HERBAL", herbal_words)]:
    single_count = 0
    bench_count = 0
    for w in words:
        for bg in bench_patterns:
            bench_count += w.count(bg)
        w_clean = w
        for bg in bench_patterns:
            w_clean = w_clean.replace(bg, '___')
        for g in ['t', 'k', 'p', 'f']:
            single_count += w_clean.count(g)
    total = single_count + bench_count
    if total:
        print(f"    {label}: bench={bench_count} ({100*bench_count/total:.1f}%), single={single_count} ({100*single_count/total:.1f}%)")

# ========================================================================
# H9: SEARCH FOR "ANA" EQUIVALENT
# ========================================================================
print("\n" + "=" * 70)
print("H9: SEARCHING FOR 'ANA' EQUIVALENT IN VMS")
print("=" * 70)

# In AN, "ana" = 340/16192 = 2.1% of all tokens
# In pharma, ana = ~340/5741-ref or about 6% of dose/unit tokens
# We need a VMS word that:
# 1. Is very frequent in pharma
# 2. Appears at consistent positions (after ingredient lists, before units)
# 3. Is relatively short (3-4 EVA chars like "ana" is 3 Latin chars)

print("\n1. Frequency test: Words with pharma concentration similar to 'ana'")
print("   'ana' in AN: 340/16192 = 2.1% of all tokens")
print("   Target: a VMS word at ~2-5% of pharma tokens (14480 total)")
print(f"   That means ~290-720 occurrences in pharma\n")

total_pharma = sum(int(v) for v in freq_pharma.values())
candidates = []
for w in freq_pharma:
    count = int(freq_pharma[w])
    h = int(freq_herbal.get(w, 0))
    pct = 100 * count / total_pharma
    ratio = count / h if h > 0 else float('inf')

    # "ana" characteristics: short, frequent, dose-related
    # Pharma concentration > 40%, short word (2-6 chars)
    if 2 <= len(w) <= 6 and count >= 30 and pct >= 0.5:
        candidates.append((w, count, pct, h, ratio))

candidates.sort(key=lambda x: -x[2])  # sort by pharma %
print(f"{'Word':12s} {'P_count':>8s} {'P%':>6s} {'H_count':>8s} {'P/H':>6s} {'Len':>4s}")
print("-" * 50)
for w, c, pct, h, ratio in candidates[:30]:
    marker = ""
    if ratio > 5 and pct > 1.0:
        marker = " *** ANA CANDIDATE"
    elif ratio > 3 and pct > 0.8:
        marker = " ** possible"
    print(f"  {w:10s} {c:8d} {pct:6.2f} {h:8d} {ratio:6.1f} {len(w):4d}{marker}")

# ========================================================================
# H10: STRUCTURAL COMPARISON VMS PHARMA VS AN
# ========================================================================
print("\n" + "=" * 70)
print("H10: STRUCTURAL COMPARISON VMS PHARMA vs AN")
print("=" * 70)

# Re-parse IVTFF to get paragraph-level data for pharma
def get_section(folio):
    m = re.match(r'f(\d+)', folio)
    if not m:
        return 'other'
    num = int(m.group(1))
    if 87 <= num <= 116:
        return 'pharma'
    return 'other'

# Parse pharma lines grouped by folio
pharma_folios = defaultdict(list)  # folio -> [words per line]
with open(IVTFF, encoding='latin-1') as f:
    for line in f:
        line = line.rstrip('\n')
        if not line or line.startswith('#'):
            continue
        m = re.match(r'<(f\d+\w?\d?)\.(\d+),[^;]*;H>\s*(.*)', line)
        if not m:
            continue
        folio = m.group(1)
        if get_section(folio) != 'pharma':
            continue
        text = m.group(3).strip()
        # Clean
        text = re.sub(r'\{[^}]*\}', '', text)
        text = re.sub(r'<[^>]*>', '', text)
        text = re.sub(r'[!\?\*\'"]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        words = [w.strip() for w in text.split('.') if w.strip()]
        expanded = []
        for w in words:
            parts = w.split()
            expanded.extend([p for p in parts if p and re.match(r'^[a-zA-Z]+$', p)])
        if expanded:
            pharma_folios[folio].append(expanded)

# Paragraph = all lines on one folio side
print("\n1. Tokens per 'paragraph' (folio side) in VMS Pharma:")
folio_tokens = []
for folio in sorted(pharma_folios.keys()):
    total = sum(len(line) for line in pharma_folios[folio])
    folio_tokens.append((folio, total, len(pharma_folios[folio])))

# Distribution
token_counts = [t for _, t, _ in folio_tokens]
print(f"   Folios: {len(folio_tokens)}")
print(f"   Tokens/folio: min={min(token_counts)}, max={max(token_counts)}, "
      f"mean={sum(token_counts)/len(token_counts):.1f}, "
      f"median={sorted(token_counts)[len(token_counts)//2]}")

# Compare with AN
print("\n2. Tokens per recipe in Antidotarium Nicolai:")
with open(AN_PATH) as f:
    an_data = json.load(f)

an_recipe_tokens = []
for entry in an_data['entries']:
    an_recipe_tokens.append(len(entry['tokens']))

print(f"   Recipes: {len(an_recipe_tokens)}")
print(f"   Tokens/recipe: min={min(an_recipe_tokens)}, max={max(an_recipe_tokens)}, "
      f"mean={sum(an_recipe_tokens)/len(an_recipe_tokens):.1f}, "
      f"median={sorted(an_recipe_tokens)[len(an_recipe_tokens)//2]}")

# Distribution histogram
print("\n3. Token count distribution comparison:")
print(f"   {'Range':>12s} {'VMS folio':>10s} {'AN recipe':>10s}")
for lo, hi in [(1,10), (11,20), (21,30), (31,50), (51,80), (81,120), (121,200), (201,500), (501,1000)]:
    v = sum(1 for t in token_counts if lo <= t <= hi)
    a = sum(1 for t in an_recipe_tokens if lo <= t <= hi)
    print(f"   {lo:3d}-{hi:3d}    {v:10d} {a:10d}")

# ========================================================================
# H3b: WORD PAIRS AND TRIGRAMS IN PHARMA (dose patterns)
# ========================================================================
print("\n" + "=" * 70)
print("H3b: WORD PAIRS IN PHARMA SECTIONS (searching for dose patterns)")
print("=" * 70)

# Re-parse to get sequential words in pharma
pharma_sequences = []  # list of words in order
with open(IVTFF, encoding='latin-1') as f:
    for line in f:
        line = line.rstrip('\n')
        if not line or line.startswith('#'):
            continue
        m = re.match(r'<(f\d+\w?\d?)\.(\d+),[^;]*;H>\s*(.*)', line)
        if not m:
            continue
        folio = m.group(1)
        if get_section(folio) != 'pharma':
            continue
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
        pharma_sequences.extend(expanded)

# Bigrams
bigrams = Counter()
for i in range(len(pharma_sequences) - 1):
    bg = f"{pharma_sequences[i]} {pharma_sequences[i+1]}"
    bigrams[bg] += 1

print("\nTop 30 bigrams in pharma:")
for bg, c in bigrams.most_common(30):
    print(f"  {bg:30s} {c:5d}")

# Look for repeated same-word patterns (like "ana ana" or "ol ol")
print("\nRepeated word patterns (same word twice):")
for bg, c in bigrams.most_common():
    w1, w2 = bg.split()
    if w1 == w2 and c >= 5:
        print(f"  {bg:30s} {c:5d}")

# ========================================================================
# POSITIONAL ANALYSIS: Where do short words appear in the line?
# ========================================================================
print("\n" + "=" * 70)
print("POSITIONAL ANALYSIS: Short word positions in pharma lines")
print("=" * 70)

# For number candidates, check if they appear at specific positions
# (like after ingredient, before unit - typical dose position)
position_data = defaultdict(lambda: Counter())  # word -> {position_category: count}

with open(IVTFF, encoding='latin-1') as f:
    for line in f:
        line = line.rstrip('\n')
        if not line or line.startswith('#'):
            continue
        m_line = re.match(r'<(f\d+\w?\d?)\.(\d+),[^;]*;H>\s*(.*)', line)
        if not m_line:
            continue
        folio = m_line.group(1)
        if get_section(folio) != 'pharma':
            continue
        text = m_line.group(3).strip()
        text = re.sub(r'\{[^}]*\}', '', text)
        text = re.sub(r'<[^>]*>', '', text)
        text = re.sub(r'[!\?\*\'"]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        words = [w.strip() for w in text.split('.') if w.strip()]
        expanded = []
        for w in words:
            parts = w.split()
            expanded.extend([p for p in parts if p and re.match(r'^[a-zA-Z]+$', p)])

        n = len(expanded)
        if n == 0:
            continue

        for i, w in enumerate(expanded):
            if len(w) <= 3 and int(freq_pharma.get(w, 0)) >= 30:
                if i == 0:
                    pos = "LINE_START"
                elif i == n - 1:
                    pos = "LINE_END"
                elif i < n * 0.33:
                    pos = "FIRST_THIRD"
                elif i < n * 0.67:
                    pos = "MIDDLE_THIRD"
                else:
                    pos = "LAST_THIRD"
                position_data[w][pos] += 1

print(f"\n{'Word':8s} {'Start':>6s} {'1st/3':>6s} {'Mid/3':>6s} {'Lst/3':>6s} {'End':>6s} {'Total':>6s} {'Start%':>7s}")
print("-" * 60)
for w in sorted(position_data.keys(), key=lambda x: -sum(position_data[x].values())):
    d = position_data[w]
    total = sum(d.values())
    if total < 20:
        continue
    s = d["LINE_START"]
    f1 = d["FIRST_THIRD"]
    m = d["MIDDLE_THIRD"]
    l = d["LAST_THIRD"]
    e = d["LINE_END"]
    spct = 100 * s / total
    print(f"  {w:6s} {s:6d} {f1:6d} {m:6d} {l:6d} {e:6d} {total:6d} {spct:6.1f}%")

print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)
