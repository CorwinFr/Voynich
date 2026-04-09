#!/usr/bin/env python3
"""
Generate folio_catalogue.json from VOYNICH_DECODE_V12_INGREDIENTS.txt.
For each folio: section, stats, probable content description, top vocabulary, confidence.
Also checks for matching page images in data/images/pages/.
"""
import re, json, os, glob, sys

DECODE_FILE = "d:/Github/Voynich/v12/output/VOYNICH_DECODE_V12_INGREDIENTS.txt"
IMAGES_DIR  = r"D:\Github\Voynich\data\images\pages"
OUTPUT_FILE = "d:/tmp/build_paper/folio_catalogue.json"

# Section descriptions
SECTION_DESC = {
    "H": "Herbal — Plant monograph with pharmaceutical properties",
    "S": "Pharmaceutical — Recipe-dense section (Antidotarium tradition)",
    "P": "Pharmaceutical (continued)",
    "B": "Balneological — Hydrotherapy (human figures in baths/pools)",
    "C": "Cosmological — Complex diagrams, volvelles, cosmological framework",
    "A": "Astronomical — Astrological and astronomical content",
    "Z": "Zodiac — Zodiac diagrams with star labels",
    "T": "Transitional — Title/boundary pages",
}

# Medical keyword groups for content inference
PHARMA_VERBS = {"coque", "coquas", "coquere", "recipe", "misce", "tere", "cola", "ciere"}
INGREDIENTS = {"aloe", "aloes", "ture", "sal", "olei", "oleo", "aceto", "cerae", "cera",
               "mel", "iecur", "succi", "sapa", "hiera", "cicura", "enula", "inula"}
BODY_PARTS = {"rens", "iecur", "ilia", "aquam"}
ASTRO_TERMS = {"crux", "aries", "aros", "luna", "sol"}
BATH_TERMS = {"aquam", "rens", "cura", "curas", "balneum"}

def _build_image_index():
    """Build a lookup from folio id (lowercase) to image filename."""
    idx = {}
    if not os.path.isdir(IMAGES_DIR):
        return idx
    for fname in os.listdir(IMAGES_DIR):
        if not fname.lower().endswith('.jpg'):
            continue
        # e.g. "003_1r.jpg" -> extract "1r"
        base = fname.rsplit('.', 1)[0]  # "003_1r"
        parts = base.split('_', 1)
        if len(parts) == 2:
            folio_part = parts[1].lower()  # "1r"
        else:
            folio_part = base.lower()
        idx[folio_part] = fname
    return idx

_IMAGE_INDEX = None

def find_image(folio_id):
    """Find matching page image for a folio."""
    global _IMAGE_INDEX
    if _IMAGE_INDEX is None:
        _IMAGE_INDEX = _build_image_index()

    fid = folio_id.lower()  # "F103R" -> "f103r"

    # Direct match (image keys are like "1r", "103r", "57v")
    if fid in _IMAGE_INDEX:
        return _IMAGE_INDEX[fid]

    # The decode file uses "F103R" but image index has "103r" (no f prefix)
    # So strip the leading 'f' if present
    fid_no_f = fid.lstrip('f')
    if fid_no_f in _IMAGE_INDEX:
        return _IMAGE_INDEX[fid_no_f]

    # Handle special cases like "85r_(part)_86v_(part)"
    for key, fname in _IMAGE_INDEX.items():
        if fid_no_f == key or fid_no_f in key:
            return fname

    return None

def infer_content(section, words_list, medical_pct, top_words):
    """Infer probable content based on section and decoded vocabulary."""
    tw = set(top_words)

    if section == "C":
        if "crux" in tw or "aros" in tw:
            return "Medico-astrological computation instrument (volvelle)"
        return "Cosmological diagram with pharmaceutical annotations"

    if section == "Z":
        return "Zodiac diagram with star/constellation labels (nomenclator-encoded)"

    if section == "T":
        return "Transitional page (title, boundary, or mixed content)"

    if section == "A":
        return "Astronomical/astrological diagram"

    pharma_count = sum(1 for w in words_list if w in PHARMA_VERBS)
    ingr_count = sum(1 for w in words_list if w in INGREDIENTS)

    if section in ("S", "P"):
        if pharma_count > 5 and ingr_count > 3:
            return "Compound recipe with multiple ingredients (Antidotarium tradition)"
        elif pharma_count > 3:
            return "Pharmaceutical preparation instructions"
        return "Pharmaceutical text (recipe section)"

    if section == "B":
        if pharma_count > 3:
            return "Hydrotherapy protocol with pharmaceutical preparations"
        return "Balneological treatise (bath therapy)"

    if section == "H":
        if ingr_count > 2:
            return "Plant monograph with preparation recipe"
        elif pharma_count > 2:
            return "Herbal entry with pharmaceutical instructions"
        elif medical_pct > 20:
            return "Plant monograph (high medical vocabulary)"
        return "Plant monograph with text description"

    return "Unclassified content"

def main():
    with open(DECODE_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Parse folios
    folio_pattern = re.compile(
        r'FOLIO (\S+) \| Section: (\S+)\s*\n={50,}\n(.*?)={50,}\s*\n\s*STATISTICS v12\n'
        r'\s*Total words: (\d+)\n'
        r'\s*CONFIRMED:\s*(\d+).*?\n'
        r'\s*HIGH:\s*(\d+).*?\n'
        r'\s*MEDIUM:\s*(\d+).*?\n'
        r'\s*LOW:\s*(\d+).*?\n'
        r'\s*OPAQUE:\s*(\d+).*?\n'
        r'\s*Perseus:\s*(\d+).*?\n'
        r'\s*Medical:\s*(\d+)',
        re.DOTALL
    )

    catalogue = []

    for m in folio_pattern.finditer(content):
        folio_id = m.group(1)
        section = m.group(2)
        text_block = m.group(3)
        total = int(m.group(4))
        confirmed = int(m.group(5))
        high = int(m.group(6))
        medium = int(m.group(7))
        low = int(m.group(8))
        opaque = int(m.group(9))
        perseus = int(m.group(10))
        medical = int(m.group(11))

        # Extract Latin words from LATIN: lines
        latin_words = []
        for line in text_block.split('\n'):
            if 'LATIN:' in line:
                parts = line.split('LATIN:')[1].strip()
                words = re.findall(r'[a-zA-Z]{2,}', parts)
                latin_words.extend(w.lower() for w in words)

        # Word frequency
        from collections import Counter
        word_freq = Counter(latin_words)
        top_10 = [w for w, _ in word_freq.most_common(10)]

        # Compute stats
        conf_high = confirmed + high
        conf_high_pct = round(100 * conf_high / total, 1) if total > 0 else 0
        perseus_pct = round(100 * perseus / total, 1) if total > 0 else 0
        medical_pct = round(100 * medical / total, 1) if total > 0 else 0

        # Confidence level
        if perseus_pct >= 90:
            confidence = "very_high"
        elif perseus_pct >= 80:
            confidence = "high"
        elif perseus_pct >= 65:
            confidence = "medium"
        else:
            confidence = "low"

        # Content inference
        probable_content = infer_content(section, latin_words, medical_pct, top_10)

        # Find image
        image = find_image(folio_id)

        entry = {
            "folio": folio_id,
            "section": section,
            "section_name": SECTION_DESC.get(section, "Unknown"),
            "words": total,
            "confidence": confidence,
            "stats": {
                "confirmed": confirmed,
                "high": high,
                "medium": medium,
                "low": low,
                "opaque": opaque,
                "conf_high_pct": conf_high_pct,
                "perseus_pct": perseus_pct,
                "medical_pct": medical_pct,
            },
            "probable_content": probable_content,
            "top_vocabulary": top_10,
            "image": image,
        }
        catalogue.append(entry)

    # Sort by folio order (already in order from file)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(catalogue, f, indent=2, ensure_ascii=False)

    print(f"Generated {len(catalogue)} folio entries -> {OUTPUT_FILE}")

    # Summary stats
    by_conf = Counter(e["confidence"] for e in catalogue)
    by_sec = Counter(e["section"] for e in catalogue)
    print(f"Confidence: {dict(by_conf)}")
    print(f"Sections:   {dict(by_sec)}")
    print(f"With image: {sum(1 for e in catalogue if e['image'])}/{len(catalogue)}")

if __name__ == "__main__":
    main()
