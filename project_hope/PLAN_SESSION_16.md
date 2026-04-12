# SESSION 16 — Frappes chirurgicales par section

## Principe

On arrête le brute force global. On cible CHAQUE SECTION du manuscrit
avec le corpus le plus adapté. Chaque frappe produit des mots fiables
qu'on propage aux autres sections.

## FRAPPE 1 — HERBAL : Macer chapitre par chapitre

**Cible** : les 19 folios ancres (Sherwood↔Macer)
**Corpus** : Macer Floridus complet (77 chapitres)
**Méthode** : pour chaque ancre, lire le chapitre Macer EN ENTIER,
identifier chaque concept mentionné, chercher la racine VMS correspondante
par position dans le texte.

**Folios prioritaires** (les plus riches en ingrédients Macer) :
1. f48v (Ruta) — 10 ingrédients, 4 déjà trouvés
2. f9v (Viola) — 7 ingrédients
3. f41r (Origanum) — 6 ingrédients
4. f37r (Mentha) — 7 ingrédients
5. f41v (Coriandrum) — 6 ingrédients

**Objectif** : identifier 3-5 nouvelles racines par folio = 15-25 nouveaux mots

## FRAPPE 2 — PHARMA : recettes les mieux décodées

**Cible** : les 20 recettes à 85%+ de décomposition
**Corpus** : AN (150 recettes), Collectio (3680), Avicenna (2148)
**Méthode** : pour chaque recette bien décodée, les 2-3 mots encore
inconnus sont les ingrédients MANQUANTS. Chercher dans les corpus
quelle recette a exactement ces ingrédients + ceux déjà identifiés.

**Recettes prioritaires** :
1. f115v_B04 (92% décodé, 1 mot inconnu)
2. f106r_B09 (90%, 2 inconnus)
3. f114v_B02 (90%, 2 inconnus)

**Objectif** : identifier les mots manquants par élimination contextuelle

## FRAPPE 3 — BALNEA : vocabulaire du corps

**Cible** : les 11 racines exclusives au balnea
**Corpus** : S11_BALNEA (93 entrées, 169 ingrédients)
**Méthode** : les racines balnea-exclusives = parties du corps ou
types de bain. Le corpus BALNEA décrit les mêmes. Matcher par profil.

**Objectif** : identifier 5-10 termes anatomiques/balnéaires

## FRAPPE 4 — GALÉNIQUE : k/t par folio

**Cible** : les 143 folios herbal avec k/t ratio
**Corpus** : S12_TACUINUM (358 entrées avec chaud/froid/sec/humide)
**Méthode** : pour les 19 ancres, vérifier si k=froid et t=chaud
avec les qualités du Tacuinum. Si ça corrèle → valider pour les 143.

**Objectif** : confirmer ou éliminer l'hypothèse k/t = galénique

## FRAPPE 5 — VÉHICULES UNIVERSELS : aqua/succus/vinum

**Cible** : les 3 racines les plus fréquentes non décodées (qok, ch, ot)
**Méthode** : dans les recettes bien décodées, les mots restants
DOIVENT être aqua, succus ou vinum. Par exclusion :
- Le mot le plus souvent suivi de dose = vinum (on dose le vin)
- Le mot le plus souvent en fin de recette = aqua (on dilue à la fin)
- Le 3e = succus

**Objectif** : identifier les 3 véhicules = +3 mots très fréquents

## FRAPPE 6 — FONCTIONNELS : les 49 racines grammaticales

**Cible** : les racines dans >20% des folios
**Méthode** : ces racines sont des prépositions, conjonctions,
ou mots grammaticaux. Les comparer aux 18 logograms :
si une racine a le MÊME comportement distributionnel qu'un logogram,
elle signifie probablement la même chose ou un synonyme.

**Objectif** : identifier 10-15 mots grammaticaux

## ORDRE D'EXÉCUTION

```
FRAPPE 1 (Herbal×Macer) → nouveaux ingrédients
    ↓
FRAPPE 2 (Pharma recettes) → validation + nouveaux mots
    ↓
FRAPPE 5 (Véhicules) → aqua/succus/vinum
    ↓
FRAPPE 3 (Balnea) → vocabulaire corps
FRAPPE 4 (Galénique) → k/t validation
FRAPPE 6 (Fonctionnels) → grammaire
```

## CRITÈRE DE SUCCÈS

- 50+ mots décodés (vs 7+33 actuels dont beaucoup douteux)
- 5+ recettes pharma lisibles en latin
- aqua, succus, vinum identifiés
- k/t = galénique confirmé ou éliminé
- 0 incohérence pharmaceutique dans les recettes validées

## FICHIERS PAR FRAPPE

| Frappe | Script | Output |
|--------|--------|--------|
| 1 | frappe1_herbal_macer.py | nouveaux_mots_herbal.json |
| 2 | frappe2_pharma_recettes.py | recettes_decodees.json |
| 3 | frappe3_balnea_corps.py | vocabulaire_balnea.json |
| 4 | frappe4_galenique_kt.py | validation_kt.json |
| 5 | frappe5_vehicules.py | aqua_succus_vinum.json |
| 6 | frappe6_fonctionnels.py | grammaire.json |

Tout alimente `hypothesis_registry.json`.
