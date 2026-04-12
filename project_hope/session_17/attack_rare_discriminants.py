"""
SESSION 17 — RARE DISCRIMINANT ATTACK

The reverse ID failed because common ingredients match everything.
NEW STRATEGY: Use RARE ingredients as discriminants.

If mastix (shocthy) appears ONLY in f29r and f25r among herbal folios,
and in the corpora mastix appears ONLY with lactuca and aristolochia,
then those folios are probably lactuca/aristolochia.

Also: fix Collectio parsing (title field, not name).
Use ALL 8 corpora with correct field names.
Build a RARITY-WEIGHTED fingerprint.
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

LOGOS = {'o','l','d','r','v','x','k','m','f','t','y','c','s','sh','p','ch','air','h'}
FUNCTIONAL = set(registry.get('functional_words', {}).keys())
NOISE = {'ke', 'ko', 'po', 'do'}

# KNOWN ingredients — ALL of them, even low confidence, for fingerprinting
KNOWN = {}
for root, data in registry['confirmed_ingredients'].items():
    KNOWN[root] = data['latin']
for root, data in registry.get('probable_ingredients', {}).items():
    if data.get('status') == 'ELIMINATED':
        continue
    KNOWN[root] = data['latin'].replace('i_', '')

KNOWN['ypch'] = 'aqua'
KNOWN['ched'] = 'vinum'
KNOWN['opch'] = 'succus'

sorted_known = sorted(KNOWN.keys(), key=len, reverse=True)

# ================================================================
# STEP 1: Compute ingredient RARITY across herbal folios
# ================================================================
print('='*70)
print('STEP 1 — INGREDIENT RARITY IN VMS HERBAL')
print('='*70)

# For each known ingredient, count how many herbal folios contain it
ingr_folio_count = Counter()
total_herbal = 0

for fid, folio in vms['folios'].items():
    if 'herbal' not in folio['metadata']['section']:
        continue
    total_herbal += 1

    found_here = set()
    for block in folio['blocks']:
        for line in block['lines']:
            for w in line['words']:
                eva = w['eva_primary']
                if eva in LOGOS:
                    continue
                for root in sorted_known:
                    if len(root) >= 3 and root in eva:
                        found_here.add(KNOWN[root])
                        break

    for ingr in found_here:
        ingr_folio_count[ingr] += 1

print(f'\n  Total herbal folios: {total_herbal}')
print(f'\n  Ingredient rarity (in herbal folios):')
print(f'  {"Ingredient":>15s} {"Folios":>7s} {"Pct":>5s} {"Rarity"}')
print('  ' + '-' * 40)

RARE_THRESHOLD = 15  # % of herbal folios
rare_ingredients = set()
common_ingredients = set()

for ingr, n in ingr_folio_count.most_common():
    pct = n * 100 // total_herbal
    if pct <= RARE_THRESHOLD:
        rarity = 'RARE'
        rare_ingredients.add(ingr)
    else:
        rarity = 'common'
        common_ingredients.add(ingr)
    print(f'  {ingr:>15s} {n:>7d} {pct:>4d}%  {rarity}')

print(f'\n  Rare ingredients (<=15%): {len(rare_ingredients)}: {sorted(rare_ingredients)}')
print(f'  Common ingredients (>15%): {len(common_ingredients)}: {sorted(common_ingredients)}')


# ================================================================
# STEP 2: Build RARE fingerprint per folio
# ================================================================
print(f'\n{"="*70}')
print('STEP 2 — RARE FINGERPRINTS PER FOLIO')
print('='*70)

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

rare_fingerprints = {}

for fid, folio in sorted(vms['folios'].items()):
    if 'herbal' not in folio['metadata']['section']:
        continue

    found_rare = set()
    found_common = set()
    for block in folio['blocks']:
        for line in block['lines']:
            for w in line['words']:
                eva = w['eva_primary']
                if eva in LOGOS:
                    continue
                for root in sorted_known:
                    if len(root) >= 3 and root in eva:
                        ingr = KNOWN[root]
                        if ingr in rare_ingredients:
                            found_rare.add(ingr)
                        else:
                            found_common.add(ingr)
                        break

    if found_rare:
        rare_fingerprints[fid] = {
            'rare': sorted(found_rare),
            'common': sorted(found_common),
            'identified': SHERWOOD.get(fid),
        }

print(f'  Folios with rare ingredients: {len(rare_fingerprints)}')
for fid, fp in sorted(rare_fingerprints.items()):
    marker = f'= {fp["identified"]}' if fp['identified'] else '???'
    print(f'    {fid:>8s} {marker:>15s}  rare={fp["rare"]}  common={fp["common"][:3]}')


# ================================================================
# STEP 3: Load ALL corpora with CORRECT field names
# ================================================================
print(f'\n{"="*70}')
print('STEP 3 — LOAD ALL CORPORA (corrected)')
print('='*70)

plant_db = defaultdict(lambda: {'ingredients': set(), 'sources': set(), 'n_entries': 0})

corpus_files = [
    ('S05_MACER.json', 'MACER', 'name'),
    ('S08_AVICENNA.json', 'AVICENNA', 'name'),
    ('S09_COLLECTIO.json', 'COLLECTIO', 'title'),
    ('S10_ALPHITA.json', 'ALPHITA', 'name'),
    ('S11_BALNEA.json', 'BALNEA', 'name'),
    ('S12_TACUINUM.json', 'TACUINUM', 'name'),
    ('S15_ABENGUEFIT.json', 'ABENGUEFIT', 'name'),
    ('S16_RHAZES.json', 'RHAZES', 'name'),
]

for corpus_file, corpus_name, name_field in corpus_files:
    path = os.path.join(RECIPE_DIR, corpus_file)
    if not os.path.exists(path):
        continue

    with open(path, encoding='utf-8') as f:
        data = json.load(f)

    n = 0
    for entry in data.get('entries', []):
        name = entry.get(name_field, entry.get('name', entry.get('title', ''))).lower().strip()
        if not name or len(name) < 3:
            continue

        ingrs = set()
        for tok in entry.get('tokens', []):
            if tok.get('type') == 'INGR':
                ref = tok.get('ref', tok.get('raw', '')).lower().strip('.,;: ').replace('i_', '')
                if len(ref) >= 3:
                    ingrs.add(ref)

        if ingrs:
            # Use simplified plant name (first word only for matching)
            simple_name = name.split()[0] if name else name
            plant_db[simple_name]['ingredients'].update(ingrs)
            plant_db[simple_name]['sources'].add(corpus_name)
            plant_db[simple_name]['n_entries'] += 1
            n += 1

    print(f'  {corpus_name:>12s}: {n} entries loaded')

print(f'  Plant database: {len(plant_db)} unique plant keys')


# ================================================================
# STEP 4: For each RARE ingredient, find which plants use it
# ================================================================
print(f'\n{"="*70}')
print('STEP 4 — RARE INGREDIENT → PLANT LOOKUP')
print('='*70)

rare_to_plants = defaultdict(set)
for plant_name, pdata in plant_db.items():
    for ingr in pdata['ingredients']:
        if ingr in rare_ingredients:
            rare_to_plants[ingr].add(plant_name)

for ingr in sorted(rare_ingredients):
    plants = rare_to_plants.get(ingr, set())
    n = len(plants)
    examples = sorted(plants)[:8]
    print(f'  {ingr:>12s}: {n:>4d} plants  {examples}')


# ================================================================
# STEP 5: RARE-WEIGHTED MATCHING
# ================================================================
print(f'\n{"="*70}')
print('STEP 5 — RARE-WEIGHTED PLANT MATCHING')
print('='*70)

# For each folio with rare ingredients, find plants that share those RARE ingredients
results = []

for fid, fp in sorted(rare_fingerprints.items()):
    if fp['identified']:
        continue  # skip known ones for now

    rare_set = set(fp['rare'])
    if not rare_set:
        continue

    # Score each plant: how many RARE ingredients match?
    plant_scores = []
    for plant_name, pdata in plant_db.items():
        rare_overlap = rare_set & pdata['ingredients']
        if not rare_overlap:
            continue

        # Weighted score: rare matches count MORE
        score = len(rare_overlap) * 10  # rare match = 10 points
        # Bonus for common overlap
        common_overlap = set(fp['common']) & pdata['ingredients']
        score += len(common_overlap)

        plant_scores.append({
            'plant': plant_name,
            'rare_match': len(rare_overlap),
            'common_match': len(common_overlap),
            'score': score,
            'matched_rare': sorted(rare_overlap),
            'sources': sorted(pdata['sources']),
        })

    plant_scores.sort(key=lambda x: -x['score'])

    if plant_scores:
        best = plant_scores[0]
        results.append({
            'fid': fid,
            'rare_ingrs': fp['rare'],
            'best_plant': best['plant'],
            'rare_match': best['rare_match'],
            'score': best['score'],
            'sources': best['sources'],
            'matched_rare': best['matched_rare'],
            'top3': [(p['plant'], p['rare_match'], p['score']) for p in plant_scores[:3]],
        })

results.sort(key=lambda x: (-x['rare_match'], -x['score']))

print(f'\n  Unidentified folios matched by rare ingredients: {len(results)}')
print(f'\n  {"Folio":>8s} {"Rare":>5s} {"BestPlant":>20s} {"RareM":>6s} {"Score":>6s} '
      f'{"MatchedRare"}')
print('  ' + '-' * 80)

for r in results[:20]:
    print(f'  {r["fid"]:>8s} {len(r["rare_ingrs"]):>5d} {r["best_plant"]:>20s} '
          f'{r["rare_match"]:>6d} {r["score"]:>6d}  {r["matched_rare"]}')


# ================================================================
# STEP 6: VALIDATION on known folios
# ================================================================
print(f'\n\n{"="*70}')
print('STEP 6 — VALIDATION')
print('='*70)

correct = 0
tested = 0

for fid, fp in sorted(rare_fingerprints.items()):
    if not fp['identified']:
        continue

    true_plant = fp['identified']
    rare_set = set(fp['rare'])
    if not rare_set:
        continue

    plant_scores = []
    for plant_name, pdata in plant_db.items():
        rare_overlap = rare_set & pdata['ingredients']
        if not rare_overlap:
            continue
        common_overlap = set(fp['common']) & pdata['ingredients']
        score = len(rare_overlap) * 10 + len(common_overlap)
        plant_scores.append({
            'plant': plant_name,
            'score': score,
            'rare_match': len(rare_overlap),
        })

    plant_scores.sort(key=lambda x: -x['score'])
    tested += 1

    if plant_scores:
        best = plant_scores[0]['plant']
        top5 = [p['plant'] for p in plant_scores[:5]]
        match = any(true_plant[:4] in p or p[:4] in true_plant for p in top5)
        if match:
            correct += 1
            status = '✓'
        else:
            status = '✗'
        print(f'  {status} {fid:>8s} true={true_plant:>15s}  best={best:>15s}  '
              f'rare={fp["rare"]}')

if tested:
    print(f'\n  Accuracy (top5): {correct}/{tested} ({correct*100//tested}%)')


# Save
output = {
    'rare_ingredients': sorted(rare_ingredients),
    'common_ingredients': sorted(common_ingredients),
    'n_results': len(results),
    'validation_correct': correct,
    'validation_tested': tested,
    'identifications': results[:30],
}

with open(os.path.join(RESULTS, 'attack_rare_results.json'), 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f'\nSaved attack_rare_results.json')
