# Exploring a Tironian Shorthand Hypothesis for the Voynich Manuscript:
# A Computational Study with Cautionary Results

**Guillaume Clement**
Flow Line Integration, April 2026

---

## Abstract

We present a computational investigation of the Voynich Manuscript (Beinecke
MS 408) that examines the hypothesis that its writing system functions as
personal Tironian shorthand. Through systematic analysis of the 38,456-word
text against 8 medieval pharmaceutical corpora comprising over 7,000 entries,
we identified 8 statistically significant structural regularities in the
writing system and produced 7 candidate ingredient identifications through
cross-folio fingerprint matching. We also report extensive negative results:
multiple decoding approaches—including positional alignment, constraint
propagation, and global optimization—failed to produce cross-validated
readings. While the structural findings are robust, the ingredient
identifications remain **tentative and possibly artifactual**. This paper
documents both the methodology and its limitations, in the hope that the
approach may inform future research even where our specific results do not
hold.

**Keywords:** Voynich Manuscript, Tironian notes, medieval pharmacy,
computational linguistics, hypothesis testing

---

## 1. Introduction

The Voynich Manuscript (Beinecke MS 408), radiocarbon-dated to 1404–1438
[McCrone 2009, Hodgins 2011], has resisted decipherment since its modern
rediscovery in 1912. Its 226 folios contain approximately 38,456 words
written in an unknown script, accompanied by illustrations of plants,
astronomical diagrams, bathing scenes, and pharmaceutical recipes.

The manuscript has attracted numerous decipherment claims, none universally
accepted. Previous approaches have treated the text as a cipher
[Friedman 1930s–1960s, Tiltman 1967], a constructed language
[Stolfi 1997], a hoax [Rugg 2004], or a natural language in an unknown
script [Bax 2014, Cheshire 2019]. Our investigation began without
commitment to any specific hypothesis and arrived at the Tironian shorthand
model through a process of elimination.

### 1.1 The Tironian Hypothesis

Tironian notes (*notae Tironianae*) were a Roman shorthand system attributed
to Marcus Tullius Tiro, Cicero's secretary. The system persisted in medieval
European usage through the 15th century, particularly in monasteries and
chanceries [Schmitz 1893, Cappelli 1899]. Key features include:

- **Base signs** modified with strokes or extensions to indicate related words
- **Logograms** for common function words (*et, est, cum, per*)
- **Arbitrary abbreviation** of content words, memorized through practice

We hypothesize—but cannot prove—that the Voynich script represents a
**personal, idiosyncratic** version of this tradition: a pharmacist's private
stenographic system for recording pharmaceutical knowledge.

### 1.2 Scope and Limitations

This paper presents a **speculative hypothesis** supported by statistical
regularities. We explicitly acknowledge:

- Our 7 candidate ingredient identifications may be statistical artifacts
- The positional alignment readings we attempted are almost certainly noisy
- We cannot distinguish our hypothesis from other models that predict
  similar structural regularities
- Complete decipherment, if possible at all, is beyond our current methods

---

## 2. Data

### 2.1 The VMS Text

We used the ZL transcription (Zandbergen & Landini, version 3b, May 2025),
which provides an EVA (European Voynich Alphabet) rendering of each glyph.
The transcription was parsed into a structured JSON representation with
morphological decomposition: 38,456 words across 226 folios organized in
8 sections (herbal_a: 111 folios, herbal_b: 32, pharma: 24, balnea: 20,
cosmo: 22, astro: 10, bio: 6, volvelle: 1).

### 2.2 Botanical Identifications

We compiled 115 botanical identifications from multiple independent
researchers spanning 100 years of analysis:

| Researcher | Period | Identifications | Approach |
|-----------|--------|-----------------|----------|
| Ethel Voynich & O'Neill | 1920s–1944 | ~20 | Visual comparison |
| Petersen | 1950s | ~30 | Morphological analysis |
| Tiltman | 1967 | Commentary | Cryptographic + botanical |
| Edith Sherwood | 2008–2016 | 124 (anagram-based) | Italian anagram + visual |
| Dana Scott | 2012–present | ~50 | Systematic taxonomy |
| Tucker & Janick | 2013–2019 | 166 (New World thesis) | Ethnobotanical |
| Bax | 2014 | ~10 | Linguistic + visual |
| Vatne | 2022 | ~20 | Morphological reanalysis |

These identifications are **highly contested**—researchers frequently disagree
on the same folio. We used them as working hypotheses, not established facts.
Where 2+ researchers agreed on a genus, we gave higher weight.

### 2.3 Reference Corpora

We assembled 8 medieval pharmaceutical corpora, tokenized and annotated with
ingredient, quality, and preparation markers:

| Code | Source | Period | Entries | Ingredients | Editor |
|------|--------|--------|---------|-------------|--------|
| S01_AN | Antidotarium Nicolai | 12th c. | 150 | 890 | van den Berg 1917 |
| S02_CI | Circa Instans | c. 1150 | 141 | 141 | Dorveaux 1913 |
| S05_MACER | Macer Floridus | 11th c. | 77 | 171 | Choulant 1832 |
| S08_AVICENNA | Canon Medicinae | 11th c. | 2,362 | 257 | Würzburg Corpus |
| S09_COLLECTIO | Collectio Salernitana | Medieval | 3,680 | 333 | De Renzi 1852 |
| S10_ALPHITA | Alphita | 13th c. | 1,714 | 324 | Mowat 1887 |
| S12_TACUINUM | Tacuinum Sanitatis | 11th c. | 312 | 129 | Schott 1531 |
| S14_GALEN | De simplici medicina | 2nd c. | 91 | 118 | Würzburg Corpus |

The Würzburg Arabic-Latin Corpus provided structured XML versions of Arabic
medical texts in Latin translation.

The full Macer Floridus text (2,270 hexameter verses, 77 plant chapters) was
downloaded from la.wikisource.org and parsed with custom regex-based ingredient
extraction covering 24 ingredient categories.

---

## 3. Methodology

### 3.1 Structural Analysis

We tested positional, distributional, and morphological properties of the
VMS text using permutation tests and enrichment analysis.

**Positional analysis**: For each character, compute its distribution across
word positions (start, middle, end). Test significance by permuting character
positions within words and comparing observed vs. expected distributions.

**Block-initial gallows test**: Count gallows characters (p, t, k, f) in
first vs. non-first word of each text block. Significance via permutation
test (100,000 iterations).

**Section vocabulary**: For each root, count occurrences per manuscript
section. Identify section-exclusive vocabulary using chi-squared tests.

### 3.2 Corpus Matching

To determine what TYPE of text the VMS resembles, we compared its
word-frequency profile against 15 medieval corpora using:

1. Rank-frequency correlation (Spearman ρ)
2. Vocabulary overlap ratio
3. Type-token ratio comparison
4. Hapax legomena proportion

### 3.3 Cross-Folio Fingerprint Matching

This is the **core identification method** and the only one that produced
results surviving cross-validation.

**Principle**: If a VMS root represents ingredient X, then that root should
appear in exactly those herbal folios whose plant uses ingredient X.

**Procedure**:
1. For each identified herbal folio, determine the corresponding Macer
   chapter (via Sherwood botanical identification)
2. Extract the ingredient list for that Macer chapter (regex on full text)
3. For each Macer ingredient, build a binary "expected presence" vector
   across the identified folios
4. For each unknown VMS root, build a binary "actual presence" vector
   across the same folios
5. Compare vectors: compute Jaccard similarity and Fisher exact test p-value
6. Accept candidates with: Jaccard ≥ 0.3, TP ≥ 3, FP ≤ 1, p < 0.05

**Why this method**: It uses only presence/absence patterns and requires
no assumptions about word order, text alignment, or encoding logic. It
treats the encoding as a black box—whatever the root means, it should
appear where that meaning is relevant.

**Limitation**: The method is constrained by the number of identified
anchor folios. With 16 anchors (Sherwood identifications that match Macer
chapters), only ingredients with distinctive presence patterns can be
detected. Common ingredients (appearing in >50% of chapters) are
indistinguishable from functional words.

### 3.4 Positional Alignment (Death Match)

We attempted word-by-word alignment between VMS folios and corresponding
Macer chapters:

1. Extract significant Latin words from the Macer chapter with normalized
   positions (0–1 through the text)
2. Extract VMS roots with normalized positions (0–1 through the folio)
3. Use confirmed ingredient identifications as positional calibration anchors
4. For each unknown root, find the closest Latin word by adjusted position

**Critical caveat**: This method assumes a roughly linear correspondence
between VMS and Macer text order. Cross-corpus validation (Macer vs.
Collectio Salernitana) showed **0 agreements** for the same roots,
indicating the method produces noise for non-anchor words. We report the
f48v reading as **illustrative only**, not as a validated result.

### 3.5 Global Optimization

We tested three global approaches to simultaneously assign plants to folios
and ingredients to roots:

- **Expectation-Maximization** (alternating plant assignment and ingredient
  mapping)
- **Simulated Annealing** on graph isomorphism (VMS co-occurrence graph vs.
  Macer ingredient graph)
- **Constraint Propagation** (Sudoku-like cascading assignment)

All three converged to trivial solutions (most folios assigned to the
richest Macer chapters) because common ingredients dominate the signal.
These negative results are reported in Section 5.

### 3.6 Independent Validation

For each candidate identification, we applied distributional tests
**independent** of the method that produced it:

- **Section distribution**: Does the root appear in the expected sections?
- **Context analysis**: What types of words surround it?
- **Cross-corpus consistency**: Does the identification hold when tested
  against Collectio Salernitana instead of Macer?
- **Fingerprint precision**: What is the false-positive rate on held-out
  anchor folios?

---

## 4. Results

### 4.1 Structural Regularities

Eight structural properties were confirmed with statistical significance:

| # | Property | Evidence | p-value |
|---|----------|----------|---------|
| 1 | Prefix + root + suffix morphology | 67% of pharma words decompose | — |
| 2 | Gallows 88% block-initial | Permutation test, 100K iterations | < 0.001 |
| 3 | Character 'n' at word-end (98%) | Positional analysis | < 0.001 |
| 4 | Character 'q' at word-start (99%) | Positional analysis | < 0.001 |
| 5 | Suffix '-am' at clause boundaries (72%) | 5.3× enrichment | < 0.01 |
| 6 | Folio f57v as alphabet table | 52 consecutive logograms × 4 repetitions | 0.00016 |
| 7 | VMS best matches Macer Floridus type | Ranked #1 of 15 corpora (1.61×) | — |
| 8 | Herbal roots as substrings in pharma compounds | 635 compound occurrences | — |

These structural findings are **independent of the Tironian hypothesis**
and hold regardless of the encoding's nature. They establish that the VMS
text has regular morphological structure consistent with a pharmaceutical text.

**Additional structural findings**:
- 53% of pharma block openers (154/286) contain a known plant name root,
  linking recipes to their target plant
- 62 high-frequency roots (>20% of folios) are classified as functional
  (grammatical) words, not content words
- 56% of pharma vocabulary is section-exclusive, consistent with specialized
  technical content

### 4.2 Candidate Ingredient Identifications

The fingerprint method produced 7 candidate identifications at our acceptance
threshold. **We emphasize that these are candidates, not confirmed decodings.**

| VMS Root | Candidate Latin | TP | FP | FN | Jaccard | p-value |
|----------|----------------|----|----|-----|---------|---------|
| cth | acetum (vinegar) | 4 | 0 | 2 | 0.67 | < 0.05 |
| yk | mel (honey) | 3 | 0 | 2 | 0.60 | < 0.05 |
| cht | piper (pepper) | 3 | 0 | 1 | 0.75 | < 0.05 |
| shocthy | mastix (mastic) | 2 | 0 | 0 | 1.00 | < 0.05 |
| shotch | nigella (black cumin) | 2 | 0 | 0 | 1.00 | < 0.05 |
| chk | oleum (oil) | 3 | 0 | 1 | 0.75 | < 0.05 |
| otoly | sal (salt) | 2 | 0 | 1 | 0.67 | < 0.05 |

Additional candidates with weaker evidence:

| VMS Root | Candidate | Method | Confidence |
|----------|-----------|--------|------------|
| ypch | aqua (water) | Fingerprint, 81% accuracy on 16 anchors | 0.75 |
| dal | vinum (wine) | Fingerprint, 100% precision on 4 folios | 0.80 |
| seees | lens (lentil) | Positional, 0 false positives | 0.75 |
| ykeed | nitrum (saltpeter) | Positional, 0 false positives | 0.70 |

**Why these may be artifacts**:
- With 16 anchor folios and ~250 roots, random patterns can produce
  Jaccard ≥ 0.3 by chance. We did not correct for multiple testing.
- The "confirmed" roots (cth, yk, cht) are among the most frequent in
  the VMS. Frequent roots have more opportunity to produce coincidental
  fingerprint matches.
- The Macer Floridus ingredient lists used as reference are extracted by
  regex from a poem, introducing potential parsing errors.

### 4.3 Evidence for Tironian-Type Composition

If the candidate identifications are correct, the codes exhibit a
base+modifier structure reminiscent of Tironian notes:

- Base `ch`: ch+k (oleum), ch+t (piper)
- Base `sh`: sh+octhy (mastix), sh+otch (nigella)

Herbal roots appear as substrings in longer pharma words, consistent with
Tironian compound formation: `pched` (lens, f26v) → `opchedy`
(= `o`(with?) + `pched`(lens) + `y`(in?)).

This observation is **consistent with but not exclusive to** Tironian
shorthand. Other abbreviation systems could produce similar patterns.

### 4.4 Attempted Recipe Reading

Using positional alignment on folio f48v (identified as *Ruta graveolens*
by consensus of Sherwood, Tucker & Janick), we produced a tentative reading
of lines 8 and 10:

**Line 10**: [?] [?] [?] **MEL** [?] [?] **PIPER** [?] [?] **ACETUM** [?] [?] [?]

The three bolded words (if correctly identified) form a pharmaceutically
coherent combination: honey + pepper + vinegar = *oxymel cum pipere*
(spiced oxymel), a preparation described in the Macer Ruta chapter.

**This reading is illustrative only.** The non-bolded words are unknown,
the positional method is unreliable (0 cross-corpus agreement), and the
coherence may be coincidental—honey, pepper, and vinegar are among the
most common medieval pharmaceutical ingredients.

---

## 5. Negative Results

We consider these failures as important as the positive results, since
they constrain future research.

### 5.1 Methods That Failed

| Method | Expectation | Result | Lesson |
|--------|-------------|--------|--------|
| Positional alignment | Read recipes by text alignment | 0/4 cross-corpus agreement | VMS is not a linear copy |
| EM optimization | Joint plant-ingredient assignment | Converges to trivial solution | Common ingredients dominate |
| Simulated annealing (graph matching) | Structural isomorphism | All folios → richest chapters | Too few discriminant anchors |
| Constraint propagation | Cascading Sudoku-like solving | Blocked at margin=0 | 15 anchors insufficient |
| Co-occurrence mapping | Root pairs → ingredient pairs | Zipf artifact (p=0.92) | Frequency confounds |
| Galenic quality encoding | k/t ratio = hot/cold | Wrong direction | Also: suffix -or/-al = cold at p=0.005 with Macer qualities, but p=0.386 with Circa Instans |
| Recipe gap-filling | Identify missing ingredients | Functional words dominate unknowns | Cannot distinguish grammar from content |

### 5.2 The Short-Root Problem

23 of our 61 candidate roots are 2–3 characters long. These match inside
longer words as substrings, inflating apparent decode rates. Our "strict"
decode rate (roots ≥ 4 characters only) is **13%**, not the 36% obtained
with all roots. Four roots (`ke`, `ko`, `po`, `do`) appear less than 10%
as standalone words and should never be used for matching.

### 5.3 The Chicken-and-Egg Problem

To identify plants, we need ingredient codes. To identify ingredient codes,
we need identified plants. We broke this cycle for the 7 easiest ingredients
(those with highly distinctive fingerprints), but the remaining ingredients
are either too common (appearing in >50% of chapters, indistinguishable from
functional words) or too rare (appearing in 1–2 folios, insufficient for
statistical testing).

---

## 6. Discussion

### 6.1 What the Structural Findings Tell Us

Regardless of whether our ingredient identifications are correct, the 8
structural regularities demonstrate that:

1. The VMS text is **not random** — it has consistent morphological structure
2. It is **not a simple substitution cipher** — there is no character-level
   correspondence to any alphabet
3. It is **consistent with pharmaceutical content** — it best matches a
   medieval herbal among 15 tested corpora
4. It contains **section-specific vocabulary** — different sections use
   different words, as expected in a multi-topic reference work

### 6.2 The Catalogue Interpretation

The VMS appears to be a **personal pharmacopoeia** rather than a copy of
any specific text:

- Herbal section: 1–2 text blocks per folio (one plant per page)
- Pharma section: ~12 blocks per folio (multiple recipes per page)
- This matches the format of medieval pharmaceutical catalogues (Circa
  Instans, Tacuinum Sanitatis) rather than narrative or poetic texts

This explains why positional alignment against Macer (a poem with
metrically-constrained word order) performs poorly: the VMS author
was compiling his own catalogue from multiple sources, not copying
any single text.

### 6.3 Why Tironian?

The Tironian hypothesis is the most parsimonious explanation we found, but
it is not the only one consistent with the evidence. Alternative explanations
include:

- A **constructed language** with Tironian-like features
- A **pictographic system** unrelated to Latin abbreviation traditions
- An **elaborate hoax** that mimics statistical properties of real text

We favor the Tironian hypothesis because it explains both the structural
regularities AND the resistance to decipherment: a personal shorthand system,
developed through years of daily practice, would be legible only to its
creator. But we cannot exclude the alternatives.

### 6.4 Path Forward

If this hypothesis has merit, progress requires:

1. **More botanical identifications** — the fingerprint method's power
   scales directly with the number of identified anchor folios
2. **A prose herbal in Latin** — the Tractatus de Herbis (BL Egerton 747)
   or Dioscorides' De Materia Medica would provide better alignment targets
   than Macer's hexameter poetry
3. **Glyph-level analysis** — if the writing system uses Tironian-type
   base+modifier composition, visual clustering of glyph shapes should
   reveal semantic categories

---

## 7. Conclusion

We present a computational study exploring the hypothesis that the Voynich
Manuscript is written in personal Tironian shorthand. Our structural analysis
is robust: 8 statistical regularities confirm the text has consistent
morphological structure matching a pharmaceutical reference work. Our
ingredient identifications are fragile: 7 candidates from fingerprint
matching that may be artifacts of limited anchor data and multiple testing.

The most honest assessment of our work: we have demonstrated **what the VMS
text looks like** (a pharmaceutical catalogue with regular morphology) more
convincingly than **what it says** (specific ingredient codes that remain
unverified). We hope the structural framework and the methodological lessons
—particularly the extensive negative results—will be useful to future
researchers, even if our specific identifications prove incorrect.

The Voynich Manuscript may be, as we speculate, a pharmacist's personal
notebook in invented shorthand. Or it may be something else entirely. After
600 years and 35 hours of computational analysis, we are certain only that
it is not random, not a simple cipher, and not easily solved.

---

## Acknowledgments

This research was conducted through a human-AI collaboration: Guillaume
Clement provided domain expertise, strategic direction, botanical knowledge,
and critical evaluation; Claude (Anthropic) performed computational analysis,
corpus processing, and statistical testing. All methodological decisions and
hypotheses were jointly developed.

We thank the Voynich research community, particularly René Zandbergen for
the ZL transcription, Edith Sherwood for botanical identifications, and
the Beinecke Rare Book & Manuscript Library for making the manuscript
digitally accessible.

---

## References

### Primary Sources
- Avicenna (Ibn Sīnā). *Canon Medicinae*. Latin trans., Würzburg Arabic-Latin Corpus.
- Galen. *De simplici medicina*. Latin trans., Würzburg Arabic-Latin Corpus.
- Ibn Butlan. *Tacuinum Sanitatis*. Latin trans., Strasbourg: Schott, 1531.
- Ibn Wāfid. *Liber aggregatus in medicinis simplicibus*. Würzburg Arabic-Latin Corpus.
- Nicolaus Salernitanus. *Antidotarium Nicolai*. Ed. W.S. van den Berg, Brill, 1917.
- Odo Magdunensis. *De viribus herbarum* (Macer Floridus). Ed. Choulant, 1832.
- Platearius, Matthaeus. *Circa Instans*. Ed. Dorveaux, 1913.
- al-Rāzī. *Antidotarium*. Würzburg Arabic-Latin Corpus.

### Voynich Manuscript Studies
- Bax, S. (2014). "A proposed partial decoding of the Voynich script." *CL2014*.
- Cheshire, G. (2019). "The Language and Writing System of MS408." *Romance Studies* 37(4).
- Currier, P. (1976). "Papers on the Voynich Manuscript." *New Research on the VM*.
- D'Imperio, M. (1978). *The Voynich Manuscript: An Elegant Enigma*. NSA.
- Friedman, W. & E. (1930s–60s). Unpublished working papers. NSA archives.
- Hodgins, G. (2011). "Radiocarbon Dating of Parchment." In *Proceedings of AMS-12*.
- Kennedy, G. & Churchill, R. (2006). *The Voynich Manuscript*. Orion.
- McCrone, W. (2009). "Pigment Analysis of the VM." *The Microscope* 57(2).
- Rugg, G. (2004). "An Elegant Hoax?" *Cryptologia* 28(1), 31–46.
- Stolfi, J. (1997). "A Voynich Manuscript Word Model." Unpublished.
- Tiltman, J. (1967). "The Voynich Manuscript: The Most Mysterious Manuscript in the World." NSA Technical Journal.
- Zandbergen, R. (2025). "The Voynich MS." voynich.nu.

### Botanical Identifications
- Petersen, T. (1953). Unpublished notes on VM plant identifications.
- Scott, D. (2012–present). "Voynich Manuscript Botanical List." voynichbotany.wordpress.com.
- Sherwood, E. (2008–2016). "The Voynich Botanical Plants." edithsherwood.com.
- Tucker, A.O. & Janick, J. (2016). "Identification of phytomorphs in the Voynich Codex." *Horticultural Reviews* 44, 1–64.
- Tucker, A.O. & Janick, J. (2019). *Flora of the Voynich Codex*. Springer.
- Vatne, S.B. (2022). "The morphology of the Voynich plants." crackingthevoynichcipher.com.

### Medieval Pharmacy and Abbreviation Systems
- Cappelli, A. (1899). *Lexicon Abbreviaturarum*. Milan: Hoepli.
- Connelly, E. et al. (2020). "Data Mining a Medieval Medical Text Reveals Patterns in Ingredient Choice." *mBio* 11(1).
- De Renzi, S. (1852–1859). *Collectio Salernitana*. 5 vols. Naples.
- De Vos, P. (2010). "European Materia Medica in Historical Texts." *J. Ethnopharmacol.* 132(1), 28–47.
- Kyle, S. (2017). *Medicine and Humanism in Late Medieval Italy*. Routledge.
- Lev, E. & Amar, Z. (2007). "Practice vs Theory: Medieval Materia Medica According to the Cairo Genizah." *Medical History* 51(4), 507–526.
- Mowat, J. (1887). *Alphita: A Medico-Botanical Glossary*. Oxford: Clarendon.
- Schmitz, W. (1893). *Commentarii Notarum Tironianarum*. Leipzig: Teubner.

### Digital Resources
- Beinecke Digital Library: collections.library.yale.edu/catalog/2002046
- DALME Project: dalme.org (Documentary Archaeology of Late Medieval Europe)
- Würzburg Arabic-Latin Corpus: arabic-latin-corpus.philosophie.uni-wuerzburg.de
- ZL Transcription: voynich.nu

---

## Appendix A: Eliminated Hypotheses

| Hypothesis | Test | Result | Session |
|-----------|------|--------|---------|
| Letter substitution cipher | Volvelle f57v as key | Score 0.00 | 12 |
| f↔p meaningful variants | Permutation test | p = 1.0 (noise) | 13 |
| VMS = recoded Antidotarium Nicolai | Co-occurrence test | p = 0.92 (Zipf artifact) | 13 |
| i-glyph count = dose number | Distribution analysis | i₂ = 81% in herbal (inverted) | 14 |
| Encoding has phonetic logic | All alphabet mappings | 0–12% match | 14 |
| Root 'che' = caro (flesh) | Frequency analysis | In 80% of folios = functional | 15 |
| k/t ratio = galenic quality | Permutation + cross-source | Wrong direction; p=0.386 with CI | 16–17 |
| Gap-filling identifies ingredients | Constraint intersection | ch → 6 different ingredients = functional | 16 |
| Death match reads recipes | Cross-corpus validation | 0/4 Macer-Collectio agreements | 17 |
| EM/SA global optimization | Convergence analysis | Trivial solutions (richest chapters) | 17 |

## Appendix B: Code and Data Availability

All analysis scripts, intermediate results, and the hypothesis registry
(tracking all evidence for and against each identification, with nothing
deleted) are available at: https://github.com/[repository]

Key scripts in `project_hope/engine/`:
- `fingerprint_115.py` — Cross-folio fingerprint matching
- `death_match_auto.py` — Auto-iterating positional alignment
- `propagation_v3.py` — Rarity-weighted constraint propagation
- `isomorphism.py` — Graph matching via simulated annealing
- `validate_tier3.py` — Independent distributional validation
