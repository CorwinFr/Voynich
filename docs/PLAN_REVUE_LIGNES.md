# PLAN D'ACTIONS : Revue systematique des lignes etranges

## Objectif
Passer en revue CHAQUE ligne du decode dual de f103r (et ensuite f104-f116)
pour identifier les INCOHERENCES structurelles et les corriger.

## Methode : detection d'anomalies par le pattern TYPE

Le format 3 lignes (EVA / TYPE / LAT) revele les anomalies :

### ANOMALIES A DETECTER

**1. INGR + INGR + INGR (3+ ingredients consecutifs)**
Une recette alterne ingredient et dosage. 3 ingredients d'affilee
signifie soit :
- Des fonctions mal classees en INGR
- Un ingredient COMPOSE (2-3 mots formant un seul nom)
- Une liste "ana" (de chaque) avec dosage implicite

**2. DOSE isole (sans INGR avant)**
Un dosage doit SUIVRE un ingredient. Un dosage seul ou apres
une fonction est suspect — peut-etre un ingredient mal classifie.

**3. VERB + VERB (2 verbes consecutifs)**
Rare dans les recettes. "Recipe misce" ou "tere et coque" existent
mais "recipe recipe" non. Indique un logogramme mal identifie.

**4. func func func func (longue chaine de fonctions)**
4+ fonctions d'affilee = probablement des parties d'un ingredient
que le classifieur a coupe en morceaux.

**5. INGR decode identique au voisin**
Si deux INGR consecutifs decodent au meme mot latin, c'est une
erreur de segmentation (un seul mot coupe en deux).

**6. DOSE avec prefixe long**
Un DOSE comme "cioqu ana I dr." a un prefixe ingredient (`cioqu`)
attache au dosage. C'est un MIXED mal gere.

**7. Lignes sans aucun INGR**
Une ligne de recette SANS ingredient est suspecte. Soit c'est une
instruction generale, soit les ingredients sont caches dans les func.

**8. INGR tres court (3-4 chars)**
Un ingredient de 3-4 caracteres est suspect — les noms de plantes
latins font typiquement 5-10 caracteres. Souvent c'est un fragment.

### CORRECTIONS POSSIBLES

Pour chaque anomalie detectee :

1. **Re-classifier** : changer le type du mot (func→INGR ou INGR→func)
2. **Re-segmenter** : fusionner 2 mots courts en 1 ingredient
3. **Ajouter au FUNCTION_PATTERNS** : si un mot est toujours func
4. **Ajouter aux LOGOGRAMS** : si un mot a un decode fixe et stable
5. **Tester les variantes EVA** : si le mot a des lectures alternatives

## Etapes

### ETAPE 1 : Script de detection d'anomalies
Ecrire un script qui parcourt le decode 3-lignes et COMPTE :
- Nombre de sequences INGR+INGR+INGR (objectif : 0)
- Nombre de DOSE isoles (objectif : 0)
- Nombre de func chains 4+ (objectif : minimal)
- Nombre de lignes sans INGR (objectif : comprendre pourquoi)
- Ratio VERB/INGR global (objectif : 1:3-8)

### ETAPE 2 : Revue manuelle des 10 pires lignes
Prendre les 10 lignes avec le plus d'anomalies.
Pour chacune :
- Lire l'EVA original
- Comparer avec le decode Antidotarium attendu
- Proposer une correction du classifieur ou du decode

### ETAPE 3 : Corrections et iteration
Appliquer les corrections.
Regenerer le decode.
Recompter les anomalies.
Iterer jusqu'a ratio 1:3-8.

### ETAPE 4 : Extension a f104-f116
Appliquer le meme processus aux 13 autres pages de recettes.
Accumuler les ingredients identifies.
Chercher les sequences matchant l'Antidotarium.

### ETAPE 5 : Rapport d'identification
Produire la liste complete :
- INGREDIENTS IDENTIFIES (nom, EVA, folio, confiance)
- INGREDIENTS CANDIDATS (decode mais pas dans les corpora)
- MOTS OPAQUES (pas d'identification possible)

## Fichiers

| Fichier | Description |
|---------|-------------|
| v12/analysis/anomaly_detector.py | Script de detection |
| v12/output/F103R_ANOMALIES.md | Rapport des anomalies |
| v12/output/F103R_DUAL_DECODE.md | Decode annote (mis a jour) |
| v12/classifier.py | Classifieur (mis a jour iterativement) |

## Critere de succes

- Ratio VERB/INGR entre 1:3 et 1:8
- 0 sequence de 3+ INGR consecutifs
- 15+ ingredients identifies par nom
- 1+ sequence de 4 ingredients matchant l'Antidotarium
