# L04 CRACK — BILAN TOTAL DE TOUS LES TESTS

Date : 10 avril 2026, session 5

## DECOUVERTE MAJEURE : L04 utilise un systeme d'encodage DIFFERENT

**Preuve** : frequence des glyphes radicalement differente du VMS global.
- v: 33x sur-represente, x: 11x, f: 4.7x
- h: 3x sous-represente, c: 3x
- q, p, m, g, b: ABSENTS
- Ce n'est pas du bruit. C'est un systeme different.

## TESTS EFFECTUES (EXHAUSTIF)

### 1. Tests K&A (REFUTES pour L04)
| Test | Score | Verdict |
|------|-------|---------|
| Crib semantique 5 lunaires | 31% | Signaux partiels |
| Crib lexical latin beam=50 | 10% | Fragile |
| Crib zodiacal Fasciculus | ~12% | Pas de valeur ajoutee |
| Analyse structurelle 9 tests | 27/29 uniques | INCOMPATIBLE lunaire |
| Permutation zodiacale | p=0.49 | NON significatif |

### 2. Tests substitution simple (AUCUN RESULTAT)
| Test | Resultat |
|------|----------|
| Substitution char→lettre vs noms mansions | 0 cascade >1 |
| Substitution token→lettre vs mansions | 80 cascades=1 (bruit) |
| 145 rotations mansion→position | Max 1 match/rotation |
| Crib drag exhaustif (tout target x tout mot) | 0 coherent |

### 3. Tests transposition/anagramme
| Test | Resultat |
|------|----------|
| Toutes permutations tokens (chaque mot) | 1 hit: aros=rosa |
| Toutes permutations caracteres (chaque mot) | 1 hit: aros=rosa |
| Rotations cycliques | 0 hit additionnel |
| Echanges de paires | 0 hit |
| Inversion (miroir) | 0 hit |
| Propagation du mapping aros=rosa aux autres mots | 0 cascade |

**Verdict : aros=rosa est probablement une COINCIDENCE (4 lettres, 24 permutations).**

### 4. Tests de chiffrement L03
| Test | Resultat |
|------|----------|
| Atbash sur alphabet L03 | Pas de mots reconnaissables |
| Caesar shifts (1-13) sur alphabet L03 | 0 hit |
| Position L03 → lettre latine (A-N) | 0 hit |
| L03 comme cle de permutation | Pas de pattern clair |

### 5. Tests linguistiques
| Test | Resultat |
|------|----------|
| Racines 3-consonnes (test arabe) | 20% (attendu 60-70%) → PAS arabe |
| Frequence arabe vs L04 | Pas de correspondance |
| Mapping frequence → mansions arabes | Gibberish |
| Mapping frequence → herbes latines | Gibberish |

### 6. Tests cross-ring (f57v)
| Test | Resultat |
|------|----------|
| L04 vs L02 (distance Manhattan) | 0.40 (le plus PROCHE) |
| L04 vs L03 | 1.11 (le plus ELOIGNE) |
| Mots partages L04-L02 | otey, dal, + glyphes isoles |
| Mots partages L04-L05 | aiin, + glyphes isoles |
| L03 consonnes vs L04 | 11/14 partages, L04 a les voyelles en plus |

### 7. Tests f68r1 (29 star labels)
| Test | Resultat |
|------|----------|
| K&A decode des 29 labels | 9/29 Perseus, aucun nom d'etoile clair |
| Comparaison noms astrolabe | 2/29 matches vagues (alioth, alnair) |
| Mots partages f68r1-L04 | daiin dans osdaiin(f68r1) et odaiin(f68r2) |
| Frequence glyphes f68r1 vs L04 | TRES differents (systemes differents) |

### 8. Tests de rotation mansions/herbes
| Test | Resultat |
|------|----------|
| 28 rotations x suffumigations (longueur tokens) | Best=offset 26 (8 matches longueur) |
| 28 rotations x herbes latines (longueur tokens) | Meme best offset |
| Propagation des matches de longueur | Aucune cascade |

## CE QU'ON SAIT MAINTENANT (CERTITUDES)

1. **L04 n'utilise PAS K&A** (frequences incompatibles)
2. **L04 n'est PAS un lunaire** (27 mots uniques vs 7-10)
3. **L04 n'est PAS une substitution monoalphabetique simple** (0 cascade)
4. **L04 n'est PAS de l'arabe** (20% racines trilitteres vs 60-70%)
5. **L04 n'est PAS un anagramme systematique** (seul aros=rosa, coincidence)
6. **L04 n'est PAS chiffre par L03** (atbash/caesar/position = 0 hit)
7. **L04 partage du vocabulaire avec L02** (otey, dal) et L05 (aiin)
8. **f68r1 a aussi 29 labels** mais dans le systeme VMS standard
9. **Le token `daiin`** est un pont L04 ↔ f68r1/f68r2 (apparait dans les deux)
10. **18 tokens uniques, 82 positions, mots de 1-6 tokens** apres tokenisation

## CE QUI RESTE COMME HYPOTHESES

### HYPOTHESE 1 : NOMENCLATEUR (code arbitraire)
Chaque mot L04 = un code arbitraire pour un concept.
Pas de relation systematique glyphe → lettre.
**Non crackable** par methodes cryptanalytiques classiques.
Necessite un parallele textuel exact (un autre manuscrit avec les memes codes).

### HYPOTHESE 2 : SYSTEME BIPARTITE
Les 9 glyphes isoles = marqueurs structurels (chiffres, separateurs, categories).
Les 20 mots-contenu = etiquettes en encodage partage avec L02.
Le fait que `otey` et `dal` apparaissent dans L02 ET L04 soutient cette idee.
→ L04 pourrait etre decodable par K&A SAUF pour les glyphes isoles qui
   sont des marqueurs, pas du texte. Le profil de frequence different
   s'expliquerait par la forte proportion de glyphes isoles (31%)
   qui "diluent" les frequences VMS standard des mots-contenu.

### HYPOTHESE 3 : VOLVELLE FONCTIONNELLE
L04 ne se decode pas seul. C'est un composant d'instrument dont le sens
emerge de l'interaction avec L02, L03, et L05. Les mots ne sont pas
du texte a lire mais des LABELS fonctionnels d'un calculateur.

## PROCHAINE ETAPE RECOMMANDEE

**TESTER HYPOTHESE 2** : Separer les 9 glyphes isoles et recalculer
les frequences de glyphes sur les 20 mots-contenu SEULEMENT.
Si les frequences des mots-contenu se rapprochent du VMS global,
alors K&A est valide pour ces mots et les glyphes isoles sont
un systeme separe (marqueurs/chiffres).
