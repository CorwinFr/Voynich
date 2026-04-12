# PLAN SESSION 12 — L'Alphabet Complet via la Volvelle

## Contexte

Session 11 a produit le décodage structurel complet (38437 mots, 226 folios).
La découverte majeure : la volvelle f57v.3 contient **17 symboles** (pas 13),
dont 4 glyphes spéciaux (@169-@172) que notre parser avait ignorés.

Une seconde analyse (IA externe) a identifié **deux couches** de glyphes :
- Couche 1 (volvelle) : 13 glyphes = c d f k l m o p r t v x y
- Couche 2 (absente) : 7 glyphes = a e h i n q s

Si h est un modificateur (ch/sh/th/kh/ph = composites), l'alphabet effectif
tombe à **16-17 glyphes** = exactement le nombre sur la volvelle.

## PHASE 1 — PARSER LES @169-@172 (bloquant)

**Objectif** : Identifier ce que sont ces 4 glyphes spéciaux.

**Actions** :
1. Chercher @169, @170, @171, @172 dans TOUT le ZL.txt et LSI.txt
   - Où apparaissent-ils en dehors de f57v ?
   - @172 est sur f66r avec "cf f57v" — d'autres aussi ?
2. Chercher la documentation EVA/IVTFF pour la signification des @NNN
3. Vérifier les scans HD : à quoi RESSEMBLENT ces glyphes visuellement ?
4. Tester l'hypothèse @169=e, @170=a, @171=i, @172=n
   (les 4 absents les plus fréquents après h et q)

**Fichier** : `project_hope/session_12/phase1_at_symbols.py`
**Résultat** : Identification des 4 symboles → mise à jour knowledge_base.json

## PHASE 2 — RE-TOKENISATION (l'alphabet réel)

**Objectif** : Reconstruire le texte avec l'alphabet VISUEL, pas EVA.

**Actions** :
1. Fusionner ch→CH, sh→SH, th→TH, kh→KH, ph→PH (5 composites)
2. Intégrer les @169-@172 comme glyphes à part entière
3. Recalculer TOUTES les fréquences avec le nouvel alphabet (~17 glyphes)
4. Comparer les fréquences avec le latin médiéval
5. Vérifier si l'alphabet réduit = exactement les symboles de la volvelle

**Fichier** : `project_hope/session_12/phase2_retokenize.py`
**Résultat** : `vms_retokenized.json` — nouveau texte source

## PHASE 3 — TEST DE SUBSTITUTION (la permutation L3→L5)

**Objectif** : La permutation est-elle un chiffre de substitution ?

La volvelle donne un mapping position-par-position :
```
L3: o  l  d  r  v  x  k  m  f  @169 t  r  @170 @171 y  c  @172
L5: o  v  l  r  m  aiin d @170 c  f   s  y  l    k    x  l  r
```

**Actions** :
1. Appliquer la substitution L3→L5 au texte retokenisé
2. Appliquer la substitution INVERSE L5→L3
3. Pour chaque direction : mesurer si les fréquences de bigrammes
   se rapprochent du latin
4. Tester les 4 configurations (f/p × i/c)
5. Si une configuration produit des mots latins reconnaissables → JACKPOT

**Fichier** : `project_hope/session_12/phase3_substitution.py`

## PHASE 4 — TEST ol=et (confirmer ou éliminer)

**Objectif** : Le ratio ol/al = 2.11 ≈ et/in = 2.08 est troublant.
Nos données disent ol≠et (précédé par DOSE 19%). Mais il faut un test
DÉFINITIF.

**Actions** :
1. Si ol=et → o=e, l=t → or=es/ex, al=in
2. Appliquer ces mappings aux 50 mots les plus fréquents
3. Vérifier : les mots résultants sont-ils du latin ?
4. Test spécifique : dans les positions où ol apparaît, est-ce que "et"
   serait grammaticalement correct en latin pharma ?

**Fichier** : `project_hope/session_12/phase4_ol_test.py`

## PHASE 5 — DÉCODER LES 8 LABELS

**Objectif** : Les 8 labels de la volvelle (f57v.6-13) doivent devenir
des mots latins lisibles si on a le bon mapping.

```
dairol, otodarag, oparairdly, olkeedal, otardaly,
arkaldy, araarar, okeely, ocfhor okear
```

**Actions** :
1. Appliquer chaque hypothèse de substitution aux 8 labels
2. Chercher dans les dictionnaires médiévaux latins/italiens
3. Si un label = un mot latin connu → validation de l'hypothèse

**Fichier** : `project_hope/session_12/phase5_labels.py`

## PHASE 6 — VALIDATION SUR f103r

**Objectif** : Appliquer le décodage qui marche sur f103r et produire
du texte lisible.

**Critères de succès** :
- Au moins 5 mots latins reconnaissables par recette
- Structure Recipe INGR DOSE INGR DOSE visible
- Noms d'ingrédients de l'AN identifiables

## DÉPENDANCES

```
PHASE 1 (@169-@172)
    ↓
PHASE 2 (re-tokenisation) ← nécessite Phase 1
    ↓
PHASE 3 (substitution)    ← nécessite Phase 2
PHASE 4 (ol=et)           ← indépendant
PHASE 5 (labels)          ← nécessite Phase 3
    ↓
PHASE 6 (validation)      ← nécessite Phase 3 ou 4
```

Phase 1 est BLOQUANTE. Sans les @169-@172, on ne peut pas compléter
l'alphabet ni tester la substitution correctement.

## DONNÉES ACQUISES (session 11)

- **ZL3b-n.txt TÉLÉCHARGÉ** (version 3b du 13/05/2025, voynich.nu)
  - Correction majeure : `@169;v` = UN token composite (v collé, pas séparé)
  - Notre ancien ZL (2022) avait `@169;.t` (point = séparé) → FAUX
  - @169 passe de 4→5 occurrences, 4 nouveaux codes @231-@234
- LSI.txt : 3 transcripteurs (H/V/U) — tous notent @169-@172 comme `?`
- @172 sur f66r.38 avec "cf f57v", f66r.37 a `c<!cf f57v seq.>`
- @169=5 occ., @170=5, @171=5, @172=6 dans tout le manuscrit
- Scan f57v disponible (114_57v.jpg) mais résolution insuffisante
- **ZL3b est dans** `data/transcriptions/ZL3b-n.txt`

## DONNÉES NÉCESSAIRES

- Scans HD de f57v : Yale Digital Library (beinecke.library.yale.edu)
- Police Eva-2 de Landini : table visuelle des @130-@199
- voynich.nu/transcr.html Table 4 : images des glyphes spéciaux
- knowledge_base.json : déjà construit (Session 11)

## CONTEXTE EXTERNE (recherche littérature)

- Nick Pelling : les 17 glyphes pourraient être 18 (2 fusionnés)
- Voynich Attacks : 17 = consonnes latines (22 - 5 voyelles) → abjad ?
- Emma May Smith : séquence = chiffres pas lettres ?
- Darren Worley : pilcrow bohémien (1445-1465) en bas de f57v
- IVTFF v2.0.2 (2025) : @169 a eu une correction de définition
- 3 nouveaux codes (221-223) ajoutés en 2025
