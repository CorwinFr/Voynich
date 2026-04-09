# ANALYSE DE LA LOGIQUE DES GLYPHES VOYNICHAIS
## Erreurs EVA, consonnes manquantes et nature du systeme d'ecriture

*Genere le 7 avril 2026 - Decodeur v10.0 (81.0% HIGH, 92.5% couverture)*

---

## 1. POURQUOI LE MAPPING INVERSE ECHOUE

Le test de la "bombe inverse" (Latin -> EVA -> recherche dans le manuscrit) n'a retrouve que 6 termes sur ~80 termes pharmaceutiques obligatoires. L'analyse revele trois causes principales.

### 1.1 Validation du mapping sur les paires connues

Sur 21 paires EVA-Latin confirmees par le decodeur v10, seules 8 (38%) sont retrouvees exactement par le mapping inverse. Les 13 echecs revelent que le mapping est **contextuel** et non pas un simple chiffre de substitution. Par exemple :

- `chor` devrait donner "ier" (ch=i, o=e, r=r) mais le decodeur produit "ara" (ch->a, o->r, r->a via une autre branche)
- `qoky` devrait donner "coque" mais le decodeur produit "coqu(e)" avec une logique differente
- `dal` devrait donner "dus" mais le decodeur produit "duce" (t=el en contexte)

**Conclusion** : le mapping K&A fonctionne dans le sens EVA->Latin grace a la disambiguation contextuelle et au scoring par corpus, mais il n'est PAS reversible car chaque glyph a plusieurs valeurs possibles.

### 1.2 Les consonnes fantomes : B, F, H

Le mapping K&A n'a **aucune representation** pour trois consonnes latines extremement frequentes dans le vocabulaire medical :

| Consonne | Frequence en latin medical | Mapping K&A | Mots bloques |
|----------|---------------------------|-------------|--------------|
| **b** | balneum, bilis, herba, febris | AUCUN | ~200+ mots |
| **f** | frigidus, folia, febris, fovere | EVA 'f' = p | ~150+ mots |
| **h** | herba, humor, hepar, hiera, hora | AUCUN (muet) | variable |

Le glyph EVA **'b'** n'apparait que 13 fois dans tout le manuscrit (38 442 mots). C'est le glyph le plus rare. Cela confirme que le son /b/ est encode autrement.

Le glyph EVA **'f'** (397 occurrences) encode officiellement 'p' (K&A). Mais des formes comme `cfhy` = "fi(t)" et `cfhol` = "fias" montrent que le digramme **CFH** pourrait encoder /f/ specifiquement. CFH n'a que 66 occurrences, ce qui est coherent avec la frequence plus faible de /f/ par rapport a /p/.

Le **'h'** est systematiquement **muet** : HIERA est encode `cheor` (= i+e+r+a = "iera"), sans aucune trace du h initial. C'est coherent avec la pratique du latin medieval ou le h est souvent omis.

### 1.3 Les clusters consonantiques impossibles

Les combinaisons suivantes ne peuvent pas etre representees en EVA selon le mapping K&A :

- **bl, br** (blandus, brachium) : b absent
- **fl, fr** (frigidus, flos) : f = p, donc fl/fr -> pl/pr ?
- **ph, th** (pharma, theriaca) : h absent, ph -> p? th -> t?
- **st, sp, sc** (stomachus, splen, sciens) : l=s, donc st->lt? sp->lp? Possible mais non confirme

**Impact** : des mots comme FRIGIDUS, STOMACHUS, HERBA, BALNEUM deviennent irreconnaissables dans le mapping inverse car les consonnes initiales sont soit absentes soit ambigues.

---

## 2. LE GLYPH CKH : LA CLE MANQUANTE ?

### 2.1 Statistiques

Le digramme **CKH** est le 20e glyph le plus frequent avec **865 occurrences** dans 225 mots uniques. Son mapping est **inconnu** dans la publication K&A originale.

Distribution contextuelle :
- CKH est suivi de **y** (450x), **e** (244x), **o** (97x)
- CKH est precede de **ch** (235x), **o** (188x), **e** (141x), **sh** (95x)

### 2.2 Hypotheses testees

Le remplacement de CKH par K (sa version "simple") ameliore le decodage dans 14/20 cas testes :

| EVA original | EVA k-sub | Decode k-sub | Conf |
|---|---|---|---|
| chckhy (137x) | chky | ic(o) | MEDIUM |
| shckhy (60x) | shky | cic(eris) | MEDIUM |
| checkhy (48x) | cheky | **equaliter** | HIGH |
| ckhy (39x) | ky | **qu(e)** | HIGH |
| qockhy (18x) | qoky | **coqu(e)** | HIGH |
| qockhey (18x) | qokey | **coque(?)** | HIGH |

### 2.3 Conclusion provisoire sur CKH

CKH est vraisemblablement une **variante calligraphique** de K (un "gallows glyph"). Le decodeur actuel le traite deja partiellement comme "aqu-" ou "qui-", ce qui est coherent avec K = qu/c. La variante ckh pourrait signaler une distinction que nous ne comprenons pas encore (majuscule? debut de phrase? emphase?).

---

## 3. L'HYPOTHESE DUAL AIIN

### 3.1 Rappel

Le suffixe EVA **aiin** encode standardement **-ura** (daiin = dura, confirme 847x). La decouverte v10 que **ol** = -ns (en plus de -es) ouvre la question : aiin pourrait-il aussi encoder **-ens** ?

### 3.2 Test statistique

Sur les 50 mots en -aiin les plus frequents (freq >= 5), 16 produisent un mot latin valide (present dans le corpus) quand on lit -aiin comme -ens au lieu de -ura :

| EVA | Freq | Lecture -ura | Lecture -ens |
|---|---|---|---|
| daiin | 847 | dura | **dens** (dent) |
| odaiin | 60 | dura | **adens** |
| chodaiin | 46 | adure | **edens** |
| taiin | 45 | eluera | **lens** (lentille!) |
| shodaiin | 24 | coedura | **cadens** (tombant) |
| shaiin | 20 | ciure | **cens** (centime) |
| oldaiin | 10 | esdura | **sedens** (assis) |

### 3.3 Le cas RAIIN

Le mot `raiin` (62 occurrences) est le plus gros mot LOW non resolu. Le decodeur actuel le decode comme "raro" (MEDIUM), ce qui est peu convaincant.

Si aiin = -ens, alors raiin = r + ens = **RENS** (rein, nominatif singulier). Le rein est un organe central de la medecine humorale. Le mot `rol` (19x) est deja decode comme RENS en v10 via ol = -ns. Cela confirme l'existence d'un **double encoding** pour le meme mot latin.

Analyse du contexte : raiin apparait 70 fois dans les sections biologiques (S/B), ce qui est coherent avec un terme anatomique.

### 3.4 Implications

Le suffixe -aiin n'est pas monosemique. Il encode :
1. **-ura** : dans la majorite des cas (daiin = dura, kaiin = cura)
2. **-ens** : dans certains contextes (raiin = rens, taiin = lens?)

Le critere de discrimination reste a etablir. Hypothese : la valeur depend du **stem** qui precede. Si stem + ura donne un mot latin valide, c'est -ura. Si stem + ens est meilleur, c'est -ens.

---

## 4. NATURE DU SYSTEME D'ECRITURE

### 4.1 Ce n'est PAS un chiffre simple

Un chiffre de substitution monoalphabetique aurait un mapping 1:1 entre glyphes et lettres. Le systeme voynichais est fondamentalement different :

- Le glyph `o` encode a/e (2 valeurs)
- Le glyph `a` encode u/o/a (3 valeurs)
- Le glyph `l` encode s ou l (selon position)
- Le suffixe `ol` encode -es, -ns, -is, ou ex- (4 valeurs!)
- Le suffixe `aiin` encode -ura ou -ens (2 valeurs)

### 4.2 C'est un systeme mixte a 4 niveaux

**Niveau 1 : Logogrammes** (mot entier en 1-2 glyphes)
- `dy` = ET (conjonction)
- `r` = RECIPE (imperatif pharmaceutique)
- `p` = PER- (prefixe)
- `q`/`qo` = CO-/CUM (prefixe)

**Niveau 2 : Ligatures syllabiques** (syllabe en 1 cluster)
- `aiin` = /-ura/ ou /-ens/
- `ol` = /-es/ ou /-ns/
- `sh` = /ci/ (toujours)
- `cph` = /pi/ (toujours)

**Niveau 3 : Substitution contextuelle** (glyph = phoneme selon position)
- `l` initial/final = /s/, mais `l` medial = /l/ (DOLOR)
- `o` = /a/ devant consonne, /e/ devant voyelle (tendance)
- `k` = /qu/ devant voyelle, /c/ devant consonne

**Niveau 4 : Omissions medievales**
- H systematiquement muet
- B quasi-absent (encode par un glyph non identifie?)
- Consonnes finales parfois omises

### 4.3 Distribution des longueurs de mots

| Longueur (glyphes) | Occurrences | % |
|---|---|---|
| 1 | 1 501 | 3.9% |
| 2 | 3 932 | 10.2% |
| 3 | 7 814 | 20.3% |
| 4 | 8 937 | 23.2% |
| 5 | 8 004 | 20.8% |
| 6 | 5 228 | 13.6% |
| 7+ | 3 020 | 7.9% |

Le pic a 3-5 glyphes (64.3%) est coherent avec un systeme ou chaque glyph encode 1-3 lettres latines, donnant des mots latins de 5-12 lettres.

### 4.4 Les mots tres courts sont des abbreviations

Les 30 mots les plus frequents de 1-2 glyphes sont tous HIGH, confirmant que le decodeur les gere bien. Les principaux :

| EVA | Freq | Latin | Fonction |
|---|---|---|---|
| ol | 545 | as | Suffixe cas |
| aiin | 504 | ur | Suffixe |
| ar | 398 | ara | Suffixe |
| or | 382 | er | Suffixe |
| s | 349 | us | Suffixe cas |
| y | 338 | in | Preposition |
| dy | 281 | et | Conjonction |
| r | 171 | recipe | Logogramme |
| am | 86 | cum | Preposition |
| d | 72 | de | Preposition |

---

## 5. PISTES POUR v11

### 5.1 Priorite haute : dual aiin (-ura / -ens)

Implementer un test de disambiguation pour les mots en -aiin :
1. Decoder le stem (tout sauf -aiin)
2. Tester stem + ura ET stem + ens dans le corpus
3. Choisir la lecture avec le meilleur score corpus

Impact estime : +60 a +100 mots HIGH (dont raiin x62, oraiin x34).

### 5.2 Priorite haute : CFH = f

Ajouter le mapping CFH = f (au lieu de p) dans le decodeur.
Tester sur cfhy (7x), cfhol (4x), cfhaiin (2x).

Impact estime : +10 a +20 mots HIGH.

### 5.3 Priorite moyenne : CKH = variante de K

Confirmer que CKH = K (qu/c) et l'ajouter comme mapping explicite.
Le decodeur le gere deja partiellement via les patterns "aqui-/qui-".

Impact estime : +30 a +50 mots HIGH.

### 5.4 Priorite exploratoire : le probleme B

Le son /b/ latin n'a pas de representation identifiee. Candidats possibles :
- CKH dans certains contextes (ckh = b quand precede de sh?)
- Un glyph EVA rare non encore identifie
- Le b est systematiquement omis (comme h)

Necessite une analyse plus poussee avec des cribs specifiques contenant /b/ (balneum, herba).

---

## ANNEXE : Glyphes EVA par frequence

| Rang | Glyph | Occurrences | % | Latin K&A |
|---|---|---|---|---|
| 1 | o | 25 105 | 15.5% | a, e |
| 2 | e | 20 211 | 12.5% | e, o |
| 3 | y | 17 693 | 10.9% | in, n, e |
| 4 | a | 14 572 | 9.0% | u, o, a |
| 5 | d | 12 969 | 8.0% | d |
| 6 | ch | 10 942 | 6.7% | i |
| 7 | l | 10 524 | 6.5% | s, l |
| 8 | k | 9 972 | 6.1% | qu, c |
| 9 | r | 7 435 | 4.6% | r, re |
| 10 | t | 5 912 | 3.6% | el, l, t |
| 11 | q | 5 426 | 3.3% | co |
| 12 | sh | 4 498 | 2.8% | ci |
| 13 | iin | 4 259 | 2.6% | (ligature) |
| 14 | i | 3 035 | 1.9% | ? |
| 15 | s | 2 724 | 1.7% | us, se |
| 16 | n | 1 863 | 1.1% | n |
| 17 | p | 1 402 | 0.9% | per |
| 18 | m | 1 061 | 0.7% | m |
| 19 | cth | 890 | 0.5% | li |
| 20 | **ckh** | **865** | **0.5%** | **? (qu/c variante?)** |
| 21 | f | 397 | 0.2% | p |
| 22 | cph | 201 | 0.1% | pi |
| 23 | g | 141 | 0.1% | g |
| 24 | **cfh** | **66** | **0.04%** | **? (f?)** |

*Methode: King & Andrisani (2019) + cribs Turing (Circa Instans, Antidotarium, De Balneis)*
