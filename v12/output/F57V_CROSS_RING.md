# F57V CROSS-RING ANALYSIS

## 1. INVENTAIRE DES ANNEAUX

- L01 (centre): 1 mot = `dairal`
- L02 (exterieur): 49 mots
- L03 (cle): 51 elements (4 quadrants x ~17)
- L04 (cible): 29 mots
- L05 (interieur): 32 elements
- Centre (L06-L13): 8 labels

## 2. L03 — LA CLE DE CHIFFRE (4x17)

### Structure des 4 quadrants
```
Pos:  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17
Q1:   o  l  d  r  v  x  k  m  f  ?  t  r  ?  ?  y  I  @
Q2:   o  l  d  r  v  x  k  m  f  ?  t  r  ?  ?  y  c  @
Q3:   o  l  d  r  v  x  k  m  p  ?  t  r  ?  ?  y  c  @
Q4:   o  l  d  r  v  x  k  m  p  ?  t  r  ?  ?  y  c  @
```

### DIFFERENCES entre quadrants
- Position 3 : Q1=**d**/Q1alt=**j**, Q2-Q4=d
- Position 9 : Q1-Q2=**f**, Q3-Q4=**p** ← HOMOPHONIE f/p !
- Position 16: Q1=**I**, Q2-Q4=**c** ← I vs c
- Positions 10,13,14: glyphes speciaux (@169, @170, @171)

### Elements de L03 vs glyphes de L04

Glyphes L03: ['I', 'c', 'd', 'f', 'k', 'l', 'm', 'o', 'p', 'r', 't', 'v', 'x', 'y'] (14)
Glyphes L04: ['a', 'c', 'd', 'e', 'f', 'h', 'i', 'k', 'l', 'n', 'o', 'r', 's', 't', 'v', 'x', 'y'] (17)
**Partages**: ['c', 'd', 'f', 'k', 'l', 'o', 'r', 't', 'v', 'x', 'y'] (11)
L03 seulement: ['I', 'm', 'p'] (3)
L04 seulement: ['a', 'e', 'h', 'i', 'n', 's'] (6)

### L03 COMME ALPHABET DE REFERENCE

L03 contient 14 glyphes distincts (en excluant les speciaux).
L04 contient 17 caracteres distincts.
Intersection: 11/14 L03 glyphs appear in L04 (78%)

Les 3 glyphes de L03 ABSENTS de L04: m, p, I
Les 6 glyphes de L04 ABSENTS de L03: a, e, h, i, n, s

**OBSERVATION CRUCIALE**: Les glyphes de L03 sont presque
tous des CONSONNES dans le systeme K&A (o,l,d,r,v,x,k,m,f,t,y,c,p).
Les glyphes de L04 absents de L03 sont presque tous des VOYELLES
ou des elements vocaliques (a, e, i) plus h, n, s.

**HYPOTHESE**: L03 fournit les CONSONNES, L04 les VOYELLES+CONSONNES
= L03 est une cle de selection/permutation, pas un texte.

## 3. L05 — ANNEAU INTERIEUR

Elements: ['o', 'a', 'l', 'r', 'm', 'aiin', 'd', 'c', 'f', 'r', 'y', 'l', 'k', 'x', 'l', 'r', 'ar', 'o', 'r', 't', 'l', 'r', 'd', 'y', 'dar', 'teodar', 'otodal', 'sheky', 'oteeody', 'x', 'r', 'l']
Total: 32

Glyphes L05: ['a', 'c', 'd', 'e', 'f', 'h', 'i', 'k', 'l', 'm', 'n', 'o', 'r', 's', 't', 'x', 'y'] (17)
Partages L04-L05: ['a', 'c', 'd', 'e', 'f', 'h', 'i', 'k', 'l', 'n', 'o', 'r', 's', 't', 'x', 'y'] (16)

**Mots partages L04-L05**: {'l', 'x', 'y', 'o', 'aiin', 'k', 'd'}

**Mots partages L02-L04**: {'l', 's', 'v', 'y', 'o', 'otey', 'k', 'd', 'dal'}
**Mots partages L02-L05**: {'l', 'f', 'r', 'ar', 'y', 'o', 'a', 'k', 'd'}

## 4. PROFILS DE FREQUENCE — TOUS LES ANNEAUX

| Glyph | L02% | L03% | L04% | L05% | Centre% |
|-------|------|------|------|------|---------|
| a     |  11.6% |   0.0% |  10.6% |  10.3% |  20.0% |
| c     |   1.8% |   5.9% |   1.9% |   1.7% |   1.5% |
| d     |   9.1% |   5.9% |  11.5% |  10.3% |   7.7% |
| e     |   8.5% |   0.0% |  16.3% |   6.9% |   7.7% |
| f     |   2.4% |   3.9% |   1.9% |   1.7% |   1.5% |
| g     |   0.6% |   0.0% |   0.0% |   0.0% |   0.0% |
| h     |   4.3% |   0.0% |   2.9% |   1.7% |   1.5% |
| i     |   3.7% |   0.0% |   7.7% |   3.4% |   1.5% |
| j     |   0.0% |   2.0% |   0.0% |   0.0% |   0.0% |
| k     |   6.7% |   7.8% |   4.8% |   3.4% |   6.2% |
| l     |   6.1% |   7.8% |   5.8% |  10.3% |   9.2% |
| m     |   1.2% |   7.8% |   0.0% |   1.7% |   1.5% |
| n     |   1.2% |   0.0% |   3.8% |   1.7% |   0.0% |
| o     |  12.8% |   7.8% |  12.5% |  12.1% |  15.4% |
| p     |   1.2% |   3.9% |   0.0% |   0.0% |   1.5% |
| q     |   0.6% |   0.0% |   0.0% |   0.0% |   0.0% |
| r     |   6.7% |  15.7% |   4.8% |  15.5% |  15.4% |
| s     |  10.4% |   0.0% |   3.8% |   1.7% |   0.0% |
| t     |   1.8% |   7.8% |   3.8% |   6.9% |   3.1% |
| v     |   1.8% |   7.8% |   1.9% |   0.0% |   0.0% |
| x     |   0.0% |   7.8% |   1.0% |   3.4% |   0.0% |
| y     |   7.3% |   7.8% |   4.8% |   6.9% |   6.2% |

### Matrice de distance (Manhattan)

| | L02 | L03 | L04 | L05 | Centre |
|---|---|---|---|---|---|
| L02     | 0.00 | 0.98 | 0.40 | 0.48 | 0.49 |
| L03     | 0.98 | 0.00 | 1.11 | 0.74 | 0.83 |
| L04     | 0.40 | 1.11 | 0.00 | 0.49 | 0.64 |
| L05     | 0.48 | 0.74 | 0.49 | 0.00 | 0.36 |
| Centre  | 0.49 | 0.83 | 0.64 | 0.36 | 0.00 |

### Interpretation

Paire la plus PROCHE: **L05-Centre** (distance=0.36)
Paire la plus ELOIGNEE: **L03-L04** (distance=1.11)

### Distance de L04 a chaque anneau
  L04 ↔ L02: 0.40
  L04 ↔ L03: 1.11
  L04 ↔ L05: 0.49
  L04 ↔ Centre: 0.64

## 5. L03 COMME CLE — TEST

Si L03 est un alphabet de substitution (14 glyphes = 14 lettres),
et L04 utilise ces glyphes + des voyelles supplementaires,
alors L04 pourrait etre lu DIRECTEMENT en remplacant chaque
glyphe L03 par sa position dans la sequence.

L03 unique sequence: ['o', 'l', 'd', 'r', 'v', 'x', 'k', 'm', 'f', 't', 'y', 'c', 'p', 'I']
= 14 unique values

L03 → number mapping: {'o': 1, 'l': 2, 'd': 3, 'r': 4, 'v': 5, 'x': 6, 'k': 7, 'm': 8, 'f': 9, 't': 10, 'y': 11, 'c': 12, 'p': 13, 'I': 14}

### L04 words as L03-position numbers

| Pos | EVA | As L03 positions |
|-----|-----|-----------------|
|  1 | daiin      | 3 (a) (i) (i) (n) |
|  2 | otey       | 1 10 (e) 11 |
|  3 | ofeeey     | 1 9 (e) (e) (e) 11 |
|  4 | shes       | (s) (h) (e) (s) |
|  5 | o          | 1 |
|  6 | d          | 3 |
|  7 | okeeod     | 1 7 (e) (e) 1 3 |
|  8 | l          | 2 |
|  9 | o          | 1 |
| 10 | lkeeol     | 2 7 (e) (e) 1 2 |
| 11 | dkedar     | 3 7 (e) 3 (a) 4 |
| 12 | yf         | 11 9 |
| 13 | aros       | (a) 4 1 (s) |
| 14 | s          | (s) |
| 15 | y          | 11 |
| 16 | chedaiin   | 12 (h) (e) 3 (a) (i) (i) (n) |
| 17 | k          | 7 |
| 18 | eeety      | (e) (e) (e) 10 11 |
| 19 | x          | 6 |
| 20 | deeodal    | 3 (e) (e) 1 3 (a) 2 |
| 21 | vo         | 5 1 |
| 22 | tchor      | 10 12 (h) 1 4 |
| 23 | kedar      | 7 (e) 3 (a) 4 |
| 24 | dal        | 3 (a) 2 |
| 25 | daiin      | 3 (a) (i) (i) (n) |
| 26 | aiin       | (a) (i) (i) (n) |
| 27 | otal       | 1 10 (a) 2 |
| 28 | daro       | 3 (a) 4 1 |
| 29 | v          | 5 |
