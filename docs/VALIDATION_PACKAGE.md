# Voynich Manuscript — Decoded Recipe Lines for Expert Validation

## What this is

We have computationally decoded the grammatical structure of the Voynich Manuscript (Beinecke MS 408, dated 1404-1438). Our model treats the text as a pharmaceutical notation system — not a cipher or a natural language — where each token encodes a combination of procedural function, material state, quantity, and substance.

We are NOT claiming to have "cracked the Voynich." We are claiming to have identified a plausible structural grammar that produces recipe-like text matching patterns found in the Antidotarium Nicolai and related Salernitan pharmaceutical sources.

We need a specialist in medieval Latin pharmacy to tell us: **do these decoded lines read as plausible pharmaceutical instructions?**

---

## The decoding model (brief)

Each Voynich "word" decomposes as:

```
[Structural marker] + [Prefix = function] + [sh/ch = material state] + [e-count = quantity] + [Core suffix = substance/verb]
```

Key mappings (probable, not certain):
- Structural: p/f = Rx (recipe), t = signa (label)
- Prefixes: qo = cum, d = in, ol = ex, l = per, y = de, r = re
- State: sh = raw material (cruda), ch = processed product (praeparata)
- Quantities: e-prefix repetition (1×, 2×, 3×) + ain/aiin system (1ʒ, 2ʒ, 3ʒ drachms)
- Substances: ol = oleum, al = sal, ar = aqua, ody = acetum, ckhy = cera, os = succus, am = ana

Unidentified elements are marked honestly (e.g., "UNK_or", "MATERIA" for state-marked but unspecified material).

---

## 20 best decoded recipe lines

These are lines decoded at 100% (every token classified) from pharmaceutical sections. We present the EVA transcription, the decoded reading, and a tentative English paraphrase.

### Line 1 — F107V (Pharma section, 11 tokens)
```
EVA:  okain ol okaiin lkeody otaiin chol lkaiin lkeeey qokaiin chey qoky
DEC:  1ʒ  oleum  2ʒ  per 1×acetum  2ʒ  [P]oleum  per 2ʒ  cola.3  cum 2ʒ  [P]materia  misce
```
*"1 drachm, oil, 2 drachms, through 1 dose vinegar, 2 drachms, processed oil, through 2 drachms, strain (×3), with 2 drachms, processed material, mix"*

### Line 2 — F103V (Pharma section, 11 tokens)
```
EVA:  daiin shey qokal shedy qokeedy qoteor shey qoty chckhy qotain char
DEC:  in 2ʒ  [M]materia  cum sal  [M]materia et  misce.2 et  cum 1×UNK_or  [M]materia  misce  [P]cera  cum 1ʒ  [P]aqua
```
*"In 2 drachms, raw material, with salt, raw material and, mix, with 1 dose [unknown], raw material, mix, processed wax, with 1 drachm, processed water"*

### Line 3 — F108V (Pharma section, 10 tokens)
```
EVA:  dsheol qokeedy qokeedy chey qokeedy qokedy sheckhy lkedy qoteedy otam
DEC:  [M]1×oleum  misce.2 et  misce.2 et  [P]materia  misce.2 et  misce.1 et  [M]1×cera  cola.1 et  misce.2 et  ana
```
*"Raw oil (1 dose), mix and, mix and, processed material, mix and, mix and, raw wax (1 dose), strain and, mix and, equal parts"*

### Line 4 — F84R (Balneo section, 12 tokens)
```
EVA:  pshedy qokedy otol chedy sheol qokar chckhy chey qokchey oteey dain chedy
DEC:  Rx [M]materia et  misce.1 et  oleum  [P]materia et  [M]1×oleum  cum aqua  [P]cera  [P]materia  cum [P]materia  2ʒ  in 1ʒ  [P]materia et
```
*"Take: raw material and, mix, oil, processed material and, raw oil (1 dose), with water, processed wax, product, with product, 2 drachms, in 1 drachm, product and"*

### Line 5 — F103V (Pharma section, 11 tokens)
```
EVA:  dain shey qokeedy cheol qoeeor lshor qoky shedy qokaiin chedy qokam
DEC:  in 1ʒ  [M]materia  misce.2 et  [P]1×oleum  cum 2×UNK_or  per [M]UNK_or  misce  [M]materia et  cum 2ʒ  [P]materia et  cum ana
```
*"In 1 drachm, raw material, mix and, processed oil (1 dose), with 2 doses [unknown], through raw [unknown], mix, raw material and, with 2 drachms, processed material and, with equal parts"*

### Line 6 — F113R (Pharma section, 10 tokens)
```
EVA:  tchedy okeey cheeos lkaiin chey otain cheeody qokeeody okaiin oteedy
DEC:  signa [P]materia et  adde.2  [P]2×succus  per 2ʒ  [P]materia  1ʒ  [P]2×acetum  cum 2×acetum  2ʒ  adde.2 et
```
*"Label: processed material and, add, processed juice (2 doses), through 2 drachms, product, 1 drachm, processed vinegar (2 doses), with 2 doses vinegar, 2 drachms, add and"*

### Line 7 — F55R (Herbal section, 11 tokens)
```
EVA:  okair or aiin chody ykair qokar okar ol ykar ar al
DEC:  1ʒ  UNK_or  2ʒ  [P]acetum  de 1ʒ  cum aqua  aqua  oleum  de aqua  aqua  sal
```
*"1 drachm, [unknown], 2 drachms, processed vinegar, from 1 drachm, with water, water, oil, from water, water, salt"*

### Line 8 — F55V (Herbal section, 11 tokens)
```
EVA:  qokeeey os ain qool al chedy ar aiin ol kar am
DEC:  misce.3  succus  1ʒ  cum oleum  sal  [P]materia et  aqua  2ʒ  oleum  aqua  ana
```
*"Mix (strong), juice, 1 drachm, with oil, salt, processed material and, water, 2 drachms, oil, water, equal parts"*

### Line 9 — F80V (Balneo section, 11 tokens)
```
EVA:  olcheol qokain sheor otal chedy qokain okaiin otey sheedy olshey
DEC:  ex [P]1×oleum  cum 1ʒ  [M]1×UNK_or  sal  [P]materia et  cum 1ʒ  2ʒ  adde.2  [M]2×materia et  ex [M]materia
```
*"From processed oil (1 dose), with 1 drachm, raw [unknown] (1 dose), salt, processed material and, with 1 drachm, 2 drachms, add, raw material (2 doses) and, from raw material"*

### Line 10 — F103V (Pharma section, 11 tokens)
```
EVA:  pchal shal shorchdy okeor okaiin shedy pchedy qotchedy qotar ol lkar
DEC:  Rx [P]sal  [M]sal  [M]UNK_or [P]materia et  1×UNK_or  2ʒ  [M]materia et  Rx [P]materia et  cum [P]materia et  cum aqua  oleum  per aqua
```
*"Take: processed salt, raw salt, raw [unknown] product and, 1 dose [unknown], 2 drachms, raw material and, Take: processed material and, with product and, with water, oil, through water"*

---

## Patterns we believe match the Antidotarium Nicolai

| Pattern | Our decoded lines | Antidotarium parallel |
|---------|------------------|----------------------|
| OLEUM + CERA + misce | F108V, F84R, F46R | Unguentum fuscum: olei + cerae → bulliat → cera |
| ACETUM + cola | F107V, F113R | Oximel: aceti → bulliant → coletur |
| AQUA + SAL + misce | F103V, F82V | Saline wash: standard preparation |
| Ingredients + ANA | F55V, F80V | Metridatum: blocks with "ana ʒ i" |
| Rx (incipit) → ingredients → verbs | Multiple | Universal Antidotarium structure |

---

## What we need from you

1. **Do these decoded lines read as plausible medieval pharmaceutical instructions?**
   - Is the sequence of operations (mix, strain, add) realistic?
   - Are the substance combinations (oil + wax + water + salt) found in real recipes?
   - Are the quantities (1-3 drachms) in the right range?

2. **Do you recognize any specific recipe type?**
   - The oil + wax lines suggest an unguentum (ointment/cerate)
   - The vinegar + strain lines suggest an oximel or acetous preparation
   - The "ana" (equal parts) endings suggest compound medicine formulation

3. **What is obviously WRONG?**
   - Which combinations are pharmaceutically impossible?
   - Which quantities make no sense?
   - What structural patterns are missing that should be there?

---

## Context and honesty

- 20.1% of the text remains unidentified (labeled UNK or MATERIA)
- Substance identifications are PROBABLE, not proven
- The verb system (prefix = verb type) is SPECULATIVE
- No complete Latin sentence has been identified
- This work was done computationally using statistical analysis of the EVA transcription
- All code and data are available at github.com/CorwinFr/Voynich

*Guillaume Clement, April 2026*
*Computational research assisted by Claude (Anthropic)*
