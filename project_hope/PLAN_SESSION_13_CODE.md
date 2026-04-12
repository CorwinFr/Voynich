# SESSION 13 — Plan de Codage

## SCRIPT 1 : `encode_an_signatures.py`

**Input** : `attacks/RECIPE_DATASET/S01_AN.json` (150 recettes)
**Output** : `session_13/an_signatures.json`

```
Pour chaque recette AN :
  1. Extraire la séquence de types : [VERB, INGR, INGR, DOSE, INGR, ...]
  2. Simplifier : V=verb, I=ingr, D=dose+qty+unit, G=gram+conj+prep
  3. Ignorer les G (grammaire) → séquence pure V I I D I I D...
  4. Stocker : {
       "id": "AN_001",
       "name": "Recipe asari...",
       "signature": "VIIIDIIDIIIIIIIIIIIDIIID...",
       "signature_with_lengths": [(V,6),(I,5),(I,12),...],
       "ingredients": ["asarum","carpobalsamum",...],
       "n_ingr": 78,
       "n_dose": 7
     }
```

## SCRIPT 2 : `encode_vms_signatures.py`

**Input** : `session_11/structural_decode.json` + `reclassified_analysis.json`
**Output** : `session_13/vms_signatures.json`

```
Pour chaque bloc pharma VMS :
  1. Extraire la séquence reclassifiée : [VERB, INGR*, DOSE, PLANT, ...]
  2. Simplifier : V=verb+logo(recipe/misce), I=ingr+ingr*+plant, D=dose
  3. Ignorer FUNC restants (grammaire pure)
  4. Stocker : {
       "id": "f103r_B01",
       "signature": "VIIDIIIDIIID...",
       "signature_with_lengths": [(V,7),(I,4),(I,6),...],
       "roots": ["pched","shd","ol",...],
       "n_ingr": 35,
       "n_dose": 4
     }
```

## SCRIPT 3 : `align_signatures.py`

**Input** : `an_signatures.json` + `vms_signatures.json`
**Output** : `session_13/alignments.json`

```
Pour chaque paire (VMS_bloc, AN_recette) :
  1. Calculer LCS (Longest Common Subsequence) des signatures
  2. Score = LCS / max(len_vms, len_an)
  3. Si score > 0.4 : aligner mot par mot (Needleman-Wunsch simplifié)
  4. Stocker les top 10 matchs par bloc VMS

Optimisation : pré-filtrer par taille
  - Ignorer les paires avec |n_ingr_vms - n_ingr_an| > 20
  - Ignorer les paires avec ratio de taille > 3x
```

## SCRIPT 4 : `extract_mappings.py`

**Input** : `alignments.json` + `knowledge_base.json`
**Output** : `session_13/candidate_mappings.json`

```
Pour chaque alignement avec score > 0.4 :
  1. Pour chaque position alignée (VMS_ingr ↔ AN_ingr) :
     - Enregistrer : (eva_root, latin_name, score, source_pair)
  2. Agréger par eva_root :
     - Compter combien de paires donnent le même latin
     - Score = n_convergent / n_total
  3. Filtrer : garder si n_convergent >= 2 et score > 0.3
  
  Si VMS[i] = PLANT_fXXr → ancre forte (on sait que c'est une plante)
  Si VMS[i] = INGR_NNN → candidat à identifier
```

## SCRIPT 5 : `cleartext_short_words.py`

**Input** : `vms_structured.json` + dictionnaires latins
**Output** : `session_13/cleartext_candidates.json`

```
Hypothèse : les mots courts (2-3 lettres) sont en CLAIR
  sal = sel (CONFIRMÉ, 49 occ)
  
Test pour chaque mot EVA de 2-3 lettres :
  1. Est-ce un mot latin existant ?
  2. Le contexte est-il cohérent (position, section) ?
  3. La fréquence est-elle plausible ?
  
Dictionnaire : mots latins pharma de 2-3 lettres
  sal, sol, mel, fel, ros, lac, vas, vis, ius, cor, os, 
  par, ver, ars, dos, fex, pix, nux, lux, dux, rex
```

## SCRIPT 6 : `validate_and_decode.py`

**Input** : `candidate_mappings.json` + `cleartext_candidates.json`
**Output** : `session_13/F103R_DECODED_V2.md`

```
Appliquer tous les mappings sur f103r :
  1. Logograms → latin confirmé
  2. DOSE → marqueur
  3. PLANT_fXXr → mapping si trouvé
  4. INGR_NNN → mapping si convergent
  5. Mots courts → cleartext si confirmé
  6. Reste → EVA brut
  
Produire un décodage annoté avec niveaux de confiance
```

## ORDRE D'EXÉCUTION

```
Script 1 (AN) ──┐
                 ├──→ Script 3 (align) ──→ Script 4 (mappings) ─┐
Script 2 (VMS) ─┘                                                ├→ Script 6 (decode)
                                                                  │
Script 5 (cleartext) ─────────────────────────────────────────────┘
```

Scripts 1+2 en parallèle, puis 3, puis 4+5 en parallèle, puis 6.

## DONNÉES

Tout est déjà disponible :
- `attacks/RECIPE_DATASET/S01_AN.json` ✓
- `project_hope/session_11/structural_decode.json` ✓
- `project_hope/session_11/reclassified_analysis.json` ✓
- `project_hope/knowledge_base.json` ✓
- `project_hope/vms/vms_structured.json` ✓

## DURÉE ESTIMÉE

- Scripts 1+2 : 10 min (encodage)
- Script 3 : 30 min (42750 comparaisons, LCS = O(n²))
- Script 4 : 10 min (agrégation)
- Script 5 : 5 min (dictionnaire)
- Script 6 : 5 min (application)
- Total : ~1h de code + exécution
