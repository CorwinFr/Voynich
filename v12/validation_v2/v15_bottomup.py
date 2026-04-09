#!/usr/bin/env python3
"""
V15 — Bottom-up approach.
Start from CONFIRMED anchors (logograms + strong glyphs).
Derive unknown glyphs by constraint propagation.
Build the mapping one glyph at a time, verify at each step.
"""
import json, sys, re, math
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

BASE = Path("d:/Github/Voynich")
DECODED_FILE = BASE / "v12/output/VOYNICH_DECODE_V12_INGREDIENTS.txt"
RESULTS = BASE / "v12/validation_v2/results"
RESULTS.mkdir(exist_ok=True)
PERSEUS_PATH = BASE / "data/latin_valid_wordset.json"
LOGOGRAMS_PATH = BASE / "v12/rules/logograms.json"
GLYPHS_PATH = BASE / "v12/rules/glyphs.json"


def load_perseus():
    with open(PERSEUS_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return set(w.lower() for w in (data if isinstance(data, list) else data.keys()))


def load_eva_tokens():
    tokens = []
    with open(DECODED_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            if 'EVA' in line and ':' in line:
                parts = line.split(':')
                if 'EVA' in parts[0]:
                    for w in parts[1].strip().split():
                        if w.isalpha() and len(w) >= 2:
                            tokens.append(w.lower())
    return tokens


def load_logograms():
    with open(LOGOGRAMS_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # Format: {"dy": {"latin": "et", ...}, ...}
    result = {}
    for eva, info in data.items():
        if isinstance(info, dict):
            latin = info.get("latin", "")
            if latin:
                result[eva.lower()] = latin.lower()
        elif isinstance(info, str):
            result[eva.lower()] = info.lower()
    return result


# ══════════════════════════════════════════
# STEP 1: WHAT DO LOGOGRAMS TELL US?
# Each logogram is a known (EVA → Latin) pair.
# From these pairs, extract implied glyph values.
# ══════════════════════════════════════════
def step1_logogram_constraints():
    print("=" * 60)
    print("STEP 1: EXTRACT GLYPH CONSTRAINTS FROM LOGOGRAMS")
    print("=" * 60)

    logograms = load_logograms()
    print(f"  Loaded {len(logograms)} logograms")

    # For each logogram, what does each character position imply?
    # E.g., "qoky" → "coque" implies:
    #   q → co (positions 0→0-1)
    #   o → qu (positions 1→2-3) ... but this doesn't work simply
    #
    # Better approach: look at SHORT logograms (1-2 EVA chars) where
    # the mapping is unambiguous.

    short_logograms = {k: v for k, v in logograms.items() if len(k) <= 3}
    print(f"  Short logograms (<=3 EVA chars): {len(short_logograms)}")

    # Single-char logograms: direct glyph→value
    single = {k: v for k, v in logograms.items() if len(k) == 1}
    print(f"\n  SINGLE-CHAR LOGOGRAMS (direct glyph values):")
    for eva, latin in sorted(single.items()):
        print(f"    {eva} → {latin}")

    # Two-char logograms: can sometimes extract per-glyph values
    double = {k: v for k, v in logograms.items() if len(k) == 2}
    print(f"\n  TWO-CHAR LOGOGRAMS ({len(double)}):")
    for eva, latin in sorted(double.items()):
        print(f"    {eva} → {latin}")

    # Constraint extraction: for each glyph, collect all implied values
    glyph_evidence = defaultdict(list)

    for eva, latin in logograms.items():
        if len(eva) == 1:
            glyph_evidence[eva].append(("logogram_single", latin, 1.0))
        elif len(eva) == 2:
            # Can't uniquely decompose without assumptions
            # But we can note that glyph[0] starts the latin and glyph[1] ends it
            glyph_evidence[eva[0]].append(("logogram_start", latin[:len(latin)//2+1], 0.5))
            glyph_evidence[eva[1]].append(("logogram_end", latin[len(latin)//2:], 0.5))

    return logograms, glyph_evidence


# ══════════════════════════════════════════
# STEP 2: FREQUENCY ANALYSIS OF EVA
# What are the most common EVA tokens?
# What are their structural properties?
# ══════════════════════════════════════════
def step2_eva_frequency():
    print()
    print("=" * 60)
    print("STEP 2: EVA TOKEN FREQUENCY ANALYSIS")
    print("=" * 60)

    eva_tokens = load_eva_tokens()
    freq = Counter(eva_tokens)
    total = len(eva_tokens)

    print(f"  Total tokens: {total}")
    print(f"  Unique types: {len(freq)}")
    print(f"\n  Top 30 EVA tokens:")

    top30 = freq.most_common(30)
    for i, (token, count) in enumerate(top30):
        pct = 100 * count / total
        print(f"    {i+1:2d}. {token:15s} x{count:5d} ({pct:4.1f}%)  len={len(token)}")

    # Character frequency
    char_freq = Counter()
    for token in eva_tokens:
        for c in token:
            char_freq[c] += 1

    print(f"\n  EVA character frequency:")
    for c, cnt in char_freq.most_common():
        print(f"    {c}: {cnt:7d} ({100*cnt/sum(char_freq.values()):4.1f}%)")

    return freq, char_freq


# ══════════════════════════════════════════
# STEP 3: LOGOGRAM COVERAGE
# How much of the text do confirmed logograms cover?
# ══════════════════════════════════════════
def step3_logogram_coverage():
    print()
    print("=" * 60)
    print("STEP 3: LOGOGRAM COVERAGE")
    print("=" * 60)

    logograms = load_logograms()
    eva_tokens = load_eva_tokens()
    perseus = load_perseus()

    covered = 0
    not_covered = 0
    covered_words = []
    uncovered_words = []

    for token in eva_tokens:
        if token in logograms:
            covered += 1
            latin = logograms[token]
            covered_words.append((token, latin))
        else:
            not_covered += 1
            uncovered_words.append(token)

    coverage_pct = 100 * covered / len(eva_tokens)

    # Of the covered words, how many are in Perseus?
    covered_perseus = sum(1 for _, latin in covered_words if latin in perseus)
    covered_perseus_pct = 100 * covered_perseus / max(covered, 1)

    # Of the uncovered words, what are they?
    uncovered_freq = Counter(uncovered_words)

    print(f"  Logogram coverage: {covered}/{len(eva_tokens)} = {coverage_pct:.1f}%")
    print(f"  Covered words in Perseus: {covered_perseus}/{covered} = {covered_perseus_pct:.1f}%")
    print(f"  Uncovered tokens: {not_covered} ({len(uncovered_freq)} unique)")
    print(f"\n  Top 20 UNCOVERED EVA tokens (need phonetic decoding):")
    for token, count in uncovered_freq.most_common(20):
        print(f"    {token:15s} x{count:5d}  len={len(token)}")

    # What % of text would be decoded with JUST logograms?
    logogram_latin = [logograms[t] for t in eva_tokens if t in logograms]
    logogram_perseus = sum(1 for w in logogram_latin if w in perseus)

    results = {
        "total_tokens": len(eva_tokens),
        "covered_by_logograms": covered,
        "coverage_pct": round(coverage_pct, 1),
        "covered_perseus_pct": round(covered_perseus_pct, 1),
        "uncovered_unique": len(uncovered_freq),
        "top_uncovered": uncovered_freq.most_common(50),
    }

    with open(RESULTS / "v15_logogram_coverage.json", 'w') as f:
        json.dump(results, f, indent=2)
    return results


# ══════════════════════════════════════════
# STEP 4: KNOWN-WORD REVERSE ENGINEERING
# For the most common UNCOVERED EVA tokens,
# what Latin word would make the most sense?
# Use position-in-text, co-occurrence with known words.
# ══════════════════════════════════════════
def step4_reverse_engineering():
    print()
    print("=" * 60)
    print("STEP 4: REVERSE ENGINEERING UNCOVERED TOKENS")
    print("=" * 60)

    logograms = load_logograms()
    eva_tokens = load_eva_tokens()
    perseus = load_perseus()

    # Build context windows: for each uncovered token, what logograms surround it?
    contexts = defaultdict(lambda: {"prev": Counter(), "next": Counter(), "count": 0})

    for i, token in enumerate(eva_tokens):
        if token not in logograms:
            contexts[token]["count"] += 1
            if i > 0 and eva_tokens[i-1] in logograms:
                contexts[token]["prev"][logograms[eva_tokens[i-1]]] += 1
            if i < len(eva_tokens) - 1 and eva_tokens[i+1] in logograms:
                contexts[token]["next"][logograms[eva_tokens[i+1]]] += 1

    # For top uncovered tokens, show context
    sorted_uncovered = sorted(contexts.items(), key=lambda x: -x[1]["count"])

    print(f"  Top 15 uncovered tokens with logogram context:")
    results = {"tokens": []}

    for token, ctx in sorted_uncovered[:15]:
        prev_top = ctx["prev"].most_common(3)
        next_top = ctx["next"].most_common(3)
        prev_str = ', '.join(f"{w}({c})" for w, c in prev_top)
        next_str = ', '.join(f"{w}({c})" for w, c in next_top)

        # Try to guess what this word might be from context
        # In pharmaceutical Latin: [prev] TOKEN [next]
        # Common patterns: et TOKEN et, in TOKEN cum, etc.

        entry = {
            "eva": token,
            "count": ctx["count"],
            "length": len(token),
            "prev_context": prev_top,
            "next_context": next_top,
        }
        results["tokens"].append(entry)

        print(f"    {token:15s} x{ctx['count']:4d}  prev=[{prev_str}]  next=[{next_str}]")

    with open(RESULTS / "v15_reverse_engineering.json", 'w') as f:
        json.dump(results, f, indent=2)
    return results


# ══════════════════════════════════════════
# STEP 5: GLYPH-BY-GLYPH BRUTE FORCE
# For each of the top 5 signal glyphs (o, r, y, t, iin),
# test ALL possible Latin letter assignments.
# Which value maximizes Perseus matches on the uncovered tokens?
# ══════════════════════════════════════════
def step5_glyph_brute_force():
    print()
    print("=" * 60)
    print("STEP 5: BRUTE-FORCE OPTIMAL GLYPH VALUES")
    print("=" * 60)

    perseus = load_perseus()
    logograms = load_logograms()
    eva_tokens = load_eva_tokens()

    # Get uncovered tokens (need phonetic decoding)
    uncovered = [t for t in eva_tokens if t not in logograms]
    uncovered_sample = uncovered[::5]  # 1/5 sample for speed

    # Load current K&A
    with open(GLYPHS_PATH, 'r', encoding='utf-8') as f:
        glyphs_raw = json.load(f)

    ka_primary = {}
    for g, info in glyphs_raw.items():
        if g.startswith('_'):
            continue
        if isinstance(info, dict) and "phonemes" in info:
            phonemes = info["phonemes"]
            if phonemes:
                ka_primary[g] = str(phonemes[0])

    # Target glyphs to optimize (from V14 ablation: highest signal)
    TARGET_GLYPHS = ['o', 'r', 'y', 't', 'l', 'a', 'e', 's', 'k', 'd']
    CANDIDATES = list("abcdefghilmnopqrstuvx") + [""]  # include empty (silent)

    print(f"  Uncovered sample: {len(uncovered_sample)} tokens")
    print(f"  Testing {len(TARGET_GLYPHS)} glyphs x {len(CANDIDATES)} candidates")

    def decode_simple(eva_word, char_map):
        result = ""
        i = 0
        while i < len(eva_word):
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

    def score_mapping(char_map, sample):
        """Count Perseus matches for decoded words of 4+ letters."""
        matches = 0
        total_4plus = 0
        for eva_w in sample:
            decoded = decode_simple(eva_w, char_map)
            if len(decoded) >= 4:
                total_4plus += 1
                if decoded in perseus:
                    matches += 1
        return matches, total_4plus

    # Baseline with K&A primary
    base_matches, base_total = score_mapping(ka_primary, uncovered_sample)
    base_pct = 100 * base_matches / max(base_total, 1)
    print(f"\n  Baseline K&A primary: {base_pct:.1f}% ({base_matches}/{base_total} words 4+)")

    results = {"baseline": {"matches": base_matches, "total_4plus": base_total,
                            "pct": round(base_pct, 1)},
               "optimized_glyphs": {}}

    # Optimize each glyph independently
    for target in TARGET_GLYPHS:
        best_val = ka_primary.get(target, target)
        best_score = base_matches
        ka_val = ka_primary.get(target, "?")

        for candidate in CANDIDATES:
            test_map = dict(ka_primary)
            test_map[target] = candidate
            matches, total = score_mapping(test_map, uncovered_sample)
            if matches > best_score:
                best_score = matches
                best_val = candidate

        improvement = best_score - base_matches
        results["optimized_glyphs"][target] = {
            "ka_value": ka_val,
            "optimal_value": best_val,
            "improvement": improvement,
            "changed": best_val != ka_val,
        }

        marker = " *** DIFFERENT" if best_val != ka_val else ""
        print(f"    {target}: K&A='{ka_val}' → optimal='{best_val}' "
              f"(+{improvement} matches){marker}")

    # Build optimized full mapping
    optimized_map = dict(ka_primary)
    total_improvement = 0
    for g, data in results["optimized_glyphs"].items():
        if data["changed"]:
            optimized_map[g] = data["optimal_value"]
            total_improvement += data["improvement"]

    opt_matches, opt_total = score_mapping(optimized_map, uncovered_sample)
    opt_pct = 100 * opt_matches / max(opt_total, 1)

    results["optimized_total"] = {
        "matches": opt_matches, "total_4plus": opt_total,
        "pct": round(opt_pct, 1),
        "improvement_over_ka": round(opt_pct - base_pct, 1),
    }

    print(f"\n  Optimized mapping: {opt_pct:.1f}% ({opt_matches}/{opt_total})")
    print(f"  Improvement over K&A: +{opt_pct - base_pct:.1f}pp")

    with open(RESULTS / "v15_glyph_optimization.json", 'w') as f:
        json.dump(results, f, indent=2)
    return results


# ══════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════
if __name__ == "__main__":
    print("V15 BOTTOM-UP RECONSTRUCTION")
    print("=" * 60)

    logograms, glyph_evidence = step1_logogram_constraints()
    eva_freq, char_freq = step2_eva_frequency()
    coverage = step3_logogram_coverage()
    contexts = step4_reverse_engineering()
    optimization = step5_glyph_brute_force()

    print()
    print("=" * 60)
    print("V15 SYNTHESIS")
    print("=" * 60)
    print(f"  Logogram coverage: {coverage['coverage_pct']}% of all tokens")
    print(f"  Logogram Perseus:  {coverage['covered_perseus_pct']}%")
    print(f"  Uncovered tokens:  {coverage['uncovered_unique']} unique types need phonetic decoding")
    print(f"  K&A baseline (4+): {optimization['baseline']['pct']}%")
    print(f"  Optimized (4+):    {optimization['optimized_total']['pct']}%")
    print(f"  Improvement:       +{optimization['optimized_total']['improvement_over_ka']}pp")
    print()

    # List changed glyphs
    changed = {g: d for g, d in optimization["optimized_glyphs"].items() if d["changed"]}
    if changed:
        print(f"  GLYPHS TO CHANGE ({len(changed)}):")
        for g, d in changed.items():
            print(f"    {g}: '{d['ka_value']}' → '{d['optimal_value']}'")
    else:
        print(f"  No glyph changes improve the score")

    print(f"\n  All results in {RESULTS}/")
