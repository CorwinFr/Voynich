# REFERENTIEL UNIVERSEL DE PHARMACOPEE MEDIEVALE

## Objectif

Base de donnees PURE de la pharmacopee medievale (XIIe-XVe siecle).
Chaque recette = une sequence de tokens types.
Chaque token pointe vers un referentiel centralise.
Toutes les sources dans le MEME format.

**REGLE ABSOLUE** : Aucune donnee Voynich dans ce referentiel.
C'est la verite historique independante. Le VMS est un CONSOMMATEUR
de ce referentiel, pas une source.

---

## ARCHITECTURE

```
datasets/
|
|--- REFERENTIELS (un concept = une entree) ------
|    |
|    |-- R01_verbs.json             TOUS les verbes pharma medievaux
|    |-- R02_ingredients.json       TOUS les ingredients connus
|    |-- R03_units.json             Unites de mesure + poids + abreviations
|    |-- R04_forms.json             Formes galeniques (electuarium, unguentum, ...)
|    |-- R05_tools.json             Outils et supports (mortarium, ignis, ...)
|    |-- R06_qualities.json         Qualites galeniques (4 x 4 degres)
|    |-- R07_plant_parts.json       Parties de plantes (radix, folia, ...)
|    |-- R08_indications.json       Maladies et indications therapeutiques
|
|--- RECETTES TOKENISEES (une source = un fichier) ------
|    |
|    |-- S01_AN.json                Antidotarium Nicolai (137 recettes)
|    |-- S02_CI.json                Circa Instans (~270 monographies)
|    |-- S03_AUREA.json             Aurea Alexandrina (AN recette #1)
|    |-- S04_GRABADIN.json          Liber Servitoris / Grabadin
|    |-- S05_MACER.json             Macer Floridus (~77 plantes)
|    |-- S06_REGIMEN.json           Regimen Sanitatis Salernitanum
|    |-- S07_DALME.json             Inventaires pharmacie reelles
|    |-- S08_AVICENNA.json          Canon Medicinae (extraits)
|    |-- S09_COLLECTIO.json         Collectio Salernitana (extraits)
|    |-- S10_ALPHITA.json           Alphita (glossaire herbal)
|
|--- META ------
|    |-- SCHEMA_FINAL.md            CE FICHIER
|    |-- INVENTORY.md               Inventaire des sources brutes
|    |-- build_referentiels.py      Script de generation
|    |-- build_recipes.py           Script de parsing
```

---

## SCHEMA D'UN REFERENTIEL

Chaque referentiel est un dictionnaire indexe par `ref_id`.
Chaque entree documente UN concept avec TOUTES ses formes attestees.

### R01_verbs.json — Exemple

```json
{
  "_meta": {
    "description": "Pharmaceutical verbs of medieval Latin and vernacular traditions",
    "period": "12th-15th century",
    "count": 42,
    "version": "2026-04-11"
  },

  "V_recipe": {
    "ref_id": "V_recipe",
    "canonical": "recipe",
    "gloss_en": "take/prepare",
    "gloss_fr": "prends/prepare",
    "forms": {
      "latin": ["recipe", "recipiat", "recipiatur", "recipiantur"],
      "old_french": ["prenez", "pren"],
      "middle_dutch": ["nemt"],
      "italian": ["prendi", "recipe"]
    },
    "pos": "verb_imperative",
    "frequency": {"AN": 137, "CI": 365, "Macer": 20, "Grabadin": 80},
    "notes": "Universal opening verb. Abbreviated Rp. in manuscripts.",
    "sources_attested": ["AN (van den Berg 1917)", "CI (Dorveaux 1913)", "Grabadin", "Ricettario Fiorentino 1498"]
  },

  "V_coque": {
    "ref_id": "V_coque",
    "canonical": "coque",
    "gloss_en": "cook/boil",
    "gloss_fr": "cuis/fais cuire",
    "forms": {
      "latin": ["coque", "coquatur", "coquantur", "coctum", "cocta", "coctus", "decoque", "decoquatur"],
      "old_french": ["cuire", "cuite", "cuisiez", "faites cuire"],
      "italian": ["cuoci", "cuocere", "cotto"]
    },
    "pos": "verb_imperative",
    "frequency": {"AN": 45, "CI": 175, "Grabadin": 60},
    "notes": "Core preparation verb. Often with cum (with) + liquid.",
    "sources_attested": ["AN", "CI", "Grabadin"]
  }
}
```

### R02_ingredients.json — Exemple

```json
{
  "I_myrrha": {
    "ref_id": "I_myrrha",
    "canonical": "myrrha",
    "gloss_en": "myrrh",
    "gloss_fr": "myrrhe",
    "forms": {
      "latin": ["myrrha", "myrrhae", "myrrham", "mirra", "mirre", "mirram"],
      "old_french": ["mirre"],
      "italian": ["mirra"],
      "arabic_origin": "murr"
    },
    "category": "resin",
    "plant_part": "P_gummi",
    "botanical": "Commiphora myrrha",
    "galenic": "Q_calidum_2_siccum_2",
    "frequency": {"AN": 72, "CI": 12, "DALME_Roux": 1, "Lylye": 8},
    "pct_AN_recipes": 52.6,
    "sources_attested": ["AN", "CI", "DALME", "Lylye", "Alphita", "Avicenna"],
    "nomenclator_italian": "mirra"
  }
}
```

### R03_units.json — Exemple

```json
{
  "U_drachma": {
    "ref_id": "U_drachma",
    "canonical": "drachma",
    "gloss_en": "drachm",
    "forms": {
      "latin": ["drachma", "drachmam", "drachmas", "drachmae", "dragma"],
      "old_french": ["drame", "dragme"],
      "abbreviation": [".z.", "dr.", "3"]
    },
    "type": "weight",
    "weight_grams": 3.9,
    "subdivisions": "1 drachma = 3 scrupuli = 60 grana",
    "parent": "U_uncia (1 uncia = 8 drachmae)",
    "sources_attested": ["AN", "CI", "Compendium Aromatariorum (Saladino 1488)"]
  },

  "D_ana": {
    "ref_id": "D_ana",
    "canonical": "ana",
    "gloss_en": "of each / equal parts",
    "forms": {
      "latin": ["ana", "an"],
      "abbreviation": ["aa.", "an."]
    },
    "type": "dose_marker",
    "notes": "Indicates all preceding ingredients share the same dose.",
    "sources_attested": ["AN (universal)", "CI", "Grabadin"]
  }
}
```

### R06_qualities.json — Exemple

```json
{
  "Q_calidum_2_siccum_2": {
    "ref_id": "Q_calidum_2_siccum_2",
    "thermal": "calidum",
    "thermal_degree": 2,
    "moisture": "siccum",
    "moisture_degree": 2,
    "latin_formula": "calidum in secundo gradu et siccum in secundo",
    "old_french_formula": "chauz el segont degre et ses el segont",
    "plants_with_this_quality": ["myrrha", "cinnamomum", "mastix", "mentha", "salvia", "iris"],
    "source": "Circa Instans (Platearius ~1166), ed. Dorveaux 1913"
  }
}
```

---

## SCHEMA D'UNE RECETTE

```json
{
  "_meta": {
    "source_text": "Antidotarium Nicolai",
    "edition": "van den Berg 1917",
    "file": "data/raw_corpus_9a/antidotarium_nicolai_1917.txt",
    "language": "latin",
    "period": "~1150, Salerno",
    "count": 137
  },

  "entries": [
    {
      "id": "AN_001",
      "name": "Aurea Alexandrina",
      "form": "F_electuarium",
      "indication": "ad omne capitis vitium ex frigidate",

      "raw_text": "Recipe asari carpobalsami iusquiami an .z.ii. ...",

      "tokens": [
        {"pos": 1,  "raw": "Recipe",      "type": "VERB", "ref": "V_recipe"},
        {"pos": 2,  "raw": "asari",        "type": "INGR", "ref": "I_asarum"},
        {"pos": 3,  "raw": "carpobalsami", "type": "INGR", "ref": "I_carpobalsamum"},
        {"pos": 4,  "raw": "iusquiami",    "type": "INGR", "ref": "I_iusquiamus"},
        {"pos": 5,  "raw": "an",           "type": "DOSE", "ref": "D_ana"},
        {"pos": 6,  "raw": ".z.ii.",       "type": "QTY",  "value": "2 drachmae"},
        {"pos": 7,  "raw": "et",           "type": "CONJ"},
        {"pos": 8,  "raw": ".S.",           "type": "QTY",  "value": "0.5"},
        {"pos": 9,  "raw": "gariofilorum", "type": "INGR", "ref": "I_gariofilum"},
        {"pos": 10, "raw": "mirre",        "type": "INGR", "ref": "I_myrrha"},
        {"pos": 11, "raw": "terantur",     "type": "VERB", "ref": "V_tere"},
        {"pos": 12, "raw": "cum",          "type": "PREP"},
        {"pos": 13, "raw": "melle",        "type": "INGR", "ref": "I_mel"},
        {"pos": 14, "raw": "dispensentur", "type": "VERB", "ref": "V_dispensare"},
        {"pos": 15, "raw": "in",           "type": "PREP"},
        {"pos": 16, "raw": "modum",        "type": "GRAM"},
        {"pos": 17, "raw": "electuarii",   "type": "FORM", "ref": "F_electuarium"}
      ],

      "pattern": "VERB INGR INGR INGR DOSE QTY CONJ QTY INGR INGR VERB PREP INGR VERB PREP GRAM FORM",

      "summary": {
        "n_tokens": 17,
        "n_ingredients": 5,
        "n_verbs": 3,
        "n_dosage_groups": 1,
        "ingredients": ["I_asarum", "I_carpobalsamum", "I_iusquiamus", "I_gariofilum", "I_myrrha", "I_mel"],
        "verbs": ["V_recipe", "V_tere", "V_dispensare"],
        "ratio_verb_ingr": "1:2.0"
      }
    }
  ]
}
```

---

## LES 17 TYPES DE TOKENS

| Code | Role | Exemples latins | Exemples vx francais | Ref |
|------|------|-----------------|----------------------|-----|
| VERB | Action pharma | recipe, tere, coque, misce, cola, fiat | prenez, metez, cuire, donez | R01 |
| INGR | Substance | aloe, myrrha, crocus, mel, oleum | mirre, eve, vin, miel | R02 |
| DOSE | Marqueur de dosage | ana, quantum sufficit | autant que | R03 |
| QTY | Quantite | .z.ii., .lb.i., unam, semis | .ii. drames | R03 |
| UNIT | Unite de mesure | drachma, uncia, libra, scrupulus | drame, once, livre | R03 |
| PREP | Preposition | cum, in, per, de, ad, contra, super | ovec, en, par, contre | - |
| ADJ | Qualificatif | epaticum, album, rubeum, subtile | blanc, rouge, fin | - |
| QUAL | Qualite galenique | calidum, frigidum, siccum, humidum | chauz, froid, sec | R06 |
| DEG | Degre | primo, secundo, tertio, quarto gradu | premier, segont, tierz | R06 |
| TOOL | Instrument | mortarium, ignis, pannum, vas | mortier, feu, drap | R05 |
| FORM | Forme galenique | electuarium, unguentum, emplastrum | oignement, emplastre | R04 |
| NAME | Nom de recette | Aurea Alexandrina, Hiera Picra | | - |
| PART | Partie de plante | radix, folia, semen, cortex, succus | racine, fuelles, semence | R07 |
| IND | Indication | contra dolorem, ad tussim, pro febre | contre dolor, por la toz | R08 |
| CONJ | Connecteur | et, vel, sive, aut | et, ou | - |
| COP | Copule | est, sunt, sit | est, sont | - |
| GRAM | Mot grammatical | que, qui, non, sed, in modum | le, la, ce, qui | - |

---

## PATTERNS DE RECETTES (signatures structurelles)

Chaque source a un pattern TYPIQUE. C'est la carte d'identite du format.

```
ANTIDOTARIUM NICOLAI (liste + dosage final) :
  VERB [INGR]+ DOSE QTY [INGR]+ DOSE QTY ... VERB PREP INGR VERB PREP FORM
  R.   aloe myrrha crocus ana 2dr gariof. opii  ana 2dr  tere cum  mel  fiat electuarium
  Ratio verb:ingr = 1:30     Dosage = apres groupes d'ingredients     Verbes = 1-2 a la fin

CIRCA INSTANS (monographie par plante) :
  INGR COP QUAL DEG CONJ QUAL DEG PUNCT IND PUNCT VERB INGR VERB PREP INGR PUNCT
  Ache est chaud 3   et   sec  2   .    contra  .   R.   jus  cuire cum  vin   .
  Ratio verb:ingr = 1:3-5     Galenic = TOUJOURS en premiere phrase     Multi-recettes par plante

GRABADIN (procedural step-by-step) :
  VERB INGR CONJ INGR CONJ VERB PREP TOOL CONJ VERB ADJ CONJ VERB PREP TOOL
  Acc. oleum et   ceram et  liqu. sup. ignem et  misce bene et  cola  per  pannum
  Ratio verb:ingr = 1:1-2     Chaque mot = une ETAPE     Outils explicites

TACUINUM SANITATIS (fiche normalisee) :
  INGR PUNCT NAME:Natura QUAL PUNCT NAME:Optimum ADJ PUNCT NAME:Iuvamentum IND PUNCT
  Format fixe a 5-6 champs     Pas de verbes     Pas de dosages
```

---

## REFERENTIELS CROISES

```
Token :  {"raw": "mirre", "type": "INGR", "ref": "I_myrrha"}
                                                     |
         R02_ingredients.json ----------------------+
         "I_myrrha": {                              |
           canonical: "myrrha",                     |
           galenic: "Q_calidum_2_siccum_2"  ------->+-- R06_qualities.json
           plant_part: "P_gummi"  ----------------->+-- R07_plant_parts.json
           category: "resin",                       |
           frequency: {AN: 72, CI: 12}              |
         }
```

Prefixes de ref_id :
- `V_xxx` -> R01_verbs
- `I_xxx` -> R02_ingredients
- `D_xxx` / `U_xxx` -> R03_units
- `F_xxx` -> R04_forms
- `T_xxx` -> R05_tools
- `Q_xxx` -> R06_qualities
- `P_xxx` -> R07_plant_parts
- `M_xxx` -> R08_indications

---

## SOURCES PRIMAIRES

| Code | Nom | Date | Lieu | Fichier | Lignes | Langue | Contenu | Statut |
|------|-----|------|------|---------|--------|--------|---------|--------|
| AN | Antidotarium Nicolai | ~1150 | Salerne | data/raw_corpus_9a/antidotarium_nicolai_1917.txt | 17264 | Latin/NL | 137 recettes composees | A PARSER |
| CI | Circa Instans (Platearius) | ~1166 | Salerne | BruteForce/.../circa_instans_full_text.txt | 13911 | Vx fr | ~270 monographies | **FAIT** |
| AUREA | Aurea Alexandrina (AN#1) | ~1150 | Salerne | BruteForce/.../aurea_alexandrina_crib_L1.txt | 40 | Latin | 1 recette (68 ingr) | **FAIT** |
| GRAB | Grabadin / Liber Servitoris | XIIe s. | Cordoue | (a trouver) | ? | Latin | Procedures galeniques | MANQUE |
| MACER | Macer Floridus | XIe s. | France? | data/raw_corpus_9a/macer_floridus_choulant_1832.txt | 13737 | Latin | ~77 plantes en vers | A PARSER |
| REG | Regimen Sanitatis | XIIIe s. | Salerne | data/raw_corpus_9a/regimen_sanitatis.txt | 500 | Latin | Regime de sante | A PARSER |
| DALME | Inventaires pharmacie | XIVe-XVe | Provence | BruteForce/Plants/PlantCypher/dalme_*.txt | ~4700 | Multi | ~2485 items reels | A PARSER |
| AVIC | Canon Medicinae (Avicenne) | 1507 ed. | Venise | data/raw_corpus_9a/canon_medicinae_1507.txt | 161K | Latin | Encyclopedie | A PARSER |
| CS | Collectio Salernitana | XIIe-XIIIe | Salerne | data/raw_corpus_9a/collectio_salernitana_v1-5.txt | ~176K | Latin/It | Compilation | A PARSER |
| ALPH | Alphita | XIIIe s. | Angleterre? | data/raw_corpus_9a/alphita_mowat_1887.txt | 32749 | Latin | Glossaire herbal | A PARSER |
| CLAV | Clavis Sanationis (Simon de Genes) | 1292 | Genes | data/raw_corpus_9a/clavis_sanationis_biusante.txt | 33858 | Latin | Dict. medical | A PARSER |

**Total : ~470,000 lignes de texte source**

---

## WORKFLOW D'AJOUT D'UNE SOURCE

```
1. OBTENIR le texte brut
   |
2. PARSER en recettes/entrees individuelles
   |  -> identifier les debuts/fins
   |
3. TOKENISER chaque recette
   |  -> attribuer un TYPE parmi les 17
   |  -> rattacher au ref_id si le mot est connu
   |  -> si INCONNU : classer INGR par defaut, marquer pour revue
   |
4. ENRICHIR les referentiels
   |  -> nouveau verbe -> R01 (source = cette source)
   |  -> nouvel ingredient -> R02
   |  -> nouvelle forme d'un mot connu -> ajouter dans forms[]
   |
5. CALCULER summary + pattern
   |
6. SAUVEGARDER comme SXX_NOM.json
```

---

## METRIQUES STRUCTURELLES PAR SOURCE

| Metrique | AN | CI | Grabadin | Tacuinum | Macer |
|----------|----|----|----------|----------|-------|
| ratio verb:ingr | 1:30 | 1:3-5 | 1:1-2 | 0 (pas de verbes) | 1:5-8 |
| pattern dominant | LISTE | STEP-BY-STEP | PROCEDURAL | FICHE | VERS |
| dosage_position | FIN (apres liste) | INLINE | INLINE | ABSENT | RARE |
| galenic_formula | ABSENTE | TOUJOURS (1ere phrase) | RARE | TOUJOURS | PARFOIS |
| organisation | Alpha par nom | Par plante A-Z | Par forme galenique | Par categorie | Par plante |
| n_ingr moyen | 8-15 | 2-5 | 3-6 | 1 | 3-8 |
| n_verbes moyen | 1-2 | 3-6 | 5-10 | 0 | 2-4 |
| indications | DEBUT (preambule) | APRES qualites | RARES | CHAMP FIXE | EN VERS |

---

## STATISTIQUES CIBLES

| Referentiel | Cible |
|-------------|-------|
| R01_verbs | 50-100 verbes uniques |
| R02_ingredients | 500-800 ingredients normalises |
| R03_units | 15-20 unites + 10 abreviations |
| R04_forms | 20-30 formes galeniques |
| R05_tools | 15-20 outils |
| R06_qualities | 207 plantes x 4 proprietes (fait) |
| R07_plant_parts | 15-20 parties |
| R08_indications | 100-200 maladies/symptomes |
| Recettes totales | 500-1000+ |

---

## ETAT ACTUEL

| Fichier | Statut | Entrees |
|---------|--------|---------|
| R01_verbs | A CREER (fusionner 02_verbs + enrichir) | cible 50+ |
| R02_ingredients | A CREER (fusionner 05_ingredients, normaliser) | cible 500+ |
| R03_units | A CREER (fusionner 07_dosages) | cible 20 |
| R04_forms | **A CREER** | cible 25 |
| R05_tools | **A CREER** | cible 20 |
| R06_qualities | FAIT (renommer 06_galenic) | 207 |
| R07_plant_parts | **A CREER** | cible 20 |
| R08_indications | **A CREER** | cible 100+ |
| S02_CI | FAIT (renommer 12_recipes_CI) | 1453 |
| S03_AUREA | FAIT (renommer 13_recipes_AUREA) | 1 |
| S01_AN | **PRIORITE** — A PARSER | cible 137 |
| S05-S10 | A PARSER | cible 500+ |
