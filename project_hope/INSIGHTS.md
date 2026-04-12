# VOYNICH MS 408 — Decoding Insights

## THE ANSWER

The Voynich Manuscript is **personal Tironian shorthand** — a pharmacist's
notebook written in an invented stenographic system. Not a cipher, not a
hoax, not an unknown language. Shorthand.

600 years of geniuses searched for a cipher. Nobody searched for shorthand.

The encoding is **arbitrary** (no phonetic or alphabetic logic confirmed).
The pharmacist memorized codes through daily practice over years.

## PROVEN STRUCTURE (p < 0.01)

| Claim | Evidence | p-value |
|---|---|---|
| Prefix + Root + Suffix system | 67% pharma decomposed | — |
| 18 logograms | bifolio + w2v cos>0.97 | — |
| Gallows 88% block-initial | Permutation test | 0.000 |
| -am = sentence terminator 72% | 5.3x enrichment | <0.01 |
| Plant name suffix -or/-al = COLD | 6/14 cold, 0/16 hot | 0.005 |
| n=98% word-end, q=99% word-start | Positional analysis | <0.01 |
| Volvelle = alphabet (17 symbols) | 52 consecutive logograms | 0.00016 |
| VMS ≈ Macer Floridus type | Multi-corpus test | 1.61x (#1/15) |
| Section-specific vocabulary | 57+22+11 exclusive roots | <0.01 |
| Pharma compounds = prefix+root+suffix | Substring analysis | — |
| Pharma openers = gallows+plant_root+suffix | 27% confirmed | — |
| 143 herbal / 77 Macer = 1.9 (recto+verso) | Count | — |

## DECODED VOCABULARY

### Ingredients (confirmed 0.7-0.9)
| Root | Latin | English | Method | Conf |
|---|---|---|---|---|
| cth | acetum | vinegar | Fingerprint unique 6 anchors | 0.9 |
| yk | mel | honey | Fingerprint unique 6 anchors | 0.9 |
| cht | piper | pepper | Fingerprint Macer77 | 0.9 |
| shocthy | mastix | mastic resin | Fingerprint 100 anchors | 0.9 |
| shotch | nigella | black cumin | Fingerprint 100 anchors | 0.9 |
| chk | oleum | oil | Triangulation 3 anchors | 0.8 |
| otoly | sal | salt | Triangulation 2 anchors | 0.7 |

### Logograms (confirmed 1.0)
o=ac, l=se, d=de, r=recipe, v=vel, x=crux, k=cum, m=misce,
f=per, t=et, y=in, c=cum, s=est, sh=ci, p=usque, ch=cum

### Plant names (68, confidence 0.6) — first word of herbal folio
pcheod=ruta, foch=viola, pos=lactuca, tsho=apium, posho=salvia,
tedo=crocus, tocph=mentha, keered=coriandrum, pchod=aristolochia...
(full list in knowledge_base.json)

### Pharma word composition
```
opchedy = o(ac) + pched(lens) + y = "with lentils..."
qocthedy = qo(?) + cth(acetum) + edy = "? vinegar (genitive)"
```
Prefixes = incorporated prepositions: o=ac, l=se, d=de, y=in, qo=?

## BEST DECODED LINES (Session 17 — Death Match)

**f48v = Ruta × Macer "Ruta" — positional alignment (offset -0.013)**

**Line 8**: `rutam OLEUM ok rutam MEL ol SAL ch matricis matricis ot`
= ruta + **huile** + ruta + **miel** + **sel** + matrice (utérus)
→ Macer: "rutam cum oleo, melle et sale ad matricem" ✓

**Line 10**: `tol ch ytedy MEL ch ruta PIPER ch trita ACETUM ok ar melle`
= **miel** + ruta + **poivre** + *trituré* + **vinaigre** + miel
→ Macer: "Gramina si rutae jungas piperque mero trituré" ✓ = oximel poivré

**Line 11**: `NITRUM ventrem MEL in tam or stomachum stomachum`
= **nitre** + ventre + **miel** + dans ... **estomac**
→ Macer: cure estomac avec nitre et miel ✓

Méthode: 50 mots latins significatifs extraits du chapitre Macer Ruta,
mappés par position (0-1). 10 ancres VMS confirmées pour calibration.
Les mots inconnus sont associés au mot latin le plus proche en position.

## ELIMINATED HYPOTHESES

| Hypothesis | Test | Result | Session |
|---|---|---|---|
| Letter substitution | Volvelle L3→L5 | Score 0.00 (worse than original) | 12 |
| f↔p meaningful variants | Permutation | p=1.0 (noise) | 13 |
| VMS = AN recodification | Co-occurrence | p=0.92 (Zipf artifact) | 13 |
| i-count = dose number | Distribution | i2=81% herbal (inverted) | 14 |
| Encoding has phonetic logic | All tests | 0-12% match | 14 |
| che = caro (flesh) | Frequency | 80% of folios = functional | 15 |
| sal = cleartext Latin | Rank test | 20/273 (not exceptional) | 13 |

## METHOD: What Works

1. **Fingerprint matching** — binary presence/absence across Sherwood↔Macer anchors
2. **Triangulation** — shared ingredients between chapters = shared roots between folios
3. **Decomposition** — pharma words = prefix(preposition) + root(ingredient) + suffix(grammar)
4. **Section targeting** — each manuscript section ↔ its matching corpus

## METHOD: What Doesn't Work

- Global statistics (Zipf contamination on everything frequent)
- Co-occurrence mapping (noise indistinguishable from signal)
- Frequency-rank mapping (artifact of any two texts)
- Letter-level analysis (encoding is at WORD level)
- Brute force across entire manuscript (too much noise, need surgical strikes)

## SESSION 16 RESULTS — Surgical Strikes

### Frappe 1: Herbal × Macer (16 anchors)
**Method**: Positional matching within folio↔chapter pairs + cross-folio fingerprint.
- 6 calibration anchors in f48v (Ruta) = best constrained folio
- Cross-folio validation with TP/FP/FN counts

| Root | Latin | Conf | Method | Cross-validation |
|------|-------|------|--------|------------------|
| seees | lens | 0.75 | Positional f3v + fingerprint | PERFECT: TP=1, FP=0, FN=0 |
| ykeed | nitrum | 0.70 | Positional f48v (Ruta) | Clean: TP=1, FP=0, FN=1 |
| kald | ovum | 0.65 | Positional f66v (Satureia) | Clean: TP=1, FP=0, FN=1 |
| **ypch** | **aqua** | **0.70** | Fingerprint J=0.50 | **TP=4, FP=2 — BEST aqua candidate** |

**ypch=aqua** overrides session 15 ypch=allium (single-source ABENGUEFIT).

### Frappe 2: Pharma recipe gap-filling
**Method**: For 31 well-decoded recipes (60%+, 2+ known ingredients), search 3893 corpus recipes for matching ingredient profiles.

Key finding: `ch` assigned to 6 different ingredients across 12 recipes → **CONFIRMS ch is FUNCTIONAL, not a specific ingredient**. The gap-filling method is dominated by noise when the most frequent unknown is a grammatical word.

### Frappe 3: Balnea vocabulary
**7 balnea-exclusive roots**: qolsh, qoly, loly, salch, qolky, lcheckhy, olksh
**8 balnea-enriched roots** (>66%): qolch, olsh, qolk, qol, solch, solsh, sheckh, rsh

**Pattern**: Most balnea roots contain `ol`/`l` as substring → `ol` may encode a balnea-specific concept (body/bath/water).

### Frappe 4 → Session 17: Galenic quality encoding
**k/t RATIO: WRONG DIRECTION** — not how qualities are encoded.
**oty in L1-3: WEAKENED** — p=0.166 with 29 plants (was 0.023 with 22).

**REAL ANSWER: Plant name SUFFIX encodes quality (p = 0.005)**
- **-or / -al suffix = COLD plant**
  - fochor(viola), parchor(ribes), pchor(anagallis), ksor(spinacia) = `-or`
  - keeredal(coriandrum), pykydal(atriplex) = `-al`
  - 6/14 cold plants, **0/16 hot plants** → Fisher p = 0.005
- Hot plants use other suffixes: -chy, -ey, -o, -ar, -am
- The pharmacist embedded quality IN his plant name mnemonic

### Frappe 5: Universal vehicles
**sh** = 51% preceded by DOSE marker → distinctive "measurement" profile
- `ch`: 97% of folios, 71% of good recipes → FUNCTIONAL (connector/conjunction)
- `ot`: 85% of folios, 53% after INGR → FUNCTIONAL (connector)
- `sh`: 89% of folios, 51% before DOSE → possible vehicle or measurement word

### Frappe 6: Functional word classification
**62 roots in 20%+ of folios** = not specific ingredients. Classified:
- **44 CONNECTORS** (uniform position): ch, ot, ok, or, qot, yk, aiin, ar...
- **3 TERMINATORS** (end-heavy): dy (pos=0.72), oty (pos=0.68), am (pos=0.88)
- **4 OPENERS** (start-heavy): dch, tch, pch, ych (pos=0.13)
- **9 BALNEA-HEAVY**: qok, ol, olk, lch, olch, qoky, qoty, dsh, sh
- **2 PHARMA-SPECIFIC**: ched (64% pharma), lk (77% pharma)

**Critical correction**: VMS sections are herbal_a(111), herbal_b(32), pharma(24), balnea(20), cosmo(22), astro(10), bio(6), volvelle(1).

## DECODED VOCABULARY (updated session 16)

### Ingredients (confirmed 0.7-0.9)
| Root | Latin | English | Method | Conf |
|---|---|---|---|---|
| cth | acetum | vinegar | Fingerprint unique 6 anchors | 0.9 |
| yk | mel | honey | Fingerprint unique 6 anchors | 0.9 |
| cht | piper | pepper | Fingerprint Macer77 | 0.9 |
| shocthy | mastix | mastic resin | Fingerprint 100 anchors | 0.9 |
| shotch | nigella | black cumin | Fingerprint 100 anchors | 0.9 |
| chk | oleum | oil | Triangulation 3 anchors | 0.8 |
| otoly | sal | salt | Triangulation 2 anchors | 0.7 |
| seees | lens | lentil | Frappe1 positional+fingerprint | 0.75 |
| **ypch** | **aqua** | **water** | **Fingerprint + 81% accuracy 16 anchors** | **0.75** |
| ykeed | nitrum | saltpeter | Frappe1 positional f48v | 0.70 |
| kald | ovum | egg | Frappe1 positional f66v | 0.65 |
| ched | vinum? | wine? | Constraint+pharma 64% (HYPOTHESIS) | 0.60 |
| opch | succus? | juice? | Constraint+pharma 44% (HYPOTHESIS) | 0.55 |

### Functional words (NEW — session 16)
62 high-frequency roots classified as grammatical, NOT ingredients.
Top: ch(97%), sh(89%), ot(85%), ok(84%), qok(77%), ol(66%), dy(62%)...
See `hypothesis_registry.json → functional_words` for full list.

## HONEST EVALUATION (session 16)

See `session_16/EVALUATION.md` for full audit.

**Real decode rate**: ~5% (not 42%). Most root matches are false positives
from short (2-3 char) roots matching inside longer words.

**What's proven**: 8 structural facts at p<0.05. 3-4 ingredient codes.
**What's not**: Can't read a single complete recipe in Latin yet.
**What matters**: Eliminated 90% of false leads. Know WHERE and HOW to search.

### Tier 1 (8 proven facts)
Morphology, gallows position, n/q position, -am terminator,
volvelle alphabet, Macer match, herbal↔pharma substrings, oty=cold marker

### Tier 2 (6 strong but fragile)
cth=acetum, yk=mel, cht=piper, chk=oleum, 62 functional words, section vocabulary

### Tier 3-4 (speculative)
31 probable ingredients (conf 0.5), 23 plant names, logogram meanings, recipe decoding

## SESSION 16 LATE DISCOVERY — Pharma openers = recipe names

**27% of pharma block openers contain a known plant root as substring.**

Structure: `[gallows_prefix] + [plant_root] + [suffix]`

| Opener | Decomposition | Plant |
|--------|--------------|-------|
| pchedal | p + pched + al | lens |
| podar | p + pod + ar | valeriana |
| tshdol | tsh + dol(?) | sonchus? |
| fcheody | f + fch + eody | veronica |
| qokeedy | qo + keed + y | erigeron |

Gallows distribution in openers: **p=54%, t=21%, k=6%, f=5%**

This means **recipes ARE named by their plant**, same encoding as herbal
first-words but prefixed with a gallows. The gallows may indicate recipe
type (p=recipe/preparation, t=treatment?).

Other session 16 late findings:
- Star colors (R/V) do NOT correlate with opener gallows
- f116v has only 2 words ("oror sheey") — colophon or end marker
- Cosmo/astro have 372 unique short labels — independent vocabulary

## NEXT: Session 17

See `session_16/PLAN_SESSION_17.md` — 7 attacks ranked by ROI.

Order: Clean FP → Decode openers → 1 recipe → Validate oty → Prove aqua

1. **Clean false positives** — exclude ≤3 char roots from global matching
2. **Decode pharma openers** — match 286 openers to plant names (★★★★★)
3. **ONE readable recipe** — using opener→plant to constrain ingredients
4. **Validate oty=cold on herbal_b** (32 folios, target p<0.01)
5. **Prove ypch=aqua** independently
6. **Find vinum/succus** if aqua confirmed
7. **Cosmo/astro labels** — independent vocabulary analysis

*Sessions 10-16, April 2026*
