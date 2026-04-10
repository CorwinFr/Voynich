#!/usr/bin/env python3
"""
V33 — Expand Known: Reclassify markers + exploit e-count patterns.

Phase 1: [M]y, [P]y, [M]dy, [P]dy → STATE MARKERS (not unknowns)
Phase 2: eedy, eeey, eeody → are these just 2×/3× of known suffixes?
Phase 3: chol, chor, chey, cthy, chdy → are these ch+KNOWN_SUFFIX?
Phase 4: Rebuild decoder with expanded knowledge, honest UNK_N for rest.
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

# V32 confirmed substances
SUBSTANCES = {
    "ol": "OLEUM", "or": "HIERA", "al": "SAL", "ar": "AQUA",
    "ody": "ACETUM", "ckhy": "CERA", "os": "SUCCUS", "am": "ANA",
}

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

def strip_token(token):
    """Full decomposition: gallows, prefix, e_count, core."""
    w = token
    gallows = ""
    if len(w) > 1 and w[0] in "ptf":
        gallows = w[0]; w = w[1:]
    prefix = ""
    for pfx in PREFIXES_ORDER:
        if w.startswith(pfx) and len(w) > len(pfx):
            prefix = pfx; w = w[len(pfx):]; break
    if w.startswith('k') and len(w) > 1:
        prefix = prefix + "+k" if prefix else "k"; w = w[1:]
    # Unit?
    um = UNIT_RE.match(w)
    if um: return gallows, prefix, 0, "UNIT", len(um.group(1)), um.group(2)
    # E-count
    e = 0
    while w.startswith('e') and len(w) > 1:
        r = w[1:]
        if len(r) >= 1: e += 1; w = r
        else: break
    return gallows, prefix, e, w, 0, ""


# ══════════════════════════════════════════
# PHASE 1: Analyze what's really behind the "unknowns"
# ══════════════════════════════════════════
def phase1_analyze_unknowns(lines):
    print("=" * 70)
    print("PHASE 1: What are the unknowns REALLY?")
    print("=" * 70)

    all_cores = Counter()
    core_with_sh = Counter()
    core_with_ch = Counter()
    core_with_neither = Counter()
    core_with_gallows = Counter()
    core_e_distribution = defaultdict(Counter)

    for line in lines:
        for token in line["words"]:
            g, pfx, e, core, un, ut = strip_token(token)
            base_pfx = pfx.split("+")[0]
            all_cores[core] += 1
            core_e_distribution[core][e] += 1

            if base_pfx == "sh": core_with_sh[core] += 1
            elif base_pfx == "ch": core_with_ch[core] += 1
            else: core_with_neither[core] += 1
            if g: core_with_gallows[core] += 1

    # For each frequent core, determine: is it substance, verb, both, or unknown?
    print(f"\n  TOP 40 CORES — Full analysis:")
    print(f"  {'Core':>10s} {'Total':>6s} {'sh%':>5s} {'ch%':>5s} {'other%':>6s} {'gal%':>5s} {'e0%':>5s} {'e1%':>5s} {'e2%':>5s} {'Type':>15s}")

    expanded = {}  # New classifications
    for core, total in all_cores.most_common(40):
        if core == "UNIT": continue
        sh = core_with_sh.get(core, 0)
        ch = core_with_ch.get(core, 0)
        other = core_with_neither.get(core, 0)
        gal = core_with_gallows.get(core, 0)
        e_dist = core_e_distribution[core]
        e0 = e_dist.get(0, 0)
        e1 = e_dist.get(1, 0)
        e2 = e_dist.get(2, 0)

        sh_pct = 100*sh/total
        ch_pct = 100*ch/total
        other_pct = 100*other/total
        gal_pct = 100*gal/total
        e0_pct = 100*e0/total
        e1_pct = 100*e1/total
        e2_pct = 100*e2/total

        # Classification logic
        if core in SUBSTANCES:
            ctype = "SUBSTANCE"
        elif core == "y":
            if sh_pct + ch_pct > 30:
                ctype = "DUAL(mat/verb)"
            else:
                ctype = "VERB"
        elif core == "dy":
            if sh_pct + ch_pct > 30:
                ctype = "DUAL(mat+et/vrb)"
            else:
                ctype = "VERB+ET"
        elif core == "ey":
            ctype = "DUAL(mat/verb)"
        elif sh_pct + ch_pct > 50:
            ctype = "SUBSTANCE?"
        elif sh_pct + ch_pct > 25:
            ctype = "DUAL?"
        elif gal_pct > 10:
            ctype = "VERB?"
        elif other_pct > 70:
            ctype = "STANDALONE"
        else:
            ctype = "UNKNOWN"

        expanded[core] = ctype

        print(f"  {core:>10s} {total:6d} {sh_pct:5.1f} {ch_pct:5.1f} {other_pct:6.1f} {gal_pct:5.1f} {e0_pct:5.1f} {e1_pct:5.1f} {e2_pct:5.1f} {ctype:>15s}")

    return expanded, all_cores


# ══════════════════════════════════════════
# PHASE 2: e-count patterns — are multiples of known suffixes hiding?
# ══════════════════════════════════════════
def phase2_e_patterns(all_cores):
    print()
    print("=" * 70)
    print("PHASE 2: E-COUNT PATTERNS — Multiples of known suffixes?")
    print("=" * 70)

    # For each known suffix, check if e+suffix, ee+suffix, eee+suffix exist
    print(f"\n  {'Base':>8s} {'0e':>7s} {'1e':>7s} {'2e':>7s} {'3e':>7s} {'Total':>7s}")
    for base in ["dy", "ey", "y", "ol", "or", "al", "ar", "ody", "ckhy", "os"]:
        e0 = all_cores.get(base, 0)
        e1 = all_cores.get("e" + base, 0)
        e2 = all_cores.get("ee" + base, 0)
        e3 = all_cores.get("eee" + base, 0)
        total = e0 + e1 + e2 + e3
        print(f"  {base:>8s} {e0:7d} {e1:7d} {e2:7d} {e3:7d} {total:7d}")

    # Also check ch+suffix and sh+suffix
    print(f"\n  CH/SH + KNOWN SUFFIX:")
    print(f"  {'Compound':>10s} {'Count':>7s} {'= ch/sh + ?':>20s}")
    for pfx in ["ch", "sh"]:
        for base in ["ol", "or", "al", "ar", "ody", "ckhy", "os", "dy", "ey", "y"]:
            compound = pfx + base
            if compound in all_cores and all_cores[compound] >= 50:
                meaning = f"{pfx}+{base}"
                if base in SUBSTANCES:
                    meaning += f" = [{pfx.upper()}]{SUBSTANCES[base]}"
                print(f"  {compound:>10s} {all_cores[compound]:7d} {meaning:>20s}")

    # Check for NEW patterns: cores that are just prefix+known
    print(f"\n  RECLASSIFIABLE CORES (prefix embedded in core):")
    reclassified = {}
    for core, count in all_cores.most_common(100):
        if core in SUBSTANCES or core in ("y", "dy", "ey", "UNIT"):
            continue
        # Check if core = ch/sh + known_substance
        for pfx in ["ch", "sh"]:
            remainder = core[len(pfx):] if core.startswith(pfx) else None
            if remainder and remainder in SUBSTANCES:
                reclassified[core] = (pfx, remainder, SUBSTANCES[remainder])
                print(f"    {core:>10s} ({count:5d}x) = {pfx}+{remainder} = [{'P' if pfx=='ch' else 'M'}]{SUBSTANCES[remainder]}")
        # Check if core = cth/ckh + something
        for pfx in ["cth", "ckh"]:
            if core.startswith(pfx) and len(core) > len(pfx):
                remainder = core[len(pfx):]
                if remainder in ("y", "dy", "ey", "ol", "or", "al", "ar"):
                    reclassified[core] = (pfx, remainder, f"[{pfx}]{remainder}")
                    print(f"    {core:>10s} ({count:5d}x) = {pfx}+{remainder}")

    return reclassified


# ══════════════════════════════════════════
# PHASE 3: Build expanded decoder
# ══════════════════════════════════════════
def phase3_build_decoder(lines, expanded, reclassified):
    print()
    print("=" * 70)
    print("PHASE 3: EXPANDED DECODER — Reclassified tokens")
    print("=" * 70)

    # New substance map: add ch+known and sh+known
    new_substances = dict(SUBSTANCES)
    for core, (pfx, base, meaning) in reclassified.items():
        if base in SUBSTANCES:
            state = "[P]" if pfx == "ch" else "[M]" if pfx == "sh" else ""
            new_substances[core] = f"{state}{SUBSTANCES[base]}"

    # Verb map
    VERB_BY_PREFIX = {
        "qo": "misce", "qok": "misce", "qot": "misce",
        "d": "coque", "da": "coque",
        "ol": "cola", "l": "cola",
        "sh": "tere", "ch": "fiat",
        "y": "solve", "r": "repete",
        "ok": "adde", "ot": "adde",
        "": "fac", "k": "fac",
    }
    GALLOWS_VERB = {"p": "Rx", "f": "Rx", "t": "signa"}
    PREFIX_PREP = {
        "qo": "cum", "qok": "cum", "qot": "cum",
        "d": "in", "da": "in", "ol": "ex", "l": "per",
        "y": "de", "r": "re", "": "", "ok": "", "ot": "", "k": "",
    }

    # STATE markers: sh/ch + y/dy/ey = material state
    STATE_MARKERS = {
        "[P]y": "[P]MATERIA", "[M]y": "[M]MATERIA",
        "[P]dy": "[P]MATERIA et", "[M]dy": "[M]MATERIA et",
        "[P]ey": "[P]MATERIA.1", "[M]ey": "[M]MATERIA.1",
    }

    # Unknown registry
    unk_reg = {}
    unk_n = [0]
    def get_unk(core):
        if core not in unk_reg:
            unk_n[0] += 1
            unk_reg[core] = f"UNK_{unk_n[0]:03d}"
        return unk_reg[core]

    def decode(token):
        g, pfx, e, core, un, ut = strip_token(token)
        base_pfx = pfx.split("+")[0]
        is_sh = base_pfx == "sh"
        is_ch = base_pfx == "ch"
        is_material = is_sh or is_ch
        state = "[M]" if is_sh else "[P]" if is_ch else ""
        qty = f"{e}×" if e > 0 else ""
        g_str = GALLOWS_VERB.get(g, "") if g else ""
        prep = PREFIX_PREP.get(base_pfx, "") if not is_material else ""
        connector = ""

        # UNIT
        if core == "UNIT":
            sym = "℥" if ut == "n" else "ʒ"
            unit = f"{un}{sym}"
            return " ".join(p for p in [g_str, prep, unit] if p), "UNIT"

        # KNOWN SUBSTANCE
        if core in new_substances:
            s = new_substances[core]
            return " ".join(p for p in [g_str, prep, f"{state}{qty}{s}"] if p), "SUBSTANCE"

        # DUAL SUFFIX (y, dy, ey)
        if core in ("y", "dy", "ey"):
            connector = " et" if core == "dy" else ""
            suffix_num = ".1" if core == "ey" else ""

            if is_material:
                # State marker: "[M]MATERIA" or "[P]MATERIA"
                return f"{state}{qty}MATERIA{suffix_num}{connector}", "STATE"

            if g:
                verb = GALLOWS_VERB.get(g, "§")
                return f"{verb}{suffix_num}{connector}", "VERB"

            verb = VERB_BY_PREFIX.get(base_pfx, "fac")
            e_str = f".{e}" if e > 0 else ""
            return f"{verb}{e_str}{suffix_num}{connector}", "VERB"

        # RECLASSIFIED (cth+y, ckh+ey, etc.)
        if core in reclassified:
            rpfx, rbase, rmeaning = reclassified[core]
            return " ".join(p for p in [g_str, prep, f"{state}{qty}{rmeaning}"] if p), "SUBSTANCE"

        # UNKNOWN
        unk = get_unk(core)
        return " ".join(p for p in [g_str, prep, f"{state}{qty}{unk}"] if p), "UNKNOWN"

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

    total = sum(stats.values())
    known = total - stats["UNKNOWN"]
    print(f"\n  CLASSIFICATION:")
    for cat, n in stats.most_common():
        print(f"    {cat:>12s}: {n:6d} ({100*n/total:.1f}%)")
    print(f"    {'KNOWN':>12s}: {known:6d} ({100*known/total:.1f}%)")
    print(f"  Unknown labels: {unk_n[0]}")

    # === SHOW BEST LINES ===
    scored = [(sum(1 for c in dl["cats"] if c != "UNKNOWN") / len(dl["cats"]) * 100,
               len(dl["cats"]), dl) for dl in decoded_lines if len(dl["cats"]) >= 5]
    scored.sort(key=lambda x: (-x[0], -x[1]))

    print(f"\n  TOP PHARMA RECIPES (S/P, 5+tok, 80%+):")
    shown = 0
    for pct, n, dl in scored:
        if shown >= 15: break
        if dl["section"] not in ("S", "P"): continue
        if pct < 80: continue
        print(f"\n    [{dl['folio']}] {pct:.0f}%, {n}tok")
        print(f"      {dl['decoded'][:130]}")
        shown += 1

    print(f"\n  TOP F103R/V:")
    shown = 0
    for pct, n, dl in scored:
        if shown >= 10: break
        if dl["folio"].upper() not in ("F103R", "F103V"): continue
        if pct < 70: continue
        print(f"\n    [{dl['folio']}] {pct:.0f}%, {n}tok")
        print(f"      {dl['decoded'][:130]}")
        shown += 1

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

    with open(BASE / "VOYNICH_DECODED_V33.txt", 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))

    rev_reg = {v: k for k, v in unk_reg.items()}
    unk_freq = Counter()
    for dl in decoded_lines:
        for m in re.findall(r'UNK_\d+', dl["decoded"]):
            unk_freq[m] += 1

    with open(RESULTS / "v33_expanded.json", 'w', encoding='utf-8') as f:
        json.dump({
            "stats": dict(stats),
            "known_pct": round(100*known/total, 1),
            "unknowns": unk_n[0],
            "registry_top50": [(uid, rev_reg.get(uid,"?"), freq) for uid, freq in unk_freq.most_common(50)],
            "new_substances": {k: v for k, v in new_substances.items() if k not in SUBSTANCES},
            "reclassified": {k: v[2] for k, v in reclassified.items()},
        }, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*70}")
    print(f"V33 FINAL: {known}/{total} ({100*known/total:.1f}%) known")
    print(f"  Output: VOYNICH_DECODED_V33.txt")
    print(f"  Unknowns: {unk_n[0]}")

    return decoded_lines, stats, unk_reg


if __name__ == "__main__":
    print("V33 EXPAND KNOWN")
    print("=" * 70)
    lines = parse_lines()
    print(f"  {len(lines)} lines, {sum(len(l['words']) for l in lines)} tokens\n")

    expanded, all_cores = phase1_analyze_unknowns(lines)
    reclassified = phase2_e_patterns(all_cores)
    phase3_build_decoder(lines, expanded, reclassified)
