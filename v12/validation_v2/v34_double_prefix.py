#!/usr/bin/env python3
"""
V34 — Double Prefix Stripping

The big unknowns (chedy, chey, cthy, chdy, shedy, shey) are NOT unknown
suffixes. They're tokens where ch/sh is a SECOND prefix layer:

  dchedy = d + ch + edy = "in" + [PROCESSED] + substance
  qochey = qo + ch + ey = "cum" + [PROCESSED] + verb/substance

Token = gallows + PREFIX1(qo,d,ol,y,ok,ot...) + PREFIX2(ch,sh) + e-count + CORE

Also: single-letter cores 'l' and 'r' are likely residual prefixes.
"""
import sys, re, json
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

BASE = Path("d:/Github/Voynich")
DECODED_FILE = BASE / "v12/output/VOYNICH_DECODE_V12_INGREDIENTS.txt"
RESULTS = BASE / "v12/validation_v2/results"

PREFIXES_OUTER = ["qok", "qot", "qo", "ok", "ot", "ol", "da",
                  "d", "y", "r", "p", "l", "t", "f", "k"]
PREFIXES_OUTER.sort(key=len, reverse=True)

INNER_PREFIXES = {"ch", "sh", "cth", "ckh", "cfh"}

UNIT_RE = re.compile(r'^a?(i+)([nr])$')

SUBSTANCES = {
    "ol": "OLEUM", "or": "HIERA", "al": "SAL", "ar": "AQUA",
    "ody": "ACETUM", "ckhy": "CERA", "os": "SUCCUS", "am": "ANA",
}
DUAL_CORES = {"y", "dy", "ey"}

VERB_BY_PREFIX = {
    "qo": "misce", "qok": "misce", "qot": "misce",
    "d": "coque", "da": "coque", "ol": "cola", "l": "cola",
    "y": "solve", "r": "repete", "ok": "adde", "ot": "adde",
    "": "fac", "k": "fac",
}
GALLOWS_VERB = {"p": "Rx", "f": "Rx", "t": "signa"}
PREFIX_PREP = {
    "qo": "cum", "qok": "cum", "qot": "cum",
    "d": "in", "da": "in", "ol": "ex", "l": "per",
    "y": "de", "r": "re", "ok": "", "ot": "", "k": "", "": "",
}

_unk_reg = {}
_unk_n = [0]
def get_unk(core):
    if core not in _unk_reg:
        _unk_n[0] += 1
        _unk_reg[core] = f"UNK_{_unk_n[0]:03d}"
    return _unk_reg[core]


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
    """Double-prefix decomposition."""
    w = token
    gallows = ""
    if len(w) > 1 and w[0] in "ptf":
        gallows = w[0]; w = w[1:]

    # Outer prefix
    outer = ""
    for pfx in PREFIXES_OUTER:
        if pfx in ("ch", "sh"):
            continue  # ch/sh handled as inner
        if w.startswith(pfx) and len(w) > len(pfx):
            outer = pfx; w = w[len(pfx):]; break

    # Inner prefix (ch, sh, cth, ckh, cfh)
    inner = ""
    for ipfx in sorted(INNER_PREFIXES, key=len, reverse=True):
        if w.startswith(ipfx) and len(w) > len(ipfx):
            inner = ipfx; w = w[len(ipfx):]; break

    # k-strip
    k_mod = False
    if w.startswith('k') and len(w) > 1:
        k_mod = True; w = w[1:]

    # Unit?
    um = UNIT_RE.match(w)
    if um:
        return gallows, outer, inner, k_mod, 0, "UNIT", len(um.group(1)), um.group(2)

    # E-count
    e = 0
    while w.startswith('e') and len(w) > 1:
        e += 1; w = w[1:]

    return gallows, outer, inner, k_mod, e, w, 0, ""


def decode(token):
    g, outer, inner, k_mod, e, core, un, ut = decompose(token)

    g_str = GALLOWS_VERB.get(g, "") if g else ""
    prep = PREFIX_PREP.get(outer, outer) if outer else ""

    # Material state from inner prefix
    state = ""
    if inner == "sh": state = "[M]"
    elif inner == "ch": state = "[P]"
    elif inner == "cth": state = "[CTH]"
    elif inner == "ckh": state = "[CKH]"
    elif inner == "cfh": state = "[CFH]"

    qty = f"{e}×" if e > 0 else ""

    # UNIT
    if core == "UNIT":
        sym = "℥" if ut == "n" else "ʒ"
        unit = f"{un}{sym}"
        return " ".join(p for p in [g_str, prep, unit] if p), "UNIT"

    # SUBSTANCE
    if core in SUBSTANCES:
        s = SUBSTANCES[core]
        return " ".join(p for p in [g_str, prep, f"{state}{qty}{s}"] if p), "SUBSTANCE"

    # DUAL (y, dy, ey)
    if core in DUAL_CORES:
        conn = " et" if core == "dy" else ""
        suf = ".1" if core == "ey" else ""

        if state:  # Has inner ch/sh → STATE marker
            return " ".join(p for p in [g_str, prep, f"{state}{qty}MATERIA{suf}{conn}"] if p), "STATE"

        if g:  # Gallows → recipe verb
            v = GALLOWS_VERB.get(g, "§")
            e_str = f".{e}" if e > 0 else ""
            return f"{v}{e_str}{suf}{conn}", "VERB"

        # Outer prefix → verb
        v = VERB_BY_PREFIX.get(outer, "fac")
        e_str = f".{e}" if e > 0 else ""
        return f"{v}{e_str}{suf}{conn}", "VERB"

    # Single-char residuals
    if core in ("l", "r", "s", "o", "m", "d", "n"):
        # These are likely residual prefix fragments or short function words
        meaning = {"l": "PER", "r": "RE", "s": "EST", "o": "EO",
                   "m": "CUM", "d": "IN", "n": "IN"}.get(core, core)
        return " ".join(p for p in [g_str, prep, f"{state}{qty}{meaning}"] if p), "FUNCTION"

    # UNKNOWN
    unk = get_unk(core)
    return " ".join(p for p in [g_str, prep, f"{state}{qty}{unk}"] if p), "UNKNOWN"


def main():
    print("V34 DOUBLE PREFIX DECODER")
    print("=" * 70)

    lines = parse_lines()
    total_tokens = sum(len(l["words"]) for l in lines)
    print(f"  {len(lines)} lines, {total_tokens} tokens\n")

    stats = Counter()
    decoded_lines = []
    for line in lines:
        parts = []
        cats = []
        for w in line["words"]:
            dec, cat = decode(w)
            parts.append(dec)
            cats.append(cat)
            stats[cat] += 1
        decoded_lines.append({
            "folio": line["folio"], "section": line["section"],
            "eva": " ".join(line["words"]),
            "decoded": "  ".join(parts),
            "cats": cats,
        })

    known = total_tokens - stats["UNKNOWN"]
    print(f"  CLASSIFICATION:")
    for cat, n in stats.most_common():
        print(f"    {cat:>12s}: {n:6d} ({100*n/total_tokens:.1f}%)")
    print(f"  {'KNOWN':>14s}: {known:6d} ({100*known/total_tokens:.1f}%)")
    print(f"  Unknowns: {_unk_n[0]} unique labels")

    # Best lines
    scored = []
    for dl in decoded_lines:
        n = len(dl["cats"])
        k = sum(1 for c in dl["cats"] if c != "UNKNOWN")
        pct = 100*k/n if n else 0
        scored.append((pct, n, dl))
    scored.sort(key=lambda x: (-x[0], -x[1]))

    # Count 100% lines
    perfect = sum(1 for p, n, _ in scored if p == 100 and n >= 4)
    good = sum(1 for p, n, _ in scored if p >= 80 and n >= 5)
    print(f"\n  100% decoded lines (4+ tokens): {perfect}")
    print(f"  80%+ decoded lines (5+ tokens): {good}")

    print(f"\n{'='*70}")
    print("BEST PHARMACEUTICAL RECIPES (100%, 8+ tokens)")
    print(f"{'='*70}")
    shown = 0
    for pct, n, dl in scored:
        if shown >= 20: break
        if pct < 100 or n < 6: continue
        print(f"\n  [{dl['folio']}|{dl['section']}] {n} tokens")
        print(f"    {dl['decoded'][:140]}")
        shown += 1

    print(f"\n{'='*70}")
    print("BEST LONG LINES (80%+, 10+ tokens)")
    print(f"{'='*70}")
    shown = 0
    for pct, n, dl in scored:
        if shown >= 15: break
        if pct < 80 or n < 10: continue
        print(f"\n  [{dl['folio']}|{dl['section']}] {pct:.0f}%, {n} tokens")
        print(f"    {dl['decoded'][:150]}")
        shown += 1

    print(f"\n{'='*70}")
    print("F103R/V (70%+)")
    print(f"{'='*70}")
    shown = 0
    for pct, n, dl in scored:
        if shown >= 12: break
        if dl["folio"].upper() not in ("F103R", "F103V"): continue
        if pct < 70: continue
        print(f"\n  [{dl['folio']}] {pct:.0f}%, {n}tok")
        print(f"    {dl['decoded'][:150]}")
        shown += 1

    # Save
    output = []
    current = None
    for dl in decoded_lines:
        if dl["folio"] != current:
            current = dl["folio"]
            output.append(f"\n{'='*60}")
            output.append(f"  FOLIO {dl['folio']} | Section: {dl['section']}")
            output.append(f"{'='*60}")
        output.append(f"  {dl['decoded']}")

    with open(BASE / "VOYNICH_DECODED_V34.txt", 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))

    rev = {v: k for k, v in _unk_reg.items()}
    unk_freq = Counter()
    for dl in decoded_lines:
        for m in re.findall(r'UNK_\d+', dl["decoded"]):
            unk_freq[m] += 1

    with open(RESULTS / "v34_double_prefix.json", 'w', encoding='utf-8') as f:
        json.dump({
            "stats": dict(stats), "known_pct": round(100*known/total_tokens, 1),
            "unknowns": _unk_n[0], "perfect_lines_4plus": perfect,
            "top50_unknowns": [(uid, rev.get(uid,"?"), freq) for uid, freq in unk_freq.most_common(50)],
        }, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*70}")
    print(f"V34 FINAL: {known}/{total_tokens} ({100*known/total_tokens:.1f}%) known")
    print(f"  100% lines (4+tok): {perfect}")
    print(f"  80%+ lines (5+tok): {good}")
    print(f"  Unknowns: {_unk_n[0]} unique")
    print(f"  Output: VOYNICH_DECODED_V34.txt")


if __name__ == "__main__":
    main()
