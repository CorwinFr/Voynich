# ÉVALUATION HONNÊTE — Sessions 10-16 (~25 heures)

## Chiffres bruts

| Métrique | Valeur | Commentaire |
|----------|--------|-------------|
| Mots dans le VMS | 38 456 | 8 039 mots uniques, 226 folios |
| Mots matchés (logo+racine) | 36% | Inclut beaucoup de faux positifs |
| Matchés haute confiance (≥0.7) | 20% | 20 racines fiables |
| Mots fonctionnels identifiés | 32% | Grammaticaux, pas des ingrédients |
| f48v (meilleur folio) | 42% apparent | ~23% réel (3/13 sûrs sur L10) |
| Hypothèses éliminées | 6 | Aussi important que les découvertes |

## Le problème des faux positifs

23/61 racines font 2-3 caractères (yk, cth, cht, do, ko...).
Ces racines courtes matchent à l'intérieur de mots plus longs par hasard.
Le 42% de f48v est gonflé. La lecture réelle de la ligne 10 :

```
(tol) (chedy) (ytedy) MEL (chdy) (chdor) PIPER (chdy) (ytchedal) ACETUM (okar) (ar) (ary)
```

3 mots sûrs sur 13 = 23% de confiance réelle sur notre meilleure ligne.

## TIER 1 — PROUVÉ (survivrait un peer review)

7 faits structurels + 1 découverte session 16 :

1. **Morphologie prefix+root+suffix** — mesurable, reproductible
2. **Gallows 88% en tête de bloc** — permutation test p=0.000
3. **n=98% word-end, q=99% word-start** — analyse positionnelle
4. **-am terminateur de phrase** — 72%, enrichissement 5.3x
5. **Volvelle f57v = table alphabétique** — 52 logograms, p=0.00016
6. **VMS ≈ Macer Floridus** — #1/15 corpus, score 1.61x
7. **Racines herbal = substrings en pharma** — composition pched→opchedy
8. **`oty` en lignes 1-3 = marqueur plante froide** — p=0.023, 7.2x enrichissement

## TIER 2 — FORTE ÉVIDENCE, BESOIN DE PLUS DE DONNÉES

- **cth=acetum** — fingerprint 6 ancres, lecture cohérente f48v L10 (conf 0.9)
- **yk=mel** — fingerprint 6 ancres, lecture cohérente f48v L10 (conf 0.9)
- **cht=piper** — fingerprint 19 ancres Macer77 (conf 0.9, mais était plantaginis avec 6)
- **chk=oleum** — triangulation 3 ancres (conf 0.8)
- **62 racines fonctionnelles classifiées** — robuste, mais distinguer connecteur/véhicule reste incertain
- **Section-specific vocabulary** — herbal, pharma, balnea ont des racines exclusives

## TIER 3 — PLAUSIBLE MAIS NON PROUVÉ

- **otoly=sal, seees=lens, ykeed=nitrum** — peu d'ancres
- **ypch=aqua** — meilleur candidat jamais trouvé (J=0.50, 4/6), mais single method
- **23 noms de plantes** — dépendent de Sherwood, seulement 74% uniques
- **18 logograms** — validés w2v mais significations arbitraires
- **L'hypothèse tironienne** — meilleure explication mais pas prouvée formellement
- **Balnea ol-pattern** — observé mais pas expliqué

## TIER 4 — SPÉCULATIF

- 31 ingrédients "probables" (conf 0.5, source unique)
- Gap-filling pharma (ch s'assigne à 6 ingrédients différents = BRUIT)
- Recipe-level decoding (trop de faux positifs de racines courtes)

## CE QUI A ÉCHOUÉ

| Méthode | Résultat | Leçon |
|---------|----------|-------|
| Substitution (volvelle) | Score 0.00 | Ce n'est pas un chiffre |
| Co-occurrence VMS↔AN | Zipf artifact p=0.92 | Le bruit domine |
| Fréquence-rang mapping | Artifact de toute paire de textes | Non discriminant |
| f↔p variants | Permutation p=1.0 | Bruit aléatoire |
| i-count = doses | i2=81% herbal (inversé) | Probablement grammatical |
| che = caro | 80% des folios | Fonctionnel, pas ingrédient |
| k/t ratio = galénique | Direction inversée | MAIS oty=froid trouvé |
| Gap-filling pharma | ch→6 ingrédients | Fonctionnels dominent les inconnus |

## BILAN

**Ce qu'on sait** : Le VMS est un texte pharmaceutique structuré (herbier type Macer).
Son système d'écriture a une morphologie régulière (prefix+root+suffix).
On a 3-4 mots d'ingrédients fiables (acetum, mel, piper, oleum).

**Ce qu'on ne sait pas** : Comment lire une phrase complète.
Pas une seule recette lisible en latin produite.
Le décodage réel est à ~5%, pas 42%.

**La vraie avancée** : Élimination de 90% des fausses pistes.
On sait maintenant OÙ et COMMENT chercher.

## PLAN SESSION 17

### Priorité 1 — Réduire les faux positifs
- Exclure racines ≤3 chars des matchs globaux
- Ne les utiliser que dans des contextes chirurgicaux (folio spécifique, position connue)
- Recalculer le % de décodage RÉEL sans faux positifs

### Priorité 2 — Prouver ypch=aqua indépendamment
- Tester dans les recettes pharma : se comporte-t-il comme un liquide ?
- Vérifier la position : avant/après dose ?
- Croiser avec un 2e corpus (pas seulement Macer fingerprint)

### Priorité 3 — UNE recette lisible
- Choisir la recette pharma la mieux contrainte
- Ne garder que les mots à conf ≥ 0.8
- Produire 5+ mots sûrs dans le bon ordre = première lecture

### Priorité 4 — Valider oty=froid sur herbal_b
- 32 folios herbal_b non encore testés
- Si oty corrèle aussi → p <<< 0.01 avec 54 folios

### Priorité 5 — Chercher vinum/succus
- Parmi les racines NON fonctionnelles (pas dans les 62)
- Profil : fréquent en pharma, rare en herbal, suit dose
- Méthode : exclusion (si on a aqua, les 2 autres sont contraintables)

### Critère de succès Session 17
- 1 recette lisible (5+ mots latins dans l'ordre)
- ypch=aqua confirmé ou éliminé
- oty=froid validé sur herbal_b
- % de décodage RÉEL (sans faux positifs) calculé
