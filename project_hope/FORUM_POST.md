# The VMS as a personal shorthand pharmacopoeia: structural evidence

Hi all,

60 hours of computational analysis, 8 medieval pharmaceutical corpora, one corrected paper, and a lot of failed approaches. Here's what survived.

**Disclosure**: I previously published a phonetic decryption using King-Andrisani. It was wrong (Zipf artifact, p=0.92). Corrected on Zenodo. I bring this up because if I'm willing to retract my own work, maybe the structural findings below deserve a look.

---

## First: how we rebuilt the manuscript's structure

Before any decryption attempt, we parsed the entire ZL v3b transcription (38,456 words, 226 folios) into a structured database. Every word was decomposed by the morphological parser into its components: root, prefix, suffix, logogram status. This gives us a machine-readable map of the entire manuscript.

The manuscript breaks down into 8 sections with very different structures:

```
Section      Folios  Words    Blocks/folio  What it looks like
─────────────────────────────────────────────────────────────
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

We then classified every root by its frequency across the manuscript. Roots appearing in more than 20% of all folios (62 roots) are **functional/grammatical words** — too ubiquitous to be specific ingredients. Roots appearing in only a few folios are **content words** — candidates for plant names or ingredients. This separation is critical: it prevents the most common error in VMS analysis, which is assigning ingredient meanings to words that are actually grammatical connectors.

With this structural map, we can ask precise questions: which roots are shared between the herbal and pharma sections? Which are section-exclusive? Which have positional constraints? This is where the main discovery emerged.

## The core finding: herbal roots reappear inside pharma compounds

This is not about botanical IDs, decryption, or any specific theory. It's a measurable structural property of the text.

The root `pched` appears as a standalone word in herbal folio f26v. The **same root** appears embedded inside **635 compound words** in the pharmaceutical section:

```
Herbal:    pched, pchedy                    (standalone, f26v)
Pharma:    o·pched·y, qo·pched·edy, pched·al, pched·aiin    (compounds)
```

The compound structure decomposes as:

```
[prefix]  +  [root]  +  [suffix]
   o            pched       y
(logogram)   (content)   (grammar)
```

This happens systematically: **53% of pharma block openers** (154/286) contain a herbal plant root as a substring. The pharma section references the herbal section through embedded roots, exactly as a recipe collection references its ingredient catalogue.

This finding is **botanical-ID-agnostic**. Even if you swap every plant identification, the structural pattern — herbal roots appearing as substrings in pharma compounds — remains statistically visible. It's a property of the text, not of any interpretation.

---

## What this looks like in practice: decoded lines

Using 7 candidate ingredient codes from cross-folio fingerprint matching, plus 18 logograms and 62 classified functional words, here's what the text produces. **Bold** = candidate ingredient. `[FUNC]` = high-frequency grammatical word. `[logo]` = logogram. `(?)` = unknown.

### f48v, line 10 (best line, 3 candidate ingredients)

```
EVA:    tol   chedy  ytedy  ykeol  chdy   chdor  chtol    chdy   ytchedal  cthey   okar  ar  ary
Decode: (?)   [FUNC] [FUNC] (?)    [FUNC] (?)    PIPER    [FUNC] (?)       ACETUM  [FUNC][FUNC](?)
```

Three candidate ingredients: **PIPER** (pepper), then **ACETUM** (vinegar) a few words later, connected by functional words. The Macer Floridus chapter on Ruta describes exactly this combination: *"Gramina si rutae jungas salque piperque cumque mero"* — rue with salt, pepper, and wine. The `[FUNC]` words between ingredients likely correspond to Latin conjunctions and prepositions (*cum*, *et*, *in*).

### f48v, line 8 (2 candidate ingredients)

```
EVA:    oteody chkedy  okaiin chckhedy ykedy  oldy  otolychdy  kaly   tokar  otam
Decode: (?)    OLEUM   [FUNC] (?)      (?)    [FUNC] SAL       (?)    (?)    [FUNC+am]
```

**OLEUM** (oil) and **SAL** (salt), ending with the clause terminator `-am`. Macer's Ruta chapter: *"rutam cum oleo et sale ad matricem"* — rue with oil and salt for the womb.

### f9v, line 2 (Viola, 2 candidate ingredients)

```
EVA:    dchor  qoaiin chkaiin cthor  chol   chor   cphol  dy   oty   qokaiin  dy
Decode: [FUNC] [FUNC] OLEUM   ACETUM [FUNC] [FUNC] [FUNC] [END][END] [FUNC]   [END]
```

**OLEUM** (oil) followed immediately by **ACETUM** (vinegar), then a sequence of functional words ending with terminators. Macer's Viola chapter mentions violet oil prepared with vinegar: *"ex violis oleum... cum aceto"*.

### f28r, line 4 (Aristolochia, 2 candidate ingredients)

```
EVA:    choty  chtol   otaiin  chotal  cthol   otaiin  choky  qotyp
Decode: (?)    PIPER   [FUNC]  (?)     ACETUM  [FUNC]  (?)    [FUNC]
```

**PIPER** and **ACETUM** in an Aristolochia folio. Macer's Aristolochia chapter: *"aristolochiam cum pipere et aceto contra morsus serpentium"* — aristolochia with pepper and vinegar against snakebites.

### What the functional words tell us

The `[FUNC]` words between ingredients aren't noise — they have distinct positional behavior:

- **Connectors** (ch, ot, ok, or): uniform position across the line = conjunctions (cum, et, ac?)
- **Terminators** (dy, oty, am): end-heavy position (0.68–0.88) = clause/sentence enders
- **Openers** (dch, tch, pch, ych): start-heavy position (0.13–0.35) = paragraph/recipe starters

This gives us a grammatical skeleton even where we can't read specific words: `[OPENER] (?) [CONNECTOR] INGREDIENT [CONNECTOR] INGREDIENT [CONNECTOR] (?) [TERMINATOR]`. That's the structure of a recipe instruction.

---

## Why "personal shorthand" and not "cipher" or "language"

The compound formation mechanism (prefix + root + suffix, with herbal roots embedded in pharma compounds) is how **Tironian-style abbreviation** works: prepositions fused to abbreviated content words, grammatical endings attached as suffixes.

To be clear: I am **not** claiming these are standard Tironian notes from Schmitz's dictionary. The signs don't match classical Tironian glyphs. What I'm saying is the **structural principle** — base signs modified by prefixes and suffixes to form compound abbreviations — is the same. This is a **personalized shorthand system** following the Tironian logic, not the Tironian alphabet.

Why not a cipher:
- Every character-level substitution mapping tested: 0–12% consistency (random = 4%)
- No phonetic structure at any level

Why not a natural language:
- No sound-based encoding detected
- The positional constraints (n=98% final, q=99% initial) don't behave like phonetic characters

Why personal shorthand explains the resistance to decipherment:
- A system memorized through years of daily practice by one person
- No shared key, no dictionary, no second copy
- 600 years of searching for a cipher or a language when it's neither

---

## Eight structural facts (all reproducible from ZL transcription)

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

## What failed (long list)

- Phonetic decryption: 0-12% match on all alphabet mappings
- Co-occurrence mapping to Antidotarium Nicolai: Zipf artifact (p=0.92)
- Positional text alignment: 0/4 cross-corpus agreements
- EM/SA/constraint propagation: trivial solutions (common ingredients have no discriminant power)
- Recipe gap-filling: functional words dominate unknowns
- Galenic quality in k/t ratio: wrong direction
- Suffix -or/-al = cold plants: p=0.005 with Macer qualities, p=0.386 with Circa Instans (not robust)

---

## What's needed to go further

1. **More reliable botanical IDs.** The fingerprint method scales with anchor count. 16 anchors gave 7 candidates. 30+ could break into the medium-frequency ingredient range. Any approach to plant identification helps — even contested ones add statistical weight when multiple researchers converge.

2. **A prose herbal as reference corpus.** Macer is hexameter poetry — the word order is metrically distorted. A prose herbal (Tractatus de Herbis, Latin Dioscorides) would be better for any structural comparison.

3. **Independent verification.** Every structural claim above is testable from the ZL transcription. If anyone wants to check, the code is on GitHub.

---

Papers:
- Structural analysis: [DOI 10.5281/zenodo.19543917](https://doi.org/10.5281/zenodo.19543917)
- Corrective to previous work: [DOI 10.5281/zenodo.19477552](https://doi.org/10.5281/zenodo.19477552)
- Code and data: [github]

Not claiming to have solved anything. Theorizing that the herbal-pharma structural link is real, that 7 ingredient candidates are worth investigating, and that the personalized shorthand model fits the observed evidence better than cipher or language models. All data and code are open. Happy to be challenged on any of it.
