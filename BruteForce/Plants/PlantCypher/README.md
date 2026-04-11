# PlantCypher - Corpus DALME d'inventaires de pharmacie medievale

## Objectif

Extraction et normalisation d'inventaires d'apothicaires medievaux issus de la base DALME (Documentary Archaeology of Late Medieval Europe) pour constituer un 5e corpus de reference dans le pipeline de decodage du Manuscrit de Voynich (K&A v12).

L'hypothese centrale : si le texte decode du Voynich (V39) contient un vocabulaire pharmaceutique coherent, les ingredients identifies doivent correspondre a ce que l'on retrouve dans les boutiques d'apothicaires reelles du XVe siecle.

## Sources

Tous les textes proviennent de **DALME** (https://dalme.org), collection "Historical Pharmacopeias".

| Inventaire | Lieu | Date | Langue | Items bruts |
|---|---|---|---|---|
| Rostaing de Greoux | Manosque | 1547 | Latin/Provencal | 559 |
| Steve Villa | Aix-en-Provence | 1506 | Latin/Provencal | 210 |
| Johannes Cambarelli | Marseille | 1432 | Latin/Provencal | 871 |
| Table des prix de Rome | Rome | 1674 | Italien | 809 |
| Guillem Coll | Girona | 1454 | Catalan | 24 |
| Donna Miquella | Avignon | 1492 | Provencal/Occitan | 11 |

**Total : 2484 items extraits, 118 ingredients latins uniques resolus.**

NB : L'inventaire de Mathieu Roux (Marseille, 1488) a ete traite separement dans `Corpus_Pharmaceutique/datasets/dalme_mathieu_roux_1488.csv` (459 items, 168 ingredients latins uniques).

## Fichiers

### Textes sources (extraits de DALME)
- `dalme_Inventory_of_Rostaing_de_Gr_oux.txt` - Inventaire complet, latin pharmaceutique direct
- `dalme_Inventory_of_the_boutique_of_Steve_Villa.txt` - Boutique provencale, formes latines et vernaculaires
- `dalme_Inventory_of_the_shop_of_Johannes_Cambarelli.txt` - Texte concatene sans retours a la ligne, tres dense
- `dalme_A_table_of_prices_of_medicines_in_Rome_1674.txt` - Tarification italienne structuree
- `dalme_Inventory_of_Guillem_Coll.txt` - Inventaire domestique catalan, contenu pharma minimal
- `dalme_Inventory_of_the_shop_of_Donna_Miquella.txt` - Surtout equipement, tres peu d'ingredients

### Donnees produites
- `dalme_all_inventories_unified.csv` - CSV unifie : 2484 lignes, colonnes (Inventaire, Item_Original, Latin_Standard, Categorie)
- `parse_all_dalme_v2.py` - Script Python de parsing et lemmatisation

## Methodologie

### Extraction
Les textes DALME ont ete extraits via un script JavaScript execute dans la console du navigateur sur dalme.org. Le script navigue automatiquement entre les folios de chaque inventaire, collecte le contenu TEI du conteneur `#tei-container`, et telecharge le tout en fichier texte.

### Lemmatisation
Le script `parse_all_dalme_v2.py` utilise :

1. **Dictionnaire de lemmes** (~200+ entrees) couvrant les formes latines (nominatif, genitif, ablatif), provencales, occitanes, catalanes et italiennes. Exemples : "galbani" et "galbanum" vers Galbanum, "rosarum" vers Rosa, "reubarbaro" vers Rhabarbarum.

2. **Decapage de suffixes latins** : -orum, -arum, -ii, -is, -i, -um, -ae, -e, -s pour attraper les formes declinees non presentes dans le dictionnaire.

3. **Detection de categories** : AQUA, OLEUM, CYRUPUS, ELECTUARIUM, PILLULA, EMPLASTRUM, CONSERVA, UNGUENT, PULVIS, CONFITURE, TROCISCUS, SEMEN, RADIX, SUCCUS, GRAISSE, LAPIS.

4. **Parsers specialises** par inventaire pour gerer les formats tres differents (texte structure vs. concatene, latin vs. italien, etc.).

### Taux de resolution

| Inventaire | Items | Resolus | Taux | Latins uniques |
|---|---|---|---|---|
| Greoux (1547) | 559 | 180 | 32% | 109 |
| Villa (1506) | 210 | 52 | 25% | 45 |
| Cambarelli (1432) | 871 | 76 | 9% | 50 |
| Rome (1674) | 809 | 115 | 14% | 60 |
| Coll (1454) | 24 | 5 | 21% | 3 |
| Miquella (1492) | 11 | 4 | 36% | 4 |

Les taux "bruts" sont moderes car une grande partie des items sont du materiel (pots, boites, balances), des preparations composees, ou des noms de localites, pas des ingredients simples. Le chiffre cle est le nombre d'ingredients latins uniques resolus.

## Croisement avec l'Antidotarium Nicolai

Sur les 40 ingredients les plus frequents de l'Antidotarium Nicolai (base du formulaire pharmaceutique medieval), **35 sont attestes dans au moins un inventaire DALME** :

- **Greoux** : 33/40 (inventaire le plus complet)
- **Rome** : 21/40
- **Cambarelli** : 16/40
- **Villa** : 13/40
- **Coll** : 2/40
- **Miquella** : 1/40

Les 5 ingredients AN non retrouves dans DALME : Absinthium, Acetum, Petroselinum, Crocus, Ricinus. Absinthium et Crocus sont certainement presents sous des formes vernaculaires non encore capturees par le lemmatiseur.

## Contexte dans le projet Voynich

Ce corpus DALME constitue le **5e pilier** du systeme de validation croisee :

1. **Antidotarium Nicolai** - Le formulaire de reference (114 ingredients, 137 recettes)
2. **Circa Instans** - L'encyclopedie des simples (207 entrees avec degres galeniques)
3. **Lylye of Medicynes** - La pharmacopee anglaise (715 ingredients, 421 recettes)
4. **V39 decode** - Le texte du Voynich decode par pipeline K&A v12
5. **DALME** - Inventaires reels d'apothicaires (7 inventaires, 286 ingredients uniques avec Roux)

La convergence entre texte decode et stocks reels de boutiques constitue un argument fort pour la coherence pharmaceutique du decodage.

## References

- DALME Project : https://dalme.org
- Antidotarium Nicolai : W.S. van den Berg (ed.), *Eene Middelnederlandsche vertaling van het Antidotarium Nicolai*, 1917
- Circa Instans : H. Dorveaux, *L'Antidotaire Nicolas*, 1913
- Lylye of Medicynes : AncientBiotics Project, mBio 2020 (doi:10.1128/mBio.03136-19)
- Pipeline K&A v12 : decodage du Manuscrit de Voynich (MS 408, Beinecke Library)
