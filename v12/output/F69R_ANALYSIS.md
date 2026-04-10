# F69R ANALYSIS — Structure parallele a f57v

## 1. STRUCTURE COMPAREE f69r vs f57v

| Element | f57v | f69r |
|---------|------|------|
| Texte paragraphe | L02 (54 mots, @Cc) | P0 (4 lignes, @P0) |
| Cle/pattern | L03 (4x17, +Cc) | - |
| Labels anneau | L04 (29 mots, +Cc) | Sectors (16 labels, &L0) |
| Anneau rotatif | - | Hours (22 positions, @Ro) |
| Cercle concentrique | - | CC (1 ligne, @Cc) |
| Centre/labels | L06-L13 (8 labels) | - |
| **Glyphes isoles** | **9 (o,d,l,o,s,y,k,x,v)** | **6 (y,d,o,l,s,ed)** |

## 2. GLYPHES ISOLES — COMPARAISON DIRECTE

| Position f69r | Glyph | Aussi dans L04 ? | L04 decode |
|--------------|-------|-----------------|-----------|
| 44 (#1) | y | OUI | in |
| 45 (#2) | d | OUI | de |
| 46 (#3) | o | OUI | ac |
| 47 (#4) | l | OUI | [l] |
| 48 (#5) | s | OUI | est |
| 49 (#6) | ed | non | - |

**5/6 glyphes isoles de f69r sont les MEMES que ceux de L04** (y, d, o, l, s)
Le 6e (ed/eg) n'apparait pas dans L04.

**Les numeros <!1> a <!6> suggerent un ORDRE ou une NUMEROTATION.**
Si y=1, d=2, o=3, l=4, s=5, ed=6, alors les glyphes isoles
sont des CHIFFRES, pas des mots !

## 3. VOCABULAIRE PARTAGE f69r ↔ L04

Mots L04: 27 uniques
Mots f69r: 120 uniques
**Partages: ['aiin', 'daiin', 'dal', 'otal']** (4 mots)

  `aiin`: L04 j[26] ↔ f69r ['P0.3']
  `daiin`: L04 j[1, 25] ↔ f69r ['P0.2', 'Sector.19']
  `dal`: L04 j[24] ↔ f69r ['Sector.19', 'Hour.25(11:30)', 'Hour.26(00:00)', 'Hour.33(04:00)']
  `otal`: L04 j[27] ↔ f69r ['P0.1']

## 4. ANNEAU DES HEURES (f69r.21-42)

f69r a un anneau avec des marqueurs d'HEURE (09:15 a 08:45).
C'est un CADRAN — probablement horaire.

| Pos | Heure | Texte | Mots partages L04 |
|-----|-------|-------|-------------------|
| 21 | 09:15 | chodchy.chotal                      | - |
| 22 | 10:00 | okeo.sho.qotam                      | - |
| 23 | 10:30 | okeodar.oteody                      | - |
| 24 | 11:00 | ykeeos.al.dair.dar                  | - |
| 25 | 11:30 | ykeey.dal.oky                       | dal |
| 26 | 00:00 | doly.dal.dar.chyky                  | dal |
| 27 | 00:30 | okchol.qokol.daly                   | - |
| 28 | 01:00 | ykechody.otar                       | - |
| 29 | 01:30 | dary.dar.aloly                      | - |
| 30 | 02:30 | okeeocthy.okar.ar                   | - |
| 31 | 03:00 | chey.ar.cthorary                    | - |
| 32 | 03:30 | sair.chekey.sairam                  | - |
| 33 | 04:00 | okeeo.dal.okar.ar                   | dal |
| 34 | 05:00 | sol.aiir.okeytam                    | - |
| 35 | 05:30 | okeos.ar.ald                        | - |
| 36 | 05:45 | docheeo.kody.sar                    | - |
| 37 | 06:15 | dchokey.shkchodyal                  | - |
| 38 | 06:45 | chor.al.alchy.ral                   | - |
| 39 | 07:00 | sair.al.okody.otedy                 | - |
| 40 | 07:30 | okody.cheody.sar                    | - |
| 41 | 08:00 | chokeod.okeey                       | - |
| 42 | 08:45 | dkochy.cthody.dy                    | - |

## 5. LABELS DE SECTEUR (f69r.5-20) — Decode pipeline

| Pos | Texte | Mots | Pipeline decode |
|-----|-------|------|----------------|
| 5 | oteos.chop.otaeky              | 3 | aloes eius aper taequ |
| 6 | ar.odair.chtaly                | 3 | iure edaire aceti |
| 7 | oto.dar.archol                 | 3 | ele in iure asari |
| 8 | okeey.cheydy                   | 2 | eo eius onde et |
| 9 | dcho.char.ar                   | 3 | in ia iure iure |
| 10 | ytal.air.al                    | 3 | in luce aquare alo |
| 11 | shy.chtairy                    | 2 | cibus eius eluire |
| 12 | yt.oetear                      | 2 | inl aoeloura |
| 13 | ytey.cholam                    | 2 | in le eius esum |
| 14 | dair.ar.yteey.chdy             | 4 | in uira iure in eleo eius et |
| 15 | okair.os.air                   | 3 | iecur aus aquare |
| 16 | chytos.aly                     | 2 | eius ineles alo |
| 17 | chetar.araly                   | 2 | eius oelure areace |
| 18 | dair.alody                     | 2 | in uira used |
| 19 | dal.daiin.otalam               | 3 | in alo in aquam usum |
| 20 | ytcheodytor                    | 1 | inelioedenelere |

## 6. LE PONT : `dal.daiin` dans les deux

f69r.19 = `dal.daiin.otalam`
L04 j24-j25 = `dal` + [@172] + `daiin`

Le meme bigram `dal.daiin` apparait dans les DEUX instruments !
En K&A: `dal` = in alo (dans l'aloes) + `daiin` = in aquam (dans l'eau)
Suivi de `otalam`/`otal` qui decodent similairement (sal/tus)

## 7. FREQUENCE DE GLYPHES f69r vs L04 vs VMS

| Glyph | f69r% | L04% | Diff | Note |
|-------|-------|------|------|------|
| a | 11.8% | 10.6% | -1.2 |  |
| c | 6.7% | 1.9% | -4.8 |  |
| d | 6.0% | 11.5% | +5.6 | *** |
| e | 9.8% | 16.3% | +6.5 | *** |
| f | 0.0% | 1.9% | +1.9 |  |
| h | 8.3% | 2.9% | -5.4 | *** |
| i | 4.4% | 7.7% | +3.3 |  |
| k | 5.3% | 4.8% | -0.5 |  |
| l | 5.0% | 5.8% | +0.8 |  |
| m | 1.0% | 0.0% | -1.0 |  |
| n | 1.1% | 3.8% | +2.7 |  |
| o | 13.2% | 12.5% | -0.7 |  |
| p | 0.3% | 0.0% | -0.3 |  |
| q | 0.4% | 0.0% | -0.4 |  |
| r | 6.7% | 4.8% | -1.9 |  |
| s | 4.0% | 3.8% | -0.1 |  |
| t | 5.3% | 3.8% | -1.4 |  |
| v | 0.0% | 1.9% | +1.9 |  |
| x | 0.0% | 1.0% | +1.0 |  |
| y | 10.7% | 4.8% | -5.9 | *** |

**Distance Manhattan f69r-L04: 0.473**

## 8. SYNTHESE

### f69r et f57v sont des INSTRUMENTS PARALLELES

Points communs :
1. Glyphes isoles IDENTIQUES (y, d, o, l, s)
2. Vocabulaire partage (dal, daiin, otal, etc.)
3. Structure circulaire/concentrique
4. Labels fonctionnels sur des anneaux

Differences :
1. f69r a des marqueurs d'HEURE (cadran horaire)
2. f57v a la cle L03 (4x17 pattern)
3. f69r a 16 secteurs (pas 29)
4. f69r a 22 positions horaires (pas 29)

### LES GLYPHES ISOLES SONT DES CHIFFRES

Sur f69r, les glyphes isoles ont des NUMEROS explicites :
y=1, d=2, o=3, l=4, s=5, ed=6

Si ce systeme s'applique aussi a L04 de f57v :
| Pos L04 | Glyph | = Chiffre | Ancien decode K&A |
|---------|-------|-----------|-------------------|
| 5 | o | **3** | ac |
| 6 | d | **2** | de |
| 8 | l | **4** | [l] |
| 9 | o | **3** | ac |
| 14 | s | **5** | est |
| 15 | y | **1** | in |
| 17 | k | **?** | [k] (pas dans f69r) |
| 19 | x | **?** | crux (pas dans f69r) |
| 29 | v | **?** | vel (pas dans f69r) |

Les 6 premiers (y=1 a ed=6) couvrent 6 positions.
k, x, v pourraient etre 7, 8, 9 ou des valeurs speciales.
