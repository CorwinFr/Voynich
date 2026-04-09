# Diagnostic computationnel : King & Andrisani (2019)

## Auteur : Guillaume (FLI) / Assisté par Claude
## Date : 2026-04-07
## Statut : TEST COMPLET

---

## 1. Methode

Extraction systematique de la table K&A depuis leur publication (PDF + JSON 22 glyphes). Alignement caracteriere par caractere entre le texte EVA (ZL.txt) et les transliterations K&A de f1v (12 lignes) et f9v (11 lignes). Verification croisee sur f9v ligne 2 : 11/11 mots alignes parfaitement. Construction du mapping EVA-vers-K&A. Application au VMS complet (32 085 tokens, 8 397 types) avec scoring bigramme latin 1.82M mots.

---

## 2. Le mapping EVA vers K&A (confirme par alignement)

| EVA | K&A glyph | Valeurs latines | Confiance | Obs. |
|-----|-----------|-----------------|-----------|------|
| o | "e" | e, a, ae | HAUTE | 21 |
| a | "u" | u | HAUTE | 8 |
| ch | "i" | i | HAUTE | 15 |
| e | "o" | o | HAUTE | 3 |
| c | "o" | o (=e) | MOYENNE | - |
| d | "de" | d, de, ed | HAUTE | 8 |
| k | "que" | qu, c, aequ | HAUTE | 5 |
| t | "le" | l, le, el | HAUTE | 3 |
| r | "re" | r, re, ar, ra | HAUTE | 7 |
| l | "se" | s, se, ce, es | HAUTE | 8 |
| s | "us" | us, su | MOYENNE | 1 |
| y | "un" | n, un, in | HAUTE | 10 |
| q | "co" | co, con | HAUTE | 2 |
| p/f | "pe" | p, pe, per, f | HAUTE | 3 |
| sh | "si" | ci, si | HAUTE | 3 |
| cth | "li" | li, ili, eli | HAUTE | 2 |
| cph/cfh | "pi" | pi, epi, fi | HAUTE | 2 |
| iin | "-ure" | ure, ur, ura | HAUTE | 5 |

Remarque importante : l'alignement est remarquablement propre. Sur f9v ligne 2, les 11 mots s'alignent avec 100% de coherence interne (chaque EVA-char produit la meme valeur K&A a chaque occurrence).

---

## 3. Resultats des metriques

### 3.1 Mots-outils dans le top 20

| Rang | Mot expanse | Freq | Source EVA | En corpus ? |
|------|-----------|------|-----------|------------|
| 1 | duure | 691 | daiin | NON |
| 2 | iodin | 391 | chedy | NON |
| 3 | es | 349 | ol | 242x |
| 4 | ciodin | 346 | shedy | NON |
| 5 | us | 338 | s | 261x |
| 9 | **in** | 263 | chy | **32 102x** |

**Verdict : 1 seul mot-outil dans le top 20 ("in" a rang 9).** Le latin medical attendrait et, in, est, cum, ad, de dans les 10 premiers. "et" est totalement absent du texte expanse.

### 3.2 Reconnaissance dictionnaire

- Meilleure expansion (bigramme) en corpus : **20.4%** (6 551 / 32 085)
- Au moins une expansion valide (mots uniques) : **10.1%** (846 / 8 397)

**Contexte :**
- Lunazzi (Triage T1) : ~0%
- Substitution 1:1 Phase 7 : 0.6% (latin), 4.1% (italien)
- Random baseline : ~2-3%

**Verdict : 20.4% est significativement au-dessus du hasard**, mais la polyvalence du systeme K&A (chaque glyphe a 2-5 valeurs possibles) gonfle ce chiffre. Avec 2-5 choix par position et 5+ positions par mot, on genere des centaines d'expansions par mot. 10.1% des mots uniques trouvent AU MOINS UNE expansion valide parmi des dizaines/centaines de candidats.

### 3.3 Index de Coincidence

- IC du texte expanse K&A : **0.0983**
- IC attendu pour du latin : 0.065 - 0.080
- IC du VMS en EVA : 0.077

**Verdict : IC trop eleve (0.098 > 0.080).** La distribution de caracteres est trop concentree sur quelques lettres. Le texte expanse n'a PAS la distribution d'un texte latin naturel.

### 3.4 Distribution de caracteres

| Lettre | K&A | Latin attendu | Ratio | Diagnostic |
|--------|-----|---------------|-------|-----------|
| u | 11.4% | 7.5% | 1.5x | |
| e | 12.5% | 9.5% | 1.3x | |
| o | 11.7% | 6.3% | 1.9x | |
| i | 14.4% | 11.1% | 1.3x | ok |
| n | 11.3% | 6.2% | 1.8x | |
| t | **0.0%** | **8.6%** | **0.0x** | **ABSENT** |
| b | 0.0% | 1.8% | 0.0x | ABSENT |
| f | 0.2% | 3.5% | 0.1x | quasi-absent |
| g | 0.0% | 1.2% | 0.0x | ABSENT |
| m | 0.5% | 4.4% | 0.1x | quasi-absent |
| v | 0.0% | 1.1% | 0.0x | ABSENT |

**Correlation Pearson K&A vs Latin : 0.796** (bon mais pas excellent).

### 3.5 Phonemes manquants

Le systeme K&A ne peut PAS produire les lettres : b, g, h, j, k, t, v, w, x, y, z.

**Le plus grave : le 't' latin est completement absent.** C'est la 4e lettre la plus frequente en latin (8.6% du texte). Le mot "et" (le plus frequent en latin, 45 204 occurrences dans notre corpus 1.82M) ne peut pas etre produit par le mapping K&A.

K&A argumente que /t/ > /d/ en latin vulgaire au nord de la ligne La Spezia-Rimini. Mais meme en venitien medieval, "et" reste "et" (pas "ed"), et les terminaisons en -t (3e personne verbale : est, habet, facit) ne deviennent pas toutes -d.

**Ces phonemes manquants representent 14.9% du texte latin attendu.** C'est un deficit structurel majeur.

### 3.6 Le test "daiin"

K&A lit "daiin" comme "dura" (durete/affliction). L'expansion bigramme donne "duure" (non atteste). "dura" EST dans le corpus (200x) et est semantiquement plausible pour un texte medical.

Mais : "dura" n'est PAS un mot-outil. Le mot #1 d'un texte latin de 32K tokens devrait etre "et" (5.3% du texte), "in" (3.8%), ou "est" (1.2%). "dura" a une frequence de 200/1.82M = 0.011% dans le corpus medical. A 691/32K = 2.15% dans le VMS, "daiin" est 200 fois plus frequent que "dura" ne l'est en latin medical.

---

## 4. Comparaison avec les tests precedents

| Metrique | K&A | Lunazzi | Mono-subst 1:1 | Seuil "vivant" |
|----------|-----|---------|---------------|---------------|
| Func words top 20 | 1/20 | 0/20 | 0/20 | >5/20 |
| Dict recognition | 20.4% | ~0% | 0.6-4.1% | >30% |
| IC | 0.098 | N/A | 0.077 | 0.065-0.080 |
| Char correlation | 0.796 | N/A | N/A | >0.90 |
| Missing phonemes | 14.9% | N/A | 0% | <5% |

---

## 5. VERDICT

### K&A est FAIBLE, pas MORT

Le mapping K&A est de loin le plus coherent teste jusqu'ici :
- L'alignement EVA/K&A est remarquablement propre (100% consistent sur f9v l2)
- 20.4% de reconnaissance dico vs ~0% pour Lunazzi
- La lecture de f1v comme un traite sur Atropa belladonna est semantiquement coherente
- Les noms celestes (Hyades, Sirius, Arcturus) sur f68r sont plausibles

Mais il a des problemes structurels graves :
- IC trop eleve (0.098 vs 0.065-0.080)
- 14.9% de phonemes latins absents (dont t = 8.6%)
- 1 seul mot-outil dans le top 20
- Le systeme est TROP polyvalent : avec 2-5 valeurs par glyphe, on peut "lire" presque n'importe quoi

### Le dilemme de la polyvalence

C'est le probleme fondamental. K&A dit : "le lecteur fluent en la langue determinerait la valeur correcte d'apres le contexte." Mais si chaque glyphe a 3-5 valeurs et qu'on a 5+ glyphes par mot, on genere des milliers de lectures possibles par phrase. Un systeme aussi ambigu serait ILLISIBLE meme par un lecteur natif.

Pour comparaison : les notes tironiennes historiques ont en moyenne 1.2-1.5 valeurs par signe, pas 3-5. La polyvalence de K&A depasse largement les systemes brachigraphiques attestes.

---

## 6. TEST DE SPECIFICITE (REALISE)

### Question : le 20.4% est-il un artefact de la polyvalence ?

100 mappings aleatoires generes avec la MEME structure de polyvalence que K&A (meme nombre de valeurs par glyphe EVA, memes longueurs de valeurs, lettres latines tirees au hasard). Chacun applique au VMS complet, dict% mesure avec le meme pipeline.

### Resultats :

| | K&A | Random (N=100) |
|---|---|---|
| Dict rate | **20.42%** | mean=10.20%, std=2.85% |
| Min/Max | - | 3.92% / 18.74% |
| **Z-score** | **3.6 sigma** | - |
| **p-value empirique** | **< 0.01** (0/100 random >= K&A) | - |

**Le signal K&A est REEL.** Aucun des 100 mappings aleatoires n'atteint le score K&A. Le meilleur random est 18.74% vs 20.42% pour K&A. A 3.6 sigma, la probabilite que ce soit du hasard est inferieure a 0.02%.

Cela confirme que le mapping K&A capture quelque chose de specifique dans la structure du VMS. Ce n'est PAS un simple artefact de polyvalence.

---

## 7. VERDICT REVISE

### K&A est FAIBLE mais REEL

Le test de specificite change la donne. K&A n'est pas un mirage :

**Signaux positifs (confirmes) :**
- 20.42% dict recognition, significativement au-dessus du hasard (3.6 sigma, p < 0.01)
- Alignement EVA/K&A internement coherent (11/11 sur f9v l2)
- Le mapping capte une structure reelle du VMS

**Problemes structurels (non resolus) :**
- IC trop eleve (0.098 vs 0.065-0.080)
- 14.9% de phonemes latins absents (t = 8.6%)
- 1 seul mot-outil dans le top 20
- Polyvalence excessive par rapport aux systemes brachigraphiques attestes

### Interpretation

Le mapping K&A est "dans la bonne direction" mais pas au bon niveau de precision. Il y a probablement une correspondance partielle entre les glyphes Voynich et les sons tironniens proposes par K&A, mais le mapping exact est incomplet ou degrade par :
- L'atomisation EVA (qui coupe des glyphes composites en faux caracteres unitaires)
- L'absence de normalisation latin classique / latin vulgaire
- Des assignations incorrectes pour certains glyphes rares

---

## 8. PLAN D'ACTIONS V2

### Piste principale : Raffiner K&A (le signal est reel)

1. **Reduire la polyvalence** : utiliser les contraintes morphologiques V1 (13 suffixes) pour eliminer les valeurs impossibles par position. Si EVA '-y' = K&A "un" (n/un/in), tester laquelle des 3 valeurs est la plus frequente en position finale latine.

2. **Compenser les phonemes manquants** : ajouter une couche de normalisation t/d, b/v pour le latin vulgaire. Tester si le remplacement systematique de 'd' par 't' dans certaines positions ameliore la reconnaissance.

3. **Tester sur les ancres botaniques** : verifier que le mapping produit des noms de plantes coherents sur les 106 folios identifies. Le test f9v = Viola tricolor ("ion" dans K&A) est deja un bon signe.

4. **Valider les noms celestes** : extraire les labels de f68r1/f68r2 dans ZL.txt et verifier si le mapping K&A produit les noms d'etoiles publies (Hyades, Sirius, Arcturus, etc.).

5. **Construire un corpus de latin vulgaire** venitien/nord-italien pour recalibrer le modele bigramme et la distribution de caracteres attendue.

### Piste parallele : Approche hybride

Combiner le mapping K&A (qui capte un signal reel) avec les ancres botaniques V1 (106 cribs) et la grille suffixale (13 paradigmes). Pipeline :
1. K&A comme initialisation du mapping
2. Propagation de contraintes depuis les ancres botaniques
3. Verification par grille suffixale a chaque etape
4. Scoring par modele de langue (bigramme ou LLM)

### Piste exploratoire : Images directes

Si le raffinement K&A plafonne, passer a l'analyse directe des images Beinecke HD avec Claude Vision pour decomposer visuellement les glyphes en composantes tironiennes.

---

*"3.6 sigma. Le signal est la. La question n'est plus SI, mais COMBIEN."*
