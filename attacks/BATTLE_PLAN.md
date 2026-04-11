# PLAN DE BATAILLE — Decodage computationnel du VMS

## Philosophie

> "La bataille sera dure. Il y aura des echecs.
> On ne joue pas tout sur une solution.
> Chaque mot a N candidats, chaque candidat a un score.
> La verite emerge de la CONVERGENCE."

Ce n'est pas un chiffre militaire. C'est un carnet professionnel
ecrit dans un raccourci personnel. On ne "casse" pas un code,
on APPREND a lire — mot par mot, contrainte par contrainte.

### Principes de Turing adaptes

1. **MULTIPLICITE DES CRIBS.** Turing n'avait pas UNE seule interception.
   Il en avait des MILLIERS. Nous avons 150 recettes AN, 1453 CI, 2484 DALME.
   Chaque recette est un TEST independant. On ne mise pas sur l'Aurea seule.

2. **PROBABILITES, PAS CERTITUDES.** Chaque attaque produit des CANDIDATS
   avec des SCORES. Rien n'est vrai ou faux — tout est plus ou moins probable.
   Le mapping final emerge de la convergence multi-source.

3. **LES ECHECS SONT INFORMATIFS.** Si une attaque echoue, elle ELIMINE
   des hypotheses et REDUIT l'espace. L'echec nourrit les attaques suivantes.

4. **COHERENCE GLOBALE.** Un mapping qui marche sur 1 page mais pas sur
   les autres est FAUX. Chaque candidat doit etre teste sur TOUT le corpus.

5. **LE TEXTE A DU SENS.** Le critere ultime : "un apothicaire ecrirait-il ca?"
   Si le decode dit "nourriture" 435 fois, c'est faux.

---

## ARSENAL

### Donnees confirmees (fiabilite haute)
| Arme | Volume | Usage |
|------|--------|-------|
| 16 logograms confirmes | 16 mappings fixes | Squelette grammatical |
| 14 suffixes flexionnels | 14 types + stats | Classification syntaxique |
| 127 racines classees | LEX/FUNC + paradigme | Vocabulaire de base |
| 492 ingredients references | Cross-ref AN+DALME+Lylye | Dictionnaire de l'attendu |
| 25 verbes references | 264 formes flechies | Reconnaissance des verbes |
| 4252 recettes tokenisees | AN+CI+Macer+Regimen+DALME | Patterns structurels |
| Distribution par folio | 500 mots × 148 folios | Matching par frequence |
| 141 qualites galeniques | Circa Instans | Proprietes des plantes |

### Puissance de calcul
| Ressource | Usage |
|-----------|-------|
| GPU | Entrainement modele de langue medieval latin |
| ML pipeline | Scoring de vraisemblance des decodages candidats |
| CPU multi-thread | Brute-force contraint sur espaces reduits |

### Terrain (le VMS)
| Element | Volume |
|---------|--------|
| Texte VMS total | ~39000 tokens, 7820 mots uniques |
| Section herbal | ~20000 tokens (registres -ol et -edy) |
| Section pharma | ~8000 tokens |
| Section balnea | ~5000 tokens |
| f103r | ~800 tokens (crib Aurea) |

---

## STRUCTURE DE DONNEES CENTRALE : LE REGISTRE DE CANDIDATS

**Chaque mot EVA a un REGISTRE de candidats, pas une solution unique.**

```json
{
  "eva_word": "chckhy",
  "frequency": 245,
  "n_folios": 16,
  "suffix": "?",
  "root": "chckh",
  "sections": {"herbal_A": 80, "pharma": 120, "balnea": 45},

  "candidates": [
    {
      "latin": "myrrha",
      "ref_id": "I_myrrha",
      "score_total": 0.87,
      "scores": {
        "frequency_match": 0.92,
        "crib_aurea": 0.85,
        "crib_hiera": null,
        "ka_phonetic": 0.45,
        "word_length": 0.78,
        "context_bigram": 0.91,
        "section_match": 0.88,
        "ml_lm_score": 0.82
      },
      "evidence": [
        {"source": "attack_03", "detail": "16 folios vs 12.6 expected, delta=3.4"},
        {"source": "attack_01_aurea", "detail": "Position 5 sur f103r match myrrha position 5 dans Aurea"},
        {"source": "session_6", "detail": "matrice de presence match"}
      ],
      "counter_evidence": [
        {"source": "attack_04", "detail": "chckhy=5 glyphes mais myrrha=6 lettres=2 syllabes, ratio atypique"}
      ]
    },
    {
      "latin": "mastix",
      "ref_id": "I_mastix",
      "score_total": 0.42,
      "scores": {
        "frequency_match": 0.65,
        "crib_aurea": null,
        "ka_phonetic": 0.12,
        "word_length": 0.90,
        "context_bigram": 0.35,
        "section_match": 0.55,
        "ml_lm_score": 0.38
      },
      "evidence": [...],
      "counter_evidence": [...]
    }
  ],

  "best_candidate": "I_myrrha",
  "confidence": 0.87,
  "status": "PROBABLE"
}
```

**Regles du registre :**
- Chaque attaque AJOUTE des scores, elle ne remplace jamais
- Le score_total est un COMBINE pondere de tous les scores
- Un candidat avec 1 score tres haut et 4 nulls < un candidat avec 5 scores moyens
- Le status est : CONFIRMED (>0.95), PROBABLE (>0.75), POSSIBLE (>0.50), DOUBTFUL (<0.50)

---

## LES ATTAQUES

### Phase 0 — INFRASTRUCTURE (prerequis)

```
attacks/lib/
|-- loader.py           Charge R01-R08 + G01-G03 + S01-S07
|-- vms_parser.py       Parse ZL.txt en mots EVA avec folio/section/ligne/position
|-- candidate_store.py  Registre central des candidats (JSON persistant)
|-- scorer.py           Fonctions de scoring (frequence, longueur, contexte)
|-- reporter.py         Genere des rapports lisibles des resultats
```

**candidate_store.py** est le COEUR. C'est un fichier JSON persistant
qui accumule les scores de toutes les attaques. Chaque attaque lit le store,
ajoute ses scores, et ecrit le store mis a jour.

---

### Phase 0.5 — SEGMENTATION PROBABILISTE (avant les cribs)

**Probleme :** On ne peut pas aligner une recette sur un bloc VMS
si on ne sait pas ou le bloc commence et finit.

**Hypotheses de separateurs (a scorer, pas a presumer) :**
- `-am` en fin de ligne (71% = probable separateur de phrase)
- Logogram `r` (recipe) = debut de recette ?
- Etoiles marginales / marqueurs visuels sur les folios
- Changement de registre suffixal (-ol → -edy) = changement de section ?

**Methode :**
1. Lister tous les candidats separateurs
2. Pour chaque hypothese, calculer la distribution des segments resultants
3. Comparer avec les longueurs de recettes dans S01-S07
4. Scorer chaque hypothese de segmentation
5. Travailler avec les TOP 3 segmentations en parallele (pas une seule)

**Output :** 3 hypotheses de segmentation du VMS avec scores

---

### ATTAQUE 4 — TEST FONDAMENTAL : MOT ou SYLLABE ? (en premier !)
```
Priorite : ★★★★★ PREMIER TEST A FAIRE
Impact : Valide ou invalide TOUT le postulat mot-a-mot du registre
```

**Principe :**
Si le VMS est logo-syllabique (comme les hieroglyphes),
alors le registre mot-a-mot est BIAISE et il faut tout repenser.
Ce test DOIT passer avant toute autre attaque.

**Methode :**
1. Pour chaque ingredient de R02, compter lettres ET syllabes latines
2. Pour chaque mot VMS candidat, compter les glyphes EVA
3. Tester 3 correlations :
   a) longueur_EVA × lettres_latin (encodage alphabetique)
   b) longueur_EVA × syllabes_latin (encodage syllabique)
   c) pas de correlation (encodage par code/logogramme pur)
4. Si (a) gagne → K&A a raison, le registre mot-a-mot est valide
5. Si (b) gagne → systeme syllabique, il faut un registre syllabe-a-syllabe
6. Si (c) gagne → nomenclator pur, le registre mot-a-mot est valide
   mais K&A est faux (chaque mot = un code arbitraire)

**CE TEST EST PREREQUIS A TOUT LE RESTE.**

---

### ATTAQUE 3 — GRAMMAIRE SUFFIXALE (contraintes dures)
```
Priorite : ★★★★★ DEUXIEME ATTAQUE (apres test fondamental)
Impact : Classe les 39000 tokens en categories syntaxiques
```

---

### ATTAQUE 1 — CRIB MULTI-RECETTES (pas juste l'Aurea)
```
Priorite : ★★★★ (APRES attaques 3+4 qui reduisent l'espace)
Impact : Propose des mappings directs EVA → ingredient
Prerequis : Attaques 3 et 4 terminees + segmentation probabiliste
```

**Principe :**
On ne crib PAS avec une seule recette. On crib avec TOUTES les recettes
qui pourraient etre dans le VMS.

**Methode :**
1. Pour CHAQUE recette de S01_AN (150), extraire la SIGNATURE :
   - Nombre d'ingredients
   - Nombre de verbes
   - Longueur totale
   - Sequence de types (VERB INGR INGR DOSE QTY...)
2. Pour CHAQUE page/bloc du VMS (folios pharma : f103r-f116r) :
   - Retirer les logograms connus
   - Compter les mots restants
   - Comparer la longueur avec les recettes AN
   - Tester l'alignement avec les 10 meilleures recettes candidates
3. Pour chaque alignement :
   - Proposer des candidats pour chaque position
   - Scorer la coherence (meme mot EVA = meme ingredient partout?)
   - Stocker dans le registre

**Output :** Pour chaque folio pharma, les 5 recettes AN les plus probables +
les mappings EVA → ingredient proposes par chacune.

---

### ATTAQUE 2 — MATCHING PAR DISTRIBUTION (statistique pure)
```
Priorite : ★★★★
Impact : Identifie les 30 ingredients les plus probables
```

**Principe :**
Distribution = verite. Les probas ne mentent pas.

**Methode multi-critere :**
Pour chaque paire (mot_VMS, ingredient_ref) :
1. **Frequence absolue** : correlation entre freq_VMS et freq_AN
2. **Distribution par folio** : chi-carre entre distribution VMS et distribution attendue
3. **Co-occurrence** : si myrrha+crocus co-occurrent dans 40% des recettes AN,
   leurs mots VMS equivalents doivent co-occurrer sur ~40% des folios
4. **Exclusion mutuelle** : si un mot VMS est sur 16 folios et un ingredient est dans 52% des recettes
   mais un AUTRE ingredient est dans 53% → distinguer par co-occurrence
5. **Section-specifique** : certains ingredients sont herbal-only, d'autres pharma-only

**Algorithme :**
PREMIERE PASSE : scoring par rang (pas d'assignation forcee).
Pour chaque mot VMS, classer les ingredients par score decroissant.
Pour chaque ingredient, classer les mots VMS par score decroissant.
Pas de matching bijectif en premiere passe — le systeme peut avoir
des homographes (1 mot EVA = 2 concepts) ou des synonymes graphiques
(2 mots EVA = 1 concept).

DEUXIEME PASSE (apres convergence attaque 7) :
Hungarian assignment sur l'espace REDUIT par toutes les contraintes.
A ce stade, la bijection est plus justifiee.

**Output :** Top 50 matchs avec scores + rang d'alternatives

---

### ATTAQUE 3 — GRAMMAIRE SUFFIXALE (decoder la structure)
```
Priorite : ★★★★
Impact : Classe les 39000 tokens en categories syntaxiques
```

**Principe :**
Les 14 suffixes EVA correspondent aux 17 types de tokens (VERB, INGR, DOSE...).
Le matching entre les matrices de transition suffit a trouver la correspondance.

**Methode :**
1. Matrice de transition des TYPES dans les recettes reelles (17×17)
2. Matrice de transition des SUFFIXES dans le VMS (14×14)
3. Optimisation : trouver le mapping SUFFIXE→TYPE qui minimise la distance
   entre les deux matrices (probleme d'affectation, solvable)
4. Contraintes supplementaires :
   - -am est terminateur (71% en fin) → PUNCT ou fin de phrase
   - -or est ouvreur (22% en debut) → probablement VERB ou NAME
   - -edy est procedural (78% balnea+pharma) → INGR ou VERB
   - -ol est descriptif (55% herbal) → QUAL ou INGR
5. ML : entrainer un classifieur sur les mots de type CONNU (logograms)
   et predire le type des mots inconnus

**Output :** Table SUFFIXE → TYPE + probabilites

---

### ATTAQUE 4 — CONTRAINTES DE FORME (longueur, structure)
```
Priorite : ★★★
Impact : Filtre les candidats impossibles
```

**Methode :**
1. Longueur EVA vs longueur latin (correlation?)
2. Structure interne : les mots EVA ont-ils des patterns de composition?
   (prefixe + racine + suffixe, comme en latin?)
3. Debut/fin de mot : les mots EVA commencant par qo- sont-ils un type?
   Les mots finissant par -aiin un autre?
4. Hapax vs mots frequents : les hapax VMS matchent-ils les ingredients rares?

---

### ATTAQUE 5 — MODELE DE LANGUE MEDIEVAL (ML/GPU)
```
Priorite : ★★ (utile pour ELIMINER le charabia, pas pour departager 2 candidats latins valides)
Impact : Filtre — tue les decodages absurdes, ne tranche pas entre plausibles
Note : "recipe myrrham" et "recipe masticem" auront la meme perplexite.
       Le LM sert a tuer "recipe xkzqdm", pas a choisir entre myrrha et mastix.
```

**Principe :**
Entrainer un Language Model sur nos 470K lignes de corpus medieval latin.
Pour chaque decodage candidat, calculer P(texte_decode | modele_latin).
Un bon decodage doit avoir une perplexite BASSE.

**Methode :**
1. Corpus d'entrainement :
   - clean_antidotarium_nicolai (1726 lignes)
   - clean_circa_instans (174 lignes latin OCR)
   - clean_macer_floridus (2608 lignes)
   - clean_collectio_salernitana v1-5 (~32K lignes)
   - clean_canon_medicinae (~35K lignes)
   - corpus_herbal.txt + corpus_pharma.txt + corpus_balnea.txt (5.2M)
2. Modele : character-level ou word-level LM (GPT-2 fine-tune ou LSTM)
3. Pour chaque mot VMS, pour chaque candidat latin :
   - Remplacer le mot EVA par le candidat dans le contexte
   - Calculer la log-vraisemblance du contexte decode
4. Les candidats qui produisent du "bon latin" scorent haut
5. Les candidats qui produisent du charabia scorent bas

**GPU necessaire** pour l'entrainement. Inference possible CPU.

**Output :** Score LM pour chaque candidat dans le registre

---

### ATTAQUE 6 — ANALYSE CONTEXTUELLE (bigrams, trigrams)
```
Priorite : ★★★
Impact : Exploite le VOISINAGE de chaque mot
```

**Principe :**
Dans le latin medieval, certaines combinaisons sont frequentes :
"recipe" est TOUJOURS suivi d'un ingredient.
"cum" est TOUJOURS suivi d'un nom (ingredie, tool, liquid).
"ana" est TOUJOURS suivi d'une quantite.
"contra" est TOUJOURS suivi d'une maladie.

Si on connait un mot, les mots ADJACENTS sont contraints.

**Methode :**
1. Construire les bigrams types du corpus de reference (R01+R02)
2. Pour chaque logogram VMS connu (16), lister les mots adjacents
3. k=cum est suivi de quels mots VMS? → ces mots sont des ingredients/outils
4. r=recipe est suivi de quels mots? → ces mots sont des ingredients
5. Cross-referencer avec les candidats du registre

---

### ATTAQUE 7 — CONVERGENCE (CSP + renforcement mutuel)
```
Priorite : ★★★★★ (finale)
Impact : DECISIF
```

**Principe :**
Toutes les attaques precedentes ont alimente le REGISTRE DE CANDIDATS.
Maintenant on exploite les CONTRAINTES CROISEES.

**Contraintes :**
- **Unicite** : un mot EVA = un seul mot latin (pas d'homographes dans un systeme professionnel)
- **Coherence positionnelle** : si X=myrrha, X doit apparaitre la ou myrrha est attendue
- **Coherence contextuelle** : si X=myrrha et Y=crocus, X et Y doivent co-occurrer
  avec la bonne frequence
- **Coherence de type** : si -ol = INGR, alors tous les mots en -ol doivent etre des ingredients
- **Coherence globale** : le texte decode doit faire SENS (pas "nourriture dieu nourriture")

**Algorithme :**
1. Fixer les mots les plus CERTAINS (score > 0.95)
2. Propager les contraintes (arc consistency)
3. Pour les mots restants, tester les candidats par ordre de score
4. A chaque ajout, verifier toutes les contraintes
5. Si contradiction → backtrack
6. Iterer jusqu'a convergence

---

## STRUCTURE DU REPERTOIRE

```
attacks/
|
|-- BATTLE_PLAN.md                  <- CE FICHIER
|
|-- lib/                            <- Code partage
|   |-- loader.py                   <- Charge referentiels + VMS
|   |-- vms_parser.py               <- Parse ZL.txt en tokens structures
|   |-- candidate_store.py          <- Registre central (coeur du systeme)
|   |-- scorer.py                   <- Fonctions de scoring
|   |-- constraints.py              <- Moteur de contraintes
|   |-- lm_scorer.py                <- Interface modele de langue
|   |-- reporter.py                 <- Rapports lisibles
|
|-- attack_01_crib.py               <- Multi-crib (150 recettes × folios pharma)
|-- attack_02_distribution.py       <- Matching par frequence/co-occurrence
|-- attack_03_grammar.py            <- Mapping suffixes → types
|-- attack_04_form.py               <- Contraintes de longueur/structure
|-- attack_05_lm.py                 <- Modele de langue (GPU)
|-- attack_06_context.py            <- Bigrams/trigrams contextuels
|-- attack_07_convergence.py        <- CSP combine
|
|-- results/                        <- Resultats persistants
|   |-- candidate_registry.json     <- LE fichier central (tous les candidats)
|   |-- attack_01_results.json
|   |-- attack_02_results.json
|   |-- ...
|   |-- convergence_report.md       <- Rapport final lisible
|
|-- models/                         <- Modeles ML
|   |-- train_lm.py                 <- Entrainement LM medieval
|   |-- lm_medieval_latin/          <- Modele entraine
```

---

## WORKFLOW

```
   Phase 0 : INFRASTRUCTURE (loader, parser, candidate_store)
       │
   Phase 0.5 : SEGMENTATION PROBABILISTE (ou sont les frontieres?)
       │
   Phase 1 : CONTRAINTES DURES (pas d'hypothese sur le contenu)
       │
       ├── ATTAQUE 4 : Test fondamental MOT vs SYLLABE
       │   └── Si syllabique → STOP, refaire le registre
       │   └── Si mot-a-mot → continuer
       │
       ├── ATTAQUE 3 : Grammaire suffixale (suffixe → type)
       │
       └── ATTAQUE 2 : Distribution de frequence (scoring souple)
               │
   Phase 2 : CRIBS (espace deja reduit par Phase 1)
       │
       ├── ATTAQUE 1 : Multi-crib (150 recettes × folios pharma)
       │
       └── ATTAQUE 6 : Contexte (bigrams autour des logograms connus)
               │
   Phase 3 : SCORING AVANCE
       │
       └── ATTAQUE 5 : LM medieval (elimine le charabia)
               │
   Phase 4 : CONVERGENCE
       │
       └── ATTAQUE 7 : CSP combine (contraintes croisees)
               │
       ┌───────┴───────┐
       │   RESULTAT     │
       │  candidate_    │
       │  registry.json │
       │  + rapport     │
       └───────────────┘
```

**Chaque attaque :**
1. Lit le registre actuel
2. Calcule ses scores
3. Ajoute ses scores au registre
4. Sauvegarde le registre mis a jour
5. Genere un rapport de ce qu'elle a trouve

Les attaques sont INDEPENDANTES et peuvent tourner en PARALLELE.
Elles communiquent uniquement via le registre central.

---

## CRITERES DE SUCCES (progressifs)

| Niveau | Critere | Comment on le mesure |
|--------|---------|---------------------|
| BRONZE | 20 mots EVA ont un candidat a score > 0.75 | Registre apres attaques 1-3 |
| ARGENT | 50 mots decodes avec coherence croisee (3+ attaques concordent) | Registre apres attaque 7 |
| OR | La grammaire suffixale resolue + 100 mots decodes | Attaque 3 + registre |
| PLATINE | Une recette complete lue et identifiee (ex: Aurea sur f103r) | Verification manuelle |
| DIAMANT | Le systeme d'ecriture est compris et reproductible par un humain | Publication |

---

## CE QUI PEUT MAL TOURNER (et comment s'adapter)

| Risque | Probabilite | Mitigation |
|--------|------------|------------|
| L'Aurea n'est PAS sur f103r | 30% | Les attaques 2-6 ne dependent pas du crib |
| Les suffixes ne sont PAS des types syntaxiques | 20% | L'attaque 2 (frequence) marche independamment |
| Le K&A est fondamentalement faux | 15% | Les attaques structurelles (1-4) ne dependent pas de K&A |
| Le VMS n'est PAS pharmaceutique | 5% | Les distributions de frequence le refuteraient vite |
| Nos sources de reference manquent LE bon texte | 25% | Ajouter de nouvelles sources enrichit le registre sans tout refaire |
| Le systeme d'ecriture n'est pas un code mais un langage construit | 10% | Le ML (attaque 5) le detecterait par la distribution atypique |
| Le systeme est LOGO-SYLLABIQUE (comme les hieroglyphes) | 15% | L'attaque 4 (test fondamental) le detecte AVANT tout le reste. Si positif, refaire le registre en syllabe-a-syllabe |

---

## PRINCIPES NON-NEGOCIABLES

1. **JAMAIS de solution unique.** Toujours N candidats avec scores.
2. **JAMAIS de raccourci.** Chaque mapping est teste sur TOUT le corpus.
3. **TOUJOURS reproductible.** Chaque resultat peut etre regenere par le script.
4. **TOUJOURS stocke.** Le registre est persistant, rien ne se perd.
5. **L'ECHEC EST UNE DONNEE.** Une attaque qui ne trouve rien REDUIT l'espace.
