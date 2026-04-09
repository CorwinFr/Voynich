#!/usr/bin/env python3
"""
V15b — Deep attack on the key tokens.
daiin (847x), aiin (504x), qo- family, ch- family.
What are they? What do they DO in the text?
"""
import json, sys, re
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

BASE = Path("d:/Github/Voynich")
DECODED_FILE = BASE / "v12/output/VOYNICH_DECODE_V12_INGREDIENTS.txt"
RESULTS = BASE / "v12/validation_v2/results"
LOGOGRAMS_PATH = BASE / "v12/rules/logograms.json"
PERSEUS_PATH = BASE / "data/latin_valid_wordset.json"
CORPUS_MED = BASE / "data/corpus_latin_medical_extended.txt"


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


def parse_eva_lines():
    """Return list of (folio, section, line_num, [eva_words])."""
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
                    line_id = parts[0].strip().split()[-1] if parts[0].strip().split() else ""
                    words = [w.lower() for w in parts[1].strip().split() if w.isalpha()]
                    lines.append({
                        "folio": current_folio,
                        "section": current_section,
                        "line_id": line_id,
                        "words": words,
                    })
    return lines


def load_corpus_words(max_n=500000):
    words = []
    with open(CORPUS_MED, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            for w in re.findall(r'[a-zA-Z]{2,}', line.lower()):
                words.append(w)
                if len(words) >= max_n:
                    return words
    return words


# ══════════════════════════════════════════
# ANALYSIS 1: daiin EXHAUSTIVE PROFILE
# ══════════════════════════════════════════
def analyze_daiin():
    print("=" * 60)
    print("ANALYSIS 1: daiin — THE MOST FREQUENT WORD")
    print("=" * 60)

    lines = parse_eva_lines()
    logograms = load_logograms()

    # Find every occurrence with full context
    occurrences = []
    for line_data in lines:
        words = line_data["words"]
        for i, w in enumerate(words):
            if w == "daiin":
                prev2 = words[max(0,i-2):i]
                next2 = words[i+1:i+3]
                occurrences.append({
                    "folio": line_data["folio"],
                    "section": line_data["section"],
                    "position_in_line": i,
                    "line_length": len(words),
                    "prev2": prev2,
                    "next2": next2,
                })

    print(f"  Total occurrences: {len(occurrences)}")

    # Section distribution
    by_section = Counter(o["section"] for o in occurrences)
    print(f"\n  By section:")
    for sec, cnt in by_section.most_common():
        print(f"    {sec}: {cnt} ({100*cnt/len(occurrences):.1f}%)")

    # Position in line
    positions = [o["position_in_line"] for o in occurrences]
    line_lengths = [o["line_length"] for o in occurrences]
    relative_pos = [p/max(l,1) for p, l in zip(positions, line_lengths)]
    avg_pos = sum(positions) / len(positions)
    avg_rel = sum(relative_pos) / len(relative_pos)
    print(f"\n  Average position: {avg_pos:.1f} (absolute), {avg_rel:.2f} (relative)")

    # Is it more common at start, middle, end?
    starts = sum(1 for p in positions if p == 0)
    ends = sum(1 for p, l in zip(positions, line_lengths) if p == l - 1)
    middles = len(positions) - starts - ends
    print(f"  Position: start={starts} ({100*starts/len(positions):.1f}%), "
          f"middle={middles} ({100*middles/len(positions):.1f}%), "
          f"end={ends} ({100*ends/len(positions):.1f}%)")

    # Bigram context (what precedes and follows)
    prev_words = Counter()
    next_words = Counter()
    prev_bigrams = Counter()
    next_bigrams = Counter()
    for o in occurrences:
        if o["prev2"]:
            prev_words[o["prev2"][-1]] += 1
        if len(o["prev2"]) >= 2:
            prev_bigrams[tuple(o["prev2"][-2:])] += 1
        if o["next2"]:
            next_words[o["next2"][0]] += 1
        if len(o["next2"]) >= 2:
            next_bigrams[tuple(o["next2"][:2])] += 1

    print(f"\n  What comes BEFORE daiin:")
    for w, c in prev_words.most_common(10):
        latin = logograms.get(w, "?")
        print(f"    {w:15s} ({latin:10s}) x{c:4d}")

    print(f"\n  What comes AFTER daiin:")
    for w, c in next_words.most_common(10):
        latin = logograms.get(w, "?")
        print(f"    {w:15s} ({latin:10s}) x{c:4d}")

    # THE KEY QUESTION: does daiin behave like ONE Latin word?
    # Compare with corpus: what Latin word has similar frequency and context?
    corpus = load_corpus_words()
    corpus_freq = Counter(corpus)

    # daiin = 847/36983 = 2.3% of tokens
    # In Latin medical: what words are at 2-3%?
    total_corpus = len(corpus)
    target_freq = 0.023
    candidates = []
    for word, count in corpus_freq.most_common(100):
        freq = count / total_corpus
        if 0.015 < freq < 0.035:
            candidates.append((word, count, freq))

    print(f"\n  Latin medical words at similar frequency (2-3%):")
    for w, c, f in candidates[:10]:
        print(f"    {w:15s} x{c:5d} ({100*f:.1f}%)")

    # STRUCTURAL ANALYSIS: daiin decomposition
    print(f"\n  STRUCTURAL DECOMPOSITION:")
    print(f"    d + aiin  (prefix d=in + root aiin)")
    print(f"    da + iin  (prefix da=? + root iin)")
    print(f"    dai + in  (root dai + suffix in)")
    print(f"    d + a + i + i + n  (5 glyphs)")

    # Compare aiin vs daiin
    aiin_count = sum(1 for line in lines for w in line["words"] if w == "aiin")
    print(f"\n  aiin alone: {aiin_count} occurrences")
    print(f"  daiin:      {len(occurrences)} occurrences")
    print(f"  Ratio d-prefixed: {len(occurrences) / (len(occurrences) + aiin_count) * 100:.1f}%")

    # Other X+aiin words
    aiin_variants = Counter()
    for line in lines:
        for w in line["words"]:
            if w.endswith("aiin") and len(w) >= 5:
                prefix = w[:-4]
                aiin_variants[prefix + "+aiin"] += 1

    print(f"\n  All X+aiin variants:")
    for variant, count in aiin_variants.most_common(15):
        print(f"    {variant:15s} x{count:4d}")

    results = {
        "total": len(occurrences),
        "by_section": dict(by_section),
        "position": {"start": starts, "middle": middles, "end": ends},
        "avg_position": round(avg_pos, 1),
        "prev_top10": prev_words.most_common(10),
        "next_top10": next_words.most_common(10),
        "aiin_variants": aiin_variants.most_common(15),
        "similar_latin_freq": [(w, c) for w, c, f in candidates[:10]],
    }

    with open(RESULTS / "v15b_daiin_profile.json", 'w') as f:
        json.dump(results, f, indent=2)
    return results


# ══════════════════════════════════════════
# ANALYSIS 2: THE qo- FAMILY
# ══════════════════════════════════════════
def analyze_qo_family():
    print()
    print("=" * 60)
    print("ANALYSIS 2: THE qo- FAMILY")
    print("=" * 60)

    lines = parse_eva_lines()
    logograms = load_logograms()

    # Collect all qo- tokens
    qo_tokens = Counter()
    for line in lines:
        for w in line["words"]:
            if w.startswith("qo"):
                qo_tokens[w] += 1

    total_qo = sum(qo_tokens.values())
    print(f"  Total qo- tokens: {total_qo}")
    print(f"  Unique qo- types: {len(qo_tokens)}")

    # Decompose: what comes after qo?
    roots_after_qo = Counter()
    for token, count in qo_tokens.items():
        root = token[2:]  # strip "qo"
        roots_after_qo[root] += count

    print(f"\n  Top 20 roots after qo-:")
    for root, count in roots_after_qo.most_common(20):
        # Does this root appear WITHOUT qo- prefix?
        standalone = sum(1 for line in lines for w in line["words"]
                        if w == root)
        logo = logograms.get(root, "")
        logo_str = f"(={logo})" if logo else ""
        print(f"    qo+{root:12s} x{count:4d}  standalone '{root}': x{standalone:4d} {logo_str}")

    # Key insight: do qo- tokens appear in specific positions?
    positions = []
    for line in lines:
        for i, w in enumerate(line["words"]):
            if w.startswith("qo"):
                positions.append(i / max(len(line["words"]) - 1, 1))

    avg_pos = sum(positions) / max(len(positions), 1)
    print(f"\n  Average relative position of qo-: {avg_pos:.2f}")
    print(f"  (0.0 = start of line, 1.0 = end)")

    results = {
        "total_qo": total_qo,
        "unique_types": len(qo_tokens),
        "top_tokens": qo_tokens.most_common(20),
        "top_roots": roots_after_qo.most_common(20),
        "avg_position": round(avg_pos, 2),
    }

    with open(RESULTS / "v15b_qo_family.json", 'w') as f:
        json.dump(results, f, indent=2)
    return results


# ══════════════════════════════════════════
# ANALYSIS 3: THE ch- FAMILY
# ══════════════════════════════════════════
def analyze_ch_family():
    print()
    print("=" * 60)
    print("ANALYSIS 3: THE ch- FAMILY")
    print("=" * 60)

    lines = parse_eva_lines()
    logograms = load_logograms()

    ch_tokens = Counter()
    for line in lines:
        for w in line["words"]:
            if w.startswith("ch"):
                ch_tokens[w] += 1

    total_ch = sum(ch_tokens.values())
    print(f"  Total ch- tokens: {total_ch}")
    print(f"  Unique ch- types: {len(ch_tokens)}")

    roots_after_ch = Counter()
    for token, count in ch_tokens.items():
        root = token[2:]
        roots_after_ch[root] += count

    print(f"\n  Top 15 ch- tokens:")
    for token, count in ch_tokens.most_common(15):
        logo = logograms.get(token, "")
        print(f"    {token:15s} x{count:4d}  {f'(={logo})' if logo else ''}")

    # V14 showed ch→i is SUSPECT (removing it improves score)
    # What if ch is not a prefix but part of the glyph system?
    # Compare: how many ch- words are logograms vs need decoding?
    ch_logogram = sum(count for token, count in ch_tokens.items() if token in logograms)
    ch_unknown = total_ch - ch_logogram
    print(f"\n  ch- as logogram: {ch_logogram} ({100*ch_logogram/total_ch:.1f}%)")
    print(f"  ch- unknown:     {ch_unknown} ({100*ch_unknown/total_ch:.1f}%)")

    results = {
        "total_ch": total_ch,
        "unique_types": len(ch_tokens),
        "top_tokens": ch_tokens.most_common(20),
        "ch_logogram": ch_logogram,
        "ch_unknown": ch_unknown,
    }

    with open(RESULTS / "v15b_ch_family.json", 'w') as f:
        json.dump(results, f, indent=2)
    return results


# ══════════════════════════════════════════
# ANALYSIS 4: ROOT PATTERNS
# Strip all known prefixes (d, qo, ch, y, ol, ok, ot)
# and see what ROOT VOCABULARY remains
# ══════════════════════════════════════════
def analyze_root_vocabulary():
    print()
    print("=" * 60)
    print("ANALYSIS 4: ROOT VOCABULARY (after stripping prefixes)")
    print("=" * 60)

    lines = parse_eva_lines()
    logograms = load_logograms()
    perseus = load_perseus()

    PREFIXES = ["qok", "qot", "qo", "ok", "ot", "ol", "da", "ch", "sh"]
    # Ordered longest first to avoid partial matches

    roots = Counter()
    prefix_usage = Counter()

    all_tokens = []
    for line in lines:
        all_tokens.extend(line["words"])

    for token in all_tokens:
        if token in logograms:
            continue  # skip logograms, already handled

        # Try to strip a prefix
        stripped = False
        for pfx in PREFIXES:
            if token.startswith(pfx) and len(token) > len(pfx) + 1:
                root = token[len(pfx):]
                roots[root] += 1
                prefix_usage[pfx] += 1
                stripped = True
                break

        if not stripped:
            # No prefix, the whole thing is a root
            roots[token] += 1
            prefix_usage["(none)"] += 1

    print(f"  Prefix usage:")
    for pfx, cnt in prefix_usage.most_common():
        print(f"    {pfx:6s}: {cnt:5d}")

    print(f"\n  Unique roots: {len(roots)}")
    print(f"\n  Top 30 roots:")
    for root, count in roots.most_common(30):
        # Does this root appear with multiple prefixes?
        variants = []
        for pfx in PREFIXES + [""]:
            full = pfx + root
            full_count = sum(1 for t in all_tokens if t == full)
            if full_count > 0:
                variants.append(f"{pfx if pfx else '-'}({full_count})")
        variant_str = ', '.join(variants)
        print(f"    {root:12s} x{count:5d}  variants: {variant_str}")

    # THE KEY TEST: do the top roots look like Latin word endings?
    print(f"\n  Root ending analysis (do roots have Latin morphology?):")
    latin_endings = {"aiin": "-uram/-am", "ain": "-um/-am", "edy": "?",
                     "eey": "?", "ey": "?", "al": "-al/-alis",
                     "ol": "?", "ar": "-are/-aris", "or": "-or/-oris",
                     "ain": "-anem?"}
    for root, count in roots.most_common(20):
        ending = ""
        for end, meaning in latin_endings.items():
            if root.endswith(end):
                ending = meaning
                break
        print(f"    {root:12s} x{count:5d}  ending: {ending if ending else '?'}")

    results = {
        "prefix_usage": dict(prefix_usage),
        "unique_roots": len(roots),
        "top_roots": roots.most_common(50),
    }

    with open(RESULTS / "v15b_root_vocabulary.json", 'w') as f:
        json.dump(results, f, indent=2)
    return results


# ══════════════════════════════════════════
# ANALYSIS 5: THE -aiin MORPHEME
# If aiin = aquam, what are ALL the -aiin words?
# ══════════════════════════════════════════
def analyze_aiin_morpheme():
    print()
    print("=" * 60)
    print("ANALYSIS 5: THE -aiin MORPHEME")
    print("=" * 60)

    lines = parse_eva_lines()

    aiin_words = Counter()
    non_aiin = Counter()
    for line in lines:
        for w in line["words"]:
            if "aiin" in w:
                aiin_words[w] += 1
            else:
                non_aiin[w] += 1

    total_aiin = sum(aiin_words.values())
    total_all = total_aiin + sum(non_aiin.values())

    print(f"  Words containing 'aiin': {total_aiin} ({100*total_aiin/total_all:.1f}% of corpus)")
    print(f"  Unique types: {len(aiin_words)}")

    print(f"\n  All -aiin words by frequency:")
    for word, count in aiin_words.most_common(25):
        # Decompose
        if word.endswith("aiin"):
            prefix = word[:-4] if len(word) > 4 else "(bare)"
        elif "aiin" in word:
            idx = word.index("aiin")
            prefix = word[:idx]
        else:
            prefix = "?"
        print(f"    {word:15s} x{count:4d}  prefix='{prefix}'")

    # If aiin = some fixed Latin word (like "aquam"), then ALL
    # X+aiin should be PREPOSITION + aquam.
    # Let's check: are the prefixes consistent with known prepositions?
    prefix_freq = Counter()
    for word, count in aiin_words.items():
        if word.endswith("aiin") and len(word) > 4:
            pfx = word[:-4]
            prefix_freq[pfx] += count
        elif word == "aiin":
            prefix_freq["(bare)"] += count

    print(f"\n  Prefix distribution for X+aiin:")
    print(f"  (If aiin=aquam, these should be prepositions)")
    known_prefixes = {"d": "in", "s": "?", "k": "?", "ok": "qu?",
                      "qok": "cum", "sh": "ci?", "": "(none)",
                      "ot": "t?", "qo": "cum"}
    for pfx, count in prefix_freq.most_common(15):
        expected = known_prefixes.get(pfx, "?")
        print(f"    {pfx if pfx != '(bare)' else '(bare)':8s} x{count:4d}  "
              f"expected: {expected}")

    results = {
        "total_aiin_words": total_aiin,
        "pct_of_corpus": round(100 * total_aiin / total_all, 1),
        "unique_types": len(aiin_words),
        "all_words": aiin_words.most_common(30),
        "prefix_distribution": prefix_freq.most_common(15),
    }

    with open(RESULTS / "v15b_aiin_morpheme.json", 'w') as f:
        json.dump(results, f, indent=2)
    return results


# ══════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════
if __name__ == "__main__":
    print("V15b DEEP TOKEN ATTACK")
    print("=" * 60)

    r1 = analyze_daiin()
    r2 = analyze_qo_family()
    r3 = analyze_ch_family()
    r4 = analyze_root_vocabulary()
    r5 = analyze_aiin_morpheme()

    print()
    print("=" * 60)
    print("V15b KEY INSIGHTS")
    print("=" * 60)
    print(f"  daiin: {r1['total']}x, always surrounded by 'eius' and 'cies'")
    print(f"  qo- family: {r2['total_qo']} tokens, {r2['unique_types']} types")
    print(f"  ch- family: {r3['total_ch']} tokens")
    print(f"  Unique roots (after prefix stripping): {r4['unique_roots']}")
    print(f"  -aiin morpheme: {r5['pct_of_corpus']}% of corpus, {r5['unique_types']} types")
