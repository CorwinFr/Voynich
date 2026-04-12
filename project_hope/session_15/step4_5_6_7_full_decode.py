"""
STEPS 4-7 — Decompose pharma, validate, find universals, decode.
"""
import json, sys, io, os
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

VMS_PATH = os.path.join(os.path.dirname(__file__), '..', 'vms', 'vms_structured.json')
REG_PATH = os.path.join(os.path.dirname(__file__), '..', 'hypothesis_registry.json')
RESULTS = os.path.dirname(__file__)

with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)
with open(REG_PATH, encoding='utf-8') as f:
    registry = json.load(f)

LOGOS = {'o':'ac','l':'se','d':'de','r':'recipe','v':'vel','x':'crux',
         'k':'cum','m':'misce','f':'per','t':'et','y':'in','c':'cum',
         's':'est','sh':'ci','p':'usque','ch':'cum'}
LOGO_SET = set(LOGOS.keys())

# Build complete root→latin dictionary from ALL sources
all_roots = {}
for root, data in registry['confirmed_ingredients'].items():
    all_roots[root] = {'latin': data['latin'], 'conf': data.get('confidence', 0.9)}
for root, data in registry.get('probable_ingredients', {}).items():
    if root not in all_roots:
        all_roots[root] = {'latin': data['latin'], 'conf': data.get('confidence', 0.5)}
for root, data in registry['plant_names'].items():
    if root not in all_roots:
        all_roots[root] = {'latin': data['latin'], 'conf': 0.6}

sorted_roots = sorted(all_roots.keys(), key=len, reverse=True)
print(f'Total vocabulary: {len(all_roots)} roots + {len(LOGOS)} logograms')

# ================================================================
# STEP 4: Decompose ALL pharma words
# ================================================================
print(f'\n{"="*70}')
print('STEP 4 — DECOMPOSE PHARMA')
print('=' * 70)

def find_root(eva):
    for root in sorted_roots:
        if len(root) < 2: continue
        idx = eva.find(root)
        if idx >= 0:
            prefix = eva[:idx]
            suffix = eva[idx+len(root):]
            if len(prefix) <= 4 and len(suffix) <= 5:
                return prefix, root, suffix, all_roots[root]
    return None, None, None, None

decomposed = 0
total_pharma = 0
recipe_decodings = defaultdict(list)

for fid, folio in vms['folios'].items():
    if folio['metadata']['section'] != 'pharma': continue
    for block in folio['blocks']:
        bid = block.get('block_id', '')
        for line in block['lines']:
            for w in line['words']:
                eva = w['eva_primary']
                if eva in LOGO_SET or len(eva) < 3:
                    if eva in LOGO_SET:
                        recipe_decodings[bid].append(('LOGO', eva, LOGOS[eva], 1.0))
                    continue
                morph = w.get('morphology') or {}
                ic = morph.get('i_count')
                total_pharma += 1

                if ic is not None:
                    recipe_decodings[bid].append(('DOSE', eva, f'({ic})', 0.9))
                    decomposed += 1
                    continue

                pfx, root, sfx, data = find_root(eva)
                if root:
                    latin = data['latin']
                    conf = data['conf']
                    pfx_str = LOGOS.get(pfx, pfx) if pfx else ''
                    recipe_decodings[bid].append(('INGR', eva, f'{pfx_str}+{latin}.{sfx}' if pfx_str else f'{latin}.{sfx}', conf))
                    decomposed += 1
                else:
                    recipe_decodings[bid].append(('UNK', eva, eva, 0))

pct = decomposed * 100 // max(total_pharma, 1)
print(f'  Decomposed: {decomposed}/{total_pharma} = {pct}%')

# ================================================================
# STEP 5: Find best-decoded recipes
# ================================================================
print(f'\n{"="*70}')
print('STEP 5 — BEST DECODED RECIPES')
print('=' * 70)

recipe_scores = []
for bid, words in recipe_decodings.items():
    n_total = len(words)
    n_decoded = sum(1 for t, _, _, c in words if c > 0)
    n_ingr = sum(1 for t, _, _, _ in words if t == 'INGR')
    pct_decoded = n_decoded * 100 // max(n_total, 1)
    ingr_names = [latin for t, _, latin, c in words if t == 'INGR' and c >= 0.7]
    unique_ingr = len(set(ingr_names))

    recipe_scores.append({
        'bid': bid,
        'n_total': n_total,
        'n_decoded': n_decoded,
        'pct': pct_decoded,
        'n_ingr': n_ingr,
        'unique_ingr': unique_ingr,
        'ingredients': list(set(ingr_names))[:10],
    })

recipe_scores.sort(key=lambda x: -x['pct'])

print(f'\n  TOP 20 best-decoded recipes:')
print(f'  {"Block":>20s} {"Tot":>4s} {"Dec":>4s} {"Pct":>4s} {"Ingr":>5s} {"Ingredients":>50s}')
print('  ' + '-' * 90)

for r in recipe_scores[:20]:
    ingr_str = ', '.join(r['ingredients'][:5])
    print(f'  {r["bid"]:>20s} {r["n_total"]:>4d} {r["n_decoded"]:>4d} {r["pct"]:>3d}% {r["unique_ingr"]:>5d} {ingr_str:>50s}')

# ================================================================
# STEP 6: Identify universal vehicles (aqua/succus/vinum)
# ================================================================
print(f'\n{"="*70}')
print('STEP 6 — UNIVERSAL VEHICLES')
print('=' * 70)

# Roots that appear in 70%+ of pharma blocks and are NOT yet decoded
root_in_blocks = defaultdict(set)
for fid, folio in vms['folios'].items():
    if folio['metadata']['section'] != 'pharma': continue
    for block in folio['blocks']:
        bid = block.get('block_id', '')
        for line in block['lines']:
            for w in line['words']:
                eva = w['eva_primary']
                if eva in LOGO_SET: continue
                root = (w.get('morphology') or {}).get('root', '')
                if root and len(root) >= 2:
                    root_in_blocks[root].add(bid)

n_blocks = len(recipe_decodings)
universal_candidates = []

for root, blocks in root_in_blocks.items():
    pct = len(blocks) * 100 // n_blocks
    if pct >= 50 and root not in all_roots:
        universal_candidates.append((root, len(blocks), pct))

universal_candidates.sort(key=lambda x: -x[1])

print(f'\n  Roots in 50%+ pharma blocks, NOT yet decoded:')
print(f'  (These are likely aqua, succus, or vinum)')
print(f'\n  {"Root":>12s} {"Blocks":>7s} {"Pct":>5s}')
print('  ' + '-' * 28)

for root, n, pct in universal_candidates[:15]:
    print(f'  {root:>12s} {n:>7d} {pct:>4d}%')

# The top 3 unknown universal roots are probably aqua, succus, vinum
if len(universal_candidates) >= 3:
    u1, u2, u3 = universal_candidates[0], universal_candidates[1], universal_candidates[2]
    print(f'\n  HYPOTHESIS (by frequency):')
    print(f'    {u1[0]:>12s} ({u1[2]}%) = aqua? (most universal)')
    print(f'    {u2[0]:>12s} ({u2[2]}%) = succus or vinum?')
    print(f'    {u3[0]:>12s} ({u3[2]}%) = succus or vinum?')

# ================================================================
# STEP 7: Decode f48v and f103r B01
# ================================================================
print(f'\n{"="*70}')
print('STEP 7 — FINAL DECODE f48v (Ruta)')
print('=' * 70)

f48v = vms['folios']['f48v']
total_f = decoded_f = 0

for block in f48v['blocks']:
    for line in block['lines']:
        parts = []
        for w in line['words']:
            eva = w['eva_primary']
            morph = w.get('morphology') or {}
            ic = morph.get('i_count')
            total_f += 1

            if eva in LOGO_SET:
                parts.append(LOGOS[eva].upper())
                decoded_f += 1
            elif ic is not None:
                parts.append(f'({ic})')
                decoded_f += 1
            else:
                pfx, root, sfx, data = find_root(eva)
                if root:
                    latin = data['latin']
                    pfx_m = LOGOS.get(pfx, pfx) if pfx else ''
                    p = f'{pfx_m}+' if pfx_m else ''
                    s = f'.{sfx}' if sfx else ''
                    parts.append(f'{p}{latin}{s}')
                    decoded_f += 1
                else:
                    parts.append(f'({eva})')

        print(f'  {line["line_id"]}: {" ".join(parts)}')

print(f'\n  f48v: {decoded_f}/{total_f} = {decoded_f*100//total_f}%')

print(f'\n{"="*70}')
print('f103r B01 — FIRST PHARMA RECIPE')
print('=' * 70)

block1 = vms['folios']['f103r']['blocks'][0]
total_r = decoded_r = 0

for line in block1['lines']:
    parts = []
    for w in line['words']:
        eva = w['eva_primary']
        morph = w.get('morphology') or {}
        ic = morph.get('i_count')
        total_r += 1

        if eva in LOGO_SET:
            parts.append(LOGOS[eva].upper())
            decoded_r += 1
        elif ic is not None:
            parts.append(f'({ic})')
            decoded_r += 1
        else:
            pfx, root, sfx, data = find_root(eva)
            if root:
                latin = data['latin']
                pfx_m = LOGOS.get(pfx, pfx) if pfx else ''
                p = f'{pfx_m}+' if pfx_m else ''
                s = f'.{sfx}' if sfx else ''
                parts.append(f'{p}{latin}{s}')
                decoded_r += 1
            else:
                parts.append(f'({eva})')

    print(f'  {line["line_id"]}: {" ".join(parts)}')

print(f'\n  f103r B01: {decoded_r}/{total_r} = {decoded_r*100//total_r}%')

# Save
output = {
    'pharma_decomposed_pct': pct,
    'f48v_pct': decoded_f * 100 // total_f,
    'f103r_b01_pct': decoded_r * 100 // total_r,
    'top_recipes': recipe_scores[:20],
    'universal_candidates': [{'root': r, 'blocks': n, 'pct': p} for r, n, p in universal_candidates[:10]],
    'total_vocabulary': len(all_roots) + len(LOGOS),
}

with open(os.path.join(RESULTS, 'full_decode_results.json'), 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f'\nSaved full_decode_results.json')
