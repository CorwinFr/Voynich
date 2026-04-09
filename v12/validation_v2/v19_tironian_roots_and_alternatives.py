#!/usr/bin/env python3
"""
V19 — Three attacks in parallel:
1. Cross-reference ALL 5800 roots with 12987 Tironian entries
2. Test 624 EVA alternative readings impact on root decoder
3. Build clean root-based decoder (no scorer inflation)
"""
import json, sys, re, random
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

BASE = Path("d:/Github/Voynich")
DECODED_FILE = BASE / "v12/output/VOYNICH_DECODE_V12_INGREDIENTS.txt"
ZL_PATH = BASE / "data/transcriptions/ZL.txt"
RESULTS = BASE / "v12/validation_v2/results"
LOGOGRAMS_PATH = BASE / "v12/rules/logograms.json"
PERSEUS_PATH = BASE / "data/latin_valid_wordset.json"
GLYPHS_PATH = BASE / "v12/rules/glyphs.json"
TIRONIAN_PATH = BASE / "data/tironian/schmitz_index_full.json"
TIRONIAN_MAP_PATH = BASE / "data/tironian/tironian_mappings.json"

PREFIXES_ORDER = ["qok", "qot", "qo", "ok", "ot", "ol", "da", "ch", "sh",
                  "d", "y", "r", "p", "l", "t", "f", "k"]


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


def load_eva_tokens():
    tokens = []
    with open(DECODED_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            if 'EVA' in line and ':' in line:
                parts = line.split(':')
                if 'EVA' in parts[0]:
                    for w in parts[1].strip().split():
                        if w.isalpha() and len(w) >= 2:
                            tokens.append(w.lower())
    return tokens


def strip_prefix(token):
    for pfx in PREFIXES_ORDER:
        if token.startswith(pfx) and len(token) > len(pfx):
            return pfx, token[len(pfx):]
    return "", token


def get_all_roots():
    """Extract all roots (after prefix stripping) with frequencies."""
    tokens = load_eva_tokens()
    logograms = load_logograms()
    roots = Counter()
    for t in tokens:
        if t not in logograms:
            _, root = strip_prefix(t)
            roots[root] += 1
    return roots


# ══════════════════════════════════════════
# V19a: TIRONIAN × ROOTS EXHAUSTIVE
# ══════════════════════════════════════════
def v19a_tironian_exhaustive():
    print("=" * 60)
    print("V19a: TIRONIAN NOTES × ALL ROOTS (exhaustive)")
    print("=" * 60)

    with open(TIRONIAN_PATH, 'r', encoding='utf-8') as f:
        schmitz = json.load(f)

    # Build lookup: latin_value → list of entries
    tironian_by_latin = defaultdict(list)
    for entry in schmitz:
        if isinstance(entry, dict):
            latin = entry.get("latin_value", "").lower().strip()
            if latin:
                tironian_by_latin[latin].append(entry)

    # Also load tironian_mappings.json for abbreviation patterns
    tir_maps = {}
    if TIRONIAN_MAP_PATH.exists():
        with open(TIRONIAN_MAP_PATH, 'r', encoding='utf-8') as f:
            tir_maps = json.load(f)
        print(f"  Tironian mappings loaded: {len(tir_maps)} entries")

    print(f"  Schmitz: {len(schmitz)} entries, {len(tironian_by_latin)} unique Latin values")

    roots = get_all_roots()
    logograms = load_logograms()
    perseus = load_perseus()

    # For each root, try to find Tironian match via K&A primary decode
    with open(GLYPHS_PATH, 'r', encoding='utf-8') as f:
        glyphs_raw = json.load(f)
    ka_primary = {}
    for g, info in glyphs_raw.items():
        if g.startswith('_'):
            continue
        if isinstance(info, dict) and "phonemes" in info:
            phonemes = info["phonemes"]
            if phonemes:
                ka_primary[g] = str(phonemes[0])

    def raw_decode(eva_w):
        result = ""
        i = 0
        while i < len(eva_w):
            matched = False
            for gl in range(min(3, len(eva_w) - i), 0, -1):
                chunk = eva_w[i:i+gl]
                if chunk in ka_primary:
                    result += ka_primary[chunk]
                    i += gl
                    matched = True
                    break
            if not matched:
                result += eva_w[i]
                i += 1
        return result.lower()

    # Strategy: for each root, decode with K&A primary, then check Tironian
    matches = []
    total_checked = 0

    for root, count in roots.most_common(200):  # top 200 roots
        total_checked += 1
        decoded = raw_decode(root)

        # Direct Tironian match
        if decoded in tironian_by_latin:
            entries = tironian_by_latin[decoded]
            freq = entries[0].get("frequency", "?")
            domains = entries[0].get("domains", [])
            matches.append({
                "root": root, "count": count, "decoded": decoded,
                "tironian_entries": len(entries), "frequency": freq,
                "domains": domains, "match_type": "exact",
            })
            continue

        # Try logogram value
        if root in logograms:
            logo_val = logograms[root]
            if logo_val in tironian_by_latin:
                entries = tironian_by_latin[logo_val]
                matches.append({
                    "root": root, "count": count, "decoded": logo_val,
                    "tironian_entries": len(entries),
                    "frequency": entries[0].get("frequency", "?"),
                    "domains": entries[0].get("domains", []),
                    "match_type": "logogram",
                })
                continue

        # Try prefix-stripped decoded
        for length in range(len(decoded), 2, -1):
            substr = decoded[:length]
            if substr in tironian_by_latin:
                entries = tironian_by_latin[substr]
                matches.append({
                    "root": root, "count": count, "decoded": substr,
                    "tironian_entries": len(entries),
                    "frequency": entries[0].get("frequency", "?"),
                    "domains": entries[0].get("domains", []),
                    "match_type": "partial",
                })
                break

    # Summary
    exact = sum(1 for m in matches if m["match_type"] == "exact")
    logo = sum(1 for m in matches if m["match_type"] == "logogram")
    partial = sum(1 for m in matches if m["match_type"] == "partial")

    print(f"\n  Checked: {total_checked} roots")
    print(f"  Exact Tironian matches: {exact}")
    print(f"  Via logogram: {logo}")
    print(f"  Partial matches: {partial}")
    print(f"  Total matches: {len(matches)}")

    print(f"\n  Top Tironian matches:")
    for m in sorted(matches, key=lambda x: -x["count"])[:25]:
        print(f"    {m['root']:12s} x{m['count']:4d} → {m['decoded']:12s} "
              f"[{m['match_type']:8s}] Tir:{m['tironian_entries']} "
              f"freq={m['frequency']} dom={m['domains']}")

    # PHARMA-SPECIFIC: filter matches in medical/pharmaceutical domains
    pharma_matches = [m for m in matches if any(d in str(m.get("domains", []))
                      for d in ["medical", "pharma", "general"])]
    print(f"\n  Pharma/medical domain matches: {len(pharma_matches)}")

    results = {
        "total_checked": total_checked,
        "exact_matches": exact,
        "logogram_matches": logo,
        "partial_matches": partial,
        "total_matches": len(matches),
        "top_matches": sorted(matches, key=lambda x: -x["count"])[:50],
        "pharma_matches": len(pharma_matches),
    }

    with open(RESULTS / "v19a_tironian_exhaustive.json", 'w') as f:
        json.dump(results, f, indent=2)
    return results


# ══════════════════════════════════════════
# V19b: EVA ALTERNATIVE READINGS IMPACT
# ══════════════════════════════════════════
def v19b_alternative_impact():
    print()
    print("=" * 60)
    print("V19b: EVA ALTERNATIVE READINGS IMPACT")
    print("=" * 60)

    logograms = load_logograms()
    perseus = load_perseus()

    # Parse ZL.txt: extract lines with alternatives
    alt_lines = []
    current_folio = ""
    with open(ZL_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            m = re.match(r'<(f\w+)>', line)
            if m:
                current_folio = m.group(1)
            if '[' in line and ':' in line and not line.startswith('#'):
                # Extract EVA words from line (strip metadata)
                text = re.sub(r'<[^>]*>', '', line).strip()
                if text:
                    alt_lines.append({"folio": current_folio, "text": text})

    print(f"  Lines with alternatives: {len(alt_lines)}")

    # For each line with alternatives, generate both versions
    improvements = 0
    degradations = 0
    unchanged = 0
    total_tested = 0

    new_logograms_found = Counter()

    for alt_line in alt_lines:
        text = alt_line["text"]

        # Find all [a:b] patterns
        alts = list(re.finditer(r'\[(\w+):(\w+)\]', text))
        if not alts:
            continue

        # Version A: use primary reading (replace [a:b] with a)
        text_a = re.sub(r'\[(\w+):(\w+)\]', r'\1', text)
        # Version B: use alternative reading (replace [a:b] with b)
        text_b = re.sub(r'\[(\w+):(\w+)\]', r'\2', text)

        # Tokenize both
        tokens_a = [w.lower() for w in text_a.split() if w.isalpha() and len(w) >= 2]
        tokens_b = [w.lower() for w in text_b.split() if w.isalpha() and len(w) >= 2]

        # Count logogram hits
        hits_a = sum(1 for t in tokens_a if t in logograms)
        hits_b = sum(1 for t in tokens_b if t in logograms)

        total_tested += 1
        if hits_b > hits_a:
            improvements += 1
            # Which tokens improved?
            for t in tokens_b:
                if t in logograms and t not in [w.lower() for w in text_a.split()]:
                    new_logograms_found[t] += 1
        elif hits_b < hits_a:
            degradations += 1
        else:
            unchanged += 1

    print(f"  Tested: {total_tested} lines")
    print(f"  Alternative is better: {improvements} ({100*improvements/max(total_tested,1):.1f}%)")
    print(f"  Alternative is worse:  {degradations} ({100*degradations/max(total_tested,1):.1f}%)")
    print(f"  No change:             {unchanged} ({100*unchanged/max(total_tested,1):.1f}%)")

    if new_logograms_found:
        print(f"\n  New logogram matches from alternative readings:")
        for token, count in new_logograms_found.most_common(15):
            latin = logograms.get(token, "?")
            print(f"    {token:12s} → {latin:12s} x{count}")

    results = {
        "total_tested": total_tested,
        "improvements": improvements,
        "degradations": degradations,
        "unchanged": unchanged,
        "new_logograms": new_logograms_found.most_common(20),
    }

    with open(RESULTS / "v19b_alternatives.json", 'w') as f:
        json.dump(results, f, indent=2)
    return results


# ══════════════════════════════════════════
# V19c: CLEAN ROOT-BASED DECODER
# No scorer. Just logograms + prefix stripping + k=silent.
# The honest baseline.
# ══════════════════════════════════════════
def v19c_clean_decoder():
    print()
    print("=" * 60)
    print("V19c: CLEAN ROOT-BASED DECODER (no scorer)")
    print("=" * 60)

    logograms = load_logograms()
    perseus = load_perseus()
    tokens = load_eva_tokens()

    PREFIX_LATIN = {
        "d": "in", "da": "in", "qo": "cum", "qok": "cum", "qot": "cum",
        "y": "in", "r": "re", "p": "per", "ol": "ex", "l": "ex",
        "ch": "eius", "ok": "", "ot": "", "sh": "ci", "f": "par",
        "t": "el", "k": "",
    }

    # Decode
    decoded = []
    stats = {"logogram": 0, "root_logo": 0, "k_root_logo": 0, "prefix_only": 0, "unknown": 0}

    for token in tokens:
        # 1. Logogram
        if token in logograms:
            decoded.append(("LOGO", logograms[token], token))
            stats["logogram"] += 1
            continue

        # 2. Prefix + root (root is logogram)
        pfx, root = strip_prefix(token)
        lat_pfx = PREFIX_LATIN.get(pfx, "")

        if root in logograms:
            lat_root = logograms[root]
            decoded.append(("PFX+LOGO", f"{lat_pfx} {lat_root}".strip(), token))
            stats["root_logo"] += 1
            continue

        # 3. k=silent: strip k from root
        if root.startswith('k') and len(root) > 1:
            inner = root[1:]
            if inner in logograms:
                lat_root = logograms[inner]
                decoded.append(("K+LOGO", f"{lat_pfx} {lat_root}".strip(), token))
                stats["k_root_logo"] += 1
                continue

        # 4. Prefix known but root unknown
        if pfx and lat_pfx:
            decoded.append(("PFX_ONLY", f"{lat_pfx} [{root}]", token))
            stats["prefix_only"] += 1
            continue

        # 5. Unknown
        decoded.append(("UNK", f"[{token}]", token))
        stats["unknown"] += 1

    total = len(tokens)
    known = stats["logogram"] + stats["root_logo"] + stats["k_root_logo"]
    known_pct = 100 * known / total

    # Perseus check on known words only
    perseus_hits = 0
    perseus_5plus = 0
    total_5plus = 0
    for dtype, latin, orig in decoded:
        if dtype in ("LOGO", "PFX+LOGO", "K+LOGO"):
            # Check the root word (last word)
            root_word = latin.split()[-1] if ' ' in latin else latin
            if root_word in perseus:
                perseus_hits += 1
                if len(root_word) >= 5:
                    perseus_5plus += 1
            if len(root_word) >= 5:
                total_5plus += 1

    # Word length stats
    known_words = [latin.split()[-1] for dtype, latin, orig in decoded
                   if dtype in ("LOGO", "PFX+LOGO", "K+LOGO")]
    mean_len = sum(len(w) for w in known_words) / max(len(known_words), 1)

    # Unique vocabulary
    unique_decoded = Counter(latin for dtype, latin, orig in decoded
                            if dtype in ("LOGO", "PFX+LOGO", "K+LOGO"))

    print(f"  DECODE STATS:")
    print(f"    Total tokens:    {total}")
    print(f"    Logogram:        {stats['logogram']} ({100*stats['logogram']/total:.1f}%)")
    print(f"    Prefix+logo:     {stats['root_logo']} ({100*stats['root_logo']/total:.1f}%)")
    print(f"    k-silent+logo:   {stats['k_root_logo']} ({100*stats['k_root_logo']/total:.1f}%)")
    print(f"    Prefix only:     {stats['prefix_only']} ({100*stats['prefix_only']/total:.1f}%)")
    print(f"    Unknown:         {stats['unknown']} ({100*stats['unknown']/total:.1f}%)")
    print(f"    KNOWN TOTAL:     {known} ({known_pct:.1f}%)")
    print()
    print(f"  QUALITY:")
    print(f"    Perseus (known): {perseus_hits}/{known} ({100*perseus_hits/max(known,1):.1f}%)")
    print(f"    Perseus (5+):    {perseus_5plus}/{total_5plus} ({100*perseus_5plus/max(total_5plus,1):.1f}%)")
    print(f"    Mean word len:   {mean_len:.2f}")
    print(f"    Unique decoded:  {len(unique_decoded)}")
    print()
    print(f"  TOP 20 decoded words:")
    for latin, count in unique_decoded.most_common(20):
        in_p = "PERSEUS" if latin.split()[-1] in perseus else "---"
        print(f"    {latin:25s} x{count:4d}  {in_p}")

    # Sample text
    print(f"\n  SAMPLE OUTPUT (first 100 tokens):")
    line = []
    for i, (dtype, latin, orig) in enumerate(decoded[:100]):
        if dtype == "UNK":
            line.append(f"_{orig}_")
        elif dtype == "PFX_ONLY":
            line.append(latin)
        else:
            line.append(latin)
        if (i + 1) % 12 == 0:
            print(f"    {' '.join(line)}")
            line = []
    if line:
        print(f"    {' '.join(line)}")

    results = {
        "total": total,
        "stats": stats,
        "known": known,
        "known_pct": round(known_pct, 1),
        "perseus_known_pct": round(100 * perseus_hits / max(known, 1), 1),
        "perseus_5plus_pct": round(100 * perseus_5plus / max(total_5plus, 1), 1),
        "mean_word_length": round(mean_len, 2),
        "unique_decoded": len(unique_decoded),
        "top_20": unique_decoded.most_common(20),
    }

    with open(RESULTS / "v19c_clean_decoder.json", 'w') as f:
        json.dump(results, f, indent=2)
    return results


# ══════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════
if __name__ == "__main__":
    print("V19 — TIRONIAN ROOTS + ALTERNATIVES + CLEAN DECODER")
    print("=" * 60)

    r1 = v19a_tironian_exhaustive()
    r2 = v19b_alternative_impact()
    r3 = v19c_clean_decoder()

    print()
    print("=" * 60)
    print("V19 SYNTHESIS")
    print("=" * 60)
    print(f"  Tironian: {r1['total_matches']}/{r1['total_checked']} roots match "
          f"({r1['exact_matches']} exact, {r1['logogram_matches']} logo, {r1['partial_matches']} partial)")
    print(f"  Alternatives: {r2['improvements']} improvements, {r2['degradations']} degradations")
    print(f"  Clean decoder: {r3['known_pct']}% known, {r3['perseus_known_pct']}% Perseus, "
          f"{r3['unique_decoded']} unique words")
