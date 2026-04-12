# Voynich Manuscript Structural Analysis

### A computational investigation by Guillaume Clement & Claude (Anthropic)

> **Status:** ~60 hours of analysis, 8 medieval corpora, 18 sessions, one corrected paper. The structural findings (8 confirmed properties) are robust. The ingredient identifications (7 candidates) are tentative. A previous phonetic decryption attempt contained a methodological bias and has been corrected.

---

## The hypothesis in plain English

The Voynich Manuscript is a **pharmacist's personal notebook**, written in his own private shorthand system. Not a cipher. Not a language. One man's stenography, invented for his own use and never shared.

Think of it this way: a modern doctor scribbles abbreviations on prescriptions that only the pharmacist can read. Now imagine a 15th-century apothecary who invented his own complete writing system to record every plant and recipe he knew. That's what we think the VMS is.

---

## How we rebuilt the manuscript's structure

We parsed the entire ZL v3b transcription (38,456 words, 226 folios) into a structured database. Every word was decomposed into its components: root, prefix, suffix, logogram status.

The manuscript breaks down into 8 sections with very different structures:

```
Section      Folios  Words    Blocks/folio  What it looks like
herbal_a     111     10,243   2.0           1 plant drawing per page, short text
herbal_b      32      3,976   2.7           Same, slightly denser
pharma        24     10,891   11.9          Dense text, ~12 recipe blocks per page
balnea        20      6,954   4.8           Bath/body entries
cosmo         22      2,587   1.0           Circular diagrams with short labels
astro         10      1,752   4.0           Star diagrams
bio            6      1,855   5.2           Anatomical
volvelle       1        198   1.0           The famous f57v
```

The key number: **herbal = 2 blocks/folio** (one entry per page) vs **pharma = 12 blocks/folio** (a dozen recipes per page). This is the structure of a **personal pharmaceutical catalogue**: a plant reference section and a recipe formulary, exactly like the Circa Instans paired with an Antidotarium.

We then classified every root by frequency. Roots in more than 20% of folios (62 roots) are **functional/grammatical words**, too ubiquitous to be ingredients. This separation prevents the most common error in VMS analysis: assigning ingredient meanings to words that are actually grammatical connectors.

---

## The core finding: herbal roots reappear inside pharma compounds

This is a measurable structural property of the text, independent of any theory.

The root `pched` appears as a standalone word in herbal folio f26v. The **same root** appears embedded inside **635 compound words** in the pharmaceutical section:

```
Herbal:    pched, pchedy                                    (standalone, f26v)
Pharma:    o·pched·y, qo·pched·edy, pched·al, pched·aiin   (compounds)
```

The compound structure decomposes as:

```
[prefix]  +  [root]  +  [suffix]
   o            pched       y
(logogram)   (content)   (grammar)
```

This happens systematically: **53% of pharma block openers** (154/286) contain a herbal plant root as a substring. The pharma section references the herbal section through embedded roots, exactly as a recipe collection references its ingredient catalogue.

This finding is **botanical-ID-agnostic**. Even if you swap every plant identification, the structural pattern remains statistically visible.

---

## Decoded lines

Using 7 candidate ingredient codes from cross-folio fingerprint matching, plus 18 logograms and 62 classified functional words:

### f48v, line 10 (best line, 3 candidate ingredients)

```
EVA:    tol   chedy  ytedy  ykeol  chdy   chdor  chtol    chdy   ytchedal  cthey   okar  ar  ary
Decode: (?)   [FUNC] [FUNC] (?)    [FUNC] (?)    PIPER    [FUNC] (?)       ACETUM  [FUNC][FUNC](?)
```

**PIPER** (pepper) and **ACETUM** (vinegar) connected by functional words. The Macer Floridus chapter on Ruta describes exactly this combination: *"Gramina si rutae jungas salque piperque cumque mero"*. The `[FUNC]` words between ingredients likely correspond to Latin conjunctions (*cum*, *et*, *in*).

### f48v, line 8 (2 candidate ingredients)

```
EVA:    oteody chkedy  okaiin chckhedy ykedy  oldy  otolychdy  kaly   tokar  otam
Decode: (?)    OLEUM   [FUNC] (?)      (?)    [FUNC] SAL       (?)    (?)    [FUNC+am]
```

**OLEUM** (oil) and **SAL** (salt), ending with the clause terminator `-am`. Macer's Ruta chapter: *"rutam cum oleo et sale ad matricem"*.

### f9v, line 2 (Viola, 2 candidate ingredients)

```
EVA:    dchor  qoaiin chkaiin cthor  chol   chor   cphol  dy   oty   qokaiin  dy
Decode: [FUNC] [FUNC] OLEUM   ACETUM [FUNC] [FUNC] [FUNC] [END][END] [FUNC]   [END]
```

**OLEUM** followed by **ACETUM**. Macer's Viola chapter: *"ex violis oleum... cum aceto"*.

### f28r, line 4 (Aristolochia, 2 candidate ingredients)

```
EVA:    choty  chtol   otaiin  chotal  cthol   otaiin  choky  qotyp
Decode: (?)    PIPER   [FUNC]  (?)     ACETUM  [FUNC]  (?)    [FUNC]
```

**PIPER** and **ACETUM** in an Aristolochia folio. Macer: *"aristolochiam cum pipere et aceto contra morsus serpentium"*.

### The functional word skeleton

The `[FUNC]` words have distinct positional behavior:

- **Connectors** (ch, ot, ok, or): uniform position = conjunctions (*cum, et, ac?*)
- **Terminators** (dy, oty, am): end-heavy (position 0.68-0.88) = clause enders
- **Openers** (dch, tch, pch, ych): start-heavy (position 0.13-0.35) = recipe starters

This gives us a grammatical skeleton: `[OPENER] (?) [CONN] INGREDIENT [CONN] INGREDIENT [CONN] (?) [TERM]`. That's a recipe instruction.

---

## Why "personal shorthand" and not "cipher" or "language"

The compound formation (prefix + root + suffix, with herbal roots embedded in pharma compounds) is how **Tironian-style abbreviation** works: prepositions fused to abbreviated content words.

We are **not** claiming these are standard Tironian notes from Schmitz's dictionary. The signs don't match classical Tironian glyphs. The **structural principle** (base signs modified by prefixes and suffixes to form compounds) is the same. This is a **personalized shorthand system** following the Tironian logic, not the Tironian alphabet.

- **Not a cipher**: every character-level substitution tested, 0-12% consistency (random = 4%)
- **Not a language**: no phonetic structure at any level
- **Why it resists decipherment**: memorized by one person through daily practice, no shared key

---

## Eight structural facts

All reproducible from the ZL transcription.

| # | Property | Significance |
|---|----------|:---:|
| 1 | Prefix + Root + Suffix morphology | Measured on 67% of pharma |
| 2 | Gallows 88% block-initial | p < 0.001 |
| 3 | n = 98% word-final | p < 0.001 |
| 4 | q = 99% word-initial | p < 0.001 |
| 5 | -am terminates clauses (72%) | 5.3x enrichment, p < 0.01 |
| 6 | f57v = alphabet table (17 symbols x 4) | p = 0.00016 |
| 7 | VMS best matches Macer Floridus type | #1 of 15 corpora |
| 8 | Herbal roots = pharma substrings | 635 occurrences |

---

## Seven candidate ingredient codes

From cross-folio fingerprint matching (tentative, may be artifactual):

| Root | Candidate | True Pos. | False Pos. | Jaccard |
|------|-----------|:-:|:-:|:---:|
| cth | acetum (vinegar) | 4 | 0 | 0.67 |
| yk | mel (honey) | 3 | 0 | 0.60 |
| cht | piper (pepper) | 3 | 0 | 0.75 |
| shocthy | mastix (mastic) | 2 | 0 | 1.00 |
| shotch | nigella (black cumin) | 2 | 0 | 1.00 |
| chk | oleum (oil) | 3 | 0 | 0.75 |
| otoly | sal (salt) | 2 | 0 | 0.67 |

Additional weaker candidates: ypch=aqua, dal=vinum, seees=lens, ykeed=nitrum, kald=ovum.

---

## What failed

- Phonetic decryption (K&A): 0-12% match on all alphabet mappings
- Co-occurrence mapping to Antidotarium Nicolai: Zipf artifact (p=0.92)
- Positional text alignment: 0/4 cross-corpus agreements
- EM/SA/constraint propagation: trivial solutions
- Recipe gap-filling: functional words dominate unknowns
- Galenic quality in k/t ratio: wrong direction
- Suffix -or/-al = cold plants: p=0.005 with Macer, p=0.386 with Circa Instans (not robust)

---

## Publications

| Document | DOI |
|----------|-----|
| Structural analysis (new) | [10.5281/zenodo.19543917](https://doi.org/10.5281/zenodo.19543917) |
| Corrective to V1 | [10.5281/zenodo.19477552](https://doi.org/10.5281/zenodo.19477552) |

PDFs also in `project_hope/`.

## Repository structure

```
project_hope/
  engine/                    Core analysis scripts (fingerprint, propagation, etc.)
  session_10/ to session_17/ All analysis sessions with scripts and results
  vms/                       Parsed VMS text (vms_structured.json, 38K words)
  hypothesis_registry.json   All evidence for/against each identification
  INSIGHTS.md                Complete findings
  BILAN_FINAL.md             Honest final assessment
  FORUM_POST.md              Forum discussion post
  *.pdf                      Publications
```

## Data requirements (not included, copyrighted)

- ZL transcription v3b: voynich.nu
- Macer Floridus: la.wikisource.org
- Avicenna, Collectio, Alphita, etc.: Wurzburg Arabic-Latin Corpus and published editions

## Who we are

**Guillaume Clement** - Director of AI at [Flow Line Integration](https://www.flowline-integration.com/). An engineer applying computational methods to an unsolved problem. [LinkedIn](https://www.linkedin.com/in/guillaume-clement-erp-cloud/)

**Claude** (Anthropic, Opus 4.6) - AI research partner for all computational analysis.

## License

Code: MIT. Publications: CC-BY 4.0. Copyrighted source texts not included.
