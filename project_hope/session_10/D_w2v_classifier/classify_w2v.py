"""
W2V CENTROID CLASSIFIER — Classify every VMS word by distributional semantics.

Define Latin centroid clusters for 6 categories:
  VERB, GRAM, INGR, DOSE, TEMPORAL, PREP

For each VMS word (aligned to Latin space via Procrustes), compute cosine
similarity to each centroid. Assign the category with highest similarity.

Apply to f103r recipes for full semantic annotation.
"""
import json, sys, io, os
import numpy as np
from collections import Counter, defaultdict
from gensim.models import Word2Vec

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.dirname(__file__)
VMS_PATH = os.path.join(BASE, '..', '..', 'vms', 'vms_structured.json')
LATIN_MODEL_PATH = os.path.join(BASE, '..', 'B_gpu_embeddings', 'results', 'latin_w2v.model')
VMS_MODEL_PATH = os.path.join(BASE, '..', 'B_gpu_embeddings', 'results', 'vms_w2v.model')
INGR_PATH = os.path.join(BASE, '..', 'A_ingredients', 'results', 'f103r_ingredients_v2.json')
RESULTS = os.path.join(BASE, 'results')
os.makedirs(RESULTS, exist_ok=True)

# ================================================================
# CATEGORY DEFINITIONS — Latin seed words for each centroid
# ================================================================
CATEGORIES = {
    'VERB': [
        'recipe', 'misce', 'tere', 'coque', 'adde', 'fiat', 'cola',
        'dissolve', 'pone', 'fac', 'accipe', 'contere', 'commisce',
        'confice', 'munde', 'decoque', 'solve', 'distempera',
        'incorpora', 'infunde', 'bulliat', 'coletur', 'ponatur',
        'terantur', 'misceantur', 'addatur', 'imponatur',
    ],
    'GRAM': [
        'et', 'in', 'cum', 'de', 'vel', 'est', 'per', 'se',
        'ad', 'non', 'sed', 'sic', 'si', 'aut', 'que', 'hoc',
        'inde', 'item', 'quod', 'eius', 'autem', 'ergo',
    ],
    'INGR': [
        'rosa', 'piper', 'aloe', 'crocus', 'sal', 'mel', 'opium',
        'mirra', 'camphora', 'cassia', 'cinnamomum', 'zingiber',
        'galanga', 'nardus', 'absinthium', 'feniculum', 'anetum',
        'petroselinum', 'ruta', 'salvia', 'origanum', 'cera',
        'oleum', 'vinum', 'aqua', 'acetum', 'mastix', 'thus',
        'galbanum', 'opopanax', 'bdellium', 'ammoniacum',
        'aloes', 'opii', 'mirre', 'ciperi', 'croci', 'piperis',
        'rosarum', 'gariofilorum', 'cinamomi', 'masticis',
        'absintii', 'feniculi', 'petroselini', 'cassie',
    ],
    'DOSE': [
        'ana', 'drachma', 'uncia', 'libra', 'semis', 'scrupulum',
        'manipulum', 'pugillum', 'quantum', 'pondus',
        'drachmas', 'uncias', 'libras', 'dragma',
    ],
    'TEMPORAL': [
        'mane', 'nocte', 'die', 'hora', 'sero', 'vespere',
        'diebus', 'noctibus', 'horis', 'continuis', 'donec',
        'postea', 'ante', 'post', 'semper', 'quotidie',
    ],
    'PREP_FORM': [
        'unguentum', 'electuarium', 'siropi', 'sirupus', 'pilulae',
        'emplastrum', 'pulvis', 'confectio', 'cataplasma',
        'ptisanum', 'potio', 'decoctio', 'infusio', 'collyrium',
        'trochiscus', 'oximel', 'conditum',
    ],
}

LOGOGRAMS = {
    'o': 'ac', 'l': 'se', 'd': 'de', 'r': 'recipe', 'v': 'vel',
    'x': 'crux', 'k': 'cum', 'm': 'misce', 'f': 'per', 't': 'et',
    'y': 'in', 'c': 'cum', 's': 'est', 'sh': 'ci', 'p': 'usque',
    'ch': 'cum', 'air': 'air', 'h': '(h)',
}

# ================================================================
# 1. Load models
# ================================================================
print('Loading models...')
latin_model = Word2Vec.load(LATIN_MODEL_PATH)
vms_model = Word2Vec.load(VMS_MODEL_PATH)

with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)

# Load ingredient tags from Attack A
with open(INGR_PATH, encoding='utf-8') as f:
    ingr_data = json.load(f)

print(f'  Latin vocab: {len(latin_model.wv)}')
print(f'  VMS vocab: {len(vms_model.wv)}')

# ================================================================
# 2. Rebuild Procrustes rotation (same as Attack B)
# ================================================================
from scipy.linalg import orthogonal_procrustes

LOGO_ANCHORS = {
    'o': 'ac', 'l': 'se', 'd': 'de', 'r': 'recipe', 'v': 'vel',
    'k': 'cum', 'm': 'misce', 'f': 'per', 't': 'et',
    'y': 'in', 's': 'est', 'p': 'usque',
}

anchor_vms, anchor_latin = [], []
for eva, latin in LOGO_ANCHORS.items():
    if eva in vms_model.wv and latin in latin_model.wv:
        anchor_vms.append(vms_model.wv[eva])
        anchor_latin.append(latin_model.wv[latin])

R, _ = orthogonal_procrustes(np.array(anchor_vms), np.array(anchor_latin))

# Transform all VMS vectors
vms_aligned = {}
for word in vms_model.wv.index_to_key:
    vms_aligned[word] = vms_model.wv[word] @ R

print(f'  Procrustes rotation computed, {len(vms_aligned)} VMS words aligned')

# ================================================================
# 3. Build centroids for each category
# ================================================================
print('\nBuilding category centroids...')

centroids = {}
centroid_words = {}

for cat, seeds in CATEGORIES.items():
    vecs = []
    found = []
    for word in seeds:
        if word in latin_model.wv:
            vecs.append(latin_model.wv[word])
            found.append(word)
    if vecs:
        centroid = np.mean(vecs, axis=0)
        centroid = centroid / (np.linalg.norm(centroid) + 1e-10)
        centroids[cat] = centroid
        centroid_words[cat] = found
        print(f'  {cat:12s}: {len(found)}/{len(seeds)} seed words found → centroid built')
    else:
        print(f'  {cat:12s}: NO seed words found!')

# ================================================================
# 4. Classify each VMS word
# ================================================================
print('\nClassifying VMS words...')

def classify_word(eva):
    """Classify a VMS word by cosine similarity to category centroids."""
    if eva not in vms_aligned:
        return None, {}

    vec = vms_aligned[eva]
    vec_norm = vec / (np.linalg.norm(vec) + 1e-10)

    scores = {}
    for cat, centroid in centroids.items():
        scores[cat] = float(np.dot(vec_norm, centroid))

    best_cat = max(scores, key=scores.get)
    return best_cat, scores

# Classify ALL VMS words (for global analysis)
all_classifications = {}
for eva in vms_aligned:
    cat, scores = classify_word(eva)
    if cat:
        all_classifications[eva] = {
            'category': cat,
            'scores': {k: round(v, 4) for k, v in scores.items()},
            'confidence': round(scores[cat] - sorted(scores.values())[-2], 4),  # margin
        }

# Category distribution
cat_dist = Counter(c['category'] for c in all_classifications.values())
print(f'\nGlobal VMS word classification ({len(all_classifications)} words):')
for cat, n in cat_dist.most_common():
    print(f'  {cat:12s}: {n:5d} ({n*100//len(all_classifications)}%)')

# ================================================================
# 5. Apply to f103r — annotate each recipe
# ================================================================
print('\n' + '=' * 70)
print('f103r — FULL SEMANTIC ANNOTATION')
print('=' * 70)

# Build ingredient tag lookup from Attack A
ingr_tags = {}
for recipe in ingr_data['recipes']:
    for tw in recipe['tagged']:
        if tw['tag'] == 'INGR':
            ingr_tags[(recipe['id'], tw['pos'])] = tw

f103r = vms['folios']['f103r']
annotated_recipes = []
role_counts = Counter()

# Color-coded tags for display
TAG_SYMBOLS = {
    'LOGO': 'L',
    'DOSE_MORPH': 'D',  # from morphology (i_count)
    'INGR_XREF': '★',  # from herbal crossref
    'VERB': 'V',
    'GRAM': 'G',
    'INGR': 'I',
    'DOSE': 'Q',
    'TEMPORAL': 'T',
    'PREP_FORM': 'P',
}

for b in f103r['blocks']:
    recipe_id = b['block_id']
    words = [w for line in b['lines'] for w in line['words']]

    print(f'\n{"─"*70}')
    print(f'{recipe_id} ({len(words)} words)')
    print(f'{"─"*70}')

    tagged = []
    for i, w in enumerate(words):
        eva = w['eva_primary']
        morph = w.get('morphology', {})
        ic = morph.get('i_count')

        # Priority 1: logogram (known)
        if eva in LOGOGRAMS:
            role = 'LOGO'
            detail = LOGOGRAMS[eva]

        # Priority 2: dose by morphology (i_count)
        elif ic is not None:
            role = 'DOSE_MORPH'
            detail = f'i{ic}'

        # Priority 3: ingredient by crossref (Attack A)
        elif (recipe_id, i) in ingr_tags:
            role = 'INGR_XREF'
            detail = ingr_tags[(recipe_id, i)]['label']

        # Priority 4: w2v classification
        elif eva in all_classifications:
            cl = all_classifications[eva]
            role = cl['category']
            detail = f'{cl["scores"][role]:.2f}'

        else:
            role = '?'
            detail = ''

        role_counts[role] += 1
        sym = TAG_SYMBOLS.get(role, '?')
        tagged.append({
            'pos': i,
            'eva': eva,
            'role': role,
            'detail': detail,
            'sym': sym,
        })

    # Print compact: EVA with role symbol above
    line1 = []  # symbols
    line2 = []  # EVA words
    for tw in tagged:
        width = max(len(tw['eva']), 3)
        line1.append(f'{tw["sym"]:>{width}s}')
        line2.append(f'{tw["eva"]:>{width}s}')

    # Print in chunks of 10
    chunk = 10
    for start in range(0, len(tagged), chunk):
        end = min(start + chunk, len(tagged))
        print('  ' + ' '.join(line1[start:end]))
        print('  ' + ' '.join(line2[start:end]))

        # Detail line for non-UNK
        details = []
        for tw in tagged[start:end]:
            if tw['role'] not in ('?',):
                details.append(f'{tw["eva"]}={tw["role"]}')
        if details:
            print('  → ' + ', '.join(details))
        print()

    # Summary
    recipe_roles = Counter(tw['role'] for tw in tagged)
    summary_parts = []
    for role in ['LOGO', 'DOSE_MORPH', 'INGR_XREF', 'VERB', 'GRAM', 'INGR', 'DOSE', 'TEMPORAL', 'PREP_FORM', '?']:
        n = recipe_roles.get(role, 0)
        if n:
            summary_parts.append(f'{TAG_SYMBOLS.get(role, "?")}:{n}')
    print(f'  SUMMARY: {" | ".join(summary_parts)}')

    annotated_recipes.append({
        'id': recipe_id,
        'n_words': len(words),
        'tagged': tagged,
        'role_counts': dict(recipe_roles),
    })

# ================================================================
# 6. Global analysis
# ================================================================
print('\n' + '=' * 70)
print('GLOBAL ROLE DISTRIBUTION IN f103r')
print('=' * 70)

total = sum(role_counts.values())
for role, n in role_counts.most_common():
    pct = n * 100 // total
    bar = '█' * (pct // 2)
    print(f'  {role:12s}: {n:4d} ({pct:2d}%) {bar}')

# Ratio analysis
n_verb = role_counts.get('VERB', 0) + role_counts.get('LOGO', 0)
n_ingr_total = role_counts.get('INGR', 0) + role_counts.get('INGR_XREF', 0)
n_dose_total = role_counts.get('DOSE', 0) + role_counts.get('DOSE_MORPH', 0)
n_gram = role_counts.get('GRAM', 0)
n_temporal = role_counts.get('TEMPORAL', 0)

print(f'\n  FUNCTIONAL (VERB+LOGO): {n_verb} ({n_verb*100//total}%)')
print(f'  INGREDIENTS (INGR+XREF): {n_ingr_total} ({n_ingr_total*100//total}%)')
print(f'  DOSAGES (DOSE+MORPH): {n_dose_total} ({n_dose_total*100//total}%)')
print(f'  GRAMMAR: {n_gram} ({n_gram*100//total}%)')
print(f'  TEMPORAL: {n_temporal} ({n_temporal*100//total}%)')

print(f'\n  AN reference: VERB ~4%, INGR ~50%, DOSE ~12%, GRAM ~25%')
print(f'  VMS observed: VERB {n_verb*100//total}%, INGR {n_ingr_total*100//total}%, '
      f'DOSE {n_dose_total*100//total}%, GRAM {n_gram*100//total}%, '
      f'TEMPORAL {n_temporal*100//total}%')

# ================================================================
# 7. Most confident classifications (high margin)
# ================================================================
print('\n' + '=' * 70)
print('MOST CONFIDENT W2V CLASSIFICATIONS (top margin)')
print('=' * 70)

# Filter to words that appear in f103r
f103r_evas = set()
for b in f103r['blocks']:
    for line in b['lines']:
        for w in line['words']:
            f103r_evas.add(w['eva_primary'])

f103r_classified = {eva: cl for eva, cl in all_classifications.items()
                    if eva in f103r_evas and cl['category'] not in ('GRAM',)}

for cat in ['VERB', 'INGR', 'TEMPORAL', 'PREP_FORM', 'DOSE']:
    words_in_cat = [(eva, cl) for eva, cl in f103r_classified.items()
                    if cl['category'] == cat]
    words_in_cat.sort(key=lambda x: -x[1]['confidence'])

    if not words_in_cat:
        continue
    print(f'\n  {cat}:')
    for eva, cl in words_in_cat[:10]:
        score = cl['scores'][cat]
        margin = cl['confidence']
        print(f'    {eva:18s} score={score:.3f} margin={margin:.3f}')

# ================================================================
# 8. VERB candidates — most important for recipe structure
# ================================================================
print('\n' + '=' * 70)
print('VERB CANDIDATES IN f103r (w2v distributional)')
print('=' * 70)

verb_candidates = [(eva, cl) for eva, cl in f103r_classified.items()
                   if cl['category'] == 'VERB']
verb_candidates.sort(key=lambda x: -x[1]['scores']['VERB'])

vms_vocab = Counter()
for fid, folio in vms['folios'].items():
    for block in folio['blocks']:
        for line in block['lines']:
            for w in line['words']:
                vms_vocab[w['eva_primary']] += 1

for eva, cl in verb_candidates[:20]:
    freq = vms_vocab.get(eva, 0)
    verb_score = cl['scores']['VERB']
    # Find nearest Latin verbs
    if eva in vms_aligned:
        vec = vms_aligned[eva]
        vec_norm = vec / (np.linalg.norm(vec) + 1e-10)
        # Distance to each verb seed
        verb_dists = []
        for vw in CATEGORIES['VERB']:
            if vw in latin_model.wv:
                lv = latin_model.wv[vw]
                lv_norm = lv / (np.linalg.norm(lv) + 1e-10)
                cos = float(np.dot(vec_norm, lv_norm))
                verb_dists.append((vw, cos))
        verb_dists.sort(key=lambda x: -x[1])
        top3 = ', '.join(f'{w}({s:.2f})' for w, s in verb_dists[:3])
    else:
        top3 = ''

    print(f'  {eva:18s} (x{freq:4d}) verb={verb_score:.3f} → {top3}')

# ================================================================
# Save results
# ================================================================
results = {
    'categories': {cat: words for cat, words in centroid_words.items()},
    'global_distribution': dict(cat_dist),
    'f103r_role_counts': dict(role_counts),
    'f103r_recipes': annotated_recipes,
    'f103r_ratios': {
        'verb_logo': n_verb,
        'ingr_total': n_ingr_total,
        'dose_total': n_dose_total,
        'gram': n_gram,
        'temporal': n_temporal,
    },
    'verb_candidates': [
        {'eva': eva, 'freq': vms_vocab.get(eva, 0),
         'verb_score': round(cl['scores']['VERB'], 4),
         'confidence': round(cl['confidence'], 4)}
        for eva, cl in verb_candidates[:30]
    ],
    'all_f103r_classifications': {
        eva: cl for eva, cl in all_classifications.items() if eva in f103r_evas
    },
}

with open(os.path.join(RESULTS, 'w2v_classifier.json'), 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print('\nSaved w2v_classifier.json')
