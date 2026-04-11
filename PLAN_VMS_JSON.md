# PLAN — Construction du VMS Structuré (vms_structured.json)

## Pourquoi

On decode du texte EVA brut depuis 7 sessions. Chaque script re-parse ZL.txt
a sa maniere, perd les variantes de lecture, ignore les marqueurs visuels,
et accumule les erreurs. C'est fini.

On construit UNE source de verite structuree. Tout le reste en depend.

## Architecture : TEXTE vs INTERPRETATION

```
STABLE (le texte, ne change jamais)        EVOLUE (interpretations, versionnees)
─────────────────────────────────          ───────────────────────────────────
vms_structured.json                        ka_decode_v12.json
  = le TEXTE du manuscrit                    = decodage K&A (reference word_id)
  = folio > block > line > word              = peut etre regenere/corrige
  = EVA + variantes + morphologie
  = marqueurs visuels (etoiles etc.)       candidates_v1.json
  = metadata (quire, hand, section)          = registre de candidats (word_id)
                                             = alimente par les attaques
NE CONTIENT JAMAIS :
  - de decodage K&A                        suffix_analysis_v1.json
  - de candidats de mapping                  = analyse session 7 (word_id)
  - d'hypotheses interpretatives
                                           block_analysis_v1.json
CONTIENT (faits de transcription) :          = metriques par bloc (doses/bloc etc.)
  - root + suffix (morphologie EVA)
  - is_logogram (16 confirmes)
  - i_count dans -ain/-aiin/-aiiin
  - n_glyphs (comptage objectif)
```

## La structure cible (vms_structured.json)

```json
{
  "_meta": {
    "source": "ZL.txt (Zandbergen-Landini v2b, 2022)",
    "alt_source": "LSI.txt (interlinear, variantes multiples)",
    "version": "1.0",
    "date": "2026-04-12",
    "total_folios": 225,
    "total_blocks": "~800",
    "total_lines": "~8500",
    "total_words": "~39000",
    "note": "TEXTE UNIQUEMENT — pas de decodage K&A ni de candidats"
  },

  "folios": {
    "f103r": {
      "folio_id": "f103r",
      "folio_num": 103,
      "rv": "r",
      "sub": "",

      "metadata": {
        "quire": "T",
        "bifolio": "20",
        "section": "pharma",
        "illustration_type": "T",
        "language": "B",
        "hand": "3",
        "currier_hand": "X",
        "n_lines": 54,
        "n_words": 532,
        "has_illustrations": false,
        "has_stars": true,
        "has_labels": false,
        "n_blocks": 18
      },

      "blocks": [
        {
          "block_id": "f103r_B01",
          "block_type": "recipe",
          "block_index": 0,
          "separator": {"type": "star", "color": "dark", "points": 7},
          "n_lines": 4,
          "n_words": 52,

          "lines": [
            {
              "line_id": "f103r.1",
              "line_num": 1,
              "paragraph": "P0",
              "is_block_start": true,
              "is_block_end": false,
              "raw_zl": "<%>pchedal.shdy.ytechypchy.otey...",

              "words": [
                {
                  "word_id": "f103r.1.1",
                  "position": 0,
                  "position_in_block": 0,
                  "eva_primary": "pchedal",
                  "eva_variants": [],
                  "uncertain_chars": [],
                  "special_glyphs": [],
                  "consensus": null,

                  "morphology": {
                    "root": "pch",
                    "suffix": "al",
                    "n_glyphs": 5,
                    "is_logogram": false,
                    "logogram_latin": null,
                    "i_count": 0,
                    "e_count": 1,
                    "is_dose_candidate": false
                  }
                },
                {
                  "word_id": "f103r.1.10",
                  "position": 9,
                  "position_in_block": 9,
                  "eva_primary": "dain",
                  "eva_variants": [],
                  "uncertain_chars": [],
                  "special_glyphs": [],

                  "morphology": {
                    "root": "d",
                    "suffix": "ain",
                    "n_glyphs": 3,
                    "is_logogram": false,
                    "logogram_latin": null,
                    "i_count": 1,
                    "e_count": 0,
                    "is_dose_candidate": true
                  }
                }
              ]
            }
          ]
        },
        {
          "block_id": "f103r_B02",
          "block_type": "recipe",
          "block_index": 1,
          "separator": {"type": "star", "color": "light", "points": 8}
        }
      ]
    }
  }
}
```

## Sources a parser

### Source 1 : ZL.txt (PRIMAIRE)
```
Format IVTFF. Contient :
- Folios et lignes (<f103r.1,@P0>)
- Marqueurs de bloc : <%> (star), <$> (fin de section)
- Variantes de lecture : [a:o] = 'a' ou 'o'
- Glyphes incertains : ? apres un caractere
- Glyphes speciaux : @NNN;, {xxx}
- Annotations : <!star>, <!plant>, <!nymph>, <!doodle: @NNN;>
- Metadata de folio : $Q=quire, $I=illustration, $L=language, $H=hand
```

### Source 2 : LSI.txt (SECONDAIRE, variantes)
```
Transcription interlineaire avec 5+ lecteurs (H, C, F, N, U).
Chaque ligne a jusqu'a 5 lectures differentes.
Utiliser pour enrichir eva_variants[] quand les lectures divergent.
```

### Source 3 : Metadata visuelles (ENRICHISSEMENT)
```
- docs/VMS_GUIDE_VISUEL.md : classification par folio
- data/botanical_identifications.tsv : plantes par folio
- Commentaires ZL.txt : couleur des etoiles, type d'illustration
```

## Plan d'execution

### ETAPE 1 : Parser ZL.txt complet (3-4h)
```
Script : build_vms_json.py
Temps realiste : 3-4h (edge cases nombreux)
```

**EDGE CASES a gerer :**
- Sous-folios : f85r1, f85r2, f89r1, f89r2 (pages divisees)
- Lignes de commentaires ZL (commencent par #)
- Metadata multi-champs ($Q=A $P=B $F=a $B=1 $I=H $L=A $H=1)
- Glyphes speciaux : @132; a @255; (86 codes differents)
- Accolades : {cphh}, {ikh}, {c'y}, {ct} (ligatures?)
- Corrections editoriales : <!corr?>, <!funny o>
- Variantes multiples : [cth:oto], [a:o:?]
- Points d'interrogation : ok??, d?n (incertain)
- Virgules dans les mots : ok[a:o]in,d?n (separateur vs ponctuation)
- Lignes vides et commentaires entre folios
- Folios manquants (f59-f64 n'existent pas dans le MS)
- Rosette (fRos) : folio special multi-panneaux

Pour chaque ligne de ZL.txt :
1. Distinguer commentaire (#), metadata (<f...> <!$...>), texte
2. Extraire folio (avec sous-folio), ligne, paragraphe, type (@P0, +P0, *P0, =P0)
3. Extraire metadata (premiere ligne de chaque folio : $Q, $I, $L, $H, $C, $X)
4. Detecter les marqueurs de bloc (<%> star, <$> fin, <-> line break)
5. Extraire les annotations (<!star>, <!plant>, <!nymph>, <!doodle:>, <!corr?>)
6. Parser les mots avec variantes ([a:o]) et incertitudes (?)
7. Detecter les glyphes speciaux (@NNN;, {xxx})

Pour chaque mot :
1. EVA primaire (lecture preferee — PREMIERE option dans [x:y])
2. EVA variantes (lectures alternatives — TOUTES les options dans [x:y])
3. Caracteres incertains (positions des ?)
4. Glyphes speciaux (@NNN;, {xxx})
5. Flag de confiance (nombre de ? dans le mot)

### ETAPE 2 : Enrichir avec l'analyse morphologique (1h)
```
Ajout au JSON existant
```

Pour chaque mot :
1. Root + suffix (session 7)
2. Nombre de glyphes EVA
3. Is_logogram (16 connus)
4. Logogram_latin (si applicable)
5. i_count (nombre de 'i' dans le suffixe -ain/-aiin/-aiiin)
6. Is_dose_candidate (basé sur suffixe + position)

### ETAPE 3 : Detecter les blocs (1h)
```
Types de blocs :
```

| Type | Detecte par | Sections |
|------|-------------|----------|
| recipe | Etoile <%> | Pharma (f103-f116) |
| paragraph | <%> sans etoile ou @P0 | Herbal, balnea |
| label | Lignes courtes (<= 3 mots) | Astro, herbal (pres des figures) |
| ring | Ring concentrique | Volvelle (f57v) |
| continuous | Pas de separateur | Certaines pages |

Pour le herbal : chaque folio = 1 plante = 1 bloc principal.
Pour le pharma : les etoiles separent les recettes (19 etoiles sur f103r = 18 recettes).
Pour l'astro : les labels sont pres des figures (nymphes). ~30 labels/page.
Pour la balnea : VERIFIER si les <%> existent (probable — meme format que pharma).
Pour la volvelle f57v : rings concentriques (L01-L05), chaque ring = 1 bloc.

### ETAPE 4 : Enrichir avec LSI.txt (1-2h)
```
Variantes de lecture independantes
```

**ATTENTION :** Le transcripteur "H" dans LSI est un COMPOSITE
(Takahashi/Stolfi), pas un lecteur independant. Le vrai consensus
doit etre calcule SANS H, puis verifie contre H.

Pour chaque mot du JSON :
1. Chercher la meme position dans LSI.txt (folio+ligne+position)
2. Extraire les lectures de chaque transcripteur (C, F, N, U, H)
3. Calculer le consensus SANS H (lecteurs independants seulement)
4. Ajouter le champ `consensus` au mot :
   - 4/4 independants d'accord = "certain"
   - 3/4 d'accord = "probable"
   - 2/4 ou moins = "incertain"
5. Si H diverge de la majorite independante, le noter
6. Les variantes LSI enrichissent le champ `eva_variants[]`

### ETAPE 5 : Generer K&A decode SEPARE (optionnel, 1h)
```
Fichier SEPARE : data/ka_decode_v12.json
NE VA PAS dans vms_structured.json !
```

Structure :
```json
{
  "_meta": {"pipeline": "v12", "date": "2026-04-12"},
  "decodes": {
    "f103r.1.1": {"latin": "uscieidas", "confidence": 0.12, "perseus": false},
    "f103r.1.10": {"latin": "duin", "confidence": 0.45, "perseus": true}
  }
}
```

Pour chaque mot de 4+ glyphes (PAS les logograms) :
1. Appliquer le pipeline K&A existant (v12/pipeline.py)
2. Stocker le decode + confiance + validite Perseus
3. Le fichier reference les word_id de vms_structured.json
4. Peut etre regenere/corrige sans toucher au JSON principal

### ETAPE 6 : Validation et stats (30min)

1. Verifier la coherence : nombre de folios, mots, lignes vs ZL.txt brut
2. Generer des stats globales
3. Verifier que les etoiles de f103r donnent bien 18 blocs
4. Verifier les variantes de lecture sur des cas connus

## Fichiers generes

```
data/
|-- vms_structured.json         <- LE TEXTE (source unique, stable)
|-- vms_structured_stats.json   <- Stats globales
|-- ka_decode_v12.json          <- Decodage K&A (SEPARE, versionne)
|-- build_vms_json.py           <- Script de construction
|-- validate_vms_json.py        <- Script de validation

attacks/results/
|-- candidates_v1.json          <- Registre de candidats (evolue)
|-- suffix_analysis_v1.json     <- Analyse suffixale (evolue)
|-- block_analysis_v1.json      <- Metriques par bloc (evolue)
```

### Principe : SEPARATION TEXTE / INTERPRETATION

Le vms_structured.json est le SOCLE IMMUTABLE.
Tout fichier d'interpretation (K&A, candidats, analyses)
est SEPARE et reference les word_id du JSON principal.

On peut :
- Changer K&A v12 → v13 sans toucher au JSON
- Ajouter des candidats sans toucher au JSON
- Corriger une analyse suffixale sans toucher au JSON

On ne peut PAS :
- Mettre un decodage K&A dans le JSON principal
- Mettre un candidat de mapping dans le JSON principal
- Mettre une hypothese interpretative dans le JSON principal

## Ce que ca debloque

1. **Crib Aurea** : aligner chacun des 18 blocs de f103r avec les recettes AN
   en utilisant la BONNE segmentation (pas le texte brut)

2. **Attack 02 (frequence)** : calculer les frequences par BLOC pas par folio
   (les recettes courtes ont des distributions differentes)

3. **Attack 03 (grammaire)** : les suffixes par position DANS LE BLOC
   (pas dans la ligne brute)

4. **GPU embeddings** : entrainer word2vec sur des SEQUENCES CORRECTES
   (bloc par bloc, pas ligne par ligne)

5. **Variantes de lecture** : tester les DEUX lectures quand ZL a [a:o]
   (certains mots suspects pourraient etre des erreurs de transcription)

6. **Reproductibilite** : chaque resultat pointe vers un word_id precis
   (f103r.1.10 = le 10eme mot de la ligne 1 de f103r)

## Temps total estime

| Etape | Temps | Complexite |
|-------|-------|------------|
| 1. Parser ZL.txt | 3-4h | HAUTE (edge cases) |
| 2. Morphologie | 1h | MOYENNE |
| 3. Blocs | 1h | MOYENNE |
| 4. LSI variantes | 1-2h | HAUTE (alignement) |
| 5. K&A separe | 1h | FAIBLE (pipeline existant) |
| 6. Validation | 30min | FAIBLE |
| **TOTAL** | **7-9h** | |

## Priorite ABSOLUE

Ce JSON est la FONDATION. Rien d'autre ne se construit tant qu'il n'est pas fait.
Toutes les attaques, tous les decodages, toutes les analyses lisent depuis ce fichier.
Plus jamais de re-parsing ad hoc de ZL.txt dans chaque script.

## Dependances

```
Etape 1 (parser ZL) ─────> Etape 2 (morphologie) ─────> Etape 3 (blocs)
                                                              |
                                                    Etape 4 (LSI, en parallele)
                                                              |
                                                    Etape 5 (K&A, en parallele)
                                                              |
                                                    Etape 6 (validation finale)
```

Etapes 4 et 5 sont INDEPENDANTES et peuvent tourner en parallele apres l'etape 3.
