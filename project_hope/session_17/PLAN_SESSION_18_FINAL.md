# SESSION 18 — Death Match Multi-Corpus

## Diagnostic (fin session 17)

- 18 folios assignés, 16 ancres fiables, ~106 concepts
- Propagation bloquée à marge=0 (19 ancres insuffisantes, besoin de 38+)
- Death match positionnel = seule méthode qui produit du vocabulaire
- Macer seul = 54 items discriminants. Avicenna = 257. Collectio = 333.

## Stratégie : Death Match Multi-Corpus

### Phase 1 — Construire les chapitres Avicenna/Collectio

Pour chaque plante Sherwood (16 identifiées), trouver le chapitre correspondant
dans Avicenna ET Collectio. Ces chapitres sont PLUS LONGS et PLUS DÉTAILLÉS
que Macer → plus de mots à aligner, plus d'items rares.

Exemple :
- Macer "Ruta" = 421 mots, 10 ingrédients
- Avicenna "Ruta" = probablement 2000+ mots, 30+ ingrédients + body parts + diseases

### Phase 2 — Death Match avec 3 sources

Pour chaque folio assigné (f48v=Ruta, f9v=Viola, etc.) :
1. Death match vs Macer chapitre → déjà fait (session 17)
2. Death match vs Avicenna chapitre → NOUVEAU
3. Death match vs Collectio chapitre → NOUVEAU

Les matchs trouvés dans 2+ sources = haute confiance.

### Phase 3 — Cross-validation multi-source

Un root→word trouvé dans :
- Macer seul = tier 3 (incertain, session 17)
- Macer + Avicenna = tier 2 (solide)
- Macer + Avicenna + Collectio = tier 1 (confirmé)

### Phase 4 — Relancer propagation

Avec 38+ ancres (objectif) → propagation v3 débloquée → assigner 30+ folios
→ death match sur ces folios → encore plus d'ancres → cercle vertueux

## Plan d'exécution

```
1. Parse Avicenna → find chapters for our 16 Sherwood plants
2. Parse Collectio → same
3. Run death match: 16 folios × 3 corpus = 48 alignements
4. Cross-validate: root trouvé dans 2+ corpus = tier 2
5. Update anchors (objectif: 38+)
6. Re-run propagation v3
7. Death match sur les nouveaux folios assignés
8. Iterate
```

## Fichiers

| Script | Description |
|--------|-------------|
| `engine/corpus_parser.py` | Parse Avicenna+Collectio, find plant chapters |
| `engine/death_match_multicorpus.py` | Death match 16 folios × 3 corpus |
| `engine/cross_validate.py` | Multi-source cross-validation |
| `engine/propagation_v3.py` | Relancer avec ancres enrichies |

## Critères de succès

- [ ] 38+ ancres fiables (tier 1+2)
- [ ] 40+ folios assignés (28% des herbal)
- [ ] 10+ root→ingredient confirmés par 2+ corpus
- [ ] Propagation v3 assigne au moins 10 folios avec marge > 5
- [ ] 1 recette pharma lisible en latin (5+ mots dans l'ordre)
