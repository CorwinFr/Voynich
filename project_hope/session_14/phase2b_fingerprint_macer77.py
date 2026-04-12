"""
PHASE 2B — Fingerprint matching with FULL Macer (77 chapters).

Use the 100 anchor folios matched against 77 Macer chapters.
Much more discriminant fingerprints.
"""
import json, sys, io, os, re
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

VMS_PATH = os.path.join(os.path.dirname(__file__), '..', 'vms', 'vms_structured.json')
MACER_PATH = os.path.join(os.path.dirname(__file__), 'macer_complete.json')
ANCHORS_PATH = os.path.join(os.path.dirname(__file__), 'extended_anchors.json')
RESULTS = os.path.dirname(__file__)

with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)
with open(MACER_PATH, encoding='utf-8') as f:
    macer = json.load(f)
with open(ANCHORS_PATH, encoding='utf-8') as f:
    anchor_data = json.load(f)

LOGOS = {'o','l','d','r','v','x','k','m','f','t','y','c','s','sh','p','ch','air','h'}

# ================================================================
# Match anchors to Macer chapters
# ================================================================
print('Matching anchors to Macer 77 chapters...')

macer_by_name = {}
for ch in macer['chapters']:
    name = ch['name'].lower()
    macer_by_name[name] = ch

anchor_macer = []  # (folio, macer_chapter, ingredients)

for anchor in anchor_data['anchors']:
    fid = anchor['folio']
    species = (anchor.get('species', '') or '').lower()
    common = (anchor.get('common', '') or '').lower()

    # Try to match with Macer chapter
    matched = None
    for macer_name, ch in macer_by_name.items():
        # Match by species name parts
        for part in re.split(r'[/\s,]', species):
            part = part.strip().lower()
            if len(part) >= 4 and (part in macer_name or macer_name in part):
                matched = ch
                break
        if matched: break

        # Match by common name
        for part in re.split(r'[/\s,]', common):
            part = part.strip().lower()
            if len(part) >= 4 and (part in macer_name or macer_name in part):
                matched = ch
                break
        if matched: break

    if matched and matched['n_ingredients'] >= 2:
        anchor_macer.append({
            'folio': fid,
            'macer_chapter': matched['name'],
            'ingredients': set(matched['ingredients']),
            'qualities': matched['qualities'],
            'confidence': anchor.get('confidence', 0),
        })

print(f'  {len(anchor_macer)} anchors matched to Macer chapters with 2+ ingredients')

# ================================================================
# Build fingerprints
# ================================================================
fp_folios = [a['folio'] for a in anchor_macer]
n_fp = len(fp_folios)
print(f'  Fingerprint size: {n_fp} bits')

# Root fingerprints
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

folio_root_sets = {fid: get_roots(fid) for fid in fp_folios}

root_global = Counter()
for fid, folio in vms['folios'].items():
    for block in folio['blocks']:
        for line in block['lines']:
            for w in line['words']:
                root = (w.get('morphology') or {}).get('root', '')
                if root and len(root) >= 2:
                    root_global[root] += 1

root_fps = {}
for root in root_global:
    if root_global[root] < 3: continue
    fp = tuple(1 if root in folio_root_sets.get(fid, set()) else 0 for fid in fp_folios)
    if sum(fp) >= 2:
        root_fps[root] = fp

# Ingredient fingerprints
ingr_fps = defaultdict(lambda: [0] * n_fp)
for i, anchor in enumerate(anchor_macer):
    for ingr in anchor['ingredients']:
        ingr_fps[ingr][i] = 1

ingr_fps = {ingr: tuple(fp) for ingr, fp in ingr_fps.items() if sum(fp) >= 2}

print(f'  Root fingerprints: {len(root_fps)} ({n_fp}-bit)')
print(f'  Ingredient fingerprints: {len(ingr_fps)}')

# ================================================================
# EXACT MATCHES
# ================================================================
print(f'\n{"="*70}')
print('EXACT FINGERPRINT MATCHES (Macer 77)')
print('=' * 70)

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
    strength = 'UNIQUE' if len(roots) == 1 and len(ingrs) == 1 else \
               'STRONG' if len(roots) <= 2 and len(ingrs) <= 2 else \
               'MEDIUM' if len(roots) <= 5 and len(ingrs) <= 5 else 'WEAK'

    exact_matches.append({
        'fp': fp, 'n_present': n_present,
        'roots': roots, 'ingredients': ingrs,
        'strength': strength,
        'folios': [fp_folios[i] for i, v in enumerate(fp) if v],
    })

exact_matches.sort(key=lambda x: (-x['n_present'], x['strength'] != 'UNIQUE'))

unique = [m for m in exact_matches if m['strength'] == 'UNIQUE']
strong = [m for m in exact_matches if m['strength'] == 'STRONG']
medium = [m for m in exact_matches if m['strength'] == 'MEDIUM']

print(f'\n  Total exact matches: {len(exact_matches)}')
print(f'  ★★★ UNIQUE: {len(unique)}')
print(f'  ★★  STRONG: {len(strong)}')
print(f'  ★   MEDIUM: {len(medium)}')

print(f'\n  ★★★ UNIQUE MATCHES:')
for m in unique:
    root = m['roots'][0]
    ingr = m['ingredients'][0]
    freq = root_global.get(root, 0)
    print(f'    {root:>12s} = {ingr:>20s} ({m["n_present"]} folios, freq={freq}) {m["folios"]}')

print(f'\n  ★★ STRONG MATCHES:')
for m in strong[:20]:
    print(f'    {m["roots"]} = {m["ingredients"]} ({m["n_present"]} folios) {m["folios"][:3]}')

# ================================================================
# HAMMING 1 fuzzy
# ================================================================
print(f'\n{"="*70}')
print('FUZZY MATCHES (Hamming=1)')
print('=' * 70)

fuzzy = []
for root, r_fp in root_fps.items():
    for ingr, i_fp in ingr_fps.items():
        dist = sum(a != b for a, b in zip(r_fp, i_fp))
        if dist == 1 and sum(r_fp) >= 3 and sum(i_fp) >= 3:
            fuzzy.append((root, ingr, sum(r_fp), sum(i_fp), root_global.get(root, 0)))

fuzzy.sort(key=lambda x: -(x[2] + x[3]))
print(f'  {len(fuzzy)} fuzzy matches')
for root, ingr, rn, in_, freq in fuzzy[:15]:
    print(f'    {root:>12s} ≈ {ingr:>20s} (root:{rn}f ingr:{in_}f freq={freq})')

# ================================================================
# SUMMARY
# ================================================================
print(f'\n{"="*70}')
print('SUMMARY')
print('=' * 70)

all_decoded = {}
for m in unique:
    all_decoded[m['roots'][0]] = {
        'latin': m['ingredients'][0], 'confidence': 'confirmed',
        'n_folios': m['n_present'], 'freq': root_global.get(m['roots'][0], 0),
    }
for m in strong:
    if len(m['roots']) == 1 and m['roots'][0] not in all_decoded:
        all_decoded[m['roots'][0]] = {
            'latin': '/'.join(m['ingredients']), 'confidence': 'strong',
            'n_folios': m['n_present'],
        }

print(f'\n  Confirmed (UNIQUE): {len(unique)}')
print(f'  Strong: {len([m for m in strong if len(m["roots"])==1])}')
print(f'  Fuzzy: {len(fuzzy)}')
print(f'  Total new decodings: {len(all_decoded)}')

# Save
output = {
    'n_anchors': len(anchor_macer),
    'fp_size': n_fp,
    'n_root_fps': len(root_fps),
    'n_ingr_fps': len(ingr_fps),
    'unique_matches': [{
        'root': m['roots'][0], 'ingredient': m['ingredients'][0],
        'n_folios': m['n_present'], 'folios': m['folios'],
        'freq': root_global.get(m['roots'][0], 0),
    } for m in unique],
    'strong_matches': [{
        'roots': m['roots'], 'ingredients': m['ingredients'],
        'n_folios': m['n_present'], 'folios': m['folios'],
    } for m in strong],
    'fuzzy_matches': [{
        'root': r, 'ingredient': i, 'root_folios': rn, 'ingr_folios': in_,
    } for r, i, rn, in_, _ in fuzzy[:30]],
    'all_decoded': all_decoded,
}

with open(os.path.join(RESULTS, 'macer77_fingerprint.json'), 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f'\nSaved macer77_fingerprint.json')
