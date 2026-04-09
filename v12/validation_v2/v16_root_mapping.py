#!/usr/bin/env python3
"""
V16 — Root-level mapping.
Treat roots as units, not individual glyphs.
Map the top 100 roots to Latin by frequency, context, and co-occurrence.
"""
import json, sys, re, math
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

BASE = Path("d:/Github/Voynich")
DECODED_FILE = BASE / "v12/output/VOYNICH_DECODE_V12_INGREDIENTS.txt"
RESULTS = BASE / "v12/validation_v2/results"
LOGOGRAMS_PATH = BASE / "v12/rules/logograms.json"
PERSEUS_PATH = BASE / "data/latin_valid_wordset.json"
CORPUS_MED = BASE / "data/corpus_latin_medical_extended.txt"

# Known prefixes (from V15b confirmed)
PREFIXES = ["qok", "qot", "qo", "ok", "ot", "ol", "da", "ch", "sh", "d", "y", "r", "p", "l", "t", "f"]
# Sort longest first
PREFIXES.sort(key=len, reverse=True)

# Known prefix → Latin
PREFIX_LATIN = {
    "d": "in", "da": "in", "qo": "cum", "qok": "cum", "qot": "cum",
    "y": "in", "r": "re", "p": "per", "ol": "ex", "l": "ex",
    "ch": "eius", "ok": "", "ot": "", "sh": "",  # uncertain
}


def load_perseus():
    with open(PERSEUS_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return set(w.lower() for w in (data if isinstance(data, list) else data.keys()))


def load_logograms():
    with open(LOGOGRAMS_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    result = {}
    for eva, info in data.items():
        if isinstance(info, dict):
            latin = info.get("latin", "")
            if latin:
                result[eva.lower()] = latin.lower()
        elif isinstance(info, str):
            result[eva.lower()] = info.lower()
    return result


def load_corpus_words(max_n=500000):
    words = []
    with open(CORPUS_MED, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            for w in re.findall(r'[a-zA-Z]{2,}', line.lower()):
                words.append(w)
                if len(words) >= max_n:
                    return words
    return words


def parse_eva_lines():
    lines = []
    current_folio = None
    current_section = None
    with open(DECODED_FILE, 'r', encoding='utf-8') as f:
        for raw_line in f:
            m = re.match(r'\s*FOLIO (\S+) \| Section: (\S+)', raw_line)
            if m:
                current_folio = m.group(1)
                current_section = m.group(2)
                continue
            if 'EVA' in raw_line and ':' in raw_line:
                parts = raw_line.split(':')
                if 'EVA' in parts[0]:
                    words = [w.lower() for w in parts[1].strip().split() if w.isalpha()]
                    lines.append({"folio": current_folio, "section": current_section, "words": words})
    return lines


def strip_prefix(token):
    """Strip known prefix, return (prefix, root)."""
    for pfx in PREFIXES:
        if token.startswith(pfx) and len(token) > len(pfx):
            return pfx, token[len(pfx):]
    return "", token


# ══════════════════════════════════════════
# STEP 1: BUILD ROOT CORPUS
# ══════════════════════════════════════════
def step1_build_root_corpus():
    print("=" * 60)
    print("STEP 1: BUILD ROOT CORPUS")
    print("=" * 60)

    lines = parse_eva_lines()
    logograms = load_logograms()

    # Convert EVA text to root-level representation
    root_sequences = []  # list of (root_or_logogram, is_logogram, original_token)
    root_freq = Counter()
    all_tokens = []

    for line in lines:
        seq = []
        for token in line["words"]:
            if token in logograms:
                seq.append(("LOGO:" + logograms[token], True, token))
            else:
                pfx, root = strip_prefix(token)
                seq.append((root, False, token))
                root_freq[root] += 1
            all_tokens.append(token)
        root_sequences.append(seq)

    print(f"  Total tokens: {len(all_tokens)}")
    print(f"  Unique roots (non-logogram): {len(root_freq)}")

    # Top 50 roots
    print(f"\n  Top 50 roots by frequency:")
    top_roots = root_freq.most_common(50)
    cumulative = 0
    for i, (root, count) in enumerate(top_roots):
        cumulative += count
        cum_pct = 100 * cumulative / sum(root_freq.values())
        print(f"    {i+1:2d}. {root:12s} x{count:5d}  cumulative: {cum_pct:.1f}%")

    return root_sequences, root_freq, logograms


# ══════════════════════════════════════════
# STEP 2: FREQUENCY RANK MATCHING
# Compare root frequencies with Latin word frequencies
# ══════════════════════════════════════════
def step2_frequency_matching(root_freq):
    print()
    print("=" * 60)
    print("STEP 2: FREQUENCY RANK MATCHING")
    print("=" * 60)

    corpus = load_corpus_words()
    latin_freq = Counter(corpus)
    total_latin = len(corpus)
    total_roots = sum(root_freq.values())

    # Build frequency rank tables
    root_ranked = [(r, c, c/total_roots) for r, c in root_freq.most_common(50)]
    latin_ranked = [(w, c, c/total_latin) for w, c in latin_freq.most_common(200)]

    # For each top root, find Latin words with closest frequency
    print(f"  Root frequency → closest Latin word by frequency:")
    matches = []
    for root, rcount, rfreq in root_ranked[:30]:
        # Find closest Latin freq match
        best = None
        best_diff = float('inf')
        for lword, lcount, lfreq in latin_ranked:
            diff = abs(rfreq - lfreq)
            if diff < best_diff:
                best_diff = diff
                best = (lword, lcount, lfreq)

        ratio = rfreq / best[2] if best[2] > 0 else 0
        matches.append({
            "root": root, "root_freq": round(rfreq * 100, 3),
            "latin_match": best[0], "latin_freq": round(best[2] * 100, 3),
            "ratio": round(ratio, 2),
        })
        print(f"    {root:12s} ({rfreq*100:.2f}%) ↔ {best[0]:12s} ({best[2]*100:.2f}%)  ratio={ratio:.2f}")

    return matches


# ══════════════════════════════════════════
# STEP 3: CO-OCCURRENCE MATCHING
# What roots appear next to what logograms?
# Compare with Latin: what words appear next to "et", "in", "cum"?
# ══════════════════════════════════════════
def step3_cooccurrence(root_sequences, root_freq, logograms):
    print()
    print("=" * 60)
    print("STEP 3: CO-OCCURRENCE ANALYSIS")
    print("=" * 60)

    # For each root, what logograms appear before/after it?
    root_context = defaultdict(lambda: {"prev": Counter(), "next": Counter()})

    for seq in root_sequences:
        for i, (item, is_logo, original) in enumerate(seq):
            if not is_logo:  # it's a root
                root = item
                if i > 0 and seq[i-1][1]:  # prev is logogram
                    root_context[root]["prev"][seq[i-1][0]] += 1
                if i < len(seq) - 1 and seq[i+1][1]:  # next is logogram
                    root_context[root]["next"][seq[i+1][0]] += 1

    # Same analysis on Latin corpus
    corpus = load_corpus_words()
    # Common Latin "logograms" equivalent: et, in, cum, de, per, ex
    LATIN_FUNC = {"et", "in", "cum", "de", "per", "ex", "ad", "ab", "est"}

    latin_context = defaultdict(lambda: {"prev": Counter(), "next": Counter()})
    for i, w in enumerate(corpus):
        if w not in LATIN_FUNC:
            if i > 0 and corpus[i-1] in LATIN_FUNC:
                latin_context[w]["prev"][corpus[i-1]] += 1
            if i < len(corpus) - 1 and corpus[i+1] in LATIN_FUNC:
                latin_context[w]["next"][corpus[i+1]] += 1

    # Now match: for each top root, find the Latin word with most similar context
    print(f"  Context-based matching (top 20 roots):")
    context_matches = []

    for root, count in root_freq.most_common(20):
        ctx = root_context[root]
        prev_vec = ctx["prev"]
        next_vec = ctx["next"]

        # Build a simple context fingerprint
        # What % of time is preceded by "et"? by "in"? by "cum"?
        total_prev = sum(prev_vec.values()) or 1
        root_fingerprint = {
            "prev_et": prev_vec.get("LOGO:et", 0) / total_prev,
            "prev_in": prev_vec.get("LOGO:in", 0) / total_prev,
            "prev_eius": prev_vec.get("LOGO:eius", 0) / total_prev,
            "prev_eius et": prev_vec.get("LOGO:eius et", 0) / total_prev,
        }

        # Find Latin words with most similar context
        best_match = None
        best_score = -1
        for lword, lctx in latin_context.items():
            if latin_context[lword]["prev"].total() < 10:
                continue
            ltotal = sum(lctx["prev"].values()) or 1
            latin_fp = {
                "prev_et": lctx["prev"].get("et", 0) / ltotal,
                "prev_in": lctx["prev"].get("in", 0) / ltotal,
            }
            # Cosine-like similarity
            score = sum(root_fingerprint.get(k, 0) * latin_fp.get(k, 0) for k in latin_fp)
            if score > best_score:
                best_score = score
                best_match = lword

        prev_str = ', '.join(f"{k.replace('LOGO:','')}({v})" for k, v in prev_vec.most_common(3))
        context_matches.append({
            "root": root,
            "count": count,
            "prev_context": prev_vec.most_common(3),
            "best_latin_match": best_match,
            "match_score": round(best_score, 3),
        })
        print(f"    {root:12s} x{count:4d}  prev=[{prev_str}]  → {best_match or '?'}")

    return context_matches


# ══════════════════════════════════════════
# STEP 4: THE ROOT MAP
# Combine all evidence: logograms, frequency, context
# Build THE mapping table for the top 50 roots
# ══════════════════════════════════════════
def step4_build_root_map(root_freq, freq_matches, context_matches, logograms):
    print()
    print("=" * 60)
    print("STEP 4: THE ROOT MAP")
    print("=" * 60)

    perseus = load_perseus()

    # Index evidence
    freq_by_root = {m["root"]: m for m in freq_matches}
    ctx_by_root = {m["root"]: m for m in context_matches}

    # Also check: is the root itself a known logogram?
    root_map = []

    for root, count in root_freq.most_common(50):
        entry = {
            "root": root,
            "count": count,
            "evidence": [],
            "best_guess": None,
            "confidence": "low",
        }

        # Check if root is a logogram
        if root in logograms:
            entry["best_guess"] = logograms[root]
            entry["confidence"] = "confirmed"
            entry["evidence"].append(f"logogram: {logograms[root]}")

        # Frequency match
        fm = freq_by_root.get(root)
        if fm:
            entry["evidence"].append(f"freq_match: {fm['latin_match']} (ratio={fm['ratio']})")
            if not entry["best_guess"]:
                entry["best_guess"] = fm["latin_match"]

        # Context match
        cm = ctx_by_root.get(root)
        if cm and cm["best_latin_match"]:
            entry["evidence"].append(f"context: {cm['best_latin_match']} (score={cm['match_score']})")
            if not entry["best_guess"] or entry["confidence"] == "low":
                if cm["match_score"] > 0.01:
                    entry["best_guess"] = cm["best_latin_match"]
                    entry["confidence"] = "medium"

        # Check if best_guess is in Perseus
        if entry["best_guess"] and entry["best_guess"] in perseus:
            if entry["confidence"] != "confirmed":
                entry["confidence"] = "medium"
            entry["evidence"].append("perseus: YES")

        root_map.append(entry)

    # Print the map
    print(f"\n  {'ROOT':12s} {'COUNT':>6s} {'CONF':10s} {'BEST GUESS':15s} EVIDENCE")
    print(f"  {'-'*80}")
    for entry in root_map:
        ev = '; '.join(entry["evidence"][:2])
        conf_marker = {"confirmed": "***", "medium": " * ", "low": "   "}
        print(f"  {entry['root']:12s} {entry['count']:6d} {conf_marker.get(entry['confidence'], '   ')}"
              f"{entry['confidence']:10s} {entry['best_guess'] or '?':15s} {ev}")

    # Coverage: how much of the non-logogram corpus do the top 50 roots cover?
    total_roots_corpus = sum(root_freq.values())
    top50_coverage = sum(count for _, count in root_freq.most_common(50))
    print(f"\n  Top 50 roots cover {100*top50_coverage/total_roots_corpus:.1f}% of non-logogram tokens")

    confirmed = sum(1 for e in root_map if e["confidence"] == "confirmed")
    medium = sum(1 for e in root_map if e["confidence"] == "medium")
    low = sum(1 for e in root_map if e["confidence"] == "low")
    print(f"  Confidence: {confirmed} confirmed, {medium} medium, {low} low")

    results = {
        "root_map": root_map,
        "top50_coverage_pct": round(100 * top50_coverage / total_roots_corpus, 1),
        "confidence_counts": {"confirmed": confirmed, "medium": medium, "low": low},
    }

    with open(RESULTS / "v16_root_map.json", 'w') as f:
        json.dump(results, f, indent=2)
    return results


# ══════════════════════════════════════════
# STEP 5: TEST THE ROOT MAP
# Apply the root map to reconstruct Latin text
# Compare with v12 output
# ══════════════════════════════════════════
def step5_test_root_map(root_sequences, root_map_data):
    print()
    print("=" * 60)
    print("STEP 5: TEST THE ROOT MAP — RECONSTRUCT LATIN")
    print("=" * 60)

    perseus = load_perseus()
    root_map = {e["root"]: e["best_guess"] for e in root_map_data["root_map"] if e["best_guess"]}

    # Reconstruct Latin from root sequences
    total_words = 0
    perseus_hits = 0
    long_hits = 0  # 5+ letter hits
    total_long = 0
    reconstructed_lines = []

    for seq in root_sequences[:500]:  # first 500 lines
        latin_line = []
        for item, is_logo, original in seq:
            total_words += 1
            if is_logo:
                latin_word = item.replace("LOGO:", "")
                latin_line.append(latin_word)
                if latin_word in perseus:
                    perseus_hits += 1
                    if len(latin_word) >= 5:
                        long_hits += 1
                if len(latin_word) >= 5:
                    total_long += 1
            else:
                root = item
                pfx, _ = strip_prefix(original)
                latin_pfx = PREFIX_LATIN.get(pfx, "")

                if root in root_map:
                    latin_word = latin_pfx + " " + root_map[root] if latin_pfx else root_map[root]
                    latin_word = latin_word.strip()
                else:
                    latin_word = f"[{original}]"  # unknown

                latin_line.append(latin_word)
                # Check the root word (without prefix) against Perseus
                root_latin = root_map.get(root, "")
                if root_latin and root_latin in perseus:
                    perseus_hits += 1
                    if len(root_latin) >= 5:
                        long_hits += 1
                if root_latin and len(root_latin) >= 5:
                    total_long += 1

        reconstructed_lines.append(' '.join(latin_line))

    pct = 100 * perseus_hits / max(total_words, 1)
    long_pct = 100 * long_hits / max(total_long, 1)

    print(f"  Perseus match (all words):  {pct:.1f}% ({perseus_hits}/{total_words})")
    print(f"  Perseus match (5+ letters): {long_pct:.1f}% ({long_hits}/{total_long})")
    print(f"\n  Sample reconstructed lines:")
    for line in reconstructed_lines[:10]:
        if line.strip():
            print(f"    {line[:120]}")

    results = {
        "perseus_all_pct": round(pct, 1),
        "perseus_5plus_pct": round(long_pct, 1),
        "total_words": total_words,
        "perseus_hits": perseus_hits,
        "sample_lines": reconstructed_lines[:20],
    }

    with open(RESULTS / "v16_reconstruction.json", 'w') as f:
        json.dump(results, f, indent=2)
    return results


# ══════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════
if __name__ == "__main__":
    print("V16 ROOT-LEVEL MAPPING")
    print("=" * 60)

    root_sequences, root_freq, logograms = step1_build_root_corpus()
    freq_matches = step2_frequency_matching(root_freq)
    context_matches = step3_cooccurrence(root_sequences, root_freq, logograms)
    root_map_data = step4_build_root_map(root_freq, freq_matches, context_matches, logograms)
    reconstruction = step5_test_root_map(root_sequences, root_map_data)

    print()
    print("=" * 60)
    print("V16 FINAL")
    print("=" * 60)
    print(f"  Root map: {root_map_data['confidence_counts']}")
    print(f"  Top 50 roots cover: {root_map_data['top50_coverage_pct']}% of non-logogram tokens")
    print(f"  Reconstruction Perseus: {reconstruction['perseus_all_pct']}% all, "
          f"{reconstruction['perseus_5plus_pct']}% long")
