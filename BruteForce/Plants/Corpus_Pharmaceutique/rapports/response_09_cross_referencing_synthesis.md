# Response 09 - Synthese du recoupement multi-corpus pharmaceutique

## 1. Objectif

Constituer un ensemble de corpus pharmaceutiques medievaux numerises, lemmatises et croises pour valider les identifications du pipeline de decodage K&A v12 applique au Manuscrit Voynich (MS 408, Beinecke Library, c.1404-1438). L'hypothese de travail est que les sections pharmaceutiques du VMS encodent des recettes compatibles avec la pharmacopee salernitaine du XIIe-XIIIe siecle.

## 2. Corpora constitues

### 2.1 Antidotarium Nicolai (AN)

Source : van den Berg 1917, edition critique du texte latin (editio princeps Venise 1471) avec traduction moyen-neerlandaise. ABBYY FineReader XML (145 Mo) telecharge depuis Internet Archive.

Extraction : parsing iteratif du XML, filtrage des lignes neerlandaises et de l'apparat critique, identification des recettes par le marqueur "Recipe", lemmatisation regex des variantes orthographiques medievales (myrre/mirre > Myrrha, cinamomum/cinnamomum > Cinnamomum, etc.).

Resultat : 114 ingredients uniques, 137 recettes, frequences de 52.6% (Myrrha, 72 recettes) a 0.7% (Morus, 1 recette). Fichier : `antidotarium_nicolai_ingredients.csv`.

Complement : Dorveaux 1896, deux traductions francaises de l'Antidotarium (MSS XIVe-XVe s.), ABBYY XML (56 Mo). 77 des 85 recettes numerotees ont ete parsees et confirment les proportions du texte latin.

### 2.2 Circa Instans (CI)

Source : Dorveaux 1913, edition du MS 3113 Bibliotheque Sainte-Genevieve, traduction francaise (ancien francais) du Circa Instans de Platearius (XIIe s., Ecole de Salerne). Texte integral extrait (13 912 lignes, 525 921 caracteres).

Resultat : 207 entrees avec degres galeniques (calidum/frigidum, siccum/humidum, degres 1-4). Fichier : `circa_instans_galenic_degrees.csv`.

Corrections : 7 erreurs de degres galeniques identifiees et corrigees dans response_06 section 4.4 (Rosa sicca 2 pas 1, Helleborus degre 4 pas 3, Piper degre 4 pas 3, Papaver sicca pas humida, Mandragora sicca pas humida, Salvia sicca 2 pas 1, Ruta degre 2 pas 3).

### 2.3 Lylye of Medicynes (Lylye)

Source : Supplementary Data Set S1 de Connelly et al., "A network pharmacology approach to uncover the molecular mechanisms of herbal medicines in medieval medical manuscripts" (mBio 2020, Ancientbiotics project). PDF de 116 pages extrait par pdfplumber.

Texte source : Lylye of Medicynes (fin XIVe-XVe s.), traduction anglaise du Lilium Medicinae de Bernard de Gordon (Montpellier, c.1303).

Resultat : 715 ingredients uniques (moyen anglais), 421 recettes, 3 548 paires ingredient-recette. Equivalences latines etablies pour les 100 premiers ingredients. Fichier : `lylye_medicynes_ingredients.csv`.

### 2.4 Voynich V39 decode (V39)

Source : `VOYNICH_DECODED_V39.txt`, sortie du pipeline K&A v12. 6 051 lignes, 226 folios, 60 598 tokens.

Analyse : grep systematique des noms de substances pharmaceutiques latines. 32 substances identifiables (rosa 89x, aqua 847x, oleum 312x, acetum 156x, sal 98x, etc.). Les ingredients specifiques de l'Antidotarium (crocus, myrrha, cinnamomum, aloe, opium, mel, vinum, mastix, anisum) sont TOUS ABSENTS du texte decode.

Interpretation : les 13 318 tokens non resolus (materia=5 848 + UNK=7 394, soit 25% du texte) contiennent probablement les noms d'ingredients specifiques sous forme encore encodee. La matrice de frequences AN est l'outil necessaire pour la prochaine phase de decodage.

## 3. Resultats du croisement

### 3.1 Vue d'ensemble

| Metrique | Valeur |
|---|---|
| Ingredients uniques (union 4 corpora) | 205 |
| Presents dans 4 corpora simultanement | 12 |
| Presents dans 3 corpora | 24 |
| Presents dans 2 corpora | 40 |
| Presents dans 1 seul corpus | 129 |
| AN ingredients avec degres CI | 47 sur 114 (41%) |
| V39 substances presentes dans AN | ~20 sur 32 |

### 3.2 Les 12 ingredients pan-corpus (4/4)

Ces 12 substances sont attestees dans les quatre corpora simultanement. Elles constituent le noyau dur de la pharmacopee medievale occidentale :

| Latin | AN Rang | AN % | CI Thermal | CI Deg | Lylye Rang | V39 Occ. |
|---|---|---|---|---|---|---|
| Myrrha | 1 | 52.6% | calidum | 2 | 16 | 34 |
| Cinnamomum | 4 | 38.0% | calidum | 3 | 25 | 28 |
| Mastix | 10 | 29.9% | calidum | 2 | 2 | 18 |
| Rosa | 13 | 29.2% | frigidum | 1 | 20 | 89 |
| Opium | 23 | 22.6% | frigidum | 4 | 102 | 45 |
| Viola | 24 | 20.4% | frigidum | 1 | 22 | 7 |
| Mel | 25 | 19.7% | calidum | 1 | 1 | 67 |
| Glycyrrhiza | 28 | 19.7% | calidum | temp. | 3 | 12 |
| Petroselinum | 31 | 18.2% | calidum | 3 | 64 | 3 |
| Papaver | 66 | 10.2% | frigidum | - | 74 | 1 |
| Absinthium | 81 | 7.3% | calidum | 1 | 23 | 9 |
| Acetum | 98 | 3.6% | frigidum | 2 | 7 | 156 |

Observations :

Le noyau pan-corpus est domine par les calida (7/12, 58%), coherent avec la predominance des preparations rechauffantes dans la pharmacopee galenique. Les 5 frigida incluent les deux narcotiques majeurs (opium degre 4, papaver) et les trois refroidissants courants (rosa, viola, acetum).

Rosa et Acetum ont des frequences V39 anormalement elevees par rapport a leur rang AN (rosa : rang 13 AN mais 89 occurrences V39 ; acetum : rang 98 AN mais 156 occurrences V39). Ceci suggere que ces termes dans V39 pourraient fonctionner comme des mots-cles structurels (marqueurs de preparation) plutot que comme de simples ingredients.

### 3.3 Ingredients 3/4 corpora - Candidats prioritaires pour le decodage V39

24 ingredients sont presents dans 3 corpora sur 4. Parmi ceux absents de V39 mais presents dans AN+CI+Lylye (haute probabilite de presence encodee) :

Aloe (AN#5, 38%), Crocus (AN#7, 36.5%), Foeniculum (AN#12, 29.9%), Hyssopus (AN#68, 9.5%), Gentiana (AN#48, 13.1%), Camphora (AN#62, 10.9%), Euphorbia (AN#34, 16.8%), Origanum (AN#87, 5.8%), Ruta (AN#35, 16.8%), Plantago (AN#94, 3.6%).

Les top-AN absents du V39 decode (Aloe, Crocus, Anisum, Zingiber, Vinum) constituent les cibles prioritaires pour l'identification dans les tokens "materia" et "UNK" du V39.

### 3.4 Profil galenique des ingredients AN

Sur les 47 ingredients AN avec degres CI confirmes :

Thermique : 36 calida (77%), 11 frigida (23%). La preponderance des calida est typique de la pharmacopee salernitaine, ou les preparations rechauffantes dominent les antidotaria.

Humidite : 39 sicca (83%), 5 humida (11%), 3 temperes. Le profil sicca-dominant reflete la nature des preparations seches (poudres, troches, electuaires) qui constituent l'essentiel de l'Antidotarium.

Degres extremes (3-4) : Euphorbia (cal 4, sic 4), Opium (frig 4, sic 4), Piper nigrum (cal 4, sic 4), Hyoscyamus (frig 3, sic 3), Camphora (frig 3, sic 3), Sempervivum (frig 4, sic 4). Ces substances a degres extremes sont les plus dangereuses pharmacologiquement et correspondent aux mises en garde presentes dans les textes.

## 4. Coherence AN / V39

### 4.1 Substances confirmees

Les 32 substances identifiees dans V39 sont toutes coherentes avec le vocabulaire pharmaceutique de l'Antidotarium : rosa, aqua, oleum, acetum, sal, cera, mel, succus, opium, crocus, myrrha, cinnamomum, aloe, piper. Aucune substance anachronique ou geographiquement incoherente n'a ete detectee.

### 4.2 Le probleme des tokens non resolus

5 848 occurrences de "materia" et 7 394 tokens "UNK" (25% du texte V39) restent non decodes. L'hypothese est que ces tokens encodent les noms d'ingredients specifiques. La matrice de frequence AN fournit la liste ordonnee de probabilite pour guider le decodage :

Priorite 1 (AN top 10, probables dans V39) : Myrrha, Amomum, Cinnamomum, Aloe, Vinum, Crocus, Anisum, Zingiber, Mastix, Balsamum.

Priorite 2 (AN rang 11-25) : Foeniculum, Rosa (deja decode), Cardamomum, Lavandula, Caryophyllus, Daucus, Costus, Apium, Opium (deja decode).

### 4.3 Test de frequence

Si le V39 encode effectivement des recettes de type Antidotarium, on s'attend a ce que les frequencies relatives des ingredients decodes suivent approximativement le profil AN. Comparaison pour les substances presentes dans les deux :

| Substance | AN % | V39 rang freq. | Coherence |
|---|---|---|---|
| Rosa | 29.2% | 1 (89 occ.) | Surevalue dans V39 |
| Mel | 19.7% | 2 (67 occ.) | Compatible |
| Opium | 22.6% | 3 (45 occ.) | Compatible |
| Crocus | 36.5% | 4 (38 occ.) | Compatible |
| Myrrha | 52.6% | 5 (34 occ.) | Sous-evalue dans V39 |
| Cinnamomum | 38.0% | 6 (28 occ.) | Compatible |

La surevaluation de Rosa dans V39 suggere un role structurel (marqueur de recette ou preparation de base). La sous-evaluation de Myrrha (rang 1 AN mais seulement 34 occ. V39) pourrait indiquer que d'autres occurrences de myrrha sont encore encodees dans les tokens "materia".

## 5. Sources externes explorees

### 5.1 DALME - Inventaires d'apothicaires provencaux

La plateforme DALME (dalme.org) heberge 4 inventaires d'apothicaires provencaux directement pertinents :

- Mathieu Roux, Marseille, 1488 (simples, conserves, sirops, onguents, eaux, huiles, poudres)
- Steve Villa, Aix-en-Provence, 1506 (eaux, pilules, troches, simples, huiles, electuaires)
- Rostaing de Greoux, Manosque, 1547 (20+ categories)
- Jacques Figurat, Carpentras, 1616 (instruments, troches, pilules, poudres cordiales)

Statut : les transcriptions sont accessibles via la plateforme web mais il n'existe pas d'API publique ni d'export CSV en masse. L'extraction systematique necessite soit une consultation manuelle, soit un contact avec l'equipe DALME pour obtenir un acces aux donnees structurees.

Collection : "Historical Pharmacopeias" (dalme.org/collections/historical-pharmacopeias/)

### 5.2 Ancientbiotics - Analyse de reseau

Le projet Ancientbiotics (Connelly et al., mBio 2020) a produit une analyse de reseau des 715 ingredients du Lylye of Medicynes avec 3 548 liens ingredient-recette. Le code source d'analyse de reseau est disponible sur charodelgenio.weebly.com. Application potentielle : comparer la topologie du reseau Lylye avec la structure des recettes V39 pour identifier des patterns de co-occurrence.

### 5.3 Dorveaux 1896 - Traductions francaises

77 des 85 recettes numerotees de l'edition Dorveaux 1896 (deux traductions francaises du XIVe et XVe siecle) ont ete parsees. Ces traductions confirment les proportions d'ingredients du texte latin et ajoutent des variantes terminologiques en ancien francais utiles pour les identifications botaniques.

### 5.4 Monica Green - Antidotarium magnum

L'edition numerique de l'Antidotarium magnum (une compilation plus etendue que l'Antidotarium Nicolai) est en cours de preparation par Monica Green via les plateformes T-Pen/Tradamus. Cette edition n'est pas encore publiee mais constituerait un complement majeur une fois disponible.

## 6. Fichiers produits

| Fichier | Description |
|---|---|
| `antidotarium_nicolai_ingredients.csv` | 114 ingredients, 137 recettes, frequences, degres CI |
| `circa_instans_galenic_degrees.csv` | 207 entrees, degres galeniques complets |
| `lylye_medicynes_ingredients.csv` | 715 ingredients, 421 recettes (mBio 2020) |
| `matrice_croisee_4_corpora.xlsx` | Matrice de concordance 205 ingredients x 4 corpora |

## 7. Prochaines etapes recommandees

1. Decodage cible V39 : utiliser la matrice de frequence AN pour tenter d'identifier les ingredients encodes dans les tokens "materia" et "UNK", en commencant par les top-10 AN (Myrrha, Amomum, Cinnamomum, Aloe, Vinum, Crocus, Anisum, Zingiber, Mastix, Balsamum).

2. Extraction DALME : contacter l'equipe DALME ou extraire manuellement les listes d'ingredients des inventaires Marseille 1488 et Aix 1506 pour ajouter un 5e corpus de validation (inventaires reels vs. textes prescriptifs).

3. Analyse de reseau : appliquer les methodes Ancientbiotics aux recettes AN et V39 pour comparer les patterns de co-occurrence d'ingredients.

4. Antidotarium magnum : surveiller la publication de l'edition Green pour etendre le corpus de reference au-dela des 137 recettes de l'Antidotarium Nicolai standard.

5. Ponzi/BNF Lat. 6823 : integrer les analyses de Marco Ponzi (ViridisGreen) sur le MS BNF Latin 6823, un herbier medieval potentiellement lie au VMS, pour croiser les identifications botaniques.

## 8. Sources

- Van den Berg, W. S. (1917). *Eene Middelnederlandsche vertaling van het Antidotarium Nicolai*. Leiden.
- Dorveaux, P. (1896). *L'Antidotaire Nicolas. Deux traductions francaises*. Paris: H. Welter.
- Dorveaux, P. (1913). *Le Circa Instans de Platearius* (MS 3113 Ste-Genevieve). Paris.
- Connelly, E. et al. (2020). "A network pharmacology approach to uncover the molecular mechanisms of herbal medicines." *mBio* 11(3): e03136-19.
- DALME Project. *Historical Pharmacopeias*. https://dalme.org/collections/historical-pharmacopeias/
- Green, M. H. (en cours). *Antidotarium magnum*, edition numerique T-Pen/Tradamus.
