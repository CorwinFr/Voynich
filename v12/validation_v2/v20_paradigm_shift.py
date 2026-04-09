#!/usr/bin/env python3
"""
V20 — Paradigm shift tests.
1. sh vs ch distribution by section (procedural vs cipher?)
2. Tironian baseline (are 51 matches significant?)
3. edy→eedy→ain processing cycle
4. Gallows stripping impact
"""
import json, sys, re, random, math
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

BASE = Path("d:/Github/Voynich")
DECODED_FILE = BASE / "v12/output/VOYNICH_DECODE_V12_INGREDIENTS.txt"
RESULTS = BASE / "v12/validation_v2/results"
TIRONIAN_PATH = BASE / "data/tironian/schmitz_index_full.json"
GLYPHS_PATH = BASE / "v12/rules/glyphs.json"
PERSEUS_PATH = BASE / "data/latin_valid_wordset.json"
LOGOGRAMS_PATH = BASE / "v12/rules/logograms.json"


def load_perseus():
    with open(PERSEUS_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return set(w.lower() for w in (data if isinstance(data, list) else data.keys()))


def load_logograms():
    with open(LOGOGRAMS_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    result = {}
    for eva, info in data.items():
        if isinstance(info, dict) and info.get("latin"):
            result[eva.lower()] = info["latin"].lower()
        elif isinstance(info, str):
            result[eva.lower()] = info.lower()
    return result


def parse_folios_eva():
    """Return dict: folio_id -> {section, tokens: [eva_words]}"""
    folios = {}
    current = None
    with open(DECODED_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            m = re.match(r'\s*FOLIO (\S+) \| Section: (\S+)', line)
            if m:
                current = m.group(1)
                folios[current] = {"section": m.group(2), "tokens": []}
                continue
            if current and 'EVA' in line and ':' in line:
                parts = line.split(':')
                if 'EVA' in parts[0]:
                    for w in parts[1].strip().split():
                        if w.isalpha() and len(w) >= 2:
                            folios[current]["tokens"].append(w.lower())
    return folios


def parse_lines_eva():
    """Return list of {folio, section, words: [eva]}"""
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
                    words = [w.lower() for w in parts[1].strip().split() if w.isalpha() and len(w) >= 2]
                    if words:
                        lines.append({"folio": current_folio, "section": current_section, "words": words})
    return lines


# ══════════════════════════════════════════
# TEST 1: sh vs ch DISTRIBUTION BY SECTION
# ══════════════════════════════════════════
def test_sh_ch_distribution():
    print("=" * 60)
    print("TEST 1: sh vs ch DISTRIBUTION BY SECTION")
    print("If procedural: H should have more sh (raw), S/P more ch (processed)")
    print("If cipher: uniform distribution")
    print("=" * 60)

    folios = parse_folios_eva()

    section_stats = defaultdict(lambda: {"sh": 0, "ch": 0, "total": 0, "sh_words": Counter(), "ch_words": Counter()})

    for fid, data in folios.items():
        sec = data["section"]
        for token in data["tokens"]:
            section_stats[sec]["total"] += 1
            if token.startswith("sh"):
                section_stats[sec]["sh"] += 1
                section_stats[sec]["sh_words"][token] += 1
            elif token.startswith("ch"):
                section_stats[sec]["ch"] += 1
                section_stats[sec]["ch_words"][token] += 1

    print(f"\n  {'Section':8s} {'sh-':>6s} {'ch-':>6s} {'Total':>7s} {'sh%':>6s} {'ch%':>6s} {'sh/ch':>7s}")
    print(f"  {'-'*50}")

    results = {}
    for sec in sorted(section_stats.keys()):
        s = section_stats[sec]
        sh_pct = 100 * s["sh"] / max(s["total"], 1)
        ch_pct = 100 * s["ch"] / max(s["total"], 1)
        ratio = s["sh"] / max(s["ch"], 1)
        results[sec] = {
            "sh": s["sh"], "ch": s["ch"], "total": s["total"],
            "sh_pct": round(sh_pct, 1), "ch_pct": round(ch_pct, 1),
            "sh_ch_ratio": round(ratio, 3),
        }
        print(f"  {sec:8s} {s['sh']:6d} {s['ch']:6d} {s['total']:7d} {sh_pct:5.1f}% {ch_pct:5.1f}% {ratio:6.3f}")

    # Chi-squared test: is the sh/ch ratio significantly different across sections?
    total_sh = sum(s["sh"] for s in section_stats.values())
    total_ch = sum(s["ch"] for s in section_stats.values())
    total_all = sum(s["total"] for s in section_stats.values())
    expected_sh_rate = total_sh / total_all
    expected_ch_rate = total_ch / total_all

    chi2_sh = 0
    chi2_ch = 0
    for sec, s in section_stats.items():
        exp_sh = expected_sh_rate * s["total"]
        exp_ch = expected_ch_rate * s["total"]
        if exp_sh > 0:
            chi2_sh += (s["sh"] - exp_sh) ** 2 / exp_sh
        if exp_ch > 0:
            chi2_ch += (s["ch"] - exp_ch) ** 2 / exp_ch

    df = len(section_stats) - 1
    print(f"\n  Chi-squared (sh distribution): {chi2_sh:.1f} (df={df})")
    print(f"  Chi-squared (ch distribution): {chi2_ch:.1f} (df={df})")
    print(f"  Critical value (p<0.01, df={df}): ~18.5")

    verdict_sh = "SIGNIFICANT" if chi2_sh > 18.5 else "NOT significant"
    verdict_ch = "SIGNIFICANT" if chi2_ch > 18.5 else "NOT significant"
    print(f"  sh variation across sections: {verdict_sh}")
    print(f"  ch variation across sections: {verdict_ch}")

    # KEY: which sections have highest and lowest sh/ch ratio?
    ratios = [(sec, r["sh_ch_ratio"]) for sec, r in results.items() if r["total"] > 100]
    ratios.sort(key=lambda x: -x[1])
    print(f"\n  sh/ch ratio ranking (higher = more raw material):")
    for sec, ratio in ratios:
        bar = "#" * int(ratio * 10)
        print(f"    {sec:4s}: {ratio:.3f} {bar}")

    results["chi2_sh"] = round(chi2_sh, 1)
    results["chi2_ch"] = round(chi2_ch, 1)
    results["verdict_sh"] = verdict_sh
    results["verdict_ch"] = verdict_ch

    with open(RESULTS / "v20_sh_ch_distribution.json", 'w') as f:
        json.dump(results, f, indent=2)
    return results


# ══════════════════════════════════════════
# TEST 2: TIRONIAN BASELINE
# ══════════════════════════════════════════
def test_tironian_baseline():
    print()
    print("=" * 60)
    print("TEST 2: TIRONIAN BASELINE — Are 51 matches significant?")
    print("=" * 60)

    with open(TIRONIAN_PATH, 'r', encoding='utf-8') as f:
        schmitz = json.load(f)

    tironian_latin = set()
    for entry in schmitz:
        if isinstance(entry, dict) and "latin_value" in entry:
            tironian_latin.add(entry["latin_value"].lower().strip())

    print(f"  Tironian unique Latin values: {len(tironian_latin)}")

    # Our actual roots decoded via K&A primary
    with open(GLYPHS_PATH, 'r', encoding='utf-8') as f:
        glyphs_raw = json.load(f)
    ka_primary = {}
    for g, info in glyphs_raw.items():
        if g.startswith('_'):
            continue
        if isinstance(info, dict) and "phonemes" in info:
            p = info["phonemes"]
            if p:
                ka_primary[g] = str(p[0])

    logograms = load_logograms()
    folios = parse_folios_eva()
    all_tokens = []
    for fid, data in folios.items():
        all_tokens.extend(data["tokens"])

    # Get unique roots
    PREFIXES = ["qok", "qot", "qo", "ok", "ot", "ol", "da", "ch", "sh",
                "d", "y", "r", "p", "l", "t", "f", "k"]
    PREFIXES.sort(key=len, reverse=True)

    roots = set()
    for t in all_tokens:
        if t not in logograms:
            for pfx in PREFIXES:
                if t.startswith(pfx) and len(t) > len(pfx):
                    roots.add(t[len(pfx):])
                    break
            else:
                roots.add(t)

    top_200_roots = Counter()
    for t in all_tokens:
        if t not in logograms:
            for pfx in PREFIXES:
                if t.startswith(pfx) and len(t) > len(pfx):
                    top_200_roots[t[len(pfx):]] += 1
                    break
            else:
                top_200_roots[t] += 1
    top_200 = [r for r, _ in top_200_roots.most_common(200)]

    # Decode top 200 roots with K&A primary
    def raw_decode(eva_w):
        result = ""
        i = 0
        while i < len(eva_w):
            matched = False
            for gl in range(min(3, len(eva_w) - i), 0, -1):
                chunk = eva_w[i:i+gl]
                if chunk in ka_primary:
                    result += ka_primary[chunk]
                    i += gl
                    matched = True
                    break
            if not matched:
                result += eva_w[i]
                i += 1
        return result.lower()

    # Count actual matches
    actual_matches = 0
    for root in top_200:
        decoded = raw_decode(root)
        if decoded in tironian_latin:
            actual_matches += 1
        elif root in logograms and logograms[root] in tironian_latin:
            actual_matches += 1

    print(f"  Actual Tironian matches (top 200 roots): {actual_matches}")

    # Random baseline: generate random "roots" of same length distribution
    root_lengths = [len(r) for r in top_200]
    eva_chars = list("oehyacdiklrstqnpmfgx")

    N_TRIALS = 500
    random_matches = []
    for trial in range(N_TRIALS):
        random_roots = []
        for length in root_lengths:
            rand_root = ''.join(random.choices(eva_chars, k=length))
            random_roots.append(rand_root)

        matches = 0
        for root in random_roots:
            decoded = raw_decode(root)
            if decoded in tironian_latin:
                matches += 1
        random_matches.append(matches)

    avg_random = sum(random_matches) / len(random_matches)
    std_random = (sum((x - avg_random)**2 for x in random_matches) / len(random_matches)) ** 0.5
    max_random = max(random_matches)
    z_score = (actual_matches - avg_random) / max(std_random, 0.01)

    print(f"  Random baseline: {avg_random:.1f} +/- {std_random:.1f} (max: {max_random})")
    print(f"  Z-score: {z_score:.1f}")

    if z_score > 3:
        verdict = "HIGHLY SIGNIFICANT (z > 3)"
    elif z_score > 2:
        verdict = "SIGNIFICANT (z > 2)"
    elif z_score > 1.5:
        verdict = "MARGINALLY SIGNIFICANT"
    else:
        verdict = "NOT SIGNIFICANT"

    print(f"  VERDICT: {verdict}")

    results = {
        "actual_matches": actual_matches,
        "random_avg": round(avg_random, 1),
        "random_std": round(std_random, 1),
        "random_max": max_random,
        "z_score": round(z_score, 1),
        "n_trials": N_TRIALS,
        "verdict": verdict,
    }

    with open(RESULTS / "v20_tironian_baseline.json", 'w') as f:
        json.dump(results, f, indent=2)
    return results


# ══════════════════════════════════════════
# TEST 3: PROCESSING CYCLE edy→eedy→ain
# ══════════════════════════════════════════
def test_processing_cycle():
    print()
    print("=" * 60)
    print("TEST 3: PROCESSING CYCLE edy -> eedy -> ain")
    print("=" * 60)

    lines = parse_lines_eva()

    # For each line, check if roots appear in cycle order
    CYCLE_ROOTS = {
        "edy": 1,   # step 1: basic processing
        "eedy": 2,  # step 2: refinement
        "ain": 3,   # step 3: result/output
    }

    # Also check variant endings
    CYCLE_VARIANTS = {
        "edy": 1, "shedy": 1, "chedy": 1, "okedy": 1, "otedy": 1,
        "eedy": 2, "sheedy": 2, "cheedy": 2, "okeedy": 2, "oteedy": 2, "keedy": 2,
        "ain": 3, "dain": 3, "kain": 3, "shain": 3, "chain": 3, "okain": 3,
        "aiin": 3, "daiin": 3, "kaiin": 3, "okaiin": 3,
    }

    # Count ordered vs disordered sequences
    ordered = 0  # step N followed by step N+1 or N+2
    reverse = 0  # step N followed by step N-1 or N-2
    same = 0     # same step repeated
    total_transitions = 0

    # Per-line analysis
    cycle_lines = 0
    total_lines = 0

    for line_data in lines:
        steps_in_line = []
        for token in line_data["words"]:
            # Check if token ends with a cycle root
            for pattern, step in sorted(CYCLE_VARIANTS.items(), key=lambda x: -len(x[0])):
                if token.endswith(pattern) or token == pattern:
                    steps_in_line.append(step)
                    break

        if len(steps_in_line) >= 2:
            total_lines += 1
            has_order = False
            for i in range(len(steps_in_line) - 1):
                a, b = steps_in_line[i], steps_in_line[i+1]
                total_transitions += 1
                if b > a:
                    ordered += 1
                    has_order = True
                elif b < a:
                    reverse += 1
                else:
                    same += 1
            if has_order:
                cycle_lines += 1

    # Expected by chance: if steps are random, ordered/reverse should be ~equal
    expected_ordered = total_transitions / 3  # roughly

    print(f"  Lines with 2+ cycle markers: {total_lines}")
    print(f"  Lines with at least one ordered transition: {cycle_lines}")
    print(f"  Total transitions: {total_transitions}")
    print(f"  Ordered (step N -> N+1/N+2): {ordered} ({100*ordered/max(total_transitions,1):.1f}%)")
    print(f"  Reverse (step N -> N-1/N-2): {reverse} ({100*reverse/max(total_transitions,1):.1f}%)")
    print(f"  Same step repeated:          {same} ({100*same/max(total_transitions,1):.1f}%)")

    if total_transitions > 0:
        ratio = ordered / max(reverse, 1)
        print(f"  Ordered/Reverse ratio: {ratio:.2f} (1.0 = random, >1.5 = cycle)")
        verdict = "CYCLE DETECTED" if ratio > 1.3 else "NO CLEAR CYCLE" if ratio > 0.8 else "REVERSE CYCLE?"
    else:
        ratio = 0
        verdict = "INSUFFICIENT DATA"

    print(f"  VERDICT: {verdict}")

    # Section breakdown
    section_cycles = defaultdict(lambda: {"ordered": 0, "reverse": 0, "same": 0})
    for line_data in lines:
        sec = line_data["section"]
        steps = []
        for token in line_data["words"]:
            for pattern, step in sorted(CYCLE_VARIANTS.items(), key=lambda x: -len(x[0])):
                if token.endswith(pattern) or token == pattern:
                    steps.append(step)
                    break
        for i in range(len(steps) - 1):
            if steps[i+1] > steps[i]:
                section_cycles[sec]["ordered"] += 1
            elif steps[i+1] < steps[i]:
                section_cycles[sec]["reverse"] += 1
            else:
                section_cycles[sec]["same"] += 1

    print(f"\n  By section:")
    for sec in sorted(section_cycles.keys()):
        c = section_cycles[sec]
        tot = c["ordered"] + c["reverse"] + c["same"]
        r = c["ordered"] / max(c["reverse"], 1)
        print(f"    {sec}: ordered={c['ordered']} reverse={c['reverse']} same={c['same']} ratio={r:.2f}")

    results = {
        "total_transitions": total_transitions,
        "ordered": ordered,
        "reverse": reverse,
        "same": same,
        "ratio": round(ratio, 2),
        "verdict": verdict,
        "by_section": {sec: dict(c) for sec, c in section_cycles.items()},
    }

    with open(RESULTS / "v20_processing_cycle.json", 'w') as f:
        json.dump(results, f, indent=2)
    return results


# ══════════════════════════════════════════
# TEST 4: GALLOWS STRIPPING
# ══════════════════════════════════════════
def test_gallows_stripping():
    print()
    print("=" * 60)
    print("TEST 4: GALLOWS STRIPPING")
    print("If gallows are paragraph markers, removing them should help")
    print("=" * 60)

    logograms = load_logograms()
    perseus = load_perseus()
    lines = parse_lines_eva()

    GALLOWS = set("ktpf")

    # Baseline: logogram hits with gallows
    all_tokens = []
    for line in lines:
        all_tokens.extend(line["words"])

    base_logo = sum(1 for t in all_tokens if t in logograms)

    # Strip gallows from start of words (if they're paragraph markers)
    stripped_tokens = []
    for token in all_tokens:
        if len(token) > 1 and token[0] in GALLOWS:
            stripped = token[1:]
            stripped_tokens.append(stripped)
        else:
            stripped_tokens.append(token)

    strip_logo = sum(1 for t in stripped_tokens if t in logograms)

    # Also count: gallows-initial words that become logograms after stripping
    new_logograms = Counter()
    for orig, stripped in zip(all_tokens, stripped_tokens):
        if orig != stripped and stripped in logograms and orig not in logograms:
            new_logograms[(orig, stripped, logograms[stripped])] += 1

    # Paragraph-initial analysis
    para_initial_gallows = 0
    para_initial_total = 0
    for line in lines:
        if line["words"]:
            para_initial_total += 1
            first = line["words"][0]
            if first[0] in GALLOWS:
                para_initial_gallows += 1

    print(f"  Baseline logogram hits: {base_logo}/{len(all_tokens)} ({100*base_logo/len(all_tokens):.1f}%)")
    print(f"  After gallows strip:    {strip_logo}/{len(all_tokens)} ({100*strip_logo/len(all_tokens):.1f}%)")
    print(f"  Net change: {strip_logo - base_logo:+d} ({100*(strip_logo-base_logo)/max(base_logo,1):+.1f}%)")
    print(f"\n  Paragraph-initial gallows: {para_initial_gallows}/{para_initial_total} "
          f"({100*para_initial_gallows/max(para_initial_total,1):.1f}%)")

    print(f"\n  New logogram matches after gallows stripping (top 15):")
    for (orig, stripped, latin), count in new_logograms.most_common(15):
        print(f"    {orig:12s} -> {stripped:10s} = {latin:10s} x{count}")

    # Gallows frequency by position
    gallows_pos = defaultdict(lambda: {"initial": 0, "medial": 0, "final": 0, "total": 0})
    for line in lines:
        for i, token in enumerate(line["words"]):
            if token[0] in GALLOWS:
                g = token[0]
                gallows_pos[g]["total"] += 1
                if i == 0:
                    gallows_pos[g]["initial"] += 1
                elif i == len(line["words"]) - 1:
                    gallows_pos[g]["final"] += 1
                else:
                    gallows_pos[g]["medial"] += 1

    print(f"\n  Gallows position distribution:")
    for g in "ktpf":
        p = gallows_pos[g]
        if p["total"] > 0:
            print(f"    {g}: initial={p['initial']} ({100*p['initial']/p['total']:.0f}%) "
                  f"medial={p['medial']} ({100*p['medial']/p['total']:.0f}%) "
                  f"final={p['final']} ({100*p['final']/p['total']:.0f}%) "
                  f"total={p['total']}")

    results = {
        "base_logo": base_logo,
        "strip_logo": strip_logo,
        "net_change": strip_logo - base_logo,
        "para_initial_gallows": para_initial_gallows,
        "para_initial_total": para_initial_total,
        "para_initial_pct": round(100 * para_initial_gallows / max(para_initial_total, 1), 1),
        "new_logograms": [(orig, stripped, latin, count)
                         for (orig, stripped, latin), count in new_logograms.most_common(20)],
        "gallows_positions": {g: dict(p) for g, p in gallows_pos.items()},
    }

    with open(RESULTS / "v20_gallows_stripping.json", 'w') as f:
        json.dump(results, f, indent=2)
    return results


# ══════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════
if __name__ == "__main__":
    print("V20 PARADIGM SHIFT TESTS")
    print("=" * 60)

    r1 = test_sh_ch_distribution()
    r2 = test_tironian_baseline()
    r3 = test_processing_cycle()
    r4 = test_gallows_stripping()

    print()
    print("=" * 60)
    print("V20 VERDICT")
    print("=" * 60)
    print(f"  1. sh vs ch: sh chi2={r1['chi2_sh']}, ch chi2={r1['chi2_ch']}")
    print(f"     sh varies: {r1['verdict_sh']}, ch varies: {r1['verdict_ch']}")
    procedural = r1['chi2_sh'] > 18.5 or r1['chi2_ch'] > 18.5
    print(f"     -> {'PROCEDURAL HYPOTHESIS SUPPORTED' if procedural else 'CIPHER HYPOTHESIS SUPPORTED'}")
    print()
    print(f"  2. Tironian: {r2['actual_matches']} matches, z={r2['z_score']}")
    print(f"     {r2['verdict']}")
    print()
    print(f"  3. Processing cycle: ratio={r3['ratio']}")
    print(f"     {r3['verdict']}")
    print()
    print(f"  4. Gallows: {r4['para_initial_pct']}% paragraph-initial")
    print(f"     Stripping: {r4['net_change']:+d} logogram matches")
    print()

    # OVERALL
    score = 0
    if procedural:
        score += 1
    if r2['z_score'] > 2:
        score += 1
    if r3['ratio'] > 1.3:
        score += 1
    if r4['net_change'] > 0:
        score += 1

    print(f"  OVERALL: {score}/4 tests support paradigm shift")
    if score >= 3:
        print(f"  -> STRONG: Procedural notation system, not simple cipher")
    elif score >= 2:
        print(f"  -> MODERATE: Mixed evidence, proceed with caution")
    else:
        print(f"  -> WEAK: Stay with current approach or explore cipher model")
