"""
SESSION 17 — MEGA MATCH: 143 herbal folios × 77 Macer chapters

For each of the 11,011 folio×chapter combinations:
1. Extract significant Latin words from Macer chapter with positions
2. Extract known ingredient roots from VMS folio with positions
3. Compute alignment score:
   - How many confirmed ingredients are shared?
   - How good is the positional alignment of shared ingredients?
   - Penalize mismatches (ingredient in chapter but not in folio)
4. Rank: best chapter for each folio = plant identification

Validate against 30 Sherwood identifications.
"""
import json, sys, io, os, re
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.dirname(__file__)
VMS_PATH = os.path.join(BASE, '..', 'vms', 'vms_structured.json')
MACER_PATH = os.path.join(BASE, '..', 'session_14', 'macer_complete.json')
REG_PATH = os.path.join(BASE, '..', 'hypothesis_registry.json')
RESULTS = BASE

with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)
with open(MACER_PATH, encoding='utf-8') as f:
    macer = json.load(f)
with open(REG_PATH, encoding='utf-8') as f:
    registry = json.load(f)

LOGOS = {'o','l','d','r','v','x','k','m','f','t','y','c','s','sh','p','ch','air','h'}

# Confirmed ingredients for matching (only HIGH confidence, real short roots)
CONFIRMED = {}
REAL_SHORT = {'chk', 'cht', 'yk', 'dsh'}
for root, data in registry['confirmed_ingredients'].items():
    if len(root) >= 4 or root in REAL_SHORT:
        CONFIRMED[root] = data['latin']
CONFIRMED['ypch'] = 'aqua'
CONFIRMED['ykeed'] = 'nitrum'
CONFIRMED['seees'] = 'lens'
CONFIRMED['kald'] = 'ovum'
CONFIRMED['otoly'] = 'sal'

sorted_confirmed = sorted(CONFIRMED.keys(), key=len, reverse=True)
print(f'Confirmed anchors: {len(CONFIRMED)}')

# Ingredient patterns for Macer text search
INGR_PATTERNS = {
    'acetum': r'\bacet[uoia]\w*\b',
    'aqua':   r'\baqua[em]?\b|\bamne\b',
    'mel':    r'\bmel\b|\bmell[ei]\w*\b|\bmulsa\b',
    'piper':  r'\bpiper\w*\b',
    'oleum':  r'\boleu[mi]\b|\boleo\b',
    'sal':    r'\bsal[ei]?\b|\bsale\b|\bsalque\b',
    'vinum':  r'\bvin[uoia]\w*\b|\bmero\b|\bmust[uo]\b',
    'succus': r'\bsucc[uoia]\w*\b',
    'lac':    r'\blac\b|\blact[ei]\w*\b',
    'ovum':   r'\bov[uoia]\w*\b',
    'nitrum': r'\bnitr[uoia]\w*\b',
    'myrrha': r'\bmyrrh\w*\b',
    'lens':   r'\blen[st]\w*\b',
    'nardus': r'\bnard\w*\b',
    'rosa':   r'\bros[ai]\w*\b',
    'faba':   r'\bfab[ae]\w*\b',
}

# Reverse: confirmed root → ingredient name
ROOT_TO_INGR = {}
for root, latin in CONFIRMED.items():
    ROOT_TO_INGR[root] = latin

# ================================================================
# STEP 1: Pre-compute Macer chapter ingredient positions
# ================================================================
print(f'\n{"="*70}')
print('STEP 1 — Pre-compute Macer chapters')
print('='*70)

chapter_data = {}

for ch in macer['chapters']:
    name = ch['name']
    text = ch['text'].lower()
    text_len = max(len(text), 1)

    # Find all ingredient positions
    ingr_positions = {}  # ingredient → list of positions (0-1)
    for ingr_name, pattern in INGR_PATTERNS.items():
        positions = []
        for m in re.finditer(pattern, text):
            positions.append(m.start() / text_len)
        if positions:
            ingr_positions[ingr_name] = positions

    chapter_data[name] = {
        'ingredients': set(ingr_positions.keys()),
        'positions': ingr_positions,
        'n_words': len(text.split()),
    }

print(f'  Macer chapters processed: {len(chapter_data)}')


# ================================================================
# STEP 2: Pre-compute VMS folio ingredient positions
# ================================================================
print(f'\n{"="*70}')
print('STEP 2 — Pre-compute VMS herbal folios')
print('='*70)

SHERWOOD = {
    'f48v':'ruta','f9v':'viola','f44v':'apium','f51v':'salvia',
    'f29r':'lactuca','f41r':'origanum','f37r':'mentha',
    'f41v':'coriandrum','f22r':'verbena','f28r':'aristolochia',
    'f5v':'malva','f45r':'atriplex','f66v':'satureia',
    'f65v':'centaurea','f3v':'elleborus','f95v1':'althaea',
    'f11r':'rosmarinus','f16r':'cannabis','f39r':'crocus',
    'f44r':'mandragora','f50v':'gentiana','f29v':'nigella',
    'f35v':'ribes','f47v':'pulmonaria','f53r':'achillea',
    'f14r':'scorzonera','f21r':'anagallis','f27r':'spinacia',
    'f33v':'tanacetum','f49r':'nymphaea','f87r':'satureia',
}

# Sherwood → Macer name mapping
SHERWOOD_TO_MACER = {
    'ruta':'Ruta','viola':'Violae','apium':'Apium','salvia':'Salvia',
    'lactuca':'Lactuca','origanum':'Origanum','mentha':'Mentha',
    'coriandrum':'Coriandrum','verbena':'Verbena','aristolochia':'Aristolochia',
    'malva':'Malva','atriplex':'Atriplex','satureia':'Satureia',
    'centaurea':'Centaurea','elleborus':'Elleborus','althaea':'Althaea',
}

folio_data = {}

for fid, folio in sorted(vms['folios'].items()):
    sec = folio['metadata']['section']
    if 'herbal' not in sec:
        continue

    # Find confirmed ingredients with positions
    all_words = []
    for block in folio['blocks']:
        for line in block['lines']:
            for w in line['words']:
                all_words.append(w)

    total_words = max(len(all_words), 1)
    ingr_positions = defaultdict(list)

    for i, w in enumerate(all_words):
        eva = w['eva_primary']
        if eva in LOGOS:
            continue
        for root in sorted_confirmed:
            if len(root) >= 3 and root in eva:
                ingr = CONFIRMED[root]
                ingr_positions[ingr].append(i / total_words)
                break

    folio_data[fid] = {
        'ingredients': set(ingr_positions.keys()),
        'positions': dict(ingr_positions),
        'n_words': total_words,
        'sherwood': SHERWOOD.get(fid),
    }

print(f'  Herbal folios processed: {len(folio_data)}')


# ================================================================
# STEP 3: MEGA MATCH — score every folio×chapter pair
# ================================================================
print(f'\n{"="*70}')
print('STEP 3 — MEGA MATCH ({} folios × {} chapters = {} pairs)'.format(
    len(folio_data), len(chapter_data), len(folio_data) * len(chapter_data)))
print('='*70)

all_scores = []

for fid, fdata in folio_data.items():
    folio_ingrs = fdata['ingredients']
    if not folio_ingrs:
        continue

    best_score = -999
    best_chapter = None
    chapter_scores = []

    for ch_name, cdata in chapter_data.items():
        ch_ingrs = cdata['ingredients']

        # Score components:
        # 1. Shared ingredients (Jaccard-like)
        shared = folio_ingrs & ch_ingrs
        n_shared = len(shared)

        if n_shared == 0:
            continue

        folio_only = folio_ingrs - ch_ingrs
        chapter_only = ch_ingrs - folio_ingrs

        # 2. Positional alignment quality for shared ingredients
        pos_score = 0
        n_pos_checked = 0

        for ingr in shared:
            if ingr in fdata['positions'] and ingr in cdata['positions']:
                # Compare positions: find best matching positions
                vms_positions = fdata['positions'][ingr]
                macer_positions_list = cdata['positions'][ingr]

                for vp in vms_positions:
                    best_dist = min(abs(vp - mp) for mp in macer_positions_list)
                    if best_dist < 0.3:  # reasonable alignment
                        pos_score += (0.3 - best_dist)  # higher = closer
                    n_pos_checked += 1

        # 3. Composite score
        # Weight: shared ingredients (most important) + positional alignment
        score = n_shared * 10 + pos_score * 5 - len(folio_only) * 2

        chapter_scores.append({
            'chapter': ch_name,
            'n_shared': n_shared,
            'pos_score': round(pos_score, 2),
            'folio_only': len(folio_only),
            'chapter_only': len(chapter_only),
            'score': round(score, 2),
            'shared_ingrs': sorted(shared),
        })

    chapter_scores.sort(key=lambda x: -x['score'])

    if chapter_scores:
        best = chapter_scores[0]
        second = chapter_scores[1] if len(chapter_scores) > 1 else None
        margin = best['score'] - second['score'] if second else best['score']

        all_scores.append({
            'fid': fid,
            'sherwood': fdata['sherwood'],
            'n_folio_ingrs': len(folio_ingrs),
            'best_chapter': best['chapter'],
            'best_score': best['score'],
            'best_shared': best['n_shared'],
            'best_ingrs': best['shared_ingrs'],
            'margin': round(margin, 2),
            'second_chapter': second['chapter'] if second else None,
            'second_score': second['score'] if second else 0,
            'top5': [(cs['chapter'], cs['score'], cs['n_shared']) for cs in chapter_scores[:5]],
        })

all_scores.sort(key=lambda x: (-x['best_score'], -x['margin']))


# ================================================================
# STEP 4: VALIDATION on Sherwood-identified folios
# ================================================================
print(f'\n{"="*70}')
print('STEP 4 — VALIDATION')
print('='*70)

correct_top1 = 0
correct_top5 = 0
tested = 0
validation_details = []

for s in all_scores:
    true_plant = s['sherwood']
    if not true_plant:
        continue

    true_macer = SHERWOOD_TO_MACER.get(true_plant)
    if not true_macer:
        continue

    tested += 1
    top5_chapters = [t[0] for t in s['top5']]

    is_top1 = s['best_chapter'] == true_macer
    is_top5 = true_macer in top5_chapters

    if is_top1:
        correct_top1 += 1
        correct_top5 += 1
        status = '✓ TOP1'
    elif is_top5:
        correct_top5 += 1
        rank = top5_chapters.index(true_macer) + 1
        status = f'~ TOP{rank}'
    else:
        status = '✗'

    validation_details.append({
        'fid': s['fid'],
        'true': true_macer,
        'predicted': s['best_chapter'],
        'status': status,
        'score': s['best_score'],
        'margin': s['margin'],
    })

    print(f'  {status:>8s} {s["fid"]:>8s} true={true_macer:>15s}  pred={s["best_chapter"]:>15s}  '
          f'score={s["best_score"]:>6.1f}  margin={s["margin"]:>5.1f}  '
          f'shared={s["best_ingrs"][:4]}')

if tested:
    print(f'\n  Top-1 accuracy: {correct_top1}/{tested} ({correct_top1*100//tested}%)')
    print(f'  Top-5 accuracy: {correct_top5}/{tested} ({correct_top5*100//tested}%)')


# ================================================================
# STEP 5: Show BEST new identifications (unidentified folios)
# ================================================================
print(f'\n\n{"="*70}')
print('STEP 5 — NEW PLANT IDENTIFICATIONS (speculative)')
print('='*70)

print(f'\n  {"Folio":>8s} {"BestChapter":>15s} {"Score":>6s} {"Margin":>7s} '
      f'{"Shared":>7s} {"2ndBest":>15s} {"Ingredients"}')
print('  ' + '-' * 90)

new_ids = []
for s in all_scores:
    if s['sherwood']:
        continue  # skip known
    if s['best_score'] < 15:
        continue  # skip low scores

    new_ids.append(s)
    print(f'  {s["fid"]:>8s} {s["best_chapter"]:>15s} {s["best_score"]:>6.1f} '
          f'{s["margin"]:>7.1f} {s["best_shared"]:>7d} '
          f'{s["second_chapter"] or "":>15s} {s["best_ingrs"][:5]}')

print(f'\n  Total new identifications (score >= 15): {len(new_ids)}')


# ================================================================
# SAVE
# ================================================================
output = {
    'total_pairs': len(folio_data) * len(chapter_data),
    'validation_top1': correct_top1,
    'validation_top5': correct_top5,
    'validation_tested': tested,
    'validation_details': validation_details,
    'new_identifications': [{
        'fid': s['fid'],
        'chapter': s['best_chapter'],
        'score': s['best_score'],
        'margin': s['margin'],
        'shared': s['best_ingrs'],
        'top5': s['top5'],
    } for s in new_ids],
    'all_scores_top20': [{
        'fid': s['fid'],
        'best_chapter': s['best_chapter'],
        'score': s['best_score'],
        'sherwood': s['sherwood'],
    } for s in all_scores[:20]],
}

with open(os.path.join(RESULTS, 'attack_mega_results.json'), 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f'\n{"="*70}')
print(f'MEGA MATCH SUMMARY')
print(f'  Pairs tested: {len(folio_data) * len(chapter_data)}')
print(f'  Validation: {correct_top1}/{tested} top-1, {correct_top5}/{tested} top-5')
print(f'  New identifications: {len(new_ids)}')
print(f'{"="*70}')
print(f'\nSaved attack_mega_results.json')
