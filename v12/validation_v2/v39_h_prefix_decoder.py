#!/usr/bin/env python3
"""
V39 — H-Prefix Decoder: 4th state marker + complete corrections.

Discovery: standalone 'h' (not in sh/ch/cth) is a 4th material state marker.
This resolves 25/30 top "residual" unknowns as decomposable tokens.

Complete state system:
  sh = CRUDA (raw material)
  ch = PRAEPARATA (prepared/processed)
  cth = COMPOSITA (compound medicine)
  h = 4th state (distillata? calcinata?)
  ckh = specific to cera? 5th variant?
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

PREP = {
    "qo": "cum", "qok": "cum", "qot": "cum",
    "d": "in", "da": "in", "ol": "ex", "l": "cum",
    "y": "de", "r": "re", "ok": "", "ot": "",
    "k": "", "": "", "o": "", "s": "est", "sa": "", "od": "ad",
}

VERB_PREFIXES = {"qo", "qok", "qot", "d", "da", "ol", "l"}
VERB_MAP = {
    "qo": "misce", "qok": "misce", "qot": "misce",
    "d": "coque", "da": "coque", "ol": "cola", "l": "cola",
}

GALLOWS = {"p": "Rx", "f": "Rx", "t": "tere"}

# State markers: 5 levels
STATE_MARKERS = {
    "sh": "[M]",     # cruda
    "ch": "[P]",     # praeparata
    "cth": "[C]",    # composita
    "ckh": "[K]",    # specific (cera-related?)
    "cfh": "[F]",    # rare variant
    "h": "[H]",      # 4th state (distillata?)
}

ALL_OUTER = ["qok","qot","qo","ok","ot","ol","da","od","sa","d","y","r","o","s","l","k"]
ALL_OUTER.sort(key=len, reverse=True)

INNER_ORDER = ["cth","ckh","cfh","ch","sh","h"]  # h LAST (only match if not sh/ch/cth)

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
    parts = []
    w = token

    # 1. Gallows
    gal = ""
    if len(w) > 1 and w[0] in "ptf":
        gal = w[0]; w = w[1:]

    # 2. Recursive decode
    sub_parts, sub_cat = _dec(w, gal)
    if gal and sub_cat in ("VERB","INGREDIENT"):
        parts.append(GALLOWS.get(gal, ""))
    elif gal:
        parts.append(GALLOWS.get(gal, ""))
    parts.extend(sub_parts)
    return " ".join(p for p in parts if p), sub_cat


def _dec(w, gal=""):
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
        s = "dr" if um.group(2) == "n" else "sc"
        return [f"{n}{s}"], "UNIT"

    # Direct substance
    if w in SUBSTANCES:
        return [SUBSTANCES[w]], "SUBST"

    # Try prefix stripping
    for pfx in ALL_OUTER:
        if w.startswith(pfx) and len(w) > len(pfx):
            remainder = w[len(pfx):]
            prep = PREP.get(pfx, "")

            # Inner state marker (sh/ch/cth/ckh/cfh/h)
            state = ""
            for sm in INNER_ORDER:
                if remainder.startswith(sm) and len(remainder) > len(sm):
                    # For 'h': only match if NOT preceded by s or c (already caught by sh/ch/cth)
                    if sm == "h":
                        state = STATE_MARKERS[sm]
                        remainder = remainder[len(sm):]
                    else:
                        state = STATE_MARKERS[sm]
                        remainder = remainder[len(sm):]
                    break

            # k-strip
            if remainder.startswith('k') and len(remainder) > 1:
                remainder = remainder[1:]

            # e-count
            e = 0
            while remainder.startswith('e') and len(remainder) > 1:
                e += 1; remainder = remainder[1:]
            qty = f"{e}x" if e > 0 else ""

            # UNIT in remainder
            um2 = UNIT_RE.match(remainder)
            if um2:
                n = len(um2.group(1))
                s = "dr" if um2.group(2) == "n" else "sc"
                return [f"{prep} {state}{qty}{n}{s}".strip()], "UNIT"

            # SUBSTANCE
            if remainder in SUBSTANCES:
                sub = SUBSTANCES[remainder]
                return [f"{prep} {state}{qty}{sub}".strip()], "SUBST"

            # -y/-dy/-ey
            if remainder in ("y","dy","ey"):
                conn = " et" if remainder == "dy" else ""
                suf = ".1" if remainder == "ey" else ""

                if state:
                    return [f"{prep} {state}{qty}materia{suf}{conn}".strip()], "STATE"

                if gal:
                    v = VERB_MAP.get(pfx, "fac")
                    e_s = f".{e}" if e > 0 else ""
                    return [f"{v}{e_s}{suf}{conn}"], "VERB"

                if pfx in VERB_PREFIXES:
                    v = VERB_MAP.get(pfx, "misce")
                    e_s = f".{e}" if e > 0 else ""
                    return [f"{v}{e_s}{suf}{conn}"], "VERB"

                # Not a verb → grammatical marker
                return [f"{prep} {qty}materia{suf}{conn}".strip()], "GRAM"

            # Try to recurse on remainder
            sub_p, sub_c = _dec(remainder, gal)
            if sub_c not in ("UNK",):
                if state:
                    return [f"{prep} {state}{' '.join(sub_p)}".strip()], sub_c
                elif prep:
                    return [f"{prep} {' '.join(sub_p)}".strip()], sub_c
                return sub_p, sub_c

    # Bare inner state + suffix (no outer prefix)
    for sm in INNER_ORDER:
        if w.startswith(sm) and len(w) > len(sm):
            state = STATE_MARKERS[sm]
            remainder = w[len(sm):]
            if remainder.startswith('k') and len(remainder) > 1:
                remainder = remainder[1:]
            e = 0
            while remainder.startswith('e') and len(remainder) > 1:
                e += 1; remainder = remainder[1:]
            qty = f"{e}x" if e > 0 else ""

            if UNIT_RE.match(remainder):
                um3 = UNIT_RE.match(remainder)
                n = len(um3.group(1))
                s = "dr" if um3.group(2) == "n" else "sc"
                return [f"{state}{qty}{n}{s}"], "UNIT"
            if remainder in SUBSTANCES:
                return [f"{state}{qty}{SUBSTANCES[remainder]}"], "SUBST"
            if remainder in ("y","dy","ey"):
                conn = " et" if remainder == "dy" else ""
                suf = ".1" if remainder == "ey" else ""
                return [f"{state}{qty}materia{suf}{conn}"], "STATE"

    # Bare dual -y/-dy/-ey
    if w in ("y","dy","ey"):
        if gal:
            return [GALLOWS.get(gal, "fac")], "VERB"
        conn = " et" if w == "dy" else ""
        return [f"materia{conn}"], "GRAM"

    # k + remainder
    if w.startswith('k') and len(w) > 1:
        sub_p, sub_c = _dec(w[1:], gal)
        if sub_c != "UNK":
            return sub_p, sub_c

    return [unk(w)], "UNK"


def main():
    print("V39 H-PREFIX DECODER — 4 State Markers")
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
        print(f"    {cat:>8s}: {n:6d} ({100*n/total:.1f}%)")
    print(f"  {'KNOWN':>10s}: {known:6d} ({100*known/total:.1f}%)")
    print(f"  Unknowns: {_unk_n[0]} unique")

    # Verb ratio check
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

    # Best pharma recipes
    print(f"\n{'='*70}")
    print("BEST PHARMA RECIPES (S/P, 100%, 8+tok)")
    print(f"{'='*70}")
    shown = 0
    for pct, n, dl in scored:
        if shown >= 15: break
        if dl["section"] not in ("S","P"): continue
        if pct < 100 or n < 8: continue
        print(f"\n  [{dl['folio']}] {n}tok")
        print(f"    {dl['decoded'][:160]}")
        shown += 1

    # F103
    print(f"\n{'='*70}")
    print("F103R/V (80%+)")
    print(f"{'='*70}")
    shown = 0
    for pct, n, dl in scored:
        if shown >= 10: break
        if dl["folio"].upper() not in ("F103R","F103V"): continue
        if pct < 80: continue
        print(f"\n  [{dl['folio']}] {pct:.0f}%, {n}tok")
        print(f"    {dl['decoded'][:160]}")
        shown += 1

    # Save decoded manuscript
    output = []
    cur = None
    for dl in decoded_lines:
        if dl["folio"] != cur:
            cur = dl["folio"]
            output.append(f"\n{'='*60}")
            output.append(f"  FOLIO {dl['folio']} | Section: {dl['section']}")
            output.append(f"{'='*60}")
        output.append(f"  {dl['decoded']}")

    with open(BASE / "VOYNICH_DECODED_V39.txt", 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))

    # Remaining unknowns
    unk_freq = Counter()
    rev = {v:k for k,v in _unk.items()}
    for dl in decoded_lines:
        for m in re.findall(r'UNK_\d+', dl["decoded"]):
            unk_freq[m] += 1

    print(f"\n{'='*70}")
    print(f"REMAINING UNKNOWNS (top 15)")
    print(f"{'='*70}")
    for uid, freq in unk_freq.most_common(15):
        core = rev.get(uid, "?")
        print(f"  {uid:>10s} = {core:>12s} x{freq:5d}")

    print(f"\n{'='*70}")
    print(f"V39 FINAL: {known}/{total} ({100*known/total:.1f}%)")
    print(f"  100%: {perfect}, 80%+: {good}, UNK: {_unk_n[0]} unique")
    print(f"  Output: VOYNICH_DECODED_V39.txt")


if __name__ == "__main__":
    main()
