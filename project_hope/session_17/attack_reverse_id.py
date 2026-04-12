"""
SESSION 17 — REVERSE PLANT IDENTIFICATION

Strategy: We have ~113 unidentified herbal folios. Each contains roots.
Some roots are KNOWN ingredients (cth=acetum, yk=mel, cht=piper, etc).
For each folio, build an ingredient fingerprint from known roots,
then search ALL corpora for plants that match.

Corpora available:
  S05_MACER (77 chapters, 36 ingredients) — small but precise
  S08_AVICENNA (2148 entries) — HUGE
  S09_COLLECTIO (3680 entries) — HUGE
  S10_ALPHITA (8.7MB) — large
  S15_ABENGUEFIT — medium
  S12_TACUINUM — medium

This is speculative. We WILL get false matches. But with 6+ corpora
cross-validating, the TRUE plant should emerge.
"""
import json, sys, io, os
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.dirname(__file__)
VMS_PATH = os.path.join(BASE, '..', 'vms', 'vms_structured.json')
REG_PATH = os.path.join(BASE, '..', 'hypothesis_registry.json')
RECIPE_DIR = os.path.join(BASE, '..', '..', 'attacks', 'RECIPE_DATASET')
RESULTS = BASE

with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)
with open(REG_PATH, encoding='utf-8') as f:
    registry = json.load(f)

# Build KNOWN ingredient vocabulary (STRICT: real short roots only)
KNOWN = {}
REAL_SHORT = {'chk', 'cht', 'yk', 'dsh', 'olk', 'ych'}
for root, data in registry['confirmed_ingredients'].items():
    if len(root) >= 4 or root in REAL_SHORT:
        KNOWN[root] = data['latin']
for root, data in registry.get('probable_ingredients', {}).items():
    if data.get('status') == 'ELIMINATED':
        continue
    if data.get('confidence', 0) >= 0.60:
        if len(root) >= 4 or root in REAL_SHORT:
            KNOWN[root] = data['latin'].replace('i_', '')

# Add ypch=aqua, ched=vinum, opch=succus
KNOWN['ypch'] = 'aqua'
KNOWN['ched'] = 'vinum'
KNOWN['opch'] = 'succus'

sorted_known = sorted(KNOWN.keys(), key=len, reverse=True)

print(f'Known ingredient roots: {len(KNOWN)}')
for r, l in sorted(KNOWN.items(), key=lambda x: x[1]):
    print(f'  {r:>10s} = {l}')

LOGOS = {'o','l','d','r','v','x','k','m','f','t','y','c','s','sh','p','ch','air','h'}
FUNCTIONAL = set(registry.get('functional_words', {}).keys())

# Already identified folios
SHERWOOD = {
    'f48v':'ruta','f9v':'viola','f44v':'apium','f51v':'salvia',
    'f29r':'lactuca','f41r':'origanum','f37r':'mentha',
    'f41v':'coriandrum','f22r':'verbena','f28r':'aristolochia',
    'f5v':'malva','f45r':'atriplex','f66v':'satureia',
    'f65v':'centaurea','f3v':'elleborus','f95v1':'althaea',
    'f11r':'rosmarinus','f16r':'cannabis','f39r':'crocus',
    'f44r':'mandragora','f50v':'gentiana','f29v':'nigella',
    'f35v':'ribes','f47v':'pulmonaria','f53r':'achillea',
    'f14r':'scorzonera','f21r':'anagallis','f27r':'spinacia',
    'f33v':'tanacetum','f49r':'nymphaea','f87r':'satureia',
}

# ================================================================
# STEP 1: Build ingredient fingerprint for EVERY herbal folio
# ================================================================
print(f'\n{"="*70}')
print('STEP 1 — INGREDIENT FINGERPRINTS PER FOLIO')
print('='*70)

folio_fingerprints = {}

for fid, folio in sorted(vms['folios'].items()):
    sec = folio['metadata']['section']
    if 'herbal' not in sec:
        continue

    # Find known ingredients in this folio
    found_ingredients = set()
    for block in folio['blocks']:
        for line in block['lines']:
            for w in line['words']:
                eva = w['eva_primary']
                if eva in LOGOS:
                    continue
                for root in sorted_known:
                    if root in eva and len(root) >= 3:
                        found_ingredients.add(KNOWN[root])
                        break

    if found_ingredients:
        is_identified = fid in SHERWOOD
        folio_fingerprints[fid] = {
            'ingredients': sorted(found_ingredients),
            'n_ingredients': len(found_ingredients),
            'identified': SHERWOOD.get(fid, None),
            'section': sec,
        }

print(f'  Folios with ingredient fingerprints: {len(folio_fingerprints)}')
identified = sum(1 for f in folio_fingerprints.values() if f['identified'])
unidentified = len(folio_fingerprints) - identified
print(f'  Already identified: {identified}')
print(f'  UNIDENTIFIED (targets): {unidentified}')

# Show folios with richest fingerprints
rich = sorted(folio_fingerprints.items(), key=lambda x: -x[1]['n_ingredients'])
print(f'\n  Top 20 richest fingerprints:')
for fid, fp in rich[:20]:
    marker = f'= {fp["identified"]}' if fp['identified'] else '???'
    print(f'    {fid:>8s} ({fp["n_ingredients"]:>2d} ingr) {marker:>15s}: '
          f'{", ".join(fp["ingredients"][:8])}')

# ================================================================
# STEP 2: Load ALL corpora → build plant→ingredient database
# ================================================================
print(f'\n{"="*70}')
print('STEP 2 — LOAD ALL CORPORA')
print('='*70)

# Plant database: plant_name → set of ingredients
plant_db = defaultdict(lambda: {'ingredients': set(), 'sources': set()})

corpus_files = [
    ('S05_MACER.json', 'MACER'),
    ('S08_AVICENNA.json', 'AVICENNA'),
    ('S09_COLLECTIO.json', 'COLLECTIO'),
    ('S10_ALPHITA.json', 'ALPHITA'),
    ('S11_BALNEA.json', 'BALNEA'),
    ('S12_TACUINUM.json', 'TACUINUM'),
    ('S15_ABENGUEFIT.json', 'ABENGUEFIT'),
    ('S16_RHAZES.json', 'RHAZES'),
]

total_entries = 0
for corpus_file, corpus_name in corpus_files:
    path = os.path.join(RECIPE_DIR, corpus_file)
    if not os.path.exists(path):
        print(f'  {corpus_name}: NOT FOUND')
        continue

    with open(path, encoding='utf-8') as f:
        data = json.load(f)

    n_entries = 0
    for entry in data.get('entries', []):
        name = entry.get('name', '').lower().strip()
        if not name or len(name) < 3:
            continue

        ingrs = set()
        for tok in entry.get('tokens', []):
            if tok.get('type') == 'INGR':
                ref = tok.get('ref', tok.get('raw', '')).lower().strip('.,;: ')
                # Normalize: remove i_ prefix
                ref = ref.replace('i_', '')
                if len(ref) >= 3:
                    ingrs.add(ref)

        if ingrs:
            plant_db[name]['ingredients'].update(ingrs)
            plant_db[name]['sources'].add(corpus_name)
            n_entries += 1

    total_entries += n_entries
    print(f'  {corpus_name:>12s}: {n_entries} plant entries')

print(f'\n  Total plant database: {len(plant_db)} unique plants, {total_entries} entries')

# ================================================================
# STEP 3: REVERSE MATCH — folio fingerprint → plant database
# ================================================================
print(f'\n{"="*70}')
print('STEP 3 — REVERSE PLANT IDENTIFICATION')
print('='*70)

# For each unidentified folio, find plants whose ingredient set
# CONTAINS all the folio's known ingredients
results = []

for fid, fp in sorted(folio_fingerprints.items()):
    if fp['identified']:
        continue  # skip already identified
    if fp['n_ingredients'] < 2:
        continue  # need at least 2 ingredients to constrain

    folio_ingrs = set(fp['ingredients'])

    # Find matching plants
    matches = []
    for plant_name, plant_data in plant_db.items():
        plant_ingrs = plant_data['ingredients']
        # How many of our folio ingredients are in this plant?
        overlap = folio_ingrs & plant_ingrs
        if len(overlap) >= 2:  # at least 2 ingredients match
            coverage = len(overlap) / len(folio_ingrs)
            matches.append({
                'plant': plant_name,
                'overlap': len(overlap),
                'coverage': coverage,
                'plant_total': len(plant_ingrs),
                'sources': sorted(plant_data['sources']),
                'matched_ingrs': sorted(overlap),
            })

    matches.sort(key=lambda x: (-x['overlap'], -x['coverage']))

    if matches:
        best = matches[0]
        n_sources = len(best['sources'])
        results.append({
            'fid': fid,
            'n_folio_ingrs': fp['n_ingredients'],
            'folio_ingrs': fp['ingredients'],
            'best_plant': best['plant'],
            'best_overlap': best['overlap'],
            'best_coverage': best['coverage'],
            'best_sources': best['sources'],
            'n_matches': len(matches),
            'top3': [(m['plant'], m['overlap'], m['sources'][:2]) for m in matches[:3]],
        })

results.sort(key=lambda x: (-x['best_overlap'], -x['best_coverage']))

print(f'\n  Unidentified folios with 2+ matches: {len(results)}')
print(f'\n  {"Folio":>8s} {"#Ingr":>6s} {"BestPlant":>20s} {"Overlap":>8s} {"Cov":>5s} '
      f'{"#Match":>7s} {"Sources"}')
print('  ' + '-' * 80)

for r in results[:30]:
    print(f'  {r["fid"]:>8s} {r["n_folio_ingrs"]:>6d} {r["best_plant"]:>20s} '
          f'{r["best_overlap"]:>8d} {r["best_coverage"]:>4.0%} '
          f'{r["n_matches"]:>7d} {r["best_sources"][:3]}')

# ================================================================
# STEP 4: VALIDATION — check identified folios
# ================================================================
print(f'\n\n{"="*70}')
print('STEP 4 — VALIDATION ON KNOWN FOLIOS')
print('='*70)

correct = 0
wrong = 0
not_found = 0

for fid, fp in sorted(folio_fingerprints.items()):
    if not fp['identified']:
        continue
    if fp['n_ingredients'] < 2:
        continue

    true_plant = fp['identified']
    folio_ingrs = set(fp['ingredients'])

    matches = []
    for plant_name, plant_data in plant_db.items():
        overlap = folio_ingrs & plant_data['ingredients']
        if len(overlap) >= 2:
            matches.append({
                'plant': plant_name,
                'overlap': len(overlap),
            })

    matches.sort(key=lambda x: -x['overlap'])

    if matches:
        best = matches[0]['plant']
        # Check if true plant is in top 3
        top3_plants = [m['plant'] for m in matches[:3]]
        if true_plant in best or best in true_plant:
            status = '✓'
            correct += 1
        elif any(true_plant in p or p in true_plant for p in top3_plants):
            status = '~'  # in top 3
            correct += 1
        else:
            status = '✗'
            wrong += 1
            # Show what we got vs expected
        print(f'  {status} {fid:>8s} true={true_plant:>15s}  '
              f'best={best:>20s}  ingr={", ".join(fp["ingredients"][:5])}')
    else:
        not_found += 1
        print(f'  - {fid:>8s} true={true_plant:>15s}  NO MATCH (ingr={fp["ingredients"]})')

total_test = correct + wrong + not_found
print(f'\n  Correct/Top3: {correct}/{total_test} ({correct*100//max(total_test,1)}%)')
print(f'  Wrong: {wrong}/{total_test}')
print(f'  No match: {not_found}/{total_test}')

# ================================================================
# SAVE
# ================================================================
output = {
    'n_known_roots': len(KNOWN),
    'n_folio_fingerprints': len(folio_fingerprints),
    'n_unidentified_matched': len(results),
    'validation_correct': correct,
    'validation_wrong': wrong,
    'validation_total': total_test,
    'reverse_identifications': results[:50],
    'plant_db_size': len(plant_db),
}

with open(os.path.join(RESULTS, 'attack_reverse_id_results.json'), 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f'\nSaved attack_reverse_id_results.json')
