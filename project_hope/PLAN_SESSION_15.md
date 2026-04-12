# SESSION 15 — Plan d'actions

## Objectif : passer de 7 à 30+ ingrédients décodés

## ÉTAPE 1 — Triangulation Avicenna (28 plantes)

Avicenna (S08, 2148 chapitres, 254 ingrédients) a 28 folios VMS matchés.
C'est 3x plus que le Macer. Même méthode :
- Pour chaque paire de folios VMS matchés à Avicenna
- Quels ingrédients Avicenna dit qu'ils partagent ?
- Quelles racines VMS ces folios partagent ?
- Fingerprint matching sur 28 bits

**Script** : `step1_avicenna_triangulation.py`
**Résultat** : nouveaux mots dans `hypothesis_registry.json`

## ÉTAPE 2 — Triangulation Abenguefit (22 plantes)

Abenguefit (S15, 515 chapitres, 237 ingrédients) — source INDÉPENDANTE.
Un mot trouvé par Avicenna ET confirmé par Abenguefit = confiance 0.9.

**Script** : `step2_abenguefit_triangulation.py`
**Résultat** : confirmation croisée Avicenna↔Abenguefit

## ÉTAPE 3 — Consolider : Macer + Avicenna + Abenguefit

Fusionner les résultats des 3 sources.
Un mapping trouvé par 2 sources indépendantes = CONFIRMÉ.
Un mapping trouvé par 1 seule source = PROBABLE.
Conflits entre sources = SIGNALÉ (pas supprimé).

**Script** : `step3_consolidate.py`
**Résultat** : `hypothesis_registry.json` mis à jour

## ÉTAPE 4 — Décomposer les recettes pharma avec le nouveau vocabulaire

Avec 30+ ingrédients, re-décomposer les 9935 mots pharma.
Objectif : passer de 11% à 25%+ décomposés.
Pour chaque recette : lister les ingrédients identifiés.

**Script** : `step4_decompose_pharma.py`
**Résultat** : recettes partiellement lisibles

## ÉTAPE 5 — Valider par cohérence pharmaceutique

Pour chaque recette partiellement décodée :
- Les ingrédients ont-ils du sens ensemble ?
- La combinaison existe-t-elle dans UN des 15 corpus ?
- Si oui → la recette est validée, les ingrédients inconnus sont contraints

**Script** : `step5_validate_recipes.py`

## ÉTAPE 6 — Identifier aqua/succus/vinum par exclusion

Ces 3 véhicules universels sont impossibles par triangulation directe.
Stratégie alternative :
- Dans les recettes où TOUS les autres ingrédients sont identifiés,
  les mots restants = aqua, succus ou vinum
- Si un mot restant apparaît dans 80%+ des recettes → probablement aqua
- Si un mot restant est souvent suivi de dose → probablement vinum (vin dosé)
- Si un mot restant est associé à des plantes broyées → succus (jus)

**Script** : `step6_universal_vehicles.py`

## ÉTAPE 7 — Mettre à jour TOUS les fichiers

- `hypothesis_registry.json` : tout ajouté avec preuves
- `knowledge_base.json` : vocabulaire mis à jour
- `INSIGHTS.md` : nouvelles découvertes
- Décoder f48v et f103r B01 avec le vocabulaire élargi

**Script** : `step7_final_decode.py`

## FICHIERS

| Script | Étape | Input | Output |
|--------|-------|-------|--------|
| step1_avicenna_triangulation.py | 1 | S08 + VMS + anchors | hypothèses |
| step2_abenguefit_triangulation.py | 2 | S15 + VMS + anchors | hypothèses |
| step3_consolidate.py | 3 | toutes hypothèses | registry mis à jour |
| step4_decompose_pharma.py | 4 | registry + pharma | recettes décomposées |
| step5_validate_recipes.py | 5 | recettes + 15 corpus | validation |
| step6_universal_vehicles.py | 6 | recettes validées | aqua/succus/vinum |
| step7_final_decode.py | 7 | tout | f48v + f103r décodés |

## CRITÈRE DE SUCCÈS

- 30+ ingrédients décodés (vs 7 actuellement)
- 25%+ des mots pharma décomposés (vs 11%)
- 3+ recettes lisibles en latin pharma
- aqua et/ou vinum identifiés
- Aucune incohérence pharmaceutique dans les recettes décodées

## PRINCIPE

Chaque étape alimente le registre d'hypothèses.
Les échecs sont PRÉSERVÉS avec leur raison.
Les conflits entre sources sont SIGNALÉS, pas résolus arbitrairement.
La confiance s'accumule par convergence multi-sources.
