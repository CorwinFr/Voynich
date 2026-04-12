"""
PHASE 2 — AN Constraints
Use Antidotarium Nicolai recipe structure to constrain VMS decoding.

For each VMS pharma recipe block:
1. Count roots, doses, logograms
2. Find AN recipes with similar profile
3. If any VMS root is already identified (Phase 1), use it as anchor
4. Constrain remaining roots by what AN says should be there
"""
import json, sys, io, os
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

KB_PATH = os.path.join(os.path.dirname(__file__), '..', 'knowledge_base.json')
VMS_PATH = os.path.join(os.path.dirname(__file__), '..', 'vms', 'vms_structured.json')
AN_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'attacks', 'RECIPE_DATASET', 'S01_AN.json')

with open(KB_PATH, encoding='utf-8') as f:
    kb = json.load(f)
with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)
with open(AN_PATH, encoding='utf-8') as f:
    an = json.load(f)

LOGOGRAM_SET = set(kb['logograms'].keys())

# ================================================================
# 1. Build AN ingredient co-occurrence profiles
# ================================================================
print('Building AN co-occurrence matrix...')

an_recipes = []
an_ingr_sets = []

for entry in an['entries']:
    ingredients = []
    for tok in entry['tokens']:
        if tok['type'] == 'INGR' and 'ref' in tok:
            ingredients.append(tok['ref'])
    an_recipes.append({
        'id': entry['id'],
        'name': entry.get('name', ''),
        'n_tokens': entry['summary']['n_tokens'],
        'n_ingr': len(ingredients),
        'ingredients': list(set(ingredients)),
    })
    an_ingr_sets.append(set(ingredients))

# Co-occurrence: for each pair of ingredients, in how many recipes?
pair_count = Counter()
for ingr_set in an_ingr_sets:
    for a in ingr_set:
        for b in ingr_set:
            if a < b:
                pair_count[(a, b)] += 1

print(f'  {len(an_recipes)} AN recipes')
print(f'  {len(pair_count)} ingredient pairs')

# ================================================================
# 2. Build VMS recipe profiles (all pharma blocks)
# ================================================================
print('\nBuilding VMS recipe profiles...')

vms_recipes = []
for fid, folio in sorted(vms['folios'].items()):
    if folio['metadata']['section'] != 'pharma': continue
    for block in folio['blocks']:
        if not block.get('separator'): continue
        words = [w for line in block['lines'] for w in line['words']]
        roots = []
        identified = []
        unidentified = []

        for w in words:
            eva = w['eva_primary']
            if eva in LOGOGRAM_SET: continue
            morph = w.get('morphology') or {}
            root = morph.get('root', '')
            if not root: continue
            ic = morph.get('i_count')
            if ic is not None: continue  # skip doses

            roots.append(root)
            root_data = kb['roots'].get(root)
            if root_data and root_data.get('cracked_latin'):
                identified.append((root, root_data['cracked_latin']))
            else:
                unidentified.append(root)

        vms_recipes.append({
            'block_id': block['block_id'],
            'folio': fid,
            'n_words': len(words),
            'n_roots': len(roots),
            'identified': identified,
            'unidentified': list(set(unidentified)),
            'unique_roots': list(set(roots)),
        })

print(f'  {len(vms_recipes)} VMS pharma recipe blocks')

# ================================================================
# 3. For recipes with identified roots, find matching AN recipes
# ================================================================
print('\nMatching VMS recipes with AN...')

matches_found = 0
new_candidates = defaultdict(Counter)  # root → {latin: count}

for vr in vms_recipes:
    if not vr['identified']:
        continue

    # Known ingredient names for this VMS recipe
    known_latins = set(lat for _, lat in vr['identified'])

    # Find AN recipes containing ALL known ingredients
    matching_an = []
    for ar in an_recipes:
        # Check if known latins appear in AN recipe (fuzzy: check if substring)
        an_ingr_lower = [i.lower().replace('i_', '') for i in ar['ingredients']]
        match_count = 0
        for lat in known_latins:
            for an_i in an_ingr_lower:
                if lat in an_i or an_i in lat:
                    match_count += 1
                    break

        if match_count >= 1:  # At least 1 known ingredient matches
            matching_an.append((ar, match_count))

    if matching_an:
        matching_an.sort(key=lambda x: -x[1])
        matches_found += 1

        # From the best matching AN recipes, get the OTHER ingredients
        # These are candidates for the UNIDENTIFIED roots
        for ar, mc in matching_an[:3]:
            an_ingr_names = [i.lower().replace('i_', '') for i in ar['ingredients']]
            candidate_ingr = [i for i in an_ingr_names if i not in known_latins]

            # Weight: number of unidentified roots that could map
            if vr['unidentified'] and candidate_ingr:
                for unk_root in vr['unidentified']:
                    for cand in candidate_ingr:
                        new_candidates[unk_root][cand] += 1

# ================================================================
# 4. Aggregate candidates and update KB
# ================================================================
print(f'\n  Recipes with matches: {matches_found}')
print(f'  Roots with new candidates: {len(new_candidates)}')

print('\n' + '=' * 70)
print('TOP CANDIDATES FROM AN CONSTRAINTS')
print('=' * 70)

updated = 0
for root in sorted(new_candidates.keys(), key=lambda r: -kb['roots'].get(r, {}).get('pharma_freq', 0)):
    if root not in kb['roots']: continue
    cands = new_candidates[root].most_common(5)
    pharma = kb['roots'][root]['pharma_freq']

    if pharma < 5: continue

    print(f'\n  {root:12s} (pharma:x{pharma})')
    for lat, count in cands:
        print(f'    → {lat:25s} (from {count} AN recipes)')

    # Store in KB
    kb['roots'][root]['an_candidates'] = [
        {'latin': lat, 'an_recipe_count': count}
        for lat, count in cands
    ]
    updated += 1

print(f'\n  Updated {updated} roots with AN candidates')

# ================================================================
# 5. Cross-validate: roots with BOTH botanical ID and AN candidates
# ================================================================
print('\n' + '=' * 70)
print('CROSS-VALIDATION: Botanical ID vs AN Candidates')
print('=' * 70)

for root, data in kb['roots'].items():
    bot = data.get('botanical_id')
    an_cands = data.get('an_candidates', [])
    if not bot or not an_cands: continue

    bot_latin = data.get('cracked_latin', '')
    print(f'\n  {root:12s}:')
    print(f'    Botanical: {bot.get("species","")} → {bot_latin}')
    for c in an_cands[:3]:
        match = '✓ MATCH' if bot_latin and bot_latin in c['latin'] else ''
        print(f'    AN:        {c["latin"]:25s} (x{c["an_recipe_count"]}) {match}')

# Save
with open(KB_PATH, 'w', encoding='utf-8') as f:
    json.dump(kb, f, indent=2, ensure_ascii=False)
print(f'\nUpdated knowledge_base.json')
