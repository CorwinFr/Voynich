"""
SESSION 17 — DEATH MATCH: Exhaustive positional alignment Macer×VMS

For f48v (Ruta) — our best folio with 6 confirmed ingredient anchors:
1. Parse EVERY mention of ANY substance in the Macer Ruta chapter
2. Map their positions in the text (normalized 0-1)
3. Map confirmed ingredients to their VMS positions
4. Use these as alignment calibration
5. For each unknown VMS root, find the closest Macer substance at that position

This goes beyond ingredients to include: body parts, preparation verbs,
dose markers, diseases, adjectives — EVERYTHING in the Macer text.
"""
import json, sys, io, os, re
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.dirname(__file__)
VMS_PATH = os.path.join(BASE, '..', 'vms', 'vms_structured.json')
MACER_PATH = os.path.join(BASE, '..', 'session_14', 'macer_complete.json')
MACER_TXT = os.path.join(BASE, '..', '..', 'data', 'De_viribus_herbarum.txt')
REG_PATH = os.path.join(BASE, '..', 'hypothesis_registry.json')
RESULTS = BASE

with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)
with open(MACER_PATH, encoding='utf-8') as f:
    macer_json = json.load(f)
with open(REG_PATH, encoding='utf-8') as f:
    registry = json.load(f)

LOGOS = {'o': 'ac', 'l': 'se', 'd': 'de', 'r': 'recipe', 'v': 'vel',
         'x': 'crux', 'k': 'cum', 'm': 'misce', 'f': 'per', 't': 'et',
         'y': 'in', 'c': 'cum', 's': 'est', 'sh': 'ci', 'p': 'usque', 'ch': 'cum'}
LOGO_SET = set(LOGOS.keys())
FUNCTIONAL = set(registry.get('functional_words', {}).keys())

# Confirmed root→latin for calibration
CONFIRMED = {}
for root, data in registry['confirmed_ingredients'].items():
    CONFIRMED[root] = data['latin']
# Add high-confidence
CONFIRMED['ypch'] = 'aqua'
CONFIRMED['ykeed'] = 'nitrum'
CONFIRMED['seees'] = 'lens'
CONFIRMED['kald'] = 'ovum'

# ================================================================
# STEP 1: Parse Macer Ruta chapter — extract ALL Latin words with positions
# ================================================================
print('='*70)
print('DEATH MATCH — f48v (Ruta) × Macer "Ruta"')
print('='*70)

# Find Ruta chapter
ruta_ch = None
for ch in macer_json['chapters']:
    if ch['name'].lower() == 'ruta':
        ruta_ch = ch
        break

ruta_text = ruta_ch['text']
print(f'\n  Macer Ruta chapter: {len(ruta_text)} chars, {len(ruta_text.split())} words')

# Parse every SIGNIFICANT Latin word with position
# Focus on: nouns (substances, body parts, diseases), verbs (preparation)
LATIN_SUBSTANCES = {
    # Ingredients
    'acetum': 'INGR', 'aceto': 'INGR', 'aceti': 'INGR',
    'aqua': 'INGR', 'aquae': 'INGR', 'aquam': 'INGR', 'amne': 'INGR',
    'mel': 'INGR', 'melle': 'INGR', 'melli': 'INGR', 'mulsa': 'INGR',
    'piper': 'INGR', 'pipere': 'INGR', 'piperque': 'INGR',
    'oleum': 'INGR', 'oleo': 'INGR',
    'sal': 'INGR', 'sale': 'INGR', 'salque': 'INGR',
    'vinum': 'INGR', 'vino': 'INGR', 'vini': 'INGR', 'mero': 'INGR',
    'succus': 'INGR', 'succo': 'INGR', 'succi': 'INGR', 'succum': 'INGR',
    'nitrum': 'INGR', 'nitro': 'INGR',
    'ruta': 'PLANT', 'rutae': 'PLANT', 'rutam': 'PLANT',
    'lens': 'INGR', 'lente': 'INGR', 'lentis': 'INGR',
    # Body parts
    'oculus': 'BODY', 'oculis': 'BODY', 'oculos': 'BODY', 'oculorum': 'BODY',
    'caput': 'BODY', 'capitis': 'BODY',
    'stomachus': 'BODY', 'stomachum': 'BODY', 'stomachi': 'BODY',
    'venter': 'BODY', 'ventrem': 'BODY', 'ventris': 'BODY',
    'auris': 'BODY', 'aures': 'BODY', 'aurium': 'BODY',
    'dens': 'BODY', 'dentes': 'BODY', 'dentium': 'BODY',
    'vulnus': 'BODY', 'vulnera': 'BODY', 'vulnerum': 'BODY',
    'matrix': 'BODY', 'matricis': 'BODY',
    'splenis': 'BODY', 'splen': 'BODY',
    'lumbos': 'BODY', 'lumbis': 'BODY',
    'urina': 'BODY', 'urinam': 'BODY',
    'menstrua': 'BODY',
    # Preparation verbs
    'coquas': 'VERB', 'coquatur': 'VERB', 'cocta': 'VERB', 'coctum': 'VERB',
    'bibatur': 'VERB', 'bibitum': 'VERB', 'bibendo': 'VERB',
    'trita': 'VERB', 'tritam': 'VERB', 'terendo': 'VERB', 'teras': 'VERB',
    'superaddita': 'VERB', 'superaddatur': 'VERB',
    'juncta': 'VERB', 'jungas': 'VERB', 'jungatur': 'VERB',
    'mixto': 'VERB', 'miscetur': 'VERB',
    'sumpta': 'VERB', 'sumpserit': 'VERB', 'sumitur': 'VERB',
    'decoctio': 'VERB', 'decoctave': 'VERB', 'decocta': 'VERB',
    'apponere': 'VERB', 'appositum': 'VERB',
    'peruncta': 'VERB', 'perungas': 'VERB',
    # Diseases/conditions
    'febris': 'DISEASE', 'febrem': 'DISEASE',
    'dolor': 'DISEASE', 'dolorem': 'DISEASE', 'dolori': 'DISEASE',
    'tumor': 'DISEASE', 'tumorem': 'DISEASE', 'tumores': 'DISEASE',
    'morsus': 'DISEASE', 'morsum': 'DISEASE',
    'venenum': 'DISEASE', 'venena': 'DISEASE', 'venenatis': 'DISEASE',
    'serpens': 'DISEASE', 'serpentes': 'DISEASE',
    'tussim': 'DISEASE', 'tussis': 'DISEASE',
    'ictericis': 'DISEASE', 'ictericorum': 'DISEASE',
    # Quantities/modes
    'potus': 'MODE', 'potu': 'MODE', 'potum': 'MODE',
    'cataplasma': 'MODE',
    'pulvis': 'MODE', 'pulvino': 'MODE',
    'unguen': 'MODE', 'unguine': 'MODE',
}

# Find all matches in Ruta text
ruta_lower = ruta_text.lower()
text_len = len(ruta_lower)

macer_positions = []
for word, wtype in LATIN_SUBSTANCES.items():
    for m in re.finditer(r'\b' + re.escape(word) + r'\b', ruta_lower):
        pos = m.start() / text_len
        macer_positions.append({
            'word': word,
            'type': wtype,
            'position': pos,
            'char_pos': m.start(),
        })

macer_positions.sort(key=lambda x: x['position'])

print(f'\n  Significant words found in Ruta text: {len(macer_positions)}')
print(f'\n  Positional map:')
for mp in macer_positions:
    print(f'    pos={mp["position"]:.3f}  [{mp["type"]:>7s}]  {mp["word"]}')


# ================================================================
# STEP 2: Map VMS f48v roots with positions
# ================================================================
print(f'\n{"="*70}')
print('VMS f48v — Root positions')
print('='*70)

f48v = vms['folios']['f48v']
vms_words = []
word_idx = 0

for block in f48v['blocks']:
    for line in block['lines']:
        for w in line['words']:
            eva = w['eva_primary']
            root = (w.get('morphology') or {}).get('root', '')
            vms_words.append({
                'eva': eva,
                'root': root,
                'idx': word_idx,
            })
            word_idx += 1

total_words = len(vms_words)

# Identify confirmed anchor positions
anchors = []
for i, vw in enumerate(vms_words):
    eva = vw['eva']
    if eva in LOGO_SET:
        continue
    for root, latin in CONFIRMED.items():
        if len(root) >= 3 and root in eva:
            anchors.append({
                'root': root,
                'latin': latin,
                'vms_pos': i / total_words,
                'idx': i,
                'eva': eva,
            })
            break

print(f'\n  Total words: {total_words}')
print(f'  Calibration anchors: {len(anchors)}')
for a in anchors:
    # Find corresponding Macer position
    macer_pos = None
    for mp in macer_positions:
        if a['latin'] in mp['word'] or mp['word'] in a['latin']:
            if macer_pos is None or abs(mp['position'] - a['vms_pos']) < abs(macer_pos - a['vms_pos']):
                macer_pos = mp['position']
    mp_str = f'{macer_pos:.3f}' if macer_pos is not None else '?'
    off_str = f'{a["vms_pos"]-macer_pos:.3f}' if macer_pos is not None else '?'
    print(f'    {a["root"]:>8s} = {a["latin"]:>8s}  VMS={a["vms_pos"]:.3f}  '
          f'Macer={mp_str}  offset={off_str}')


# ================================================================
# STEP 3: Compute alignment offset from anchors
# ================================================================
print(f'\n{"="*70}')
print('ALIGNMENT')
print('='*70)

# For each anchor, find the CLOSEST Macer position
offsets = []
for a in anchors:
    best_offset = None
    best_dist = 999
    for mp in macer_positions:
        if a['latin'] in mp['word'] or mp['word'] in a['latin']:
            dist = abs(a['vms_pos'] - mp['position'])
            if dist < best_dist:
                best_dist = dist
                best_offset = a['vms_pos'] - mp['position']
    if best_offset is not None:
        offsets.append(best_offset)

if offsets:
    mean_offset = sum(offsets) / len(offsets)
    print(f'  Mean offset (VMS - Macer): {mean_offset:.3f}')
    print(f'  Offsets: {[f"{o:.3f}" for o in offsets]}')
else:
    mean_offset = 0
    print(f'  No offsets computed')


# ================================================================
# STEP 4: For each UNKNOWN VMS root, find closest Macer word
# ================================================================
print(f'\n{"="*70}')
print('POSITIONAL MATCHING — Unknown roots → Macer words')
print('='*70)

matches = []

for i, vw in enumerate(vms_words):
    eva = vw['eva']
    root = vw['root']

    if eva in LOGO_SET:
        continue
    if root in FUNCTIONAL or root in {'ke', 'ko', 'po', 'do'}:
        continue
    if any(root == cr for cr in CONFIRMED):
        continue
    if len(root) < 3:
        continue

    vms_pos = i / total_words
    adjusted_pos = vms_pos - mean_offset  # align to Macer space

    # Find closest Macer word
    best = None
    best_dist = 999
    for mp in macer_positions:
        dist = abs(adjusted_pos - mp['position'])
        if dist < best_dist:
            best_dist = dist
            best = mp

    if best and best_dist < 0.15:  # within 15% of text
        matches.append({
            'vms_root': root,
            'vms_eva': eva,
            'vms_pos': vms_pos,
            'macer_word': best['word'],
            'macer_type': best['type'],
            'macer_pos': best['position'],
            'distance': best_dist,
        })

matches.sort(key=lambda x: x['vms_pos'])

print(f'\n  Matches (within 15% distance):')
print(f'  {"Root":>10s} {"Eva":>15s} {"VPos":>5s} → {"MacerWord":>12s} {"Type":>8s} {"MPo":>5s} {"Dist":>5s}')
print('  ' + '-' * 75)

for m in matches:
    print(f'  {m["vms_root"]:>10s} {m["vms_eva"]:>15s} {m["vms_pos"]:.2f} → '
          f'{m["macer_word"]:>12s} {m["macer_type"]:>8s} {m["macer_pos"]:.2f} {m["distance"]:.3f}')


# ================================================================
# STEP 5: Full reading attempt
# ================================================================
print(f'\n\n{"="*70}')
print('FULL READING ATTEMPT — f48v')
print('='*70)

match_lookup = {}
for m in matches:
    if m['vms_root'] not in match_lookup or m['distance'] < match_lookup[m['vms_root']]['distance']:
        match_lookup[m['vms_root']] = m

for block in f48v['blocks']:
    for line in block['lines']:
        parts = []
        for w in line['words']:
            eva = w['eva_primary']
            root = (w.get('morphology') or {}).get('root', '')

            if eva in LOGO_SET:
                parts.append(f'[{LOGOS[eva]}]')
            elif root in CONFIRMED:
                parts.append(f'**{CONFIRMED[root]}**')
            elif root in match_lookup:
                m = match_lookup[root]
                parts.append(f'{m["macer_word"]}({m["macer_type"][:1]})')
            elif root in FUNCTIONAL:
                parts.append(f'~{root}~')
            else:
                parts.append(f'({eva})')

        print(f'  {line["line_id"]}: {" ".join(parts)}')


# Save
output = {
    'macer_positions': len(macer_positions),
    'vms_words': total_words,
    'anchors': len(anchors),
    'mean_offset': mean_offset,
    'matches': matches,
    'n_matches': len(matches),
}

with open(os.path.join(RESULTS, 'attack_death_results.json'), 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f'\nSaved attack_death_results.json')
