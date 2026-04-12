"""
Cross-validation: Compare w2v classifications with Attack A ingredient tags.
Identify where they agree/disagree, and refine the classification.

Key questions:
1. Are w2v DOSE words actually doses or misclassified ingredients?
2. Do w2v VERB words match known verb patterns?
3. Can we identify TEMPORAL words as a distinct class?
"""
import json, sys, io, os
import numpy as np
from collections import Counter, defaultdict
from gensim.models import Word2Vec
from scipy.linalg import orthogonal_procrustes

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.dirname(__file__)
VMS_PATH = os.path.join(BASE, '..', '..', 'vms', 'vms_structured.json')
LATIN_MODEL_PATH = os.path.join(BASE, '..', 'B_gpu_embeddings', 'results', 'latin_w2v.model')
VMS_MODEL_PATH = os.path.join(BASE, '..', 'B_gpu_embeddings', 'results', 'vms_w2v.model')
CLASSIFIER_PATH = os.path.join(BASE, 'results', 'w2v_classifier.json')
RESULTS = os.path.join(BASE, 'results')

# Load data
with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)
with open(CLASSIFIER_PATH, encoding='utf-8') as f:
    classifier = json.load(f)

latin_model = Word2Vec.load(LATIN_MODEL_PATH)
vms_model = Word2Vec.load(VMS_MODEL_PATH)

# Rebuild Procrustes
LOGO_ANCHORS = {
    'o': 'ac', 'l': 'se', 'd': 'de', 'r': 'recipe', 'v': 'vel',
    'k': 'cum', 'm': 'misce', 'f': 'per', 't': 'et',
    'y': 'in', 's': 'est', 'p': 'usque',
}
avms, alat = [], []
for e, l in LOGO_ANCHORS.items():
    if e in vms_model.wv and l in latin_model.wv:
        avms.append(vms_model.wv[e])
        alat.append(latin_model.wv[l])
R, _ = orthogonal_procrustes(np.array(avms), np.array(alat))
vms_aligned = {w: vms_model.wv[w] @ R for w in vms_model.wv.index_to_key}

# ================================================================
# 1. POSITIONAL ANALYSIS: where do each role appear in recipes?
# ================================================================
print('=' * 70)
print('POSITIONAL ANALYSIS: where do roles appear in recipes?')
print('=' * 70)

# For each role, compute relative position distribution
role_positions = defaultdict(list)

f103r = vms['folios']['f103r']
for recipe in classifier['f103r_recipes']:
    n = recipe['n_words']
    for tw in recipe['tagged']:
        rel_pos = tw['pos'] / max(n - 1, 1)
        role_positions[tw['role']].append(rel_pos)

for role in ['VERB', 'LOGO', 'INGR_XREF', 'INGR', 'DOSE_MORPH', 'DOSE', 'GRAM', 'TEMPORAL', 'PREP_FORM']:
    positions = role_positions.get(role, [])
    if not positions:
        continue
    avg = sum(positions) / len(positions)
    # Position quartiles
    positions.sort()
    q1 = positions[len(positions)//4] if len(positions) >= 4 else positions[0]
    q3 = positions[3*len(positions)//4] if len(positions) >= 4 else positions[-1]
    # Start vs end bias
    n_start = sum(1 for p in positions if p < 0.25)
    n_end = sum(1 for p in positions if p > 0.75)
    n_mid = len(positions) - n_start - n_end

    print(f'  {role:12s}: n={len(positions):3d} avg={avg:.2f} '
          f'Q1={q1:.2f} Q3={q3:.2f} | start={n_start} mid={n_mid} end={n_end}')

# ================================================================
# 2. SUFFIX ANALYSIS: do w2v categories correlate with EVA suffixes?
# ================================================================
print('\n' + '=' * 70)
print('SUFFIX vs W2V CATEGORY')
print('=' * 70)

suffix_by_role = defaultdict(Counter)
for recipe in classifier['f103r_recipes']:
    for tw in recipe['tagged']:
        eva = tw['eva']
        # Extract suffix from morphology
        for block in f103r['blocks']:
            if block['block_id'] != recipe['id']:
                continue
            words = [w for line in block['lines'] for w in line['words']]
            if tw['pos'] < len(words):
                morph = words[tw['pos']].get('morphology', {})
                suffix = morph.get('suffix', '')
                if suffix:
                    suffix_by_role[tw['role']][suffix] += 1
                else:
                    suffix_by_role[tw['role']]['(none)'] += 1

for role in ['VERB', 'INGR_XREF', 'INGR', 'DOSE', 'GRAM', 'TEMPORAL', 'PREP_FORM']:
    suffixes = suffix_by_role.get(role, Counter())
    if not suffixes:
        continue
    top3 = ', '.join(f'{s}({c})' for s, c in suffixes.most_common(5))
    print(f'  {role:12s}: {top3}')

# ================================================================
# 3. VMS INTERNAL NEIGHBORS: do w2v categories cluster in VMS space too?
# ================================================================
print('\n' + '=' * 70)
print('VMS INTERNAL CLUSTERING: are w2v categories coherent in VMS space?')
print('=' * 70)

# For each classified f103r word, check its VMS neighbors (pre-alignment)
categories_vms = defaultdict(list)
f103r_evas = set()
for recipe in classifier['f103r_recipes']:
    for tw in recipe['tagged']:
        if tw['role'] not in ('LOGO', 'DOSE_MORPH', '?'):
            categories_vms[tw['role']].append(tw['eva'])
            f103r_evas.add(tw['eva'])

for cat in ['VERB', 'INGR_XREF', 'INGR', 'DOSE', 'GRAM', 'TEMPORAL']:
    words_in_cat = [w for w in categories_vms[cat] if w in vms_model.wv]
    if len(words_in_cat) < 3:
        continue

    # Compute average pairwise cosine within category (VMS space, pre-alignment)
    vecs = [vms_model.wv[w] for w in set(words_in_cat)]
    if len(vecs) < 2:
        continue

    total_cos = 0
    n_pairs = 0
    for i in range(len(vecs)):
        for j in range(i+1, len(vecs)):
            cos = float(np.dot(vecs[i], vecs[j]) /
                       (np.linalg.norm(vecs[i]) * np.linalg.norm(vecs[j]) + 1e-10))
            total_cos += cos
            n_pairs += 1

    avg_cos = total_cos / max(n_pairs, 1)
    print(f'  {cat:12s}: {len(set(words_in_cat))} unique words, '
          f'avg VMS internal cos={avg_cos:.3f} ({"TIGHT" if avg_cos > 0.3 else "LOOSE"})')

# ================================================================
# 4. RECIPE PATTERN ANALYSIS with full annotation
# ================================================================
print('\n' + '=' * 70)
print('RECIPE PATTERNS (full annotation)')
print('=' * 70)

# Use compact symbols
SYM = {
    'LOGO': 'L', 'DOSE_MORPH': 'D', 'INGR_XREF': '★',
    'VERB': 'V', 'GRAM': 'G', 'INGR': 'I',
    'DOSE': 'Q', 'TEMPORAL': 'T', 'PREP_FORM': 'P', '?': '·',
}

for recipe in classifier['f103r_recipes']:
    rid = recipe['id']
    pattern = ''.join(SYM.get(tw['role'], '?') for tw in recipe['tagged'])

    # Look for VERB-INGR sequences (recipe structure)
    vi_count = sum(1 for i in range(len(pattern)-1)
                   if pattern[i] in 'VL' and pattern[i+1] in 'I★')
    # Look for INGR-DOSE sequences
    id_count = sum(1 for i in range(len(pattern)-1)
                   if pattern[i] in 'I★' and pattern[i+1] in 'DQ')

    print(f'  {rid}: {pattern}')
    print(f'    V→I:{vi_count} I→D:{id_count}')

# ================================================================
# 5. IDENTIFY VERBS: combine position + w2v + suffix
# ================================================================
print('\n' + '=' * 70)
print('VERB IDENTIFICATION (multi-signal)')
print('=' * 70)

# A word is likely a VERB if:
# 1. w2v classifies it as VERB
# 2. It tends to appear early in recipes or after doses
# 3. Its suffix is -al, -ar, -am (verb-like) or no suffix

verb_signals = defaultdict(lambda: {'w2v': 0, 'position': 0, 'suffix': 0, 'total': 0})

for recipe in classifier['f103r_recipes']:
    n = recipe['n_words']
    for i, tw in enumerate(recipe['tagged']):
        eva = tw['eva']
        if eva in ({'o','l','d','r','v','x','k','m','f','t','y','c','s','sh','p','ch','air','h'}):
            continue
        if tw['role'] == 'DOSE_MORPH':
            continue

        signals = verb_signals[eva]

        # w2v signal
        if tw['role'] == 'VERB':
            signals['w2v'] += 1
        signals['total'] += 1

        # Position signal: first 3 words
        rel_pos = tw['pos'] / max(n - 1, 1)
        if rel_pos < 0.15:
            signals['position'] += 1

# Find words with multiple verb signals
print(f'\n{"EVA":<18s} {"w2v":>4s} {"pos":>4s} {"tot":>4s}  {"score":>5s}')
print('-' * 45)

verb_scores = []
for eva, sig in verb_signals.items():
    if sig['total'] < 2:
        continue
    w2v_pct = sig['w2v'] / max(sig['total'], 1)
    pos_pct = sig['position'] / max(sig['total'], 1)
    score = w2v_pct * 0.6 + pos_pct * 0.4
    if score > 0.3:
        verb_scores.append((eva, sig, score))

verb_scores.sort(key=lambda x: -x[2])
for eva, sig, score in verb_scores[:20]:
    print(f'  {eva:<18s} {sig["w2v"]:4d} {sig["position"]:4d} {sig["total"]:4d}  {score:5.2f}')

# ================================================================
# 6. FINAL ANNOTATED RECIPE EXAMPLE (B01, most ingredients)
# ================================================================
print('\n' + '=' * 70)
print('ANNOTATED RECIPE f103r_B01 — WORD BY WORD')
print('=' * 70)

recipe_b01 = classifier['f103r_recipes'][0]
b01_block = f103r['blocks'][0]
b01_words = [w for line in b01_block['lines'] for w in line['words']]

for tw in recipe_b01['tagged']:
    eva = tw['eva']
    role = tw['role']
    detail = tw.get('detail', '')

    # Get nearest Latin for this word
    latin_nn = ''
    if eva in vms_aligned:
        vec = vms_aligned[eva]
        vec_norm = vec / (np.linalg.norm(vec) + 1e-10)

        lat_words = list(latin_model.wv.index_to_key)
        lat_vecs = np.array([latin_model.wv[w] for w in lat_words])
        lat_norms = np.linalg.norm(lat_vecs, axis=1, keepdims=True) + 1e-10
        sims = (lat_vecs / lat_norms) @ vec_norm
        top3_idx = np.argsort(-sims)[:3]
        latin_nn = ', '.join(f'{lat_words[i]}({sims[i]:.2f})' for i in top3_idx)

    sym = SYM.get(role, '?')
    print(f'  [{tw["pos"]:2d}] {sym} {eva:18s} {role:12s} {detail:20s} → {latin_nn}')

# Save cross-validation results
results = {
    'role_positions': {role: {
        'count': len(positions),
        'avg': round(sum(positions)/max(len(positions),1), 3),
    } for role, positions in role_positions.items()},
    'suffix_by_role': {role: dict(suffixes) for role, suffixes in suffix_by_role.items()},
    'verb_candidates': [
        {'eva': eva, 'w2v_count': sig['w2v'], 'pos_count': sig['position'],
         'total': sig['total'], 'score': round(score, 3)}
        for eva, sig, score in verb_scores[:30]
    ],
}
with open(os.path.join(RESULTS, 'crossval_analysis.json'), 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print('\nSaved crossval_analysis.json')
