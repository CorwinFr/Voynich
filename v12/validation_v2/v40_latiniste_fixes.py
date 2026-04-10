#!/usr/bin/env python3
"""
V40 — Latiniste Fixes: sh-bug + -dy relabeled + cleaner output.

Fix 1: sh was split into s+h. Now state markers (sh/ch/cth/ckh/h)
       are checked BEFORE single-char outer prefixes.
Fix 2: -dy relabeled from "et" to "," (list separator).
Fix 3: -y = base form, -dy = list form, -ey = variant form.
Fix 4: Single-char 's' no longer mapped to "est" (was producing artifact).
"""
import sys, re, json
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

BASE = Path("d:/Github/Voynich")
DECODED_FILE = BASE / "v12/output/VOYNICH_DECODE_V12_INGREDIENTS.txt"
RESULTS = BASE / "v12/validation_v2/results"

UNIT_RE = re.compile(r'^a?(i+)([nr])$')

SUBSTANCES = {
    "ol": "oleum", "or": "rosa", "al": "sal", "ar": "aqua",
    "ody": "acetum", "ckhy": "cera", "os": "succus", "am": "ana",
}

# FIX 1: State markers checked FIRST (before outer prefixes)
STATE_MARKERS = ["cth", "ckh", "cfh", "ch", "sh", "h"]

# Outer prefixes: EXCLUDE single-chars that conflict with state markers
OUTER_MULTI = ["qok", "qot", "qo", "ok", "ot", "ol", "da", "od", "sa"]
OUTER_SINGLE = ["d", "y", "r", "o", "l", "k"]  # 's' REMOVED (was causing est artifact)

VERB_PREFIXES = {"qo", "qok", "qot", "d", "da", "ol", "l"}
VERB_MAP = {
    "qo": "misce", "qok": "misce", "qot": "misce",
    "d": "coque", "da": "coque", "ol": "cola", "l": "cola",
}
GALLOWS = {"p": "Rx", "f": "Rx", "t": "tere"}
PREP = {
    "qo": "cum", "qok": "cum", "qot": "cum",
    "d": "in", "da": "in", "ol": "ex", "l": "cum",
    "y": "de", "r": "re", "ok": "", "ot": "",
    "k": "", "o": "", "od": "ad", "sa": "", "": "",
}
STATE_LABEL = {
    "sh": "[M]", "ch": "[P]", "cth": "[C]",
    "ckh": "[K]", "cfh": "[F]", "h": "[H]",
}

_unk = {}
_unk_n = [0]
def unk(core):
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
                    words = [w.lower() for w in parts[1].strip().split() if w.isalpha() and len(w) >= 2]
                    if words: lines.append({"folio": folio, "section": sec, "words": words})
    return lines


def decode(token):
    w = token
    parts_out = []

    # 1. Gallows
    gal = ""
    if len(w) > 1 and w[0] in "ptf":
        gal = w[0]; w = w[1:]

    # 2. Try multi-char outer prefix FIRST
    outer = ""
    for pfx in OUTER_MULTI:
        if w.startswith(pfx) and len(w) > len(pfx):
            outer = pfx; w = w[len(pfx):]; break

    # 3. FIX 1: Check state markers BEFORE single-char prefixes
    state = ""
    for sm in STATE_MARKERS:
        if w.startswith(sm) and len(w) > len(sm):
            state = sm; w = w[len(sm):]; break

    # 4. If no state marker found, try single-char outer prefix
    if not state and not outer:
        for pfx in OUTER_SINGLE:
            if w.startswith(pfx) and len(w) > len(pfx):
                outer = pfx; w = w[len(pfx):]; break
        # After single-char prefix, check state marker again
        if not state:
            for sm in STATE_MARKERS:
                if w.startswith(sm) and len(w) > len(sm):
                    state = sm; w = w[len(sm):]; break

    # 5. k-strip
    if w.startswith('k') and len(w) > 1:
        w = w[1:]

    # 6. e-count
    e = 0
    while w.startswith('e') and len(w) > 1:
        e += 1; w = w[1:]

    # Build prefix string
    gal_str = GALLOWS.get(gal, "") if gal else ""
    prep_str = PREP.get(outer, "") if outer else ""
    state_str = STATE_LABEL.get(state, "") if state else ""
    qty_str = f"{e}x" if e > 0 else ""

    # 7. UNIT
    um = UNIT_RE.match(w)
    if um:
        n = len(um.group(1))
        sym = "dr" if um.group(2) == "n" else "sc"
        token_str = f"{gal_str} {prep_str} {state_str}{qty_str}{n}{sym}".strip()
        return re.sub(r'  +', ' ', token_str), "UNIT"

    # 8. SUBSTANCE
    if w in SUBSTANCES:
        s = SUBSTANCES[w]
        token_str = f"{gal_str} {prep_str} {state_str}{qty_str}{s}".strip()
        return re.sub(r'  +', ' ', token_str), "SUBST"

    # 9. FIX 2+3: -y/-dy/-ey
    if w in ("y", "dy", "ey"):
        # FIX 2: -dy = list separator ",", not "et"
        sep = "," if w == "dy" else ""
        form = ".v" if w == "ey" else ""  # variant form

        if state:
            # State-marked = material reference
            token_str = f"{gal_str} {prep_str} {state_str}{qty_str}materia{form}{sep}".strip()
            return re.sub(r'  +', ' ', token_str), "STATE"

        if gal:
            v = VERB_MAP.get(outer, "fac") if outer in VERB_PREFIXES else GALLOWS.get(gal, "fac")
            token_str = f"{v}{form}{sep}"
            return token_str, "VERB"

        if outer in VERB_PREFIXES:
            v = VERB_MAP.get(outer, "misce")
            e_s = f".{e}" if e > 0 else ""
            token_str = f"{v}{e_s}{form}{sep}"
            return token_str, "VERB"

        # Otherwise: grammatical marker
        token_str = f"{gal_str} {prep_str} {qty_str}materia{form}{sep}".strip()
        return re.sub(r'  +', ' ', token_str), "GRAM"

    # 10. Single char residual (FIX 4: no more "est" for 's')
    if len(w) == 1:
        m = {"o": "eo", "l": "cum", "r": "re", "d": "in",
             "m": "cum", "n": "in", "a": "a", "s": "s"}.get(w, w)
        token_str = f"{gal_str} {prep_str} {state_str}{m}".strip()
        return re.sub(r'  +', ' ', token_str), "FUNC"

    # 11. Try recursive: remaining might contain prefix+known
    for sm2 in STATE_MARKERS:
        if w.startswith(sm2) and len(w) > len(sm2):
            rem = w[len(sm2):]
            while rem.startswith('e') and len(rem) > 1: rem = rem[1:]
            if rem in SUBSTANCES:
                s = SUBSTANCES[rem]
                st2 = STATE_LABEL[sm2]
                token_str = f"{gal_str} {prep_str} {state_str}{st2}{qty_str}{s}".strip()
                return re.sub(r'  +', ' ', token_str), "SUBST"
            if rem in ("y","dy","ey"):
                sep = "," if rem == "dy" else ""
                st2 = STATE_LABEL[sm2]
                token_str = f"{gal_str} {prep_str} {state_str}{st2}{qty_str}materia{sep}".strip()
                return re.sub(r'  +', ' ', token_str), "STATE"

    # 12. Unknown
    token_str = f"{gal_str} {prep_str} {state_str}{qty_str}{unk(w)}".strip()
    return re.sub(r'  +', ' ', token_str), "UNK"


def main():
    print("V40 LATINISTE FIXES")
    print("=" * 70)

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
        print(f"    {cat:>8s}: {n:6d} ({100*n/total:.1f}%)")
    print(f"  {'KNOWN':>10s}: {known:6d} ({100*known/total:.1f}%)")

    # Check: how many "est" remain?
    est_count = sum(dl["decoded"].count(" s ") + dl["decoded"].count(" s,") for dl in decoded_lines)
    et_count = sum(dl["decoded"].count(" et ") for dl in decoded_lines)
    comma_count = sum(dl["decoded"].count(",") for dl in decoded_lines)
    print(f"\n  ARTIFACT CHECK:")
    print(f"    'est' occurrences: ~{est_count} (was 3259, should be near 0)")
    print(f"    'et' occurrences: ~{et_count} (was 4469, should be near 0)")
    print(f"    ',' (list sep): ~{comma_count} (new: replaces 'et')")

    # Verb ratio
    print(f"\n  VERB RATIO:")
    for sn, sc in [("S","S"),("H","H"),("B","B")]:
        v = sum(1 for dl in decoded_lines if dl["section"]==sc for c in dl["cats"] if c=="VERB")
        si = sum(1 for dl in decoded_lines if dl["section"]==sc for c in dl["cats"] if c in ("SUBST","STATE","GRAM"))
        u = sum(1 for dl in decoded_lines if dl["section"]==sc for c in dl["cats"] if c=="UNIT")
        r = (si+u)/max(v,1)
        print(f"    {sn}: verb={v} subst+state+gram={si} unit={u} ratio={r:.1f}:1")

    # Best lines
    scored = [(sum(1 for c in dl["cats"] if c!="UNK")/len(dl["cats"])*100,
               len(dl["cats"]), dl) for dl in decoded_lines if len(dl["cats"])>=4]
    scored.sort(key=lambda x: (-x[0], -x[1]))
    perfect = sum(1 for p,n,_ in scored if p==100 and n>=4)
    good = sum(1 for p,n,_ in scored if p>=80 and n>=5)
    print(f"\n  100% lines (4+tok): {perfect}")
    print(f"  80%+ lines (5+tok): {good}")

    # Show samples
    print(f"\n{'='*70}")
    print("SAMPLE PHARMA RECIPES (S/P, 100%, 10+tok)")
    print(f"{'='*70}")
    shown = 0
    for pct, n, dl in scored:
        if shown >= 10: break
        if dl["section"] not in ("S","P"): continue
        if pct < 100 or n < 8: continue
        print(f"\n  [{dl['folio']}] {n}tok")
        print(f"    {dl['decoded'][:160]}")
        shown += 1

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

    with open(BASE / "VOYNICH_DECODED_V40.txt", 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))

    print(f"\n{'='*70}")
    print(f"V40 FINAL: {known}/{total} ({100*known/total:.1f}%)")
    print(f"  100%: {perfect}, 80%+: {good}, UNK: {_unk_n[0]}")
    print(f"  Output: VOYNICH_DECODED_V40.txt")


if __name__ == "__main__":
    main()
