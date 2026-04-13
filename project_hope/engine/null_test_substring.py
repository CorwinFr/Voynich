"""
Null test: are herbal-pharma substring matches above random chance?
Picks random VMS words of same lengths as herbal roots, checks match rate.
Result: real=55%, null mean=25%, p=0.004
"""
import json, sys, io, random
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
BASE = os.path.dirname(os.path.dirname(__file__))
with open(os.path.join(BASE, 'vms', 'vms_structured.json'), encoding='utf-8') as f:
    vms = json.load(f)

LOGOS = {'o','l','d','r','v','x','k','m','f','t','y','c','s','sh','p','ch','air','h'}

herbal_roots = {}
for fid, folio in sorted(vms['folios'].items()):
    if 'herbal' not in folio['metadata']['section']: continue
    for block in folio['blocks']:
        for line in block['lines']:
            if line['words']:
                root = (line['words'][0].get('morphology') or {}).get('root', line['words'][0]['eva_primary'])
                if root and len(root) >= 3: herbal_roots[fid] = root
                break
        break

pharma_openers = []
for fid, folio in vms['folios'].items():
    if folio['metadata']['section'] != 'pharma': continue
    for block in folio['blocks']:
        if block['lines'] and block['lines'][0]['words']:
            pharma_openers.append(block['lines'][0]['words'][0]['eva_primary'])

real_matches = sum(1 for op in pharma_openers if any(r in op for r in herbal_roots.values() if len(r)>=3))
print(f'Real: {real_matches}/{len(pharma_openers)} = {real_matches*100//len(pharma_openers)}%')

all_words = list(set(w['eva_primary'] for fid, folio in vms['folios'].items()
    for block in folio['blocks'] for line in block['lines'] for w in line['words']
    if w['eva_primary'] not in LOGOS and len(w['eva_primary'])>=3))

lengths = [len(r) for r in herbal_roots.values()]
random.seed(42)
null = []
for _ in range(500):
    fakes = [random.choice([w for w in all_words if len(w)==l] or all_words)[:l] for l in lengths]
    null.append(sum(1 for op in pharma_openers if any(f in op for f in fakes if len(f)>=3)))

print(f'Null mean: {sum(null)/len(null):.1f} ({sum(null)/len(null)*100/len(pharma_openers):.1f}%)')
print(f'Null max: {max(null)}')
print(f'p-value: {sum(1 for n in null if n >= real_matches)/len(null)}')
