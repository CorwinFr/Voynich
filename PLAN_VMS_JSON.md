# PLAN — Construction du VMS Structuré (vms_structured.json)

## Pourquoi

On decode du texte EVA brut depuis 7 sessions. Chaque script re-parse ZL.txt
a sa maniere, perd les variantes de lecture, ignore les marqueurs visuels,
et accumule les erreurs. C'est fini.

On construit UNE source de verite structuree. Tout le reste en depend.

## La structure cible

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
    "total_words": "~39000"
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
        "has_labels": false
      },

      "blocks": [
        {
          "block_id": "f103r_B01",
          "block_type": "recipe",
          "separator": {"type": "star", "color": "dark", "points": 7},
          "lines": [
            {
              "line_id": "f103r.1",
              "line_num": 1,
              "paragraph": "P0",
              "is_first": true,
              "raw_zl": "<%>pchedal.shdy.ytechypchy.otey...",

              "words": [
                {
                  "word_id": "f103r.1.1",
                  "position": 0,
                  "eva_primary": "pchedal",
                  "eva_variants": [],
                  "uncertain": false,

                  "analysis": {
                    "root": "pch",
                    "suffix": "al",
                    "suffix_type": "MEASURE/LOCATION",
                    "n_glyphs": 5,
                    "is_logogram": false,
                    "logogram_latin": null
                  },

                  "ka_decode": {
                    "monolithic": "uscieidas",
                    "confidence": 0.12,
                    "perseus_valid": false
                  },

                  "candidates": []
                },
                {
                  "word_id": "f103r.1.2",
                  "position": 1,
                  "eva_primary": "shdy",
                  "eva_variants": [],

                  "analysis": {
                    "root": "sh",
                    "suffix": "dy",
                    "suffix_type": "INSTRUCTION_MARKER",
                    "n_glyphs": 3,
                    "is_logogram": false
                  }
                },
                {
                  "word_id": "f103r.1.10",
                  "position": 9,
                  "eva_primary": "dain",
                  "eva_variants": [],

                  "analysis": {
                    "root": "d",
                    "suffix": "ain",
                    "suffix_type": "SHORT_CONNECTOR",
                    "n_glyphs": 3,
                    "is_logogram": false,
                    "is_dose_candidate": true,
                    "i_count": 1
                  }
                }
              ]
            }
          ]
        },
        {
          "block_id": "f103r_B02",
          "block_type": "recipe",
          "separator": {"type": "star", "color": "light", "points": 8},
          "lines": ["..."]
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

### ETAPE 1 : Parser ZL.txt complet (2h)
```
Script : build_vms_json.py
```

Pour chaque ligne de ZL.txt :
1. Extraire folio, ligne, paragraphe
2. Extraire metadata (premiere ligne de chaque folio : $Q, $I, $L, $H)
3. Detecter les marqueurs de bloc (<%>, <$>)
4. Extraire les annotations (<!star>, <!plant>, etc.)
5. Parser les mots avec variantes ([a:o]) et incertitudes (?)
6. Detecter les glyphes speciaux (@NNN;, {xxx})

Pour chaque mot :
1. EVA primaire (lecture principale)
2. EVA variantes (lectures alternatives entre [])
3. Flag d'incertitude
4. Glyphes speciaux

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
Pour le pharma : les etoiles separent les recettes.
Pour l'astro : les labels sont pres des figures (nymphes).
Pour la balnea : structure a determiner.

### ETAPE 4 : Enrichir avec LSI.txt (1h)
```
Variantes de lecture
```

Pour chaque mot du JSON :
1. Chercher la meme position dans LSI.txt
2. Si les lecteurs (H, C, F, N, U) divergent, ajouter les variantes
3. Marquer le degre de consensus (5/5 = certain, 3/5 = incertain)

### ETAPE 5 : Ajouter K&A decode (optionnel, 1h)
```
Seulement si K&A est pertinent (mots longs)
```

Pour chaque mot de 4+ glyphes :
1. Appliquer le pipeline K&A existant (v12/pipeline.py)
2. Stocker le decode + confiance + validite Perseus
3. NE PAS utiliser pour les logograms (K&A est faux pour eux)

### ETAPE 6 : Validation et stats (30min)

1. Verifier la coherence : nombre de folios, mots, lignes vs ZL.txt brut
2. Generer des stats globales
3. Verifier que les etoiles de f103r donnent bien 18 blocs
4. Verifier les variantes de lecture sur des cas connus

## Fichiers generes

```
data/
|-- vms_structured.json         <- LE fichier (source unique de verite)
|-- vms_structured_stats.json   <- Stats globales
|-- build_vms_json.py           <- Script de construction
|-- validate_vms_json.py        <- Script de validation
```

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

## Priorite ABSOLUE

Ce JSON est la FONDATION. Rien d'autre ne se construit tant qu'il n'est pas fait.
Toutes les attaques, tous les decodages, toutes les analyses lisent depuis ce fichier.
Plus jamais de re-parsing ad hoc de ZL.txt dans chaque script.
