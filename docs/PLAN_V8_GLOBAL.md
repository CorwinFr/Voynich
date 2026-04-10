# PLAN V8 : Pipeline global avec combinaisons de glyphes

## Principe

Pour chaque mot du VMS, au lieu de choisir UNE lecture EVA :
1. Generer TOUTES les lectures plausibles (variantes de glyphes)
2. Pour CHAQUE variante, decoder avec le systeme dual (table + K&A)
3. Scorer TOUTES les combinaisons
4. Garder la meilleure

C'est un pipeline EXHAUSTIF qui ne fait aucun choix premature.

## Architecture

```
ZL.txt + LSI.txt (3 transcripteurs)
         │
    ┌────▼────┐
    │ EVA     │  Pour chaque mot : generer 3-12 variantes
    │ Variants│  (ch↔ee, s↔r, a↔o, p↔f, t↔k, frontieres)
    └────┬────┘
         │ N variantes par mot
    ┌────▼────┐
    │Classifier│  Pour chaque variante : LOGO / INGR / DOSE / FUNC
    └────┬────┘
         │
    ┌────▼──────────────────────────┐
    │ Dual Decoder                  │
    │                               │
    │  LOGO → Table (instant)       │
    │  DOSE → Quantites (regex)     │
    │  INGR → K&A beam=30          │
    │         + nomenclator match   │
    │         + corpora validation   │
    └────┬──────────────────────────┘
         │ Scored results per variant
    ┌────▼────┐
    │ Scorer  │  Score = table_match + ingredient_match + structure
    │ Global  │  + coherence avec voisins (VERB→INGR→DOSE pattern)
    └────┬────┘
         │
    ┌────▼────┐
    │ Output  │  3 lignes : EVA / TYPE / LAT
    │         │  + variante choisie si ≠ ZL consensus
    └─────────┘
```

## Scoring (sans logarithmes, regles simples)

| Critere | Points | Condition |
|---------|--------|-----------|
| Table match | +100 | Glyphe isole dans la table des 18 |
| Logogram match | +80 | Mot dans les 122 logograms confirmes |
| Ingredient connu (AN) | +90 | Decode matche un ingredient Antidotarium |
| Ingredient italien | +85 | Decode matche un nom du nomenclator |
| Ingredient multi-corpus | +70 | Decode dans 2+ corpora (matrice) |
| Dosage pattern | +60 | Pattern ana/I/II/dr. reconnu |
| Structure coherente | +50 | Suit le pattern VERB→INGR→DOSE |
| K&A Perseus valide | +30 | Mot latin atteste dans Perseus |
| K&A corpus frequent | +20 | Mot dans le corpus medical |
| Variante ZL consensus | +10 | Lecture principale du transcripteur |
| Variante alt (H/V/U) | +5 | Lecture d'un seul transcripteur |
| Variante confusion | +2 | Generee par confusion de glyphes |

**Le score est ADDITIF et SIMPLE** — pas de log, pas de HMM.
L'apothicaire utilisait des regles, on utilise des regles.

## Etapes d'implementation

### ETAPE 1 : Generateur de variantes complet
Fichier : `v12/loaders/eva_variants.py` (deja fait, a enrichir)

Enrichir avec :
- Variantes de FRONTIERES DE MOTS (tchor.kedar vs sh.tedar)
- Variantes de LONGUEUR (ain vs aiin — scribal abbreviation)
- Variantes par FOLIO (certains folios ont plus d'ambiguites)
- Ponderation par TRANSCRIPTEUR (H vs V vs U fiabilite)

### ETAPE 2 : Classifieur contextuel
Fichier : `v12/classifier.py` (deja fait, a ameliorer)

Ameliorer avec :
- Contexte BIDIRECTIONNEL (mot avant ET mot apres)
- Pattern matching : VERB doit etre suivi par INGR ou DOSE
- Frequence globale : mots >15x dans recettes = FUNCTION
- Longueur : mots 3-4 chars apres DOSE = probablement INGR (ingredient court)

### ETAPE 3 : Scorer simple a regles
Fichier : `v12/scorer_rules.py` (NOUVEAU — remplace scorer.py pour le dual)

Regles au lieu de probabilites :
- Table match → score fixe (pas de calcul)
- Ingredient match → score fixe selon nb corpora
- Structure → bonus si le pattern local est coherent
- PAS de log, PAS de HMM, PAS de beam scoring

### ETAPE 4 : Pipeline combine
Fichier : `v12/pipeline_v2.py` (NOUVEAU — le pipeline global)

Pour chaque LIGNE du VMS :
1. Parser les mots EVA
2. Pour chaque mot, generer variantes
3. Pour chaque variante, classifier + decoder
4. Scorer chaque combinaison
5. Selectionner le meilleur scoring global DE LA LIGNE
   (pas mot par mot — la LIGNE entiere doit etre coherente)

La selection par LIGNE est importante : on veut la combinaison
qui produit la meilleure alternance VERB→INGR→DOSE, pas
le meilleur score MOT par MOT.

### ETAPE 5 : Detection d'anomalies (revue des lignes etranges)
Fichier : `v12/analysis/anomaly_detector.py` (NOUVEAU)

Apres le decode, detecter :
- INGR+INGR+INGR (3+ consecutifs)
- DOSE sans INGR precedent
- func chains 4+
- Lignes sans INGR
- Mots decodes identiques consecutifs

Pour chaque anomalie → flag pour revue manuelle.

### ETAPE 6 : Decode complet f103r-f116r
Script : `v12/analysis/decode_all_recipes.py`

- Decoder les 25 pages de recettes
- Produire un rapport par page (3 lignes)
- Accumuler les ingredients identifies
- Detecter les sequences matchant l'Antidotarium

### ETAPE 7 : Registre d'ingredients
Fichier : `v12/output/INGREDIENT_REGISTRY.md`

Table finale de TOUS les ingredients identifies :
- Nom latin / italien
- Mot EVA source
- Folio(s) d'apparition
- Score de confiance
- Validation (nb corpora)
- Variante EVA utilisee (si ≠ ZL)

## Dependances

```
ETAPE 1 (variants)
    ↓
ETAPE 2 (classifieur)
    ↓
ETAPE 3 (scorer regles) ← table + nomenclator + matrice
    ↓
ETAPE 4 (pipeline v2) ← combine tout
    ↓
ETAPE 5 (anomalies) → corrections → retour ETAPE 2
    ↓
ETAPE 6 (decode complet)
    ↓
ETAPE 7 (registre)
```

## Criteres de succes

| Metrique | Objectif |
|----------|----------|
| Ratio VERB:INGR | 1:3 a 1:8 |
| Ingredients identifies | 30+ (actuellement 8) |
| Sequences 4+ ingredients matchant AN | 1+ |
| Anomalies INGR+INGR+INGR | 0 |
| Couverture table (glyphes connus) | 67% (deja atteint) |
| Couverture totale (table+K&A) | 85%+ |

## Ce qu'on GARDE de V7

- La TABLE des 18 logograms (fondation, ne change pas)
- Le systeme de quantites (a=ana, i=1, n=dr.)
- Les EVA variants (v12/loaders/eva_variants.py)
- Le nomenclator italien (4466 noms)
- La matrice 5-corpora (230 ingredients)
- Le fix aiin ≠ aquam
- Le format 3 lignes (EVA/TYPE/LAT)

## Ce qu'on AJOUTE

- Scoring par REGLES (pas probabilites)
- Selection par LIGNE (pas par mot)
- Detection d'anomalies automatique
- Pipeline qui teste TOUTES les variantes EVA
- Registre d'ingredients cumule

## Estimation

- Etape 1-3 : 1 session (fondations)
- Etape 4-5 : 1 session (pipeline + debug)
- Etape 6-7 : 1 session (decode + registre)
- Total : 3 sessions pour le decode complet des recettes
