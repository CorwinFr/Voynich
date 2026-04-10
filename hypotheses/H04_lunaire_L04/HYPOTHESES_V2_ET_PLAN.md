# L04 — NOUVELLES HYPOTHESES ET PLAN DE TESTS (v2)

## LE RETOURNEMENT

Le test "mots L04 dans le VMS global" montre que **10/19 mots-contenu
sont des mots VMS parfaitement standards** :
- daiin (622x), aiin (428x), dal (207x), otal (115x), otey (51x)
- chedaiin (30x), tchor (21x), shes (14x), kedar (4x), lkeeol (3x)

Les 9 glyphes isoles sont aussi standard (o=161x, y=257x, s=249x, etc.)

**CONCLUSION : L04 est en systeme VMS standard. K&A s'applique.**

La "divergence de frequence" etait un artefact d'echantillon trop petit
(29 mots vs 30000 dans le VMS global). Pas un systeme different.

## L'UTILISATEUR LISAIT CA TOUS LES JOURS

Implications cruciales :
1. Pas de chiffre complexe — le texte est DIRECT
2. K&A donne le texte latin (ou les abreviations latines)
3. Les mots rares (9 hapax) sont probablement des formes agglutinees
   que le pipeline n'a pas vues ailleurs par hasard
4. Le sens emerge du CONTEXTE (volvelle) pas du dechiffrement

## NOUVELLES HYPOTHESES

### H4a : L04 = INSTRUCTIONS PHARMACEUTIQUES ABREGEES

K&A decode les 10 mots communs correctement. Voici ce qu'on obtient :

| Pos | EVA | K&A | Freq VMS | Sens probable |
|-----|-----|-----|----------|---------------|
| 1 | daiin | dura / in aquam | 622 | "dans l'eau" ou "durablement" |
| 2 | otey | de / te / oleo | 51 | preposition ou ingredient |
| 4 | shes | cies | 14 | forme verbale |
| 13 | aros | ares (?) | 1 | HAPAX — mot unique |
| 16 | chedaiin | eius + dura | 30 | "de cela" + "dans l'eau" |
| 22 | tchor | lier / eliara | 21 | "lier" (action pharma) |
| 23 | kedar | codura | 4 | mot rare |
| 24 | dal | dus / duce | 207 | suffixe ou prep |
| 25 | daiin | dura / in aquam | 622 | = jour 1 |
| 26 | aiin | are / ura | 428 | suffixe nominal |
| 27 | otal | tus / luce | 115 | "encens" ou "lumiere" |
| 28 | daro | dura / dare | 1 | "dur" ou "donner" |

**Le probleme** : K&A produit des prepositions et des suffixes,
pas des phrases completes. Mais c'est NORMAL pour une volvelle :
chaque mot est un FRAGMENT d'instruction qui se combine avec les
autres anneaux pour former un sens complet.

### H4b : L04 = ETIQUETTES DE VOLVELLE (mots-cles fonctionnels)

L04 n'est PAS du texte continu. Ce sont des LABELS :
- "in aquam" (j1,25) = methode de preparation (dans l'eau)
- "oleo" (j2) = methode (dans l'huile)
- "luce" (j27) = moment (a la lumiere / de jour)
- "crux" (j19) = marqueur (jour critique)
- Les glyphes isoles = ABREVIATIONS courantes

Chaque label se lit en combinaison avec la position de la volvelle.
L'utilisateur tourne le disque, aligne une date avec un label,
et lit l'instruction.

### H4c : L04 = TEXTE CONTINU MAL SEGMENTE

Et si les separations de mots sont FAUSSES ? Le scribe n'utilisait
peut-etre pas d'espaces reguliers. Les transcripteurs modernes ont
segment le texte de L04 en 29 "mots" la ou il pourrait y avoir
15-20 mots reels (en regroupant certains glyphes isoles avec les
mots adjacents).

Par exemple : `aros.s.y.chedaiin` pourrait etre lu comme
`aros.sy.chedaiin` ou `arossychedaiin` (un seul long mot).

### H4d : L04 = MEME TEXTE QUE LE CORPS DU MANUSCRIT

Si `daiin` apparait 622 fois, `aiin` 428 fois, etc., alors L04
n'est PAS un systeme special. C'est du texte Voynich NORMAL,
comme n'importe quelle autre page. Le fait qu'il soit sur une
volvelle ne change pas l'encodage — ca change le CONTENU
(instructions de volvelle au lieu de recettes de plantes).

## PLAN DE TESTS

### TEST 1 : Contexte des mots partages (PRIORITAIRE)
Pour chaque mot L04 qui apparait ailleurs :
- Ou apparait-il ? (section herbal, pharma, zodiac ?)
- Quels mots le precedent/suivent habituellement ?
- Le K&A decode est-il coherent dans ces contextes ?
→ Si `daiin` est toujours "in aquam" dans le reste du VMS,
  alors c'est aussi "in aquam" dans L04.

### TEST 2 : Resegmentation
Tester des segmentations alternatives de L04 :
- Regrouper glyphes isoles avec mots adjacents
- Tester si les nouvelles unites sont des mots VMS plus courants

### TEST 3 : K&A decode des 9 hapax avec contexte
Pour les 9 mots uniques a L04, utiliser le CONTEXTE (mots voisins)
pour discriminer entre les alternatives K&A.
Ex : si le mot avant est "in aquam", le mot apres devrait etre
un ingredient ou une action.

### TEST 4 : Bigrams L04 vs bigrams VMS
Verifier si les paires de mots consecutifs de L04 (daiin+otey,
otey+ofeeey, etc.) apparaissent comme bigrams dans le VMS global.
Si oui → texte normal. Si non → labels independants.

### TEST 5 : EVA glyph verification
Reexaminer les 6 positions avec variantes de transcription
en privilegiant la lecture la plus SIMPLE (Occam) :
- j14 : s ou r ? → si r, decode = "recipe" (instruction pharma !)
- j18 : eeety ou chety ou echty ? → quel decode est le plus courant ?
- j22-23 : tchor.kedar ou sh.tedar ? → quel est le plus coherent ?

### TEST 6 : Structure de phrase
Lire L04 comme une PHRASE continue (pas 29 mots isoles) :
"daiin otey ofeeey shes o d okeeod l o lkeeol dkedar yf..."
Decoder par K&A et voir si ca forme du latin lisible.

### PRIORITE D'EXECUTION
1. TEST 4 (bigrams) — 10 min — determine si c'est du texte continu ou des labels
2. TEST 1 (contexte) — 15 min — confirme les decodages K&A
3. TEST 5 (glyphes douteux) — 5 min — resout les ambiguites
4. TEST 6 (phrase continue) — 10 min — test de lecture directe
5. TEST 2 (resegmentation) — 20 min — si les autres echouent
