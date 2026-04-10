# L04 - REPRENDRE A ZERO : QU'EST-CE QUE CHAQUE LABEL APPORTE ?
## Hypotheses reformulees a partir du principe d'usage quotidien

Date : 2026-04-10

---

## LE PRINCIPE DIRECTEUR

L'utilisateur consultait cet instrument CHAQUE JOUR. Il ne passait pas une heure
a dechiffrer. Il regardait, il lisait, il SAVAIT. Chaque label lui apportait une
information pratique, immediatement actionnable.

Question centrale : **QUELLE information ?**

---

## CADRE PHYSIQUE DE L04

L04 est l'anneau EXTERIEUR de f57v. Les anneaux interieurs (L01, L02, L03) encodent
probablement le mecanisme calendaire/astronomique. L04 est le RESULTAT : ce que
l'utilisateur lit APRES avoir positionne le mecanisme.

29 positions. 20 "mots" (2+ glyphes). 9 glyphes isoles. 1 symbole special (@172).
Le mot `daiin` se repete (j1 = j25).

---

## LES HYPOTHESES

### H1. NOMS DE MANSIONS LUNAIRES
*Ce qu'on a teste jusqu'ici*

Chaque label = le nom (arabe/latin) de la mansion lunaire correspondante.
L'utilisateur lit "dainn" et pense "al-Butain" ou "Alnath".

**Pour :** 28 mansions ~ 28 positions uniques. Le pont f68r1 (etoiles). Le contexte
astronomique de f57v.

**Contre :** Aucun offset de rotation ne domine. Les scores phonetiques restent
faibles (max moyen 0.43). 9 glyphes isoles seraient des abreviations - possible
mais 28 mansions ont des noms trop longs pour etre abregees en 1 lettre sans ambiguite.

**Testabilite :** 7/10. Deja teste, resultats mitigés.

---

### H2. NOMS DE PLANTES / HERBES (prescription quotidienne)

Chaque label = le nom de la PLANTE a utiliser ce jour-la. L'utilisateur lit
"dainn" et pense "c'est le jour du daiinum / de l'herbe X".

**Pour :** Le VMS est tres probablement un ouvrage medical/pharmaceutique. Les pages
"recettes" montrent des plantes avec du texte. L'usage quotidien a plus de sens avec
une prescription qu'avec un nom d'etoile. Un praticien veut savoir QUOI FAIRE, pas
ou est la lune.

**Contre :** Aucune liste canonique herbe-par-mansion ne survit dans la litterature
medievale. Les noms de plantes latines sont generalement longs (3-5 syllabes :
plantago, artemisia, cinnamomum...). Difficile de matcher avec les mots courts de L04.

**Testabilite :** 6/10. On peut comparer avec les herbiers du VMS : si les mots de L04
apparaissent dans les sections herbier/pharma du VMS, c'est un signal fort.

**TEST PROPOSE :** Extraire les labels des illustrations de plantes du VMS (herbal
section, folios 1-66) et chercher des recoupements avec les mots de L04.

---

### H3. PARTIES DU CORPS (melothesie lunaire)

Chaque label = la partie du corps gouvernee par la mansion. En astrologie medicale,
chaque signe du zodiaque (et par extension chaque mansion) gouverne une partie du
corps. C'est la MELOTHESIE ("homme zodiacal").

**Pour :** Tres pratique pour un medecin : "aujourd'hui, on ne saigne PAS la tete."
Le Fasciculus Medicinae (que tu as deja etudie) contient exactement ce systeme.
Les noms de parties du corps en latin sont courts (caput, cor, pes, manus, venter...)
et pourraient correspondre aux mots courts de L04.

**Contre :** La melothesie suit les 12 signes, pas les 28 mansions.
Il faudrait ~2-3 labels par signe, ce qui donne bien ~28-36 positions.
Mais les noms de parties du corps se repeteraient (chaque signe a la meme partie),
or L04 a 27 mots uniques sur 28.

**Testabilite :** 8/10. Les noms sont courts, latins, et previsibles.

**TEST PROPOSE :** Liste des ~15-20 parties du corps de la melothesie et test
phonetique contre L04.

---

### H4. INSTRUCTIONS MEDICALES (verbes/actions)

Chaque label = une ACTION medicale : saigner, purger, baigner, couper les cheveux,
voyager, semer, eviter...

Les lunaires medievaux donnent des instructions du type :
- "bon pour saigner" (bonum ad phlebotomiam)
- "ne rien couper" (nihil incidas)
- "bon pour les bains" (bonum ad balnea)

**Pour :** Usage TRES pratique. Un verbe par jour. On a deja vu que les lunaires
utilisent un vocabulaire restreint (7-10 actions types), mais si c'est des actions
SPECIFIQUES (pas juste "bon/mauvais"), le vocabulaire pourrait atteindre 20-28 termes.

**Contre :** Les tests precedents ont montre 27 mots uniques, ce qui est TROP pour
un jeu d'actions medicales standard (rarement plus de 15). Et l'entropie 3.74 est
trop haute pour un vocabulaire aussi contraint.

**Testabilite :** 7/10. Le vocabulaire medical medieval est bien documente.

**TEST PROPOSE :** Liste des verbes/actions des lunaires latins (sanguinare,
purgare, balneari, incidere, arare, navigare, nubere...) et test phonetique.

---

### H5. REFERENCES CROISEES (numeros de recettes)

Chaque label = un RENVOI a une autre page du VMS. Le label ne dit pas quoi faire,
il dit OU CHERCHER la recette complete.

Les glyphes isoles (o, d, l, s, y, k, x, v) seraient des NUMEROS ou des INDEX.
Les mots-contenu seraient des NOMS de sections.

**Pour :** Tres fonctionnel. Un index rotatif. Le VMS a ~240 folios ; 28 sections
pharmaceutiques pourraient correspondre a 28 positions de L04. Les pages recettes
du VMS (f99-f116) ont des "titres" ou labels en haut.

**Contre :** On n'a pas d'evidence que les glyphes VMS encodent des nombres.
Et les "titres" des pages recettes ne matchent pas L04.

**Testabilite :** 9/10. On peut directement comparer les labels de L04 avec les
labels/titres en haut des pages recettes du VMS.

**TEST PROPOSE :** Extraire les premiers mots de chaque "recette" des folios
f99-f116 et les comparer aux mots de L04.

---

### H6. QUALITES/ELECTIONS ASTROLOGIQUES

Chaque label = la QUALITE de ce jour/mansion pour une activite donnee.
Pas un simple "bon/mauvais" mais un descripteur precis.

En astrologie electionnelle, chaque mansion a des elections specifiques :
M1 = voyages, M2 = tresors, M3 = navigation, M4 = destruction, M5 = enseignement...

**Pour :** Le Picatrix donne une ELECTION specifique pour chaque mansion (28 elections
uniques). Cela expliquerait 28 mots uniques. L'information est immediatement pratique.

**Contre :** Les elections du Picatrix sont des PHRASES, pas des mots isoles
("pour detruire les batiments", "pour gagner l'amour"). Difficile de comprimer en
un mot.

**Testabilite :** 5/10. Les elections sont des concepts, pas des mots simples.

---

### H7. ESPRITS/ANGES DES MANSIONS (invocations)

Chaque label = le nom de l'ESPRIT ou ANGE qui gouverne cette mansion.
Le Picatrix donne un seigneur (dominus) pour chaque mansion :
M1=Geriz, M2=Enedil, M3=Annuncia, M4=Assarez...

**Pour :** 28 noms uniques. L'utilisateur prononce le nom de l'esprit dans sa
pratique quotidienne (invocation, priere, talisman). Peter d'Abano a ecrit un
"Liber experimentorum de Annulis secundum Mansiones Lunae" - des experiences
avec des ANNEAUX selon les mansions. Un anneau sur une volvelle = un anneau
talismanique ?

**Contre :** Deja teste dans l'attaque v2 (categorie "spirits"). Resultats faibles
(meilleur offset 5, score 0.247). Mais le mapping phonetique etait peut-etre
trop bruite.

**Testabilite :** 8/10. Les 28 noms sont connus. A retester avec le mapping simple.

---

### H8. NOMS D'ETOILES (catalogue stellaire)

Chaque label = le nom de l'etoile VISIBLE ce jour-la, pas necessairement liee
aux mansions. Un guide observationnel : "ce soir, cherchez cette etoile."

**Pour :** Le match otal/altair (0.833) reste le plus fort de toute l'analyse.
Altair est une des etoiles les plus brillantes. f68r1 est un folio d'etoiles
avec 50% de vocabulaire partage avec L04.

**Contre :** 28 etoiles specifiques ne correspondent pas a un catalogue connu.
Les catalogues stellaires medievaux (Ptolemee, Al-Sufi) listent 48 ou 1022 etoiles,
pas 28. SAUF si ce sont les 28 etoiles de REFERENCE des mansions.

**Testabilite :** 8/10. Les 28 etoiles de reference sont connues.

---

### H9. MOTS VERNACULAIRES (pas latin, pas arabe)

ET SI L04 N'EST NI LATIN NI ARABE ?

Si l'utilisateur etait un locuteur d'une langue vernaculaire (italien, occitan,
ancien francais, judeo-espagnol, hebreu...), les labels pourraient etre dans SA
langue, pas en latin savant.

**Pour :** Expliquerait pourquoi aucune correspondance latine/arabe ne domine.
Le VMS pourrait etre en langue vernaculaire (hypothese Romane de Cheshire, bien
que tres contestee). Les noms de plantes en langue vulgaire sont souvent tres
differents des noms latins.

**Contre :** Enorme espace de recherche. Quelle langue tester ? Sans savoir la
langue, on ne peut pas calibrer le mapping phonetique.

**Testabilite :** 3/10 (sans contrainte sur la langue) a 7/10 (si on teste
specifiquement l'italien du Nord, le plus probable geographiquement).

---

### H10. SYSTEME HYBRIDE (mix de categories)

Les 20 mots-contenu ne sont PAS tous de la meme categorie.
Certains sont des noms, d'autres des instructions, d'autres des renvois.

Structure possible :
- Mots LONGS (6-8 glyphes : chedaiin, deeodal, okeeod, lkeeol, dkedar, ofeeey)
  = noms complets (mansions? plantes? etoiles?)
- Mots COURTS (2-4 glyphes : otey, shes, vo, dal, aros, daro)
  = abreviations ou instructions
- Glyphes ISOLES (o, d, l, s, y, k, x, v)
  = marqueurs de categorie ou separateurs

**Pour :** Expliquerait pourquoi aucune hypothese unique ne matche tout.
Les familles morphologiques (aiin, eeo, kedar) seraient des mots de la meme
categorie.

**Contre :** Plus complexe = plus difficile a tester. Risque de sur-interpreter.

**Testabilite :** 4/10 (trop de degres de liberte).

---

### H11. TABLE DE CORRESPONDANCES (matrice rotation)

L04 ne se lit PAS seul. Il se lit EN COMBINAISON avec un autre anneau.
La lecture = l04[position] x L03[position alignee] = information complete.

Sur une volvelle, la ROTATION d'un anneau par rapport a l'autre produit
des combinaisons differentes. Chaque label sur L04 est une COORDONNEE
dans une matrice a double entree.

**Pour :** C'est le fonctionnement standard d'une volvelle. Ca expliquerait pourquoi
les labels seuls ne forment pas un sens complet. Peter d'Abano : annulis SECUNDUM
mansiones - "anneaux SELON les mansions" = l'anneau sert de selecteur.

**Contre :** On ne peut pas tester ca sans connaitre le contenu des autres anneaux.
Et les labels sont QUAND MEME des mots, pas des lettres arbitraires.

**Testabilite :** 2/10 (necessite de decoder les autres anneaux d'abord).

---

### H12. MOTS-CLES MNEMONIQUES

Chaque label est un MOT-CLE qui rappelle un ensemble de connaissances.
Comme un aide-memoire. "dainn" rappelle a l'utilisateur TOUT ce qu'il sait
sur cette mansion/jour/position.

L'utilisateur ne DECODE pas le mot. Il le RECONNAIT. Comme un nom propre.
C'est un label, pas un message.

**Pour :** Le plus simple. Pas besoin de correspondance phonetique avec des noms
connus. Le label est ARBITRAIRE pour nous mais SIGNIFICATIF pour l'utilisateur.
Ca colle avec l'usage quotidien.

**Contre :** Si les labels sont arbitraires, on ne peut pas les decoder par analyse
linguistique. C'est un cul-de-sac cryptanalytique.

**Testabilite :** 1/10 (irrefutable donc non testable).

---

## CLASSEMENT PAR TESTABILITE

| # | Hypothese | Testabilite | Signal actuel | Priorite |
|---|-----------|-------------|---------------|----------|
| H5 | References croisees VMS | 9/10 | non teste | **URGENT** |
| H3 | Melothesie (parties du corps) | 8/10 | non teste | **HAUTE** |
| H7 | Esprits/anges (Picatrix) | 8/10 | faible | MOYENNE |
| H8 | Catalogue stellaire | 8/10 | otal=altair | HAUTE |
| H2 | Herbes/plantes | 6/10 | non teste (VMS interne) | **HAUTE** |
| H4 | Instructions medicales | 7/10 | non teste | HAUTE |
| H1 | Noms de mansions | 7/10 | faible | BASSE (deja teste) |
| H6 | Elections astrologiques | 5/10 | non teste | BASSE |
| H10 | Systeme hybride | 4/10 | plausible | BASSE |
| H9 | Langue vernaculaire | 3/10 | non teste | BASSE |
| H11 | Matrice double anneau | 2/10 | non teste | BASSE |
| H12 | Mnemoniques arbitraires | 1/10 | irrefutable | -- |

---

## TESTS PRIORITAIRES (ce qu'on peut faire MAINTENANT)

### TEST A : References croisees internes VMS (H5)
Comparer les mots de L04 avec les labels/premiers mots des sections
recettes (f99-f116) et herbier (f1-f66) du VMS.
Si les mots de L04 apparaissent comme "titres" de recettes elsewhere,
c'est un index rotatif.

### TEST B : Melothesie - parties du corps (H3)
Generer la liste latine : caput, collum, pectus, cor, venter, ren, crus,
pes, manus, dorsum, lumbus, vesica, hepar, lien, etc.
Tester phonetiquement avec mapping simple.

### TEST C : Herbes du VMS interne (H2)
Extraire les labels identifies des plantes du VMS (section herbier).
Checker les recoupements avec L04.
Si `daiin` apparait aussi sur un dessin de plante, on tient quelque chose.

### TEST D : Verbes medicaux latins (H4)
Vocabulaire des lunaires : sanguinare/flebotomare, purgare, balneari,
incidere, arare, seminare, navigare, nubere, emere, vendere, aedificare...
Test phonetique.

### TEST E : Retester esprits Picatrix avec mapping simple (H7)
Les 28 noms d'esprits du Picatrix avec 1 seule valeur par glyph.
Plus propre que l'attaque v2.

---

## LE FIL ROUGE : QU'EST-CE QUI EST VRAIMENT SOLIDE ?

Ce qui survit a TOUS les doutes :

1. **La racine `aiin`** = morpheme reel, 4 occurrences certaines
2. **Le prefixe `o-` = /al-/** = article defini arabe (coherent avec f68r1)
3. **Le pont L04 <-> f68r1** = vocabulaire partage (50%), c'est un FAIT
4. **28 positions uniques** = parfait pour les 28 mansions
5. **L04 est en labelese** (pas en VMS standard) = systeme d'encodage different
6. **L'utilisateur lisait ca VITE** = systeme direct, pas chiffre

Ce qui est INCERTAIN :
- Les transcriptions de 7/29 mots
- La nature exacte du contenu (noms? herbes? instructions? mix?)
- L'offset de rotation (s'il y en a un)
- La valeur phonetique exacte de chaque glyph
