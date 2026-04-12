"""
VOYNICH ENGINE — Death Match Multi-Corpus

Death match on Collectio Salernitana entries for our 16 Sherwood plants.
Cross-validate with Macer death match results.
Root found in BOTH Macer AND Collectio = high confidence.
"""
import json, sys, io, os, re
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.dirname(os.path.dirname(__file__))
VMS_PATH = os.path.join(BASE, 'vms', 'vms_structured.json')
REG_PATH = os.path.join(BASE, 'hypothesis_registry.json')
COLL_PATH = os.path.join(os.path.dirname(BASE), 'attacks', 'RECIPE_DATASET', 'S09_COLLECTIO.json')
AVIG_PATH = os.path.join(os.path.dirname(BASE), 'attacks', 'RECIPE_DATASET', 'S08_AVICENNA.json')
RESULTS = os.path.join(BASE, 'engine')

with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)
with open(REG_PATH, encoding='utf-8') as f:
    registry = json.load(f)
with open(COLL_PATH, encoding='utf-8') as f:
    collectio = json.load(f)

LOGOS = {'o': 'ac', 'l': 'se', 'd': 'de', 'r': 'recipe', 'v': 'vel',
         'x': 'crux', 'k': 'cum', 'm': 'misce', 'f': 'per', 't': 'et',
         'y': 'in', 'c': 'cum', 's': 'est', 'sh': 'ci', 'p': 'usque', 'ch': 'cum'}
LOGO_SET = set(LOGOS.keys())
FUNCTIONAL = set(registry.get('functional_words', {}).keys())

# All tier 1+2 anchors
ANCHORS = {}
for root, data in registry['confirmed_ingredients'].items():
    if len(root) >= 3: ANCHORS[root] = data['latin']
ANCHORS.update({'ypch':'aqua','ykeed':'nitrum','seees':'lens','kald':'ovum',
                'otoly':'sal','shocthy':'mastix','shotch':'nigella'})
for root, data in registry.get('death_match_vocabulary', {}).items():
    if data.get('type') == 'INGR' and data.get('status') not in ('ELIMINATED','CONFLICTED'):
        if len(root) >= 3: ANCHORS[root] = data['latin']

# Extended Latin word patterns
LATIN_WORDS = {
    'acetum': ('INGR', r'\bacet\w*\b'), 'aqua': ('INGR', r'\baqua\w*\b'),
    'mel': ('INGR', r'\bmel\b|\bmell\w*\b'), 'piper': ('INGR', r'\bpiper\w*\b'),
    'oleum': ('INGR', r'\boleu\w*\b|\boleo\b'), 'sal': ('INGR', r'\bsal[ei]?\b|\bsale\b'),
    'vinum': ('INGR', r'\bvin\w*\b'), 'succus': ('INGR', r'\bsucc\w*\b'),
    'lac': ('INGR', r'\blac\b|\blact[ei]\w*\b'), 'ovum': ('INGR', r'\bov[uoia]\w*\b'),
    'nitrum': ('INGR', r'\bnitr\w*\b'), 'myrrha': ('INGR', r'\bmyrrh\w*\b'),
    'rosa': ('INGR', r'\bros[aisae]\w*\b'), 'faba': ('INGR', r'\bfab[ae]\w*\b'),
    'feniculum': ('INGR', r'\bfenic\w*\b'), 'cera': ('INGR', r'\bcer[ae]\w*\b'),
    'adeps': ('INGR', r'\badep\w*\b|\baxungi\w*\b'),
    'thus': ('INGR', r'\bthus\b|\bthur\w*\b'),
    'hordeum': ('INGR', r'\bhorde\w*\b'), 'amygdala': ('INGR', r'\bamygdal\w*\b'),
    'camphora': ('INGR', r'\bcamphor\w*\b'), 'alumen': ('INGR', r'\balum\w*\b'),
    'opium': ('INGR', r'\bopi\w*\b'), 'crocus': ('INGR', r'\bcroc\w*\b'),
    'cinnamomum': ('INGR', r'\bcinnam\w*\b'), 'gummi': ('INGR', r'\bgumm\w*\b'),
    'cassia': ('INGR', r'\bcassi\w*\b'), 'mastix': ('INGR', r'\bmastic\w*\b'),
    'aloe': ('INGR', r'\balo[eë]\w*\b'), 'absinthium': ('INGR', r'\babsinth\w*\b'),
    'oculus': ('BODY', r'\bocul\w*\b'), 'caput': ('BODY', r'\bcapit\w*\b|\bcaput\b'),
    'stomachus': ('BODY', r'\bstomach\w*\b'), 'venter': ('BODY', r'\bventr\w*\b'),
    'matrix': ('BODY', r'\bmatri[cx]\w*\b'), 'pulmo': ('BODY', r'\bpulmon\w*\b'),
    'hepar': ('BODY', r'\bhepar\b|\bhepat\w*\b|\bjecur\w*\b'),
    'ren': ('BODY', r'\bren[eiu]\w*\b'), 'splen': ('BODY', r'\bsplen\w*\b'),
    'sanguis': ('BODY', r'\bsangu\w*\b'), 'urina': ('BODY', r'\burin\w*\b'),
    'dolor': ('DISEASE', r'\bdolor\w*\b'), 'tumor': ('DISEASE', r'\btumor\w*\b'),
    'febris': ('DISEASE', r'\bfebr\w*\b'), 'tussis': ('DISEASE', r'\btuss\w*\b'),
    'podagra': ('DISEASE', r'\bpodag\w*\b'), 'lepra': ('DISEASE', r'\blepr\w*\b'),
    'trita': ('VERB', r'\btrit\w*\b'), 'decoctio': ('VERB', r'\bdecoct\w*\b'),
    'bibere': ('VERB', r'\bbib\w*\b'), 'sumere': ('VERB', r'\bsum[epi]\w*\b'),
}

TARGETS = {
    'f48v':'ruta','f9v':'viola','f44v':'apium','f51v':'salvia',
    'f29r':'lactuca','f41r':'origanum','f37r':'mentha',
    'f41v':'coriandrum','f22r':'verbena','f28r':'aristolochia',
    'f5v':'malva','f45r':'atriplex','f3v':'elleborus',
}

# ================================================================
# STEP 1: Find best Collectio entry per plant
# ================================================================
print('='*70)
print('STEP 1 — Find Collectio chapters for Sherwood plants')
print('='*70)

plant_texts = {}  # plant → (entry_title, raw_text, ingredients)

for plant in set(TARGETS.values()):
    best = None
    best_score = 0

    for entry in collectio['entries']:
        title = entry.get('title', entry.get('name', '')).lower()
        raw = entry.get('raw_text', '')

        # Match plant name in title (strict: plant name must be a word)
        if not re.search(r'\b' + re.escape(plant[:4]) + r'\w*\b', title):
            continue

        # Score: prefer entries with more ingredients and longer text
        n_ingr = sum(1 for t in entry.get('tokens', []) if t.get('type') == 'INGR')
        score = len(raw) + n_ingr * 100

        if score > best_score and len(raw) >= 100:
            best_score = score
            # Combine ALL matching entries for this plant
            if best is None:
                best = {'title': title, 'raw': raw, 'ingrs': set()}
            else:
                best['raw'] += '\n' + raw

            for t in entry.get('tokens', []):
                if t.get('type') == 'INGR':
                    ref = t.get('ref', t.get('raw', '')).lower().replace('i_', '')
                    if len(ref) >= 3:
                        best['ingrs'].add(ref)

    if best and len(best['raw']) >= 100:
        plant_texts[plant] = best
        print(f'  {plant:>15s}: {len(best["raw"])} chars, {len(best["ingrs"])} ingredients')
    else:
        print(f'  {plant:>15s}: NOT FOUND (no entry with 100+ chars)')

# Also combine ALL entries mentioning each plant
print(f'\n  Combining all entries per plant...')
for plant in set(TARGETS.values()):
    if plant in plant_texts:
        continue
    combined_raw = ''
    combined_ingrs = set()
    for entry in collectio['entries']:
        raw = entry.get('raw_text', '')
        if plant[:4] in raw.lower() and len(raw) >= 50:
            combined_raw += '\n' + raw
            for t in entry.get('tokens', []):
                if t.get('type') == 'INGR':
                    ref = t.get('ref', t.get('raw', '')).lower().replace('i_', '')
                    if len(ref) >= 3:
                        combined_ingrs.add(ref)

    if len(combined_raw) >= 200:
        plant_texts[plant] = {'title': f'combined_{plant}', 'raw': combined_raw, 'ingrs': combined_ingrs}
        print(f'  {plant:>15s}: COMBINED {len(combined_raw)} chars, {len(combined_ingrs)} ingredients')

print(f'\n  Plants with Collectio text: {len(plant_texts)}/{len(set(TARGETS.values()))}')

# ================================================================
# STEP 2: Death match function
# ================================================================
def death_match_text(fid, text, source_name):
    """Run positional alignment between VMS folio and a Latin text."""
    text_lower = text.lower()
    text_len = max(len(text_lower), 1)

    # Find Latin words in text
    macer_words = []
    for concept, (ctype, pattern) in LATIN_WORDS.items():
        for m in re.finditer(pattern, text_lower):
            macer_words.append({'word': concept, 'type': ctype, 'position': m.start() / text_len})
    macer_words.sort(key=lambda x: x['position'])

    if len(macer_words) < 3:
        return None

    # VMS folio words
    folio = vms['folios'].get(fid)
    if not folio: return None
    all_words = []
    for block in folio['blocks']:
        for line in block['lines']:
            all_words.extend(line['words'])
    total_words = max(len(all_words), 1)

    # Find anchors
    cal = []
    for i, w in enumerate(all_words):
        eva = w['eva_primary']
        if eva in LOGO_SET: continue
        for root, latin in sorted(ANCHORS.items(), key=lambda x: -len(x[0])):
            if len(root) >= 3 and root in eva:
                for mw in macer_words:
                    if mw['word'] == latin or latin in mw['word'] or mw['word'] in latin:
                        cal.append({'vms': i/total_words, 'macer': mw['position']})
                        break
                break

    if not cal: return None
    offset = sum(c['vms']-c['macer'] for c in cal) / len(cal)

    # Match unknowns
    matches = []
    for i, w in enumerate(all_words):
        eva = w['eva_primary']
        root = (w.get('morphology') or {}).get('root', '')
        if eva in LOGO_SET or not root or len(root) < 3: continue
        if root in FUNCTIONAL or root in {'ke','ko','po','do'}: continue
        if root in ANCHORS: continue

        adj = (i/total_words) - offset
        best = None
        best_dist = 999
        for mw in macer_words:
            d = abs(adj - mw['position'])
            if d < best_dist:
                best_dist = d
                best = mw
        if best and best_dist < 0.10:
            matches.append({
                'root': root, 'macer_word': best['word'],
                'macer_type': best['type'], 'distance': round(best_dist, 4),
            })

    return {
        'n_anchors': len(cal), 'n_matches': len(matches),
        'offset': round(offset, 3), 'matches': matches,
    }

# ================================================================
# STEP 3: Run death match on all folios × Collectio
# ================================================================
print(f'\n{"="*70}')
print('STEP 3 — Death Match × Collectio')
print('='*70)

coll_mappings = defaultdict(Counter)
coll_results = []

for fid, plant in TARGETS.items():
    if plant not in plant_texts:
        continue
    text = plant_texts[plant]['raw']
    result = death_match_text(fid, text, 'COLLECTIO')
    if not result:
        print(f'  {fid:>6s} × {plant:>15s}: NO RESULT')
        continue

    coll_results.append({'fid': fid, 'plant': plant, **result})
    print(f'  {fid:>6s} × {plant:>15s}  anchors={result["n_anchors"]:>2d}  '
          f'matches={result["n_matches"]:>2d}')

    for m in result['matches']:
        coll_mappings[m['root']][(m['macer_word'], m['macer_type'])] += 1

# Cross-validate within Collectio
print(f'\n  Collectio cross-validated (2+ folios):')
coll_cv = []
for root, cands in sorted(coll_mappings.items(), key=lambda x: -max(x[1].values())):
    best_key, best_count = cands.most_common(1)[0]
    if best_count >= 2:
        word, wtype = best_key
        coll_cv.append({'root': root, 'word': word, 'type': wtype, 'count': best_count})
        print(f'    {root:>12s} = {word:>15s} [{wtype:>7s}] ({best_count} folios)')

# ================================================================
# STEP 4: Cross-validate Collectio × Macer
# ================================================================
print(f'\n{"="*70}')
print('STEP 4 — CROSS-CORPUS VALIDATION (Collectio × Macer)')
print('='*70)

# Load Macer death match results
macer_dm_path = os.path.join(RESULTS, 'death_match_auto_results.json')
macer_mappings = defaultdict(Counter)
if os.path.exists(macer_dm_path):
    with open(macer_dm_path, encoding='utf-8') as f:
        macer_dm = json.load(f)
    # Rebuild macer mappings from all results
    for r in macer_dm.get('history', []):
        for root, desc in r.get('new_mappings', {}).items():
            word = desc.split('(')[0]
            macer_mappings[root][word] += 1

# Also from batch results
batch_path = os.path.join(RESULTS, 'death_match_batch_results.json')
if os.path.exists(batch_path):
    with open(batch_path, encoding='utf-8') as f:
        batch = json.load(f)
    for cv in batch.get('cross_validated', []):
        macer_mappings[cv['root']][cv['word']] += cv['count']

# Find roots that appear in BOTH Collectio and Macer
multi_corpus = []
for cv in coll_cv:
    root = cv['root']
    coll_word = cv['word']

    if root in macer_mappings:
        macer_best = macer_mappings[root].most_common(1)[0][0]
        if macer_best == coll_word:
            multi_corpus.append({
                'root': root, 'word': coll_word, 'type': cv['type'],
                'coll_count': cv['count'],
                'macer_count': macer_mappings[root][coll_word],
                'agreement': 'BOTH_AGREE',
            })
        else:
            multi_corpus.append({
                'root': root, 'word': coll_word, 'type': cv['type'],
                'coll_count': cv['count'],
                'macer_word': macer_best,
                'agreement': 'DISAGREE',
            })

print(f'\n  Roots in both Collectio AND Macer death match:')
for mc in multi_corpus:
    if mc['agreement'] == 'BOTH_AGREE':
        print(f'    ★★★ {mc["root"]:>12s} = {mc["word"]:>15s} [{mc["type"]}]  '
              f'Coll={mc["coll_count"]}  Macer={mc["macer_count"]}  BOTH AGREE')
    else:
        print(f'    ✗   {mc["root"]:>12s}  Coll={mc["word"]}  Macer={mc["macer_word"]}  DISAGREE')

# Also: Collectio-only findings (not in Macer)
coll_only = [cv for cv in coll_cv if cv['root'] not in macer_mappings]
if coll_only:
    print(f'\n  Collectio-ONLY (new, not in Macer):')
    for cv in coll_only[:15]:
        print(f'    {cv["root"]:>12s} = {cv["word"]:>15s} [{cv["type"]}] ({cv["count"]} folios)')

# ================================================================
# SAVE
# ================================================================
output = {
    'n_plants_with_text': len(plant_texts),
    'n_coll_results': len(coll_results),
    'n_coll_cv': len(coll_cv),
    'n_multi_corpus': len(multi_corpus),
    'multi_corpus_agree': [mc for mc in multi_corpus if mc['agreement'] == 'BOTH_AGREE'],
    'coll_cv': coll_cv,
    'coll_only': [{'root': cv['root'], 'word': cv['word'], 'type': cv['type']} for cv in coll_only[:20]],
}

with open(os.path.join(RESULTS, 'death_match_multicorpus_results.json'), 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f'\n{"="*70}')
print(f'SUMMARY')
print(f'  Plants with Collectio text: {len(plant_texts)}')
print(f'  Collectio cross-validated: {len(coll_cv)}')
print(f'  Multi-corpus agreements: {sum(1 for mc in multi_corpus if mc["agreement"]=="BOTH_AGREE")}')
print(f'  Collectio-only new: {len(coll_only)}')
print(f'{"="*70}')
print(f'\nSaved death_match_multicorpus_results.json')
