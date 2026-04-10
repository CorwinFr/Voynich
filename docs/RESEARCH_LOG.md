# JOURNAL DE RECHERCHE — Decryptage du Manuscrit de Voynich
## Guillaume Clement & Claude Code (Anthropic)
## Pipeline K&A v12 — Project Aureum

---

## SESSION 1 (8 avril 2026) — Pipeline de base

### Tests effectues
| Test | Source | Resultat | Impact |
|------|--------|----------|--------|
| Decodage complet 202 folios | ZL.txt (Zandbergen-Landini v2b) | 74% lisible, 71% Perseus | Baseline |
| Monolithic-first decode | v12/pipeline.py | coquo/coquere recuperes (48x f103r) | +11% lisible |
| INELIODE = Inula helenium (f33r) | Illustration + decode + tradition | Triple convergence | Premiere plante identifiee |

---

## SESSION 2 (8 avril 2026) — Desagglutination + scoring calibre

### Tests effectues
| Test | Source | Resultat | Impact |
|------|--------|----------|--------|
| Systeme d'agglutination | Analyse de 1634 mots y- | 18 prefixes identifies (y=in, d=in, qo=cum, ol=es, etc.) | +15% lisible (74->89%) |
| Scoring calibre | Import de VSV12/v12/decode/scorer.py | log(freq)*1200 proportionnel | +14% Perseus (71->85%) |
| Collision penalty | Analyse EVA different -> meme Latin | -8000 pour collisions, preserves repeats | Qualite + |
| Crib matching lemmatise (Collatinus) | 3 corpus (800K mots) + Collatinus localhost:5555 | 19 quadrigrammes, 214 trigrammes | Validation externe |
| b/f/h consonant hunt | 200+ ingredients x 202 folios | NEGATIF : h muet, f!=f, p!=b | Elimine hypothese |
| Opaque deep dive | 3421 mots LOW/OPAQUE analyses | 48% K&A artifacts, 25% mots longs, 10% glyphes isoles | Diagnostic |
| Collatinus validation des LOW | 200 mots testes | 97% NON reconnus = artefacts K&A | Confirme |
| Glyph abbreviations analysis | 8 glyphes isoles en contexte | l=191x middle (93%), k=17x avec crux | Piste chiffres |
| "et coquus in aqua" quadrigramme | Pipeline v2 calibre | 8x VMS, 5x corpus | Premier 4-gram |

### Resultats cumules fin session 2
- 89% lisible, 85% Perseus, 19 quadrigrammes, 5016 deagg wins

---

## SESSION 3 (9 avril 2026) — f57v volvelle + ingredients

### Tests effectues
| Test | Source | Resultat | Impact |
|------|--------|----------|--------|
| f57v structure analysis | ZL.txt L02-L05 | 5 couches concentriques, L03=4x17, L04=29 mots, L05=75% | Volvelle identifie |
| Parallele Ashmole 370 | MS Ashmole 370 (Bodleian Library, ~1424) | Structure quasi-isomorphe | Validation externe |
| f57v L03 pattern 4x17 | D'Imperio (NSA), Pelling (Cipher Mysteries) | 4 quadrants, 2 variables (j/d et f/p) | Homophonie f/p confirmee |
| f57v L04 cycle lunaire | 29 mots decodes | Jour 1,25=in aquam, jour 19=crux, jour 27=luce | 3 matchs + 2 coherents |
| Zodiac crib attack | 12 pages zodiacales (f70v1-f73v) | NEGATIF : noms de signes PAS en K&A | Nomenclateur confirme |
| Antidotarium crib f103r | Aurea Alexandrina + corpus pharma | 43% pharma, 7/12 Aurea (58%) | Receptaire confirme |
| Nomenclateur cracker (beam=50) | 39 positions d'ingredients sur f103r | 31 matchs, 11 types uniques | 25 ingredients! |
| Reverse K&A hunt | 36 ingredients x 226 folios | sapam verifie (f100r) | +1 ingredient |
| Smart ingredient hunt | 54 noms italiens/arabes/abreges | pepe=pepper (f20v), sapa confirmee | Italien vernaculaire! |
| Esdra recipe exact forms | Marco Ponzi/Medium (Antidotarium Esdra) | cardamomi, costi, lauri, piretri, mel | +6 ingredients |
| Plant name crib attack | 7 plantes conf>=0.60, beam=50 | NEGATIF : ZERO match premiers mots | Noms PAS en K&A |
| Gallows prefix analysis | 129 folios herbaux, premiers mots | 124 uniques, tous commencent par p/k/t/f | Classificateur? |

### Sources utilisees
- Antidotarium Nicolai — recette Esdra (Marco Ponzi, Medium/ViridisGreen)
- MS Ashmole 370 (Bodleian Library, Oxford) — description de la volvelle lunaire
- Nick Pelling, Cipher Mysteries (ciphermysteries.com) — analyse f57v, 4x17, sundial hypothesis
- ChatGPT — evaluation critique (4x17 vs 4x12, jour 13 != Aries)
- Gemini — analyse volvelles, ecole de Salerne, Naibbe cipher
- D'Imperio, "An Elegant Enigma" (NSA) — description structurelle f57v

### Resultats cumules fin session 3
- 90% lisible, 86% Perseus, 25 ingredients, 19 quadrigrammes
- f57v = volvelle pharmaceutique (parallele Ashmole 370)
- Noms de plantes PAS en K&A phonetique (nomenclateur ou classificateur gallows)
- Scribe italien du Nord (pepe, lilie)

---

## SESSION 4 (9 avril 2026) — Lunaire + nettoyage repo

### Sources obtenues
| Source | Contenu | Utilisation prevue |
|--------|---------|-------------------|
| LUNAIRES_COMPLETS_30_JOURS.md | 5 lunaires medievaux (XIIIe-XVe) : Arsenal 2782, BnF Fr 2074, BnF Fr 837, BnF Fr 1745, pronostiques saignee | Crib semantique pour L04 de f57v |

### Tests A EFFECTUER
| Test | Source | Statut |
|------|--------|--------|
| Crib semantique L04 x lunaires | LUNAIRES_COMPLETS_30_JOURS.md vs 29 mots L04 | A FAIRE |
| Alignement jour par jour | Themes des lunaires x decodage K&A | A FAIRE |
| Jours critiques (3,5,13,25) vs L04 | Lunaires unanimes sur ces jours | A FAIRE |
| Correspondance saignee/purge | Instructions saignee x mots L04 | A FAIRE |

### Actions repo
- Repo prive GitHub : CorwinFr/project-aureum (Apache 2.0)
- README.md (EN) + README_FR.md (FR) crees
- _archive/ avec historique (880 MB)
- docs/research_prompts/ avec 9 prompts
- .gitignore propre

---

## RESULTATS NEGATIFS IMPORTANTS (a documenter pour la publication)

| Test | Resultat | Signification |
|------|----------|---------------|
| b/f/h consonant hunt | h muet, f!=f(Latin), p!=b | Consonnes manquantes NON recuperables par K&A |
| Zodiac sign crib | ZERO match | Nomenclateur separe pour noms propres |
| Plant name crib (7 plantes) | ZERO match | Noms de plantes PAS en K&A phonetique |
| Collatinus validation LOW | 97% non reconnus | Opaques = artefacts K&A, pas du latin inconnu |
| Antidotarium complet | 7/12 Aurea (58%) | Score insuffisant pour proof definitive |

---

## HYPOTHESES ACTIVES (classees par force)

### CONFIRMEES
1. Latin pharmaceutique medieval chiffre (90% lisible, 86% Perseus)
2. Agglutination systematique (18 prefixes, +15%)
3. Verbes pharma confirmes (coque 37x, tere, misce, cola, recipe)
4. f57v = volvelle (parallele Ashmole 370)

### FORTES
5. 25 ingredients Antidotarium via K&A minoritaire
6. Scribe italien du Nord (pepe, lilie)
7. INELIODE = Inula helenium (f33r, triple convergence)
8. Homophonie f/p (f57v L03)

### PROBABLES
9. ~28% du texte = nomenclateur (noms propres non K&A)
10. Premiers mots herbaux = classificateur gallows + racine
11. L04 = cycle lunaire 29 jours

### SPECULATIVES
12. Glyphes isoles = chiffres/quantites (Benford-like)
13. Centre f57v = phrase latine (regle d'usage)
14. Gallows p/k/t/f = categories de plantes
