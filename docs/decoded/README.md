# Voynich Manuscript — Decoded Latin Text (v12)

**Pipeline**: K&A v12 (King-Andrisani transliteration + agglutinative segmentation + Perseus validation)  
**Date**: April 2026  
**Authors**: Guillaume Clement & Claude (Anthropic, Opus 4.6)

## Files

| File | Description | Size |
|------|-------------|------|
| `VOYNICH_LATIN_CLEAN.txt` | Clean readable Latin text (CONFIRMED + HIGH confidence only). 226 folio sides. | 5,724 lines |
| `VOYNICH_DECODE_V12_INGREDIENTS.txt` | Full decode with EVA + Latin side-by-side, per-folio statistics, confidence grades. | 19,959 lines |
| `folio_catalogue_enriched.json` | Per-folio catalogue: section, stats, description, ingredients, tier, image URLs. 226 entries. | JSON |

## Statistics

| Metric | Value |
|--------|-------|
| Total words decoded | 38,442 |
| Folio sides | 226 |
| Perseus validation | 89.3% |
| CONFIRMED + HIGH confidence | 90.6% |
| Pharmaceutical terms identified | 33 |
| Shannon entropy H1 | ~3.65 bits (ref: Latin ~4.0, EVA ~2.1) |

## How to Read the Decoded Text

`VOYNICH_LATIN_CLEAN.txt` contains only high-confidence decoded words. Words marked `...` are OPAQUE (undecoded). The text is organized by folio with section markers:

```
--- F103R ---
  ... cio olei ... eius et iqui hiera cerae aquam ... el cura ture eius ...
  in eius et cum ede et ede et coque aeque eius dare es sal eius ...
```

Key pharmaceutical vocabulary:
- **coque/coquere** = cook/boil
- **recipe** = take (Rx)
- **misce** = mix
- **tere** = grind
- **cola** = strain
- **ciere** = stir
- **equaliter** = equal parts (ana)
- **hiera** = compound sacred remedy
- **aquam** = water
- **olei** = oil
- **aloe/aloes** = aloe
- **ture** = frankincense
- **sal** = salt

## Image Sources

Page images are from the **Beinecke Rare Book and Manuscript Library, Yale University** (MS 408).  
Available via IIIF: `https://collections.library.yale.edu/catalog/2002046`  
See `data/images/urls.txt` for individual page IIIF URLs.

The manuscript is considered to be in the **public domain** (created 1404-1438).  
Yale provides digital images under their [Terms of Use](https://web.library.yale.edu/digital-collections/terms-use).

## License

The decoded text and pipeline code are released under the same license as the parent project.  
The EVA transcription is by Zandbergen & Landini (1998), publicly available.
