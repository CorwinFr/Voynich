# Rapport : Mots Opaques du Manuscrit de Voynich
## Pipeline v12 + deagg + scoring calibre + collision penalty
## Date : 2026-04-08

**Total mots** : 38442
**Opaques (LOW + OPAQUE)** : 3421 (8%)

---
## 1. Distribution par section

| Section | Total mots | Opaques | Taux | Commentaire |
|---------|-----------|---------|------|-------------|
| H (Herbal) | 11578 | 944 | 8% | |
| S (Stars/Recettes) | 11644 | 1070 | 9% | |
| B (Balnea) | 6389 | 301 | 4% | |
| P (Pharma) | 2586 | 270 | 10% | |
| T (Texte) | 2360 | 203 | 8% | |
| Z (Zodiac) | 1311 | 246 | 18% | |
| A (Astro) | 883 | 144 | 16% | |
| C (Cosmo) | 1691 | 243 | 14% | |

---
## 2. Mots opaques les plus frequents (EVA)

| EVA | Occurrences | Decode actuel | Sections | Confidence |
|-----|------------|---------------|----------|------------|
| l | 191 | [l] | S:103, B:27, H:26 | OPAQUE |
| air | 81 | aquare | S:39, H:13, C:8 | LOW |
| shodaiin | 24 | ciedura | H:15, S:6, C:2 | LOW |
| sh | 21 | [sh] | H:11, T:3, S:3 | OPAQUE |
| sheal | 19 | cioas | S:11, B:3, Z:2 | LOW |
| aral | 19 | areace | S:9, Z:2, T:2 | LOW |
| soiin | 18 | useura | H:5, B:4, P:4 | LOW |
| olol | 18 | esns | B:9, H:5, S:2 | OPAQUE |
| odain | 17 | edura | S:7, H:6, P:2 | LOW |
| k | 17 | [k] | H:9, C:7, T:1 | OPAQUE |
| oy | 17 | e | S:7, H:3, Z:3 | OPAQUE |
| t | 15 | [t] | H:7, C:5, T:2 | OPAQUE |
| opaiin | 15 | eperura | S:6, C:5, Z:3 | LOW |
| a | 14 | [a] | S:6, C:4, H:3 | OPAQUE |
| shedaiin | 14 | ciodura | C:6, B:4, H:2 | LOW |
| ch | 13 | [ch] | S:5, H:4, B:2 | OPAQUE |
| e | 12 | [e] | H:6, A:3, S:2 | OPAQUE |
| shdar | 12 | cideare | T:4, S:4, H:1 | LOW |
| shedain | 12 | ciodeain | S:10, H:2 | LOW |
| otedar | 12 | tedure | S:8, Z:2, B:1 | LOW |
| shod | 11 | ciede | S:5, H:4, T:2 | LOW |
| ay | 10 | u | S:4, A:2, H:1 | OPAQUE |
| ykeeol | 10 | inquoes | H:3, P:3, S:3 | LOW |
| f | 10 | [f] | C:4, T:4, H:1 | OPAQUE |
| shees | 9 | ciosu | H:3, A:2, B:2 | LOW |
| opar | 9 | epura | H:2, S:2, C:1 | LOW |
| opal | 9 | epuce | S:5, H:1, C:1 | LOW |
| oteeol | 9 | eons | S:4, H:2, Z:2 | OPAQUE |
| sheaiin | 8 | cioura | H:7, S:1 | LOW |
| koldy | 8 | eset | B:4, H:3, A:1 | LOW |
| arar | 8 | areara | Z:3, S:2, H:1 | LOW |
| shedar | 8 | ciodure | S:4, H:2, B:1 | LOW |
| sheety | 8 | ciole | B:6, P:1, S:1 | LOW |
| soraiin | 8 | usereure | S:4, H:2, T:1 | LOW |
| okaiir | 7 | quuir | H:2, S:2, T:1 | OPAQUE |
| q | 7 | [q] | H:6, T:1 | OPAQUE |
| ksho | 7 | ccie | H:7 | LOW |
| p | 7 | [p] | H:3, C:2, T:1 | OPAQUE |
| oteodar | 7 | toedura | Z:4, H:1, C:1 | LOW |
| osaiin | 7 | eusura | S:3, T:2, A:1 | LOW |
| ksheo | 6 | ccioe | H:5, Z:1 | LOW |
| kshey | 6 | ccio | H:3, B:2, C:1 | LOW |
| shoiin | 6 | cieura | H:5, T:1 | LOW |
| ytchol | 6 | inleiece | H:4, C:1, P:1 | LOW |
| okedal | 6 | quedus | S:3, H:1, Z:1 | LOW |
| okedar | 6 | quedure | B:3, S:2, H:1 | LOW |
| oteodaiin | 6 | toedeura | A:2, S:2, H:1 | LOW |
| oteodal | 6 | toeduce | Z:3, H:2, A:1 | LOW |
| okeod | 6 | queade | C:4, Z:1, P:1 | LOW |
| ykeeor | 6 | inquoer | H:2, S:2, Z:1 | LOW |

---
## 3. Longueur des mots opaques vs lisibles

| Longueur EVA | Lisibles | Opaques | % opaque |
|-------------|----------|---------|----------|
| 1 | 1177 | 282 | 19% |
| 2 | 2458 | 62 | 2% |
| 3 | 3481 | 128 | 3% |
| 4 | 6740 | 165 | 2% |
| 5 | 9024 | 436 | 4% |
| 6 | 6642 | 757 | 10% |
| 7 | 3642 | 686 | 15% |
| 8 | 1260 | 532 | 29% |
| 9 | 426 | 250 | 36% |
| 10 | 113 | 89 | 44% |
| 11 | 38 | 19 | 33% |
| 12 | 14 | 11 | 44% |
| 13 | 5 | 4 | 44% |
| 14 | 1 | 0 | 0% |

---
## 4. Patterns structurels des mots opaques

Classification par structure EVA (debut, fin, composition):

### Prefixes EVA des opaques (debut du mot)

| Prefixe | Count | Latin attendu |
|---------|-------|---------------|
| o | 1043 | e/a |
| sh | 541 | ci |
| a | 299 | u |
| y | 291 | in |
| s | 254 | us |
| k | 178 | c/qu |
| t | 168 | el |
| r | 88 | re |
| ct | 50 | ? |
| q | 45 | co/cum |
| e | 30 | ? |
| f | 27 | par |
| cp | 25 | ? |
| ck | 23 | ? |
| i | 8 | ? |
| cf | 4 | ? |
| z | 1 | ? |
| x | 1 | ? |
| j | 1 | ? |

### Suffixes EVA des opaques (fin du mot)

| Suffixe | Count |
|---------|-------|
| -aiin | 392 |
| -ar | 339 |
| -al | 285 |
| -ol | 206 |
| -ir | 197 |
| -ain | 180 |
| -ey | 162 |
| -or | 130 |
| -am | 103 |
| -iin | 76 |
| -od | 64 |
| -chy | 57 |
| -es | 52 |
| -ky | 51 |
| -hy | 50 |
| -ly | 50 |
| -os | 49 |
| -shy | 34 |
| -ed | 32 |
| -ho | 30 |

---
## 5. Contexte des mots opaques

### Mot AVANT un opaque (top 20)

| Mot precedent | Count | Interpretation |
|--------------|-------|----------------|
| aquam | 90 | |
| iure | 72 | |
| in aquam | 70 | |
| eius | 58 | |
| ac | 43 | |
| hiera | 42 | |
| eius et | 39 | |
| cum ede et | 38 | |
| coque | 35 | |
| cies | 34 | |
| cum aquam | 33 | |
| es | 32 | |
| in | 30 | |
| est | 28 | |
| alo | 28 | |
| ciere | 27 | |
| in iure | 27 | |
| ede et | 21 | |
| cibo et | 20 | |
| eo | 19 | |

### Mot APRES un opaque (top 20)

| Mot suivant | Count | Interpretation |
|------------|-------|----------------|
| aquam | 94 | |
| eius | 73 | |
| iure | 52 | |
| eius et | 51 | |
| cies | 50 | |
| in aquam | 45 | |
| in | 42 | |
| es | 39 | |
| cum aquam | 38 | |
| eo | 38 | |
| est | 36 | |
| hiera | 33 | |
| cibo et | 33 | |
| cum ede et | 32 | |
| ciere | 30 | |
| coque | 30 | |
| ac | 28 | |
| ede et | 27 | |
| alo | 26 | |
| recipe | 25 | |

### Confidence du contexte

| Mot avant (conf) | Count | Mot apres (conf) | Count |
|-----------------|-------|------------------|-------|
| CONFIRMED | 536 | CONFIRMED | 653 |
| HIGH | 1730 | HIGH | 1695 |
| MEDIUM | 31 | MEDIUM | 44 |
| LOW | 246 | LOW | 242 |
| OPAQUE | 41 | OPAQUE | 45 |

---
## 6. Position des opaques dans la ligne

| Position | Count | % |
|----------|-------|---|
| Milieu | 1477 | 43% |
| Premier mot | 837 | 24% |
| Mots 2-3 | 692 | 20% |
| Dernier mot | 415 | 12% |

---
## 7. Exemples detailles par section

### Section H (Herbal) — 944 opaques

- **f1v L01**: `l` -> `[l]` [OPAQUE]
  - Contexte: ...ac **[[l]]** el eius...
- **f1v L02**: `okodar` -> `quedure` [LOW]
  - Contexte: ...ex cade et **[quedure]** eius ede et...
  - Alternatives: quadure, aequedure, aequadure
- **f1v L03**: `ckhockhy` -> `aquieaqui` [LOW]
  - Contexte: ...aqui **[aquieaqui]** cibus...
  - Alternatives: quieaqui, aquiequi, aquiaqui
- **f1v L04**: `sochey` -> `sueio` [LOW]
  - Contexte: ...deum **[sueio]** eius quede et...
  - Alternatives: sueie, suaio, suaie
- **f1v L05**: `cphoal` -> `piaus` [LOW]
  - Contexte: ...in uira **[piaus]** in iure...
  - Alternatives: piaeus, piace, pieace
- **f1v L05**: `shoshy` -> `cieci` [LOW]
  - Contexte: ...taure **[cieci]** -...
  - Alternatives: ciaci
- **f1v L06**: `l` -> `[l]` [OPAQUE]
  - Contexte: ...elie **[[l]]** cies...
- **f1v L08**: `okolshol` -> `quesciece` [LOW]
  - Contexte: ...- **[quesciece]** cis...
  - Alternatives: quesciace, quasciece, quasciace
- **f2r L01**: `kydainy` -> `cndeain` [LOW]
  - Contexte: ...- **[cndeain]** in piece...
  - Alternatives: qundeain, cndeuin, qundeuin
- **f2r L01**: `ckholsy` -> `quieceus` [LOW]
  - Contexte: ...in piura **[quieceus]** -...
  - Alternatives: quiaceus, quiessu, quiassu
- **f2r L05**: `shodaiin` -> `ciedura` [LOW]
  - Contexte: ...alo **[ciedura]** eius...
  - Alternatives: ciadura, ciedeure, ciedeuram
- **f2r L05**: `ytchaiin` -> `inleiura` [LOW]
  - Contexte: ...dum **[inleiura]** dum...
  - Alternatives: inliure, inliuram, ineliare
- **f2r L08**: `kydain` -> `cndeain` [LOW]
  - Contexte: ...- **[cndeain]** ciura...
  - Alternatives: qundeain, cndain, qundain
- **f2r L10**: `e` -> `[e]` [OPAQUE]
  - Contexte: ...aquam **[[e]]** [a]...
- **f2r L10**: `a` -> `[a]` [OPAQUE]
  - Contexte: ...[e] **[[a]]** [iin]...

### Section S (Stars/Recettes) — 1070 opaques

- **f58r L01**: `shofchy` -> `ciepi` [LOW]
  - Contexte: ...eius espar **[ciepi]** tereusi...
  - Alternatives: ciefi, ciapi, ciafi
- **f58r L01**: `otoralchy` -> `tereusi` [LOW]
  - Contexte: ...ciepi **[tereusi]** eius epariens...
  - Alternatives: tareusi, tereasi, tareasi
- **f58r L02**: `olchokal` -> `esiquas` [LOW]
  - Contexte: ...in iure **[esiquas]** -...
  - Alternatives: esiaequas, asiquas, asiaequas
- **f58r L03**: `ykechod` -> `inquoiad` [LOW]
  - Contexte: ...- **[inquoiad]** in ususdum...
  - Alternatives: inqueiad, inquoiede, inquoiade
- **f58r L04**: `sholar` -> `ciesure` [LOW]
  - Contexte: ...deciere **[ciesure]** aquam...
  - Alternatives: ciasure, cieceura, ciaceura
- **f58r L04**: `shalom` -> `ciacem` [LOW]
  - Contexte: ...aquam **[ciacem]** cius...
  - Alternatives: ciaceam, ciucem, ciuceam
- **f58r L04**: `sholala` -> `cieceusu` [LOW]
  - Contexte: ...in alo **[cieceusu]** -...
  - Alternatives: ciaceusu, ciesasu, ciasasu
- **f58r L05**: `ytalar` -> `inelasure` [LOW]
  - Contexte: ...iure **[inelasure]** eius um...
  - Alternatives: ineluceure, inlusura, inelasura
- **f58r L07**: `sholteol` -> `cieseloece` [LOW]
  - Contexte: ...ciam **[cieseloece]** inelasede et...
  - Alternatives: cieseloace, cieselece, cieseleace
- **f58r L08**: `toleeshal` -> `elesociuce` [LOW]
  - Contexte: ...- **[elesociuce]** es eum...
  - Alternatives: elesoeciuce, eleseociuce, eleseciuce
- **f58r L08**: `oteodchy` -> `toedi` [LOW]
  - Contexte: ...in **[toedi]** in loei...
  - Alternatives: toedei, toadei, tedei
- **f58r L09**: `sholaiin` -> `cieceura` [LOW]
  - Contexte: ...- **[cieceura]** eius...
  - Alternatives: ciaceura, ciesure, ciesuram
- **f58r L09**: `yteodaiin` -> `ineloedeure` [LOW]
  - Contexte: ...eius **[ineloedeure]** cum iure...
  - Alternatives: ineloedeuram, ineloadeure, ineloadeuram
- **f58r L09**: `arary` -> `ureura` [LOW]
  - Contexte: ...aquam **[ureura]** ciere...
  - Alternatives: uraure, areare, urure
- **f58r L09**: `e` -> `[e]` [OPAQUE]
  - Contexte: ...in aquam **[[e]]** usum...

### Section B (Balnea) — 301 opaques

- **f75r L01**: `kchedykary` -> `ciodenqure` [LOW]
  - Contexte: ...- **[ciodenqure]** eo...
  - Alternatives: ciedenqure, quiodenqure, quiedenqure
- **f75r L02**: `ssheol` -> `sucioece` [LOW]
  - Contexte: ...ce **[sucioece]** cum sed et...
  - Alternatives: sucioace, suciece, sucieace
- **f75r L12**: `ssheckhy` -> `uscioaqui` [LOW]
  - Contexte: ...- **[uscioaqui]** cum curas...
  - Alternatives: uscieaqui, sucioqui, suciequi
- **f75r L14**: `keishy` -> `ecoici` [LOW]
  - Contexte: ...alo **[ecoici]** cum aquam...
  - Alternatives: eceici, coici, ceici
- **f75r L16**: `shokain` -> `ciequain` [LOW]
  - Contexte: ...si **[ciequain]** in...
  - Alternatives: ciaquain, ciaeaequin, ciaeaequain
- **f75r L17**: `shepchy` -> `ciobi` [LOW]
  - Contexte: ...per iodure **[ciobi]** ex ciodura...
  - Alternatives: ciebi, ciopei, ciepei
- **f75r L21**: `oqokain` -> `ecoquin` [LOW]
  - Contexte: ...- **[ecoquin]** eius...
  - Alternatives: ecoaequin, acoquin, acoaequin
- **f75r L23**: `kshey` -> `ccio` [LOW]
  - Contexte: ...per eius **[ccio]** coque...
  - Alternatives: ccie, qucio, qucie
- **f75r L27**: `shtol` -> `ciles` [LOW]
  - Contexte: ...per dusciere **[ciles]** cole...
  - Alternatives: cileace, cilece, cilace
- **f75r L28**: `oldair` -> `esdaire` [LOW]
  - Contexte: ...es **[esdaire]** cibolis...
  - Alternatives: asdaire, esdeuire, asdeuire
- **f75r L28**: `l` -> `[l]` [OPAQUE]
  - Contexte: ...cum ce **[[l]]** ciode et...
- **f75r L29**: `okeedyqol` -> `quodencoece` [LOW]
  - Contexte: ...es **[quodencoece]** in aquam...
  - Alternatives: quodencoace, quoedencoece, quoedencoace
- **f75r L33**: `l` -> `[l]` [OPAQUE]
  - Contexte: ...coque **[[l]]** cibo et...
- **f75r L35**: `sheety` -> `ciole` [LOW]
  - Contexte: ...cum aquam **[ciole]** cum aquam...
  - Alternatives: cioele, cieole, ciol
- **f75r L37**: `sheety` -> `ciole` [LOW]
  - Contexte: ...et **[ciole]** cum ede et...
  - Alternatives: cioele, cieole, ciol

### Section P (Pharma) — 270 opaques

- **f88r L01**: `otorchety` -> `tereioel` [OPAQUE]
  - Contexte: ...- **[tereioel]** -...
  - Alternatives: tereiel, tareioel, tareiel
- **f88r L03**: `orald` -> `ereusde` [LOW]
  - Contexte: ...- **[ereusde]** -...
  - Alternatives: areusde, ereucede, areucede
- **f88r L07**: `sholfchor` -> `ciespariere` [LOW]
  - Contexte: ...ciere **[ciespariere]** in alo...
  - Alternatives: ciespariare, ciesperiere, ciesperiare
- **f88r L08**: `shekor` -> `cioquer` [LOW]
  - Contexte: ...eius iure **[cioquer]** cum hiera...
  - Alternatives: cioquar, ciequer, ciequar
- **f88r L18**: `orchor` -> `ereier` [LOW]
  - Contexte: ...piens **[ereier]** per ioece...
  - Alternatives: ereiar, areier, areiar
- **f88r L18**: `salsaly` -> `sussuce` [LOW]
  - Contexte: ...es et **[sussuce]** -...
  - Alternatives: usususus, usususace, usuceusuce
- **f88r L21**: `sheoldg` -> `cioesdeg` [OPAQUE]
  - Contexte: ...ciens **[cioesdeg]** -...
  - Alternatives: cioesedg, cioasdeg, cioasedg
- **f88r L23**: `ofyskydal` -> `eparnuscnduce` [LOW]
  - Contexte: ...- **[eparnuscnduce]** -...
  - Alternatives: eparnusqunduce, epernuscnduce, epernusqunduce
- **f88r L25**: `ofaldo` -> `eparusde` [LOW]
  - Contexte: ...- **[eparusde]** -...
  - Alternatives: eparusda, eperusde, eperusda
- **f88r L30**: `ofal` -> `epuce` [LOW]
  - Contexte: ...eius eli **[epuce]** -...
  - Alternatives: efuce, apuce, afuce
- **f88v L01**: `okalyd` -> `alode` [LOW]
  - Contexte: ...- **[alode]** -...
  - Alternatives: quacende, aequacende, ucede
- **f88v L06**: `teodal` -> `eloedus` [LOW]
  - Contexte: ...- **[eloedus]** es ce...
  - Alternatives: eloadus, eledus, eleadus
- **f88v L06**: `roshckhy` -> `raeciaqui` [LOW]
  - Contexte: ...eius hiera **[raeciaqui]** userci...
  - Alternatives: raciaqui, raeciqui, reciaqui
- **f88v L06**: `sorshy` -> `userci` [LOW]
  - Contexte: ...raeciaqui **[userci]** aquam...
  - Alternatives: usarci, suereci, suareci
- **f88v L06**: `saldaiin` -> `usucedura` [LOW]
  - Contexte: ...eius oquans **[usucedura]** -...
  - Alternatives: usasdura, ususdure, ususduram

---
## 8. Hypotheses sur la nature des mots opaques

| Categorie | Count | % des opaques |
|-----------|-------|---------------|
| Combinaisons K&A inconnues | 1649 | 48% |
| Mots longs non attestes | 870 | 25% |
| Glyphes isoles (1-2 chars) | 344 | 10% |
| Prefixe IN + mot inconnu | 291 | 8% |
| T-trigger + mot inconnu | 251 | 7% |
| Splits -dy non resolus | 13 | 0% |
| Prefixe CUM + mot inconnu | 2 | 0% |
| Voyelles seules (pas de consonnes) | 1 | 0% |

---
## 9. Candidats noms de plantes / termes techniques

Mots opaques en premiere position de ligne dans les folios Herbal :

| Folio | Ligne | EVA | Decode | Mot suivant |
|-------|-------|-----|--------|-------------|
| f1v | L08 | okolshol | quesciece | cis |
| f2r | L01 | kydainy | cndeain | in piece |
| f2r | L08 | kydain | cndeain | ciura |
| f2r | L14 | ytoail | inelauis | - |
| f2v | L01 | kooiin | ceaure | eius oe |
| f3r | L01 | tsheos | elcioesu | cum perus |
| f3r | L06 | ychtaiin | inileura | iera |
| f3r | L12 | okadaiin | quadura | cum ciere |
| f3r | L15 | tsheoarom | elcioaurem | ciere |
| f3r | L17 | soeom | usaoem | quem |
| f3v | L09 | ytcheear | inelioure | quece |
| f4r | L01 | kodalchy | cedeusi | eius perude et |
| f4r | L12 | soiin | useura | eius aquam |
| f5v | L05 | shokeeol | ciquoece | iera |
| f6v | L18 | ytchocthol | inelieliece | eius os |
| f7r | L01 | fchodaiin | pariedeure | ciepio |
| f7r | L05 | oaiir | euir | aquam |
| f7r | L06 | ksholo | cciese | eius |
| f7v | L07 | okshodeeeb | quciedeob | eius ereioere |
| f8r | L09 | tchoep | lieoper | cibo |
| f8r | L13 | okokchodg | ququiedeg | - |
| f8v | L08 | okcholksh | quiescci | eius |
| f8v | L10 | scharchy | suiuri | eosuede et |
| f8v | L11 | sorain | usereain | - |
| f9r | L01 | tydlo | elndce | eius est |
| f9v | L08 | soiin | useura | in aquam |
| f10r | L09 | oykchor | enquier | ciere |
| f10r | L10 | oqotar | ecoelure | tere |
| f10r | L11 | otchoshor | tieciere | cole |
| f10v | L06 | shoiin | cieura | iera |