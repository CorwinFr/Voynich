# INVENTORY - RECIPE_DATASET
## Etat au 2026-04-11 (post Phase 7 : Wurzburg Arabic-Latin Corpus)

### REFERENTIELS (R01-R08)

| Fichier | Entrees | Description |
|---------|---------|-------------|
| R01_verbs.json | 88 | Verbes pharmaceutiques (+Phase 7: abstergere, desiccare, miscere, terere, laxare...) |
| R02_ingredients.json | 409 | Ingredients (+Phase 7: opium, myrrha, liquiritia, ruta, aqua, armoniacum...) |
| R03_units.json | 12 | Unites de mesure (+Phase 7: dosis) |
| R04_forms.json | 22 | Formes galeniques (+Phase 7: trociscus, pillula, collirium, confectio) |
| R05_tools.json | 16 | Outils (+Phase 7: colatorium) |
| R06_qualities.json | 211 | Qualites (+Phase 7: caliditas, frigiditas, humiditas, siccitas, temperatus, subtilis) |
| R07_plant_parts.json | 16 | Parties de plantes |
| R08_indications.json | 95 | Maladies (+Phase 7: hulcus, apostema, dolor, alopitia, furfures, ventris) |

Total referentiels: 869 entrees

### SOURCES TOKENISEES (S01-S16)

| Fichier | Entrees | Tokens | Avec ref_id | Score | Statut |
|---------|---------|--------|-------------|-------|--------|
| S01_AN.json | 150 | 16192 | 5741 (35.5%) | 76.7 B | FAIT v4 - Antidotarium Nicolai |
| S02_CI.json | 141 | 862 | 411 (47.7%) | 91.7 A | FAIT v1 - Circa Instans |
| S03_AUREA.json | 1 | 105 | 84 (80.0%) | 94.0 A | FAIT - Aurea Alexandrina (crib) |
| S04_GRABADIN.json | - | - | - | - | SOURCE MANQUANTE |
| S05_MACER.json | 25 | 24148 | 3942 (16.3%) | 60.6 C | FAIT - Macer Floridus |
| S06_REGIMEN.json | 106 | 2512 | 594 (23.6%) | 65.8 B | FAIT - Regimen Sanitatis |
| S07_DALME.json | 2480 | 6367 | 1071 (16.8%) | 57.1 C | FAIT - Inventaires DALME |
| S08_AVICENNA.json | 2943 | 942283 | 110299 (11.7%) | 58.0 C | FAIT v1 - Canon Medicinae (Wurzburg XML) |
| S09_COLLECTIO.json | 3680 | 274910 | 51366 (18.7%) | 63.4 C | FAIT v1 - Collectio Salernitana |
| S10_ALPHITA.json | 1714 | 74620 | 9235 (12.4%) | 56.2 C | FAIT - Alphita Glossaire |
| S11_BALNEA.json | 98 | 19769 | 3237 (16.4%) | 62.4 C | FAIT v2 - De Balneis |
| S12_TACUINUM.json | 358 | 67948 | 13007 (19.1%) | 66.6 B | FAIT v4 - Tacuinum Sanitatis (Wurzburg XML) |
| S13_FASCICULUS.json | 48 | 2426 | 251 (10.3%) | 51.5 C | FAIT v2 - Fasciculus Medicinae 1491 |
| S14_GALEN.json | 91 | 94837 | 6357 (6.7%) | 59.1 C | FAIT v1 - Galen De simplici medicina (Wurzburg XML) |
| S15_ABENGUEFIT.json | 539 | 194600 | 32056 (16.5%) | 66.2 B | FAIT v1 - Abenguefit Med. simplicibus (Wurzburg XML) |
| S16_RHAZES.json | 47 | 13345 | 4155 (31.1%) | 74.2 B | FAIT v1 - Rhazes Antidotarium (Wurzburg XML) |

Total: 12421 entrees, 1,734,924 tokens, 241,806 avec ref_id (13.9%)

### COUVERTURE DES SECTIONS VMS

| Section VMS | Suffixe | Sources | Statut |
|-------------|---------|---------|--------|
| Herbal | -ol | S02_CI + S05_MACER + S10_ALPHITA + S14_GALEN + S15_ABENGUEFIT | COUVERT++ |
| Pharma | -edy | S01_AN + S03_AUREA + S08_AVICENNA + S09_COLLECTIO + S16_RHAZES | COUVERT++ |
| Balnea | -edy | S11_BALNEA | COUVERT |
| Astro/Cosmo | mixte | S12_TACUINUM + S13_FASCICULUS | COUVERT |
| Volvelle | logos | R03 (unites) | PARTIEL |

### TOTAL DATASET

| Metrique | Phase 6 | Phase 7 | Delta |
|----------|---------|---------|-------|
| Fichiers sources | 11 | 15 | +4 |
| Entrees referentiels | 846 | 869 | +23 |
| Entrees sources | 8501 | 12421 | +3920 |
| Tokens total | 439,964 | 1,734,924 | +1,294,960 |
| Tokens avec ref | 72,999 | 241,806 | +168,807 |
| Taux ref global | 16.6% | 13.9% | -2.7% (dilution par gros corpus) |
| Grades A | 2 | 2 | = |
| Grades B | 1 | 5 | +4 |
| Grades C | 8 | 8 | = |
| Grades D/F | 0 | 0 | = |
| Invalid refs | 0 | 0 | = |
| None refs | 0 | 0 | = |
| Taille totale | ~42 MB | ~250 MB | +208 MB |

### HISTORIQUE

| Phase | Date | Actions | Impact |
|-------|------|---------|--------|
| Phase 1-3 | 2026-04-10/11 | Build initial R01-R08, S01-S10 | 10 sources, 744->771 refs |
| Phase 4 | 2026-04-11 | S11_BALNEA + S12_TACUINUM | Couverture VMS 4/5 |
| Phase 5-5b | 2026-04-11 | Enrichissement + nettoyage OCR S12 | S12 sort du D, +30 refs |
| Phase 6 | 2026-04-11 | S13_FASCICULUS + astro-medical | 846 refs, Astro couvert |
| Phase 7 | 2026-04-11 | WURZBURG : S12 XML + S08 Avicenna + S14 Galen + S15 Abenguefit + S16 Rhazes + 40 refs arabo-latins | **1.73M tokens, 5 B, 0 D/F** |

### SOURCES WURZBURG DISPONIBLES (non encore integrees)

Le site arabic-latin-corpus.philosophie.uni-wuerzburg.de contient 201 textes TEI-XML (CC BY-SA 4.0).
Candidats prioritaires pour futures phases :

| Texte | Auteur | Interet |
|-------|--------|---------|
| Galen De complexionibus | Galen | Temperaments/humeurs |
| Galen Megategni | Galen | Art therapeutique |
| Isaac Israeli Liber febrium | Isaac Israeli | Maladies/fievres |
| Isaac Israeli Liber urinarum | Isaac Israeli | Uroscopie |
| Albumasar Introductorius | Albumasar | Astrologie (VMS Astro) |
| Secretum Secretorum | Ps-Aristotle | Alchimie/gouvernance |
| Ps-Galen De medicinis experimentatis | Ps-Galen | Medecines testees |
| Anonymous De cibis | Anonymous | Aliments |
| Rhazes Liber divisionum | Rhazes | Nosologie |
| Rhazes Continens | Rhazes | Encyclopedie medicale |
