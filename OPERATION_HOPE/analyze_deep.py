#!/usr/bin/env python3
"""
OPERATION HOPE - Deep analysis
H4: Gematria / letter-value analysis
H9b: Deep dive on qokeey/qokeedy/qokain family
H3c: "al" and "ain" as number candidates
Line-initial word analysis (potential recipe markers)
"""

import json, re, os
from collections import Counter, defaultdict

DATADIR = "/sessions/laughing-jolly-bell/mnt/Voynich FINAL/OPERATION_HOPE/data"
RESDIR = "/sessions/laughing-jolly-bell/mnt/Voynich FINAL/OPERATION_HOPE/results"
IVTFF = f"{DATADIR}/LSI_ivtff_0d.txt"

# ========================================================================
# Load freq data
# ========================================================================
with open(f"{RESDIR}/freq_pharma.json") as f:
    freq_pharma = json.load(f)
with open(f"{RESDIR}/freq_herbal.json") as f:
    freq_herbal = json.load(f)
with open(f"{RESDIR}/freq_all.json") as f:
    freq_all = json.load(f)

# ========================================================================
# H9b: THE "qok-" FAMILY - a dose/unit pattern?
# ========================================================================
print("=" * 70)
print("H9b: THE 'qok-' FAMILY ANALYSIS")
print("=" * 70)

# Words starting with "qok" are massively pharma-concentrated
qok_words = [(w, int(freq_all[w])) for w in freq_all if w.startswith('qok')]
qok_words.sort(key=lambda x: -x[1])

total_qok_all = sum(c for _, c in qok_words)
total_qok_pharma = sum(int(freq_pharma.get(w, 0)) for w, _ in qok_words)
total_qok_herbal = sum(int(freq_herbal.get(w, 0)) for w, _ in qok_words)

print(f"\nTotal 'qok-' words: {len(qok_words)} types, {total_qok_all} tokens")
print(f"  Pharma: {total_qok_pharma} ({100*total_qok_pharma/total_qok_all:.1f}%)")
print(f"  Herbal: {total_qok_herbal} ({100*total_qok_herbal/total_qok_all:.1f}%)")
print(f"\n{'Word':18s} {'All':>5s} {'Pharma':>7s} {'Herbal':>7s} {'Balnea':>7s} {'P/H':>6s}")
print("-" * 55)
for w, total in qok_words:
    if total >= 5:
        p = int(freq_pharma.get(w, 0))
        h = int(freq_herbal.get(w, 0))
        from json import load
        with open(f"{RESDIR}/freq_balnea.json") as fb:
            freq_balnea = load(fb)
        b = int(freq_balnea.get(w, 0))
        ratio = p / h if h > 0 else float('inf')
        print(f"  {w:16s} {total:5d} {p:7d} {h:7d} {b:7d} {ratio:6.1f}")

# ========================================================================
# Similarly check "ok-" family (without q prefix)
# ========================================================================
print("\n" + "=" * 70)
print("'ok-' FAMILY (without q prefix)")
print("=" * 70)

ok_words = [(w, int(freq_all[w])) for w in freq_all
            if w.startswith('ok') and not w.startswith('qok')]
ok_words.sort(key=lambda x: -x[1])

print(f"\n{'Word':18s} {'All':>5s} {'Pharma':>7s} {'Herbal':>7s} {'P/H':>6s}")
for w, total in ok_words:
    if total >= 10:
        p = int(freq_pharma.get(w, 0))
        h = int(freq_herbal.get(w, 0))
        ratio = p / h if h > 0 else float('inf')
        print(f"  {w:16s} {total:5d} {p:7d} {h:7d} {ratio:6.1f}")

# ========================================================================
# "ot-" family
# ========================================================================
print("\n" + "=" * 70)
print("'ot-' FAMILY")
print("=" * 70)

ot_words = [(w, int(freq_all[w])) for w in freq_all if w.startswith('ot')]
ot_words.sort(key=lambda x: -x[1])

print(f"\n{'Word':18s} {'All':>5s} {'Pharma':>7s} {'Herbal':>7s} {'P/H':>6s}")
for w, total in ot_words:
    if total >= 10:
        p = int(freq_pharma.get(w, 0))
        h = int(freq_herbal.get(w, 0))
        ratio = p / h if h > 0 else float('inf')
        print(f"  {w:16s} {total:5d} {p:7d} {h:7d} {ratio:6.1f}")

# ========================================================================
# LINE-INITIAL WORDS IN PHARMA (recipe start markers?)
# ========================================================================
print("\n" + "=" * 70)
print("LINE-INITIAL WORDS IN PHARMA (potential recipe markers)")
print("=" * 70)

def get_section(folio):
    m = re.match(r'f(\d+)', folio)
    if not m:
        return 'other'
    num = int(m.group(1))
    if 87 <= num <= 116:
        return 'pharma'
    elif 1 <= num <= 66:
        return 'herbal'
    return 'other'

first_words_pharma = Counter()
first_words_herbal = Counter()

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
        if section not in ('pharma', 'herbal'):
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
        if expanded:
            if section == 'pharma':
                first_words_pharma[expanded[0]] += 1
            else:
                first_words_herbal[expanded[0]] += 1

print(f"\nPharma lines: {sum(first_words_pharma.values())}")
print(f"Herbal lines: {sum(first_words_herbal.values())}")

print(f"\n{'Word':18s} {'P_1st':>6s} {'H_1st':>6s} {'P/H':>6s}")
print("-" * 40)
for w, c in first_words_pharma.most_common(30):
    h = first_words_herbal.get(w, 0)
    ratio = c / h if h > 0 else float('inf')
    marker = " ***" if ratio > 3 and c > 5 else ""
    print(f"  {w:16s} {c:6d} {h:6d} {ratio:6.1f}{marker}")

# ========================================================================
# LINE-FINAL WORDS IN PHARMA (dose/closing patterns?)
# ========================================================================
print("\n" + "=" * 70)
print("LINE-FINAL WORDS IN PHARMA")
print("=" * 70)

last_words_pharma = Counter()
last_words_herbal = Counter()

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
        if section not in ('pharma', 'herbal'):
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
        if expanded:
            if section == 'pharma':
                last_words_pharma[expanded[-1]] += 1
            else:
                last_words_herbal[expanded[-1]] += 1

print(f"\n{'Word':18s} {'P_last':>7s} {'H_last':>7s} {'P/H':>6s}")
print("-" * 42)
for w, c in last_words_pharma.most_common(30):
    h = last_words_herbal.get(w, 0)
    ratio = c / h if h > 0 else float('inf')
    marker = " ***" if ratio > 3 and c > 5 else ""
    print(f"  {w:16s} {c:7d} {h:7d} {ratio:6.1f}{marker}")

# ========================================================================
# H4: WORD SUFFIX PATTERNS (potential morphological encoding)
# ========================================================================
print("\n" + "=" * 70)
print("H4: SUFFIX ANALYSIS - Pharma vs Herbal")
print("=" * 70)

# If numbers are encoded as suffixes, we'd see different suffix distributions
def get_suffix(w, n=3):
    return w[-n:] if len(w) >= n else w

suffix_pharma = Counter()
suffix_herbal = Counter()

with open(f"{DATADIR}/vms_pharma_words.json") as f:
    pharma_words = json.load(f)
with open(f"{DATADIR}/vms_herbal_words.json") as f:
    herbal_words = json.load(f)

for w in pharma_words:
    if len(w) >= 3:
        suffix_pharma[get_suffix(w)] += 1
for w in herbal_words:
    if len(w) >= 3:
        suffix_herbal[get_suffix(w)] += 1

# Find suffixes with strong pharma or herbal preference
print(f"\nSuffixes strongly pharma-associated (P/H > 2.5, min 30):")
pharma_suffixes = []
for suf, pc in suffix_pharma.most_common():
    hc = suffix_herbal.get(suf, 0)
    ratio = pc / hc if hc > 0 else float('inf')
    if ratio > 2.5 and pc >= 30:
        pharma_suffixes.append((suf, pc, hc, ratio))

pharma_suffixes.sort(key=lambda x: -x[3])
for suf, pc, hc, ratio in pharma_suffixes[:20]:
    print(f"  -{suf}: pharma={pc}, herbal={hc}, P/H={ratio:.1f}")

print(f"\nSuffixes strongly herbal-associated (H/P > 2.5, min 30):")
herbal_suffixes = []
for suf, hc in suffix_herbal.most_common():
    pc = suffix_pharma.get(suf, 0)
    ratio = hc / pc if pc > 0 else float('inf')
    if ratio > 2.5 and hc >= 30:
        herbal_suffixes.append((suf, hc, pc, ratio))

herbal_suffixes.sort(key=lambda x: -x[3])
for suf, hc, pc, ratio in herbal_suffixes[:20]:
    print(f"  -{suf}: herbal={hc}, pharma={pc}, H/P={ratio:.1f}")

# ========================================================================
# CRITICAL: "ee" vs "ii" ending distribution
# ========================================================================
print("\n" + "=" * 70)
print("CRITICAL: '-eey' vs '-aiin' ending words")
print("=" * 70)

eey_pharma = sum(c for w, c in Counter(pharma_words).items() if w.endswith('eey'))
eey_herbal = sum(c for w, c in Counter(herbal_words).items() if w.endswith('eey'))
aiin_pharma = sum(c for w, c in Counter(pharma_words).items() if w.endswith('aiin'))
aiin_herbal = sum(c for w, c in Counter(herbal_words).items() if w.endswith('aiin'))
edy_pharma = sum(c for w, c in Counter(pharma_words).items() if w.endswith('edy'))
edy_herbal = sum(c for w, c in Counter(herbal_words).items() if w.endswith('edy'))

print(f"  -eey:  pharma={eey_pharma}, herbal={eey_herbal}, P/H={eey_pharma/max(eey_herbal,1):.2f}")
print(f"  -aiin: pharma={aiin_pharma}, herbal={aiin_herbal}, P/H={aiin_pharma/max(aiin_herbal,1):.2f}")
print(f"  -edy:  pharma={edy_pharma}, herbal={edy_herbal}, P/H={edy_pharma/max(edy_herbal,1):.2f}")

# Words ending in -eey
print(f"\n  Top '-eey' words:")
eey_words = [(w, int(freq_all[w])) for w in freq_all if w.endswith('eey')]
eey_words.sort(key=lambda x: -x[1])
for w, total in eey_words[:15]:
    p = int(freq_pharma.get(w, 0))
    h = int(freq_herbal.get(w, 0))
    print(f"    {w:16s} all={total:4d}  pharma={p:4d}  herbal={h:4d}")

# Words ending in -aiin
print(f"\n  Top '-aiin' words:")
aiin_words = [(w, int(freq_all[w])) for w in freq_all if w.endswith('aiin')]
aiin_words.sort(key=lambda x: -x[1])
for w, total in aiin_words[:15]:
    p = int(freq_pharma.get(w, 0))
    h = int(freq_herbal.get(w, 0))
    print(f"    {w:16s} all={total:4d}  pharma={p:4d}  herbal={h:4d}")

# ========================================================================
# DOSE POSITION TEST: In AN, doses follow ingredients.
# In VMS pharma, what follows the most common "ingredient-like" words?
# ========================================================================
print("\n" + "=" * 70)
print("DOSE POSITION TEST: What follows long words in pharma?")
print("=" * 70)

# Hypothesis: longer words = ingredients, shorter words after them = doses
# Get sequential word pairs where word1 is long (>= 6 chars) and word2 is short (<= 4 chars)
pharma_seq = []
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
        pharma_seq.extend(expanded)

# After long words (>=6), what short words (<=3) appear?
post_long = Counter()
for i in range(len(pharma_seq) - 1):
    if len(pharma_seq[i]) >= 6 and len(pharma_seq[i+1]) <= 3:
        post_long[pharma_seq[i+1]] += 1

print(f"\nShort words (<=3) following long words (>=6) in pharma:")
print(f"{'Word':8s} {'Count':>6s}")
for w, c in post_long.most_common(20):
    print(f"  {w:6s} {c:6d}")

# After short words, what comes next?
post_short = Counter()
for i in range(len(pharma_seq) - 2):
    if len(pharma_seq[i]) >= 6 and len(pharma_seq[i+1]) <= 3:
        post_short[pharma_seq[i+2]] += 1

print(f"\nWord after [long + short] in pharma (position 3):")
print(f"{'Word':18s} {'Count':>6s}")
for w, c in post_short.most_common(15):
    print(f"  {w:16s} {c:6d}")

print("\n" + "=" * 70)
print("DEEP ANALYSIS COMPLETE")
print("=" * 70)
