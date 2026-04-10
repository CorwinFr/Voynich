#!/usr/bin/env python3
"""
V28 — Volvelle & Zodiac: The Cross-Reference System

The apothecary needs:
1. Volvelle (f57v) → what TYPE of preparation for today's lunar day
2. Zodiac → which body part/condition for current zodiac sign
3. Recipe section → specific preparation matching both

This script applies the V26 quantity notation model to f57v and zodiac
to decode the cross-reference system.
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

PREFIX_MEANING = {
    "": "", "d": "IN", "da": "IN", "qo": "CUM", "qok": "CUM", "qot": "CUM",
    "y": "DE", "r": "RE", "ol": "EX", "l": "PER",
    "ch": "[P]", "sh": "[M]", "ok": "", "ot": "", "f": "", "t": "§", "k": "",
}
GALLOWS_M = {"p": "Rx", "t": "§", "k": "", "f": "Rx", "": ""}

# V27 substance proposals
SUBSTANCE = {
    "ol": "OLEUM", "or": "HIERA", "al": "SAL", "ar": "AQUA",
    "ody": "ACETUM", "ckhy": "CERA", "chy": "MEL",
    "dy": "RES", "y": "·", "am": "ANA", "os": "SUCCUS",
}


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


def decompose(token):
    result = {"raw": token, "gallows": "", "prefix": "", "e_count": 0,
              "core": "", "unit_n": 0, "unit_type": ""}
    w = token
    if len(w) > 1 and w[0] in "ptf":
        result["gallows"] = w[0]; w = w[1:]
    for pfx in PREFIXES_ORDER:
        if w.startswith(pfx) and len(w) > len(pfx):
            result["prefix"] = pfx; w = w[len(pfx):]; break
    if w.startswith('k') and len(w) > 1:
        result["prefix"] += "+k" if result["prefix"] else "k"; w = w[1:]

    um = re.match(r'^a?(i+)([nr])$', w)
    if um:
        result["unit_n"] = len(um.group(1)); result["unit_type"] = um.group(2)
        result["core"] = "UNIT"; return result

    e_count = 0
    valid = {"dy","ey","ol","or","al","ar","os","eo","y","o","s","l","r",
             "ody","ckhy","chy","chey","chol","chor","cthy"}
    while w.startswith('e') and len(w) > 1:
        rem = w[1:]
        if rem in valid or (len(rem) >= 2 and rem[0] != 'e'):
            e_count += 1; w = rem
        else: break
    result["e_count"] = e_count; result["core"] = w
    return result


def decode_token_full(token):
    """Human-readable decode using V26+V27 model."""
    d = decompose(token)
    parts = []

    g = GALLOWS_M.get(d["gallows"], "")
    if g: parts.append(g)

    pfx = d["prefix"].split("+")[0]
    p = PREFIX_MEANING.get(pfx, pfx.upper())
    if p: parts.append(p)

    if d["core"] == "UNIT":
        sym = "℥" if d["unit_type"] == "n" else "ʒ"
        parts.append(f"{d['unit_n']}{sym}")
    elif d["core"] in SUBSTANCE:
        s = SUBSTANCE[d["core"]]
        if d["e_count"] > 0:
            parts.append(f"{d['e_count']}×{s}")
        else:
            parts.append(s)
    else:
        if d["e_count"] > 0:
            parts.append(f"{d['e_count']}×[{d['core']}]")
        else:
            parts.append(f"[{d['core']}]")

    return ' '.join(parts)


# ══════════════════════════════════════════
# F57V VOLVELLE DECODE
# ══════════════════════════════════════════
def decode_volvelle(lines):
    print("=" * 70)
    print("F57V VOLVELLE — Decoded with V26+V27 model")
    print("=" * 70)

    f57v = [l for l in lines if l["folio"].upper() == "F57V"]

    print(f"\n  {len(f57v)} text lines on f57v\n")

    all_tokens = []
    for line in f57v:
        eva = ' '.join(line["words"])
        decoded = [decode_token_full(w) for w in line["words"]]
        decoded_str = ' . '.join(decoded)

        print(f"  EVA: {eva}")
        print(f"  DEC: {decoded_str}")
        print()

        all_tokens.extend(line["words"])

    # Suffix analysis of volvelle
    print(f"\n  SUFFIX ANALYSIS of f57v:")
    suffix_counter = Counter()
    for t in all_tokens:
        d = decompose(t)
        suffix_counter[d["core"]] += 1

    print(f"  {'Suffix':>10s} {'Count':>6s} {'Substance':>12s}")
    for core, count in suffix_counter.most_common(15):
        s = SUBSTANCE.get(core, "?")
        print(f"  {core:>10s} {count:6d} {s:>12s}")

    # What's special about f57v compared to S section?
    print(f"\n  F57V SPECIFICITY:")
    corpus_suffixes = Counter()
    for l in lines:
        if l["section"] == "S":
            for w in l["words"]:
                d = decompose(w)
                corpus_suffixes[d["core"]] += 1

    total_v = sum(suffix_counter.values())
    total_s = sum(corpus_suffixes.values())
    for core, count in suffix_counter.most_common(10):
        v_rate = count / total_v
        s_rate = corpus_suffixes.get(core, 0) / max(total_s, 1)
        ratio = v_rate / max(s_rate, 0.0001)
        marker = "** ENRICHED **" if ratio > 2 else ""
        print(f"    {core:>10s}: f57v={100*v_rate:.1f}%  S={100*s_rate:.1f}%  ratio={ratio:.1f}x {marker}")


# ══════════════════════════════════════════
# ZODIAC DECODE — Body parts?
# ══════════════════════════════════════════
def decode_zodiac(lines):
    print()
    print("=" * 70)
    print("ZODIAC — Decoded by folio (each = one zodiac sign)")
    print("=" * 70)

    zodiac_signs = {
        "F70V1": "Pisces?", "F70V2": "Aries", "F71R": "Taurus",
        "F71V": "Gemini", "F72R1": "Cancer", "F72R2": "Leo",
        "F72R3": "Virgo", "F72V1": "Libra", "F72V2": "Scorpio",
        "F72V3": "Sagittarius", "F73R": "Capricorn?", "F73V": "Aquarius?",
    }

    body_parts = {
        "Aries": "CAPUT (head)", "Taurus": "COLLUM (neck/throat)",
        "Gemini": "BRACCHIA (arms)", "Cancer": "PECTUS (chest/stomach)",
        "Leo": "COR (heart/back)", "Virgo": "VENTER (intestines)",
        "Libra": "RENES (kidneys)", "Scorpio": "GENITALIA",
        "Sagittarius": "FEMORA (thighs)", "Capricorn?": "GENUA (knees)",
        "Aquarius?": "CRURA (legs)", "Pisces?": "PEDES (feet)",
    }

    folio_suffix_profiles = {}

    for zf in sorted(set(l["folio"] for l in lines if l["section"] == "Z")):
        sign = zodiac_signs.get(zf, "?")
        body = body_parts.get(sign, "?")

        z_lines = [l for l in lines if l["folio"] == zf]
        tokens = [w for l in z_lines for w in l["words"]]

        # Suffix profile
        suffix_counter = Counter()
        prefix_counter = Counter()
        e_counts = Counter()
        unit_counts = Counter()

        for t in tokens:
            d = decompose(t)
            suffix_counter[d["core"]] += 1
            if d["prefix"]:
                prefix_counter[d["prefix"].split("+")[0]] += 1
            e_counts[d["e_count"]] += 1
            if d["core"] == "UNIT":
                unit_counts[d["unit_n"]] += 1

        folio_suffix_profiles[zf] = suffix_counter

        print(f"\n  {zf} = {sign} → {body}")
        print(f"    Tokens: {len(tokens)}, Unique suffixes: {len(suffix_counter)}")

        # Show sample decoded lines
        for l in z_lines[:3]:
            eva = ' '.join(l["words"][:10])
            dec = ' . '.join(decode_token_full(w) for w in l["words"][:10])
            print(f"    EVA: {eva}")
            print(f"    DEC: {dec}")

        # Top suffixes specific to this page
        top = suffix_counter.most_common(8)
        top_str = ', '.join(f"{SUBSTANCE.get(c,c)}({n})" for c, n in top)
        print(f"    Top: {top_str}")

    # Do different zodiac signs have DIFFERENT suffix profiles?
    print(f"\n\n  {'='*70}")
    print(f"  ZODIAC SUFFIX VARIATION (do signs differ?)")
    print(f"  {'='*70}")

    # Compare suffix distributions across zodiac pages
    key_suffixes = ["dy", "ol", "or", "al", "ar", "ody", "ckhy", "UNIT"]
    print(f"\n  {'Folio':>8s} {'Sign':>12s}", end="")
    for s in key_suffixes:
        label = SUBSTANCE.get(s, s)[:5]
        print(f" {label:>6s}", end="")
    print()

    for zf in sorted(folio_suffix_profiles.keys()):
        sign = zodiac_signs.get(zf, "?")
        sc = folio_suffix_profiles[zf]
        total = sum(sc.values())
        print(f"  {zf:>8s} {sign:>12s}", end="")
        for s in key_suffixes:
            rate = 100 * sc.get(s, 0) / max(total, 1)
            print(f" {rate:6.1f}", end="")
        print()


# ══════════════════════════════════════════
# THE OT- PREFIX: Body part marker?
# ══════════════════════════════════════════
def analyze_ot_prefix(lines):
    print()
    print("=" * 70)
    print("THE OT- PREFIX: Body part marker in zodiac?")
    print("=" * 70)

    # ot- is enriched in zodiac. Is it a body-part marker?
    # In zodiac: each page = different sign = different body part
    # If ot- = body part, different ot-SUFFIX combinations should dominate
    # on different zodiac pages

    zodiac_signs = {
        "F70V2": "Aries(head)", "F71R": "Taurus(neck)",
        "F71V": "Gemini(arms)", "F72R1": "Cancer(chest)",
        "F72R2": "Leo(heart)", "F72R3": "Virgo(intest)",
        "F72V1": "Libra(kidneys)", "F72V2": "Scorpio(genit)",
        "F72V3": "Sagit(thighs)", "F73R": "Capric(knees)",
    }

    print(f"\n  OT-tokens by zodiac page:")
    for zf in sorted(zodiac_signs.keys()):
        sign = zodiac_signs[zf]
        z_tokens = [w for l in lines if l["folio"] == zf for w in l["words"]]

        ot_tokens = [t for t in z_tokens if t.startswith("ot") and len(t) > 2]
        ot_counter = Counter(ot_tokens)

        print(f"\n    {zf} ({sign}):")
        for t, c in ot_counter.most_common(8):
            d = decompose(t)
            dec = decode_token_full(t)
            print(f"      {t:15s} x{c:2d}  → {dec}")

    # Compare: which ot-tokens are UNIQUE to each zodiac page?
    print(f"\n  OT-tokens UNIQUE to each zodiac page (not on other zodiac pages):")
    all_ot_by_page = {}
    for zf in zodiac_signs:
        z_tokens = [w for l in lines if l["folio"] == zf for w in l["words"]]
        all_ot_by_page[zf] = set(t for t in z_tokens if t.startswith("ot") and len(t) > 2)

    for zf in sorted(zodiac_signs.keys()):
        sign = zodiac_signs[zf]
        other_ot = set()
        for ozf in zodiac_signs:
            if ozf != zf:
                other_ot |= all_ot_by_page[ozf]
        unique = all_ot_by_page[zf] - other_ot
        if unique:
            dec_unique = [f"{t}→{decode_token_full(t)}" for t in sorted(unique)[:5]]
            print(f"    {zf} ({sign}): {', '.join(dec_unique)}")


# ══════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════
if __name__ == "__main__":
    print("V28 VOLVELLE & ZODIAC CROSS-REFERENCE")
    print("=" * 70)
    print()

    lines = parse_lines_eva()
    print(f"  {len(lines)} lines, {sum(len(l['words']) for l in lines)} tokens\n")

    decode_volvelle(lines)
    decode_zodiac(lines)
    analyze_ot_prefix(lines)

    print()
    print("=" * 70)
    print("V28 SYNTHESIS")
    print("=" * 70)
