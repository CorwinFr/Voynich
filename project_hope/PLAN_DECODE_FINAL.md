# PLAN FINAL — Décodage du Voynich par le Macer Floridus

## La situation

On a 2 mots confirmés (cth=vinaigre, yk=miel), 5 probables, 18 logograms,
et 6 folios ancres. La méthode (fingerprint matching) marche mais on
manque d'ancres. Ce plan exploite TOUT ce qu'on a, tolère les erreurs,
et pousse jusqu'au bout.

## PRINCIPE : on ne cherche plus la certitude, on cherche la masse

Chaque mapping individuel peut être faux. Mais si on décode 50 roots
et que 35 donnent du texte pharma cohérent, les 35 sont probablement
justes et les 15 erreurs se voient par incohérence.

---

## PHASE 1 — ÉTENDRE LES ANCRES (le levier le plus fort)

### 1A. Exploiter TOUTES les identifications botaniques

On a 106 folios dans botanical_anchors.json. On n'en utilise que 6.
Pour chaque folio identifié, chercher si la plante existe dans :
- Macer Floridus (25 chapitres)
- Circa Instans (141 entrées dans S02_CI)
- Tacuinum Sanitatis (358 entrées dans S12)
- Alphita (1714 entrées dans S10)

Même avec confidence 0.4, si 3 sources indépendantes concordent
→ ancre utilisable. Tolérer l'erreur.

**Action** : croiser les 106 IDs botaniques avec les 4 corpus.
Objectif : passer de 6 à 20-30 ancres.

### 1B. Utiliser les dessins comme ancres DIRECTES

Certains dessins sont ÉVIDENTS même sans Sherwood :
- Folio avec un tournesol = Helianthus (si post-1492) ou Chrysanthemum
- Folio avec une racine grosse = mandragore ou bryonia
- Folio avec des baies = sambucus ou juniperus

**Action** : parcourir les images herbal, identifier les 10 plantes
les plus évidentes visuellement. Ajouter comme ancres conf=0.3.

### 1C. Utiliser les noms dans les autres corpus

Le Circa Instans a 141 plantes. Le Tacuinum 358. L'Alphita 1714.
Pour chaque plante du CI/Tac/Alph, lister ses ingrédients associés.
Même méthode de fingerprint mais avec une matrice plus grande.

## PHASE 2 — FINGERPRINT MASSIF (la machine à décoder)

### 2A. Matrice étendue

Avec 20-30 ancres au lieu de 6 :
- 20 ancres = 190 paires (vs 15 avec 6)
- Chaque paire = contrainte d'élimination
- Les fingerprints deviennent BEAUCOUP plus discriminants
  (un vecteur de 20 bits vs 6 bits)

**Action** : rebuild la matrice de présence/absence avec toutes les ancres.
Pour chaque root : fingerprint 20-bit.
Pour chaque ingrédient (dans tous les corpus) : fingerprint 20-bit.
Match exact → mapping.

### 2B. Matching FLOU (tolérer l'erreur)

Les identifications botaniques ne sont pas parfaites.
Les corpus ne sont pas parfaits (variantes de texte).

Tolérer 1 bit de différence sur le fingerprint :
- Si root a fingerprint 11010100... et ingrédient a 11010110...
  (1 bit de diff) → mapping PROBABLE (pas confirmé)
- Si 2 bits de diff → mapping POSSIBLE
- Si 3+ bits → rejeté

**Action** : pour chaque root, trouver les ingrédients avec distance
de Hamming ≤ 1 sur le fingerprint.

### 2C. Propagation

Chaque mapping confirmé CONTRAINT les autres :
- Si root X = ingredient A, alors dans toute paire contenant X,
  A est "pris" et ne peut plus mapper vers une autre root
- Itérer : chaque nouveau mapping → réduire les candidats → nouveau match

**Action** : algorithme itératif d'élimination.

## PHASE 3 — ATTAQUE PAR CHAPITRE (le Macer mot-à-mot)

### 3A. Aligner chaque chapitre Macer avec son folio VMS

Pour chaque ancre (ex: f48v = Ruta) :
1. Lire le chapitre Macer Ruta : quels ingrédients, dans quel ORDRE ?
2. Lire le folio f48v : quelles roots, dans quel ORDRE ?
3. L'ORDRE d'apparition dans le texte est une contrainte
4. Le Macer mentionne la Rue elle-même en premier → le premier mot
   après le gallows = le code pour Ruta

**Action** : pour chaque ancre, extraire l'ORDRE des ingrédients dans
le Macer et l'ORDRE des roots dans le VMS. Aligner séquentiellement.

### 3B. Le premier mot = le nom de la plante

Dans CHAQUE folio herbal, le premier mot après le gallows est le
NOM DE LA PLANTE (comme dans le Macer, qui commence par le nom).

Si f48v = Ruta, le premier mot de f48v donne le code pour "ruta".
Si f9v = Viola, le premier mot de f9v donne le code pour "viola".

**Action** : extraire le premier mot content de chaque folio ancre.
Mapping direct : premier_mot(f48v) = ruta, premier_mot(f9v) = viola, etc.

### 3C. Les qualités galéniques

Chaque chapitre Macer commence par les qualités :
"Ruta est calida et sicca in tertio gradu"

Les mots du VMS juste après le premier ingrédient pourraient être
ces qualités. Le k/t ratio par folio corrèle (σ=0.175).

**Action** : pour chaque ancre, identifier les 2-3 mots après le gallows
et les matcher avec "calidus/frigidus" + "gradu I/II/III".

## PHASE 4 — ATTAQUE PAR RECETTE (pharma f103r-f116r)

### 4A. Chaque recette pharma utilise des ingrédients herbal

On sait que les roots herbal réapparaissent en pharma (session 9).
Avec nos mappings de Phase 2, on peut maintenant LIRE les recettes :
- root cth en pharma = "vinaigre"
- root yk en pharma = "miel"
- etc.

**Action** : appliquer tous les mappings sur les 285 blocs pharma.
Pour chaque bloc : combien de roots sont décodées ? Quel % de lecture ?

### 4B. Validation par cohérence pharmaceutique

Une recette décodée doit avoir du SENS en pharmacie médiévale :
- Miel + vinaigre = oximel (préparation classique !) ✓
- Plantain + vinaigre = cataplasme ✓
- Ail + miel = sirop ✓

**Action** : pour chaque recette partiellement décodée, vérifier
si la combinaison d'ingrédients existe dans la littérature pharma.

### 4C. Les recettes courtes comme validation

Les recettes de 5-8 ingrédients sont les plus faciles à valider.
Si on décode 4/5 ingrédients et que c'est une recette connue → VALIDÉ.

## PHASE 5 — BALNEA ET ASTRO (extension)

### 5A. Balnea = mêmes ingrédients, contexte différent

La section balnea utilise les mêmes roots + 11 exclusives.
Avec nos mappings, on peut lire les bains : "miel dans eau avec vinaigre..."

### 5B. Le Tacuinum pour les qualités galéniques

Le Tacuinum a chaud/froid/sec/humide pour 335 plantes.
Avec les mappings, on peut tester : les folios k-dominant sont-ils
effectivement les plantes "chaudes" du Tacuinum ?

## PHASE 6 — PRODUIRE UN DÉCODAGE LISIBLE

### 6A. Décoder f48v (Ruta) complètement

Avec tous les mappings : remplacer chaque root par son ingrédient latin.
Les suffixes → cas grammaticaux.
Les logograms → mots-outils.
Produire un texte latin lisible.

### 6B. Décoder f103r (pharma) bloc par bloc

18 blocs, chacun une recette.
Pour chaque recette : ingrédients, doses, verbes.
Comparer avec l'AN et le Macer.

### 6C. Produire le document de résultat

Un fichier MD ou PDF avec :
- La méthode (fingerprint matching)
- Les ancres utilisées
- Chaque mapping avec sa justification
- Le texte décodé de f48v et f103r
- Les validations croisées

---

## FICHIERS À CRÉER

| Script | Phase | Input | Output |
|--------|-------|-------|--------|
| extend_anchors.py | 1A | botanical_anchors + 4 corpus | extended_anchors.json |
| visual_anchors.py | 1B | images herbal | visual_anchors.json |
| fingerprint_massive.py | 2A-2C | extended_anchors + VMS | all_mappings.json |
| chapter_alignment.py | 3A-3C | Macer chapters + VMS folios | chapter_mappings.json |
| decode_pharma.py | 4A-4C | all_mappings + pharma blocks | decoded_pharma.json |
| decode_balnea.py | 5A | all_mappings + balnea | decoded_balnea.json |
| galenic_test.py | 5B | mappings + Tacuinum | galenic_validation.json |
| final_decode.py | 6A-6C | everything | F48V_DECODED.md, F103R_DECODED.md |

## TOLÉRANCE D'ERREUR

- Ancres conf=0.4 acceptées (pas juste 0.65+)
- Fingerprint flou : Hamming distance ≤ 1 = probable
- Recettes avec 1 ingrédient incohérent = toléré (variantes de texte)
- Si 70% d'une recette fait sens pharma → la recette est "décodée"

## CRITÈRE DE VICTOIRE

**Minimum** : 30 roots décodées, f48v lisible à 50%+
**Bon** : 100 roots décodées, 10 recettes pharma lisibles
**Exceptionnel** : 200+ roots, texte latin continu lisible

## ORDRE D'EXÉCUTION

```
Phase 1A (ancres étendues) → Phase 2A (fingerprint massif) → Phase 2C (propagation)
     ↓                              ↓
Phase 1B (visuels)          Phase 3A (chapitres)
                                     ↓
                            Phase 3B (premiers mots)
                                     ↓
                            Phase 4A (pharma decode)
                                     ↓
                            Phase 6 (output final)
```

Phase 1A est le LEVIER. Plus d'ancres = exponentiellement plus de mappings.
