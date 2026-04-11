# PROJECT_HOPE — Plan de la version finale

## Principe

Un seul repertoire, propre, reproductible. Fusionne le meilleur de notre
travail (sessions 6-7) et de l'autre IA (OPERATION_HOPE).

**UN SEUL vms_structured.json** : ZL comme texte primaire (consensus 2022),
variantes LSI importees dedans. Pas deux sources concurrentes.

---

## Architecture

```
project_hope/
|
|-- data/                           <- Sources brutes (en lecture seule)
|   |-- ZL.txt                      <- Transcription ZL v2b 2022 (primaire)
|   |-- LSI_ivtff_0d.txt            <- Transcription LSI interlineaire (variantes)
|
|-- vms/                            <- LE VMS structure (source unique de verite)
|   |-- build_vms.py                <- Construit le JSON depuis ZL + LSI
|   |-- vms_structured.json         <- LE fichier (folio > block > line > word)
|   |-- vms_stats.json              <- Statistiques globales
|   |-- VMS_SCHEMA.md               <- Documentation du schema
|
|-- referentiel/                    <- Pharmacopee medievale (PAS de VMS dedans)
|   |-- R01-R08 *.json              <- Copie depuis attacks/RECIPE_DATASET/
|   |-- S01-S16 *.json              <- Sources tokenisees
|
|-- analysis/                       <- Scripts d'analyse (lisent vms/ et referentiel/)
|   |-- analyze_suffixes.py         <- Systeme de 14 suffixes (session 7)
|   |-- analyze_icount.py           <- Distribution i-count (HOPE)
|   |-- analyze_dose.py             <- Hypothese dosage (HOPE)
|   |-- analyze_sections.py         <- Comparaison par section
|   |-- test_permutation.py         <- Tests de permutation (NOTRE ajout)
|   |-- test_benford.py             <- Test Benford (HOPE)
|
|-- attacks/                        <- Attaques computationnelles
|   |-- lib/
|   |   |-- loader.py               <- Charge vms/ + referentiel/
|   |   |-- candidate_store.py      <- Registre central de candidats
|   |   |-- scorer.py               <- Fonctions de scoring
|   |
|   |-- attack_crib.py              <- Multi-crib (recettes AN × blocs VMS)
|   |-- attack_frequency.py         <- Matching par distribution
|   |-- attack_grammar.py           <- Mapping suffixes → types
|   |-- attack_context.py           <- Bigrams autour des logograms
|   |-- attack_form.py              <- Test mot vs syllabe (FAIT — nomenclator)
|
|-- gpu/                            <- Attaques GPU
|   |-- gpu_mcmc.py                 <- Simulated annealing
|   |-- gpu_embeddings.py           <- word2vec + Procrustes
|   |-- gpu_neural.py               <- Neural decipherment
|
|-- results/                        <- Tous les resultats (persistants)
|   |-- candidate_registry.json     <- Registre de candidats
|   |-- attack_*.json               <- Resultats par attaque
|   |-- verdict_*.md                <- Verdicts iteratifs
|
|-- docs/                           <- Documentation
|   |-- PLAN.md                     <- Ce fichier (copie)
|   |-- BATTLE_PLAN.md              <- Plan de bataille (copie)
|   |-- BILAN.md                    <- Bilan d'etape
```

---

## Etape 1 : BUILD vms_structured.json (3-4h)

### Source primaire : ZL.txt
- EVA primary = lecture ZL (consensus Zandbergen 2022)
- Variantes [a:o] = dans eva_variants[]
- Marqueurs <%> = separateurs de bloc (etoiles)
- Marqueurs <$> = fins de section
- Annotations <!...> = metadata visuelles
- Glyphes speciaux @NNN;, {xxx}

### Source secondaire : LSI.txt
- Variantes des 5 transcripteurs (C, F, N, U + composite H)
- Alignement LIGNE PAR LIGNE (pas mot par mot — ZL a +1416 mots)
- Pour chaque ligne ZL, trouver la ligne LSI correspondante (meme folio.lnum)
- Comparer mot par mot DANS la ligne (alignement best-effort)
- Consensus = nombre de transcripteurs qui concordent (SANS H)

### Schema JSON final

```json
{
  "word_id": "f103r.1.0",
  "position": 0,
  "eva_primary": "pchedal",        // ZL (reference)
  "eva_variants": [                // LSI + ZL [a:o]
    {"source": "ZL", "alt": "pchedol"},
    {"source": "LSI_C", "eva": "pchedal"},
    {"source": "LSI_F", "eva": "pchedral"},
  ],
  "consensus": 3,                  // 3/4 transcripteurs independants d'accord
  "uncertain": false,
  "special_glyphs": null,
  "morphology": {
    "root": "pch",
    "suffix": "al",
    "suffix_type": "AL",
    "n_glyphs": 5,
    "is_logogram": false,
    "logogram_latin": null,
    "i_count": null,
    "e_count": null,
    "is_dose_candidate": false,
    "has_gallows": true
  }
}
```

### Blocs

| Section | Separateur | block_type |
|---------|-----------|------------|
| pharma | Etoile <%> | recipe |
| herbal | Nouveau paragraphe @P0 | paragraph |
| balnea | Etoile <%> (a verifier) | recipe ou paragraph |
| astro | Labels courts | label + paragraph |
| volvelle | Rings concentriques | ring |

### Validation

1. f103r = 18 blocs (etoiles)
2. Total folios = ~226
3. Total mots ZL ~ 38000-39000
4. Total mots LSI ~ 37000
5. Variantes LSI enrichies dans le JSON

---

## Etape 2 : COMPARER avec OPERATION_HOPE (1h)

Generer un rapport DELTA :

```
DELTA ZL vs LSI
===============
Folios : 226 vs 226 (=)
Lignes : 5229 vs 5220 (+9)
Mots : 38436 vs 37020 (+1416)
Blocs : 784 vs 818 (-34)

Mots divergents par folio :
  f1r  : ZL=235 LSI=213 (+22)
  f103r: ZL=531 LSI=525 (+6)
  ...

Mots ou ZL et LSI different :
  f1r.1.0  ZL=fachys  LSI=fyays  consensus=2/4
  ...

Total divergences : N mots (X%)
Mots a HAUTE INCERTITUDE (consensus <= 2/4) : M mots
```

Ce rapport identifie les mots qu'on ne doit PAS utiliser comme ancres
dans les attaques (trop incertains).

---

## Etape 3 : PORTER les analyses (2h)

Reprendre les analyses OPERATION_HOPE en les ameliorant :

| Script HOPE | Notre version | Amelioration |
|-------------|---------------|-------------|
| parse_vms.py | (integre dans build_vms.py) | Merge ZL+LSI |
| analyze_hypotheses.py | analyze_suffixes.py | + chi-carre + p-values |
| analyze_deep.py | analyze_dose.py | + permutation test |
| analyze_suffix_cross.py | analyze_sections.py | + Bonferroni correction |
| test_icount.py | analyze_icount.py | + validation externe |
| crib_aurea.py | attack_crib.py | + multi-crib 150 recettes |
| multicrib.py | (integre dans attack_crib.py) | + candidate_store |

### Ce qu'on AJOUTE (pas dans HOPE) :

1. **test_permutation.py** — pour chaque signal, shuffler et mesurer p-value
2. **candidate_store.py** — registre central multi-attaque
3. **scorer.py** — scoring combine (frequence + contexte + longueur + ...)
4. **GPU attacks** — embeddings, MCMC, neural

---

## Etape 4 : LANCER les attaques (4-8h)

Ordre d'execution (revise apres Tacuinum et HOPE) :

```
1. attack_form.py    — DEJA FAIT (nomenclator confirme)
2. analyze_*         — reprendre les analyses HOPE avec stats
3. attack_grammar.py — suffixes → types
4. attack_frequency  — matching par distribution
5. attack_crib.py    — multi-crib (18 recettes f103r × 150 AN)
6. attack_context.py — bigrams autour des logograms
7. gpu_embeddings.py — word2vec + Procrustes
8. CONVERGENCE       — CSP combine
```

---

## Differences cles avec OPERATION_HOPE

| Aspect | OPERATION_HOPE | PROJECT_HOPE |
|--------|---------------|--------------|
| Source primaire | LSI (1998) | ZL (2022) |
| Variantes | LSI 5 transcripteurs | ZL + LSI merge |
| Stats | Visuelles, pas de p-value | Chi-carre + permutation |
| Referentiel | Pas de referentiel pharma | R01-R08 (869 concepts) |
| Attaques | crib_aurea + multicrib | 7 CPU + 6 GPU attacks |
| Registre | Pas de candidats | candidate_store persistant |
| Faux positifs | Non detectes | Permutation systematique |
| Reproductibilite | Scripts ad hoc | Pipeline complet |

---

## Critere de succes

| Niveau | Critere |
|--------|---------|
| BRONZE | vms_structured.json construit + valide (f103r=18 blocs) |
| ARGENT | Delta ZL/LSI genere, mots incertains identifies |
| OR | 20 mots avec candidats a score > 0.75 dans le registre |
| PLATINE | 1 recette identifiee sur f103r |
| DIAMANT | Systeme d'ecriture compris et reproductible |

---

## Estimation temps total

| Etape | Temps |
|-------|-------|
| 1. Build vms_structured.json (ZL+LSI) | 3-4h |
| 2. Delta report | 1h |
| 3. Porter les analyses + stats | 2h |
| 4. Attaques | 4-8h |
| **TOTAL** | **10-15h** |
