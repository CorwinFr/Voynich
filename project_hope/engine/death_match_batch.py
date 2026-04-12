"""
VOYNICH ENGINE — Death Match Batch

Run positional alignment on ALL confirmed folio↔Macer chapter pairs.
Extract new root→word mappings from each alignment.
Cross-validate: a mapping found in 2+ folios is more reliable.

Targets:
  f48v = Ruta (already done, reference)
  f9v  = Violae
  f41r = Origanum
  f37r = Mentha
  f28r = Aristolochia
  f3v  = Elleborus
  f22r = Verbena
  f44v = Apium
  f41v = Coriandrum
  f45r = Atriplex
  f51v = Salvia
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

CONFIRMED = {}
for root, data in registry['confirmed_ingredients'].items():
    if len(root) >= 3:
        CONFIRMED[root] = data['latin']
CONFIRMED['ypch'] = 'aqua'
CONFIRMED['ykeed'] = 'nitrum'
CONFIRMED['seees'] = 'lens'
CONFIRMED['kald'] = 'ovum'
CONFIRMED['otoly'] = 'sal'
CONFIRMED['shocthy'] = 'mastix'
CONFIRMED['shotch'] = 'nigella'

# ALL significant Latin words to search in Macer text
LATIN_WORDS = {
    # Ingredients
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
    # Body parts
    'oculus': ('BODY', r'\bocul\w*\b'), 'caput': ('BODY', r'\bcapit\w*\b|\bcaput\b'),
    'stomachus': ('BODY', r'\bstomach\w*\b'), 'venter': ('BODY', r'\bventr\w*\b|\bvent[re]\w*\b'),
    'auris': ('BODY', r'\baur[ei]\w*\b'), 'dens': ('BODY', r'\bdent\w*\b'),
    'vulnus': ('BODY', r'\bvulner\w*\b|\bvulnus\b'), 'matrix': ('BODY', r'\bmatri[cx]\w*\b'),
    'splen': ('BODY', r'\bsplen\w*\b'), 'urina': ('BODY', r'\burin\w*\b'),
    'menstrua': ('BODY', r'\bmenstr\w*\b'), 'ren': ('BODY', r'\bren[ui]\w*\b'),
    'pulmo': ('BODY', r'\bpulmon\w*\b|\bpulm\w*\b'), 'hepar': ('BODY', r'\bhepar\b|\bhepat\w*\b'),
    'os': ('BODY', r'\boss[aei]\w*\b'), 'sanguis': ('BODY', r'\bsangu\w*\b|\bcruor\w*\b'),
    'lumbus': ('BODY', r'\blumb\w*\b'), 'tussis': ('BODY', r'\btuss\w*\b'),
    # Preparation
    'decoctio': ('VERB', r'\bdecoct\w*\b'), 'trita': ('VERB', r'\btrit\w*\b|\bter\w*\b'),
    'bibere': ('VERB', r'\bbib\w*\b'), 'coquere': ('VERB', r'\bcoqu\w*\b|\bcoct\w*\b'),
    'superaddere': ('VERB', r'\bsuperadd\w*\b'), 'jungere': ('VERB', r'\bjung\w*\b|\bjunct\w*\b'),
    'sumere': ('VERB', r'\bsum[epi]\w*\b'), 'apponere': ('VERB', r'\bappon\w*\b|\bapposit\w*\b'),
    # Conditions
    'dolor': ('DISEASE', r'\bdolor\w*\b'), 'tumor': ('DISEASE', r'\btumor\w*\b'),
    'febris': ('DISEASE', r'\bfebr\w*\b'), 'morsus': ('DISEASE', r'\bmors\w*\b'),
    'venenum': ('DISEASE', r'\bvenen\w*\b'), 'serpens': ('DISEASE', r'\bserpen\w*\b'),
    'podagra': ('DISEASE', r'\bpodag\w*\b'), 'icterus': ('DISEASE', r'\bicter\w*\b'),
}

# Target folio↔chapter pairs
TARGETS = {
    'f9v':  'Violae',
    'f41r': 'Origanum',
    'f37r': 'Mentha',
    'f28r': 'Aristolochia',
    'f3v':  'Elleborus',
    'f22r': 'Verbena',
    'f44v': 'Apium',
    'f41v': 'Coriandrum',
    'f45r': 'Atriplex',
    'f51v': 'Salvia',
    'f48v': 'Ruta',
}

MACER_BY_NAME = {ch['name']: ch for ch in macer_data['chapters']}
if 'Violae' not in MACER_BY_NAME and 'Violae' in [ch['name'] for ch in macer_data['chapters']]:
    pass  # already there

# ================================================================
# DEATH MATCH FUNCTION
# ================================================================
def death_match(fid, chapter_name):
    """Run positional alignment between a VMS folio and a Macer chapter."""
    ch = MACER_BY_NAME.get(chapter_name)
    if not ch:
        return None

    text = ch['text'].lower()
    text_len = max(len(text), 1)

    # Find all significant Latin words with positions in the chapter
    macer_words = []
    for concept, (ctype, pattern) in LATIN_WORDS.items():
        for m in re.finditer(pattern, text):
            macer_words.append({
                'word': concept,
                'type': ctype,
                'position': m.start() / text_len,
            })
    macer_words.sort(key=lambda x: x['position'])

    # Extract VMS words with positions
    folio = vms['folios'].get(fid)
    if not folio:
        return None

    all_words = []
    for block in folio['blocks']:
        for line in block['lines']:
            for w in line['words']:
                all_words.append(w)

    total_words = max(len(all_words), 1)

    # Find calibration anchors (confirmed roots that appear in this chapter)
    anchors = []
    for i, w in enumerate(all_words):
        eva = w['eva_primary']
        if eva in LOGO_SET:
            continue
        for root, latin in CONFIRMED.items():
            if len(root) >= 3 and root in eva:
                # Is this ingredient in the chapter?
                for mw in macer_words:
                    if mw['word'] == latin or latin in mw['word']:
                        anchors.append({
                            'root': root,
                            'latin': latin,
                            'vms_pos': i / total_words,
                            'macer_pos': mw['position'],
                        })
                        break
                break

    if not anchors:
        return None

    # Compute mean offset
    offsets = [a['vms_pos'] - a['macer_pos'] for a in anchors]
    mean_offset = sum(offsets) / len(offsets)

    # Match unknown VMS roots to closest Macer word
    matches = []
    for i, w in enumerate(all_words):
        eva = w['eva_primary']
        root = (w.get('morphology') or {}).get('root', '')

        if eva in LOGO_SET or not root or len(root) < 3:
            continue
        if root in FUNCTIONAL or root in {'ke', 'ko', 'po', 'do'}:
            continue
        if root in CONFIRMED:
            continue

        vms_pos = i / total_words
        adjusted = vms_pos - mean_offset

        best = None
        best_dist = 999
        for mw in macer_words:
            dist = abs(adjusted - mw['position'])
            if dist < best_dist:
                best_dist = dist
                best = mw

        if best and best_dist < 0.12:  # strict: within 12%
            matches.append({
                'root': root,
                'eva': eva,
                'vms_pos': round(vms_pos, 3),
                'macer_word': best['word'],
                'macer_type': best['type'],
                'distance': round(best_dist, 4),
            })

    return {
        'fid': fid,
        'chapter': chapter_name,
        'n_anchors': len(anchors),
        'mean_offset': round(mean_offset, 3),
        'n_matches': len(matches),
        'matches': matches,
        'anchors': [(a['root'], a['latin']) for a in anchors],
    }

# ================================================================
# RUN ALL DEATH MATCHES
# ================================================================
print('='*70)
print(f'DEATH MATCH BATCH — {len(TARGETS)} folio×chapter pairs')
print('='*70)

all_results = []
all_mappings = defaultdict(Counter)  # root → {macer_word: count}

for fid, chapter in TARGETS.items():
    result = death_match(fid, chapter)
    if not result:
        print(f'\n  {fid} × {chapter}: NO RESULT (no anchors or chapter not found)')
        continue

    all_results.append(result)

    print(f'\n  {fid:>6s} × {chapter:>15s}  anchors={result["n_anchors"]}  '
          f'offset={result["mean_offset"]:+.3f}  matches={result["n_matches"]}')
    print(f'    Anchors: {result["anchors"][:5]}')

    for m in result['matches'][:10]:
        print(f'    {m["root"]:>10s} → {m["macer_word"]:>12s} [{m["macer_type"]:>7s}]  '
              f'dist={m["distance"]:.3f}')

    # Accumulate mappings
    for m in result['matches']:
        all_mappings[m['root']][m['macer_word']] += 1


# ================================================================
# CROSS-VALIDATION: mappings found in 2+ folios
# ================================================================
print(f'\n\n{"="*70}')
print('CROSS-VALIDATED MAPPINGS (found in 2+ death matches)')
print('='*70)

cross_validated = []

for root, candidates in sorted(all_mappings.items(), key=lambda x: -max(x[1].values())):
    best_word, best_count = candidates.most_common(1)[0]
    total = sum(candidates.values())

    if best_count >= 2:
        consistency = best_count / total
        alternatives = [(w, c) for w, c in candidates.most_common(3)[1:] if c > 0]

        cross_validated.append({
            'root': root,
            'word': best_word,
            'type': '',
            'count': best_count,
            'total': total,
            'consistency': round(consistency, 2),
            'alternatives': alternatives,
        })

        # Find the type
        for r in all_results:
            for m in r['matches']:
                if m['root'] == root and m['macer_word'] == best_word:
                    cross_validated[-1]['type'] = m['macer_type']
                    break

cross_validated.sort(key=lambda x: (-x['count'], -x['consistency']))

print(f'\n  {"Root":>12s} {"Word":>12s} {"Type":>8s} {"Count":>6s} {"Total":>6s} '
      f'{"Consist":>8s} {"Alternatives"}')
print('  ' + '-' * 75)

for cv in cross_validated:
    alt_str = ', '.join(f'{w}({c})' for w, c in cv['alternatives'][:2])
    marker = '★★★' if cv['count'] >= 4 else '★★' if cv['count'] >= 3 else '★'
    print(f'  {cv["root"]:>12s} {cv["word"]:>12s} {cv["type"]:>8s} '
          f'{cv["count"]:>6d} {cv["total"]:>6d} {cv["consistency"]:>7.0%}  '
          f'{alt_str}  {marker}')

print(f'\n  Total cross-validated: {len(cross_validated)}')
print(f'  High confidence (3+): {sum(1 for cv in cross_validated if cv["count"] >= 3)}')


# ================================================================
# SAVE
# ================================================================
output = {
    'n_targets': len(TARGETS),
    'n_results': len(all_results),
    'n_cross_validated': len(cross_validated),
    'results': all_results,
    'cross_validated': cross_validated,
}

with open(os.path.join(RESULTS, 'death_match_batch_results.json'), 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f'\nSaved death_match_batch_results.json')
