# PLAN SESSION 13 — Attaque par Alignement Structurel

## Contexte — Où on en est

**Acquis solides (sessions 10-12, 36 insights) :**
- Le VMS n'est PAS un chiffre par substitution de lettres (test volvelle : score 0)
- C'est un système d'abréviations au niveau des MOTS (tironiennes personnelles)
- 18 logograms confirmés, 14 suffixes, gallows=88% en tête de bloc
- Structure de recette = VERB INGR DOSE INGR DOSE (match AN)
- INGR+PLANT=65% des mots, DOSE=15%, ratio identique à l'AN
- Groupes d'ingrédients entre doses : médiane=3 (AN ANA=2-4)
- `sal` = seul mot EVA identique au latin (sel, 49 occ)
- knowledge_base.json + structural_decode.json complets

**Ce qui manque :** identifier les mots individuels. On ne sait pas quel
mot EVA = quel ingrédient latin.

## APPROCHE : Encoder l'AN comme le VMS et chercher des isomorphismes

### Principe

On a 150 recettes AN avec chaque mot typé (VERB/INGR/DOSE/GRAM).
On a 285 blocs pharma VMS avec chaque mot typé (VERB/PLANT/INGR/DOSE/FUNC).

Si on réduit chaque recette à sa **signature structurelle** — la séquence
de types — on peut chercher des matchs :

```
VMS bloc X :  V I I I D I I D I I I D I I D I
AN recette Y: V I I I D I I D I I I D I I D I  ← MATCH !
```

Si deux signatures matchent, les INGR en position 2 du VMS = l'INGR
en position 2 de l'AN. On sait alors que ce mot VMS = cet ingrédient latin.

### Pourquoi ça peut marcher

1. Les recettes médiévales sont RIGIDES — la structure est fixe
2. On a 285 blocs VMS × 150 recettes AN = 42750 comparaisons
3. La médiane d'ingrédients/dose est la MÊME (3 vs 2-4)
4. Certains ingrédients sont quasi-universels (aqua, mel, succus)
5. Un match partiel (même séquence de types sur 10+ positions) est
   statistiquement improbable par hasard

### Les 3 niveaux d'attaque

**Niveau 1 : Signature de types (VERB/INGR/DOSE)**
- Réduire chaque recette à V I I D I I D I...
- Chercher des matchs exacts ou proches (edit distance ≤ 2)
- Rapide, beaucoup de faux positifs attendus

**Niveau 2 : Signature enrichie (+ longueur des mots)**
- Chaque position = (type, longueur_mot)
- Ex: (I,5)(I,7)(D,4)(I,3) vs (I,asari)(I,carpobalsami)(D,ana)(I,opii)
- La longueur du mot EVA contraint le mot latin possible

**Niveau 3 : Signature avec contraintes croisées**
- Si le mot EVA en position 5 = PLANT_f22r, et que la recette AN
  en position 5 contient "rosa", alors PLANT_f22r = rosa
- Propagation : un seul match confirme tous les autres dans la recette
- C'est le jackpot si ça marche

### Données disponibles

| Source | Recettes | Mots typés | Prêt |
|--------|----------|------------|------|
| VMS pharma | 285 blocs | 10889 mots | ✓ structural_decode.json |
| S01_AN | 150 recettes | 16192 tokens typés | ✓ RECIPE_DATASET |
| S02_CI | 141 entrées | 862 tokens | ✓ |
| S09_COLLECTIO | 3680 entrées | 274K tokens | ✓ |
| S05_MACER | 25 entrées | 24K tokens | ✓ |

### Plan d'exécution

**ÉTAPE 1 : Encoder l'AN en signature structurelle**
- Pour chaque recette AN : extraire la séquence de types
  VERB INGR INGR INGR DOSE INGR INGR DOSE...
- Normaliser : ignorer les GRAM/CONJ (ponctuation), garder V/I/D/U
- Résultat : 150 signatures

**ÉTAPE 2 : Encoder le VMS en même signature**
- Pour chaque bloc pharma : extraire la séquence
  VERB INGR INGR DOSE INGR DOSE...
- Utiliser le structural_decode reclassifié (INGR*=INGR)
- Résultat : 285 signatures

**ÉTAPE 3 : Alignement**
- Pour chaque paire (VMS_bloc, AN_recette) :
  - Calcul de distance d'édition entre signatures
  - Calcul de sous-séquence commune la plus longue (LCS)
  - Score = LCS / max(len_vms, len_an)
- Top matchs : les paires avec score > 0.5

**ÉTAPE 4 : Extraction des mappings**
- Pour chaque top match :
  - Aligner mot par mot
  - Si VMS[i] = INGR et AN[i] = INGR(rosa) → mapping candidat
  - Si VMS[i] = PLANT_f22r et AN[i] = INGR(rosa) → PLANT_f22r = rosa
- Convergence : un mapping qui apparaît dans 3+ paires = PROBABLE

**ÉTAPE 5 : Propagation**
- Chaque mapping confirmé contraint les paires suivantes
- Itérer : nouveau mapping → réduire les candidats → nouveau match

### Critères de succès

- Au moins 5 paires (VMS, AN) avec score > 0.5
- Au moins 3 mappings INGR_VMS → INGR_AN convergents
- Les mappings doivent être cohérents avec les fréquences (un mot
  fréquent dans le VMS doit mapper vers un ingrédient fréquent dans l'AN)

### Risques

- Les recettes VMS sont plus COURTES (moy=38 tok) que les AN (moy=108)
  → il faudra peut-être regrouper les blocs VMS (étoiles rouges+blanches)
- Le VMS utilise peut-être un AUTRE antidotaire que l'AN comme source
  → tester aussi CI, Collectio, Macer
- Les types VMS sont moins précis que les AN (nos FUNC reclassifiés
  en INGR* peuvent être faux)

### Fichiers à créer

| Fichier | Description |
|---------|-------------|
| session_13/step1_an_signatures.py | Encoder AN en signatures |
| session_13/step2_vms_signatures.py | Encoder VMS en signatures |
| session_13/step3_alignment.py | Alignement par LCS |
| session_13/step4_mappings.py | Extraction des mappings |
| session_13/step5_propagation.py | Propagation itérative |

### La question `sal`

`sal` (sel) apparaît 49 fois dans le VMS = identique au latin.
Si le système est des tironiennes, pourquoi `sal` n'est pas abrégé ?
Parce que `sal` est DÉJÀ court (3 lettres). Les tironiennes n'abrègent
que les mots longs. Les mots courts restent EN CLAIR.

Ça veut dire : d'autres mots courts du VMS pourraient aussi être en clair.
Candidats : `sol` (66x), `dal` (241x), `dar` (320x), `sar` (82x).
Sont-ils des mots latins ? sol=soleil, dar=? sar=?

C'est une piste complémentaire à tester.
