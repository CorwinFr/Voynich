# Voynich Manuscript Structural Analysis

### A computational investigation by Guillaume Clement & Claude (Anthropic)

> **Status:** This repository contains structural analysis code, results, and two publications. The structural findings (8 confirmed properties) are robust. The ingredient identifications (7 candidates) are tentative and may be artifactual. A previous phonetic decryption attempt has been corrected. See publications below.

---

## What this is

A computational structural analysis of the Voynich Manuscript (Beinecke MS 408, c. 1404-1438), testing the hypothesis that its writing system is a form of personalized shorthand used by a medieval pharmacist.

**~60 hours of analysis across 18 sessions**, testing the VMS text (38,456 words, ZL transcription v3b) against 8 medieval pharmaceutical corpora totaling 7,000+ entries.

## Key findings

### Structural (robust, reproducible)

1. **Prefix + Root + Suffix morphology** in 67% of pharmaceutical words
2. **Gallows 88% block-initial** (p < 0.001) — recipe/paragraph openers
3. **n = 98% word-final, q = 99% word-initial** — positional markers
4. **-am terminates clauses** with 5.3x enrichment (p < 0.01)
5. **f57v = alphabet table** — 17 symbols x 4 repetitions (p = 0.00016)
6. **Best corpus match: Macer Floridus** — #1 of 15 tested
7. **Herbal roots reappear as substrings in pharma compounds** — 635 occurrences
8. **53% of pharma openers contain a plant name root** — recipes named by plant

### Ingredient candidates (fragile, possibly artifactual)

7 candidates from cross-folio fingerprint matching: cth=acetum, yk=mel, cht=piper, shocthy=mastix, shotch=nigella, chk=oleum, otoly=sal. Zero false positives but limited anchor data (16 folios). Not corrected for multiple testing.

### What failed

Phonetic decryption, positional alignment (0/4 cross-corpus), EM optimization, simulated annealing, constraint propagation, co-occurrence mapping (Zipf artifact p=0.92), recipe gap-filling. All documented in the publications.

## Publications

| Document | DOI | Description |
|----------|-----|-------------|
| Structural Analysis (new) | [10.5281/zenodo.19543917](https://doi.org/10.5281/zenodo.19543917) | Full structural findings, candidate identifications, failed approaches |
| Corrective to V1 (erratum) | [10.5281/zenodo.19477552](https://doi.org/10.5281/zenodo.19477552) | V2 correcting the methodological bias in V1's phonetic approach |

## Repository structure

```
project_hope/
  engine/                    — Core analysis scripts
    fingerprint_115.py       — Cross-folio fingerprint matching
    death_match_auto.py      — Positional alignment (auto-iterating)
    propagation_v3.py        — Constraint propagation
    isomorphism.py           — Graph matching via simulated annealing
    validate_tier3.py        — Independent distributional validation
  session_16/                — Surgical strike analysis (6 approaches)
  session_17/                — Decisive attack + preparation scripts
  vms/                       — Parsed VMS text (vms_structured.json)
  hypothesis_registry.json   — All evidence for/against each identification
  INSIGHTS.md                — Complete findings summary
  BILAN_FINAL.md             — Honest final assessment
  FORUM_POST.md              — Forum discussion post
  *.pdf                      — Final publications
```

## Data requirements (not included — copyrighted)

The analysis requires medieval pharmaceutical corpora that cannot be redistributed:
- Macer Floridus (De viribus herbarum) — available from la.wikisource.org
- ZL transcription v3b — available from voynich.nu
- Avicenna Canon, Collectio Salernitana, Alphita, etc. — from the Würzburg Arabic-Latin Corpus and published editions

## How to reproduce

1. Obtain the ZL v3b transcription from voynich.nu
2. Parse it using the build scripts in `project_hope/vms/`
3. Obtain Macer Floridus text from la.wikisource.org
4. Run `project_hope/engine/fingerprint_115.py` for ingredient identification
5. Run `project_hope/session_16/frappe6_fonctionnels.py` for functional word classification

All structural claims are testable from the ZL transcription alone.

## Who we are

**Guillaume Clement** — Director of AI at [Flow Line Integration](https://www.flowline-integration.com/). Not a medievalist, not a cryptographer — an engineer applying computational methods to an unsolved problem.

**Claude** (Anthropic, Opus 4.6) — AI research partner. All computational analysis, corpus processing, and statistical testing performed collaboratively.

## License

Code: MIT. Publications: CC-BY 4.0. Copyrighted source texts (corpora) not included.
