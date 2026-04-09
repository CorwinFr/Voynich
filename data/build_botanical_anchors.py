#!/usr/bin/env python3
"""Build botanical_anchors.json by merging botanical IDs, medieval Latin names, and EVA words."""

import csv
import json
import re
from pathlib import Path

DATA = Path(__file__).parent

# --- 1. Load botanical identifications ---
identifications = {}
with open(DATA / "botanical_identifications.tsv", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter="\t")
    for row in reader:
        folio = row["folio"].strip()
        if folio not in identifications:
            identifications[folio] = []
        identifications[folio].append({
            "species": row["proposed_species"].strip(),
            "common_name": row["common_name"].strip(),
            "proposer": row["proposer"].strip(),
            "confidence": row["confidence"].strip(),
            "notes": row["notes"].strip(),
            "section": row["section"].strip(),
        })

# --- 2. Load medieval Latin names ---
medieval_names = {}
with open(DATA / "medieval_latin_plant_names.tsv", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter="\t")
    for row in reader:
        binomial = row["modern_binomial"].strip()
        # Map each species (and variants) to medieval name(s)
        for sp in re.split(r"\s*/\s*", binomial):
            sp_clean = sp.strip()
            # Also store genus-only key
            genus = sp_clean.split()[0] if sp_clean else ""
            medieval_names[sp_clean.lower()] = {
                "medieval_latin": row["medieval_latin_name(s)"].strip(),
                "source_texts": row["source_texts"].strip(),
            }
            if genus:
                medieval_names[genus.lower()] = {
                    "medieval_latin": row["medieval_latin_name(s)"].strip(),
                    "source_texts": row["source_texts"].strip(),
                }

# --- 3. Load EVA words per folio ---
with open(DATA / "herbal_folio_words.json", encoding="utf-8") as f:
    eva_data = json.load(f)

# --- 4. Confidence scoring ---
def score_confidence(conf_str, n_proposers):
    """Convert string confidence to a numeric score 0-1."""
    base = {
        "high": 0.85,
        "medium-high": 0.75,
        "medium": 0.60,
        "low-medium": 0.40,
        "low": 0.20,
    }
    return base.get(conf_str, 0.30)

def find_medieval_name(species):
    """Look up medieval Latin name(s) for a species."""
    sp_lower = species.lower()
    # Try exact match
    if sp_lower in medieval_names:
        return medieval_names[sp_lower]
    # Try genus only
    genus = sp_lower.split()[0] if sp_lower else ""
    if genus in medieval_names:
        return medieval_names[genus]
    # Try parenthetical removal
    clean = re.sub(r"\s*\(.*?\)\s*", " ", sp_lower).strip()
    if clean in medieval_names:
        return medieval_names[clean]
    genus2 = clean.split()[0]
    if genus2 in medieval_names:
        return medieval_names[genus2]
    return None

# --- 5. Build anchors: select best identification per folio ---
anchors = []

for folio, ids in sorted(identifications.items()):
    # Group by genus to find consensus
    genus_groups = {}
    for ident in ids:
        genus = ident["species"].split()[0] if ident["species"] else "unknown"
        if genus not in genus_groups:
            genus_groups[genus] = []
        genus_groups[genus].append(ident)

    # Pick the best identification (highest confidence, most proposers)
    best = None
    best_score = -1
    alternatives = []

    for genus, group in genus_groups.items():
        # Use the entry with highest confidence
        for ident in group:
            n_proposers = len([p.strip() for p in ident["proposer"].split(";")])
            s = score_confidence(ident["confidence"], n_proposers)
            # Bonus for multiple proposers
            s += 0.05 * (n_proposers - 1)
            if s > best_score:
                if best:
                    alternatives.append(best)
                best = ident
                best_score = s
            else:
                alternatives.append(ident)

    if not best:
        continue

    # Only include entries with at least low-medium confidence
    if best_score < 0.35:
        continue

    # Look up medieval Latin name
    med = find_medieval_name(best["species"])

    # Get EVA words
    eva = eva_data.get(folio, {})

    # Build candidate EVA words list (hapax confirmed + distinctive)
    candidate_eva = []
    if eva:
        confirmed = eva.get("hapax_confirmed_takahashi", [])
        distinctive = eva.get("distinctive_2_3_folios", [])
        candidate_eva = confirmed[:8] + distinctive[:5]

    entry = {
        "folio": folio,
        "section": best["section"],
        "proposed_species": best["species"],
        "common_name": best["common_name"],
        "proposers": best["proposer"],
        "confidence_label": best["confidence"],
        "confidence_score": round(best_score, 2),
        "medieval_latin_name": med["medieval_latin"] if med else None,
        "medieval_source_texts": med["source_texts"] if med else None,
        "notes": best["notes"],
        "alternative_ids": [
            {"species": a["species"], "proposer": a["proposer"], "confidence": a["confidence"]}
            for a in alternatives
        ] if alternatives else [],
        "eva_candidate_words": candidate_eva if candidate_eva else None,
        "eva_hapax_count": eva.get("hapax", None) and len(eva["hapax"]),
        "eva_total_unique_words": eva.get("unique_words", None),
    }
    anchors.append(entry)

# Sort by confidence score descending
anchors.sort(key=lambda x: (-x["confidence_score"], x["folio"]))

# --- 6. Write output ---
output = {
    "metadata": {
        "description": "Botanical identifications for Voynich Manuscript herbal folios",
        "sources": [
            "Tucker & Talbert (2013) - New World identifications",
            "Tucker & Janick (2018) - Flora of the Voynich Codex (Springer)",
            "Edith Sherwood - European/Mediterranean identifications",
            "Dana Scott - Independent identifications",
            "Stephen Bax - Linguistic decoding + morphology",
            "Steve D - Gap-filling identifications",
            "Ethel Voynich / O'Neill (1944) / Petersen - Earliest identifications",
            "René Zandbergen (voynich.nu) - Compilation",
            "Sergio Toresella - Alchemical herbal tradition",
        ],
        "medieval_name_sources": [
            "Circa instans (Matthaeus Platearius, 12th c. Salerno)",
            "Pseudo-Apuleius Herbarium (Howald-Sigerist edition)",
            "Macer Floridus / De viribus herbarum",
            "Dioscorides De Materia Medica (Latin translations)",
        ],
        "eva_transcription": "Zandbergen-Landini (ZL), cross-referenced with Takahashi (;H lines in LSI)",
        "total_entries": 0,  # filled below
        "confidence_scoring": {
            "high": "0.85+ — Multiple independent researchers agree, distinctive morphology",
            "medium-high": "0.75-0.84 — Two+ researchers agree with strong evidence",
            "medium": "0.60-0.74 — Two researchers agree or one strong morphological match",
            "low-medium": "0.40-0.59 — Single well-argued identification",
            "low": "<0.40 — Single proposer, controversial, or weak evidence (excluded)",
        },
    },
    "anchors": anchors,
}
output["metadata"]["total_entries"] = len(anchors)

with open(DATA / "botanical_anchors.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"Written {len(anchors)} entries to botanical_anchors.json")
print(f"Top 10 by confidence:")
for a in anchors[:10]:
    print(f"  {a['folio']:6s} {a['confidence_score']:.2f} {a['proposed_species']:30s} medieval: {a['medieval_latin_name'] or '—'}")
