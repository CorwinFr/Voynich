#!/usr/bin/env python3
"""
V37 — Fixed Parser: recursive decomposition handles all known patterns.

The V34 parser misses ~5000 tokens because after stripping the outer prefix,
the remaining core contains ANOTHER prefix+suffix that isn't decomposed.

Example: qodaiin → strip qo → daiin → should be d(in) + aiin(2ʒ)
         okodaiin → strip ok → odaiin → should be o + d + aiin(2ʒ)

Fix: after extracting the core, TRY TO DECOMPOSE IT FURTHER.
"""
import sys, re, json
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

BASE = Path("d:/Github/Voynich")
DECODED_FILE = BASE / "v12/output/VOYNICH_DECODE_V12_INGREDIENTS.txt"
RESULTS = BASE / "v12/validation_v2/results"

UNIT_RE = re.compile(r'^a?(i+)([nr])$')

SUBSTANCES = {
    "ol": "oleum", "al": "sal", "ar": "aqua",
    "ody": "acetum", "ckhy": "cera", "os": "succus", "am": "ana",
    "or": "UNK_or",  # H-dominant simple, identity unknown
}

PREP = {
    "qo": "cum", "qok": "cum", "qot": "cum",
    "d": "in", "da": "in", "ol": "ex", "l": "per",
    "y": "de", "r": "re", "ok": "", "ot": "", "k": "", "": "",
    "o": "", "s": "est", "sa": "usa", "od": "ad",
}

VERB_BY_PREFIX = {
    "qo": "misce", "qok": "misce", "qot": "misce",
    "d": "coque", "da": "coque", "ol": "cola", "l": "cola",
    "y": "solve", "r": "repete", "ok": "adde", "ot": "adde",
    "o": "fac", "s": "fac", "": "fac", "k": "fac",
}

GALLOWS_V = {"p": "Rx", "f": "Rx", "t": "signa"}

# All possible prefixes in priority order
ALL_PREFIXES = ["qok", "qot", "qo", "ok", "ot", "ol", "da", "od",
                "sa", "ch", "sh", "d", "y", "r", "o", "s",
                "l", "k", "p", "t", "f"]
ALL_PREFIXES.sort(key=len, reverse=True)

INNER_PFX = {"ch", "sh", "cth", "ckh", "cfh"}


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


_unk = {}
_unk_n = [0]
def unk(core):
    if core not in _unk:
        _unk_n[0] += 1
        _unk[core] = f"UNK_{_unk_n[0]}"
    return _unk[core]


def decode(token):
    """Recursive decoder that handles nested prefix+suffix patterns."""
    parts = []
    cat = "UNK"
    w = token

    # 1. Gallows
    gallows = ""
    if len(w) > 1 and w[0] in "ptf":
        gallows = w[0]; w = w[1:]
        parts.append(GALLOWS_V.get(gallows, "§"))

    # 2. Recursive decomposition of the remainder
    sub_parts, sub_cat = _decode_remainder(w)
    parts.extend(sub_parts)
    cat = sub_cat

    return " ".join(p for p in parts if p), cat


def _decode_remainder(w):
    """Recursively decompose a token remainder."""
    if not w or len(w) < 2:
        if len(w) == 1:
            m = {"o": "eo", "l": "per", "r": "re", "s": "est", "d": "in",
                 "m": "cum", "e": "e", "n": "in", "a": "a"}.get(w, w)
            return [m], "FUNC"
        return [], "EMPTY"

    # UNIT pattern (most specific, check first)
    um = UNIT_RE.match(w)
    if um:
        n = len(um.group(1))
        sym = "ʒ" if um.group(2) == "n" else "℈"
        return [f"{n}{sym}"], "UNIT"

    # Direct substance match
    if w in SUBSTANCES:
        return [SUBSTANCES[w]], "SUBST"

    # E-count + known core
    e = 0
    ew = w
    while ew.startswith('e') and len(ew) > 1:
        e += 1; ew = ew[1:]

    if e > 0:
        # Check if remainder after e-strip is known
        um2 = UNIT_RE.match(ew)
        if um2:
            n = len(um2.group(1))
            sym = "ʒ" if um2.group(2) == "n" else "℈"
            return [f"{e}×{n}{sym}"], "UNIT"

        if ew in SUBSTANCES:
            return [f"{e}×{SUBSTANCES[ew]}"], "SUBST"

        if ew in ("y", "dy", "ey"):
            # No prefix context → just report
            conn = " et" if ew == "dy" else ""
            return [f"fac.{e}{conn}"], "VERB"

    # Try stripping a prefix and recurse
    for pfx in ALL_PREFIXES:
        if w.startswith(pfx) and len(w) > len(pfx):
            remainder = w[len(pfx):]

            # Determine prefix meaning based on whether it's sh/ch (state) or other (prep)
            is_inner = pfx in INNER_PFX

            # Recurse on remainder
            sub_parts, sub_cat = _decode_remainder(remainder)

            if sub_cat in ("UNIT", "SUBST", "VERB", "STATE", "FUNC"):
                # Prefix successfully decomposed the remainder
                if is_inner:
                    state = "[M]" if pfx == "sh" else "[P]"
                    # If remainder was a verb suffix, it becomes a STATE marker
                    if sub_cat == "VERB":
                        text = state + " ".join(sub_parts).replace("fac", "materia")
                        return [text], "STATE"
                    return [state + " ".join(sub_parts)], sub_cat
                else:
                    prep = PREP.get(pfx, pfx)
                    if sub_cat == "VERB":
                        # Prefix determines the verb
                        verb = VERB_BY_PREFIX.get(pfx, "fac")
                        # Reconstruct with correct verb
                        text = " ".join(sub_parts).replace("fac", verb)
                        return [text], "VERB"
                    if prep:
                        return [prep + " " + " ".join(sub_parts)], sub_cat
                    return sub_parts, sub_cat

    # Dual suffix (y/dy/ey) without prefix = verb
    if w in ("y", "dy", "ey"):
        conn = " et" if w == "dy" else ""
        return [f"fac{conn}"], "VERB"

    # k + remainder
    if w.startswith('k') and len(w) > 1:
        sub_parts, sub_cat = _decode_remainder(w[1:])
        if sub_cat != "UNK":
            return sub_parts, sub_cat

    # Nothing worked → true unknown
    return [unk(w)], "UNK"


def main():
    print("V37 FIXED PARSER — Recursive decomposition")
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

    known = total_tokens - stats["UNK"]
    print(f"  CLASSIFICATION:")
    for cat, n in stats.most_common():
        print(f"    {cat:>8s}: {n:6d} ({100*n/total_tokens:.1f}%)")
    print(f"  {'KNOWN':>10s}: {known:6d} ({100*known/total_tokens:.1f}%)")
    print(f"  Unknowns: {_unk_n[0]} unique")

    # Best lines
    scored = []
    for dl in decoded_lines:
        n = len(dl["cats"])
        k = sum(1 for c in dl["cats"] if c != "UNK")
        pct = 100*k/n if n else 0
        scored.append((pct, n, dl))
    scored.sort(key=lambda x: (-x[0], -x[1]))

    perfect = sum(1 for p, n, _ in scored if p == 100 and n >= 4)
    good = sum(1 for p, n, _ in scored if p >= 80 and n >= 5)
    print(f"\n  100% lines (4+tok): {perfect}")
    print(f"  80%+ lines (5+tok): {good}")

    # Show best long lines
    print(f"\n{'='*70}")
    print("BEST LINES (100%, 10+ tokens)")
    print(f"{'='*70}")
    shown = 0
    for pct, n, dl in scored:
        if shown >= 20: break
        if pct < 100 or n < 8: continue
        print(f"\n  [{dl['folio']}|{dl['section']}] {n} tokens")
        print(f"    {dl['decoded'][:150]}")
        shown += 1

    # F103 lines
    print(f"\n{'='*70}")
    print("F103R/V (80%+)")
    print(f"{'='*70}")
    shown = 0
    for pct, n, dl in scored:
        if shown >= 12: break
        if dl["folio"].upper() not in ("F103R","F103V"): continue
        if pct < 80: continue
        print(f"\n  [{dl['folio']}] {pct:.0f}%, {n}tok")
        print(f"    {dl['decoded'][:150]}")
        shown += 1

    # Remaining unknowns
    print(f"\n{'='*70}")
    print(f"REMAINING UNKNOWNS (top 20)")
    print(f"{'='*70}")
    unk_freq = Counter()
    rev = {v: k for k, v in _unk.items()}
    for dl in decoded_lines:
        for m in re.findall(r'UNK_\d+', dl["decoded"]):
            unk_freq[m] += 1
    for uid, freq in unk_freq.most_common(20):
        core = rev.get(uid, "?")
        print(f"  {uid:>10s} = {core:>12s} x{freq:5d}")

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

    with open(BASE / "VOYNICH_DECODED_V37.txt", 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))

    print(f"\n{'='*70}")
    print(f"V37 FINAL: {known}/{total_tokens} ({100*known/total_tokens:.1f}%)")
    print(f"  100% lines: {perfect}, 80%+ lines: {good}")
    print(f"  Unknowns: {_unk_n[0]} unique")
    print(f"  Output: VOYNICH_DECODED_V37.txt")


if __name__ == "__main__":
    main()
