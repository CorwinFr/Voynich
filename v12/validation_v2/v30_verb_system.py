#!/usr/bin/env python3
"""
V30 — The Verb System: What is -y/-ey/-eey?

Hypothesis: -y is a VERB MARKER. The e-count on verbs = procedure STEP number.
Position in line determines WHICH verb:
  - Line start → recipe (take)
  - After ingredients → misce (mix) / coque (boil)
  - After processing → cola (strain) / fiat (let it be made)

If true:
  - y/ey/eey should appear at DIFFERENT line positions
  - They should appear BETWEEN substance tokens, not after them
  - dy = y + et = "do AND" (procedural connector)
  - The prefix determines the verb TYPE:
    qo+y = "cum + verb" = "mix with"
    d+y = "in + verb" = "process in"
    sh+y = "[M] + verb" = "process raw material"
    ch+y = "[P] + verb" = "process product"
"""
import sys, re, json
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

BASE = Path("d:/Github/Voynich")
DECODED_FILE = BASE / "v12/output/VOYNICH_DECODE_V12_INGREDIENTS.txt"
RESULTS = BASE / "v12/validation_v2/results"

PREFIXES_ORDER = ["qok", "qot", "qo", "ok", "ot", "ol", "da", "ch", "sh",
                  "d", "y", "r", "p", "l", "t", "f", "k"]
PREFIXES_ORDER.sort(key=len, reverse=True)

SUBSTANCE_SUFFIXES = {"ol", "or", "al", "ar", "ody", "ckhy", "os", "am"}
VERB_CANDIDATE_SUFFIXES = {"y", "dy"}
UNIT_PATTERN = re.compile(r'^a?(i+)([nr])$')


def parse_lines_eva():
    lines = []
    folio = sec = None
    with open(DECODED_FILE, 'r', encoding='utf-8') as f:
        for raw in f:
            m = re.match(r'\s*FOLIO (\S+) \| Section: (\S+)', raw)
            if m: folio, sec = m.group(1), m.group(2); continue
            if folio and 'EVA' in raw and ':' in raw:
                parts = raw.split(':')
                if 'EVA' in parts[0]:
                    words = [w.lower() for w in parts[1].strip().split() if w.isalpha() and len(w)>=2]
                    if words: lines.append({"folio": folio, "section": sec, "words": words})
    return lines


def classify_token(token):
    """Classify a token as SUBSTANCE, VERB, UNIT, GALLOWS, or UNKNOWN."""
    w = token
    gallows = ""
    if len(w) > 1 and w[0] in "ptf":
        gallows = w[0]; w = w[1:]

    prefix = ""
    for pfx in PREFIXES_ORDER:
        if w.startswith(pfx) and len(w) > len(pfx):
            prefix = pfx; w = w[len(pfx):]; break

    if w.startswith('k') and len(w) > 1:
        w = w[1:]

    # Unit?
    if UNIT_PATTERN.match(w):
        return "UNIT", gallows, prefix, w, 0

    # Strip e-count
    e_count = 0
    while w.startswith('e') and len(w) > 1:
        rem = w[1:]
        if rem in SUBSTANCE_SUFFIXES or rem in VERB_CANDIDATE_SUFFIXES or len(rem) >= 2:
            e_count += 1; w = rem
        else:
            break

    if w in SUBSTANCE_SUFFIXES:
        return "SUBSTANCE", gallows, prefix, w, e_count
    elif w in VERB_CANDIDATE_SUFFIXES:
        return "VERB", gallows, prefix, w, e_count
    else:
        return "OTHER", gallows, prefix, w, e_count


# ══════════════════════════════════════════
# TEST 1: LINE POSITION OF VERBS vs SUBSTANCES
# ══════════════════════════════════════════
def test_line_position(lines):
    print("=" * 70)
    print("TEST 1: WHERE do VERBS vs SUBSTANCES appear in lines?")
    print("=" * 70)
    print()

    verb_positions = []  # relative position 0-1
    subst_positions = []
    unit_positions = []

    for line in lines:
        n = len(line["words"])
        if n < 4: continue
        for i, w in enumerate(line["words"]):
            cat, g, pfx, core, e = classify_token(w)
            rel_pos = i / (n - 1) if n > 1 else 0.5
            if cat == "VERB":
                verb_positions.append(rel_pos)
            elif cat == "SUBSTANCE":
                subst_positions.append(rel_pos)
            elif cat == "UNIT":
                unit_positions.append(rel_pos)

    # Histogram
    bins = 5
    print(f"  Position in line (0=start, 1=end), lines with 4+ tokens:")
    print(f"  {'Bin':>10s} {'VERB':>8s} {'SUBST':>8s} {'UNIT':>8s}")
    for b in range(bins):
        lo, hi = b/bins, (b+1)/bins
        v = sum(1 for p in verb_positions if lo <= p < hi)
        s = sum(1 for p in subst_positions if lo <= p < hi)
        u = sum(1 for p in unit_positions if lo <= p < hi)
        label = f"{lo:.1f}-{hi:.1f}"
        v_pct = 100*v/max(len(verb_positions),1)
        s_pct = 100*s/max(len(subst_positions),1)
        u_pct = 100*u/max(len(unit_positions),1)
        print(f"  {label:>10s} {v_pct:7.1f}% {s_pct:7.1f}% {u_pct:7.1f}%")

    print(f"\n  Total: VERB={len(verb_positions)}, SUBST={len(subst_positions)}, UNIT={len(unit_positions)}")

    # Mean positions
    if verb_positions and subst_positions and unit_positions:
        print(f"\n  Mean position: VERB={sum(verb_positions)/len(verb_positions):.3f}, "
              f"SUBST={sum(subst_positions)/len(subst_positions):.3f}, "
              f"UNIT={sum(unit_positions)/len(unit_positions):.3f}")


# ══════════════════════════════════════════
# TEST 2: WHAT SURROUNDS VERBS?
# ══════════════════════════════════════════
def test_verb_context(lines):
    print()
    print("=" * 70)
    print("TEST 2: WHAT SURROUNDS VERB TOKENS?")
    print("=" * 70)
    print()
    print("  If -y is a verb, it should appear BETWEEN substances/units")
    print("  Pattern: SUBSTANCE → VERB → SUBSTANCE (ingredient, action, ingredient)")
    print()

    # Trigram analysis: what category comes before and after VERB tokens?
    before_verb = Counter()
    after_verb = Counter()
    trigrams = Counter()

    for line in lines:
        words = line["words"]
        cats = [classify_token(w)[0] for w in words]
        for i in range(len(cats)):
            if cats[i] == "VERB":
                if i > 0: before_verb[cats[i-1]] += 1
                if i < len(cats)-1: after_verb[cats[i+1]] += 1
                if i > 0 and i < len(cats)-1:
                    trigrams[(cats[i-1], "VERB", cats[i+1])] += 1

    print("  What comes BEFORE a verb token:")
    total_bv = sum(before_verb.values())
    for cat, count in before_verb.most_common():
        print(f"    {cat:>12s}: {count:6d} ({100*count/total_bv:.1f}%)")

    print(f"\n  What comes AFTER a verb token:")
    total_av = sum(after_verb.values())
    for cat, count in after_verb.most_common():
        print(f"    {cat:>12s}: {count:6d} ({100*count/total_av:.1f}%)")

    print(f"\n  TRIGRAM PATTERNS around verbs:")
    for tri, count in trigrams.most_common(10):
        print(f"    {tri[0]:>10s} → VERB → {tri[2]:>10s}: {count:6d}")

    # Does SUBSTANCE → VERB → SUBSTANCE dominate?
    svs = trigrams.get(("SUBSTANCE", "VERB", "SUBSTANCE"), 0)
    total_tri = sum(trigrams.values())
    print(f"\n  SUBSTANCE → VERB → SUBSTANCE: {svs}/{total_tri} ({100*svs/max(total_tri,1):.1f}%)")


# ══════════════════════════════════════════
# TEST 3: E-COUNT ON VERBS = STEP NUMBER?
# ══════════════════════════════════════════
def test_verb_e_count(lines):
    print()
    print("=" * 70)
    print("TEST 3: E-COUNT ON VERBS = PROCEDURE STEP?")
    print("=" * 70)
    print()
    print("  If e-count on verbs = step number:")
    print("  - ey (e=1) should appear EARLIER in lines (first step)")
    print("  - eey (e=2) should appear LATER (second step)")
    print("  - eeey (e=3) even later (third step)")
    print()

    # For -y suffix: track position by e-count
    positions_by_e = defaultdict(list)
    # For -dy suffix: same
    positions_dy_by_e = defaultdict(list)

    for line in lines:
        n = len(line["words"])
        if n < 4: continue
        for i, w in enumerate(line["words"]):
            cat, g, pfx, core, e_count = classify_token(w)
            if cat != "VERB": continue
            rel_pos = i / (n - 1) if n > 1 else 0.5

            if core == "y":
                positions_by_e[e_count].append(rel_pos)
            elif core == "dy":
                positions_dy_by_e[e_count].append(rel_pos)

    print("  SUFFIX -y (verb marker):")
    print(f"  {'e-count':>8s} {'N':>7s} {'Mean pos':>10s} {'Early%':>8s} {'Late%':>8s}")
    for e in sorted(positions_by_e.keys()):
        positions = positions_by_e[e]
        if len(positions) < 10: continue
        mean = sum(positions) / len(positions)
        early = 100 * sum(1 for p in positions if p < 0.33) / len(positions)
        late = 100 * sum(1 for p in positions if p > 0.67) / len(positions)
        print(f"  e={e:6d} {len(positions):7d} {mean:10.3f} {early:8.1f} {late:8.1f}")

    print(f"\n  SUFFIX -dy (verb+et marker):")
    print(f"  {'e-count':>8s} {'N':>7s} {'Mean pos':>10s} {'Early%':>8s} {'Late%':>8s}")
    for e in sorted(positions_dy_by_e.keys()):
        positions = positions_dy_by_e[e]
        if len(positions) < 10: continue
        mean = sum(positions) / len(positions)
        early = 100 * sum(1 for p in positions if p < 0.33) / len(positions)
        late = 100 * sum(1 for p in positions if p > 0.67) / len(positions)
        print(f"  e={e:6d} {len(positions):7d} {mean:10.3f} {early:8.1f} {late:8.1f}")


# ══════════════════════════════════════════
# TEST 4: PREFIX ON VERBS = VERB TYPE?
# ══════════════════════════════════════════
def test_verb_prefix(lines):
    print()
    print("=" * 70)
    print("TEST 4: PREFIX ON VERBS = VERB TYPE?")
    print("=" * 70)
    print()
    print("  If prefix determines the action:")
    print("  qo+y = misce (mix with)")
    print("  d+y = coque in (process in)")
    print("  sh+y = tere (grind raw)")
    print("  ch+y = cola (strain product)")
    print("  y+y = de+verb (about/from)")
    print("  l+y = per+verb (through/filter)")
    print("  gallows+y = recipe (take)")
    print()

    prefix_verb = Counter()
    prefix_substance = Counter()

    for line in lines:
        for w in line["words"]:
            cat, g, pfx, core, e = classify_token(w)
            full_pfx = (g + "+" if g else "") + pfx
            if cat == "VERB":
                prefix_verb[full_pfx] += 1
            elif cat == "SUBSTANCE":
                prefix_substance[full_pfx] += 1

    print("  PREFIX DISTRIBUTION on VERBS:")
    total_v = sum(prefix_verb.values())
    for pfx, count in prefix_verb.most_common(15):
        label = pfx if pfx else "(none)"
        # Compare with substance prefix
        s_count = prefix_substance.get(pfx, 0)
        total_s = sum(prefix_substance.values())
        v_pct = 100*count/total_v
        s_pct = 100*s_count/max(total_s,1)
        ratio = v_pct / max(s_pct, 0.1)
        enriched = "← VERB-enriched" if ratio > 1.5 else ""
        print(f"    {label:>10s}: VERB={count:5d} ({v_pct:5.1f}%)  SUBST={s_count:5d} ({s_pct:5.1f}%)  ratio={ratio:.1f}x {enriched}")


# ══════════════════════════════════════════
# TEST 5: RECIPE FLOW — Complete line classification
# ══════════════════════════════════════════
def test_recipe_flow(lines):
    print()
    print("=" * 70)
    print("TEST 5: RECIPE FLOW — Read lines as procedures")
    print("=" * 70)

    SUBSTANCE_NAME = {
        "ol": "OLEUM", "or": "HIERA", "al": "SAL", "ar": "AQUA",
        "ody": "ACETUM", "ckhy": "CERA", "os": "SUCCUS", "am": "ANA",
    }
    PREFIX_NAME = {
        "": "", "d": "in", "da": "in", "qo": "cum", "qok": "cum", "qot": "cum",
        "y": "de", "r": "re", "ol": "ex", "l": "per",
        "ch": "[P]", "sh": "[M]", "ok": "", "ot": "", "k": "",
    }
    GALLOWS_NAME = {"p": "Rx", "t": "§", "f": "Rx"}

    def read_token(token):
        cat, g, pfx, core, e_count = classify_token(token)
        parts = []

        gn = GALLOWS_NAME.get(g, "")
        if gn: parts.append(gn)

        pn = PREFIX_NAME.get(pfx.split("+")[0], pfx)
        if pn: parts.append(pn)

        if cat == "UNIT":
            um = UNIT_PATTERN.match(core)
            if um:
                sym = "℥" if um.group(2) == "n" else "ʒ"
                parts.append(f"{len(um.group(1))}{sym}")
            else:
                parts.append(f"?{core}?")
        elif cat == "SUBSTANCE":
            s = SUBSTANCE_NAME.get(core, core)
            if e_count > 0:
                parts.append(f"{e_count}×{s}")
            else:
                parts.append(s)
        elif cat == "VERB":
            if core == "dy":
                if e_count > 0:
                    parts.append(f"FACI.{e_count} et")
                else:
                    parts.append("FACI et")
            else:  # y
                if e_count > 0:
                    parts.append(f"FACI.{e_count}")
                else:
                    parts.append("FACI")
        else:
            if e_count > 0:
                parts.append(f"{e_count}×?{core}?")
            else:
                parts.append(f"?{core}?")

        return " ".join(parts)

    # Decode best lines from pharma sections
    print(f"\n  PHARMACEUTICAL RECIPES (S section, 6+ tokens):")
    shown = 0
    for line in lines:
        if shown >= 20: break
        if line["section"] != "S": continue
        if len(line["words"]) < 6: continue

        cats = [classify_token(w)[0] for w in line["words"]]
        known = sum(1 for c in cats if c in ("VERB", "SUBSTANCE", "UNIT"))
        pct = 100 * known / len(cats)
        if pct < 70: continue

        eva = " ".join(line["words"])
        decoded = " . ".join(read_token(w) for w in line["words"])
        cat_str = " ".join(c[0] for c in cats)  # V=verb, S=substance, U=unit, O=other

        print(f"\n    [{line['folio']}] ({pct:.0f}%)")
        print(f"      EVA:  {eva[:110]}")
        print(f"      READ: {decoded[:110]}")
        print(f"      TYPE: {cat_str}")
        shown += 1

    # F103R
    print(f"\n  F103R BEST LINES:")
    shown = 0
    for line in lines:
        if shown >= 15: break
        if line["folio"].upper() != "F103R": continue

        cats = [classify_token(w)[0] for w in line["words"]]
        known = sum(1 for c in cats if c in ("VERB", "SUBSTANCE", "UNIT"))
        pct = 100 * known / len(cats)
        if pct < 60: continue

        eva = " ".join(line["words"])
        decoded = " ".join(read_token(w) for w in line["words"])
        cat_str = " ".join(c[0] for c in cats)

        print(f"\n    [{line['folio']}] ({pct:.0f}%)")
        print(f"      EVA:  {eva[:110]}")
        print(f"      READ: {decoded[:110]}")
        print(f"      TYPE: {cat_str}")
        shown += 1


# ══════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════
if __name__ == "__main__":
    print("V30 THE VERB SYSTEM")
    print("=" * 70)
    print()

    lines = parse_lines_eva()
    print(f"  {len(lines)} lines, {sum(len(l['words']) for l in lines)} tokens\n")

    test_line_position(lines)
    test_verb_context(lines)
    test_verb_e_count(lines)
    test_verb_prefix(lines)
    test_recipe_flow(lines)

    print()
    print("=" * 70)
    print("V30 SUMMARY")
    print("=" * 70)
