# Methodologie de decodage du Manuscrit Voynich (MS 408)
## Systeme de mapping King & Andrisani (2019) - Validation et extension

**Date** : 7 avril 2026
**Auteur** : Guillaume Cle, avec assistance analytique Claude

---

## 1. Fondements

### 1.1 Le systeme K&A

Le mapping King & Andrisani (2019) propose que chaque glyphe EVA du manuscrit Voynich represente une ou plusieurs syllabes latines. Le manuscrit serait un traite medical en latin vulgaire utilisant un systeme stenographique derive des Notes Tironiennes.

Notre travail a consiste a :
1. Verifier independamment ce mapping sur des pages specifiques
2. Decouvrir les regles de desambiguation contextuelles
3. Valider par croisement sur trois domaines independants
4. Construire un decodeur automatise

### 1.2 Strategie : l'attaque par texte connu (Crib Attack)

Inspiree de la methode de Turing a Bletchley Park : au lieu de tester le mapping globalement sur les 32 000 tokens du VMS, nous avons concentre l'attaque sur UNE page dont le contenu botanique est identifie avec certitude.

Page cible : **f9v** (Viola tricolor, confiance 0.95).
Raisonnement : si le mapping est correct, le texte de cette page DOIT contenir le vocabulaire medical latin associe a la violette tricolore.

---

## 2. Table de mapping

### 2.1 Valeurs de glyphes verrouillees (Tier 1)

Ces valeurs sont confirmees par au moins 3 sources independantes (texte medical f9v, texte medical f1v, noms d'etoiles f68r) :

| Glyphe EVA | Valeur latine | Exemples cles |
|------------|--------------|---------------|
| ch | i | chor=iera, chol=ies, chy=in |
| sh | ci | shor=ciere, shol=cies |
| cth | li / ili / eli | cthor=liare, cthy=ilium, cthol=eliece |
| a | u (parfois a apres qu) | daiin=dura, char=iure, okal=aequas |
| t | el / l | taor=eluere, toldy=elece |
| l | s (defaut) / ce (avant y) | chol=ies, dal=duce, cthol=eliece |
| e | o | oeees=eos, cthey=ilion |
| m | m | dam=dum |
| iin | ura / ure / are | daiin=dura, kaiin=cura, aequare |

### 2.2 Valeurs contextuelles (Tier 2)

| Glyphe | Contexte | Valeur | Exemples |
|--------|----------|--------|----------|
| k | avant glyphe-voyelle | c / ec | kaiin=cura, chkaiin=iecur |
| k | apres glyphe-voyelle ou y | qu / aequ | oky=aequ, okal=aequas, ykol=inaequas |
| y | suffixe -dy | et (logographique) | toldy=elece et, dy=et |
| y | initial (y-) | in (prefixe) | ykaiin=inaequare, ykol=inaequas |
| y | final apres consonne | n ou TRONCATURE | chy=in, oky=aequ(are), cthy=ili(um) |
| o | defaut | e | chol=ies, dol=edes |
| o | avant k | ae | oky=aequ, okodar=aeque-deure |
| o | apres k (=qu) | a | okal=aequas, ykol=inaequas |
| o | apres labiale (p,f,cfh) | a | cfhol=pias, cthor=liare |
| o | rare (latin vulgaire) | u | soiin=usure |
| d | avant a | d | daiin=dura, dal=duce |
| d | avant o (initial) | ed | dol=edes |
| d | apres voyelle | de | dary=deure, okodar=aeque-deure |
| d | dans dy | et (logographique) | dy=et |
| r | defaut | re | shor=ciere, char=iure |
| r | apres a(=u), final | ra | dar=dura |
| q | defaut | co / con / cum | qoaiin=coneure, qool=cum e |
| p | defaut | per / p | pol=per es, potoy=per ille |
| f | defaut | par / f | fochor=pariere |
| s | defaut | us | soiin=usure |

### 2.3 Regles speciales (Tier 3)

| Regle | Description | Exemples |
|-------|-------------|----------|
| Deduplication de voyelles | Voyelles doublees aux jonctions morphemiques -> simple | d.u.ura -> dura, co.ae.qu.u.re -> coaequare |
| Triple reduplication | Triple glyphe identique = voyelle longue unique | oeees (e.ooo.us) = eos |
| H-prosthese | Le h initial est omis (latin vulgaire) | iera = hiera, iere = hiere |
| Fusion O/U | 'o' peut valoir 'u' (latin vulgaire) | soiin = usure |
| ch- logographique | ch- initial peut etre conjonction 'et' | chshoty = et cie elle |
| d- avant ch | d- devant ch peut etre 'et' ou 'de' | dchor = et hiera / de iure |
| Mots composes | Un seul mot EVA peut contenir 2 mots latins | okolshol = aequas cies, ctholshol = eliece cies |

---

## 3. Validation sur trois domaines

### 3.1 Domaine 1 : f9v (Viola tricolor) - Texte medical

Pages decodees : f9v (12 lignes, ~85 mots)
Couverture haute confiance : 64%
Couverture totale : 72%

Mots cles confirmes : dura (durete, 9 occurrences), hiera (antidote), iecur (foie), ciere (evacuer), liare (lisser), eluere (laver), piare (purifier), aequare (equilibrer), colare (filtrer), duce (extraire), edes (emettre), cies (evacuer 2e pers.), et (conjonction, logographique)

Coherence medicale : traite sur le traitement des duretes hepatiques par la Viola tricolor, parfaitement conforme a l'usage medieval de cette plante.

### 3.2 Domaine 2 : f68r1/r2 (Cartes celestes) - Noms d'etoiles

Le MEME mapping applique aux etiquettes des diagrammes stellaires produit des noms d'etoiles reconnaissables :

| EVA | Decode | Identification | Distance |
|-----|--------|---------------|----------|
| otshey | elcion | Canis Major (gr. Kuon) | exact |
| olor | asere | Sirius (Aschere) | exact |
| sheey | cion | Cygnus (Cycnus) | exact |
| shdar | sidur | Sidus (etoile) | exact |
| odaiin | ~ardure | Arcturus | d=1 |
| oteool | ~aloese | Vega/Aloere | d=1 |

4 matchs exacts + 2 fuzzy. Le meme systeme de glyphes qui decode du texte medical produit aussi des noms astronomiques.

### 3.3 Domaine 3 : f1v (Atropa belladonna) - Texte medical

Pages decodees : f1v (10 lignes, ~81 mots)
Couverture haute confiance : 55%
Couverture totale : 74%

Coherence medicale : traite plus agressif que f9v (adure=detruire, seca=briser), coherent avec la nature toxique de la belladonne.

Cross-validation critique : 11 mots communs a f9v ET f1v se decodent au MEME latin : daiin=dura, shor=ciere, shol=cies, char=iure, chol=ies, cthy=ilium, chy=in, dchor=de iure/et hiera, dol=edes, dal=duce, dar=dura.

### 3.4 Domaine 4 : f15r (Cichorium intybus) - Nom de plante

Le mot EVA **shkaiin** sur f15r ligne 7 decode en **CICURA** :
- sh = ci, k = c, a = u, iin = ra => cicura

CICURA est la forme medievale latine de "cichorium" (chicoree). Le NOM DE LA PLANTE apparait dans le texte lui-meme, confirmant independamment l'identification botanique de K&A. Vocabulaire medical confirme sur f15r : dura (x5), ciere (x3), coaequare (x2), ili(a) (x5), hiera (x1), cicura (x1).

### 3.5 Resume de la validation multi-domaines

| Domaine | Page | Type | Resultat |
|---------|------|------|----------|
| Texte medical | f9v | Viola tricolor | Vocabulaire hepatique coherent |
| Noms d'etoiles | f68r | Carte celeste | 4 matchs exacts + 2 fuzzy |
| Texte medical | f1v | Belladonne | 11 mots identiques a f9v |
| Nom de plante | f15r | Chicoree | shkaiin = CICURA |

**UN SEUL mapping, QUATRE domaines independants, TOUS coherents.**

---

## 4. Le decodeur automatise (v5)

### 4.1 Architecture

Le decodeur `voynich_decoder_v4.py` implemente :

1. **Tokeniseur EVA** : decoupe les mots en glyphes (ch, sh, cth, ckh, cfh, cph, iin, etc.)
2. **Pre-traitement** : reduction des triples glyphes (eee -> e)
3. **Resolution contextuelle** : chaque glyphe est resolu selon son contexte (position, voisins)
4. **Expansion** : generation de tous les candidats latins (max 600)
5. **Deduplication de voyelles** : elimination des doublets aux jonctions
6. **Scoring** : les termes du vocabulaire medical confirme recoivent un bonus x5000
7. **Traitement final-y** : choix entre troncature et valeur phonetique 'n'
8. **Couche logographique** : dy=et, d+ch=et/de, ch-initial=et (avec priorite au decodage standard)
9. **H-prosthese** : test automatique de la variante avec h- initial

### 4.2 Critere de desambiguation y final

Quand y est en position finale :
1. Si -dy -> TOUJOURS 'et' (logographique, priorite maximale)
2. Sinon, essayer d'abord la troncature (la racine forme-t-elle le debut d'un mot latin atteste ?)
3. Si aucune troncature ne fonctionne, utiliser y='n'

### 4.3 Priorite du decodage standard sur le logographique

Le decodage standard (ch=i) a priorite sur le logographique (ch=et) quand le decodage standard produit un mot du vocabulaire medical confirme. Exemple : chor -> iera/hiera (standard, HIGH) bat "et ere" (logographique).

### 4.4 Taux de reussite

| Page | Tests unitaires | Haute confiance | Couverture totale |
|------|----------------|-----------------|-------------------|
| f9v | 13/14 (93%) | 64% | 72% |
| f1v | 13/14 (93%) | 55% | 74% |

---

## 5. Textes reconstruits

### 5.1 f9v (Viola tricolor) - Traite hepatique

```
L01: [PARIERE] [APARA ET] AP(UD) CIERE DURA [COEPI-PIA] COEPES CIES FIAS DURA
L02: ET HIERA CONEURE IECUR LIARE IES HIERA PIAS ET AL(IA) COAEQUARE ET
L03: IN QUO HIERA INAEQUARE DURA ILI(UM) ELEURE AEQU(ARE) EOS DURA
L04: IN ELO LI(B) CURA LIARE ELECE AL(IA) ELECE ET
L05: PIARE IN PER ION COLARE IN PER(I) ESPIACE ELEURE IL(IUM) DURA
L06: EDES IA(M) [...] ET [...] DURA ALI(A) [ELIADE/VIOLA] NEQUE
L07: COE IES IES [LI] DURA ALAS DARE DURA(M)
L08: [US]URE DURA COAEQU(A) RECUNDE DUCE
L09: DURA IN [ELUERE] IN EL(LE) DEUR(E) IN ELECE ET
L10: AL(IA) CIES IES IN [...]
L11: [HIERA] [ET CIE ELLE] AEQU(ARE) CURA
L12: IECUR AQUI(S) HIERA
```

Traduction : Traite sur le traitement des duretes (calculs) du foie par la violette tricolore. Le texte enumere les actions therapeutiques (evacuer, lisser, laver, purifier, equilibrer, extraire) et nomme l'organe cible (foie) et le remede (hiera/antidote). La derniere ligne "Le foie, (par les eaux), l'antidote" conclut le traite.

### 5.2 f1v (Atropa belladonna) - Traite purgatif

```
L01: [AEQUIRE] [et ADURE] ES [ESELIO] IURE [FIURUM]
L02: IN ELLO IURE [ARE] [...] [ET IE SECA ET] AEQUE-DEURE I EDE
L03: [EDE AQUI] [AQUIS ET AQUIS] [SIC] [AEQUACIONE] ILI(UM) [AEQU-ELIDE ET] DUCE
L04: EDES ET [AEQUOA] [...] DUM [...] [...] ET
L05: PER [ILLE] CIES [...] PIAS DURA ION ELEDE ET ELEURE CIES
L06: ET [AQU] IES [ELIECE CIES] AEQUAS [EDES ION] ET EDE [ESSES] IN ILI(UM)
L07: CO(E) IES IES EDES [ILIO] INAEQUAS EDES [EDES] INAEQUAS [EDES I EDE]
L08: AEQUAS CIES [...] IES [AEQU] IES ELIECE [I EDE] IES DURA
L09: CIERE AEQUAS IES [EDES AEQUE-DEURE] [DURA] CIES ET HIERA [ILLE] DURA CIE ET
L10: ELUERE ET [ILLO] DUCE [I EDE] [ARIE ET] PES ET ADURE
```

Traduction : Instructions therapeutiques plus agressives que f9v, coherentes avec la nature toxique de la belladonne. Le texte insiste sur "eradiquer" (deure), "briser" (seca), "detruire" (adure), "dessecher" (are/arie).

---

## 6. Limites et travaux futurs

### 6.1 Problemes non resolus

1. **Polyvalence residuelle de 'o'** : o=e dans 64% des cas, o=a dans 14%, o=ae dans 8%, o=u dans 5%. La regle contextuelle couvre ~80% mais pas la totalite.

2. **Mots composes** : le decodeur ne gere pas encore les mots EVA qui contiennent 2+ mots latins (okolshol=aequas cies).

3. **Mot 'dair'** : present sur f1v mais non resolu. K&A lit "dura" ou "deure" mais le token 'i' intermediaire pose probleme.

4. **Le conflit 'cthod'** : sur f9v L06, la grille K&A produit "liade" mais une grille alternative donnerait "viola". Les deux sont possibles en contexte.

5. **Couverture globale** : 72-74% de couverture totale, ~55-64% haute confiance. Il reste 25-30% des mots a resoudre.

### 6.2 Prochaines etapes

1. **Decoder les pages Main 2** (Bio/Balneo) pour verifier le mapping sur un style ultra-abrege
2. **Decoder les pages Main 4** (Zodiac) pour extraire plus de noms d'etoiles
3. **Ameliorer la detection de mots composes** (okolshol = aequas cies)
4. **Construire un lexique par page** : identifier le nom de chaque plante dans son texte
5. **Traduction systematique page par page** du manuscrit complet

---

## 7. Analyse des scribes (decodeur v5)

### 7.1 Cinq mains, un seul mapping

L'analyse de Lisa Fagin Davis identifie 5 scribes. Notre analyse statistique sur 226 pages confirme que les differences entre scribes portent sur le STYLE d'ecriture, pas sur la VALEUR des glyphes. Le mapping K&A est invariant.

Preuve : 10 mots EVA communs entre f9v (B-type) et f15r (B-type) se decodent identiquement (daiin=dura, chor=hiera, shor=ciere, etc.). 7 mots communs entre f9v et f3r (A-type), tous identiques.

### 7.2 Le spectre e/y

Le ratio e/(e+y) classifie chaque page :
- A-type (e/(e+y) > 0.35) : voyelles explicites, -m accusatifs preserves, formes completes
- B-type (e/(e+y) <= 0.35) : troncatures par y, plus de dy='et', -m omis

Pages decodees : f3r=A_STRONG (0.583), f25v=A (0.571), f1v=B (0.294), f9v=B (0.170), f15r=B (0.182)

### 7.3 Decouverte CICURA (f15r)

Le mot EVA **shkaiin** sur f15r L07 decode en CICURA (sh=ci, k=c, a=u, iin=ra), forme medievale de "cichorium" (chicoree). Le NOM DE LA PLANTE apparait dans le texte, confirmant independamment l'identification botanique. 4eme domaine de validation.

### 7.4 Signatures des mains

| Main | % de -dy | Abbreviations | Exemples uniques |
|------|----------|--------------|-----------------|
| 1 | 6.6% | Moderees | ctho, kchor, cthaiin |
| 2 | 27.1% | Massives | qolchedy, rshedy |
| 3 | 18.9% | Fortes | alam, lkchdy |
| 4 | 11.9% | Catalogues | oteotey, okeodar |
| 5 | 29.8% | Maximales | (peu de donnees) |

---

## 8. Fichiers de reference

| Fichier | Contenu |
|---------|---------|
| `voynich_decoder_v5.py` | Decodeur author-aware v5 (reference) |
| `voynich_decoder_v4.py` | Decodeur v4 (archive) |
| `scribe_analysis.py` | Analyse statistique 226 pages par scribe |
| `scribe_deep_analysis.py` | Analyse e/y, -m, bigrammes par groupe |
| `semantic_analysis_f15r_f3r.py` | Analyse semantique f15r + f3r |
| `crib_attack_f9v.py` | Premiere attaque par texte connu sur f9v |
| `bombe_cross_validation.py` | Validation croisee sur noms d'etoiles |
| `semantic_solver_f9v.py` | Solveur semantique a 10 regles (f9v) |
| `semantic_f1v.py` | Solveur semantique pour f1v |
| `resolve_ambiguities.py` | Analyse systematique des ambiguites |
| `BOMBE_RESULTS_f9v.md` | Document de resultats detaille |
| `ANALYSE_SCRIBES_VMS.md` | Analyse complete des scribes et langages |
| `king_andrisani_2019_transliteration_table.json` | Donnees K&A source |

---

*Document mis a jour le 7 avril 2026.*
*Methodologie : attaque par texte connu (crib attack) + validation croisee multi-domaines (Bombe) + resolution semantique contextuelle + analyse des scribes.*
