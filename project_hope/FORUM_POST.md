# The VMS as a personal shorthand pharmacopoeia: structural evidence

**Disclosure**: I previously published a phonetic decryption using King-Andrisani. It was wrong. Corrected on Zenodo. If I'm willing to correct my own work publicly, maybe these structural findings deserve a look.

---

## The idea

A 15th-century apothecary invented his own shorthand to record his pharmaceutical knowledge. Not a cipher, not a language: **one man's private stenography**, memorized through years of daily practice.

Every word in the VMS is built from three parts:

```
[prefix]  +  [root]   +  [suffix]
   o          pched         y
 ("with")   (lentil)    (grammar)
```

The prefix is a logogram (a single-character word meaning a preposition: o="with", d="from", y="in"). The root is the content (a plant name or ingredient, arbitrarily abbreviated). The suffix marks grammar (-am = clause terminator, -or/-al/-dy = other grammatical roles).

This is how Tironian-style abbreviation works in medieval manuscripts: prepositions fused to abbreviated content words. We're not claiming standard Tironian notes from Schmitz's dictionary. The glyphs don't match. The **structural principle** (base + modifier compounds) is the same.

---

## The structural proof: herbal roots inside pharma compounds

Every herbal folio has a **unique first word** that acts as that plant's code. Folio f26v starts with `pched`, folio f48v starts with `pcheod`, folio f9v starts with `foch`, and so on. Each plant has its own identifier, like entries in a catalogue.

Now the key: the root `pched` (the code for f26v's plant) doesn't just appear on that herbal page. The **same root** appears embedded inside **635 compound words** in the pharmaceutical section:

```
Herbal:   pched, pchedy                  (standalone, naming the plant)
Pharma:   o·pched·y, pched·al, pched·aiin   (compounds in recipe text)
```

This happens systematically. **53% of pharma recipe openers** (154 out of 286) contain a herbal plant root as a substring. Each recipe is titled by its target plant, using the same code that names the plant in the herbal section.

This is **botanical-ID-agnostic**: even if every plant identification is wrong, the structural link between herbal and pharma sections remains visible. It's a property of the text itself.

---

## The writing system's architecture

We parsed all 38,456 words (ZL v3b) and classified them:

**18 logograms** (single-character function words): o, l, d, r, v, x, k, m, f, t, y, c, s + digraphs sh, ch, etc. These appear to be prepositions and conjunctions (*cum, et, in, de, per, recipe, misce*...).

**62 functional roots** (in >20% of all folios): too ubiquitous to be ingredients. They are the grammar:
- **Connectors** (ch 97%, ot 85%, ok 84%): uniform position in lines = conjunctions
- **Terminators** (dy 62%, oty 35%, am 24%): cluster at line ends = clause/sentence enders
- **Openers** (dch 43%, tch 38%, pch 29%): cluster at line starts = recipe/paragraph starters

**~250 content roots** (in <20% of folios): these are the actual plants, ingredients, body parts, diseases. The specific content.

This separation is critical. Any approach that assigns a specific meaning to `ch` (which appears in 97% of all folios) is producing an artifact. Previous decryption attempts, including my own V1, made this error.

---

## What a recipe looks like structurally

With this framework, a VMS recipe line has a readable skeleton:

```
[OPENER] (unknown) [CONNECTOR] INGREDIENT [CONNECTOR] INGREDIENT [CONNECTOR] (unknown) [TERMINATOR]
```

Concrete example, f48v line 10:

```
EVA:    tol   chedy  ytedy  ykeol  chdy   chdor  chtol    chdy   ytchedal  cthey   okar  ar  ary
Role:   (?)   [CONN] [CONN] (?)    [CONN] (?)    PIPER    [CONN] (?)       ACETUM  [CONN][CONN](?)
```

The connectors (ch, ok, ar) separate content words. Two candidate ingredients (PIPER, ACETUM) appear in their expected position. This folio is identified as Ruta (rue), and the Macer Floridus Ruta chapter prescribes exactly pepper with vinegar (*piperque cumque mero*).

Another example, f48v line 8:

```
(?)  OLEUM  [CONN]  (?)  (?)  [CONN]  SAL  (?)  (?)  [CONN+am]
```

Oil and salt, ending with the clause terminator -am. Macer Ruta: *"rutam cum oleo et sale ad matricem"* (rue with oil and salt for the womb).

---

## Eight statistical facts

All testable from the ZL transcription:

| Property | Significance |
|----------|:---:|
| Prefix + Root + Suffix morphology | 67% of pharma words |
| Gallows 88% block-initial | p < 0.001 |
| n = 98% word-final | p < 0.001 |
| q = 99% word-initial | p < 0.001 |
| -am terminates clauses (72%) | 5.3x enrichment, p < 0.01 |
| f57v = alphabet table (17 symbols x 4) | p = 0.00016 |
| Best corpus match: Macer Floridus type | #1 of 15 corpora |
| Herbal roots = pharma substrings | 635 occurrences |

## Seven candidate ingredient codes

Cross-folio fingerprint matching (tentative):

| Root | Candidate | TP | FP | Method |
|------|-----------|:--:|:--:|--------|
| cth | acetum (vinegar) | 4 | 0 | Fingerprint, 6 anchors |
| yk | mel (honey) | 3 | 0 | Fingerprint, 6 anchors |
| cht | piper (pepper) | 3 | 0 | Fingerprint, 19 anchors |
| shocthy | mastix (mastic) | 2 | 0 | Fingerprint, 100 anchors |
| shotch | nigella (black cumin) | 2 | 0 | Fingerprint, 100 anchors |
| chk | oleum (oil) | 3 | 0 | Triangulation |
| otoly | sal (salt) | 2 | 0 | Triangulation |

These may be artifacts. 16 anchor folios, ~250 roots, no multiple testing correction.

## What failed

Phonetic decryption (0-12%), positional alignment (0/4 cross-corpus), EM optimization (trivial solutions), constraint propagation (blocked), co-occurrence (Zipf p=0.92), galenic k/t (wrong direction).

## What would help

More botanical IDs (the fingerprint method scales directly with anchor count), a prose herbal as reference corpus (Macer is poetry, distorts word order), and independent verification of the structural claims.

---

Papers: [Structural analysis](https://doi.org/10.5281/zenodo.19543917) | [V1 corrective](https://doi.org/10.5281/zenodo.19477552) | [GitHub](https://github.com/CorwinFr/Voynich)

Not claiming to have solved anything. Theorizing that the herbal-pharma structural link is real, that the shorthand model fits the evidence, and that the writing system's architecture (logograms + functional roots + content roots + terminators) is worth investigating further. All data and code are open.

I've been at this for a while now and I'm aware of the limits of working in isolation on this manuscript. Any feedback, criticism, alternative interpretation, or suggestion for a better reference corpus is genuinely welcome. If someone sees a flaw in the structural analysis, I'd rather know now. And if someone has better botanical identifications or knows of a prose herbal text that could serve as a reference, that would directly strengthen (or break) the fingerprint method.

Thank you for reading this far. This community's collective knowledge of the manuscript is far deeper than anything I could build alone.
