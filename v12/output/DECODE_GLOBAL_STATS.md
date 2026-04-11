# DECODE GLOBAL — Statistiques recettes f103r-f116r
# Pipeline V2 (variants + dual + rules)
# Date: 2026-04-11

## VUE D ENSEMBLE

Total mots decodes: 10893
Folios traites: 24
Ingredients identifies: 141
Anomalies totales: 876

## DISTRIBUTION DES TYPES

| Type | Count | % | Description |
|------|-------|---|-------------|
| func | 4242 | 38% | Fonction |
| INGR | 3646 | 33% | Ingredient (K&A) |
| logo | 1897 | 17% | Logogram (table) |
| DOSE | 794 | 7% | Dosage (quantite) |
| VERB | 270 | 2% | Verbe pharma |
| MIX | 44 | 0% | Mixte |

Ratio VERB:INGR = 1:13.5

## PAR FOLIO

| Folio | Mots | Ingredients | Anomalies | Variants |
|-------|------|------------|-----------|----------|
| f103r | 532 | 37 | 39 | 99 | <<<
| f103v | 454 | 31 | 32 | 78 | <<<
| f104r | 448 | 32 | 44 | 105 | <<<
| f104v | 476 | 35 | 26 | 125 | <<<
| f105r | 379 | 34 | 32 | 66 | <<<
| f105v | 398 | 39 | 55 | 96 | <<<
| f106r | 432 | 34 | 27 | 94 | <<<
| f106v | 444 | 40 | 34 | 98 | <<<
| f107r | 487 | 41 | 27 | 124 | <<<
| f107v | 462 | 34 | 41 | 107 | <<<
| f108r | 494 | 37 | 35 | 100 | <<<
| f108v | 581 | 31 | 33 | 118 | <<<
| f111r | 624 | 38 | 50 | 129 | <<<
| f111v | 568 | 39 | 34 | 140 | <<<
| f112r | 401 | 31 | 39 | 81 | <<<
| f112v | 420 | 26 | 28 | 97 | <<<
| f113r | 529 | 46 | 52 | 129 | <<<
| f113v | 502 | 40 | 36 | 115 | <<<
| f114r | 460 | 40 | 45 | 135 | <<<
| f114v | 376 | 25 | 28 | 93 | <<<
| f115r | 461 | 36 | 38 | 99 | <<<
| f115v | 410 | 42 | 43 | 103 | <<<
| f116r | 553 | 32 | 58 | 92 | <<<
| f116v | 2 | 0 | 0 | 0 |

## ANOMALIES

| Type | Count | Description |
|------|-------|-------------|
| INGR_RUN | 361 | 3+ ingredients consecutifs |
| FUNC_CHAIN | 257 | 4+ fonctions consecutives |
| ORPHAN_DOSE | 222 | Dosage sans ingredient |
| NO_INGR | 36 | Ligne sans ingredient |

## FOLIOS A PROBLEMES (plus d anomalies)

### f116r — 58 anomalies, 32 ingredients
  - FUNC_CHAIN: 4 consecutive func
  - NO_INGR: No ingredient in line
  - ORPHAN_DOSE: DOSE after func
  - FUNC_CHAIN: 4 consecutive func
  - FUNC_CHAIN: 5 consecutive func

### f105v — 55 anomalies, 39 ingredients
  - INGR_RUN: 3 consecutive INGR
  - INGR_RUN: 4 consecutive INGR
  - INGR_RUN: 5 consecutive INGR
  - INGR_RUN: 6 consecutive INGR
  - INGR_RUN: 7 consecutive INGR

### f113r — 52 anomalies, 46 ingredients
  - FUNC_CHAIN: 4 consecutive func
  - INGR_RUN: 3 consecutive INGR
  - FUNC_CHAIN: 4 consecutive func
  - ORPHAN_DOSE: DOSE after func
  - ORPHAN_DOSE: DOSE after func

### f111r — 50 anomalies, 38 ingredients
  - FUNC_CHAIN: 4 consecutive func
  - ORPHAN_DOSE: DOSE after func
  - ORPHAN_DOSE: DOSE after func
  - INGR_RUN: 3 consecutive INGR
  - FUNC_CHAIN: 4 consecutive func

### f114r — 45 anomalies, 40 ingredients
  - INGR_RUN: 3 consecutive INGR
  - INGR_RUN: 4 consecutive INGR
  - FUNC_CHAIN: 4 consecutive func
  - INGR_RUN: 3 consecutive INGR
  - INGR_RUN: 4 consecutive INGR

### f104r — 44 anomalies, 32 ingredients
  - INGR_RUN: 3 consecutive INGR
  - INGR_RUN: 4 consecutive INGR
  - INGR_RUN: 5 consecutive INGR
  - INGR_RUN: 6 consecutive INGR
  - FUNC_CHAIN: 4 consecutive func

### f115v — 43 anomalies, 42 ingredients
  - INGR_RUN: 3 consecutive INGR
  - INGR_RUN: 4 consecutive INGR
  - INGR_RUN: 3 consecutive INGR
  - FUNC_CHAIN: 4 consecutive func
  - INGR_RUN: 3 consecutive INGR

### f107v — 41 anomalies, 34 ingredients
  - INGR_RUN: 3 consecutive INGR
  - INGR_RUN: 4 consecutive INGR
  - FUNC_CHAIN: 4 consecutive func
  - ORPHAN_DOSE: DOSE after func
  - INGR_RUN: 3 consecutive INGR

### f103r — 39 anomalies, 37 ingredients
  - INGR_RUN: 3 consecutive INGR
  - FUNC_CHAIN: 4 consecutive func
  - FUNC_CHAIN: 5 consecutive func
  - ORPHAN_DOSE: DOSE after func
  - FUNC_CHAIN: 4 consecutive func

### f112r — 39 anomalies, 31 ingredients
  - INGR_RUN: 3 consecutive INGR
  - FUNC_CHAIN: 4 consecutive func
  - FUNC_CHAIN: 5 consecutive func
  - FUNC_CHAIN: 6 consecutive func
  - INGR_RUN: 3 consecutive INGR

## TOP 37 INGREDIENTS IDENTIFIES

| Ingredient | Occurrences | Folios |
|------------|-------------|--------|
| colocynthis | 190 | f103r f103v f104r f104v f105r |
| eliotropio | 117 | f103v f104r f104v f105r f105v |
| esca da pesci | 110 | f103r f103v f104r f104v f105r |
| periclimeno | 87 | f103r f103v f104r f104v f105r |
| incenso | 75 | f103r f103v f104r f104v f105r |
| laurus | 67 | f103r f104r f105r f105v f106r |
| eliantemo | 57 | f103v f104r f104v f105r f105v |
| perennis, flore pieno | 56 | f103r f103v f104v f105r f105v |
| aqua | 55 | f103r f104r f105r f105v f106r |
| squinanthum | 50 | f103r f103v f104v f105v f106r |
| apari ne | 49 | f103r f103v f104r f104v f105r |
| apio ortense | 48 | f103r f103v f104r f104v f105r |
| colubrinus | 48 | f103r f103v f104r f104v f105r |
| careno | 41 | f103r f104r f104v f105r f105v |
| aurantium , striis argenteis | 34 | f103v f104r f105r f105v f106r |
| aloe | 30 | f103r f103v f104r f104v f105r |
| luisa buona | 24 | f104v f105r f105v f106r f106v |
| coda 1 cavallina | 22 | f104r f105r f105v f107v f108r |
| edera | 21 | f103r f104r f104v f105v f106v |
| coerulescens | 20 | f103r f103v f104r f105v f108v |
| idaei, fructus | 18 | f103v f105r f105v f106v f112v |
| alido | 18 | f104r f104v f105v f106r f108r |
| oleum | 18 | f104v f107r f108r f111r f111v |
| querciola maggiore | 16 | f103r f103v f106r f106v f107r |
| sederino | 16 | f103r f104v f105v f106r f107v |
| esperide | 16 | f103v f105r f105v f106r f107v |
| aleatico di spagna | 16 | f103v f104r f105r f107r f107v |
| conchula indica ,cr vnguis odoratus | 15 | f103r f103v f104v f106r f107r |
| cicerbita | 15 | f103r f104v f106v f108r f111r |
| peruvianus | 15 | f105r f105v f107r f107v f108v |
| scoeff | 13 | f103r f104r f105r f106r f108r |
| reas | 13 | f106v f107r f108r f111r f111v |
| acero | 12 | f103r f103v f104v f105r f111v |
| ipericon | 12 | f103r f104v f105r f105v f106r |
| colchico | 12 | f103v f104r f106v f108v f111v |
| cece di terra | 12 | f105v f106v f107r f111r f112r |
| quassia | 11 | f104r f107r f107v f108r f108v |
| lens | 10 | f103r f103v f105r f108r f111r |
| aloisia | 10 | f103r f103v f104r f104v f107v |
| duraz | 10 | f104v f105r f105v f106r f107r |
| seseli? scsclio | 9 | f103r f103v f104v f106v f107v |
| cuminum | 9 | f104r f104v f106r f107r f108r |
| scodelline scarlatte | 9 | f108r f108v f111r f113v f115v |
| leucacantha | 8 | f103r f108v f111r f111v f112r |
| piera | 8 | f103v f104v f105r f105v f113r |
| scoi pa arborea | 8 | f104r f106r f111r f113r f115v |
| indica | 8 | f104v f105r f106r f112r f114r |
| lucens | 7 | f103r f104r f108r f108v f111v |
| asiaticus, flore pieno croceo | 7 | f104r f104v f106v f108v f111r |
| indaco guattimalo | 7 | f104v f106v f107r f114r f115v |
| carum | 7 | f105v f106v f107r f107v f112r |
| aconito | 6 | f103v f104r f105r f106v f114r |
| cicad<e | 6 | f103v f106v f111r f111v f114r |
| apium | 6 | f104r f107r f108r f113v f114r |
| arcidiavolo | 6 | f105v f106r f106v f107r f116r |
| cainpestris latifolia | 6 | f106r f107v f111v f114v |
| cuscuta | 6 | f106v f107r f107v f114r |
| cono vero | 6 | f107v f111v f114v f115r |
| pero | 5 | f103r f106r f113v f115v f116r |
| cilia.fava di tunisi | 5 | f103r f106r f106v f111v |
| ciciliana | 5 | f103r f103v f111r f113r f115v |
| leontopodio | 5 | f103v f108r f111v f112r |
| opium | 5 | f104v f111r f113r f115r f116r |
| quinquefolia | 5 | f105r f112r f113r f116r |
| pernicona romana | 5 | f106v f107r f108r f111r f113v |
| sedanina | 5 | f108v f113r f115r f116r |
| squama dello ftomoma | 4 | f103r f107v f111r f113r |
| cascarilla | 4 | f104v f107r f107v |
| pareira brava | 4 | f105v f108r f113r f113v |
| erniaria | 4 | f105v f106v f115r f115v |
| cera | 4 | f106v f111v f113v f115r |
| siderite prima | 4 | f106v f108r f111v f114v |
| spodium | 4 | f113r f115r f115v |
| rhus toxicodendron | 3 | f103r f111v |
| asarum | 3 | f103r f105v f113r |
| sciampion | 3 | f103v f113r f116r |
| ladanum | 3 | f104r f108r f114v |
| leandro | 3 | f104r f113v f114v |
| giuseppe rossa doppia | 3 | f105r f105v f112v |
| incarico | 3 | f106r f113v |
| cesino , o segeno | 3 | f106v f111r f115v |
| enaero | 3 | f106v f108r f108v |
| elleboro nero | 3 | f107r f113v f115v |
| sesquipedalis | 3 | f107r f111v f115v |
| paeonia | 3 | f108r f111r f114r |
| lorenza terza | 3 | f108v f113v f114r |
| araco nero | 3 | f113v |
| liquirizia | 2 | f103r f108r |
| esula | 2 | f103r |
| colore | 2 | f103r f108v |
| alcea rosea fl | 2 | f104v f115r |
| arietinum rubru m | 2 | f104v f115r |
| eruca | 2 | f105r f112v |
| corallium | 2 | f105r f105v |
| lesi | 2 | f106v f107r |
| cinque nerbi | 2 | f106v f111v |
| sarniensis | 2 | f107r f107v |
| connina | 2 | f108r f112v |
| ciampolina | 2 | f108r |
| ceciarello | 2 | f108r f111r |
| peso | 2 | f111v f112r |
| oleander, flore albo | 2 | f113v f115v |
| perdigli di fuentcarai | 2 | f114r |
| arancio | 2 | f115r |
| radula, roseum | 2 | f115v |
| daucus | 1 | f103r |
| cofius | 1 | f103v |
| pinus | 1 | f104r |
| judaica | 1 | f104v |
| pesco | 1 | f105r |
| erisamo | 1 | f105v |
| casiajolo bianco | 1 | f105v |
| cnico | 1 | f105v |
| colloquintida | 1 | f106r |
| los | 1 | f106r |
| insanum | 1 | f106v |
| cereo comune | 1 | f107r |
| spina bianca | 1 | f107r |
| acetum | 1 | f107v |
| perasites | 1 | f107v |
| stnilace liscia | 1 | f111r |
| cenizza | 1 | f111r |
| line aquatico | 1 | f112r |
| alno | 1 | f112r |
| cespitosus | 1 | f112r |
| del | 1 | f112v |
| fumaria | 1 | f112v |
| racemosus | 1 | f113r |
| pieno l | 1 | f113r |
| rhaponticum | 1 | f113r |
| scorza d’ arancia | 1 | f113v |
| caspi | 1 | f114r |
| soda | 1 | f114r |
| decumana | 1 | f114r |
| radicchione salva- tico | 1 | f114r |
| anisum | 1 | f114r |
| codolina | 1 | f114r |
| sesamo | 1 | f115v |
| calamintha | 1 | f116r |
| assenzio | 1 | f116r |
| pianta del balsamo | 1 | f116r |

## FOLIOS LES PLUS RICHES EN INGREDIENTS

### f113r — 46 ingredients
  ['aleatico di spagna', 'alido', 'aloe', 'apio ortense', 'aqua', 'asarum', 'aurantium , striis argenteis', 'careno', 'carum', 'cece di terra', 'cicerbita', 'ciciliana', 'coerulescens', 'colchico', 'colocynthis', 'colubrinus', 'conchula indica ,cr vnguis odoratus', 'cuminum', 'eliantemo', 'eliotropio', 'esca da pesci', 'esperide', 'idaei, fructus', 'incenso', 'ipericon', 'laurus', 'oleum', 'opium', 'pareira brava', 'perennis, flore pieno', 'periclimeno', 'peruvianus', 'pieno l', 'piera', 'querciola maggiore', 'quinquefolia', 'racemosus', 'reas', 'rhaponticum', 'sciampion', 'scoi pa arborea', 'sedanina', 'sederino', 'spodium', 'squama dello ftomoma', 'squinanthum']

### f115v — 42 ingredients
  ['alido', 'aloe', 'aloisia', 'apio ortense', 'apium', 'aqua', 'aurantium , striis argenteis', 'careno', 'cesino , o segeno', 'ciciliana', 'colchico', 'colocynthis', 'colubrinus', 'conchula indica ,cr vnguis odoratus', 'eliantemo', 'eliotropio', 'elleboro nero', 'erniaria', 'esca da pesci', 'esperide', 'idaei, fructus', 'incenso', 'indaco guattimalo', 'indica', 'ipericon', 'laurus', 'oleander, flore albo', 'oleum', 'perennis, flore pieno', 'periclimeno', 'pero', 'piera', 'radula, roseum', 'reas', 'scodelline scarlatte', 'scoi pa arborea', 'sederino', 'sesamo', 'seseli? scsclio', 'sesquipedalis', 'spodium', 'squinanthum']

### f107r — 41 ingredients
  ['aleatico di spagna', 'aloe', 'apari ne', 'apio ortense', 'apium', 'aqua', 'arcidiavolo', 'aurantium , striis argenteis', 'careno', 'carum', 'cascarilla', 'cece di terra', 'cereo comune', 'colocynthis', 'colubrinus', 'conchula indica ,cr vnguis odoratus', 'cuminum', 'cuscuta', 'duraz', 'eliantemo', 'eliotropio', 'elleboro nero', 'esca da pesci', 'incenso', 'indaco guattimalo', 'ipericon', 'laurus', 'lesi', 'luisa buona', 'oleum', 'perennis, flore pieno', 'periclimeno', 'pernicona romana', 'peruvianus', 'quassia', 'querciola maggiore', 'reas', 'sarniensis', 'sesquipedalis', 'spina bianca', 'squinanthum']

### f106v — 40 ingredients
  ['aconito', 'aloe', 'apari ne', 'apio ortense', 'aqua', 'arcidiavolo', 'asiaticus, flore pieno croceo', 'aurantium , striis argenteis', 'careno', 'carum', 'cece di terra', 'cera', 'cesino , o segeno', 'cicad<e', 'cicerbita', 'cilia.fava di tunisi', 'cinque nerbi', 'colchico', 'colubrinus', 'cuscuta', 'edera', 'eliantemo', 'eliotropio', 'enaero', 'erniaria', 'esca da pesci', 'idaei, fructus', 'incenso', 'indaco guattimalo', 'insanum', 'laurus', 'lesi', 'luisa buona', 'perennis, flore pieno', 'periclimeno', 'pernicona romana', 'querciola maggiore', 'reas', 'seseli? scsclio', 'siderite prima']

### f113v — 40 ingredients
  ['aleatico di spagna', 'aloisia', 'apari ne', 'apio ortense', 'apium', 'aqua', 'araco nero', 'aurantium , striis argenteis', 'careno', 'cera', 'coerulescens', 'colocynthis', 'colubrinus', 'cuminum', 'duraz', 'eliantemo', 'eliotropio', 'elleboro nero', 'esca da pesci', 'idaei, fructus', 'incarico', 'incenso', 'laurus', 'leandro', 'lens', 'lorenza terza', 'luisa buona', 'oleander, flore albo', 'oleum', 'pareira brava', 'perennis, flore pieno', 'periclimeno', 'pernicona romana', 'pero', 'peruvianus', 'querciola maggiore', 'scodelline scarlatte', 'scorza d’ arancia', 'seseli? scsclio', 'squinanthum']

### f114r — 40 ingredients
  ['aconito', 'alido', 'aloe', 'anisum', 'apari ne', 'apio ortense', 'apium', 'aqua', 'careno', 'caspi', 'cicad<e', 'coda 1 cavallina', 'codolina', 'coerulescens', 'colocynthis', 'colubrinus', 'cuscuta', 'decumana', 'duraz', 'eliantemo', 'eliotropio', 'esca da pesci', 'idaei, fructus', 'incenso', 'indaco guattimalo', 'indica', 'ipericon', 'laurus', 'lorenza terza', 'luisa buona', 'paeonia', 'perdigli di fuentcarai', 'perennis, flore pieno', 'periclimeno', 'peruvianus', 'quassia', 'radicchione salva- tico', 'reas', 'soda', 'squinanthum']

### f105v — 39 ingredients
  ['alido', 'aloe', 'apari ne', 'apio ortense', 'aqua', 'arcidiavolo', 'asarum', 'aurantium , striis argenteis', 'careno', 'carum', 'casiajolo bianco', 'cece di terra', 'cnico', 'coda 1 cavallina', 'coerulescens', 'colocynthis', 'colubrinus', 'corallium', 'duraz', 'edera', 'eliantemo', 'eliotropio', 'erisamo', 'erniaria', 'esca da pesci', 'esperide', 'giuseppe rossa doppia', 'idaei, fructus', 'incenso', 'ipericon', 'laurus', 'luisa buona', 'pareira brava', 'perennis, flore pieno', 'periclimeno', 'peruvianus', 'piera', 'sederino', 'squinanthum']

### f111v — 39 ingredients
  ['acero', 'aleatico di spagna', 'aloe', 'apari ne', 'apio ortense', 'aqua', 'cainpestris latifolia', 'careno', 'cera', 'cicad<e', 'cicerbita', 'cilia.fava di tunisi', 'cinque nerbi', 'coerulescens', 'colchico', 'colocynthis', 'colubrinus', 'conchula indica ,cr vnguis odoratus', 'cono vero', 'eliantemo', 'eliotropio', 'esca da pesci', 'incenso', 'leontopodio', 'leucacantha', 'lucens', 'oleum', 'perennis, flore pieno', 'periclimeno', 'peruvianus', 'peso', 'querciola maggiore', 'reas', 'rhus toxicodendron', 'scoeff', 'sederino', 'sesquipedalis', 'siderite prima', 'squinanthum']

### f111r — 38 ingredients
  ['aleatico di spagna', 'aloe', 'apio ortense', 'asiaticus, flore pieno croceo', 'cece di terra', 'ceciarello', 'cenizza', 'cesino , o segeno', 'cicad<e', 'cicerbita', 'ciciliana', 'coda 1 cavallina', 'coerulescens', 'colocynthis', 'cuminum', 'edera', 'eliantemo', 'eliotropio', 'esca da pesci', 'esperide', 'incenso', 'ipericon', 'lens', 'leucacantha', 'oleum', 'opium', 'paeonia', 'perennis, flore pieno', 'periclimeno', 'pernicona romana', 'reas', 'scodelline scarlatte', 'scoeff', 'scoi pa arborea', 'sederino', 'squama dello ftomoma', 'squinanthum', 'stnilace liscia']

### f103r — 37 ingredients
  ['acero', 'aloe', 'aloisia', 'apari ne', 'apio ortense', 'aqua', 'asarum', 'careno', 'cicerbita', 'ciciliana', 'cilia.fava di tunisi', 'coerulescens', 'colocynthis', 'colore', 'colubrinus', 'conchula indica ,cr vnguis odoratus', 'daucus', 'edera', 'esca da pesci', 'esula', 'incenso', 'ipericon', 'laurus', 'lens', 'leucacantha', 'liquirizia', 'lucens', 'perennis, flore pieno', 'periclimeno', 'pero', 'querciola maggiore', 'rhus toxicodendron', 'scoeff', 'sederino', 'seseli? scsclio', 'squama dello ftomoma', 'squinanthum']

### f108r — 37 ingredients
  ['alido', 'apari ne', 'apio ortense', 'apium', 'aqua', 'ceciarello', 'ciampolina', 'cicerbita', 'coda 1 cavallina', 'colocynthis', 'colubrinus', 'connina', 'cuminum', 'edera', 'eliotropio', 'enaero', 'esca da pesci', 'esperide', 'incenso', 'ladanum', 'laurus', 'lens', 'leontopodio', 'liquirizia', 'lucens', 'oleum', 'paeonia', 'pareira brava', 'perennis, flore pieno', 'periclimeno', 'pernicona romana', 'quassia', 'reas', 'scodelline scarlatte', 'scoeff', 'siderite prima', 'squinanthum']

### f115r — 36 ingredients
  ['alcea rosea fl', 'alido', 'aloe', 'apio ortense', 'arancio', 'arietinum rubru m', 'aurantium , striis argenteis', 'careno', 'cera', 'cicerbita', 'coda 1 cavallina', 'coerulescens', 'colchico', 'colocynthis', 'colubrinus', 'conchula indica ,cr vnguis odoratus', 'cono vero', 'edera', 'eliantemo', 'eliotropio', 'erniaria', 'esca da pesci', 'incenso', 'luisa buona', 'oleum', 'opium', 'perennis, flore pieno', 'periclimeno', 'peruvianus', 'piera', 'querciola maggiore', 'scoeff', 'sedanina', 'sederino', 'spodium', 'squinanthum']

### f104v — 35 ingredients
  ['acero', 'alcea rosea fl', 'alido', 'aloe', 'aloisia', 'apari ne', 'apio ortense', 'arietinum rubru m', 'asiaticus, flore pieno croceo', 'careno', 'cascarilla', 'cicerbita', 'colocynthis', 'colubrinus', 'conchula indica ,cr vnguis odoratus', 'cuminum', 'duraz', 'edera', 'eliantemo', 'eliotropio', 'esca da pesci', 'incenso', 'indaco guattimalo', 'indica', 'ipericon', 'judaica', 'luisa buona', 'oleum', 'opium', 'perennis, flore pieno', 'periclimeno', 'piera', 'sederino', 'seseli? scsclio', 'squinanthum']

### f105r — 34 ingredients
  ['acero', 'aconito', 'aleatico di spagna', 'aloe', 'apari ne', 'apio ortense', 'aqua', 'aurantium , striis argenteis', 'careno', 'coda 1 cavallina', 'colocynthis', 'colubrinus', 'corallium', 'duraz', 'eliantemo', 'eliotropio', 'eruca', 'esca da pesci', 'esperide', 'giuseppe rossa doppia', 'idaei, fructus', 'incenso', 'indica', 'ipericon', 'laurus', 'lens', 'luisa buona', 'perennis, flore pieno', 'periclimeno', 'peruvianus', 'pesco', 'piera', 'quinquefolia', 'scoeff']

### f106r — 34 ingredients
  ['alido', 'apari ne', 'apio ortense', 'aqua', 'arcidiavolo', 'aurantium , striis argenteis', 'cainpestris latifolia', 'careno', 'cilia.fava di tunisi', 'colloquintida', 'colocynthis', 'colubrinus', 'conchula indica ,cr vnguis odoratus', 'cuminum', 'duraz', 'eliantemo', 'eliotropio', 'esca da pesci', 'esperide', 'incarico', 'incenso', 'indica', 'ipericon', 'laurus', 'los', 'luisa buona', 'perennis, flore pieno', 'periclimeno', 'pero', 'querciola maggiore', 'scoeff', 'scoi pa arborea', 'sederino', 'squinanthum']

### f107v — 34 ingredients
  ['acetum', 'aleatico di spagna', 'aloisia', 'apari ne', 'apio ortense', 'aqua', 'aurantium , striis argenteis', 'cainpestris latifolia', 'careno', 'carum', 'cascarilla', 'coda 1 cavallina', 'colocynthis', 'colubrinus', 'conchula indica ,cr vnguis odoratus', 'cono vero', 'cuscuta', 'edera', 'eliotropio', 'esca da pesci', 'esperide', 'ipericon', 'laurus', 'luisa buona', 'perasites', 'perennis, flore pieno', 'periclimeno', 'peruvianus', 'quassia', 'sarniensis', 'sederino', 'seseli? scsclio', 'squama dello ftomoma', 'squinanthum']

### f104r — 32 ingredients
  ['aconito', 'aleatico di spagna', 'alido', 'aloe', 'aloisia', 'apari ne', 'apio ortense', 'apium', 'aqua', 'asiaticus, flore pieno croceo', 'aurantium , striis argenteis', 'careno', 'coda 1 cavallina', 'coerulescens', 'colchico', 'colocynthis', 'colubrinus', 'cuminum', 'edera', 'eliantemo', 'eliotropio', 'esca da pesci', 'incenso', 'ladanum', 'laurus', 'leandro', 'lucens', 'periclimeno', 'pinus', 'quassia', 'scoeff', 'scoi pa arborea']

### f116r — 32 ingredients
  ['aconito', 'alido', 'apio ortense', 'aqua', 'arcidiavolo', 'assenzio', 'aurantium , striis argenteis', 'calamintha', 'cicerbita', 'coerulescens', 'colocynthis', 'colubrinus', 'conchula indica ,cr vnguis odoratus', 'eliantemo', 'eliotropio', 'esca da pesci', 'idaei, fructus', 'incenso', 'oleum', 'opium', 'periclimeno', 'pero', 'peruvianus', 'pianta del balsamo', 'quassia', 'quinquefolia', 'sciampion', 'scoeff', 'sedanina', 'sederino', 'seseli? scsclio', 'squinanthum']

### f103v — 31 ingredients
  ['acero', 'aconito', 'aleatico di spagna', 'aloe', 'aloisia', 'apari ne', 'apio ortense', 'aurantium , striis argenteis', 'cicad<e', 'ciciliana', 'coerulescens', 'cofius', 'colchico', 'colocynthis', 'colubrinus', 'conchula indica ,cr vnguis odoratus', 'eliantemo', 'eliotropio', 'esca da pesci', 'esperide', 'idaei, fructus', 'incenso', 'lens', 'leontopodio', 'perennis, flore pieno', 'periclimeno', 'piera', 'querciola maggiore', 'sciampion', 'seseli? scsclio', 'squinanthum']

### f108v — 31 ingredients
  ['aloe', 'apari ne', 'apio ortense', 'aqua', 'asiaticus, flore pieno croceo', 'careno', 'coda 1 cavallina', 'coerulescens', 'colchico', 'colocynthis', 'colore', 'colubrinus', 'conchula indica ,cr vnguis odoratus', 'eliantemo', 'eliotropio', 'enaero', 'esca da pesci', 'incenso', 'laurus', 'leucacantha', 'lorenza terza', 'lucens', 'perennis, flore pieno', 'periclimeno', 'peruvianus', 'quassia', 'querciola maggiore', 'scodelline scarlatte', 'sedanina', 'sederino', 'squinanthum']

### f112r — 31 ingredients
  ['acero', 'aleatico di spagna', 'alido', 'alno', 'aloe', 'apari ne', 'apio ortense', 'aqua', 'asiaticus, flore pieno croceo', 'carum', 'cece di terra', 'cespitosus', 'cicerbita', 'coda 1 cavallina', 'colocynthis', 'colubrinus', 'eliantemo', 'eliotropio', 'incenso', 'indica', 'laurus', 'leontopodio', 'leucacantha', 'line aquatico', 'luisa buona', 'perennis, flore pieno', 'periclimeno', 'peso', 'querciola maggiore', 'quinquefolia', 'seseli? scsclio']

### f112v — 26 ingredients
  ['aloe', 'apari ne', 'aqua', 'aurantium , striis argenteis', 'cece di terra', 'coda 1 cavallina', 'coerulescens', 'colocynthis', 'colubrinus', 'connina', 'del', 'eliantemo', 'eliotropio', 'eruca', 'esca da pesci', 'fumaria', 'giuseppe rossa doppia', 'idaei, fructus', 'incenso', 'laurus', 'lucens', 'oleum', 'perennis, flore pieno', 'periclimeno', 'quassia', 'querciola maggiore']

### f114v — 25 ingredients
  ['aleatico di spagna', 'apari ne', 'apio ortense', 'aqua', 'aurantium , striis argenteis', 'cainpestris latifolia', 'careno', 'cicerbita', 'colocynthis', 'cono vero', 'edera', 'eliantemo', 'eliotropio', 'esca da pesci', 'idaei, fructus', 'incenso', 'indica', 'ladanum', 'laurus', 'leandro', 'oleum', 'periclimeno', 'scoeff', 'siderite prima', 'squinanthum']

## OU CONCENTRER LES EFFORTS

### Priorite 1 : Folios riches en ingredients mais aussi en anomalies
  - **f103r** : 37 ingredients, 39 anomalies — corriger les anomalies revelera PLUS d ingredients
  - **f103v** : 31 ingredients, 32 anomalies — corriger les anomalies revelera PLUS d ingredients
  - **f104r** : 32 ingredients, 44 anomalies — corriger les anomalies revelera PLUS d ingredients
  - **f104v** : 35 ingredients, 26 anomalies — corriger les anomalies revelera PLUS d ingredients
  - **f105r** : 34 ingredients, 32 anomalies — corriger les anomalies revelera PLUS d ingredients
  - **f105v** : 39 ingredients, 55 anomalies — corriger les anomalies revelera PLUS d ingredients
  - **f106r** : 34 ingredients, 27 anomalies — corriger les anomalies revelera PLUS d ingredients
  - **f106v** : 40 ingredients, 34 anomalies — corriger les anomalies revelera PLUS d ingredients
  - **f107r** : 41 ingredients, 27 anomalies — corriger les anomalies revelera PLUS d ingredients
  - **f107v** : 34 ingredients, 41 anomalies — corriger les anomalies revelera PLUS d ingredients
  - **f108r** : 37 ingredients, 35 anomalies — corriger les anomalies revelera PLUS d ingredients
  - **f108v** : 31 ingredients, 33 anomalies — corriger les anomalies revelera PLUS d ingredients
  - **f111r** : 38 ingredients, 50 anomalies — corriger les anomalies revelera PLUS d ingredients
  - **f111v** : 39 ingredients, 34 anomalies — corriger les anomalies revelera PLUS d ingredients
  - **f112r** : 31 ingredients, 39 anomalies — corriger les anomalies revelera PLUS d ingredients
  - **f112v** : 26 ingredients, 28 anomalies — corriger les anomalies revelera PLUS d ingredients
  - **f113r** : 46 ingredients, 52 anomalies — corriger les anomalies revelera PLUS d ingredients
  - **f113v** : 40 ingredients, 36 anomalies — corriger les anomalies revelera PLUS d ingredients
  - **f114r** : 40 ingredients, 45 anomalies — corriger les anomalies revelera PLUS d ingredients
  - **f114v** : 25 ingredients, 28 anomalies — corriger les anomalies revelera PLUS d ingredients
  - **f115r** : 36 ingredients, 38 anomalies — corriger les anomalies revelera PLUS d ingredients
  - **f115v** : 42 ingredients, 43 anomalies — corriger les anomalies revelera PLUS d ingredients
  - **f116r** : 32 ingredients, 58 anomalies — corriger les anomalies revelera PLUS d ingredients

### Priorite 2 : Folios avec beaucoup de mots mais peu d ingredients

### Priorite 3 : Anomalies FUNC_CHAIN (ingredients caches)
  257 chaines de 4+ fonctions consecutives
  Ces chaines contiennent probablement des ingredients non reconnus.
  Chaque chaine corrigee pourrait reveler 1-3 ingredients supplementaires.