# L04 CRACK — Etat apres session 5 (10 avril 2026)

## LA DECOUVERTE MAJEURE

**L04 n'est PAS encode en K&A.** Le profil de frequence des glyphes est
radicalement different du VMS global :
- `v` sur-represente de **33x** (0.06% VMS → 1.9% L04)
- `x` sur-represente de **11x** (0.09% VMS → 1.0% L04)
- `f` sur-represente de **4.7x**
- `h` sous-represente de **3x** (8.4% VMS → 2.9% L04)
- `c` sous-represente de **3x** (6.2% VMS → 1.9% L04)
- `q`, `p`, `m`, `g`, `b` = **ABSENTS** de L04

Ce n'est pas du bruit statistique. C'est un SYSTEME DIFFERENT.

## CE QU'ON A TESTE (exhaustif)

### Tests K&A (refutes)
- Crib semantique 5 lunaires → 31%
- Crib lexical latin beam=50 → 10%
- Crib zodiacal Fasciculus → ~12%
- Analyse structurelle 9 tests → INCOMPATIBLE avec lunaire

### Tests substitution simple (pas de resultat)
- Substitution caractere→lettre : 0 cascade >1
- Substitution token→lettre : 80 cascades a 1, toutes artefacts combinatoires
  (les mots de 4 tokens matchent tous les memes cibles de 4 lettres)
- 145 rotations de mapping mansions : 65 avec match, max 1 par rotation
- Crib drag exhaustif (tout target vs tout mot) : rien de coherent

### Tests structurels
- Permutation zodiacale : p=0.49 (non significatif)
- 27/29 mots uniques → pas un lunaire
- Entropie 3.74 bits → texte compresse, pas code repetitif
- Aucune difference bons/mauvais jours

## TOKENISATION CORRIGEE

Avec les vrais glyphes Voynich (ch, sh, ee, aiin = glyphes uniques) :
- **18 tokens uniques** (pas 17 caracteres)
- **82 positions totales** (pas 104 caracteres)
- Mots de **1 a 6 tokens** (pas 1 a 8 caracteres)
- `daiin` = 2 tokens (d + aiin), PAS 5 "lettres"
- `chedaiin` = 4 tokens (ch + e + d + aiin), PAS 8
- `aiin` seul = 1 token unique
- Le token `aiin` est partage par 4 mots (daiin x2, aiin, chedaiin)

## PARALLELES MANUSCRITS TROUVES

1. **Astrolabe al-Misri (1227, Oxford)** : 28 pictogrammes de mansions en
   cercle + **29 pointeurs d'etoiles** sur le rete → nombre 29 !
2. **BL Add. MS 25435** : volvelle allemande XVe s. avec 28 divisions lunaires
3. **Kitab al-Bulhan (Bodleian Or. 133, ~1400)** : 28 mansions illustrees,
   contemporain du VMS
4. **Ibn Arabi diagramme lunaire** : 28 lettres arabes = 28 mansions en cercle
5. **Aucun manuscrit trouve avec volvelle papier + noms de mansions en cercle**

## CE QUI N'A PAS MARCHE ET POURQUOI

1. **K&A sur L04** : mauvais systeme (profil glyphes different)
2. **Substitution simple** : trop de mots de meme longueur → bruit combinatoire,
   pas assez de contraintes pour discriminer
3. **Noms de mansions arabes** : translitterations trop variables (chaque source
   donne des noms differents), impossible de fixer une cible
4. **Approche mot par mot** : L04 a trop peu de texte (82 tokens) pour
   casser un chiffre par analyse statistique seule

## PISTES SURVIVANTES

### PISTE 1 : NOMENCLATEUR (code arbitraire)
Chaque mot = un code pour un concept (ingredient, operation, signe).
Pas de relation systematique glyphe→lettre.
→ Non cassable par substitution. Necessite un parallele textuel exact.

### PISTE 2 : SYSTEME DE L'INSTRUMENT
L04 ne se decode PAS seul. Sa signification emerge de l'INTERACTION
avec les autres anneaux (L02, L03, L05). Il faut analyser f57v
comme un systeme complet, pas anneau par anneau.

### PISTE 3 : AUTRE ALPHABET
L04 pourrait utiliser un alphabet different (arabe, hebreu, grec)
translittere en glyphes Voynich. Les 18 tokens pourraient correspondre
aux ~22 lettres hebraiques ou aux 28 arabes.

### PISTE 4 : SYSTEME NUMERIQUE
Les 9 glyphes isoles = chiffres. Les 20 mots-contenu = nombres
multi-chiffres ou codes numeriques.

### PISTE 5 : L03 COMME CLE
L03 (4×17 = 68 elements) est la "cipher key" de f57v. Les 17 elements
de L03 sont peut-etre les valeurs de substitution, et L04 utilise
ces valeurs pour encoder 29 positions.

## PROCHAINES ETAPES RECOMMANDEES

1. Analyser L03 EN DETAIL : les 17 elements + le symbole @172 + les
   variations entre quadrants (d/j, f/p, I/c)
2. Comparer L04 avec L02 et L05 : partage de tokens ? memes glyphes ?
3. Chercher le parallele textuel exact : un manuscrit medieval avec
   28-29 etiquettes sur un instrument rotatif
4. Essayer lecture en ARABE : mapper les 18 tokens EVA aux lettres arabes
   et voir si les mots forment des mots arabes
5. Examiner l'image HD de f57v glyph par glyph
