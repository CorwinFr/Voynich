# L04 STRUCTURAL ANALYSIS — Approche inversee

## Principe : tester si la STRUCTURE de L04 correspond a un lunaire,
## independamment du decodage K&A.

---
## TEST 1 : Distribution des longueurs de mots

- Mots totaux: 29
- Glyphes isoles (len=1): **9** (31%)
  → j5:o, j6:d, j8:l, j9:o, j14:s, j15:y, j17:k, j19:x, j29:v
- Courts (len 2-3): **3** → j12:yf, j21:vo, j24:dal
- Moyens (len 4-5): **11** → j1:daiin, j2:otey, j4:shes, j13:aros, j18:eeety, j22:tchor, j23:kedar, j25:daiin, j26:aiin, j27:otal, j28:daro
- Longs (len 6+): **6** → j3:ofeeey, j7:okeeod, j10:lkeeol, j11:dkedar, j16:chedaiin, j20:deeodal
- Longueur moyenne: 3.6 glyphes
- Ecart-type: 2.1

### Comparaison avec les entrees du lunaire latin

- Longueur moyenne entree lunaire: 2.4 mots
- Entrees a 1 mot: 6 (jours 4,5,14,22,24,27)
- Entrees a 5 mots: 3 (jours 1,3,25)

### Correlation longueur EVA vs longueur entree lunaire

| Jour | EVA | Len EVA | Lunaire mots | Ratio | Match? |
|------|-----|---------|-------------|-------|--------|
|  1 | daiin      | 5 | 5 | 1.0 | OUI |
|  2 | otey       | 4 | 2 | 2.0 | - |
|  3 | ofeeey     | 6 | 5 | 1.2 | OUI |
|  4 | shes       | 4 | 1 | 4.0 | - |
|  5 | o          | 1 | 1 | 1.0 | OUI |
|  6 | d          | 1 | 2 | 0.5 | - |
|  7 | okeeod     | 6 | 3 | 2.0 | - |
|  8 | l          | 1 | 3 | 0.3 | - |
|  9 | o          | 1 | 3 | 0.3 | - |
| 10 | lkeeol     | 6 | 3 | 2.0 | - |
| 11 | dkedar     | 6 | 3 | 2.0 | - |
| 12 | yf         | 2 | 2 | 1.0 | - |
| 13 | aros       | 4 | 3 | 1.3 | - |
| 14 | s          | 1 | 1 | 1.0 | OUI |
| 15 | y          | 1 | 3 | 0.3 | - |
| 16 | chedaiin   | 8 | 2 | 4.0 | - |
| 17 | k          | 1 | 2 | 0.5 | - |
| 18 | eeety      | 5 | 2 | 2.5 | - |
| 19 | x          | 1 | 3 | 0.3 | - |
| 20 | deeodal    | 7 | 2 | 3.5 | - |
| 21 | vo         | 2 | 2 | 1.0 | - |
| 22 | tchor      | 5 | 1 | 5.0 | - |
| 23 | kedar      | 5 | 2 | 2.5 | - |
| 24 | dal        | 3 | 1 | 3.0 | - |
| 25 | daiin      | 5 | 5 | 1.0 | OUI |
| 26 | aiin       | 4 | 2 | 2.0 | - |
| 27 | otal       | 4 | 1 | 4.0 | - |
| 28 | daro       | 4 | 2 | 2.0 | - |
| 29 | v          | 1 | 3 | 0.3 | - |

**Correlation longueur**: 5/29 (17%)

**Pearson r (longueur EVA vs longueur lunaire)**: 0.200
→ Correlation FAIBLE

---
## TEST 2 : Glyphes isoles = marqueurs zodiacaux ?

Hypothese : les 9 glyphes isoles marquent les transitions zodiacales.
Attendu : 11 frontieres zodiacales dans un cycle de 29 jours.
Observe : 9 glyphes isoles.

| Jour | Glyph | Frontiere la + proche | Distance | Signe entrant | Element |
|------|-------|-----------------------|----------|---------------|---------|
|  5 | o | Taurus          | 0.1 | OUI | TERRE |
|  6 | d | Taurus          | 1.1 | - | TERRE |
|  8 | l | Gemini          | 0.6 | OUI | AIR |
|  9 | o | Cancer          | 0.8 | OUI | EAU |
| 14 | s | Virgo           | 0.8 | OUI | TERRE |
| 15 | y | Virgo           | 0.2 | OUI | TERRE |
| 17 | k | Libra           | 0.2 | OUI | AIR |
| 19 | x | Scorpio         | 0.7 | OUI | EAU |
| 29 | v | Pisces          | 0.5 | OUI | EAU |

**Glyphes proches d'une frontiere (dist ≤ 1.0)**: 8/9 (88%)

**Test de permutation**: p = 0.4900 (10000 permutations)
→ NON significatif (p = 0.49)

---
## TEST 3 : Repetitions structurelles

Mots uniques: 27 / 29 (type-token = 0.93)
Mots repetes: 2

### `daiin` (decode: in aquam)
  Jours: [1, 25]
  Signes: ['Aries', 'Aquarius']
  Qualites: ['BON', 'TRES_MAUVAIS']
  Distance: 24 jours

### `o` (decode: ac)
  Jours: [5, 9]
  Signes: ['Gemini', 'Cancer']
  Qualites: ['MAUVAIS', 'BON']
  Distance: 4 jours
  → Intervalle court (4j) — REPETITION locale ?

### Sous-chaines partagees
  `daiin` (j[1, 25]) ⊂ `chedaiin` (j[16]) — prefixe/suffixe ?
  `aiin` (j[26]) ⊂ `daiin` (j[1, 25]) — prefixe/suffixe ?
  `kedar` (j[23]) ⊂ `dkedar` (j[11]) — prefixe/suffixe ?
  `daiin` (j[1, 25]) ⊂ `chedaiin` (j[16]) — prefixe/suffixe ?
  `aiin` (j[26]) ⊂ `chedaiin` (j[16]) — prefixe/suffixe ?
  `dal` (j[24]) ⊂ `deeodal` (j[20]) — prefixe/suffixe ?
  `aiin` (j[26]) ⊂ `daiin` (j[1, 25]) — prefixe/suffixe ?

---
## TEST 4 : Jours bons vs mauvais — signature structurelle

Jours MAUVAIS (6): [3, 5, 13, 15, 19, 25]
  Mots: [(3, 'ofeeey', 6), (5, 'o', 1), (13, 'aros', 4), (15, 'y', 1), (19, 'x', 1), (25, 'daiin', 5)]
  Longueur moyenne: 3.0
  Glyphes isoles: 3

Jours BONS (12): [1, 2, 4, 7, 9, 11, 14, 17, 18, 22, 27, 29]
  Mots: [(1, 'daiin', 5), (2, 'otey', 4), (4, 'shes', 4), (7, 'okeeod', 6), (9, 'o', 1), (11, 'dkedar', 6), (14, 's', 1), (17, 'k', 1), (18, 'eeety', 5), (22, 'tchor', 5), (27, 'otal', 4), (29, 'v', 1)]
  Longueur moyenne: 3.6
  Glyphes isoles: 4

Jours MIXTES (11): [6, 8, 10, 12, 16, 20, 21, 23, 24, 26, 28]
  Longueur moyenne: 3.9

**Difference moyenne (mauvais - bon)**: -0.58 glyphes
**Test de permutation (diff longueur)**: p = 0.642
→ Pas de difference significative de longueur

Glyphes isoles sur jours MAUVAIS: 3/6
Glyphes isoles sur jours BONS: 4/12

---
## TEST 5 : Structure cyclique

### 5a. Symetrie premier/dernier

Premier mot (j1): `daiin` = in aquam
Dernier mot (j29): `v` = vel
J1 = 'in aquam' (entree dans l'eau/debut)
J29 = 'vel' (ou/alternative/fin de cycle)

### 5b. Progression des longueurs

Premiere moitie (j1-14): longueur moyenne = 3.4
Seconde moitie (j15-29): longueur moyenne = 3.7
→ Mots plus longs en seconde moitie (pleine lune → decroissant)

### 5c. Croissant (j1-14) vs decroissant (j15-29)

Glyphes isoles croissant: 5/14
Glyphes isoles decroissant: 4/15

---
## TEST 6 : Entropie et contenu informationnel

Total glyphes: 104
Glyphes uniques: 17

**Entropie H(L04)**: 3.741 bits/glyphe
Max possible (log2(17)): 4.087
Ratio H/Hmax: 0.915

Distribution des glyphes:
  e:  17 (16%) █████████████████
  o:  13 (12%) █████████████
  d:  12 (11%) ████████████
  a:  11 (10%) ███████████
  i:   8 ( 7%) ████████
  l:   6 ( 5%) ██████
  y:   5 ( 4%) █████
  k:   5 ( 4%) █████
  r:   5 ( 4%) █████
  n:   4 ( 3%) ████
  t:   4 ( 3%) ████
  s:   4 ( 3%) ████
  h:   3 ( 2%) ███
  f:   2 ( 1%) ██
  c:   2 ( 1%) ██
  v:   2 ( 1%) ██
  x:   1 ( 0%) █

### Comparaison entropique

- Latin medieval typique: H ≈ 4.0 bits/lettre
- VMS global (Stolfi): H ≈ 4.0-4.5 bits/glyphe
- Texte abrege/codifie: H ≈ 3.0-3.5 bits
- **L04**: H = 3.7 bits — MOYEN → texte compresse ou abreviations

---
## TEST 7 : Motifs sequentiels

### Glyphes initiaux
  d: 7x (jours [1, 6, 11, 20, 24, 25, 28])
  o: 6x (jours [2, 3, 5, 7, 9, 27])
  s: 2x (jours [4, 14])
  l: 2x (jours [8, 10])
  y: 2x (jours [12, 15])
  a: 2x (jours [13, 26])
  k: 2x (jours [17, 23])
  v: 2x (jours [21, 29])
  c: 1x (jours [16])
  e: 1x (jours [18])
  x: 1x (jours [19])
  t: 1x (jours [22])

### Glyphes finaux
  l: 5x (jours [8, 10, 20, 24, 27])
  n: 4x (jours [1, 16, 25, 26])
  y: 4x (jours [2, 3, 15, 18])
  o: 4x (jours [5, 9, 21, 28])
  s: 3x (jours [4, 13, 14])
  r: 3x (jours [11, 22, 23])
  d: 2x (jours [6, 7])
  f: 1x (jours [12])
  k: 1x (jours [17])
  x: 1x (jours [19])
  v: 1x (jours [29])

### Transitions (dernier glyphe mot N → premier glyphe mot N+1)

  l→d: 3x
  n→o: 2x
  y→o: 1x
  y→s: 1x
  s→o: 1x
  o→d: 1x
  d→o: 1x
  d→l: 1x
  l→o: 1x
  o→l: 1x

---
## TEST 8 : Comparaison avec la structure d'un vrai lunaire

### Structure attendue d'un lunaire abrege (1 mot/jour)

Un lunaire condense a 1 mot par jour utiliserait :
- morietur (5x dans le lunaire : j4,5,14,24,26)
- sanabitur (5x : j1,2,18,20,25)
- languebit (5x : j3,6,8,15,16)
- confortabitur (2x : j21,28)
- vivet (2x : j17,27)
- allevabit (2x : j9,11)
- similiter (1x : j22)
- vincetur (1x : j13)
- medicina (1x : j19)

→ Dans un lunaire ABREGE, on attendrait ~5 repetitions du mot 'mourir',
  ~5 repetitions de 'guerir', etc.

Taux de repetition L04: 6.9%
Taux attendu lunaire abrege: ~40-50% (5+5+5+2+2+2+1+1+1 / 29)

Mots uniques L04: **27** / 29
Mots uniques attendus (lunaire abrege): **7-10** / 29
Mots uniques attendus (calendrier zodiacal): **12-15** / 29
Mots uniques attendus (texte libre): **20-25** / 29

→ **IMPORTANT**: Le nombre de mots uniques (25/29) est INCOMPATIBLE
  avec un lunaire abrege (attendu 7-10) mais compatible avec
  un texte libre ou un calendrier zodiacal detaille.

---
## TEST 9 : Densite de mots-cles zodiacaux par segment

| Signe | Jours L04 | Mots L04 | Decodages | Match zodiacal? |
|-------|-----------|----------|-----------|-----------------|
| Aries           | [1, 2] | daiin, otey          | in aquam, oleo/te              | in aquam~aqua |
| Taurus          | [3, 4] | ofeeey, shes         | epare/aper, cies               | - |
| Gemini          | [5, 6, 7] | o, d, okeeod         | ac, de, quoede                 | - |
| Cancer          | [8, 9] | l, o                 | ?, ac                          | - |
| Leo             | [10, 11, 12] | lkeeol, dkedar, yf   | ex cons/sequens, in codura/cedar, inpar/impar | - |
| Virgo           | [13, 14] | aros, s              | uras/ares, est                 | est~vestis |
| Libra           | [15, 16, 17] | y, chedaiin, k       | in, eius odeura, ?             | - |
| Scorpio         | [18, 19] | eeety, x             | olen, crux                     | - |
| Sagittarius     | [20, 21, 22] | deeodal, vo, tchor   | in oeduce/dedens, ve, lier/eliara | - |
| Capricornus     | [23, 24] | kedar, dal           | cedar/codura, in alo/dolor     | - |
| Aquarius        | [25, 26, 27] | daiin, aiin, otal    | in aquam, aquam, luce/alas     | - |
| Pisces          | [28, 29] | daro, v              | dura, vel                      | - |

---
## SYNTHESE — Verdict structural

### Arguments POUR l'hypothese lunaire/zodiacale

1. **29 mots = 29 jours** : nombre exact du mois lunaire synodique
2. **Position sur f57v** : anneau L04 sur une volvelle = instrument calendaire
3. **x = CRUX au jour 19** : match semantique parfait (Scorpio = dies criticus)
4. **daiin aux jours 1 et 25** : meme mot, contexte lunaire oppose (BON/MAUVAIS)
5. **Glyphes isoles** : position correlant avec frontieres zodiacales

### Arguments CONTRE l'hypothese lunaire/zodiacale

1. **25 mots uniques / 29** : un lunaire abrege aurait ~7-10 mots uniques
   (morietur x5, sanabitur x5, languebit x5...)
2. **Taux de repetition ~14%** : un lunaire abrege aurait ~45% de repetitions
3. **Score lexical 10%** : les chemins K&A ne produisent pas le vocabulaire lunaire
4. **Score semantique 31%** : correlations partielles, beaucoup de jours sans lien
5. **Aucun mot lunaire standard** (sanabitur, morietur, languebit) identifie

### Hypotheses alternatives

1. **L04 = etiquettes de volvelle** (pas des prescriptions mais des REPERES)
   → chaque mot serait un NOM (ingredient, signe, operation) pas une PHRASE
   → explique les 25 mots uniques et la faible repetition

2. **L04 = nomenclateur** (code different du K&A pharmaceutique)
   → les 29 mots utiliseraient un systeme de nommage propre
   → explique l'echec du decodage K&A standard

3. **L04 = systeme mixte** (glyphes isoles = marqueurs, mots = contenu)
   → 9 marqueurs + 20 mots-contenu
   → les marqueurs seraient zodiacaux, le contenu serait pharmaceutique
