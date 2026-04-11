# Response 04 : Systeme de notation pharmaceutique abrege
## Validation externe du modele V22-V34

**Date** : 9 avril 2026
**Sources croisees** : 1 rapport ChatGPT (2 pages) + recherche independante Claude
**Niveau de confiance global** : MODERE (des paralleles partiels existent, aucun systeme identique n'est documente)

---

## 1. Notes tironiennes : le parallele le plus proche

### 1.1 Principe de fonctionnement
La stenographie latine inventee par Marcus Tullius Tiro (c. 63 av. J.-C.), secretaire de Ciceron. Initialement ~4 000 signes, etendu a ~13 000 au Moyen Age. Utilise du Ier siecle av. J.-C. jusqu'au XVIIe siecle.

**Structure modulaire :**
- Un **radical** (racine du mot) = signe de base
- Un petit **signe auxiliaire** pour la terminaison/inflexion
- La **position de l'auxiliaire par rapport au radical** peut changer le sens

Gamer (2015, etude moderne sur les notes tironiennes) note que "la signification peut changer selon la position de l'auxiliaire". C'est explicitement un systeme a couches (radical = nom, auxiliaire = inflexion), analogue a prefixe/suffixe.

**Points communs avec le modele Voynich :**
- Un signe de base combine a un marqueur (suffixe) modifie le sens
- "Meme suffixe = meme substance, prefixe different = action differente" - c'est exactement la logique des notes tironiennes ou le radical reste constant et l'auxiliaire varie

### 1.2 Similarite avec le modele V22-V34 : ~7/10

**Ce qui correspond :**
- Encodage multi-couches explicite (radical = substance, auxiliaire = inflexion/fonction)
- La position du signe auxiliaire est significative
- Un seul glyphe encode a la fois une racine semantique ET une information grammaticale

**Ce qui differe :**
- Les notes tironiennes encodent des MOTS complets (radical + terminaison), pas des combinaisons multi-parametriques (substance + quantite + methode + fonction)
- Pas de notion de quantite codee dans le glyphe tironien
- Pas d'indication d'etat de la matiere (brut vs prepare)

### 1.3 Source de reference
- Schmitz, Wilhelm. *Commentarii Notarum Tironianarum* (Leipzig: B.G. Teubner, 1893). 394 pages + 132 tables. Numerise sur Internet Archive (https://archive.org/details/commentariinotar00schm) et Hathi Trust
- Gamer (2015), etude moderne (Zurich, https://www.zora.uzh.ch/server/api/core/bitstreams/2571fef4-0090-49cf-a06a-6bed7f3cb24c/content)
- Le symbole "et tironien" (⁊) est le seul survivant moderne de ce systeme

---

## 2. Abreviations pharmaceutiques latines (XIIIe-XVe s.)

### 2.1 Systeme d'abreviations standard
Usage d'abreviations normalisees pour verbes et matieres en pharmacie. Chaque sigle abrege rend un verbe d'action ou une forme de preparation, parfois avec un point :
- **Coq.** = coque (cuire/bouillir)
- **M.** = misce (melanger) OU minim (goutte) OU manipulus (poignee)
- **Col.** = cola (filtrer)
- **Ft.** = fiat (qu'il soit fait)
- **Colat.** = colatura (liquide filtre)
- **ss** = semis (demi)
- **℥** = uncia (once) - forme aplatie du "3"
- **ʒ** = drachme (lettre yogh medievale anglaise)
- **℈** = scrupule (epsilon grec inverse)
- **℮** = manipulus (poignee)
- **an** = ana (parties egales)
- **q.s.** = quantum sufficit (quantite suffisante)

### 2.2 Similiarite avec le modele V22-V34 : ~3-5/10

**Ce qui correspond :**
- Il existe des prefixes verbaux (Coq. = cuire, M. = melanger, Ft. = fiat) et des suffixes pour formes (colat. = colatura)
- Les etats materiels se notent par des suffixes : Cappelli donne "(Coqu.) coque" = "faire bouillir" et "(Colat.) colaturae" = "(filtrats)"
- Les quantites sont denotees par abreviation + chiffres romains minuscules (℥ss pour demi-once, ʒiij pour 3 drachmes)

**Ce qui differe :**
- Ce n'est PAS un systeme hierarchique multi-couches : c'est un ensemble d'abreviations composees
- L'ingredient, la quantite et le verbe sont toujours des elements SEPARES dans la ligne de recette, jamais fusionnes en un seul symbole
- Les quantites sont toujours separees de l'abreviation d'ingredient (ex. "ad 2 vices" separe, jamais dans la meme abreviation)

### 2.3 Source de reference
- Cappelli, Adriano. *Lexicon Abbreviaturarum: Dizionario di Abbreviature Latine ed Italiane* (Hoepli, Milan, 1899). 14 357 abreviations. En ligne : Calameo (https://www.calameo.com/books/00010704456b06fd9e304) ; Ad Fontes (Zurich) ; Archive.org
- Text Partnership (Cambridge) : symboles d'apothicaires (https://www.textpartnership.net/docs/dox/medical.html)

---

## 3. Notation de l'etat de la matiere (brut vs prepare)

### 3.1 Terminologie attestee
Dans le latin pharmaceutique medieval, la distinction brut/prepare est exprimee par des adjectifs/participes :
- **Brut/frais** : recens (frais), viridis (vert/frais), crudus (cru)
- **Prepare/traite** : despumatus (ecume), ablutus (lave), contusus (broye), incisus (coupe), preparata (prepare), siccatus (seche), pulverizatus (pulverise), distillatus (distille)
- **Exemple concret** : dans l'Oleum rosatum, on trouve "oleum ... ablutus" (huile lavee) et roses "contusae" (roses broyees) vs "rosarum ... viridium" (roses fraiches/vertes)
- "cera preparata" ou "cera lota" (cire preparee/lavee) vs cera brute

### 3.2 Systeme de prefixe/suffixe formel ?
**NON CONFIRME.** Aucun systeme formel ou une LETTRE-PREFIXE indiquerait systematiquement l'etat M (materia = brut) vs P (praeparata = prepare) n'a ete retrouve dans la litterature secondaire. La distinction est faite par des adjectifs en toutes lettres (ou leurs abreviations standard), pas par un code positionnel.

### 3.3 Implication pour le modele Voynich
La DISTINCTION CONCEPTUELLE brut/prepare est parfaitement medievale et standard. Le CODAGE par prefixe positionnel [M] vs [P] est, en revanche, une innovation propre au systeme Voynich (si le decodage est correct). C'est un encodage plus compact du meme concept.

---

## 4. Encodage multi-couches : un seul symbole = plusieurs informations

### 4.1 La question centrale
Le modele V22-V34 postule que chaque token Voynich encode simultanement : (1) marqueur structurel, (2) prefixe fonctionnel (cum/in/ex/per/de/re), (3) etat materiel (brut/prepare), (4) quantite (1x, 2x, 3x), (5) substance de base (~10 ingredients).

### 4.2 Existe-t-il un systeme medieval comparable ?
**AUCUN SYSTEME IDENTIQUE n'a ete documente** dans la litterature secondaire accessible. Neanmoins :

**Notes tironiennes (similarite ~7/10)** : radical + auxiliaire positionnel = 2 couches d'information (mot + inflexion). Le parallele structurel le plus fort.

**Abreviations pharmaceutiques (~3-5/10)** : prefixes verbaux + suffixes de forme + symboles de quantite, mais toujours en elements SEPARES.

**Abreviations notariales (~5/10)** : traits et petits signes attaches indiquent des groupes frequents. Une barre sur une lettre = omission de "m/n" ; le chiffre "9" medieval = con/cum. Prefixe/suffixe par signe special, terminaisons -us/-os marquees par un petit crochet ou une barre. C'est proche de l'idee prefixe/suffixe, mais pour du texte courant, pas pour un encodage parametrique.

**Notation musicale carree (~3/10)** : elements positionnels (hauteur du neume sur la portee = ton), mais applique au son, pas a l'information pharmaceutique.

### 4.3 Verdict
Le concept d'un glyphe multi-parametrique encodant simultanement 5 couches d'information pharmaceutique n'a **pas de parallele medieval exact connu**. Les paralleles partiels les plus forts sont les notes tironiennes (2 couches) et les abreviations notariales (prefixe/suffixe). Si le decodage est correct, le systeme Voynich represente une innovation d'encodage plus dense que tout ce qui est documente dans la tradition manuscrite medievale.

---

## 5. Manuscrits pharmaceutiques italiens (1350-1450)

### 5.1 Manuscrits verifies
**Carrara Herbal** (British Library, Egerton 2020) : Fin XIVe siecle, Padoue. Commande par Francesco II da Carrara (r. 1390-1405). Traduction italienne (dialecte padouan) du *Liber de Semplici Medicamentis* d'Ibn Sarabi. Entrees formulaires avec illustrations. C'est le manuscrit pharmaceutique illustre padouan le plus proche du VMS en termes de date et lieu.

**Fasciculus Medicinae** : Circule sous forme manuscrite fin XIVe-debut XVe siecle, premiere impression Venise 1491. "Faisceau" de 6 traites medievaux independants. Combine texte et illustrations didactiques.

**Circa Instans** : ~240 manuscrits survivants, premiere impression Venise 1497. Largement diffuse et traduit en italien.

**Fonds Bodleian** : Manuscrits italiens c.1461 (Padoue), c.1400 (Bologne), fin XIVe s. (Venise), c.1450-1460 (Padoue), milieu XVe s. (Bologne).

**Source** : Sarah Kyle, *Medicine and Humanism in Late Medieval Italy: The Carrara Herbal in Padua* (Routledge, 2017) ; Medieval Bodleian catalog (Italie, https://medieval.bodleian.ox.ac.uk/catalog/place_1000080)

### 5.2 Script mercantesca
- **Confirme** : ecriture cursive a usage marchand, utilisee par les marchands italiens a partir du milieu du XIVe siecle
- Employe dans des textes techniques (livres de recettes, traites), surtout en vernaculaire, sur papier
- Certains manuscrits pharmaceutiques montrent une influence mercantesque
- Les experts notent que ce "script marchand" est "tres difficile" a lire et depend fortement des abreviations
- **MAIS** : pas de systeme code structure a plusieurs niveaux - c'est une ecriture dense en abreviations (contractions phonetiques ou de mots frequents), pas un systeme d'encodage parametrique

**Source** : Raab Collection (https://www.raabcollection.com/blog/mercantesca-italian-renaissance-script)

### 5.3 "Codebooks" pharmaceutiques
**NON CONFIRME.** Aucun "codebook" ou "nomenclateur" pharmaceutique professionnel specifique aux apothicaires italiens n'a ete retrouve dans les sources accessibles. Les apothicaires utilisaient les abreviations standard latines et le vocabulaire galenique, pas un systeme code proprietaire.

---

## 6. Chiffres mantouans (1401, 1450)

### 6.1 Structure
**Chiffre de 1401 (Francesco Ier Gonzague, Mantoue)** : Premier chiffre a substitution homophonique connu pour la correspondance diplomatique. Plusieurs formes allouees a chacune des 5 voyelles (homophones pour eviter l'analyse frequentielle).

**Chiffre de 1450 (registre Tranchedino)** : Plus complexe, 80+ entrees speciales. Combine : alphabet de substitution monoalphabetique + nulles + equivalents en code de 2 lettres pour mots/noms frequents.

### 6.2 Similarite : ~2/10

**Ce qui correspond :**
- Plusieurs symboles speciaux : un glyphe pour "9" du Tironien signifiant "et/cum" et "℞" pour recipe
- Mini-dictionnaire de mots frequents (nomenclateur)

**Ce qui ne correspond pas :**
- Ce sont des chiffres de texte (securises), pas des notations pharmaceutiques
- Pas de notion de quantite codee ou d'etats materiels
- Le but est le SECRET, pas la COMPACITE de l'information

**Source** : Cipher Mysteries (https://ciphermysteries.com/2016/07/06/fifteenth-century-cryptography) ; DePaul University, "Nomenclators"

---

## 7. Synthese : echelle de similarite des systemes paralleles

| Systeme | Date | Encodage | Similarite /10 | Points communs avec V22-V34 |
|---|---|---|---|---|
| **Notes tironiennes** | Ier s. av. J.-C. - XVIIe s. | Radical + auxiliaire positionnel | **7/10** | Position de l'auxiliaire = sens different ; "meme suffixe = meme substance" ; 2 couches d'info dans 1 glyphe |
| **Abreviations notariales** | Moyen Age | Traits/signes sur lettres = omission/fonction | **5/10** | Prefixe/suffixe par signe special ; barre = omission ; "9" = con/cum ; terminaisons codees |
| **Abreviations pharmaceutiques** | XIIIe-XVe s. | Sigles pour verbes + symboles pour quantites | **3-5/10** | Prefixes verbaux (Coq., M., Col.), suffixes de forme (colat.), symboles de quantite. Mais toujours separes |
| **Mercantesca** | XVe s., Italie | Contractions phonetiques denses | **2-3/10** | Ecriture tres abregee, mais pas structuree en couches |
| **Chiffres mantouans** | 1401, 1450 | Substitution + nomenclateur | **2/10** | Symboles speciaux pour mots frequents (et/cum, Rx), mais chiffre de securite, pas notation compacte |

---

## 8. Verdict global pour le modele V22-V34

### 8.1 Ce qui EST valide
- Le concept d'un glyphe combinant une racine semantique et un modificateur positionnel est atteste (notes tironiennes, ~13 000 signes combinant radical + auxiliaire)
- L'existence d'abreviations pharmaceutiques medievales est massive et bien documentee
- La distinction brut/prepare est un concept pharmaceutique standard medieval
- Le milieu padouan/venitien du XVe siecle produisait des manuscrits pharmaceutiques illustres (Carrara Herbal, Fasciculus Medicinae)

### 8.2 Ce qui N'EST PAS valide
- **Aucun systeme medieval connu n'encode 5 couches d'information** (marqueur + fonction + etat + quantite + substance) dans un seul symbole
- Les abreviations pharmaceutiques gardent toujours ingredient, quantite et verbe comme elements SEPARES
- Aucun "codebook" pharmaceutique proprietaire n'est documente
- La quantite n'est jamais INCLUSE dans l'abreviation elle-meme (toujours en numeraux romains separes)

### 8.3 Implication
Si le decodage V22-V34 est correct, le systeme Voynich represente une densification d'encodage SANS parallele exact medieval. Le parallele le plus proche (notes tironiennes) encode 2 couches ; le modele Voynich en postule 5. C'est soit :
- (a) Un systeme notationnel innovant invente par un apothicaire/medecin pour son usage personnel (plausible - les medecins medievaux developpaient des notations personnelles)
- (b) Un type de document dont les survivants n'ont pas encore ete identifies
- (c) Une sur-interpretation du decodage, et le systeme reel est plus simple que le modele ne le suggere

L'absence de parallele exact est a la fois une faiblesse (pas de validation directe possible) et une force (si le VMS etait un simple recueil de recettes en clair, il aurait ete dechiffre depuis longtemps).

---

## 9. Sources de reference

### 9.1 Notes tironiennes
- Schmitz (1893), Internet Archive : https://archive.org/details/commentariinotar00schm
- Gamer (2015), Zurich : https://www.zora.uzh.ch/
- Roger Pearse : https://www.roger-pearse.com/weblog/2019/08/14/an-ancient-handbook-of-short-hand-tironian-notes/

### 9.2 Abreviations
- Cappelli (1899), Calameo : https://www.calameo.com/books/00010704456b06fd9e304
- EADH, "Cappelli Online" project
- Text Partnership (Cambridge), medical symbols

### 9.3 Manuscrits italiens
- Sarah Kyle, *Medicine and Humanism in Late Medieval Italy: The Carrara Herbal* (Routledge, 2017)
- Bodleian Library, medieval manuscripts Italy : https://medieval.bodleian.ox.ac.uk/catalog/place_1000080
- Raab Collection, mercantesca : https://www.raabcollection.com/blog/mercantesca-italian-renaissance-script

### 9.4 Chiffres
- Cipher Mysteries : https://ciphermysteries.com/2016/07/06/fifteenth-century-cryptography
- DePaul University, nomenclators
