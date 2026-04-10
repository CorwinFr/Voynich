#!/usr/bin/env python3
"""
V24 — Top-Down Recipe Constraint Decoder

V23 showed that bottom-up decomposition produces noise. V24 takes the
opposite approach: use the STRUCTURE of medieval pharmaceutical recipes
to constrain what each unknown root can mean.

A medieval recipe follows a rigid structure:
  Rx [ingredient] [quantity], [ingredient] [quantity].
  [verb] cum [vehicle].
  [verb] in [container/duration].
  Fiat [final form].

Strategy:
1. Map every unknown root's POSITION relative to known recipe keywords
2. Determine its functional ROLE (ingredient, verb, vehicle, quantity, etc.)
3. Search Schmitz + pharmaceutical dictionaries for candidates matching that role
4. Build a constrained decoder that produces readable recipes
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
    entries = []
    for entry in data:
        val = entry.get("latin_value", "").lower()
        if val:
            entries.append(entry)
    return entries


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


def extract_root(token):
    working = token
    gallows = ""
    if len(working) > 1 and working[0] in "ptf":
        gallows = working[0]
        working = working[1:]
    pfx = ""
    root = working
    for p in PREFIXES_ORDER:
        if working.startswith(p) and len(working) > len(p):
            pfx = p
            root = working[len(p):]
            break
    if root.startswith('k') and len(root) > 1:
        root = root[1:]
    return gallows, pfx, root


def build_base_root_map():
    """V21-level root map (no speculative entries)."""
    logograms = load_logograms()
    tironian = load_tironian_matches()
    root_map = dict(logograms)
    for root, latin in tironian.items():
        if root not in root_map:
            root_map[root] = latin
    return root_map


# Known recipe structure keywords (from our confirmed mappings)
# These are the KNOWN decoded words we can use as anchors
RECIPE_ANCHORS = {
    # Prepositions (from prefix system)
    "d": "in", "da": "in", "qo": "cum", "y": "de", "r": "re",
    "ol": "ex", "l": "per",
    # Logograms
    "dy": "et", "or": "hiera", "ol": "es", "ar": "are",
    # Functional
    "sh": "[MATERIA]", "ch": "[PRODUCT]",
    "p": "Rx", "f": "Rx",
}

# Pharmaceutical role categories
ROLES = {
    "INGREDIENT": ["sal", "mel", "cera", "oleum", "aqua", "vinum", "nardus",
                    "cassia", "aloe", "mastic", "hiera", "acet", "cibo"],
    "VERB": ["recipe", "misce", "coque", "tere", "cola", "fiat", "adde",
             "solve", "distilla", "macera", "filtra", "seca"],
    "VEHICLE": ["aqua", "vinum", "oleum", "mel", "acetum", "lac", "succus"],
    "QUANTITY": ["uncia", "drachma", "scrupulum", "libra", "ana", "semis"],
    "QUALITY": ["calidus", "frigidus", "siccus", "humidus"],
    "FORM": ["unguentum", "electuarium", "emplastrum", "pilula", "potio",
             "syrupus", "pulvis", "decoctum", "infusum"],
}


# ══════════════════════════════════════════
# STEP 1: POSITIONAL PROFILING OF UNKNOWNS
# ══════════════════════════════════════════
def positional_profiling(lines, root_map):
    print("=" * 70)
    print("STEP 1: POSITIONAL PROFILING — What role does each unknown play?")
    print("=" * 70)

    # For each root, track:
    # - Position in line (start/middle/end)
    # - What comes BEFORE it (known keyword?)
    # - What comes AFTER it
    # - What PREFIX it carries
    # - What SECTION it appears in

    root_profiles = defaultdict(lambda: {
        "count": 0,
        "line_pos": Counter(),      # first, early, middle, late, last
        "prev_prefix": Counter(),    # what prefix does the PREVIOUS token have
        "prev_root": Counter(),      # what root precedes this
        "next_root": Counter(),      # what root follows this
        "own_prefix": Counter(),     # what prefix does THIS token carry
        "own_gallows": Counter(),    # gallows on this token
        "sections": Counter(),       # which sections
        "after_known": Counter(),    # which known Latin word precedes
    })

    for line in lines:
        words = line["words"]
        n = len(words)
        roots_in_line = []

        for i, w in enumerate(words):
            g, pfx, root = extract_root(w)
            known = root in root_map
            latin = root_map.get(root, None)
            roots_in_line.append((g, pfx, root, known, latin))

        for i, (g, pfx, root, known, latin) in enumerate(roots_in_line):
            if known:
                continue  # Only profile UNKNOWN roots

            prof = root_profiles[root]
            prof["count"] += 1

            # Line position
            if i == 0:
                prof["line_pos"]["first"] += 1
            elif i == n - 1:
                prof["line_pos"]["last"] += 1
            elif i < n / 3:
                prof["line_pos"]["early"] += 1
            elif i < 2 * n / 3:
                prof["line_pos"]["middle"] += 1
            else:
                prof["line_pos"]["late"] += 1

            # Own prefix and gallows
            if pfx:
                prof["own_prefix"][pfx] += 1
            if g:
                prof["own_gallows"][g] += 1

            # Previous token
            if i > 0:
                pg, ppfx, proot, pknown, platin = roots_in_line[i-1]
                if pknown and platin:
                    prof["after_known"][platin] += 1
                prof["prev_root"][proot] += 1

            # Next token
            if i + 1 < n:
                ng, npfx, nroot, nknown, nlatin = roots_in_line[i+1]
                prof["next_root"][nroot] += 1

            # Section
            prof["sections"][line["section"]] += 1

    return root_profiles


# ══════════════════════════════════════════
# STEP 2: ROLE ASSIGNMENT
# ══════════════════════════════════════════
def assign_roles(root_profiles):
    print()
    print("=" * 70)
    print("STEP 2: ROLE ASSIGNMENT — Functional classification")
    print("=" * 70)

    # Rules for role assignment:
    # INGREDIENT: appears after cum/in/ex, in ingredient lists, with sh/ch markers
    # VERB: appears line-initial, after gallows (Rx), before prepositions
    # SUFFIX/ENDING: always in final position of token (handled by V22)
    # QUANTITY: appears with degree markers
    # VEHICLE: appears specifically after "cum" (with X)

    role_assignments = {}

    top_unknowns = sorted(root_profiles.items(), key=lambda x: -x[1]["count"])[:30]

    print(f"\n  {'Root':>10s} {'Count':>6s} {'Role':>15s} {'Evidence':>50s}")
    print(f"  {'-'*83}")

    for root, prof in top_unknowns:
        evidence = []
        role = "UNKNOWN"

        total = prof["count"]
        after_known = prof["after_known"]

        # Check what known words precede this root
        after_cum = after_known.get("cum", 0) + after_known.get("coquam", 0)
        after_in = after_known.get("in", 0) + after_known.get("de", 0)
        after_et = after_known.get("et", 0)
        after_rx = after_known.get("recipe", 0) + after_known.get("Rx", 0)
        after_hiera = after_known.get("hiera", 0)
        after_cibo = after_known.get("cibo", 0) + after_known.get("cibus", 0)
        after_ciere = after_known.get("ciere", 0) + after_known.get("cies", 0)

        # Line position
        first_pct = 100 * prof["line_pos"]["first"] / total
        last_pct = 100 * prof["line_pos"]["last"] / total

        # Prefix distribution
        has_sh = prof["own_prefix"].get("sh", 0)
        has_ch = prof["own_prefix"].get("ch", 0)
        has_qo = sum(prof["own_prefix"].get(p, 0) for p in ["qo", "qok", "qot"])
        has_d = sum(prof["own_prefix"].get(p, 0) for p in ["d", "da"])
        has_y = prof["own_prefix"].get("y", 0)
        has_gallows = sum(prof["own_gallows"].values())

        # Section concentration
        s_count = prof["sections"].get("S", 0)
        h_count = prof["sections"].get("H", 0)
        p_count = prof["sections"].get("P", 0)
        pharma_pct = 100 * (s_count + p_count) / total
        herbal_pct = 100 * h_count / total

        # Role assignment logic
        if has_sh > total * 0.1 or has_ch > total * 0.1:
            role = "MATERIA/PRODUCT"
            evidence.append(f"sh={has_sh} ch={has_ch}")

        if after_cum > total * 0.05:
            if role == "UNKNOWN":
                role = "VEHICLE/INSTR"
            evidence.append(f"after_cum={after_cum}")

        if after_et > total * 0.05:
            if role == "UNKNOWN":
                role = "LIST_ITEM"
            evidence.append(f"after_et={after_et}")

        if first_pct > 25:
            if role == "UNKNOWN":
                role = "VERB/COMMAND"
            evidence.append(f"first={first_pct:.0f}%")

        if last_pct > 30:
            if role == "UNKNOWN":
                role = "TERMINATOR"
            evidence.append(f"last={last_pct:.0f}%")

        if has_gallows > total * 0.05:
            if role == "UNKNOWN":
                role = "VERB/COMMAND"
            evidence.append(f"gallows={has_gallows}")

        if has_qo > total * 0.3:
            evidence.append(f"qo={has_qo}")

        if pharma_pct > 50:
            evidence.append(f"pharma={pharma_pct:.0f}%")
        if herbal_pct > 40:
            evidence.append(f"herbal={herbal_pct:.0f}%")

        role_assignments[root] = {
            "role": role,
            "evidence": evidence,
            "count": total,
            "profile": {
                "first_pct": round(first_pct, 1),
                "last_pct": round(last_pct, 1),
                "after_cum": after_cum,
                "after_et": after_et,
                "after_in": after_in,
                "sh_prefix": has_sh,
                "ch_prefix": has_ch,
                "qo_prefix": has_qo,
                "pharma_pct": round(pharma_pct, 1),
                "herbal_pct": round(herbal_pct, 1),
            }
        }

        ev_str = '; '.join(evidence[:3]) if evidence else "no strong signal"
        print(f"  {root:>10s} {total:6d} {role:>15s} {ev_str:>50s}")

    return role_assignments


# ══════════════════════════════════════════
# STEP 3: SCHMITZ CANDIDATE SEARCH
# ══════════════════════════════════════════
def schmitz_candidate_search(role_assignments):
    print()
    print("=" * 70)
    print("STEP 3: SCHMITZ CANDIDATE SEARCH BY ROLE")
    print("=" * 70)

    schmitz_entries = load_schmitz()
    perseus = load_perseus()

    # Build domain-specific sublists from Schmitz
    pharma_words = set()
    verb_words = set()
    ingredient_words = set()
    all_schmitz = {}

    for entry in schmitz_entries:
        val = entry.get("latin_value", "").lower()
        domains = entry.get("domains", [])
        if not val:
            continue
        all_schmitz[val] = entry

        if "medical" in domains or "pharmaceutical" in domains:
            pharma_words.add(val)
        if entry.get("type") == "verb":
            verb_words.add(val)

    # Known pharmaceutical vocabulary from Antidotarium Nicolai and Circa Instans
    PHARMA_VOCAB = {
        "INGREDIENT": [
            "sal", "mel", "cera", "oleum", "aqua", "vinum", "acetum",
            "nardus", "cassia", "cinnamomum", "aloe", "mastix", "opium",
            "piper", "crocus", "gummi", "resina", "thus", "myrrha",
            "succus", "pulvis", "cortex", "radix", "folium", "semen",
            "flos", "herba", "fructus", "lignum", "lac", "butyrum",
            "ova", "sanguis", "fel", "stercus", "urina",
        ],
        "VERB": [
            "recipe", "misce", "coque", "tere", "cola", "fiat",
            "adde", "solve", "distilla", "macera", "filtra", "seca",
            "contere", "infunde", "exprime", "calefac", "refrigera",
            "desiccas", "commisce", "incorpora", "liquefac",
        ],
        "VEHICLE": [
            "aqua", "vinum", "oleum", "mel", "acetum", "lac",
            "succus", "serum", "decocto", "infuso",
        ],
        "FORM": [
            "unguentum", "electuarium", "emplastrum", "pilula",
            "potio", "syrupus", "pulvis", "decoctum", "infusum",
            "ceratum", "collyrium", "cataplasma", "linimentum",
        ],
        "QUANTITY": [
            "uncia", "drachma", "scrupulum", "libra", "ana",
            "semis", "manipulus", "pugillus", "cochleare",
        ],
    }

    print(f"\n  Schmitz pharma words: {len(pharma_words)}")
    print(f"  Schmitz verbs: {len(verb_words)}")

    # For each top unknown, search for candidates
    print(f"\n  CANDIDATE MAPPINGS:")
    print(f"  {'Root':>10s} {'Count':>6s} {'Role':>15s} {'Candidates (Perseus + Schmitz match)':>50s}")
    print(f"  {'-'*83}")

    candidates = {}
    for root, info in sorted(role_assignments.items(), key=lambda x: -x[1]["count"]):
        role = info["role"]
        count = info["count"]

        # Search strategy depends on role
        search_pool = []
        if role in ("MATERIA/PRODUCT", "LIST_ITEM"):
            search_pool = PHARMA_VOCAB["INGREDIENT"]
        elif role in ("VERB/COMMAND",):
            search_pool = PHARMA_VOCAB["VERB"]
        elif role in ("VEHICLE/INSTR",):
            search_pool = PHARMA_VOCAB["VEHICLE"] + PHARMA_VOCAB["INGREDIENT"]
        elif role == "TERMINATOR":
            # Look for Latin suffixes/endings
            search_pool = ["etur", "atur", "endi", "ando", "endo",
                          "ibus", "orum", "arum", "alis", "ilis",
                          "ione", "tione", "tura", "ura", "mentum"]
        else:
            search_pool = PHARMA_VOCAB["INGREDIENT"] + PHARMA_VOCAB["VERB"]

        # Also check Schmitz direct match
        matches = []
        if root in all_schmitz:
            val = all_schmitz[root]["latin_value"]
            matches.append(f"{val}(Schmitz)")

        # Check if root length matches any candidate (within EVA->Latin char ratio)
        # EVA typically has ~1.5x more chars than Latin equivalent
        root_len = len(root)
        for candidate in search_pool:
            if candidate in perseus:
                # Length heuristic: EVA root of length N maps to Latin of length N-1 to N+2
                if root_len - 1 <= len(candidate) <= root_len + 3:
                    matches.append(candidate)

        # Limit matches
        matches = matches[:5]
        candidates[root] = matches

        match_str = ', '.join(matches) if matches else "---"
        print(f"  {root:>10s} {count:6d} {role:>15s} {match_str:>50s}")

    return candidates


# ══════════════════════════════════════════
# STEP 4: DEEP ANALYSIS OF TOP 4 UNKNOWNS
# ══════════════════════════════════════════
def deep_analysis_top4(lines, root_map, root_profiles):
    print()
    print("=" * 70)
    print("STEP 4: DEEP ANALYSIS — edy, aiin, eey, al")
    print("=" * 70)

    for target_root in ["edy", "aiin", "eey", "al"]:
        print(f"\n  ══ {target_root.upper()} (root) ══")
        prof = root_profiles.get(target_root, {})
        if not prof:
            print(f"    Not found as unknown root")
            continue

        print(f"  Count: {prof['count']}")

        # Full context: show 10 example lines where this root appears
        print(f"\n  EXAMPLE LINES (EVA context):")
        shown = 0
        for line in lines:
            if shown >= 8:
                break
            for w in line["words"]:
                _, _, root = extract_root(w)
                if root == target_root:
                    # Show the full EVA line with the target highlighted
                    eva_line = ' '.join(line["words"])
                    # Also show what we DO know on this line
                    decoded_parts = []
                    for tw in line["words"]:
                        tg, tp, tr = extract_root(tw)
                        if tr in root_map:
                            decoded_parts.append(root_map[tr])
                        elif tp and tp in ("d", "da", "qo", "y", "r", "ol", "l"):
                            prefix_lat = {"d": "in", "da": "in", "qo": "cum",
                                         "y": "de", "r": "re", "ol": "ex", "l": "per"}
                            decoded_parts.append(f"{prefix_lat.get(tp, tp)}+[{tr}]")
                        else:
                            decoded_parts.append(f"_{tw}_")
                    decoded = ' '.join(decoded_parts)

                    print(f"    [{line['folio']}|{line['section']}] {eva_line[:90]}")
                    print(f"      → {decoded[:90]}")
                    shown += 1
                    break

        # Prefix distribution
        print(f"\n  PREFIX DISTRIBUTION:")
        for pfx, count in prof["own_prefix"].most_common(10):
            print(f"    {pfx:>6s}: {count:5d} ({100*count/prof['count']:.1f}%)")

        # After which known words?
        print(f"\n  APPEARS AFTER (known words):")
        for word, count in prof["after_known"].most_common(10):
            print(f"    {word:>15s}: {count:5d} ({100*count/prof['count']:.1f}%)")

        # Section distribution
        print(f"\n  SECTIONS:")
        for sec, count in prof["sections"].most_common():
            print(f"    {sec}: {count:5d} ({100*count/prof['count']:.1f}%)")

        # Key question: is this a SUFFIX or a WORD?
        # Check: how long are the tokens containing this root?
        root_token_lengths = Counter()
        standalone_count = 0
        prefixed_count = 0
        for line in lines:
            for w in line["words"]:
                _, pfx, root = extract_root(w)
                if root == target_root:
                    root_token_lengths[len(w)] += 1
                    if w == target_root:
                        standalone_count += 1
                    elif pfx:
                        prefixed_count += 1

        print(f"\n  TOKEN LENGTH DISTRIBUTION (containing {target_root}):")
        print(f"    Standalone: {standalone_count}")
        print(f"    Prefixed:   {prefixed_count}")
        for length, count in sorted(root_token_lengths.items()):
            bar = '#' * min(count // 10, 40)
            print(f"    len={length}: {count:5d} {bar}")


# ══════════════════════════════════════════
# STEP 5: BIGRAM CHAINS — Reconstructing recipe flow
# ══════════════════════════════════════════
def bigram_chains(lines, root_map):
    print()
    print("=" * 70)
    print("STEP 5: BIGRAM CHAINS — Recipe flow reconstruction")
    print("=" * 70)
    print()
    print("  Reading decoded bigrams to find recipe patterns...")

    # Build root-level bigrams (root_i, root_i+1)
    bigrams = Counter()
    for line in lines:
        roots = []
        for w in line["words"]:
            _, pfx, root = extract_root(w)
            latin = root_map.get(root, f"[{root}]")
            roots.append(latin)

        for i in range(len(roots) - 1):
            bigrams[(roots[i], roots[i+1])] += 1

    # Show top bigrams involving known recipe words
    print(f"\n  TOP BIGRAMS with recipe keywords:")
    recipe_bigrams = [(bi, count) for bi, count in bigrams.most_common(200)
                      if any(w in ("et", "cum", "in", "hiera", "ciere", "cibo",
                                   "recipe", "coque", "es", "ura", "iure")
                             for w in bi)]

    print(f"  {'Bigram':>35s} {'Count':>6s}")
    for (w1, w2), count in recipe_bigrams[:40]:
        print(f"  {w1:>15s} → {w2:>15s} {count:6d}")

    # Focus: what follows "et"?
    print(f"\n  WHAT FOLLOWS 'et'? (recipe continuation)")
    et_next = Counter()
    for (w1, w2), count in bigrams.items():
        if w1 == "et":
            et_next[w2] += count
    for w, c in et_next.most_common(15):
        print(f"    et → {w:>15s} {c:6d}")

    # What follows "cum"?
    print(f"\n  WHAT FOLLOWS 'cum'?")
    cum_next = Counter()
    for (w1, w2), count in bigrams.items():
        if w1 == "cum":
            cum_next[w2] += count
    for w, c in cum_next.most_common(15):
        print(f"    cum → {w:>15s} {c:6d}")

    # What follows "in"?
    print(f"\n  WHAT FOLLOWS 'in'?")
    in_next = Counter()
    for (w1, w2), count in bigrams.items():
        if w1 == "in":
            in_next[w2] += count
    for w, c in in_next.most_common(15):
        print(f"    in → {w:>15s} {c:6d}")

    # What PRECEDES "et"?
    print(f"\n  WHAT PRECEDES 'et'? (list items)")
    et_prev = Counter()
    for (w1, w2), count in bigrams.items():
        if w2 == "et":
            et_prev[w1] += count
    for w, c in et_prev.most_common(15):
        print(f"    {w:>15s} → et {c:6d}")


# ══════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════
if __name__ == "__main__":
    print("V24 TOP-DOWN RECIPE CONSTRAINT DECODER")
    print("=" * 70)
    print()

    root_map = build_base_root_map()
    lines = parse_lines_eva()
    print(f"Loaded {len(lines)} lines, {sum(len(l['words']) for l in lines)} tokens")
    print(f"Known roots: {len(root_map)}")
    print()

    # Step 1: Profile unknowns
    profiles = positional_profiling(lines, root_map)

    # Step 2: Assign roles
    roles = assign_roles(profiles)

    # Step 3: Schmitz candidates
    candidates = schmitz_candidate_search(roles)

    # Step 4: Deep analysis of top 4
    deep_analysis_top4(lines, root_map, profiles)

    # Step 5: Bigram chains
    bigram_chains(lines, root_map)

    # Save results
    results = {
        "role_assignments": {k: {
            "role": v["role"],
            "count": v["count"],
            "evidence": v["evidence"],
            "profile": v["profile"],
        } for k, v in roles.items()},
        "candidates": {k: v for k, v in candidates.items()},
    }
    with open(RESULTS / "v24_recipe_constraints.json", 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print()
    print("=" * 70)
    print("V24 SUMMARY")
    print("=" * 70)
    print(f"  Profiled {len(profiles)} unknown roots")
    print(f"  Role assignments: {Counter(v['role'] for v in roles.values())}")
    print(f"  Results saved to {RESULTS / 'v24_recipe_constraints.json'}")
