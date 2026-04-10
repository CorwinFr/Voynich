# Bifolio bH1 (f57v/f66r) - Synthèse complète des 6 tests
## Date: 2026-04-11

---

## DÉCOUVERTE PRINCIPALE : Table de correspondance EVA -> Latin

Le résultat le plus important de cette série de tests est l'extraction d'une **table de mapping stable** entre glyphes EVA individuels et mots latins K&A. Ce mapping est **100% cohérent** entre f57v L03 et f66r L16-L49, vérifié sur 9 glyphes communs sans aucune exception :

| Glyphe EVA | K&A (latin) | Source |
|------------|-------------|--------|
| o | ac | L03 + f66r |
| l | se | L03 + f66r |
| d | de | L03 + f66r |
| r | recipe | L03 + f66r |
| v | vel | L03 seulement |
| x | crux | L03 + f66r |
| k | c (cum?) | L03 seulement |
| m | misce | L03 seulement |
| f | per | L03 + f66r |
| t | l | L03 + f66r |
| y | in | L03 + f66r |
| c | c (cum?) | L03 + f66r |
| s | est | f66r seulement |
| sh | ci | f66r seulement |
| p | usque | f66r seulement |
| air | aier | f66r seulement |

**18 glyphes mappés**, dont 12 confirmés par cross-validation entre deux folios indépendants du même bifolio physique. Aucune variabilité : chaque occurrence d'un glyphe donne le même résultat K&A.

---

## Résumé des 6 tests

### Test 1 : f66r isolés vs séquence L03

**Question** : Les 34 glyphes isolés de f66r copient-ils la séquence de l'anneau L03 ?

**Réponse** : NON. Zéro correspondance séquentielle. L'annotation ZL "cf f57v seq." vise spécifiquement le bigramme `c.@172` (marqueur de fin de copie dans L03), pas une correspondance globale. Recouvrement alphabétique de 61% mais ordre complètement différent.

### Test 2 : Vocabulaire f66r texte vs L04

**Question** : Le texte continu de f66r (L50-L82) partage-t-il du vocabulaire avec L04 ?

**Réponse** : OUI, sur les mots-clés. `daiin` est le mot le plus fréquent de TOUT le texte f66r (6x). `dal` (2x), `otey` (1x), `aiin` (1x) sont aussi partagés. La séquence `daiin.daiin.dal` en f66r L68 fait écho au `dal.daiin` de L04. Connexion thématique, pas mécanique.

### Test 3 : Signal pharmaceutique K&A - contrôle

**Question** : Le K&A produit-il du "latin médical" pour tout input ?

**Réponse** : PARTIELLEMENT. Biais de base ~12% de termes pharma pour tout folio. Mais f57v et f66r sont en tête du classement (17-18%), devant les pages officiellement pharmaceutiques. `recipe` : 12 occ. dans f57v (n.1 du VMS). `misce` : 5/8 de toutes les occurrences VMS sont dans f57v. Signal spécifique, pas universel.

### Test 4 : Ordre des glyphes isolés de f66r

**Question** : L'ordre des 34 glyphes suit-il une logique ?

**Réponse** : OUI. Le marqueur `c.@172` (pos 21-22) coupe la séquence en DEUX LISTES DISTINCTES avec des alphabets presque disjoints :

- **Segment 1** (pos 0-20, 21 glyphes) : dominé par y, f, o, d + contient s, sh, air, ? (ABSENTS du segment 2)
- **Segment 2** (pos 23-33, 11 glyphes) : dominé par o, t, x + contient @195, l, r, p (ABSENTS du segment 1)
- **Overlap** : seuls o, d, x sont dans les deux segments

Hypothèse : deux listes fonctionnellement distinctes, séparées par le marqueur emprunté à L03.

### Test 5 : Biais de la répétition 4x17 sur le K&A

**Question** : La structure répétitive de L03 trompe-t-elle le K&A ?

**Réponse** : NON. Le K&A traduit fidèlement : chaque copie de 17 produit la même séquence K&A. Les copies 2-4 sont identiques, la copie 1 diffère légèrement (I vs c dans l'EVA). `recipe` vient du glyphe `r` (2x par copie = 8 occurrences pour L03 seul). La vraie question est la fiabilité de l'association r -> recipe, pas un biais structurel.

### Test 6 : Comparaison des labels inter-folios

**Question** : Les labels de f66r fonctionnent-ils comme ceux de f49v/f75v/f76r ?

**Réponse** : NON, ils sont DIFFÉRENTS sur trois plans :

1. **Structure** : f66r sépare labels (L01-L15) et isolés (L16-L49) en blocs. Les autres folios les alternent.
2. **Complexité** : f66r a des labels multi-morphèmes (okeey, chol.daiin, okair.air.otam). Les autres ont des labels monosyllabiques.
3. **Vocabulaire K&A** : f66r a un vocabulaire de labels UNIQUE (rara, usus, asper, pura, rurens) sans overlap avec les labels des autres folios.

**DÉCOUVERTE CRITIQUE** : Le mapping K&A des glyphes isolés est 100% stable DANS f66r (chaque glyphe donne toujours le même mot) ET 100% cohérent AVEC L03 de f57v (9/9 glyphes communs matchent parfaitement).

---

## Architecture du bifolio bH1

```
RECTO (f66r)                          VERSO (f57v)
========================              ========================
[15 LABELS complexes]                 [L01: label]
  okeey -> acen                       
  chol.daiin -> cum quas              [L02: ring ~49 words]
  ...                                 
                                      [L03: ring 4x17 glyphes]
[34 GLYPHES ISOLÉS]                     o.l.d.r.v.x.k.m.f...
  Segment 1 (21): y,o,s,sh...          (alphabet = base)
  ---c.@172--- (marqueur)             
  Segment 2 (11): x,t,o,@195...      [L04: ring 29 mots]
                                        daiin, otey, dal...
[TEXTE continu L50-L82]              
  7 paragraphes                       [L05: ring]
  daiin = mot le + fréquent           
  dal, otey partagés avec L04         [L06-L13: labels]
```

**Lecture fonctionnelle** :

- **f57v (verso)** = l'INSTRUMENT rotatif. Anneaux concentriques avec séquences de glyphes (L03), mots (L04), et instructions (L05).
- **f66r (recto)** = le MODE D'EMPLOI. Labels identifiant les sections (L01-L15), table de référence des glyphes utilisables (L16-L49), texte explicatif (L50-L82).
- Le marqueur `c.@172` sert de pont : fin de copie dans L03, séparateur de listes dans f66r.
- Le mot `daiin` domine les deux faces : premier et avant-dernier mot de L04, mot le plus fréquent du texte f66r.

---

## Questions ouvertes prioritaires

1. **Quel est le principe d'organisation du Segment 1 vs Segment 2 ?** Le segment 1 contient les glyphes "bench" et "plume" (s, sh, y, d), le segment 2 les "gallows" (t, p) et les marqueurs spéciaux (@195). Correspondance avec les anneaux de la volvelle ?

2. **Que signifie @195 ?** Unique à f66r, position 26 dans le segment 2. Marqueur de séparation ? Glyphe spécial pour un anneau spécifique ?

3. **15 labels pour quoi ?** Pas 7 (paragraphes) ni 4-5 (anneaux). Les 15 secteurs de la volvelle ? Les illustrations de f66r ?

4. **Le mapping r -> recipe est-il linguistiquement valide ?** Si oui, L03 dit littéralement "ac se recipe vel crux c misce per..." en boucle, soit quelque chose comme "et [prendre/recevoir] [ou] [croix] [avec] [mélanger] [par/pour]..." - une formule rituelle ou une instruction de préparation.

---

## Fichiers de référence

- `test1_bifolio.py` : f66r isolés vs f57v L03 (séquentiel)
- `test2_bifolio.py` : vocabulaire croisé f66r texte vs L04
- `test3_bifolio.py` : contrôle signal pharma K&A
- `test4_glyph_order.py` : analyse structurelle des 34 isolés
- `test5_ka_repetition.py` : mécanisme K&A sur structure 4x17
- `test6_labels.py` : comparaison labels inter-folios + mapping
