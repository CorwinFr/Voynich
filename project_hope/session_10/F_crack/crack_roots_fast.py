"""
CRACK ROOTS FAST — Vectorized version.
"""
import json, sys, io, os
import numpy as np
from collections import Counter, defaultdict
from gensim.models import Word2Vec
from scipy.linalg import orthogonal_procrustes

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.dirname(__file__)
VMS_PATH = os.path.join(BASE, '..', '..', 'vms', 'vms_structured.json')
AN_PATH = os.path.join(BASE, '..', '..', '..', 'attacks', 'RECIPE_DATASET', 'S01_AN.json')
CROSSREF_PATH = os.path.join(BASE, '..', '..', 'session_09', 'results', 'plant_crossref_complete.json')
LATIN_MODEL = os.path.join(BASE, '..', 'B_gpu_embeddings', 'results', 'latin_w2v.model')
VMS_MODEL = os.path.join(BASE, '..', 'B_gpu_embeddings', 'results', 'vms_w2v.model')
RESULTS = os.path.join(BASE, 'results')

print('Loading...')
with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)
with open(AN_PATH, encoding='utf-8') as f:
    an = json.load(f)
with open(CROSSREF_PATH, encoding='utf-8') as f:
    crossref = json.load(f)

latin_model = Word2Vec.load(LATIN_MODEL)
vms_model = Word2Vec.load(VMS_MODEL)

# Procrustes
LOGOS = {'o':'ac','l':'se','d':'de','r':'recipe','v':'vel',
         'k':'cum','m':'misce','f':'per','t':'et','y':'in','s':'est','p':'usque'}
avms, alat = [], []
for e, l in LOGOS.items():
    if e in vms_model.wv and l in latin_model.wv:
        avms.append(vms_model.wv[e]); alat.append(latin_model.wv[l])
R, _ = orthogonal_procrustes(np.array(avms), np.array(alat))

LOGOGRAMS = set(LOGOS.keys()) | {'x','c','sh','ch','air','h'}

# ================================================================
# 1. EVA root frequencies in pharma
# ================================================================
root_freq = Counter()
root_herbal = Counter()
root_words = defaultdict(set)

for fid, folio in vms['folios'].items():
    section = folio['metadata']['section']
    for b in folio['blocks']:
        for line in b['lines']:
            for w in line['words']:
                eva = w['eva_primary']
                if eva in LOGOGRAMS: continue
                root = (w.get('morphology') or {}).get('root', '')
                if not root: continue
                root_words[root].add(eva)
                if section == 'pharma': root_freq[root] += 1
                if section in ('herbal_a','herbal_b'): root_herbal[root] += 1

# Top pharma roots (>= 5)
top_roots = [(r, c) for r, c in root_freq.most_common() if c >= 5]
print(f'{len(top_roots)} roots with >=5 pharma occurrences')

# ================================================================
# 2. AN ingredient frequencies
# ================================================================
an_freq = Counter()
for entry in an['entries']:
    for tok in entry['tokens']:
        if tok['type'] == 'INGR':
            an_freq[tok['raw'].lower()] += 1

top_an = an_freq.most_common(100)
an_names = [n for n, _ in top_an]
print(f'{len(an_names)} AN ingredients for matching')

# ================================================================
# 3. W2V similarity matrix (vectorized)
# ================================================================
print('Computing w2v similarity matrix...')

# Get EVA vectors (aligned)
eva_vecs = {}
for root, _ in top_roots:
    for eva_word in root_words[root]:
        if eva_word in vms_model.wv:
            eva_vecs[root] = vms_model.wv[eva_word] @ R
            break

# Get Latin vectors
lat_vecs = {}
for name in an_names:
    if name in latin_model.wv:
        lat_vecs[name] = latin_model.wv[name]

# Build matrices
roots_with_vec = [r for r, _ in top_roots if r in eva_vecs]
latins_with_vec = [n for n in an_names if n in lat_vecs]

if roots_with_vec and latins_with_vec:
    E = np.array([eva_vecs[r] for r in roots_with_vec])
    L = np.array([lat_vecs[n] for n in latins_with_vec])
    E_norm = E / (np.linalg.norm(E, axis=1, keepdims=True) + 1e-10)
    L_norm = L / (np.linalg.norm(L, axis=1, keepdims=True) + 1e-10)
    SIM = E_norm @ L_norm.T  # shape: (n_roots, n_latins)
    print(f'  Similarity matrix: {SIM.shape}')

# ================================================================
# 4. Combined scoring
# ================================================================
print('\nScoring...')

results = []

for i, root in enumerate(roots_with_vec):
    freq_rank = i  # already sorted by frequency
    root_count = root_freq[root]
    root_len = len(root)
    is_herbal = root_herbal[root] > 0

    for j, latin in enumerate(latins_with_vec):
        # W2V score (strongest signal)
        w2v = float(SIM[i, j])

        # Frequency rank correlation
        freq_score = max(0, 1.0 - abs(i - j) / 50) * 0.15

        # Length ratio
        len_ratio = root_len / max(len(latin), 1)
        len_score = (1.0 - abs(len_ratio - 0.5) * 2) * 0.10 if 0.3 <= len_ratio <= 0.8 else 0

        # Herbal bonus (if root appears in herbal = plant)
        herbal_bonus = 0.05 if is_herbal else 0

        total = w2v * 0.50 + freq_score + len_score + herbal_bonus

        results.append((root, latin, total, w2v, root_count, an_freq[latin]))

# Sort by score
results.sort(key=lambda x: -x[2])

# ================================================================
# 5. Best match per root
# ================================================================
print('\n' + '=' * 70)
print('BEST MATCH PER EVA ROOT (top 40)')
print('=' * 70)

seen_roots = set()
best_per_root = []

for root, latin, score, w2v, rc, ac in results:
    if root in seen_roots: continue
    seen_roots.add(root)
    best_per_root.append((root, latin, score, w2v, rc, ac))
    if len(best_per_root) >= 40: break

# Also get runner-up for each
root_all = defaultdict(list)
for root, latin, score, w2v, rc, ac in results:
    root_all[root].append((latin, score, w2v))

# Crossref herbal info
herbal_info = {}
for entry in crossref['crossref']:
    herbal_info[entry['root']] = entry['folio']

for root, latin, score, w2v, rc, ac in best_per_root:
    hf = herbal_info.get(root, '')
    hf_str = f' [herbal:{hf}]' if hf else ''

    # Runner-up
    cands = root_all[root]
    runner = cands[1] if len(cands) > 1 else ('', 0, 0)
    margin = score - runner[1]

    print(f'  {root:12s} → {latin:20s} score={score:.3f} w2v={w2v:.3f} '
          f'margin={margin:.3f} EVA:x{rc} AN:x{ac}{hf_str}')
    # Show top 3
    for lat2, sc2, w2 in cands[:3]:
        if lat2 != latin:
            print(f'    alt: {lat2:20s} score={sc2:.3f} w2v={w2:.3f}')
            break

# ================================================================
# 6. Herbal roots specifically
# ================================================================
print('\n' + '=' * 70)
print('HERBAL ROOTS — These ARE plant names')
print('=' * 70)

for root, folio in sorted(herbal_info.items(), key=lambda x: -root_freq.get(x[0], 0)):
    if root not in eva_vecs: continue
    cands = root_all.get(root, [])
    if not cands: continue
    latin, score, w2v = cands[0]
    print(f'  {root:12s} ({folio}) → {latin:20s} score={score:.3f} w2v={w2v:.3f} '
          f'pharma:x{root_freq[root]}')

# ================================================================
# 7. DECODE f103r recipe 1 with best matches
# ================================================================
print('\n' + '=' * 70)
print('f103r RECIPE 1 — DECODED')
print('=' * 70)

best_map = {root: latin for root, latin, _, _, _, _ in best_per_root}
LOGO_DECODE = {
    'o':'ac','l':'se','d':'de','r':'RECIPE','v':'vel',
    'k':'cum','m':'MISCE','f':'per','t':'et',
    'y':'in','s':'est','sh':'ci','p':'usque','ch':'cum',
}

f103r = vms['folios']['f103r']
block1 = f103r['blocks'][0]
words = [w for line in block1['lines'] for w in line['words']]

for w in words:
    eva = w['eva_primary']
    morph = w.get('morphology') or {}
    root = morph.get('root', '')
    suffix = morph.get('suffix', '') or ''
    ic = morph.get('i_count')

    if eva in LOGO_DECODE:
        decoded = f'[{LOGO_DECODE[eva]}]'
    elif ic is not None:
        decoded = f'<DOSE:i{ic}>'
    elif root in best_map:
        decoded = f'*{best_map[root]}*'
        if suffix:
            decoded += f'(-{suffix})'
    else:
        decoded = eva

    print(f'  {eva:18s} → {decoded}')

# Save
save = {
    'best_per_root': [
        {'root': r, 'latin': l, 'score': round(s, 4), 'w2v': round(w, 4),
         'pharma_freq': rc, 'an_freq': ac}
        for r, l, s, w, rc, ac in best_per_root
    ],
}
with open(os.path.join(RESULTS, 'crack_roots.json'), 'w', encoding='utf-8') as f:
    json.dump(save, f, indent=2, ensure_ascii=False)

print('\nSaved crack_roots.json')
