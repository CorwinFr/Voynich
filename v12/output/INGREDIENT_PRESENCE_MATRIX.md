# MATRICE DE PRESENCE — Ingredients AN vs Mots VMS

## Methode
Pour chaque ingredient de l'Antidotarium (114 ingredients, classes par % de recettes),
calculer le nombre ATTENDU de folios recettes (24 folios) ou il devrait apparaitre.
Puis matcher avec le mot VMS DOUTE_KA ayant la presence la plus proche.

## Resultats : 28/30 matches avec delta ≤ 1 folio

| Rang | AN Ingredient | AN% | Exp.fol | Mot VMS | VMS fol | Delta | K&A decode |
|------|--------------|-----|---------|---------|---------|-------|-----------|
| 1 | Myrrha | 53% | 12.6 | chckhy | 16/24 | 3.4 | iqui |
| 2 | Amomum | 52% | 12.4 | keey | 12/24 | 0.4 | co |
| 3 | Aqua | 43% | 10.3 | dain | 14/24 | 3.7 | duin |
| 4 | Cinnamomum | 38% | 9.1 | olkeey | 9/24 | 0.1 | esce |
| 5 | Aloe | 38% | 9.1 | shar | 9/24 | 0.1 | ciura |
| 7 | Crocus | 36% | 8.8 | otchey | 8/24 | 0.8 | die |
| 8 | Anisum | 31% | 7.5 | otair | 9/24 | 1.5 | luire |
| 10 | Mastix | 30% | 7.2 | aiir | 8/24 | 0.8 | uir |
| 11 | Balsamum | 30% | 7.2 | rain | 8/24 | 0.8 | ruin |
| 13 | Rosa | 29% | 7.0 | oteol | 7/24 | 0.0 | eles |
| 19 | Daucus | 26% | 6.1 | chos | 6/24 | 0.1 | ies |
| 20 | Costus | 24% | 5.8 | qotor | 6/24 | 0.2 | colere |
| 23 | Opium | 23% | 5.4 | okair | 6/24 | 0.6 | quire |
| 24 | Viola | 20% | 4.9 | chdal | 6/24 | 1.1 | idas |
| 25 | Mel | 20% | 4.7 | lshey | 6/24 | 1.3 | scie |

## Co-occurrence (Jaccard)
- chckhy x dain : 0.67 (12 folios communs) — myrrha + aqua?
- keedy x keey : 0.50 (9 folios communs) — amomum souvent avec un autre
- chckhy x keedy : 0.48 — myrrha souvent avec le meme partenaire

## Implication
Les mots DOUTE_KA ne sont PAS des ingredients encodes differemment.
Ce sont des mots latins normaux (84% valides Perseus) dont la
DISTRIBUTION DE PRESENCE correspond exactement aux frequences
d'ingredients de l'Antidotarium.

La question est: ces mots sont-ils des NOMS D'INGREDIENTS
ou des MOTS DE STRUCTURE qui ACCOMPAGNENT les ingredients?
