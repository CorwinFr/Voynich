# Deep Research Prompt 5 : Identification of 109 Ingredient Codes

## Context

We have computationally decoded 80% of the Voynich Manuscript (Beinecke MS 408, 1404-1438) as a pharmaceutical notation system. The structure is solved: each token encodes a function prefix, a material state marker (raw/processed), a quantity, and a substance suffix.

We have identified **109 specific ingredient codes** used by the scribe. Each ingredient appears in TWO forms:
- `sh-X` = raw/crude form (materia cruda)
- `ch-X` = processed/prepared form (materia praeparata)

Where X is a short code (1-5 EVA characters) invented by the scribe. We know the codes but NOT which real substance each code represents.

We also know:
- **8 base excipients** are already identified: oleum (oil), rosa (rose), sal (salt), aqua (water), acetum (vinegar), cera (wax), succus (juice), ana (equal parts)
- The manuscript's **herbal section** has ~130 illustrated plant pages where each plant is drawn and the text describes how to prepare it
- The **recipe sections** mix multiple ingredients with quantities in drachms
- Recipes match patterns from the **Antidotarium Nicolai** (Salernitan pharmaceutical tradition)

## The 30 most frequent ingredient codes

Each code is listed with: EVA core, total frequency (ch+sh combined), and what suffix it ends with (which tells us the PRIMARY PREPARATION TYPE of this ingredient).

| # | EVA code | Freq | Suffix | = Primary prep type |
|---|----------|------|--------|-------------------|
| 1 | o | 212 | (none) | Unknown base form |
| 2 | eo | 126 | (none) | Unknown base form |
| 3 | cthy | 113 | -y | Grammatical/generic |
| 4 | eky | 99 | -y | Grammatical/generic |
| 5 | odaiin | 70 | -aiin | Contains unit marker (2 drachms?) |
| 6 | aiin | 68 | -aiin | Unit marker (2 drachms) |
| 7 | es | 54 | -s | Short form |
| 8 | edaiin | 52 | -aiin | 1x + unit marker |
| 9 | ecthy | 49 | -y | 1x + compound form |
| 10 | oky | 48 | -y | Structural |
| 11 | ees | 46 | -s | 1x + short form |
| 12 | oty | 45 | -y | Structural |
| 13 | edar | 43 | -ar | 1x + aqua-type preparation |
| 14 | ckhey | 41 | -ey | Cera-related? |
| 15 | eeky | 38 | -y | 2x variant of eky |
| 16 | edal | 37 | -al | 1x + sal/aloe-type |
| 17 | ed | 37 | (short) | 1x + base |
| 18 | dar | 33 | -ar | Aqua-type preparation |
| 19 | octhy | 31 | -y | o + compound |
| 20 | ety | 31 | -y | 1x + generic |

## What we know about the herbal page structure

Each herbal folio has:
1. An **illustration** of the plant (visual identification possible)
2. A **label** (first line) that is the scribe's preparation code for that plant
3. **Running text** describing preparation methods

The label encodes HOW TO PREPARE the plant, NOT the plant's name:
- Gallows at start: p = "Recipe/Take" (aromatic herbs), t = "Tere/Grind" (roots/powders), k = use raw
- Suffix at end: -ol = make into oil, -ar = make into water/decoction, -or = make into floral water

Example: folio F90R1 shows THYME. Label is `poleeol` = p(Rx) + ol(oil) + ee(2x) + ol(oil) = "Recipe: make double-refined oil." Thyme is indeed primarily used for its essential oil.

## Visually identified plants (by multiple researchers)

These plants have been identified by Edith Sherwood, Stephen Bax, and other researchers based on the illustrations:

| Folio | Plant | Label EVA | Suffix | Known pharmaceutical use |
|-------|-------|-----------|--------|------------------------|
| F1V | Atropa belladonna | kchsy | none | Narcotic, external ointment only |
| F2R | Centaurea | kydainy | none | Bitter tonic, decoction |
| F2V | Nymphaea | kooiin | none | Cooling, sedative, water prep |
| F4V | Viola | pchooiin | none | Cooling syrup, laxative |
| F9V | Viola tricolor | fochor | -or | Skin conditions, external wash |
| F11R | Calendula | schoal | -al | Wound healing, oil/ointment |
| F13R | Artemisia | torshor | -or | Bitter, vermifuge, wine infusion |
| F22R | Coriandrum | fcholy | -ol(y) | Seed oil, digestive |
| F25V | Helleborus | poeeaiin | -aiin | Toxic purgative, tiny doses |
| F33R | Inula | tshdar | -ar | Expectorant, root decoction |
| F34R | Rosmarinus | pcheoepchy | none | Aromatic oil, memory |
| F38R | Papaver | tolor | -or | Narcotic, latex extraction |
| F40V | Salvia | pchedain | none | Aromatic, gargle, hot infusion |
| F42R | Origanum | cthay | none | Aromatic, digestive |
| F43R | Borago | tarodaiin | -aiin | Cooling, cordial, juice |
| F44R | Mentha | tshodpy | none | Digestive, aromatic, oil |
| F46R | Ruta | pcheocphy | none | Toxic, emmenagogue, small doses |
| F49R | Ocimum | pychol | -ol | Aromatic, seed oil |
| F50R | Verbena | psheor | -or | Wound herb, external infusion |
| F56R | Drosera | chchsy | none | Sundew |
| F65R | Mandragora | otaim | none | Narcotic, soporific, root |
| F90R1 | Thymus | poleeol | -ol | Aromatic essential oil |
| F93R | Urtica | kodshol | -ol | Diuretic, juice, oil |

## Questions for the research agent

### Question 1: Match ingredient codes to Antidotarium Nicolai substances

The Antidotarium Nicolai (~150 recipes) uses a finite set of ingredients. The most common ones are:

**Spices/Aromatics (appear in 30-60% of recipes):**
cinnamomum, piper (pepper), crocus (saffron), zingiber (ginger), nardus (spikenard), galanga, cardamomum, caryophyllum (clove), cubeba, macis (mace), nux moschata (nutmeg)

**Resins/Gums:**
mastix (mastic), thus/olibanum (frankincense), myrrha (myrrh), galbanum, opopanax, bdellium, gummi arabicum, colophonia

**Purgatives/Active drugs:**
aloe, scammonia, helleborus, coloquintida, turbit, agaricus, rhabarbarum, senna, cassia fistula

**Common herbs:**
rosa, salvia, mentha, origanum, absinthium (wormwood), ruta, hyssopus, artemisia, plantago, verbena, betonica, centaurea

**Minerals/Other:**
sal, lithargyrum, cerusa, sulfur, auripigmentum, antimonium

For each of our 30 ingredient codes, **which Antidotarium ingredient is the most likely match**, considering:
- The frequency (code #1 at 212x should match one of the TOP ingredients)
- The suffix (if -ar → water-based preparation, if -ol → oil-based)
- The section distribution (H-dominant = simple/herb, S-dominant = compound ingredient)
- The ch/sh ratio (high ch/sh = heavily processed, like minerals; low ch/sh = used mostly raw, like fresh herbs)

### Question 2: What are the top 20 most frequent ingredients in the Antidotarium Nicolai?

Find published analyses, ingredient lists, or databases that COUNT how many times each ingredient appears across all ~150 recipes. We need a RANKED LIST by frequency. This would directly map to our 109 codes ranked by frequency.

### Question 3: The Circa Instans ingredient order

The Circa Instans describes ~270 simples alphabetically. But which simples appear MOST FREQUENTLY in medieval recipe collections? Is there published data on which Circa Instans entries were most cross-referenced by practicing apothecaries?

### Question 4: Plant identification verification

For each of the 23 visually identified plants listed above:
1. What is the standard medieval Latin preparation for this plant according to the Circa Instans?
2. Does our decoded suffix (oil, water, floral water, etc.) match the documented primary preparation?
3. If the suffix is wrong, what preparation SHOULD it be?

### Question 5: Ingredient pairing patterns

In the Antidotarium Nicolai, which ingredients are ALWAYS used together? For example:
- Cinnamomum + crocus + nardus (the "aromatic trio" in many theriacs)
- Aloe + mastix + rosa (common in purgatives)
- Oleum + cera + resina (ointment base)

If we can find these FIXED PAIRS in our decoded recipes, we can identify the ingredient codes by their co-occurrence patterns, even without knowing which specific code = which specific substance.

### Question 6: The "o" and "eo" ingredients

Our two most frequent ingredient codes are:
- "o" (212 occurrences, appears with both sh and ch)
- "eo" (126 occurrences)

These are VERY SHORT codes for VERY COMMON ingredients. In a personal shorthand, the most common ingredient gets the shortest code. What are the single most common ingredients in:
- The Antidotarium Nicolai?
- The Circa Instans (by cross-reference frequency)?
- A typical 15th-century Italian apothecary inventory?

Candidates: rosa? piper? cinnamomum? mel (honey)? opium?

## Output format

For each ingredient code, provide:
1. The EVA code
2. The proposed Latin substance name
3. The confidence level (HIGH/MEDIUM/LOW)
4. The reasoning (frequency match, suffix match, section match, co-occurrence)
5. Source reference

For the frequency-ranked Antidotarium list, provide:
1. Rank
2. Latin name
3. Approximate number of recipes it appears in (out of ~150)
4. Primary pharmaceutical form (powder, oil, water, etc.)
