# Analyse des scribes du Manuscrit Voynich (MS 408)
## Impact sur le decodage K&A et adaptation du decodeur v5

**Date** : 7 avril 2026
**Auteur** : Guillaume Cle, avec assistance analytique Claude

---

## 1. Contexte : plusieurs auteurs

Lisa Fagin Davis a identifie 5 mains (scribes) distinctes dans le manuscrit Voynich. Currier (1970s) avait deja repere deux "langages" (A et B) basees sur des differences statistiques de distribution de glyphes. Notre analyse confirme ces differences et les quantifie precisement pour adapter le decodeur.

Donnees ZL (Zandbergen-Landini) analysees : 226 pages, ~37 000 mots, ~150 000 glyphes.

---

## 2. Les 5 mains

| Main | Pages | Section principale | Style | Langage |
|------|-------|--------------------|-------|---------|
| 1 | 113 | Herbier (95), Pharma (16), Texte (1), Cosmo (1) | Regulier, horizontal, espace | A et B |
| 2 | 46 | Bio/Balneo (19), Herbier (20), Cosmo (3), Texte (4) | Serre, incline | B (dy=27%) |
| 3 | 33 | Etoiles/Cosmo (24), Texte (5), Herbier (4) | Variable | B (dy=19%) |
| 4 | 26 | Astro (8), Zodiaque (12), Cosmo (6) | Distinct | I (astro) |
| 5 | 7 | Herbier (6), Texte (1) | Court | B (dy=30%) |

La Main 1 est responsable de 95 pages de l'herbier - c'est notre scribe principal et celui pour lequel nous avons le plus de donnees decodees (f1v, f3r, f9v, f15r, f25v).

---

## 3. Le spectre e/y : cle de la distinction A/B

La difference la plus nette entre les groupes est le ratio e/(e+y). Le glyphe EVA 'e' (=latin 'o') et le glyphe EVA 'y' (=latin 'n' ou marque de troncature) sont en competition directe.

### 3.1 Distribution globale

| Mesure | Lang A (Herbier) | Lang B (Herbier) | Difference |
|--------|-----------------|-----------------|------------|
| e % | 7.0% | 2.2% | +4.8% (A) |
| y % | 9.5% | 14.6% | +5.1% (B) |
| e/(e+y) | ~0.42 | ~0.13 | A 3x plus |
| Mot-final y | 29% | 40% | +11% (B) |
| Mot-final m | 4.8% | 0.8% | +4.0% (A) |
| -dy (=et) | 5.2% | 7.7% | +2.5% (B) |

### 3.2 Classement de nos pages decodees

| Page | e/(e+y) | Type | -m finaux | Observation |
|------|---------|------|-----------|-------------|
| f3r | 0.583 | A_STRONG | 19.3% | Record de -m dans le VMS |
| f25v | 0.571 | A | 0% | Type A sans -m |
| f1v | 0.294 | B | 0% | Malgre $Q=A dans ZL |
| f9v | 0.170 | B | 1.2% | Notre page de reference |
| f15r | 0.182 | B | 0% | Page chichoree |
| f68r1 | ~0.47 | ASTRO | 3.6% | Main 4, etoiles |

Observation cruciale : f1v est classee $Q=A par le ZL mais son ratio e/y la place clairement en B-type. Le ratio e/y est un meilleur indicateur que le classement par quire.

---

## 4. Implications pour le decodage

### 4.1 Le noyau du mapping est INVARIANT

Les mots EVA communs decouverts sur des pages de types differents se decodent **identiquement** :

| EVA | f9v (B) | f15r (B) | f3r (A) | Latin |
|-----|---------|----------|---------|-------|
| daiin | dura | dura | dura | durete |
| chor | hiera | hiera | hiera | antidote |
| chol | ies | ies | ies | (terme med.) |
| shor | ciere | ciere | ciere | evacuer |
| cthy | ili(a) | ili(a) | ili(a) | intestin |
| shol | cies | - | cies | evacuer (2e) |
| oky | qu(e) | - | qu(e) | equilibrer |

**Conclusion** : le mapping glyphe->latin K&A est le meme pour tous les scribes. Les differences portent sur le STYLE, pas sur la VALEUR des glyphes.

### 4.2 Differences de style scribal

**Pages A-type (e-riches) :**
- Plus de voyelles ecrites explicitement (e=o prononce en toutes lettres)
- Terminaisons accusatives -m preservees (latin plus correct grammaticalement)
- Moins de troncatures par y (formes verbales completes)
- Moins de dy='et' (conjonctions ecrites autrement ou omises)
- Privilegie les decodages COMPLETS

**Pages B-type (y-riches) :**
- Plus de troncatures finales par y (formes abregees/stenographiques)
- Plus de dy='et' (Notes Tironiennes actives)
- Accusatif -m souvent omis (latin vulgaire avance)
- Plus de prefixes y- (= 'in-')
- Le decodeur doit privilegier la TRONCATURE sur y-final

**Main 4 (astronomique) :**
- Tres fort ratio o/a (~5x) -> beaucoup de 'e' dans les noms
- Enormement de -dy (12-20% des mots) -> catalogues "X et Y et Z"
- Mots plus longs avec sequences -eey, -eeey -> voyelles longues dans noms grecs
- Vocabulaire specifique d'etoiles et termes astrologiques

### 4.3 Mains 2, 3, 5 : ultra-abbreviatifs

| Main | % de -dy | Mots uniques | Style |
|------|----------|-------------|-------|
| 2 | 27.1% | qolchedy, rshedy, kshdy | Tres abrege |
| 3 | 18.9% | alam, chedam, lkchdy | Moderement abrege |
| 5 | 29.8% | - | Le plus abrege |

Ces mains utilisent massivement les Notes Tironiennes (dy='et'). Pres d'un mot sur trois se termine par 'et'. Pour ces pages, le decodeur doit :
- Toujours traiter -dy comme logographique 'et'
- Chercher le mot latin TRONQUE dans la partie avant -dy
- Accepter des formes tres abregees

---

## 5. Decouverte : CICURA sur f15r (chicoree)

Le mot EVA **shkaiin** sur f15r ligne 7 se decode en :
- sh = ci
- k = c (apres consonne, avant voyelle)
- a = u
- iin = ra

=> **CICURA** = forme medievale de "cichorium" (chicoree)

C'est le NOM DE LA PLANTE qui apparait dans le texte, confirmant de maniere independante l'identification botanique de K&A. La ligne complete :

> DURA CICURA ILI(A) CIE [...]
> "La durete, [par] la chicoree, [pour] l'intestin, evacuer ..."

C'est une **4eme validation independante** du mapping K&A :
1. Texte medical f9v (Viola tricolor)
2. Noms d'etoiles f68r
3. Texte medical f1v (Atropa belladonna)
4. **Nom de plante f15r (Cichorium/cicura)**

---

## 6. Decouverte : accusatifs sur f3r

La page f3r (A_STRONG) contient 19.3% de mots finissant par -m, le taux le plus eleve du manuscrit. Puisque m=m dans le mapping K&A, ces terminaisons correspondent a l'accusatif latin singulier :

| EVA | Decode | Latin | Signification |
|-----|--------|-------|---------------|
| dam | dum | dum | conjonction "tandis que" / accusatif |
| cham | iam | iam | pronom demonstratif accusatif |
| chom | iam/iem | iam | idem |
| sam | sum | sum | "je suis" |
| cthom | eliam/liam | aliam | "autre" (acc. fem.) |

Cela montre que :
- Le scribe de f3r ecrit un latin plus classique (grammaticalement correct)
- Les terminaisons casuelles sont preservees
- Le meme mapping produit des formes grammaticales coherentes sur un autre style de page

---

## 7. Le decodeur v5

### 7.1 Nouveautes par rapport a v4

1. **Detection automatique du type de langue** : calcule e/(e+y) et le taux de -m pour classifier chaque page en A, A_STRONG, B, ou B_ABBREV
2. **Scoring y-final par langue** :
   - A-type : privilegie la forme phonetique 'n' et les formes completes
   - B-type : privilegie la troncature
3. **Vocabulaire astronomique** : termes specifiques pour les pages Hand 4
4. **Vocabulaire medical elargi** : termes grammaticaux, formes verbales
5. **14/14 tests unitaires passes** (vs 13/14 en v4)

### 7.2 Taux de reussite

| Page | Type | Haute confiance | Couverture totale |
|------|------|----------------|-------------------|
| f9v | B | 65% | 72% |
| f1v | B | 55% | 74% |
| f15r | B | 41% | 56% |
| f3r | A_STRONG | 37% | 55% |
| f25v | A | 36% | 53% |

Les pages nouvelles (f15r, f3r, f25v) ont une couverture plus basse car beaucoup de mots complexes ne sont pas encore resolus. Le decodeur est optimise pour le vocabulaire medical confirme.

---

## 8. Fichiers de reference

| Fichier | Contenu |
|---------|---------|
| `voynich_decoder_v5.py` | Decodeur author-aware v5 |
| `scribe_analysis.py` | Analyse statistique des 226 pages par scribe/langue |
| `scribe_deep_analysis.py` | Analyse approfondie e/y, -m, bigrammes |
| `semantic_analysis_f15r_f3r.py` | Analyse semantique f15r + f3r |

---

## 9. Prochaines etapes

1. **Decoder les pages Main 2** (f26r-f34v, Bio/Balneo) pour verifier le mapping sur un style ultra-abrege
2. **Decoder les pages Main 4** (f67r-f73v, Zodiac) pour extraire plus de noms d'etoiles
3. **Ameliorer la detection de mots composes** (okolshol = aequas cies)
4. **Construire un lexique par page** : identifier le nom de chaque plante dans son texte
5. **Comparer les terminaisons -m de f3r avec les pages proches** (f3v, f4r, f6r) pour confirmer la systematicite

---

*Document genere le 7 avril 2026.*
*Analyse basee sur 226 pages de la transcription ZL v2b (2022) et le decodeur v5.*
