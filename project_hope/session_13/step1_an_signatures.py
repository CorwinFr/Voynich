"""
STEP 1 — Encode AN recipes as type signatures.
"""
import json, sys, io, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

AN_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'attacks', 'RECIPE_DATASET', 'S01_AN.json')
RESULTS = os.path.join(os.path.dirname(__file__), 'results')

with open(AN_PATH, encoding='utf-8') as f:
    an = json.load(f)

TYPE_MAP = {
    'VERB': 'V', 'INGR': 'I', 'DOSE': 'D', 'QTY': 'D', 'UNIT': 'D',
    'GRAM': None, 'CONJ': None, 'PREP': None, 'COP': None,
    'ADJ': 'I', 'PART': 'I', 'FORM': 'V', 'TOOL': 'I',
}

signatures = []

for entry in an['entries']:
    # Build signature (skip grammar)
    sig = []
    sig_with_info = []
    ingredients = []

    for tok in entry['tokens']:
        t = TYPE_MAP.get(tok['type'])
        if t is None:
            continue
        sig.append(t)
        sig_with_info.append({
            'type': t,
            'raw': tok['raw'],
            'ref': tok.get('ref', ''),
            'length': len(tok['raw']),
        })
        if t == 'I':
            ingredients.append(tok['raw'].lower())

    signatures.append({
        'id': entry['id'],
        'name': entry.get('name', ''),
        'signature': ''.join(sig),
        'tokens': sig_with_info,
        'ingredients': list(dict.fromkeys(ingredients)),  # unique, preserve order
        'n_ingr': sum(1 for s in sig if s == 'I'),
        'n_dose': sum(1 for s in sig if s == 'D'),
        'n_verb': sum(1 for s in sig if s == 'V'),
        'n_total': len(sig),
    })

# Stats
print(f'AN signatures: {len(signatures)}')
print(f'  Avg length: {sum(s["n_total"] for s in signatures)//len(signatures)}')
print(f'  Avg ingr: {sum(s["n_ingr"] for s in signatures)//len(signatures)}')
print(f'  Avg dose: {sum(s["n_dose"] for s in signatures)//len(signatures)}')

# Size distribution
from collections import Counter
size_dist = Counter(s['n_total'] // 10 * 10 for s in signatures)
print(f'\n  Size distribution (bucket of 10):')
for bucket in sorted(size_dist.keys()):
    print(f'    {bucket}-{bucket+9}: {size_dist[bucket]} recipes')

with open(os.path.join(RESULTS, 'an_signatures.json'), 'w', encoding='utf-8') as f:
    json.dump(signatures, f, indent=2, ensure_ascii=False)
print(f'\nSaved an_signatures.json')
