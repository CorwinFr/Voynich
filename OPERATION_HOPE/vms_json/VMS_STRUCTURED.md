# vms_structured.json

Source unique de verite pour le texte du manuscrit de Voynich (MS 408).

**Date de build** : 2026-04-11
**Source** : LSI_ivtff_0d.txt (Stolfi/Takahashi interlinear, 1998)
**Parser** : build_vms_json.py
**Transcripteur primaire** : H (composite)


## Chiffres

| Metrique | Valeur |
|---|---|
| Folios | 226 |
| Lignes | 5 220 |
| Mots | 37 020 |
| Blocs | 818 |
| Recettes pharma | 372 |
| Mots avec variantes | 16 860 (45.5%) |
| Logrammes | 632 (1.7%) |

**Sections** :

| Section | Folios | Lignes | Mots | Blocs |
|---|---|---|---|---|
| herbal_a | 110 | 1 442 | 9 394 | 237 |
| herbal_b | 8 | 206 | 1 438 | 24 |
| astro | 26 | 732 | 3 031 | 50 |
| balnea | 20 | 917 | 6 866 | 99 |
| bio | 6 | 188 | 1 810 | 35 |
| pharma | 56 | 1 735 | 14 481 | 373 |


## Architecture

Le principe : **ce fichier contient LE TEXTE, rien d'autre**.

Le decodage K&A, les candidats, les scores sont dans des fichiers externes qui referencent les `word_id` de ce JSON. Cela permet de faire evoluer le decode sans jamais toucher au texte de base.

Fichiers externes prevus (pas encore construits) :

- `ka_decode_v12.json` : decode K&A par word_id
- `candidates_v1.json` : candidats de traduction par word_id
- `suffix_analysis_v1.json` : analyses statistiques des suffixes


## Schema JSON

```
{
  "_meta": {
    "source": "...",
    "version": "1.0",
    "date": "2026-04-11",
    "parser": "build_vms_json.py",
    "primary_transcriber": "H (composite)",
    "total_folios": 226,
    "total_lines": 5220,
    "total_words": 37020,
    "total_blocks": 818
  },
  "folios": {
    "<folio_id>": {                    // ex: "f1r", "f103r"
      "folio_id": "f1r",
      "folio_num": 1,
      "rv": "r",                       // recto / verso
      "sub": "",                       // "" ou "a"/"b" pour bifolios
      "metadata": {
        "section": "herbal_a",         // herbal_a, herbal_b, astro, balnea, bio, pharma
        "quire": "A",
        "illustration": "T",           // H=herbal, Z=zodiac, S=pharma, T=text, ...
        "language": "A",               // A ou B (Currier)
        "hand": "1",                   // main du scribe
        "n_lines": 31,
        "n_words": 213,
        "n_blocks": 5,
        "has_stars": true
      },
      "blocks": [
        {
          "block_id": "f1r_B01",
          "block_type": "paragraph",   // "recipe" (pharma) ou "paragraph" (autres)
          "block_num": 1,
          "n_lines": 6,
          "n_words": 46,
          "n_dose_candidates": 8,
          "n_unit_candidates": 1,
          "lines": [
            {
              "line_id": "f1r.1",
              "line_num": 1,
              "paragraph": "P0",
              "has_star": false,
              "n_words": 10,
              "words": [
                {
                  "word_id": "f1r.1.0",         // ID UNIQUE, reference pour fichiers externes
                  "position": 0,
                  "eva_primary": "fachys",        // lecture EVA transcripteur H
                  "uncertain": false,
                  "analysis": {
                    "n_glyphs": 6,
                    "is_logogram": false,
                    "logogram_latin": null,
                    "root": "fachys",
                    "suffix": "",
                    "suffix_type": null,          // null, AIN_SINGLE, AIN_DOUBLE, AIN_TRIPLE,
                                                  // EY_SINGLE, EEY_DOUBLE, EEY_TRIPLE,
                                                  // EDY_SINGLE, EDY_DOUBLE, AR, OR, AL,
                                                  // OL, EOL, DY, AM, CHY, SHY
                    "i_count": null,              // 1, 2, 3 pour -ain, -aiin, -aiiin
                    "e_count": null,              // 1, 2, 3 pour -ey, -eey, -eeey
                    "is_dose_candidate": false,   // true si suffixe -ain/-aiin/-aiiin
                    "has_gallows": true,
                    "has_bench_gallows": false
                  },
                  "eva_variants": [               // lectures des autres transcripteurs
                    {
                      "transcriber": "F",
                      "eva": "fyays"
                    }
                  ]
                }
              ]
            }
          ]
        }
      ]
    }
  }
}
```


## Classification des suffixes

18 types de suffixes identifies par le parser :

| Suffixe | Type | i_count | e_count | Frequence |
|---|---|---|---|---|
| -ain | AIN_SINGLE | 1 | - | 1 578 |
| -aiin | AIN_DOUBLE | 2 | - | 3 303 |
| -aiiin | AIN_TRIPLE | 3 | - | 65 |
| -ey | EY_SINGLE | - | 1 | 2 064 |
| -eey | EEY_DOUBLE | - | 2 | 1 682 |
| -eeey | EEY_TRIPLE | - | 3 | 184 |
| -edy | EDY_SINGLE | - | 1 | 2 897 |
| -eedy | EDY_DOUBLE | - | 2 | 1 205 |
| -ar | AR | - | - | 2 269 |
| -or | OR | - | - | 1 884 |
| -al | AL | - | - | 1 763 |
| -ol | OL | - | - | 2 171 |
| -eol | EOL | - | - | 842 |
| -dy | DY | - | - | 2 244 |
| -am | AM | - | - | 656 |
| -chy | CHY | - | - | 799 |
| -shy | SHY | - | - | 170 |

Ratio AIN_DOUBLE / AIN_SINGLE = 2.09 (inversion vs AN ou .i. domine).

Le ratio -aiin/-ain varie de 0.16 a 42.0 entre folios (260x), ce qui exclut une simple marque grammaticale uniforme.


## Validation f103r

Le folio f103r est le test cle : ses marqueurs etoiles (<$> dans IVTFF) doivent produire exactement 18 blocs.

Resultat : **18 blocs, 525 mots, 54 lignes**.

Tokens/recette : min=13, max=63, moyenne=29.2, mediane ~28.
Doses/recette : min=1, max=12, moyenne=3.6.

La moyenne de 3.6 doses/recette est coherente avec l'Antidotarium Nicolai (3.3 doses/recette).


## Comment utiliser ce fichier

**Charger en Python** :

```python
import json

with open('vms_structured.json') as f:
    vms = json.load(f)

# Acceder a un folio
f103r = vms['folios']['f103r']

# Iterer sur toutes les recettes pharma
for fid, folio in vms['folios'].items():
    if folio['metadata']['section'] != 'pharma':
        continue
    for block in folio['blocks']:
        # block['block_type'] == 'recipe'
        for line in block['lines']:
            for word in line['words']:
                print(word['word_id'], word['eva_primary'], word['analysis']['suffix_type'])
```

**Compter les mots par section** :

```python
from collections import Counter
section_words = Counter()
for fid, folio in vms['folios'].items():
    section = folio['metadata']['section']
    section_words[section] += folio['metadata']['n_words']
```

**Filtrer les candidats dose** :

```python
doses = [
    w for fid, folio in vms['folios'].items()
    for block in folio['blocks']
    for line in block['lines']
    for w in line['words']
    if w['analysis']['is_dose_candidate']
]
print(f"{len(doses)} dose candidates")
```


## Fichiers dans ce repertoire

| Fichier | Description |
|---|---|
| `vms_structured.json` | Le JSON (29.7 MB) |
| `build_vms_json.py` | Script de construction, reproductible |
| `VMS_STRUCTURED.md` | Ce fichier |
