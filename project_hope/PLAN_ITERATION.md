# PLAN ITÉRATIF — Décoder par accumulation logique

## Principe

Le nomenclator est arbitraire. On ne le craque PAS par logique interne.
On le craque par ACCUMULATION D'INDICES EXTERNES, folio par folio,
ingrédient par ingrédient. Chaque nouveau mot décodé contraint les suivants.

Boucle : identifier → vérifier → propager → recommencer.

---

## CE QU'ON A

- 5 mots confirmés : cth=acetum, yk=mel, cht=piper, shocthy=mastix, shotch=nigella
- 18 logograms
- 68 noms de plantes (premier mot, fiabilité 0.6)
- 49 racines fonctionnelles identifiées
- Racines herbal = sous-chaînes dans les mots pharma
- Le Macer complet (77 chapitres avec ingrédients)
- 19 ancres Sherwood↔Macer
- k/t = froid/chaud (trend)

## ITÉRATION 1 — Décomposer les mots pharma

**Problème** : les mots pharma sont des COMPOSÉS (opchedy = o + pched + edy).
On ne peut pas les lire sans les décomposer.

**Action** :
1. Pour chaque mot pharma, chercher si une racine-plante connue est DEDANS
2. Si oui : extraire le préfixe et le suffixe
3. Cataloguer les préfixes pharma (o-, qo-, l-, d-, s-, op-, ot-...)
4. Déterminer si ces préfixes ont un sens (préposition incorporée ? mode de préparation ?)

**Test** : si pched=lens, alors opchedy = o(?) + pched(lens) + edy(génitif?)
Et dans le Macer Ruta, lens est mentionné → vérifier que opchedy apparaît sur f48v.

## ITÉRATION 2 — Identifier les plantes par les dessins

**Problème** : on a 68 noms de plantes mais seulement 19 matchent le Macer.
Les 49 autres n'ont pas de texte parallèle.

**Action** :
1. Pour les 19 ancres Macer : le chapitre Macer dit quels INGRÉDIENTS
   sont utilisés avec cette plante. Chercher ces ingrédients (comme sous-chaînes)
   dans le texte du folio VMS. Chaque match = un nouveau mot décodé.
2. Pour les 49 sans Macer : chercher dans le Circa Instans (141 entrées),
   le Tacuinum (358), l'Alphita (1714). Un des corpus aura la plante.
3. Pour les plantes ÉVIDENTES visuellement : les dessins de racines = mandragore,
   les fleurs en étoile = bourrache, les feuilles en pointe = plantain.
   Même une ID visuelle incertaine donne un candidat testable.

## ITÉRATION 3 — Vérifier les quantités

**Problème** : i-count n'est PAS un compteur de drachmes (i2=81% en herbal).

**Action** :
1. Dans les 5 mots confirmés, vérifier : quand acetum(cth) apparaît avec
   suffix -ain(i1) vs -aiin(i2), le CONTEXTE change-t-il ?
2. Comparer : dans le Macer, quand "acetum" est au génitif vs nominatif,
   est-ce que ça corrèle avec -ain vs -aiin dans le VMS ?
3. Si i-count = cas grammatical : i1=nominatif (sujet), i2=génitif (complément)
   → tester sur les positions dans les phrases.

## ITÉRATION 4 — Propagation dans les recettes pharma

**Problème** : on a 285 recettes pharma mais seulement ~5 ingrédients décodés.

**Action** :
1. Décomposer CHAQUE mot pharma en préfixe + racine + suffixe
2. Chercher les racines-plantes dans chaque mot
3. Pour chaque recette : lister les plantes identifiées
4. Comparer avec les combinaisons d'ingrédients connues dans les corpus
5. Si une recette VMS a mel + acetum + [inconnu] et que le Macer dit
   "mel + acetum + piper pour la Rue" → l'inconnu = piper ? Vérifier
   que ce n'est pas déjà cht(=piper confirmé).

## ITÉRATION 5 — Valider par cohérence pharmaceutique

**Critère** : une recette décodée doit avoir du SENS en pharmacie médiévale.

**Tests** :
1. Mel + acetum = oximel → préparation classique ✓
2. Piper + mel = sirop poivré → préparation classique ✓
3. Lens + ruta = cataplasme → existe dans le Macer ✓
4. Si une recette donne "sable + musique + étoile" → FAUX, on a un bug.

## ITÉRATION 6 — Les préfixes pharma

**Hypothèse** : les préfixes pharma (o-, qo-, l-, op-, ot-) sont des
prépositions INCORPORÉES dans le mot.

**Test** :
Si o = ac (logogram), alors o + pched = ac + lens = "avec des lentilles" ?
Si qo = ? alors qo + pched = "? + lentilles" ?

**Action** :
1. Lister tous les préfixes devant les racines-plantes connues
2. Croiser avec les logograms : o=ac, l=se, d=de, qo=?
3. Si un préfixe corrèle avec un logogram, c'est la préposition fusionnée.

## ITÉRATION 7 — La section balnea

**Problème** : balnea a 11 mots exclusifs + les mêmes ingrédients.

**Action** :
1. Appliquer les mêmes décompositions aux mots balnea
2. Les 11 mots exclusifs = vocabulaire du corps (tête, ventre, pied...)
3. Chercher dans le Tacuinum les parties du corps mentionnées
4. Les nymphes dans les dessins = les organes traités

## ORDRE D'EXÉCUTION

```
ITÉRATION 1 (décomposer pharma) ← PREMIER, débloque tout
    ↓
ITÉRATION 2 (identifier plantes par Macer/CI/Tac)
    ↓
ITÉRATION 3 (vérifier i-count = cas grammatical)
    ↓
ITÉRATION 4 (propagation dans recettes)
    ↓
ITÉRATION 5 (validation cohérence pharma)
    ↓
ITÉRATION 6 (préfixes = prépositions)
    ↓
ITÉRATION 7 (balnea)
```

Chaque itération produit de nouveaux mots → nourrit les suivantes.
On boucle jusqu'à saturation.

## CRITÈRE D'ARRÊT

**Succès** : 50+ mots décodés, 5+ recettes lisibles en latin pharma
**Échec** : les décompositions ne produisent aucun match cohérent
**Saturation** : chaque nouvelle itération ajoute <2 mots → on a extrait le maximum
