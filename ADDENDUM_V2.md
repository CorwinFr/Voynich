# Addendum V2 — Validation Results and Honest Reassessment

*Guillaume Clement, April 2026*
*Following the initial publication (DOI: 10.5281/zenodo.19477552)*

---

## What This Document Is

After publishing our initial results, we conducted a rigorous series of validation tests (V13 through V18) designed to stress-test, and if necessary break, our own claims. This addendum presents the findings honestly. The complete test code and raw results are available in `v12/validation_v2/` on the GitHub repository.

---

## What We Got Wrong

### The 89% headline is misleading

The initial paper reported 89.3% Perseus dictionary validation across 38,442 words. Deeper analysis reveals this figure is inflated by short words:

| Word length | Perseus match | Random baseline | Real signal |
|-------------|--------------|-----------------|-------------|
| 2 characters | 100% | 100% | **0 pp** (no signal) |
| 3 characters | 99.9% | 77.3% | +22.6 pp |
| 4 characters | 96.7% | 17.1% | **+79.6 pp** |
| 5 characters | 86.5% | 1.5% | **+85.0 pp** |
| 6 characters | 38.4% | 0.1% | +38.3 pp |
| 7+ characters | <17% | 0% | weak |

75% of the decoded corpus consists of words under 5 characters (et, in, ex, es, cum, eo, ac). These match Latin trivially. The honest signal lies in the 4-5 letter range.

### The scorer does most of the work, not the K&A mapping

When we tested the raw K&A mapping with no scoring optimizer (V13b), it produced **14.1% Perseus matches, below the 24.4% random baseline**. The multi-candidate scorer adds 77.5 percentage points by searching the candidate space for valid Latin words.

However, when we tested K&A + simplified scorer against 200 random mappings + same scorer (V14), K&A scored **36.7% vs 18.4% average random** (z-score: 4.6). The K&A mapping captures real structure above chance, but the amplification from 36.7% to 91.6% by the full pipeline is where artifact meets signal.

### No Latin sentences were found

Zero sequences of 5 consecutive specific words were found in any medieval Latin corpus. Zero sequences of 4 words with 2+ non-generic terms. The decoded output has pharmaceutical **vocabulary** but no detectable Latin **syntax**. Shuffling word order barely changes coherence scores.

---

## What We Got Right

### The morphological structure is real

The manuscript has a clear **PREFIX + ROOT** system (V15-V16). The root `-aiin` appears in 10.2% of all words and combines productively with every known prefix (d+aiin, qok+aiin, ok+aiin, ot+aiin, ch+aiin, s+aiin, k+aiin...). This is grammar, not noise.

5,805 unique roots were identified after prefix stripping. The top 50 roots cover 49.5% of non-logogram tokens. This is a structured morphological system.

### The K&A mapping has a real signal

K&A + simplified scorer: 36.7% Perseus. Random mapping + same scorer: 18.4%. Z-score: **4.6**. The mapping is statistically significant, Latin-specific (36.7% Latin vs 15.8% Italian), and outperforms pure frequency matching by 13.4 points. Some glyphs carry strong signal: o (+7.2 pp when ablated), r (+6.1 pp), y (+5.0 pp), t (+3.6 pp).

### The logograms work

123 confirmed whole-word mappings (logograms) cover 20.6% of all tokens at **70.7% Perseus validation**. These include: dy=et, or=hiera, qoky=coque, ar=iure, chedy=eius et, r=recipe, m=misce. Seven of fourteen confirmed root-Latin values are attested in the Schmitz Tironian Notes index (12,987 entries).

### The k-prefix is probably silent

Testing all hypotheses for the k-prefix value (V17), k=silent wins at 100% (all k+root combinations produce valid Latin by simply removing k). Other hypotheses (k=t, k=c, k=h, k=qu) score 50% or less. The EVA transcription itself confirms t/k confusion with 21 alternative readings.

### Held-out folios generalize

20 randomly selected held-out folios produce 31.2% average Perseus match with the root decoder (V18), consistent with the training set. No overfitting detected.

---

## The Honest Picture

| Metric | Initial claim | After V13-V18 | Status |
|--------|--------------|---------------|--------|
| Perseus validation | 89.3% | 27-44% (length-dependent) | Overstated |
| Signal above random | Not tested | +67 pp (raw), +18 pp (with scorer) | Real |
| Z-score vs random | Not tested | 4.6 | Significant |
| Latin vs Italian | Not tested | 36.7% vs 15.8% | Latin-specific |
| Morphological structure | Described | Confirmed (5,805 roots) | Solid |
| Logograms | 123 confirmed | 70.7% Perseus, 7/14 in Tironian | Solid |
| Latin sentences | Implied | 0 found (5-word) | Not demonstrated |
| Syntactic coherence | Implied | Not detected | Not demonstrated |
| Manuscript = pharma manual | Claimed | Compatible, not proven | Hypothesis |

---

## What Needs To Happen Next

1. **A medieval Latin specialist** must evaluate whether the decoded vocabulary (aquam, coque, hiera, aloes, ciere, curam, recipe, iecur, ture, sal) forms coherent pharmaceutical text or is a statistically plausible word salad.

2. **The root mapping approach** (V16, 87.3% Perseus on 5+ letter words) should replace the glyph-by-glyph pipeline as the primary decoder.

3. **The ~5,800 roots** need systematic Latin identification, starting from the 18 confirmed logograms and propagating constraints outward.

4. **The 624 alternative readings** in the EVA transcription should be systematically tested as they may resolve known glyph confusions (o/a: 165x, s/r: 120x, t/k: 21x).

5. **The 12,987 Tironian abbreviations** in the Schmitz index should be cross-referenced with the root inventory.

---

## Conclusion

We did not crack the Voynich Manuscript. We built a computational tool that reveals a real morphological structure and a statistically significant (but modest) Latin vocabulary signal. The 89% figure was wrong. The PREFIX + ROOT system, the logogram matches, and the Tironian Notes correspondence are right. The truth is somewhere between our initial enthusiasm and the harshest criticism: a partially correct framework that needs domain expertise to refine.

Everything is open source. We hope someone will take this further.

---

*Full validation code: `v12/validation_v2/` on github.com/CorwinFr/Voynich*
*Tests: V13 (random baseline), V14 (1000 random mappings), V15 (root extraction), V16 (root mapping), V17 (k-prefix, Tironian), V18 (held-out, o/a swap)*

---
---

# Addendum V2 — Résultats de Validation et Réévaluation Honnête

*Guillaume Clement, avril 2026*
*Suite à la publication initiale (DOI: 10.5281/zenodo.19477552)*

---

## Ce que ce document est

Après la publication de nos résultats initiaux, nous avons conduit une série rigoureuse de tests de validation (V13 à V18) conçus pour mettre sous pression, et si nécessaire casser, nos propres affirmations. Cet addendum présente les résultats honnêtement. Le code complet des tests et les résultats bruts sont disponibles dans `v12/validation_v2/` sur le dépôt GitHub.

---

## Ce que nous avons dit de faux

### Le chiffre de 89% est trompeur

Le papier initial rapportait 89,3% de validation au dictionnaire Perseus sur 38 442 mots. L'analyse approfondie révèle que ce chiffre est gonflé par les mots courts :

| Longueur | Perseus match | Baseline aléatoire | Signal réel |
|----------|--------------|-------------------|-------------|
| 2 caractères | 100% | 100% | **0 pp** (aucun signal) |
| 3 caractères | 99,9% | 77,3% | +22,6 pp |
| 4 caractères | 96,7% | 17,1% | **+79,6 pp** |
| 5 caractères | 86,5% | 1,5% | **+85,0 pp** |
| 6 caractères | 38,4% | 0,1% | +38,3 pp |
| 7+ caractères | <17% | 0% | faible |

75% du corpus décodé est constitué de mots de moins de 5 caractères (et, in, ex, es, cum, eo, ac). Ils matchent le latin trivialement.

### Le scorer fait le gros du travail, pas le mapping K&A

Le mapping K&A brut sans scorer produit **14,1% de Perseus, en dessous du hasard (24,4%)**. Le scorer multi-candidats ajoute 77,5 points. Toutefois, K&A + scorer simplifié bat 200 mappings aléatoires + même scorer : **36,7% vs 18,4%** (z-score: 4,6). Le signal K&A est réel mais modeste.

### Aucune phrase latine trouvée

Zéro séquences de 5 mots consécutifs dans un corpus médiéval connu. Le résultat décodé a un **vocabulaire** pharmaceutique mais pas de **syntaxe** latine détectable.

---

## Ce que nous avons dit de vrai

### La structure morphologique est réelle

Le manuscrit a un système clair de **PRÉFIXE + RACINE** (V15-V16). La racine `-aiin` apparaît dans 10,2% des mots et se combine productivement avec tous les préfixes connus. 5 805 racines uniques ont été identifiées. C'est de la grammaire, pas du bruit.

### Le mapping K&A a un signal réel

Z-score de 4,6 au-dessus du random. Spécifique au latin (36,7% latin vs 15,8% italien). Bat le mapping par fréquence de 13,4 points. Certains glyphes portent un signal fort : o (+7,2 pp), r (+6,1 pp), y (+5,0 pp).

### Les logograms fonctionnent

123 mappings mot-complet couvrent 20,6% du texte à **70,7% Perseus**. Sept de nos quatorze valeurs racine-Latin confirmées sont attestées dans l'index des Notes Tironiennes de Schmitz (12 987 entrées).

### Le préfixe k est probablement silencieux

L'hypothèse k=silencieux gagne à 100% sur les tests. La confusion t/k dans la transcription EVA (21 lectures alternatives) confirme l'ambiguïté de ce glyphe.

### Les folios held-out généralisent

20 folios aléatoires réservés produisent 31,2% Perseus moyen avec le décodeur par racines, cohérent avec l'ensemble d'entraînement. Pas de surapprentissage.

---

## Le bilan honnête

| Métrique | Affirmation initiale | Après V13-V18 | Statut |
|----------|---------------------|---------------|--------|
| Validation Perseus | 89,3% | 27-44% (selon longueur) | Surévalué |
| Signal au-dessus du hasard | Non testé | +67 pp (brut), +18 pp (avec scorer) | Réel |
| Z-score vs random | Non testé | 4,6 | Significatif |
| Latin vs Italien | Non testé | 36,7% vs 15,8% | Spécifique au latin |
| Structure morphologique | Décrite | Confirmée (5 805 racines) | Solide |
| Logograms | 123 confirmés | 70,7% Perseus, 7/14 dans Tironiennes | Solide |
| Phrases latines | Implicite | 0 trouvées (5 mots) | Non démontré |
| Cohérence syntaxique | Implicite | Non détectée | Non démontré |
| Manuscrit = manuel pharma | Affirmé | Compatible, non prouvé | Hypothèse |

---

## Ce qui doit se passer ensuite

1. Un **spécialiste du latin médiéval** doit évaluer si le vocabulaire décodé forme du texte pharmaceutique cohérent ou un sac de mots statistiquement plausible.
2. L'**approche par racines** (V16, 87,3% Perseus sur les mots de 5+ lettres) devrait remplacer le pipeline glyphe par glyphe.
3. Les **~5 800 racines** doivent être systématiquement identifiées en latin.
4. Les **624 lectures alternatives** de la transcription EVA doivent être testées.
5. Les **12 987 abréviations tironiennes** de l'index Schmitz doivent être croisées avec l'inventaire des racines.

---

## Conclusion

Nous n'avons pas craqué le Manuscrit de Voynich. Nous avons construit un outil computationnel qui révèle une structure morphologique réelle et un signal de vocabulaire latin statistiquement significatif mais modeste. Le 89% était faux. Le système PRÉFIXE + RACINE, les logograms, et la correspondance avec les Notes Tironiennes sont justes.

La vérité est quelque part entre notre enthousiasme initial et la critique la plus sévère : un cadre partiellement correct qui nécessite l'expertise du domaine pour être affiné.

Tout est en open source. Nous espérons que quelqu'un ira plus loin.

---

*Code de validation complet : `v12/validation_v2/` sur github.com/CorwinFr/Voynich*
*Tests : V13 (baseline), V14 (1000 mappings), V15 (racines), V16 (root mapping), V17 (k-prefix, Tironiennes), V18 (held-out)*
