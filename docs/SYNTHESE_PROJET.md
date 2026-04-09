# Projet Voynich — Synthèse Complète

> Document de contexte pour repartir clean. Couvre l'intégralité du travail réalisé :
> méthodes, corpus, résultats, échecs, et conclusions.
> Dernière mise à jour : 2026-04-07.

---

## 1. Objectif du projet

Déchiffrement computationnel du manuscrit de Voynich (Beinecke MS 408, ~1404-1438) par analyse statistique, propagation de contraintes et modèles de langue. Approche systématique : identifier le "type de machine" (nature du système d'écriture) avant d'attaquer le contenu.

---

## 2. Infrastructure technique

### 2.1 Transcription source

| Fichier | Description | Format |
|---------|-------------|--------|
| `data/transcriptions/ZL.txt` | Transcription Zandbergen-Landini v2b (2022) | IVTFF |
| `data/transcriptions/LSI.txt` | Archive interlinéaire Stolfi (1998) | IVTFF multi-transcripteur |

**Parseur** : `src/parse_ivtff.py` — extrait pages, mots, labels, sections, mains, loci.
```python
import sys; sys.path.insert(0, 'src')
import parse_ivtff as p
orig = p._merge_ligatures
p._merge_ligatures = lambda w: w  # SANS fusion de ligatures
pages = p.parse('data/transcriptions/ZL.txt')
p._merge_ligatures = orig
words = p.word_list(pages)  # 32 085 tokens, 8 397 types, 25 glyphes EVA
```

**Biais connus de la transcription EVA** (audit Phase 0) :
- Caractères rares (`@NNN;`) supprimés silencieusement (~5-20/page)
- Lectures alternatives `[a:b]` → toujours le premier choix (741 cas)
- Confusions non traquées : a/o, r/s, g/m
- 340 lectures incertaines (?) supprimées sans trace
- **Impact** : bruit de fond sur les analyses statistiques, mais n'invalide pas les conclusions à forte significativité

### 2.2 Corpus de référence

#### Corpus principal : Latin médical étendu (1.82M mots)
**Fichier** : `data/corpus_latin_medical_extended.txt` (12 MB, 63 871 lignes)

**Sources** (toutes dans `data/raw_corpus_9a/`) :
| Source | Époque | Contenu |
|--------|--------|---------|
| Canon Medicinae (Avicenne, trad. Gérard de Crémone) | XIIe s. | Médecine générale, pharmacologie |
| Collectio Salernitana (5 volumes) | XIe-XIIIe s. | École de Salerne, thérapeutique |
| Clavis Sanationis (Simon de Gênes) | XIIIe s. | Dictionnaire médical, synonymes |
| Alphita (anonyme salernitain) | XIIIe s. | Glossaire médico-botanique |
| Macer Floridus (Odo de Meung) | XIe s. | Poème sur les vertus des plantes |
| Antidotarium Nicolai | XIIe s. | Formulaire pharmaceutique |
| Regimen Sanitatis Salernitanum | XIIIe s. | Hygiène et diététique |

**Construction** : OCR/téléchargement brut → nettoyage (`data/raw_corpus_9a/clean_corpus.py`) → concaténation. Nettoyage : suppression en-têtes, numéros de page, normalisation accents, filtrage caractères non-latins.

#### Autres corpus
| Fichier | Taille | Usage |
|---------|--------|-------|
| `corpus_latin_medical.txt` | 52 KB | Ancien corpus (Herbarium Apulei seul) |
| `corpus_latin_combined.txt` | 84 KB | ~15K mots, combinaison ancienne |
| `corpus_italian.txt` | 631 KB | Divina Commedia (~71K mots) |
| `corpus_italian_medical.txt` | 51 KB | Médecine italienne |
| `corpus_ovid.txt` | 775 KB | Ovide (latin classique, contrôle) |
| `corpus_circa_instans_noisy.txt` | ~2K mots | Bruité, NON utilisable pour modèle de langue |

#### Données de référence spécialisées
| Fichier | Contenu |
|---------|---------|
| `botanical_anchors.json` | 106 folios → plantes identifiées (espèce, confiance 0-1, nom latin médiéval, mots EVA candidats) |
| `herbal_folio_words.json` | Tous les mots EVA par folio herbal |
| `dict_latin_medical_suffixes.json` | 91 entrées, 20 catégories de terminaisons avec fréquences |
| `latin_bigram_model.json` | P(char_i | char_{i-1}), alphabet a-z + #, lissage add-1 |
| `medieval_latin_plant_names.tsv` | 25 mappings nom moderne → médiéval |
| `botanical_identifications.tsv` | 163 identifications brutes |

#### Tironiennes
| Fichier | Contenu |
|---------|---------|
| `tironian/schmitz_raw.txt` | OCR Schmitz 1893 (1.1 MB) |
| `tironian/schmitz_index_full.json` | 12 987 entrées de l'Index Alphabeticus |
| `tironian/tironian_mappings.json` | 271 signes prioritaires + conventions d'abréviation |

### 2.3 Dictionnaires
- `data/dictionaries/` : latin.txt, italian.txt, french.txt, spanish.txt
- `data/quadgrams/` : quadgrammes par langue (pour scoring)

---

## 3. Faits établis (invariants du projet)

Ces résultats ont été validés à travers plusieurs phases indépendantes et ne sont PAS remis en question :

| Fait | Preuve | Phase |
|------|--------|-------|
| Alphabet effectif = 24 chars (g=y seul homophone confirmé) | Clustering Phase 5, r=0.436 pour qo | 5 |
| 18 chars significatifs (freq > 1%) : o,e,g,h,a,d,c,i,k,l,r,s,t,n,q,p,m,f | Distribution de fréquence | 0 |
| IC = 0.077 → langue naturelle, pas polyalphabétique | Calcul direct | 3 |
| 13 suffixes paradigmatiques dans une grille NOYAU(a,o,e,i,∅) × TERMINATEUR(y,r,l,s,d) | Analyse morphologique | 5, 8 |
| Espaces EVA = vrais mots | 5 tests (KS, entropy, Zipf, bigram divergence, DP coverage) | 7B |
| Mono-substitution 1:1 → ÉCHEC TOTAL (0 ligne lisible, toutes langues) | Frequency attack + suffix validation | 7 |
| Rigidité positionnelle = 0.79 → chars verrouillés par position | Phase 0 profiling | 0 |
| Le texte est du CONTENU SIGNIFICATIF (pas du gibberish) | 7/8 tests structurels passent | Structure |
| Meilleur match structural = Latin médical (23/26) | Suffix cooccurrence + paradigmes | 8 |
| Le VMS n'est PAS un chiffre homophonique verbose | Simulation Naibbe : 2 suffixes vs 13, TTR 0.69 vs 0.26 | Triage T3 |

---

## 4. Phases du projet — Résumé

### Phase 0 : Élimination & Profiling
**Méthode** : Distribution des caractères, rigidité positionnelle, auto-citation, corrélation Zipf.
**Résultat** : H1 (substitution simple) ÉLIMINÉE. Rigidité 0.79 trop haute. Classes de caractères identifiées : initiaux (q), finaux (y,m,n), médiaux (e,h,i).

### Phase 0.5 : Faisabilité
**Méthode** : Inventaire des cribs disponibles (zodiac, plantes).
**Résultat** : 16 cribs (12 zodiac + 4 labels plantes). FAISABLE.

### Phase 1 : Cribs
**Méthode** : Extraction automatique des labels botaniques et zodiacaux, croisement avec le texte.
**Résultat** : 80 identifications de plantes dans ZL.txt, mais seulement 4 ont des loci labels.

### Phase 2B : Verbose solver
**Méthode** : Alignement de cribs sur les mots EVA, scoring multi-langue.
**Résultat** : Français score 12 (17 cribs alignés), Italien 8 mappings cohérents. Suffixes multiples → voyelle 'a'.

### Phase 2D : Test de Timm
**Méthode** : Comparaison de la structure thématique (topic modelling) VMS vs textes réels.
**Résultat** : Mean diff 0.21 > seuil 0.15 → H3 (texte généré) affaiblie mais non réfutée. Delta discriminant = 0.006 (quasi-identique).

### Phase 3 : IC & Identification de langue
**Méthode** : Index de Coïncidence, corrélation longueur de mots, analyse gallows.
**Résultat** : IC = 0.077. Corrélation Latin r=0.794, Italien r=0.626. → Langue romane.

### Phase 4 : Bombe
**Méthode** : Propagation de contraintes depuis les cribs vérifiés.
**Résultat** : 6 mappings vérifiés (Q=qu, l=t, a=a, k=h, o=o, n=p). Cohérence 46%, blocs 0/6 → la bombe montre que le mapping 1:1 simple est insuffisant.

### Phase 5 : Homophones & Morphologie
**Méthode** : Clustering contextuel, extraction des familles suffixales.
**Résultat** : g=y confirmé (seul homophone). 13 suffixes paradigmatiques. Grille NOYAU × TERMINATEUR. Alphabet réduit à 24.

### Phase 6 : Identification de langue
**Méthode** : Corrélation Spearman des rangs de suffixes EVA vs langues candidates.
**Résultat** : Latin médical ρ=1.0, Italien ρ=1.0, mais test peu discriminant (petit N). → Latin médical retenu.

### Phase 7 : Attaque par fréquence
**Méthode** : Mapping par fréquence lettre/bigramme, validation suffixale, scoring composite.
**Résultat** : Score composite Italien 85.9 > Latin 75.1. Mais pourcentages absolus très bas (0.6-4.1%). → La substitution simple échoue.

### Phase 7B : Réalité des espaces
**Méthode** : 5 tests (KS longueur, entropie aux frontières, divergence bigramme, perturbation Zipf, couverture DP).
**Résultat** : 3/5 tests confirment que les espaces sont des vrais séparateurs de mots. **Conclusion définitive : les espaces EVA délimitent de vrais mots.**

### Phase 8 : Grammaire & Bootstrap
**Méthode** : Analyse de la grille suffixale, matching structural contre 12 langues, initialisation du mapping.
**Résultat** : Latin_medical 23/26, Latin_Ovid 21/26, Vénitien 19/26. Bootstrap mapping :
```
a→o  d→e  e→u  l→t  o→i  r→a  s→m  y→s
```
64% de caractères décodés, 631 mots pleinement décodés, 62.5% de couverture textuelle.

### Phase 9D : Test positionnel
**Méthode** : KL-divergence positionnelle (initiale/médiale/finale) pour chaque char EVA vs baseline latin.
**Résultat** : Ratio EVA/Latin = 1.27 (< 2.0). → **ALPHABÉTIQUE** — pas de valeurs position-dépendantes.

### Phase 10A : Modèle bigramme
**Méthode** : Modèle P(char_i|char_{i-1}) sur le corpus latin 1.82M, alphabet a-z + #, lissage add-1.
**Résultat** : 729 entrées bigramme. Sauvé dans `data/latin_bigram_model.json`.

### Phase 10B : Validation suffixale
**Méthode** : Traduction des 13 suffixes EVA via le mapping bootstrap, vérification morphologique + corpus.
**Résultat** : **12/12 suffixes testables produisent des terminaisons latines valides.** → GO.

### Phase 10C : EM sténographique (v1, v2, v3)
**Méthode** : EM caractère-par-caractère, puis hill-climbing sous contrainte 1:1, puis EM contraint.
**Résultat** : ÉCHEC. v1 : collapse alphabétique (IC 0.185). v2 : 7.4% recognition, IC 0.1037. v3 : 8.1% en 1:1, dégradé à 7.7% par l'EM. L'EM bigramme ne maintient pas la diversité alphabétique. Le mapping 1:1 simple ne fonctionne pas.

### Phase 10E : Attaque par les mots
**Méthode** : Approche top-down (mot → caractère). Profilage des 100 mots EVA et latins les plus fréquents. Matrice de compatibilité. Ancres botaniques comme cribs. Propagation de contraintes.
**Résultat** : Meilleure clique (score 152) : 5 hypothèses, 10 chars résolus, 251 mots reconnus, 26% texte couvert. Inclut cthod=viola (f9v), dal=aut, dy=ad, al=ut. Les mots longs restent du bruit.

### Triage : 3 tests décisifs

| Test | Hypothèse | Méthode | Verdict |
|------|-----------|---------|---------|
| T1 Lunazzi | Brachigraphie latine | Expansion EVA via table Lunazzi → vérif. dictionnaire | **MORTE** (0/7 mots-clés, 0 function words) |
| T2 Gladyševa | Galicien médiéval | Cohérence alphabet + croisement botanique | **FAIBLE** (1/5 botanique, 11% mots) |
| T3 Naibbe | Chiffre verbose homophonique | Simulation chiffre → comparaison métriques VMS | **MORTE** (2 suffixes vs 13, TTR 0.69 vs 0.26) |

---

## 5. Conclusion majeure : le VMS est du texte en clair abrégé

Le Test 3 du triage est le résultat le plus important du projet. Un chiffre homophonique verbose :
- **Détruit** les 13 suffixes paradigmatiques (n'en produit que 2)
- **Explose** le TTR (0.69 vs 0.26 — trop de mots uniques)
- **Aplatit** l'IC (0.060 vs 0.077)

**Donc** : la morphologie riche du VMS (13 suffixes, grille NOYAU×TERMINATEUR, familles productives de stems) est une propriété du texte source, **pas** un artefact de chiffrement.

Le VMS est du **texte en clair dans un système d'écriture abréviatif**. La substitution 1:1 simple échoue (Phase 7, Phase 10C), ce qui signifie que le système d'écriture encode plus d'une lettre par glyphe (abréviations, ligatures, ou sténographie).

---

## 6. Morphologie EVA — La structure interne

### Les 13 suffixes et la grille

```
Suffixe EVA │ Fréq. │ % paradigme │ Probable latin (Phase 8)
────────────┼───────┼─────────────┼─────────────────────────
-y          │  88%  │ omniprésent │ -s (nominatif sg.)
-dy         │  76%  │ très commun │ -es (nom/acc pl. 3e)
-ol         │  70%  │ commun      │ -it (3e pers. parfait)
-or         │  70%  │ commun      │ -ia (neutre pl.)
-al         │  68%  │ commun      │ -ot (?)
-aiin       │  68%  │ commun      │ non résolu
-ar         │  66%  │ commun      │ -oa (?)
-ey         │  62%  │ commun      │ -us (nominatif sg. 2e)
-s          │  56%  │ courant     │ -m (accusatif sg.)
-edy        │  52%  │ courant     │ -ues (?)
-d          │  54%  │ courant     │ -e (ablatif/adverbe)
-r          │  40%  │ modéré      │ -a (féminin sg.)
-l          │  34%  │ modéré      │ -t (3e pers. verbe)
```

### Stems les plus productifs

| Stem | Formes | Tokens | Suffixes attestés |
|------|--------|--------|-------------------|
| ch   | 14     | 1 529  | tous les 13 + NONE |
| sh   | 13     | 983    | tous les 13 + NONE |
| qok  | 11     | 1 126  | 11/13 |
| ot   | 10     | 761    | 10/13 |
| ok   | 9      | 770    | 9/13 |
| qoke | 7      | 617    | 7/13 |
| che  | 9      | 463    | 9/13 |
| qot  | 9      | 430    | 9/13 |

### Le problème "daiin"
- Mot #1 (691 occ., 5 chars). Structure : stem `d` + suffixe `-aiin`.
- `d` est un stem productif (51 formes : dar, dal, dain, dol, dor, dy...).
- `-aiin` est productif avec 61 stems différents.
- Présent dans TOUTES les sections → mot grammatical ou terme très générique.
- Position en milieu de ligne (0.502) → pas spécifiquement sentence-initial.
- PAS un logogramme (prend des suffixes).

---

## 7. Ce qui a échoué et pourquoi

| Approche | Pourquoi ça échoue |
|----------|--------------------|
| Substitution 1:1 caractère (Phase 7, 10C) | 0 ligne lisible. L'écriture n'est pas un alphabet simple. |
| EM bigramme (Phase 10C v1-v3) | Collapse alphabétique : le modèle bigramme attire tous les chars vers 'c'. Injectivité impossible à maintenir. |
| Hill-climbing 1:1 (Phase 10C v3) | 8.1% recognition, IC 0.077 (bon), mais mots longs = bruit. L'EM empire ensuite les résultats. |
| Table Lunazzi mécanique (Triage T1) | 0/7 mots-clés. La brachigraphie est trop ambiguë sans contexte humain. |
| Chiffre verbose (Triage T3) | Détruit la morphologie. Le VMS a trop de structure pour être chiffré. |

**Leçon centrale** : les approches bottom-up (lettre → mot) échouent. Les approches top-down (mot → lettre) sont plus prometteuses mais manquent de contraintes suffisantes.

---

## 8. Ce qui fonctionne (partiellement)

| Approche | Signal |
|----------|--------|
| Bootstrap suffixal (Phase 8+10B) | 12/12 suffixes → terminaisons latines valides. Le mapping a→o, d→e, l→t, y→s, r→a est le plus solide. |
| Ancres botaniques (Phase 10E) | cthod=viola (f9v, confiance 0.83) est le crib le plus fort. 106 ancres disponibles. |
| Propagation de contraintes (Phase 10E) | 26% de couverture, 251 mots reconnus, 3 function words (aut, ad, ut). |
| Analyse structurelle | 7/8 tests passent → le texte EST du contenu significatif. |

---

## 9. Pistes ouvertes pour V2

### 9.1 King & Andrisani (Tironian)
Hypothèse : l'écriture Voynich dérive des notes tironiennes. Ils ont translitéré 2 pages et publié une table de correspondances. Leurs PDFs sont sur Academia.edu mais derrière un paywall — récupération manuelle nécessaire.
- URLs : academia.edu/39776000 et academia.edu/121095492
- À tester avec nos 5 métriques standard (IC, dict%, function words, suffixes, cohérence).

### 9.2 Dialecte italien du Nord
La provenance Véneto est bien supportée (iconographie, paléographie). Le vénitien/padouan comme langue source avec abréviation tironienne adaptée est une piste cohérente avec :
- Le match structural Phase 8 (Vénitien 19/26)
- Le contenu médical (école de Padoue, XVe s.)
- Les conventions sténographiques (notes tironiennes encore utilisées dans les scriptoria vénitiens)

### 9.3 Approche hybride mot-caractère
Combiner les cribs botaniques (top-down) avec la grille suffixale (bottom-up) :
1. Utiliser les 106 ancres botaniques pour fixer des mots
2. Propager les implications caractère sous contrainte d'injectivité
3. Vérifier chaque propagation contre la grille suffixale
4. Utiliser un LLM pour évaluer la plausibilité des textes partiellement décodés

---

## 10. Arborescence du repo

```
d:/Github/Voynich/
├── src/
│   ├── parse_ivtff.py              # Parseur EVA (API: parse, word_list, _merge_ligatures)
│   ├── phase0_identify_machine.py  # Phase 0 : élimination
│   ├── phase05_feasibility.py      # Phase 0.5 : faisabilité
│   ├── phase1_cribs.py             # Phase 1 : extraction de cribs
│   ├── phase2b_verbose.py          # Phase 2B : solver verbose multi-langue
│   ├── phase2d_timm_test.py        # Phase 2D : test de Timm
│   ├── phase3_identify.py          # Phase 3 : IC + identification
│   ├── phase4_bombe.py             # Phase 4 : propagation Bombe
│   ├── phase5_homophones_morphology.py  # Phase 5 : homophones + morphologie
│   ├── phase6_language_id.py       # Phase 6 : identification de langue
│   ├── phase7_frequency_attack.py  # Phase 7 : attaque par fréquence
│   ├── phase7b_boundary_tests.py   # Phase 7B : réalité des espaces
│   ├── phase8_grammar_id.py        # Phase 8 : grammaire + bootstrap
│   ├── phase9b_tironian.py         # Phase 9B : inventaire tironien
│   ├── phase9d_positional_test.py  # Phase 9D : test positionnel
│   ├── phase10a_bigram_model.py    # Phase 10A : modèle bigramme
│   ├── phase10b_suffix_validation.py  # Phase 10B : validation suffixale
│   ├── phase10c_em_stenographic.py # Phase 10C : EM + hill-climbing (3 versions)
│   ├── phase10e_1_word_profiles.py # Phase 10E : profilage mots
│   ├── phase10e_2_botanical_hypotheses.py  # Phase 10E : ancres botaniques
│   ├── phase10e_3_word_hypotheses.py       # Phase 10E : mots fréquents
│   ├── phase10e_4_constraints.py   # Phase 10E : propagation de contraintes
│   ├── triage_test1_lunazzi.py     # Triage : test Lunazzi
│   ├── triage_test2_gladyseva.py   # Triage : test Gladyševa
│   ├── triage_test3_naibbe.py      # Triage : test Naibbe
│   └── build_botanical_anchors.py  # Construction des ancres botaniques
├── data/
│   ├── transcriptions/ZL.txt       # Transcription EVA complète
│   ├── corpus_latin_medical_extended.txt  # CORPUS PRINCIPAL (1.82M mots)
│   ├── latin_bigram_model.json     # Modèle de langue bigramme
│   ├── botanical_anchors.json      # 106 ancres botaniques scorées
│   ├── herbal_folio_words.json     # Mots EVA par folio herbal
│   ├── dict_latin_medical_suffixes.json  # Terminaisons latines
│   ├── tironian/                   # Notes tironiennes (Schmitz + mappings)
│   ├── raw_corpus_9a/              # Sources brutes des corpus
│   └── dictionaries/               # Dictionnaires latin/italien/français/espagnol
├── outputs/
│   ├── phase0_elimination.json     # → Phase 8
│   ├── phase3/ à phase8/           # Résultats détaillés par phase
│   ├── phase9d/                    # Test positionnel
│   ├── phase10b/ et phase10c/      # Validation + EM
│   ├── phase10e/                   # Attaque par les mots
│   └── triage/                     # 3 tests décisifs + DECISION.md
└── SYNTHESE_PROJET.md              # CE FICHIER
```

---

## 11. Glossaire rapide

| Terme | Définition |
|-------|------------|
| **EVA** | Extensible Voynich Alphabet — alphabet de transcription standard (Landini/King, 1998) |
| **IC** | Index de Coincidence — mesure de la "platitude" d'un texte. Latin ~0.065-0.080, random ~0.038 |
| **TTR** | Type/Token Ratio — mots uniques / mots totaux. VMS = 0.26 (naturel), chiffre = 0.69 |
| **Gallows** | Caractères EVA grands (f, k, p, t) — positionnellement contraints |
| **Bench chars** | Caractères EVA bas (e, c, i, ligatures ch, sh) — haute fréquence médiale |
| **NOYAU** | Voyelle précédant le terminateur dans un suffixe EVA (a, o, e, i, ou ∅) |
| **TERMINATEUR** | Consonne finale d'un suffixe EVA (y, r, l, s, d) |
| **Brachigraphie** | Système d'abréviation médiéval (ex : notes tironiennes) |
| **Crib** | Fragment de texte clair connu, utilisé pour casser un chiffre (ex : nom de plante identifié) |
| **IVTFF** | Intermediate Voynich Text File Format — format standard de transcription |

---

## 12. Pour repartir : checklist V2

- [ ] Récupérer les PDFs King & Andrisani (academia.edu) → tester leur table
- [ ] Construire un corpus vénitien/padouan médiéval (alternative au latin)
- [ ] Implémenter un solver mot-niveau combinant ancres botaniques + grille suffixale
- [ ] Tester l'hypothèse tironienne adaptée (Schmitz index → mapping EVA)
- [ ] Obtenir une clé API Anthropic pour le scoring LLM des pages décodées
- [ ] Considérer les 741 lectures alternatives EVA comme source de variabilité
