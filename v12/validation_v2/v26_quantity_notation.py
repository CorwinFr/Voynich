#!/usr/bin/env python3
"""
V26 — Quantity Notation Hypothesis

BREAKTHROUGH INSIGHT from V25b:
  The "e" repetition IS a quantity system. The "i" repetition IS a unit counter.
  The SUFFIXES (-dy, -ey, -ol, -or, -al, -ar) are the REAL vocabulary.

New decomposition model:
  TOKEN = [gallows] + [prefix] + [e-count] + [SUFFIX]

Where:
  - gallows (p,t,k,f) = structural/procedural markers
  - prefix (qo,d,sh,ch,y,r,ol...) = function (with, in, raw, processed, about, again, from...)
  - e-count = QUANTITY (0=base, 1=one, 2=two, 3=three)
  - SUFFIX = the SUBSTANCE or ACTION name

If true:
  - The entire Voynich vocabulary reduces to ~10 core suffixes
  - This explains the low Zipf exponent (0.663) — it's notation, not prose
  - This matches Tironian compositing (base sign + modifying strokes)
  - The "ain/aiin/aiiin" system = separate UNIT counter (a + i×N + n)
"""
import json, sys, re
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

BASE = Path("d:/Github/Voynich")
DECODED_FILE = BASE / "v12/output/VOYNICH_DECODE_V12_INGREDIENTS.txt"
RESULTS = BASE / "v12/validation_v2/results"
LOGOGRAMS_PATH = BASE / "v12/rules/logograms.json"

PREFIXES_ORDER = ["qok", "qot", "qo", "ok", "ot", "ol", "da", "ch", "sh",
                  "d", "y", "r", "p", "l", "t", "f", "k"]
PREFIXES_ORDER.sort(key=len, reverse=True)

# The UNIT counter system
# a + i×N + n = N units
# a + i×N + r = N [something else, maybe a different unit]
UNIT_PATTERNS = {
    "ain": 1, "aiin": 2, "aiiin": 3,
    "air": 1, "aiir": 2, "aiiir": 3,
    "in": 1, "iin": 2, "iiin": 3,
    "ir": 1, "iir": 2, "iiir": 3,
}


def parse_lines_eva():
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


def decompose_token(token):
    """
    New decomposition: gallows + prefix + e-quantity + core-suffix + unit-marker
    Returns dict with all components.
    """
    result = {
        "raw": token,
        "gallows": "",
        "prefix": "",
        "e_count": 0,
        "core": "",
        "unit_n": 0,      # from ain/aiin system
        "unit_type": "",   # "n" or "r" ending
        "residual": "",    # anything not parsed
    }

    working = token

    # Step 1: Strip gallows
    if len(working) > 1 and working[0] in "ptf":
        result["gallows"] = working[0]
        working = working[1:]

    # Step 2: Strip prefix
    for pfx in PREFIXES_ORDER:
        if working.startswith(pfx) and len(working) > len(pfx):
            result["prefix"] = pfx
            working = working[len(pfx):]
            break

    # Step 3: Strip leading 'k' (silent modifier)
    if working.startswith('k') and len(working) > 1:
        if not result["prefix"]:
            result["prefix"] = "k"
        else:
            result["prefix"] += "+k"
        working = working[1:]

    # Step 4: Check if this is a UNIT pattern (a+i*N+n/r)
    unit_match = re.match(r'^a(i+)([nr])$', working)
    if unit_match:
        result["unit_n"] = len(unit_match.group(1))
        result["unit_type"] = unit_match.group(2)
        result["core"] = "UNIT"
        return result

    # Also check bare i+n/r patterns
    unit_match2 = re.match(r'^(i+)([nr])$', working)
    if unit_match2:
        result["unit_n"] = len(unit_match2.group(1))
        result["unit_type"] = unit_match2.group(2)
        result["core"] = "UNIT"
        return result

    # Step 5: Count leading 'e' (quantity marker)
    e_count = 0
    while working.startswith('e') and len(working) > 1:
        # But don't strip 'e' if it's part of a known suffix
        # Check: is the remainder (without this 'e') a valid suffix?
        remainder = working[1:]
        if remainder in ("dy", "ey", "ol", "or", "al", "ar", "os", "eo",
                         "edy", "eey", "eol", "eor", "eal", "ear",
                         "ody", "oey", "ool", "oor",
                         "y", "o", "s", "l", "r",
                         "ky", "ko", "ks",
                         "chy", "cho", "cthy", "ckhey", "ckhy"):
            e_count += 1
            working = remainder
        else:
            break

    result["e_count"] = e_count

    # Step 6: What remains is the CORE SUFFIX
    result["core"] = working

    return result


# ══════════════════════════════════════════
# STEP 1: DECOMPOSE ENTIRE CORPUS
# ══════════════════════════════════════════
def decompose_corpus(lines):
    print("=" * 70)
    print("STEP 1: FULL CORPUS DECOMPOSITION")
    print("=" * 70)

    all_tokens = [w for line in lines for w in line["words"]]
    total = len(all_tokens)

    decomposed = [decompose_token(t) for t in all_tokens]

    # Statistics
    print(f"\n  Total tokens: {total}")

    # Core suffix distribution
    core_counter = Counter()
    for d in decomposed:
        core_counter[d["core"]] += 1

    print(f"\n  CORE SUFFIXES (the REAL vocabulary):")
    print(f"  {'Core':>12s} {'Count':>7s} {'%':>7s} {'Cumul%':>7s}")
    cumul = 0
    for core, count in core_counter.most_common(30):
        pct = 100 * count / total
        cumul += pct
        print(f"  {core:>12s} {count:7d} {pct:7.2f} {cumul:7.1f}")

    # How many core suffixes cover 80% of the corpus?
    cumul = 0
    for i, (core, count) in enumerate(core_counter.most_common()):
        cumul += count
        if cumul >= 0.8 * total:
            print(f"\n  → {i+1} core suffixes cover 80% of the corpus!")
            break

    # E-count distribution
    print(f"\n  E-COUNT (QUANTITY) DISTRIBUTION:")
    e_counter = Counter()
    for d in decomposed:
        e_counter[d["e_count"]] += 1

    for e, count in sorted(e_counter.items()):
        print(f"    e={e}: {count:7d} ({100*count/total:.1f}%)")

    # Unit system
    print(f"\n  UNIT SYSTEM (ain/aiin/aiiin family):")
    unit_counter = Counter()
    unit_type_counter = Counter()
    for d in decomposed:
        if d["core"] == "UNIT":
            unit_counter[d["unit_n"]] += 1
            unit_type_counter[d["unit_type"]] += 1

    for n, count in sorted(unit_counter.items()):
        print(f"    {n} units: {count:5d}")
    print(f"    Type 'n': {unit_type_counter.get('n', 0)}")
    print(f"    Type 'r': {unit_type_counter.get('r', 0)}")

    # Prefix distribution
    print(f"\n  PREFIX DISTRIBUTION:")
    pfx_counter = Counter()
    for d in decomposed:
        pfx_counter[d["prefix"]] += 1

    for pfx, count in pfx_counter.most_common(20):
        label = pfx if pfx else "(none)"
        print(f"    {label:>10s}: {count:7d} ({100*count/total:.1f}%)")

    return decomposed, core_counter


# ══════════════════════════════════════════
# STEP 2: CORE SUFFIX IDENTITY
# ══════════════════════════════════════════
def identify_core_suffixes(core_counter, decomposed, lines):
    print()
    print("=" * 70)
    print("STEP 2: WHAT ARE THE CORE SUFFIXES?")
    print("=" * 70)
    print()
    print("  If the system is: prefix + e-count + SUFFIX")
    print("  Then each suffix is a substance or action.")
    print("  The prefix tells you the FUNCTION.")
    print("  The e-count tells you the QUANTITY.")
    print()

    # For each top suffix, show its prefix distribution
    # sh- prefix = raw material
    # ch- prefix = processed product
    # qo- prefix = "with" (cum)
    # d- prefix = "in"
    # This tells us: is it a SUBSTANCE (gets sh/ch) or ACTION (gets d/qo)?

    top_cores = [core for core, _ in core_counter.most_common(15)
                 if core != "UNIT" and len(core) >= 2]

    print(f"  {'Core':>8s} {'Total':>7s} {'sh%':>6s} {'ch%':>6s} {'qo%':>6s} {'d%':>5s} {'y%':>5s} {'no-pfx%':>8s} {'Type':>12s}")
    print(f"  {'-'*70}")

    suffix_types = {}
    for core in top_cores:
        tokens = [d for d in decomposed if d["core"] == core]
        total = len(tokens)
        sh = sum(1 for d in tokens if d["prefix"].startswith("sh"))
        ch = sum(1 for d in tokens if d["prefix"].startswith("ch"))
        qo = sum(1 for d in tokens if d["prefix"].startswith("qo"))
        d_pfx = sum(1 for d in tokens if d["prefix"] in ("d", "da"))
        y_pfx = sum(1 for d in tokens if d["prefix"] == "y")
        no_pfx = sum(1 for d in tokens if d["prefix"] == "")

        sh_pct = 100 * sh / total
        ch_pct = 100 * ch / total
        qo_pct = 100 * qo / total
        d_pct = 100 * d_pfx / total
        y_pct = 100 * y_pfx / total
        no_pct = 100 * no_pfx / total

        # Classify
        if sh_pct + ch_pct > 30:
            stype = "SUBSTANCE"
        elif qo_pct > 20:
            stype = "CUM-COMPOUND"
        elif d_pct > 15:
            stype = "IN-CONTEXT"
        elif no_pct > 40:
            stype = "STANDALONE"
        else:
            stype = "MIXED"

        suffix_types[core] = stype
        print(f"  {core:>8s} {total:7d} {sh_pct:6.1f} {ch_pct:6.1f} {qo_pct:6.1f} {d_pct:5.1f} {y_pct:5.1f} {no_pct:8.1f} {stype:>12s}")

    return suffix_types


# ══════════════════════════════════════════
# STEP 3: DECODE WITH NEW MODEL
# ══════════════════════════════════════════
def decode_with_new_model(lines, decomposed):
    print()
    print("=" * 70)
    print("STEP 3: DECODE SAMPLE LINES WITH QUANTITY NOTATION MODEL")
    print("=" * 70)

    PREFIX_MEANING = {
        "": "", "d": "IN", "da": "IN", "qo": "CUM", "qok": "CUM", "qot": "CUM",
        "y": "DE", "r": "RE", "p": "", "ol": "EX", "l": "PER",
        "ch": "[P]", "sh": "[M]", "ok": "", "ot": "", "f": "", "t": "§", "k": "",
    }

    GALLOWS_MEANING = {"p": "Rx", "t": "§", "k": "", "f": "Rx", "": ""}

    # Decode a token using the new model
    def new_decode(d):
        parts = []

        # Gallows
        g = GALLOWS_MEANING.get(d["gallows"], "")
        if g:
            parts.append(g)

        # Prefix
        pfx = d["prefix"].split("+")[0]  # handle "k+k" etc
        p = PREFIX_MEANING.get(pfx, pfx)
        if p:
            parts.append(p)

        # E-count + Core
        if d["core"] == "UNIT":
            parts.append(f"{d['unit_n']}×UNIT({d['unit_type']})")
        elif d["e_count"] > 0:
            parts.append(f"{d['e_count']}×{d['core']}")
        else:
            parts.append(d["core"])

        return ' '.join(parts)

    # Show pharmaceutical section samples
    print(f"\n  PHARMACEUTICAL SECTIONS (S/P):")
    token_idx = 0
    shown = 0
    for line in lines:
        if shown >= 25:
            break
        if line["section"] not in ("S", "P"):
            token_idx += len(line["words"])
            continue
        if len(line["words"]) < 4:
            token_idx += len(line["words"])
            continue

        eva = ' '.join(line["words"])
        decoded_parts = []
        for i, w in enumerate(line["words"]):
            d = decomposed[token_idx + i]
            decoded_parts.append(new_decode(d))

        decoded = ' | '.join(decoded_parts)
        print(f"\n    [{line['folio']}]")
        print(f"      EVA: {eva[:100]}")
        print(f"      NEW: {decoded[:100]}")
        shown += 1
        token_idx += len(line["words"])

    # F103R specifically
    print(f"\n  F103R (the 'coquo' folio):")
    token_idx = 0
    shown = 0
    for line in lines:
        if line["folio"].upper() == "F103R" and shown < 15:
            eva = ' '.join(line["words"])
            decoded_parts = []
            for i, w in enumerate(line["words"]):
                d = decomposed[token_idx + i]
                decoded_parts.append(new_decode(d))
            decoded = ' | '.join(decoded_parts)
            print(f"\n    EVA: {eva[:110]}")
            print(f"    NEW: {decoded[:110]}")
            shown += 1
        token_idx += len(line["words"])

    # Herbal labels (short lines, often just ingredient names)
    print(f"\n  HERBAL LABELS (short lines, H section):")
    token_idx = 0
    shown = 0
    for line in lines:
        if line["section"] == "H" and len(line["words"]) <= 3 and shown < 15:
            eva = ' '.join(line["words"])
            decoded_parts = []
            for i, w in enumerate(line["words"]):
                d = decomposed[token_idx + i]
                decoded_parts.append(new_decode(d))
            decoded = ' | '.join(decoded_parts)
            print(f"    [{line['folio']}] {eva:30s} → {decoded}")
            shown += 1
        token_idx += len(line["words"])


# ══════════════════════════════════════════
# STEP 4: SECTORIAL VARIATION OF CORE SUFFIXES
# ══════════════════════════════════════════
def sectorial_core_analysis(lines, decomposed):
    print()
    print("=" * 70)
    print("STEP 4: DO CORE SUFFIXES VARY BY SECTION?")
    print("=" * 70)
    print()
    print("  If suffixes are substances, herbal sections should differ from pharma.")

    section_cores = defaultdict(Counter)
    section_total = Counter()

    token_idx = 0
    for line in lines:
        for i, w in enumerate(line["words"]):
            d = decomposed[token_idx + i]
            section_cores[line["section"]][d["core"]] += 1
            section_total[line["section"]] += 1
        token_idx += len(line["words"])

    top_cores = ["dy", "ey", "ol", "or", "al", "ar", "y", "UNIT", "o", "ody"]

    print(f"\n  {'Core':>8s}", end="")
    for sec in sorted(section_total.keys()):
        print(f"  {sec:>6s}", end="")
    print()

    for core in top_cores:
        print(f"  {core:>8s}", end="")
        for sec in sorted(section_total.keys()):
            rate = 100 * section_cores[sec][core] / max(section_total[sec], 1)
            print(f"  {rate:6.1f}", end="")
        print()


# ══════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════
if __name__ == "__main__":
    print("V26 QUANTITY NOTATION HYPOTHESIS")
    print("=" * 70)
    print()
    print("  Model: TOKEN = [gallows] + [prefix] + [e-count] + [CORE SUFFIX]")
    print("  The 'e' repetition encodes QUANTITY.")
    print("  The 'a+i×N+n' encodes UNITS.")
    print("  The CORE SUFFIX is the actual substance/action.")
    print()

    lines = parse_lines_eva()
    print(f"  {len(lines)} lines, {sum(len(l['words']) for l in lines)} tokens")
    print()

    decomposed, core_counter = decompose_corpus(lines)
    suffix_types = identify_core_suffixes(core_counter, decomposed, lines)
    decode_with_new_model(lines, decomposed)
    sectorial_core_analysis(lines, decomposed)

    # Save
    results = {
        "model": "gallows + prefix + e-count + core-suffix",
        "core_suffixes": core_counter.most_common(30),
        "suffix_types": suffix_types,
    }
    with open(RESULTS / "v26_quantity_notation.json", 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print()
    print("=" * 70)
    print("V26 SUMMARY")
    print("=" * 70)
    unique_cores = len([c for c, n in core_counter.items() if n >= 10])
    print(f"  Unique core suffixes (freq >= 10): {unique_cores}")
    print(f"  Top 10 cores cover: {100*sum(c for _,c in core_counter.most_common(10))/sum(core_counter.values()):.1f}%")
    print(f"  Results saved to {RESULTS / 'v26_quantity_notation.json'}")
