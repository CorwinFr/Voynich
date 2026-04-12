"""
SESSION 16 — FRAPPE 3: Balnea × Balnea corpus (body vocabulary)

Identify the 11 balnea-exclusive roots using:
1. Frappe 6 data: roots enriched in balnea section (>30% balnea)
2. S11_BALNEA corpus: body parts and bath types
3. Fingerprint matching against balnea-specific vocabulary
"""
import json, sys, io, os
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.dirname(__file__)
VMS_PATH = os.path.join(BASE, '..', 'vms', 'vms_structured.json')
BALNEA_PATH = os.path.join(BASE, '..', '..', 'attacks', 'RECIPE_DATASET', 'S11_BALNEA.json')
RESULTS = BASE

with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)

LOGOS = {'o','l','d','r','v','x','k','m','f','t','y','c','s','sh','p','ch','air','h'}

# ================================================================
# STEP 1: Find balnea-exclusive or balnea-enriched roots
# ================================================================
print('='*70)
print('FRAPPE 3 — BALNEA VOCABULARY')
print('='*70)

# Count roots per section
root_sections = defaultdict(Counter)
root_total = Counter()

# Identify balnea folios
balnea_folios = set()
all_sections = Counter()

for fid, folio in vms['folios'].items():
    section = folio['metadata']['section']
    all_sections[section] += 1
    if 'baln' in section.lower():
        balnea_folios.add(fid)

    for block in folio['blocks']:
        for line in block['lines']:
            for w in line['words']:
                eva = w['eva_primary']
                if eva in LOGOS or len(eva) < 3:
                    continue
                root = (w.get('morphology') or {}).get('root', '')
                if root and len(root) >= 2:
                    root_sections[root][section] += 1
                    root_total[root] += 1

print(f'\n  Sections in VMS: {dict(all_sections)}')
print(f'  Balnea folios: {len(balnea_folios)}')

# Find balnea-enriched roots
balnea_roots = []
for root, sections in root_sections.items():
    total = sum(sections.values())
    if total < 3:
        continue

    balnea_count = sum(v for k, v in sections.items() if 'baln' in k.lower())
    balnea_pct = balnea_count * 100 // total

    # Also check if exclusive to balnea
    non_balnea = total - balnea_count
    is_exclusive = non_balnea == 0

    if balnea_pct >= 40 or (balnea_count >= 3 and is_exclusive):
        balnea_roots.append({
            'root': root,
            'total': total,
            'balnea_count': balnea_count,
            'balnea_pct': balnea_pct,
            'exclusive': is_exclusive,
            'sections': dict(sections),
        })

balnea_roots.sort(key=lambda x: (-x['balnea_pct'], -x['balnea_count']))

print(f'\n  Balnea-enriched roots (>=40% balnea): {len(balnea_roots)}')
print(f'\n  {"Root":>12s} {"Total":>6s} {"Baln":>5s} {"BPct":>5s} {"Excl":>5s}')
print('  ' + '-' * 40)

exclusive_roots = []
enriched_roots = []

for br in balnea_roots[:30]:
    marker = '★' if br['exclusive'] else ''
    print(f'  {br["root"]:>12s} {br["total"]:>6d} {br["balnea_count"]:>5d} '
          f'{br["balnea_pct"]:>4d}% {marker}')
    if br['exclusive']:
        exclusive_roots.append(br)
    else:
        enriched_roots.append(br)


# ================================================================
# STEP 2: Load balnea corpus
# ================================================================
if os.path.exists(BALNEA_PATH):
    print(f'\n\n{"="*70}')
    print('S11_BALNEA CORPUS ANALYSIS')
    print('='*70)

    with open(BALNEA_PATH, encoding='utf-8') as f:
        balnea_corpus = json.load(f)

    # Extract body parts and bath types from corpus
    body_parts = Counter()
    bath_types = Counter()
    balnea_ingredients = Counter()

    for entry in balnea_corpus.get('entries', []):
        for tok in entry.get('tokens', []):
            tok_type = tok.get('type', '')
            ref = tok.get('ref', tok.get('raw', '')).lower().strip('.,;: ')
            if tok_type == 'INGR':
                balnea_ingredients[ref] += 1
            elif tok_type == 'BODY':
                body_parts[ref] += 1
            elif tok_type == 'BATH':
                bath_types[ref] += 1

    print(f'\n  Body parts: {len(body_parts)}')
    for part, count in body_parts.most_common(20):
        print(f'    {part:>20s}: {count}')

    print(f'\n  Bath types: {len(bath_types)}')
    for bath, count in bath_types.most_common(10):
        print(f'    {bath:>20s}: {count}')

    print(f'\n  Top balnea ingredients: {len(balnea_ingredients)}')
    for ingr, count in balnea_ingredients.most_common(15):
        print(f'    {ingr:>20s}: {count}')

else:
    print(f'\n  S11_BALNEA.json not found')
    body_parts = Counter()
    bath_types = Counter()


# ================================================================
# STEP 3: Positional analysis of balnea-exclusive roots
# ================================================================
print(f'\n\n{"="*70}')
print('BALNEA ROOT POSITIONS AND CONTEXT')
print('='*70)

# For balnea-exclusive roots, check their positions and neighbors
for br in exclusive_roots[:15]:
    root = br['root']
    occurrences = []

    for fid in balnea_folios:
        folio = vms['folios'][fid]
        for block in folio['blocks']:
            for line in block['lines']:
                for wi, w in enumerate(line['words']):
                    r = (w.get('morphology') or {}).get('root', '')
                    if r == root:
                        # Get context (previous and next root)
                        prev_root = ''
                        next_root = ''
                        if wi > 0:
                            prev_root = (line['words'][wi-1].get('morphology') or {}).get('root', line['words'][wi-1]['eva_primary'])
                        if wi < len(line['words']) - 1:
                            next_root = (line['words'][wi+1].get('morphology') or {}).get('root', line['words'][wi+1]['eva_primary'])
                        norm_pos = wi / max(len(line['words']) - 1, 1)
                        occurrences.append({
                            'fid': fid,
                            'pos': norm_pos,
                            'prev': prev_root,
                            'next': next_root,
                        })

    if occurrences:
        positions = [o['pos'] for o in occurrences]
        mean_pos = sum(positions) / len(positions)
        prev_roots = Counter(o['prev'] for o in occurrences if o['prev'])
        next_roots = Counter(o['next'] for o in occurrences if o['next'])

        print(f'\n  {root:>12s} ({len(occurrences)} occ, mean pos={mean_pos:.2f}):')
        print(f'    Before: {dict(prev_roots.most_common(3))}')
        print(f'    After:  {dict(next_roots.most_common(3))}')


# ================================================================
# SAVE
# ================================================================
output = {
    'n_balnea_folios': len(balnea_folios),
    'n_exclusive_roots': len(exclusive_roots),
    'n_enriched_roots': len(enriched_roots),
    'exclusive_roots': [{'root': r['root'], 'total': r['total'],
                         'balnea_count': r['balnea_count']}
                        for r in exclusive_roots[:20]],
    'enriched_roots': [{'root': r['root'], 'total': r['total'],
                        'balnea_pct': r['balnea_pct']}
                       for r in enriched_roots[:20]],
    'body_parts': dict(body_parts.most_common(20)),
    'bath_types': dict(bath_types.most_common(10)),
}

with open(os.path.join(RESULTS, 'frappe3_results.json'), 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f'\nSaved frappe3_results.json')
