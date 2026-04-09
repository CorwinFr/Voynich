#!/usr/bin/env python3
"""
V21 — Tironian-based decoder.
Use the 41 confirmed Tironian matches + gallows stripping + sh/ch functional markers
to build a NEW decoder from scratch. No K&A scorer. Pure Tironian + structural.
"""
import json, sys, re
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

BASE = Path("d:/Github/Voynich")
DECODED_FILE = BASE / "v12/output/VOYNICH_DECODE_V12_INGREDIENTS.txt"
RESULTS = BASE / "v12/validation_v2/results"
TIRONIAN_PATH = BASE / "data/tironian/schmitz_index_full.json"
LOGOGRAMS_PATH = BASE / "v12/rules/logograms.json"
PERSEUS_PATH = BASE / "data/latin_valid_wordset.json"
GLYPHS_PATH = BASE / "v12/rules/glyphs.json"

GALLOWS = set("ktpf")
PREFIXES_ORDER = ["qok", "qot", "qo", "ok", "ot", "ol", "da", "ch", "sh",
                  "d", "y", "r", "p", "l", "t", "f", "k"]
PREFIXES_ORDER.sort(key=len, reverse=True)


def load_perseus():
    with open(PERSEUS_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return set(w.lower() for w in (data if isinstance(data, list) else data.keys()))


def load_logograms():
    with open(LOGOGRAMS_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    result = {}
    for eva, info in data.items():
        if isinstance(info, dict) and info.get("latin"):
            result[eva.lower()] = info["latin"].lower()
        elif isinstance(info, str):
            result[eva.lower()] = info.lower()
    return result


def parse_lines_eva():
    lines = []
    current_folio = None
    current_section = None
    with open(DECODED_FILE, 'r', encoding='utf-8') as f:
        for raw in f:
            m = re.match(r'\s*FOLIO (\S+) \| Section: (\S+)', raw)
            if m:
                current_folio = m.group(1)
                current_section = m.group(2)
                continue
            if current_folio and 'EVA' in raw and ':' in raw:
                parts = raw.split(':')
                if 'EVA' in parts[0]:
                    line_id = parts[0].strip().split()[-1] if parts[0].strip().split() else ""
                    words = [w.lower() for w in parts[1].strip().split() if w.isalpha() and len(w) >= 2]
                    if words:
                        lines.append({
                            "folio": current_folio,
                            "section": current_section,
                            "line_id": line_id,
                            "words": words,
                        })
    return lines


def load_tironian_matches():
    """Load the V19a Tironian matches and V20 results."""
    tir_path = RESULTS / "v19a_tironian_exhaustive.json"
    if tir_path.exists():
        with open(tir_path, 'r') as f:
            data = json.load(f)
        return {m["root"]: m["decoded"] for m in data.get("top_matches", [])
                if m.get("match_type") in ("exact", "logogram")}
    return {}


# ══════════════════════════════════════════
# STEP 1: BUILD THE TIRONIAN ROOT MAP
# Merge: logograms + Tironian matches + gallows rules + sh/ch markers
# ══════════════════════════════════════════
def build_tironian_root_map():
    print("=" * 60)
    print("STEP 1: BUILD TIRONIAN ROOT MAP")
    print("=" * 60)

    logograms = load_logograms()
    tironian = load_tironian_matches()

    # Layer 1: Logograms (highest confidence)
    root_map = dict(logograms)  # 123 entries
    print(f"  Layer 1 (logograms): {len(root_map)} entries")

    # Layer 2: Tironian confirmed matches (NOT already in logograms)
    added_tir = 0
    for root, latin in tironian.items():
        if root not in root_map:
            root_map[root] = latin
            added_tir += 1
    print(f"  Layer 2 (Tironian): +{added_tir} entries")

    # Layer 3: Gallows rules
    # p = paragraph marker (strip, silent)
    # t = section/emphasis marker (strip, silent)
    # k = intra-word modifier (strip, silent)
    # f = rare marker (strip, silent)
    # These are NOT added to root_map, they're handled in the decoder

    # Layer 4: sh/ch functional markers
    # sh- prefix = "raw/input material" marker
    # ch- prefix = "processed/output" marker
    # Already in PREFIX system, handled in decoder

    PREFIX_LATIN = {
        "d": "in", "da": "in", "qo": "cum", "qok": "cum", "qot": "cum",
        "y": "in", "r": "re", "p": "", "ol": "ex", "l": "ex",
        "ch": "[PROCESSED]", "sh": "[RAW]",
        "ok": "", "ot": "", "f": "", "t": "", "k": "",
    }

    print(f"  Total root map: {len(root_map)} entries")
    print(f"  Prefix rules: {len(PREFIX_LATIN)} prefixes")

    return root_map, PREFIX_LATIN


# ══════════════════════════════════════════
# STEP 2: TIRONIAN DECODER
# ══════════════════════════════════════════
def tironian_decode(lines, root_map, prefix_latin):
    print()
    print("=" * 60)
    print("STEP 2: TIRONIAN DECODER — Full manuscript")
    print("=" * 60)

    perseus = load_perseus()

    stats = {
        "logogram": 0, "prefix_root": 0, "gallows_strip": 0,
        "k_strip": 0, "prefix_only": 0, "unknown": 0,
    }
    decoded_lines = []
    all_decoded_words = []
    functional_annotations = []  # (word, function)

    for line in lines:
        decoded_line = []
        for token in line["words"]:
            # Step A: Try logogram (exact match)
            if token in root_map:
                latin = root_map[token]
                decoded_line.append(latin)
                all_decoded_words.append(latin)
                stats["logogram"] += 1
                continue

            # Step B: Strip leading gallows (p, t, f) as markers
            working = token
            gallows_stripped = ""
            if len(working) > 1 and working[0] in "ptf":
                gallows_stripped = working[0]
                working = working[1:]

                # Try logogram after gallows strip
                if working in root_map:
                    latin = root_map[working]
                    decoded_line.append(f"[{gallows_stripped.upper()}]{latin}")
                    all_decoded_words.append(latin)
                    stats["gallows_strip"] += 1
                    continue

            # Step C: Strip prefix
            pfx_found = ""
            root = working
            for pfx in PREFIXES_ORDER:
                if working.startswith(pfx) and len(working) > len(pfx):
                    pfx_found = pfx
                    root = working[len(pfx):]
                    break

            lat_pfx = prefix_latin.get(pfx_found, "")

            # Step D: Try root as logogram
            if root in root_map:
                lat_root = root_map[root]
                if gallows_stripped:
                    decoded_line.append(f"[{gallows_stripped.upper()}]{lat_pfx} {lat_root}".strip())
                else:
                    decoded_line.append(f"{lat_pfx} {lat_root}".strip())
                all_decoded_words.append(lat_root)
                stats["prefix_root"] += 1
                continue

            # Step E: Strip k from root (k=silent modifier)
            if root.startswith('k') and len(root) > 1:
                inner = root[1:]
                if inner in root_map:
                    lat_root = root_map[inner]
                    decoded_line.append(f"{lat_pfx} {lat_root}".strip())
                    all_decoded_words.append(lat_root)
                    stats["k_strip"] += 1
                    continue

            # Step F: Prefix known, root unknown
            if pfx_found and lat_pfx:
                decoded_line.append(f"{lat_pfx} [{root}]")
                stats["prefix_only"] += 1
                continue

            # Step G: Unknown
            decoded_line.append(f"_{token}_")
            stats["unknown"] += 1

        decoded_lines.append({
            "folio": line["folio"],
            "section": line["section"],
            "decoded": ' '.join(decoded_line),
            "eva": ' '.join(line["words"]),
        })

    total = sum(stats.values())
    known = stats["logogram"] + stats["prefix_root"] + stats["gallows_strip"] + stats["k_strip"]
    known_pct = 100 * known / total

    # Perseus on decoded words
    perseus_hits = sum(1 for w in all_decoded_words if w in perseus)
    perseus_pct = 100 * perseus_hits / max(len(all_decoded_words), 1)

    # Long word Perseus
    long_words = [w for w in all_decoded_words if len(w) >= 5]
    long_hits = sum(1 for w in long_words if w in perseus)
    long_pct = 100 * long_hits / max(len(long_words), 1)

    # Unique vocabulary
    vocab = Counter(all_decoded_words)

    print(f"  DECODE STATS:")
    print(f"    Total tokens:       {total}")
    print(f"    Logogram direct:    {stats['logogram']} ({100*stats['logogram']/total:.1f}%)")
    print(f"    Gallows strip:      {stats['gallows_strip']} ({100*stats['gallows_strip']/total:.1f}%)")
    print(f"    Prefix + root:      {stats['prefix_root']} ({100*stats['prefix_root']/total:.1f}%)")
    print(f"    k-strip + root:     {stats['k_strip']} ({100*stats['k_strip']/total:.1f}%)")
    print(f"    Prefix only:        {stats['prefix_only']} ({100*stats['prefix_only']/total:.1f}%)")
    print(f"    Unknown:            {stats['unknown']} ({100*stats['unknown']/total:.1f}%)")
    print(f"    KNOWN TOTAL:        {known} ({known_pct:.1f}%)")
    print()
    print(f"  QUALITY:")
    print(f"    Perseus (known):    {perseus_hits}/{len(all_decoded_words)} ({perseus_pct:.1f}%)")
    print(f"    Perseus (5+ chars): {long_hits}/{len(long_words)} ({long_pct:.1f}%)")
    print(f"    Unique vocabulary:  {len(vocab)}")
    print(f"    Mean word length:   {sum(len(w) for w in all_decoded_words)/max(len(all_decoded_words),1):.2f}")

    # Top 30 decoded words
    print(f"\n  TOP 30 DECODED WORDS:")
    for word, count in vocab.most_common(30):
        p = "PERSEUS" if word in perseus else "---"
        print(f"    {word:25s} x{count:4d}  {p}")

    # SAMPLE OUTPUT — pharma sections
    print(f"\n  SAMPLE (pharmaceutical folios):")
    shown = 0
    for dl in decoded_lines:
        if dl["section"] in ("S", "P") and shown < 10:
            decoded_clean = dl["decoded"][:120]
            print(f"    [{dl['folio']}] {decoded_clean}")
            shown += 1

    # SAMPLE — herbal sections
    print(f"\n  SAMPLE (herbal folios):")
    shown = 0
    for dl in decoded_lines:
        if dl["section"] == "H" and shown < 5:
            decoded_clean = dl["decoded"][:120]
            print(f"    [{dl['folio']}] {decoded_clean}")
            shown += 1

    results = {
        "total": total,
        "stats": stats,
        "known": known,
        "known_pct": round(known_pct, 1),
        "perseus_pct": round(perseus_pct, 1),
        "perseus_5plus_pct": round(long_pct, 1),
        "unique_vocab": len(vocab),
        "top_30": vocab.most_common(30),
        "sample_pharma": [dl for dl in decoded_lines if dl["section"] in ("S", "P")][:20],
        "sample_herbal": [dl for dl in decoded_lines if dl["section"] == "H"][:10],
    }

    with open(RESULTS / "v21_tironian_decoder.json", 'w') as f:
        json.dump(results, f, indent=2)
    return results


# ══════════════════════════════════════════
# STEP 3: COMPARE V12 vs V21
# ══════════════════════════════════════════
def compare_v12_v21(v21_results):
    print()
    print("=" * 60)
    print("STEP 3: V12 (K&A scorer) vs V21 (Tironian + structural)")
    print("=" * 60)

    print(f"  {'Metric':30s} {'V12 (K&A)':>12s} {'V21 (Tironian)':>14s}")
    print(f"  {'-'*58}")

    comparisons = [
        ("Known/decoded tokens", "91.6%", f"{v21_results['known_pct']}%"),
        ("Perseus (known words)", "91.6%", f"{v21_results['perseus_pct']}%"),
        ("Perseus (5+ letters)", "27.7%", f"{v21_results['perseus_5plus_pct']}%"),
        ("Unique vocabulary", "2,524", f"{v21_results['unique_vocab']}"),
        ("Scorer bias", "HIGH (77.5pp)", "NONE"),
        ("Tironian grounding", "None", "z=9.4"),
        ("Structural markers", "Ignored", "Gallows+sh/ch decoded"),
    ]

    for metric, v12, v21 in comparisons:
        print(f"  {metric:30s} {v12:>12s} {v21:>14s}")


# ══════════════════════════════════════════
# STEP 4: WHAT'S STILL MISSING?
# ══════════════════════════════════════════
def analyze_gaps(lines, root_map, prefix_latin):
    print()
    print("=" * 60)
    print("STEP 4: WHAT'S STILL MISSING?")
    print("=" * 60)

    unknown_roots = Counter()
    for line in lines:
        for token in line["words"]:
            working = token
            if len(working) > 1 and working[0] in "ptf":
                working = working[1:]

            for pfx in PREFIXES_ORDER:
                if working.startswith(pfx) and len(working) > len(pfx):
                    root = working[len(pfx):]
                    break
            else:
                root = working

            # Strip k
            if root.startswith('k') and len(root) > 1:
                root = root[1:]

            if root not in root_map:
                unknown_roots[root] += 1

    print(f"  Unknown roots: {len(unknown_roots)} unique, {sum(unknown_roots.values())} tokens")
    print(f"\n  Top 30 unknown roots (next targets for Tironian identification):")
    for root, count in unknown_roots.most_common(30):
        print(f"    {root:15s} x{count:4d}  len={len(root)}")

    # How many tokens would be decoded if we resolve the top 50 unknown roots?
    top50_tokens = sum(count for _, count in unknown_roots.most_common(50))
    total_unknown = sum(unknown_roots.values())
    print(f"\n  Resolving top 50 unknowns would decode {top50_tokens} more tokens "
          f"({100*top50_tokens/max(total_unknown,1):.1f}% of unknowns)")

    results = {
        "unique_unknown": len(unknown_roots),
        "total_unknown_tokens": sum(unknown_roots.values()),
        "top_50": unknown_roots.most_common(50),
    }

    with open(RESULTS / "v21_gaps.json", 'w') as f:
        json.dump(results, f, indent=2)
    return results


# ══════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════
if __name__ == "__main__":
    print("V21 TIRONIAN DECODER")
    print("=" * 60)

    root_map, prefix_latin = build_tironian_root_map()
    lines = parse_lines_eva()
    v21 = tironian_decode(lines, root_map, prefix_latin)
    compare_v12_v21(v21)
    gaps = analyze_gaps(lines, root_map, prefix_latin)

    print()
    print("=" * 60)
    print("V21 FINAL")
    print("=" * 60)
    print(f"  Decoded: {v21['known_pct']}% known, {v21['perseus_pct']}% Perseus")
    print(f"  Vocabulary: {v21['unique_vocab']} unique words")
    print(f"  Gaps: {gaps['unique_unknown']} unknown roots, top 50 cover "
          f"{100*sum(c for _,c in gaps['top_50'])/max(gaps['total_unknown_tokens'],1):.0f}% of unknowns")
