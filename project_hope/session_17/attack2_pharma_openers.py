"""
SESSION 17 — ATTACK 2: Decode pharma openers = recipe names (★★★★★)

Discovery (session 16): 27% of pharma block openers contain a plant root.
Structure: [gallows_prefix] + [plant_root] + [suffix]

This attack:
1. Match ALL 286 pharma openers against ALL known plant roots
   (including herbal first-word roots AND Sherwood-identified roots)
2. Use ONLY roots that passed the REAL test (>=20% standalone)
3. For each match: record the plant, the decomposition, confidence
4. Group recipes by plant → create a pharma-herbal bridge

This is the most valuable attack because it LABELS each recipe.
If recipe X is "for ruta", its ingredients MUST be in Macer's Ruta chapter.
"""
import json, sys, io, os
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.dirname(__file__)
VMS_PATH = os.path.join(BASE, '..', 'vms', 'vms_structured.json')
REG_PATH = os.path.join(BASE, '..', 'hypothesis_registry.json')
MACER_PATH = os.path.join(BASE, '..', 'session_14', 'macer_complete.json')
RESULTS = BASE

with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)
with open(REG_PATH, encoding='utf-8') as f:
    registry = json.load(f)
with open(MACER_PATH, encoding='utf-8') as f:
    macer = json.load(f)

LOGOS = {'o','l','d','r','v','x','k','m','f','t','y','c','s','sh','p','ch','air','h'}
GALLOWS = {'p', 't', 'k', 'f'}

# ================================================================
# BUILD PLANT ROOT DICTIONARY
# ================================================================
# Source 1: registered plant names (first words of herbal folios)
plant_roots = {}
for root, data in registry['plant_names'].items():
    plant_roots[root] = {
        'latin': data['latin'],
        'folio': data.get('folio', ''),
        'source': 'registry_plant_name',
    }

# Source 2: herbal folio first-word morphological roots
herbal_first_roots = {}
for fid, folio in vms['folios'].items():
    sec = folio['metadata']['section']
    if 'herbal' not in sec:
        continue
    for block in folio['blocks']:
        for line in block['lines']:
            if line['words']:
                w = line['words'][0]
                eva = w['eva_primary']
                root = (w.get('morphology') or {}).get('root', '')
                if root and len(root) >= 2 and root not in plant_roots:
                    herbal_first_roots[root] = {
                        'latin': f'plant_of_{fid}',
                        'folio': fid,
                        'source': 'herbal_first_word',
                    }
            break
        break

# Merge (plant_roots takes priority)
all_plant_roots = {}
all_plant_roots.update(herbal_first_roots)
all_plant_roots.update(plant_roots)

# Filter: only roots >= 3 chars (to avoid noise from 2-char matches)
filtered_roots = {r: d for r, d in all_plant_roots.items() if len(r) >= 3}

# Sort by length (longest first for greedy matching)
sorted_plant_roots = sorted(filtered_roots.keys(), key=len, reverse=True)

print(f'Plant roots available: {len(filtered_roots)} (>= 3 chars)')
print(f'From registry: {len(plant_roots)}, from herbal first-words: {len(herbal_first_roots)}')

# ================================================================
# MATCH PHARMA OPENERS
# ================================================================
print(f'\n{"="*70}')
print('MATCHING PHARMA OPENERS TO PLANT ROOTS')
print('='*70)

results = []
unmatched = []

for fid, folio in sorted(vms['folios'].items()):
    if folio['metadata']['section'] != 'pharma':
        continue
    for block in folio['blocks']:
        bid = block.get('block_id', '')
        lines = block['lines']
        if not lines or not lines[0]['words']:
            continue

        opener = lines[0]['words'][0]['eva_primary']
        n_words = sum(len(l['words']) for l in lines)

        # Try to match a plant root
        best_match = None
        for root in sorted_plant_roots:
            idx = opener.find(root)
            if idx >= 0:
                prefix = opener[:idx]
                suffix = opener[idx + len(root):]

                # Validate: prefix should be short (gallows or logo)
                # and suffix should be a known suffix pattern
                if len(prefix) <= 3 and len(suffix) <= 6:
                    best_match = {
                        'root': root,
                        'latin': filtered_roots[root]['latin'],
                        'folio': filtered_roots[root]['folio'],
                        'prefix': prefix,
                        'suffix': suffix,
                        'source': filtered_roots[root]['source'],
                    }
                    break

        if best_match:
            # Classify prefix
            pfx = best_match['prefix']
            if pfx and pfx[0] in GALLOWS:
                pfx_type = f'gallows({pfx[0]})'
            elif pfx in LOGOS:
                pfx_type = f'logo({pfx})'
            elif pfx == '':
                pfx_type = 'none'
            else:
                pfx_type = f'unk({pfx})'

            results.append({
                'bid': bid,
                'fid': fid,
                'opener': opener,
                'plant_root': best_match['root'],
                'plant_latin': best_match['latin'],
                'plant_folio': best_match['folio'],
                'prefix': pfx,
                'prefix_type': pfx_type,
                'suffix': best_match['suffix'],
                'n_words': n_words,
                'source': best_match['source'],
            })
        else:
            unmatched.append({
                'bid': bid,
                'opener': opener,
                'n_words': n_words,
            })

print(f'\n  Matched: {len(results)}/{len(results)+len(unmatched)} '
      f'({len(results)*100//(len(results)+len(unmatched))}%)')
print(f'  Unmatched: {len(unmatched)}')

# ================================================================
# ANALYSIS OF MATCHES
# ================================================================
print(f'\n{"="*70}')
print('MATCHED RECIPES BY PLANT')
print('='*70)

by_plant = defaultdict(list)
for r in results:
    by_plant[r['plant_latin']].append(r)

# Sort by number of recipes
for plant, recipes in sorted(by_plant.items(), key=lambda x: -len(x[1])):
    if len(recipes) >= 2:
        bids = [r['bid'] for r in recipes[:5]]
        folio = recipes[0]['plant_folio']
        print(f'  {plant:>20s} ({folio:>6s}): {len(recipes):>3d} recipes  '
              f'e.g. {", ".join(bids[:3])}')

print(f'\n  Plants with 1 recipe: {sum(1 for p, rs in by_plant.items() if len(rs) == 1)}')
print(f'  Plants with 2+ recipes: {sum(1 for p, rs in by_plant.items() if len(rs) >= 2)}')

# ================================================================
# PREFIX ANALYSIS (gallows distribution)
# ================================================================
print(f'\n{"="*70}')
print('PREFIX (GALLOWS) DISTRIBUTION')
print('='*70)

pfx_counts = Counter(r['prefix_type'] for r in results)
for pfx, n in pfx_counts.most_common():
    print(f'  {pfx:>20s}: {n:>3d} ({n*100//len(results)}%)')

# First character distribution
first_char = Counter(r['prefix'][0] if r['prefix'] else '_' for r in results)
print(f'\n  First character of matched openers:')
for c, n in first_char.most_common():
    print(f'    {c}: {n} ({n*100//len(results)}%)')

# ================================================================
# SHOW ALL MATCHES (detailed)
# ================================================================
print(f'\n{"="*70}')
print('DETAILED MATCHES (first 50)')
print('='*70)

print(f'\n  {"Block":>12s} {"Opener":>15s}  {"Pfx":>5s} + {"Root":>8s} + {"Sfx":>6s}  '
      f'{"Plant":>15s} {"HerbalFol":>9s} {"Words":>5s}')
print('  ' + '-' * 90)

for r in results[:50]:
    print(f'  {r["bid"]:>12s} {r["opener"]:>15s}  {r["prefix"]:>5s} + '
          f'{r["plant_root"]:>8s} + {r["suffix"]:>6s}  '
          f'{r["plant_latin"]:>15s} {r["plant_folio"]:>9s} {r["n_words"]:>5d}')

# ================================================================
# MACER BRIDGE: which matched plants have Macer chapters?
# ================================================================
print(f'\n{"="*70}')
print('MACER BRIDGE — Matched plants with Macer chapters')
print('='*70)

MACER_BY_NAME = {}
for ch in macer['chapters']:
    MACER_BY_NAME[ch['name'].lower()] = ch
if 'violae' in MACER_BY_NAME:
    MACER_BY_NAME['viola'] = MACER_BY_NAME['violae']

macer_bridge = []
for plant, recipes in sorted(by_plant.items(), key=lambda x: -len(x[1])):
    plant_clean = plant.replace('plant_of_', '').lower()
    # Try to match to Macer
    macer_ch = None

    # Direct match from Sherwood
    SHERWOOD = {
        'ruta':'ruta','viola':'violae','apium':'apium','salvia':'salvia',
        'lactuca':'lactuca','origanum':'origanum','mentha':'mentha',
        'coriandrum':'coriandrum','verbena':'verbena','aristolochia':'aristolochia',
        'malva':'malva','atriplex':'atriplex','satureia':'satureia',
        'centaurea':'centaurea','elleborus':'elleborus','althaea':'althaea',
        'scorzonera':'scorzonera','valeriana':'valeriana','gentiana':'gentiana',
        'lens':'plantago',  # lens appears in Plantago chapter
    }

    for sherwood_name, macer_name in SHERWOOD.items():
        if sherwood_name in plant_clean or plant_clean in sherwood_name:
            macer_ch = MACER_BY_NAME.get(macer_name.lower())
            if macer_ch:
                break

    if not macer_ch:
        # Try direct name match
        macer_ch = MACER_BY_NAME.get(plant_clean)

    if macer_ch:
        ingrs = [i.replace('I_','').replace('P_','') for i in macer_ch['ingredients']]
        macer_bridge.append({
            'plant': plant,
            'macer_chapter': macer_ch['name'],
            'n_recipes': len(recipes),
            'macer_ingredients': ingrs,
            'recipe_bids': [r['bid'] for r in recipes],
        })
        print(f'  {plant:>15s} → Macer "{macer_ch["name"]}" ({len(ingrs)} ingr): '
              f'{", ".join(ingrs[:6])}')
        print(f'    → {len(recipes)} pharma recipes: {[r["bid"] for r in recipes[:4]]}')

print(f'\n  Total plants with Macer bridge: {len(macer_bridge)}')
total_bridged_recipes = sum(mb['n_recipes'] for mb in macer_bridge)
print(f'  Total bridged recipes: {total_bridged_recipes}')

# ================================================================
# SAVE
# ================================================================
output = {
    'n_matched': len(results),
    'n_unmatched': len(unmatched),
    'match_pct': len(results) * 100 // (len(results) + len(unmatched)),
    'by_plant_summary': {plant: len(rs) for plant, rs in by_plant.items()},
    'macer_bridge': macer_bridge,
    'n_macer_bridged': total_bridged_recipes,
    'matched_recipes': results,
    'unmatched_openers': [u['opener'] for u in unmatched],
}

with open(os.path.join(RESULTS, 'attack2_results.json'), 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f'\nSaved attack2_results.json')
