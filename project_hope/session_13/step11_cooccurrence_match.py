"""
STEP 11 — Co-occurrence graph matching.

Forget letters, forget lengths. Pure CODE matching.

For each recipe corpus (VMS and AN):
  1. Build co-occurrence matrix: which codes appear together in recipes
  2. Build frequency vector: how often each code appears
  3. Match VMS codes to AN codes by graph isomorphism:
     - Same frequency rank
     - Same co-occurrence neighbors

No length constraint, no letter matching. Pure structure.
"""
import json, sys, io, os
import numpy as np
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

VMS_PATH = os.path.join(os.path.dirname(__file__), '..', 'vms', 'vms_structured.json')
AN_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'attacks', 'RECIPE_DATASET', 'S01_AN.json')
RESULTS = os.path.join(os.path.dirname(__file__), 'results')

with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)
with open(AN_PATH, encoding='utf-8') as f:
    an = json.load(f)

LOGOS = {'o','l','d','r','v','x','k','m','f','t','y','c','s','sh','p','ch','air','h'}

# ================================================================
# 1. Build VMS co-occurrence graph (pharma only)
# ================================================================
print('Building VMS co-occurrence graph...')

vms_recipes = []  # each = set of root codes
vms_freq = Counter()

for fid, folio in vms['folios'].items():
    if folio['metadata']['section'] != 'pharma': continue
    for block in folio['blocks']:
        if not block.get('separator'): continue
        roots = set()
        for line in block['lines']:
            for w in line['words']:
                eva = w['eva_primary']
                if eva in LOGOS: continue
                morph = w.get('morphology') or {}
                root = morph.get('root', '')
                if root and len(root) >= 2:
                    roots.add(root)
                    vms_freq[root] += 1
        if len(roots) >= 2:
            vms_recipes.append(roots)

# Co-occurrence
vms_cooc = defaultdict(Counter)
for recipe in vms_recipes:
    for a in recipe:
        for b in recipe:
            if a < b:
                vms_cooc[a][b] += 1
                vms_cooc[b][a] += 1

# Top VMS codes
vms_top = [code for code, _ in vms_freq.most_common(50)]
print(f'  {len(vms_recipes)} recipes, {len(vms_freq)} unique roots')
print(f'  Top 10: {vms_top[:10]}')

# ================================================================
# 2. Build AN co-occurrence graph
# ================================================================
print('\nBuilding AN co-occurrence graph...')

an_recipes = []
an_freq = Counter()

for entry in an['entries']:
    ingrs = set()
    for tok in entry['tokens']:
        if tok['type'] == 'INGR' and tok.get('ref'):
            ref = tok['ref']
            ingrs.add(ref)
            an_freq[ref] += 1
    if len(ingrs) >= 2:
        an_recipes.append(ingrs)

an_cooc = defaultdict(Counter)
for recipe in an_recipes:
    for a in recipe:
        for b in recipe:
            if a < b:
                an_cooc[a][b] += 1
                an_cooc[b][a] += 1

an_top = [code for code, _ in an_freq.most_common(50)]
print(f'  {len(an_recipes)} recipes, {len(an_freq)} unique ingredients')
print(f'  Top 10: {an_top[:10]}')

# ================================================================
# 3. Build FINGERPRINTS — for each code, its co-occurrence profile
# ================================================================
print('\nBuilding fingerprints...')

def build_fingerprint(code, cooc, freq, top_n=20):
    """Build a normalized co-occurrence fingerprint for a code."""
    # Get top co-occurring codes, normalized by frequency
    neighbors = cooc.get(code, Counter())
    code_freq = freq[code]
    if code_freq == 0: return {}

    fp = {}
    for other, count in neighbors.most_common(top_n):
        # Normalize: P(other | code) = count / code_freq
        fp[other] = count / code_freq
    return fp

# For VMS and AN, build fingerprints of top 30 codes
vms_fps = {code: build_fingerprint(code, vms_cooc, vms_freq) for code in vms_top[:30]}
an_fps = {code: build_fingerprint(code, an_cooc, an_freq) for code in an_top[:30]}

# ================================================================
# 4. Match by RANK CORRELATION of co-occurrence profiles
# ================================================================
print('\nMatching by co-occurrence rank correlation...')

# For each VMS code, find the AN code with most similar co-occurrence SHAPE
# Shape = the RANK ORDER of top neighbors (not the actual codes)

def rank_profile(fp, top_codes):
    """Convert co-occurrence fingerprint to rank vector relative to top_codes."""
    return [fp.get(c, 0) for c in top_codes]

# Idea: if VMS code X co-occurs with VMS rank-1, rank-3, rank-7 most,
# and AN code Y co-occurs with AN rank-1, rank-3, rank-7 most,
# then X might = Y.

# For each VMS code, compute: which VMS RANK positions are its top neighbors?
vms_rank_profiles = {}
for code in vms_top[:30]:
    neighbors = vms_cooc.get(code, Counter())
    # Convert neighbors to RANK among vms_top
    profile = []
    for rank, top_code in enumerate(vms_top[:30]):
        profile.append(neighbors.get(top_code, 0) / max(vms_freq[code], 1))
    vms_rank_profiles[code] = profile

an_rank_profiles = {}
for code in an_top[:30]:
    neighbors = an_cooc.get(code, Counter())
    profile = []
    for rank, top_code in enumerate(an_top[:30]):
        profile.append(neighbors.get(top_code, 0) / max(an_freq[code], 1))
    an_rank_profiles[code] = profile

# Compute cosine similarity between all VMS and AN rank profiles
print(f'\n  Matching {len(vms_rank_profiles)} VMS × {len(an_rank_profiles)} AN codes')

matches = []
for v_code, v_prof in vms_rank_profiles.items():
    v_arr = np.array(v_prof)
    v_norm = np.linalg.norm(v_arr)
    if v_norm < 0.001: continue

    for a_code, a_prof in an_rank_profiles.items():
        a_arr = np.array(a_prof)
        a_norm = np.linalg.norm(a_arr)
        if a_norm < 0.001: continue

        cos = float(np.dot(v_arr, a_arr) / (v_norm * a_norm))
        # Also factor in frequency rank similarity
        v_rank = vms_top.index(v_code)
        a_rank = an_top.index(a_code)
        rank_sim = 1.0 - abs(v_rank - a_rank) / 30

        combined = cos * 0.7 + rank_sim * 0.3

        matches.append({
            'vms': v_code,
            'an': a_code,
            'cosine': round(cos, 3),
            'rank_sim': round(rank_sim, 3),
            'combined': round(combined, 3),
            'vms_freq': vms_freq[v_code],
            'an_freq': an_freq[a_code],
            'vms_rank': v_rank,
            'an_rank': a_rank,
        })

matches.sort(key=lambda x: -x['combined'])

# ================================================================
# 5. BEST MATCH PER VMS CODE
# ================================================================
print(f'\n{"="*70}')
print('BEST MATCH PER VMS CODE (co-occurrence + frequency)')
print('=' * 70)

seen_vms = set()
best_per_vms = []

for m in matches:
    if m['vms'] in seen_vms: continue
    seen_vms.add(m['vms'])
    best_per_vms.append(m)

print(f'\n  {"VMS root":>12s} {"rk":>3s} {"freq":>5s} → {"AN ingredient":>20s} {"rk":>3s} {"freq":>5s} '
      f'{"cos":>5s} {"rank":>5s} {"comb":>5s}')
print('  ' + '-' * 70)

for m in best_per_vms[:30]:
    an_name = m['an'].replace('I_','').replace('P_','')
    print(f'  {m["vms"]:>12s} #{m["vms_rank"]:>2d} {m["vms_freq"]:>5d} → '
          f'{an_name:>20s} #{m["an_rank"]:>2d} {m["an_freq"]:>5d} '
          f'{m["cosine"]:>5.3f} {m["rank_sim"]:>5.3f} {m["combined"]:>5.3f}')

# ================================================================
# 6. CONSISTENCY CHECK — do the mappings form a coherent set?
# ================================================================
print(f'\n{"="*70}')
print('CONSISTENCY CHECK')
print('=' * 70)

# If VMS_A → AN_X and VMS_B → AN_Y, then:
# VMS_A and VMS_B should co-occur roughly as much as AN_X and AN_Y

mapping = {m['vms']: m['an'] for m in best_per_vms[:15]}

consistent = 0
inconsistent = 0
checks = 0

for v1, a1 in mapping.items():
    for v2, a2 in mapping.items():
        if v1 >= v2: continue
        checks += 1

        vms_cooc_val = vms_cooc[v1].get(v2, 0)
        an_cooc_val = an_cooc[a1].get(a2, 0)

        # Normalize
        vms_max = max(vms_cooc[v1].values()) if vms_cooc[v1] else 1
        an_max = max(an_cooc[a1].values()) if an_cooc[a1] else 1

        vms_norm = vms_cooc_val / max(vms_max, 1)
        an_norm = an_cooc_val / max(an_max, 1)

        if abs(vms_norm - an_norm) < 0.3:
            consistent += 1
        else:
            inconsistent += 1

print(f'\n  Checked {checks} pairs')
print(f'  Consistent: {consistent} ({consistent*100//max(checks,1)}%)')
print(f'  Inconsistent: {inconsistent} ({inconsistent*100//max(checks,1)}%)')

# ================================================================
# 7. SPECIFIC QUESTIONS
# ================================================================
print(f'\n{"="*70}')
print('SPECIFIC QUESTIONS')
print('=' * 70)

# Q1: What maps to aqua (most frequent AN ingredient)?
aqua_matches = [(m['vms'], m['combined'], m['vms_freq'], m['vms_rank'])
                for m in matches if m['an'] == 'I_aqua']
aqua_matches.sort(key=lambda x: -x[1])
print(f'\n  What maps to AQUA (water)?')
for v, score, freq, rank in aqua_matches[:5]:
    print(f'    {v:>12s} (rank #{rank}, freq={freq}) score={score:.3f}')

# Q2: What maps to mel (honey)?
mel_matches = [(m['vms'], m['combined'], m['vms_freq'], m['vms_rank'])
               for m in matches if m['an'] == 'I_mel']
mel_matches.sort(key=lambda x: -x[1])
print(f'\n  What maps to MEL (honey)?')
for v, score, freq, rank in mel_matches[:5]:
    print(f'    {v:>12s} (rank #{rank}, freq={freq}) score={score:.3f}')

# Q3: What maps to rosa?
rosa_matches = [(m['vms'], m['combined'], m['vms_freq'], m['vms_rank'])
                for m in matches if m['an'] == 'I_rosa']
rosa_matches.sort(key=lambda x: -x[1])
print(f'\n  What maps to ROSA (rose)?')
for v, score, freq, rank in rosa_matches[:5]:
    print(f'    {v:>12s} (rank #{rank}, freq={freq}) score={score:.3f}')

# Q4: What maps to cinnamomum?
cin_matches = [(m['vms'], m['combined'], m['vms_freq'], m['vms_rank'])
               for m in matches if m['an'] == 'I_cinnamomum']
cin_matches.sort(key=lambda x: -x[1])
print(f'\n  What maps to CINNAMOMUM (cinnamon)?')
for v, score, freq, rank in cin_matches[:5]:
    print(f'    {v:>12s} (rank #{rank}, freq={freq}) score={score:.3f}')

# Save
results = {
    'best_mappings': best_per_vms[:30],
    'consistency': {'checked': checks, 'consistent': consistent,
                    'inconsistent': inconsistent},
}
with open(os.path.join(RESULTS, 'cooccurrence_match.json'), 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print('\nSaved cooccurrence_match.json')
