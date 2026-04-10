# Deep Research Prompt 1 : Recettes de l'Antidotarium Nicolai

## Context
We are studying the Voynich Manuscript (MS 408, dated 1404-1438) and believe it contains pharmaceutical recipes. We have computationally decoded recipe lines that look like:

```
Rx OLEUM . signa AQUA . [M]1×MATERIA et . misce . SAL . [M]MATERIA . cum AQUA . [P]CERA . cum 2℥
```

Which reads as: "Take oil, label water, raw material (1 dose) and, mix, salt, raw material, with water, processed wax, with 2 ounces"

We need to compare this against REAL medieval pharmaceutical recipes.

## Questions

### 1. Antidotarium Nicolai — Actual recipe texts
Find the LATIN TEXT of at least 10 recipes from the Antidotarium Nicolai (12th century, Salerno). We need:
- The exact Latin wording (not translations)
- The ingredient lists with quantities (℥, ʒ, ℈)
- The procedural verbs used (recipe, misce, coque, tere, cola, fiat, adde, solve)
- How ingredients are connected (et, cum, in, per, ex)

Specific recipes to find:
- **Hiera Picra** (the most famous laxative electuary)
- **Theriac** (universal antidote)
- **Mithridate** (compound medicine)
- **Unguentum rosatum** (rose ointment)
- **Electuarium de succo rosarum** (rose juice electuary)
- Any recipe involving: oleum + cera + sal + aqua together

### 2. Recipe structure patterns
In medieval pharmaceutical Latin, what is the standard WORD ORDER in a recipe?
- Does the verb come before or after the ingredient?
- How are quantities written relative to ingredients? (before, after, or interleaved?)
- Is "et" used between ingredients in a list, or is it implicit?
- What is the role of "cum" in recipes? (vehicle? instrument?)
- Does "in" introduce a container, a duration, or a method?

### 3. Specific recipe patterns we need to validate
We observe these decoded patterns. Do they match real medieval recipes?
- "cum AQUA" (with water) — is this standard for describing a vehicle?
- "Rx [ingredient] [quantity], misce, cola" (take, mix, strain) — standard sequence?
- "[M]MATERIA et [P]MATERIA" (raw material and processed material) — did medieval recipes explicitly distinguish raw vs processed forms of the same ingredient?
- "2℥" as the most common dose — is 2 ounces really the standard?
- "HIERA 3℥" — is 3 ounces of Hiera Picra a normal dose?
- "ACETUM" for external applications (legs, throat) — documented?
- "OLEUM + CERA" together — ointment base?
- "ANA" (equal parts) at the end of ingredient lists — standard placement?

### 4. Circa Instans
Find the structure of entries in the Circa Instans (12th century herbal):
- How are simples described? (name, quality, degree, uses)
- What is the format of the Galenic quality description? (hot/cold degree 1-4, wet/dry degree 1-4)
- Are preparation instructions included for each simple?

### 5. Sources to search
- Antidotarium Nicolai Latin text (any edition: Goltz 1976, Lugt 2011)
- BNF Latin 6823 (Southern Italy, contains Antidotarium)
- Circa Instans Latin text
- Tractatus de Herbis (15th century Veneto)
- Any digitized medieval pharmaceutical manuscript from Northern Italy, 14th-15th century
- Marco Ponzi's blog posts on Antidotarium Nicolai (Medium/ViridisGreen)
- The Routledge Pocket Guide to Medical Latin (Jon R. Stone, 2024)
- Early Modern Recipes Online Collective (EMROC)

## Output format
For each recipe found, provide:
1. Recipe name
2. Full Latin text
3. List of ingredients with quantities
4. List of procedural verbs in order
5. Source reference
