# PLAN D'ACTION - RECIPE_DATASET
## Referentiel Universel de Pharmacopee Medievale

Date: 2026-04-11
Responsable qualite: Claude (delegue par Guillaume)
Principe directeur: tokenisation mot-a-mot avec ref_id, zero compromis

---

## ETAT ACTUEL

Fait: R01-R08 (571 entrees), S01_AN (105 recettes, 12989 tokens), S05_MACER (25 monographies, 24148 tokens), S10_ALPHITA (1714 entrees, 74620 tokens).
Total: 12.6 MB, 1844 entrees, 111757 tokens.

A faire: S02_CI, S03_AUREA, S04_GRABADIN, S06_REGIMEN, S07_DALME, S08_AVICENNA, S09_COLLECTIO.
A ameliorer: S01_AN (105 -> 150 recettes), R02 (enrichissement continu).

---

## PHASE 1 - GAINS RAPIDES (estimee: 1 session)

### 1.1 S03_AUREA.json - Merger depuis Compare/
- Source: Compare/S03_AUREA.json (1 recette, 105 tokens, bonne qualite)
- Travail: Ajouter les ref_id manquants, valider contre R01-R08, integrer
- Effort: minimal
- Valeur: la recette Aurea Alexandrina est LE crib premium pour le VMS (f89r)

### 1.2 S06_REGIMEN.json - Parser Regimen Sanitatis
- Source: data/raw_corpus_9a/cleaned/clean_regimen_sanitatis.txt (18K)
- Travail: ecrire build_S06_REGIMEN.py, structure vers/distiques
- Effort: faible (petit fichier, structure reguliere comme Macer)
- Valeur: hygiene alimentaire salernitaine, recettes simples, overlap fort avec CI

### 1.3 S07_DALME.json - Parser inventaires pharmacie
- Source: Clean/PlantCypher/dalme_all_inventories_unified.csv (148KB, 6 inventaires)
- Travail: ecrire build_S07_DALME.py, adapter format inventaire (pas "recette" classique)
- Structure speciale: chaque entree = 1 item pharmacie (nom, quantite, prix, lieu)
- Effort: moyen (format different des recettes)
- Valeur: ancrage dans la realite materielle, prix reels, noms vernaculaires -> latin

### 1.4 Ameliorer S01_AN.json - 105 -> 150 recettes
- Probleme: notre extraction par mot-cle "Recipe" rate ~45 recettes
- Cause probable: certaines recettes n'ont pas le mot "Recipe" explicite dans l'OCR
- Action: comparer notre liste de 105 noms avec les 150 de Compare/S01_AN_final.json, identifier les manquantes, ajuster le parsing
- Effort: moyen

---

## PHASE 2 - EXTRACTION COMPLEXE (estimee: 2-3 sessions)

### 2.1 S09_COLLECTIO.json - CI latin depuis Collectio Salernitana
- Source: clean_collectio_salernitana_v2.txt (2.0M)
- Difficulte: melange italien (commentaires editoriaux De Renzi) et latin (textes originaux CI)
- Strategie: detecter les blocs latins par analyse linguistique (proportion de mots latins vs italiens), extraire les monographies CI
- Effort: eleve (separation langues, identification des entrees CI)
- Valeur: TRES HAUTE - c'est la meilleure source CI en latin qu'on a

### 2.2 S02_CI.json - Circa Instans complet
- Sources disponibles:
  a) CS2 (via S09) - meilleur latin mais melange
  b) CircaInstans.xml (101MB, Clean/) - OCR brut, qualite variable
  c) CI_fr Dorveaux (13911 l, vieux francais) - complet mais pas latin
  d) Compare/S02_CI.json (1453 entrees Dorveaux) - existe mais qualite tokens mediocre
- Strategie recommandee: d'abord extraire le max de S09 (CS2 latin), puis completer avec le Dorveaux pour les entrees manquantes, enfin tenter CircaInstans.xml pour les cas restants
- Effort: eleve (multi-source, reconciliation)
- Valeur: CRITIQUE - le CI est le texte fondateur de la pharmacopee salernitaine

### 2.3 Enrichir R02 en continu
- Chaque nouveau parser ajoute des formes d'ingredients
- Maintenir le pattern: AN_INGREDIENTS, MACER_INGREDIENTS, etc.
- Objectif: R02 devrait depasser 500 entrees propres (vs 268 actuellement)

---

## PHASE 3 - GROS CORPUS (estimee: 3-4 sessions)

### 3.1 S08_AVICENNA.json - Canon Medicinae
- Source: clean_canon_medicinae_1507.txt (4.7M)
- Difficulte: tres gros fichier, structure complexe (livres, fens, traites, chapitres)
- Strategie: NE PAS tout parser. Cibler les sections pharmaceutiques:
  - Livre II (simples medicinaux - equivalent du CI mais arabe->latin)
  - Livre V (medicaments composes - equivalent de l'AN)
- Effort: tres eleve (identification des sections pertinentes dans 4.7M)
- Valeur: haute (autorite medicale supreme au Moyen Age, reference pour le VMS)

### 3.2 Clavis Sanationis (bonus, pas dans S01-S10 initial)
- Source: clean_clavis_sanationis_biusante.txt (798K)
- Type: glossaire medical (comme Alphita mais plus oriente pathologie)
- Decision: creer un S11_CLAVIS.json si le schema le permet
- Effort: moyen (structure glossaire, parser similaire a S10_ALPHITA)

---

## PHASE 4 - SOURCES A TROUVER

### 4.1 S04_GRABADIN.json - Liber Servitoris / Grabadin
- Auteur: pseudo-Mesue (Jean de Saint-Amand?) ou Abulcasis pour le Liber Servitoris
- Statut: AUCUNE source texte trouvee en ligne
- Pistes:
  a) archive.org - chercher "Grabadin", "Mesue", "Opera Mesuae", "Liber Servitoris Abulcasis"
  b) Google Books - editions latines du XVIe (Mesue cum expositione, Venise 1471, etc.)
  c) BnF Gallica - manuscrits numerises
  d) Bayerische Staatsbibliothek - MDZ digital
  e) Wellcome Library - manuscrits medicaux medievaux
- Guillaume peut: utiliser un script browser pour extraire le texte OCR si on trouve une edition scannee
- Valeur: TRES HAUTE - le Grabadin est la principale source de recettes composees apres l'AN

### 4.2 DALME supplementaires
- dalme.org a surtout des inventaires commerciaux generaux
- Pistes specifiques pharmacie:
  a) Chercher "apothicaire inventaire medieval" / "apothecary inventory medieval latin"
  b) Publications de Michael McVaugh (pharmacie medievale Crown of Aragon)
  c) Publications de Patrick Gautier Dalche et Danielle Jacquart
  d) Revue "Medievale" et "Sudhoffs Archiv" pour articles avec transcriptions
- On a deja 6 inventaires dans Clean/PlantCypher/ - les parser proprement d'abord

### 4.3 Tacuinum Sanitatis
- Pas dans notre schema initial mais TRES pertinent
- Texte court par entree (1 plante = nom + nature + proprietes + danger + remede)
- Sources possibles: editions Schuba ou Elkhadem
- Structure ideale pour tokenisation (tres normalise)
- Decision: ajouter un S12_TACUINUM.json si source trouvee

---

## PHASE 5 - SOURCES PASSIONNES ET COLLECTIONS EN LIGNE

Le monde medieval-pharma a une communaute active. Voici les pistes les plus prometteuses:

### 5.1 Sites academiques avec textes complets
- **Corpus Corporum** (mlat.uzh.ch) - corpus de textes latins medievaux, recherche plein texte
- **The Latin Library** (thelatinlibrary.com) - textes latins classiques et medievaux
- **Digital Medievalist** - communaute et ressources
- **Monastic Medicine** (blogs specialises) - transcriptions de manuscrits par des passionnes

### 5.2 Reconstitution historique et reenactment
- Communautes SCA (Society for Creative Anachronism) - membres transcrivent des recettes medievales
- Blogs "medieval kitchen" et "medieval pharmacy" - souvent avec sources latines originales
- Reddit r/AskHistorians et r/MedievalHistory - threads sur pharmacopee medievale
- Groupes Facebook "Medieval Medicine" et "History of Pharmacy"

### 5.3 Projets de transcription collaborative
- **FromThePage** - plateforme de transcription participative de manuscrits
- **Transkribus** - HTR (Handwritten Text Recognition) pour manuscrits medievaux
- **e-codices** (Suisse) - manuscrits numerises avec parfois transcriptions

### 5.4 Scripts browser pour Guillaume
Si on trouve une source scannee mais sans texte extractible:
- Script Tampermonkey pour extraire le texte OCR des pages archive.org
- Script pour scraper les pages de Google Books en mode "snippet view"
- Script pour extraire les transcriptions de FromThePage
- Script pour concatener les pages OCR de Gallica/BnF

Je fournirai ces scripts sur demande, adaptes a chaque source specifique.

---

## PRIORITES ORDONNEES

| # | Tache | Effort | Valeur | Priorite |
|---|-------|--------|--------|----------|
| 1 | S03_AUREA merger | minimal | haute (crib premium) | IMMEDIAT |
| 2 | S06_REGIMEN parser | faible | moyenne | IMMEDIAT |
| 3 | S07_DALME parser | moyen | haute (ancrage reel) | IMMEDIAT |
| 4 | S01_AN amelioration 105->150 | moyen | haute | COURT TERME |
| 5 | S09_COLLECTIO CI latin | eleve | tres haute | COURT TERME |
| 6 | S02_CI complet | eleve | critique | MOYEN TERME |
| 7 | Trouver source Grabadin | variable | tres haute | EN PARALLELE |
| 8 | S08_AVICENNA extraits | tres eleve | haute | MOYEN TERME |
| 9 | S11_CLAVIS bonus | moyen | moyenne | OPTIONNEL |
| 10 | Tacuinum Sanitatis | variable | haute | SI SOURCE TROUVEE |

---

## METRIQUES CIBLES

- R02_ingredients: 268 -> 500+ entrees propres (enrichissement iteratif)
- Tokens total: 111757 -> 300000+ (objectif realiste avec CI + Regimen + DALME + Avicenna)
- Sources tokenisees: 3/10 -> 8/10 minimum
- Taux GRAM dans S01_AN: 40% -> 25% (reclassification avec meilleurs dicos)
- Couverture ref_id dans INGR: ameliorer les 663 sans ref_id dans S01_AN

---

## NOTES POUR GUILLAUME

Tu peux contribuer directement sur:
1. Recherche du Grabadin/Liber Servitoris - c'est la source la plus critique manquante
2. Scripts browser si on trouve des scans sans OCR extractible
3. Exploration communautes de passionnes (SCA, blogs, Reddit) pour des transcriptions
4. Validation des recettes tokenisees contre ta connaissance du domaine

Moi je me charge de:
1. Qualite de tokenisation (mot-a-mot, ref_id, coherence cross-refs)
2. Ecriture des parsers (build_S0X.py)
3. Enrichissement continu R02
4. Verification systematique de chaque output
