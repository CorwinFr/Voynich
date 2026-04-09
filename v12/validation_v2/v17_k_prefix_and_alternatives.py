#!/usr/bin/env python3
"""
V17 — Two critical investigations:
1. Resolve the k-prefix Latin value
2. Exploit 624 alternative readings [a:b] from ZL.txt
"""
import json, sys, re
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

BASE = Path("d:/Github/Voynich")
ZL_PATH = BASE / "data/transcriptions/ZL.txt"
DECODED_FILE = BASE / "v12/output/VOYNICH_DECODE_V12_INGREDIENTS.txt"
RESULTS = BASE / "v12/validation_v2/results"
LOGOGRAMS_PATH = BASE / "v12/rules/logograms.json"
PERSEUS_PATH = BASE / "data/latin_valid_wordset.json"


def load_perseus():
    with open(PERSEUS_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return set(w.lower() for w in (data if isinstance(data, list) else data.keys()))


def load_logograms():
    with open(LOGOGRAMS_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    result = {}
    for eva, info in data.items():
        if isinstance(info, dict):
            latin = info.get("latin", "")
            if latin:
                result[eva.lower()] = latin.lower()
        elif isinstance(info, str):
            result[eva.lower()] = info.lower()
    return result


# ══════════════════════════════════════════
# PART 1: RESOLVE k-PREFIX
# ══════════════════════════════════════════
def resolve_k_prefix():
    print("=" * 60)
    print("PART 1: RESOLVE k-PREFIX")
    print("=" * 60)

    logograms = load_logograms()
    perseus = load_perseus()

    # Parse EVA tokens
    all_tokens = []
    with open(DECODED_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            if 'EVA' in line and ':' in line:
                parts = line.split(':')
                if 'EVA' in parts[0]:
                    for w in parts[1].strip().split():
                        if w.isalpha() and len(w) >= 2:
                            all_tokens.append(w.lower())

    # Collect all k-initial tokens (excluding logogram qoky=coque etc.)
    k_tokens = Counter()
    for t in all_tokens:
        if t.startswith('k') and t not in logograms:
            k_tokens[t] += 1

    # For each k-token, the root after k
    k_roots = Counter()
    for t, c in k_tokens.items():
        root = t[1:]
        k_roots[root] += c

    print(f"  k-initial tokens (non-logogram): {sum(k_tokens.values())}")
    print(f"  Unique k-roots: {len(k_roots)}")

    # KEY TEST: for each k+root, does the root also appear with OTHER prefixes?
    # And what Latin value does the root have?
    known_roots = {
        "ar": "iure", "aiin": "aquam", "ain": "?", "edy": "?",
        "eey": "?", "eedy": "?", "al": "?", "ol": "es",
        "y": "in", "or": "hiera",
    }

    print(f"\n  k+root decomposition:")
    for root, count in k_roots.most_common(20):
        known = logograms.get(root, known_roots.get(root, "?"))
        # Does root appear standalone?
        standalone = sum(1 for t in all_tokens if t == root)
        # Does root appear with other prefixes?
        d_count = sum(1 for t in all_tokens if t == 'd' + root)
        qo_count = sum(1 for t in all_tokens if t == 'qo' + root)
        ch_count = sum(1 for t in all_tokens if t == 'ch' + root)

        print(f"    k+{root:10s} x{count:4d}  root={known:8s}  "
              f"standalone={standalone:3d}  d+={d_count:3d}  qo+={qo_count:3d}  ch+={ch_count:3d}")

    # TEST HYPOTHESES for k-prefix:
    # H1: k = empty (silent, just a determinant)
    # H2: k = t (from V15 brute force)
    # H3: k = c (from K&A)
    # H4: k = h (from Bombe Phase 0)
    # H5: k = qu (from K&A alternative)

    # For each hypothesis, what Latin words do we get?
    print(f"\n  HYPOTHESIS TESTING for k-prefix value:")
    hypotheses = {
        "k=∅ (silent)": "",
        "k=t": "t",
        "k=c": "c",
        "k=h": "h",
        "k=qu": "qu",
        "k=a": "a",
    }

    for hyp_name, k_val in hypotheses.items():
        # Take top 10 k+root, apply hypothesis, check Perseus
        hits = 0
        total = 0
        examples = []
        for root, count in k_roots.most_common(10):
            known_root_val = logograms.get(root)
            if known_root_val:
                latin_word = k_val + known_root_val
                total += 1
                if latin_word in perseus:
                    hits += 1
                    examples.append(f"k+{root} → {latin_word} ✓")
                else:
                    examples.append(f"k+{root} → {latin_word} ✗")

        pct = 100 * hits / max(total, 1)
        print(f"    {hyp_name:15s}: {hits}/{total} Perseus matches ({pct:.0f}%)")
        for ex in examples[:5]:
            print(f"      {ex}")

    # CONTEXTUAL TEST: what Latin word typically follows the same
    # words that precede k-tokens?
    k_context_prev = Counter()
    k_context_next = Counter()
    for i, t in enumerate(all_tokens):
        if t.startswith('k') and t not in logograms:
            if i > 0:
                prev = all_tokens[i-1]
                if prev in logograms:
                    k_context_prev[logograms[prev]] += 1
            if i < len(all_tokens) - 1:
                nxt = all_tokens[i+1]
                if nxt in logograms:
                    k_context_next[logograms[nxt]] += 1

    print(f"\n  Context around k-tokens:")
    print(f"    Before: {', '.join(f'{w}({c})' for w, c in k_context_prev.most_common(8))}")
    print(f"    After:  {', '.join(f'{w}({c})' for w, c in k_context_next.most_common(8))}")

    results = {
        "total_k_tokens": sum(k_tokens.values()),
        "unique_k_roots": len(k_roots),
        "top_k_roots": k_roots.most_common(20),
        "k_context_prev": k_context_prev.most_common(10),
        "k_context_next": k_context_next.most_common(10),
    }

    with open(RESULTS / "v17_k_prefix.json", 'w') as f:
        json.dump(results, f, indent=2)
    return results


# ══════════════════════════════════════════
# PART 2: EXPLOIT ALTERNATIVE READINGS
# ══════════════════════════════════════════
def exploit_alternatives():
    print()
    print("=" * 60)
    print("PART 2: ALTERNATIVE READINGS IN ZL.txt")
    print("=" * 60)

    # Parse ZL.txt for all annotations
    alternatives = []  # list of (folio, line, primary, alternative, context)
    doubts = []  # list of (folio, line, char)
    weirdos = []

    current_folio = ""
    with open(ZL_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            # Folio marker
            m = re.match(r'<(f\w+)>', line)
            if m:
                current_folio = m.group(1)

            # Alternative readings [a:b]
            for m in re.finditer(r'\[(\w+):(\w+)\]', line):
                primary = m.group(1)
                alt = m.group(2)
                alternatives.append({
                    "folio": current_folio,
                    "primary": primary,
                    "alternative": alt,
                    "context": line.strip()[:80],
                })

            # Doubt markers
            for m in re.finditer(r'(\w)\?', line):
                doubts.append({"folio": current_folio, "char": m.group(1)})

            # Weirdos
            for m in re.finditer(r'@(\d+)', line):
                weirdos.append({"folio": current_folio, "code": m.group(1)})

    # Analyze alternatives
    pair_freq = Counter()
    for alt in alternatives:
        pair = f"{alt['primary']}→{alt['alternative']}"
        pair_freq[pair] += 1

    print(f"  Total alternative readings: {len(alternatives)}")
    print(f"  Total doubt markers (?): {len(doubts)}")
    print(f"  Total weirdos (@NNN): {len(weirdos)}")

    print(f"\n  Top 20 glyph confusion pairs:")
    for pair, count in pair_freq.most_common(20):
        primary, alt = pair.split('→')
        print(f"    {primary:5s} ↔ {alt:5s}  x{count:3d}")

    # KEY ANALYSIS: bidirectional confusions
    bidir = defaultdict(int)
    for pair, count in pair_freq.items():
        a, b = pair.split('→')
        key = tuple(sorted([a, b]))
        bidir[key] += count

    print(f"\n  Bidirectional confusion pairs (total both directions):")
    for (a, b), count in sorted(bidir.items(), key=lambda x: -x[1])[:15]:
        print(f"    {a:5s} ↔ {b:5s}  x{count:3d}")

    # IMPACT ANALYSIS: for the most confused pairs, what % of tokens are affected?
    total_tokens = sum(1 for _ in open(ZL_PATH, 'r', encoding='utf-8')
                       if not _.startswith('#') and not _.startswith('<'))

    print(f"\n  IMPACT: if we swap all alternatives, what changes?")
    print(f"  o↔a ({bidir.get(('a','o'), 0)}x): affects our most common vowels")
    print(f"  r↔s ({bidir.get(('r','s'), 0)}x): r=recipe/re prefix, s=est/us suffix")
    print(f"  o↔y ({bidir.get(('o','y'), 0)}x): o=vowel vs y=in prefix")
    print(f"  t↔k ({bidir.get(('k','t'), 0)}x): DIRECTLY impacts our k-prefix question!")
    print(f"  ch↔ee ({bidir.get(('ch','ee'), 0)}x): ch=eius prefix vs ee=vowel")

    # Folios with most alternatives
    folio_alt_count = Counter(a["folio"] for a in alternatives)
    print(f"\n  Folios with most alternative readings:")
    for folio, count in folio_alt_count.most_common(10):
        print(f"    {folio:10s}: {count} alternatives")

    # Folios with most doubt markers
    folio_doubt_count = Counter(d["folio"] for d in doubts)
    print(f"\n  Folios with most doubt markers:")
    for folio, count in folio_doubt_count.most_common(10):
        print(f"    {folio:10s}: {count} doubts")

    results = {
        "total_alternatives": len(alternatives),
        "total_doubts": len(doubts),
        "total_weirdos": len(weirdos),
        "pair_freq": pair_freq.most_common(30),
        "bidirectional": [(list(k), v) for k, v in sorted(bidir.items(), key=lambda x: -x[1])[:20]],
        "folios_most_alternatives": folio_alt_count.most_common(15),
        "folios_most_doubts": folio_doubt_count.most_common(15),
    }

    with open(RESULTS / "v17_alternatives.json", 'w') as f:
        json.dump(results, f, indent=2)
    return results


# ══════════════════════════════════════════
# PART 3: TIRONIAN NOTES CROSS-REFERENCE
# ══════════════════════════════════════════
def tironian_crossref():
    print()
    print("=" * 60)
    print("PART 3: TIRONIAN NOTES CROSS-REFERENCE")
    print("=" * 60)

    tironian_path = BASE / "data/tironian/schmitz_index_full.json"
    if not tironian_path.exists():
        print("  Schmitz index not found, skipping")
        return {}

    with open(tironian_path, 'r', encoding='utf-8') as f:
        schmitz = json.load(f)

    print(f"  Schmitz entries: {len(schmitz)}")

    # What format is it?
    if isinstance(schmitz, list):
        sample = schmitz[:5]
    elif isinstance(schmitz, dict):
        sample = list(schmitz.items())[:5]
    else:
        sample = str(schmitz)[:500]
    print(f"  Sample: {sample}")

    # Search for pharmaceutical terms in Tironian Notes
    PHARMA_TERMS = ["aqua", "coque", "recipe", "misce", "aloe", "oleum",
                    "hiera", "sal", "mel", "cera", "tere", "cola"]

    found = {}
    if isinstance(schmitz, dict):
        for term in PHARMA_TERMS:
            matches = [(k, v) for k, v in schmitz.items()
                       if term in str(v).lower() or term in str(k).lower()]
            if matches:
                found[term] = matches[:5]
                print(f"  '{term}' found in {len(matches)} Tironian entries")
    elif isinstance(schmitz, list):
        for term in PHARMA_TERMS:
            matches = [entry for entry in schmitz
                       if term in str(entry).lower()]
            if matches:
                found[term] = [str(m)[:100] for m in matches[:5]]
                print(f"  '{term}' found in {len(matches)} Tironian entries")

    results = {
        "total_entries": len(schmitz) if isinstance(schmitz, (list, dict)) else 0,
        "pharma_matches": {k: len(v) for k, v in found.items()},
        "sample_matches": {k: [str(x)[:100] for x in v[:3]] for k, v in found.items()},
    }

    with open(RESULTS / "v17_tironian.json", 'w') as f:
        json.dump(results, f, indent=2)
    return results


# ══════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════
if __name__ == "__main__":
    print("V17 k-PREFIX + ALTERNATIVE READINGS + TIRONIAN")
    print("=" * 60)

    r1 = resolve_k_prefix()
    r2 = exploit_alternatives()
    r3 = tironian_crossref()

    print()
    print("=" * 60)
    print("V17 SYNTHESIS")
    print("=" * 60)
    print(f"  k-prefix tokens: {r1['total_k_tokens']}")
    print(f"  Alternative readings: {r2['total_alternatives']}")
    print(f"  Doubt markers: {r2['total_doubts']}")
    print(f"  Tironian matches: {r3.get('pharma_matches', {})}")
