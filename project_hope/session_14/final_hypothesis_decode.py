"""
FINAL HYPOTHESIS DECODE — Assemble ALL layers, tolerate errors.

Layer 1: Logograms (18, confirmed)
Layer 2: Doses (i-count)
Layer 3: Confirmed words (5 fingerprint matches)
Layer 4: Plant names (86 from first words)
Layer 5: Macer profile matches (60 folios → chapters)
Layer 6: Suffix meanings (structural)
Layer 7: k/t = cold/hot

Decode f48v (Ruta) as complete Latin text.
Then f103r recipe 1.
"""
import json, sys, io, os
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

VMS_PATH = os.path.join(os.path.dirname(__file__), '..', 'vms', 'vms_structured.json')
MACER_PATH = os.path.join(os.path.dirname(__file__), 'macer_complete.json')
ANCHORS_PATH = os.path.join(os.path.dirname(__file__), 'extended_anchors.json')
RESULTS = os.path.dirname(__file__)

with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)
with open(MACER_PATH, encoding='utf-8') as f:
    macer = json.load(f)
with open(ANCHORS_PATH, encoding='utf-8') as f:
    anchors = json.load(f)

# ================================================================
# ALL KNOWN MAPPINGS
# ================================================================

LOGOS = {
    'o':'ac','l':'se','d':'de','r':'recipe','v':'vel','x':'crux',
    'k':'cum','m':'misce','f':'per','t':'et','y':'in','c':'cum',
    's':'est','sh':'ci','p':'usque','ch':'cum','air':'air',
}

CONFIRMED = {
    'cth': 'acetum', 'yk': 'mel', 'cht': 'piper',
    'shocthy': 'mastix', 'shotch': 'nigella',
}

PLANT_NAMES = anchors.get('plant_name_mappings', {})

SUFFIX_MEANING = {
    'aiin': '(dose)', 'ain': '(dose)', 'aiiin': '(dose)',
    'eey': '(unitatem)', 'eeey': '(unitatem)',
    'edy': '(genitif?)', 'eedy': '(genitif?)',
    'eol': '(ablatif?)',
    'ol': '(nominatif?)', 'ar': '(accusatif?)',
    'al': '(datif?)', 'or': '(vocatif?)',
    'am': '.FIN', 'om': '.FIN',
    'dy': '(instruct.)', 'ey': '(adjectif?)',
    'air': '(qualitas)', 'chy': '(praep.)', 'shy': '(praep.)',
}

# Ruta Macer chapter ingredients (for context)
ruta_macer = next(ch for ch in macer['chapters'] if ch['name'] == 'Ruta')
ruta_ingr = ruta_macer['ingredients']

# ================================================================
# DECODE FUNCTION
# ================================================================

def decode_word(eva, morph, position, folio_context=None):
    """Decode a single EVA word using all layers."""
    root = morph.get('root', '')
    suffix = morph.get('suffix', '') or ''
    ic = morph.get('i_count')

    # Layer 1: Logogram
    if eva in LOGOS:
        return LOGOS[eva].upper(), 'LOGO', 3

    # Layer 2: Dose
    if ic is not None:
        roman = {1:'I', 2:'II', 3:'III', 4:'IV'}.get(ic, str(ic))
        return f'({roman})', 'DOSE', 3

    # Layer 3: Confirmed words
    if root in CONFIRMED:
        suf = SUFFIX_MEANING.get(suffix, f'.{suffix}' if suffix else '')
        return f'{CONFIRMED[root]}{suf}', 'CONFIRMED', 3

    # Layer 4: Plant name (first word mapping)
    if root in PLANT_NAMES:
        pn = PLANT_NAMES[root]
        suf = SUFFIX_MEANING.get(suffix, f'.{suffix}' if suffix else '')
        return f'{pn["latin"]}{suf}', 'PLANT', 2

    # Layer 5: Gallows initial = verb + plant title
    if position == 0 and eva[0] in 'ptkf' and eva not in LOGOS:
        if folio_context and 'plant' in folio_context:
            return f'Recipe {folio_context["plant"]}', 'VERB', 2
        return f'Recipe(...)', 'VERB', 1

    # Layer 6: Suffix gives function
    if suffix in SUFFIX_MEANING:
        suf_str = SUFFIX_MEANING[suffix]
        return f'[{root}]{suf_str}', 'PARTIAL', 1

    # Layer 7: Unknown
    return f'({eva})', 'UNK', 0

# ================================================================
# DECODE f48v (RUTA)
# ================================================================
print('=' * 70)
print('f48v — RUTA (Rue) — HYPOTHÈSE DE TRADUCTION')
print('=' * 70)
print(f'Macer dit: Ruta est calida.')
print(f'Ingrédients Macer: {", ".join(i.replace("I_","") for i in ruta_ingr)}')
print(f'k/t ratio f48v = 0.41 → t-dominant → plante CHAUDE ✓')
print('=' * 70)

f48v = vms['folios']['f48v']
context = {'plant': 'ruta'}

total = decoded_full = decoded_partial = unknown = 0
latin_lines = []

for block in f48v['blocks']:
    for line in block['lines']:
        words = line['words']
        line_latin = []

        for i, w in enumerate(words):
            eva = w['eva_primary']
            morph = w.get('morphology') or {}
            total += 1

            text, method, confidence = decode_word(eva, morph, i, context)

            if confidence >= 2:
                decoded_full += 1
            elif confidence == 1:
                decoded_partial += 1
            else:
                unknown += 1

            line_latin.append(text)

        latin_line = ' '.join(line_latin)
        latin_lines.append(latin_line)
        print(f'\n  {line["line_id"]}:')
        print(f'    EVA:   {" ".join(w["eva_primary"] for w in words)}')
        print(f'    LATIN: {latin_line}')

print(f'\n{"="*70}')
print(f'BILAN f48v:')
print(f'  Total: {total} mots')
print(f'  Décodés (conf≥2): {decoded_full} ({decoded_full*100//total}%)')
print(f'  Partiels (conf=1): {decoded_partial} ({decoded_partial*100//total}%)')
print(f'  Inconnus (conf=0): {unknown} ({unknown*100//total}%)')
print(f'  TOTAL lisible: {(decoded_full+decoded_partial)*100//total}%')

# ================================================================
# DECODE f103r B01 (première recette pharma)
# ================================================================
print(f'\n\n{"="*70}')
print('f103r B01 — PREMIÈRE RECETTE PHARMA')
print('=' * 70)

f103r = vms['folios']['f103r']
block1 = f103r['blocks'][0]

total2 = df2 = dp2 = uk2 = 0
recipe_latin = []

for line in block1['lines']:
    words = line['words']
    line_latin = []

    for i, w in enumerate(words):
        eva = w['eva_primary']
        morph = w.get('morphology') or {}
        total2 += 1

        text, method, confidence = decode_word(eva, morph, i)

        if confidence >= 2: df2 += 1
        elif confidence == 1: dp2 += 1
        else: uk2 += 1

        line_latin.append(text)

    latin_line = ' '.join(line_latin)
    recipe_latin.append(latin_line)
    print(f'\n  {line["line_id"]}:')
    print(f'    EVA:   {" ".join(w["eva_primary"] for w in words)}')
    print(f'    LATIN: {latin_line}')

print(f'\n{"="*70}')
print(f'BILAN f103r B01:')
print(f'  Total: {total2} mots')
print(f'  Décodés: {df2} ({df2*100//total2}%)')
print(f'  Partiels: {dp2} ({dp2*100//total2}%)')
print(f'  Inconnus: {uk2} ({uk2*100//total2}%)')

# ================================================================
# SAVE FULL DECODE
# ================================================================
output = {
    'f48v': {
        'plant': 'Ruta',
        'macer_ingredients': ruta_ingr,
        'kt_ratio': 0.41,
        'galenic': 'calida (hot)',
        'latin_lines': latin_lines,
        'stats': {'total': total, 'decoded': decoded_full,
                  'partial': decoded_partial, 'unknown': unknown},
    },
    'f103r_B01': {
        'latin_lines': recipe_latin,
        'stats': {'total': total2, 'decoded': df2, 'partial': dp2, 'unknown': uk2},
    },
    'method': {
        'logograms': len(LOGOS),
        'confirmed_words': len(CONFIRMED),
        'plant_names': len(PLANT_NAMES),
        'suffix_meanings': len(SUFFIX_MEANING),
    },
}

with open(os.path.join(RESULTS, 'final_decode.json'), 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

# Human-readable output
with open(os.path.join(RESULTS, 'DECODE_HYPOTHESIS.md'), 'w', encoding='utf-8') as f:
    f.write('# HYPOTHÈSE DE TRADUCTION DU VOYNICH\n\n')
    f.write('## Méthode\n')
    f.write(f'- {len(LOGOS)} logograms confirmés\n')
    f.write(f'- {len(CONFIRMED)} mots confirmés par fingerprint\n')
    f.write(f'- {len(PLANT_NAMES)} noms de plantes par premier mot\n')
    f.write(f'- {len(SUFFIX_MEANING)} suffixes avec fonction grammaticale\n')
    f.write(f'- k/t = froid/chaud (galénique)\n\n')

    f.write('## f48v — Ruta (Rue)\n')
    f.write(f'Macer: {", ".join(i.replace("I_","") for i in ruta_ingr)}\n\n')
    for line in latin_lines:
        f.write(f'{line}\n')
    f.write(f'\nDécodé: {decoded_full*100//total}% + {decoded_partial*100//total}% partiel\n\n')

    f.write('## f103r B01 — Première recette pharma\n\n')
    for line in recipe_latin:
        f.write(f'{line}\n')
    f.write(f'\nDécodé: {df2*100//total2}% + {dp2*100//total2}% partiel\n')

print(f'\nSaved final_decode.json + DECODE_HYPOTHESIS.md')
