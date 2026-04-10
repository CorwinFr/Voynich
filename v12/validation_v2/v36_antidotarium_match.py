#!/usr/bin/env python3
"""
V36 — Antidotarium Match: Find THE recipe that proves it.

1. Fix model: remove or→hiera, relabel ℥→ʒ
2. Decode best lines with corrected model
3. Compare against 10 known Antidotarium Nicolai recipes
4. Look for pattern matches: OLEUM+CERA (unguentum), MEL+ACETUM (oximel), etc.

The Antidotarium recipe patterns (from research):
  Unguentum fuscum: Recipe olei + cerae → bulliat → apponatur cera → liquefiant
  Oximel: Recipe mellis + aceti → bulliant → coletur → addatur
  Oleum rosatum: olei + rosarum → ponatur in olla → bulliant → exprimatur
  Electuarium: Recipe + ana + tempera → datur cum aqua calida
  Hiera Picra: Recipe aloes + spices ana ʒii + mel q.s. → fiat confectio
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

# CORRECTED substances: or removed, relabeled
SUBSTANCES = {
    "ol": "oleum", "al": "sal", "ar": "aqua",
    "ody": "acetum", "ckhy": "cera", "os": "succus", "am": "ana",
    # or is now UNK — to be identified
}

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
        _unk_reg[core] = f"UNK_{_unk_n[0]}"
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

def decode(token):
    w = token
    g = ""
    if len(w) > 1 and w[0] in "ptf": g = w[0]; w = w[1:]
    outer = ""
    for pfx in PREFIXES_ORDER:
        if pfx in ("ch","sh"): continue
        if w.startswith(pfx) and len(w) > len(pfx): outer = pfx; w = w[len(pfx):]; break
    inner = ""
    for ipfx in ["cth","ckh","cfh","ch","sh"]:
        if w.startswith(ipfx) and len(w) > len(ipfx): inner = ipfx; w = w[len(ipfx):]; break
    if w.startswith('k') and len(w) > 1: w = w[1:]

    um = UNIT_RE.match(w)
    if um:
        n = len(um.group(1))
        # CORRECTED: ʒ for type n, ℈ for type r
        sym = "ʒ" if um.group(2) == "n" else "℈"
        unit = f"{n}{sym}"
        prep = PREFIX_PREP.get(outer, "")
        gv = GALLOWS_VERB.get(g, "")
        return " ".join(p for p in [gv, prep, unit] if p), "UNIT"

    e = 0
    while w.startswith('e') and len(w) > 1: e += 1; w = w[1:]
    qty = f"{e}×" if e > 0 else ""
    state = "[M]" if inner == "sh" else "[P]" if inner in ("ch","cth","ckh","cfh") else ""
    prep = PREFIX_PREP.get(outer, "") if not state else ""
    gv = GALLOWS_VERB.get(g, "")

    if w in SUBSTANCES:
        s = SUBSTANCES[w]
        return " ".join(p for p in [gv, prep, f"{state}{qty}{s}"] if p), "SUBST"

    if w in ("y", "dy", "ey"):
        conn = " et" if w == "dy" else ""
        if state:
            return " ".join(p for p in [gv, prep, f"{state}{qty}materia{conn}"] if p), "STATE"
        if g:
            v = GALLOWS_VERB.get(g, "§")
            return f"{v}{conn}", "VERB"
        v = VERB_BY_PREFIX.get(outer, "fac")
        e_str = f".{e}" if e > 0 else ""
        return f"{v}{e_str}{conn}", "VERB"

    if w in ("l","r","s","o","m","d","n") and len(w) == 1:
        meaning = {"l":"per","r":"re","s":"est","o":"eo","m":"cum","d":"in","n":"in"}.get(w, w)
        return " ".join(p for p in [gv, prep, f"{state}{meaning}"] if p), "FUNC"

    unk = get_unk(w)
    return " ".join(p for p in [gv, prep, f"{state}{qty}{unk}"] if p), "UNK"


# ══════════════════════════════════════════
# ANTIDOTARIUM RECIPE PATTERNS
# ══════════════════════════════════════════
RECIPE_PATTERNS = {
    "UNGUENTUM": {
        "desc": "Ointment base (oleum + cera → melt → mix)",
        "must_have": ["oleum", "cera"],
        "verbs": ["misce", "coque", "fac"],
        "sequence": "Rx + oleum + cera + verb",
    },
    "OXIMEL": {
        "desc": "Honey-vinegar preparation (mel + acetum → boil → strain)",
        "must_have": ["acetum"],
        "nice_have": ["mel", "cola"],
        "verbs": ["coque", "cola", "adde"],
        "sequence": "Rx + mel + acetum + coque + cola",
    },
    "ELECTUARIUM": {
        "desc": "Electuary (ingredients + ana + mel → fiat)",
        "must_have": ["ana"],
        "nice_have": ["cum", "fac"],
        "sequence": "ingredients + ana + mel + fiat",
    },
    "OLEUM_PREP": {
        "desc": "Oil preparation (oleum + plant → coque in aqua → cola)",
        "must_have": ["oleum"],
        "nice_have": ["aqua", "coque", "cola"],
        "sequence": "Rx + oleum + plant + coque cum aqua + cola",
    },
    "WASH": {
        "desc": "Wash/gargle (aqua/acetum + sal → misce)",
        "must_have": ["aqua"],
        "nice_have": ["sal", "acetum", "misce"],
        "sequence": "aqua + sal/acetum + misce",
    },
}


def find_recipe_matches(lines):
    print("=" * 70)
    print("ANTIDOTARIUM RECIPE MATCHING")
    print("=" * 70)

    all_decoded = []
    for line in lines:
        parts = []
        cats = []
        words_decoded = []
        for w in line["words"]:
            dec, cat = decode(w)
            parts.append(dec)
            cats.append(cat)
            words_decoded.append(dec.lower())
        known = sum(1 for c in cats if c != "UNK")
        pct = 100 * known / len(cats) if cats else 0
        all_decoded.append({
            "folio": line["folio"], "section": line["section"],
            "eva": " ".join(line["words"]),
            "decoded": "  ".join(parts),
            "words": words_decoded, "pct": pct, "n": len(cats),
        })

    # For each recipe pattern, find matching lines
    for pattern_name, pattern in RECIPE_PATTERNS.items():
        print(f"\n  {'='*60}")
        print(f"  PATTERN: {pattern_name} — {pattern['desc']}")
        print(f"  {'='*60}")

        matches = []
        for dl in all_decoded:
            if dl["n"] < 4: continue
            text = " ".join(dl["words"])

            # Check must_have
            has_all = all(kw in text for kw in pattern["must_have"])
            if not has_all: continue

            # Count nice_have
            nice_count = sum(1 for kw in pattern.get("nice_have", []) if kw in text)
            # Count verbs
            verb_count = sum(1 for v in pattern.get("verbs", []) if v in text)

            score = dl["pct"] + nice_count * 10 + verb_count * 5
            matches.append((score, dl))

        matches.sort(key=lambda x: -x[0])

        if matches:
            print(f"\n  Found {len(matches)} matching lines. Top 10:")
            for score, dl in matches[:10]:
                print(f"\n    [{dl['folio']}|{dl['section']}] {dl['pct']:.0f}%, {dl['n']}tok, score={score:.0f}")
                print(f"      {dl['decoded'][:140]}")
        else:
            print(f"\n  NO MATCHES FOUND")

    # Also: find the absolute BEST decoded recipe lines (any pattern)
    print(f"\n  {'='*60}")
    print(f"  ABSOLUTE BEST RECIPE LINES (S/P, 80%+, 6+tok)")
    print(f"  {'='*60}")

    best = [(dl["pct"], dl["n"], dl) for dl in all_decoded
            if dl["section"] in ("S","P") and dl["n"] >= 6 and dl["pct"] >= 80]
    best.sort(key=lambda x: (-x[0], -x[1]))

    for pct, n, dl in best[:20]:
        # Annotate: what recipe type does this look like?
        text = " ".join(dl["words"])
        recipe_type = ""
        if "oleum" in text and "cera" in text: recipe_type = "[UNGUENTUM?]"
        elif "acetum" in text and ("cola" in text or "coque" in text): recipe_type = "[OXIMEL?]"
        elif "ana" in text: recipe_type = "[ELECTUARIUM?]"
        elif "oleum" in text and "aqua" in text: recipe_type = "[OLEUM PREP?]"
        elif "aqua" in text and "sal" in text: recipe_type = "[WASH?]"

        print(f"\n    [{dl['folio']}] {pct:.0f}%, {n}tok {recipe_type}")
        print(f"      EVA: {dl['eva'][:120]}")
        print(f"      DEC: {dl['decoded'][:120]}")

    # Side-by-side comparison with Antidotarium
    print(f"\n  {'='*60}")
    print(f"  SIDE-BY-SIDE: Best UNGUENTUM candidates vs Antidotarium")
    print(f"  {'='*60}")
    print(f"\n  ANTIDOTARIUM (Unguentum fuscum):")
    print(f"    Recipe olei lb.i½, cerae ʒiiii, colofoniae ʒii...")
    print(f"    oleum bulliat → apponatur cera → liquefiant → agitando → reservetur")
    print(f"\n  OUR BEST MATCHES:")
    ung_matches = [(dl["pct"], dl) for dl in all_decoded
                   if "oleum" in " ".join(dl["words"]) and "cera" in " ".join(dl["words"])
                   and dl["n"] >= 5]
    ung_matches.sort(key=lambda x: -x[0])
    for pct, dl in ung_matches[:8]:
        print(f"\n    [{dl['folio']}] {pct:.0f}%")
        print(f"      {dl['decoded'][:140]}")

    # Stats
    total = len(all_decoded)
    known_lines = sum(1 for dl in all_decoded if dl["pct"] == 100 and dl["n"] >= 4)
    good_lines = sum(1 for dl in all_decoded if dl["pct"] >= 80 and dl["n"] >= 5)
    print(f"\n  {'='*60}")
    print(f"  STATS (corrected model)")
    print(f"  {'='*60}")
    total_tokens = sum(dl["n"] for dl in all_decoded)
    total_known = sum(sum(1 for c in ["SUBST","UNIT","VERB","STATE","FUNC"] if c in str(dl["words"])) for dl in all_decoded)
    print(f"    100% lines (4+tok): {known_lines}")
    print(f"    80%+ lines (5+tok): {good_lines}")
    print(f"    Total lines: {total}")


if __name__ == "__main__":
    print("V36 ANTIDOTARIUM MATCH")
    print("=" * 70)
    lines = parse_lines()
    print(f"  {len(lines)} lines, {sum(len(l['words']) for l in lines)} tokens\n")
    find_recipe_matches(lines)
