"""
ITERATIONS 2+3+4 — Identify plants, test i-count, propagate into recipes.
"""
import json, sys, io, os
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

VMS_PATH = os.path.join(os.path.dirname(__file__), '..', 'vms', 'vms_structured.json')
MACER_PATH = os.path.join(os.path.dirname(__file__), 'macer_complete.json')
RESULTS = os.path.dirname(__file__)

with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)
with open(MACER_PATH, encoding='utf-8') as f:
    macer = json.load(f)

LOGOS = {'o':'ac','l':'se','d':'de','r':'recipe','v':'vel','x':'crux',
         'k':'cum','m':'misce','f':'per','t':'et','y':'in','c':'cum',
         's':'est','sh':'ci','p':'usque','ch':'cum'}

known_roots = {
    'cth':'acetum','yk':'mel','cht':'piper','shocthy':'mastix','shotch':'nigella',
    'pcheod':'ruta','foch':'viola','pos':'lactuca','tsho':'apium',
    'posho':'salvia','tedo':'crocus','tocph':'mentha','keered':'coriandrum',
    'pchod':'aristolochia','pched':'lens','kooiin':'nenuphar',
    'do':'gentiana','kodal':'saxifraga','fchol':'thymus','kcho':'arnica',
    'ko':'lonicera','koary':'ricinus','psh':'pisum','por':'paris',
    'chod':'symphytum','told':'dictamnus','och':'drosera',
    'keed':'erigeron','fch':'veronica','po':'inula','ksh':'rhododendron',
    'tsh':'sonchus','pcho':'scorzonera','cphy':'centaurea','fo':'acanthus',
    'pod':'valeriana','tshd':'silene','poly':'myrica','pshe':'astrantia',
}

sorted_roots = sorted(known_roots.keys(), key=len, reverse=True)

def find_root_in_word(eva):
    for root in sorted_roots:
        if len(root) < 2: continue
        idx = eva.find(root)
        if idx >= 0:
            prefix = eva[:idx]
            suffix = eva[idx+len(root):]
            if len(prefix) <= 4 and len(suffix) <= 5:
                return prefix, root, suffix
    return None, None, None

# ================================================================
# ITER 2: For each Macer anchor, check if Macer ingredients appear in VMS folio
# ================================================================
print('=' * 70)
print('ITERATION 2 — Macer ingredients in VMS anchor folios')
print('=' * 70)

anchors = [
    ('f48v','Ruta'),('f9v','Violae'),('f44v','Apium'),('f51v','Salvia'),
    ('f29r','Lactuca'),('f41r','Origanum'),('f37r','Mentha'),
    ('f41v','Coriandrum'),('f22r','Verbena'),('f28r','Aristolochia'),
]

macer_by_name = {ch['name'].lower(): ch for ch in macer['chapters']}

new_discoveries = {}

for fid, mname in anchors:
    ch = macer_by_name.get(mname.lower())
    if not ch: continue

    folio = vms['folios'].get(fid)
    if not folio: continue

    # Get all EVA words on this folio
    folio_words = []
    for block in folio['blocks']:
        for line in block['lines']:
            for w in line['words']:
                folio_words.append(w['eva_primary'])

    # For each Macer ingredient, search as substring in folio words
    macer_ingr = ch.get('ingredients', [])

    print(f'\n  {fid} = {mname} | Macer ingredients: {", ".join(i.replace("I_","") for i in macer_ingr)}')

    for ingr in macer_ingr:
        ingr_name = ingr.replace('I_','').replace('P_','').replace('Q_','')

        # Check if we already know this ingredient
        already_known = any(v == ingr_name for v in known_roots.values())

        if already_known:
            # Find which root encodes it
            root_for = [r for r, v in known_roots.items() if v == ingr_name]
            # Check if that root appears on this folio (as substring)
            found_on_folio = False
            for w in folio_words:
                for rf in root_for:
                    if rf in w:
                        found_on_folio = True
                        break
                if found_on_folio: break
            status = '✓ FOUND' if found_on_folio else '✗ missing'
            print(f'    {ingr_name:>15s}: known root={root_for[0]:>8s} → {status}')
        else:
            print(f'    {ingr_name:>15s}: UNKNOWN — need to identify')

# ================================================================
# ITER 3: Test i-count = grammatical case
# ================================================================
print(f'\n\n{"="*70}')
print('ITERATION 3 — i-count = grammatical case?')
print('=' * 70)

# For confirmed roots, check: does i-count correlate with position?
for root, latin in [('cth','acetum'),('yk','mel'),('cht','piper')]:
    i1_positions = []
    i2_positions = []

    for fid, folio in vms['folios'].items():
        if folio['metadata']['section'] != 'pharma': continue
        for block in folio['blocks']:
            words = [w for line in block['lines'] for w in line['words']]
            n = len(words)
            for i, w in enumerate(words):
                eva = w['eva_primary']
                morph = w.get('morphology') or {}
                wr = morph.get('root', '')
                ic = morph.get('i_count')
                suf = morph.get('suffix', '') or ''

                # Check if this word contains our root
                if root in eva:
                    rel_pos = i / max(n-1, 1)
                    if 'ain' in suf and ic == 1:
                        i1_positions.append(rel_pos)
                    elif 'aiin' in suf and ic == 2:
                        i2_positions.append(rel_pos)

    if i1_positions and i2_positions:
        avg1 = sum(i1_positions) / len(i1_positions)
        avg2 = sum(i2_positions) / len(i2_positions)
        print(f'\n  {root} ({latin}):')
        print(f'    -ain (i1): {len(i1_positions)}x, avg position = {avg1:.2f}')
        print(f'    -aiin (i2): {len(i2_positions)}x, avg position = {avg2:.2f}')
        print(f'    Difference: {abs(avg1-avg2):.2f}')
        if abs(avg1-avg2) > 0.1:
            print(f'    → i1 and i2 appear in DIFFERENT positions → grammatical!')
        else:
            print(f'    → No positional difference')

# Global test: all -ain vs -aiin
print(f'\n  GLOBAL: all words with -ain vs -aiin')
all_ain_pos = []
all_aiin_pos = []
for fid, folio in vms['folios'].items():
    if folio['metadata']['section'] != 'pharma': continue
    for block in folio['blocks']:
        words = [w for line in block['lines'] for w in line['words']]
        n = len(words)
        for i, w in enumerate(words):
            morph = w.get('morphology') or {}
            suf = morph.get('suffix', '') or ''
            ic = morph.get('i_count')
            if ic == 1: all_ain_pos.append(i / max(n-1, 1))
            elif ic == 2: all_aiin_pos.append(i / max(n-1, 1))

if all_ain_pos and all_aiin_pos:
    avg_ain = sum(all_ain_pos) / len(all_ain_pos)
    avg_aiin = sum(all_aiin_pos) / len(all_aiin_pos)
    print(f'    -ain (i1): {len(all_ain_pos)}x, avg position = {avg_ain:.3f}')
    print(f'    -aiin (i2): {len(all_aiin_pos)}x, avg position = {avg_aiin:.3f}')
    print(f'    Difference: {abs(avg_ain-avg_aiin):.3f}')

    # What comes BEFORE -ain vs -aiin?
    print(f'\n  What PRECEDES -ain vs -aiin?')
    before_ain = Counter()
    before_aiin = Counter()
    for fid, folio in vms['folios'].items():
        if folio['metadata']['section'] != 'pharma': continue
        for block in folio['blocks']:
            words = [w for line in block['lines'] for w in line['words']]
            for i, w in enumerate(words):
                ic = (w.get('morphology') or {}).get('i_count')
                if i > 0 and ic is not None:
                    prev = words[i-1]['eva_primary']
                    prev_type = 'LOGO' if prev in LOGOS else 'WORD'
                    if ic == 1: before_ain[prev_type] += 1
                    elif ic == 2: before_aiin[prev_type] += 1

    print(f'    Before -ain: {dict(before_ain)}')
    print(f'    Before -aiin: {dict(before_aiin)}')

# ================================================================
# ITER 4: Decode f48v with decomposition
# ================================================================
print(f'\n\n{"="*70}')
print('ITERATION 4 — f48v DECODED WITH DECOMPOSITION')
print('=' * 70)

f48v = vms['folios']['f48v']
ruta_ch = macer_by_name.get('ruta', {})
print(f'Macer Ruta ingredients: {", ".join(i.replace("I_","") for i in ruta_ch.get("ingredients",[]))}')

total = decoded = 0

for block in f48v['blocks']:
    for line in block['lines']:
        words = line['words']
        parts = []

        for i, w in enumerate(words):
            eva = w['eva_primary']
            morph = w.get('morphology') or {}
            ic = morph.get('i_count')
            total += 1

            # 1. Logogram
            if eva in LOGOS:
                parts.append(LOGOS[eva].upper())
                decoded += 1
                continue

            # 2. Dose
            if ic is not None:
                parts.append(f'({ic})')
                decoded += 1
                continue

            # 3. Decompose
            pfx, root, sfx = find_root_in_word(eva)
            if root:
                latin = known_roots[root]
                pfx_meaning = LOGOS.get(pfx, pfx) if pfx else ''
                pfx_str = f'{pfx_meaning}+' if pfx_meaning else ''
                sfx_str = f'.{sfx}' if sfx else ''
                parts.append(f'{pfx_str}{latin}{sfx_str}')
                decoded += 1
                continue

            # 4. Unknown
            parts.append(f'({eva})')

        print(f'\n  {line["line_id"]}:')
        print(f'    {" ".join(parts)}')

print(f'\n  BILAN: {decoded}/{total} = {decoded*100//total}% décodé')

# Save
with open(os.path.join(RESULTS, 'iter234_results.json'), 'w', encoding='utf-8') as f:
    json.dump({'decoded_pct': decoded*100//total, 'total': total, 'decoded': decoded}, f)

print('\nSaved iter234_results.json')
