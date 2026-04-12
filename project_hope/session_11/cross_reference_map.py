"""
CROSS-REFERENCE MAP — Reconstruct the consultation system.

For each pharma recipe block:
  - Which PLANT codes appear? → links to herbal folios
  - Which INGR codes appear? → unknown but trackable
  - Build the map: pharma_block → [herbal_folios referenced]

Then: which herbal pages are referenced TOGETHER?
= which plants are used in the SAME recipes = therapeutic groups
"""
import json, sys, io, os
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

VMS_PATH = os.path.join(os.path.dirname(__file__), '..', 'vms', 'vms_structured.json')
KB_PATH = os.path.join(os.path.dirname(__file__), '..', 'knowledge_base.json')

with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)
with open(KB_PATH, encoding='utf-8') as f:
    kb = json.load(f)

LOGOS = set(kb['logograms'].keys())
plant_roots = {r: d['herbal_folio'] for r, d in kb['roots'].items() if d.get('herbal_folio')}

# Also detect plant roots with prefix stripping
def find_plant_refs(words):
    """Find all plant references in a word list (with prefix stripping)."""
    refs = []
    for w in words:
        eva = w['eva_primary']
        if eva in LOGOS: continue
        root = (w.get('morphology') or {}).get('root', '')

        # Direct root match
        if root in plant_roots:
            refs.append(plant_roots[root])
            continue

        # Prefix stripping
        for pfx in ['qo','op','ot','ok','sh','ch','p','t','k','f','o','d','l','s']:
            if eva.startswith(pfx) and len(eva) > len(pfx) + 1:
                stripped = eva[len(pfx):]
                # Check stripped as root
                if stripped in plant_roots:
                    refs.append(plant_roots[stripped])
                    break
                # Strip suffix too
                for suf in ['edy','eedy','eey','ey','ol','al','ar','or','dy','am']:
                    if stripped.endswith(suf) and len(stripped) > len(suf) + 1:
                        inner = stripped[:-len(suf)]
                        if inner in plant_roots:
                            refs.append(plant_roots[inner])
                            break
    return refs

# ================================================================
# 1. PHARMA → HERBAL cross-references
# ================================================================
print('=' * 70)
print('1. PHARMA RECIPES → HERBAL FOLIOS')
print('=' * 70)

pharma_to_herbal = {}
herbal_usage = defaultdict(list)  # herbal_folio → [pharma_blocks]

for fid, folio in sorted(vms['folios'].items()):
    if folio['metadata']['section'] != 'pharma': continue
    for block in folio['blocks']:
        if not block.get('separator'): continue
        words = [w for line in block['lines'] for w in line['words']]
        refs = find_plant_refs(words)
        unique_refs = sorted(set(refs))

        bid = block.get('block_id', '')
        pharma_to_herbal[bid] = {
            'folio': fid,
            'n_words': len(words),
            'herbal_refs': unique_refs,
            'n_refs': len(unique_refs),
            'ref_counts': dict(Counter(refs)),
        }

        for href in unique_refs:
            herbal_usage[href].append(bid)

# Stats
n_with_refs = sum(1 for v in pharma_to_herbal.values() if v['n_refs'] > 0)
print(f'\n  {len(pharma_to_herbal)} pharma blocks')
print(f'  {n_with_refs} with herbal references ({n_with_refs*100//len(pharma_to_herbal)}%)')
print(f'  {len(herbal_usage)} herbal folios referenced')

# Distribution of refs per block
ref_counts = [v['n_refs'] for v in pharma_to_herbal.values()]
ref_dist = Counter(ref_counts)
print(f'\n  Herbal refs per block:')
for n in sorted(ref_dist.keys()):
    print(f'    {n} refs: {ref_dist[n]} blocks')

# Top referenced herbal folios
print(f'\n  Most referenced herbal folios:')
for href in sorted(herbal_usage.keys(), key=lambda hr: -len(herbal_usage[hr])):
    n = len(herbal_usage[href])
    root = next((r for r, f in plant_roots.items() if f == href), '?')
    bot = kb['roots'].get(root, {}).get('botanical_id', {})
    species = (bot or {}).get('species', '?')
    print(f'    {href:8s} (root={root:8s}): {n:3d} pharma blocks → {species}')

# ================================================================
# 2. PLANT CO-OCCURRENCE — which plants appear TOGETHER?
# ================================================================
print(f'\n{"="*70}')
print('2. PLANT CO-OCCURRENCE — quelles plantes ensemble?')
print('=' * 70)

pair_count = Counter()
for bid, info in pharma_to_herbal.items():
    refs = info['herbal_refs']
    for i, a in enumerate(refs):
        for b in refs[i+1:]:
            pair = tuple(sorted([a, b]))
            pair_count[pair] += 1

print(f'\n  {len(pair_count)} paires de plantes')
print(f'\n  TOP 20 paires les plus fréquentes:')
for (a, b), count in pair_count.most_common(20):
    root_a = next((r for r, f in plant_roots.items() if f == a), '?')
    root_b = next((r for r, f in plant_roots.items() if f == b), '?')
    print(f'    {a}({root_a:6s}) + {b}({root_b:6s}): {count:3d} recettes ensemble')

# ================================================================
# 3. BALNEA → HERBAL cross-references
# ================================================================
print(f'\n{"="*70}')
print('3. BALNEA → HERBAL (mêmes plantes?)')
print('=' * 70)

balnea_refs = defaultdict(int)
for fid, folio in vms['folios'].items():
    if folio['metadata']['section'] != 'balnea': continue
    for block in folio['blocks']:
        words = [w for line in block['lines'] for w in line['words']]
        refs = find_plant_refs(words)
        for r in set(refs):
            balnea_refs[r] += 1

print(f'\n  Herbal folios referenced from balnea:')
for href in sorted(balnea_refs.keys(), key=lambda h: -balnea_refs[h]):
    pharma_n = len(herbal_usage.get(href, []))
    balnea_n = balnea_refs[href]
    root = next((r for r, f in plant_roots.items() if f == href), '?')
    print(f'    {href:8s} (root={root:8s}): balnea={balnea_n:3d} pharma={pharma_n:3d}')

# ================================================================
# 4. HERBAL FOLIOS NEVER REFERENCED — orphan pages?
# ================================================================
print(f'\n{"="*70}')
print('4. HERBAL FOLIOS JAMAIS RÉFÉRENCÉS (orphelins?)')
print('=' * 70)

all_herbal_folios = set()
for fid, folio in vms['folios'].items():
    if 'herbal' in folio['metadata']['section']:
        all_herbal_folios.add(fid)

referenced = set(herbal_usage.keys()) | set(balnea_refs.keys())
orphans = all_herbal_folios - referenced

print(f'\n  Total herbal folios: {len(all_herbal_folios)}')
print(f'  Referenced in pharma/balnea: {len(referenced)}')
print(f'  ORPHANS (never referenced): {len(orphans)}')
if orphans:
    for fid in sorted(orphans):
        n_words = sum(1 for b in vms['folios'][fid]['blocks']
                      for l in b['lines'] for w in l['words'])
        print(f'    {fid} ({n_words} mots)')

# ================================================================
# 5. THERAPEUTIC CLUSTERS — groups of co-occurring plants
# ================================================================
print(f'\n{"="*70}')
print('5. CLUSTERS THÉRAPEUTIQUES')
print('=' * 70)

# Build adjacency matrix
all_plants = sorted(set(h for pair in pair_count for h in pair))
adj = defaultdict(Counter)
for (a, b), count in pair_count.items():
    adj[a][b] += count
    adj[b][a] += count

# Simple clustering: find groups of plants that always appear together
print(f'\n  Plants with strongest bonds (co-occur in 50%+ of their recipes):')
for plant in sorted(all_plants, key=lambda p: -len(herbal_usage.get(p, []))):
    n_recipes = len(herbal_usage.get(plant, []))
    if n_recipes < 5: continue

    bonded = []
    for other, co_count in adj[plant].most_common(5):
        bond_pct = co_count * 100 // n_recipes
        if bond_pct >= 30:
            bonded.append(f'{other}({bond_pct}%)')

    if bonded:
        root = next((r for r, f in plant_roots.items() if f == plant), '?')
        print(f'    {plant}({root:6s}, {n_recipes:3d}rx) bonds: {", ".join(bonded)}')

# ================================================================
# 6. RECIPE EXAMPLE — full cross-reference for f103r_B01
# ================================================================
print(f'\n{"="*70}')
print('6. EXEMPLE: f103r_B01 — carte de consultation')
print('=' * 70)

b01 = pharma_to_herbal.get('f103r_B01', {})
if b01:
    print(f'\n  Recette f103r_B01 ({b01["n_words"]} mots)')
    print(f'  Références herbal: {b01["herbal_refs"]}')
    print(f'\n  Pour préparer cette recette, consulter:')
    for href in b01['herbal_refs']:
        root = next((r for r, f in plant_roots.items() if f == href), '?')
        count = b01['ref_counts'].get(href, 0)
        bot = kb['roots'].get(root, {}).get('botanical_id', {})
        species = (bot or {}).get('species', '?')
        print(f'    📖 Folio {href} (root={root}, {count}x) → {species}')

    # What OTHER recipes use the SAME plants?
    similar = Counter()
    for href in b01['herbal_refs']:
        for other_bid in herbal_usage.get(href, []):
            if other_bid != 'f103r_B01':
                similar[other_bid] += 1

    print(f'\n  Recettes SIMILAIRES (mêmes plantes):')
    for other_bid, shared in similar.most_common(10):
        total_other = pharma_to_herbal[other_bid]['n_refs']
        print(f'    {other_bid}: {shared}/{len(b01["herbal_refs"])} plantes en commun '
              f'(sur {total_other} refs)')

# Save
results = {
    'pharma_to_herbal': pharma_to_herbal,
    'herbal_usage': {k: v for k, v in herbal_usage.items()},
    'plant_pairs': [{'pair': list(p), 'count': c} for p, c in pair_count.most_common(50)],
    'orphan_folios': sorted(orphans),
    'n_referenced': len(referenced),
    'n_orphans': len(orphans),
}

with open(os.path.join(os.path.dirname(__file__), 'cross_reference_map.json'), 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print('\nSaved cross_reference_map.json')
