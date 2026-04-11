# Expertise de validation : lignes decodees du Voynich MS 408
## Analyse pharmaceutique medievale des 20 lignes proposees

**Date** : 9 avril 2026
**Methode** : Comparaison systematique avec l'Antidotarium Nicolai (ed. DBNL van den Berg 1917), les transcriptions de BNF Latin 6823 (Ponzi/ViridisGreen), le Circa Instans (Platearius) et la tradition salernitaine.

---

## PARTIE I : VERDICT SYNTHETIQUE

### Question 1 : Ces lignes se lisent-elles comme des instructions pharmaceutiques plausibles ?

**Reponse : PARTIELLEMENT OUI, avec des reserves majeures.**

Le vocabulaire de base (oleum, cera, sal, aqua, acetum, succus, ana, misce, cola, Rx) est parfaitement authentique et place bien le texte dans le registre pharmaceutique salernitain du XIIe-XVe siecle. Les combinaisons oleum+cera (base d'onguent), acetum+cola (preparation acetique), et la cloture par ana (parties egales) sont des motifs reels, attestes dans l'Antidotarium.

Cependant, la STRUCTURE des lignes decodees devie significativement de la norme receptaire medievale sur cinq points critiques que je detaille ci-dessous.

### Question 2 : Reconnaissez-vous des types de recettes specifiques ?

**Oui, trois types emergent :**
- Les lignes avec oleum + cera + misce (F108V, F84R) evoquent un **ceratum/unguentum** (onguent/cerat)
- Les lignes avec acetum + cola (F107V, F113R) evoquent un **oxymel** ou une preparation acetique filtrante
- Les lignes avec ana en cloture (F55V, F80V) evoquent une **formulation composee** a doses egales

### Question 3 : Qu'est-ce qui est manifestement FAUX ?

**Cinq anomalies structurelles majeures** (detaillees en Partie II).

---

## PARTIE II : LES CINQ ANOMALIES STRUCTURELLES

### Anomalie 1 : Densite de verbes proceduraux TROP ELEVEE

C'est le probleme le plus grave. Dans l'Antidotarium Nicolai, le ratio verbes/ingredients est d'environ **1 verbe pour 3 a 8 ingredients nommees**. L'Athanasia (30+ ingredients) n'utilise que 4 verbes proceduraux. L'Esdra (40 ingredients) en utilise environ 17 sur plus de 2000 mots.

Dans vos lignes decodees, le ratio est inverse : **1 verbe pour 1,5 a 2 tokens**. La ligne F108V est l'exemple extreme : "Raw oil, mix and, mix and, product, mix and, mix and, raw wax, strain and, mix and, equal parts" - 5 occurrences de "misce" et 1 "cola" pour seulement 3 elements identifies (oleum, cera, ana). C'est comme si quelqu'un disait "prends, melange, melange, melange, filtre, melange" sans jamais nommer ce qu'il melange.

**Dans une vraie recette**, on lit : "Recipe cinamomi, cassie fistule, croci, iusqami, squinanti, storaci calidi an drachme iii et grana vi. Mel quod sufficit. Fiat confectio." (Athanasia, Ponzi/BNF Lat. 6823) - une LONGUE liste d'ingredients, puis 1-2 verbes de cloture.

**Diagnostic** : soit le modele de decodage attribue trop de tokens au role "verbe", soit le VMS ne contient pas des recettes au format Antidotarium mais un autre genre de texte pharmaceutique (instructions de preparation etape par etape, par exemple, plutot qu'une formule).

### Anomalie 2 : Absence quasi totale d'ingredients NOMMES

C'est la deuxieme anomalie la plus grave. Les lignes decodees ne contiennent que ~6 substances identifiees : oleum (huile), cera (cire), sal (sel), aqua (eau), acetum (vinaigre), succus (jus). Ce sont tous des **excipients/vehicules** - les substances de base qui PORTENT les ingredients actifs.

Dans l'Antidotarium, chaque recette nomme entre 4 et 60+ **ingredients specifiques** : cinamomum, crocus, aloe, mastix, xilobalsami, opobalsami, agarici, turbit, scammonie, etc. Les ingredients generiques ("materia", "herba") sont rares (<23% des mentions).

Or, dans les 10 lignes presentees, 20,1% du texte est marque "UNK" et une part encore plus grande est marquee "[M]MATERIA" ou "[P]MATERIA" - ce qui signifie que le modele a identifie un etat (brut/prepare) mais PAS la substance elle-meme.

**Diagnostic** : le modele a correctement identifie la couche des excipients (les tokens les plus frequents dans tout texte pharmaceutique) mais n'a pas encore dechiffre les tokens qui encodent la matiere medicale specifique. C'est comme si on lisait une recette de cuisine ou on ne comprenait que "huile, eau, sel, melanger, filtrer" sans jamais savoir quels legumes, epices ou viandes sont utilises.

**C'est en fait un resultat prometteur** : le modele a capture la "grammaire" receptaire sans avoir encore la "semantique" complete. La prochaine etape serait d'identifier ce que les tokens "[M]MATERIA" et "[P]MATERIA" encodent specifiquement.

### Anomalie 3 : Le prefixe "per" est anachronique ou surdetermine

Dans la recette de l'Esdra (2000+ mots, la plus longue recette documentee de l'Antidotarium), le mot "per" n'apparait **PAS UNE SEULE FOIS**. Le decompte des prepositions dans l'Esdra donne : cum (6), ad (5), in (3), ab (1), super (1), ex (1), per (0).

Dans le latin pharmaceutique medieval, "cum" domine massivement pour introduire le vehicule (cum aqua, cum vino, cum melle), le co-ingredient (cum cera), ou le moyen (cum aceto). "In" introduit le recipient (in olla, in caldario), le temps (in mane, in sero), ou l'etat (in pulvere). "Ex" introduit l'origine (ex succo). "Per" n'est presque jamais utilise en contexte receptaire - il appartient plutot au registre medical general ("per os" = par voie orale, "per nares" = par les narines), pas au registre des formulations.

Pourtant, dans vos lignes decodees, "per" (mappe sur le prefixe "l") apparait frequemment : "per 1x acetum" (F107V), "per 2ʒ" (F107V), "per [M]UNK_or" (F103V), "per aqua" (F103V). Chaque occurrence est suspecte.

**Diagnostic** : soit la correspondance l = per est incorrecte (peut-etre l = cum ou l = ad ?), soit les sections pharmaceutiques du VMS n'utilisent pas la syntaxe de l'Antidotarium.

### Anomalie 4 : "signa" ne correspond pas au registre de l'Antidotarium

Le decodage de "t" comme "signa" (etiqueter/marquer) place le texte dans le registre de la **prescription** (un medecin ordonne a l'apothicaire), pas dans celui du **receptaire** (une collection de formules).

Dans l'Antidotarium Nicolai, "signa" n'apparait JAMAIS. Les recettes sont des formules autonomes qui commencent par le nom du composita ("Yerapigra Galieni", "Metridatum", "Unguentum fuscum") puis "Recipe [ingredients]... Fiat [forme]... Datur [posologie]". Le verbe "signa" appartient au format d'ordonnance (Rx ... Misce ... Signa), qui est une structure plus tardive (post-XIIIe s. au plus tot, generalise au XVIe s.).

La ligne F113R decode "signa [P]materia et, adde.2, [P]2x succus..." - c'est grammaticalement bizarre. "Signa" n'est jamais suivi d'une liste d'ingredients. Si c'est une inscription/etiquette, on attendrait "signa [mode d'administration]" (ex. : "signa: bibatur in mane cum aqua calida").

**Diagnostic** : soit "t" n'encode pas "signa", soit il introduit un element different (une rubrique, un titre de section, un marqueur de paragraphe). La lecture "signa" comme etiquette d'incipit est la plus fragile de vos hypotheses de decodage.

### Anomalie 5 : Les quantites isolees sont pharmaceutiquement impossibles

Plusieurs tokens decodent comme des quantites pures sans ingredient associe : "1ʒ", "2ʒ" apparaissant seuls. La ligne F107V commence par "1ʒ oleum 2ʒ" - ou 1ʒ est un token SEPARE d'oleum.

Dans le latin pharmaceutique medieval, une quantite est TOUJOURS greffee sur un ingredient. On ecrit "olei ʒ ii" (huile, 2 drachmes) ou "ana ʒ i" (chacun 1 drachme), jamais "ʒ i" puis un blanc puis "oleum" puis "ʒ ii" comme trois mots distincts.

**Diagnostic** : les tokens de quantite ne sont probablement pas des "mots" separes mais des composantes du meme token que l'ingredient qui les accompagne. Cela conforte en fait votre propre modele (le e-count est une COMPOSANTE du token, pas un mot autonome). Mais le rendu lineaire separe ce qui devrait etre lu comme une unite : [olei ʒ ii] = un seul concept "huile, 2 drachmes".

---

## PARTIE III : CE QUI EST CORRECT ET PROMETTEUR

### 3.1 Le vocabulaire excipientaire est parfait

Les 6 substances identifiees (oleum, cera, sal, aqua, acetum, succus) + ana forment precisement la base excipientaire de la pharmacie salernitaine :
- **Oleum + cera** = base d'onguent/cerat. Le Cerotum sandelatum dans l'Antidotarium : "Rosarum ʒ xii; Sandelorum rubeorum ʒ x; ... Cere albe ʒ xxx; Oley rosati lib. i." EXACTEMENT huile + cire
- **Aqua** = vehicule universel (cum aqua calida dans l'Electuarium de succo rosarum)
- **Sal** = ingredient actif dans de nombreuses preparations (compressions, cataplasmes, lavages chirurgicaux)
- **Acetum** = base d'oxymel (aceti fortissimi lb.i et ½ dans l'Oximel), agent topique
- **Succus** = jus vegetal frais (succi rosarum dans l'Electuarium de succo rosarum, succi apii dans l'Oximel)
- **Ana** = marqueur de dose egale (universellement atteste dans l'Antidotarium)

### 3.2 La distinction [M]/[P] (brut/prepare) est conceptuellement exacte

La distinction brut/prepare est FONDAMENTALE dans la pharmacie medievale. Le Circa Instans enseigne explicitement comment transformer une substance "brute" en "produit" : exprime succum (extraire le jus), radix siccata (racine sechee), mel despumatum (miel ecume), cera lota/preparata (cire lavee/preparee).

L'Antidotarium distingue systematiquement : rosarum viridium (roses fraiches = brut) vs rosarum [siccatarum] (roses sechees = prepare) ; mellis despumati (miel ecume = prepare) vs mellis [crudi] (miel cru = brut). Le concept est identique a votre [M]/[P].

Cependant, le CODAGE medieval est fait par des adjectifs en toutes lettres, pas par un prefixe binaire. Votre systeme est plus compact mais fonctionnellement equivalent.

### 3.3 La sequence Rx -> ingredients -> verbes proceduraux -> fiat/datur est correcte

L'architecture globale Recipe [ingredients] -> Misce/Cola/Coque -> Fiat [forme] -> Datur [posologie] est parfaitement salernitaine. Si on abstrait les details, plusieurs de vos lignes suivent ce patron :
- F84R : Rx -> ingredients -> misce -> cum aqua -> [P]cera = un onguent en preparation
- F107V : oleum -> acetum -> cola -> misce = une preparation acetique filtree

### 3.4 Les quantites en drachmes sont dans la bonne fourchette pour des INGREDIENTS ACTIFS

1-3 drachmes par ingredient est la fourchette standard dans l'Antidotarium pour les ingredients actifs : l'Athanasia donne "drachme iii et grana vi" pour le cinnamome, "drachme i et ℥ i" pour le castoreum. L'Esdra donne "drachma i et scrupulum i et granum i" pour de nombreux ingredients.

**ATTENTION** : cette fourchette est correcte pour les ingredients ACTIFS (herbes, epices, mineraux) mais INCORRECTE pour les excipients/bases. Les bases (mel, oleum, cera, aqua) sont mesurees en LIVRES et ONCES, pas en drachmes. "Olei lb. i et ½" (1,5 livres d'huile) dans l'Unguentum fuscum, "mellis despumati lb. x" (10 livres de miel) dans le Mel rosaceum. Si toutes les quantites decodees sont en drachmes, y compris pour oleum et cera, c'est suspect pour des formules entieres mais correct pour des sous-doses d'un ingredient parmi beaucoup d'autres.

---

## PARTIE IV : ANALYSE LIGNE PAR LIGNE

### Ligne 1 - F107V : oleum + acetum + cola
```
1ʒ oleum 2ʒ per 1×acetum 2ʒ [P]oleum per 2ʒ cola.3 cum 2ʒ [P]materia misce
```
**Plausibilite** : MODEREE. La sequence oleum -> acetum -> cola (filtrer) evoque une preparation oleo-acetique. Le filtrage triple (cola.3) est documente (le Mel rosaceum specifies de filtrer l'ecume 7 fois). Probleme : "per 1x acetum" est syntactiquement bizarre - attendu "cum aceto" ou "in aceto". L'alternance oleum/[P]oleum (huile brute puis huile preparee) est interessante et pourrait signifier : d'abord l'huile de base, puis l'huile deja aromatisee/infusee.

### Ligne 2 - F103V : sal + cera + aqua
```
in 2ʒ [M]materia cum sal [M]materia et misce.2 et cum 1×UNK_or [M]materia misce [P]cera cum 1ʒ [P]aqua
```
**Plausibilite** : MODEREE-HAUTE. La combinaison sal + [P]cera + [P]aqua (sel + cire preparee + eau traitee) evoque un ceratum salin - un onguent de base cire avec du sel comme agent actif, delaye dans de l'eau (probablement eau de rose ou eau salicylee). L'eau "preparee" ([P]aqua) est un concept reel : aqua rosarum (eau de rose distillee) est de l'eau "preparee". Probleme : "in 2ʒ" en ouverture est bizarre - "in" ne s'utilise pas avec une quantite seule en contexte receptaire.

### Ligne 3 - F108V : oleum + cera + misce x5
```
[M]1×oleum misce.2 et misce.2 et [P]materia misce.2 et misce.1 et [M]1×cera cola.1 et misce.2 et ana
```
**Plausibilite** : FAIBLE. Trop de "misce" consecutifs. Aucune recette reelle ne dit "melange, melange, melange, melange, filtre, melange". La cloture par "ana" (parties egales) est correcte mais contradictoire : "ana" implique que les ingredients qui precedent sont en parts egales, or seuls oleum et cera sont nommes. Le squelette oleum + cera + cola + ana est plausible, mais le remplissage par des verbes est excessif.

### Ligne 4 - F84R : Rx + oleum + aqua + cera
```
Rx [M]materia et misce.1 et oleum [P]materia et [M]1×oleum cum aqua [P]cera [P]materia cum [P]materia 2ʒ in 1ʒ [P]materia et
```
**Plausibilite** : MODEREE. L'incipit Rx est parfait. La sequence oleum + cum aqua + [P]cera est exactement la base d'un ceratum : on chauffe l'huile, on ajoute la cire, on delaye avec de l'eau. L'alternance [M]oleum (huile brute) et [P]cera (cire preparee/lavee) est coherente : la cire doit etre lavee avant utilisation (cera lota). Probleme : "[P]materia et" repete sans specification est la signature d'un decodage incomplet, pas d'un texte pharmaceutique.

### Ligne 6 - F113R : "signa" + succus + acetum
```
signa [P]materia et adde.2 [P]2×succus per 2ʒ [P]materia 1ʒ [P]2×acetum cum 2×acetum 2ʒ adde.2 et
```
**Plausibilite** : FAIBLE pour "signa", HAUTE pour le contenu. Le verbe "adde" (ajouter) est excellent - atteste dans de nombreuses recettes ("deinde addantur" dans l'Oximel). La combinaison succus + acetum (jus + vinaigre) est une base standard pour des sirops medicinaux. Mais "signa" en tete est problematique (cf. Anomalie 4).

### Ligne 7 - F55R (Section Herbal) : aqua + oleum + sal
```
1ʒ UNK_or 2ʒ [P]acetum de 1ʒ cum aqua aqua oleum de aqua aqua sal
```
**Plausibilite** : BASSE comme phrase latine, HAUTE comme liste d'ingredients. Cela ressemble plus a un INDEX ou une TABLE MATIERE qu'a une recette procedurale : "acetum, de aqua, aqua, oleum, de aqua, aqua, sal" = une enumeration de substances-cles pour un simple (herbe) dans la tradition du Circa Instans (chapitre : "De X : complexionne calida et sicca... ualet cum aqua... cum aceto..."). Le prefixe "de" (de/a propos de) renforce cette lecture.

### Ligne 8 - F55V (Section Herbal) : succus + oleum + sal + aqua + ana
```
misce.3 succus 1ʒ cum oleum sal [P]materia et aqua 2ʒ oleum aqua ana
```
**Plausibilite** : MODEREE-HAUTE. C'est la ligne la plus "receptaire" du lot. Succus + oleum + sal + aqua + ana = "Melange fort: jus 1 drachme, avec huile, sel, [produit] et eau 2 drachmes, huile, eau, parties egales". La cloture par "ana" est parfaite. La combinaison succus + oleum est une base d'onguent vegetal. Le probleme reste l'absence d'ingredients specifiques apres "succus" (succus de QUOI ? rosarum ? apii ? plantaginis ?).

### Ligne 10 - F103V : Rx + sal + aqua + oleum
```
Rx [P]sal [M]sal [M]UNK_or [P]materia et 1×UNK_or 2ʒ [M]materia et Rx [P]materia et cum [P]materia et cum aqua oleum per aqua
```
**Plausibilite** : FAIBLE pour la double occurrence de Rx. Une recette n'a qu'UN SEUL incipit "Recipe". Deux "Rx" dans la meme ligne signifie soit que c'est un RETOUR A LA LIGNE mal segmente (deux recettes consecutives), soit que le decodage de "p/f" comme Rx est trop large. La distinction [P]sal / [M]sal (sel prepare vs sel brut) est cependant tres pertinente - en pharmacie medievale, le sel pouvait etre "sal preparatum" (sel purifie par dissolution et cristallisation) vs "sal commune" (sel gemme brut).

---

## PARTIE V : RECETTES REELLES DE COMPARAISON

Pour apprecier l'ecart, voici comment les memes TYPES de preparations apparaissent dans l'Antidotarium :

### Un onguent reel (Unguentum fuscum, DBNL)
```
Recipe olei lb.i et ½ ; cerae ʒ iiii ; colofoniae ʒ ii ; gummi serapini an ʒ iii ;
picis navalis colatae an ʒ iii ; mastici an ʒ i ; galbani an ʒ i ; terebintinae an ʒ i.
Confice sic: oleum prius in olla mittatur et bulliat: tunc apponatur cera incisa
et cetera alia species. Et cum coeperint liquefieri, ab igne remoueatur semper agitando...
```
Structure : Rx + 8 ingredients NOMMES avec quantites + instructions procedurales DETAILLEES.

### Un oxymel reel (Oximel, DBNL)
```
OXimel sic fit. Recipe aque lb.viii in qua bulliant radices feniculi ʒ ii ; radices rafani ʒ ½ ;
radices apii petroselini macedonici sparagi bruxi saxifrage an ʒ iiii ; polipodii ʒ viii.
Deinde coletur: et colaturae addatur mellis despumati lb.i et aceti fortissimi lb.i et ½.
Et bulliat usque ad consumptionem tertie partis uel quarte...
```
Structure : Rx + 9 ingredients racines NOMMES + "coletur" + miel + vinaigre + cuisson.

**Comparaison avec vos lignes** : vos decodages capturent la couche "aqua, oleum, acetum, mel, cola, misce" - mais il manque les 80% de contenu specifique (feniculum, rafanus, apium, petroselinum, macedonicum, sparagi, bruxi, saxifraga, polipodium...).

---

## PARTIE VI : RECOMMANDATIONS POUR LA SUITE

### 6.1 Priorite absolue : decoder les tokens "[M]MATERIA" et "[P]MATERIA"

Ces tokens sont la cle. Ils contiennent vraisemblablement les noms de la matiere medicale specifique (les plantes, mineraux, et composites). Si le modele peut identifier ne serait-ce que 5-10 ingredients specifiques supplementaires (cinamomum, crocus, aloe, mastix, piper, etc.), la validation deviendrait beaucoup plus forte.

### 6.2 Reexaminer la correspondance l = per

Remplacer "per" par "cum" dans les decodages ameliorerait considerablement la plausibilite syntactique. "Cum aceto" est standard, "per acetum" ne l'est pas. Verifier si le prefixe "l" ne pourrait pas correspondre a "cum" (qui est aussi une preposition monosyllabique).

### 6.3 Reexaminer t = signa

Envisager que "t" soit un marqueur de paragraphe/section/rubrique plutot que le verbe "signa". Dans un contexte receptaire, ce pourrait etre l'equivalent d'un titre de recette ou d'un separateur ("Item", "Aliud", "Experimentum").

### 6.4 Distinguer les types de texte par section

Les lignes de la section Herbal (F55R, F55V) ne ressemblent pas a des recettes mais a des monographies de simples (type Circa Instans). Les lignes des sections Pharma (F103V, F107V, F108V, F113R) ressemblent davantage a des procedures de preparation. Les lignes Balneo (F84R, F80V) pourraient etre des prescriptions (format ordonnance). Ce ne sont pas les memes genres textuels et ne devraient pas etre evalues avec les memes criteres.

### 6.5 L'hypothese "notation" vs "langue"

Le fait que les lignes decodees n'aient pas l'allure d'un latin continu mais plutot d'une LISTE PARAMETREE (substance + etat + quantite + verbe) conforte en fait votre hypothese de depart : ce n'est PAS du latin ecrit, c'est une **notation compacte**. Mais alors, le comparateur ne devrait pas etre le texte continu de l'Antidotarium mais plutot des LISTES d'ingredients abrégées, du type qu'on trouverait dans un carnet d'apothicaire personnel ou une table de composition.

---

## PARTIE VII : TABLEAU RECAPITULATIF DE VALIDATION

| Element decode | Authentique ? | Confiance | Commentaire |
|---|---|---|---|
| Rx (Recipe) en incipit | OUI | 95% | Universel, parfaitement atteste |
| oleum (huile) | OUI | 95% | Excipient majeur |
| cera (cire) | OUI | 95% | Base de cerats/onguents |
| sal (sel) | OUI | 90% | Ingredient actif et excipient |
| aqua (eau) | OUI | 95% | Vehicule universel |
| acetum (vinaigre) | OUI | 90% | Base oxymel, topique |
| succus (jus) | OUI | 85% | Jus vegetal frais, atteste |
| ana (parties egales) | OUI | 90% | Marqueur de dose egale |
| misce (melanger) | OUI | 90% | Imperatif pharmaceutique standard |
| cola (filtrer) | OUI | 85% | Imperatif atteste (coletur aussi) |
| adde (ajouter) | OUI | 85% | Atteste dans Oximel etc. |
| cum = vehicule | OUI | 95% | Emploi dominant dans l'Antidotarium |
| [M]/[P] brut/prepare | CONCEPT OUI | 80% | Concept exact, codage non medieval |
| Quantites 1-3ʒ | PARTIELLEMENT | 70% | Correct pour actifs, faux pour bases |
| per = preposition | DOUTEUX | 30% | Quasi absent du registre receptaire |
| signa = etiqueter | DOUTEUX | 25% | N'appartient pas au registre de l'Antidotarium |
| "MATERIA" generique | ANORMAL | 20% | Les recettes reelles nomment tout |
| Densite de verbes | ANORMAL | 15% | 5-10x trop elevee vs Antidotarium |
| Quantites isolees | ANORMAL | 20% | Toujours greffees sur un ingredient |

---

## Conclusion

Le modele V22-V34 a correctement identifie **la couche excipientaire** du texte pharmaceutique du Voynich. C'est un resultat significatif : les 6 substances de base, les 3-4 verbes proceduraux, et les marqueurs structurels (Rx, ana, [M]/[P]) sont tous authentiquement salernitains. La combinatoire oleum+cera (onguent), acetum+cola (preparation filtree), et la syntaxe cum+vehicule sont des preuves de plausibilite forte.

Ce qui manque est la couche semantique : les 80% du texte qui contiennent les noms de la matiere medicale specifique (plantes, mineraux, composites nommes). Les tokens "[M]MATERIA" et "[P]MATERIA" sont le prochain verrou a faire sauter.

Le texte decode ne se lit pas comme du latin pharmaceutique continu - il se lit comme une **notation tabulaire compacte**, ce qui est en fait coherent avec votre hypothese d'un systeme notationnel plutot que d'une langue naturelle chiffree. Le comparateur ideal n'est peut-etre pas le texte courant de l'Antidotarium mais les tabulations d'une ricettario d'apothicaire.

*Analyse realisee en croisant l'ed. DBNL van den Berg 1917, les transcriptions Ponzi/BNF Lat. 6823, le Circa Instans (Platearius), la Collectio Salernitana (De Renzi), et les corpus construits pour le pipeline K&A v12 (799K mots de latin medical medieval valide par Collatinus).*
