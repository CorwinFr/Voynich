# PLAN D'ACTIONS COMPLET — Decryptage du Manuscrit de Voynich MS 408
## Pipeline v12 — Guillaume Clement & Claude Anthropic
## Date: 2026-04-08

---

# ETAT ACTUEL

| Metrique | Valeur |
|----------|--------|
| Mots totaux | 38 442 |
| Lisible (CONF+HIGH) | **89%** (34 533 mots) |
| Perseus valide | **85%** (32 800 mots) |
| Opaques (LOW+OPAQUE) | **8%** (3 421 mots) |
| Quadrigrammes corpus | **19** |
| Trigrammes corpus | **214** |
| Bigrammes corpus | **1 069** |

---

# AXE 1 — AMELIORATION DU PIPELINE (Qualite du decode)

## 1.1 Reranker T5 avec LMs sectoriels
**Impact**: Casser les repetitions, ameliorer le type-token ratio (0.154 -> 0.20+)
**Effort**: 2h
**Source**: VSV12/v12/decode/reranker.py + language_model.py
**Methode**:
- Beam search (width=20, top_k=3 par mot)
- 3 LMs sectoriels (herbal/pharma/balnea) deja construits
- Poids: T4=0.3, LM=0.5, morpho=0.2
- Le bigram "coquere coquere" sera naturellement penalise
**Fichiers**: v12/stages/reranker.py (nouveau), v12/folio_reader.py (modifier)
**Test**: Comparer f77r L42 avant/apres (le cas "cum ede et" x4)

## 1.2 K&A valeurs minoritaires
**Impact**: Reduire les 48% d'opaques "combinaisons K&A inconnues"
**Effort**: 3h
**Methode**:
- Pour chaque glyph, explorer les valeurs que le HMM ne choisit jamais
- k devant ee: forcer "qu" au lieu de "c" dans certains contextes
- t devant ee: forcer "ter" au lieu de "el"
- Ajouter des regles contextuelles dans glyphs.json
**Fichiers**: v12/rules/glyphs.json, v12/models/hmm.py
**Test**: Les 50 mots LOW les plus frequents — combien deviennent HIGH?

## 1.3 Deagglutination recursive (niveau 2)
**Impact**: Decoder les mots longs (8+ glyphes, 29-44% opaques)
**Effort**: 1h
**Methode**:
- Actuellement: 1 niveau (y + reste)
- Ajouter: 2 niveaux (y + t + reste = IN + EL + mot)
- Pour les mots 8+ glyphes, tester toutes les paires de prefixes
**Fichiers**: v12/pipeline.py (modifier S2c)
**Test**: Les mots longs de la section 3 de l'Opaque Deep Dive

## 1.4 Collision penalty amelioree
**Impact**: Meilleures alternatives quand le penalty se declenche
**Effort**: 30min
**Methode**:
- Actuellement: -8000 brut, choisit parfois des candidats mediocres
- Ameliorer: forcer le choix parmi les candidats Perseus-valides uniquement
**Test**: f77r L42

---

# AXE 2 — f57v VOLVELLE (Craquer le sous-systeme)

## 2.1 Labels des pages zodiacales
**Impact**: Identifier les noms de signes zodiacaux en EVA
**Effort**: 2h
**Methode**:
- Les pages zodiacales ont des labels INDIVIDUELS autour de chaque nymphe
- Ces labels sont souvent des mots courts (1-3 glyphes)
- Extraire TOUS les labels (pas le texte courant) de f70v-f73v
- Comparer avec les noms de signes attendus
- Utiliser les identifications botaniques comme analogie (labels de plantes)
**Source**: voynich.nu/extra/labels.html, botanical_anchors.json
**Fichiers**: v12/analysis/zodiac_labels.py (nouveau)

## 2.2 L03 comme cle de chiffrement
**Impact**: Potentiellement decoder le systeme de substitution lui-meme
**Effort**: 3h
**Methode**:
- L03 repete 4 fois une sequence de 12 glyphes avec 2 variations
- Si c'est une table de substitution, chaque position = une lettre
- Mapper: position 1=o, 2=l, 3=j/d, 4=r, 5=v, 6=x, 7=k, 8=m, 9=f/p, 10=t, 11=r, 12=y
- Comparer avec les alphabets de substitution du XVe siecle (Naibbe cipher)
- Tester: si la sequence est l'ALPHABET du chiffre, l'appliquer aux labels zodiacaux
**Reference**: Greshko, "The Naibbe cipher" (Taylor & Francis 2025)

## 2.3 L04 cycle lunaire — identification complete
**Impact**: Confirmer le volvelle, identifier les termes astronomiques
**Effort**: 1h
**Methode**:
- 29 mots = 29 jours. Pour chaque jour, quelle est la phase lunaire attendue?
- Jour 1 = nouvelle lune, 8 = 1er quartier, 15 = pleine lune, 22 = dernier quartier
- Decoder chaque mot avec TOUTES les alternatives K&A (beam=50)
- Comparer avec les termes du Kalendarium de Nicholas of Lynn
- Verifier: `aros` (jour 13) est-il dans le signe du Belier?
**Source**: MS Ashmole 370, Kalendarium de Nicholas of Lynn

## 2.4 L05 cadran horaire — mapping des heures
**Impact**: Confirmer le cadran solaire, identifier les unites de temps
**Effort**: 1h
**Methode**:
- 26 glyphes isoles en sequence = potentiel cadran de 18-24 heures
- Comparer l'ordre des glyphes avec les heures canoniques medievales
- Verifier si les glyphes repetes (r=6x, l=4x) marquent les heures principales
  vs les subdivisions
- Tester l'hypothese: r = marque d'heure, l = marque de subdivision

## 2.5 Comparaison avec volvelles connus
**Impact**: Validation externe de l'hypothese
**Effort**: 2h
**Methode**:
- MS Ashmole 370 (Bodleian Library) — lunar volvelle du Kalendarium
- Volvelle du Getty Museum (Decoding the Medieval Volvelle)
- Volvelle de Lambeth Palace
- MS Medical-Astrological Convolute (Utrecht University Library)
- Comparer structure, nombre d'anneaux, type de marqueurs
**Source**: digital.bodleian.ox.ac.uk, blogs.getty.edu/iris

---

# AXE 3 — MOTS OPAQUES (Les 8% restants)

## 3.1 Glyphes isoles — hypothese chiffres/unites
**Impact**: +344 mots si confirme
**Effort**: 1h
**Methode**:
- EXCLURE f57v (volvelle, pas du texte)
- Sur les 179 `l` restants: tester si toujours entre ingredient et verbe
- Tester Benford: l(179) > k(17) > t(15) > ch(13) > a(14) > e(12) > f(10)?
- Hypotheses: l=libra, a=ana, k=calefac/chiffre, t=tere/chiffre, f=fiat
- Si chiffres: chercher des patterns type "l l l" = "3" ou "l k" = "13"
**Fichiers**: v12/rules/logograms.json (ajouter les mappings confirmes)
**ATTENTION**: f57v exclue de l'analyse (glyphes = marqueurs de cadran)

## 3.2 Sous-systeme des noms propres
**Impact**: Decoder les noms de plantes et signes zodiacaux (~300 mots)
**Effort**: 4h (recherche)
**Methode**:
- Le crib zodiacal a montre que K&A ne decode PAS les noms propres
- Les noms de plantes en premiere position des herbaux sont aussi opaques
- Hypothese: le scribe utilise un systeme DIFFERENT pour les noms
- Tester: comparer les 30 opaques en tete de ligne herbale avec botanical_anchors.json
- Chercher un pattern: les noms propres utilisent-ils des glyphes specifiques?
**Reference**: Labels dans voynich.nu/extra/labels.html

## 3.3 Termes arabes latinises
**Impact**: Decoder le vocabulaire arabo-latin (asarum, zingiber, etc.)
**Effort**: 2h
**Methode**:
- Le Circa Instans et l'Antidotarium utilisent des termes arabes latinises
- Ces termes ne sont pas dans Perseus (classique) mais dans les pharmacopees
- Construire un dictionnaire de ~200 termes arabes latinises
- Les ajouter au pipeline (dictionary.add_arabic_forms())
**Source**: Circa Instans de Matthaeus Platearius, Canon d'Avicenne

## 3.4 Corpus astrologique
**Impact**: Reduire le taux d'opaques de la section Z (18%) et A (16%)
**Effort**: 2h
**Methode**:
- Les sections Zodiac/Astro utilisent un vocabulaire astrologique specifique
- Termes attendus: dodecatemoria, ascensional, meridianus, benefic, malefic
- Construire un LM astrologique a partir de la Tetrabiblos et des traites medievaux
- Ajouter au reranker T5 comme 4eme LM sectoriel
**Source**: Tetrabiblos de Ptolemee (traduction latine), Liber Astronomiae de Bonatti

---

# AXE 4 — VALIDATION ET PUBLICATION

## 4.1 Crib matching avec Collatinus (relance post-ameliorations)
**Impact**: Trouver des pentagrammes
**Effort**: 30min
**Methode**:
- Relancer crib_lemmatized.py apres chaque amelioration du pipeline
- Objectif: quadrigrammes 19 -> 30+, premier pentagramme
- Chaque amelioration (reranker, K&A, deagg recursive) devrait augmenter les matches

## 4.2 Validation adversariale
**Impact**: Solidifier les resultats pour la publication
**Effort**: 3h
**Methode**:
- Test 1: Encoder un texte latin CONNU avec K&A, puis le decoder — retrouve-t-on l'original?
- Test 2: Encoder un texte ALEATOIRE — produit-il les memes patterns statistiques?
- Test 3: Permuter les glyphs K&A — le score Perseus chute-t-il?
- Test 4: Comparer notre type-token ratio avec un vrai receptaire medieval
**Reference**: Methode de Rugg (2004) sur les tests de validation

## 4.3 Rapport de publication
**Impact**: Publier les resultats
**Effort**: 4h
**Contenu**:
1. Decouverte du systeme d'agglutination (18 prefixes, contribution originale)
2. f57v = volvelle pharmaceutique (parallele Ashmole 370)
3. 19 quadrigrammes matchant des corpus medievaux
4. INELIODE = Inula helenium sur f33r (triple convergence)
5. "et coquus in aqua" — instruction pharmaceutique mot pour mot
6. 89% du manuscrit lisible en latin pharmaceutique
7. Le VMS est un kit complet d'apothicaire: recettes + volvelle + herbier
**Format**: Article soumis a Cryptologia ou Journal of Medieval Studies

## 4.4 Mise a jour du rapport Gemini
**Impact**: Corriger les erreurs du rapport existant
**Effort**: 1h
**Corrections**:
- Retirer asara/apio/olen (artefacts v11c)
- Ajouter deagglutination, f57v volvelle, 19 quadrigrammes
- Mettre a jour les chiffres (89%, 85% Perseus)
- Ajouter INELIODE et "et coquus in aqua" comme preuves

---

# AXE 5 — OUTILS ET INFRASTRUCTURE

## 5.1 Fusionner v12 et VSV12
**Impact**: Un seul pipeline unifie
**Effort**: 4h
**Methode**:
- v12 a: deagglutination, collision penalty, logograms enrichis
- VSV12 a: beam search, Kneser-Ney LMs, YAML configs, T5 reranker
- Creer v13 qui combine les deux
**Attention**: Ne PAS casser ce qui fonctionne

## 5.2 Interface de lecture
**Impact**: Rendre le decode navigable
**Effort**: 3h
**Methode**:
- Page web simple (HTML/JS) qui affiche:
  - Image du folio (Beinecke digital library)
  - Texte EVA
  - Decode latin avec niveaux de confiance en couleur
  - Traduction anglaise
- Utiliser le VOYNICH_DECODE_V12_FINAL.txt comme source

## 5.3 Collatinus en batch
**Impact**: Accelerer les analyses qui utilisent Collatinus
**Effort**: 1h
**Methode**:
- Actuellement: connexion TCP par mot (lent)
- Creer un cache persistant (JSON) de toutes les formes deja lemmatisees
- Pre-lemmatiser les 38442 mots du decode en un seul batch

---

# ORDRE DE PRIORITE RECOMMANDE

## Session immediate (2-3h)
1. **1.1** Reranker T5 — impact le plus fort sur la qualite
2. **2.1** Labels zodiacaux — rapide, potentiellement revelateur
3. **4.1** Relancer crib matching

## Session suivante (3-4h)
4. **2.2** L03 comme cle de chiffrement — la piste la plus excitante
5. **1.2** K&A valeurs minoritaires — reduire les opaques
6. **3.2** Sous-systeme des noms propres
7. **1.3** Deagglutination recursive

## Session 3 (3-4h)
8. **2.3** L04 cycle lunaire complet
9. **3.3** Termes arabes latinises
10. **3.4** Corpus astrologique
11. **4.2** Validation adversariale

## Session 4 (4h)
12. **4.3** Rapport de publication
13. **5.1** Fusion v12/VSV12 en v13
14. **2.5** Comparaison avec volvelles connus
15. **5.2** Interface de lecture

---

# METRIQUES CIBLES

| Metrique | Actuel | Cible S1 | Cible S2 | Cible finale |
|----------|--------|----------|----------|-------------|
| Readable | 89% | 91% | 93% | 95%+ |
| Perseus | 85% | 87% | 90% | 92%+ |
| Type-token ratio | 0.154 | 0.18 | 0.22 | 0.28+ |
| Quadrigrammes | 19 | 25 | 35 | 50+ |
| Pentagrammes | 0 | 1 | 3 | 5+ |
| Opaques | 8% | 6% | 4% | <3% |

---

# FICHIERS DE REFERENCE

## Pipeline v12 (code)
- v12/pipeline.py — orchestrateur principal
- v12/stages/scorer.py — scoring calibre (9 signaux)
- v12/stages/reranker.py — A CREER (reranker T5)
- v12/rules/glyphs.json — mappings K&A
- v12/rules/logograms.json — 105+ logograms
- v12/models/hmm.py — HMM Viterbi
- v12/models/lm_herbal.json, lm_pharma.json, lm_balnea.json — LMs sectoriels

## Analyses (rapports)
- v12/output/VOYNICH_DECODE_V12_FINAL.txt — decode complet
- v12/output/VOYNICH_LATIN_CLEAN.txt — texte latin lisible (91.1%)
- v12/output/SESSION2_CHANGELOG.md — changelog de la session
- v12/output/OPAQUE_DEEP_DIVE.md — analyse des 3421 opaques
- v12/output/GLYPH_ABBREVIATIONS.md — glyphes isoles
- v12/output/COLLATINUS_VALIDATION.md — validation LOW/Collatinus
- v12/output/CRIB_LEMMATIZED_REPORT.txt — 19 quadrigrammes
- v12/output/F57V_ROSETTA.md — analyse volvelle
- v12/output/ZODIAC_CRIB_ATTACK.md — crib zodiacal
- v12/output/BFH_HUNTER_REPORT.txt — b/f/h (negatif)
- v12/output/DEAGGLUTINATOR_REPORT.txt — systeme d'agglutination
- v12/output/PREFIX_MAP_REPORT.txt — prefixes EVA → racines latines
- v12/output/PATTERN_HUNTER_REPORT.txt — patterns syntaxiques
- v12/output/PLANT_HUNTER_REPORT.txt — noms de plantes

## Donnees
- data/transcriptions/ZL.txt — manuscrit complet EVA
- data/latin_valid_wordset.json — 85K formes Perseus
- data/botanical_anchors.json — 106 plantes identifiees
- CORPORA_FINAL/ — 3 corpus (herbal 178K, pharma 426K, balnea 195K)
- Collatinus daemon — localhost:5555

## Pipeline VSV12 (a fusionner)
- VSV12/v12/decode/scorer.py — scoring calibre (source)
- VSV12/v12/decode/reranker.py — beam search T5
- VSV12/v12/decode/language_model.py — Kneser-Ney LMs
- VSV12/v12/data/*.yaml — configs YAML
