"""
CRACK ROOTS — Map EVA roots to Latin ingredient names.

Model: VMS = personal Tironian system
  - Gallows (p/t/k/f) = verb openers (Recipe, Accipe, Fiat, Misce)
  - Root = abbreviated ingredient name
  - Suffix = grammatical case marker

Signals for matching:
  1. FREQUENCY: rank of EVA root in pharma ↔ rank of ingredient in AN
  2. LENGTH: EVA root length ↔ Latin name length (abbreviation ratio)
  3. W2V: distributional neighbors
  4. CO-OCCURRENCE: which roots appear together ↔ which AN ingredients co-occur
  5. HERBAL PAGE: each herbal page = 1 plant, root = that plant's identifier
  6. SECTION PROFILE: which sections the root appears in (herbal/pharma/balnea)
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

# ================================================================
# LOAD EVERYTHING
# ================================================================
print('Loading data...')
with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)
with open(AN_PATH, encoding='utf-8') as f:
    an = json.load(f)
with open(CROSSREF_PATH, encoding='utf-8') as f:
    crossref = json.load(f)

latin_model = Word2Vec.load(LATIN_MODEL)
vms_model = Word2Vec.load(VMS_MODEL)

# Procrustes
LOGO_ANCHORS = {
    'o':'ac','l':'se','d':'de','r':'recipe','v':'vel',
    'k':'cum','m':'misce','f':'per','t':'et',
    'y':'in','s':'est','p':'usque',
}
avms, alat = [], []
for e, l in LOGO_ANCHORS.items():
    if e in vms_model.wv and l in latin_model.wv:
        avms.append(vms_model.wv[e])
        alat.append(latin_model.wv[l])
R, _ = orthogonal_procrustes(np.array(avms), np.array(alat))
vms_aligned = {w: vms_model.wv[w] @ R for w in vms_model.wv.index_to_key}

# Latin ingredient vectors
latin_words = list(latin_model.wv.index_to_key)
latin_matrix = np.array([latin_model.wv[w] for w in latin_words])
latin_norms = np.linalg.norm(latin_matrix, axis=1, keepdims=True) + 1e-10
latin_normalized = latin_matrix / latin_norms

LOGOGRAMS = {'o','l','d','r','v','x','k','m','f','t','y','c','s','sh','p','air','ch','h'}

# ================================================================
# 1. BUILD EVA ROOT PROFILES
# ================================================================
print('Building EVA root profiles...')

# Extract all roots from pharma with their contexts
root_profiles = defaultdict(lambda: {
    'count': 0, 'pharma': 0, 'herbal': 0, 'balnea': 0,
    'words': [], 'suffixes': Counter(), 'neighbors': [],
    'positions': [],  # relative position in recipe
    'co_roots': Counter(),  # which other roots appear in same recipe
})

for fid, folio in vms['folios'].items():
    section = folio['metadata']['section']
    for block in folio['blocks']:
        words = [w for line in block['lines'] for w in line['words']]
        roots_in_block = []
        for i, w in enumerate(words):
            eva = w['eva_primary']
            if eva in LOGOGRAMS: continue
            morph = w.get('morphology') or {}
            root = morph.get('root', '')
            suffix = morph.get('suffix', '') or ''
            if not root: continue

            root_profiles[root]['count'] += 1
            root_profiles[root]['words'].append(eva)
            root_profiles[root]['suffixes'][suffix] += 1
            if section == 'pharma': root_profiles[root]['pharma'] += 1
            elif section in ('herbal_a','herbal_b'): root_profiles[root]['herbal'] += 1
            elif section == 'balnea': root_profiles[root]['balnea'] += 1

            if block.get('separator') and len(words) > 1:
                root_profiles[root]['positions'].append(i / len(words))

            roots_in_block.append(root)

        # Co-occurrence
        for r in set(roots_in_block):
            for r2 in set(roots_in_block):
                if r != r2:
                    root_profiles[r]['co_roots'][r2] += 1

# Filter: keep roots with >= 5 occurrences in pharma
pharma_roots = {r: p for r, p in root_profiles.items()
                if p['pharma'] >= 5}
print(f'  {len(pharma_roots)} roots with >=5 pharma occurrences')

# ================================================================
# 2. BUILD AN INGREDIENT PROFILES
# ================================================================
print('Building AN ingredient profiles...')

an_ingredients = defaultdict(lambda: {
    'count': 0, 'recipes': [], 'co_ingr': Counter(),
    'positions': [], 'latin': '',
})

for entry in an['entries']:
    ingr_in_recipe = []
    for tok in entry['tokens']:
        if tok['type'] != 'INGR': continue
        name = tok['raw'].lower()
        ref = tok.get('ref', '')
        an_ingredients[name]['count'] += 1
        an_ingredients[name]['latin'] = name
        an_ingredients[name]['recipes'].append(entry['id'])
        if 'pos' in tok:
            an_ingredients[name]['positions'].append(tok['pos'] / max(entry['summary']['n_tokens'], 1))
        ingr_in_recipe.append(name)

    for ing in set(ingr_in_recipe):
        for ing2 in set(ingr_in_recipe):
            if ing != ing2:
                an_ingredients[ing]['co_ingr'][ing2] += 1

# Top AN ingredients by frequency
an_sorted = sorted(an_ingredients.items(), key=lambda x: -x[1]['count'])
print(f'  {len(an_sorted)} unique AN ingredients')

# ================================================================
# 3. MULTI-SIGNAL MATCHING
# ================================================================
print('\nMulti-signal matching...')

# For each pharma root, compute match score against each AN ingredient
candidates = {}

for root, profile in sorted(pharma_roots.items(), key=lambda x: -x[1]['pharma']):
    scores = []

    # Find representative EVA word for w2v
    eva_words = list(set(profile['words']))
    eva_in_model = [w for w in eva_words if w in vms_aligned]

    for an_name, an_prof in an_sorted[:100]:  # Top 100 AN ingredients
        score = 0.0
        signals = []

        # SIGNAL 1: Frequency rank correlation
        root_rank = sorted(pharma_roots.keys(),
                          key=lambda r: -pharma_roots[r]['pharma']).index(root)
        an_rank = [n for n, _ in an_sorted].index(an_name)
        rank_diff = abs(root_rank - an_rank)
        freq_score = max(0, 1.0 - rank_diff / 50)
        score += freq_score * 0.15
        if freq_score > 0.5:
            signals.append(f'freq={freq_score:.2f}')

        # SIGNAL 2: Length ratio (EVA root should be shorter than Latin)
        # Tironian abbreviation: keep ~40-60% of letters
        len_ratio = len(root) / max(len(an_name), 1)
        if 0.3 <= len_ratio <= 0.8:
            len_score = 1.0 - abs(len_ratio - 0.5) * 2
        else:
            len_score = 0.0
        score += len_score * 0.10
        if len_score > 0.5:
            signals.append(f'len={len_ratio:.2f}')

        # SIGNAL 3: W2V distributional similarity
        w2v_score = 0.0
        if eva_in_model and an_name in latin_model.wv:
            lat_vec = latin_model.wv[an_name]
            lat_norm = lat_vec / (np.linalg.norm(lat_vec) + 1e-10)
            best_cos = -1
            for ew in eva_in_model[:3]:
                vec = vms_aligned[ew]
                vec_norm = vec / (np.linalg.norm(vec) + 1e-10)
                cos = float(np.dot(vec_norm, lat_norm))
                if cos > best_cos:
                    best_cos = cos
            w2v_score = max(0, best_cos)
            score += w2v_score * 0.35
            if w2v_score > 0.3:
                signals.append(f'w2v={w2v_score:.2f}')

        # SIGNAL 4: Co-occurrence pattern similarity
        # Do the co-roots of this EVA root match the co-ingredients of this AN ingredient?
        if profile['co_roots'] and an_prof['co_ingr']:
            # Jaccard-like: how many top co-roots also appear as top matches?
            # (indirect — we can't compare directly, but frequency profiles)
            top_co_roots = [r for r, _ in profile['co_roots'].most_common(5)]
            top_co_ingr = [n for n, _ in an_prof['co_ingr'].most_common(5)]
            # Co-occurrence diversity match
            co_div_vms = len(profile['co_roots'])
            co_div_an = len(an_prof['co_ingr'])
            div_ratio = min(co_div_vms, co_div_an) / max(co_div_vms, co_div_an, 1)
            score += div_ratio * 0.10

        # SIGNAL 5: Position in recipe
        if profile['positions'] and an_prof['positions']:
            avg_pos_vms = sum(profile['positions']) / len(profile['positions'])
            avg_pos_an = sum(an_prof['positions']) / len(an_prof['positions'])
            pos_score = 1.0 - abs(avg_pos_vms - avg_pos_an)
            score += pos_score * 0.10
            if pos_score > 0.7:
                signals.append(f'pos={pos_score:.2f}')

        # SIGNAL 6: Section profile (herbal presence = plant ingredient)
        if profile['herbal'] > 0 and an_name in [
            n for n, p in an_sorted if any(
                'I_' in (t.get('ref','') or '') for e in an['entries'] for t in e['tokens']
                if t['raw'].lower() == n and t['type'] == 'INGR'
            )
        ]:
            score += 0.10
            signals.append('herbal+')

        scores.append((an_name, score, signals))

    scores.sort(key=lambda x: -x[1])
    candidates[root] = scores[:10]

# ================================================================
# 4. RESULTS
# ================================================================
print('\n' + '=' * 70)
print('TOP CANDIDATES FOR EACH EVA ROOT')
print('=' * 70)

# Sort roots by pharma frequency
for root in sorted(pharma_roots.keys(), key=lambda r: -pharma_roots[r]['pharma'])[:40]:
    profile = pharma_roots[root]
    top5 = candidates.get(root, [])[:5]
    if not top5: continue

    # Herbal folio if known
    herbal_folio = ''
    for entry in crossref['crossref']:
        if entry['root'] == root:
            herbal_folio = f' (herbal {entry["folio"]})'
            break

    print(f'\n  {root:12s} pharma={profile["pharma"]:3d} herbal={profile["herbal"]:3d}{herbal_folio}')
    print(f'    Suffixes: {dict(profile["suffixes"].most_common(3))}')
    for an_name, score, signals in top5:
        sig = ', '.join(signals) if signals else ''
        print(f'    → {an_name:20s} score={score:.3f}  {sig}')

# ================================================================
# 5. HIGH-CONFIDENCE MATCHES
# ================================================================
print('\n' + '=' * 70)
print('HIGH-CONFIDENCE MATCHES (score > 0.40)')
print('=' * 70)

high_conf = []
for root, cands in candidates.items():
    if not cands: continue
    best_name, best_score, best_sig = cands[0]
    second_score = cands[1][1] if len(cands) > 1 else 0
    margin = best_score - second_score

    if best_score > 0.40:
        high_conf.append((root, best_name, best_score, margin, best_sig,
                         pharma_roots[root]['pharma']))

high_conf.sort(key=lambda x: -x[2])
for root, latin, score, margin, sig, freq in high_conf:
    sig_str = ', '.join(sig) if sig else ''
    print(f'  {root:12s} → {latin:20s} score={score:.3f} margin={margin:.3f} '
          f'freq={freq:3d} [{sig_str}]')

# ================================================================
# Save
# ================================================================
results = {
    'n_roots': len(pharma_roots),
    'n_ingredients': len(an_sorted),
    'high_confidence': [
        {'root': r, 'latin': l, 'score': round(s, 4), 'margin': round(m, 4),
         'pharma_freq': f}
        for r, l, s, m, _, f in high_conf
    ],
    'all_candidates': {
        root: [{'latin': n, 'score': round(s, 4)} for n, s, _ in cands[:5]]
        for root, cands in candidates.items()
    },
}
with open(os.path.join(RESULTS, 'crack_roots.json'), 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f'\n{len(high_conf)} high-confidence matches')
print('Saved crack_roots.json')
