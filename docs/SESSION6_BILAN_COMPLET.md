# SESSION 6 — BILAN COMPLET POUR COMPACTAGE

## Date : 11 avril 2026
## 31 commits, ~20 heures d'analyse

---

## DECOUVERTES MAJEURES (a retenir)

### 1. DICTIONNAIRE VMS (7820 mots)
Chaque mot du VMS a UN decode fixe. Lookup instantane.
Fichier: `v12/data/vms_dictionary.json`
- 37% SUR, 44% PROBABLE, 11% DOUTE, 7% INCONNU
- 81% decode (mais 11% suspect → vrai taux ~70%)

### 2. FIX CRITIQUE: aiin ≠ aquam
Le confirmed_root aiin=aquam (score 34989) etait FAUX.
- okaiin = CURA (1540x corpus), pas "aquam"
- chaiin = IURE (jus), lkaiin = SECURE
- Le suffixe -aiin est GRAMMATICAL, pas toujours "eau"
- Mais -aiin n'est probablement PAS non plus "ana II drachmes"
- 72 "dosages" sur f103r = trop → -aiin est un suffixe, pas un dosage

### 3. TABLE DES 18 LOGOGRAMS
Cross-validee bifolio bH1 (f57v/f66r), 9/9 glyphes, 0 exception.
o=ac, l=se, d=de, r=recipe, v=vel, x=crux, k=cum, m=misce,
f=per, t=el, y=in, c=cum, s=est, sh=ci, p=usque, ch=cum

### 4. GALLOWS = PREPOSITIONS
108 pages herbal: p/f=per(58 pages), k=cum(21), t=el(20), aucun(9)
Le gallows introduit le nom de plante, ne le classifie PAS.

### 5. 217 INGREDIENTS + 105 PLANTES
- 92 plantes par gallows strip + nomenclator
- 37 plantes par ch→c substitution
- 13 plantes par identification externe (Sherwood/Scott)
- 75 ingredients par nomenclator dans les recettes

### 6. MATRICE DE PRESENCE
28/30 top ingredients AN matchent des mots VMS par distribution de folios.
chckhy(16 fol)~MYRRHA, keey(12)~AMOMUM, olkeey(9)~CINNAMOMUM

### 7. K&A FONCTIONNE (84% Perseus)
84% des mots DOUTE_KA sont des mots latins valides dans Perseus.
Pas de systeme separe. Pas de syllabaire. K&A pour tout.

### 8. VOCABULAIRE PAR SECTION
- HERBAL: daiin(51%), chol(56%), chor(71%) = termes botaniques
- BIO/BAINS: shedy(56%), ol(42%), chedy(41%) = termes balneologiques
- RECETTES: al(53%), cheey(42%) = termes pharmaceutiques

### 9. PROBLEME DES 13 MOTS SUSPECTS (11% du texte)
chedy(504x), shedy(435x), chol(396x), chey(353x), ol(545x),
dal(241x), chor(214x), daiin(847x), dar(327x), etc.
Leurs decodes K&A ne font PAS SENS dans le contexte:
- "nourriture" 435x, "dieu" 241x, "tu es" 545x = ABSURDE
- 4 mots differents pour "eius" (1212 tokens)
- 2 mots pour "dura" (1174 tokens)

### 10. f103r N'EST PAS UNE SEULE RECETTE
73 groupes entre "dosages" vs 7 groupes dans l'Aurea.
Soit c'est ~10 recettes courtes, soit -aiin n'est pas un dosage.

---

## CE QUI EST FIABLE vs CE QUI EST DOUTEUX

### FIABLE (garder)
- Dictionnaire 7820 mots (structure)
- Verbes: recipe, coque, tere, misce, cola
- 217 ingredients identifies (nomenclator confirmes)
- 105/108 plantes herbal
- Table des 18 logograms
- Gallows = prepositions
- K&A fonctionne (84% Perseus)
- Matrice de presence (28/30 match)

### DOUTEUX (a revoir)
- Les 13 mots suspects (11% du texte)
- Le systeme de quantites (a=ana, i=1, n=drachme) — probablement faux
- Le suffixe -aiin comme dosage — trop frequent pour etre un dosage
- Le "mode dual" (table vs K&A) — probablement inutile
- Le syllabaire (t=lo, l=sa) — fonctionne sur 2 ancres seulement
- Le ratio verbe/ingredient — 1:10-13 au lieu de 1:30-75 de l'AN

### FAUX (abandonne)
- aiin = aquam (corrige)
- Lunaire des malades pour L04 (refute)
- Substitution simple pour ingredients (0 cascade)
- Anagrammes (coincidence aros=rosa)
- Systeme different du VMS pour L04 (meme systeme)

---

## FICHIERS CLES

### Pipeline
- v12/data/vms_dictionary.json — LE dictionnaire (7820 mots)
- v12/data/vms_wordlist.json — frequences
- v12/data/pharma_validation_matrix.json — 230 ingr x 4 corpora
- v12/decoder_table.py — table des logograms
- v12/classifier.py — classifieur de mots
- v12/decoder_dual.py — decodeur dual
- v12/pipeline_v2.py — pipeline complet avec variantes
- v12/loaders/eva_variants.py — generateur de variantes EVA

### Analyses
- v12/output/DECODE_GLOBAL_STATS.md — stats globales
- v12/output/F103R_TRANSLATION.md — premiere traduction
- v12/output/INGREDIENT_PRESENCE_MATRIX.md — matrice de presence
- v12/output/CRITICAL_REVIEW_TOP30.md — revue des 13 suspects
- v12/output/GALLOWS_HERBAL_ANALYSIS.md — gallows = prepositions
- v12/output/ANALYSE_GLOBALE_CORRELATIONS.md — correlations par section

### Documents
- docs/CONCLUSION_SESSION6.md — conclusion
- docs/PLAN_V8_GLOBAL.md — plan pipeline
- docs/PLAN_ITERATION_ANOMALIES.md — plan anomalies
- hypotheses/H04_lunaire_L04/ — tout le travail L04

---

## PROCHAINE SESSION — PRIORITES

1. **Resoudre les 13 mots suspects** — surtout chol.daiin (bigram #1 de l'herbal)
   et shedy (435x). Que signifient-ils VRAIMENT?

2. **Determiner la vraie valeur de -aiin** — ce n'est PAS "aquam" (corrige),
   ce n'est probablement PAS "ana II drachmes" (trop frequent).
   C'est un SUFFIXE GRAMMATICAL — mais lequel?

3. **Comparer avec le Circa Instans** — le VMS est peut-etre organise
   par PLANTE (comme le CI) pas par RECETTE (comme l'AN).
   Chaque section = instructions pour UNE plante.

4. **Lire f103r comme ~10 recettes courtes** — pas une seule Aurea.
   Identifier les SEPARATEURS de recettes.

5. **Verifier les 105 plantes herbal** contre les illustrations HD.
