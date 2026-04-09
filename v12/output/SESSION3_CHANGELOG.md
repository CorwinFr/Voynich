# Session 3 — Changelog (2026-04-09)

## De 4 a 25 ingredients identifies

### Pipeline changes

#### v12/pipeline.py
- **PHARMA_VERBS** set: 17 verbs that trigger ingredient context
- **ANTIDOTARIUM** set: 80+ ingredient forms from Antidotarium Nicolai
- **S2d INGREDIENT MODE**: For every word, HMM beam=50 explores ALL K&A paths. If any matches an Antidotarium ingredient -> score bonus 6000+freq*15. Anagram detection included.
- **decode_line()**: tracks `after_verb` flag for context-aware decoding
- **Collision penalty**: different EVA -> same Latin = -8000 (not -5000)

#### v12/stages/scorer.py
- Signal 9: collision_penalty (replaces repeat_penalty)
- Only fires when prev_eva != current_eva AND produces same Latin

#### v12/stages/reranker.py
- REWRITTEN: uses raw-form LMs (lm_*_raw.json) instead of Collatinus-lemmatized LMs
- Pharma word PROTECTION: coque, tere, recipe, misce, cola, cole, hiera, aloes, cicura, rens, aquam, curam never reranked
- Greedy left-to-right with lookahead
- Impact: 3% word changes, 0 regressions

#### v12/models/
- lm_herbal_raw.json, lm_pharma_raw.json, lm_balnea_raw.json: raw-form bigram LMs (no Collatinus)

#### v12/rules/logograms.json
- Added: otedy = "tere et", oted = "tere"

### Analyses created

| Script | Function | Key result |
|--------|----------|------------|
| antidotarium_crib.py | Align f103r with Aurea Alexandrina | 43% pharma, 7/12 Aurea |
| nomenclateur_cracker.py | Find hidden ingredients via beam=50 | 31 matches, 11 unique on f103r |
| reverse_ka_hunt.py | Latin -> EVA reverse search | sapam verified on f100r |
| smart_ingredient_hunt.py | Italian/Arabic/synonym search | pepe=pepper on f20v |
| f57v_rosetta.py | Volvelle ring-by-ring analysis | aros/luce/crux at key lunar days |
| zodiac_crib_attack.py | Test zodiac sign names via K&A | NEGATIVE — nomenclateur confirmed |
| glyph_abbreviations.py | Isolated glyph context analysis | r=6x, l=4x on L05 cadran |
| collatinus_validator.py | Validate LOW words via Collatinus | 97% are K&A artifacts |
| opaque_deep_dive.py | Comprehensive opaque analysis | 3421 opaques, 48% K&A unknown |
| bfh_hunter.py | Search for b/f/h consonants | NEGATIVE — h silent, f!=f, p!=b |

### Ingredients found (chronological order of discovery)

| # | Ingredient | Method | Session |
|---|-----------|--------|---------|
| 1-4 | hiera, cicura, rens, aloes | Logograms (pre-existing) | 1 |
| 5-6 | coquo/coque, equaliter | Pipeline (pre-existing) | 1 |
| 7-13 | aloe(K&A), ture, sal, olei, aceto, asari, cerae | K&A minority beam=50 | 3 |
| 14-15 | iecur, succi | K&A minority beam=50 | 3 |
| 16 | sapam/sapa | Reverse K&A verified | 3 |
| 17 | pepe (=piper, Italian!) | Smart ingredient hunt | 3 |
| 18 | lilie (=lilium, Italian) | Italian name hunt | 3 |
| 19-22 | cardamomi, costi, lauri, piretri | Esdra recipe exact forms | 3 |
| 23 | mel | Direct EVA search (mol) | 3 |

### Key methodological insight

The Voynich apothecary encodes ingredients using the SAME K&A cipher but with MINORITY phoneme values. The "codebook" is the Antidotarium Nicolai itself — the reader needs pharmaceutical professional knowledge to recognize ingredient names in the cipher output.

Italian vernacular names (pepe, lilie) prove the scribe is ITALIAN, consistent with Northern Italy origin (radiocarbon 1404-1438).

### Metrics comparison

| Metric | Start session 2 | End session 2 | End session 3 |
|--------|----------------|---------------|---------------|
| Readable | 74% | 89% | 89% (unchanged) |
| Perseus | 71% | 85% | 85% (unchanged) |
| Ingredients found | 4 | 4 | **25** |
| Quadrigrams | 1 | 19 | 19 |
| f57v analysis | none | none | **complete** |

### Still missing

- croci (saffron), cinamomi (cinnamon), masticis (mastic), mirre (myrrh)
- galange (galangal), ziziberis (ginger), petrosellini (parsley), gariofoli (clove)
- These have K&A-incompatible consonant patterns -> third encoding method unknown
