# Session 2 — Changelog v12

## Pipeline v12 : de 74% a 89% lisible

### Modifications de code

#### v12/pipeline.py
- **S2c DEAGGLUTINATION** (nouveau) — 13 prefixes dans `DEAGG_PREFIXES`. Strip le prefixe EVA, decode le reste, ajoute comme candidat.
- **Collision detection** — `decode_word()` recoit `prev_eva` + `prev_latin`. Si EVA different mais Latin identique → passe `collision_latin` au scorer.
- **decode_line()** — passe le contexte (prev_latin, prev_eva) entre les mots.
- **T-trigger ameliore** — score proportionnel a la frequence corpus (`5000 + freq*10` si atteste).

#### v12/stages/scorer.py
- **REECRIT** — Borda rank remplace par scoring direct calibre (importe de VSV12).
- 9 signaux : Perseus (+3000/+5000), Corpus (log*300), Morpho (+500), Fusion bonus (2000+log*400), Split penalty (-2000-et_discount), Monolithic priority (log*1200), Short fragment (-3000), Medical (+500), Collision (-8000).
- Confidence calibree : HIGH si Perseus+Corpus, MEDIUM si Perseus ou Corpus+Morpho.

#### v12/rules/logograms.json
- Ajoute `otedy` → "tere et" (confirmed, freq=514)
- Ajoute `oted` → "tere" (confirmed, freq=514)

### Analyses creees

| Script | Fonction |
|--------|----------|
| analysis/pattern_hunter.py | Patterns syntaxiques sur tout le manuscrit |
| analysis/plant_hunter.py | Noms de plantes dans les opaques |
| analysis/l_logogram.py | Analyse de contexte du `l` isole |
| analysis/prefix_mapper.py | Mapping prefixes EVA → racines latines |
| analysis/yt_dissector.py | IN+EL vs INULA (6 tests) |
| analysis/deagglutinator.py | Carte d'agglutination complete |
| analysis/clean_latin.py | Texte latin lisible |
| analysis/crib_lemmatized.py | Crib matching avec Collatinus |
| analysis/bfh_hunter.py | Recherche consonnes b/f/h |
| analysis/opaque_deep_dive.py | Analyse comprehensive des opaques |
| analysis/glyph_abbreviations.py | Glyphes isoles = abbreviations/chiffres |
| analysis/collatinus_validator.py | Validation LOW par Collatinus |

### Metriques comparees

| Metrique | Debut session | Fin session | Delta |
|----------|--------------|-------------|-------|
| Readable (CONF+HIGH) | 74% | **89%** | +15% |
| Perseus valid | 71% | **85%** | +14% |
| HIGH | 53% | **67%** | +14% |
| LOW | 17% | **7%** | -10% |
| OPAQUE | 1% | **1%** | = |
| Bigrams corpus | 793 | **1069** | +35% |
| Trigrams corpus | 84 | **214** | +155% |
| Quadrigrams | 1 | **19** | +1800% |

### Decouvertes

1. **Systeme d'agglutination** — Le scribe colle prepositions au mot suivant (18 prefixes identifies)
2. **yt- = IN + EL** (pas INULA sauf f33r avec illustration)
3. **h est muet** — confirme par logogramme or=hiera
4. **f(EVA) ≠ f(Latin), p(EVA) ≠ b(Latin)** — invalide par les donnees
5. **97% des LOW sont des artefacts K&A** — pas du latin invalide, le mapping lui-meme produit du non-latin
6. **Glyphes isoles = probablement des chiffres** — frequences decroissantes (Benford), adjacents sur f57v
7. **19 quadrigrammes** matchent le corpus medieval (best: "et coquus in aqua" 8x VMS / 5x corpus)

### Prochains chantiers

1. Reranker T5 avec LMs sectoriels (repetitions, type-token ratio)
2. Hypothese chiffres (f57v, glyphes isoles adjacents)
3. K&A valeurs minoritaires (les 8% restants)
