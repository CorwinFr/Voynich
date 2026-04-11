# PLAN D'ITERATION — Corriger les 876 anomalies

## Situation actuelle

141 ingredients, 876 anomalies, ratio VERB:INGR = 1:13.5 (objectif 1:3-8)

| Anomalie | Count | Cause probable | Correction |
|----------|-------|---------------|------------|
| INGR_RUN (361) | 3+ ingredients d'affilee | Faux INGR = fonctions deguisees | Ajouter au FUNCTION_PATTERNS |
| FUNC_CHAIN (257) | 4+ fonctions d'affilee | Vrais ingredients non reconnus | Retirer du FUNCTION_PATTERNS ou identifier |
| ORPHAN_DOSE (222) | Dosage sans ingredient | Ingredient precede mal classifie | Reclassifier le mot precedent |
| NO_INGR (36) | Ligne sans ingredient | Ligne d'instruction pure ou tout mal classifie | Verifier manuellement |

## Strategie : 3 passes

### PASSE 1 : INGR_RUN — Reduire les faux ingredients

**Principe** : Si un mot est classifie INGR mais apparait 20+x dans les
recettes, c'est une FONCTION. Un vrai ingredient est RARE (1-10x par recette).

**Action** :
1. Extraire TOUS les mots classes INGR dans le decode global
2. Compter leur frequence GLOBALE dans f103-f116
3. Tout mot INGR apparaissant 30+x → ajouter a FUNCTION_PATTERNS
4. Regenerer le decode

**Seuils** :
- 50+x → certainement FUNCTION (ajouter automatiquement)
- 30-49x → probablement FUNCTION (verifier le decode K&A)
- 10-29x → peut-etre reel (verifier contre nomenclator)
- 1-9x → probablement reel (garder INGR)

**Verification** : Apres correction, les INGR_RUN doivent diminuer de 50%+.
Si un vrai ingredient est supprime par erreur (ex: aloe=30x), le matcher
l'aurait identifie et il serait protege.

**Risque** : Supprimer un vrai ingredient rare.
**Mitigation** : Ne jamais supprimer un mot qui matche le nomenclator ou la matrice.

### PASSE 2 : FUNC_CHAIN — Recuperer les ingredients caches

**Principe** : Une chaine de 4+ fonctions consecutives cache probablement
un ingredient que le classifieur ne reconnait pas.

**Action** :
1. Extraire toutes les FUNC_CHAIN (257 cas)
2. Pour chaque chaine, identifier le mot le plus LONG (probable ingredient)
3. Decoder ce mot par K&A avec variantes
4. Chercher dans le nomenclator/matrice
5. Si match → reclassifier en INGR, ajouter au registre

**Heuristique** : Dans une chaine func-func-func-func-func :
- Le mot le plus long (5+ chars) est probablement l'ingredient
- Les mots courts (2-3 chars) sont probablement des vrais fonctions
- Le mot qui ne matche aucun logogram est probablement l'ingredient

**Verification** : Chaque FUNC_CHAIN corrigee doit produire un pattern
valide (func→INGR→func ou func→INGR→DOSE).

**Gain attendu** : 50-150 ingredients supplementaires (1-3 par chaine).

### PASSE 3 : ORPHAN_DOSE — Reparer les dosages isoles

**Principe** : Un dosage doit suivre un ingredient. Si le mot precedent
est func, c'est que cet ingredient a ete mal classifie.

**Action** :
1. Pour chaque ORPHAN_DOSE, examiner le mot PRECEDENT
2. Si ce mot est classe func mais a 4+ chars → reclassifier en INGR
3. Si ce mot est un logogram court → regarder 2 mots en arriere
4. Decoder le candidat par K&A et chercher dans les corpora

**Verification** : Le pattern doit devenir INGR→DOSE (ou INGR→func→DOSE).

## Metriques cibles par passe

| Metrique | Actuel | Apres Passe 1 | Apres Passe 2 | Apres Passe 3 |
|----------|--------|--------------|--------------|--------------|
| INGR_RUN | 361 | <150 | <100 | <50 |
| FUNC_CHAIN | 257 | 257 | <100 | <80 |
| ORPHAN_DOSE | 222 | 222 | <150 | <80 |
| NO_INGR | 36 | <30 | <20 | <15 |
| Ingredients | 141 | ~130 (-faux) | ~200 (+recup) | ~220 |
| Ratio V:I | 1:13.5 | 1:10 | 1:8 | 1:5 |

## Implementation

### Script unique : `v12/analysis/fix_anomalies.py`

```
Entree : DECODE_GLOBAL_STATS.md + classifier.py
Sortie : classifier.py mis a jour + nouveau decode

Pour chaque PASSE :
  1. Analyser les anomalies
  2. Proposer des corrections (ajout/retrait FUNCTION_PATTERNS)
  3. Appliquer
  4. Regenerer le decode
  5. Recompter les anomalies
  6. Afficher le delta
```

### Protection des vrais ingredients

Mots JAMAIS ajoutes a FUNCTION_PATTERNS (proteges) :
- Tout mot matchant le nomenclator (4466 italiens)
- Tout mot matchant l'Antidotarium (114 ingredients)
- Tout mot matchant la matrice 2+ corpora
- Tout mot identifie dans le decode actuel (141 ingredients)

### Ordre d'execution

```
PASSE 1 (INGR_RUN) ← elimine les faux ingredients
    ↓
Regenerer decode
    ↓
PASSE 2 (FUNC_CHAIN) ← recupere les vrais ingredients caches
    ↓
Regenerer decode
    ↓
PASSE 3 (ORPHAN_DOSE) ← repare les dosages
    ↓
Regenerer decode
    ↓
Stats finales
```

## Critere de succes

- Anomalies totales < 200 (actuellement 876)
- Ingredients identifies > 200 (actuellement 141)
- Ratio VERB:INGR entre 1:3 et 1:8 (actuellement 1:13.5)
- 0 chaine de 6+ fonctions consecutives
- Au moins 5 folios avec 50+ ingredients identifies

## Folios prioritaires pour verification manuelle

Apres les 3 passes, verifier manuellement :

1. **f113r** (46 ingr, 52 anom) — le plus riche, doit s'ameliorer le plus
2. **f105v** (39 ingr, 55 anom) — le plus anomalique, beaucoup de INGR_RUN
3. **f107r** (41 ingr, 27 anom) — bon ratio, peu d'anomalies = deja correct ?
4. **f103r** (37 ingr, 39 anom) — notre reference, comparer avant/apres
5. **f116r** (32 ingr, 58 anom) — beaucoup de FUNC_CHAIN, ingredients caches
