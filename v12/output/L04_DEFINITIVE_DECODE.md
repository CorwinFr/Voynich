# L04 DEFINITIVE DECODE — Pipeline v12

## Methode : meme pipeline que le reste du VMS. PAS de systeme special.
## 10/19 mots-contenu sont des mots VMS standard (confirme par le corpus).
## K&A s'applique. Le decode ci-dessous est le meme que pour f103r, etc.

| Pos | EVA | Latin (pipeline) | Conf | Freq | Alternatives HMM | Note |
|-----|-----|-----------------|------|------|-----------------|------|
| 1 | daiin | **in aquam** | HIGH | 0 | dura(200), dare(141) | Deagg: d=in + aiin=aquam. 622x dans VMS |
| 2 | otey | **aloe** | HIGH | 197 | le(742), te(978) | INGREDIENT_ANAGRAM. aloe=herbe M10 |
| 3 | ofeeey | **epare** | HIGH | 9 | apo(74), epe(21) | "preparer" ? Ou deagg: o=a + feeey |
| 4 | shes | **cies** | HIGH | 20 | - | cieo = "stimuler/mouvoir". 14x VMS |
| 5 | **o** | **ac** | CONF | 743 | - | Logogramme standard VMS |
| 6 | **d** | **de** | CONF | 14482 | - | Logogramme standard VMS |
| 7 | okeeod | **quoede** | LOW | 0 | quoad(13) | Deagg: ok=qu + oede. Opaque |
| 8 | **l** | **[l]** | OPAQUE | 0 | - | UNKNOWN. Logogramme sans decode |
| 9 | **o** | **ac** | CONF | 743 | - | = position 5 |
| 10 | lkeeol | **ex cons** | HIGH | 0 | sces(3) | Deagg: l=ex + keeol=cons |
| 11 | dkedar | **in codura** | HIGH | 0 | - | Deagg: d=in + kedar=codura |
| 12 | yf | **inpar** | HIGH | 2 | inf(21), inp(4) | "impar" = impair/inegal |
| 13 | aros | **ares** | HIGH | 3 | uras(3) | K&A standard. NB: anagramme de rosa |
| 14 | **s** | **est** | HIGH | 10345 | recipe (si V lit `r`) | Logogramme. 2e mot le + frequent |
| 15 | **y** | **in** | CONF | 32102 | - | Logogramme. LE mot le + frequent |
| 16 | chedaiin | **eius odeura** | HIGH | 0 | iodeura | Deagg: ch=eius + e + daiin |
| 17 | **k** | **[k]** | OPAQUE | 0 | - | UNKNOWN. Logogramme sans decode |
| 18 | eeety | **el** | HIGH | 542 | et(45204), ed(585) | "et" ou "el" — conjonction |
| 19 | **x** | **crux** | HIGH | 7 | - | Logogramme. Croix/marqueur |
| 20 | deeodal | **in oeduce** | HIGH | 0 | deduce | Deagg: d=in + eeodal=oeduce |
| 21 | vo | **ve** | HIGH | 424 | va(158) | Exclamation/abreviation |
| 22 | tchor | **eliara** | HIGH | 3 | lier(8) | "lier" (action pharma). 21x VMS |
| 23 | kedar | **codura** | HIGH | 1 | - | Mot rare. Meme racine que j11 |
| 24 | dal | **in alo** | HIGH | 0 | dus(61), duce(10) | Deagg: d=in + al=alo. 207x VMS |
| @172 | *(lambda)* | *separateur* | - | - | - | Symbole special f57v uniquement |
| 25 | daiin | **in aquam** | HIGH | 0 | dura(200) | = position 1 (repetition) |
| 26 | aiin | **aquam** | CONF | 438 | are(69) | Racine confirmee. 428x VMS |
| 27 | otal | **sal** | HIGH | 164 | tus(131), luce(20) | INGREDIENT (sel). Ou tus (encens) |
| 28 | daro | **dura** | HIGH | 200 | dare(141) | "dur" / "durable" |
| 29 | **v** | **vel** | HIGH | 9241 | - | Logogramme. "ou" (conjonction) |

---

## LECTURE INTERPRETATIVE (tentative)

En lisant L04 comme 29 labels de volvelle, position par position :

| Pos | Latin | Interpretation | Type |
|-----|-------|---------------|------|
| 1 | in aquam | "dans l'eau" | METHODE de preparation |
| 2 | aloe | "aloes" | INGREDIENT |
| 3 | epare | "preparer" | ACTION |
| 4 | cies | "stimuler/mouvoir" | ACTION |
| 5 | ac | "et" | CONJONCTION (separateur) |
| 6 | de | "de/depuis" | PREPOSITION |
| 7 | quoede | ??? (opaque) | UNKNOWN |
| 8 | [l] | ??? | UNKNOWN |
| 9 | ac | "et" | CONJONCTION |
| 10 | ex cons | "de la consistance" | QUALITE |
| 11 | in codura | "dans la coction dure" | METHODE |
| 12 | inpar | "impar/inegal" | QUALITE |
| 13 | ares | "belier/sables" | UNKNOWN — ou rosa ? |
| 14 | est | "est" | COPULE |
| 15 | in | "dans" | PREPOSITION |
| 16 | eius odeura | "de cela l'odeur" | QUALITE (olfactive) |
| 17 | [k] | ??? | UNKNOWN |
| 18 | el/et | "et/ou" | CONJONCTION |
| 19 | crux | "croix" (marqueur) | MARQUEUR (jour critique) |
| 20 | in oeduce | "en decoction" | METHODE |
| 21 | ve | "va!/helas" | EXCLAMATION ? |
| 22 | eliara | "lier" | ACTION (pharma) |
| 23 | codura | "coction dure" | METHODE |
| 24 | in alo | "dans l'aile/cote" | LOCALISATION ? |
| @172 | — | SEPARATEUR | STRUCTURE |
| 25 | in aquam | "dans l'eau" | = pos 1 (REPETITION) |
| 26 | aquam | "eau" | INGREDIENT/METHODE |
| 27 | sal | "sel" | INGREDIENT |
| 28 | dura | "dur/durable" | QUALITE |
| 29 | vel | "ou" (alternative) | CONJONCTION |

---

## PATTERNS EMERGENTS

### Vocabulaire par categorie :
- **METHODES** : in aquam (x2), in codura, in oeduce, codura = preparations dans l'eau/coction
- **INGREDIENTS** : aloe, aquam, sal = ingredients de base (aloes, eau, sel)
- **ACTIONS** : epare (preparer), cies (mouvoir), eliara (lier)
- **QUALITES** : inpar (inegal), ex cons (consistance), odeura (odeur), dura (dur)
- **STRUCTURE** : ac, de, in, est, et/el, vel, crux = prepositions, conjonctions, marqueurs

### Observations cruciales :
1. **"in aquam"** apparait aux positions 1 ET 25 — SEULE repetition de mot
   → Ca pourrait marquer le DEBUT et la FIN du cycle (retour au depart)
2. **Le @172** (lambda inverse) est entre j24 et j25 — il separe peut-etre
   le cycle principal (1-24) du retour/coda (25-29)
3. **Positions 25-29** = in aquam, aquam, sal, dura, vel
   → "dans l'eau, eau, sel, dur, ou" — une FORMULE de clotureou une instruction finale
4. **crux** (j19) = le seul marqueur isole non-prepositionnel
   → "jour critique" sur la volvelle (position a eviter)
5. **Les mots de methode** (in aquam, in codura, in oeduce, codura)
   sont TOUS des instructions de CUISSON/PREPARATION pharmaceutique

### Ce que c'est probablement :
L04 est un anneau d'instructions pharmaceutiques de PREPARATION.
Chaque position indique COMMENT preparer le remede selon la position
de la volvelle (jour, signe, mansion, ou toute autre variable
determinee par les autres anneaux).

L'utilisateur :
1. Determine la date/position (anneaux L02, L03, L05)
2. Lit le label L04 aligne
3. Prepare le remede selon l'instruction (in aquam, aloe, codura, etc.)
