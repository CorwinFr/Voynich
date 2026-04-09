#!/usr/bin/env python3
"""
V13 Validation Suite — The hard tests.
2.2 Random baseline, 1.3 Perseus by length, 2.1 Fake manuscript,
1.2 Agglutination A/B, 3.3 Strict filter, 5.1 Pentagram hunt.
"""
import json, os, sys, math, re, random
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

BASE = Path("d:/Github/Voynich")
DECODED = BASE / "v12/output/VOYNICH_DECODE_V12_INGREDIENTS.txt"
CLEAN = BASE / "v12/output/VOYNICH_LATIN_CLEAN.txt"
RESULTS = BASE / "v12/validation_v2/results"
RESULTS.mkdir(exist_ok=True)

PERSEUS_PATH = BASE / "data/latin_valid_wordset.json"
CORPUS_MED = BASE / "data/corpus_latin_medical_extended.txt"


def load_perseus():
    with open(PERSEUS_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if isinstance(data, list):
        return set(w.lower() for w in data)
    elif isinstance(data, dict):
        return set(w.lower() for w in data.keys())
    return set()


def load_decoded_words():
    words = []
    with open(CLEAN, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('=') or line.startswith('#') or line.startswith('---'):
                continue
            for w in re.findall(r'[a-zA-Z]{2,}', line.lower()):
                if not w.startswith('_'):
                    words.append(w)
    return words


def load_corpus_words(path, max_n=500000):
    words = []
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            for w in re.findall(r'[a-zA-Z]{2,}', line.lower()):
                words.append(w)
                if len(words) >= max_n:
                    return words
    return words


# ══════════════════════════════════════════
# TEST 2.2 : RANDOM EVA BASELINE
# ══════════════════════════════════════════
def test_random_baseline():
    print("=" * 60)
    print("TEST 2.2: RANDOM EVA BASELINE")
    print("=" * 60)

    perseus = load_perseus()
    decoded = load_decoded_words()

    # Real Perseus match rate
    real_matches = sum(1 for w in decoded if w in perseus)
    real_pct = 100 * real_matches / len(decoded)

    # EVA character distribution (from decoded file to mimic real EVA)
    eva_chars = "okedy aiin shey chol qoky otal dar lkeey"
    eva_alphabet = list("abcdefghiklmnopqrstxy")
    eva_freq = Counter()
    with open(DECODED, 'r', encoding='utf-8') as f:
        for line in f:
            if 'EVA' in line and ':' in line:
                eva_part = line.split(':', 1)[1] if 'EVA' in line.split(':')[0] else ''
                for c in eva_part.lower():
                    if c in set(eva_alphabet):
                        eva_freq[c] += 1

    total_chars = sum(eva_freq.values())
    eva_weights = [(c, freq/total_chars) for c, freq in eva_freq.most_common()]

    # K&A simplified mapping (primary values only)
    ka_primary = {
        'k': 'c', 'o': 'e', 'd': 'd', 'l': 's', 'a': 'u',
        'r': 'r', 't': 'l', 'e': 'o', 's': 's', 'q': 'c',
        'p': 'p', 'f': 'p', 'i': 'i', 'n': 'n', 'y': 'n',
        'c': 'i', 'h': '', 'g': 'g', 'x': 'x', 'm': 'm',
        'b': 'b', 'v': 'v',
    }

    # Generate random EVA words with same length distribution as real
    real_eva_lengths = []
    with open(DECODED, 'r', encoding='utf-8') as f:
        for line in f:
            if 'EVA' in line and ':' in line:
                parts = line.split(':')
                if 'EVA' in parts[0]:
                    for w in parts[1].strip().split():
                        if w.isalpha():
                            real_eva_lengths.append(len(w))

    if not real_eva_lengths:
        real_eva_lengths = [len(w) for w in decoded]  # fallback

    chars_pool = [c for c, _ in eva_weights]
    weights_pool = [w for _, w in eva_weights]

    N_TRIALS = 10
    random_rates = []

    for trial in range(N_TRIALS):
        random_words = []
        for _ in range(len(decoded)):
            wlen = random.choice(real_eva_lengths)
            # Generate random EVA word
            eva_word = ''.join(random.choices(chars_pool, weights=weights_pool, k=wlen))
            # Apply primary K&A mapping
            latin = ''.join(ka_primary.get(c, c) for c in eva_word)
            latin = latin.replace('ii', 'i')  # basic cleanup
            random_words.append(latin)

        matches = sum(1 for w in random_words if w in perseus)
        rate = 100 * matches / len(random_words)
        random_rates.append(rate)

    avg_random = sum(random_rates) / len(random_rates)
    max_random = max(random_rates)

    # Also test: how many REAL decoded words of each length match Perseus?
    by_len = defaultdict(lambda: {"total": 0, "match": 0})
    for w in decoded:
        by_len[len(w)]["total"] += 1
        if w in perseus:
            by_len[len(w)]["match"] += 1

    # Same for random
    random_by_len = defaultdict(lambda: {"total": 0, "match": 0})
    random_words_last = []
    for _ in range(len(decoded)):
        wlen = random.choice(real_eva_lengths)
        eva_word = ''.join(random.choices(chars_pool, weights=weights_pool, k=wlen))
        latin = ''.join(ka_primary.get(c, c) for c in eva_word)
        random_words_last.append(latin)
        random_by_len[len(latin)]["total"] += 1
        if latin in perseus:
            random_by_len[len(latin)]["match"] += 1

    results = {
        "real_perseus_pct": round(real_pct, 1),
        "random_avg_pct": round(avg_random, 1),
        "random_max_pct": round(max_random, 1),
        "signal_above_noise": round(real_pct - avg_random, 1),
        "n_trials": N_TRIALS,
        "n_words": len(decoded),
        "real_by_length": {str(k): {"total": v["total"], "match": v["match"],
            "pct": round(100*v["match"]/max(v["total"],1), 1)}
            for k, v in sorted(by_len.items())},
        "random_by_length": {str(k): {"total": v["total"], "match": v["match"],
            "pct": round(100*v["match"]/max(v["total"],1), 1)}
            for k, v in sorted(random_by_len.items()) if v["total"] > 10},
    }

    print(f"  Real Perseus match:   {real_pct:.1f}%")
    print(f"  Random baseline avg:  {avg_random:.1f}% (max: {max_random:.1f}%)")
    print(f"  SIGNAL ABOVE NOISE:   {real_pct - avg_random:.1f} percentage points")
    print()
    print(f"  Perseus % by word length (real vs random):")
    for length in sorted(by_len.keys()):
        if length <= 10:
            r = by_len[length]
            rr = random_by_len.get(length, {"total": 0, "match": 0})
            r_pct = 100*r["match"]/max(r["total"],1)
            rr_pct = 100*rr["match"]/max(rr["total"],1) if rr["total"] > 0 else 0
            signal = r_pct - rr_pct
            marker = " <<<" if signal > 20 else ""
            print(f"    {length} chars: real={r_pct:5.1f}% random={rr_pct:5.1f}% "
                  f"signal={signal:+5.1f}pp (n={r['total']}){marker}")

    with open(RESULTS / "v13_random_baseline.json", 'w') as f:
        json.dump(results, f, indent=2)
    print(f"  -> {RESULTS / 'v13_random_baseline.json'}")
    return results


# ══════════════════════════════════════════
# TEST 1.3 : PERSEUS BY WORD LENGTH
# ══════════════════════════════════════════
def test_perseus_by_length():
    print()
    print("=" * 60)
    print("TEST 1.3: PERSEUS MATCH BY WORD LENGTH")
    print("=" * 60)

    perseus = load_perseus()
    decoded = load_decoded_words()

    by_len = defaultdict(lambda: {"total": 0, "match": 0, "examples_match": [], "examples_miss": []})
    for w in decoded:
        l = len(w)
        by_len[l]["total"] += 1
        if w in perseus:
            by_len[l]["match"] += 1
            if len(by_len[l]["examples_match"]) < 5:
                by_len[l]["examples_match"].append(w)
        else:
            if len(by_len[l]["examples_miss"]) < 5:
                by_len[l]["examples_miss"].append(w)

    # Compute filtered scores
    total_5plus = sum(v["total"] for k, v in by_len.items() if k >= 5)
    match_5plus = sum(v["match"] for k, v in by_len.items() if k >= 5)
    total_6plus = sum(v["total"] for k, v in by_len.items() if k >= 6)
    match_6plus = sum(v["match"] for k, v in by_len.items() if k >= 6)

    results = {
        "by_length": {str(k): {
            "total": v["total"],
            "match": v["match"],
            "pct": round(100*v["match"]/max(v["total"],1), 1),
            "examples_match": v["examples_match"],
            "examples_miss": v["examples_miss"],
        } for k, v in sorted(by_len.items())},
        "filtered_5plus": {
            "total": total_5plus,
            "match": match_5plus,
            "pct": round(100*match_5plus/max(total_5plus,1), 1),
        },
        "filtered_6plus": {
            "total": total_6plus,
            "match": match_6plus,
            "pct": round(100*match_6plus/max(total_6plus,1), 1),
        },
        "overall": {
            "total": len(decoded),
            "match": sum(1 for w in decoded if w in perseus),
            "pct": round(100*sum(1 for w in decoded if w in perseus)/len(decoded), 1),
        },
    }

    print(f"  Overall: {results['overall']['pct']}% ({results['overall']['match']}/{results['overall']['total']})")
    print(f"  5+ letters: {results['filtered_5plus']['pct']}% ({match_5plus}/{total_5plus})")
    print(f"  6+ letters: {results['filtered_6plus']['pct']}% ({match_6plus}/{total_6plus})")
    print()
    for length in sorted(by_len.keys()):
        v = by_len[length]
        pct = 100*v["match"]/max(v["total"],1)
        bar = "#" * int(pct/2)
        print(f"    {length:2d} chars: {pct:5.1f}% ({v['match']:5d}/{v['total']:5d}) {bar}")

    with open(RESULTS / "v13_perseus_by_length.json", 'w') as f:
        json.dump(results, f, indent=2)
    print(f"  -> {RESULTS / 'v13_perseus_by_length.json'}")
    return results


# ══════════════════════════════════════════
# TEST 3.3 : STRICT CONFIDENCE FILTER
# ══════════════════════════════════════════
def test_strict_filter():
    print()
    print("=" * 60)
    print("TEST 3.3: STRICT FILTER (5+ letters only)")
    print("=" * 60)

    perseus = load_perseus()
    decoded = load_decoded_words()

    short = [w for w in decoded if len(w) < 5]
    long_words = [w for w in decoded if len(w) >= 5]

    short_match = sum(1 for w in short if w in perseus)
    long_match = sum(1 for w in long_words if w in perseus)

    # Word frequency in long words
    long_freq = Counter(long_words)

    # Check: are long matches real words or repetitive?
    long_unique = set(long_words)
    long_unique_match = sum(1 for w in long_unique if w in perseus)

    results = {
        "all_words": {"n": len(decoded), "perseus": sum(1 for w in decoded if w in perseus)},
        "short_under_5": {"n": len(short), "perseus": short_match,
            "pct": round(100*short_match/max(len(short),1), 1)},
        "long_5plus": {"n": len(long_words), "perseus": long_match,
            "pct": round(100*long_match/max(len(long_words),1), 1)},
        "long_unique_types": {"n": len(long_unique), "perseus": long_unique_match,
            "pct": round(100*long_unique_match/max(len(long_unique),1), 1)},
        "top_long_matched": [{"word": w, "count": c, "in_perseus": w in perseus}
            for w, c in long_freq.most_common(30)],
        "composition": {
            "pct_short": round(100*len(short)/len(decoded), 1),
            "pct_long": round(100*len(long_words)/len(decoded), 1),
        },
    }

    print(f"  ALL words:      {results['all_words']['perseus']}/{results['all_words']['n']}")
    print(f"  Short (<5):     {results['short_under_5']['pct']}% ({short_match}/{len(short)}) "
          f"= {results['composition']['pct_short']}% of corpus")
    print(f"  Long (5+):      {results['long_5plus']['pct']}% ({long_match}/{len(long_words)}) "
          f"= {results['composition']['pct_long']}% of corpus")
    print(f"  Long unique:    {results['long_unique_types']['pct']}% ({long_unique_match}/{len(long_unique)})")
    print()
    print(f"  Top 15 long matched words:")
    for item in results["top_long_matched"][:15]:
        flag = "PERSEUS" if item["in_perseus"] else "NOT IN PERSEUS"
        print(f"    {item['word']:20s} x{item['count']:4d}  {flag}")

    with open(RESULTS / "v13_strict_filter.json", 'w') as f:
        json.dump(results, f, indent=2)
    print(f"  -> {RESULTS / 'v13_strict_filter.json'}")
    return results


# ══════════════════════════════════════════
# TEST 5.1 : PENTAGRAM HUNT
# ══════════════════════════════════════════
def test_pentagram():
    print()
    print("=" * 60)
    print("TEST 5.1: PENTAGRAM HUNT (5-word sequences)")
    print("=" * 60)

    decoded = load_decoded_words()
    corpus = load_corpus_words(CORPUS_MED)

    # Common/generic words to exclude from "interesting" matches
    GENERIC = {"et", "in", "cum", "de", "ex", "per", "ad", "ab", "es", "est",
               "ac", "eo", "eius", "hic", "vel", "sed", "non", "ut", "si",
               "an", "aut", "quod", "qui", "que"}

    # Build corpus n-gram sets
    corpus_5g = defaultdict(int)
    corpus_4g = defaultdict(int)
    for i in range(len(corpus) - 4):
        g5 = tuple(corpus[i:i+5])
        g4 = tuple(corpus[i:i+4])
        corpus_5g[g5] += 1
        corpus_4g[g4] += 1

    # Search decoded text
    decoded_5g = []
    decoded_4g = []
    for i in range(len(decoded) - 4):
        g5 = tuple(decoded[i:i+5])
        g4 = tuple(decoded[i:i+4])

        if g5 in corpus_5g:
            # Check if it's interesting (not all generic)
            non_generic = sum(1 for w in g5 if w not in GENERIC)
            decoded_5g.append({
                "sequence": ' '.join(g5),
                "corpus_count": corpus_5g[g5],
                "non_generic_words": non_generic,
                "position": i,
            })

        if g4 in corpus_4g:
            non_generic = sum(1 for w in g4 if w not in GENERIC)
            if non_generic >= 2:  # At least 2 non-generic words
                decoded_4g.append({
                    "sequence": ' '.join(g4),
                    "corpus_count": corpus_4g[g4],
                    "non_generic_words": non_generic,
                })

    # Deduplicate 4-grams
    unique_4g = {}
    for g in decoded_4g:
        key = g["sequence"]
        if key not in unique_4g or g["non_generic_words"] > unique_4g[key]["non_generic_words"]:
            unique_4g[key] = g
    decoded_4g = sorted(unique_4g.values(), key=lambda x: -x["non_generic_words"])

    results = {
        "pentagrams_found": len(decoded_5g),
        "pentagram_details": decoded_5g[:20],
        "quadrigrams_interesting": len(decoded_4g),
        "top_quadrigrams": decoded_4g[:30],
        "corpus_size": len(corpus),
        "decoded_size": len(decoded),
    }

    print(f"  5-word matches in corpus: {len(decoded_5g)}")
    if decoded_5g:
        for g in decoded_5g[:10]:
            print(f"    '{g['sequence']}' (corpus: {g['corpus_count']}x, "
                  f"non-generic: {g['non_generic_words']})")
    else:
        print(f"    NONE FOUND")

    print(f"  4-word matches (2+ non-generic): {len(decoded_4g)}")
    for g in decoded_4g[:10]:
        print(f"    '{g['sequence']}' (corpus: {g['corpus_count']}x, "
              f"non-generic: {g['non_generic_words']})")

    with open(RESULTS / "v13_pentagram.json", 'w') as f:
        json.dump(results, f, indent=2)
    print(f"  -> {RESULTS / 'v13_pentagram.json'}")
    return results


# ══════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════
if __name__ == "__main__":
    print("V13 VALIDATION SUITE")
    print("=" * 60)
    print()

    r1 = test_random_baseline()
    r2 = test_perseus_by_length()
    r3 = test_strict_filter()
    r4 = test_pentagram()

    # Summary
    print()
    print("=" * 60)
    print("V13 SUMMARY")
    print("=" * 60)
    print(f"  Random baseline:     {r1['random_avg_pct']}% (our floor)")
    print(f"  Real Perseus:        {r1['real_perseus_pct']}%")
    print(f"  Signal above noise:  {r1['signal_above_noise']} pp")
    print(f"  Perseus 5+ letters:  {r2['filtered_5plus']['pct']}%")
    print(f"  Perseus 6+ letters:  {r2['filtered_6plus']['pct']}%")
    print(f"  Short words (<5):    {r3['composition']['pct_short']}% of corpus")
    print(f"  Pentagram matches:   {r4['pentagrams_found']}")
    print(f"  Interesting 4-grams: {r4['quadrigrams_interesting']}")
    print()
    print(f"All results in {RESULTS}/")
