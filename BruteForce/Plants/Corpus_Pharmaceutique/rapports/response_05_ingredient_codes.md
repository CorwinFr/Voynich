# Response 05 : Identification des 109 codes d'ingredients
## Validation externe du modele V22-V34

**Date** : 10 avril 2026
**Sources croisees** : 3 agents de recherche + recherche independante Claude + responses 01-04
**Niveau de confiance global** : MODERE-FAIBLE (aucun classement frequentiel publie de l'Antidotarium ; propositions fondees sur des inferences croisees)

---

## 1. Etat de la question : existe-t-il un classement frequentiel des ingredients de l'Antidotarium ?

### 1.1 Reponse courte : NON

Aucune etude publiee ne fournit un classement complet des ingredients par frequence d'apparition dans les ~150 recettes de l'Antidotarium Nicolai. Les sources les plus proches sont :

**Goltz 1976** (Mittelalterliche Pharmazie und Medizin, Stuttgart) : ouvrage de reference de 252 pages, fournit le contexte historique et analytique mais PAS de table de frequence ingredient par ingredient.

**Voronov & Ruzhinskaya 2018** (Pharmacy & Pharmacology, Russie) : "Technology of Medicines and Galenical Preparations: The Case of Prescription Formulas from 'Antidotarium' Nicolai" - systematise 85 recettes sur les ~150 mais la table complete n'est pas accessible en libre acces.

**DBNL woordenlijst** (van den Berg 1917) : glossaire alphabetique de l'editio princeps confirmant la presence de tous les ingredients cles (cinnamomum, crocus, piper, rosa, mel, mastix, aloe...) mais SANS comptage de frequence.

**Gonzalez Blanco 2018** (these MPhil, Glasgow) : edition diplomatique du Middle English Antidotarium avec commentaire herbal, inclut une analyse de vocabulaire mais pas de donnees frequentielles completes.

### 1.2 Donnee quantitative la plus concrete

**75 electuaria sur 142 remedes** dans l'Antidotarium (variantes manuscrites entre 115 et 175 recettes). Le miel (mel) est confirme comme liant universel des electuaires, avec insistance dans la preface sur le fait que "le miel ne doit etre ni trop liquide ni trop dur" et constitue le meilleur conservateur.

### 1.3 Source computationnelle la plus proche

L'etude **"Data Mining a Medieval Medical Text" (mBio, 2020)** a analyse le *Lylye of Medicynes* (XVe s.) par methode de reseau : 354 noeuds d'ingredients, 3 073 liens ponderes de co-occurrence. C'est l'analyse computationnelle la plus rigoureuse existante sur un texte pharmaceutique medieval, mais elle porte sur un texte DIFFERENT de l'Antidotarium.

**Ingredients les plus connectes dans ce reseau** : honey (miel), vinegar (vinaigre), oil (huile), wax (cire), rose - ce qui correspond exactement a la couche excipient deja identifiee dans les decodages Voynich.

---

## 2. Classement frequentiel ESTIME des ingredients de l'Antidotarium

En l'absence de donnees publiees, le classement suivant est une reconstruction par inferences croisees a partir de : (a) le nombre de recettes ou chaque ingredient apparait dans les 10 recettes DBNL transcrites (response_01), (b) les listes d'ingredients des temoins Ponzi (BNF Latin 6823), (c) les donnees du reseau mBio, (d) les inventaires d'apothicaires florentins (Ricettario 1498).

### 2.1 Top 20 estime (ordre decroissant de frequence)

| Rang | Latin | Categorie | Recettes estimees (/150) | Forme principale |
|------|-------|-----------|--------------------------|------------------|
| 1 | **mel** (miel) | Excipient/liant | ~75-90 | Electuaire, oxymel, miel rose |
| 2 | **rosa** (rose) | Herbe/excipient | ~50-70 | Eau de rose, sirop, poudre |
| 3 | **cinnamomum** (cannelle) | Epice aromatique | ~45-60 | Poudre, dans 80%+ des theriaques |
| 4 | **piper** (poivre) | Epice | ~40-55 | Poudre (blanc, noir, long) |
| 5 | **crocus** (safran) | Epice aromatique | ~35-50 | Poudre, colorant/aromatique |
| 6 | **oleum** (huile) | Excipient/base | ~30-45 | Base d'onguents, vehicule |
| 7 | **mastix** (mastic) | Resine | ~25-40 | Poudre, onguents, electuaires |
| 8 | **aloe** | Purgatif | ~25-35 | Poudre, electuaire (Hiera Picra) |
| 9 | **cera** (cire) | Excipient | ~20-35 | Base d'onguents/cerats |
| 10 | **zingiber** (gingembre) | Epice | ~20-30 | Poudre, electuaire |
| 11 | **galanga** | Epice | ~15-25 | Poudre, electuaire |
| 12 | **nardus** (spikenard) | Aromatique | ~15-25 | Huile, poudre |
| 13 | **myrrha** (myrrhe) | Resine | ~15-25 | Poudre, onguent |
| 14 | **thus/olibanum** (encens) | Resine | ~15-25 | Poudre, onguent |
| 15 | **acetum** (vinaigre) | Excipient | ~15-20 | Oxymel, solvant, topique |
| 16 | **aqua** (eau) | Vehicule | ~15-20 | Vehicule, bain-marie |
| 17 | **scammonia** | Purgatif | ~12-18 | Poudre, purgatif |
| 18 | **turbit** | Purgatif | ~12-18 | Poudre, electuaire |
| 19 | **sal** (sel) | Mineral | ~10-15 | Cataplasme, solution |
| 20 | **opium** | Narcotique | ~10-15 | Latex, theriaque |

### 2.2 Fiabilite de ce classement

**FAIBLE A MODEREE.** Ce classement est une estimation informee, pas un comptage empirique. Les positions relatives des 5 premiers (mel, rosa, cinnamomum, piper, crocus) sont probablement correctes car convergentes entre toutes les sources. Au-dela du rang 5, l'incertitude augmente fortement.

**Recommandation critique** : utiliser le corpus PHARMA de 426K mots deja constitue (response corpora v4) pour effectuer un comptage computationnel reel des occurrences de chaque ingredient. C'est la seule methode fiable.

---

## 3. Propositions d'identification pour les codes "o" et "eo"

### 3.1 Code "o" (212 occurrences, rang #1)

**Proposition : mel (miel)**
- Confiance : MODEREE-HAUTE

**Arguments pour :**
- Mel est l'ingredient le plus transversal de la pharmacopee medievale : liant de TOUS les electuaires (75/142 recettes), conservateur, vehicule
- Dans le reseau mBio (354 noeuds), honey est le noeud le plus connecte
- Frequence 212x = ubiquite compatible avec mel
- Code ultra-court ("o" = 1 caractere) = ingredient le plus courant merite le raccourci le plus court (principe d'economie d'ecriture, parallele avec les notes tironiennes)
- Le code apparait en formes sh-o (miel cru) ET ch-o (miel despumatus/ecume), ce qui correspond a la distinction mel crudus / mel despumatus attestee dans l'Antidotarium

**Arguments contre :**
- Rosa est egalement omni-presente et pourrait pretendre au rang #1
- Sans comptage empirique, impossible de trancher definitivement

### 3.2 Code "eo" (126 occurrences, rang #2)

**Proposition : rosa (rose)**
- Confiance : MODEREE

**Arguments pour :**
- Rosa est le deuxieme ingredient le plus polyvalent : aqua rosarum (eau de rose) comme vehicule dans de tres nombreuses recettes, rosa en poudre dans les electuaires, oleum rosatum, mel rosaceum, sirop de rose
- Les formes attestees sont multiples : fleurs fraiches (sh-eo ?), preparations variees (ch-eo ?)
- Le code "eo" (2 caracteres) est compatible avec le rang #2 par economie
- Rosa apparait dans les sections herbal (plante illustree) ET pharma (ingredient compose), ce qui expliquerait une distribution sur les deux sections du manuscrit

**Arguments contre :**
- Cinnamomum est aussi un candidat serieux pour le rang #2 (present dans quasi toutes les theriaques, electuaires, confections)
- Piper (poivre) est un autre concurrent potentiel

### 3.3 Test discriminant propose

Pour departager mel/rosa/cinnamomum/piper aux rangs 1-2, examiner le **ratio ch/sh** des codes "o" et "eo" :
- Si ch/sh est ELEVE (>2:1) : favorise mel (car mel est presque toujours despumatus, donc "prepare")
- Si ch/sh est MODEREE (~1:1) : favorise rosa (utilisee aussi bien fraiche que preparee)
- Si ch/sh est BAS (<1:2) : favorise une plante utilisee surtout crue/fraiche

---

## 4. Verification des preparations des 23 plantes identifiees visuellement

### 4.1 Concordances suffixe/preparation verifiees

| Folio | Plante | Suffixe decode | Preparation attestee (Circa Instans / sources medicales) | Match |
|-------|--------|----------------|----------------------------------------------------------|-------|
| F13R | **Artemisia** | -or (eau florale) | Decoction dans vin/biere ; fumigation. PAS d'eau florale standard | PARTIEL - la decoction (aqua) existe, mais -or implique distillation |
| F22R | **Coriandrum** | -ol (huile) | Huile de graines documentee ; usage digestif | BON |
| F25V | **Helleborus** | -aiin (unite/drachmes) | Racine en poudre, doses minuscules (0,02-0,1g) ; sirop (Syrupus Rosaceus Solutivus cum Helleboro) | COHERENT - le suffixe de dosage correspond a un ingredient ou la quantite exacte est critique |
| F33R | **Inula** | -ar (preparation aqueuse) | Decoction de racine ; melange miel/vin | BON - decoction = preparation aqueuse |
| F38R | **Papaver** | -or (eau florale) | Extraction de latex (incision capsules) ; sirop | PARTIEL - le latex n'est pas une "eau florale" mais le sirop pourrait correspondre |
| F40V | **Salvia** | (aucun suffixe clair) | Decoction dans vin ; gargarisme avec vin/eau/miel/alun | N/A |
| F43R | **Borago** | -aiin (unite/drachmes) | Sirop de fleurs ; infusion dans vin/eau | PARTIEL - le suffixe de dosage est possible si la recette specifie une quantite |
| F44R | **Mentha** | (aucun suffixe clair) | Jus ; gargarisme au vin ; pilules | N/A |
| F46R | **Ruta** | (aucun suffixe clair) | Petites doses en huile (1-5 gouttes) ; vinaigre (Vinaigre des Quatre Voleurs) ; infusion au vin | N/A |
| F49R | **Ocimum** | -ol (huile) | Huile aromatique de graines | BON |
| F50R | **Verbena** | -or (eau florale) | Decoction dans vin ; infusions aqueuses | PARTIEL - l'infusion aqueuse est attestee mais "eau florale" distillee est anachronique pour verbena |
| F90R1 | **Thymus** | -ol (huile) | Huile essentielle ; decoction au miel | EXCELLENT - le thym est un des rares simples ou l'huile essentielle est la preparation primaire |
| F93R | **Urtica** | -ol (huile) | Diuretique ; jus ; huile | BON |
| F9V | **Viola tricolor** | -or (eau florale) | Affections cutanees, lavage externe | COHERENT - lavage externe ~ preparation aqueuse |
| F11R | **Calendula** | -al (sel/aloe ?) | Cicatrisant ; huile/onguent | FAIBLE - on attendrait -ol (huile) plutot que -al |
| F34R | **Rosmarinus** | (aucun suffixe clair) | Huile aromatique ; infusion au vin | N/A |

### 4.2 Plantes sans verification possible dans le Circa Instans

Les plantes suivantes n'ont pas ete trouvees dans les sources accessibles du Circa Instans ou les donnees de preparation sont trop vagues :

- **Atropa belladonna** (F1V) : le Circa Instans original ne contient probablement PAS d'entree pour la belladone, qui est davantage documentee dans les sources plus tardives (XVe-XVIe s.)
- **Centaurea** (F2R) : les sources mentionnent un usage comme tonique amer en decoction, mais sans details de preparation specifiques dans le Circa Instans
- **Nymphaea** (F2V) : documentee comme "refroidissant, sedatif" ; preparation aqueuse probable, mais pas de texte latin de reference localise
- **Drosera** (F56R) : aucune entree dans le Circa Instans (le genre Drosera est tres marginal dans la materia medica medievale)
- **Mandragora** (F65R) : bien documentee comme narcotique/soporifique dans la tradition salernitaine, mais les details de preparation varient enormement (ecorce de racine, vin, eponge somnifere)

### 4.3 Synthese : fiabilite du systeme de suffixes

Sur les 12 plantes ou une comparaison suffixe/preparation est possible :
- 4 matchs BONS a EXCELLENTS : Coriandrum (-ol), Inula (-ar), Thymus (-ol), Ocimum (-ol)
- 4 matchs PARTIELS : Artemisia (-or), Papaver (-or), Verbena (-or), Borago (-aiin)
- 1 match COHERENT : Helleborus (-aiin)
- 1 match FAIBLE : Calendula (-al)
- 2 sans suffixe applicable

Le systeme de suffixes (-ol = huile, -ar = eau/decoction) fonctionne correctement pour les huiles aromatiques (thym, coriandre, ocimum, ortie). Il est plus fragile pour le suffixe -or (eau florale), qui suppose un processus de distillation pas toujours atteste dans les sources les plus anciennes, mais compatible avec la pratique italienne du XVe siecle ou la distillation se developpe.

---

## 5. Modeles de co-occurrence des ingredients

### 5.1 Paires et groupes fixes attestes

**Base d'onguents (FORTEMENT ATTESTE) :**
- Oleum + cera = definition du cerat (ceratum). Atteste dans Unguentum fuscum, Unguentum album, etc.
- Oleum + cera + resina : dans certains onguents, PAS universel

**Electuaires (FORTEMENT ATTESTE) :**
- Mel + [poudre d'ingredients] = definition de l'electuaire
- Mel + aloe + epices = structure de la Hiera Picra et variantes

**Oxymels et sirops :**
- Mel + acetum = oxymel (Oximel de l'Antidotarium)
- Zucharum + succus + acetum = base des oxyzacchares

**Purgatifs :**
- Aloe + sarcocolla : paire purgative la plus frequente dans le reseau mBio
- Scammonia + zingiber + feniculum : combinaison purgative attestee
- Turbit + scammonia : dans les "benedictum laxativum"

**Aromatics des theriaques :**
- Cinnamomum + crocus + piper : noyau aromatique quasi-universel dans les grandes compositions (Metridatum, Tyriaca magna, Athanasia)

**Topiques :**
- Plantago + mel + malum granatum + acetum : combinaison identifiee dans le reseau mBio comme cluster persistant

### 5.2 Implication pour le decodage des 109 codes

La methode la plus prometteuse pour identifier les codes serait d'appliquer une analyse de co-occurrence aux 109 codes dans les recettes decodees, puis de comparer les clusters obtenus avec les clusters connus :

1. Si un groupe de ~3 codes apparait systematiquement ensemble dans les recettes longues (theriaques) : candidats = cinnamomum, crocus, piper
2. Si un code co-apparait avec presque TOUS les autres dans les electuaires : candidat = mel
3. Si deux codes forment un binome stable dans les onguents : candidats = oleum + cera
4. Si un code apparait surtout avec mel dans des recettes courtes purgatives : candidat = aloe

---

## 6. Propositions d'identification pour les 30 codes les plus frequents

### 6.1 Methode

Les propositions ci-dessous croisent : (a) le rang de frequence du code Voynich, (b) le suffixe de preparation, (c) la categorie (excipient deja identifie vs ingredient actif), (d) les donnees de co-occurrence disponibles. Les codes dont le suffixe est -y (grammatical/generique) sont les plus difficiles a identifier car le suffixe n'indique pas de preparation specifique.

### 6.2 Table de propositions

| # | Code EVA | Freq | Suffixe | Proposition | Confiance | Raisonnement |
|---|----------|------|---------|-------------|-----------|--------------|
| 1 | o | 212 | (aucun) | **mel** (miel) | MODEREE-HAUTE | Ingredient le plus transversal, liant universel des electuaires. Code le plus court = ingredient le plus frequent (economie). Distinction sh/ch = mel crudus / mel despumatus |
| 2 | eo | 126 | (aucun) | **rosa** (rose) | MODEREE | 2e ingredient le plus polyvalent (aqua rosarum, poudre, sirop, huile). Code court = ingredient frequent |
| 3 | cthy | 113 | -y | **cinnamomum** (cannelle) | FAIBLE-MODEREE | 3e rang compatible avec cinnamomum (dans ~45-60 recettes). Suffixe -y non discriminant |
| 4 | eky | 99 | -y | **piper** (poivre) | FAIBLE | 4e rang compatible avec piper. Suffixe -y non discriminant. Le prefixe "e" pourrait indiquer 1x dose |
| 5 | odaiin | 70 | -aiin | **crocus** (safran) + dosage | FAIBLE | 5e rang compatible avec crocus. Suffixe -aiin = marqueur de quantite (2 drachmes ?). Le safran est toujours dose avec precision |
| 6 | aiin | 68 | -aiin | marqueur de **quantite** (ana/2ʒ) | MODEREE | Pourrait etre un marqueur structurel (quantite) plutot qu'un ingredient |
| 7 | es | 54 | -s | **mastix** (mastic) | FAIBLE | 7e rang compatible. Resine tres frequente |
| 8 | edaiin | 52 | -aiin | **aloe** + dosage | FAIBLE | Purgatif majeur, toujours dose avec precision |
| 9 | ecthy | 49 | -y | **zingiber** (gingembre) | FAIBLE | Epice chaude, rang compatible |
| 10 | oky | 48 | -y | **galanga** | TRES FAIBLE | Rang compatible mais aucun critere discriminant |
| 11 | ees | 46 | -s | **myrrha** (myrrhe) | TRES FAIBLE | Resine, rang compatible |
| 12 | oty | 45 | -y | **nardus** (spikenard) | TRES FAIBLE | Aromatique, rang compatible |
| 13 | edar | 43 | -ar | **feniculum** (fenouil) - decoction | FAIBLE-MODEREE | Suffixe -ar = preparation aqueuse. Radices feniculi dans l'Oximel. Decoction de fenouil tres attestee |
| 14 | ckhey | 41 | -ey | **cera** derivee ? | FAIBLE | Suffixe -ey evoque cera. Mais cera est identifie comme excipient de base |
| 15 | eeky | 38 | -y | **absinthium** (absinthe) | TRES FAIBLE | Herbe amere, dans Hiera Picra |
| 16 | edal | 37 | -al | **sal** derive ou **aloe** prep | FAIBLE | Suffixe -al evoque sal ou aloe. Mais sal deja identifie comme excipient |
| 17 | ed | 37 | court | ingredient de base non identifie | INDETERMINE | Trop peu de criteres discriminants |
| 18 | dar | 33 | -ar | **apium** (celeri/ache) - decoction | FAIBLE | Suffixe -ar = eau/decoction. Radices apii dans l'Oximel |
| 19 | octhy | 31 | -y | **mentha** (menthe) | TRES FAIBLE | Herbe aromatique, rang compatible |
| 20 | ety | 31 | -y | **origanum** (origan) | TRES FAIBLE | Aromatique digestif |

### 6.3 Avertissement methodologique

**Les propositions au-dela du rang 2 sont largement speculatives.** Sans analyse de co-occurrence dans les recettes decodees, les suffixes -y (generique) ne permettent pas de discriminer entre des dizaines de candidats possibles. Seules les identifications suivantes reposent sur des arguments convergents :

- **o = mel** : convergence frequence + economie + reseau mBio + distinction sh/ch
- **eo = rosa** : convergence frequence + polyvalence + economie
- **Codes en -ar** (edar, dar) : la preparation aqueuse/decoction restreint les candidats aux racines et herbes bouillies (feniculum, apium, petroselinum, rafanus)
- **Codes en -ol** : huiles essentielles ou grasses (deja verifiees sur les pages herbal : thymus, coriandrum, ocimum)

---

## 7. Methode computationnelle recommandee

### 7.1 Comptage frequentiel sur le corpus PHARMA

Le corpus PHARMA de 426 000 mots (Collatinus 89,6% valide) constitue la meilleure base pour un comptage reel. Methode proposee :

1. Extraire tous les lemmes d'ingredients (via Collatinus en mode medieval) du corpus PHARMA
2. Compter les occurrences de chaque lemme d'ingredient
3. Classer par frequence decroissante
4. Comparer directement ce classement avec le classement des 109 codes Voynich par frequence

Si les deux classements montrent une correlation significative (test de Spearman rho > 0,6), cela validerait le modele de decodage a l'echelle du vocabulaire.

### 7.2 Analyse de co-occurrence sur les recettes decodees

Methode inspiree de l'etude mBio (2020) :

1. Pour chaque recette decodee, construire la liste des codes d'ingredients presents
2. Compter les co-occurrences par paires (matrice 109x109)
3. Identifier les clusters par analyse de reseau (modularity detection)
4. Comparer les clusters avec les groupes connus : {cinnamomum, crocus, piper} = aromates de theriaque ; {oleum, cera} = base d'onguent ; {mel, aloe, mastix} = electuaire purgatif
5. Si les clusters correspondent, les identifications sont confirmees

### 7.3 Verification croisee par la section herbal

Pour les 23 plantes identifiees visuellement :
1. Verifier que le code du label de la page herbal apparait dans les recettes de la section pharma avec une frequence coherente
2. Verifier que les co-occurrences de ce code dans les recettes correspondent aux usages attestes de la plante

---

## 8. Verdict global

### 8.1 Ce qui est POSSIBLE avec les donnees actuelles

- **Identifier mel et rosa** comme les deux codes les plus frequents avec une confiance moderee
- **Verifier le systeme de suffixes** (-ol, -ar, -or) sur les 23 plantes identifiees : 4 bons matchs, 4 partiels sur 12 testables
- **Confirmer les paires de co-occurrence** oleum+cera et mel+acetum si une analyse de reseau est appliquee aux recettes decodees
- **Restreindre les candidats** pour les codes en -ar (racines en decoction) et -ol (huiles)

### 8.2 Ce qui est IMPOSSIBLE sans travail supplementaire

- **Identifier individuellement les ~80 codes restants** : les suffixes -y sont trop generiques et les rangs de frequence trop proches pour discriminer
- **Valider le classement frequentiel** sans comptage computationnel sur le corpus PHARMA
- **Confirmer cinnamomum, piper, crocus** aux rangs 3-5 sans analyse de co-occurrence dans les recettes decodees

### 8.3 Prochaines etapes prioritaires

1. **Comptage automatise** des lemmes d'ingredients dans le corpus PHARMA (426K mots)
2. **Matrice de co-occurrence** des 109 codes dans les recettes decodees
3. **Test statistique** de correlation rang Voynich / rang corpus (Spearman)
4. **Verification des ratios ch/sh** pour les codes "o" et "eo" pour discriminer mel vs rosa

---

## 9. Sources de reference

### 9.1 Etudes quantitatives
- **mBio (2020)** : "Data Mining a Medieval Medical Text Reveals Patterns in Medieval Drug Prescribing" - PMC7018648 - reseau de 354 ingredients, 3073 liens
- **Voronov & Ruzhinskaya (2018)** : "Technology of Medicines and Galenical Preparations: The Case of Prescription Formulas from 'Antidotarium' Nicolai" - journals.eco-vector.com/2307-9266/article/view/111547
- **Goltz (1976)** : Mittelalterliche Pharmazie und Medizin, Stuttgart, 252 pp.
- **Gonzalez Blanco (2018)** : MPhil(R) Thesis, University of Glasgow - theses.gla.ac.uk/8965/

### 9.2 Textes de reference
- **DBNL editio princeps** : van den Berg 1917 - dbnl.org/tekst/_ant004wsva01_01/
- **DBNL woordenlijst** : dbnl.org/tekst/_ant004wsva01_01/_ant004wsva01_01_0019.php
- **Marco Ponzi (ViridisGreen)** : Transcriptions BNF Latin 6823 - medium.com/viridisgreen/
- **Ricettario Fiorentino (1498)** : premiere pharmacopee officielle europeenne

### 9.3 Circa Instans
- Brewminate : "A Medieval Pharmaceutical Bestseller: The 'Circa instans'"
- Wellcome Library : blog.wellcomelibrary.org/2017/02/
- Academia.edu : Mattheus Platearius, Circa Instans (trans. M.H. Green)
- NCBI Bookshelf NBK606146 : Medieval Mediterranean Pharmacology

### 9.4 Preparations vegetales
- Met Museum Cloisters Garden Blog : salvia, inula, verbena
- PMC7767097 : "Descriptive Overview of Medical Uses of Mentha Aromatic Herbs"
- Botanical.com (Mrs. Grieve, A Modern Herbal) : borage, thyme, rue
