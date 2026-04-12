# SESSION 18 — ISOMORPHISME STRUCTURAL (l'attaque computationnelle)

## Le changement de paradigme

On a cherché : "quel ingrédient est ce root ?" → échec (trop d'ubiquitaires)
On a cherché : "quelle plante est ce folio ?" → échec (pas assez d'ancres)

La bonne question : **la STRUCTURE des relations entre folios dans le VMS
ressemble-t-elle à la structure des relations entre chapitres dans le Macer ?**

## Le principe

### Graphe VMS (observable, pas besoin de décoder)
- Nœuds = 143 folios herbal
- Arêtes = racines partagées entre folios
- Poids = nombre de racines partagées
- Ex: f48v et f9v partagent 12 racines → arête de poids 12

### Graphe Macer (connu)
- Nœuds = 77 chapitres
- Arêtes = ingrédients partagés entre chapitres
- Poids = nombre d'ingrédients partagés
- Ex: Ruta et Viola partagent acetum+mel+oleum+vinum → arête de poids 4

### L'isomorphisme
Trouver l'assignation folio→chapitre telle que les STRUCTURES RELATIONNELLES
se correspondent au mieux. Si f48v partage beaucoup de racines avec f9v,
alors la plante de f48v devrait partager beaucoup d'ingrédients avec la plante de f9v.

C'est un problème de **graph matching** / **quadratic assignment problem**.

## Avantages

1. **ZERO présupposition** sur les ingrédients — on utilise uniquement la structure
2. **Résistant au bruit** — les mots fonctionnels polluent mais sont uniformes
   (ils ne créent pas de patterns de co-occurrence spécifiques)
3. **Scalable** — on peut utiliser TOUS les corpus (Macer + Avicenna + Collectio)
4. Si le matching structural est bon, les root↔ingrédient tombent AUTOMATIQUEMENT

## Implémentation

### Phase 1 : Construire les graphes
```
VMS_graph[i][j] = nb de racines NON-fonctionnelles partagées entre folios i et j
MACER_graph[a][b] = nb d'ingrédients partagés entre chapitres a et b
```

### Phase 2 : Fixer les ancres Sherwood
16 folios sont identifiés (f48v=Ruta, f9v=Viola, etc.)
→ Contrainte : ces assignations sont fixes

### Phase 3 : Optimisation
Pour les 127 folios restants, trouver l'assignation qui MAXIMISE :
```
Score = Σ_{i,j} VMS_graph[i][j] × MACER_graph[assign(i)][assign(j)]
```

Algorithmes possibles :
- **Simulated Annealing** (simple, efficace pour ce type de problème)
- **Hungarian algorithm** variant (pour matching biparti)
- **Genetic algorithm** (explore l'espace de combinaisons)

### Phase 4 : Extraire les mappings root↔ingrédient
Une fois les folios assignés aux chapitres, chaque racine partagée
entre un folio et son chapitre Macer = un mapping root→ingrédient potentiel.

### Phase 5 : Valider
- Cross-validation : retirer 1 ancre Sherwood, prédire, comparer
- Score de cohérence global
- Death match positionnel sur les meilleures assignations

## Complexité

- 143 folios × 77 chapitres = 11 011 paires pour les graphes
- Optimisation : ~127! possibilités mais prunées par contraintes
- Simulated Annealing : converge en ~10 000 itérations × 143 swaps = faisable en secondes

## Datasets à utiliser

| Source | Entrées | Ingrédients uniques | Utilité |
|--------|---------|---------------------|---------|
| S05_MACER | 25 | 171 | Structure primaire |
| S08_AVICENNA | 2362 | 257 | Enrichir les arêtes |
| S09_COLLECTIO | 2643 | 333 | Plus de combinaisons |
| S10_ALPHITA | 1009 | 324 | Glossaire médical |
| S12_TACUINUM | 312 | 129 | Qualités galéniques |
| S15_ABENGUEFIT | 518 | 241 | Source arabe |

On fusionne TOUT en une seule méga-matrice plante×ingrédient.

## Structure du code

```
project_hope/engine/
  graph_builder.py     — Construit les graphes VMS et corpus
  matcher.py           — Simulated annealing / optimisation
  extractor.py         — Extrait root→ingredient des assignations
  validator.py         — Cross-validation et scoring
  pipeline.py          — Orchestre le tout

project_hope/data/
  vms_graph.json       — Graphe de co-occurrence VMS
  corpus_graph.json    — Graphe combiné de tous les corpus
  assignments.json     — Résultat de l'optimisation
```

## Critère de succès

- [ ] Assignation folio→plante pour 50+ folios avec score significatif
- [ ] Validation Sherwood : top-1 > 30%, top-5 > 60%
- [ ] 20+ root→ingrédient stables (confirmés par 3+ assignations)
- [ ] Death match sur les nouvelles assignations → latin lisible
