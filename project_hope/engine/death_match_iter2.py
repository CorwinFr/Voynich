"""
VOYNICH ENGINE — Death Match Iteration 2

Re-run with EXPANDED vocabulary (original 10 + 8 from iter 1 = 18 anchors).
More anchors → better calibration → more matches → more vocabulary.
"""
import json, sys, io, os, re
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.dirname(os.path.dirname(__file__))
VMS_PATH = os.path.join(BASE, 'vms', 'vms_structured.json')
MACER_PATH = os.path.join(BASE, 'session_14', 'macer_complete.json')
REG_PATH = os.path.join(BASE, 'hypothesis_registry.json')
RESULTS = os.path.join(BASE, 'engine')

with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)
with open(MACER_PATH, encoding='utf-8') as f:
    macer_data = json.load(f)
with open(REG_PATH, encoding='utf-8') as f:
    registry = json.load(f)

LOGOS = {'o': 'ac', 'l': 'se', 'd': 'de', 'r': 'recipe', 'v': 'vel',
         'x': 'crux', 'k': 'cum', 'm': 'misce', 'f': 'per', 't': 'et',
         'y': 'in', 'c': 'cum', 's': 'est', 'sh': 'ci', 'p': 'usque', 'ch': 'cum'}
LOGO_SET = set(LOGOS.keys())
FUNCTIONAL = set(registry.get('functional_words', {}).keys())

# EXPANDED ANCHORS: confirmed + iter1 death match vocabulary
ANCHORS = {}
for root, data in registry['confirmed_ingredients'].items():
    if len(root) >= 3:
        ANCHORS[root] = data['latin']
ANCHORS['ypch'] = 'aqua'
ANCHORS['ykeed'] = 'nitrum'
ANCHORS['seees'] = 'lens'
ANCHORS['kald'] = 'ovum'
ANCHORS['otoly'] = 'sal'
ANCHORS['shocthy'] = 'mastix'
ANCHORS['shotch'] = 'nigella'

# Add iter1 death match vocabulary
for root, data in registry.get('death_match_vocabulary', {}).items():
    if len(root) >= 3:
        ANCHORS[root] = data['latin']

print(f'ITERATION 2 — Anchors: {len(ANCHORS)} (was 10 in iter 1)')
for r, l in sorted(ANCHORS.items(), key=lambda x: x[1]):
    print(f'  {r:>10s} = {l}')

# ALL significant Latin words
LATIN_WORDS = {
    'acetum': ('INGR', r'\bacet\w*\b'), 'aqua': ('INGR', r'\baqua\w*\b|\bamne\b'),
    'mel': ('INGR', r'\bmel\b|\bmell\w*\b|\bmulsa\b'),
    'piper': ('INGR', r'\bpiper\w*\b'), 'oleum': ('INGR', r'\boleu\w*\b|\boleo\b'),
    'sal': ('INGR', r'\bsal[ei]?\b|\bsale\b|\bsalque\b'),
    'vinum': ('INGR', r'\bvin\w*\b|\bmero\b|\bmust\w*\b'),
    'succus': ('INGR', r'\bsucc\w*\b'), 'lac': ('INGR', r'\blac\b|\blact\w*\b'),
    'ovum': ('INGR', r'\bov[uoia]\w*\b'), 'nitrum': ('INGR', r'\bnitr\w*\b'),
    'myrrha': ('INGR', r'\bmyrrh\w*\b'), 'lens': ('INGR', r'\blen[st]\w*\b'),
    'nardus': ('INGR', r'\bnard\w*\b'), 'rosa': ('INGR', r'\bros[aisae]\w*\b'),
    'faba': ('INGR', r'\bfab\w*\b'), 'linum': ('INGR', r'\blin[uoi]\w*\b'),
    'feniculum': ('INGR', r'\bfenic\w*\b'), 'vesica': ('INGR', r'\bvesic\w*\b'),
    'cera': ('INGR', r'\bcer[ae]\w*\b'), 'thus': ('INGR', r'\bthus\b|\bthur\w*\b'),
    'origanum': ('INGR', r'\borigan\w*\b'), 'anethum': ('INGR', r'\baneth\w*\b'),
    'coriandrum': ('INGR', r'\bcoriand\w*\b'), 'chamomilla': ('INGR', r'\bchamom\w*\b'),
    'plantago': ('INGR', r'\bplantag\w*\b'), 'centaurea': ('INGR', r'\bcentaur\w*\b'),
    'ruta': ('PLANT', r'\brut[ae]\w*\b'), 'mentha': ('PLANT', r'\bment[ha]\w*\b'),
    'aristolochia': ('PLANT', r'\baristoloch\w*\b'), 'salvia': ('PLANT', r'\bsalvi\w*\b'),
    'verbena': ('PLANT', r'\bverben\w*\b'), 'betonica': ('PLANT', r'\bbetonic\w*\b'),
    'urtica': ('PLANT', r'\burtic\w*\b'),
    # Body
    'oculus': ('BODY', r'\bocul\w*\b'), 'caput': ('BODY', r'\bcapit\w*\b|\bcaput\b'),
    'stomachus': ('BODY', r'\bstomach\w*\b'), 'venter': ('BODY', r'\bventr\w*\b'),
    'auris': ('BODY', r'\baur[ei]\w*\b'), 'dens': ('BODY', r'\bdent\w*\b'),
    'vulnus': ('BODY', r'\bvulner\w*\b|\bvulnus\b'), 'matrix': ('BODY', r'\bmatri[cx]\w*\b'),
    'splen': ('BODY', r'\bsplen\w*\b'), 'urina': ('BODY', r'\burin\w*\b'),
    'menstrua': ('BODY', r'\bmenstr\w*\b'), 'ren': ('BODY', r'\bren[ui]\w*\b'),
    'pulmo': ('BODY', r'\bpulmon\w*\b'), 'sanguis': ('BODY', r'\bsangu\w*\b|\bcruor\w*\b'),
    'lumbus': ('BODY', r'\blumb\w*\b'), 'tussis': ('BODY', r'\btuss\w*\b'),
    # Verbs
    'decoctio': ('VERB', r'\bdecoct\w*\b'), 'trita': ('VERB', r'\btrit\w*\b'),
    'bibere': ('VERB', r'\bbib\w*\b'), 'coquere': ('VERB', r'\bcoqu\w*\b|\bcoct\w*\b'),
    'superaddere': ('VERB', r'\bsuperadd\w*\b'), 'jungere': ('VERB', r'\bjung\w*\b|\bjunct\w*\b'),
    'sumere': ('VERB', r'\bsum[epi]\w*\b'), 'apponere': ('VERB', r'\bappon\w*\b|\bapposit\w*\b'),
    'perungere': ('VERB', r'\bperung\w*\b|\bperunct\w*\b'),
    # Diseases
    'dolor': ('DISEASE', r'\bdolor\w*\b'), 'tumor': ('DISEASE', r'\btumor\w*\b'),
    'febris': ('DISEASE', r'\bfebr\w*\b'), 'morsus': ('DISEASE', r'\bmors\w*\b'),
    'venenum': ('DISEASE', r'\bvenen\w*\b'), 'podagra': ('DISEASE', r'\bpodag\w*\b'),
    'icterus': ('DISEASE', r'\bicter\w*\b'),
}

TARGETS = {
    'f9v': 'Violae', 'f41r': 'Origanum', 'f37r': 'Mentha',
    'f28r': 'Aristolochia', 'f3v': 'Elleborus', 'f22r': 'Verbena',
    'f44v': 'Apium', 'f41v': 'Coriandrum', 'f45r': 'Atriplex',
    'f48v': 'Ruta', 'f5v': 'Malva', 'f65v': 'Centaurea',
    'f29r': 'Lactuca',
}

MACER_BY_NAME = {ch['name']: ch for ch in macer_data['chapters']}

# ================================================================
# DEATH MATCH FUNCTION (same as iter1 but with expanded anchors)
# ================================================================
def death_match(fid, chapter_name):
    ch = MACER_BY_NAME.get(chapter_name)
    if not ch:
        return None
    text = ch['text'].lower()
    text_len = max(len(text), 1)

    macer_words = []
    for concept, (ctype, pattern) in LATIN_WORDS.items():
        for m in re.finditer(pattern, text):
            macer_words.append({'word': concept, 'type': ctype, 'position': m.start() / text_len})
    macer_words.sort(key=lambda x: x['position'])

    folio = vms['folios'].get(fid)
    if not folio:
        return None
    all_words = []
    for block in folio['blocks']:
        for line in block['lines']:
            for w in line['words']:
                all_words.append(w)
    total_words = max(len(all_words), 1)

    # Find anchors
    anchors = []
    for i, w in enumerate(all_words):
        eva = w['eva_primary']
        if eva in LOGO_SET:
            continue
        for root, latin in sorted(ANCHORS.items(), key=lambda x: -len(x[0])):
            if len(root) >= 3 and root in eva:
                for mw in macer_words:
                    if mw['word'] == latin or latin in mw['word'] or mw['word'] in latin:
                        anchors.append({
                            'root': root, 'latin': latin,
                            'vms_pos': i / total_words, 'macer_pos': mw['position'],
                        })
                        break
                break

    if not anchors:
        return None

    mean_offset = sum(a['vms_pos'] - a['macer_pos'] for a in anchors) / len(anchors)

    matches = []
    for i, w in enumerate(all_words):
        eva = w['eva_primary']
        root = (w.get('morphology') or {}).get('root', '')
        if eva in LOGO_SET or not root or len(root) < 3:
            continue
        if root in FUNCTIONAL or root in {'ke', 'ko', 'po', 'do'}:
            continue
        if root in ANCHORS:
            continue

        adjusted = (i / total_words) - mean_offset
        best = None
        best_dist = 999
        for mw in macer_words:
            dist = abs(adjusted - mw['position'])
            if dist < best_dist:
                best_dist = dist
                best = mw

        if best and best_dist < 0.10:  # tighter threshold for iter 2
            matches.append({
                'root': root, 'eva': eva,
                'vms_pos': round(i / total_words, 3),
                'macer_word': best['word'], 'macer_type': best['type'],
                'distance': round(best_dist, 4),
            })

    return {
        'fid': fid, 'chapter': chapter_name,
        'n_anchors': len(anchors), 'mean_offset': round(mean_offset, 3),
        'n_matches': len(matches), 'matches': matches,
    }

# ================================================================
# RUN
# ================================================================
print(f'\n{"="*70}')
print(f'DEATH MATCH ITERATION 2 — {len(TARGETS)} targets, {len(ANCHORS)} anchors')
print('='*70)

all_mappings = defaultdict(Counter)
all_results = []

for fid, chapter in TARGETS.items():
    result = death_match(fid, chapter)
    if not result:
        print(f'  {fid:>6s} × {chapter:>15s}: NO RESULT')
        continue
    all_results.append(result)
    print(f'  {fid:>6s} × {chapter:>15s}  anchors={result["n_anchors"]:>2d}  '
          f'offset={result["mean_offset"]:+.3f}  matches={result["n_matches"]:>2d}')

    for m in result['matches']:
        all_mappings[m['root']][m['macer_word']] += 1

# ================================================================
# CROSS-VALIDATION
# ================================================================
print(f'\n{"="*70}')
print('CROSS-VALIDATED MAPPINGS (iteration 2)')
print('='*70)

cross_validated = []
for root, candidates in sorted(all_mappings.items(), key=lambda x: -max(x[1].values())):
    best_word, best_count = candidates.most_common(1)[0]
    total = sum(candidates.values())
    if best_count >= 2:
        consistency = best_count / total
        alts = [(w, c) for w, c in candidates.most_common(3)[1:] if c > 0]
        # Find type
        wtype = ''
        for r in all_results:
            for m in r['matches']:
                if m['root'] == root and m['macer_word'] == best_word:
                    wtype = m['macer_type']
                    break
            if wtype:
                break

        cross_validated.append({
            'root': root, 'word': best_word, 'type': wtype,
            'count': best_count, 'total': total,
            'consistency': round(consistency, 2),
            'alternatives': alts,
        })

cross_validated.sort(key=lambda x: (-x['count'], -x['consistency']))

print(f'\n  {"Root":>12s} {"Word":>15s} {"Type":>8s} {"N":>3s} {"Tot":>4s} '
      f'{"Con":>4s} {"Alt"}')
print('  ' + '-' * 70)

for cv in cross_validated:
    alt_str = ', '.join(f'{w}({c})' for w, c in cv['alternatives'][:2])
    stars = '★★★' if cv['count'] >= 4 else '★★' if cv['count'] >= 3 else '★'
    print(f'  {cv["root"]:>12s} {cv["word"]:>15s} {cv["type"]:>8s} '
          f'{cv["count"]:>3d} {cv["total"]:>4d} {cv["consistency"]:>3.0%}  '
          f'{alt_str} {stars}')

# New vs iter1
iter1_roots = {'cthy', 'otch', 'chy', 'dary', 'qoty', 'alch', 'cho', 'chek'}
new_in_iter2 = [cv for cv in cross_validated if cv['root'] not in iter1_roots]

print(f'\n  Total cross-validated: {len(cross_validated)}')
print(f'  From iter 1: {sum(1 for cv in cross_validated if cv["root"] in iter1_roots)}')
print(f'  NEW in iter 2: {len(new_in_iter2)}')
if new_in_iter2:
    print(f'\n  NEW DISCOVERIES (iter 2 only):')
    for cv in new_in_iter2:
        print(f'    {cv["root"]:>12s} = {cv["word"]:>15s} [{cv["type"]:>8s}] '
              f'({cv["count"]} folios, {cv["consistency"]:.0%})')

# Save
output = {
    'n_anchors': len(ANCHORS),
    'n_targets': len(TARGETS),
    'n_cross_validated': len(cross_validated),
    'n_new_iter2': len(new_in_iter2),
    'cross_validated': cross_validated,
    'results': [{
        'fid': r['fid'], 'chapter': r['chapter'],
        'n_anchors': r['n_anchors'], 'n_matches': r['n_matches'],
    } for r in all_results],
}

with open(os.path.join(RESULTS, 'death_match_iter2_results.json'), 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f'\nSaved death_match_iter2_results.json')
