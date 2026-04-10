# Deep Research Prompt 6 : Complete Plant Identification for ALL 130 Herbal Folios

## Context

We are decoding the Voynich Manuscript (Beinecke MS 408, 1404-1438) as a pharmaceutical formulary. We have decoded 80% of its notation system and confirmed it matches patterns from the Antidotarium Nicolai (Salernitan pharmaceutical tradition).

Each herbal page contains ONE plant illustration with preparation instructions. The plant drawings are NOT purely naturalistic — the scribe was a pharmacist, not a botanist. He drew plants to show their PHARMACEUTICAL FUNCTION, not their exact botanical appearance. This means:

- **Exaggerated roots** may indicate the ROOT is the medicinal part (not that the plant has giant roots)
- **Blue or colored leaves** may indicate the plant's Galenic QUALITY (cold=blue, hot=red) not its real color
- **Flowers with unusual shapes** may represent the plant's PREPARATION form (distilled=drops, ground=powder shapes)
- **Multiple plants on one page** may show the plant at different STAGES of preparation
- **Strange "fantasy" features** are likely FUNCTIONAL annotations: a plant shown with water around it = aquatic preparation, a plant with fire-like features = needs to be heated

Previous researchers (Edith Sherwood, Stephen Bax, Dana Scott) have identified many plants but sometimes struggled with the "unrealistic" drawings. Their identifications should be treated as starting points, not certainties.

## What we need

For EVERY herbal folio in the Voynich Manuscript (f1v through f96v), we need:

1. **The best botanical identification** (Latin name + common name)
2. **The confidence level** (HIGH = multiple researchers agree, MEDIUM = one researcher with good evidence, LOW = disputed or uncertain)
3. **The medieval pharmaceutical name** (how this plant was called in Latin pharmacy: e.g., "Rosmarinus" in botanical Latin but "Anthos" in some medieval pharmacies)
4. **The primary pharmaceutical preparation** according to the Circa Instans or Antidotarium Nicolai (oil, water/decoction, powder, juice, syrup, ointment)
5. **The Galenic qualities** (hot/cold degree 1-4, wet/dry degree 1-4)

## Specific folios where identification is CRITICAL

These are the plants most frequently used in the recipe sections. Correct identification here directly unlocks recipe reading:

| Folio | Recipes | Current ID (Sherwood) | Problem |
|-------|---------|----------------------|---------|
| **f10v** | 868x | Linnaea borealis (twinflower) | UNLIKELY — twinflower has no medieval pharma use. This is the MOST USED plant in the entire manuscript. It must be something fundamental: rosa? piper? cinnamomum? |
| **f33v** | 469x | Tanacetum parthenium (feverfew) | Plausible but needs confirmation. Is the illustration really feverfew? |
| **f24r** | 203x | Cucumis sativus (cucumber) | Possible but 203 recipe references seems high for cucumber alone |
| **f94v** | 145x | Agrostemma githago (corncockle) | UNLIKELY — corncockle is toxic and rarely used medicinally |
| **f41r** | 117x | Origanum vulgare (marjoram) | Good match — marjoram is a major pharmaceutical herb |
| **f39v** | 42x | Unidentified | Needs identification |
| **f44v** | 23x | Apium graveolens (celery) | Good — "radices apii" appears in the Antidotarium |
| **f38r** | 7x | Unidentified by Sherwood | Needs identification |
| **f42r** | (herbal) | Unidentified by Sherwood | Needs identification — different from f42v (Aquilegia) |

## Known researchers and their work

Please cross-reference these sources:

1. **Edith Sherwood** (edithsherwood.com/voynich_botanical_plants/) — 124/126 plants identified, Mediterranean focus, Italian manuscript hypothesis
2. **Stephen Bax** (stephenbax.net) — partial decoding, identified Centaurea, Nigella, Hellebore, Coriander, Juniper via text analysis
3. **Dana Scott** (voynichbotany.wordpress.com) — independent identifications, sometimes differs from Sherwood
4. **Jules Janick** (Flora of the Voynich Codex, Springer 2019) — New World plant hypothesis (controversial)
5. **nightrad.io** ("Not solvable" + "Plants" documents) — Arabic/Syriac identification attempt using Ibn Sina and al-Biruni references. Mapped plants to Iraqi/Mesopotamian species. While the Arabic language hypothesis was refuted by our analysis, the VISUAL plant identifications may still be valid.
6. **Alain Touwaide** (Institute for the Preservation of Medical Traditions) — expert in medieval botanical illustration, confirmed many illustrations match 14th-15th century herbal style
7. **Tucker & Talbert** (2013) — identified plants as New World species (controversial)

## Important: the pharmacist's drawing style

The scribe was NOT drawing for a botanical encyclopedia. He was drawing for HIMSELF as a working pharmacist. Key drawing conventions to consider:

- **The root shape** may indicate the PREPARATION method:
  - Long thin roots = decoction (boiled in water)
  - Bulbous roots = the root IS the medicine
  - No visible roots = the aerial parts (leaves, flowers) are used
  
- **Leaf patterns** may encode Galenic QUALITIES:
  - Rounded leaves = "cool" quality (degree 1-2)
  - Pointed/serrated leaves = "hot" quality
  - Thick fleshy leaves = "moist"
  - Thin dry leaves = "dry"

- **Flower representations** may not be botanically accurate but FUNCTIONALLY meaningful:
  - A flower drawn larger than natural = the flower IS the medicinal part
  - Multiple small flowers = the plant is used in compound preparations
  - Unusual colors = Galenic quality indicators, not real colors

- **"Fantasy" or "impossible" plants** are NOT evidence of a hoax. They are a pharmacist's shorthand combining:
  - The plant's appearance (approximate)
  - Its medicinal properties (visual coding)
  - Its preparation method (root/leaf/flower emphasis)
  
  A similar phenomenon exists in medieval herbals where plants are drawn with exaggerated features to aid identification of the medicinally important parts.

## Geographic constraints

The manuscript is carbon-dated to 1404-1438. The writing system has Tironian connections (z=9.4) and the zodiac month names are in Occitan/Provençal. This suggests:

- **Northern Italy / Southern France** origin (Padua, Venice, Provence)
- Plants should be native to or cultivated in the Mediterranean region
- Some exotic imports are expected (cinnamon, pepper, saffron, ginger) as these were standard in medieval pharmacy
- New World plants (sunflower, chili pepper) are EXCLUDED by the carbon dating

## Output format

For each folio, provide:

```
Folio: f__
Sherwood ID: [name]
Bax ID: [name if different]
Scott ID: [name if different]
nightrad ID: [name if available]
BEST ID: [your consensus]
Confidence: HIGH/MEDIUM/LOW
Medieval pharma name: [Latin]
Primary preparation: oil / water / powder / juice / syrup / ointment
Galenic quality: hot/cold degree X, wet/dry degree Y
Circa Instans entry: [yes/no, brief description]
Notes: [any special observations]
```

For the 9 critical folios listed above (f10v, f33v, f24r, f94v, f41r, f39v, f44v, f38r, f42r), provide DETAILED analysis with multiple candidates ranked by plausibility, considering:
- Visual features of the illustration
- Frequency of use in our decoded recipes
- Medieval pharmaceutical importance
- Geographic compatibility (Mediterranean)
- Consistency with the preparation suffix we decoded for that folio's label
