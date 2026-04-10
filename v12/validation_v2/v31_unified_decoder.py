#!/usr/bin/env python3
"""
V31 — Unified Decoder: Everything we know in one decoder.

Assembles V22-V30 findings into a single complete decoder:
- Token = [gallows] + [prefix] + [sh/ch] + [e-count] + [CORE]
- CORE is either: SUBSTANCE, VERB(-y/-dy), UNIT(ain/aiin), or UNKNOWN
- Prefix on verbs determines the verb type
- e-count on substances = quantity, on verbs = intensity/position
- Produces full decoded manuscript + gaps analysis

Then: extract herbal labels and attempt plant identification.
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

# ══════════════════════════════════════════
# THE COMPLETE KNOWLEDGE BASE
# ══════════════════════════════════════════

SUBSTANCES = {
    "ol": "oleum",   "or": "hiera",   "al": "sal",     "ar": "aqua",
    "ody": "acetum", "ckhy": "cera",  "os": "succus",  "am": "ana",
}

# Verb system: prefix determines the verb
# -y = verb marker, -dy = verb + et (connector)
VERB_BY_PREFIX = {
    "qo": "misce",    "qok": "misce",   "qot": "misce",
    "d": "coque",     "da": "coque",
    "ol": "cola",     "l": "cola",
    "sh": "tere",
    "ch": "fiat",
    "y": "solve",
    "r": "repete",
    "ok": "adde",     "ot": "adde",
    "": "fac",
    "k": "fac",
}

GALLOWS_VERB = {"p": "recipe", "f": "recipe", "t": "signa"}

PREFIX_PREP = {
    "qo": "cum", "qok": "cum", "qot": "cum",
    "d": "in", "da": "in",
    "ol": "ex", "l": "per",
    "y": "de", "r": "re",
    "sh": "[M]", "ch": "[P]",
    "ok": "", "ot": "", "k": "", "": "",
}

UNIT_PATTERN = re.compile(r'^a?(i+)([nr])$')


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


def decode_token(token):
    """The unified decoder. Returns human-readable string + metadata."""
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

    # UNIT pattern
    um = UNIT_PATTERN.match(w)
    if um:
        n = len(um.group(1))
        sym = "℥" if um.group(2) == "n" else "ʒ"
        unit_str = f"{n}{sym}"
        if gallows:
            return f"{GALLOWS_VERB.get(gallows, '§')} {unit_str}", "UNIT"
        if prefix:
            prep = PREFIX_PREP.get(prefix, prefix)
            if prep: return f"{prep} {unit_str}", "UNIT"
        return unit_str, "UNIT"

    # E-count
    e_count = 0
    valid_cores = set(SUBSTANCES.keys()) | {"y", "dy"}
    while w.startswith('e') and len(w) > 1:
        rem = w[1:]
        if rem in valid_cores or (len(rem) >= 2 and rem[0] != 'e'):
            e_count += 1; w = rem
        else: break

    # SUBSTANCE
    if w in SUBSTANCES:
        subst = SUBSTANCES[w]
        qty = f"{e_count}×" if e_count > 0 else ""
        if gallows:
            g_verb = GALLOWS_VERB.get(gallows, "§")
            if prefix in ("sh", "ch"):
                state = "[M]" if prefix == "sh" else "[P]"
                return f"{g_verb} {state}{qty}{subst}", "SUBSTANCE"
            prep = PREFIX_PREP.get(prefix, "")
            return f"{g_verb} {prep} {qty}{subst}".strip(), "SUBSTANCE"

        if prefix in ("sh", "ch"):
            state = "[M]" if prefix == "sh" else "[P]"
            prep = ""
        else:
            state = ""
            prep = PREFIX_PREP.get(prefix, "")

        parts = [p for p in [prep, f"{state}{qty}{subst}"] if p]
        return " ".join(parts) if parts else f"{qty}{subst}", "SUBSTANCE"

    # VERB (-y or -dy)
    if w in ("y", "dy"):
        connector = " et" if w == "dy" else ""
        intensity = f".{e_count}" if e_count > 0 else ""

        if gallows:
            verb = GALLOWS_VERB.get(gallows, "§")
            return f"{verb}{intensity}{connector}", "VERB"

        # Prefix determines the verb
        base_pfx = prefix.split("+")[0] if "+" in prefix else prefix
        verb = VERB_BY_PREFIX.get(base_pfx, "fac")
        if prefix in ("sh", "ch"):
            state = "[M]" if prefix == "sh" else "[P]"
            return f"{state}{verb}{intensity}{connector}", "VERB"
        return f"{verb}{intensity}{connector}", "VERB"

    # UNKNOWN — still decompose what we can
    qty = f"{e_count}×" if e_count > 0 else ""
    if gallows:
        g_str = GALLOWS_VERB.get(gallows, "§")
        if prefix in ("sh", "ch"):
            state = "[M]" if prefix == "sh" else "[P]"
            return f"{g_str} {state}{qty}«{w}»", "UNKNOWN"
        prep = PREFIX_PREP.get(prefix, "")
        return f"{g_str} {prep} {qty}«{w}»".strip(), "UNKNOWN"

    if prefix in ("sh", "ch"):
        state = "[M]" if prefix == "sh" else "[P]"
        return f"{state}{qty}«{w}»", "UNKNOWN"

    prep = PREFIX_PREP.get(prefix, "")
    if prep:
        return f"{prep} {qty}«{w}»".strip(), "UNKNOWN"

    return f"{qty}«{w}»" if qty else f"«{w}»", "UNKNOWN"


# ══════════════════════════════════════════
# DECODE FULL MANUSCRIPT
# ══════════════════════════════════════════
def decode_manuscript(lines):
    print("=" * 70)
    print("FULL MANUSCRIPT DECODE")
    print("=" * 70)

    stats = Counter()
    unknown_cores = Counter()
    decoded_lines = []

    for line in lines:
        parts = []
        line_cats = []
        for w in line["words"]:
            decoded, cat = decode_token(w)
            parts.append(decoded)
            line_cats.append(cat)
            stats[cat] += 1
            if cat == "UNKNOWN":
                # Extract the core for gap analysis
                core = decoded.split("«")[1].split("»")[0] if "«" in decoded else decoded
                unknown_cores[core] += 1

        decoded_lines.append({
            "folio": line["folio"], "section": line["section"],
            "eva": " ".join(line["words"]),
            "decoded": " . ".join(parts),
            "cats": line_cats,
        })

    total = sum(stats.values())
    print(f"\n  TOKEN CLASSIFICATION:")
    for cat, count in stats.most_common():
        print(f"    {cat:>12s}: {count:6d} ({100*count/total:.1f}%)")
    print(f"    {'TOTAL':>12s}: {total:6d}")
    known = total - stats.get("UNKNOWN", 0)
    print(f"\n  KNOWN: {known}/{total} ({100*known/total:.1f}%)")

    return decoded_lines, unknown_cores


# ══════════════════════════════════════════
# HERBAL LABELS — THE ROSETTA STONE
# ══════════════════════════════════════════
def extract_herbal_labels(lines, decoded_lines):
    print()
    print("=" * 70)
    print("HERBAL LABELS — Plant Name Identification")
    print("=" * 70)
    print()

    # Herbal pages typically have short lines (1-3 tokens) that are labels
    # And longer lines that describe properties/uses
    # The FIRST short line on each folio is often the plant name

    herbal_folios = sorted(set(l["folio"] for l in lines if l["section"] == "H"))
    print(f"  Herbal folios: {len(herbal_folios)}")

    labels = []
    for hf in herbal_folios:
        folio_lines = [(l, dl) for l, dl in zip(lines, decoded_lines)
                       if l["folio"] == hf]
        if not folio_lines: continue

        # First line is often the label
        first_line, first_dl = folio_lines[0]
        # Also check for short lines (labels scattered in text)
        short_lines = [(l, dl) for l, dl in folio_lines if len(l["words"]) <= 3]

        if short_lines:
            label_line, label_dl = short_lines[0]
        else:
            label_line, label_dl = first_line, first_dl

        labels.append({
            "folio": hf,
            "eva": " ".join(label_line["words"]),
            "decoded": label_dl["decoded"],
            "n_tokens": len(label_line["words"]),
            "unknowns": [w for w, c in zip(label_dl["decoded"].split(" . "), label_dl["cats"])
                        if c == "UNKNOWN"],
        })

    # Print all labels
    print(f"\n  {'Folio':>8s} {'EVA':>30s} {'Decoded':>50s}")
    print(f"  {'-'*90}")
    for lab in labels:
        print(f"  {lab['folio']:>8s} {lab['eva']:>30s} {lab['decoded'][:50]:>50s}")

    # Extract unknown cores from labels — these are PLANT NAMES
    plant_candidates = Counter()
    for lab in labels:
        for unk in lab["unknowns"]:
            core = unk.split("«")[1].split("»")[0] if "«" in unk else ""
            if core and len(core) >= 2:
                plant_candidates[core] += 1

    print(f"\n  CANDIDATE PLANT NAME CORES ({len(plant_candidates)} unique):")
    print(f"  These are the unknown cores in herbal labels = likely plant names")
    for core, count in plant_candidates.most_common(30):
        print(f"    «{core}»: appears in {count} label(s)")

    return labels, plant_candidates


# ══════════════════════════════════════════
# SCHMITZ PLANT NAME SEARCH
# ══════════════════════════════════════════
def search_plant_names(plant_candidates):
    print()
    print("=" * 70)
    print("SCHMITZ SEARCH — Plant names in Tironian index")
    print("=" * 70)

    with open(TIRONIAN_PATH, 'r', encoding='utf-8') as f:
        schmitz = json.load(f)

    # Build plant-relevant subset
    plant_entries = []
    for entry in schmitz:
        val = entry.get("latin_value", "").lower()
        domains = entry.get("domains", [])
        if any(d in ("botanical", "medical", "pharmaceutical") for d in domains):
            plant_entries.append(entry)
        # Also include common plant names regardless of domain
        if val in ("rosa", "salvia", "mentha", "malva", "urtica", "plantago",
                   "artemisia", "absinthium", "ruta", "anethum", "foeniculum",
                   "petroselinum", "apium", "cannabis", "papaver", "mandragora",
                   "helleborus", "gentiana", "verbena", "betonica", "centaurea",
                   "hyssopus", "origanum", "thymus", "basilicum", "lavandula",
                   "rosmarinus", "cinnamomum", "piper", "zingiber", "crocus",
                   "aloe", "myrrha", "thus", "galbanum", "bdellium",
                   "nardus", "cassia", "costus", "amomum"):
            plant_entries.append(entry)

    print(f"  Plant-relevant Schmitz entries: {len(plant_entries)}")

    # For each candidate core, search for matching plant names
    print(f"\n  PLANT NAME MATCHES:")
    print(f"  {'Core':>15s} {'Schmitz match':>20s} {'Domains':>30s}")

    matches = {}
    for core, count in plant_candidates.most_common(40):
        # Search by similarity (length match, partial match)
        best = None
        for entry in plant_entries:
            val = entry.get("latin_value", "").lower()
            # Exact length match (EVA core ≈ Latin word in length)
            if abs(len(core) - len(val)) <= 2 and len(val) >= 3:
                # Check first letter similarity
                if core[0] == val[0] or (core[0] in "aeiou" and val[0] in "aeiou"):
                    if not best or len(val) > len(best.get("latin_value", "")):
                        best = entry

        if best:
            val = best.get("latin_value", "")
            domains = best.get("domains", [])
            matches[core] = val
            print(f"  «{core}»{' '*(13-len(core))} → {val:>20s} {str(domains):>30s}")
        else:
            print(f"  «{core}»{' '*(13-len(core))} → {'---':>20s}")

    return matches


# ══════════════════════════════════════════
# SHOW BEST DECODED PAGES
# ══════════════════════════════════════════
def show_best_pages(decoded_lines):
    print()
    print("=" * 70)
    print("BEST DECODED FOLIOS (highest known %)")
    print("=" * 70)

    # Group by folio and compute known %
    folio_stats = defaultdict(lambda: {"known": 0, "total": 0, "lines": []})
    for dl in decoded_lines:
        fs = folio_stats[dl["folio"]]
        for cat in dl["cats"]:
            fs["total"] += 1
            if cat != "UNKNOWN":
                fs["known"] += 1
        fs["lines"].append(dl)

    ranked = sorted(folio_stats.items(),
                    key=lambda x: -x[1]["known"]/max(x[1]["total"],1))

    print(f"\n  TOP 20 BEST DECODED FOLIOS:")
    print(f"  {'Folio':>10s} {'Section':>8s} {'Known%':>7s} {'Tokens':>7s} {'Lines':>6s}")
    for folio, fs in ranked[:20]:
        sec = fs["lines"][0]["section"] if fs["lines"] else "?"
        pct = 100 * fs["known"] / max(fs["total"], 1)
        print(f"  {folio:>10s} {sec:>8s} {pct:7.1f} {fs['total']:7d} {len(fs['lines']):6d}")

    # Show the #1 best folio fully decoded
    if ranked:
        best_folio, best_fs = ranked[0]
        print(f"\n  BEST FOLIO: {best_folio} ({100*best_fs['known']/best_fs['total']:.0f}% known)")
        for dl in best_fs["lines"][:10]:
            print(f"    EVA: {dl['eva'][:90]}")
            print(f"    DEC: {dl['decoded'][:90]}")
            print()


# ══════════════════════════════════════════
# GAPS ANALYSIS
# ══════════════════════════════════════════
def gaps_analysis(unknown_cores):
    print()
    print("=" * 70)
    print("GAPS ANALYSIS — What's still unknown?")
    print("=" * 70)

    total_unknown = sum(unknown_cores.values())
    unique_unknown = len(unknown_cores)

    print(f"\n  Unknown tokens: {total_unknown}")
    print(f"  Unique unknown cores: {unique_unknown}")

    # Top 30 unknowns
    print(f"\n  TOP 30 UNKNOWN CORES (next targets):")
    cumul = 0
    for core, count in unknown_cores.most_common(30):
        cumul += count
        pct_of_unknown = 100 * cumul / total_unknown
        print(f"    «{core}»{' '*(15-len(core))} x{count:5d}  (cumul: {pct_of_unknown:.1f}% of unknowns)")

    # How many cores needed to cover 50% of unknowns?
    cumul = 0
    for i, (core, count) in enumerate(unknown_cores.most_common()):
        cumul += count
        if cumul >= total_unknown * 0.5:
            print(f"\n  → {i+1} cores cover 50% of unknowns")
            break

    return total_unknown, unique_unknown


# ══════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════
if __name__ == "__main__":
    print("V31 UNIFIED DECODER — Full Manuscript")
    print("=" * 70)
    print()

    lines = parse_lines_eva()
    print(f"  {len(lines)} lines, {sum(len(l['words']) for l in lines)} tokens\n")

    decoded_lines, unknown_cores = decode_manuscript(lines)
    labels, plant_candidates = extract_herbal_labels(lines, decoded_lines)
    plant_matches = search_plant_names(plant_candidates)
    show_best_pages(decoded_lines)
    total_unk, unique_unk = gaps_analysis(unknown_cores)

    # Save full decoded manuscript
    output = []
    current_folio = None
    for dl in decoded_lines:
        if dl["folio"] != current_folio:
            current_folio = dl["folio"]
            output.append(f"\n{'='*60}")
            output.append(f"  FOLIO {dl['folio']} | Section: {dl['section']}")
            output.append(f"{'='*60}")
        output.append(f"  EVA: {dl['eva']}")
        output.append(f"  DEC: {dl['decoded']}")

    with open(BASE / "VOYNICH_DECODED_V31.txt", 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))

    # Save JSON results
    results = {
        "total_tokens": sum(len(l["words"]) for l in lines),
        "known_pct": round(100 * (sum(len(l["words"]) for l in lines) - sum(unknown_cores.values())) / sum(len(l["words"]) for l in lines), 1),
        "unknown_cores_top50": unknown_cores.most_common(50),
        "herbal_labels": len(labels),
        "plant_candidates": len(plant_candidates),
    }
    with open(RESULTS / "v31_unified_decoder.json", 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print()
    print("=" * 70)
    print("V31 FINAL")
    print("=" * 70)
    known = sum(len(l["words"]) for l in lines) - sum(unknown_cores.values())
    total = sum(len(l["words"]) for l in lines)
    print(f"  Decoded: {known}/{total} ({100*known/total:.1f}%)")
    print(f"  Unknown cores: {unique_unk} unique, {total_unk} tokens")
    print(f"  Herbal labels extracted: {len(labels)}")
    print(f"  Full decoded manuscript: VOYNICH_DECODED_V31.txt")
    print(f"  Results: {RESULTS / 'v31_unified_decoder.json'}")
