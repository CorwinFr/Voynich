#!/usr/bin/env python3
"""
V32 — Final Decoder: Honest, publishable.

Key fix: dy/ey/y are DUAL-FUNCTION:
  - With sh/ch prefix → SUBSTANCE (raw/processed material)
  - Without sh/ch → VERB (procedural action)
  - Gallows + any → VERB (recipe/signa)

Unknown suffixes get UNKNOWN_N labels, NOT guessed plant names.
A recipe that reads "Rx UNK_7 2℥, misce cum OLEUM" is publishable.
A recipe with guessed plant names is not.
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

# CONFIRMED substances (V27)
KNOWN_SUBSTANCES = {
    "ol": "OLEUM", "or": "HIERA", "al": "SAL", "ar": "AQUA",
    "ody": "ACETUM", "ckhy": "CERA", "os": "SUCCUS", "am": "ANA",
}

# DUAL suffixes: SUBSTANCE when sh/ch prefixed, VERB otherwise
DUAL_SUFFIXES = {"y", "dy", "ey"}

# VERB meanings by prefix (V30)
VERB_BY_PREFIX = {
    "qo": "misce", "qok": "misce", "qot": "misce",
    "d": "coque", "da": "coque",
    "ol": "cola", "l": "cola",
    "y": "solve", "r": "repete",
    "ok": "adde", "ot": "adde",
    "": "fac", "k": "fac",
}

GALLOWS_VERB = {"p": "Rx", "f": "Rx", "t": "signa"}

PREFIX_PREP = {
    "qo": "cum", "qok": "cum", "qot": "cum",
    "d": "in", "da": "in",
    "ol": "ex", "l": "per",
    "y": "de", "r": "re",
    "ok": "", "ot": "", "k": "", "": "",
}

UNIT_RE = re.compile(r'^a?(i+)([nr])$')

# Unknown registry: assigns stable IDs to unknown cores
_unknown_registry = {}
_unknown_counter = [0]


def get_unknown_id(core):
    if core not in _unknown_registry:
        _unknown_counter[0] += 1
        _unknown_registry[core] = f"UNK_{_unknown_counter[0]:03d}"
    return _unknown_registry[core]


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
    """The FINAL decoder. Returns (readable_string, category)."""
    w = token
    gallows = ""
    if len(w) > 1 and w[0] in "ptf":
        gallows = w[0]; w = w[1:]

    prefix = ""
    for pfx in PREFIXES_ORDER:
        if w.startswith(pfx) and len(w) > len(pfx):
            prefix = pfx; w = w[len(pfx):]; break

    if w.startswith('k') and len(w) > 1:
        if not prefix: prefix = "k"
        w = w[1:]

    # === UNIT ===
    um = UNIT_RE.match(w)
    if um:
        n = len(um.group(1))
        sym = "℥" if um.group(2) == "n" else "ʒ"
        unit = f"{n}{sym}"
        prep = PREFIX_PREP.get(prefix, "")
        g = GALLOWS_VERB.get(gallows, "")
        return " ".join(p for p in [g, prep, unit] if p), "UNIT"

    # === E-COUNT ===
    e_count = 0
    check_cores = set(KNOWN_SUBSTANCES) | DUAL_SUFFIXES
    while w.startswith('e') and len(w) > 1:
        rem = w[1:]
        if rem in check_cores or (len(rem) >= 2 and rem[0] != 'e'):
            e_count += 1; w = rem
        else: break

    qty = f"{e_count}×" if e_count > 0 else ""
    is_material = prefix in ("sh", "ch")
    state = "[M]" if prefix == "sh" else "[P]" if prefix == "ch" else ""

    # === KNOWN SUBSTANCE ===
    if w in KNOWN_SUBSTANCES:
        s = KNOWN_SUBSTANCES[w]
        g = GALLOWS_VERB.get(gallows, "")
        if is_material:
            return " ".join(p for p in [g, f"{state}{qty}{s}"] if p), "SUBSTANCE"
        prep = PREFIX_PREP.get(prefix, "")
        return " ".join(p for p in [g, prep, f"{qty}{s}"] if p), "SUBSTANCE"

    # === DUAL SUFFIX: SUBSTANCE or VERB? ===
    if w in DUAL_SUFFIXES:
        connector = " et" if w == "dy" else ""

        if is_material:
            # sh/ch + dy/ey/y = SUBSTANCE (raw/processed material)
            # This is the material being acted upon
            unk = get_unknown_id(f"{state}{w}")
            return f"{state}{qty}{unk}{connector}", "SUBSTANCE"

        if gallows:
            # Gallows + verb = recipe command
            verb = GALLOWS_VERB.get(gallows, "§")
            if e_count > 0:
                return f"{verb}.{e_count}{connector}", "VERB"
            return f"{verb}{connector}", "VERB"

        # Prefix determines verb
        base_pfx = prefix
        verb = VERB_BY_PREFIX.get(base_pfx, "fac")
        if e_count > 0:
            return f"{verb}.{e_count}{connector}", "VERB"
        return f"{verb}{connector}", "VERB"

    # === UNKNOWN ===
    unk = get_unknown_id(w)
    g = GALLOWS_VERB.get(gallows, "")
    if is_material:
        return " ".join(p for p in [g, f"{state}{qty}{unk}"] if p), "UNKNOWN"
    prep = PREFIX_PREP.get(prefix, "")
    return " ".join(p for p in [g, prep, f"{qty}{unk}"] if p), "UNKNOWN"


def main():
    print("V32 FINAL DECODER")
    print("=" * 70)

    lines = parse_lines()
    total_tokens = sum(len(l["words"]) for l in lines)
    print(f"  {len(lines)} lines, {total_tokens} tokens\n")

    # === DECODE ALL ===
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
    print(f"    {'KNOWN':>12s}: {known:6d} ({100*known/total_tokens:.1f}%)")
    print(f"    {'UNKNOWN':>12s}: {stats['UNKNOWN']:6d} ({100*stats['UNKNOWN']/total_tokens:.1f}%)")
    print(f"  Unknown labels assigned: {_unknown_counter[0]}")

    # === BEST LINES ===
    print(f"\n{'='*70}")
    print("BEST DECODED RECIPE LINES")
    print(f"{'='*70}")

    scored = []
    for dl in decoded_lines:
        n = len(dl["cats"])
        k = sum(1 for c in dl["cats"] if c != "UNKNOWN")
        pct = 100*k/n if n else 0
        scored.append((pct, n, dl))

    scored.sort(key=lambda x: (-x[0], -x[1]))

    # Pharma recipes
    print(f"\n  PHARMACEUTICAL RECIPES (S/P, 6+tok, 70%+known):")
    shown = 0
    for pct, n, dl in scored:
        if shown >= 20: break
        if dl["section"] not in ("S", "P"): continue
        if n < 6 or pct < 70: continue
        print(f"\n    [{dl['folio']}|{dl['section']}] {pct:.0f}% known, {n} tokens")
        print(f"      {dl['decoded'][:120]}")
        shown += 1

    # F103R
    print(f"\n  F103R/V RECIPES (60%+known):")
    shown = 0
    for pct, n, dl in scored:
        if shown >= 15: break
        if dl["folio"].upper() not in ("F103R", "F103V"): continue
        if pct < 60: continue
        print(f"\n    [{dl['folio']}] {pct:.0f}%, {n}tok")
        print(f"      {dl['decoded'][:120]}")
        shown += 1

    # Herbal labels
    print(f"\n  HERBAL LABELS (short H lines):")
    shown = 0
    for pct, n, dl in scored:
        if shown >= 20: break
        if dl["section"] != "H" or n > 4: continue
        print(f"    [{dl['folio']}] {dl['eva']:35s} → {dl['decoded'][:60]}")
        shown += 1

    # Zodiac labels
    print(f"\n  ZODIAC LABELS:")
    zodiac = {"F70V1":"Pisces","F70V2":"Aries","F71R":"Taurus","F71V":"Gemini",
              "F72R1":"Cancer","F72R2":"Leo","F72R3":"Virgo","F72V1":"Libra",
              "F72V2":"Scorpio","F72V3":"Sagittarius","F73R":"Capricorn","F73V":"Aquarius"}
    shown = 0
    for pct, n, dl in scored:
        if dl["section"] != "Z" or n > 3: continue
        if shown >= 20: break
        sign = zodiac.get(dl["folio"], "?")
        print(f"    [{dl['folio']}={sign}] {dl['eva']:25s} → {dl['decoded'][:50]}")
        shown += 1

    # === UNKNOWN REGISTRY ===
    print(f"\n{'='*70}")
    print(f"UNKNOWN REGISTRY ({_unknown_counter[0]} unique unknowns)")
    print(f"{'='*70}")

    # Count frequency of each unknown
    unk_freq = Counter()
    for dl in decoded_lines:
        for part in dl["decoded"].split("  "):
            for unk_id in re.findall(r'UNK_\d+', part):
                unk_freq[unk_id] += 1

    # Reverse registry
    rev = {v: k for k, v in _unknown_registry.items()}

    print(f"\n  TOP 30 UNKNOWNS:")
    print(f"  {'ID':>10s} {'Core':>15s} {'Freq':>6s}")
    for unk_id, freq in unk_freq.most_common(30):
        core = rev.get(unk_id, "?")
        print(f"  {unk_id:>10s} {core:>15s} {freq:6d}")

    # === SAVE ===
    output = []
    current = None
    for dl in decoded_lines:
        if dl["folio"] != current:
            current = dl["folio"]
            output.append(f"\n{'='*60}")
            output.append(f"  FOLIO {dl['folio']} | Section: {dl['section']}")
            output.append(f"{'='*60}")
        output.append(f"  {dl['decoded']}")

    with open(BASE / "VOYNICH_DECODED_V32.txt", 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))

    # Save unknown registry
    registry = {v: k for k, v in _unknown_registry.items()}
    with open(RESULTS / "v32_unknown_registry.json", 'w', encoding='utf-8') as f:
        json.dump({
            "total_unknowns": _unknown_counter[0],
            "registry": registry,
            "frequency": dict(unk_freq.most_common(100)),
            "stats": dict(stats),
            "known_pct": round(100*known/total_tokens, 1),
        }, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*70}")
    print(f"V32 FINAL")
    print(f"{'='*70}")
    print(f"  Decoded: {known}/{total_tokens} ({100*known/total_tokens:.1f}%)")
    print(f"  Unknowns: {_unknown_counter[0]} unique labels")
    print(f"  Output: VOYNICH_DECODED_V32.txt")
    print(f"  Registry: {RESULTS/'v32_unknown_registry.json'}")


if __name__ == "__main__":
    main()
