#!/usr/bin/env python3
"""
V35 — Dose Crisis: Are our quantities lethal?

If aiin=2℥ (2 ounces=60g) and HIERA dose should be ʒiii (3 drachms=11g),
our model produces DANGEROUS doses. This tests ALL alternative hypotheses:

Piste 1: Units are drachms (ʒ), not ounces (℥)
Piste 2: e-count and i-count are TWO different unit systems
Piste 3: ain/aiin are NOT quantities (Galenic degrees?)
Piste 4: ain/aiin are reference indices
Piste 5: The system is RELATIVE (proportions, not absolute)
Piste 6: or≠hiera (mapping is wrong)
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

UNIT_RE = re.compile(r'^a?(i+)([nr])$')

SUBSTANCES = {
    "ol": "OLEUM", "or": "HIERA", "al": "SAL", "ar": "AQUA",
    "ody": "ACETUM", "ckhy": "CERA", "os": "SUCCUS", "am": "ANA",
}

def parse_lines():
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

def decompose(token):
    w = token
    gallows = ""
    if len(w) > 1 and w[0] in "ptf":
        gallows = w[0]; w = w[1:]
    prefix = ""
    for pfx in PREFIXES_ORDER:
        if w.startswith(pfx) and len(w) > len(pfx):
            prefix = pfx; w = w[len(pfx):]; break
    inner = ""
    for ipfx in ["cth", "ckh", "cfh", "ch", "sh"]:
        if w.startswith(ipfx) and len(w) > len(ipfx):
            inner = ipfx; w = w[len(ipfx):]; break
    if w.startswith('k') and len(w) > 1:
        w = w[1:]
    um = UNIT_RE.match(w)
    if um:
        return gallows, prefix, inner, 0, "UNIT", len(um.group(1)), um.group(2)
    e = 0
    while w.startswith('e') and len(w) > 1:
        e += 1; w = w[1:]
    return gallows, prefix, inner, e, w, 0, ""

def classify(token):
    g, pfx, inner, e, core, un, ut = decompose(token)
    if core == "UNIT": return "UNIT", un, ut, pfx, g
    if core in SUBSTANCES: return "SUBSTANCE", core, e, pfx, g
    if core in ("y", "dy", "ey"): return "VERB_OR_STATE", core, e, pfx, inner
    return "OTHER", core, e, pfx, g


# ══════════════════════════════════════════
# PISTE 1: Units as drachms — does it make pharmaceutical sense?
# ══════════════════════════════════════════
def piste1_drachms(lines):
    print("=" * 70)
    print("PISTE 1: Units are DRACHMS (ʒ), not ounces (℥)")
    print("=" * 70)
    print()
    print("  Medieval standard doses (Antidotarium Nicolai):")
    print("  Hiera Picra dose: ʒ iii (3 drachms ≈ 11g)")
    print("  Electuaries: ʒ i - ʒ iii (3-11g)")
    print("  Individual ingredients: ʒ ii - ℥ ii (7-60g)")
    print("  Mel/Oleum base: lb i - lb ii (370-740g)")
    print()

    # What i-counts appear near each substance?
    subst_units = defaultdict(Counter)  # substance → i-count frequencies
    for line in lines:
        words = line["words"]
        for i, w in enumerate(words):
            cat = classify(w)
            if cat[0] == "SUBSTANCE":
                subst = cat[1]
                # Look for UNIT tokens within 2 positions
                for j in range(max(0,i-2), min(len(words), i+3)):
                    if j == i: continue
                    c2 = classify(words[j])
                    if c2[0] == "UNIT":
                        subst_units[subst][c2[1]] += 1  # i-count

    print("  UNIT COUNTS NEAR EACH SUBSTANCE:")
    print(f"  {'Substance':>10s} {'1-unit':>7s} {'2-unit':>7s} {'3-unit':>7s} {'Ratio 2/1':>9s}")
    for subst in sorted(SUBSTANCES.keys()):
        s_name = SUBSTANCES[subst]
        u1 = subst_units[subst].get(1, 0)
        u2 = subst_units[subst].get(2, 0)
        u3 = subst_units[subst].get(3, 0)
        ratio = u2 / max(u1, 1)
        print(f"  {s_name:>10s} {u1:7d} {u2:7d} {u3:7d} {ratio:9.2f}")

    # If units are DRACHMS:
    print(f"\n  IF DRACHMS (ʒ): typical decoded doses would be:")
    print(f"    'HIERA 2ʒ' = 7.4g → SAFE (standard range ʒi-ʒiii)")
    print(f"    'OLEUM 2ʒ' = 7.4g → small amount of oil (for dropping, not base)")
    print(f"    'SAL 1ʒ' = 3.7g → reasonable salt dose")
    print(f"    'CERA 2ʒ' = 7.4g → small amount of wax")

    print(f"\n  IF OUNCES (℥): typical decoded doses would be:")
    print(f"    'HIERA 2℥' = 60g → DANGEROUS (5× standard dose)")
    print(f"    'OLEUM 2℥' = 60g → large amount (base quantity)")
    print(f"    'SAL 2℥' = 60g → very large salt dose")
    print(f"    'CERA 2℥' = 60g → large wax base")

    # Check: in the Antidotarium, what units go with what?
    print(f"\n  ANTIDOTARIUM EVIDENCE:")
    print(f"    Individual spices/herbs: typically ʒ ii - ʒ vi (7-22g)")
    print(f"    Aloe in Hiera: ℥ iii (90g, but that's the INGREDIENT, not the dose)")
    print(f"    Mel base: lb i - lb x (370-3700g)")
    print(f"    Dose of finished medicine: ʒ i - ʒ iii (3-11g)")
    print(f"    'in modum avellane' = hazelnut-sized portion")
    print(f"\n  KEY DISTINCTION: ingredient quantities (℥) vs administration doses (ʒ)")
    print(f"  Our ain/aiin might encode INGREDIENT quantities, not doses!")


# ══════════════════════════════════════════
# PISTE 2: e-count vs i-count = two different systems
# ══════════════════════════════════════════
def piste2_two_systems(lines):
    print()
    print("=" * 70)
    print("PISTE 2: E-COUNT and I-COUNT are TWO DIFFERENT unit systems")
    print("=" * 70)
    print()
    print("  Hypothesis: e-count = OUNCES (large, for ingredients)")
    print("              i-count = DRACHMS (small, for precise doses)")
    print()

    # Where do e-count tokens vs i-count tokens appear?
    e_positions = []  # relative position in line
    i_positions = []
    e_sections = Counter()
    i_sections = Counter()
    e_near_substance = 0
    i_near_substance = 0
    e_total = 0
    i_total = 0

    for line in lines:
        n = len(line["words"])
        if n < 3: continue
        for idx, w in enumerate(line["words"]):
            cat = classify(w)
            rel = idx / (n-1) if n > 1 else 0.5

            if cat[0] == "UNIT":
                i_positions.append(rel)
                i_sections[line["section"]] += 1
                i_total += 1
                # Check if near a substance
                for j in range(max(0,idx-1), min(n, idx+2)):
                    if j != idx and classify(line["words"][j])[0] == "SUBSTANCE":
                        i_near_substance += 1
                        break

            elif cat[0] == "SUBSTANCE" and cat[2] > 0:  # e-count > 0
                e_positions.append(rel)
                e_sections[line["section"]] += 1
                e_total += 1
                e_near_substance += 1  # by definition it IS on a substance

    print(f"  E-count tokens (on substances): {e_total}")
    print(f"  I-count tokens (UNIT markers): {i_total}")

    if e_positions and i_positions:
        print(f"\n  MEAN POSITION in line:")
        print(f"    E-count: {sum(e_positions)/len(e_positions):.3f}")
        print(f"    I-count: {sum(i_positions)/len(i_positions):.3f}")

    print(f"\n  SECTORIAL DISTRIBUTION:")
    print(f"  {'Section':>8s} {'E-count%':>9s} {'I-count%':>9s}")
    all_secs = sorted(set(list(e_sections.keys()) + list(i_sections.keys())))
    for sec in all_secs:
        e_pct = 100 * e_sections.get(sec, 0) / max(e_total, 1)
        i_pct = 100 * i_sections.get(sec, 0) / max(i_total, 1)
        print(f"  {sec:>8s} {e_pct:9.1f} {i_pct:9.1f}")

    # Do they appear TOGETHER or separately?
    both_in_line = 0
    e_only = 0
    i_only = 0
    for line in lines:
        has_e = False
        has_i = False
        for w in line["words"]:
            cat = classify(w)
            if cat[0] == "UNIT": has_i = True
            if cat[0] == "SUBSTANCE" and cat[2] > 0: has_e = True
        if has_e and has_i: both_in_line += 1
        elif has_e: e_only += 1
        elif has_i: i_only += 1

    print(f"\n  CO-OCCURRENCE in lines:")
    print(f"    Both E and I: {both_in_line}")
    print(f"    E only:       {e_only}")
    print(f"    I only:       {i_only}")
    print(f"    Neither:      {len(lines) - both_in_line - e_only - i_only}")

    if both_in_line > 100:
        print(f"\n  → E and I CO-OCCUR frequently → they're measuring DIFFERENT things")
    else:
        print(f"\n  → E and I rarely co-occur → they might be the SAME system")


# ══════════════════════════════════════════
# PISTE 3: ain/aiin = Galenic degrees (revisited)
# ══════════════════════════════════════════
def piste3_galenic_degrees(lines):
    print()
    print("=" * 70)
    print("PISTE 3: ain/aiin = GALENIC DEGREES (revisited)")
    print("=" * 70)
    print()
    print("  V22 refuted this because aiin(1733) > ain(915)")
    print("  BUT: research shows degree 2 IS the most common in Circa Instans!")
    print("  Most substances are 'moderately hot/cold' (degree 2)")
    print("  Degree 1 = mild, Degree 3-4 = extreme (rare)")
    print()

    # NEW TEST: In Circa Instans, how are degrees distributed?
    # "Aloe calide et sicce complexionis est in secundo gradu"
    # Most herbs are degree 1-2, few are degree 3-4
    # So degree 2 > degree 1 is actually EXPECTED!

    # Check: do ain/aiin appear in HERBAL section labels (where quality descriptions go)?
    h_units = Counter()
    s_units = Counter()
    for line in lines:
        for w in line["words"]:
            cat = classify(w)
            if cat[0] == "UNIT":
                i_count = cat[1]
                if line["section"] == "H":
                    h_units[i_count] += 1
                elif line["section"] == "S":
                    s_units[i_count] += 1

    print(f"  I-COUNT distribution by section:")
    print(f"  {'I-count':>8s} {'Herbal%':>9s} {'Pharma%':>9s}")
    h_total = sum(h_units.values())
    s_total = sum(s_units.values())
    for i in [1, 2, 3]:
        h_pct = 100 * h_units.get(i, 0) / max(h_total, 1)
        s_pct = 100 * s_units.get(i, 0) / max(s_total, 1)
        print(f"  {i:>8d} {h_pct:9.1f} {s_pct:9.1f}")

    print(f"\n  IF Galenic degrees:")
    print(f"    Herbal section should have MORE i-count (quality descriptions)")
    print(f"    Pharma section should have proportionally fewer")
    if h_total > 0 and s_total > 0:
        h_rate = h_total / sum(len(l["words"]) for l in lines if l["section"] == "H")
        s_rate = s_total / sum(len(l["words"]) for l in lines if l["section"] == "S")
        print(f"    Herbal UNIT rate: {100*h_rate:.2f}%")
        print(f"    Pharma UNIT rate: {100*s_rate:.2f}%")
        if s_rate > h_rate * 1.3:
            print(f"    → Pharma has MORE units → supports QUANTITY interpretation")
        elif h_rate > s_rate * 1.3:
            print(f"    → Herbal has MORE units → supports DEGREE interpretation")
        else:
            print(f"    → Similar rates → AMBIGUOUS")

    # Also: do ain/aiin appear AFTER substance tokens or AFTER quality tokens?
    print(f"\n  WHAT PRECEDES ain/aiin (all sections)?")
    prev_cat = Counter()
    for line in lines:
        words = line["words"]
        for i, w in enumerate(words):
            cat = classify(w)
            if cat[0] == "UNIT" and i > 0:
                prev = classify(words[i-1])
                prev_cat[prev[0]] += 1

    for cat_name, count in prev_cat.most_common():
        print(f"    After {cat_name:>15s}: {count:5d} ({100*count/sum(prev_cat.values()):.1f}%)")


# ══════════════════════════════════════════
# PISTE 4: ain/aiin = reference indices
# ══════════════════════════════════════════
def piste4_indices(lines):
    print()
    print("=" * 70)
    print("PISTE 4: ain/aiin = REFERENCE INDICES (recipe numbers?)")
    print("=" * 70)

    # If indices, they should appear at FIXED positions (always first, or always last)
    positions = defaultdict(list)
    for line in lines:
        n = len(line["words"])
        if n < 3: continue
        for i, w in enumerate(line["words"]):
            cat = classify(w)
            if cat[0] == "UNIT":
                positions[cat[1]].append(i / (n-1))

    print(f"\n  Position distribution of UNIT tokens:")
    print(f"  {'I-count':>8s} {'Mean':>8s} {'StdDev':>8s} {'N':>6s}")
    for ic in [1, 2, 3]:
        pos = positions.get(ic, [])
        if len(pos) >= 10:
            mean = sum(pos) / len(pos)
            std = (sum((p-mean)**2 for p in pos) / len(pos)) ** 0.5
            print(f"  {ic:>8d} {mean:8.3f} {std:8.3f} {len(pos):6d}")

    # If reference indices: they would cluster at specific positions
    # If quantities: they would be distributed (appear anywhere near ingredients)
    all_pos = [p for ic in [1,2,3] for p in positions.get(ic, [])]
    if all_pos:
        mean = sum(all_pos) / len(all_pos)
        std = (sum((p-mean)**2 for p in all_pos) / len(all_pos)) ** 0.5
        print(f"\n  Overall: mean={mean:.3f}, std={std:.3f}")
        if std < 0.15:
            print(f"  → LOW spread → consistent with FIXED position (indices)")
        elif std > 0.25:
            print(f"  → HIGH spread → distributed throughout line (quantities)")
        else:
            print(f"  → MODERATE spread → ambiguous")


# ══════════════════════════════════════════
# PISTE 5: Relative proportions (1:2:3)
# ══════════════════════════════════════════
def piste5_proportions(lines):
    print()
    print("=" * 70)
    print("PISTE 5: ain/aiin = RELATIVE proportions (1:2:3 parts)")
    print("=" * 70)

    # If proportions: lines with MULTIPLE unit tokens should show consistent ratios
    # E.g., a line with ain + aiin = "1 part + 2 parts"
    # The KEY test: do we see ain+aiin on the same line? And do they relate?

    multi_unit_lines = 0
    ratio_patterns = Counter()  # what combinations of i-counts appear per line
    for line in lines:
        units = []
        for w in line["words"]:
            cat = classify(w)
            if cat[0] == "UNIT":
                units.append(cat[1])  # i-count
        if len(units) >= 2:
            multi_unit_lines += 1
            pattern = tuple(sorted(units))
            ratio_patterns[pattern] += 1

    print(f"\n  Lines with 2+ UNIT tokens: {multi_unit_lines}")
    print(f"\n  Most common UNIT combinations per line:")
    for pattern, count in ratio_patterns.most_common(15):
        print(f"    {pattern}: {count:5d}")

    # If proportional: (1,2) should be more common than (1,1) or (2,2)
    same = sum(c for p, c in ratio_patterns.items() if len(set(p)) == 1)
    diff = sum(c for p, c in ratio_patterns.items() if len(set(p)) > 1)
    print(f"\n  Same value combos (1,1) (2,2) etc: {same}")
    print(f"  Different value combos (1,2) (1,3) etc: {diff}")
    if diff > same * 1.5:
        print(f"  → MORE different combos → supports PROPORTIONAL interpretation")
    elif same > diff * 1.5:
        print(f"  → MORE same combos → supports FIXED UNIT interpretation")
    else:
        print(f"  → ROUGHLY EQUAL → ambiguous")


# ══════════════════════════════════════════
# PISTE 6: Is or=HIERA correct?
# ══════════════════════════════════════════
def piste6_verify_hiera(lines):
    print()
    print("=" * 70)
    print("PISTE 6: Is or=HIERA correct? (V19 Tironian match)")
    print("=" * 70)

    # or was matched to "hiera" in V19 Tironian exhaustive
    # Let's check: does "or" behave like a compound medicine name should?

    # Hiera Picra profile:
    # - A COMPOUND medicine (not a simple)
    # - Used as a purgative
    # - Appears in recipe sections (S), not herbal labels (H)
    # - Would be an INGREDIENT in other recipes, not a standalone

    or_sections = Counter()
    or_positions = []
    or_after = Counter()
    or_before = Counter()
    total_tokens = Counter()

    for line in lines:
        n = len(line["words"])
        total_tokens[line["section"]] += n
        for i, w in enumerate(line["words"]):
            g, pfx, inner, e, core, un, ut = decompose(w)
            if core == "or":
                or_sections[line["section"]] += 1
                if n > 1: or_positions.append(i / (n-1))
                if i > 0:
                    g2, p2, i2, e2, c2, u2, t2 = decompose(line["words"][i-1])
                    or_before[c2] += 1
                if i < n-1:
                    g2, p2, i2, e2, c2, u2, t2 = decompose(line["words"][i+1])
                    or_after[c2] += 1

    print(f"\n  SUFFIX 'or' PROFILE:")
    print(f"  Total occurrences: {sum(or_sections.values())}")
    print(f"\n  Sectorial distribution:")
    for sec in sorted(or_sections.keys()):
        rate = 1000 * or_sections[sec] / max(total_tokens[sec], 1)
        print(f"    {sec}: {or_sections[sec]:5d} ({rate:.1f}‰)")

    if or_positions:
        print(f"\n  Mean line position: {sum(or_positions)/len(or_positions):.3f}")

    print(f"\n  WHAT FOLLOWS 'or'?")
    for core, count in or_after.most_common(10):
        print(f"    → {core:>10s}: {count:5d}")

    print(f"\n  WHAT PRECEDES 'or'?")
    for core, count in or_before.most_common(10):
        print(f"    ← {core:>10s}: {count:5d}")

    # Check: Hiera is H-dominant. Is 'or' H-dominant?
    h_rate = 1000 * or_sections.get("H", 0) / max(total_tokens.get("H", 1), 1)
    s_rate = 1000 * or_sections.get("S", 0) / max(total_tokens.get("S", 1), 1)
    print(f"\n  Herbal rate: {h_rate:.1f}‰, Pharma rate: {s_rate:.1f}‰")
    if h_rate > s_rate * 1.5:
        print(f"  → H-dominant → consistent with a PLANT/SIMPLE, not necessarily Hiera")
        print(f"  → Hiera is a COMPOUND medicine, should be S-dominant, not H-dominant!")
        print(f"  → POSSIBLE ERROR: 'or' might not be 'hiera'")
    elif s_rate > h_rate * 1.5:
        print(f"  → S-dominant → consistent with Hiera (compound medicine)")
    else:
        print(f"  → Mixed → ambiguous")


# ══════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════
if __name__ == "__main__":
    print("V35 DOSE CRISIS — All hypotheses tested")
    print("=" * 70)
    print()

    lines = parse_lines()
    print(f"  {len(lines)} lines, {sum(len(l['words']) for l in lines)} tokens\n")

    piste1_drachms(lines)
    piste2_two_systems(lines)
    piste3_galenic_degrees(lines)
    piste4_indices(lines)
    piste5_proportions(lines)
    piste6_verify_hiera(lines)

    print()
    print("=" * 70)
    print("V35 SYNTHESIS — Which piste wins?")
    print("=" * 70)
