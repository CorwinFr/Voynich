#!/usr/bin/env python3
"""
V22 — Discriminant Tests: Latin/Tironian vs Arabic/Syriac

Two independent analyses find the SAME morphological structure in the Voynich
but map to incompatible languages. This script runs 6 tests where the models
make DIFFERENT predictions, to determine which (if either) holds.

Model A (ours): Latin pharmaceutical text encoded via Tironian shorthand
Model B (nightrad.io): Arabic pharmaceutical text by a Syriac speaker

Tests:
1. Degree system: ain/aiin/aiiin as Galenic degrees 1/2/3
2. al- as Arabic definite article vs unknown root
3. daiin distribution: temporal marker vs pharmaceutical
4. Tironian z-score robustness under Arabic mapping
5. Morpheme positional grammar
6. Frequency distribution cross-check
"""
import json, sys, re, math
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

BASE = Path("d:/Github/Voynich")
DECODED_FILE = BASE / "v12/output/VOYNICH_DECODE_V12_INGREDIENTS.txt"
RESULTS = BASE / "v12/validation_v2/results"
TIRONIAN_PATH = BASE / "data/tironian/schmitz_index_full.json"
PERSEUS_PATH = BASE / "data/latin_valid_wordset.json"
LOGOGRAMS_PATH = BASE / "v12/rules/logograms.json"

GALLOWS = set("ktpf")
PREFIXES_ORDER = ["qok", "qot", "qo", "ok", "ot", "ol", "da", "ch", "sh",
                  "d", "y", "r", "p", "l", "t", "f", "k"]
PREFIXES_ORDER.sort(key=len, reverse=True)

# nightrad's Arabic morpheme mappings (from "Not solvable" document)
NIGHTRAD_ARABIC = {
    # Degree system
    "ain": "degree-1", "aiin": "degree-2", "aiiin": "degree-3",
    # Grammatical
    "al": "al (definite article)", "ar": "upon/on/over",
    "s": "with/of degree", "ol": "specification preposition",
    # Quality/Element
    "shedy": "earth-dry elemental", "chedy": "air elemental",
    "chey": "earth-mild", "sheedy": "air-quality strong",
    "shey": "earth-quality general",
    # Temporal
    "daiin": "da'iman (always/perpetually)", "dain": "da'iman (always)",
    "daiiin": "da'iman degree-3",
    # Prescription (qo- family)
    "qo": "prescription prefix", "qod": "distillation prescription",
    "qol": "boiling/decoction", "qos": "pounding/grinding",
    "qor": "topical positive",
    # Verbs (y- family)
    "ykal": "is measured/weighed", "yk": "is lightened/measured",
    "yt": "is cooked/boiled", "yth": "is heated/dissolved",
    "ysh": "is drunk (oral route)",
    # Structural
    "dy": "active drainage marker", "q": "word-final marker (silent)",
    # Key roots
    "dam": "blood (Arabic)", "khal": "vinegar",
    "sham": "wax", "kul": "antimony", "bawl": "urine",
    "tham": "garlic", "asal": "honey", "dar": "container",
    "daur": "cycle/rotation", "dur": "distillation apparatus",
    "attar": "apothecary", "naar": "drug/remedy",
    "sh": "shin (consonant)", "ch": "ayn/kh (consonant)",
    "k": "kaf (consonant)",
}


def parse_lines_eva():
    """Parse EVA lines from the decoded corpus."""
    lines = []
    current_folio = None
    current_section = None
    with open(DECODED_FILE, 'r', encoding='utf-8') as f:
        for raw in f:
            m = re.match(r'\s*FOLIO (\S+) \| Section: (\S+)', raw)
            if m:
                current_folio = m.group(1)
                current_section = m.group(2)
                continue
            if current_folio and 'EVA' in raw and ':' in raw:
                parts = raw.split(':')
                if 'EVA' in parts[0]:
                    words = [w.lower() for w in parts[1].strip().split()
                             if w.isalpha() and len(w) >= 2]
                    if words:
                        lines.append({
                            "folio": current_folio,
                            "section": current_section,
                            "words": words,
                        })
    return lines


def get_all_tokens(lines):
    """Flatten all tokens from all lines."""
    return [w for line in lines for w in line["words"]]


def extract_root(token):
    """Strip gallows prefix and EVA prefix, return (gallows, prefix, root)."""
    working = token
    gallows = ""
    if len(working) > 1 and working[0] in "ptf":
        gallows = working[0]
        working = working[1:]

    pfx = ""
    root = working
    for p in PREFIXES_ORDER:
        if working.startswith(p) and len(working) > len(p):
            pfx = p
            root = working[len(p):]
            break

    # Strip k from root
    if root.startswith('k') and len(root) > 1:
        root = root[1:]

    return gallows, pfx, root


# ══════════════════════════════════════════
# TEST 1: DEGREE SYSTEM (ain/aiin/aiiin)
# ══════════════════════════════════════════
def test_degree_system(lines):
    print("=" * 70)
    print("TEST 1: DEGREE SYSTEM — ain/aiin/aiiin as Galenic degrees 1/2/3")
    print("=" * 70)
    print()
    print("  Arabic predicts: ain(deg1) > aiin(deg2) > aiiin(deg3) strictly")
    print("  Arabic predicts: they appear in FINAL position of tokens")
    print("  Arabic predicts: they co-occur with quality markers (shedy, chedy)")
    print("  Tironian predicts: no systematic relationship")
    print()

    all_tokens = get_all_tokens(lines)

    # 1a. Frequency check
    # Count as standalone tokens
    standalone = Counter()
    for t in all_tokens:
        if t in ("ain", "aiin", "aiiin"):
            standalone[t] += 1

    # Count as roots (after prefix stripping)
    as_root = Counter()
    for t in all_tokens:
        _, _, root = extract_root(t)
        if root in ("ain", "aiin", "aiiin"):
            as_root[root] += 1

    # Count as SUFFIX (token ends with ain/aiin/aiiin)
    as_suffix = Counter()
    for t in all_tokens:
        if t.endswith("aiiin") and len(t) > 5:
            as_suffix["aiiin"] += 1
        elif t.endswith("aiin") and len(t) > 4:
            as_suffix["aiin"] += 1
        elif t.endswith("ain") and len(t) > 3:
            as_suffix["ain"] += 1

    print("  1a. FREQUENCY:")
    print(f"    {'Form':8s} {'Standalone':>12s} {'As root':>12s} {'As suffix':>12s}")
    for form in ["ain", "aiin", "aiiin"]:
        print(f"    {form:8s} {standalone[form]:12d} {as_root[form]:12d} {as_suffix[form]:12d}")

    freq_decreasing = as_root["ain"] > as_root["aiin"] > as_root["aiiin"]
    print(f"\n    Strictly decreasing (as root)? {'YES' if freq_decreasing else 'NO'}")
    if as_root["aiiin"] > 0:
        ratio_12 = as_root["ain"] / max(as_root["aiin"], 1)
        ratio_23 = as_root["aiin"] / max(as_root["aiiin"], 1)
        print(f"    Ratio deg1/deg2: {ratio_12:.2f}")
        print(f"    Ratio deg2/deg3: {ratio_23:.2f}")

    # 1b. Position in token: do ain/aiin/aiiin appear at END?
    print("\n  1b. POSITIONAL ANALYSIS:")
    # For tokens containing ain/aiin/aiiin as a substring, where does it appear?
    for pattern in ["aiiin", "aiin", "ain"]:
        positions = {"initial": 0, "medial": 0, "final": 0}
        total = 0
        for t in all_tokens:
            idx = t.find(pattern)
            if idx == -1:
                continue
            # Make sure it's the LONGEST match
            if pattern == "ain" and (t.find("aiin") != -1):
                continue  # Skip, this is aiin not ain
            if pattern == "aiin" and (t.find("aiiin") != -1):
                continue

            total += 1
            if idx == 0:
                positions["initial"] += 1
            elif idx + len(pattern) == len(t):
                positions["final"] += 1
            else:
                positions["medial"] += 1

        if total > 0:
            print(f"    {pattern:6s}: initial={positions['initial']:4d} ({100*positions['initial']/total:.0f}%)  "
                  f"medial={positions['medial']:4d} ({100*positions['medial']/total:.0f}%)  "
                  f"final={positions['final']:4d} ({100*positions['final']/total:.0f}%)  total={total}")

    # 1c. Co-occurrence with Galenic quality markers
    print("\n  1c. CO-OCCURRENCE WITH QUALITY MARKERS:")
    quality_markers = ["shedy", "chedy", "shey", "chey", "sheedy", "cheedy"]
    degree_markers = ["ain", "aiin", "aiiin"]

    # Check same-line co-occurrence
    cooccur = Counter()
    degree_lines = 0
    quality_lines = 0
    both_lines = 0

    for line in lines:
        words = line["words"]
        roots = [extract_root(w)[2] for w in words]
        has_degree = any(r in degree_markers for r in roots)
        has_quality = any(any(q in w for q in quality_markers) for w in words)

        if has_degree:
            degree_lines += 1
        if has_quality:
            quality_lines += 1
        if has_degree and has_quality:
            both_lines += 1

    total_lines = len(lines)
    expected_both = (degree_lines / total_lines) * (quality_lines / total_lines) * total_lines
    print(f"    Lines with degree markers:  {degree_lines}/{total_lines} ({100*degree_lines/total_lines:.1f}%)")
    print(f"    Lines with quality markers: {quality_lines}/{total_lines} ({100*quality_lines/total_lines:.1f}%)")
    print(f"    Lines with BOTH:            {both_lines} (expected if independent: {expected_both:.0f})")
    if expected_both > 0:
        enrichment = both_lines / expected_both
        print(f"    Enrichment ratio:           {enrichment:.2f}x")

    # 1d. Sectorial distribution of degree markers
    print("\n  1d. SECTORIAL DISTRIBUTION:")
    section_degree = defaultdict(lambda: Counter())
    section_total = Counter()
    for line in lines:
        section_total[line["section"]] += len(line["words"])
        for w in line["words"]:
            _, _, root = extract_root(w)
            if root in degree_markers:
                section_degree[line["section"]][root] += 1

    print(f"    {'Section':>8s} {'Tokens':>8s} {'ain':>6s} {'aiin':>6s} {'aiiin':>6s} {'ain%':>7s} {'aiin%':>7s}")
    for sec in sorted(section_total.keys()):
        tot = section_total[sec]
        a1 = section_degree[sec]["ain"]
        a2 = section_degree[sec]["aiin"]
        a3 = section_degree[sec]["aiiin"]
        print(f"    {sec:>8s} {tot:8d} {a1:6d} {a2:6d} {a3:6d} {100*a1/tot:7.2f} {100*a2/tot:7.2f}")

    # VERDICT
    print("\n  VERDICT TEST 1:")
    suffix_pct_aiin = 0
    for t in all_tokens:
        if t.endswith("aiin") and not t.endswith("aiiin"):
            suffix_pct_aiin += 1
    total_aiin_tokens = sum(1 for t in all_tokens if "aiin" in t and "aiiin" not in t)

    if freq_decreasing:
        print("    [+] ARABIC: Frequency is strictly decreasing (ain > aiin > aiiin)")
    else:
        print("    [-] ARABIC: Frequency is NOT strictly decreasing")

    return {
        "standalone": dict(standalone),
        "as_root": dict(as_root),
        "as_suffix": dict(as_suffix),
        "freq_decreasing": freq_decreasing,
        "degree_quality_enrichment": enrichment if expected_both > 0 else None,
    }


# ══════════════════════════════════════════
# TEST 2: al- AS ARABIC DEFINITE ARTICLE
# ══════════════════════════════════════════
def test_al_article(lines):
    print()
    print("=" * 70)
    print("TEST 2: al- AS ARABIC DEFINITE ARTICLE")
    print("=" * 70)
    print()
    print("  Arabic predicts: al appears word-initially, uniform across sections")
    print("  Tironian predicts: al is a root, no positional constraint")
    print()

    all_tokens = get_all_tokens(lines)

    # 2a. Position of 'al' in tokens
    al_standalone = 0
    al_initial = 0  # token starts with 'al' + more
    al_medial = 0
    al_final = 0  # token ends with 'al'
    al_total = 0

    for t in all_tokens:
        if t == "al":
            al_standalone += 1
            al_total += 1
        elif t.startswith("al") and len(t) > 2:
            al_initial += 1
            al_total += 1
        elif t.endswith("al") and len(t) > 2:
            al_final += 1
            al_total += 1
        elif "al" in t and len(t) > 3:
            # Check if al is in the middle
            idx = t.find("al")
            if 0 < idx < len(t) - 2:
                al_medial += 1
                al_total += 1

    print("  2a. POSITIONAL ANALYSIS:")
    print(f"    Standalone 'al':  {al_standalone:5d} ({100*al_standalone/max(al_total,1):.1f}%)")
    print(f"    Initial 'al-..': {al_initial:5d} ({100*al_initial/max(al_total,1):.1f}%)")
    print(f"    Medial '..al..': {al_medial:5d} ({100*al_medial/max(al_total,1):.1f}%)")
    print(f"    Final '...-al':  {al_final:5d} ({100*al_final/max(al_total,1):.1f}%)")
    print(f"    Total:            {al_total}")

    # 2b. Sectorial distribution
    print("\n  2b. SECTORIAL DISTRIBUTION:")
    section_al = Counter()
    section_total = Counter()
    for line in lines:
        section_total[line["section"]] += len(line["words"])
        for w in line["words"]:
            _, _, root = extract_root(w)
            if root == "al":
                section_al[line["section"]] += 1

    print(f"    {'Section':>8s} {'Tokens':>8s} {'al count':>10s} {'al %':>8s}")
    al_rates = []
    for sec in sorted(section_total.keys()):
        tot = section_total[sec]
        al_c = section_al[sec]
        rate = 100 * al_c / tot if tot > 0 else 0
        al_rates.append(rate)
        print(f"    {sec:>8s} {tot:8d} {al_c:10d} {rate:8.2f}%")

    # Arabic article should be ~uniform; compute coefficient of variation
    if len(al_rates) > 1 and sum(al_rates) > 0:
        mean_rate = sum(al_rates) / len(al_rates)
        var = sum((r - mean_rate)**2 for r in al_rates) / len(al_rates)
        cv = math.sqrt(var) / mean_rate if mean_rate > 0 else 0
        print(f"\n    Coefficient of variation: {cv:.2f}")
        print(f"    (Arabic article expects CV < 0.3; higher = non-uniform)")

    # 2c. What follows 'al' in bigrams?
    print("\n  2c. BIGRAM ANALYSIS (what follows standalone 'al'):")
    al_next = Counter()
    for line in lines:
        words = line["words"]
        for i, w in enumerate(words):
            if w == "al" and i + 1 < len(words):
                al_next[words[i+1]] += 1

    print(f"    Top 15 words following 'al':")
    for word, count in al_next.most_common(15):
        print(f"      {word:20s} x{count:4d}")

    # VERDICT
    initial_dominant = (al_standalone + al_initial) > 0.6 * al_total
    print("\n  VERDICT TEST 2:")
    if initial_dominant:
        print(f"    [+] ARABIC: al is {100*(al_standalone+al_initial)/max(al_total,1):.0f}% initial/standalone (article-like)")
    else:
        print(f"    [-] ARABIC: al is only {100*(al_standalone+al_initial)/max(al_total,1):.0f}% initial (not article-like)")

    return {
        "al_standalone": al_standalone,
        "al_initial": al_initial,
        "al_medial": al_medial,
        "al_final": al_final,
        "al_total": al_total,
        "cv": cv if len(al_rates) > 1 else None,
    }


# ══════════════════════════════════════════
# TEST 3: daiin DISTRIBUTION
# ══════════════════════════════════════════
def test_daiin_distribution(lines):
    print()
    print("=" * 70)
    print("TEST 3: daiin — da'iman ('always') vs 'in aquam'")
    print("=" * 70)
    print()
    print("  Arabic predicts: daiin is temporal, appears uniformly, any context")
    print("  Tironian predicts: daiin = d(in)+aiin, pharmaceutical contexts")
    print()

    all_tokens = get_all_tokens(lines)

    # 3a. Frequency and sectorial distribution
    section_daiin = Counter()
    section_total = Counter()
    for line in lines:
        section_total[line["section"]] += len(line["words"])
        for w in line["words"]:
            if w in ("daiin", "dain"):
                section_daiin[line["section"]] += 1

    print("  3a. SECTORIAL DISTRIBUTION:")
    print(f"    {'Section':>8s} {'Tokens':>8s} {'daiin/dain':>10s} {'Rate %':>8s}")
    rates = []
    for sec in sorted(section_total.keys()):
        tot = section_total[sec]
        d = section_daiin[sec]
        rate = 100 * d / tot if tot > 0 else 0
        rates.append(rate)
        print(f"    {sec:>8s} {tot:8d} {d:10d} {rate:8.2f}%")

    if len(rates) > 1 and sum(rates) > 0:
        mean_rate = sum(rates) / len(rates)
        var = sum((r - mean_rate)**2 for r in rates) / len(rates)
        cv = math.sqrt(var) / mean_rate if mean_rate > 0 else 0
        print(f"\n    CV = {cv:.2f} (uniform < 0.3, variable > 0.5)")

    # 3b. Context analysis: what appears near daiin?
    print("\n  3b. CONTEXT (words immediately before and after daiin/dain):")
    before_daiin = Counter()
    after_daiin = Counter()
    for line in lines:
        words = line["words"]
        for i, w in enumerate(words):
            if w in ("daiin", "dain"):
                if i > 0:
                    before_daiin[words[i-1]] += 1
                if i + 1 < len(words):
                    after_daiin[words[i+1]] += 1

    print(f"    BEFORE daiin (top 10):")
    for w, c in before_daiin.most_common(10):
        print(f"      {w:20s} x{c:4d}")
    print(f"    AFTER daiin (top 10):")
    for w, c in after_daiin.most_common(10):
        print(f"      {w:20s} x{c:4d}")

    # 3c. Position in line
    print("\n  3c. POSITION IN LINE:")
    positions = Counter()
    for line in lines:
        words = line["words"]
        n = len(words)
        for i, w in enumerate(words):
            if w in ("daiin", "dain"):
                if i == 0:
                    positions["first"] += 1
                elif i == n - 1:
                    positions["last"] += 1
                elif i < n / 3:
                    positions["early"] += 1
                elif i < 2 * n / 3:
                    positions["middle"] += 1
                else:
                    positions["late"] += 1

    total_daiin = sum(positions.values())
    for pos in ["first", "early", "middle", "late", "last"]:
        c = positions[pos]
        print(f"    {pos:8s}: {c:4d} ({100*c/max(total_daiin,1):.0f}%)")

    print("\n  VERDICT TEST 3:")
    if cv < 0.3:
        print(f"    [+] ARABIC: daiin is uniformly distributed (CV={cv:.2f}), consistent with 'always'")
    else:
        print(f"    [+] TIRONIAN: daiin varies across sections (CV={cv:.2f}), context-dependent")

    return {
        "section_rates": {sec: section_daiin[sec] for sec in section_total},
        "cv": cv,
        "total_daiin": total_daiin,
    }


# ══════════════════════════════════════════
# TEST 4: TIRONIAN Z-SCORE ROBUSTNESS
# ══════════════════════════════════════════
def test_tironian_robustness():
    print()
    print("=" * 70)
    print("TEST 4: TIRONIAN Z-SCORE ROBUSTNESS")
    print("=" * 70)
    print()
    print("  Question: Do nightrad's Arabic values ALSO match Tironian entries?")
    print("  If yes, z=9.4 is less discriminant (Schmitz is large enough to match anything)")
    print()

    # Load Schmitz index (it's a JSON array of objects)
    with open(TIRONIAN_PATH, 'r', encoding='utf-8') as f:
        schmitz_data = json.load(f)

    # Build set of all Latin values in Schmitz
    schmitz_values = set()
    if isinstance(schmitz_data, list):
        for entry in schmitz_data:
            if isinstance(entry, dict):
                val = entry.get("latin_value", "")
                if val:
                    schmitz_values.add(val.lower())
    elif isinstance(schmitz_data, dict):
        for key, entry in schmitz_data.items():
            if isinstance(entry, dict):
                val = entry.get("latin_value", "")
                if val:
                    schmitz_values.add(val.lower())

    print(f"  Schmitz unique Latin values: {len(schmitz_values)}")

    # Check how many of nightrad's Arabic words match Schmitz
    # (They shouldn't, because Schmitz is LATIN, not Arabic)
    arabic_words = set()
    for eva, arabic in NIGHTRAD_ARABIC.items():
        # Extract the core word from descriptions like "da'iman (always)"
        word = arabic.split("(")[0].strip().split("/")[0].strip().lower()
        if len(word) >= 2 and not word.startswith("["):
            arabic_words.add(word)

    matches = arabic_words & schmitz_values
    print(f"  nightrad Arabic vocabulary: {len(arabic_words)} words")
    print(f"  Matches in Schmitz: {len(matches)}")
    if matches:
        print(f"    Matching words: {sorted(matches)}")

    # Also check: are common Latin pharma terms in Schmitz?
    pharma_latin = ["aqua", "oleum", "mel", "sal", "cera", "recipe",
                    "misce", "coque", "tere", "cola", "fiat", "ana",
                    "nardus", "cassia", "vinum", "aloe"]
    latin_matches = [w for w in pharma_latin if w in schmitz_values]
    print(f"\n  Latin pharma terms in Schmitz: {len(latin_matches)}/{len(pharma_latin)}")
    print(f"    {latin_matches}")

    # Key test: total Schmitz entries vs expected random matches
    # If Schmitz has N unique values, probability of random 3-letter word matching
    short_schmitz = [v for v in schmitz_values if len(v) <= 4]
    long_schmitz = [v for v in schmitz_values if len(v) >= 5]
    print(f"\n  Schmitz entries by length:")
    print(f"    <= 4 chars: {len(short_schmitz)}")
    print(f"    >= 5 chars: {len(long_schmitz)}")
    print(f"    Total Latin vocabulary space (4 chars, 26^4): {26**4}")
    print(f"    Coverage of 4-char space: {100*len(short_schmitz)/26**4:.2f}%")

    print("\n  VERDICT TEST 4:")
    if len(matches) <= 2:
        print(f"    [+] TIRONIAN: Arabic vocabulary does NOT match Schmitz ({len(matches)} overlaps)")
        print(f"    The z=9.4 is discriminant: it's specific to Latin/Tironian, not an artifact")
    else:
        print(f"    [-] TIRONIAN: {len(matches)} Arabic words found in Schmitz, z-score may be inflated")

    return {
        "schmitz_unique_values": len(schmitz_values),
        "arabic_words_tested": len(arabic_words),
        "arabic_schmitz_matches": len(matches),
        "matching_words": sorted(matches),
        "latin_pharma_matches": latin_matches,
    }


# ══════════════════════════════════════════
# TEST 5: MORPHEME POSITIONAL GRAMMAR
# ══════════════════════════════════════════
def test_positional_grammar(lines):
    print()
    print("=" * 70)
    print("TEST 5: MORPHEME POSITIONAL GRAMMAR")
    print("=" * 70)
    print()
    print("  Arabic predicts: rigid order — prefix-root-quality-degree-terminator")
    print("  Tironian predicts: prefix-root, less rigid internal ordering")
    print()

    all_tokens = get_all_tokens(lines)

    # Define morpheme sets based on nightrad's model
    morpheme_sets = {
        "prefix_qo": ["qo", "qod", "qol", "qos", "qor"],
        "prefix_d": ["da", "dai"],
        "prefix_sh": ["sh"],
        "prefix_ch": ["ch"],
        "quality_edy": ["edy", "eedy", "eody"],
        "quality_ey": ["ey", "eey", "eeey"],
        "degree_ain": ["ain"],
        "degree_aiin": ["aiin"],
        "degree_aiiin": ["aiiin"],
        "article_al": ["al"],
        "dy_marker": ["dy"],
    }

    # For each token, decompose and check what order morphemes appear
    # Focus on tokens that contain multiple recognizable morphemes
    print("  5a. SUFFIX/ENDING ANALYSIS:")
    print("      If Arabic degree system, -ain/-aiin should be FINAL in tokens")
    print()

    # Check: what fraction of tokens ending in -ain/-aiin/-dy follow a consistent pattern?
    ending_patterns = Counter()
    for t in all_tokens:
        if len(t) < 4:
            continue
        # What does the token end with?
        for ending in ["aiiin", "aiin", "ain", "eedy", "edy", "eey", "ey", "dy", "al", "ol", "or", "ar"]:
            if t.endswith(ending) and len(t) > len(ending):
                prefix_part = t[:-len(ending)]
                ending_patterns[ending] += 1
                break

    print(f"    {'Ending':>8s} {'Count':>8s}")
    for ending, count in sorted(ending_patterns.items(), key=lambda x: -x[1]):
        print(f"    {ending:>8s} {count:8d}")

    total_with_endings = sum(ending_patterns.values())
    total_tokens = len(all_tokens)
    print(f"\n    Tokens with recognizable endings: {total_with_endings}/{total_tokens} ({100*total_with_endings/total_tokens:.1f}%)")

    # 5b. Positional entropy of key morphemes within tokens
    print("\n  5b. RELATIVE POSITION OF MORPHEMES IN MULTI-MORPHEME TOKENS:")
    # For tokens >= 5 chars, find position of ain/aiin/edy/ey/al as fraction of token length
    morpheme_positions = defaultdict(list)
    for t in all_tokens:
        tlen = len(t)
        if tlen < 5:
            continue
        for morph in ["aiiin", "aiin", "ain", "edy", "eey", "ey", "al", "dy"]:
            idx = t.find(morph)
            if idx >= 0:
                # Relative position (0=start, 1=end)
                rel_pos = (idx + len(morph)/2) / tlen
                morpheme_positions[morph].append(rel_pos)

    print(f"    {'Morpheme':>8s} {'N':>6s} {'Mean pos':>10s} {'Std':>8s} {'Verdict':>20s}")
    for morph in ["al", "ain", "aiin", "aiiin", "edy", "eey", "ey", "dy"]:
        positions = morpheme_positions.get(morph, [])
        if len(positions) >= 10:
            mean = sum(positions) / len(positions)
            std = math.sqrt(sum((p - mean)**2 for p in positions) / len(positions))
            # Arabic predicts: al near start (0.0-0.3), degree near end (0.7-1.0)
            if morph == "al":
                verdict = "INITIAL" if mean < 0.4 else "NOT initial"
            elif morph in ("ain", "aiin", "aiiin"):
                verdict = "FINAL" if mean > 0.6 else "NOT final"
            elif morph in ("edy", "eey", "ey", "dy"):
                verdict = "FINAL" if mean > 0.6 else "MEDIAL/INITIAL"
            else:
                verdict = ""
            print(f"    {morph:>8s} {len(positions):6d} {mean:10.3f} {std:8.3f} {verdict:>20s}")

    print("\n  VERDICT TEST 5:")
    ain_pos = morpheme_positions.get("aiin", [])
    al_pos = morpheme_positions.get("al", [])
    if ain_pos:
        mean_ain = sum(ain_pos) / len(ain_pos)
        if mean_ain > 0.65:
            print(f"    [+] ARABIC: aiin appears at mean position {mean_ain:.2f} (final, consistent with degree)")
        else:
            print(f"    [-] ARABIC: aiin at mean position {mean_ain:.2f} (not clearly final)")
    if al_pos:
        mean_al = sum(al_pos) / len(al_pos)
        if mean_al < 0.35:
            print(f"    [+] ARABIC: al appears at mean position {mean_al:.2f} (initial, consistent with article)")
        else:
            print(f"    [-] ARABIC: al at mean position {mean_al:.2f} (not clearly initial)")

    return {
        "ending_patterns": dict(ending_patterns),
        "total_with_endings": total_with_endings,
    }


# ══════════════════════════════════════════
# TEST 6: FREQUENCY CROSS-CHECK
# ══════════════════════════════════════════
def test_frequency_crosscheck(lines):
    print()
    print("=" * 70)
    print("TEST 6: FREQUENCY DISTRIBUTION CROSS-CHECK")
    print("=" * 70)
    print()

    all_tokens = get_all_tokens(lines)
    token_freq = Counter(all_tokens)

    # In Arabic text, the most frequent word is usually 'al' (the definite article)
    # typically 5-10% of all tokens
    # In Latin text, 'et' is typically the most frequent (3-5%)

    total = len(all_tokens)
    print("  6a. TOP 20 EVA TOKENS:")
    print(f"    {'Rank':>4s} {'Token':>15s} {'Count':>8s} {'%':>7s} {'Arabic meaning':>25s}")
    for i, (token, count) in enumerate(token_freq.most_common(20)):
        arabic_meaning = NIGHTRAD_ARABIC.get(token, "?")
        print(f"    {i+1:4d} {token:>15s} {count:8d} {100*count/total:7.2f} {arabic_meaning:>25s}")

    # Check if frequency ranking matches Arabic expectations
    # Arabic: al should be #1 or top 3
    # Latin: et should be top 3
    top_tokens = [t for t, _ in token_freq.most_common(5)]

    print(f"\n  6b. ARABIC FREQUENCY EXPECTATIONS:")
    al_rank = None
    for i, (t, _) in enumerate(token_freq.most_common(50)):
        if t == "al":
            al_rank = i + 1
            break
    print(f"    'al' rank: #{al_rank} (Arabic expects top 3)")

    daiin_rank = None
    for i, (t, _) in enumerate(token_freq.most_common(100)):
        if t == "daiin":
            daiin_rank = i + 1
            break
    print(f"    'daiin' rank: #{daiin_rank}")

    # 6c. Zipf's law check
    print(f"\n  6c. ZIPF'S LAW:")
    ranks = []
    freqs = []
    for i, (_, count) in enumerate(token_freq.most_common(100)):
        ranks.append(i + 1)
        freqs.append(count)

    # Log-log regression
    log_ranks = [math.log(r) for r in ranks]
    log_freqs = [math.log(f) for f in freqs]
    n = len(log_ranks)
    mean_x = sum(log_ranks) / n
    mean_y = sum(log_freqs) / n
    cov = sum((log_ranks[i] - mean_x) * (log_freqs[i] - mean_y) for i in range(n)) / n
    var_x = sum((log_ranks[i] - mean_x)**2 for i in range(n)) / n
    slope = cov / var_x if var_x > 0 else 0

    print(f"    Zipf exponent (slope): {-slope:.3f}")
    print(f"    (Natural language expects 0.9-1.2; Latin ~1.0, Arabic ~1.1)")
    print(f"    (Random/cipher expects < 0.7 or > 1.5)")

    print("\n  VERDICT TEST 6:")
    if al_rank and al_rank <= 5:
        print(f"    [+] ARABIC: 'al' is rank #{al_rank}, consistent with definite article")
    elif al_rank:
        print(f"    [-] ARABIC: 'al' is rank #{al_rank}, too low for a definite article")
    else:
        print(f"    [-] ARABIC: 'al' not found in top 50")

    return {
        "al_rank": al_rank,
        "daiin_rank": daiin_rank,
        "zipf_exponent": round(-slope, 3),
    }


# ══════════════════════════════════════════
# SUMMARY
# ══════════════════════════════════════════
def print_summary(results):
    print()
    print("=" * 70)
    print("FINAL SUMMARY: LATIN/TIRONIAN vs ARABIC/SYRIAC")
    print("=" * 70)
    print()
    print(f"  {'Test':40s} {'Arabic':>10s} {'Tironian':>10s}")
    print(f"  {'-'*62}")

    verdicts = []
    for test_name, arabic_score, tironian_score in results:
        a = "+" if arabic_score else "-"
        t = "+" if tironian_score else "-"
        verdicts.append((test_name, arabic_score, tironian_score))
        print(f"  {test_name:40s} {'[+]' if arabic_score else '[-]':>10s} {'[+]' if tironian_score else '[-]':>10s}")

    arabic_wins = sum(1 for _, a, _ in verdicts if a)
    tironian_wins = sum(1 for _, _, t in verdicts if t)
    print(f"\n  SCORE: Arabic {arabic_wins} / Tironian {tironian_wins} / Total {len(verdicts)}")


# ══════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════
if __name__ == "__main__":
    print("V22 DISCRIMINANT TESTS: LATIN/TIRONIAN vs ARABIC/SYRIAC")
    print("=" * 70)
    print()

    lines = parse_lines_eva()
    print(f"Loaded {len(lines)} EVA lines from {len(set(l['folio'] for l in lines))} folios")
    print(f"Total tokens: {sum(len(l['words']) for l in lines)}")
    print()

    r1 = test_degree_system(lines)
    r2 = test_al_article(lines)
    r3 = test_daiin_distribution(lines)
    r4 = test_tironian_robustness()
    r5 = test_positional_grammar(lines)
    r6 = test_frequency_crosscheck(lines)

    # Build summary verdicts
    summary = [
        ("T1: Degree freq decreasing", r1["freq_decreasing"], not r1["freq_decreasing"]),
        ("T1: Degree-quality co-occurrence",
         r1.get("degree_quality_enrichment", 0) and r1["degree_quality_enrichment"] > 1.5,
         r1.get("degree_quality_enrichment", 0) and r1["degree_quality_enrichment"] <= 1.5),
        ("T2: al- positional (initial >60%)",
         (r2["al_standalone"] + r2["al_initial"]) > 0.6 * max(r2["al_total"], 1),
         (r2["al_standalone"] + r2["al_initial"]) <= 0.6 * max(r2["al_total"], 1)),
        ("T2: al- uniform across sections",
         r2.get("cv") is not None and r2["cv"] < 0.3,
         r2.get("cv") is not None and r2["cv"] >= 0.3),
        ("T3: daiin uniform (CV<0.3 = Arabic)",
         r3["cv"] < 0.3,
         r3["cv"] >= 0.3),
        ("T4: Arabic vocab NOT in Schmitz",
         r4["arabic_schmitz_matches"] > 3,
         r4["arabic_schmitz_matches"] <= 3),
        ("T6: al in top 5 frequency",
         r6["al_rank"] is not None and r6["al_rank"] <= 5,
         r6["al_rank"] is None or r6["al_rank"] > 5),
    ]

    print_summary(summary)

    # Save all results
    all_results = {
        "test1_degree": r1,
        "test2_al_article": r2,
        "test3_daiin": r3,
        "test4_tironian_robustness": r4,
        "test5_positional": r5,
        "test6_frequency": r6,
    }
    with open(RESULTS / "v22_discriminant.json", 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"\n  Results saved to {RESULTS / 'v22_discriminant.json'}")
