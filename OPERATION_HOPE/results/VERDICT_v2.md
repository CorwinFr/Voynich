# OPERATION HOPE - VERDICT v2
## Date: 2026-04-11 - Apres tests discriminants

---

## RESULTATS TESTS DISCRIMINANTS

### Test 1: Co-occurrence (mot precedent -ain vs -aiin en pharma)

**RESULTAT : NEGATIF pour l'hypothese dose**

Les mots qui precedent -ain et -aiin sont les memes (chedy, qokeey, qokeedy, shedy...).
Jaccard similarity des contextes = 0.32.
La distribution des mots suivants est quasi-identique (diff max < 2%).

Si -ain et -aiin encodaient des doses differentes, on attendrait des ingredients differents devant chaque suffixe. Ce n'est pas observe.

### Test 2: Decomposition prefixe x suffixe x section

**RESULTAT : SIGNAL PERSISTANT**

Le ratio -aiin:-ain pour le MEME prefixe varie selon la section :

| Prefixe | Pharma | Herbal | Balnea |
|---------|--------|--------|--------|
| d- | 3.3:1 | 6.7:1 | 1.8:1 |
| qok- | 1.1:1 | 6.6:1 | 0.6:1 |
| ok- | 1.3:1 | 3.9:1 | 0.7:1 |
| ot- | 1.4:1 | 5.5:1 | 0.5:1 |
| k- | 1.4:1 | 7.3:1 | 0.4:1 |

Pattern constant : herbal >> pharma >> balnea pour le ratio -aiin:-ain.
Ce n'est PAS explicable par une grammaire uniforme.

### Test 3: Position dans la ligne

**RESULTAT : NEGATIF pour -ain/-aiin comme doses**

Distribution positionnelle quasi-uniforme (24-25% debut, 17-22% reste).
Pas de pic en position 2-3 comme attendu pour des doses.

EN REVANCHE, -eey et -eol ont des pics en debut de ligne (26-34%), suggerant des roles d'action/marqueur d'ingredient.

### Test 4: Balnea par folio

**RESULTAT : SIGNAL POSITIF**

Distribution heterogene : f75r est -ain dominant (41:6), f76v est -aiin dominant (6:30).
Compatible avec des contenus differents par folio, pas une grammaire fixe.

### Test 5: Triple suffixe par section

**RESULTAT : BALNEA SE DISTINGUE**

| Section | -eey | -edy | -ain | eey/edy |
|---------|------|------|------|---------|
| Pharma | 1034 | 1649 | 813 | 0.63 |
| Herbal | 267 | 440 | 227 | 0.61 |
| Balnea | 319 | 1758 | 460 | 0.18 |
| Astro | 168 | 71 | 24 | 2.37 |

Balnea a massivement plus de -edy que de -eey (ratio 0.18 vs 0.63 ailleurs).
Astro a massivement plus de -eey que de -edy (ratio 2.37).

---

## SYNTHESE

### Hypothese "i = chiffre" (a-i-n = 1, a-ii-n = 2)

| Critere | Resultat |
|---------|----------|
| Contextes differents | NEGATIF (memes mots avant/apres) |
| Position de dose | NEGATIF (distribution plate) |
| Ratio variable par section | POSITIF (inexplique par grammaire) |
| Ratio variable par prefixe | POSITIF (qok- ratio tres different de d-) |
| Balnea heterogene | POSITIF (variation par folio) |

Score: 3 positifs, 2 negatifs. L'hypothese est AFFAIBLIE mais pas eliminee.

### Interpretation alternative

Le systeme -ain/-aiin n'est probablement PAS un simple compteur (1, 2, 3...) mais pourrait encoder une distinction morpho-semantique liee au type de section :
- En herbal (descriptions de plantes) : -aiin domine largement (mode descriptif)
- En pharma (recettes) : -ain et -aiin quasi-egaux (mode prescriptif)
- En balnea (bains) : -ain domine legerement (mode procedural different)

Cela ressemble plus a une FLEXION GRAMMATICALE dependante du registre qu'a un systeme de numeration.

### Tests restants

1. **Crib Aurea** : utiliser les recettes S03_AUREA connues pour tester si les patterns VMS pharma correspondent
2. **Co-occurrence structuree** : chercher des paires (prefixe+suffixe, prefixe+suffixe) qui se repetent comme des couples ingredient+dose fixes
3. **Comparaison AN** : aligner la structure de S01_AN sur les patterns VMS pharma

---

## VERDICT v2

**ON NE S'ARRETE PAS ENCORE.**

Le ratio variable par section/prefixe est un fait inexplique. Les tests co-occurrence et positionnels sont negatifs pour "i=chiffre", mais les attaques les plus discriminantes (crib Aurea, co-occurrence structuree) n'ont pas ete tentees.

Si CEUX-LA echouent, on arrete.
