# OPERATION TACUINUM — Campagne complete

> "C'est la bataille de notre projet. On tape large.
> C'est statistiquement impossible qu'on ne trouve rien.
> Si on ne trouve rien, c'est que TOUT est a revoir."

## Pourquoi le Tacuinum est notre meilleure chance

C'est le SEUL texte medieval qui combine :
1. **Structure TABULAIRE RIGIDE** — 7 colonnes fixes par entree
2. **Vocabulaire FERME** — 9 formules galeniques, 63 mots de gradus
3. **280 entrees** — coincidence suspecte avec les ~280 tokens/15.8 du VMS astro
4. **ILLUSTRE** — comme le VMS, chaque substance a une image
5. **CROISE** avec CI et AN — memes ingredients dans les 3 sources
6. **Organisation par TABLES** de 7 — les pages zodiac VMS ont des sous-folios

Si l'astro VMS est un Tacuinum, on a un crib de 280 entrees avec un
vocabulaire de 63 mots. L'espace de recherche est ridiculement petit.

---

## Donnees

### Tacuinum (reference)
- **S12_TACUINUM.json** : 280 substances, 40 tables de 7
- Source : Wuerzburg Arabic-Latin Corpus (edition savante TEI-XML)
- 9 formules galeniques : calidum+siccum (80x), calidum+humidum (54x), frigidum+siccum (31x)...
- Colonnes GRADUS : 63 mots uniques seulement
- **Qualites : calidum=166, frigidum=63, siccum=113, humidum=80**

### VMS cible (astro/cosmo f58-f73)
- 32 folios, 4437 tokens, 2007 mots uniques
- Suffixes dominants : -al (353x), -dy (354x), -ar (335x) → registre DIFFERENT du herbal
- 4437 tokens / 280 entrees = **15.8 tokens par entree** → taille d'une fiche Tacuinum
- Top mots (hors logograms) : oteey(35x), okal(29x), otar(27x), okeey(27x), dair(24x)

---

## Structure du Tacuinum — les 7 colonnes

```
| Col | Latin | Sens | Vocab | Signature statistique |
|-----|-------|------|-------|----------------------|
| 1 | NOMINA | Nom substance | 280 unique | OUVERT, divers |
| 2 | NATURA | Qualite Galien | ~9 formules | TRES FERME, 4 mots-cles |
| 3 | GRADUS | Degre | 63 mots | FERME, repetitif |
| 4 | MELIUS | Meilleur type | 628 mots | SEMI-OUVERT, adjectifs |
| 5 | IUVAMENTUM | Benefice | 525 mots | SEMI-OUVERT, verbes+corps |
| 6 | NOCUMENTUM | Nocivite | 435 mots | SEMI-OUVERT, symptomes |
| 7 | REMOTIO | Remede | 458 mots | SEMI-OUVERT, "cum" + ingr |
```

Chaque colonne a une SIGNATURE de vocabulaire unique.
C'est ce qui rend le matching possible.

---

## LES 10 OPERATIONS

### PHASE 1 : RECONNAISSANCE (pas d'hypothese, que des mesures)

#### OP-1 : COMPTAGE STRUCTUREL
```
Duree : 10 min | Script : op1_structure.py | Prerequis : rien
```

Compter les elements structurels sur chaque page astro :
- Nombre de labels/annotations dans ZL.txt (marqueurs <!...>)
- Nombre de lignes par sous-folio
- Nombre de blocs separes par des sauts
- Nombre de figures/nymphes (compter les marqueurs visuels)

Comparer avec 7 (Tacuinum), 12 (zodiac classique), 28-30 (calendrier lunaire).

---

#### OP-2 : PROFIL STATISTIQUE DE L'ASTRO
```
Duree : 20 min | Script : op2_profile.py | Prerequis : rien
```

Profiler la section astro independamment de toute hypothese :
- Frequence de chaque mot
- Distribution des suffixes (-al, -ar, -dy, -ol...)
- Longueur moyenne des mots
- Ratio logograms / mots pleins
- Bigrams les plus frequents
- Position des mots dans les lignes (debut/milieu/fin)
- Repetitivite (combien de mots couvrent 50% du texte?)

Comparer avec le profil du herbal et du pharma.

---

#### OP-3 : PROFIL DU TACUINUM
```
Duree : 20 min | Script : op3_tacuinum_profile.py | Prerequis : S12
```

Meme profil mais pour le Tacuinum :
- Frequence de chaque mot latin par colonne
- Taille du vocabulaire par colonne
- Bigrams les plus frequents
- Repetitivite par colonne
- Mots partages entre colonnes

---

### PHASE 2 : TESTS D'HYPOTHESE (chaque test est independant)

#### OP-4 : DISTRIBUTION GALENIQUE (test chi-carre)
```
Duree : 30 min | Script : op4_galenic.py | Prerequis : OP-2
```

**Hypothese :** 4 mots VMS frequent dans l'astro correspondent a
calidum:frigidum:siccum:humidum dans le ratio 166:63:113:80.

**Test :**
1. Prendre les N mots VMS les plus frequents dans l'astro (N=4,5,6,8,10)
2. Pour chaque combinaison de 4 parmi N :
   - Tester le chi-carre contre le ratio Tacuinum
   - Tester aussi contre le ratio CI (pour controle)
   - Tester contre une distribution aleatoire (permutation test)
3. Reporter la MEILLEURE combinaison et son p-value

Si p < 0.01 pour une combinaison et p > 0.1 pour les alternatives → signal fort.

---

#### OP-5 : VOCABULAIRE POSITIONNEL (test de fermeture)
```
Duree : 1h | Script : op5_positional.py | Prerequis : OP-1
```

**Hypothese :** Si chaque "fiche" a 7 colonnes, alors la position N
dans chaque fiche a un vocabulaire de taille FIXE correspondant a
la colonne N du Tacuinum.

**Test :**
1. Segmenter le texte astro en blocs de K tokens
   (tester K = 7, 10, 14, 16, 20, 28 — ne pas presumer)
2. Pour chaque K, pour chaque position 1..K dans les blocs :
   - Compter les mots uniques a cette position
   - Calculer le coefficient de variation
3. Chercher un K ou certaines positions ont un vocabulaire TRES petit
   (ex: position 3 avec ~60 mots = colonne GRADUS?)
4. Si un K produit une "empreinte" de taille de vocabulaire qui matche
   le profil du Tacuinum (9, 63, 280, 525...) → c'est le bon K

Si aucun K ne produit de signature → le texte n'est PAS tabulaire.

---

#### OP-6 : ANCRES CROISEES HERBAL × ASTRO
```
Duree : 30 min | Script : op6_crossref.py | Prerequis : rien
```

**Hypothese :** Les ingredients partages entre CI et Tacuinum
apparaissent AUSSI dans les deux sections VMS (herbal ET astro).

**Test :**
1. Lister les substances qui sont dans BOTH Tacuinum ET R02_ingredients :
   - myrrha, crocus, mel, aloe, rosa, cinnamomum... (probablement 30-50)
2. Pour chaque substance partagee, trouver le mot VMS candidat (session 6)
3. Verifier si ce mot EVA apparait dans les DEUX sections (herbal + astro)
4. Calculer le taux de match : combien de substances partagees ont
   un mot EVA present dans les deux sections?

Si le taux est > 30% → les deux sections encodent les memes ingredients → fort.
Si < 10% → sections independantes, pas forcement le meme codebook.

---

#### OP-7 : TEST DE REPETITIVITE STRUCTURELLE
```
Duree : 30 min | Script : op7_repetitivity.py | Prerequis : OP-1
```

**Hypothese :** Le Tacuinum est HAUTEMENT repetitif (memes mots
dans la colonne NATURA pour 280 entrees). Si le VMS astro encode
un Tacuinum, il doit avoir un niveau de repetitivite similaire.

**Test :**
1. Calculer le TTR (Type-Token Ratio) du Tacuinum par colonne
2. Calculer le TTR du VMS astro
3. Calculer le TTR du VMS herbal (controle)
4. Calculer le TTR du VMS pharma (controle)
5. Comparer :
   - TTR astro ~ TTR GRADUS (tres repetitif) → match
   - TTR astro ~ TTR herbal → pas un Tacuinum

Aussi : calculer l'entropie de Shannon par section. Le Tacuinum
a une entropie BASSE (vocabulaire ferme, repetitions).

---

#### OP-8 : PATTERN DE SUFFIXES PAR POSITION
```
Duree : 1h | Script : op8_suffix_position.py | Prerequis : OP-1, OP-5
```

**Hypothese :** Si les colonnes du Tacuinum correspondent a des
TYPES de contenu, et si les suffixes VMS encodent les types,
alors chaque position dans la fiche devrait avoir un SUFFIXE DOMINANT.

**Test :**
1. Segmenter en blocs (K du OP-5)
2. Pour chaque position, compter la distribution de suffixes
3. Chercher des positions avec un suffixe tres dominant :
   - Position X : 80% de -al → c'est la colonne GRADUS?
   - Position Y : 60% de -ey → c'est la colonne IUVAMENTUM?
   - Position Z : 70% de -or → c'est la colonne NOMINA?

Si les suffixes se CONCENTRENT par position → structure tabulaire.
Si les suffixes sont UNIFORMES par position → prose, pas table.

---

### PHASE 3 : MATCHING (exploite les resultats des phases 1-2)

#### OP-9 : ALIGNEMENT TABLE × PAGE
```
Duree : 2h | Script : op9_alignment.py | Prerequis : OP-4, OP-5, OP-6
```

Si les phases 1-2 confirment la structure tabulaire :

1. Pour chaque page zodiac VMS, calculer sa "signature" :
   - Proportion des 4 mots galeniques candidats (OP-4)
   - Mots dominants par position (OP-5)
   - Mots partages avec le herbal (OP-6)
2. Pour chaque table Tacuinum, calculer sa signature :
   - Proportion calidum:frigidum
   - Ingredients dominants
3. Matcher par distance de signature (matrice 40×32)
4. Pour chaque paire matchee, aligner les entrees 1-a-1
5. Chaque alignement propose des mappings mot EVA → substance

---

#### OP-10 : VALIDATION CROISEE
```
Duree : 1h | Script : op10_validation.py | Prerequis : OP-9
```

Chaque mapping propose par OP-9 doit etre VALIDE partout :
1. Le mot EVA decode comme "myrrha" dans l'astro doit aussi
   fonctionner comme "myrrha" dans le herbal et le pharma
2. Verifier la coherence avec le registre central (candidate_store)
3. Verifier la coherence avec les 16 logograms connus
4. Calculer un score de confiance final
5. Injecter les resultats dans le registre central

---

## Interactions avec le plan principal

```
TACUINUM_OPS                        BATTLE_PLAN
                                    
OP-2 (profil) ────────────────────> Compare avec profil herbal/pharma
                                    
OP-4 (galenic) ──────────────────> R06_qualities (valide les qualites CI)
                                    
OP-6 (crossref) ────────────────> Attack 02 (enrichit le frequency matching)
                                    
OP-9 (alignment) ───────────────> candidate_registry.json (mappings)
                                    
OP-10 (validation) ─────────────> candidate_registry.json (scores)
```

---

## Chronologie

```
JOUR 1 (datasets prets)
  |
  OP-1 (10 min) ──> combien d'entrees par page?
  OP-2 (20 min) ──> profil statistique astro VMS
  OP-3 (20 min) ──> profil statistique Tacuinum
  |
  DECISION : les profils sont-ils compatibles?
  |
  Si OUI :
  |
  OP-4 (30 min) ──> distribution galenique (chi-carre)
  OP-5 (1h)     ──> vocabulaire par position
  OP-6 (30 min) ──> ancres croisees herbal × astro
  OP-7 (30 min) ──> test de repetitivite
  |
  DECISION : combien de tests positifs?
  |
  Si 3+ positifs sur 4 :
  |
  OP-8 (1h) ──> suffixes par position
  OP-9 (2h) ──> alignement table × page
  OP-10 (1h) ──> validation croisee
  |
  RESULTAT FINAL
```

**Temps total si tout passe : 7-8 heures.**
**Temps si ca echoue en phase 1 : 1 heure (et on sait que c'est pas un Tacuinum).**

---

## Criteres de succes

| Niveau | Critere | Quand |
|--------|---------|-------|
| **CONTACT** | OP-1 confirme ~7 entrees par page zodiac | Phase 1 |
| **SIGNAL** | OP-4 trouve les 4 mots galeniques (p < 0.01) | Phase 2 |
| **PERCEE** | OP-5 trouve une position avec ~9 mots = NATURA | Phase 2 |
| **ANCRAGE** | OP-6 trouve 10+ mots partages herbal/astro | Phase 2 |
| **DECODAGE** | OP-9 aligne 5+ tables et decode 20+ mots | Phase 3 |
| **VICTOIRE** | OP-10 valide les mots sur TOUT le corpus | Phase 3 |

---

## Statistiquement, que peut-on attendre?

Si l'astro VMS est un Tacuinum :
- OP-4 DOIT marcher (4 mots sur 4437 tokens, c'est enorme)
- OP-5 DOIT trouver une position fermee (GRADUS = 63 mots, impossible a rater)
- OP-6 DOIT trouver des mots partages (les memes plantes sont dans le CI)
- OP-7 DOIT montrer une repetitivite elevee (TTR bas)

Si l'astro VMS N'EST PAS un Tacuinum :
- OP-4 echouera (pas de ratio galenique)
- OP-5 ne trouvera pas de position fermee
- On le saura en 1 heure, et on aura ELIMINE l'hypothese

**C'est une experience GAGNANT-GAGNANT.**
On decode ou on elimine. Les deux font avancer le projet.
