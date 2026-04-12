# PLAN : Attaque Volvelle f57v — Exploiter la clé du cipher

## Ce qu'on a trouvé

La volvelle f57v contient 5 lignes critiques + 8 labels de disque :

### L3 — LA TABLE (4 répétitions avec variantes)
```
Rep 1: o l d r v x k m f t r y i
Rep 2: o l d r v x k m f t r y c
Rep 3: o l d r v x k m p t r y c
Rep 4: o l d r v x k m p t r y c
```

**13 glyphes** dans un ordre fixe, avec 2 positions variables :
- Position 8 : f ↔ p
- Position 12 : i ↔ c

### L5 — LA PERMUTATION
```
o v l r m aiin d c f s y l k x l r ar o r a t l s d y [+ 8 mots]
```

25 logograms dans un AUTRE ordre, intercalés de 3 mots (`aiin`, `ar`, `dar`)
puis 5 mots composés (`teodar`, `otodal`, `sheky`, `oteeody`) puis `x s l`.

### L2 — HEADER (54 mots, 38% logograms)
### L4 — ENTRE CLÉ ET PERMUTATION (30 mots, 33% logograms)
### L6-L13 — 8 LABELS autour du disque (mots isolés)

---

## AXES D'ATTAQUE

### AXE 1 : La table L3 est-elle un ALPHABET ORDONNÉ ?

**Hypothèse** : `o l d r v x k m f t r y i/c` = les 13 "lettres" de
l'alphabet Voynich dans leur ordre canonique.

**Test** :
- Compter combien de ces 13 glyphes couvrent du vocabulaire VMS
- Les comparer à l'alphabet latin médiéval (a b c d e f g h i k l m n o p q r s t v x y z = 23 lettres)
- 13 glyphes ≠ 23 lettres latines → c'est un SYLLABAIRE (chaque glyphe = 2 lettres?) ou un alphabet réduit

**Action** : Lister les 13 glyphes de L3 + vérifier s'ils correspondent
aux 13 glyphes les plus fréquents du manuscrit.

### AXE 2 : Les 2 variantes (f↔p, i↔c) = positions du cadran ?

**Hypothèse** : La volvelle a un disque rotatif. En tournant, certains
glyphes changent de valeur. f et p sont interchangeables dans certaines
positions → f et p représentent le MÊME son/concept dans des contextes
différents.

**Test** :
- Dans le manuscrit, f et p apparaissent-ils dans les MÊMES positions ?
  (début de bloc → gallows → verbe d'ouverture)
- Les mots commençant par f- sont-ils des variantes des mots en p- ?
- i et c : même test. i=1 (dose), c=cum (logogram) — deux valeurs du
  même glyphe selon la position ?

**Action** : Cross-tabulation f/p et i/c dans tous les contextes.

### AXE 3 : La permutation L5 est-elle une TABLE DE DÉCODAGE ?

**Hypothèse** : L3 = alphabet en ordre standard.
L5 = alphabet en ordre CHIFFRÉ. Pour décoder : remplacer L3[i] par L5[i].

**Test** :
- Aligner L3 et L5 position par position
- Appliquer cette substitution sur tout le manuscrit
- Vérifier si le texte devient plus "latin" (fréquences, n-grams)

**Action** : Construire la table de substitution L3→L5 et l'appliquer.

### AXE 4 : L2 et L4 = TEXTE EXEMPLE ?

**Hypothèse** : L2 (54 mots) et L4 (30 mots) sont des textes-exemples
montrant comment lire le manuscrit. L2 = texte chiffré, L4 = texte
déchiffré (ou l'inverse).

**Test** :
- L2 a 38% de logograms, L4 a 33% — ratios similaires
- Sont-ils le MÊME texte avec des substitutions différentes ?
- Comparer mot par mot : mêmes positions de logograms ?

**Action** : Alignement L2↔L4, chercher correspondances.

### AXE 5 : Les 8 labels L6-L13 = NOMS DES SECTEURS ?

**Hypothèse** : Les 8 mots isolés autour du disque sont des labels
pour les 8 sections du manuscrit (herbal_a, herbal_b, pharma, balnea,
astro, cosmo, bio, volvelle).

```
L06: otodarag       → ?
L07: oparairdly     → ?
L08: olkeedal       → ?
L09: otardaly        → ?
L10: arkaldy         → ?
L11: araarar         → ?
L12: okeely          → ?
L13: ocfhor okear    → ?
```

**Test** :
- 8 labels, 8 sections → coïncidence ou structure ?
- Suffixes : -ag, -dly, -dal, -daly, -dy, -ar, -ly, -ar
  → Des suffixes qu'on connaît ? (-al, -ar, -dy = OUI)
- K&A decode de ces 8 mots → noms latins de sections ?

**Action** : Décoder les 8 labels par K&A et par table de logograms.

### AXE 6 : Le "g" mystérieux

**Observation** : L2 contient `g` — un glyphe qui N'APPARAÎT presque
nulle part ailleurs dans le manuscrit. Sur f1r, Reeds a trouvé g↔y.

**Test** :
- Combien de `g` dans tout le manuscrit ?
- Sont-ils tous sur f57v et f1r ?
- Si g=y (Reeds), alors dans L2 : `l g sos` = `se y(in) sos` = ?

**Action** : Recenser tous les `g` du manuscrit.

### AXE 7 : Reconstituer le DISQUE physique

**Hypothèse** : f57v est une volvelle (page avec disque découpé).
Les lignes L2-L5 sont sur des ANNEAUX concentriques.
Les labels L6-L13 sont autour du disque.

**Test** :
- Regarder l'image f57v : identifier les anneaux
- Mapper chaque ligne sur un anneau
- Simuler la rotation : quel texte produit chaque position ?

**Action** : Reconstruction numérique de la volvelle.

### AXE 8 : ANTI-TEST — Est-ce vraiment une clé ?

**Null hypothesis** : La séquence `o l d r v x k m f t r y` n'est pas
une clé mais un texte normal qui utilise beaucoup de logograms (comme
la volvelle en général — 58% LOGO).

**Test** :
- Quelle est la probabilité qu'une séquence de 13 logograms consécutifs
  apparaisse par hasard, sachant que la volvelle a 58% de logograms ?
- Permutation test : combien de runs de 13+ logograms consécutifs
  existent dans tout le manuscrit ?

**Action** : Test statistique de significativité.

---

## PRIORITÉS

1. **AXE 8** (anti-test) — D'abord vérifier que ce n'est pas un artefact
2. **AXE 1** (alphabet) — Confirmer la nature de la séquence
3. **AXE 2** (f↔p, i↔c) — Les variantes sont le signal le plus exploitable
4. **AXE 3** (substitution L3→L5) — Le test le plus direct
5. **AXE 5** (labels) — Rapide et informatif
6. **AXE 6** (g) — Rapide
7. **AXE 4** (L2↔L4) — Plus complexe
8. **AXE 7** (disque) — Nécessite l'image

---

## CRITÈRE DE SUCCÈS

Si c'est vraiment la clé :
- L'AXE 3 (substitution L3→L5) devrait produire des fréquences de lettres
  plus proches du latin sur au moins un folio de test
- L'AXE 2 devrait montrer que f et p sont interchangeables dans des
  contextes précis et prévisibles
- L'AXE 8 devrait montrer p < 0.01 (la séquence n'est pas due au hasard)
