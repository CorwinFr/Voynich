#!/usr/bin/env python3
"""
V25 — Noun Hypothesis Testing: What are the top 4 unknown roots?

V24 showed that edy, aiin, eey, al behave as NOUNS in recipe structure.
This script tests specific pharmaceutical noun candidates for each,
decodes sample lines, and checks which produces readable Latin recipes.

Candidates based on V24 positional profiling:
  aiin (1733x): follows hiera(111x), iure(91x), es(96x) → VEHICLE or KEY INGREDIENT
    → aqua (water), ana (of each), alumen (alum)
  edy (1845x): sh=24%, ch=32%, high MATERIA/PRODUCT marking → INGREDIENT with raw/processed form
    → oleum (oil), herba (herb), inde (thence)
  eey (1290x): sh=12%, ch=16%, pharma=46% → INGREDIENT
    → mel (honey), vinum (wine), succus (juice)
  al (1002x): after iure(58x), low sh/ch → MODIFIER or short ingredient
    → sal (salt), aloe, ana (of each)
"""
import json, sys, re
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

BASE = Path("d:/Github/Voynich")
DECODED_FILE = BASE / "v12/output/VOYNICH_DECODE_V12_INGREDIENTS.txt"
RESULTS = BASE / "v12/validation_v2/results"
LOGOGRAMS_PATH = BASE / "v12/rules/logograms.json"
PERSEUS_PATH = BASE / "data/latin_valid_wordset.json"

GALLOWS = set("ktpf")
PREFIXES_ORDER = ["qok", "qot", "qo", "ok", "ot", "ol", "da", "ch", "sh",
                  "d", "y", "r", "p", "l", "t", "f", "k"]
PREFIXES_ORDER.sort(key=len, reverse=True)

PREFIX_LATIN = {
    "d": "in", "da": "in", "qo": "cum", "qok": "cum", "qot": "cum",
    "y": "de", "r": "re", "p": "", "ol": "ex", "l": "per",
    "ch": "[P]", "sh": "[M]",  # short markers
    "ok": "", "ot": "", "f": "", "t": "§", "k": "",
}

GALLOWS_FUNC = {"p": "Rx", "t": "§", "k": "", "f": "Rx"}


def load_base_root_map():
    with open(LOGOGRAMS_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    result = {}
    for eva, info in data.items():
        if isinstance(info, dict) and info.get("latin"):
            result[eva.lower()] = info["latin"].lower()
        elif isinstance(info, str):
            result[eva.lower()] = info.lower()

    tir_path = RESULTS / "v19a_tironian_exhaustive.json"
    if tir_path.exists():
        with open(tir_path, 'r') as f:
            tdata = json.load(f)
        for m in tdata.get("top_matches", []):
            if m.get("match_type") in ("exact", "logogram"):
                if m["root"] not in result:
                    result[m["root"]] = m["decoded"]
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


def decode_line(words, root_map):
    """Decode a line of EVA tokens using the given root map."""
    parts = []
    for token in words:
        g, pfx, root = extract_root(token)

        g_func = GALLOWS_FUNC.get(g, "") if g else ""
        p_lat = PREFIX_LATIN.get(pfx, "") if pfx else ""

        if root in root_map:
            r_lat = root_map[root]
            bits = [b for b in [g_func, p_lat, r_lat] if b]
            parts.append(' '.join(bits))
        elif pfx and p_lat:
            bits = [b for b in [g_func, p_lat, f"?{root}?"] if b]
            parts.append(' '.join(bits))
        else:
            parts.append(f"_{token}_")
    return ' | '.join(parts)


# ══════════════════════════════════════════
# HYPOTHESIS SETS
# ══════════════════════════════════════════
HYPOTHESES = {
    "H1_aqua_oleum_mel_sal": {
        "aiin": "aqua",    # water - universal vehicle (1733x)
        "edy": "oleum",    # oil - raw/processed forms (1845x)
        "eey": "mel",      # honey - key excipient (1290x)
        "al": "sal",       # salt (1002x)
        "ain": "uncia",    # ounce/unit (915x)
        "eedy": "olei",    # genitive of oleum (962x)
        "eol": "semen",    # seed (539x)
        "eor": "herba",    # herb (228x)
    },
    "H2_aqua_herba_vinum_aloe": {
        "aiin": "aqua",
        "edy": "herba",    # herb
        "eey": "vinum",    # wine
        "al": "aloe",      # aloe
        "ain": "ana",      # of each/equal parts
        "eedy": "herbae",  # genitive of herba
        "eol": "radix",    # root
        "eor": "folium",   # leaf
    },
    "H3_ana_oleum_aqua_sal": {
        "aiin": "ana",     # of each (equal parts) - explains frequency
        "edy": "oleum",
        "eey": "aqua",
        "al": "sal",
        "ain": "uncia",
        "eedy": "olei",
        "eol": "semen",
        "eor": "herba",
    },
    "H4_aqua_cera_mel_sal": {
        "aiin": "aqua",
        "edy": "cera",     # wax - raw/processed
        "eey": "mel",
        "al": "sal",
        "ain": "dosis",    # dose
        "eedy": "cerae",   # genitive
        "eol": "pulvis",   # powder
        "eor": "cortex",   # bark
    },
}


# ══════════════════════════════════════════
# PHARMACEUTICAL COLLOCATION SCORING
# ══════════════════════════════════════════
# Common pharmaceutical Latin collocations (word pairs that make sense together)
GOOD_COLLOCATIONS = {
    ("cum", "aqua"), ("cum", "vinum"), ("cum", "mel"), ("cum", "oleum"),
    ("cum", "acetum"), ("cum", "sal"), ("cum", "cera"), ("cum", "aloe"),
    ("in", "aqua"), ("in", "oleum"), ("in", "vinum"), ("in", "mel"),
    ("ex", "aqua"), ("ex", "oleum"), ("ex", "herba"), ("ex", "radix"),
    ("de", "aqua"), ("de", "oleum"), ("de", "herba"),
    ("per", "aqua"), ("per", "oleum"),
    ("Rx", "aqua"), ("Rx", "oleum"), ("Rx", "mel"), ("Rx", "sal"),
    ("Rx", "cera"), ("Rx", "aloe"), ("Rx", "herba"), ("Rx", "vinum"),
    ("hiera", "cum"), ("hiera", "in"), ("hiera", "et"),
    ("coque", "cum"), ("coque", "in"),
    ("misce", "cum"), ("misce", "et"),
    ("recipe", "aqua"), ("recipe", "oleum"), ("recipe", "mel"),
    ("oleum", "et"), ("aqua", "et"), ("mel", "et"), ("sal", "et"),
    ("cera", "et"), ("vinum", "et"), ("aloe", "et"),
    ("[M]", "aqua"), ("[M]", "oleum"), ("[M]", "mel"), ("[M]", "sal"),
    ("[M]", "cera"), ("[M]", "herba"), ("[M]", "vinum"), ("[M]", "aloe"),
    ("[P]", "aqua"), ("[P]", "oleum"), ("[P]", "mel"), ("[P]", "sal"),
    ("[P]", "cera"), ("[P]", "herba"), ("[P]", "vinum"), ("[P]", "aloe"),
    # Genitive constructions
    ("aqua", "oleum"), ("oleum", "aqua"),
    ("aqua", "mel"), ("mel", "aqua"),
    ("aqua", "sal"), ("sal", "aqua"),
    # Quantity + ingredient
    ("uncia", "aqua"), ("uncia", "oleum"), ("uncia", "mel"),
    ("ana", "aqua"), ("ana", "oleum"), ("ana", "mel"), ("ana", "sal"),
    ("dosis", "aqua"), ("dosis", "oleum"),
}

BAD_COLLOCATIONS = {
    # Things that should NEVER appear together
    ("aqua", "aqua"),  # water water
    ("oleum", "oleum"),
    ("sal", "sal"),
    ("et", "et"),  # and and
    ("in", "in"),  # in in (but this exists in corpus!)
    ("cum", "cum"),
}


def score_hypothesis(lines, base_root_map, hypothesis, hyp_name):
    """Score a hypothesis by decoding pharma lines and checking collocations."""

    # Merge base + hypothesis
    test_map = dict(base_root_map)
    test_map.update(hypothesis)

    good_hits = 0
    bad_hits = 0
    total_bigrams = 0
    unknown_tokens = 0
    total_tokens = 0

    decoded_samples = []

    # Focus on pharma sections (S, P) + some herbal (H)
    pharma_lines = [l for l in lines if l["section"] in ("S", "P")]
    herbal_lines = [l for l in lines if l["section"] == "H"]

    for line in pharma_lines + herbal_lines[:200]:
        words = line["words"]
        total_tokens += len(words)

        # Decode each token to its Latin root
        decoded_roots = []
        for token in words:
            g, pfx, root = extract_root(token)
            if root in test_map:
                decoded_roots.append(test_map[root])
            else:
                decoded_roots.append(None)
                unknown_tokens += 1

        # Also get prefix values
        decoded_full = []
        for token in words:
            g, pfx, root = extract_root(token)
            g_func = GALLOWS_FUNC.get(g, "") if g else ""
            p_lat = PREFIX_LATIN.get(pfx, "") if pfx else ""
            r_lat = test_map.get(root, None)
            decoded_full.append((g_func, p_lat, r_lat))

        # Check bigrams
        for i in range(len(decoded_full) - 1):
            g1, p1, r1 = decoded_full[i]
            g2, p2, r2 = decoded_full[i+1]

            if r1 is None or r2 is None:
                continue

            total_bigrams += 1

            # Check all possible word pairs
            words1 = [w for w in [g1, p1, r1] if w]
            words2 = [w for w in [g2, p2, r2] if w]

            for w1 in words1:
                for w2 in words2:
                    if (w1, w2) in GOOD_COLLOCATIONS:
                        good_hits += 1
                    if (w1, w2) in BAD_COLLOCATIONS:
                        bad_hits += 1

        # Save some decoded samples
        if len(decoded_samples) < 40 and line["section"] in ("S", "P"):
            decoded = decode_line(words, test_map)
            unknown_in_line = decoded.count("?") + decoded.count("_")
            if unknown_in_line < len(words) * 0.4:  # At least 60% decoded
                decoded_samples.append({
                    "folio": line["folio"],
                    "section": line["section"],
                    "eva": ' '.join(words),
                    "decoded": decoded,
                })

    known_pct = 100 * (total_tokens - unknown_tokens) / max(total_tokens, 1)
    colloc_score = good_hits - bad_hits * 3  # Penalize bad collocations heavily

    return {
        "name": hyp_name,
        "good_hits": good_hits,
        "bad_hits": bad_hits,
        "colloc_score": colloc_score,
        "total_bigrams": total_bigrams,
        "known_pct": round(known_pct, 1),
        "unknown_tokens": unknown_tokens,
        "total_tokens": total_tokens,
        "samples": decoded_samples,
    }


# ══════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════
if __name__ == "__main__":
    print("V25 NOUN HYPOTHESIS TESTING")
    print("=" * 70)
    print()

    base_map = load_base_root_map()
    lines = parse_lines_eva()
    print(f"Base root map: {len(base_map)} entries")
    print(f"Corpus: {len(lines)} lines, {sum(len(l['words']) for l in lines)} tokens")
    print()

    results = {}

    for hyp_name, hypothesis in HYPOTHESES.items():
        print(f"\n{'='*70}")
        print(f"TESTING: {hyp_name}")
        print(f"  Mappings: {hypothesis}")
        print(f"{'='*70}")

        result = score_hypothesis(lines, base_map, hypothesis, hyp_name)
        results[hyp_name] = result

        print(f"\n  SCORES:")
        print(f"    Good collocations:  {result['good_hits']}")
        print(f"    Bad collocations:   {result['bad_hits']}")
        print(f"    Collocation score:  {result['colloc_score']}")
        print(f"    Known tokens:       {result['known_pct']}%")
        print(f"    Total bigrams:      {result['total_bigrams']}")

        print(f"\n  SAMPLE DECODED LINES (pharma sections):")
        for sample in result["samples"][:15]:
            print(f"\n    [{sample['folio']}|{sample['section']}]")
            print(f"      EVA: {sample['eva'][:100]}")
            print(f"      LAT: {sample['decoded'][:100]}")

    # ══════════════════════════════════════════
    # COMPARISON
    # ══════════════════════════════════════════
    print()
    print("=" * 70)
    print("HYPOTHESIS COMPARISON")
    print("=" * 70)
    print()
    print(f"  {'Hypothesis':>30s} {'Good':>6s} {'Bad':>5s} {'Score':>7s} {'Known%':>7s}")
    print(f"  {'-'*57}")

    ranked = sorted(results.values(), key=lambda x: -x["colloc_score"])
    for r in ranked:
        print(f"  {r['name']:>30s} {r['good_hits']:6d} {r['bad_hits']:5d} {r['colloc_score']:7d} {r['known_pct']:7.1f}%")

    winner = ranked[0]
    print(f"\n  WINNER: {winner['name']} (score: {winner['colloc_score']})")
    print(f"\n  Best decoded lines from winner:")
    for sample in winner["samples"][:20]:
        print(f"\n    [{sample['folio']}|{sample['section']}]")
        print(f"      EVA: {sample['eva'][:110]}")
        print(f"      LAT: {sample['decoded'][:110]}")

    # Save
    save_data = {
        "hypotheses": {k: {
            "mappings": v,
        } for k, v in HYPOTHESES.items()},
        "scores": {k: {
            "good_hits": v["good_hits"],
            "bad_hits": v["bad_hits"],
            "colloc_score": v["colloc_score"],
            "known_pct": v["known_pct"],
        } for k, v in results.items()},
        "winner": winner["name"],
        "winner_samples": winner["samples"][:30],
    }
    with open(RESULTS / "v25_noun_hypotheses.json", 'w', encoding='utf-8') as f:
        json.dump(save_data, f, indent=2, ensure_ascii=False)

    print(f"\n  Results saved to {RESULTS / 'v25_noun_hypotheses.json'}")
