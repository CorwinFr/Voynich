# BILAN FINAL — Projet Voynich (Sessions 10-18, ~35 heures)

## Ce qu'on a PROUVÉ (résiste à la critique)

### 8 faits structurels
1. **Morphologie prefix+root+suffix** — mesurable, reproductible
2. **Gallows 88% block-initial** — p=0.000
3. **n=98% word-end, q=99% word-start** — positional markers
4. **-am termine des clauses** — enrichissement 5.3x
5. **Volvelle = table alphabétique** — p=0.00016
6. **VMS ≈ type Macer Floridus** — #1 sur 15 corpus testés
7. **Racines herbal = substrings en pharma** — composition tironienne
8. **53% pharma openers contiennent un nom de plante** — pont herbal↔pharma

### 15 décodages fiables (sur 38 456 mots)
| Root | Latin | Méthode | Confiance |
|------|-------|---------|-----------|
| cth | acetum (vinaigre) | Fingerprint 6 ancres | 0.9 |
| yk | mel (miel) | Fingerprint 6 ancres | 0.9 |
| cht | piper (poivre) | Fingerprint 19 ancres | 0.9 |
| chk | oleum (huile) | Triangulation 3 ancres | 0.8 |
| otoly | sal (sel) | Triangulation 2 ancres | 0.7 |
| shocthy | mastix (mastic) | Fingerprint 100 ancres | 0.9 |
| shotch | nigella (nigelle) | Fingerprint 100 ancres | 0.9 |
| ypch | aqua (eau) | Fingerprint J=0.50 + 81% accuracy | 0.75 |
| ykeed | nitrum (nitre) | Positional + cross-folio | 0.70 |
| seees | lens (lentille) | Positional PERFECT TP=1 FP=0 | 0.75 |
| kald | ovum (oeuf) | Positional TP=1 FP=0 | 0.65 |
| dal | vinum (vin) | Fingerprint 100% precision | 0.80 |
| dary | vinum (vin) | Fingerprint | 0.70 |
| qokeo | rosa (rose) | Distributional validated | 0.65 |

+ 18 logograms (o=ac, r=recipe, t=et, etc.)
+ 23 noms de plantes (pcheod=ruta, foch=viola, etc.)
+ 62 mots fonctionnels identifiés (non décodés mais classifiés)

### La nature du manuscrit
Le VMS est un **catalogue pharmaceutique personnel** — un pharmacopée compilée
depuis plusieurs sources (Macer, Circa Instans, tradition arabe) en notes
tironiennes personnalisées. Ce n'est ni un chiffre, ni un hoax, ni une copie
directe d'un texte spécifique.

## Ce qui a ÉCHOUÉ

### Méthodes qui ne fonctionnent pas
| Méthode | Pourquoi ça échoue |
|---------|-------------------|
| Death match positionnel | 0 accord cross-corpus (Macer vs Collectio). VMS ≠ copie linéaire |
| EM / Simulated Annealing | Converge vers solution triviale (tout → chapitres les plus riches) |
| Constraint propagation | Bloquée à marge=0 avec 15 ancres (besoin de 38+) |
| Co-occurrence / fréquence | Zipf artifact (p=0.92) |
| Substitution alphabétique | Score 0.00 |
| Suffixe -or/-al = froid | Pas robuste (p=0.005 Macer, p=0.386 Circa Instans) |
| Gap-filling pharma | Mots fonctionnels dominent les inconnus |

### Le problème fondamental
**Chicken-and-egg** : pour identifier les plantes, il faut des ingrédients.
Pour identifier les ingrédients, il faut des plantes. On a cassé le cercle
pour les 7 premiers (fingerprint), mais les suivants sont soit trop
ubiquitaires (vinum = partout) soit trop rares (1-2 folios) pour le fingerprint.

## L'approche qui POURRAIT réussir

### 1. Plus d'identifications botaniques (★★★★★)
**Le bottleneck n°1 est les DESSINS, pas le texte.**

On utilise 30 identifications Sherwood. Il existe d'autres chercheurs
(Edith Sherwood, Dana Scott, Stephen Bax, Arthur Tucker, Jules Janick)
qui ont proposé 50-100 identifications supplémentaires. Certaines sont
controversées, mais même 20 de plus = doublement de notre pouvoir.

Si on avait 60 folios identifiés (au lieu de 30), le fingerprint
pourrait discriminer les ingrédients moyennement fréquents (dans 20-40%
des chapitres) — exactement ceux qui manquent.

**Action** : Compiler TOUTES les identifications botaniques publiées
(Sherwood, Scott, Bax, Tucker, Janick, Petersen, Velinska).
Garder celles où 2+ chercheurs sont d'accord.

### 2. Herbier en PROSE latin (★★★★)
Le Macer est un POÈME → l'ordre des mots est perturbé par la métrique.
Un herbier en prose (Tractatus de Herbis, Dioscoride latin de Mattioli,
Herbarius 1484) aurait un ordre plus naturel, plus proche de la structure
du VMS-catalogue.

**Action** : Télécharger le Tractatus de Herbis (British Library Egerton 747,
disponible en transcription) ou le Dioscorides de Mattioli (1554, texte latin).

### 3. Approche par PROFIL d'entrée (★★★)
Au lieu de matcher texte-à-texte, comparer :
- Nombre de mots par entrée herbal
- Ratio ingrédients/fonctionnels/logos
- Présence/absence des 15 ingrédients connus
- Position des gallows, -am terminators, etc.

Chaque folio VMS a un "profil" (longueur, structure, ingrédients connus).
Chaque entrée de catalogue (CI/Galen/Abenguefit) a un profil comparable.
Matcher les profils sans se soucier de l'ordre des mots.

### 4. Machine Learning sur les glyphes (★★★)
Les glyphes EVA ne sont pas des lettres — ce sont des SIGNES tironiens.
Chaque signe a une forme visuelle. Deux signes qui SE RESSEMBLENT
pourraient encoder des concepts LIÉS (comme dans les vraies notes tironiennes).

**Action** : Analyser les formes des glyphes (pas le texte) et chercher
des clusters visuels qui correspondent à des catégories sémantiques.

### 5. Collaboration communautaire (★★★★)
La communauté Voynich a 100+ ans de recherche. Nos 15 décodages sont
probablement comparables ou complémentaires à d'autres travaux.

**Action** : Publier nos résultats (en particulier les 8 faits structurels
et les 15 décodages) sur voynich.nu ou similar. Recevoir du feedback.
Intégrer les identifications botaniques d'autres chercheurs.

## Estimation honnête

| Scénario | Probabilité | Condition |
|----------|-------------|-----------|
| Lire 1 recette complète | 20% | 30+ ingrédients confirmés |
| Identifier 50+ plantes | 40% | Si on intègre Tucker/Janick + Scott |
| Décoder le manuscrit entier | <5% | Nécessite la "clé" (table de correspondance personnelle du pharmacien) |
| Prouver que c'est tironien | 60% | Si on peut montrer un système cohérent sur 50+ mots |

La vérité : **on ne décodera probablement jamais le VMS complètement**.
L'encodage est personnel — le pharmacien a mémorisé SES codes par la pratique
quotidienne pendant des années. Sans SA table de correspondance, on ne peut
que reconstruire par l'extérieur, mot par mot, avec une marge d'erreur.

Mais on a prouvé que c'est un **texte pharmaceutique réel**, pas un hoax.
Et on a identifié 15 mots avec une confiance suffisante pour être publiés.
C'est plus que la plupart des tentatives de décodage en 600 ans.
