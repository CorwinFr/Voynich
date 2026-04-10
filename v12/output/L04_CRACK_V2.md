# L04 CRACK V2 — Tokenisation EVA correcte

## 1. TOKENISATION — Longueurs reelles des mots

| Pos | EVA | Chars | Tokens | Tokenized |
|-----|-----|-------|--------|-----------|
|  1 | daiin      |     5 |      2 | d aiin |
|  2 | otey       |     4 |      4 | o t e y |
|  3 | ofeeey     |     6 |      4 | o f eee y |
|  4 | shes       |     4 |      3 | sh e s |
|  5 | o          |     1 |      1 | o |
|  6 | d          |     1 |      1 | d |
|  7 | okeeod     |     6 |      5 | o k ee o d |
|  8 | l          |     1 |      1 | l |
|  9 | o          |     1 |      1 | o |
| 10 | lkeeol     |     6 |      5 | l k ee o l |
| 11 | dkedar     |     6 |      6 | d k e d a r |
| 12 | yf         |     2 |      2 | y f |
| 13 | aros       |     4 |      4 | a r o s |
| 14 | s          |     1 |      1 | s |
| 15 | y          |     1 |      1 | y |
| 16 | chedaiin   |     8 |      4 | ch e d aiin |
| 17 | k          |     1 |      1 | k |
| 18 | eeety      |     5 |      3 | eee t y |
| 19 | x          |     1 |      1 | x |
| 20 | deeodal    |     7 |      6 | d ee o d a l |
| 21 | vo         |     2 |      2 | v o |
| 22 | tchor      |     5 |      4 | t ch o r |
| 23 | kedar      |     5 |      5 | k e d a r |
| 24 | dal        |     3 |      3 | d a l |
| 25 | daiin      |     5 |      2 | d aiin |
| 26 | aiin       |     4 |      1 | aiin |
| 27 | otal       |     4 |      4 | o t a l |
| 28 | daro       |     4 |      4 | d a r o |
| 29 | v          |     1 |      1 | v |

**Tokens uniques : 18**
Token list: ['o', 'd', 'a', 'l', 'e', 'y', 'k', 'r', 'aiin', 't', 's', 'ee', 'f', 'eee', 'ch', 'v', 'sh', 'x']
Total tokens: 82

| Token | Count | % |
|-------|-------|---|
| o     |    13 | 15.9% |
| d     |    12 | 14.6% |
| a     |     7 | 8.5% |
| l     |     6 | 7.3% |
| e     |     5 | 6.1% |
| y     |     5 | 6.1% |
| k     |     5 | 6.1% |
| r     |     5 | 6.1% |
| aiin  |     4 | 4.9% |
| t     |     4 | 4.9% |
| s     |     3 | 3.7% |
| ee    |     3 | 3.7% |
| f     |     2 | 2.4% |
| eee   |     2 | 2.4% |
| ch    |     2 | 2.4% |
| v     |     2 | 2.4% |
| sh    |     1 | 1.2% |
| x     |     1 | 1.2% |

## 2. CORRESPONDANCES PAR LONGUEUR (tokens)

| Pos | EVA | Tok | Targets meme longueur |
|-----|-----|-----|----------------------|
|  1 | daiin      |   2 |  |
|  2 | otey       |   4 | ruta(hM2), aloe(hM10), anus(bM15), rosa(hM16), crus(bM19), genu(bM22), batn(nM28) |
|  3 | ofeeey     |   4 | ruta(hM2), aloe(hM10), anus(bM15), rosa(hM16), crus(bM19), genu(bM22), batn(nM28) |
|  4 | shes       |   3 | pes(bM28), cor(lM18), tus(hM21) |
|  7 | okeeod     |   5 | horns(nM1), caput(bM1), tauri(lM4), hanna(nM6), dirah(nM7), atarf(nM9), tartf(nM9), frons(lM10), cauda(lM19), costa(bM11) |
| 10 | lkeeol     |   5 | horns(nM1), caput(bM1), tauri(lM4), hanna(nM6), dirah(nM7), atarf(nM9), tartf(nM9), frons(lM10), cauda(lM19), costa(bM11) |
| 11 | dkedar     |   6 | alnath(nM1), alnach(nM1), alvach(nM1), cornua(lM16), venter(bM13), soraya(nM3), mastix(hM6), oculus(lM9), agatha(sM5), signum(lM5) |
| 12 | yf         |   2 |  |
| 13 | aros       |   4 | ruta(hM2), aloe(hM10), anus(bM15), rosa(hM16), crus(bM19), genu(bM22), batn(nM28) |
| 16 | chedaiin   |   4 | ruta(hM2), aloe(hM10), anus(bM15), rosa(hM16), crus(bM19), genu(bM22), batn(nM28) |
| 18 | eeety      |   3 | pes(bM28), cor(lM18), tus(hM21) |
| 20 | deeodal    |   6 | alnath(nM1), alnach(nM1), alvach(nM1), cornua(lM16), venter(bM13), soraya(nM3), mastix(hM6), oculus(lM9), agatha(sM5), signum(lM5) |
| 21 | vo         |   2 |  |
| 22 | tchor      |   4 | ruta(hM2), aloe(hM10), anus(bM15), rosa(hM16), crus(bM19), genu(bM22), batn(nM28) |
| 23 | kedar      |   5 | horns(nM1), caput(bM1), tauri(lM4), hanna(nM6), dirah(nM7), atarf(nM9), tartf(nM9), frons(lM10), cauda(lM19), costa(bM11) |
| 24 | dal        |   3 | pes(bM28), cor(lM18), tus(hM21) |
| 25 | daiin      |   2 |  |
| 26 | aiin       |   1 |  |
| 27 | otal       |   4 | ruta(hM2), aloe(hM10), anus(bM15), rosa(hM16), crus(bM19), genu(bM22), batn(nM28) |
| 28 | daro       |   4 | ruta(hM2), aloe(hM10), anus(bM15), rosa(hM16), crus(bM19), genu(bM22), batn(nM28) |

## 3. CRIB DRAG — Substitution token→lettre

Total cribs testes: 80
**Cribs avec cascade > 0: 80**

### j11 `dkedar` = `alnath` (name M1) *** CASCADE ***
  Mapping: {'d': 'a', 'k': 'l', 'e': 'n', 'a': 't', 'r': 'h'}
  Cascade: 1
  j11 dkedar     -> alnath <<<
  j23 kedar      -> lnath

### j11 `dkedar` = `alnach` (name M1) *** CASCADE ***
  Mapping: {'d': 'a', 'k': 'l', 'e': 'n', 'a': 'c', 'r': 'h'}
  Cascade: 1
  j11 dkedar     -> alnach <<<
  j23 kedar      -> lnach

### j11 `dkedar` = `alvach` (name M1) *** CASCADE ***
  Mapping: {'d': 'a', 'k': 'l', 'e': 'v', 'a': 'c', 'r': 'h'}
  Cascade: 1
  j11 dkedar     -> alvach <<<
  j23 kedar      -> lvach

### j11 `dkedar` = `crocus` (herb M17) *** CASCADE ***
  Mapping: {'d': 'c', 'k': 'r', 'e': 'o', 'a': 'u', 'r': 's'}
  Cascade: 1
  j11 dkedar     -> crocus <<<
  j23 kedar      -> rocus

### j11 `dkedar` = `algarf` (name M27) *** CASCADE ***
  Mapping: {'d': 'a', 'k': 'l', 'e': 'g', 'a': 'r', 'r': 'f'}
  Cascade: 1
  j11 dkedar     -> algarf <<<
  j23 kedar      -> lgarf

### j20 `deeodal` = `alnath` (name M1) *** CASCADE ***
  Mapping: {'d': 'a', 'ee': 'l', 'o': 'n', 'a': 't', 'l': 'h'}
  Cascade: 1
  j20 deeodal    -> alnath <<<
  j24 dal        -> ath

### j20 `deeodal` = `alnach` (name M1) *** CASCADE ***
  Mapping: {'d': 'a', 'ee': 'l', 'o': 'n', 'a': 'c', 'l': 'h'}
  Cascade: 1
  j20 deeodal    -> alnach <<<
  j24 dal        -> ach

### j20 `deeodal` = `alvach` (name M1) *** CASCADE ***
  Mapping: {'d': 'a', 'ee': 'l', 'o': 'v', 'a': 'c', 'l': 'h'}
  Cascade: 1
  j20 deeodal    -> alvach <<<
  j24 dal        -> ach

### j20 `deeodal` = `crocus` (herb M17) *** CASCADE ***
  Mapping: {'d': 'c', 'ee': 'r', 'o': 'o', 'a': 'u', 'l': 's'}
  Cascade: 1
  j20 deeodal    -> crocus <<<
  j24 dal        -> cus

### j20 `deeodal` = `algarf` (name M27) *** CASCADE ***
  Mapping: {'d': 'a', 'ee': 'l', 'o': 'g', 'a': 'r', 'l': 'f'}
  Cascade: 1
  j20 deeodal    -> algarf <<<
  j24 dal        -> arf

### j23 `kedar` = `horns` (name M1) *** CASCADE ***
  Mapping: {'k': 'h', 'e': 'o', 'd': 'r', 'a': 'n', 'r': 's'}
  Cascade: 1
  j11 dkedar     -> rhorns
  j23 kedar      -> horns <<<

### j23 `kedar` = `caput` (body M1) *** CASCADE ***
  Mapping: {'k': 'c', 'e': 'a', 'd': 'p', 'a': 'u', 'r': 't'}
  Cascade: 1
  j11 dkedar     -> pcaput
  j23 kedar      -> caput <<<

### j23 `kedar` = `tauri` (latin_desc M4) *** CASCADE ***
  Mapping: {'k': 't', 'e': 'a', 'd': 'u', 'a': 'r', 'r': 'i'}
  Cascade: 1
  j11 dkedar     -> utauri
  j23 kedar      -> tauri <<<

### j23 `kedar` = `dirah` (name M7) *** CASCADE ***
  Mapping: {'k': 'd', 'e': 'i', 'd': 'r', 'a': 'a', 'r': 'h'}
  Cascade: 1
  j11 dkedar     -> rdirah
  j23 kedar      -> dirah <<<

### j23 `kedar` = `frons` (latin_desc M10) *** CASCADE ***
  Mapping: {'k': 'f', 'e': 'r', 'd': 'o', 'a': 'n', 'r': 's'}
  Cascade: 1
  j11 dkedar     -> ofrons
  j23 kedar      -> frons <<<

### j23 `kedar` = `costa` (body M11) *** CASCADE ***
  Mapping: {'k': 'c', 'e': 'o', 'd': 's', 'a': 't', 'r': 'a'}
  Cascade: 1
  j11 dkedar     -> scosta
  j23 kedar      -> costa <<<

### j23 `kedar` = `spica` (latin_desc M13) *** CASCADE ***
  Mapping: {'k': 's', 'e': 'p', 'd': 'i', 'a': 'c', 'r': 'a'}
  Cascade: 1
  j11 dkedar     -> ispica
  j23 kedar      -> spica <<<

### j23 `kedar` = `simak` (name M14) *** CASCADE ***
  Mapping: {'k': 's', 'e': 'i', 'd': 'm', 'a': 'a', 'r': 'k'}
  Cascade: 1
  j11 dkedar     -> msimak
  j23 kedar      -> simak <<<

### j23 `kedar` = `nates` (body M17) *** CASCADE ***
  Mapping: {'k': 'n', 'e': 'a', 'd': 't', 'a': 'e', 'r': 's'}
  Cascade: 1
  j11 dkedar     -> tnates
  j23 kedar      -> nates <<<

### j23 `kedar` = `femur` (body M20) *** CASCADE ***
  Mapping: {'k': 'f', 'e': 'e', 'd': 'm', 'a': 'u', 'r': 'r'}
  Cascade: 1
  j11 dkedar     -> mfemur
  j23 kedar      -> femur <<<

### j2 `otey` = `ruta` (herb M2) *** CASCADE ***
  Mapping: {'o': 'r', 't': 'u', 'e': 't', 'y': 'a'}
  Cascade: 1
  j 2 otey       -> ruta <<<

### j2 `otey` = `aloe` (herb M10) *** CASCADE ***
  Mapping: {'o': 'a', 't': 'l', 'e': 'o', 'y': 'e'}
  Cascade: 1
  j 2 otey       -> aloe <<<

### j2 `otey` = `anus` (body M15) *** CASCADE ***
  Mapping: {'o': 'a', 't': 'n', 'e': 'u', 'y': 's'}
  Cascade: 1
  j 2 otey       -> anus <<<

### j2 `otey` = `rosa` (herb M16) *** CASCADE ***
  Mapping: {'o': 'r', 't': 'o', 'e': 's', 'y': 'a'}
  Cascade: 1
  j 2 otey       -> rosa <<<

### j2 `otey` = `crus` (body M19) *** CASCADE ***
  Mapping: {'o': 'c', 't': 'r', 'e': 'u', 'y': 's'}
  Cascade: 1
  j 2 otey       -> crus <<<

### j2 `otey` = `genu` (body M22) *** CASCADE ***
  Mapping: {'o': 'g', 't': 'e', 'e': 'n', 'y': 'u'}
  Cascade: 1
  j 2 otey       -> genu <<<

### j2 `otey` = `batn` (name M28) *** CASCADE ***
  Mapping: {'o': 'b', 't': 'a', 'e': 't', 'y': 'n'}
  Cascade: 1
  j 2 otey       -> batn <<<

### j3 `ofeeey` = `ruta` (herb M2) *** CASCADE ***
  Mapping: {'o': 'r', 'f': 'u', 'eee': 't', 'y': 'a'}
  Cascade: 1
  j 3 ofeeey     -> ruta <<<
  j12 yf         -> au

### j3 `ofeeey` = `aloe` (herb M10) *** CASCADE ***
  Mapping: {'o': 'a', 'f': 'l', 'eee': 'o', 'y': 'e'}
  Cascade: 1
  j 3 ofeeey     -> aloe <<<
  j12 yf         -> el

### j3 `ofeeey` = `anus` (body M15) *** CASCADE ***
  Mapping: {'o': 'a', 'f': 'n', 'eee': 'u', 'y': 's'}
  Cascade: 1
  j 3 ofeeey     -> anus <<<
  j12 yf         -> sn

### j3 `ofeeey` = `rosa` (herb M16) *** CASCADE ***
  Mapping: {'o': 'r', 'f': 'o', 'eee': 's', 'y': 'a'}
  Cascade: 1
  j 3 ofeeey     -> rosa <<<
  j12 yf         -> ao

### j3 `ofeeey` = `crus` (body M19) *** CASCADE ***
  Mapping: {'o': 'c', 'f': 'r', 'eee': 'u', 'y': 's'}
  Cascade: 1
  j 3 ofeeey     -> crus <<<
  j12 yf         -> sr

### j3 `ofeeey` = `genu` (body M22) *** CASCADE ***
  Mapping: {'o': 'g', 'f': 'e', 'eee': 'n', 'y': 'u'}
  Cascade: 1
  j 3 ofeeey     -> genu <<<
  j12 yf         -> ue

### j3 `ofeeey` = `batn` (name M28) *** CASCADE ***
  Mapping: {'o': 'b', 'f': 'a', 'eee': 't', 'y': 'n'}
  Cascade: 1
  j 3 ofeeey     -> batn <<<
  j12 yf         -> na

### j7 `okeeod` = `tartf` (name M9) *** CASCADE ***
  Mapping: {'o': 't', 'k': 'a', 'ee': 'r', 'd': 'f'}
  Cascade: 1
  j 7 okeeod     -> tartf <<<

### j7 `okeeod` = `tecta` (latin_desc M15) *** CASCADE ***
  Mapping: {'o': 't', 'k': 'e', 'ee': 'c', 'd': 'a'}
  Cascade: 1
  j 7 okeeod     -> tecta <<<

### j13 `aros` = `ruta` (herb M2) *** CASCADE ***
  Mapping: {'a': 'r', 'r': 'u', 'o': 't', 's': 'a'}
  Cascade: 1
  j13 aros       -> ruta <<<

### j13 `aros` = `aloe` (herb M10) *** CASCADE ***
  Mapping: {'a': 'a', 'r': 'l', 'o': 'o', 's': 'e'}
  Cascade: 1
  j13 aros       -> aloe <<<

### j13 `aros` = `anus` (body M15) *** CASCADE ***
  Mapping: {'a': 'a', 'r': 'n', 'o': 'u', 's': 's'}
  Cascade: 1
  j13 aros       -> anus <<<

### j13 `aros` = `rosa` (herb M16) *** CASCADE ***
  Mapping: {'a': 'r', 'r': 'o', 'o': 's', 's': 'a'}
  Cascade: 1
  j13 aros       -> rosa <<<

## 4. CONTRAINTES CROISEES — Memes tokens dans differents mots

| Token | Occurrences | Mots | Position dans mot |
|-------|-------------|------|-------------------|
| o     |          11 | j2[0], j3[0], j7[0], j7[3], j10[3], j13[2], j20[2], j21[1], j22[2], j27[0], j28[3] |  |
| d     |          11 | j1[0], j7[4], j11[0], j11[3], j16[2], j20[0], j20[3], j23[2], j24[0], j25[0], j28[0] |  |
| a     |           7 | j11[4], j13[0], j20[4], j23[3], j24[1], j27[2], j28[1] |  |
| l     |           5 | j10[0], j10[4], j20[5], j24[2], j27[3] |  |
| e     |           5 | j2[2], j4[1], j11[2], j16[1], j23[1] |  |
| y     |           4 | j2[3], j3[3], j12[0], j18[2] |  |
| k     |           4 | j7[1], j10[1], j11[1], j23[0] |  |
| r     |           5 | j11[5], j13[1], j22[3], j23[4], j28[2] |  |
| aiin  |           4 | j1[1], j16[3], j25[1], j26[0] |  |
| t     |           4 | j2[1], j18[1], j22[0], j27[1] |  |
| s     |           2 | j4[2], j13[3] |  |
| ee    |           3 | j7[2], j10[2], j20[1] |  |
| f     |           2 | j3[1], j12[1] |  |
| eee   |           2 | j3[2], j18[0] |  |
| ch    |           2 | j16[0], j22[1] |  |

## 5. MAPPING PAR FREQUENCE (tokens)

Frequency mapping: {'o': 'a', 'd': 'l', 'a': 'h', 'l': 'r', 'e': 'e', 'y': 'b', 'k': 'd', 'r': 'c', 'aiin': 'i', 't': 'n', 's': 't', 'ee': 'm', 'f': 'o', 'eee': 'z', 'ch': 'y', 'v': 'f', 'sh': 'g', 'x': 's'}

| Pos | EVA | Tokens | Freq-decoded |
|-----|-----|--------|-------------|
|  1 | daiin      | d aiin          | li |
|  2 | otey       | o t e y         | aneb |
|  3 | ofeeey     | o f eee y       | aozb |
|  4 | shes       | sh e s          | get |
|  5 | o          | o               | a |
|  6 | d          | d               | l |
|  7 | okeeod     | o k ee o d      | admal |
|  8 | l          | l               | r |
|  9 | o          | o               | a |
| 10 | lkeeol     | l k ee o l      | rdmar |
| 11 | dkedar     | d k e d a r     | ldelhc |
| 12 | yf         | y f             | bo |
| 13 | aros       | a r o s         | hcat |
| 14 | s          | s               | t |
| 15 | y          | y               | b |
| 16 | chedaiin   | ch e d aiin     | yeli |
| 17 | k          | k               | d |
| 18 | eeety      | eee t y         | znb |
| 19 | x          | x               | s |
| 20 | deeodal    | d ee o d a l    | lmalhr |
| 21 | vo         | v o             | fa |
| 22 | tchor      | t ch o r        | nyac |
| 23 | kedar      | k e d a r       | delhc |
| 24 | dal        | d a l           | lhr |
| 25 | daiin      | d aiin          | li |
| 26 | aiin       | aiin            | i |
| 27 | otal       | o t a l         | anhr |
| 28 | daro       | d a r o         | lhca |
| 29 | v          | v               | f |

## 6. MAPPING PAR FREQUENCE (herbes)

Herb frequency mapping: {'o': 'a', 'd': 'i', 'a': 's', 'l': 'o', 'e': 'u', 'y': 'r', 'k': 'm', 'r': 't', 'aiin': 'c', 't': 'n', 's': 'p', 'ee': 'l', 'f': 'h', 'eee': 'e', 'ch': 'g', 'v': 'b', 'sh': 'd', 'x': 'x'}

| Pos | EVA | Freq-decoded (herbs) |
|-----|-----|---------------------|
|  1 | daiin      | ic |
|  2 | otey       | anur |
|  3 | ofeeey     | aher |
|  4 | shes       | dup |
|  5 | o          | a |
|  6 | d          | i |
|  7 | okeeod     | amlai |
|  8 | l          | o |
|  9 | o          | a |
| 10 | lkeeol     | omlao |
| 11 | dkedar     | imuist |
| 12 | yf         | rh |
| 13 | aros       | stap |
| 14 | s          | p |
| 15 | y          | r |
| 16 | chedaiin   | guic |
| 17 | k          | m |
| 18 | eeety      | enr |
| 19 | x          | x |
| 20 | deeodal    | ilaiso |
| 21 | vo         | ba |
| 22 | tchor      | ngat |
| 23 | kedar      | muist |
| 24 | dal        | iso |
| 25 | daiin      | ic |
| 26 | aiin       | c |
| 27 | otal       | anso |
| 28 | daro       | ista |
| 29 | v          | b |

## 7. CRIB SPECIFIQUE — `daiin` (j1, j25) = ?

`daiin` apparait 2 fois (j1, j25). Tokens: ['d', 'aiin']

---
## BILAN

**80 CRIBS AVEC CASCADE TROUVEES !**
- j11 `dkedar` = `alnath` (cascade=1)
- j11 `dkedar` = `alnach` (cascade=1)
- j11 `dkedar` = `alvach` (cascade=1)
- j11 `dkedar` = `crocus` (cascade=1)
- j11 `dkedar` = `algarf` (cascade=1)
- j20 `deeodal` = `alnath` (cascade=1)
- j20 `deeodal` = `alnach` (cascade=1)
- j20 `deeodal` = `alvach` (cascade=1)
- j20 `deeodal` = `crocus` (cascade=1)
- j20 `deeodal` = `algarf` (cascade=1)
- j23 `kedar` = `horns` (cascade=1)
- j23 `kedar` = `caput` (cascade=1)
- j23 `kedar` = `tauri` (cascade=1)
- j23 `kedar` = `dirah` (cascade=1)
- j23 `kedar` = `frons` (cascade=1)
- j23 `kedar` = `costa` (cascade=1)
- j23 `kedar` = `spica` (cascade=1)
- j23 `kedar` = `simak` (cascade=1)
- j23 `kedar` = `nates` (cascade=1)
- j23 `kedar` = `femur` (cascade=1)
- j2 `otey` = `ruta` (cascade=1)
- j2 `otey` = `aloe` (cascade=1)
- j2 `otey` = `anus` (cascade=1)
- j2 `otey` = `rosa` (cascade=1)
- j2 `otey` = `crus` (cascade=1)
- j2 `otey` = `genu` (cascade=1)
- j2 `otey` = `batn` (cascade=1)
- j3 `ofeeey` = `ruta` (cascade=1)
- j3 `ofeeey` = `aloe` (cascade=1)
- j3 `ofeeey` = `anus` (cascade=1)
- j3 `ofeeey` = `rosa` (cascade=1)
- j3 `ofeeey` = `crus` (cascade=1)
- j3 `ofeeey` = `genu` (cascade=1)
- j3 `ofeeey` = `batn` (cascade=1)
- j7 `okeeod` = `tartf` (cascade=1)
- j7 `okeeod` = `tecta` (cascade=1)
- j13 `aros` = `ruta` (cascade=1)
- j13 `aros` = `aloe` (cascade=1)
- j13 `aros` = `anus` (cascade=1)
- j13 `aros` = `rosa` (cascade=1)
- j13 `aros` = `crus` (cascade=1)
- j13 `aros` = `genu` (cascade=1)
- j13 `aros` = `batn` (cascade=1)
- j16 `chedaiin` = `ruta` (cascade=1)
- j16 `chedaiin` = `aloe` (cascade=1)
- j16 `chedaiin` = `anus` (cascade=1)
- j16 `chedaiin` = `rosa` (cascade=1)
- j16 `chedaiin` = `crus` (cascade=1)
- j16 `chedaiin` = `genu` (cascade=1)
- j16 `chedaiin` = `batn` (cascade=1)
- j22 `tchor` = `ruta` (cascade=1)
- j22 `tchor` = `aloe` (cascade=1)
- j22 `tchor` = `anus` (cascade=1)
- j22 `tchor` = `rosa` (cascade=1)
- j22 `tchor` = `crus` (cascade=1)
- j22 `tchor` = `genu` (cascade=1)
- j22 `tchor` = `batn` (cascade=1)
- j27 `otal` = `ruta` (cascade=1)
- j27 `otal` = `aloe` (cascade=1)
- j27 `otal` = `anus` (cascade=1)
- j27 `otal` = `rosa` (cascade=1)
- j27 `otal` = `crus` (cascade=1)
- j27 `otal` = `genu` (cascade=1)
- j27 `otal` = `batn` (cascade=1)
- j28 `daro` = `ruta` (cascade=1)
- j28 `daro` = `aloe` (cascade=1)
- j28 `daro` = `anus` (cascade=1)
- j28 `daro` = `rosa` (cascade=1)
- j28 `daro` = `crus` (cascade=1)
- j28 `daro` = `genu` (cascade=1)
- j28 `daro` = `batn` (cascade=1)
- j4 `shes` = `pes` (cascade=1)
- j4 `shes` = `cor` (cascade=1)
- j4 `shes` = `tus` (cascade=1)
- j18 `eeety` = `pes` (cascade=1)
- j18 `eeety` = `cor` (cascade=1)
- j18 `eeety` = `tus` (cascade=1)
- j24 `dal` = `pes` (cascade=1)
- j24 `dal` = `cor` (cascade=1)
- j24 `dal` = `tus` (cascade=1)