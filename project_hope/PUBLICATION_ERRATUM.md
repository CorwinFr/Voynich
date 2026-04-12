# Erratum and Reassessment:
# From Phonetic Decryption to Tironian Shorthand —
# Lessons from an Intellectual Black Hole

**Guillaume Clement**
Independent Researcher, Flow Line Integration
gcle1979@gmail.com

April 2026

---

## Foreword

This paper serves as both an erratum to our previous publication
(*Toward a Phonetic Decryption of the Voynich Manuscript*, Clement 2026,
DOI: 10.5281/zenodo.19477552) and as an independent study presenting
revised findings. **The previous paper contained a fundamental
methodological error that we retract and correct here.** We offer this
correction in the spirit of scientific honesty, and as a cautionary
tale about the extraordinary capacity of the Voynich Manuscript to
generate convincing but false results.

---

## 1. The Error in Our Previous Work

### 1.1 What We Claimed

In our April 2026 paper, we presented a computational pipeline based
on the King-Andrisani (2021) transliteration chart, which maps EVA
glyphs to Latin phonetic values. We reported:

- 89.3% validation against the Perseus Latin dictionary
- 90.6% "high-confidence" grading
- 33 identified pharmaceutical terms
- 7 of 12 Aurea Alexandrina ingredients on folio f103r
- A dual cipher system combining phonetic substitution with a nomenclator

### 1.2 What Went Wrong

Subsequent rigorous testing — including 18 additional analysis sessions
totaling approximately 35 hours of computational work — revealed that
**these results were artifacts of methodological bias**:

1. **Perseus validation is meaningless.** The Perseus Digital Library
   contains 265,419 Latin entries. Any combination of Latin-like syllables
   will match something in a dictionary of this size. An 89% match rate
   does not demonstrate decryption — it demonstrates that the search space
   is too permissive. A random syllable generator would achieve similar
   scores.

2. **The phonetic mapping has no statistical support.** We tested every
   possible character-level mapping between EVA and Latin alphabets.
   The best shift covers only 15% of character pairs — indistinguishable
   from random (expected: ~4% per shift in a 26-letter alphabet). A true
   phonetic cipher would show >80% consistency.

3. **The co-occurrence validation was a Zipf artifact.** Our claim that
   VMS ingredient frequencies matched the Antidotarium Nicolai was tested
   by permutation: p = 0.92. The apparent correlation was entirely
   explained by the universal tendency of word frequencies to follow
   Zipf's law in any text.

4. **The encoding has no phonetic logic.** Systematic testing of all
   plausible phonetic interpretations (Latin, Italian, Arabic, phonetic
   transcription) yielded 0–12% match rates. The VMS writing system does
   not encode sounds.

### 1.3 How This Happened

The Voynich Manuscript is, in a precise sense, an **intellectual black
hole** — a system with enough internal regularity to reward any hypothesis
with apparent confirmations, but enough complexity to resist definitive
refutation. The King-Andrisani transliteration produces Latin-looking
output because Latin is a flexible language and the Perseus dictionary
is vast. The ingredient matches appeared because medieval pharmacy uses
a small, frequently recurring set of substances. At every step, we found
what we were looking for — which is the hallmark of confirmation bias,
not discovery.

We apologize for the premature claims in our previous publication. The
error was not in the computational work itself, which was technically
sound, but in the **validation methodology**: we tested whether our
results *could* be Latin, not whether they *must* be Latin. The Voynich
Manuscript punishes this distinction with extraordinary efficiency.

---

## 2. What We Have Learned Since

Having recognized the failure of the phonetic approach, we spent the
subsequent 25+ hours testing the manuscript from first principles,
**without assuming any specific encoding scheme**. This led to a different
hypothesis: that the VMS uses a personal Tironian shorthand system — not
a phonetic cipher, but an arbitrary abbreviation code.

### 2.1 Methodology

We shifted from top-down decryption (assuming an encoding, trying to
read the text) to bottom-up structural analysis (measuring what the text
does, without assuming what it says). Our methods included:

**Cross-folio fingerprint matching.** For each unknown root, we compared
its presence/absence pattern across 115 botanically identified herbal
folios against ingredient presence patterns in 8 medieval pharmaceutical
corpora (Macer Floridus, Circa Instans, Canon Medicinae, Collectio
Salernitana, Alphita, Tacuinum Sanitatis, Galen, Abenguefit — over 7,000
entries total). This method makes no assumptions about the encoding — it
treats each root as a black box and tests whether its distribution matches
any known pharmaceutical substance.

**Permutation testing.** Every structural claim was tested against a null
hypothesis of random arrangement, using 10,000–100,000 permutations.

**Cross-corpus validation.** Any identification found using one corpus
(e.g., Macer Floridus) was independently tested against another
(e.g., Collectio Salernitana). Results that disagreed between corpora
were flagged as unreliable.

**Elimination before identification.** We systematically tested and
eliminated 10 alternative hypotheses (letter substitution, phonetic
encoding, frequency mapping, co-occurrence matching, etc.) before arriving
at the Tironian shorthand model. Each elimination is documented with its
test and p-value.

### 2.2 Structural Findings (Robust)

Eight structural properties of the VMS text are confirmed with statistical
significance, independent of any decoding hypothesis:

| Property | Evidence | Significance |
|----------|----------|-------------|
| Prefix + Root + Suffix morphology | 67% of pharma words decompose | Measured |
| Gallows characters 88% block-initial | Permutation test | p < 0.001 |
| 'n' at word-end in 98% of occurrences | Positional analysis | p < 0.001 |
| 'q' at word-start in 99% of occurrences | Positional analysis | p < 0.001 |
| '-am' at clause boundaries (72%) | 5.3× enrichment | p < 0.01 |
| Folio f57v = alphabet table | 52 logograms × 4 repetitions | p = 0.00016 |
| Best corpus match: Macer Floridus type | #1 of 15 corpora tested | 1.61× score |
| Herbal roots reappear as pharma substrings | 635 compound forms | Measured |

These findings hold regardless of whether the text is Tironian shorthand,
a cipher, a constructed language, or something else entirely.

### 2.3 Candidate Identifications (Fragile)

The fingerprint method produced 7 candidate ingredient codes. **We present
these as tentative hypotheses, not as confirmed decodings.** They may be
statistical artifacts arising from limited data and uncorrected multiple
testing.

| VMS Root | Candidate | True Positives | False Positives | Jaccard |
|----------|-----------|---------------|-----------------|---------|
| cth | acetum (vinegar) | 4 | 0 | 0.67 |
| yk | mel (honey) | 3 | 0 | 0.60 |
| cht | piper (pepper) | 3 | 0 | 0.75 |
| shocthy | mastix (mastic) | 2 | 0 | 1.00 |
| shotch | nigella (black cumin) | 2 | 0 | 1.00 |
| chk | oleum (oil) | 3 | 0 | 0.75 |
| otoly | sal (salt) | 2 | 0 | 0.67 |

If these identifications are correct, the codes show a base+modifier
structure (ch+k = oil, ch+t = pepper, sh+octhy = mastic, sh+otch = nigella)
consistent with Tironian-type abbreviation. However, we emphasize that this
structural observation depends entirely on the identifications being correct.

### 2.4 What Failed (Extensively)

| Method | Result | Lesson |
|--------|--------|--------|
| Positional text alignment | 0/4 cross-corpus agreements | VMS is not a linear copy of any known text |
| Global optimization (EM, SA) | Converges to trivial solutions | Common ingredients have no discriminant power |
| Constraint propagation | Blocked (insufficient anchors) | Need 38+ anchors; we have 15 |
| Galenic quality markers | Not robust across sources | p = 0.005 with Macer, p = 0.386 with Circa Instans |
| Recipe gap-filling | Functional words dominate | Cannot distinguish grammar from content |
| Multi-corpus death match | 0 Macer-Collectio agreements | Positional method is noisy |

---

## 3. The Tironian Shorthand Hypothesis

We propose — tentatively — that the Voynich Manuscript is a **personal
pharmacopoeia written in an idiosyncratic Tironian shorthand**. This
hypothesis accounts for:

- **The absence of phonetic structure**: Tironian abbreviations are
  arbitrary, not sound-based
- **The regular morphology**: prefix+root+suffix is the standard Tironian
  compound mechanism
- **The resistance to decipherment**: a personal system, never shared,
  would be opaque to anyone but its creator
- **The pharmaceutical content**: consistent with a working apothecary's
  reference tool
- **The catalogue structure**: 1 plant per page (herbal), 12 recipes
  per page (pharma) — a personal formulary

However, we cannot exclude alternative explanations:
- A constructed language with Tironian-like features
- An unknown natural language in an unknown script
- An elaborate hoax that mimics statistical regularities

The honest probability that this hypothesis is substantially correct is,
in our assessment, **moderate** — perhaps 40–60%. The probability that
our specific ingredient identifications are all correct is lower — perhaps
20–30%.

---

## 4. Reflections on Working with the Voynich Manuscript

The Voynich Manuscript is not merely unsolved; it is **actively
misleading**. Its statistical properties sit in a precise zone where they
are regular enough to invite analysis but irregular enough to defeat it.
Every approach we tested produced promising early results that dissolved
upon rigorous validation.

This is not a property of bad methodology. The manuscript genuinely
contains internal structure — our 8 confirmed structural facts demonstrate
this. But this structure is **insufficient to determine content**. It is
as if someone handed you a book in a language you don't speak: you can
identify that it has grammar, sentences, and paragraphs, but you cannot
read a single word.

We invested approximately 60 hours (the initial phonetic study plus the
subsequent structural analysis) across two major phases of research. The
first phase produced 52 pages of confident (and wrong) results. The second
produced 7 tentative (and possibly correct) identifications. The ratio of
effort to reliable output is humbling.

For future researchers, we offer this advice: **test every positive result
against an independent corpus before reporting it.** The Voynich Manuscript
will confirm your hypothesis using your training data. It will only
contradict you when you look at data you didn't use to build your model.
This is, we suspect, why it has resisted 600 years of genius.

---

## 5. Conclusion

We retract the phonetic decryption claims made in our previous publication
(*Toward a Phonetic Decryption of the Voynich Manuscript*, Clement 2026).
The King-Andrisani transliteration, while an interesting proposal, does
not survive rigorous statistical testing.

In its place, we offer a more modest result: 8 structural facts about
the VMS text, 7 candidate ingredient codes, and a hypothesis — Tironian
personal shorthand — that we believe is worth investigating further. These
results are fragile. They may be wrong. But they were produced by a
methodology that explicitly tests for and documents failure, which is,
we believe, the only honest way to approach this manuscript.

The Voynich Manuscript remains unsolved. If our work contributes anything,
it is a clearer map of where not to look — and a slightly better idea of
where to look next.

---

## References

[See full bibliography in companion document: PUBLICATION.md]

### Key references for this erratum:

- Clement, G. (2026). "Toward a Phonetic Decryption of the Voynich
  Manuscript." DOI: 10.5281/zenodo.19477552. **[RETRACTED — see Section 1]**
- King, L., Andrisani, D., Beasley, T.C., & Condo, G.M. (2021).
  "Transliteration of the Voynich Manuscript." [Working paper]
- Schmitz, W. (1893). *Commentarii Notarum Tironianarum*. Leipzig: Teubner.
- Zandbergen, R. & Landini, G. (2025). ZL Transcription v3b. voynich.nu.
- Odo Magdunensis. *De viribus herbarum* (Macer Floridus). Ed. Choulant, 1832.
- Platearius, M. *Circa Instans*. Ed. Dorveaux, 1913.
- De Renzi, S. (1852–1859). *Collectio Salernitana*. Naples.

---

*Corresponding author: gcle1979@gmail.com*
*All code and data: https://github.com/[repository]*
