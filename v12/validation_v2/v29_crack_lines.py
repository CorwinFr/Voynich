#!/usr/bin/env python3
"""
V29 — Crack Lines: Find the BEST decodable lines in the entire corpus.

Three attacks simultaneously:
1. Find lines where ALL tokens use known suffixes (perfect decode)
2. Decode zodiac nymph labels (short, verifiable against body parts)
3. Decode f103r lines containing "coque" pattern

One perfect line = proof of concept.
"""
import sys, re, json
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

BASE = Path("d:/Github/Voynich")
DECODED_FILE = BASE / "v12/output/VOYNICH_DECODE_V12_INGREDIENTS.txt"
RESULTS = BASE / "v12/validation_v2/results"
TIRONIAN_PATH = BASE / "data/tironian/schmitz_index_full.json"

PREFIXES_ORDER = ["qok", "qot", "qo", "ok", "ot", "ol", "da", "ch", "sh",
                  "d", "y", "r", "p", "l", "t", "f", "k"]
PREFIXES_ORDER.sort(key=len, reverse=True)

# V27 confirmed substance mappings
SUBSTANCE = {
    "ol": "oleum", "or": "hiera", "al": "sal", "ar": "aqua",
    "ody": "acetum", "ckhy": "cera", "chy": "mel",
    "os": "succus", "am": "ana",
}

# Logograms from V21
LOGOGRAMS_EXTRA = {
    "dy": "et", "y": "·",  # structural
}

PREFIX_LATIN = {
    "": "", "d": "in", "da": "in", "qo": "cum", "qok": "cum", "qot": "cum",
    "y": "de", "r": "re", "ol": "ex", "l": "per",
    "ch": "[P]", "sh": "[M]", "ok": "", "ot": "", "f": "", "t": "§", "k": "",
}
GALLOWS_L = {"p": "Rx", "t": "§", "k": "", "f": "Rx", "": ""}


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
    w = token
    gallows = ""
    if len(w) > 1 and w[0] in "ptf":
        gallows = w[0]; w = w[1:]

    prefix = ""
    for pfx in PREFIXES_ORDER:
        if w.startswith(pfx) and len(w) > len(pfx):
            prefix = pfx; w = w[len(pfx):]; break

    if w.startswith('k') and len(w) > 1:
        prefix += "+k" if prefix else "k"; w = w[1:]

    # Unit pattern
    um = re.match(r'^a?(i+)([nr])$', w)
    if um:
        return {"gallows": gallows, "prefix": prefix, "e_count": 0,
                "core": "UNIT", "unit_n": len(um.group(1)), "unit_type": um.group(2),
                "known": True}

    # E-count
    e_count = 0
    while w.startswith('e') and len(w) > 1:
        rem = w[1:]
        if rem in SUBSTANCE or rem in LOGOGRAMS_EXTRA or rem in ("dy","ey","ol","or","al","ar","os","ody","ckhy","chy","am"):
            e_count += 1; w = rem
        elif len(rem) >= 2 and rem[0] != 'e':
            e_count += 1; w = rem
        else:
            break

    known = w in SUBSTANCE or w in LOGOGRAMS_EXTRA or w == "UNIT"
    return {"gallows": gallows, "prefix": prefix, "e_count": e_count,
            "core": w, "unit_n": 0, "unit_type": "", "known": known}


def decode_token(token):
    """Full human-readable decode."""
    d = decompose(token)
    parts = []

    g = GALLOWS_L.get(d["gallows"], "")
    if g: parts.append(g)

    pfx = d["prefix"].split("+")[0]
    p = PREFIX_LATIN.get(pfx, pfx)
    if p and p not in ("[P]", "[M]"):
        parts.append(p)
    elif p in ("[P]", "[M]"):
        parts.append(p)

    if d["core"] == "UNIT":
        sym = "℥" if d["unit_type"] == "n" else "ʒ"
        parts.append(f"{d['unit_n']}{sym}")
    elif d["core"] in SUBSTANCE:
        s = SUBSTANCE[d["core"]]
        if d["e_count"] > 0:
            parts.append(f"{d['e_count']}×{s}")
        else:
            parts.append(s)
    elif d["core"] in LOGOGRAMS_EXTRA:
        parts.append(LOGOGRAMS_EXTRA[d["core"]])
    else:
        if d["e_count"] > 0:
            parts.append(f"{d['e_count']}×?{d['core']}?")
        else:
            parts.append(f"?{d['core']}?")

    return " ".join(parts), d["known"]


def decode_line(words):
    """Decode a full line, return (decoded_string, known_count, total_count)."""
    parts = []
    known = 0
    for w in words:
        dec, is_known = decode_token(w)
        parts.append(dec)
        if is_known:
            known += 1
    return " . ".join(parts), known, len(words)


# ══════════════════════════════════════════
# ATTACK 1: Find perfect lines (100% known suffixes)
# ══════════════════════════════════════════
def attack_perfect_lines(lines):
    print("=" * 70)
    print("ATTACK 1: PERFECT LINES (100% known suffixes)")
    print("=" * 70)
    print()

    results = []
    for line in lines:
        decoded, known, total = decode_line(line["words"])
        if total >= 3:  # At least 3 tokens
            pct = 100 * known / total
            results.append({
                "folio": line["folio"], "section": line["section"],
                "eva": " ".join(line["words"]),
                "decoded": decoded,
                "known_pct": pct, "known": known, "total": total,
            })

    # Sort by known% then by length
    results.sort(key=lambda x: (-x["known_pct"], -x["total"]))

    # Show best lines
    print("  BEST DECODED LINES (100% known, longest first):")
    shown = 0
    for r in results:
        if r["known_pct"] < 100:
            break
        if r["total"] < 4:
            continue
        if shown >= 30:
            break

        print(f"\n    [{r['folio']}|{r['section']}] ({r['total']} tokens)")
        print(f"      EVA: {r['eva']}")
        print(f"      LAT: {r['decoded']}")
        shown += 1

    # Stats
    perfect = sum(1 for r in results if r["known_pct"] == 100)
    good = sum(1 for r in results if r["known_pct"] >= 80)
    print(f"\n  STATS:")
    print(f"    100% decoded lines (3+ tokens): {perfect}")
    print(f"    80%+ decoded lines (3+ tokens): {good}")
    print(f"    Total lines (3+ tokens): {len(results)}")

    # Best LONG lines (6+ tokens, 80%+ known)
    print(f"\n  BEST LONG LINES (6+ tokens, 80%+ known):")
    shown = 0
    for r in results:
        if r["total"] >= 6 and r["known_pct"] >= 80 and shown < 20:
            print(f"\n    [{r['folio']}|{r['section']}] ({r['known_pct']:.0f}%, {r['total']}tok)")
            print(f"      EVA: {r['eva'][:110]}")
            print(f"      LAT: {r['decoded'][:110]}")
            shown += 1

    return results


# ══════════════════════════════════════════
# ATTACK 2: Zodiac nymph labels
# ══════════════════════════════════════════
def attack_zodiac_labels(lines):
    print()
    print("=" * 70)
    print("ATTACK 2: ZODIAC NYMPH LABELS")
    print("=" * 70)
    print()

    zodiac_info = {
        "F70V1": ("Pisces", "pedes", "feet"),
        "F70V2": ("Aries", "caput", "head"),
        "F71R": ("Taurus", "collum/guttur", "neck/throat"),
        "F71V": ("Gemini", "bracchia/manus", "arms/hands"),
        "F72R1": ("Cancer", "pectus/stomachus", "chest/stomach"),
        "F72R2": ("Leo", "cor/dorsum", "heart/back"),
        "F72R3": ("Virgo", "venter/intestina", "intestines"),
        "F72V1": ("Libra", "renes/lumbi", "kidneys/loins"),
        "F72V2": ("Scorpio", "genitalia/vesica", "genitals/bladder"),
        "F72V3": ("Sagittarius", "femora/coxae", "thighs/hips"),
        "F73R": ("Capricorn", "genua", "knees"),
        "F73V": ("Aquarius", "crura/tibiae", "legs/shins"),
    }

    print("  Zodiac short lines (1-4 tokens = likely labels):")
    print()

    for zf in sorted(zodiac_info.keys()):
        sign, latin_body, eng_body = zodiac_info[zf]
        z_lines = [l for l in lines if l["folio"] == zf]

        print(f"  {zf} = {sign} ({latin_body} = {eng_body}):")

        # Get ALL lines, sorted by length (short = labels)
        for l in sorted(z_lines, key=lambda x: len(x["words"])):
            if len(l["words"]) > 4:
                continue
            eva = " ".join(l["words"])
            decoded, known, total = decode_line(l["words"])
            pct_str = f"{100*known/total:.0f}%" if total > 0 else ""

            print(f"    {eva:35s} → {decoded:50s} [{pct_str}]")

        print()


# ══════════════════════════════════════════
# ATTACK 3: f103r "coque" lines
# ══════════════════════════════════════════
def attack_f103r(lines):
    print()
    print("=" * 70)
    print("ATTACK 3: F103R — The recipe folio")
    print("=" * 70)
    print()

    # Find f103r lines and decode
    f103_lines = [l for l in lines if l["folio"].upper() in ("F103R", "F103V")]

    # Score each line
    scored = []
    for l in f103_lines:
        decoded, known, total = decode_line(l["words"])
        pct = 100 * known / total if total > 0 else 0
        scored.append({
            "folio": l["folio"], "eva": " ".join(l["words"]),
            "decoded": decoded, "pct": pct, "total": total,
        })

    scored.sort(key=lambda x: (-x["pct"], -x["total"]))

    print(f"  F103R/V: {len(scored)} lines")
    print(f"\n  BEST F103R LINES (highest decode %):")
    for s in scored[:25]:
        print(f"\n    [{s['folio']}] ({s['pct']:.0f}%, {s['total']}tok)")
        print(f"      EVA: {s['eva'][:110]}")
        print(f"      LAT: {s['decoded'][:110]}")


# ══════════════════════════════════════════
# CROSS-CHECK: Do the 3 attacks converge?
# ══════════════════════════════════════════
def cross_check(all_results, lines):
    print()
    print("=" * 70)
    print("CROSS-CHECK: Pattern convergence")
    print("=" * 70)

    # What decoded PHRASES appear across multiple attacks?
    # Extract 2-gram and 3-gram decoded patterns from best lines
    patterns = Counter()
    for r in all_results:
        if r["known_pct"] < 80:
            continue
        parts = r["decoded"].split(" . ")
        for i in range(len(parts) - 1):
            bigram = f"{parts[i]} → {parts[i+1]}"
            if "?" not in bigram:
                patterns[bigram] += 1

        for i in range(len(parts) - 2):
            trigram = f"{parts[i]} → {parts[i+1]} → {parts[i+2]}"
            if "?" not in trigram:
                patterns[trigram] += 1

    print(f"\n  MOST COMMON DECODED PHRASES (from 80%+ lines):")
    print(f"  These are the 'sentences' of the Voynich:\n")
    for pattern, count in patterns.most_common(30):
        # Translate to readable
        readable = pattern.replace("[P]", "PROD.").replace("[M]", "MAT.")
        print(f"    {readable:60s} x{count:4d}")

    # Recipe-like sequences
    print(f"\n  RECIPE-LIKE SEQUENCES:")
    recipe_patterns = [(p, c) for p, c in patterns.most_common(100)
                       if any(kw in p for kw in ("Rx", "cum", "in ", "℥", "oleum", "aqua", "sal", "mel"))]
    for p, c in recipe_patterns[:20]:
        readable = p.replace("[P]", "PROD.").replace("[M]", "MAT.")
        print(f"    {readable:60s} x{c:4d}")


# ══════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════
if __name__ == "__main__":
    print("V29 CRACK LINES — Three simultaneous attacks")
    print("=" * 70)
    print()

    lines = parse_lines_eva()
    print(f"  {len(lines)} lines, {sum(len(l['words']) for l in lines)} tokens\n")

    all_results = attack_perfect_lines(lines)
    attack_zodiac_labels(lines)
    attack_f103r(lines)
    cross_check(all_results, lines)

    # Save
    best = [r for r in all_results if r["known_pct"] >= 80 and r["total"] >= 4][:100]
    with open(RESULTS / "v29_crack_lines.json", 'w', encoding='utf-8') as f:
        json.dump({"best_lines": best}, f, indent=2, ensure_ascii=False)

    print(f"\n  Results saved to {RESULTS / 'v29_crack_lines.json'}")
