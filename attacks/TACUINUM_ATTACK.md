# ATTAQUE NUCLEAIRE — Tacuinum Sanitatis × VMS Astro/Cosmo

## Pourquoi c'est une bombe

Le Tacuinum Sanitatis est le SEUL texte medieval a avoir TOUTES ces proprietes :
1. **Structure TABULAIRE RIGIDE** — chaque entree a les MEMES colonnes
2. **Vocabulaire FERME** — 63 mots uniques dans la colonne GRADUS
3. **Qualites galeniques SYSTEMATIQUES** — 9 formules seulement
4. **280 entrees** — proche du nombre de "fiches" dans la section astro VMS
5. **Illustre** — comme le VMS, chaque entree a une illustration

Le VMS astro/cosmo (f58-f73) a :
- **4437 tokens** sur 32 folios
- **15.8 tokens par entree Tacuinum** — ca colle avec une fiche de ~15 mots
- Un registre de suffixes DIFFERENT du herbal (-al domine au lieu de -ol)
- Des sous-folios (f67r1, f67r2, f67r3) = des TABLES

## La structure du Tacuinum

Chaque entree a 7 colonnes FIXES :

```
| Col | Latin | Sens | Vocabulaire |
|-----|-------|------|-------------|
| 1 | Nomina | Nom de la substance | 280 noms uniques |
| 2 | Natura | Qualite galenique | calidum/frigidum + siccum/humidum + auteur |
| 3 | Gradus | Degre | 63 mots (primo/secundo/tertio/quarto + temperate) |
| 4 | Melius | Meilleur type | 628 mots (adjectifs descriptifs) |
| 5 | Iuvamentum | Benefice | 525 mots (verbes + parties du corps) |
| 6 | Nocumentum | Nocivite | 435 mots (symptomes + organes) |
| 7 | Remotio | Remede au dommage | 458 mots (cum + ingredient correcteur) |
```

## Le mapping hypothetique VMS

Si l'astro/cosmo VMS EST un Tacuinum encode, alors :

```
VMS token sequence :  [word1] [word2] [word3] [word4] [word5] ... [word-am]
Tacuinum column :      NOMINA  NATURA  GRADUS  MELIUS  IUVAM      [fin]
VMS suffix :           -or?    -ol?    -al?    -ar?    -ey?       -am
```

## Les 5 attaques nucleaires

### NUKE 1 — Comptage d'entrees par page
```
Priorite : IMMEDIATE (5 minutes)
```

Le Tacuinum a 40 tables de 7 entrees.
Les pages zodiac VMS ont des NYMPHES/FIGURES numerotees.
Si chaque page zodiac a ~7 figures = 7 entrees = 1 table du Tacuinum.

**Test :**
Compter les figures/nymphes sur chaque page zodiac VMS.
Comparer avec 7 (nombre d'entrees par table Tacuinum).
Si ca matche → structure identique.

### NUKE 2 — Distribution des qualites galeniques
```
Priorite : HAUTE (30 minutes)
```

Le Tacuinum a 9 formules galeniques. Les 4 mots-cles sont :
calidum (166x), frigidum (63x), siccum (113x), humidum (80x)

Dans le VMS astro, les 4 mots les plus frequents NON-logograms devraient
correspondre a ces 4 qualites, avec les MEMES PROPORTIONS.

**Test :**
1. Retirer les logograms connus des tokens astro VMS
2. Prendre les 4 mots restants les plus frequents
3. Tester si leur distribution (ratio) matche calidum:frigidum:siccum:humidum
   = 166:63:113:80 = 2.63:1:1.79:1.27

**Candidats probables (par frequence dans la section astro) :**
- oteey (35x) → calidum? (le plus frequent)
- okal (29x) → siccum?
- otar (27x) → humidum?
- okeey (27x) → frigidum?

### NUKE 3 — Vocabulaire ferme par position
```
Priorite : HAUTE (1 heure)
```

Si chaque entree VMS suit la structure Tacuinum, alors les mots a une
position FIXE dans chaque "fiche" devraient venir d'un set FERME.

**Test :**
1. Segmenter le texte astro en blocs de ~16 tokens (= 1 entree)
2. Pour chaque POSITION dans le bloc (1er mot, 2e mot, ..., 7e mot)
3. Compter les mots uniques a cette position
4. La position GRADUS (3e?) devrait avoir ~63 mots uniques
5. La position NATURA (2e?) devrait avoir ~9 formules
6. Si les tailles de vocabulaire par position matchent → on a le mapping

### NUKE 4 — Cross-reference ingredients CI × Tacuinum
```
Priorite : HAUTE (1 heure)
```

Le Circa Instans et le Tacuinum partagent beaucoup d'ingredients.
Les qualites galeniques doivent etre IDENTIQUES dans les deux sources.

**Test :**
1. Pour chaque substance du Tacuinum, chercher dans R06_qualities (CI)
2. Verifier que les qualites matchent (myrrha = calidum+siccum dans les deux)
3. Les substances COMMUNES sont des ancres pour le crib :
   si myrrha est dans le CI (herbal VMS) ET dans le Tacuinum (astro VMS),
   alors le MEME mot EVA devrait apparaitre dans les DEUX sections
4. Chercher les mots EVA qui apparaissent a la fois dans le herbal ET l'astro

### NUKE 5 — Matching tabulaire GPU
```
Priorite : DECISIVE (2-4 heures GPU)
```

C'est l'attaque finale. Le Tacuinum a une structure SI rigide que le GPU
peut tester TOUTES les permutations possibles.

**Methode :**
1. Le Tacuinum a 9 formules galeniques → 9 "patterns" de tokens
2. Chaque page zodiac VMS a ~7 entrees → 7 patterns a matcher
3. Pour chaque page, tester les 9 formules galeniques
4. La formule qui matche le mieux = la qualite de la substance
5. Si 6/7 entrees d'une page matchent → on a identifie la table

L'espace de recherche est MINUSCULE : 9 formules × 40 tables × 7 positions
= 2520 combinaisons. Un CPU suffit. Pas besoin de GPU.

**Mais le GPU sert pour le SCORING :**
Pour chaque combinaison, scorer avec le LM medieval latin.
"calidum in primo gradu et siccum" → perplexite basse = bon latin.
"frigidum stomacho exercitantibus" → perplexite haute = mauvais.

## Chronologie

```
NUKE 1 (5 min)    : Compter les figures par page zodiac
                     → Confirme ou refute la structure 7-par-table
                     |
NUKE 2 (30 min)   : Tester la distribution calidum:frigidum:siccum:humidum
                     → Identifie les 4 mots-cles galeniques dans le VMS
                     |
NUKE 3 (1h)       : Vocabulaire par position dans les blocs
                     → Identifie quelle position = quelle colonne
                     |
NUKE 4 (1h)       : Cross-ref CI × Tacuinum × VMS herbal × VMS astro
                     → Ancres solides (mots partages entre sections)
                     |
NUKE 5 (2-4h)     : Matching tabulaire complet
                     → Decodage de la section astro/cosmo
```

## Pourquoi ca peut marcher

1. **L'espace de recherche est PETIT.** 9 formules, 63 mots de gradus,
   40 tables. C'est infiniment plus petit que l'espace total du VMS.

2. **La structure est REPETITIVE.** Chaque entree a la MEME structure.
   Si on decode 1 entree, on decode les 279 autres.

3. **Les qualites galeniques sont un SET FERME.** 4 mots seulement
   (calidum, frigidum, siccum, humidum). On les trouvera.

4. **Le cross-ref avec le herbal est GRATUIT.** Les memes ingredients
   sont dans les deux sections. Si on a decode myrrha dans le herbal,
   on le retrouve dans l'astro.

5. **La decouverte des suffixes nous aide.** -al domine dans l'astro (353x)
   mais pas dans le herbal. -al pourrait correspondre a la colonne GRADUS
   ou IUVAMENTUM du Tacuinum (categories fixes).

## Ce qui peut foirer

| Risque | Proba | Impact |
|--------|-------|--------|
| L'astro VMS n'est PAS un Tacuinum | 40% | Les NUKES 1-5 echouent, on passe a autre chose |
| C'est un Tacuinum mais dans un ORDRE different | 20% | Les NUKES 3-4 sont plus difficiles mais 2 marche |
| Les qualites galeniques ne sont PAS dans le texte (seulement dans les illustrations) | 15% | NUKE 2 echoue, mais les colonnes Iuvamentum/Nocumentum restent |
| La section astro est un CALENDRIER, pas un Tacuinum | 25% | Les NUKES echouent mais on apprend quelque chose |
