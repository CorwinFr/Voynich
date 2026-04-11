# OPERATION HOPE — Trouver le systeme de numeration ou tout arreter

> "Aucun systeme medicinal n'existe sans dosages.
> Si on ne trouve pas les nombres, le VMS n'est pas pharmaceutique.
> Et si le VMS n'est pas pharmaceutique, tout s'effondre."

## Le probleme

On a identifie 16 logograms, 14 suffixes, un systeme de nomenclator.
Mais on n'a PAS trouve les NOMBRES. Pas de dosages confirmes.
Notre hypothese precedente (a=ana, i=1, n=drachme) est FAUSSE
(72 dosages sur f103r vs 7 dans l'Aurea).

Un apothicaire DOIT ecrire des quantites. Chaque jour. C'est vital.
".z.ii." (2 drachmes) dans l'AN. "drame et demie" dans le CI.
Si le VMS est pharma, les nombres sont DEDANS. On les cherche.

## Ce qu'on cherche

Dans un texte pharma medieval, les dosages apparaissent :
- APRES une liste d'ingredients : "myrrha crocus ana .z.ii."
- AVEC un marqueur "ana" (de chaque) ou "quantum sufficit"
- SOUS FORME de chiffres romains (.i. .ii. .iii. .iiii.)
  ou de mots (unam, duas, tres)
- AVEC une unite (drachma, uncia, libra, scrupulus, granum)
- EN POSITION FIXE dans la recette (pas au hasard)

## Les 10 pistes

### PISTE 1 — Les glyphes EVA "numeriques"
```
Priorite : ★★★★★
Duree : 30 min
```

Les glyphes EVA qui RESSEMBLENT a des chiffres :
- `i` seul = 1 ? (`ii` = 2, `iii` = 3 ?)
- `e` repete = quantite ? (`ee` = 2, `eee` = 3 ?)
- Les sequences `aiin`, `ain`, `in` contiennent `i` et `n`
- Le `n` final pourrait etre un SIGNE de fin de nombre

**Test :**
1. Lister TOUTES les sequences contenant `ii`, `iii`, `iiii` dans le VMS
2. Lister toutes les sequences `ee`, `eee`, `eeee`
3. Compter leur frequence et leur POSITION dans la ligne
4. Comparer avec la position des dosages dans S01_AN
5. Si les sequences `ii/iii` sont aux memes positions que les `.z.ii.` de l'AN → signal

### PISTE 2 — Les "bench" glyphes (bancs)
```
Priorite : ★★★★★
Duree : 30 min
```

Le VMS a des glyphes speciaux non-EVA standard :
- Les "bench" ou "gallows" variants
- Les marques dans les marges
- Les annotations entre les lignes

Certains de ces glyphes pourraient etre des CHIFFRES.
Le systeme de Currier note des "symbols" non-alphabetiques.

**Test :**
1. Chercher dans ZL.txt les marqueurs speciaux : {}, <>, !, ?, chiffres
2. Lister les glyphes EVA rares (frequence < 10) — sont-ils numeriques ?
3. Verifier la transcription IVTFF pour les glyphes non-standard

### PISTE 3 — La page f1r (l'alphabet)
```
Priorite : ★★★★★
Duree : 30 min
```

f1r a une annotation marginale qui ressemble a un ALPHABET ou un CIPHER.
Des lettres latines sont ecrites a cote de glyphes VMS.
C'est peut-etre la CLE de tout le systeme, y compris les nombres.

**Test :**
1. Extraire les annotations marginales de f1r dans ZL.txt
2. Chercher les correspondances lettre latine → glyphe VMS
3. Y a-t-il des CHIFFRES dans cette annotation ?
4. Comparer avec le systeme de Newbold, Brumbaugh, et autres qui
   ont essaye de lire cette page

### PISTE 4 — La page f116v (la page "cipher")
```
Priorite : ★★★★★
Duree : 30 min
```

f116v a du texte en ECRITURE LATINE (pas en Voynichese).
Certains chercheurs y lisent "michiton oladabas" ou du germanique.
D'autres y voient un systeme de chiffrement.

**Test :**
1. Extraire le texte de f116v
2. Y a-t-il des CHIFFRES ou des symboles numeriques ?
3. Comparer avec les systemes de chiffrement medievaux connus
4. Cross-ref avec les marginalia de f1r

### PISTE 5 — La volvelle f57v (L03 = la cle ?)
```
Priorite : ★★★★★
Duree : 1h
```

f57v L03 contient les 17 glyphes de la table des logograms
disposes en 4 quadrants. C'est peut-etre un AIDE-MEMOIRE
qui inclut aussi les CHIFFRES.

L04 a 29 labels (29 jours ? 29 = nombre lunaire).
L05 a 75% d'un cadran solaire.

**Test :**
1. Re-analyser L03 : y a-t-il des glyphes non-identifies ?
2. Re-analyser L04 : les 29 labels contiennent-ils des NOMBRES ?
3. Les mots de L04 suivent-ils une sequence NUMERIQUE (1,2,3...) ?
4. Le "29" de f1r est-il un NOMBRE ecrit dans le systeme VMS ?

### PISTE 6 — Position des dosages dans l'AN vs position dans le VMS
```
Priorite : ★★★★
Duree : 1h
```

On a S01_AN tokenise avec 150 recettes. Chaque recette a des tokens
de type DOSE et QTY a des POSITIONS precises.

**Test :**
1. Pour chaque recette AN, calculer la POSITION RELATIVE des dosages
   (ex: dosage a 30% de la recette, a 60%, a 90%)
2. Pour f103r VMS, quels mots sont aux MEMES positions relatives ?
3. Ces mots partagent-ils un pattern commun (meme suffixe ? meme longueur ?)
4. Si oui → ces mots sont les candidats dosages

### PISTE 7 — Repetition de patterns courts
```
Priorite : ★★★★
Duree : 30 min
```

Les dosages medievaux sont REPETITIFS :
"ana .z.ii." revient des dizaines de fois dans une meme recette.
"ana" seul revient 137 fois dans l'AN.

**Test :**
1. Quels mots VMS sont les plus REPETITIFS a l'interieur d'une meme page ?
   (pas les plus frequents dans le corpus, mais les plus repetes SUR UNE PAGE)
2. "ana" dans l'AN est toujours ENTRE ingredients et AVANT un nombre.
   Quel mot VMS est toujours entre deux mots "lexicaux" et avant un mot court ?
3. Les mots EVA de 2-3 glyphes en position mediane de ligne = candidats dosages

### PISTE 8 — Le systeme de numeration romain abrege
```
Priorite : ★★★
Duree : 30 min
```

Les chiffres romains dans les manuscrits medicaux sont souvent
CONFONDUS avec des lettres :
- i = 1 (meme glyphe que la lettre i)
- ii = 2 (meme que la ligature ii)
- S = semis (demi)
- j = variante de i en position finale

Et si les GLYPHES EVA `i`, `ii`, `iii` ne sont PAS des voyelles
mais des CHIFFRES ROMAINS quand ils apparaissent a certaines positions ?

**Test :**
1. Compter les mots EVA qui se TERMINENT par `i`, `ii`, `iii`
2. Compter ceux qui se terminent par `n` (= signe de fin de nombre ?)
3. Le pattern "mot + ii" est-il distribue comme un dosage ?

### PISTE 9 — Les couleurs et decorations
```
Priorite : ★★
Duree : reference seulement
```

Certains manuscrits medicaux utilisent des COULEURS pour les dosages :
- Rouge pour les nombres
- Points rouges comme separateurs

Les images HD du VMS (Yale Beinecke) montrent-elles des marques de couleur
a des positions specifiques ?

**Note :** Necessiterait l'examen des images HD. Pas faisable computationnellement.

### PISTE 10 — Comparaison avec d'autres systemes de numeration medievaux
```
Priorite : ★★★
Duree : 1h
```

Les systemes de numeration medievaux :
- Chiffres romains (i, ii, iii, iv, v...)
- Chiffres arabes (1, 2, 3...) — adoptes en Europe XIIe-XIVe s.
- Systeme digital (doigts) — utilise dans le comput
- Notes tironiennes pour les nombres
- Systeme alphabetique (a=1, b=2...) — rare mais atteste

**Test :**
1. Lister les 10 systemes de numeration medievaux connus
2. Pour chaque systeme, definir sa SIGNATURE dans le VMS
   (quels glyphes, quelles positions, quelle frequence)
3. Tester systematiquement chacun contre le texte VMS

---

## Plan d'execution

```
Phase 1 — DONNEES (1h)
  Piste 1 : sequences ii/iii/ee/eee
  Piste 2 : glyphes rares / non-standard
  Piste 3 : f1r annotations marginales
  Piste 4 : f116v texte latin
  |
  -> Inventaire complet des candidats numeriques
  |
Phase 2 — POSITION (1h)
  Piste 5 : volvelle f57v L03/L04
  Piste 6 : positions dosages AN vs positions VMS
  Piste 7 : mots repetitifs intra-page
  |
  -> Les candidats sont-ils aux bonnes positions ?
  |
Phase 3 — SYSTEME (1h)
  Piste 8 : chiffres romains integres
  Piste 10 : comparaison avec systemes connus
  |
  -> Le systeme est-il identifiable ?
  |
DECISION
  Si un systeme emerge → ON CONTINUE
  Si rien → ON PUBLIE CE QU'ON A ET ON ARRETE
```

## Critere de succes

**MINIMUM pour continuer :**
- Identifier au moins 3 glyphes/mots qui encodent des QUANTITES
- Ces glyphes doivent etre aux positions ou l'AN met ses dosages
- Le nombre de "dosages" par recette doit etre coherent (5-10 par recette, pas 72)

**Si on trouve :** le systeme de numeration debloque TOUT.
Les dosages sont la structure la plus RIGIDE d'une recette.
Si on decode ".z.ii." → on decode "ana" → on segmente les recettes
→ on decode les ingredients entre les dosages.

**Si on ne trouve PAS :** on publie :
- Le systeme de 16 logograms (CONFIRME)
- Le systeme de 14 suffixes (CONFIRME)
- La nature de nomenclator (CONFIRME)
- Le referentiel de pharmacopee medievale (869 concepts)
- L'echec honnete sur les mots individuels

Et on laisse d'autres continuer avec notre infrastructure.
