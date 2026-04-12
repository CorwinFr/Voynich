"""
STEPS 1+2+3 — Triangulate with Avicenna + Abenguefit + consolidate.

Same method as Macer but with 28 and 22 plant matches respectively.
Each new confirmed ingredient updates hypothesis_registry.json.
"""
import json, sys, io, os, re
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

VMS_PATH = os.path.join(os.path.dirname(__file__), '..', 'vms', 'vms_structured.json')
RECIPE_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'attacks', 'RECIPE_DATASET')
REG_PATH = os.path.join(os.path.dirname(__file__), '..', 'hypothesis_registry.json')
RESULTS = os.path.dirname(__file__)
os.makedirs(RESULTS, exist_ok=True)

with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)
with open(REG_PATH, encoding='utf-8') as f:
    registry = json.load(f)

LOGOS = {'o','l','d','r','v','x','k','m','f','t','y','c','s','sh','p','ch','air','h'}

# Already known roots — don't re-discover
KNOWN_ROOTS = set(registry['confirmed_ingredients'].keys()) | set(registry['plant_names'].keys())

# All Sherwood plant identifications
ALL_SHERWOOD = {
    'f48v':'ruta','f9v':'viola','f44v':'apium','f51v':'salvia',
    'f29r':'lactuca','f41r':'origanum','f37r':'mentha',
    'f41v':'coriandrum','f22r':'verbena','f28r':'aristolochia',
    'f5v':'malva','f45r':'atriplex','f66v':'satureia','f87r':'satureia',
    'f90r':'papaver','f90v':'eruca','f65v':'centaurea','f3v':'elleborus',
    'f95v1':'althaea','f11r':'rosmarinus','f16r':'cannabis',
    'f39r':'crocus','f44r':'mandragora','f50v':'gentiana',
    'f29v':'nigella','f35v':'ribes','f47v':'pulmonaria',
    'f53r':'achillea','f14r':'scorzonera','f21r':'anagallis',
    'f27r':'spinacia','f33v':'tanacetum','f49r':'nymphaea',
}

# ================================================================
# Build VMS root sets per folio (unknown roots only)
# ================================================================
def get_unknown_roots(fid):
    roots = Counter()
    for block in vms['folios'].get(fid, {}).get('blocks', []):
        for line in block['lines']:
            for w in line['words']:
                eva = w['eva_primary']
                if eva in LOGOS or len(eva) < 3: continue
                root = (w.get('morphology') or {}).get('root', '')
                if root and len(root) >= 2 and root not in KNOWN_ROOTS:
                    roots[root] += 1
    return roots

folio_unknown = {fid: get_unknown_roots(fid) for fid in ALL_SHERWOOD}

# ================================================================
# Generic triangulation function
# ================================================================
def triangulate_corpus(corpus_path, corpus_name):
    """Run fingerprint triangulation against a corpus."""
    with open(corpus_path, encoding='utf-8') as f:
        data = json.load(f)

    # Match Sherwood plants to corpus chapters
    chapter_ingr = {}
    for entry in data.get('entries', []):
        name = entry.get('name', '').lower().strip()
        ingrs = set()
        for tok in entry.get('tokens', []):
            if tok.get('type') == 'INGR':
                ref = tok.get('ref', tok.get('raw', '')).lower().strip('.,;: ')
                if len(ref) >= 3:
                    ingrs.add(ref)
        if name and len(ingrs) >= 2:
            chapter_ingr[name] = ingrs

    # Match Sherwood → corpus
    anchors = []
    for fid, plant in ALL_SHERWOOD.items():
        for chap_name, ingrs in chapter_ingr.items():
            if plant[:4] in chap_name or chap_name[:4] in plant:
                anchors.append((fid, plant, chap_name, ingrs))
                break

    if len(anchors) < 3:
        return []

    # Collect all ingredients across matched chapters
    all_ingr = set()
    for _, _, _, ingrs in anchors:
        all_ingr.update(ingrs)

    # For each ingredient, build presence fingerprint
    results = []
    for target_ingr in all_ingr:
        present_in = [fid for fid, _, _, ingrs in anchors if target_ingr in ingrs]
        absent_from = [fid for fid, _, _, ingrs in anchors if target_ingr not in ingrs]

        if len(present_in) < 2:
            continue

        # Find unknown roots shared by ALL present folios but NOT absent
        candidate_roots = None
        for fid in present_in:
            roots_here = set(folio_unknown.get(fid, {}).keys())
            if candidate_roots is None:
                candidate_roots = roots_here.copy()
            else:
                candidate_roots &= roots_here

        if candidate_roots and absent_from:
            for fid in absent_from[:5]:
                candidate_roots -= set(folio_unknown.get(fid, {}).keys())

        if candidate_roots and len(candidate_roots) <= 3:
            for root in candidate_roots:
                results.append({
                    'root': root,
                    'ingredient': target_ingr,
                    'n_present': len(present_in),
                    'n_absent': len(absent_from),
                    'n_candidates': len(candidate_roots),
                    'present_folios': present_in,
                    'corpus': corpus_name,
                    'strength': 'UNIQUE' if len(candidate_roots) == 1 else 'NARROW',
                })

    return results

# ================================================================
# RUN ALL 3 CORPORA
# ================================================================
all_results = []

for corpus_file, corpus_name in [
    ('S05_MACER.json', 'MACER'),
    ('S08_AVICENNA.json', 'AVICENNA'),
    ('S15_ABENGUEFIT.json', 'ABENGUEFIT'),
    ('S12_TACUINUM.json', 'TACUINUM'),
    ('S10_ALPHITA.json', 'ALPHITA'),
    ('S11_BALNEA.json', 'BALNEA'),
]:
    path = os.path.join(RECIPE_DIR, corpus_file)
    if not os.path.exists(path):
        continue

    print(f'\n{"="*70}')
    print(f'TRIANGULATION: {corpus_name}')
    print('=' * 70)

    results = triangulate_corpus(path, corpus_name)

    if results:
        print(f'  {len(results)} candidates found')
        for r in sorted(results, key=lambda x: (-x['n_present'], x['n_candidates'])):
            marker = '★★★' if r['strength'] == 'UNIQUE' else '★★'
            print(f'  {marker} {r["root"]:>12s} = {r["ingredient"]:>20s} '
                  f'({r["n_present"]} folios, {r["n_candidates"]} candidates) {r["present_folios"][:3]}')
        all_results.extend(results)
    else:
        print(f'  No candidates found')

# ================================================================
# CONSOLIDATE: which mappings appear in 2+ corpora?
# ================================================================
print(f'\n\n{"="*70}')
print('CONSOLIDATION — Multi-source convergence')
print('=' * 70)

# Group by root
root_evidence = defaultdict(list)
for r in all_results:
    root_evidence[r['root']].append(r)

# Find convergent mappings
new_confirmed = {}
new_probable = {}

for root, evidences in root_evidence.items():
    # Group by ingredient
    ingr_sources = defaultdict(list)
    for ev in evidences:
        ingr_sources[ev['ingredient']].append(ev['corpus'])

    best_ingr = max(ingr_sources, key=lambda i: len(ingr_sources[i]))
    n_sources = len(set(ingr_sources[best_ingr]))
    all_sources = list(set(ingr_sources[best_ingr]))

    if n_sources >= 2:
        print(f'  ★★★ {root:>12s} = {best_ingr:>20s} ({n_sources} sources: {all_sources})')
        new_confirmed[root] = {
            'latin': best_ingr, 'confidence': 0.85,
            'sources': all_sources, 'n_sources': n_sources,
        }
    elif n_sources == 1 and evidences[0]['strength'] == 'UNIQUE':
        print(f'  ★★  {root:>12s} = {best_ingr:>20s} (1 source: {all_sources[0]}, UNIQUE)')
        new_probable[root] = {
            'latin': best_ingr, 'confidence': 0.7,
            'sources': all_sources, 'n_sources': 1,
        }
    elif n_sources == 1:
        new_probable[root] = {
            'latin': best_ingr, 'confidence': 0.5,
            'sources': all_sources, 'n_sources': 1,
        }

# All single-source UNIQUE
for r in all_results:
    if r['root'] not in new_confirmed and r['root'] not in new_probable:
        if r['strength'] == 'UNIQUE':
            new_probable[r['root']] = {
                'latin': r['ingredient'], 'confidence': 0.6,
                'sources': [r['corpus']], 'n_sources': 1,
            }

print(f'\n  CONFIRMED (2+ sources): {len(new_confirmed)}')
print(f'  PROBABLE (1 source):    {len(new_probable)}')

# ================================================================
# UPDATE REGISTRY
# ================================================================
print(f'\n{"="*70}')
print('UPDATING HYPOTHESIS REGISTRY')
print('=' * 70)

for root, data in new_confirmed.items():
    if root not in registry['confirmed_ingredients']:
        registry['confirmed_ingredients'][root] = {
            'latin': data['latin'],
            'confidence': data['confidence'],
            'evidence_for': [f'triangulation_{s}' for s in data['sources']],
            'evidence_against': [],
            'session_confirmed': 15,
        }
        print(f'  NEW CONFIRMED: {root} = {data["latin"]}')

for root, data in new_probable.items():
    if root not in registry['confirmed_ingredients'] and root not in registry.get('probable_ingredients', {}):
        if 'probable_ingredients' not in registry:
            registry['probable_ingredients'] = {}
        registry['probable_ingredients'][root] = {
            'latin': data['latin'],
            'confidence': data['confidence'],
            'evidence_for': [f'triangulation_{s}' for s in data['sources']],
            'session': 15,
        }

registry['_meta']['sessions'] = '10-15'
registry['_meta']['last_updated'] = '2026-04-12'

with open(REG_PATH, 'w', encoding='utf-8') as f:
    json.dump(registry, f, indent=2, ensure_ascii=False)

total_confirmed = len(registry['confirmed_ingredients'])
total_probable = len(registry.get('probable_ingredients', {}))
total_plants = len(registry['plant_names'])

print(f'\n  Registry totals:')
print(f'    Confirmed ingredients: {total_confirmed}')
print(f'    Probable ingredients: {total_probable}')
print(f'    Plant names: {total_plants}')
print(f'    TOTAL vocabulary: {total_confirmed + total_probable + total_plants + 18}')

# Save results
with open(os.path.join(RESULTS, 'triangulation_all.json'), 'w', encoding='utf-8') as f:
    json.dump({
        'all_results': all_results,
        'new_confirmed': new_confirmed,
        'new_probable': new_probable,
    }, f, indent=2, ensure_ascii=False)

print(f'\nSaved triangulation_all.json')
