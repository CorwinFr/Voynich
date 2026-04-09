#!/usr/bin/env python3
"""
V13b — Deep diagnostic tests.
The premise: our approach may be flawed but the manuscript may still be
an apothecary's manual. Find out what's real and what's artifact.
"""
import json, sys, re, math, random
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

BASE = Path("d:/Github/Voynich")
DECODED = BASE / "v12/output/VOYNICH_DECODE_V12_INGREDIENTS.txt"
CLEAN = BASE / "v12/output/VOYNICH_LATIN_CLEAN.txt"
RESULTS = BASE / "v12/validation_v2/results"
RESULTS.mkdir(exist_ok=True)

PERSEUS_PATH = BASE / "data/latin_valid_wordset.json"
GLYPHS_PATH = BASE / "v12/rules/glyphs.json"
CORPUS_MED = BASE / "data/corpus_latin_medical_extended.txt"
CORPUS_ITAL = BASE / "data/corpus_italian.txt"


def load_perseus():
    with open(PERSEUS_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return set(w.lower() for w in (data if isinstance(data, list) else data.keys()))


def load_decoded():
    words = []
    with open(CLEAN, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('=') or line.startswith('#') or line.startswith('---'):
                continue
            for w in re.findall(r'[a-zA-Z]{2,}', line.lower()):
                if not w.startswith('_'):
                    words.append(w)
    return words


def load_corpus(path, max_n=500000):
    words = []
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            for w in re.findall(r'[a-zA-Z]{2,}', line.lower()):
                words.append(w)
                if len(words) >= max_n:
                    return words
    return words


def load_eva_words():
    """Extract raw EVA tokens from decode file."""
    eva = []
    with open(DECODED, 'r', encoding='utf-8') as f:
        for line in f:
            if 'EVA' in line and ':' in line:
                parts = line.split(':')
                if 'EVA' in parts[0]:
                    for w in parts[1].strip().split():
                        if w.isalpha() and len(w) >= 2:
                            eva.append(w.lower())
    return eva


# ══════════════════════════════════════════
# TEST 1: RAW K&A — NO SCORER
# Apply only the primary (most probable) K&A value.
# No Perseus, no corpus, no scoring. What comes out?
# ══════════════════════════════════════════
def test_raw_ka():
    print("=" * 60)
    print("TEST 1: RAW K&A MAPPING (no scorer, no Perseus)")
    print("=" * 60)

    with open(GLYPHS_PATH, 'r', encoding='utf-8') as f:
        glyphs = json.load(f)

    # Build primary mapping (highest probability value for each glyph)
    primary = {}
    for glyph, info in glyphs.items():
        if isinstance(info, dict) and "values" in info:
            values = info["values"]
            if isinstance(values, list) and values:
                if isinstance(values[0], dict):
                    best = max(values, key=lambda x: x.get("weight", x.get("probability", 0)))
                    primary[glyph] = best.get("latin", best.get("value", ""))
                else:
                    primary[glyph] = str(values[0])
            elif isinstance(values, str):
                primary[glyph] = values
        elif isinstance(info, str):
            primary[glyph] = info
        elif isinstance(info, list):
            primary[glyph] = str(info[0]) if info else ""

    eva_words = load_eva_words()
    perseus = load_perseus()

    # Apply raw primary mapping
    raw_latin = []
    for eva_w in eva_words:
        latin = ""
        i = 0
        while i < len(eva_w):
            matched = False
            # Try longest glyph first (3, 2, 1 chars)
            for gl in range(min(3, len(eva_w)-i), 0, -1):
                chunk = eva_w[i:i+gl]
                if chunk in primary:
                    latin += primary[chunk]
                    i += gl
                    matched = True
                    break
            if not matched:
                latin += eva_w[i]
                i += 1
        if len(latin) >= 2:
            raw_latin.append(latin.lower())

    # Check against Perseus
    raw_matches = sum(1 for w in raw_latin if w in perseus)
    raw_pct = 100 * raw_matches / max(len(raw_latin), 1)

    # Length distribution
    raw_lengths = Counter(len(w) for w in raw_latin)
    raw_mean_len = sum(len(w) for w in raw_latin) / max(len(raw_latin), 1)

    # Top words
    raw_freq = Counter(raw_latin)

    results = {
        "total_words": len(raw_latin),
        "perseus_match": raw_matches,
        "perseus_pct": round(raw_pct, 1),
        "mean_length": round(raw_mean_len, 2),
        "top_30": [{"word": w, "count": c, "in_perseus": w in perseus}
                   for w, c in raw_freq.most_common(30)],
        "primary_mapping_used": {k: v for k, v in list(primary.items())[:20]},
    }

    print(f"  Raw mapping Perseus:   {raw_pct:.1f}% ({raw_matches}/{len(raw_latin)})")
    print(f"  Mean word length:      {raw_mean_len:.2f}")
    print(f"  (Compare: scored pipeline = 91.6%, random = 24.4%)")
    print(f"  Top 15 raw words:")
    for item in results["top_30"][:15]:
        flag = "PERSEUS" if item["in_perseus"] else "---"
        print(f"    {item['word']:20s} x{item['count']:5d}  {flag}")

    with open(RESULTS / "v13b_raw_ka.json", 'w') as f:
        json.dump(results, f, indent=2)
    print(f"  -> {RESULTS / 'v13b_raw_ka.json'}")
    return results


# ══════════════════════════════════════════
# TEST 2: VOCABULARY CONCENTRATION
# How many unique words make up what % of corpus?
# ══════════════════════════════════════════
def test_vocabulary_concentration():
    print()
    print("=" * 60)
    print("TEST 2: VOCABULARY CONCENTRATION")
    print("=" * 60)

    decoded = load_decoded()
    freq = Counter(decoded)
    total = len(decoded)

    # Cumulative coverage
    sorted_words = freq.most_common()
    cum = 0
    milestones = {}
    for i, (word, count) in enumerate(sorted_words):
        cum += count
        pct = 100 * cum / total
        if i+1 in (5, 10, 20, 50, 100, 200, 500):
            milestones[i+1] = round(pct, 1)

    # Hapax legomena (words appearing once)
    hapax = sum(1 for w, c in freq.items() if c == 1)
    hapax_pct = 100 * hapax / len(freq)

    # Compare with real Latin medical corpus
    corpus = load_corpus(CORPUS_MED, len(decoded))
    corpus_freq = Counter(corpus)
    corpus_hapax = sum(1 for w, c in corpus_freq.items() if c == 1)
    corpus_hapax_pct = 100 * corpus_hapax / max(len(corpus_freq), 1)

    corpus_sorted = corpus_freq.most_common()
    corpus_cum = 0
    corpus_milestones = {}
    for i, (word, count) in enumerate(corpus_sorted):
        corpus_cum += count
        pct = 100 * corpus_cum / len(corpus)
        if i+1 in (5, 10, 20, 50, 100, 200, 500):
            corpus_milestones[i+1] = round(pct, 1)

    results = {
        "decoded": {
            "total_tokens": total,
            "unique_types": len(freq),
            "type_token_ratio": round(len(freq) / total, 4),
            "top_20_coverage": milestones.get(20, 0),
            "top_100_coverage": milestones.get(100, 0),
            "hapax": hapax,
            "hapax_pct_of_types": round(hapax_pct, 1),
            "milestones": milestones,
            "top_20": [(w, c) for w, c in sorted_words[:20]],
        },
        "latin_medical": {
            "total_tokens": len(corpus),
            "unique_types": len(corpus_freq),
            "type_token_ratio": round(len(corpus_freq) / max(len(corpus), 1), 4),
            "top_20_coverage": corpus_milestones.get(20, 0),
            "top_100_coverage": corpus_milestones.get(100, 0),
            "hapax": corpus_hapax,
            "hapax_pct_of_types": round(corpus_hapax_pct, 1),
            "milestones": corpus_milestones,
        },
    }

    print(f"  DECODED:")
    print(f"    Types: {len(freq)}, Tokens: {total}, TTR: {len(freq)/total:.4f}")
    print(f"    Top 20 words cover: {milestones.get(20, '?')}% of corpus")
    print(f"    Top 100 words cover: {milestones.get(100, '?')}% of corpus")
    print(f"    Hapax: {hapax} ({hapax_pct:.1f}% of types)")
    print(f"  LATIN MEDICAL:")
    print(f"    Types: {len(corpus_freq)}, TTR: {len(corpus_freq)/max(len(corpus),1):.4f}")
    print(f"    Top 20 cover: {corpus_milestones.get(20, '?')}%")
    print(f"    Top 100 cover: {corpus_milestones.get(100, '?')}%")
    print(f"    Hapax: {corpus_hapax} ({corpus_hapax_pct:.1f}% of types)")

    with open(RESULTS / "v13b_vocab_concentration.json", 'w') as f:
        json.dump(results, f, indent=2)
    return results


# ══════════════════════════════════════════
# TEST 3: ZIPF'S LAW
# ══════════════════════════════════════════
def test_zipf():
    print()
    print("=" * 60)
    print("TEST 3: ZIPF'S LAW")
    print("=" * 60)

    decoded = load_decoded()
    corpus = load_corpus(CORPUS_MED, len(decoded))

    def zipf_exponent(words):
        freq = Counter(words)
        ranked = [(i+1, c) for i, (w, c) in enumerate(freq.most_common())]
        # Linear regression on log(rank) vs log(freq)
        n = min(200, len(ranked))
        log_r = [math.log(r) for r, _ in ranked[:n]]
        log_f = [math.log(f) for _, f in ranked[:n]]
        mean_r = sum(log_r) / n
        mean_f = sum(log_f) / n
        num = sum((log_r[i] - mean_r) * (log_f[i] - mean_f) for i in range(n))
        den = sum((log_r[i] - mean_r) ** 2 for i in range(n))
        slope = num / max(den, 1e-10)
        return round(-slope, 3)

    decoded_alpha = zipf_exponent(decoded)
    corpus_alpha = zipf_exponent(corpus)

    # Shuffled control
    shuffled = decoded.copy()
    random.shuffle(shuffled)
    # Shuffled has same Zipf by definition (same word frequencies)

    results = {
        "decoded_zipf_exponent": decoded_alpha,
        "latin_medical_zipf_exponent": corpus_alpha,
        "reference": "Natural language typically 0.9-1.1, random ~0.5",
    }

    print(f"  Decoded Zipf exponent:       {decoded_alpha}")
    print(f"  Latin medical Zipf exponent: {corpus_alpha}")
    print(f"  (Natural language: 0.9-1.1)")

    with open(RESULTS / "v13b_zipf.json", 'w') as f:
        json.dump(results, f, indent=2)
    return results


# ══════════════════════════════════════════
# TEST 4: ITALIAN DICTIONARY TEST
# Does our decoded text match Italian better than Latin?
# ══════════════════════════════════════════
def test_italian():
    print()
    print("=" * 60)
    print("TEST 4: ITALIAN vs LATIN DICTIONARY MATCH")
    print("=" * 60)

    perseus = load_perseus()
    decoded = load_decoded()

    # Build Italian word set from corpus
    italian_words_raw = load_corpus(CORPUS_ITAL, 500000)
    italian_dict = set(italian_words_raw)

    latin_match = sum(1 for w in decoded if w in perseus)
    italian_match = sum(1 for w in decoded if w in italian_dict)
    both_match = sum(1 for w in decoded if w in perseus and w in italian_dict)
    latin_only = sum(1 for w in decoded if w in perseus and w not in italian_dict)
    italian_only = sum(1 for w in decoded if w not in perseus and w in italian_dict)

    # By length
    by_len = defaultdict(lambda: {"lat": 0, "ita": 0, "both": 0, "neither": 0, "total": 0})
    for w in decoded:
        l = len(w)
        by_len[l]["total"] += 1
        in_lat = w in perseus
        in_ita = w in italian_dict
        if in_lat and in_ita:
            by_len[l]["both"] += 1
        elif in_lat:
            by_len[l]["lat"] += 1
        elif in_ita:
            by_len[l]["ita"] += 1
        else:
            by_len[l]["neither"] += 1

    results = {
        "total": len(decoded),
        "latin_match": latin_match,
        "latin_pct": round(100 * latin_match / len(decoded), 1),
        "italian_match": italian_match,
        "italian_pct": round(100 * italian_match / len(decoded), 1),
        "both": both_match,
        "latin_only": latin_only,
        "italian_only": italian_only,
        "by_length": {str(k): v for k, v in sorted(by_len.items()) if k <= 10},
        "italian_dict_size": len(italian_dict),
        "perseus_size": len(perseus),
    }

    print(f"  Latin Perseus:  {results['latin_pct']}% ({latin_match})")
    print(f"  Italian corpus: {results['italian_pct']}% ({italian_match})")
    print(f"  Both:           {both_match}")
    print(f"  Latin only:     {latin_only}")
    print(f"  Italian only:   {italian_only}")
    print(f"  Dict sizes: Perseus={len(perseus)}, Italian={len(italian_dict)}")
    print()
    print(f"  By length:")
    for l in range(2, 9):
        v = by_len[l]
        if v["total"] > 0:
            print(f"    {l} chars: Latin={v['lat']:5d} Italian={v['ita']:5d} "
                  f"Both={v['both']:5d} Neither={v['neither']:5d} (n={v['total']})")

    with open(RESULTS / "v13b_italian.json", 'w') as f:
        json.dump(results, f, indent=2)
    return results


# ══════════════════════════════════════════
# TEST 5: COLLATINUS LEMMATIZATION
# How many unique lemmas do the 5+ letter matches reduce to?
# ══════════════════════════════════════════
def test_lemma_diversity():
    print()
    print("=" * 60)
    print("TEST 5: LEMMA DIVERSITY (5+ letter Perseus matches)")
    print("=" * 60)

    import socket

    def collatinus_query(word, timeout=3):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            s.connect(('127.0.0.1', 5555))
            s.sendall(f"-len {word}".encode('utf-8'))
            data = b''
            while True:
                try:
                    chunk = s.recv(4096)
                    if not chunk:
                        break
                    data += chunk
                except:
                    break
            s.close()
            return data.decode('utf-8', errors='ignore')
        except:
            return ""

    decoded = load_decoded()
    perseus = load_perseus()

    # Get unique 5+ letter words in Perseus
    long_matched = set(w for w in decoded if len(w) >= 5 and w in perseus)
    print(f"  Unique 5+ letter Perseus matches: {len(long_matched)}")

    # Try Collatinus for lemmatization
    lemmas = {}
    collatinus_ok = False
    test = collatinus_query("aquam")
    if test and "aqua" in test.lower():
        collatinus_ok = True
        print(f"  Collatinus available, lemmatizing...")

        for i, word in enumerate(sorted(long_matched)):
            if i >= 200:  # cap at 200 queries
                break
            result = collatinus_query(word)
            if result.strip():
                # Extract lemma (first line usually has "* lemma, ...")
                for line in result.split('\n'):
                    if line.startswith('*'):
                        lemma = line.split(',')[0].replace('*', '').strip()
                        lemma = re.sub(r'[^a-zA-Z]', '', lemma).lower()
                        if lemma:
                            lemmas[word] = lemma
                            break
            if not word in lemmas:
                lemmas[word] = word  # self-lemma

        unique_lemmas = set(lemmas.values())
        print(f"  Forms checked: {len(lemmas)}")
        print(f"  Unique lemmas: {len(unique_lemmas)}")
        print(f"  Compression ratio: {len(lemmas)}/{len(unique_lemmas)} = "
              f"{len(lemmas)/max(len(unique_lemmas),1):.1f}:1")

        # Top lemmas by frequency
        lemma_freq = Counter()
        for w in decoded:
            if w in lemmas:
                lemma_freq[lemmas[w]] += 1

        top_lemmas = lemma_freq.most_common(20)
        print(f"  Top 20 lemmas:")
        for lem, cnt in top_lemmas:
            forms = [w for w, l in lemmas.items() if l == lem]
            print(f"    {lem:15s} x{cnt:5d}  forms: {', '.join(forms[:5])}")
    else:
        print(f"  Collatinus not available, skipping lemmatization")
        unique_lemmas = long_matched

    results = {
        "collatinus_available": collatinus_ok,
        "unique_5plus_forms": len(long_matched),
        "forms_checked": len(lemmas),
        "unique_lemmas": len(set(lemmas.values())) if lemmas else len(long_matched),
        "compression_ratio": round(len(lemmas) / max(len(set(lemmas.values())), 1), 2) if lemmas else 1.0,
        "lemma_map": dict(list(lemmas.items())[:100]),
    }

    with open(RESULTS / "v13b_lemma_diversity.json", 'w') as f:
        json.dump(results, f, indent=2)
    return results


# ══════════════════════════════════════════
# TEST 6: SECTION VOCABULARY DIFFERENTIATION
# If it's a real manual, pharma sections should have
# MORE pharma words than herbal sections
# ══════════════════════════════════════════
def test_section_differentiation():
    print()
    print("=" * 60)
    print("TEST 6: SECTION VOCABULARY DIFFERENTIATION")
    print("=" * 60)

    PHARMA_WORDS = {"coque", "coquas", "coquere", "recipe", "misce", "tere",
                    "cola", "ciere", "equaliter", "aloe", "aloes", "ture",
                    "sal", "olei", "oleo", "aceto", "cerae", "iecur", "mel",
                    "hiera", "cicura", "nardi", "cassiae", "apii"}

    # Parse per-folio
    with open(DECODED, 'r', encoding='utf-8') as f:
        content = f.read()

    folio_blocks = re.split(r'FOLIO (\S+) \| Section: (\S+)', content)
    sections = defaultdict(lambda: {"words": [], "pharma_count": 0, "total": 0})

    i = 1
    while i < len(folio_blocks) - 2:
        sec = folio_blocks[i+1]
        block = folio_blocks[i+2]
        for line in block.split('\n'):
            if 'LATIN:' in line:
                for w in re.findall(r'[a-zA-Z]{2,}', line.split('LATIN:')[1].lower()):
                    if not w.startswith('_'):
                        sections[sec]["words"].append(w)
                        sections[sec]["total"] += 1
                        if w in PHARMA_WORDS:
                            sections[sec]["pharma_count"] += 1
        i += 3

    results = {}
    print(f"  {'Section':8s} {'Words':>7s} {'Pharma':>7s} {'%':>7s} {'Top pharma words'}")
    for sec in sorted(sections.keys()):
        data = sections[sec]
        pct = 100 * data["pharma_count"] / max(data["total"], 1)
        pharma_in_sec = Counter(w for w in data["words"] if w in PHARMA_WORDS)
        top3 = ', '.join(f"{w}({c})" for w, c in pharma_in_sec.most_common(3))

        results[sec] = {
            "total_words": data["total"],
            "pharma_words": data["pharma_count"],
            "pharma_pct": round(pct, 1),
            "top_pharma": pharma_in_sec.most_common(10),
        }
        print(f"  {sec:8s} {data['total']:7d} {data['pharma_count']:7d} {pct:6.1f}%  {top3}")

    with open(RESULTS / "v13b_section_diff.json", 'w') as f:
        json.dump(results, f, indent=2)
    return results


# ══════════════════════════════════════════
# TEST 7: EVA WORD BOUNDARY EXPERIMENT
# What if we concatenate EVA pairs and decode?
# ══════════════════════════════════════════
def test_word_boundaries():
    print()
    print("=" * 60)
    print("TEST 7: WORD BOUNDARY EXPERIMENT")
    print("=" * 60)

    eva_words = load_eva_words()
    perseus = load_perseus()

    with open(GLYPHS_PATH, 'r', encoding='utf-8') as f:
        glyphs = json.load(f)

    primary = {}
    for glyph, info in glyphs.items():
        if isinstance(info, dict) and "values" in info:
            values = info["values"]
            if isinstance(values, list) and values:
                if isinstance(values[0], dict):
                    best = max(values, key=lambda x: x.get("weight", x.get("probability", 0)))
                    primary[glyph] = best.get("latin", best.get("value", ""))
                else:
                    primary[glyph] = str(values[0])

    def raw_decode(eva_w):
        latin = ""
        i = 0
        while i < len(eva_w):
            matched = False
            for gl in range(min(3, len(eva_w)-i), 0, -1):
                chunk = eva_w[i:i+gl]
                if chunk in primary:
                    latin += primary[chunk]
                    i += gl
                    matched = True
                    break
            if not matched:
                latin += eva_w[i]
                i += 1
        return latin.lower()

    # Standard: decode each EVA word separately
    standard_results = [raw_decode(w) for w in eva_words]
    standard_perseus = sum(1 for w in standard_results if w in perseus and len(w) >= 4)

    # Experiment: concatenate pairs and decode
    pair_results = []
    for i in range(0, len(eva_words) - 1, 2):
        combined = eva_words[i] + eva_words[i+1]
        decoded = raw_decode(combined)
        pair_results.append(decoded)
    pair_perseus = sum(1 for w in pair_results if w in perseus and len(w) >= 4)

    # Compare lengths
    standard_mean = sum(len(w) for w in standard_results) / max(len(standard_results), 1)
    pair_mean = sum(len(w) for w in pair_results) / max(len(pair_results), 1)

    results = {
        "standard": {
            "n": len(standard_results),
            "perseus_4plus": standard_perseus,
            "pct_4plus": round(100 * standard_perseus / max(len(standard_results), 1), 1),
            "mean_length": round(standard_mean, 2),
        },
        "paired": {
            "n": len(pair_results),
            "perseus_4plus": pair_perseus,
            "pct_4plus": round(100 * pair_perseus / max(len(pair_results), 1), 1),
            "mean_length": round(pair_mean, 2),
        },
        "examples_paired_match": [w for w in pair_results if w in perseus and len(w) >= 5][:20],
    }

    print(f"  Standard (1 EVA = 1 word):  {results['standard']['pct_4plus']}% Perseus (4+), "
          f"mean len={standard_mean:.2f}")
    print(f"  Paired (2 EVA = 1 word):    {results['paired']['pct_4plus']}% Perseus (4+), "
          f"mean len={pair_mean:.2f}")
    if results["examples_paired_match"]:
        print(f"  Paired Perseus matches (5+): {', '.join(results['examples_paired_match'][:10])}")

    with open(RESULTS / "v13b_word_boundaries.json", 'w') as f:
        json.dump(results, f, indent=2)
    return results


# ══════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════
if __name__ == "__main__":
    print("V13b DEEP DIAGNOSTIC SUITE")
    print("=" * 60)

    r1 = test_raw_ka()
    r2 = test_vocabulary_concentration()
    r3 = test_zipf()
    r4 = test_italian()
    r5 = test_lemma_diversity()
    r6 = test_section_differentiation()
    r7 = test_word_boundaries()

    print()
    print("=" * 60)
    print("V13b SUMMARY")
    print("=" * 60)
    print(f"  Raw K&A (no scorer):    {r1['perseus_pct']}% Perseus")
    print(f"  Scored pipeline:        91.6% Perseus")
    print(f"  Random baseline:        24.4% Perseus")
    print(f"  -> Scorer adds {91.6 - r1['perseus_pct']:.1f}pp, mapping alone adds {r1['perseus_pct'] - 24.4:.1f}pp")
    print()
    print(f"  Vocab: top 20 words cover {r2['decoded']['top_20_coverage']}% of corpus")
    print(f"  Hapax: {r2['decoded']['hapax_pct_of_types']}% of types (Latin medical: {r2['latin_medical']['hapax_pct_of_types']}%)")
    print(f"  Zipf: decoded={r3['decoded_zipf_exponent']}, Latin medical={r3['latin_medical_zipf_exponent']}")
    print(f"  Italian match: {r4['italian_pct']}% vs Latin: {r4['latin_pct']}%")
    print(f"  Lemma diversity: {r5['unique_lemmas']} unique lemmas from {r5['unique_5plus_forms']} forms")
    print()
    print(f"  All results in {RESULTS}/")
