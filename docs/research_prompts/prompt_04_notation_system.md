# Deep Research Prompt 4 : Système de notation pharmaceutique abrégé

## Context
We are studying the Voynich Manuscript (MS 408, 1404-1438) and have discovered
that it uses a NOTATION SYSTEM, not a cipher or a language. Each "word" encodes
multiple layers of information in a fixed structure:

TOKEN = [structural marker] + [function prefix] + [material state] + [quantity] + [substance suffix]

For example, a single token might encode: "Recipe (take) + cum (with) + processed + 2 doses + oil"

This is NOT a simple substitution cipher. It's more like a SHORTHAND system
where each glyph position carries a different type of information.

We need to find parallels in REAL medieval pharmaceutical notation.

## Questions

### 1. Multi-layer encoding in medieval pharmacy
- Did medieval pharmaceutical manuscripts encode multiple types of information in a single notation unit?
- Example: did a single symbol or abbreviated word encode BOTH the substance AND its quantity?
- Were there "compound abbreviations" where prefixes indicated the preparation method and suffixes the ingredient?

### 2. Material state notation
- How did medieval apothecaries distinguish between RAW and PROCESSED forms of the same ingredient?
- Was there a standard notation for: crude (crudum), powdered (pulverizatum), distilled (distillatum)?
- Were PREFIXES or SUFFIXES used to indicate material state?
- In the Antidotarium Nicolai, how is the state of an ingredient indicated?
- Specific question: did apothecaries use TWO distinct markers for the same ingredient in different states?

### 3. Quantity encoding in abbreviations
- Were quantities ever EMBEDDED in the abbreviation itself (not written separately)?
- In Tironian Notes, were numbers indicated by repeated strokes or marks?
- Were there medieval systems where doubling a sign meant "twice the amount"?
- How were quantities written in the most ABBREVIATED recipe formats?

### 4. Procedural notation
- Were there SHORTHAND systems for recipe procedures?
- Could a single mark indicate "mix" or "boil" or "strain"?
- Were procedural verbs abbreviated to single letters or symbols?
- Coq. = coque, M. = misce, Col. = cola, Ft. = fiat — were these ALWAYS written out, or were there even shorter forms?

### 5. Positional encoding
- In any known manuscript, does the POSITION of a mark within a symbol change its meaning?
- In Tironian Notes, do auxiliary strokes in different positions modify the base meaning differently?
- Is there a parallel for: "same suffix = same substance, different prefix = different action"?

### 6. Italian pharmaceutical manuscripts 1350-1450
- What specific pharmaceutical manuscripts survive from Northern Italy in this period?
- Find examples of HEAVILY ABBREVIATED recipe texts
- Were there "recipe shorthand" systems specific to Italian apothecaries?
- The mercantesca script — was it used for pharmaceutical notation?
- Were there professional pharmaceutical "codebooks" or "nomenclators"?

### 7. Comparison with our model
Our model says each Voynich token encodes:
1. Structural marker (paragraph/section/recipe start)
2. Function prefix (with/in/from/through/about/again = cum/in/ex/per/de/re)
3. Material state (raw ingredient vs processed product)
4. Quantity (1×, 2×, 3× via repeated glyph elements)
5. Core substance (one of ~10 base ingredients)

Does ANY known medieval system encode information in a similar layered structure?
We are looking for the CLOSEST PARALLEL, even if not identical.

### 8. Specific parallels to search
- Tironian Notes compositing rules (base sign + modifying strokes)
- Mantuan ciphers (1401, 1450) — nomenclator structure
- Notarial abbreviation systems in Lombardy/Veneto
- Apothecary guild regulations from Venice, Padua, Florence (14th-15th c.)
- Any digitized pharmacy manuscript from: Padua, Venice, Ferrara, Bologna, Milan

### 9. Sources to search
- Cappelli, Dizionario di Abbreviature (1899) — pharmaceutical sections
- Schmitz, Commentarii Notarum Tironianarum (1893) — compositing rules
- Supertextus notarum tironianarum (online database)
- MUFI (Medieval Unicode Font Initiative) — abbreviation databases
- Adriano Catellani on pharmaceutical history in Italy
- Studies on medieval Italian pharmacy and its documentation practices
- The Folger Library blog on brevigraphs
- Wellcome Library pharmaceutical manuscripts collection

## Output format
For each parallel system found:
1. System name and date
2. How information is encoded (layered? positional? combinatorial?)
3. How similar is it to our model (1-10 scale)
4. What specific features match
5. Source reference
