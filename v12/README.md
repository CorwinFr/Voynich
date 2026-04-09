# Voynich Manuscript Decoder — Pipeline K&A v12

## Overview

Algorithmic decoding of the Voynich Manuscript (Beinecke MS 408) based on the King & Andrisani (K&A) phonetic mapping hypothesis. The manuscript is interpreted as medieval Latin pharmaceutical text protected by a homophonic substitution cipher with agglutination.

**Authors**: Guillaume Clement & Claude (Anthropic)
**Date**: April 2026
**Pipeline version**: v12 (monolithic-first + deagglutination + ingredient-aware)

## Results

| Metric | Value |
|--------|-------|
| Total words decoded | 38,442 |
| Folios processed | 202 |
| Readable (CONFIRMED+HIGH) | ~89% |
| Perseus Latin valid | ~85% |
| Ingredients identified | 25 |
| Corpus quadrigram matches | 19 |
| Corpus trigram matches | 214 |

## Key Discoveries

### 1. Agglutination System (18 prefixes)
The scribe glues Latin prepositions to the following word as a single EVA token:
- `y` = IN, `d` = IN, `da` = IN A, `qo` = CUM, `ol`/`l` = ES/EX
- `t` = EL, `r` = RE, `p` = PER, `f` = PAR
- 5,016 words improved by deagglutination (13% of manuscript)

### 2. Ingredient Discovery (25 ingredients)
Pharmaceutical ingredients are encoded using K&A minority values. The Antidotarium Nicolai serves as the "codebook" — the reader needs professional pharmaceutical knowledge to recognize ingredient names.

| Ingredient | Latin | EVA | Method |
|-----------|-------|-----|--------|
| Aloe | aloe/aloes | oteey/oteeal | K&A minority |
| Incense | ture/turis | otar/otaiin | K&A minority |
| Salt | sal | loty | K&A minority |
| Oil | olei/oleo | otchy/cheoty | K&A minority |
| Vinegar | aceto | qotey | K&A minority |
| Asarum | asari | chorol | K&A minority |
| Wax | cera/cerae | koraiin | K&A minority |
| Pepper | pepe (Italian!) | pofochey | Italian vernacular |
| Cardamom | cardamomi | kardy | Esdra recipe form |
| Laurel | lauri | toar | Esdra recipe form |
| Costus | costi | kees | Esdra recipe form |
| Pyrethrum | piretri | pchroiin | Esdra recipe form |
| Honey | mel | mol | Direct search |
| Lily | lilie (Italian) | tchtcho | Italian vernacular |
| Must syrup | sapa/sapam | sofam | Reverse K&A |

### 3. f57v = Pharmaceutical Volvelle
Folio 57v is a medical-astrological calculating device (volvelle), parallel to MS Ashmole 370 (Bodleian Library, ~1424):
- L02 (outer ring, 54 words): calendar/zodiac labels
- L03 (middle ring, 4x17 glyphs): cipher key / quadrant markers
- L04 (29 words): lunar synodic cycle (29.5 days)
- L05 (inner ring, 75% circle): 18-hour sundial

### 4. First Quadrigram Match
"et coquus in aqua" (and cook in water) — matches 8 times in the Voynich, 5 times in medieval pharmaceutical corpus.

### 5. INELIODE = Inula helenium
On f33r, the decoded word "ineliode" matches the plant Inula helenium (Elecampane), confirmed by triple convergence: text + botanical illustration + medical tradition.

## Architecture

```
v12/
  __main__.py          # CLI entry point (--folio, --word, --all-folios)
  config.py            # Configuration loader
  pipeline.py          # Main orchestrator (S0-S4 + S2c deagg + S2d ingredients)
  folio_reader.py      # High-level folio reader with stats
  translate.py         # Latin -> English basic translation

  stages/
    tokenizer.py       # EVA tokenizer (greedy left-to-right)
    logogram.py        # Logogram/exception resolver (105+ entries)
    hmm_decoder.py     # HMM Viterbi decoder (3 states, beam search)
    scorer.py          # Calibrated 9-signal scorer
    reranker.py        # T5 sectorial reranker (raw-form LMs)

  models/
    hmm.py             # GlyphHMM model (context-conditioned emissions)
    lattice.py         # Segmentation lattice DAG
    sectorial_lm.py    # Sectorial LM builder (Collatinus)
    lm_herbal.json     # Lemmatized herbal LM
    lm_pharma.json     # Lemmatized pharma LM
    lm_balnea.json     # Lemmatized balnea LM
    lm_*_raw.json      # Raw-form bigram LMs (no Collatinus)

  loaders/
    corpus.py          # Corpus frequency model
    dictionary.py      # Perseus Latin dictionary + vulgar forms
    transcription.py   # ZL.txt parser (IVTFF format)

  rules/
    glyphs.json        # K&A glyph -> phoneme mappings
    logograms.json      # 105+ whole-word logogram mappings
    prefixes.json       # Tier 1/2 agglutination prefixes
    suffixes.json       # Suffix rules (-dy, -ol, -al)
    confirmed_roots.json # Confirmed root mappings

  validation/
    morphology.py      # Latin morphological validation
    entropy.py         # Entropy calculation (H1, H2)

  registry/
    audit.py           # Audit trail for decoded words

  analysis/            # Research scripts (not part of pipeline)
    antidotarium_crib.py
    bfh_hunter.py
    clean_latin.py
    collatinus_validator.py
    crib_lemmatized.py
    deagglutinator.py
    f57v_rosetta.py
    glyph_abbreviations.py
    l_logogram.py
    nomenclateur_cracker.py
    opaque_deep_dive.py
    pattern_hunter.py
    plant_hunter.py
    prefix_mapper.py
    reverse_ka_hunt.py
    sentinel_words.py
    smart_ingredient_hunt.py
    yt_dissector.py
    zodiac_crib_attack.py

  output/              # Generated reports and decoded text
```

## Usage

```bash
# Decode single word
python -m v12 --word daiin

# Decode single folio
python -m v12 --folio f103r

# Decode all folios
python -m v12 --all-folios > output/decode.txt

# Without English translation (faster)
python -m v12 --all-folios --no-english > output/decode.txt
```

## Dependencies

- Python 3.12+
- Collatinus daemon on localhost:5555 (for lemmatization, optional)
- Data files: ZL.txt (Zandbergen-Landini transcription), Perseus dictionary, corpus files

## Data Sources

- **ZL.txt**: Zandbergen-Landini v2b EVA transcription (IVTFF format)
- **Perseus**: 84,937 Latin forms (classical + medieval)
- **Corpus**: 800K words from medieval pharmaceutical texts
  - CORPORA_FINAL/corpus_herbal.txt (178K words)
  - CORPORA_FINAL/corpus_pharma.txt (426K words)
  - CORPORA_FINAL/corpus_balnea.txt (195K words)
- **Antidotarium Nicolai**: ~150 recipes, ~200 ingredients
- **Collatinus**: Latin lemmatizer (localhost:5555)
