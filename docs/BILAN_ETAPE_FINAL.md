# BILAN D'ETAPE COMPLET — 11 avril 2026

## LA QUESTION : on continue ou on arrete ?

Pour repondre honnetement, voici TOUT ce qu'on sait, ce qu'on croit savoir,
ce qu'on ne sait pas, et ce qui est faux. Sans complaisance.

---

## 1. CE QUI EST CERTAIN (prouve mathematiquement ou par cross-validation)

### 1a. La table des 16 logograms
```
o=ac  l=se  d=de  r=recipe  v=vel  x=crux  k=cum  m=misce
f=per  t=el  y=in  c=cum  s=est  sh=ci  p=usque  air=aier
```
**Preuve :** Cross-validation bifolio bH1 (f57v et f66r = meme feuille physique).
9/9 glyphes matchent entre les deux pages. 0 exception.
**Fiabilite : 99%** — C'est le resultat le plus solide de tout le projet.

### 1b. Le systeme de 14 suffixes flexionnels
Les MEMES racines (ch, sh, ok, qok, ot, d) prennent 10 a 14 suffixes differents.
Ce n'est PAS du hasard — c'est un systeme grammatical.

**Prouve :**
- -am est terminateur de phrase : 71% en position finale de ligne
- -or est ouvreur : 22% en position 1
- Gradient positionnel continu de -or (0.39) a -am (0.83)
- Anti-correlation -ol/-edy entre sections (ratio 0.17)
- Racine "d" est fonctionnelle (entropie 0.82, 48% -aiin)

**Fiabilite : 95%** — Les distributions sont des faits. L'INTERPRETATION
(quel suffixe = quel role) reste une hypothese.

### 1c. Le VMS est un nomenclator (au moins pour les logograms)
**Preuve :** Attack 04 — correlation r=0.17 (quasi nulle) entre longueur
EVA et longueur latin pour les 16 logograms connus.

**ATTENTION :** Ce test ne porte que sur les LOGOGRAMS (1-2 glyphes).
Les mots LONGS (5-6 glyphes) n'ont PAS ete testes faute d'ancres.
K&A pourrait encore marcher pour les mots longs.

**Fiabilite : 90% pour les logograms, INCONNU pour les mots longs.**

### 1d. Les sections utilisent des vocabulaires differents
**Prouve :**
- Herbal : -ol dominant (55%)
- Balnea : -edy dominant (44%)
- Pharma : -edy + -ain
- Astro : -al + -ar + -dy (un TROISIEME registre)
- 41% du vocabulaire astro partage avec herbal

**Fiabilite : 99%** — C'est du comptage direct.

### 1e. `aiin` est grammatical
**Prouve :**
- "est aiin" = bigram le plus frequent (58x)
- "recipe aiin" = 27x (apres un verbe, pas un ingredient)
- aiin =/= aquam (corrige session 6)
- aiin =/= dosage (72 sur f103r vs 7 dans Aurea)

**Fiabilite : 95%.** C'est grammatical. Mais on ne sait pas CE QUE c'est.

### 1f. L'astro n'est PAS un Tacuinum
**Preuve :** 5 tests independants :
- Structure : 30 labels/page (pas 7)
- Ratio galenique : faux positif (p=1.0 permutation)
- Vocabulaire positionnel : CV=0.02 (prose, pas colonnes)
- Repetitivite : TTR=0.45 (trop divers pour du tabulaire)
- Labels : TTR=0.72 (noms uniques)

**Fiabilite : 95%.**

---

## 2. CE QU'ON CROIT SAVOIR (indices, pas preuves)

### 2a. Le VMS est pharmaceutique
**Indices :**
- Verbes pharma identifies : recipe, misce, coque(?), tere(?)
- Structure ingredient-verbe sur f103r
- 28/30 matchs distribution AN (session 6)
- Nomenclator italien : 4466 noms de plantes
- 105/108 plantes herbal nommees (gallows + nomenclator)

**Ce qui cloche :**
- Les 13 mots suspects (11% du texte) n'ont PAS de decode coherent
- Le ratio verbe/ingredient (1:10-13) ne matche NI l'AN (1:30) NI le CI (1:3-5)
- Aucune recette complete n'a ete identifiee et lue de bout en bout
- Les "verbes K&A" (coque, tere, cola) ne sont PAS confirmes independamment

**Fiabilite : 70%.** C'est probablement pharma, mais la structure ne
correspond a AUCUN format de recette medieval connu.

### 2b. Les matchs de frequence
- I_cinnamomum -> otey (delta=0.0)
- I_mel -> okedy (delta=0.2)
- I_myrrha -> okeeody (delta=0.0)

**Ce qui cloche :**
- Avec 24 folios et des entiers, beaucoup de mots ont le meme nombre de folios
- Pas de validation par co-occurrence
- Pas de validation par contexte
- Le meme probleme que le ratio galenique (Zipf artifact) pourrait s'appliquer

**Fiabilite : 30%.** Candidats, pas certitudes.

### 2c. Gallows = prepositions en herbal
p/f = per (58 pages), k = cum (21 pages), t = el (20 pages).
Le gallows est le premier mot de chaque page herbal.

**Fiabilite : 60%.** Coherent avec les logograms, mais pourquoi
CERTAINES pages n'ont PAS de gallows ?

### 2d. K&A fonctionne pour les mots longs
84% des mots DOUTE_KA sont valides dans Perseus (session 6).

**Ce qui cloche :**
- Perseus accepte BEAUCOUP de mots (c'est un dictionnaire large)
- 84% de "valide" ne veut pas dire 84% de "correct"
- Les 4 mots qui decodent en "eius" prouvent que K&A peut
  donner le meme resultat pour des mots DIFFERENTS

**Fiabilite : 40%.** K&A marche "un peu" mais produit du bruit massif.

---

## 3. LE SYSTEME DE NUMERATION

Tu as pose la question specifiquement. Voici l'etat :

### Hypothese session 6 (PROBABLEMENT FAUSSE)
```
a = ana (de chaque)
i = 1 (une unite)
ii = 2
n = drachme
e = et (connecteur)
h = muet
```

**Pourquoi c'est probablement faux :**
- Produit 72 "dosages" sur f103r vs 7 dans l'Aurea
- Les abreviations medievales reelles (.z.ii. = 2 drachmes) ne ressemblent
  PAS aux sequences EVA (aiin, ain, etc.)
- Le suffixe -aiin est GRAMMATICAL (prouve attaque 06), pas un dosage
- Les "unites" (n=drachme) n'ont aucune validation independante

**Ce qui POURRAIT etre vrai :**
- Les points dans les manuscrits (.z.ii.) pourraient correspondre
  a des SEPARATEURS dans le VMS (mais lesquels ?)
- Le mot "ana" existe dans le VMS ? Pas identifie.

**Fiabilite du systeme de numeration : 10%.** A considerer comme FAUX
jusqu'a preuve du contraire.

---

## 4. CE QUI EST FAUX (refute)

| Hypothese | Refutation |
|-----------|-----------|
| aiin = aquam | okaiin=cura, trop frequent |
| aiin = dosage | 72 sur f103r vs 7 dans Aurea |
| a=ana, i=1, n=drachme | Produit trop de dosages, -aiin est grammatical |
| L'astro = Tacuinum | 5 tests negatifs |
| Le ratio galenique discrimine | Artefact Zipf, p=1.0 |
| Systeme different pour L04 | 10/19 mots apparaissent ailleurs |
| Syllabaire (t=lo, l=sa) | Ne marche que sur 2 ancres |
| Substitution simple pour ingredients | 0 cascade |
| Anagrammes (aros=rosa) | Coincidence |

---

## 5. CE QU'IL RESTE A DECHIFFRER

| Element | Volume | Difficulte |
|---------|--------|------------|
| Les 14 suffixes (quel role EXACTEMENT?) | 14 mappings | HAUTE — pas de reference directe |
| Les ~50 mots les plus frequents (chol, daiin, shedy, chedy...) | 50 mots = 60% du texte | HAUTE — les "13 suspects" sont la |
| Le systeme de numeration/dosage | ? | TRES HAUTE — rien de confirme |
| Les noms d'ingredients (pas les fonctionnels) | ~200 mots | MOYENNE — matchs de frequence possibles |
| La structure des recettes (segmentation) | ~100 recettes ? | HAUTE — separateurs inconnus |
| Le sens des mots astro (labels) | ~645 mots uniques | HAUTE — pas de crib |
| Le contenu de la volvelle f57v | 1 page | MOYENNE — L03/L04/L05 partiellement analyses |

---

## 6. CE QU'ON A CONSTRUIT (infrastructure)

| Ressource | Volume | Etat |
|-----------|--------|------|
| Referentiels R01-R08 | 869 concepts | PRET |
| Sources tokenisees S01-S10 | 399K tokens | PRET |
| Tacuinum S12 | 280 substances | PRET |
| Corpus brut GPU | ~5M+ tokens | PRET |
| VMS parse (lib/vms_parser.py) | 39K tokens structures | PRET |
| Registre de candidats (lib/candidate_store.py) | Architecture prete | VIDE (pas encore alimente) |
| Scoreur (lib/scorer.py) | 6 fonctions de scoring | PRET |
| Attack 04 (mot vs syllabe) | Execute | NOMENCLATOR confirme |
| Attack 06 (contexte logograms) | Execute | aiin=grammatical |
| Attack 02 (frequence) | Preliminaire | Matchs a valider |
| Attaques GPU (A-F) | Concues, pas codees | PLANIFIE |

---

## 7. BILAN FINANCIER (temps investi vs resultats)

| Session | Heures | Decouverte majeure | Valeur |
|---------|--------|-------------------|--------|
| S1-S5 | ~40h | Pipeline K&A, 25 ingredients | Fondation |
| S6 | ~20h | Dict 7820 mots, 217 ingredients, bifolio | HAUTE |
| S7 | ~12h | 14 suffixes, nomenclator, Tacuinum refute | HAUTE |
| **Total** | **~72h** | | |

**Rendement :** ~1 decouverte majeure toutes les 10h.
Le projet avance. Mais les decouvertes sont STRUCTURELLES (on comprend le systeme)
pas LEXICALES (on ne lit pas encore les mots).

---

## 8. DECISION : ON CONTINUE OU ON ARRETE ?

### Arguments pour CONTINUER
1. L'infrastructure est PRETE — le referentiel, les parsers, le registre
2. Les attaques GPU ne sont PAS encore lancees — c'est la qu'est la puissance
3. Le systeme suffixal est une decouverte ORIGINALE — personne n'a ca
4. L'Attack 02 (frequence) a des candidats prometteurs a valider
5. On a 400K tokens de reference + 5M de corpus brut = assez pour le ML

### Arguments pour ARRETER
1. Apres 72h, on ne lit toujours PAS un seul mot avec certitude (hors logograms)
2. K&A est au mieux partiellement faux, au pire completement faux
3. Le systeme de numeration est probablement faux
4. Les "13 mots suspects" (11% du texte) n'ont pas avance d'un pouce
5. Chaque "decouverte" ouvre plus de questions qu'elle n'en ferme
6. Le risque que le VMS soit un canular ou un langage construit reste non-nul

### MA RECOMMANDATION

**CONTINUER, mais changer de strategie.**

On a passe 72h a comprendre la STRUCTURE. C'est fait.
Maintenant il faut DECODER des MOTS. Pas des patterns, pas des distributions —
des MOTS INDIVIDUELS qu'on peut VERIFIER.

Les 3 prochaines actions a TRES HAUT rendement :

1. **Validation croisee des matchs de frequence** (2h)
   otey=cinnamomum ? Tester par co-occurrence avec les AUTRES candidats.
   Si otey et okeeody co-apparaissent la ou cinnamomum et myrrha co-apparaissent
   dans l'AN → c'est quasi-certain.

2. **Crib Aurea sur f103r** (4h)
   On a l'Aurea tokenisee (105 tokens, 80% ref). On a f103r.
   Retirer les logograms, aligner les mots restants avec les 68 ingredients.
   Si 10+ matchent → on a 10 mots decodes.

3. **GPU embedding alignment** (4h GPU)
   word2vec sur le corpus latin (5M tokens) + word2vec sur le VMS (39K tokens).
   Procrustes alignment avec les 16 logograms comme ancres.
   INDEPENDANT de K&A. Si ca produit des matchs coherents avec (1) et (2) → convergence.

**Si apres ces 3 actions on n'a TOUJOURS rien — alors on arrete.**
On publie ce qu'on a (le systeme suffixal, le nomenclator, le referentiel)
et on laisse d'autres continuer.

---

## 9. RESUME EN UNE PHRASE

On a decouvert le SQUELETTE du systeme d'ecriture
(16 logograms + 14 suffixes + nomenclator)
mais on n'a pas encore decode la CHAIR (les mots individuels).
Les 10 prochaines heures diront si c'est possible ou non.
