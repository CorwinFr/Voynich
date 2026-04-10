#!/usr/bin/env python3
"""
V27 — Substance Mapping: What are the ~10 core suffixes?

V26 established: TOKEN = gallows + prefix + sh/ch(state) + e-count(qty) + SUFFIX
The suffixes are substance names. Map them to pharmaceutical Latin.

Strategy:
1. For each suffix, build a FINGERPRINT: sectorial distribution, sh/ch ratio,
   co-occurrence with other suffixes, position in recipe flow
2. Compare fingerprints against expected profiles for known pharmaceutical substances
3. Cross-reference with Schmitz Tironian index
4. Decode complete recipe lines with the final mapping
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

PREFIXES_ORDER = ["qok", "qot", "qo", "ok", "ot", "ol", "da", "ch", "sh",
                  "d", "y", "r", "p", "l", "t", "f", "k"]
PREFIXES_ORDER.sort(key=len, reverse=True)


def parse_lines_eva():
    lines = []
    current_folio = sec = None
    with open(DECODED_FILE, 'r', encoding='utf-8') as f:
        for raw in f:
            m = re.match(r'\s*FOLIO (\S+) \| Section: (\S+)', raw)
            if m: current_folio, sec = m.group(1), m.group(2); continue
            if current_folio and 'EVA' in raw and ':' in raw:
                parts = raw.split(':')
                if 'EVA' in parts[0]:
                    words = [w.lower() for w in parts[1].strip().split() if w.isalpha() and len(w)>=2]
                    if words: lines.append({"folio": current_folio, "section": sec, "words": words})
    return lines


def decompose_token(token):
    """V26 decomposition: gallows + prefix + e-count + core suffix."""
    result = {"raw": token, "gallows": "", "prefix": "", "e_count": 0,
              "core": "", "unit_n": 0, "unit_type": ""}
    working = token

    if len(working) > 1 and working[0] in "ptf":
        result["gallows"] = working[0]; working = working[1:]

    for pfx in PREFIXES_ORDER:
        if working.startswith(pfx) and len(working) > len(pfx):
            result["prefix"] = pfx; working = working[len(pfx):]; break

    if working.startswith('k') and len(working) > 1:
        result["prefix"] += "+k" if result["prefix"] else "k"
        working = working[1:]

    # Unit pattern
    unit_match = re.match(r'^a?(i+)([nr])$', working)
    if unit_match:
        result["unit_n"] = len(unit_match.group(1))
        result["unit_type"] = unit_match.group(2)
        result["core"] = "UNIT"
        return result

    # E-count stripping
    e_count = 0
    valid_remainders = {"dy","ey","ol","or","al","ar","os","eo","y","o","s","l","r",
                        "ody","oey","ool","oor","ky","ko","ks",
                        "chy","cho","cthy","ckhey","ckhy","chey","chol","chor"}
    while working.startswith('e') and len(working) > 1:
        remainder = working[1:]
        if remainder in valid_remainders or (len(remainder) >= 2 and remainder[0] != 'e'):
            e_count += 1; working = remainder
        else:
            break
    result["e_count"] = e_count
    result["core"] = working
    return result


def load_schmitz():
    with open(TIRONIAN_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def load_perseus():
    with open(PERSEUS_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return set(w.lower() for w in (data if isinstance(data, list) else data.keys()))


# ══════════════════════════════════════════
# STEP 1: BUILD SUFFIX FINGERPRINTS
# ══════════════════════════════════════════
def build_fingerprints(lines):
    print("=" * 70)
    print("STEP 1: SUFFIX FINGERPRINTS")
    print("=" * 70)

    all_decomposed = []
    for line in lines:
        line_dec = [(decompose_token(w), line["section"]) for w in line["words"]]
        all_decomposed.extend(line_dec)

    # Build fingerprints for top suffixes
    suffix_data = defaultdict(lambda: {
        "count": 0, "sections": Counter(), "sh": 0, "ch": 0,
        "after_suffix": Counter(), "before_suffix": Counter(),
        "with_gallows": 0, "line_initial": 0, "line_final": 0,
        "e_counts": Counter(), "with_qo": 0, "with_d": 0,
    })

    # Build line-level index
    line_start = 0
    for line in lines:
        n = len(line["words"])
        for i in range(n):
            d, sec = all_decomposed[line_start + i]
            core = d["core"]
            if core == "UNIT" or d["count"] if hasattr(d, 'count') else False:
                pass

            sd = suffix_data[core]
            sd["count"] += 1
            sd["sections"][sec] += 1
            sd["e_counts"][d["e_count"]] += 1

            if d["prefix"].startswith("sh"): sd["sh"] += 1
            if d["prefix"].startswith("ch"): sd["ch"] += 1
            if d["prefix"].startswith("qo"): sd["with_qo"] += 1
            if d["prefix"] in ("d", "da"): sd["with_d"] += 1
            if d["gallows"]: sd["with_gallows"] += 1
            if i == 0: sd["line_initial"] += 1
            if i == n - 1: sd["line_final"] += 1

            # Bigrams (core-level)
            if i > 0:
                prev_d = all_decomposed[line_start + i - 1][0]
                sd["after_suffix"][prev_d["core"]] += 1
            if i < n - 1:
                next_d = all_decomposed[line_start + i + 1][0]
                sd["before_suffix"][next_d["core"]] += 1

        line_start += n

    # Print fingerprints for top suffixes
    top_suffixes = sorted(suffix_data.items(), key=lambda x: -x[1]["count"])
    top_cores = [(core, sd) for core, sd in top_suffixes
                 if core != "UNIT" and sd["count"] >= 200 and len(core) <= 4][:12]

    section_totals = Counter()
    for _, sec in all_decomposed:
        section_totals[sec] += 1

    print(f"\n  {'Core':>6s} {'N':>6s} {'sh%':>5s} {'ch%':>5s} {'qo%':>5s} {'d%':>4s} {'gal%':>5s} "
          f"{'S%':>5s} {'H%':>5s} {'B%':>5s} {'P%':>5s} {'Z%':>5s} {'e1%':>5s} {'e2%':>5s}")

    fingerprints = {}
    for core, sd in top_cores:
        n = sd["count"]
        sh_pct = 100*sd["sh"]/n
        ch_pct = 100*sd["ch"]/n
        qo_pct = 100*sd["with_qo"]/n
        d_pct = 100*sd["with_d"]/n
        gal_pct = 100*sd["with_gallows"]/n

        s_pct = 100*sd["sections"].get("S",0)/n
        h_pct = 100*sd["sections"].get("H",0)/n
        b_pct = 100*sd["sections"].get("B",0)/n
        p_pct = 100*sd["sections"].get("P",0)/n
        z_pct = 100*sd["sections"].get("Z",0)/n

        e1_pct = 100*sd["e_counts"].get(1,0)/n
        e2_pct = 100*sd["e_counts"].get(2,0)/n

        fingerprints[core] = {
            "count": n, "sh_pct": sh_pct, "ch_pct": ch_pct, "qo_pct": qo_pct,
            "s_pct": s_pct, "h_pct": h_pct, "b_pct": b_pct, "p_pct": p_pct,
            "e1_pct": e1_pct, "e2_pct": e2_pct,
            "material_pct": sh_pct + ch_pct,
        }

        print(f"  {core:>6s} {n:6d} {sh_pct:5.1f} {ch_pct:5.1f} {qo_pct:5.1f} {d_pct:4.1f} {gal_pct:5.1f} "
              f"{s_pct:5.1f} {h_pct:5.1f} {b_pct:5.1f} {p_pct:5.1f} {z_pct:5.1f} {e1_pct:5.1f} {e2_pct:5.1f}")

    return fingerprints, suffix_data, all_decomposed


# ══════════════════════════════════════════
# STEP 2: SCHMITZ CROSS-REFERENCE
# ══════════════════════════════════════════
def schmitz_crossref(fingerprints):
    print()
    print("=" * 70)
    print("STEP 2: SCHMITZ TIRONIAN CROSS-REFERENCE")
    print("=" * 70)

    schmitz = load_schmitz()
    perseus = load_perseus()

    # For each suffix, find Schmitz entries in pharmaceutical domains
    pharma_domains = {"medical", "pharmaceutical", "botanical"}

    print(f"\n  Searching {len(schmitz)} Schmitz entries...")

    # Build reverse index: what Schmitz entries exist for short Latin words?
    short_words = {}
    for entry in schmitz:
        val = entry.get("latin_value", "").lower()
        domains = set(entry.get("domains", []))
        freq = entry.get("frequency", "rare")
        if 2 <= len(val) <= 6:
            short_words[val] = {"domains": domains, "frequency": freq}

    # Known pharmaceutical substances from Antidotarium Nicolai
    PHARMA_SUBSTANCES = {
        "aqua": {"type": "vehicle", "forms": ["aqua", "aquae", "aq"], "desc": "water"},
        "oleum": {"type": "vehicle", "forms": ["oleum", "olei", "ol"], "desc": "oil"},
        "mel": {"type": "excipient", "forms": ["mel", "mellis"], "desc": "honey"},
        "sal": {"type": "ingredient", "forms": ["sal", "salis"], "desc": "salt"},
        "cera": {"type": "ingredient", "forms": ["cera", "cerae"], "desc": "wax"},
        "vinum": {"type": "vehicle", "forms": ["vinum", "vini"], "desc": "wine"},
        "acetum": {"type": "vehicle", "forms": ["acetum", "aceti"], "desc": "vinegar"},
        "aloe": {"type": "ingredient", "forms": ["aloe", "aloes"], "desc": "aloe"},
        "herba": {"type": "plant", "forms": ["herba", "herbae"], "desc": "herb"},
        "radix": {"type": "plant", "forms": ["radix", "radicis"], "desc": "root"},
        "cortex": {"type": "plant", "forms": ["cortex", "corticis"], "desc": "bark"},
        "semen": {"type": "plant", "forms": ["semen", "seminis"], "desc": "seed"},
        "flos": {"type": "plant", "forms": ["flos", "floris"], "desc": "flower"},
        "pulvis": {"type": "form", "forms": ["pulvis", "pulveris"], "desc": "powder"},
        "succus": {"type": "vehicle", "forms": ["succus", "succi"], "desc": "juice"},
        "lac": {"type": "vehicle", "forms": ["lac", "lactis"], "desc": "milk"},
        "gummi": {"type": "ingredient", "forms": ["gummi"], "desc": "gum"},
        "resina": {"type": "ingredient", "forms": ["resina", "resinae"], "desc": "resin"},
        "piper": {"type": "spice", "forms": ["piper", "piperis"], "desc": "pepper"},
        "nardus": {"type": "spice", "forms": ["nardus", "nardi"], "desc": "spikenard"},
    }

    # For each core suffix, propose best mapping based on:
    # 1. sh/ch marking (high = physical substance that gets processed)
    # 2. Sectorial distribution (H = herbal, S = pharma compound, P = recipe)
    # 3. Frequency match
    # 4. Schmitz/Perseus validation

    print(f"\n  PROPOSED SUBSTANCE MAPPINGS:")
    print(f"  {'Suffix':>6s} {'N':>6s} {'sh+ch%':>7s} {'Profile':>40s} {'Proposal':>15s}")
    print(f"  {'-'*80}")

    proposals = {}
    for core, fp in sorted(fingerprints.items(), key=lambda x: -x[1]["count"]):
        n = fp["count"]
        mat = fp["material_pct"]

        # Build profile description
        profile_parts = []
        if mat > 40:
            profile_parts.append("STRONG material marking")
        elif mat > 20:
            profile_parts.append("moderate material marking")

        if fp["s_pct"] > 40:
            profile_parts.append("pharma-dominant")
        elif fp["h_pct"] > 35:
            profile_parts.append("herbal-dominant")
        elif fp["b_pct"] > 30:
            profile_parts.append("balneo-dominant")

        if fp["qo_pct"] > 20:
            profile_parts.append("often with CUM")

        profile = '; '.join(profile_parts) if profile_parts else "mixed"

        # Propose mapping based on fingerprint
        proposal = "?"
        reason = ""

        if core == "dy":
            # Most frequent. sh=19%, ch=26%, B=20%dominant. Strong material.
            # "et" is the logogram mapping, but in new model dy is a suffix
            # Could be a generic procedural term
            proposal = "et/res"
            reason = "connective or generic substance"
        elif core == "ol":
            # P=14% dominant. sh=13%, ch=26%. Material marking.
            # In Schmitz: ol → not found as standalone
            # But oleum starts with ol...
            proposal = "oleum"
            reason = "P-dominant, material marked, ol=oil prefix"
        elif core == "ar":
            # Often standalone (32%). qo=17%. Mixed sections.
            proposal = "aqua"  # or "are" (infinitive)
            reason = "standalone, CUM-frequent, universal"
        elif core == "or":
            # H=30% dominant. sh=11%, ch=27%. Material.
            # V19 mapped or → hiera
            proposal = "hiera"
            reason = "V19 Tironian confirmed, H-dominant"
        elif core == "al":
            # qo=24% dominant. S=43%.
            proposal = "sal"
            reason = "CUM-dominant (cum sale), S-dominant"
        elif core == "ody":
            # sh=18%, ch=34%. Strong material. H+P mixed.
            proposal = "acetum"
            reason = "strong material marking, variant of dy"
        elif core == "ckhy":
            # sh=28%, ch=55%! Strongest ch marking.
            proposal = "cera"
            reason = "STRONGEST ch% = most processed substance (wax)"
        elif core == "chy":
            # qo=38%! Very high CUM usage.
            proposal = "mel"
            reason = "highest CUM% (cum melle = with honey)"
        elif core == "am":
            # Standalone 32%. Mixed.
            proposal = "cum/ana"
            reason = "often standalone, may be function word"
        elif core == "os":
            # sh=11%, ch=42%.
            proposal = "succus"
            reason = "material marked, ch-dominant (processed juice)"
        elif core == "y":
            # Very frequent but may be residual prefix
            proposal = "de/prep"
            reason = "likely residual prefix, not substance"
        elif core == "o":
            proposal = "eo/id"
            reason = "likely pronoun/reference"

        proposals[core] = proposal
        print(f"  {core:>6s} {n:6d} {mat:7.1f} {profile:>40s} {proposal:>15s}")

    # Verify proposals in Schmitz/Perseus
    print(f"\n  VERIFICATION:")
    for core, proposal in proposals.items():
        in_schmitz = any(e.get("latin_value","").lower() == proposal
                        for e in schmitz) if proposal not in ("?", "et/res", "de/prep", "cum/ana", "eo/id") else False
        in_perseus = proposal in perseus if proposal not in ("?", "et/res", "de/prep", "cum/ana", "eo/id") else False
        print(f"    {core:>6s} → {proposal:>10s}  Schmitz={'YES' if in_schmitz else 'no':>3s}  Perseus={'YES' if in_perseus else 'no':>3s}")

    return proposals


# ══════════════════════════════════════════
# STEP 3: FULL RECIPE DECODE
# ══════════════════════════════════════════
def full_recipe_decode(lines, proposals):
    print()
    print("=" * 70)
    print("STEP 3: FULL RECIPE DECODE WITH SUBSTANCE MAPPING")
    print("=" * 70)

    PREFIX_MEANING = {
        "": "", "d": "in", "da": "in", "qo": "cum", "qok": "cum", "qot": "cum",
        "y": "de", "r": "re", "ol": "ex", "l": "per",
        "ch": "[P]", "sh": "[M]", "ok": "", "ot": "", "f": "", "t": "§", "k": "",
    }
    GALLOWS_MEANING = {"p": "Rx", "t": "§", "k": "", "f": "Rx", "": ""}

    def decode_token(token):
        d = decompose_token(token)
        parts = []

        g = GALLOWS_MEANING.get(d["gallows"], "")
        if g: parts.append(g)

        pfx = d["prefix"].split("+")[0]
        p = PREFIX_MEANING.get(pfx, "")
        if p: parts.append(p)

        if d["core"] == "UNIT":
            unit_word = "℥" if d["unit_type"] == "n" else "ʒ"
            parts.append(f"{d['unit_n']}{unit_word}")
        elif d["core"] in proposals and proposals[d["core"]] not in ("?",):
            substance = proposals[d["core"]]
            if d["e_count"] > 0:
                parts.append(f"{d['e_count']}×{substance}")
            else:
                parts.append(substance)
        else:
            if d["e_count"] > 0:
                parts.append(f"{d['e_count']}×[{d['core']}]")
            else:
                parts.append(f"[{d['core']}]")

        return ' '.join(parts)

    # Decode pharma sections
    print(f"\n  PHARMACEUTICAL RECIPES (S section):")
    shown = 0
    for line in lines:
        if shown >= 25: break
        if line["section"] != "S": continue
        if len(line["words"]) < 5: continue

        eva = ' '.join(line["words"])
        decoded = ' . '.join(decode_token(w) for w in line["words"])

        # Quality filter: skip lines with too many unknowns
        unknown_count = decoded.count('[')
        total_parts = len(line["words"])
        if unknown_count > total_parts * 0.5: continue

        print(f"\n    [{line['folio']}]")
        print(f"      EVA: {eva[:110]}")
        print(f"      RCP: {decoded[:110]}")
        shown += 1

    # F103R
    print(f"\n  F103R RECIPES:")
    shown = 0
    for line in lines:
        if line["folio"].upper() != "F103R": continue
        if shown >= 15: break

        eva = ' '.join(line["words"])
        decoded = ' . '.join(decode_token(w) for w in line["words"])
        unknown_count = decoded.count('[')
        if unknown_count > len(line["words"]) * 0.5: continue

        print(f"\n    EVA: {eva[:110]}")
        print(f"    RCP: {decoded[:110]}")
        shown += 1

    # Herbal labels
    print(f"\n  HERBAL LABELS (short H lines):")
    shown = 0
    for line in lines:
        if line["section"] != "H" or len(line["words"]) > 4: continue
        if shown >= 15: break

        eva = ' '.join(line["words"])
        decoded = ' . '.join(decode_token(w) for w in line["words"])

        print(f"    [{line['folio']}] {eva:35s} → {decoded}")
        shown += 1

    return proposals


# ══════════════════════════════════════════
# STEP 4: RECIPE COHERENCE CHECK
# ══════════════════════════════════════════
def recipe_coherence(lines, proposals):
    print()
    print("=" * 70)
    print("STEP 4: RECIPE COHERENCE — Does it read like pharmacy?")
    print("=" * 70)

    # A medieval recipe should have:
    # 1. Rx (recipe/take) at beginning
    # 2. Ingredient list with quantities
    # 3. Preparation instructions (cum X, in Y)
    # 4. [M] = raw materials, [P] = processed products

    # Count recipe-like patterns
    rx_count = 0
    cum_substance = Counter()
    in_substance = Counter()
    material_substance = Counter()

    for line in lines:
        for i, w in enumerate(line["words"]):
            d = decompose_token(w)

            if d["gallows"] in ("p", "f"):
                rx_count += 1

            if d["core"] in proposals:
                subst = proposals[d["core"]]
                if d["prefix"].startswith("qo"):
                    cum_substance[subst] += 1
                if d["prefix"] in ("d", "da"):
                    in_substance[subst] += 1
                if d["prefix"].startswith("sh"):
                    material_substance[f"[M]{subst}"] += 1
                if d["prefix"].startswith("ch"):
                    material_substance[f"[P]{subst}"] += 1

    print(f"\n  Rx (recipe/take) commands: {rx_count}")
    print(f"\n  'cum' (with) + substance:")
    for subst, count in cum_substance.most_common(10):
        print(f"    cum {subst:>15s}: {count:5d}")

    print(f"\n  'in' + substance:")
    for subst, count in in_substance.most_common(10):
        print(f"    in {subst:>15s}: {count:5d}")

    print(f"\n  Material markers + substance:")
    for subst, count in material_substance.most_common(15):
        print(f"    {subst:>20s}: {count:5d}")


# ══════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════
if __name__ == "__main__":
    print("V27 SUBSTANCE MAPPING")
    print("=" * 70)
    print()

    lines = parse_lines_eva()
    print(f"  {len(lines)} lines, {sum(len(l['words']) for l in lines)} tokens\n")

    fingerprints, suffix_data, all_dec = build_fingerprints(lines)
    proposals = schmitz_crossref(fingerprints)
    full_recipe_decode(lines, proposals)
    recipe_coherence(lines, proposals)

    # Save
    results = {
        "proposals": proposals,
        "fingerprints": {k: {kk: round(vv, 1) if isinstance(vv, float) else vv
                             for kk, vv in v.items()}
                        for k, v in fingerprints.items()},
    }
    with open(RESULTS / "v27_substance_mapping.json", 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n  Results saved to {RESULTS / 'v27_substance_mapping.json'}")
