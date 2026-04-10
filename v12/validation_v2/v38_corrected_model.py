#!/usr/bin/env python3
"""
V38 — Corrected Model: 5 fixes from expert review.

Fix 1: VERB only with clear verbal prefix (qo/d/ol/l/gallows). Others → INGREDIENT
Fix 2: l = cum (not per). 0 occurrences of "per" in Antidotarium Esdra.
Fix 3: t = tere (grind), not signa. t appears mid-recipe, not just line-initial.
Fix 4: Ambiguous -y/-dy tokens → INGREDIENT_NNN (names to identify)
Fix 5: Units in drachms (already done)
"""
import sys, re, json
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

BASE = Path("d:/Github/Voynich")
DECODED_FILE = BASE / "v12/output/VOYNICH_DECODE_V12_INGREDIENTS.txt"
RESULTS = BASE / "v12/validation_v2/results"

UNIT_RE = re.compile(r'^a?(i+)([nr])$')

SUBSTANCES = {
    "ol": "oleum", "al": "sal", "ar": "aqua",
    "ody": "acetum", "ckhy": "cera", "os": "succus", "am": "ana",
    "or": "UNK_or",
}

# FIX 2: l = cum (not per)
PREP = {
    "qo": "cum", "qok": "cum", "qot": "cum",
    "d": "in", "da": "in", "ol": "ex",
    "l": "cum",  # CORRECTED from "per"
    "y": "de", "r": "re",
    "ok": "", "ot": "", "k": "", "": "",
    "o": "", "s": "est", "sa": "", "od": "ad",
}

# VERB only with CLEAR verbal prefixes
VERB_PREFIXES = {"qo", "qok", "qot", "d", "da", "ol", "l"}

VERB_MAP = {
    "qo": "misce", "qok": "misce", "qot": "misce",
    "d": "coque", "da": "coque",
    "ol": "cola", "l": "cola",  # FIX 2: l=cum but l+y = cola (strain through)
}

# FIX 3: gallows meanings
GALLOWS = {
    "p": "Rx",      # recipe (take)
    "f": "Rx",      # recipe variant
    "t": "tere",    # CORRECTED from "signa" → tere (grind) or section marker
    "k": "",        # silent
}

ALL_OUTER = ["qok","qot","qo","ok","ot","ol","da","od","sa","d","y","r","o","s","l","k"]
ALL_OUTER.sort(key=len, reverse=True)
INNER_PFX = ["cth","ckh","cfh","ch","sh"]

_ingr = {}
_ingr_n = [0]
def get_ingredient(core):
    if core not in _ingr:
        _ingr_n[0] += 1
        _ingr[core] = f"INGR_{_ingr_n[0]:03d}"
    return _ingr[core]

_unk = {}
_unk_n = [0]
def get_unk(core):
    if core not in _unk:
        _unk_n[0] += 1
        _unk[core] = f"UNK_{_unk_n[0]}"
    return _unk[core]


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


def decode(token):
    parts = []
    cat = "UNK"
    w = token

    # Gallows
    gallows = ""
    if len(w) > 1 and w[0] in "ptf":
        gallows = w[0]; w = w[1:]

    # Recursive decomposition
    sub_parts, sub_cat = _decode_remainder(w, gallows)

    if gallows and sub_cat in ("VERB", "INGREDIENT"):
        gv = GALLOWS.get(gallows, "")
        if gv:
            parts.append(gv)
    elif gallows:
        gv = GALLOWS.get(gallows, "")
        if gv:
            parts.append(gv)

    parts.extend(sub_parts)
    cat = sub_cat
    return " ".join(p for p in parts if p), cat


def _decode_remainder(w, gallows=""):
    if not w or len(w) < 2:
        if len(w) == 1:
            m = {"o":"eo","l":"cum","r":"re","s":"est","d":"in",
                 "m":"cum","e":"e","n":"in","a":"a"}.get(w, w)
            return [m], "FUNC"
        return [], "EMPTY"

    # UNIT
    um = UNIT_RE.match(w)
    if um:
        n = len(um.group(1))
        sym = "drachm" if um.group(2) == "n" else "scruple"
        return [f"{n}{sym}"], "UNIT"

    # Direct substance
    if w in SUBSTANCES:
        return [SUBSTANCES[w]], "SUBST"

    # E-count + known
    e = 0; ew = w
    while ew.startswith('e') and len(ew) > 1: e += 1; ew = ew[1:]
    if e > 0:
        um2 = UNIT_RE.match(ew)
        if um2:
            n = len(um2.group(1))
            sym = "drachm" if um2.group(2) == "n" else "scruple"
            return [f"{e}x{n}{sym}"], "UNIT"
        if ew in SUBSTANCES:
            return [f"{e}x{SUBSTANCES[ew]}"], "SUBST"

    # Try prefix stripping
    for pfx in ALL_OUTER:
        if w.startswith(pfx) and len(w) > len(pfx):
            remainder = w[len(pfx):]

            # Inner prefix (sh/ch/cth)
            inner = ""
            for ipfx in INNER_PFX:
                if remainder.startswith(ipfx) and len(remainder) > len(ipfx):
                    inner = ipfx; remainder = remainder[len(ipfx):]; break

            # K-strip
            if remainder.startswith('k') and len(remainder) > 1:
                remainder = remainder[1:]

            # E-count on remainder
            e2 = 0
            while remainder.startswith('e') and len(remainder) > 1:
                e2 += 1; remainder = remainder[1:]

            qty = f"{e2}x" if e2 > 0 else ""
            state = "[M]" if inner == "sh" else "[P]" if inner in ("ch","cth","ckh","cfh") else ""
            prep = PREP.get(pfx, "")

            # UNIT in remainder
            um3 = UNIT_RE.match(remainder)
            if um3:
                n = len(um3.group(1))
                sym = "drachm" if um3.group(2) == "n" else "scruple"
                return [f"{prep} {qty}{n}{sym}".strip()], "UNIT"

            # SUBSTANCE in remainder
            if remainder in SUBSTANCES:
                s = SUBSTANCES[remainder]
                return [f"{prep} {state}{qty}{s}".strip()], "SUBST"

            # -y/-dy/-ey in remainder: FIX 1 — strict verb classification
            if remainder in ("y", "dy", "ey"):
                conn = " et" if remainder == "dy" else ""

                # WITH inner prefix (sh/ch/cth) → always SUBSTANCE/STATE
                if inner:
                    ingr = get_ingredient(f"{inner}+{remainder}")
                    return [f"{prep} {state}{qty}{ingr}{conn}".strip()], "INGREDIENT"

                # WITH gallows → VERB (Rx + action)
                if gallows:
                    verb = VERB_MAP.get(pfx, "fac")
                    return [f"{verb}{conn}"], "VERB"

                # WITH clear verbal prefix → VERB
                if pfx in VERB_PREFIXES:
                    verb = VERB_MAP.get(pfx, "misce")
                    e_str = f".{e2}" if e2 > 0 else ""
                    return [f"{verb}{e_str}{conn}"], "VERB"

                # FIX 4: Everything else → INGREDIENT (not verb!)
                ingr = get_ingredient(f"{pfx}+{remainder}")
                return [f"{prep} {qty}{ingr}{conn}".strip()], "INGREDIENT"

            # Known remainder after prefix
            sub_p, sub_c = _decode_remainder(remainder, gallows)
            if sub_c in ("UNIT","SUBST","VERB","INGREDIENT","FUNC"):
                if state:
                    return [f"{prep} {state}{' '.join(sub_p)}".strip()], sub_c
                elif prep:
                    return [f"{prep} {' '.join(sub_p)}".strip()], sub_c
                return sub_p, sub_c

    # Bare -y/-dy/-ey without any prefix
    if w in ("y","dy","ey"):
        if gallows:
            return [GALLOWS.get(gallows, "fac")], "VERB"
        ingr = get_ingredient(f"bare+{w}")
        conn = " et" if w == "dy" else ""
        return [f"{ingr}{conn}"], "INGREDIENT"

    # k + remainder
    if w.startswith('k') and len(w) > 1:
        sub_p, sub_c = _decode_remainder(w[1:], gallows)
        if sub_c != "UNK":
            return sub_p, sub_c

    # True unknown
    return [get_unk(w)], "UNK"


def main():
    print("V38 CORRECTED MODEL — 5 Expert Fixes Applied")
    print("="*70)

    lines = parse_lines()
    total = sum(len(l["words"]) for l in lines)
    print(f"  {len(lines)} lines, {total} tokens\n")

    stats = Counter()
    decoded_lines = []
    for line in lines:
        parts = []; cats = []
        for w in line["words"]:
            dec, cat = decode(w)
            parts.append(dec); cats.append(cat)
            stats[cat] += 1
        decoded_lines.append({
            "folio": line["folio"], "section": line["section"],
            "eva": " ".join(line["words"]),
            "decoded": "  ".join(parts), "cats": cats,
        })

    known = total - stats["UNK"]
    print("  CLASSIFICATION:")
    for cat, n in stats.most_common():
        print(f"    {cat:>12s}: {n:6d} ({100*n/total:.1f}%)")
    print(f"  {'KNOWN':>14s}: {known:6d} ({100*known/total:.1f}%)")

    # Verify verb ratio per section
    print(f"\n  VERB RATIO CHECK:")
    for sec_name, sec_code in [("S(pharma)","S"),("H(herbal)","H"),("B(balneo)","B")]:
        v = sum(1 for dl in decoded_lines if dl["section"]==sec_code for c in dl["cats"] if c=="VERB")
        s = sum(1 for dl in decoded_lines if dl["section"]==sec_code for c in dl["cats"] if c in ("SUBST","INGREDIENT"))
        u = sum(1 for dl in decoded_lines if dl["section"]==sec_code for c in dl["cats"] if c=="UNIT")
        ratio = (s+u)/max(v,1)
        print(f"    {sec_name}: verb={v} subst+ingr={s} unit={u} ratio={ratio:.1f}:1 {'OK' if 3<=ratio<=10 else '!'}")

    # Best lines
    scored = []
    for dl in decoded_lines:
        n = len(dl["cats"])
        k = sum(1 for c in dl["cats"] if c != "UNK")
        pct = 100*k/n if n else 0
        scored.append((pct, n, dl))
    scored.sort(key=lambda x: (-x[0], -x[1]))

    perfect = sum(1 for p,n,_ in scored if p==100 and n>=4)
    good = sum(1 for p,n,_ in scored if p>=80 and n>=5)
    print(f"\n  100% lines (4+tok): {perfect}")
    print(f"  80%+ lines (5+tok): {good}")

    # Show best pharma lines
    print(f"\n{'='*70}")
    print("BEST PHARMA RECIPES (S/P, 100%, 8+tok)")
    print(f"{'='*70}")
    shown = 0
    for pct, n, dl in scored:
        if shown >= 15: break
        if dl["section"] not in ("S","P"): continue
        if pct < 100 or n < 6: continue
        print(f"\n  [{dl['folio']}] {n}tok")
        print(f"    {dl['decoded'][:150]}")
        shown += 1

    # Show ingredient registry
    print(f"\n{'='*70}")
    print(f"INGREDIENT REGISTRY ({_ingr_n[0]} named ingredients)")
    print(f"{'='*70}")
    ingr_freq = Counter()
    rev_ingr = {v:k for k,v in _ingr.items()}
    for dl in decoded_lines:
        for m in re.findall(r'INGR_\d+', dl["decoded"]):
            ingr_freq[m] += 1
    print(f"\n  Top 20 ingredients to identify:")
    for iid, freq in ingr_freq.most_common(20):
        core = rev_ingr.get(iid, "?")
        print(f"    {iid} = {core:>15s} x{freq:5d}")

    # Save
    output = []
    cur = None
    for dl in decoded_lines:
        if dl["folio"] != cur:
            cur = dl["folio"]
            output.append(f"\n{'='*60}")
            output.append(f"  FOLIO {dl['folio']} | Section: {dl['section']}")
            output.append(f"{'='*60}")
        output.append(f"  {dl['decoded']}")

    with open(BASE / "VOYNICH_DECODED_V38.txt", 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))

    print(f"\n{'='*70}")
    print(f"V38 FINAL: {known}/{total} ({100*known/total:.1f}%)")
    print(f"  Ingredients to identify: {_ingr_n[0]}")
    print(f"  True unknowns: {_unk_n[0]}")
    print(f"  Output: VOYNICH_DECODED_V38.txt")


if __name__ == "__main__":
    main()
