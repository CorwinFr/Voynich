"""
ATTACK B — Word2Vec + Procrustes Alignment

Train word2vec on:
  - Latin medical corpus (1.7M tokens from RECIPE_DATASET)
  - VMS text (38K words from vms_structured.json)

Align the two embedding spaces using known logogram mappings as anchors.
For each unknown VMS word, find nearest Latin neighbors.

INDEPENDENT of K&A — purely distributional.
"""
import json, sys, io, os, re
import numpy as np
from collections import Counter
from gensim.models import Word2Vec
from scipy.linalg import orthogonal_procrustes

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.dirname(__file__)
VMS_PATH = os.path.join(BASE, '..', '..', 'vms', 'vms_structured.json')
RECIPE_DIR = os.path.join(BASE, '..', '..', '..', 'attacks', 'RECIPE_DATASET')
RESULTS = os.path.join(BASE, 'results')
os.makedirs(RESULTS, exist_ok=True)

# ================================================================
# LOGOGRAM ANCHORS (unique mappings only)
# ================================================================
LOGO_ANCHORS = {
    # EVA → Latin equivalent (must be unique on both sides)
    'o': 'ac',
    'l': 'se',
    'd': 'de',
    'r': 'recipe',
    'v': 'vel',
    'k': 'cum',
    'm': 'misce',
    'f': 'per',
    't': 'et',   # corrected: t → et (el was uncertain)
    'y': 'in',
    's': 'est',
    'p': 'usque',
    # Excluded: c, ch, sh → multiple map to cum, ambiguous
}

# ================================================================
# 1. BUILD LATIN CORPUS
# ================================================================
print('Building Latin corpus...')

latin_sentences = []
latin_vocab = Counter()

def clean_latin(text):
    """Clean Latin text into word tokens."""
    text = text.lower()
    text = re.sub(r'[^a-z\s]', ' ', text)
    words = text.split()
    return [w for w in words if len(w) >= 2]

for fname in sorted(os.listdir(RECIPE_DIR)):
    if not fname.startswith('S') or not fname.endswith('.json'):
        continue
    fpath = os.path.join(RECIPE_DIR, fname)
    with open(fpath, encoding='utf-8') as f:
        data = json.load(f)

    for entry in data.get('entries', []):
        # Method 1: use tokens if available
        tokens = entry.get('tokens', [])
        if tokens:
            words = [clean_latin(t['raw'])[0] for t in tokens
                     if clean_latin(t['raw'])]
            if len(words) >= 3:
                latin_sentences.append(words)
                latin_vocab.update(words)

        # Method 2: use raw_text
        raw = entry.get('raw_text', '')
        if raw and not tokens:
            words = clean_latin(raw)
            if len(words) >= 3:
                latin_sentences.append(words)
                latin_vocab.update(words)

        # Method 3: use content/description fields
        for field in ['content', 'description', 'text']:
            txt = entry.get(field, '')
            if txt and isinstance(txt, str) and not tokens and not raw:
                words = clean_latin(txt)
                if len(words) >= 3:
                    latin_sentences.append(words)
                    latin_vocab.update(words)

print(f'  Latin: {len(latin_sentences)} sentences, '
      f'{sum(len(s) for s in latin_sentences)} tokens, '
      f'{len(latin_vocab)} unique words')

# Check anchor presence in Latin corpus
print('\n  Anchor presence in Latin corpus:')
for eva, latin in LOGO_ANCHORS.items():
    count = latin_vocab.get(latin, 0)
    status = '✓' if count >= 5 else '✗ LOW' if count > 0 else '✗ ABSENT'
    print(f'    {eva:3s} → {latin:10s} : {count:6d} occurrences {status}')

# ================================================================
# 2. BUILD VMS CORPUS
# ================================================================
print('\nBuilding VMS corpus...')

with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)

vms_sentences = []
vms_vocab = Counter()

for fid, folio in vms['folios'].items():
    for block in folio['blocks']:
        words = [w['eva_primary'] for line in block['lines'] for w in line['words']]
        if len(words) >= 2:
            vms_sentences.append(words)
            vms_vocab.update(words)

print(f'  VMS: {len(vms_sentences)} sentences, '
      f'{sum(len(s) for s in vms_sentences)} tokens, '
      f'{len(vms_vocab)} unique words')

# Check anchor presence in VMS corpus
print('\n  Anchor presence in VMS corpus:')
usable_anchors = {}
for eva, latin in LOGO_ANCHORS.items():
    vms_count = vms_vocab.get(eva, 0)
    latin_count = latin_vocab.get(latin, 0)
    if vms_count >= 5 and latin_count >= 5:
        usable_anchors[eva] = latin
        status = '✓ USABLE'
    else:
        status = '✗ SKIP'
    print(f'    {eva:3s}({vms_count:5d}) → {latin:10s}({latin_count:6d}) {status}')

print(f'\n  Usable anchors: {len(usable_anchors)}')

# ================================================================
# 3. TRAIN WORD2VEC
# ================================================================
VEC_DIM = 50  # Keep low for small VMS corpus
WINDOW = 5
MIN_COUNT_LATIN = 3
MIN_COUNT_VMS = 2

print(f'\nTraining Word2Vec (dim={VEC_DIM}, window={WINDOW})...')

print('  Latin model...')
latin_model = Word2Vec(
    sentences=latin_sentences,
    vector_size=VEC_DIM,
    window=WINDOW,
    min_count=MIN_COUNT_LATIN,
    workers=4,
    epochs=50,
    sg=1,  # skip-gram (better for small data)
    seed=42,
)
print(f'    Vocabulary: {len(latin_model.wv)} words')

print('  VMS model...')
vms_model = Word2Vec(
    sentences=vms_sentences,
    vector_size=VEC_DIM,
    window=WINDOW,
    min_count=MIN_COUNT_VMS,
    workers=4,
    epochs=100,  # More epochs for smaller corpus
    sg=1,
    seed=42,
)
print(f'    Vocabulary: {len(vms_model.wv)} words')

# ================================================================
# 4. PROCRUSTES ALIGNMENT
# ================================================================
print('\nProcrustes alignment...')

# Build anchor matrices
anchor_vms = []
anchor_latin = []
anchor_pairs_used = []

for eva, latin in usable_anchors.items():
    if eva in vms_model.wv and latin in latin_model.wv:
        anchor_vms.append(vms_model.wv[eva])
        anchor_latin.append(latin_model.wv[latin])
        anchor_pairs_used.append((eva, latin))

anchor_vms = np.array(anchor_vms)
anchor_latin = np.array(anchor_latin)

print(f'  Anchors used: {len(anchor_pairs_used)}')
for eva, latin in anchor_pairs_used:
    print(f'    {eva} → {latin}')

if len(anchor_pairs_used) < 3:
    print('ERROR: Not enough anchors for Procrustes alignment!')
    sys.exit(1)

# Procrustes: find R such that VMS @ R ≈ Latin
# (minimize ||A @ R - B||)
R, scale = orthogonal_procrustes(anchor_vms, anchor_latin)
print(f'  Rotation matrix: {R.shape}, scale={scale:.4f}')

# Transform ALL VMS vectors into Latin space
vms_aligned = {}
for word in vms_model.wv.index_to_key:
    vms_aligned[word] = vms_model.wv[word] @ R

# ================================================================
# 5. QUALITY CHECK: anchor reconstruction error
# ================================================================
print('\nAnchor reconstruction error:')
total_err = 0
for (eva, latin), vms_vec, lat_vec in zip(anchor_pairs_used, anchor_vms, anchor_latin):
    aligned_vec = vms_vec @ R
    err = np.linalg.norm(aligned_vec - lat_vec)
    cos = np.dot(aligned_vec, lat_vec) / (np.linalg.norm(aligned_vec) * np.linalg.norm(lat_vec) + 1e-10)
    total_err += err
    print(f'  {eva:3s} → {latin:10s} : err={err:.4f}, cos={cos:.4f}')

avg_err = total_err / len(anchor_pairs_used)
print(f'  Average error: {avg_err:.4f}')

# ================================================================
# 6. NEAREST NEIGHBOR SEARCH
# ================================================================
print('\n' + '=' * 70)
print('NEAREST LATIN NEIGHBORS FOR VMS WORDS')
print('=' * 70)

# Build Latin vector matrix for fast NN search
latin_words = list(latin_model.wv.index_to_key)
latin_matrix = np.array([latin_model.wv[w] for w in latin_words])

# Normalize for cosine similarity
latin_norms = np.linalg.norm(latin_matrix, axis=1, keepdims=True) + 1e-10
latin_normalized = latin_matrix / latin_norms

def find_nearest_latin(eva_word, top_k=10):
    """Find nearest Latin words for an aligned VMS word."""
    if eva_word not in vms_aligned:
        return []
    vec = vms_aligned[eva_word]
    vec_norm = vec / (np.linalg.norm(vec) + 1e-10)
    sims = latin_normalized @ vec_norm
    top_idx = np.argsort(-sims)[:top_k]
    return [(latin_words[i], float(sims[i])) for i in top_idx]

# a) Most frequent VMS words (excluding logograms)
LOGOGRAMS = {'o','l','d','r','v','x','k','m','f','t','y','c','s','sh','p','air','ch','h'}
vms_freq = [(w, c) for w, c in vms_vocab.most_common(200) if w not in LOGOGRAMS and w in vms_aligned]

print('\n--- TOP 50 MOST FREQUENT VMS WORDS ---')
all_nn_results = {}

for eva, freq in vms_freq[:50]:
    neighbors = find_nearest_latin(eva, top_k=5)
    if not neighbors:
        continue
    nn_str = ', '.join(f'{w}({s:.3f})' for w, s in neighbors[:5])
    print(f'  {eva:15s} (x{freq:4d}) → {nn_str}')
    all_nn_results[eva] = {
        'frequency': freq,
        'neighbors': [{'latin': w, 'cosine': round(s, 4)} for w, s in neighbors],
    }

# b) VMS words from f103r specifically
print('\n--- f103r WORDS ---')
f103r_words = set()
for block in vms['folios']['f103r']['blocks']:
    for line in block['lines']:
        for w in line['words']:
            if w['eva_primary'] not in LOGOGRAMS:
                f103r_words.add(w['eva_primary'])

f103r_in_model = [w for w in f103r_words if w in vms_aligned]
print(f'\nf103r: {len(f103r_words)} unique words, {len(f103r_in_model)} in model')

for eva in sorted(f103r_in_model, key=lambda w: -vms_vocab.get(w, 0))[:30]:
    neighbors = find_nearest_latin(eva, top_k=5)
    if not neighbors:
        continue
    nn_str = ', '.join(f'{w}({s:.3f})' for w, s in neighbors[:5])
    print(f'  {eva:18s} (x{vms_vocab.get(eva,0):3d}) → {nn_str}')
    if eva not in all_nn_results:
        all_nn_results[eva] = {
            'frequency': vms_vocab.get(eva, 0),
            'neighbors': [{'latin': w, 'cosine': round(s, 4)} for w, s in neighbors],
        }

# ================================================================
# 7. CLUSTER ANALYSIS: do VMS word clusters correspond to Latin word clusters?
# ================================================================
print('\n' + '=' * 70)
print('CLUSTER ANALYSIS')
print('=' * 70)

# VMS words most similar to known ingredient-type Latin words
test_latins = ['rosa', 'aloe', 'piper', 'crocus', 'sal', 'mel', 'aqua',
               'oleum', 'vinum', 'cera', 'opium', 'mirra', 'camphora',
               'recipe', 'misce', 'tere', 'coque', 'adde',
               'ana', 'drachma', 'uncia', 'libra']

for latin_word in test_latins:
    if latin_word not in latin_model.wv:
        continue
    # Find VMS words closest to this Latin word (in aligned space)
    lat_vec = latin_model.wv[latin_word]
    lat_norm = lat_vec / (np.linalg.norm(lat_vec) + 1e-10)

    vms_words_list = list(vms_aligned.keys())
    vms_vecs = np.array([vms_aligned[w] for w in vms_words_list])
    vms_norms = np.linalg.norm(vms_vecs, axis=1, keepdims=True) + 1e-10
    vms_normed = vms_vecs / vms_norms

    sims = vms_normed @ lat_norm
    top_idx = np.argsort(-sims)[:5]
    top_vms = [(vms_words_list[i], float(sims[i])) for i in top_idx]

    nn_str = ', '.join(f'{w}({s:.3f})' for w, s in top_vms)
    print(f'  {latin_word:12s} ← {nn_str}')

# ================================================================
# 8. SAVE RESULTS
# ================================================================
results = {
    'params': {
        'vec_dim': VEC_DIM,
        'window': WINDOW,
        'min_count_latin': MIN_COUNT_LATIN,
        'min_count_vms': MIN_COUNT_VMS,
        'epochs_latin': 50,
        'epochs_vms': 100,
    },
    'corpus_stats': {
        'latin_sentences': len(latin_sentences),
        'latin_tokens': sum(len(s) for s in latin_sentences),
        'latin_vocab': len(latin_model.wv),
        'vms_sentences': len(vms_sentences),
        'vms_tokens': sum(len(s) for s in vms_sentences),
        'vms_vocab': len(vms_model.wv),
    },
    'anchors_used': anchor_pairs_used,
    'anchor_error': avg_err,
    'nn_results': all_nn_results,
}

with open(os.path.join(RESULTS, 'w2v_procrustes.json'), 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

# Save models
latin_model.save(os.path.join(RESULTS, 'latin_w2v.model'))
vms_model.save(os.path.join(RESULTS, 'vms_w2v.model'))

print('\nSaved w2v_procrustes.json, latin_w2v.model, vms_w2v.model')
