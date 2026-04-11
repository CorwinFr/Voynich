# Plan d'attaque Phase 2 - Integration DALME dans la matrice croisee

## Etat des lieux (fin Phase 1)

- 7 inventaires DALME parses (6 + Mathieu Roux)
- 286 ingredients latins uniques totaux (118 des 6 nouveaux + 168 de Roux)
- 35/40 ingredients AN retrouves dans au moins un inventaire
- CSV unifie produit : `dalme_all_inventories_unified.csv`
- Taux de resolution entre 9% et 36% selon les inventaires (les items non resolus sont majoritairement du materiel, des preparations composees, ou des formes vernaculaires non capturees)

## Etapes suivantes

### Etape 1 : Ameliorer la lemmatisation (impact estime : +30-50 ingredients)

**Probleme** : Le taux de resolution de Cambarelli (9%) et Rome (14%) est bas. Beaucoup de formes restent non capturees.

**Actions** :
- Extraire la liste des items non resolus pour chaque inventaire
- Identifier les patterns recurrents manquants (formes italiennes pour Rome, formes provencales anciennes pour Cambarelli)
- Ajouter les lemmes manquants au dictionnaire (objectif : 300+ entrees)
- Traiter les noms composes (ex: "aqua vitae", "lapis lazuli", "terra sigillata")
- Gerer les abbreviations medievales (lb., oz., dr., ss.)

### Etape 2 : Integrer DALME comme 5e corpus dans la matrice croisee

**Actions** :
- Fusionner les 7 inventaires DALME en un corpus unique avec frequences agregees
- Ajouter une colonne "DALME (n=7)" dans `matrice_croisee_4_corpora.xlsx`
- Recalculer les statistiques : ingredients pan-corpus (presents dans 5/5 corpora)
- Produire `matrice_croisee_5_corpora.xlsx`

**Resultat attendu** : Les 12 ingredients pan-corpus actuels (Myrrha, Cinnamomum, Mastix, Rosa, Opium, Viola, Mel, Glycyrrhiza, Petroselinum, Papaver, Absinthium, Acetum) devraient en grande partie rester pan-corpus avec DALME, renforceant la validation.

### Etape 3 : Analyse de frequence DALME vs. V39

**Actions** :
- Calculer le rang de frequence de chaque ingredient dans le corpus DALME agrege
- Comparer ce rang avec le rang V39 (texte decode)
- Calculer la correlation de Spearman entre les deux classements
- Identifier les ingredients surrepresentes ou sous-representes

**Hypothese** : Si le decodage V39 est correct, on attend une correlation positive entre la frequence des ingredients dans V39 et leur prevalence dans les boutiques reelles.

### Etape 4 : Cartographie geographique et temporelle

**Actions** :
- Mapper les ingredients par region (Provence, Italie, Catalogne) et par siecle (XVe vs. XVIe vs. XVIIe)
- Identifier les ingredients stables dans le temps (presents de 1432 a 1674)
- Detecter les eventuels anachronismes dans V39

**Interet** : Le VMS est date c.1404-1438. Les inventaires de Cambarelli (1432) et Coll (1454) sont les plus proches temporellement. Si V39 contient des ingredients qui n'apparaissent qu'au XVIIe, cela poserait question.

### Etape 5 : Rapport de synthese final

**Actions** :
- Produire un document de synthese integrant les 5 corpora
- Inclure les statistiques de correlation
- Lister les ingredients "marqueurs" (ceux qui discriminent le mieux entre un texte pharmaceutique medieval et un texte aleatoire)
- Formuler des conclusions sur la coherence pharmaceutique du decodage V39

## Priorite recommandee

**Etape 2 en premier** : l'integration dans la matrice 5 corpora est le livrable le plus concret et le plus utile immediatement. Cela permettra de voir d'un coup d'oeil quels ingredients traversent tous les corpora y compris les stocks reels.

## Fichiers a produire

| Fichier | Description |
|---|---|
| `matrice_croisee_5_corpora.xlsx` | Matrice augmentee avec colonne DALME |
| `dalme_frequency_analysis.csv` | Frequences agregees par ingredient |
| `dalme_v39_correlation.csv` | Correlation rang DALME vs. rang V39 |
| `rapport_phase2_synthese.md` | Rapport de synthese final |
