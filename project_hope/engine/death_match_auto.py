"""
VOYNICH ENGINE — Auto-iterating Death Match

Runs death match iterations until convergence (no new cross-validated mappings).
Each iteration: expand anchors → re-run all folios → extract new mappings → repeat.
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
    'sulphur': ('INGR', r'\bsulph\w*\b'),
    'origanum': ('PLANT', r'\borigan\w*\b'), 'anethum': ('PLANT', r'\baneth\w*\b'),
    'coriandrum': ('PLANT', r'\bcoriand\w*\b'), 'chamomilla': ('PLANT', r'\bchamom\w*\b'),
    'plantago': ('PLANT', r'\bplantag\w*\b'), 'centaurea': ('PLANT', r'\bcentaur\w*\b'),
    'ruta': ('PLANT', r'\brut[ae]\w*\b'), 'mentha': ('PLANT', r'\bment[ha]\w*\b'),
    'aristolochia': ('PLANT', r'\baristoloch\w*\b'), 'salvia': ('PLANT', r'\bsalvi\w*\b'),
    'verbena': ('PLANT', r'\bverben\w*\b'), 'betonica': ('PLANT', r'\bbetonic\w*\b'),
    'urtica': ('PLANT', r'\burtic\w*\b'), 'malva': ('PLANT', r'\bmalv\w*\b'),
    'lactuca': ('PLANT', r'\blactuc\w*\b'),
    'oculus': ('BODY', r'\bocul\w*\b'), 'caput': ('BODY', r'\bcapit\w*\b|\bcaput\b'),
    'stomachus': ('BODY', r'\bstomach\w*\b'), 'venter': ('BODY', r'\bventr\w*\b'),
    'auris': ('BODY', r'\baur[ei]s?\b'), 'dens': ('BODY', r'\bdent\w*\b'),
    'vulnus': ('BODY', r'\bvulner\w*\b|\bvulnus\b'), 'matrix': ('BODY', r'\bmatri[cx]\w*\b'),
    'splen': ('BODY', r'\bsplen\w*\b'), 'urina': ('BODY', r'\burin\w*\b'),
    'menstrua': ('BODY', r'\bmenstr\w*\b'), 'ren': ('BODY', r'\bren[ui]\w*\b'),
    'pulmo': ('BODY', r'\bpulmon\w*\b'), 'sanguis': ('BODY', r'\bsangu\w*\b|\bcruor\w*\b'),
    'lumbus': ('BODY', r'\blumb\w*\b'), 'tussis': ('BODY', r'\btuss\w*\b'),
    'alvus': ('BODY', r'\balv\w*\b'), 'pectus': ('BODY', r'\bpector\w*\b|\bpectus\b'),
    'cutis': ('BODY', r'\bcut[ie]\w*\b'), 'naris': ('BODY', r'\bnar[ei]\w*\b'),
    'gingiva': ('BODY', r'\bgingiv\w*\b'),
    'decoctio': ('VERB', r'\bdecoct\w*\b'), 'trita': ('VERB', r'\btrit\w*\b'),
    'bibere': ('VERB', r'\bbib\w*\b'), 'coquere': ('VERB', r'\bcoqu\w*\b|\bcoct\w*\b'),
    'superaddere': ('VERB', r'\bsuperadd\w*\b'),
    'jungere': ('VERB', r'\bjung\w*\b|\bjunct\w*\b'),
    'sumere': ('VERB', r'\bsum[epi]\w*\b'),
    'apponere': ('VERB', r'\bappon\w*\b|\bapposit\w*\b'),
    'perungere': ('VERB', r'\bperung\w*\b|\bperunct\w*\b'),
    'fovere': ('VERB', r'\bfov\w*\b'), 'ligare': ('VERB', r'\blig\w*\b'),
    'infundere': ('VERB', r'\binfund\w*\b|\binfus\w*\b'),
    'dolor': ('DISEASE', r'\bdolor\w*\b'), 'tumor': ('DISEASE', r'\btumor\w*\b'),
    'febris': ('DISEASE', r'\bfebr\w*\b'), 'morsus': ('DISEASE', r'\bmors\w*\b'),
    'venenum': ('DISEASE', r'\bvenen\w*\b'), 'podagra': ('DISEASE', r'\bpodag\w*\b'),
    'icterus': ('DISEASE', r'\bicter\w*\b'), 'scrophula': ('DISEASE', r'\bscro[pf]\w*\b'),
    'paralysis': ('DISEASE', r'\bparaly\w*\b'),
}

TARGETS = {
    'f9v': 'Violae', 'f41r': 'Origanum', 'f37r': 'Mentha',
    'f28r': 'Aristolochia', 'f3v': 'Elleborus', 'f22r': 'Verbena',
    'f44v': 'Apium', 'f41v': 'Coriandrum', 'f45r': 'Atriplex',
    'f48v': 'Ruta', 'f5v': 'Malva', 'f29r': 'Lactuca',
}

MACER_BY_NAME = {ch['name']: ch for ch in macer_data['chapters']}

# ================================================================
# Initialize anchors from registry
# ================================================================
anchors = {}
for root, data in registry['confirmed_ingredients'].items():
    if len(root) >= 3:
        anchors[root] = data['latin']
anchors.update({
    'ypch': 'aqua', 'ykeed': 'nitrum', 'seees': 'lens',
    'kald': 'ovum', 'otoly': 'sal', 'shocthy': 'mastix', 'shotch': 'nigella',
})
for root, data in registry.get('death_match_vocabulary', {}).items():
    if len(root) >= 3:
        anchors[root] = data['latin']

# ================================================================
# Death match function
# ================================================================
def death_match(fid, chapter_name, anchor_dict, threshold=0.10):
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
            all_words.extend(line['words'])
    total_words = max(len(all_words), 1)

    # Find calibration anchors
    cal_anchors = []
    for i, w in enumerate(all_words):
        eva = w['eva_primary']
        if eva in LOGO_SET:
            continue
        for root, latin in sorted(anchor_dict.items(), key=lambda x: -len(x[0])):
            if len(root) >= 3 and root in eva:
                for mw in macer_words:
                    if mw['word'] == latin or latin in mw['word'] or mw['word'] in latin:
                        cal_anchors.append({
                            'vms_pos': i / total_words, 'macer_pos': mw['position'],
                        })
                        break
                break

    if not cal_anchors:
        return None

    mean_offset = sum(a['vms_pos'] - a['macer_pos'] for a in cal_anchors) / len(cal_anchors)

    matches = []
    for i, w in enumerate(all_words):
        eva = w['eva_primary']
        root = (w.get('morphology') or {}).get('root', '')
        if eva in LOGO_SET or not root or len(root) < 3:
            continue
        if root in FUNCTIONAL or root in {'ke', 'ko', 'po', 'do'}:
            continue
        if root in anchor_dict:
            continue

        adjusted = (i / total_words) - mean_offset
        best = None
        best_dist = 999
        for mw in macer_words:
            dist = abs(adjusted - mw['position'])
            if dist < best_dist:
                best_dist = dist
                best = mw

        if best and best_dist < threshold:
            matches.append({
                'root': root, 'macer_word': best['word'],
                'macer_type': best['type'], 'distance': round(best_dist, 4),
            })

    return {
        'n_anchors': len(cal_anchors), 'n_matches': len(matches),
        'mean_offset': round(mean_offset, 3), 'matches': matches,
    }

# ================================================================
# AUTO-ITERATE
# ================================================================
MAX_ITERS = 20
MIN_NEW = 1  # stop if fewer than this many new mappings

print('='*70)
print(f'AUTO-ITERATING DEATH MATCH')
print(f'Starting anchors: {len(anchors)}')
print('='*70)

all_history = []

for iteration in range(1, MAX_ITERS + 1):
    all_mappings = defaultdict(Counter)

    total_anchors_found = 0
    total_matches = 0

    for fid, chapter in TARGETS.items():
        result = death_match(fid, chapter, anchors)
        if not result:
            continue
        total_anchors_found += result['n_anchors']
        total_matches += result['n_matches']

        for m in result['matches']:
            all_mappings[m['root']][(m['macer_word'], m['macer_type'])] += 1

    # Cross-validate: 2+ folios agree
    new_this_iter = {}
    for root, candidates in all_mappings.items():
        if root in anchors:
            continue
        best_key, best_count = candidates.most_common(1)[0]
        if best_count >= 2:
            total = sum(candidates.values())
            consistency = best_count / total
            if consistency >= 0.25:  # at least 25% agreement
                word, wtype = best_key
                new_this_iter[root] = {
                    'word': word, 'type': wtype,
                    'count': best_count, 'consistency': round(consistency, 2),
                }

    # Add new mappings to anchors
    actually_new = {r: d for r, d in new_this_iter.items() if r not in anchors}
    for root, data in actually_new.items():
        anchors[root] = data['word']

    all_history.append({
        'iteration': iteration,
        'n_anchors': len(anchors),
        'total_anchors_found': total_anchors_found,
        'total_matches': total_matches,
        'n_new': len(actually_new),
        'new_mappings': {r: f"{d['word']}({d['type']},{d['count']}f,{d['consistency']:.0%})"
                        for r, d in actually_new.items()},
    })

    new_str = ', '.join(f'{r}={d["word"]}' for r, d in list(actually_new.items())[:5])
    extra = f' +{len(actually_new)-5} more' if len(actually_new) > 5 else ''

    print(f'\n  ITER {iteration}: anchors={len(anchors)}  '
          f'found={total_anchors_found}  matches={total_matches}  '
          f'NEW={len(actually_new)}')
    if actually_new:
        print(f'    {new_str}{extra}')

    if len(actually_new) < MIN_NEW:
        print(f'\n  CONVERGED at iteration {iteration} (no new mappings)')
        break

# ================================================================
# FINAL RESULTS
# ================================================================
print(f'\n\n{"="*70}')
print('FINAL RESULTS')
print('='*70)

# Separate initial from discovered
initial_roots = set()
for root in registry['confirmed_ingredients']:
    if len(root) >= 3:
        initial_roots.add(root)
initial_roots.update({'ypch', 'ykeed', 'seees', 'kald', 'otoly', 'shocthy', 'shotch'})
for root in registry.get('death_match_vocabulary', {}):
    initial_roots.add(root)

discovered = {r: l for r, l in anchors.items() if r not in initial_roots}

print(f'\n  Starting anchors: {len(initial_roots)}')
print(f'  Discovered (all iterations): {len(discovered)}')
print(f'  Total anchors: {len(anchors)}')

# Categorize discovered
by_type = defaultdict(list)
for root, word in discovered.items():
    # Find type from history
    wtype = 'UNK'
    for h in all_history:
        for r, desc in h['new_mappings'].items():
            if r == root:
                wtype = desc.split('(')[1].split(',')[0] if '(' in desc else 'UNK'
                break
    by_type[wtype].append((root, word))

for wtype in sorted(by_type.keys()):
    items = by_type[wtype]
    print(f'\n  {wtype} ({len(items)}):')
    for root, word in sorted(items, key=lambda x: x[1]):
        print(f'    {root:>12s} = {word}')

# Growth curve
print(f'\n  GROWTH:')
for h in all_history:
    bar = '#' * h['n_new']
    print(f'    Iter {h["iteration"]:>2d}: {h["n_anchors"]:>3d} anchors, '
          f'+{h["n_new"]:>2d} new  {bar}')

# Save
output = {
    'final_n_anchors': len(anchors),
    'n_discovered': len(discovered),
    'history': all_history,
    'all_anchors': anchors,
    'discovered': discovered,
}

with open(os.path.join(RESULTS, 'death_match_auto_results.json'), 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f'\nSaved death_match_auto_results.json')
