# INVENTAIRE COMPLET — Datasets + Sources + Mappages

## Vue d'ensemble

```
datasets/                           <- REFERENTIELS UNIVERSELS (ce dossier)
data/transcriptions/                <- TEXTE VMS BRUT (EVA)
data/raw_corpus_9a/                 <- TEXTES DE REFERENCE BRUTS (~470K lignes)
data/raw_corpus_9a/cleaned/         <- TEXTES NETTOYES
data/dictionaries/                  <- DICTIONNAIRES (latin, italien, francais, espagnol)
data/quadgrams/                     <- MODELES DE LANGUE (quadrigrammes)
BruteForce/Italien plant names/     <- NOMENCLATOR ITALIEN (4466 noms)
BruteForce/Plants/Corpus_Pharmaceutique/ <- CORPUS PHARMA STRUCTURES
BruteForce/Plants/PlantCypher/      <- INVENTAIRES DALME (pharmacies reelles)
v12/data/                           <- DICTIONNAIRE VMS (7820 mots decodes)
v12/rules/                          <- REGLES DE DECODAGE (glyphes, logograms, HMM)
v12/models/                         <- MODELES DE LANGUE PAR SECTION
v12/output/                         <- RESULTATS D'ANALYSES
docs/                               <- DOCUMENTATION DES SESSIONS
```

---

## 1. REFERENTIELS UNIVERSELS (datasets/)

### 1a. Vocabulaire VMS (CE QU'ON SAIT DU MANUSCRIT)

| Fichier | Contenu | Entrees | Fiabilite | Source de preuve |
|---------|---------|---------|-----------|-----------------|
| 01_logograms.json | 16 glyphes = 16 mots latins fixes | 16 | **CONFIRME** (bifolio bH1, 9/9 match, 0 exception) | v12/analysis/BIFOLIO_bH1_SYNTHESE_COMPLETE.md |
| 02_verbs.json | Verbes pharma : r=recipe, m=misce + K&A + attendus | 14 | CONFIRME(2) + PROBABLE(4) + SPECULATIVE(2) + REFERENCE(6) | bifolio + K&A pipeline + textes AN/CI/Grabadin |
| 03_suffixes.json | 14 suffixes flexionnels + stats position/section | 14 | **STATISTIQUE** (distributions = fait, interpretations = hypothese) | Session 7, ZL.txt, docs/SESSION7_SUFFIX_PARADIGMS.md |
| 04_roots.json | 127 racines classees LEXICAL/FUNCTIONAL | 127 | **STATISTIQUE** (classification par entropie) | Session 7, ZL.txt |
| 05_ingredients.json | Tous les ingredients identifies (dict VMS) | 2370 | SUR(37%) PROBABLE(44%) DOUTE(11%) INCONNU(7%) | v12/data/vms_dictionary.json + nomenclator + 4 corpora |
| 09_top500_words.json | 500 mots les plus frequents + section + suspect | 500 | MIXTE (13 mots suspects = 11% du texte) | ZL.txt + dict v12 |
| 10_botanical_ids.json | Identifications de plantes par folio | 163 | LOW a MEDIUM (chercheurs souvent en desaccord) | Scott, Sherwood, Bax, Tucker, Voynich |

### 1b. References externes (CE QU'ON SAIT DU CONTEXTE MEDIEVAL)

| Fichier | Contenu | Entrees | Fiabilite | Source primaire |
|---------|---------|---------|-----------|----------------|
| 06_galenic_qualities.json | Qualites galeniques : chaud/froid x sec/humide x degre 1-4 | 207 plantes | **FAIT HISTORIQUE** | Circa Instans (Platearius ~1166), ed. Dorveaux 1913 |
| 07_dosages.json | Unites medievales (drachme, once, livre) + abreviations | ~20 | **FAIT HISTORIQUE** | Antidotarium Nicolai, Compendium Aromatariorum |
| 08_recipe_structures.json | Templates : AN / CI / Grabadin / Tacuinum | 4 | **FAIT HISTORIQUE** (structures) + HYPOTHESE (mapping VMS) | Textes de reference |

### 1c. Recettes tokenisees (FORMAT UNIVERSEL)

| Fichier | Source | Entrees | Tokens | Langue | Statut |
|---------|--------|---------|--------|--------|--------|
| 12_recipes_CI.json | Circa Instans | 1453 | VERB/INGR/DOSE/PREP/QUAL/... | Vieux francais | **FAIT** |
| 13_recipes_AUREA.json | Aurea Alexandrina (AN #1) | 1 | 105 tokens | Latin | **FAIT** |
| 11_recipes_AN.json | Antidotarium Nicolai | ~137 | - | Latin | A FAIRE |
| 14_recipes_GRABADIN.json | Liber Servitoris | ? | - | Latin | A FAIRE (texte a trouver) |
| 15_recipes_MACER.json | Macer Floridus | ? | - | Latin | A FAIRE |
| 16_recipes_REGIMEN.json | Regimen Sanitatis | ? | - | Latin | A FAIRE |
| 17_recipes_VMS.json | Nos decodes VMS | ? | - | EVA->Latin | A FAIRE |
| 18_recipes_DALME.json | Inventaires pharmacie | ~2485 | - | Multi | A FAIRE |
| 99_vocab_enrichment.json | Vocabulaire extrait | 14 verbes + 10222 ingr | - | Multi | **FAIT** |

---

## 2. TEXTES VMS (data/transcriptions/)

| Fichier | Format | Lignes | Contenu |
|---------|--------|--------|---------|
| ZL.txt | IVTFF Eva-1.7 | 8513 | Transcription Zandbergen-Landini v2b (2022). **REFERENCE PRINCIPALE.** |
| LSI.txt | IVTFF Eva-1.5 | 38939 | Interlineaire multi-transcripteurs (H, C, F, N, U) |

---

## 3. TEXTES DE REFERENCE BRUTS (data/raw_corpus_9a/)

### 3a. Textes pharma/medicaux (SOURCES PRIMAIRES)

| Fichier | Texte | Lignes | Langue | Interet pour VMS |
|---------|-------|--------|--------|-----------------|
| antidotarium_nicolai_1917.txt | **Antidotarium Nicolai** (van den Berg 1917) | 17264 | Latin/NL | **CRITIQUE** — 137 recettes, codebook VMS |
| circa_instans_ms_ocr.txt | **Circa Instans** (OCR manuscrit) | 5348 | Latin | **CRITIQUE** — ~270 simples, format herbal VMS |
| macer_floridus_choulant_1832.txt | **Macer Floridus** (Choulant 1832) | 13737 | Latin | Vertus des plantes en vers latins |
| alphita_mowat_1887.txt | **Alphita** (Mowat 1887) | 32749 | Latin | Glossaire herbal / synonymes |
| clavis_sanationis_biusante.txt | **Clavis Sanationis** | 33858 | Latin | Dictionnaire medical |
| canon_medicinae_1507.txt | **Canon Medicinae** (Avicenne 1507) | 161244 | Latin | Encyclopedie medicale |
| canon_medicinae_1522.txt | Canon Medicinae (1522) | 129789 | Latin | Variante |
| regimen_sanitatis.txt | **Regimen Sanitatis Salernitanum** | 500 | Latin | Regime de sante |
| regimen_sanitatis_croke_1830.txt | Regimen (Croke 1830) | 10009 | Latin | Avec commentaires |
| collectio_salernitana_v1.txt | **Collectio Salernitana** vol.1 | 33956 | Latin/It | Compilation Salerne |
| collectio_salernitana_v2.txt | Collectio Salernitana vol.2 | 45801 | Latin/It | |
| collectio_salernitana_v3.txt | Collectio Salernitana vol.3 | 31803 | Latin/It | |
| collectio_salernitana_v4.txt | Collectio Salernitana vol.4 | 37153 | Latin/It | |
| collectio_salernitana_v5.txt | Collectio Salernitana vol.5 | 27004 | Latin/It | |

### 3b. Versions nettoyees (data/raw_corpus_9a/cleaned/)

Memes textes avec OCR corrige, notes editoriales retirees. Prefixe `clean_`.
14 fichiers, ~79000 lignes total.

---

## 4. CORPUS PHARMA STRUCTURES (BruteForce/Plants/Corpus_Pharmaceutique/)

### 4a. Datasets CSV structures

| Fichier | Contenu | Entrees | Champs |
|---------|---------|---------|--------|
| antidotarium_nicolai_ingredients.csv | 114 ingredients AN + qualites galeniques | 114 | Rang, Ingredient_Latin, Nb_Recettes, Pct, CI_Thermal, CI_Thermal_Deg, CI_Moisture, CI_Moisture_Deg, Recettes_IDs |
| circa_instans_galenic_degrees.csv | 207 plantes CI + degres galeniques | 207 | Entry#, OldFrench, Latin, French, Thermal, ThermalDeg, Moisture, MoistureDeg |
| dalme_mathieu_roux_1488.csv | Inventaire Mathieu Roux Marseille 1488 | 459 | Provencal, Latin, categorie, presence AN/CI |
| lylye_medicynes_ingredients.csv | 715 ingredients Lylye of Medicynes | 715 | Middle English, Latin, frequence |

### 4b. Textes sources

| Fichier | Contenu | Lignes |
|---------|---------|--------|
| van_den_berg_full_text.txt | AN complet (Latin + NL + apparat critique) | 11509 |
| dorveaux_antidotaire_full_text.txt | AN traduction francaise (Dorveaux 1896) | 4967 |
| circa_instans_full_text.txt | CI complet (vieux francais, Dorveaux 1913) | 13911 |

---

## 5. NOMENCLATOR ITALIEN (BruteForce/Italien plant names/)

| Fichier | Contenu | Entrees |
|---------|---------|---------|
| nomenclator_unified.csv | Noms italiens de plantes (toutes sources) | 4466 |
| nomenclator_multi_attested.csv | Noms attestes par 2+ sources | 87 |
| validation_nrf1498.json | Validation croisee Nebrija 1498 | 1227 |

---

## 6. INVENTAIRES DALME (BruteForce/Plants/PlantCypher/)

| Fichier | Inventaire | Lignes | Lieu/Date |
|---------|-----------|--------|-----------|
| dalme_A_table_of_prices_of_medicines_in_Rome_1674.txt | Prix des medicaments | 1756 | Rome 1674 |
| dalme_Inventory_of_Rostaing_de_Greoux.txt | Pharmacie Rostaing | 1156 | Provence ~1400s |
| dalme_Inventory_of_the_shop_of_Johannes_Cambarelli.txt | Pharmacie Cambarelli | 1085 | ~1400s |
| dalme_Inventory_of_the_boutique_of_Steve_Villa.txt | Pharmacie Villa | 576 | ~1400s |
| dalme_Inventory_of_Guillem_Coll.txt | Pharmacie Coll | 141 | ~1400s |
| dalme_all_inventories_unified.csv | Tous inventaires fusionnes | 2485 | Multi |

---

## 7. DICTIONNAIRES (data/dictionaries/)

| Fichier | Langue | Entrees |
|---------|--------|---------|
| latin.txt | Latin | 10207 |
| italian.txt | Italien | 14241 |
| french.txt | Francais | 192830 |
| spanish.txt | Espagnol | 23536 |

---

## 8. NOTES TIRONIENNES (data/tironian/)

| Fichier | Contenu | Entrees |
|---------|---------|---------|
| schmitz_index_full.json | Index Schmitz complet | 182716 |
| tironian_mappings.json | Mappages notes -> caracteres | 3996 |
| schmitz_raw.txt | Texte brut Schmitz | 68111 lignes |

---

## 9. DECODAGE VMS (v12/)

### 9a. Donnees de decodage

| Fichier | Contenu | Entrees |
|---------|---------|---------|
| v12/data/vms_dictionary.json | **LE** dictionnaire VMS (chaque mot = 1 decode) | 7820 |
| v12/data/vms_wordlist.json | Liste de mots VMS + frequences | 7820 |
| v12/data/pharma_validation_matrix.json | 230 ingredients x 4 corpora | 230 |

### 9b. Regles

| Fichier | Contenu |
|---------|---------|
| v12/rules/glyphs.json | Mappages glyphe -> caractere |
| v12/rules/logograms.json | Logograms (mot entier par glyphe) |
| v12/rules/confirmed_roots.json | Racines confirmees (aiin score reduit) |
| v12/rules/hmm_params.json | Parametres HMM pour K&A |

### 9c. Modeles de langue (par section)

| Fichier | Section | Tokens |
|---------|---------|--------|
| v12/models/lm_herbal.json | Herbal | 178202 |
| v12/models/lm_pharma.json | Pharma | - |
| v12/models/lm_balnea.json | Balnea | - |

### 9d. Resultats d'analyses

| Fichier | Contenu |
|---------|---------|
| v12/output/VOYNICH_DECODE_V12_INGREDIENTS.txt | Decode complet avec ingredients (19959 lignes) |
| v12/output/VOYNICH_LATIN_CLEAN.txt | Transcription latine nettoyee (5724 lignes) |
| v12/output/F103R_TRANSLATION.md | Premiere traduction f103r |
| v12/output/CRITICAL_REVIEW_TOP30.md | 13 mots suspects |
| v12/output/INGREDIENT_PRESENCE_MATRIX.md | Matrice ingredients AN vs VMS |
| v12/output/GALLOWS_HERBAL_ANALYSIS.md | Gallows = prepositions |
| v12/output/ANALYSE_GLOBALE_CORRELATIONS.md | Vocabulaire par section |

---

## 10. CORPUS FINAUX COMPILES (CORPORA_FINAL/)

| Fichier | Section | Taille |
|---------|---------|--------|
| corpus_herbal.txt | Textes herbal latins (Macer etc.) | 1.2M |
| corpus_pharma.txt | Textes pharma latins (AN etc.) | 2.7M |
| corpus_balnea.txt | Textes balnea/therapie | 1.3M |

---

## MAPPAGES ENTRE DATASETS

```
                    TEXTE VMS (ZL.txt)
                         |
                    [EVA words]
                         |
               +---------+---------+
               |                   |
        01_logograms          04_roots
        (16 glyphes)         (127 racines)
               |                   |
          02_verbs            03_suffixes
        (14 verbes)         (14 suffixes)
               |                   |
               +----> 09_top500_words <----+
                      (section + suspect)
                              |
                    05_ingredients
                    (2370 identifies)
                         |
            +------------+------------+
            |            |            |
    06_galenic      07_dosages    10_botanical
    (207 plantes)   (unites)     (163 folios)
            |            |            |
            +---> RECETTES TOKENISEES <---+
            |                             |
     12_recipes_CI              13_recipes_AUREA
     (1453 entrees)             (1 recette crib)
            |                             |
            +---> 08_recipe_structures <--+
                  (4 templates)
                        |
              99_vocab_enrichment
              (verbes + ingredients extraits)
```

### Comment ajouter une nouvelle source

1. Parser le texte en tokens (VERB/INGR/DOSE/...)
2. Sauvegarder comme `1X_recipes_NOM.json` (meme schema que les autres)
3. Collecter les nouveaux verbes/ingredients
4. Les ajouter a `02_verbs.json` et `05_ingredients.json` avec `confidence=REFERENCE` et `source=NOM`
5. Mettre a jour `99_vocab_enrichment.json`
6. Mettre a jour ce fichier (INVENTORY.md)

---

## VOLUME TOTAL

| Categorie | Fichiers | Lignes/Entrees | Taille |
|-----------|----------|----------------|--------|
| Datasets structures (datasets/) | 13 | ~15000 entrees | ~11M |
| Textes bruts (raw_corpus_9a/) | 27 | ~470000 lignes | ~40M |
| Dictionnaires | 4 | ~240000 mots | ~2.6M |
| Notes tironiennes | 3 | ~250000 entrees | ~15M |
| Nomenclator italien | 3 | ~5700 noms | ~0.5M |
| Inventaires DALME | 7 | ~7200 items | ~0.3M |
| Decodage VMS (v12/) | ~20 | ~8000 mots | ~2M |
| **TOTAL** | **~80** | **~1M entrees** | **~70M** |
