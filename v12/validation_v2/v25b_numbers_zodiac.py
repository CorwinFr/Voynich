#!/usr/bin/env python3
"""
V25b — The Number Problem & Zodiac Connection

A pharmaceutical recipe without quantities makes NO SENSE.
"Take X, mix with Y" requires "Take 2 ounces of X, mix with 3 drachms of Y".
Where are the numbers hidden?

Systematic investigation:
1. The i-stroke hypothesis: ain=1, aiin=2, aiiin=3 (count of i glyphs)
2. Are there other repeating-stroke patterns?
3. Do "numbers" appear after ingredient-like tokens?
4. What's special about the zodiac sections?
5. Gallows as quantity markers?
6. The "bench" characters and rare glyphs

Key medieval pharmaceutical notation:
  ℥ = uncia (ounce) ~30g
  ʒ = drachma (dram) = 1/8 ounce ~3.7g
  ℈ = scrupulum (scruple) = 1/3 dram ~1.3g
  ℔ = libra (pound) = 12 ounces ~373g
  ss = semis (half)
  ana/āā = of each (equal parts)
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


def extract_root(token):
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
    if root.startswith('k') and len(root) > 1:
        root = root[1:]
    return gallows, pfx, root


# ══════════════════════════════════════════
# TEST 1: THE I-STROKE HYPOTHESIS
# ══════════════════════════════════════════
def test_i_strokes(lines):
    print("=" * 70)
    print("TEST 1: THE I-STROKE HYPOTHESIS")
    print("=" * 70)
    print()
    print("  If 'i' is a vertical stroke/tally mark:")
    print("  ain = a+i+n = 1, aiin = a+ii+n = 2, aiiin = a+iii+n = 3")
    print("  in = i+n = 1?, iin = ii+n = 2?, iiin = iii+n = 3?")
    print()

    all_tokens = [w for line in lines for w in line["words"]]

    # Count ALL patterns with repeating 'i' in the corpus
    i_patterns = Counter()
    for token in all_tokens:
        # Find all maximal runs of 'i' in the token
        for match in re.finditer(r'i+', token):
            context_start = max(0, match.start() - 2)
            context_end = min(len(token), match.end() + 2)
            context = token[context_start:context_end]
            i_count = len(match.group())
            i_patterns[(i_count, context)] += 1

    # Summarize by i-count
    by_count = defaultdict(int)
    by_count_examples = defaultdict(Counter)
    for (i_count, context), freq in i_patterns.items():
        by_count[i_count] += freq
        by_count_examples[i_count][context] += freq

    print("  I-STROKE FREQUENCY DISTRIBUTION:")
    for i_count in sorted(by_count.keys()):
        total = by_count[i_count]
        examples = by_count_examples[i_count].most_common(8)
        ex_str = ', '.join(f"{ctx}({c})" for ctx, c in examples)
        print(f"    {i_count} i's: {total:6d} tokens | {ex_str[:80]}")

    # Specific patterns: a + i*N + n (the "ain" family)
    print(f"\n  THE 'a+i*N+n' FAMILY:")
    ain_family = Counter()
    for token in all_tokens:
        for match in re.finditer(r'a(i+)n', token):
            n_strokes = len(match.group(1))
            ain_family[n_strokes] += 1

    for n in sorted(ain_family.keys()):
        name = 'a' + 'i'*n + 'n'
        print(f"    {name:8s} (={n}): {ain_family[n]:6d}")

    # The 'i*N + n' family (without leading 'a')
    print(f"\n  THE 'i*N+n' FAMILY (no leading 'a'):")
    in_family = Counter()
    for token in all_tokens:
        for match in re.finditer(r'(?<!a)(i+)n', token):
            n_strokes = len(match.group(1))
            in_family[n_strokes] += 1

    for n in sorted(in_family.keys()):
        name = 'i'*n + 'n'
        print(f"    {name:8s} (={n}): {in_family[n]:6d}")

    # The 'i*N + r' family
    print(f"\n  THE 'i*N+r' FAMILY:")
    ir_family = Counter()
    for token in all_tokens:
        for match in re.finditer(r'(i+)r', token):
            n_strokes = len(match.group(1))
            ir_family[n_strokes] += 1

    for n in sorted(ir_family.keys()):
        name = 'i'*n + 'r'
        print(f"    {name:8s} (={n}): {ir_family[n]:6d}")

    # KEY QUESTION: Does 2 (aiin) dominate over 1 (ain)?
    print(f"\n  FREQUENCY RATIO ANALYSIS:")
    if ain_family.get(1, 0) > 0 and ain_family.get(2, 0) > 0:
        ratio = ain_family[2] / ain_family[1]
        print(f"    aiin/ain ratio: {ratio:.2f}")
        print(f"    In pharma: 2 drachms is the MOST COMMON dose")
        print(f"    In pharma: 'ana' (equal parts) typically implies 2+ items")
        if ratio > 1.5:
            print(f"    → CONSISTENT with 2 being the most common dose quantity")
        else:
            print(f"    → NOT consistent with standard dosing")

    return ain_family, in_family


# ══════════════════════════════════════════
# TEST 2: DO "NUMBERS" FOLLOW INGREDIENTS?
# ══════════════════════════════════════════
def test_number_position(lines):
    print()
    print("=" * 70)
    print("TEST 2: DO AIN/AIIN APPEAR AFTER INGREDIENT-LIKE TOKENS?")
    print("=" * 70)
    print()

    with open(LOGOGRAMS_PATH, 'r', encoding='utf-8') as f:
        logo_data = json.load(f)
    logograms = {}
    for eva, info in logo_data.items():
        if isinstance(info, dict) and info.get("latin"):
            logograms[eva.lower()] = info["latin"].lower()
        elif isinstance(info, str):
            logograms[eva.lower()] = info.lower()

    # What comes BEFORE ain/aiin/aiiin?
    number_roots = {"ain", "aiin", "aiiin"}

    before_number = Counter()
    after_number = Counter()
    before_number_decoded = Counter()

    for line in lines:
        words = line["words"]
        for i, w in enumerate(words):
            _, _, root = extract_root(w)
            if root in number_roots:
                if i > 0:
                    prev = words[i-1]
                    before_number[prev] += 1
                    _, ppfx, proot = extract_root(prev)
                    if proot in logograms:
                        before_number_decoded[logograms[proot]] += 1
                    else:
                        before_number_decoded[f"[{proot}]"] += 1
                if i + 1 < len(words):
                    after_number[words[i+1]] += 1

    print("  WHAT COMES BEFORE ain/aiin/aiiin (raw EVA):")
    for w, c in before_number.most_common(20):
        print(f"    {w:20s} x{c:4d}")

    print(f"\n  WHAT COMES BEFORE (decoded where possible):")
    for w, c in before_number_decoded.most_common(20):
        print(f"    {w:20s} x{c:4d}")

    print(f"\n  WHAT COMES AFTER ain/aiin/aiiin:")
    for w, c in after_number.most_common(15):
        print(f"    {w:20s} x{c:4d}")

    # Do they appear at specific LINE positions?
    print(f"\n  LINE POSITION of ain/aiin/aiiin:")
    pos = Counter()
    for line in lines:
        words = line["words"]
        n = len(words)
        for i, w in enumerate(words):
            _, _, root = extract_root(w)
            if root in number_roots:
                rel = i / max(n - 1, 1)
                if rel < 0.2:
                    pos["0-20%"] += 1
                elif rel < 0.4:
                    pos["20-40%"] += 1
                elif rel < 0.6:
                    pos["40-60%"] += 1
                elif rel < 0.8:
                    pos["60-80%"] += 1
                else:
                    pos["80-100%"] += 1

    for p in ["0-20%", "20-40%", "40-60%", "60-80%", "80-100%"]:
        print(f"    {p}: {pos[p]:5d}")


# ══════════════════════════════════════════
# TEST 3: ZODIAC SECTIONS — SPECIAL PATTERNS?
# ══════════════════════════════════════════
def test_zodiac(lines):
    print()
    print("=" * 70)
    print("TEST 3: ZODIAC SECTIONS — What's different about them?")
    print("=" * 70)
    print()

    zodiac_lines = [l for l in lines if l["section"] == "Z"]
    astro_lines = [l for l in lines if l["section"] == "A"]
    pharma_lines = [l for l in lines if l["section"] == "S"]
    herbal_lines = [l for l in lines if l["section"] == "H"]

    print(f"  Zodiac lines: {len(zodiac_lines)} (section Z)")
    print(f"  Astro lines:  {len(astro_lines)} (section A)")

    # Vocabulary comparison: what tokens are UNIQUE to zodiac?
    zodiac_vocab = Counter()
    for l in zodiac_lines:
        for w in l["words"]:
            zodiac_vocab[w] += 1

    other_vocab = Counter()
    for l in lines:
        if l["section"] != "Z":
            for w in l["words"]:
                other_vocab[w] += 1

    # Tokens that appear in zodiac but NOT elsewhere
    zodiac_unique = {w: c for w, c in zodiac_vocab.items()
                     if w not in other_vocab and c >= 2}

    print(f"\n  Tokens UNIQUE to zodiac (not found elsewhere, freq >= 2):")
    for w, c in sorted(zodiac_unique.items(), key=lambda x: -x[1])[:20]:
        print(f"    {w:20s} x{c:4d}")

    # Tokens much MORE frequent in zodiac than elsewhere
    print(f"\n  Tokens ENRICHED in zodiac (>3x expected rate):")
    total_zodiac = sum(len(l["words"]) for l in zodiac_lines)
    total_other = sum(len(l["words"]) for l in lines if l["section"] != "Z")

    enriched = []
    for w, zc in zodiac_vocab.items():
        oc = other_vocab.get(w, 0)
        z_rate = zc / max(total_zodiac, 1)
        o_rate = oc / max(total_other, 1)
        if o_rate > 0 and z_rate / o_rate > 3 and zc >= 5:
            enriched.append((w, zc, oc, z_rate / o_rate))

    enriched.sort(key=lambda x: -x[3])
    for w, zc, oc, ratio in enriched[:20]:
        print(f"    {w:20s} zodiac={zc:4d} other={oc:4d} enrichment={ratio:.1f}x")

    # Do zodiac sections have MORE or FEWER "numbers" (ain/aiin/aiiin)?
    print(f"\n  'NUMBER' TOKENS BY SECTION:")
    number_roots = {"ain", "aiin", "aiiin"}
    for section_name, section_lines in [("Z (zodiac)", zodiac_lines),
                                         ("A (astro)", astro_lines),
                                         ("S (pharma)", pharma_lines),
                                         ("H (herbal)", herbal_lines)]:
        total = sum(len(l["words"]) for l in section_lines)
        number_count = 0
        for l in section_lines:
            for w in l["words"]:
                _, _, root = extract_root(w)
                if root in number_roots:
                    number_count += 1
        rate = 100 * number_count / max(total, 1)
        print(f"    {section_name:15s}: {number_count:5d}/{total:6d} = {rate:.2f}%")

    # Show zodiac folio list
    zodiac_folios = sorted(set(l["folio"] for l in zodiac_lines))
    print(f"\n  Zodiac folios: {zodiac_folios}")

    # Show sample zodiac lines
    print(f"\n  SAMPLE ZODIAC LINES:")
    for l in zodiac_lines[:15]:
        print(f"    [{l['folio']}] {' '.join(l['words'][:12])}")


# ══════════════════════════════════════════
# TEST 4: GALLOWS AS QUANTITY MARKERS
# ══════════════════════════════════════════
def test_gallows_numbers(lines):
    print()
    print("=" * 70)
    print("TEST 4: GALLOWS AS QUANTITY MARKERS")
    print("=" * 70)
    print()
    print("  If gallows (p, t, k, f) encode weight units:")
    print("  p = Rx/recipe? or libra(pound)?")
    print("  t = section? or uncia(ounce)?")
    print("  k = silent? or drachma(dram)?")
    print("  f = rare? or scrupulum(scruple)?")
    print()

    all_tokens = [w for line in lines for w in line["words"]]

    # For each gallows, what ROOT follows it?
    gallows_roots = defaultdict(Counter)
    gallows_total = Counter()
    no_gallows_roots = Counter()

    for token in all_tokens:
        if len(token) > 1 and token[0] in "ptfk":
            gallows = token[0]
            rest = token[1:]
            _, _, root = extract_root(rest)
            gallows_roots[gallows][root] += 1
            gallows_total[gallows] += 1
        else:
            _, _, root = extract_root(token)
            no_gallows_roots[root] += 1

    for g in "ptfk":
        print(f"\n  GALLOWS '{g}' ({gallows_total[g]} tokens):")
        print(f"    Top roots after '{g}':")
        for root, count in gallows_roots[g].most_common(10):
            # Does this root also appear WITHOUT the gallows?
            without = no_gallows_roots.get(root, 0)
            ratio = count / max(without, 1)
            print(f"      {root:15s}: {count:5d} (without {g}: {without:5d}, ratio: {ratio:.2f})")

    # KEY TEST: do gallows appear near "number" tokens?
    print(f"\n  GALLOWS NEAR 'NUMBER' TOKENS (ain/aiin/aiiin):")
    number_roots = {"ain", "aiin", "aiiin"}

    gallows_near_number = Counter()
    for line in lines:
        words = line["words"]
        for i, w in enumerate(words):
            _, _, root = extract_root(w)
            if root in number_roots:
                # Check neighbors for gallows
                for j in range(max(0, i-2), min(len(words), i+3)):
                    if j != i and len(words[j]) > 1 and words[j][0] in "ptfk":
                        gallows_near_number[words[j][0]] += 1

    total_numbers = sum(1 for line in lines for w in line["words"]
                       if extract_root(w)[2] in number_roots)
    print(f"    Total number tokens: {total_numbers}")
    for g in "ptfk":
        c = gallows_near_number[g]
        print(f"    '{g}' within 2 tokens of number: {c} ({100*c/max(total_numbers,1):.1f}%)")


# ══════════════════════════════════════════
# TEST 5: THE "QUANTITY + INGREDIENT" PATTERN
# ══════════════════════════════════════════
def test_quantity_ingredient(lines):
    print()
    print("=" * 70)
    print("TEST 5: QUANTITY + INGREDIENT PATTERN SEARCH")
    print("=" * 70)
    print()
    print("  Medieval recipe pattern: 'Rx [ingredient] [quantity], [ingredient] [quantity]'")
    print("  Or: '[quantity] [ingredient]', e.g., 'ii ℥ olei' (2 ounces of oil)")
    print()

    number_roots = {"ain", "aiin", "aiiin"}

    # V25 winner: aiin=aqua, edy=oleum, eey=mel, al=sal
    # If these are ingredients, do numbers appear near them?

    ingredient_roots = {"edy", "aiin", "eey", "al", "eedy", "eol", "eor"}

    # Check: [ingredient_root] followed by [number_root] or vice versa
    ingr_then_num = 0
    num_then_ingr = 0
    ingr_total = 0
    num_total = 0

    for line in lines:
        words = line["words"]
        for i in range(len(words) - 1):
            _, _, r1 = extract_root(words[i])
            _, _, r2 = extract_root(words[i+1])

            if r1 in ingredient_roots:
                ingr_total += 1
                if r2 in number_roots:
                    ingr_then_num += 1
            if r1 in number_roots:
                num_total += 1
                if r2 in ingredient_roots:
                    num_then_ingr += 1

    print(f"  Ingredient → Number: {ingr_then_num}/{ingr_total} ({100*ingr_then_num/max(ingr_total,1):.1f}%)")
    print(f"  Number → Ingredient: {num_then_ingr}/{num_total} ({100*num_then_ingr/max(num_total,1):.1f}%)")

    # BUT WAIT — what if the NUMBERS are embedded differently?
    # What if the i-count within the SAME token as the ingredient IS the quantity?
    # E.g., "sheedy" = sh + eed + y: the "ee" could be a doubled vowel = quantity 2?

    print(f"\n  ALTERNATIVE: Quantity embedded in vowel repetition?")
    print(f"  Tokens with doubled/tripled vowels:")

    doubled_vowels = Counter()
    for token in [w for line in lines for w in line["words"]]:
        for vowel in "aeo":
            for n in [3, 2]:
                pattern = vowel * n
                if pattern in token:
                    doubled_vowels[(vowel, n)] += 1
                    break

    print(f"    {'Pattern':>10s} {'Count':>8s}")
    for (vowel, n), count in sorted(doubled_vowels.items(), key=lambda x: -x[1]):
        print(f"    {vowel*n:>10s} {count:8d}")

    # Tripled vowels are rare — suggests doubling has a function
    # But tripling exists in 'eee' — could be "3"?

    # CRUCIAL: Compare single vs double vs triple
    print(f"\n  VOWEL REPETITION AS QUANTITY:")
    all_tokens = [w for line in lines for w in line["words"]]

    for base_suffix in ["dy", "ey", "ol", "or"]:
        print(f"\n    Suffix -{base_suffix}:")
        for n_vowel in range(1, 4):
            pattern = "e" * n_vowel + base_suffix
            count = sum(1 for t in all_tokens
                       if extract_root(t)[2] == pattern)
            count_with_prefix = sum(1 for t in all_tokens
                                   if t.endswith(pattern))
            print(f"      {'e'*n_vowel + base_suffix:>8s}: as root {count:5d}, in token {count_with_prefix:5d}")


# ══════════════════════════════════════════
# TEST 6: ANA HYPOTHESIS — "EQUAL PARTS"
# ══════════════════════════════════════════
def test_ana_hypothesis(lines):
    print()
    print("=" * 70)
    print("TEST 6: ANA HYPOTHESIS — Are quantities implicit via 'equal parts'?")
    print("=" * 70)
    print()
    print("  In the Antidotarium Nicolai, 'ana' (ā/āā) means 'of each'.")
    print("  If the Voynich uses 'ana' extensively, most recipes just say")
    print("  'equal parts of X, Y, Z' without explicit quantities.")
    print()

    # How many lines have REPEATED tokens (suggesting list of equal ingredients)?
    list_lines = 0
    total_lines = len(lines)

    for line in lines:
        words = line["words"]
        roots = [extract_root(w)[2] for w in words]
        root_counts = Counter(roots)
        # A list pattern: same structure repeated
        # E.g., "sheedy sheey sheal" = [M]edy [M]eey [M]al = list of raw materials
        prefixed_same = Counter()
        for w in words:
            _, pfx, root = extract_root(w)
            if pfx:
                prefixed_same[pfx] += 1

        # If a prefix appears 3+ times in one line, it's a LIST
        max_repeat = max(prefixed_same.values()) if prefixed_same else 0
        if max_repeat >= 3:
            list_lines += 1

    print(f"  Lines with 3+ tokens sharing a prefix (lists): {list_lines}/{total_lines} ({100*list_lines/total_lines:.1f}%)")

    # Ingredient list pattern: sh+X sh+Y sh+Z or ch+X ch+Y ch+Z
    print(f"\n  INGREDIENT LIST DETECTION:")
    sh_lists = 0
    ch_lists = 0
    qo_lists = 0
    for line in lines:
        words = line["words"]
        sh_count = sum(1 for w in words if w.startswith("sh") and len(w) > 2)
        ch_count = sum(1 for w in words if w.startswith("ch") and len(w) > 2)
        qo_count = sum(1 for w in words if w.startswith("qo") and len(w) > 2)
        if sh_count >= 3:
            sh_lists += 1
        if ch_count >= 3:
            ch_lists += 1
        if qo_count >= 3:
            qo_lists += 1

    print(f"    Lines with 3+ sh- tokens (raw material lists):  {sh_lists}")
    print(f"    Lines with 3+ ch- tokens (product lists):       {ch_lists}")
    print(f"    Lines with 3+ qo- tokens ('cum' compound lists): {qo_lists}")

    # Show example "list" lines
    print(f"\n  EXAMPLE LIST LINES (pharma sections):")
    shown = 0
    for line in lines:
        if shown >= 10:
            break
        if line["section"] not in ("S", "P"):
            continue
        words = line["words"]
        sh_count = sum(1 for w in words if w.startswith("sh") and len(w) > 2)
        ch_count = sum(1 for w in words if w.startswith("ch") and len(w) > 2)
        if sh_count >= 3 or ch_count >= 3:
            print(f"    [{line['folio']}] {' '.join(words[:15])}")
            shown += 1


# ══════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════
if __name__ == "__main__":
    print("V25b: THE NUMBER PROBLEM & ZODIAC CONNECTION")
    print("=" * 70)
    print()

    lines = parse_lines_eva()
    print(f"Loaded {len(lines)} lines, {sum(len(l['words']) for l in lines)} tokens")
    print()

    ain_family, in_family = test_i_strokes(lines)
    test_number_position(lines)
    test_zodiac(lines)
    test_gallows_numbers(lines)
    test_quantity_ingredient(lines)
    test_ana_hypothesis(lines)

    print()
    print("=" * 70)
    print("SYNTHESIS: THE NUMBER PROBLEM")
    print("=" * 70)
    print()
    print("  The manuscript MUST encode quantities somehow.")
    print("  The question is: WHERE and HOW?")
    print()

    # Save key findings
    results = {
        "ain_family": dict(ain_family),
        "in_family": dict(in_family),
    }
    with open(RESULTS / "v25b_numbers_zodiac.json", 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f"  Results saved to {RESULTS / 'v25b_numbers_zodiac.json'}")
