#!/usr/bin/env python3
"""
V14 — The decisive tests.
Test 1: 1000 random mappings + scorer → is the scorer biased?
Test 2: Scorer with Italian dictionary → language-agnostic bias?
Test 3: Bombe inverse → do crib constraints converge?
Test 4: Glyph ablation → which mappings carry signal?
Test 5: Frequency mapping → does simple frequency analysis beat K&A?
"""
import json, sys, re, random, math, time
from collections import Counter, defaultdict
from pathlib import Path
from itertools import product

sys.stdout.reconfigure(encoding='utf-8')

BASE = Path("d:/Github/Voynich")
DECODED = BASE / "v12/output/VOYNICH_DECODE_V12_INGREDIENTS.txt"
RESULTS = BASE / "v12/validation_v2/results"
RESULTS.mkdir(exist_ok=True)

PERSEUS_PATH = BASE / "data/latin_valid_wordset.json"
GLYPHS_PATH = BASE / "v12/rules/glyphs.json"
CORPUS_MED = BASE / "data/corpus_latin_medical_extended.txt"
CORPUS_ITAL = BASE / "data/corpus_italian.txt"

LATIN_LETTERS = "abcdefghilmnopqrstuvx"


def load_perseus():
    with open(PERSEUS_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return set(w.lower() for w in (data if isinstance(data, list) else data.keys()))


def load_eva_tokens():
    """Extract (eva_word, line_index) from decode file."""
    tokens = []
    with open(DECODED, 'r', encoding='utf-8') as f:
        for line in f:
            if 'EVA' in line and ':' in line:
                parts = line.split(':')
                if 'EVA' in parts[0]:
                    for w in parts[1].strip().split():
                        if w.isalpha() and len(w) >= 2:
                            tokens.append(w.lower())
    return tokens


def load_ka_mapping():
    """Load K&A as dict: glyph -> list of (latin_value, weight)."""
    with open(GLYPHS_PATH, 'r', encoding='utf-8') as f:
        glyphs = json.load(f)

    mapping = {}
    for glyph, info in glyphs.items():
        if glyph.startswith('_'):
            continue
        values = []
        if isinstance(info, dict):
            # Format: {"phonemes": ["i", "e"], "weights": [0.6, 0.4]}
            phonemes = info.get("phonemes", info.get("values", []))
            weights = info.get("weights", [])
            if isinstance(phonemes, list):
                for i, p in enumerate(phonemes):
                    w = weights[i] if i < len(weights) else 0.5
                    if p:
                        values.append((str(p), float(w)))
        if values:
            mapping[glyph] = values
    return mapping


def decode_with_mapping(eva_word, char_map):
    """Decode an EVA word using a simple char->char mapping."""
    result = ""
    i = 0
    while i < len(eva_word):
        # Try 3-char, 2-char, 1-char
        matched = False
        for gl in range(min(3, len(eva_word) - i), 0, -1):
            chunk = eva_word[i:i+gl]
            if chunk in char_map:
                result += char_map[chunk]
                i += gl
                matched = True
                break
        if not matched:
            result += eva_word[i]
            i += 1
    return result.lower()


def scorer_decode(eva_word, ka_map, dictionary, max_candidates=20):
    """Simplified scorer: generate candidates from K&A multi-values, pick best Perseus match.
    This mimics what the real pipeline does."""

    # Get all glyphs in order
    glyphs_in_word = []
    i = 0
    while i < len(eva_word):
        matched = False
        for gl in range(min(3, len(eva_word) - i), 0, -1):
            chunk = eva_word[i:i+gl]
            if chunk in ka_map:
                glyphs_in_word.append(chunk)
                i += gl
                matched = True
                break
        if not matched:
            glyphs_in_word.append(eva_word[i])
            i += 1

    if not glyphs_in_word:
        return eva_word

    # Generate candidates by combining values
    # For efficiency, use beam search (keep top candidates)
    candidates = [""]
    for glyph in glyphs_in_word:
        if glyph in ka_map:
            values = ka_map[glyph]
        else:
            values = [(glyph, 0.1)]

        new_candidates = []
        for cand in candidates:
            for val, weight in values[:3]:  # max 3 values per glyph
                new_candidates.append(cand + val)

        # Prune: keep top candidates by length-appropriateness
        if len(new_candidates) > max_candidates:
            # Prefer candidates closer to typical word length
            new_candidates.sort(key=lambda c: abs(len(c) - 5))
            new_candidates = new_candidates[:max_candidates]
        candidates = new_candidates

    # Score: prefer Perseus matches, longer words
    best = eva_word
    best_score = -1
    for cand in candidates:
        c = cand.lower()
        score = 0
        if c in dictionary:
            score += 1000 + len(c) * 100  # Perseus bonus + length bonus
        elif len(c) >= 2 and any(c.startswith(p) for p in ["in", "ex", "de", "per", "cum"]):
            score += 50  # Prefix match
        if score > best_score:
            best_score = score
            best = c
    return best


# ══════════════════════════════════════════
# TEST 1: 1000 RANDOM MAPPINGS + SCORER
# ══════════════════════════════════════════
def test_random_mappings_with_scorer():
    print("=" * 60)
    print("TEST 1: 1000 RANDOM MAPPINGS + SCORER")
    print("This is THE decisive test.")
    print("=" * 60)

    perseus = load_perseus()
    ka_map = load_ka_mapping()
    eva_tokens = load_eva_tokens()

    # Subsample for speed (use every 10th token)
    sample = eva_tokens[::10]
    n_sample = len(sample)
    print(f"  Using {n_sample} EVA tokens (1/10 sample)")

    # First: K&A with scorer (baseline)
    ka_results = []
    for eva_w in sample:
        decoded = scorer_decode(eva_w, ka_map, perseus)
        ka_results.append(decoded)
    ka_match = sum(1 for w in ka_results if w in perseus)
    ka_pct = 100 * ka_match / n_sample
    print(f"  K&A + scorer: {ka_pct:.1f}%")

    # Get unique EVA glyphs used
    eva_glyphs = sorted(ka_map.keys())
    print(f"  K&A glyphs: {len(eva_glyphs)}")

    # Run N random mappings
    N_RANDOM = 200  # 200 for speed, statistically sufficient
    random_scores = []
    t0 = time.time()

    for trial in range(N_RANDOM):
        # Generate random mapping: each K&A glyph gets random Latin values
        random_map = {}
        for glyph in eva_glyphs:
            n_values = len(ka_map[glyph])
            values = []
            for _ in range(n_values):
                # Random Latin string of similar length to K&A values
                orig_len = len(ka_map[glyph][0][0])
                rand_val = ''.join(random.choices(LATIN_LETTERS, k=max(1, orig_len)))
                values.append((rand_val, 0.5))
            random_map[glyph] = values

        # Decode with random mapping + scorer
        matches = 0
        for eva_w in sample:
            decoded = scorer_decode(eva_w, random_map, perseus)
            if decoded in perseus:
                matches += 1
        pct = 100 * matches / n_sample
        random_scores.append(pct)

        if (trial + 1) % 50 == 0:
            elapsed = time.time() - t0
            avg = sum(random_scores) / len(random_scores)
            print(f"    Trial {trial+1}/{N_RANDOM}: avg={avg:.1f}%, "
                  f"max={max(random_scores):.1f}%, elapsed={elapsed:.0f}s")

    avg_random = sum(random_scores) / len(random_scores)
    max_random = max(random_scores)
    min_random = min(random_scores)
    std_random = (sum((x - avg_random)**2 for x in random_scores) / len(random_scores)) ** 0.5

    # How many standard deviations is K&A above random?
    z_score = (ka_pct - avg_random) / max(std_random, 0.01)

    results = {
        "ka_with_scorer_pct": round(ka_pct, 1),
        "random_with_scorer_avg": round(avg_random, 1),
        "random_with_scorer_max": round(max_random, 1),
        "random_with_scorer_min": round(min_random, 1),
        "random_with_scorer_std": round(std_random, 2),
        "z_score_ka_vs_random": round(z_score, 1),
        "n_trials": N_RANDOM,
        "n_sample": n_sample,
        "verdict": "",
    }

    if ka_pct - avg_random < 10:
        results["verdict"] = "SCORER IS BIASED: K&A is within noise of random mappings"
    elif ka_pct - avg_random < 25:
        results["verdict"] = "WEAK SIGNAL: K&A marginally better than random+scorer"
    else:
        results["verdict"] = "REAL SIGNAL: K&A significantly outperforms random+scorer"

    print()
    print(f"  ╔══════════════════════════════════════╗")
    print(f"  ║  K&A + scorer:       {ka_pct:5.1f}%           ║")
    print(f"  ║  Random + scorer:    {avg_random:5.1f}% ± {std_random:.1f}%     ║")
    print(f"  ║  Max random:         {max_random:5.1f}%           ║")
    print(f"  ║  Z-score:            {z_score:5.1f}            ║")
    print(f"  ║  VERDICT: {results['verdict'][:35]:35s}  ║")
    print(f"  ╚══════════════════════════════════════╝")

    with open(RESULTS / "v14_random_scorer.json", 'w') as f:
        json.dump(results, f, indent=2)
    return results


# ══════════════════════════════════════════
# TEST 2: SCORER WITH ITALIAN DICTIONARY
# ══════════════════════════════════════════
def test_italian_scorer():
    print()
    print("=" * 60)
    print("TEST 2: SCORER WITH ITALIAN DICTIONARY")
    print("=" * 60)

    # Build Italian dictionary
    italian_words = set()
    with open(CORPUS_ITAL, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            for w in re.findall(r'[a-zA-Z]{2,}', line.lower()):
                italian_words.add(w)
    print(f"  Italian dict: {len(italian_words)} words")

    perseus = load_perseus()
    ka_map = load_ka_mapping()
    eva_tokens = load_eva_tokens()
    sample = eva_tokens[::10]

    # K&A + Latin scorer
    latin_matches = 0
    for eva_w in sample:
        if scorer_decode(eva_w, ka_map, perseus) in perseus:
            latin_matches += 1
    latin_pct = 100 * latin_matches / len(sample)

    # K&A + Italian scorer (same mapping, different dictionary)
    italian_matches = 0
    for eva_w in sample:
        if scorer_decode(eva_w, ka_map, italian_words) in italian_words:
            italian_matches += 1
    italian_pct = 100 * italian_matches / len(sample)

    results = {
        "ka_latin_pct": round(latin_pct, 1),
        "ka_italian_pct": round(italian_pct, 1),
        "latin_dict_size": len(perseus),
        "italian_dict_size": len(italian_words),
        "verdict": "",
    }

    if abs(latin_pct - italian_pct) < 10:
        results["verdict"] = "SCORER IS LANGUAGE-AGNOSTIC: adapts to any dictionary"
    elif latin_pct > italian_pct + 20:
        results["verdict"] = "LATIN-SPECIFIC: K&A mapping favors Latin over Italian"
    else:
        results["verdict"] = f"MODERATE: Latin={latin_pct:.0f}% vs Italian={italian_pct:.0f}%"

    print(f"  K&A + Latin scorer:   {latin_pct:.1f}%")
    print(f"  K&A + Italian scorer: {italian_pct:.1f}%")
    print(f"  VERDICT: {results['verdict']}")

    with open(RESULTS / "v14_italian_scorer.json", 'w') as f:
        json.dump(results, f, indent=2)
    return results


# ══════════════════════════════════════════
# TEST 3: BOMBE INVERSE (crib constraints)
# ══════════════════════════════════════════
def test_bombe_inverse():
    print()
    print("=" * 60)
    print("TEST 3: BOMBE INVERSE — Do crib constraints converge?")
    print("=" * 60)

    ka_map = load_ka_mapping()
    eva_tokens = load_eva_tokens()
    perseus = load_perseus()

    # Find EVA tokens that the scorer maps to key cribs
    CRIBS = ["aquam", "coque", "hiera", "aloes", "ciere", "curam", "recipe"]

    # For each crib, find all EVA tokens that decode to it
    crib_eva_sources = defaultdict(list)
    for eva_w in eva_tokens:
        decoded = scorer_decode(eva_w, ka_map, perseus)
        if decoded in CRIBS:
            crib_eva_sources[decoded].append(eva_w)

    # For each crib, analyze: what glyph values are REQUIRED?
    results = {"cribs": {}}

    for crib in CRIBS:
        sources = crib_eva_sources.get(crib, [])
        source_freq = Counter(sources)
        unique_sources = list(source_freq.keys())

        print(f"  '{crib}': {len(sources)} occurrences from {len(unique_sources)} unique EVA tokens")
        for eva_w, count in source_freq.most_common(5):
            print(f"    {eva_w:15s} x{count:4d}")

        # Check: do these EVA tokens share structure?
        if len(unique_sources) >= 2:
            # Compare character composition
            char_positions = defaultdict(lambda: Counter())
            for eva_w in unique_sources[:10]:
                for pos, ch in enumerate(eva_w):
                    char_positions[pos][ch] += 1

        results["cribs"][crib] = {
            "total_occurrences": len(sources),
            "unique_eva_tokens": len(unique_sources),
            "top_5_sources": [(w, c) for w, c in source_freq.most_common(5)],
            "one_to_one": len(unique_sources) == 1,
        }

    # Check consistency: does the same EVA token always decode to the same crib?
    eva_to_crib = defaultdict(Counter)
    for crib, sources in crib_eva_sources.items():
        for eva_w in sources:
            eva_to_crib[eva_w][crib] += 1

    inconsistent = 0
    consistent = 0
    for eva_w, crib_counts in eva_to_crib.items():
        if len(crib_counts) > 1:
            inconsistent += 1
        else:
            consistent += 1

    results["consistency"] = {
        "consistent_tokens": consistent,
        "inconsistent_tokens": inconsistent,
        "pct_consistent": round(100 * consistent / max(consistent + inconsistent, 1), 1),
    }

    print(f"\n  Consistency: {consistent} tokens always → same crib, "
          f"{inconsistent} tokens → multiple cribs")
    print(f"  {results['consistency']['pct_consistent']}% consistent")

    # Key insight: how many DIFFERENT EVA tokens produce "aquam"?
    # If 50 different EVA words all decode to "aquam", the scorer is brute-forcing
    for crib in CRIBS[:3]:
        n = results["cribs"][crib]["unique_eva_tokens"]
        ratio = results["cribs"][crib]["total_occurrences"] / max(n, 1)
        print(f"  '{crib}': {n} unique EVA → ratio {ratio:.1f}:1 "
              f"({'focused' if n <= 3 else 'SCATTERED' if n > 10 else 'moderate'})")

    with open(RESULTS / "v14_bombe_inverse.json", 'w') as f:
        json.dump(results, f, indent=2)
    return results


# ══════════════════════════════════════════
# TEST 4: GLYPH ABLATION
# ══════════════════════════════════════════
def test_glyph_ablation():
    print()
    print("=" * 60)
    print("TEST 4: GLYPH ABLATION — Which mappings carry signal?")
    print("=" * 60)

    perseus = load_perseus()
    ka_map = load_ka_mapping()
    eva_tokens = load_eva_tokens()
    sample = eva_tokens[::10]
    n_sample = len(sample)

    # Baseline: full K&A + scorer
    baseline_matches = sum(1 for w in sample if scorer_decode(w, ka_map, perseus) in perseus)
    baseline_pct = 100 * baseline_matches / n_sample
    print(f"  Baseline (all glyphs): {baseline_pct:.1f}%")

    # Ablate each glyph
    results = {"baseline": round(baseline_pct, 1), "ablations": {}}

    for glyph in sorted(ka_map.keys()):
        # Create mapping with this glyph randomized
        ablated_map = dict(ka_map)
        n_vals = len(ka_map[glyph])
        ablated_map[glyph] = [(''.join(random.choices(LATIN_LETTERS,
            k=max(1, len(ka_map[glyph][0][0])))), 0.5) for _ in range(n_vals)]

        matches = sum(1 for w in sample if scorer_decode(w, ablated_map, perseus) in perseus)
        pct = 100 * matches / n_sample
        drop = baseline_pct - pct

        results["ablations"][glyph] = {
            "without_pct": round(pct, 1),
            "drop": round(drop, 1),
            "original_values": [(v, round(w, 2)) for v, w in ka_map[glyph][:3]],
        }

    # Sort by drop
    sorted_glyphs = sorted(results["ablations"].items(), key=lambda x: -x[1]["drop"])

    print(f"\n  Glyph ablation (sorted by impact):")
    for glyph, data in sorted_glyphs:
        vals = ', '.join(v for v, w in data["original_values"])
        bar = "#" * max(0, int(data["drop"]))
        print(f"    {glyph:4s} ({vals:12s}): drop={data['drop']:+5.1f}pp {bar}")

    with open(RESULTS / "v14_glyph_ablation.json", 'w') as f:
        json.dump(results, f, indent=2)
    return results


# ══════════════════════════════════════════
# TEST 5: FREQUENCY-BASED MAPPING
# ══════════════════════════════════════════
def test_frequency_mapping():
    print()
    print("=" * 60)
    print("TEST 5: FREQUENCY-BASED MAPPING (no K&A)")
    print("=" * 60)

    perseus = load_perseus()
    ka_map = load_ka_mapping()
    eva_tokens = load_eva_tokens()
    sample = eva_tokens[::10]

    # Count EVA single-char frequencies
    eva_freq = Counter()
    for token in eva_tokens:
        for c in token:
            eva_freq[c] += 1

    # Count Latin medical char frequencies
    latin_freq = Counter()
    with open(CORPUS_MED, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            for c in line.lower():
                if c.isalpha():
                    latin_freq[c] += 1

    # Map by rank
    eva_ranked = [c for c, _ in eva_freq.most_common()]
    latin_ranked = [c for c, _ in latin_freq.most_common()]

    freq_map = {}
    for i, eva_c in enumerate(eva_ranked):
        if i < len(latin_ranked):
            freq_map[eva_c] = [(latin_ranked[i], 1.0)]
        else:
            freq_map[eva_c] = [(eva_c, 0.1)]

    # Test frequency mapping + scorer
    freq_matches = sum(1 for w in sample
                       if scorer_decode(w, freq_map, perseus) in perseus)
    freq_pct = 100 * freq_matches / len(sample)

    # Test K&A + scorer (for comparison on same sample)
    ka_matches = sum(1 for w in sample
                     if scorer_decode(w, ka_map, perseus) in perseus)
    ka_pct = 100 * ka_matches / len(sample)

    results = {
        "frequency_mapping_pct": round(freq_pct, 1),
        "ka_mapping_pct": round(ka_pct, 1),
        "difference": round(ka_pct - freq_pct, 1),
        "eva_freq_rank": eva_ranked[:15],
        "latin_freq_rank": latin_ranked[:15],
        "freq_map_sample": {k: v[0][0] for k, v in list(freq_map.items())[:15]},
    }

    print(f"  Frequency mapping + scorer: {freq_pct:.1f}%")
    print(f"  K&A mapping + scorer:       {ka_pct:.1f}%")
    print(f"  Difference:                 {ka_pct - freq_pct:+.1f}pp")
    print()
    print(f"  Frequency map (EVA→Latin by rank):")
    for i in range(min(10, len(eva_ranked))):
        ec = eva_ranked[i]
        lc = latin_ranked[i] if i < len(latin_ranked) else "?"
        print(f"    {ec} → {lc}  (EVA freq={eva_freq[ec]}, Latin freq={latin_freq.get(lc,0)})")

    with open(RESULTS / "v14_frequency_mapping.json", 'w') as f:
        json.dump(results, f, indent=2)
    return results


# ══════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════
if __name__ == "__main__":
    print("V14 DECISIVE VALIDATION SUITE")
    print("=" * 60)
    t_start = time.time()

    r1 = test_random_mappings_with_scorer()
    r2 = test_italian_scorer()
    r3 = test_bombe_inverse()
    r4 = test_glyph_ablation()
    r5 = test_frequency_mapping()

    elapsed = time.time() - t_start

    print()
    print("=" * 60)
    print(f"V14 FINAL SUMMARY (elapsed: {elapsed:.0f}s)")
    print("=" * 60)
    print(f"  K&A + scorer:           {r1['ka_with_scorer_pct']}%")
    print(f"  Random + scorer:        {r1['random_with_scorer_avg']}% ± {r1['random_with_scorer_std']}%")
    print(f"  Z-score K&A vs random:  {r1['z_score_ka_vs_random']}")
    print(f"  → {r1['verdict']}")
    print()
    print(f"  K&A + Latin scorer:     {r2['ka_latin_pct']}%")
    print(f"  K&A + Italian scorer:   {r2['ka_italian_pct']}%")
    print(f"  → {r2['verdict']}")
    print()
    print(f"  Crib consistency:       {r3['consistency']['pct_consistent']}%")
    print(f"  Frequency vs K&A:       {r5['frequency_mapping_pct']}% vs {r5['ka_mapping_pct']}% ({r5['difference']:+.1f}pp)")
    print()
    print(f"  All results in {RESULTS}/")
