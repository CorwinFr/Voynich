#!/usr/bin/env python3
"""
V23 — Force Decode: Complete Phrase Reconstruction

Strategy: Use EVERYTHING we know to decode complete lines and see if
pharmaceutical instructions emerge. This is exploratory, not validated.

Key insight from V22: morphemes are SUFFIXAL (position 0.67-0.83).
60.7% of tokens have recognizable suffix endings.

Approach:
1. Expand root map with Tironian COMPOSITING rules
2. Add speculative suffix decompositions for top unknowns
3. Decode complete lines, annotate confidence
4. Focus on pharmaceutical folios (S/P sections) where we expect recipes
5. Look for recipe patterns: Recipe X, Misce Y, Coque Z, Cola...
"""
import json, sys, re, math
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

BASE = Path("d:/Github/Voynich")
DECODED_FILE = BASE / "v12/output/VOYNICH_DECODE_V12_INGREDIENTS.txt"
RESULTS = BASE / "v12/validation_v2/results"
TIRONIAN_PATH = BASE / "data/tironian/schmitz_index_full.json"
PERSEUS_PATH = BASE / "data/latin_valid_wordset.json"
LOGOGRAMS_PATH = BASE / "v12/rules/logograms.json"

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


def load_schmitz():
    with open(TIRONIAN_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    index = {}
    for entry in data:
        val = entry.get("latin_value", "").lower()
        if val:
            index[val] = entry
    return index


def load_tironian_matches():
    tir_path = RESULTS / "v19a_tironian_exhaustive.json"
    if tir_path.exists():
        with open(tir_path, 'r') as f:
            data = json.load(f)
        return {m["root"]: m["decoded"] for m in data.get("top_matches", [])
                if m.get("match_type") in ("exact", "logogram")}
    return {}


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
                    words = [w.lower() for w in parts[1].strip().split()
                             if w.isalpha() and len(w) >= 2]
                    if words:
                        lines.append({
                            "folio": current_folio,
                            "section": current_section,
                            "words": words,
                        })
    return lines


# ══════════════════════════════════════════
# STEP 1: BUILD EXPANDED ROOT MAP
# ══════════════════════════════════════════
def build_expanded_root_map():
    print("=" * 70)
    print("STEP 1: EXPANDED ROOT MAP WITH COMPOSITING RULES")
    print("=" * 70)

    logograms = load_logograms()
    tironian = load_tironian_matches()
    perseus = load_perseus()
    schmitz = load_schmitz()

    # Layer 1: Logograms (highest confidence)
    root_map = dict(logograms)
    confidence = {k: "logogram" for k in root_map}

    # Layer 2: Tironian confirmed
    for root, latin in tironian.items():
        if root not in root_map:
            root_map[root] = latin
            confidence[root] = "tironian"

    print(f"  Base: {len(root_map)} entries (logograms + Tironian)")

    # Layer 3: SUFFIX DECOMPOSITION
    # Known suffix values from Tironian:
    SUFFIX_MAP = {
        "dy": "et",      # logogram confirmed
        "iin": "ura",     # Tironian confirmed
        "ey": "on",       # Tironian confirmed
        "ol": "es",       # Tironian confirmed
        "or": "hiera",    # from V19 (approximate)
        "ar": "are",      # Tironian (approximate: infinitive ending)
    }

    # Try to decompose unknown roots via suffix stripping
    # For each unknown root, check if root = base + known_suffix
    # Then check if the resulting Latin word exists in Perseus

    # Load top unknowns from V21 gaps
    with open(RESULTS / "v21_gaps.json", 'r') as f:
        gaps = json.load(f)

    top_unknowns = [(root, count) for root, count in gaps["top_50"]]

    # Also build a mapping of known EVA->Latin for single chars
    # From our confirmed mappings
    CHAR_MAP = {
        "e": "e",   # Latin prefix ex/e
        "a": "a",   # vowel
        "o": "o",   # vowel
        "i": "i",   # vowel
    }

    # Strategy: for each unknown root, try:
    # 1. Direct Schmitz lookup
    # 2. Suffix decomposition: root = X + known_suffix
    # 3. If result is a Perseus word, accept it
    # 4. If result is in Schmitz, accept with higher confidence

    speculative = {}
    speculative_reasons = {}

    print(f"\n  Attempting to resolve top 50 unknowns via compositing...")
    print(f"  {'Root':>12s} {'Count':>6s} {'Decomposition':>25s} {'Latin result':>20s} {'Perseus':>8s} {'Schmitz':>8s}")

    for root, count in top_unknowns:
        if root in root_map:
            continue

        best = None
        best_reason = None

        # Strategy A: Direct Schmitz lookup
        if root in schmitz:
            best = schmitz[root]["latin_value"]
            best_reason = "schmitz_direct"

        # Strategy B: Suffix decomposition
        if not best:
            for suffix, suffix_latin in sorted(SUFFIX_MAP.items(), key=lambda x: -len(x[0])):
                if root.endswith(suffix) and len(root) > len(suffix):
                    base = root[:-len(suffix)]

                    # Try base as known root
                    if base in root_map:
                        candidate = root_map[base] + suffix_latin
                        if candidate in perseus:
                            best = candidate
                            best_reason = f"compose({base}={root_map[base]} + {suffix}={suffix_latin})"
                            break

                    # Try base as single vowel
                    if base in CHAR_MAP:
                        candidate = CHAR_MAP[base] + suffix_latin
                        if candidate in perseus:
                            best = candidate
                            best_reason = f"compose({base}={CHAR_MAP[base]} + {suffix}={suffix_latin})"
                            break

                    # Try just the suffix value
                    # "e" + suffix might be a common Latin word
                    for prefix_try in ["", "e", "a", "i", "o"]:
                        if base == prefix_try or (len(base) == 1 and base in "eaio"):
                            candidate = prefix_try + suffix_latin
                            if candidate in perseus and len(candidate) >= 3:
                                best = candidate
                                best_reason = f"compose({base} + {suffix}={suffix_latin})"
                                break
                    if best:
                        break

        # Strategy C: Double suffix (e.g., eedy = e + e + dy)
        if not best:
            # Try removing repeated initial 'e'
            if root.startswith("ee") and root[2:] in root_map:
                inner = root[2:]
                best = "e" + root_map[inner]
                best_reason = f"e_prefix({inner}={root_map[inner]})"
            elif root.startswith("e") and root[1:] in root_map:
                inner = root[1:]
                best = "e" + root_map[inner]
                best_reason = f"e_prefix({inner}={root_map[inner]})"
            elif root.startswith("e") and root[1:] in speculative:
                inner = root[1:]
                best = "e" + speculative[inner]
                best_reason = f"e_prefix({inner}={speculative[inner]})"

        # Strategy D: Check Schmitz for compound
        if not best and len(root) >= 3:
            # Try all Schmitz entries that start with the first 2-3 chars
            prefix2 = root[:2]
            for schm_word, schm_entry in schmitz.items():
                if schm_word.startswith(prefix2) and len(schm_word) >= 3:
                    # Check if the Schmitz word could map (same length +/- 1)
                    if abs(len(schm_word) - len(root)) <= 1:
                        domains = schm_entry.get("domains", [])
                        if "medical" in domains or "pharmaceutical" in domains:
                            best = schm_word
                            best_reason = f"schmitz_approx(domains={domains})"
                            break

        in_perseus = best in perseus if best else False
        in_schmitz = best in schmitz if best else False

        if best:
            speculative[root] = best
            speculative_reasons[root] = best_reason
            p_mark = "YES" if in_perseus else "no"
            s_mark = "YES" if in_schmitz else "no"
            print(f"  {root:>12s} {count:6d} {best_reason:>25s} {best:>20s} {p_mark:>8s} {s_mark:>8s}")
        else:
            print(f"  {root:>12s} {count:6d} {'---':>25s} {'???':>20s} {'':>8s} {'':>8s}")

    # Add speculative entries to root_map
    for root, latin in speculative.items():
        root_map[root] = latin
        confidence[root] = "speculative"

    print(f"\n  Expanded root map: {len(root_map)} entries")
    print(f"    Logogram:    {sum(1 for v in confidence.values() if v == 'logogram')}")
    print(f"    Tironian:    {sum(1 for v in confidence.values() if v == 'tironian')}")
    print(f"    Speculative: {sum(1 for v in confidence.values() if v == 'speculative')}")

    return root_map, confidence


# ══════════════════════════════════════════
# STEP 2: PREFIX SYSTEM
# ══════════════════════════════════════════
PREFIX_LATIN = {
    "d": "in",      # preposition
    "da": "in",     # preposition (variant)
    "qo": "cum",    # with
    "qok": "cum",   # with (k silent)
    "qot": "cum",   # with (t silent)
    "y": "de",      # about/from (Tironian)
    "r": "re",      # again
    "p": "",         # paragraph marker (silent)
    "ol": "ex",     # from/out of
    "l": "per",     # through
    "ch": "[PRODUCT]",   # processed/output marker
    "sh": "[MATERIA]",   # raw material marker
    "ok": "",       # structural
    "ot": "",       # structural
    "f": "",        # rare marker
    "t": "",        # section marker
    "k": "",        # silent modifier
}

# Gallows as procedural commands (from pharmaceutical abbreviations research)
GALLOWS_FUNCTION = {
    "p": "Rx",      # Recipe (take) — p/f resemble Rx
    "t": "§",       # Section marker
    "k": "",        # Silent medial modifier
    "f": "Rx",      # Recipe variant
}


# ══════════════════════════════════════════
# STEP 3: FORCE DECODE COMPLETE LINES
# ══════════════════════════════════════════
def force_decode(lines, root_map, confidence):
    print()
    print("=" * 70)
    print("STEP 2: FORCE DECODE — Complete pharmaceutical phrases")
    print("=" * 70)

    perseus = load_perseus()

    decoded_lines = []
    stats = Counter()
    all_decoded = []

    for line in lines:
        decoded_tokens = []
        for token in line["words"]:
            result = decode_token(token, root_map, confidence)
            decoded_tokens.append(result)
            stats[result["method"]] += 1
            if result["latin"]:
                all_decoded.append(result["latin"])

        # Build the decoded line
        parts = []
        for dt in decoded_tokens:
            if dt["latin"]:
                parts.append(dt["latin"])
            else:
                parts.append(f"_{dt['eva']}_")

        decoded_lines.append({
            "folio": line["folio"],
            "section": line["section"],
            "eva": ' '.join(line["words"]),
            "decoded": ' '.join(parts),
            "tokens": decoded_tokens,
        })

    total = sum(stats.values())
    known = total - stats.get("unknown", 0)
    print(f"\n  DECODE STATS:")
    for method, count in stats.most_common():
        print(f"    {method:25s}: {count:6d} ({100*count/total:.1f}%)")
    print(f"    {'KNOWN TOTAL':25s}: {known:6d} ({100*known/total:.1f}%)")

    # Perseus check
    perseus_hits = sum(1 for w in all_decoded if w.split()[-1] in perseus)
    print(f"\n  Perseus on decoded: {perseus_hits}/{len(all_decoded)} ({100*perseus_hits/max(len(all_decoded),1):.1f}%)")

    return decoded_lines, stats


def decode_token(token, root_map, confidence):
    """Decode a single EVA token, returning structured result."""
    result = {"eva": token, "latin": None, "method": "unknown",
              "confidence": "none", "parts": []}

    # Step A: Direct logogram
    if token in root_map:
        result["latin"] = root_map[token]
        result["method"] = "logogram"
        result["confidence"] = confidence.get(token, "speculative")
        return result

    # Step B: Strip leading gallows
    working = token
    gallows = ""
    gallows_func = ""
    if len(working) > 1 and working[0] in "ptf":
        gallows = working[0]
        gallows_func = GALLOWS_FUNCTION.get(gallows, "")
        working = working[1:]

        if working in root_map:
            latin = root_map[working]
            if gallows_func:
                result["latin"] = f"{gallows_func} {latin}"
            else:
                result["latin"] = latin
            result["method"] = "gallows_strip"
            result["confidence"] = confidence.get(working, "speculative")
            return result

    # Step C: Strip prefix
    pfx = ""
    root = working
    for p in PREFIXES_ORDER:
        if working.startswith(p) and len(working) > len(p):
            pfx = p
            root = working[len(p):]
            break

    lat_pfx = PREFIX_LATIN.get(pfx, "")

    # Step D: Root lookup
    if root in root_map:
        lat_root = root_map[root]
        parts = []
        if gallows_func:
            parts.append(gallows_func)
        if lat_pfx and lat_pfx not in ("[PRODUCT]", "[MATERIA]"):
            parts.append(lat_pfx)
        if lat_pfx in ("[PRODUCT]", "[MATERIA]"):
            parts.append(lat_pfx)
        parts.append(lat_root)
        result["latin"] = ' '.join(parts)
        result["method"] = "prefix_root"
        result["confidence"] = confidence.get(root, "speculative")
        return result

    # Step E: k-strip from root
    if root.startswith('k') and len(root) > 1:
        inner = root[1:]
        if inner in root_map:
            lat_root = root_map[inner]
            parts = []
            if gallows_func:
                parts.append(gallows_func)
            if lat_pfx:
                parts.append(lat_pfx)
            parts.append(lat_root)
            result["latin"] = ' '.join(parts)
            result["method"] = "k_strip"
            result["confidence"] = confidence.get(inner, "speculative")
            return result

    # Step F: Prefix known, root unknown
    if pfx and lat_pfx:
        parts = []
        if gallows_func:
            parts.append(gallows_func)
        if lat_pfx:
            parts.append(lat_pfx)
        parts.append(f"[{root}]")
        result["latin"] = ' '.join(parts)
        result["method"] = "prefix_only"
        result["confidence"] = "low"
        return result

    # Step G: Unknown
    return result


# ══════════════════════════════════════════
# STEP 4: RECIPE PATTERN DETECTION
# ══════════════════════════════════════════
def detect_recipe_patterns(decoded_lines):
    print()
    print("=" * 70)
    print("STEP 3: RECIPE PATTERN DETECTION")
    print("=" * 70)

    # Look for pharmaceutical recipe patterns:
    # Rx X, Y, Z  (ingredients)
    # cum X (with X)
    # in X (in X)
    # et X (and X)
    # [MATERIA] X (raw material X)
    # [PRODUCT] X (processed product X)

    recipe_keywords = {"Rx", "cum", "in", "ex", "et", "per", "re", "de"}
    material_markers = {"[MATERIA]", "[PRODUCT]"}

    recipe_lines = []
    for dl in decoded_lines:
        words = dl["decoded"].split()
        has_recipe = any(w in recipe_keywords for w in words)
        has_material = any(w in material_markers for w in words)
        unknown_count = sum(1 for w in words if w.startswith("_") or w.startswith("["))
        total_words = len(words)
        known_pct = 100 * (total_words - unknown_count) / max(total_words, 1)

        if known_pct >= 60 and total_words >= 3:
            recipe_lines.append({
                **dl,
                "known_pct": known_pct,
                "has_recipe_keyword": has_recipe,
                "has_material_marker": has_material,
            })

    # Sort by known percentage (best decoded first)
    recipe_lines.sort(key=lambda x: -x["known_pct"])

    # Print the best decoded pharmaceutical lines
    print(f"\n  Best decoded pharma lines (S/P sections, >=60% known):")
    shown = 0
    for rl in recipe_lines:
        if rl["section"] in ("S", "P") and shown < 30:
            print(f"\n    [{rl['folio']}] ({rl['known_pct']:.0f}% known)")
            print(f"      EVA:  {rl['eva'][:100]}")
            print(f"      LAT:  {rl['decoded'][:100]}")
            shown += 1

    # Print best decoded herbal lines
    print(f"\n  Best decoded herbal lines (H sections, >=60% known):")
    shown = 0
    for rl in recipe_lines:
        if rl["section"] == "H" and shown < 20:
            print(f"\n    [{rl['folio']}] ({rl['known_pct']:.0f}% known)")
            print(f"      EVA:  {rl['eva'][:100]}")
            print(f"      LAT:  {rl['decoded'][:100]}")
            shown += 1

    # Print best lines from ANY section
    print(f"\n  Best decoded lines overall (>=80% known, any section):")
    shown = 0
    for rl in recipe_lines:
        if rl["known_pct"] >= 80 and shown < 20:
            print(f"\n    [{rl['folio']}|{rl['section']}] ({rl['known_pct']:.0f}%)")
            print(f"      EVA:  {rl['eva'][:100]}")
            print(f"      LAT:  {rl['decoded'][:100]}")
            shown += 1

    return recipe_lines


# ══════════════════════════════════════════
# STEP 5: FOCUS ON F103R (the "coquo" folio)
# ══════════════════════════════════════════
def focus_f103r(decoded_lines):
    print()
    print("=" * 70)
    print("STEP 4: FOCUS ON F103R — The 'coquo' folio")
    print("=" * 70)
    print("  This folio produced 48 instances of 'coquo' in V12.")
    print("  Let's see what the force decoder produces.\n")

    for dl in decoded_lines:
        if dl["folio"].upper() in ("F103R", "F103V", "F102R", "F102V"):
            print(f"  [{dl['folio']}]")
            print(f"    EVA: {dl['eva']}")
            print(f"    LAT: {dl['decoded']}")
            print()


# ══════════════════════════════════════════
# STEP 6: COHERENCE ANALYSIS
# ══════════════════════════════════════════
def coherence_analysis(decoded_lines):
    print()
    print("=" * 70)
    print("STEP 5: COHERENCE ANALYSIS — Do decoded lines make sense?")
    print("=" * 70)

    # Count recipe-like patterns
    patterns = Counter()
    for dl in decoded_lines:
        text = dl["decoded"]
        if "Rx" in text:
            patterns["Rx (recipe/take)"] += 1
        if "cum" in text:
            patterns["cum (with)"] += 1
        if " in " in text:
            patterns["in (in/into)"] += 1
        if " et " in text:
            patterns["et (and)"] += 1
        if "[MATERIA]" in text:
            patterns["[MATERIA] marker"] += 1
        if "[PRODUCT]" in text:
            patterns["[PRODUCT] marker"] += 1
        if " ex " in text:
            patterns["ex (from)"] += 1
        if " per " in text:
            patterns["per (through)"] += 1
        if " re " in text:
            patterns["re (again)"] += 1
        if " de " in text:
            patterns["de (about)"] += 1

    print(f"\n  Recipe-like patterns across {len(decoded_lines)} lines:")
    for pattern, count in patterns.most_common():
        print(f"    {pattern:30s}: {count:5d} ({100*count/len(decoded_lines):.1f}% of lines)")

    # Look for consecutive recipe structure:
    # Recipe → ingredient → preparation → product
    print(f"\n  RECIPE SEQUENCE DETECTION:")
    print(f"  Looking for: Rx/cum/in + noun + et + noun patterns")

    recipe_sequences = 0
    for dl in decoded_lines:
        words = dl["decoded"].split()
        for i in range(len(words) - 2):
            # Pattern: preposition + noun + et
            if words[i] in ("cum", "in", "ex") and "et" in words[i+1:min(i+4, len(words))]:
                recipe_sequences += 1
                break

    print(f"    Lines with prep+noun+et patterns: {recipe_sequences}/{len(decoded_lines)}")

    # Vocabulary analysis: what are the most common decoded words?
    vocab = Counter()
    for dl in decoded_lines:
        for w in dl["decoded"].split():
            if not w.startswith("_") and not w.startswith("[") and len(w) >= 2:
                vocab[w] += 1

    print(f"\n  TOP 30 DECODED VOCABULARY:")
    perseus = load_perseus()
    print(f"    {'Word':20s} {'Count':>6s} {'Perseus':>8s}")
    for word, count in vocab.most_common(30):
        p = "YES" if word in perseus else ""
        print(f"    {word:20s} {count:6d} {p:>8s}")

    return {"patterns": dict(patterns), "recipe_sequences": recipe_sequences}


# ══════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════
if __name__ == "__main__":
    print("V23 FORCE DECODE — Complete Phrase Reconstruction")
    print("=" * 70)
    print()

    # Step 1: Build expanded root map
    root_map, confidence = build_expanded_root_map()

    # Step 2: Parse and decode
    lines = parse_lines_eva()
    print(f"\nLoaded {len(lines)} lines from {len(set(l['folio'] for l in lines))} folios")

    decoded_lines, stats = force_decode(lines, root_map, confidence)

    # Step 3: Recipe pattern detection
    recipes = detect_recipe_patterns(decoded_lines)

    # Step 4: Focus on f103r
    focus_f103r(decoded_lines)

    # Step 5: Coherence analysis
    coherence = coherence_analysis(decoded_lines)

    # Save results
    total = sum(stats.values())
    known = total - stats.get("unknown", 0)

    results = {
        "total_tokens": total,
        "known_tokens": known,
        "known_pct": round(100 * known / total, 1),
        "stats": dict(stats),
        "coherence": coherence,
        "root_map_size": len(root_map),
        "speculative_count": sum(1 for v in confidence.values() if v == "speculative"),
        "best_pharma_lines": [
            {"folio": r["folio"], "eva": r["eva"][:200], "decoded": r["decoded"][:200],
             "known_pct": r["known_pct"]}
            for r in recipes[:50] if r["section"] in ("S", "P")
        ],
    }

    with open(RESULTS / "v23_force_decode.json", 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print()
    print("=" * 70)
    print("V23 SUMMARY")
    print("=" * 70)
    print(f"  Root map: {len(root_map)} entries ({sum(1 for v in confidence.values() if v == 'speculative')} speculative)")
    print(f"  Decoded: {known}/{total} tokens ({100*known/total:.1f}%)")
    print(f"  Results saved to {RESULTS / 'v23_force_decode.json'}")
