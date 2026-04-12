# PLAN — Attaque Macer Floridus

## Contexte

Le test multi-corpus (session 13, step 13) montre que le VMS ressemble
le PLUS au Macer Floridus (1.61x mieux que le hasard), PAS à l'AN (1.18x).

Le Macer Floridus (De Viribus Herbarum, ~1070) :
- 77 chapitres, chacun = UNE plante
- Chaque chapitre décrit : nom, qualités galéniques, indications, préparations
- Structure : plante par plante (comme la section herbal du VMS)
- 171 ingrédients référencés dans S05_MACER.json

Le VMS herbal : ~130 folios, chacun = UNE plante dessinée.

## ÉTAPE 1 — Profiler le Macer

Pour chaque chapitre du Macer :
- Quelle plante principale ?
- Quels ingrédients mentionnés (co-ingrédients dans les remèdes)
- Quelles indications (maladies traitées)
- Quelles qualités galéniques (chaud/froid, degré)
- Quelle longueur de texte (nombre de tokens)

Résultat : 25 profils Macer (ou 77 si on étend le corpus)

## ÉTAPE 2 — Profiler chaque folio herbal VMS

Pour chaque folio herbal du VMS :
- Combien de mots
- Quels préfixes uniques (= ingrédients distincts)
- Ratio k/t (= possible qualité galénique)
- Quels suffixes dominants
- Position dans le manuscrit (ordre des folios)

Résultat : ~130 profils VMS

## ÉTAPE 3 — Matcher chapitres Macer ↔ folios VMS

Critères de matching (PAS de longueur de mot) :
- Nombre de concepts mentionnés (préfixes uniques VMS ↔ ingrédients Macer)
- Le k/t ratio VMS corrèle-t-il avec les qualités galéniques du Macer ?
  (plante chaude = k-dominant ? plante froide = t-dominant ?)
- Les folios VMS avec beaucoup de préfixes rares matchent-ils les chapitres
  Macer avec beaucoup d'ingrédients rares ?

## ÉTAPE 4 — Test galénique k/t vs Tacuinum

Le Tacuinum (S12, 2e meilleur match) a les qualités galéniques explicites :
- natura (chaud/froid/sec/humide)
- gradus (degré 1-4)

Test : les folios VMS k-dominant sont-ils les plantes CHAUDES du Tacuinum ?
Les t-dominant les plantes FROIDES ?

Si corrélation → k=chaud, t=froid (ou l'inverse). C'est testable.

## ÉTAPE 5 — Identification par profil croisé

Si on a :
- folio f33v : k/t=0.45, 8 préfixes uniques, 3 doses, suffixe -edy dominant
- Macer chapitre "Artemisia" : froide degré 2, 7 ingrédients, 4 préparations

Et que les SEULS chapitres du Macer avec ce profil sont Artemisia et
Plantago → on a réduit l'identification à 2 candidats.

Croiser avec l'ID botanique de Sherwood (f33v = Tanacetum parthenium) :
Tanacetum est proche d'Artemisia dans la famille des Compositae → MATCH.

## FICHIERS

| Fichier | Description |
|---------|-------------|
| step14_macer_profiles.py | Profiler le Macer |
| step15_herbal_profiles.py | Profiler les folios herbal VMS |
| step16_kt_galenic.py | Test k/t vs qualités galéniques |
| step17_cross_match.py | Matcher Macer ↔ VMS |

## DONNÉES

- S05_MACER.json (25 entrées, 24K tokens, 171 ingrédients) ✓
- S12_TACUINUM.json (358 entrées, 68K tokens, qualités galéniques) ✓
- vms_structured.json (130 folios herbal) ✓
- botanical_anchors.json (106 IDs Sherwood) ✓

## CRITÈRE DE SUCCÈS

- Au moins 5 folios VMS matchent un chapitre Macer avec score > 0.5
- La corrélation k/t vs chaud/froid a un p-value < 0.05
- Au moins 2 identifications cohérentes avec Sherwood
