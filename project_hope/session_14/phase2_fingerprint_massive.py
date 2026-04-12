"""
PHASE 2 — Massive fingerprint matching with 100 anchors.

For each root: binary fingerprint across 100 anchor folios.
For each corpus ingredient: binary fingerprint across matched chapters.
Match identical or near-identical fingerprints.
"""
import json, sys, io, os
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

VMS_PATH = os.path.join(os.path.dirname(__file__), '..', 'vms', 'vms_structured.json')
ANCHORS_PATH = os.path.join(os.path.dirname(__file__), 'extended_anchors.json')
RESULTS = os.path.dirname(__file__)

with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)
with open(ANCHORS_PATH, encoding='utf-8') as f:
    anchor_data = json.load(f)

LOGOS = {'o','l','d','r','v','x','k','m','f','t','y','c','s','sh','p','ch','air','h'}

anchors = anchor_data['anchors']
# Only use anchors that have ingredients from corpus
anchors_with_ingr = [a for a in anchors if a['n_ingredients'] >= 2]
# Also include all anchors for root fingerprint (presence/absence doesn't need ingredients)
all_anchor_folios = [a['folio'] for a in anchors]

print(f'Total anchors: {len(anchors)}')
print(f'Anchors with 2+ ingredients: {len(anchors_with_ingr)}')

# ================================================================
# Build root fingerprints (presence in each anchor folio)
# ================================================================
print('\nBuilding root fingerprints...')

def get_roots(fid):
    if fid not in vms['folios']: return set()
    roots = set()
    for block in vms['folios'][fid]['blocks']:
        for line in block['lines']:
            for w in line['words']:
                eva = w['eva_primary']
                if eva in LOGOS: continue
                root = (w.get('morphology') or {}).get('root', '')
                if root and len(root) >= 2:
                    roots.add(root)
    return roots

folio_root_sets = {fid: get_roots(fid) for fid in all_anchor_folios}

# Global root frequency
root_global = Counter()
for fid, folio in vms['folios'].items():
    for block in folio['blocks']:
        for line in block['lines']:
            for w in line['words']:
                root = (w.get('morphology') or {}).get('root', '')
                if root and len(root) >= 2:
                    root_global[root] += 1

# For fingerprinting, use only anchors WITH ingredients (for matching)
fp_folios = [a['folio'] for a in anchors_with_ingr]
n_fp = len(fp_folios)

# Root fingerprint: for each root, 1 if present in folio, 0 if not
root_fps = {}
for root in root_global:
    if root_global[root] < 3: continue  # skip very rare
    fp = tuple(1 if root in folio_root_sets.get(fid, set()) else 0 for fid in fp_folios)
    if sum(fp) >= 2:  # present in at least 2 anchor folios
        root_fps[root] = fp

print(f'  Root fingerprints ({n_fp}-bit): {len(root_fps)}')

# ================================================================
# Build ingredient fingerprints (mentioned in each anchor's corpus entry)
# ================================================================
print('Building ingredient fingerprints...')

ingr_fps = defaultdict(lambda: [0] * n_fp)

for i, anchor in enumerate(anchors_with_ingr):
    for ingr in anchor['ingredients']:
        ingr_fps[ingr][i] = 1

ingr_fps = {ingr: tuple(fp) for ingr, fp in ingr_fps.items() if sum(fp) >= 2}

print(f'  Ingredient fingerprints: {len(ingr_fps)}')

# ================================================================
# MATCH: find roots and ingredients with identical fingerprints
# ================================================================
print(f'\n{"="*70}')
print('EXACT FINGERPRINT MATCHES')
print('=' * 70)

# Group by fingerprint
fp_to_roots = defaultdict(list)
fp_to_ingr = defaultdict(list)

for root, fp in root_fps.items():
    fp_to_roots[fp].append(root)
for ingr, fp in ingr_fps.items():
    fp_to_ingr[fp].append(ingr)

exact_matches = []
for fp in set(fp_to_roots.keys()) & set(fp_to_ingr.keys()):
    roots = fp_to_roots[fp]
    ingrs = fp_to_ingr[fp]
    n_present = sum(fp)

    exact_matches.append({
        'fingerprint': fp,
        'n_present': n_present,
        'roots': roots,
        'ingredients': ingrs,
        'n_roots': len(roots),
        'n_ingr': len(ingrs),
        'strength': 'UNIQUE' if len(roots) == 1 and len(ingrs) == 1 else
                    'STRONG' if len(roots) <= 2 and len(ingrs) <= 2 else
                    'MEDIUM' if len(roots) <= 5 and len(ingrs) <= 5 else 'WEAK',
    })

exact_matches.sort(key=lambda x: (-x['n_present'], x['n_roots'] + x['n_ingr']))

print(f'\n  {len(exact_matches)} exact fingerprint matches')

unique = [m for m in exact_matches if m['strength'] == 'UNIQUE']
strong = [m for m in exact_matches if m['strength'] == 'STRONG']
medium = [m for m in exact_matches if m['strength'] == 'MEDIUM']

print(f'  UNIQUE (1 root ↔ 1 ingr): {len(unique)}')
print(f'  STRONG (≤2 ↔ ≤2):         {len(strong)}')
print(f'  MEDIUM (≤5 ↔ ≤5):         {len(medium)}')

print(f'\n  ★★★ UNIQUE MATCHES:')
for m in unique:
    root = m['roots'][0]
    ingr = m['ingredients'][0]
    freq = root_global.get(root, 0)
    folios = [fp_folios[i] for i, v in enumerate(m['fingerprint']) if v]
    print(f'    {root:>12s} = {ingr:>25s} ({m["n_present"]} folios, freq={freq}) {folios}')

print(f'\n  ★★ STRONG MATCHES:')
for m in strong[:20]:
    folios = [fp_folios[i] for i, v in enumerate(m['fingerprint']) if v]
    print(f'    {m["roots"]} = {m["ingredients"]} ({m["n_present"]} folios) {folios[:4]}...')

# ================================================================
# HAMMING DISTANCE 1 — fuzzy matches
# ================================================================
print(f'\n{"="*70}')
print('FUZZY MATCHES (Hamming distance = 1)')
print('=' * 70)

fuzzy_matches = []

for root, r_fp in root_fps.items():
    for ingr, i_fp in ingr_fps.items():
        # Hamming distance
        dist = sum(a != b for a, b in zip(r_fp, i_fp))
        if dist == 1:
            n_present_root = sum(r_fp)
            n_present_ingr = sum(i_fp)
            if n_present_root >= 3 and n_present_ingr >= 3:
                fuzzy_matches.append({
                    'root': root,
                    'ingredient': ingr,
                    'hamming': 1,
                    'root_present': n_present_root,
                    'ingr_present': n_present_ingr,
                    'root_freq': root_global.get(root, 0),
                })

fuzzy_matches.sort(key=lambda x: -(x['root_present'] + x['ingr_present']))

print(f'  {len(fuzzy_matches)} fuzzy matches (Hamming=1)')
for m in fuzzy_matches[:20]:
    print(f'    {m["root"]:>12s} ≈ {m["ingredient"]:>25s} '
          f'(root:{m["root_present"]}folios, ingr:{m["ingr_present"]}folios, freq={m["root_freq"]})')

# ================================================================
# COMPILE ALL MAPPINGS
# ================================================================
print(f'\n{"="*70}')
print('ALL DECODED MAPPINGS')
print('=' * 70)

all_mappings = {}

# From exact unique
for m in unique:
    root = m['roots'][0]
    ingr = m['ingredients'][0]
    all_mappings[root] = {'latin': ingr, 'confidence': 'confirmed', 'method': 'fingerprint_exact_unique',
                          'n_folios': m['n_present'], 'freq': root_global.get(root, 0)}

# From exact strong (take first ingredient if 1 root)
for m in strong:
    if len(m['roots']) == 1:
        root = m['roots'][0]
        if root not in all_mappings:
            all_mappings[root] = {'latin': '/'.join(m['ingredients']),
                                  'confidence': 'probable', 'method': 'fingerprint_exact_strong',
                                  'n_folios': m['n_present']}

# From plant name first words
for root, data in anchor_data['plant_name_mappings'].items():
    if root not in all_mappings:
        all_mappings[root] = {'latin': data['latin'], 'confidence': 'probable',
                              'method': 'first_word_plant_name', 'folio': data['folio']}

# From fuzzy (add as possible)
for m in fuzzy_matches[:30]:
    root = m['root']
    if root not in all_mappings:
        all_mappings[root] = {'latin': m['ingredient'], 'confidence': 'possible',
                              'method': 'fingerprint_fuzzy_hamming1'}

total_confirmed = sum(1 for m in all_mappings.values() if m['confidence'] == 'confirmed')
total_probable = sum(1 for m in all_mappings.values() if m['confidence'] == 'probable')
total_possible = sum(1 for m in all_mappings.values() if m['confidence'] == 'possible')

print(f'\n  Total mappings: {len(all_mappings)}')
print(f'    Confirmed: {total_confirmed}')
print(f'    Probable:  {total_probable}')
print(f'    Possible:  {total_possible}')

print(f'\n  CONFIRMED (★★★):')
for root, m in sorted(all_mappings.items(), key=lambda x: x[1].get('n_folios', 0) if x[1]['confidence']=='confirmed' else -1, reverse=True):
    if m['confidence'] == 'confirmed':
        print(f'    {root:>12s} = {m["latin"]:>25s} ({m.get("n_folios","?")} folios, freq={m.get("freq","?")})')

# Save
output = {
    'n_anchors': len(anchors_with_ingr),
    'n_root_fps': len(root_fps),
    'n_ingr_fps': len(ingr_fps),
    'exact_unique': len(unique),
    'exact_strong': len(strong),
    'fuzzy': len(fuzzy_matches),
    'total_mappings': len(all_mappings),
    'mappings': all_mappings,
    'exact_matches': exact_matches[:50],
    'fuzzy_matches': fuzzy_matches[:50],
}

with open(os.path.join(RESULTS, 'all_mappings.json'), 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f'\nSaved all_mappings.json')
