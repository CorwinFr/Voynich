"""
STEP 2 — Encode VMS pharma blocks as type signatures.
Uses reclassified types (INGR* → I).
"""
import json, sys, io, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DECODE_PATH = os.path.join(os.path.dirname(__file__), '..', 'session_11', 'structural_decode.json')
RECLASS_PATH = os.path.join(os.path.dirname(__file__), '..', 'session_11', 'reclassified_analysis.json')
RESULTS = os.path.join(os.path.dirname(__file__), 'results')

with open(DECODE_PATH, encoding='utf-8') as f:
    decode = json.load(f)
with open(RECLASS_PATH, encoding='utf-8') as f:
    reclass = json.load(f)

reclassified_codes = reclass.get('reclassified_codes', {})

TYPE_MAP = {
    'VERB': 'V', 'LOGO': 'V',  # logograms like recipe/misce = verbs
    'PLANT': 'I', 'INGR': 'I', 'INGR*': 'I', 'INGR?': 'I',
    'DOSE': 'D', 'DOSE_MORPH': 'D',
    'FUNC': None, 'UNK': None, 'PREP_FORM': 'V', 'TEMPORAL': None,
}

# Special logograms that are NOT verbs
LOGO_INGR = {'ac', 'vel', 'crux', 'air'}  # these are more like ingredients/connectors
LOGO_DOSE = set()
LOGO_VERB = {'recipe', 'misce', 'per', 'usque', 'est', 'et', 'de', 'in', 'cum', 'se', 'ci'}

signatures = []

for block in decode['blocks']:
    # Only pharma
    if not any(block['folio'].startswith(f'f{n}') for n in
               ['103','104','105','106','107','108','111','112','113','114','115','116']):
        continue

    sig = []
    sig_with_info = []
    roots = []

    for dw in block['decoded']:
        code = dw['code']
        base_code = code.split('.')[0]
        eva = dw['eva']
        suffix = dw.get('suffix', '')

        # Determine type
        orig_type = dw['type']

        # Apply reclassification
        if base_code in reclassified_codes:
            rtype = reclassified_codes[base_code]
            if rtype in ('INGR*', 'INGR?'):
                orig_type = rtype

        t = TYPE_MAP.get(orig_type)

        # Special handling for logos
        if orig_type == 'LOGO':
            detail = dw.get('detail', '')
            if detail in LOGO_VERB:
                t = None  # skip grammar logos (de, in, cum, et, est, se)
            else:
                t = 'I'  # treat as ingredient-like

        if t is None:
            continue

        sig.append(t)
        sig_with_info.append({
            'type': t,
            'eva': eva,
            'code': code,
            'length': len(eva),
            'suffix': suffix,
        })
        if t == 'I':
            roots.append(dw.get('eva', ''))

    if not sig:
        continue

    signatures.append({
        'id': block['block_id'],
        'folio': block['folio'],
        'signature': ''.join(sig),
        'tokens': sig_with_info,
        'roots': roots,
        'n_ingr': sum(1 for s in sig if s == 'I'),
        'n_dose': sum(1 for s in sig if s == 'D'),
        'n_verb': sum(1 for s in sig if s == 'V'),
        'n_total': len(sig),
    })

print(f'VMS signatures: {len(signatures)}')
print(f'  Avg length: {sum(s["n_total"] for s in signatures)//max(len(signatures),1)}')
print(f'  Avg ingr: {sum(s["n_ingr"] for s in signatures)//max(len(signatures),1)}')
print(f'  Avg dose: {sum(s["n_dose"] for s in signatures)//max(len(signatures),1)}')

from collections import Counter
size_dist = Counter(s['n_total'] // 5 * 5 for s in signatures)
print(f'\n  Size distribution (bucket of 5):')
for bucket in sorted(size_dist.keys()):
    print(f'    {bucket}-{bucket+4}: {size_dist[bucket]} blocks')

with open(os.path.join(RESULTS, 'vms_signatures.json'), 'w', encoding='utf-8') as f:
    json.dump(signatures, f, indent=2, ensure_ascii=False)
print(f'\nSaved vms_signatures.json')
