# H04 — BILAN FINAL : L04 = cycle lunaire 29 jours ?

## Hypothese

L'anneau L04 de f57v (29 mots) encode un calendrier lunaire pharmaceutique
(lunarium de aegrotis) ou un calendrier zodiacal medical (Fasciculus Medicinae).

## Tests realises

### Test 1 — Crib semantique (5 lunaires medievaux)
- **Script** : lunaire_crib.py
- **Methode** : aligner les 29 mots decodes avec le consensus de 5 lunaires
  (Arsenal 2782, BnF Fr 2074, BnF Fr 837, BnF Fr 1745, saignee)
- **Score** : 27/87 = **31%**
- **Matches forts** : 3/29 (aquam j1, crux j19, aquam j25)
- **Matches coherents** : 6/29

### Test 2 — Crib lexical latin (beam K&A = 50)
- **Script** : lunaire_latin_crib.py
- **Methode** : chercher dans les 50 chemins K&A de chaque mot un terme
  du vocabulaire lunaire latin atteste (80+ termes)
- **Score** : 9/87 = **10%**
- **Matches forts** : 2/29 (crux j19, luce j27)
- **Verdict** : FRAGILE

### Test 3 — Hypothese zodiacale (glyphes isoles)
- **Script** : zodiac_crib_attack.py + HYPOTHESE_ZODIACALE.md
- **Methode** : tester si les 9 glyphes isoles marquent les transitions
  entre signes zodiacaux (29j / 12 signes = ~2.46j par signe)
- **Correlation brute** : 8/9 glyphes a ≤1.0 jour d'une frontiere (88%)
- **Test de permutation (n=10000)** : p = **0.49**
- **Verdict** : **NON SIGNIFICATIF** — la densite des frontieres (11 dans 29j)
  rend ce resultat attendu par hasard

### Test 4 — Crib zodiacal (Fasciculus Medicinae)
- **Source** : FASCICULUS_CRIB_ZODIACAL.md
- **Methode** : comparer les mots-cles zodiacaux du Fasciculus avec les decodages
- **Matches notables** : aquam/balneum (Aries), crux/Scorpio, lier/reconciliare (Sagittarius)
- **Score estime** : ~12-15% — memes matches que les tests precedents
- **Verdict** : pas de valeur ajoutee par rapport aux tests 1-2

### Test 5 — Analyse structurelle inversee (9 tests statistiques)
- **Script** : l04_structural_analysis.py
- **Methode** : comparer la STRUCTURE de L04 avec celle d'un lunaire connu

#### Resultats cles :

| Mesure | L04 | Lunaire attendu | Compatible ? |
|--------|-----|-----------------|--------------|
| Mots uniques | **27/29** (93%) | 7-10/29 (25-35%) | **NON** |
| Taux repetition | **6.9%** | 40-50% | **NON** |
| Pearson longueur | r = 0.200 | r > 0.5 attendu | **NON** |
| Entropie | H = 3.74 bits | ~2.5-3.0 bits (abrege) | **NON** |
| Diff bons/mauvais | p = 0.642 | p < 0.05 attendu | **NON** |
| Permutation zodiacale | p = 0.490 | p < 0.05 attendu | **NON** |

---

## VERDICT FINAL : HYPOTHESE AFFAIBLIE

### Ce qui reste vrai
1. **29 mots** = nombre exact du mois lunaire synodique (fait structurel)
2. **Position sur volvelle** f57v = instrument calendaire probable
3. **x = CRUX au jour 19** = match semantique fort (mais 1 match sur 29)
4. **daiin aux jours 1 et 25** = repetition structurelle intrigante

### Ce qui est refute
1. **L04 n'est PAS un lunaire abrege** : 27 mots uniques vs 7-10 attendus
2. **Les glyphes isoles ne sont PAS des marqueurs zodiacaux** : p = 0.49
3. **Le decodage K&A ne produit PAS de vocabulaire lunaire** : 10% lexical
4. **Aucune signature structurelle** ne distingue jours bons de jours mauvais
5. **L'entropie** est trop haute pour un texte codifie/abrege

### Hypotheses alternatives survivantes
1. **L04 = etiquettes de volvelle** : 29 NOMS (ingredients, operations, reperes)
   et non 29 PHRASES. Explique les 27 mots uniques.
2. **L04 = nomenclateur** : systeme d'encodage different du K&A pharmaceutique.
   Les noms propres (plantes, signes) utilisent un code different.
3. **L04 = systeme mixte** : 9 marqueurs structurels + 20 mots-contenu,
   le contenu etant pharmaceutique mais les marqueurs non decodes.

### Recommandation
Classer H04 comme **AFFAIBLIE** (pas refutee completement a cause du nombre 29).
Reorienter vers l'hypothese "etiquettes de volvelle" :
- Tester si les 20 mots-contenu sont des ingredients Antidotarium
- Tester si les 9 glyphes isoles sont des CHIFFRES (numeration par position)
- Comparer avec les etiquettes de volvelles connues (Ashmole 370, etc.)

---

## Fichiers dans ce dossier

| Fichier | Description |
|---------|-------------|
| BILAN_H04_FINAL.md | Ce document — bilan consolide |
| L04_STRUCTURAL_ANALYSIS.md | Analyse structurelle (9 tests) |
| LUNAIRE_CRIB_RESULTS.md | Crib semantique (5 lunaires) |
| LUNAIRE_LATIN_CRIB.md | Crib lexical latin (beam=50) |
| LUNAIRE_LATIN_RECONSTRUCTION.md | Lunaire latin reconstruit |
| HYPOTHESE_ZODIACALE.md | Hypothese zodiacale |
| SOURCE_lunaires.md | 5 lunaires complets |
| SOURCE_lunaire_latin.md | Sources latines |
| lunaire_crib.py | Script crib semantique |
| lunaire_latin_crib.py | Script crib lexical |
