#!/usr/bin/env python3
"""
Phase A+B+D: Enrich folio_catalogue.json with:
  A1: Fixed foldout image mapping
  A2: Structured ingredient/verb extraction
  A3: Interestingness score + tier assignment
  B:  Section-based descriptions
  D2: Yale/Beinecke attribution
"""
import json, re, os, sys
from collections import Counter

DECODE_FILE = "d:/Github/Voynich/v12/output/VOYNICH_DECODE_V12_INGREDIENTS.txt"
IMAGES_DIR  = r"D:\Github\Voynich\data\images\pages"
INPUT_JSON  = "d:/tmp/build_paper/folio_catalogue.json"
OUTPUT_JSON = "d:/tmp/build_paper/folio_catalogue_enriched.json"

# ══════════════════════════════════════════
# A1: MULTI-PANEL IMAGE MAP
# ══════════════════════════════════════════
MULTI_PANEL_IMAGE_MAP = {
    "F67R1": "121_67r.jpg",  "F67R2": "121_67r.jpg",
    "F67V1": "122_67v.jpg",  "F67V2": "122_67v.jpg",
    "F68R1": "123_68r.jpg",  "F68R2": "123_68r.jpg",  "F68R3": "123_68r.jpg",
    "F68V1": "124_68v.jpg",  "F68V2": "124_68v.jpg",  "F68V3": "124_68v.jpg",
    "F70R1": "126_69v_and_70r.jpg",  "F70R2": "126_69v_and_70r.jpg",
    "F70V1": "127_70v_(part).jpg",   "F70V2": "128_70v_(part).jpg",
    "F72R1": "130_71v_and_72r.jpg",  "F72R2": "130_71v_and_72r.jpg",  "F72R3": "130_71v_and_72r.jpg",
    "F72V1": "131_72v_(part).jpg",   "F72V2": "131_72v_(part).jpg",   "F72V3": "132_72v_(part).jpg",
    "F85R1": "155_85r_(part)_(part_of_85-86_foldout).jpg",
    "F85R2": "156_85r_(part)_86v_(part)_(part_of_85-86_foldout).jpg",
    "F86V3": "157_86v_(part)_(part_of_85-86_foldout).jpg",
    "F86V4": "156_85r_(part)_86v_(part)_(part_of_85-86_foldout).jpg",
    "F86V5": "158_85v_and_86r_(foldout).jpg",
    "F86V6": "158_85v_and_86r_(foldout).jpg",
    "F89R1": "162_88v_and_89r.jpg",  "F89R2": "162_88v_and_89r.jpg",
    "F89V1": "163_89v_(part).jpg",   "F89V2": "164_89v_(part)_and_90r.jpg",
    "F90R1": "165_90r.jpg",          "F90R2": "164_89v_(part)_and_90r.jpg",
    "F90V1": "166_90v_(part).jpg",   "F90V2": "166_90v_(part).jpg",
    "F95R1": "170_94v_and_95r.jpg",  "F95R2": "170_94v_and_95r.jpg",
    "F95V1": "171_95v_(part).jpg",   "F95V2": "172_95v.jpg",
    "F100V": "179_100v.jpg",
    "F102R1": "180_101v_(part)_and_102r.jpg", "F102R2": "180_101v_(part)_and_102r.jpg",
    "F102V1": "181_102v_(part).jpg",  "F102V2": "182_102v_(part).jpg",
}

# ══════════════════════════════════════════
# A2: VOCABULARY SETS
# ══════════════════════════════════════════
INGREDIENTS = {
    "aloe", "aloes", "ture", "turis", "sal", "olei", "oleo", "oleum",
    "aceto", "acetum", "cerae", "cera", "mel", "mellis", "iecur",
    "succi", "succus", "sapa", "sapam", "asari", "asarum", "asara",
    "cardamomi", "costi", "costus", "lauri", "piretri", "pepe",
    "lilie", "enula", "inula", "hiera", "cicura", "nardi", "nardus",
    "cassiae", "cassia", "croci", "crocus", "piperis", "piper",
    "cinamomi", "cinamomum", "masticis", "mirre", "myrrha",
    "apii", "apium", "vini", "vinum", "aquam", "aqua",
}

RECIPE_VERBS = {
    "coque", "coquas", "coquere", "coquo", "coquit", "coquunt",
    "recipe", "misce", "tere", "cola", "ciere", "cies", "ciet",
    "ede", "dare", "equaliter",
}

BODY_PARTS = {
    "rens", "iecur", "ilia", "caput", "dolorem", "dolor",
    "stomachus", "venter", "pectus", "oculus", "auris",
}

ASTRO_TERMS = {
    "crux", "aros", "luna", "sol", "stella", "aries",
}

# ══════════════════════════════════════════
# A2: PARSE DECODE FILE — extract per-folio words
# ══════════════════════════════════════════
def parse_decode_file():
    """Return dict: folio_id -> list of latin words (lowercase)."""
    with open(DECODE_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    folio_words = {}
    current_folio = None
    words = []

    for line in content.split('\n'):
        m = re.match(r'\s*FOLIO (\S+) \|', line)
        if m:
            if current_folio:
                folio_words[current_folio] = words
            current_folio = m.group(1)
            words = []
        elif 'LATIN:' in line:
            latin_part = line.split('LATIN:')[1].strip()
            # Extract clean words, skip opaque markers
            for w in re.findall(r'[a-zA-Z]{2,}', latin_part):
                wl = w.lower()
                if not wl.startswith('_'):  # skip _opaque_
                    words.append(wl)

    if current_folio:
        folio_words[current_folio] = words

    return folio_words


# ══════════════════════════════════════════
# A2: EXTRACT STRUCTURED VOCABULARY
# ══════════════════════════════════════════
def extract_vocabulary(words):
    """From a word list, extract structured ingredient/verb/body/astro lists."""
    word_set = set(words)
    freq = Counter(words)

    found_ingredients = sorted(set(w for w in words if w in INGREDIENTS), key=lambda x: -freq[x])
    found_verbs = sorted(set(w for w in words if w in RECIPE_VERBS), key=lambda x: -freq[x])
    found_body = sorted(set(w for w in words if w in BODY_PARTS), key=lambda x: -freq[x])
    found_astro = sorted(set(w for w in words if w in ASTRO_TERMS), key=lambda x: -freq[x])

    # Rare words (appear <= 2 times in this folio AND are 5+ chars)
    rare = [w for w, c in freq.items() if c <= 2 and len(w) >= 5
            and w not in INGREDIENTS and w not in RECIPE_VERBS
            and w not in {"eius", "aquam", "cum", "iure"}]

    return {
        "ingredients": found_ingredients,
        "verbs": found_verbs,
        "body_parts": found_body,
        "astro_terms": found_astro,
        "rare_words": rare[:10],  # cap at 10
    }


# ══════════════════════════════════════════
# A3: INTERESTINGNESS SCORE + TIER
# ══════════════════════════════════════════
FLAGSHIP_FOLIOS = {
    "F1R", "F1V", "F33R", "F57V", "F67R1", "F71R", "F75R",
    "F84V", "F85R1", "F86V3", "F103R", "F108V", "F116V",
}

def compute_interest_and_tier(entry, vocab):
    """Return (interest_score, tier)."""
    s = entry["stats"]
    section = entry["section"]
    folio = entry["folio"]

    # Flagship override
    if folio in FLAGSHIP_FOLIOS:
        return (100, "flagship")

    score = 0.0

    # Medical vocabulary richness
    score += s["medical_pct"] * 1.5

    # Rare/notable ingredients
    notable_ingr = {"nardi", "cassiae", "asari", "cardamomi", "costi",
                    "piretri", "pepe", "lilie", "enula", "inula", "croci"}
    found_notable = len(set(vocab["ingredients"]) & notable_ingr)
    score += found_notable * 15

    # Word count (more content = more interesting)
    score += min(entry["words"] / 20, 20)

    # Non-herbal sections are inherently more interesting for catalogue
    if section in ("C", "A", "Z"):
        score += 25
    elif section == "B":
        score += 15
    elif section in ("S", "P"):
        score += 10

    # Opaque percentage (mystery factor)
    score += s.get("opaque", 0) / max(entry["words"], 1) * 100 * 0.5

    # Multi-panel = notable
    if folio in MULTI_PANEL_IMAGE_MAP:
        score += 10

    # Tier assignment
    if score >= 40:
        tier = "notable"
    elif score >= 15:
        tier = "standard"
    else:
        tier = "minimal"

    return (round(score, 1), tier)


# ══════════════════════════════════════════
# B: ILLUSTRATION TYPE + TEXT LAYOUT
# ══════════════════════════════════════════
def classify_illustration(folio, section):
    fid = folio.upper()

    if fid == "F57V":
        return "volvelle", "text_in_rings"

    if section == "H":
        return "herbal_single", "text_wraps_plant"
    if section == "B":
        return "balnea_pool", "text_columns"
    if section in ("S", "P"):
        return "pharma_jars", "text_block"
    if section == "Z":
        return "zodiac_circle", "text_in_sectors"
    if section == "A":
        return "astro_rosette", "text_in_rings"
    if section == "C":
        if "85" in fid or "86" in fid:
            return "cosmo_foldout", "text_in_rings"
        return "cosmo_diagram", "text_in_rings"
    if section == "T":
        return "text_only", "text_block"

    return "unknown", "unknown"


# ══════════════════════════════════════════
# B: GENERATE DESCRIPTION
# ══════════════════════════════════════════
def generate_description(entry, vocab):
    section = entry["section"]
    folio = entry["folio"]
    words = entry["words"]
    ingr = vocab["ingredients"]
    verbs = vocab["verbs"]
    body = vocab["body_parts"]
    astro = vocab["astro_terms"]
    med_pct = entry["stats"]["medical_pct"]
    pers_pct = entry["stats"]["perseus_pct"]

    # --- Page description (visual) ---
    illust, _ = classify_illustration(folio, section)

    if illust == "herbal_single":
        page_desc = "Single plant illustration with root system and leaves; text wraps around drawing."
    elif illust == "balnea_pool":
        page_desc = "Human figures (nude, female) in circular or connected pools/baths with pipes."
    elif illust == "pharma_jars":
        page_desc = "Dense text with colored containers/jars illustrated in margins."
    elif illust == "zodiac_circle":
        page_desc = "Circular zodiac diagram with human figures and star labels around perimeter."
    elif illust == "astro_rosette":
        page_desc = "Circular astronomical/cosmological diagram with concentric text rings."
    elif illust == "cosmo_foldout":
        page_desc = "Large multi-page foldout with complex cosmological diagrams and concentric circles."
    elif illust == "cosmo_diagram":
        page_desc = "Cosmological diagram with concentric rings and symbolic illustrations."
    elif illust == "volvelle":
        page_desc = "Circular volvelle with 4 concentric text rings, central sun motif, and 4 cardinal figures."
    elif illust == "text_only":
        page_desc = "Text-only page (title, boundary, or transitional content)."
    else:
        page_desc = "Page with text and/or illustrations."

    # --- Decoded subject ---
    parts = []

    if verbs:
        verb_str = ", ".join(verbs[:4])
        parts.append(f"preparation verbs ({verb_str})")

    if ingr:
        # Filter out ultra-common aquam
        notable = [i for i in ingr if i not in ("aquam", "aqua")][:5]
        if notable:
            parts.append(f"ingredients: {', '.join(notable)}")

    if body:
        parts.append(f"body references: {', '.join(body[:3])}")

    if astro:
        parts.append(f"astrological terms: {', '.join(astro)}")

    if parts:
        decoded_subject = f"Decoded vocabulary includes {'; '.join(parts)}."
    else:
        decoded_subject = f"Decoded text at {pers_pct}% Perseus validation."

    # Section-specific additions
    if section == "H" and med_pct > 20:
        decoded_subject += " High pharmaceutical content for a herbal page."
    elif section == "Z":
        decoded_subject += " Star/zodiac labels use nomenclator cipher (not phonetic K&A)."
    elif section == "B":
        decoded_subject += " Consistent with medieval hydrotherapy (De Balneis tradition)."
    elif section in ("S", "P") and len(ingr) >= 4:
        decoded_subject += " Recipe-dense — possible Antidotarium Nicolai parallel."

    # --- Notable discoveries ---
    discoveries = []
    notable_set = {"nardi", "cassiae", "asari", "cardamomi", "costi",
                   "piretri", "pepe", "lilie", "enula", "inula", "apii"}
    found_notable = set(ingr) & notable_set
    if found_notable:
        discoveries.append(f"Contains notable ingredients: {', '.join(sorted(found_notable))}")
    if "equaliter" in verbs:
        discoveries.append("Contains 'equaliter' (ana = equal parts) — pharmaceutical dosage marker")
    if med_pct > 25:
        discoveries.append(f"Unusually high medical vocabulary ({med_pct}%)")

    return page_desc, decoded_subject, discoveries


# ══════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════
def main():
    # Load existing catalogue
    with open(INPUT_JSON, 'r', encoding='utf-8') as f:
        catalogue = json.load(f)

    # Parse decode file
    print("Parsing decode file...")
    folio_words = parse_decode_file()

    # Build global word frequency for rarity detection
    global_freq = Counter()
    for words in folio_words.values():
        global_freq.update(words)

    print(f"Parsed {len(folio_words)} folios, {sum(len(w) for w in folio_words.values())} total words")

    # Enrich each entry
    for entry in catalogue:
        folio = entry["folio"]

        # A1: Fix image for foldouts
        if not entry.get("image") and folio in MULTI_PANEL_IMAGE_MAP:
            entry["image"] = MULTI_PANEL_IMAGE_MAP[folio]

        # Mark multi-panel
        entry["multi_panel"] = folio in MULTI_PANEL_IMAGE_MAP

        # A2: Extract structured vocabulary
        words = folio_words.get(folio, [])
        vocab = extract_vocabulary(words)
        entry["vocabulary"] = vocab

        # A3: Interestingness + tier
        interest, tier = compute_interest_and_tier(entry, vocab)
        entry["interest_score"] = interest
        entry["tier"] = tier

        # B: Illustration type + text layout
        illust_type, text_layout = classify_illustration(folio, entry["section"])
        entry["illustration_type"] = illust_type
        entry["text_layout"] = text_layout

        # B: Generate descriptions
        page_desc, decoded_subject, discoveries = generate_description(entry, vocab)
        entry["page_description"] = page_desc
        entry["decoded_subject"] = decoded_subject
        entry["notable_discoveries"] = discoveries

        # D2: Attribution
        fid_clean = folio.lower().rstrip("0123456789") if folio[-1].isdigit() and not folio[-2].isdigit() else folio.lower()
        entry["attribution"] = f"Yale University, Beinecke Rare Book and Manuscript Library, MS 408, f.{fid_clean}"

    # Save enriched catalogue
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(catalogue, f, indent=2, ensure_ascii=False)

    # Stats
    tiers = Counter(e["tier"] for e in catalogue)
    with_img = sum(1 for e in catalogue if e.get("image"))
    with_disc = sum(1 for e in catalogue if e.get("notable_discoveries"))
    notable_ingredients_all = set()
    for e in catalogue:
        notable_ingredients_all.update(e["vocabulary"]["ingredients"])

    print(f"\nEnriched {len(catalogue)} folios -> {OUTPUT_JSON}")
    print(f"Tiers: {dict(tiers)}")
    print(f"With image: {with_img}/{len(catalogue)}")
    print(f"With discoveries: {with_disc}")
    print(f"Unique ingredients across manuscript: {sorted(notable_ingredients_all)}")

    # Top 15 most interesting non-flagship folios
    print("\nTop 15 most interesting (non-flagship):")
    ranked = sorted([e for e in catalogue if e["tier"] != "flagship"],
                    key=lambda x: -x["interest_score"])
    for e in ranked[:15]:
        print(f"  {e['folio']:8s} [{e['section']}] score={e['interest_score']:5.1f} "
              f"tier={e['tier']:8s} ingr={','.join(e['vocabulary']['ingredients'][:4])}")


if __name__ == "__main__":
    main()
