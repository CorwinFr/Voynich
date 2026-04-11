# DATASETS — Structure et Schema Universel

## Objectif

Un referentiel UNIQUE ou chaque recette medievale est decomposee en atomes
(verbe, ingredient, dosage, qualite, outil, forme galenique).
Toutes les sources dans le MEME format. Cross-reference avec le VMS.
Chaque ajout d'une nouvelle source enrichit automatiquement les listes de
verbes, ingredients, etc.

---

## ARCHITECTURE

```
datasets/
|
|-- SCHEMA.md                    <-- CE FICHIER (documentation)
|
|-- MASTER LISTS (referentiels) -------
|   |-- 01_logograms.json              16 glyphes confirmes (bifolio bH1)
|   |-- 02_verbs.json                  Tous les verbes pharma (VMS + ref)
|   |-- 03_suffixes.json               14 suffixes flexionnels + stats
|   |-- 04_roots.json                  127 racines LEX/FUNC
|   |-- 05_ingredients.json            Master list ingredients (VMS + ref)
|   |-- 06_galenic_qualities.json      207 qualites galeniques (Circa Instans)
|   |-- 07_dosages.json                Unites de mesure + abreviations
|   |-- 10_botanical_ids.json          163 identifications par folio
|
|-- RECIPE DATABASE --------
|   |-- 11_recipes_AN.json            Recettes Antidotarium Nicolai
|   |-- 12_recipes_CI.json            Recettes/entrees Circa Instans
|   |-- 13_recipes_AUREA.json         Aurea Alexandrina (crib f103r)
|   |-- 14_recipes_GRABADIN.json      Liber Servitoris / Grabadin
|   |-- 15_recipes_MACER.json         Macer Floridus (vertus des plantes)
|   |-- 16_recipes_REGIMEN.json       Regimen Sanitatis Salernitanum
|   |-- 17_recipes_VMS.json           Nos recettes VMS decodees
|   |-- 18_recipes_DALME.json         Inventaires DALME (ingredients reels)
|
|-- RECIPE TEMPLATES --------
|   |-- 08_recipe_structures.json      Modeles structurels par source
|
|-- VMS ANALYSIS --------
|   |-- 09_top500_words.json           Top 500 mots VMS + analyse
```

---

## SCHEMA UNIVERSEL D'UNE RECETTE

Chaque recette dans les fichiers 11-18 suit ce format :

```json
{
  "id": "AN_001",
  "name": "Aurea Alexandrina",
  "source": {
    "text": "Antidotarium Nicolai",
    "edition": "van den Berg 1917",
    "file": "data/raw_corpus_9a/antidotarium_nicolai_1917.txt",
    "page_or_line": "p.42",
    "language": "latin"
  },
  "type": "electuarium",
  "category": "compound_recipe",

  "tokens": [
    {"pos": 1, "raw": "Recipe",     "type": "VERB",  "normalized": "recipe",    "ref_id": "V_recipe"},
    {"pos": 2, "raw": "aloem",      "type": "INGR",  "normalized": "aloe",      "ref_id": "I_aloe"},
    {"pos": 3, "raw": "epaticam",   "type": "ADJ",   "normalized": "epaticum",  "ref_id": null},
    {"pos": 4, "raw": "mirram",     "type": "INGR",  "normalized": "myrrha",    "ref_id": "I_myrrha"},
    {"pos": 5, "raw": "crocus",     "type": "INGR",  "normalized": "crocus",    "ref_id": "I_crocus"},
    {"pos": 6, "raw": "ana",        "type": "DOSE",  "normalized": "ana",       "ref_id": "D_ana"},
    {"pos": 7, "raw": "drachmam",   "type": "UNIT",  "normalized": "drachma",   "ref_id": "U_drachma"},
    {"pos": 8, "raw": "unam",       "type": "QTY",   "normalized": "1",         "ref_id": null},
    {"pos": 9, "raw": "terantur",   "type": "VERB",  "normalized": "tere",      "ref_id": "V_tere"},
    {"pos": 10,"raw": "cum",        "type": "PREP",  "normalized": "cum",       "ref_id": null},
    {"pos": 11,"raw": "melle",      "type": "INGR",  "normalized": "mel",       "ref_id": "I_mel"},
    {"pos": 12,"raw": "dispensentur","type": "VERB",  "normalized": "dispensare","ref_id": "V_dispensare"}
  ],

  "summary": {
    "n_ingredients": 4,
    "n_verbs": 3,
    "n_dosages": 1,
    "ingredients": ["aloe", "myrrha", "crocus", "mel"],
    "verbs": ["recipe", "tere", "dispensare"],
    "dosage": "ana drachma 1",
    "form": "electuarium",
    "ratio_verb_ingr": "1:1.3"
  },

  "vms_crossref": {
    "ingredients_found_in_vms": ["aloe", "myrrha", "crocus", "mel"],
    "verbs_found_in_vms": ["recipe", "tere"],
    "possible_vms_folios": ["f103r"],
    "match_quality": "PARTIAL"
  }
}
```

---

## TYPES DE TOKENS

| Type | Code | Description | Exemples |
|------|------|-------------|----------|
| Verbe | VERB | Action pharma | recipe, coque, tere, misce, cola, solve, funde |
| Ingredient | INGR | Substance | aloe, myrrha, crocus, mel, aqua, vinum |
| Dosage marqueur | DOSE | Indicateur de dosage | ana (de chaque), quantum sufficit |
| Quantite | QTY | Nombre | 1, 2, 3, semis (1/2) |
| Unite | UNIT | Unite de mesure | drachma, uncia, libra, scrupulus, manipulus |
| Preposition | PREP | Lien grammatical | cum, in, per, de, ad, contra |
| Adjectif | ADJ | Qualificatif | epaticum, album, rubeum, subtile |
| Qualite galenique | QUAL | Propriete | calidum, frigidum, siccum, humidum |
| Degre | DEG | Intensite | in primo/secundo/tertio/quarto gradu |
| Outil | TOOL | Instrument | mortarium, ignis, pannum, vas |
| Forme galenique | FORM | Type de preparation | electuarium, unguentum, emplastrum, syrupus, pilulae |
| Nom de recette | NAME | Nom propre | Aurea Alexandrina, Hiera Picra |
| Partie de plante | PART | Partie utilisee | radix, folia, semen, cortex, succus, flos |
| Maladie/indication | IND | Usage therapeutique | contra dolorem, ad tussim, pro febre |
| Connecteur | CONJ | Liaison | et, vel, sive, aut |
| Copule | COP | Etre | est, sunt, sit |
| Ponctuation | PUNCT | Separateur | ., ;, fin_recette |

---

## REFERENTIELS CROISES (ref_id)

Chaque token pointe vers un referentiel :

- `V_xxx` -> 02_verbs.json (ex: V_recipe, V_coque, V_tere)
- `I_xxx` -> 05_ingredients.json (ex: I_aloe, I_myrrha)
- `U_xxx` -> 07_dosages.json (ex: U_drachma, U_uncia)
- `D_xxx` -> 07_dosages.json (ex: D_ana, D_quantum_sufficit)
- `Q_xxx` -> 06_galenic_qualities.json (ex: Q_calidum_2)

Quand on parse une nouvelle source et qu'on trouve un verbe inconnu,
on l'ajoute a 02_verbs.json avec confidence=REFERENCE et la source.
Idem pour les ingredients.

---

## SOURCES DISPONIBLES (dans le repo)

| # | Source | Fichier | Lignes | Langue | Type | Statut |
|---|--------|---------|--------|--------|------|--------|
| AN | Antidotarium Nicolai | data/raw_corpus_9a/antidotarium_nicolai_1917.txt | 17264 | Latin | 137 recettes composees | A PARSER |
| AN_clean | AN nettoye | data/raw_corpus_9a/cleaned/clean_antidotarium_nicolai_1917.txt | 1726 | Latin | idem | A PARSER |
| CI | Circa Instans | BruteForce/.../circa_instans_full_text.txt | 13911 | Vx francais | ~270 monographies | A PARSER |
| CI_ocr | Circa Instans MS | data/raw_corpus_9a/circa_instans_ms_ocr.txt | 5348 | Latin | OCR manuscrit | A PARSER |
| Aurea | Aurea Alexandrina | BruteForce/Plants/AureaAlexandrina/aurea_alexandrina_crib_L1.txt | - | Latin | 1 recette (crib f103r) | A PARSER |
| Macer | Macer Floridus | data/raw_corpus_9a/macer_floridus_choulant_1832.txt | 13737 | Latin | Vertus en vers | A PARSER |
| Macer_clean | Macer nettoye | data/raw_corpus_9a/cleaned/clean_macer_floridus_choulant_1832.txt | 2608 | Latin | idem | A PARSER |
| Regimen | Regimen Sanitatis | data/raw_corpus_9a/regimen_sanitatis.txt | 500 | Latin | Regime de sante | A PARSER |
| Regimen2 | Regimen (Croke 1830) | data/raw_corpus_9a/regimen_sanitatis_croke_1830.txt | 10009 | Latin | idem + commentaires | A PARSER |
| CS1-5 | Collectio Salernitana | data/raw_corpus_9a/collectio_salernitana_v1-5.txt | ~176K | Latin/It | Compilation Salerne | A PARSER |
| Avicenna | Canon Medicinae | data/raw_corpus_9a/canon_medicinae_1507.txt | 161K | Latin | Encyclopedie medicale | A PARSER |
| Alphita | Alphita (glossaire) | data/raw_corpus_9a/alphita_mowat_1887.txt | 32749 | Latin | Glossaire herbal | A PARSER |
| Clavis | Clavis Sanationis | data/raw_corpus_9a/clavis_sanationis_biusante.txt | 33858 | Latin | Dictionnaire medical | A PARSER |
| DALME | Inventaires DALME | BruteForce/Plants/PlantCypher/dalme_*.txt | ~4700 | Multi | Inventaires pharmacie | A PARSER |
| VMS | Manuscrit Voynich | data/transcriptions/ZL.txt | 8513 | EVA | Le manuscrit | A PARSER |

**Total : ~470,000 lignes de texte source a parser**

---

## STATISTIQUES CIBLES (apres parsing complet)

| Dataset | Cible |
|---------|-------|
| Recettes individuelles | 500-1000+ |
| Verbes uniques | 50-100 |
| Ingredients uniques | 500-800 |
| Unites de mesure | 15-20 |
| Formes galeniques | 20-30 |
| Outils/instruments | 15-20 |
| Maladies/indications | 100-200 |
| Parties de plantes | 15-20 |
| Qualites galeniques | 8 (4 thermal x 4 degres) |

---

## USAGE

### Attaque par crib
```python
# Charger la recette Aurea Alexandrina
aurea = recipes_AN[0]
# Extraire la sequence de types
pattern = [t['type'] for t in aurea['tokens']]
# -> ['VERB', 'INGR', 'INGR', 'INGR', 'DOSE', 'UNIT', 'QTY', 'VERB', 'PREP', 'INGR', 'VERB']
# Chercher ce pattern dans le VMS (f103r)
```

### Enrichissement croise
```python
# Nouveau verbe trouve dans Macer Floridus
if 'decoque' not in verbs:
    verbs.append({'latin': 'decoque', 'source': 'Macer Floridus', ...})
    # -> automatiquement disponible pour le VMS matching
```

### Statistiques de reference
```python
# Ratio verbe/ingredient dans l'AN vs CI vs VMS
an_ratio = mean([r['summary']['ratio_verb_ingr'] for r in recipes_AN])
ci_ratio = mean([r['summary']['ratio_verb_ingr'] for r in recipes_CI])
# -> comparer avec VMS pour determiner quel format est le plus proche
```

---

## ETAT ACTUEL

| # | Fichier | Statut | Entrees | Taille |
|---|---------|--------|---------|--------|
| 01 | 01_logograms.json | FAIT | 16 | 3.6K |
| 02 | 02_verbs.json | FAIT | 14 | 4.7K |
| 03 | 03_suffixes.json | FAIT | 14 | 7.6K |
| 04 | 04_roots.json | FAIT | 127 | 52K |
| 05 | 05_ingredients.json | FAIT | 2370 | 541K |
| 06 | 06_galenic_qualities.json | FAIT | 207 | 52K |
| 07 | 07_dosages.json | FAIT | - | 3K |
| 08 | 08_recipe_structures.json | FAIT | 4 templates | 5.8K |
| 09 | 09_top500_words.json | FAIT | 500 | 165K |
| 10 | 10_botanical_ids.json | FAIT | 163 | 44K |
| 12 | 12_recipes_CI.json | FAIT | 1453 | 10M |
| 13 | 13_recipes_AUREA.json | FAIT | 1 | 17K |
| 99 | 99_vocab_enrichment.json | FAIT | 14 verbs, 10222 ingr | 4K |

### Verbes trouves dans les sources
metez(422x), prenez(365x), faites(292x), donez(212x), cuire(175x),
oigniez(79x), lavez(36x), fiat(6x), coque(3x), tere(2x), cola(1x), recipe(1x)

### Top ingredients trouves
poldre(295x), eve/eau(237x), vin(202x), herbe(165x), huile(144x),
miel(98x), racine(95x), semence(92x), poudre(84x), corne(80x)

## PROCHAINES ETAPES

1. [x] Parser l'Aurea Alexandrina (1 recette crib) -> 13_recipes_AUREA.json
2. [x] Parser le Circa Instans (~1453 entrees) -> 12_recipes_CI.json
3. [  ] Parser l'Antidotarium Nicolai (137 recettes) -> 11_recipes_AN.json
4. [  ] Parser les recettes VMS decodees -> 17_recipes_VMS.json
5. [  ] Enrichir 02_verbs.json et 05_ingredients.json a chaque parsing
6. [  ] Parser le Macer Floridus -> 15_recipes_MACER.json
7. [  ] Parser les inventaires DALME -> 18_recipes_DALME.json
8. [  ] Parser le Grabadin (si texte trouve) -> 14_recipes_GRABADIN.json
9. [  ] Parser le Regimen Sanitatis -> 16_recipes_REGIMEN.json
10. [  ] Statistiques globales : ratios, distributions, patterns
