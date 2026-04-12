"""
ATTACK C — Crib Aurea Corrigé
Match each of the 18 f103r recipes against 150 AN recipes by SIGNATURE.

Signature = (n_tokens, n_ingredients, n_doses, ratio_ingr/total, ratio_dose/total)

If a VMS recipe matches an AN recipe by size/structure, we align word-by-word.
Special focus: does any VMS recipe match the Aurea Alexandrina?

Output: results/crib_signature_match.json
"""
import json, sys, io, os, math
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.dirname(__file__)
VMS_PATH = os.path.join(BASE, '..', '..', 'vms', 'vms_structured.json')
AN_PATH = os.path.join(BASE, '..', '..', '..', 'attacks', 'RECIPE_DATASET', 'S01_AN.json')
AUREA_PATH = os.path.join(BASE, '..', '..', '..', 'attacks', 'RECIPE_DATASET', 'S03_AUREA.json')
RESULTS = os.path.join(BASE, 'results')
os.makedirs(RESULTS, exist_ok=True)

LOGOGRAMS = {'o','l','d','r','v','x','k','m','f','t','y','c','s','sh','p','air','ch'}

# ================================================================
# 1. Load VMS f103r recipes
# ================================================================
with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)

vms_recipes = []
f103r = vms['folios']['f103r']
for b in f103r['blocks']:
    words = [w for line in b['lines'] for w in line['words']]
    n_total = len(words)
    n_logo = sum(1 for w in words if w['eva_primary'] in LOGOGRAMS)
    n_dose = sum(1 for w in words if w.get('morphology', {}).get('i_count') is not None)
    n_other = n_total - n_logo - n_dose

    # Morphological breakdown
    roots = [w.get('morphology', {}).get('root', '') for w in words]
    unique_roots = len(set(r for r in roots if r))

    vms_recipes.append({
        'id': b['block_id'],
        'n_tokens': n_total,
        'n_logo': n_logo,
        'n_dose': n_dose,
        'n_content': n_other,  # potential ingredients + verbs + grammar
        'unique_roots': unique_roots,
        'ratio_dose': n_dose / max(n_total, 1),
        'ratio_logo': n_logo / max(n_total, 1),
        'words': [{'eva': w['eva_primary'],
                    'root': w.get('morphology', {}).get('root', ''),
                    'suffix': w.get('morphology', {}).get('suffix', ''),
                    'i_count': w.get('morphology', {}).get('i_count'),
                    'is_logo': w['eva_primary'] in LOGOGRAMS}
                   for w in words],
    })

# ================================================================
# 2. Load AN recipes (150) + Aurea
# ================================================================
with open(AN_PATH, encoding='utf-8') as f:
    an_data = json.load(f)

with open(AUREA_PATH, encoding='utf-8') as f:
    aurea_data = json.load(f)

an_recipes = []
for entry in an_data['entries']:
    s = entry['summary']
    td = s['type_distribution']
    n_ingr = td.get('INGR', 0)
    n_dose = td.get('DOSE', 0) + td.get('QTY', 0)
    n_verb = td.get('VERB', 0)
    n_gram = td.get('GRAM', 0) + td.get('CONJ', 0) + td.get('PREP', 0)
    n_total = s['n_tokens']

    an_recipes.append({
        'id': entry['id'],
        'name': entry['name'],
        'type': entry.get('type', ''),
        'n_tokens': n_total,
        'n_ingr': n_ingr,
        'n_dose': n_dose,
        'n_verb': n_verb,
        'n_gram': n_gram,
        'ratio_ingr': n_ingr / max(n_total, 1),
        'ratio_dose': n_dose / max(n_total, 1),
        'tokens': entry['tokens'],
    })

# Aurea separately
au = aurea_data['entries'][0]
aurea_sig = {
    'id': 'AUREA',
    'name': au['name'],
    'n_tokens': au['summary']['n_tokens'],
    'n_ingr': au['summary']['type_distribution'].get('INGR', 0),
    'n_dose': au['summary']['type_distribution'].get('DOSE', 0) + au['summary']['type_distribution'].get('QTY', 0),
    'ratio_ingr': au['summary']['type_distribution'].get('INGR', 0) / max(au['summary']['n_tokens'], 1),
    'ratio_dose': (au['summary']['type_distribution'].get('DOSE', 0) + au['summary']['type_distribution'].get('QTY', 0)) / max(au['summary']['n_tokens'], 1),
    'tokens': au['tokens'],
}

# ================================================================
# 3. Signature matching
# ================================================================
# Distance function: normalized euclidean on (n_tokens, ratio_dose, ratio_ingr)
# For VMS, we don't know n_ingr directly, so we use n_content as proxy for ingr+verb+gram

def sig_distance(vms_r, an_r):
    """Distance between VMS recipe and AN recipe signatures."""
    # Token count similarity (normalized by max)
    max_tok = max(vms_r['n_tokens'], an_r['n_tokens'], 1)
    d_tok = abs(vms_r['n_tokens'] - an_r['n_tokens']) / max_tok

    # Dose ratio similarity
    d_dose = abs(vms_r['ratio_dose'] - an_r['ratio_dose'])

    # Content ratio: VMS content words should match AN ingr+verb+gram
    vms_content_ratio = vms_r['n_content'] / max(vms_r['n_tokens'], 1)
    an_content_ratio = (an_r['n_ingr'] + an_r.get('n_verb', 0) + an_r.get('n_gram', 0)) / max(an_r['n_tokens'], 1)
    d_content = abs(vms_content_ratio - an_content_ratio)

    return math.sqrt(d_tok**2 + d_dose**2 + d_content**2)


print('=' * 70)
print('ATTACK C: CRIB AUREA CORRIGÉ — 18 VMS RECIPES vs 150 AN RECIPES')
print('=' * 70)

# ================================================================
# 4. For each VMS recipe, find top 5 AN matches
# ================================================================
all_matches = []

for vr in vms_recipes:
    distances = []
    for ar in an_recipes:
        d = sig_distance(vr, ar)
        distances.append((d, ar))

    # Also check Aurea
    d_aurea = sig_distance(vr, aurea_sig)
    distances.append((d_aurea, aurea_sig))

    distances.sort(key=lambda x: x[0])
    top5 = distances[:5]

    print(f'\n{vr["id"]}: {vr["n_tokens"]}w ({vr["n_dose"]}dose, {vr["n_logo"]}logo, {vr["n_content"]}content)')
    for rank, (d, ar) in enumerate(top5):
        is_aurea = ' *** AUREA ***' if ar['id'] == 'AUREA' else ''
        ingr_info = f'{ar.get("n_ingr","?")}ingr' if 'n_ingr' in ar else ''
        print(f'  #{rank+1} d={d:.3f} {ar["id"]} "{ar["name"][:40]}" '
              f'({ar["n_tokens"]}tok, {ingr_info}, {ar.get("n_dose","?")}dose){is_aurea}')

    match_entry = {
        'vms_id': vr['id'],
        'vms_sig': {k: vr[k] for k in ['n_tokens', 'n_logo', 'n_dose', 'n_content', 'ratio_dose']},
        'top5': [{
            'an_id': ar['id'],
            'an_name': ar.get('name', ''),
            'distance': round(d, 4),
            'an_sig': {k: ar[k] for k in ['n_tokens', 'n_ingr', 'n_dose', 'ratio_ingr', 'ratio_dose'] if k in ar},
        } for d, ar in top5],
        'aurea_distance': round(d_aurea, 4),
        'aurea_rank': next((i+1 for i, (dd, ar) in enumerate(distances) if ar['id'] == 'AUREA'), -1),
    }
    all_matches.append(match_entry)

# ================================================================
# 5. AUREA FOCUS: which VMS recipe is closest to Aurea?
# ================================================================
print('\n' + '=' * 70)
print('AUREA FOCUS: Which VMS recipe best matches Aurea Alexandrina?')
print(f'Aurea: {aurea_sig["n_tokens"]}tok, {aurea_sig["n_ingr"]}ingr, {aurea_sig["n_dose"]}dose')
print('=' * 70)

aurea_matches = [(m['aurea_distance'], m['vms_id'], m['vms_sig']) for m in all_matches]
aurea_matches.sort()

for d, vid, sig in aurea_matches[:5]:
    print(f'  d={d:.3f} {vid}: {sig["n_tokens"]}tok, {sig["n_dose"]}dose, {sig["n_content"]}content')

# ================================================================
# 6. BEST OVERALL MATCHES (d < 0.15)
# ================================================================
print('\n' + '=' * 70)
print('BEST MATCHES (d < 0.15)')
print('=' * 70)

best = []
for m in all_matches:
    for t in m['top5']:
        if t['distance'] < 0.15:
            best.append((t['distance'], m['vms_id'], t['an_id'], t['an_name'],
                         m['vms_sig'], t['an_sig']))

best.sort()
for d, vid, aid, aname, vsig, asig in best[:20]:
    print(f'  d={d:.4f} {vid} ↔ {aid} "{aname[:35]}"')
    print(f'    VMS: {vsig["n_tokens"]}tok {vsig["n_dose"]}dose {vsig["n_content"]}cont')
    print(f'    AN:  {asig["n_tokens"]}tok {asig["n_dose"]}dose {asig["n_ingr"]}ingr')

# ================================================================
# 7. SIZE DISTRIBUTION COMPARISON
# ================================================================
print('\n' + '=' * 70)
print('SIZE DISTRIBUTIONS')
print('=' * 70)

vms_sizes = sorted([vr['n_tokens'] for vr in vms_recipes])
an_sizes = sorted([ar['n_tokens'] for ar in an_recipes])

print(f'VMS f103r: min={min(vms_sizes)}, max={max(vms_sizes)}, '
      f'median={vms_sizes[len(vms_sizes)//2]}, mean={sum(vms_sizes)/len(vms_sizes):.1f}')
print(f'AN 150:    min={min(an_sizes)}, max={max(an_sizes)}, '
      f'median={an_sizes[len(an_sizes)//2]}, mean={sum(an_sizes)/len(an_sizes):.1f}')

# Token count histogram
print('\nVMS token counts:', vms_sizes)
print('AN token count buckets:')
for lo, hi in [(0,20),(20,40),(40,60),(60,80),(80,100),(100,150),(150,200),(200,300),(300,500)]:
    n = sum(1 for s in an_sizes if lo <= s < hi)
    if n: print(f'  [{lo}-{hi}): {n} recipes')

# ================================================================
# Save results
# ================================================================
results = {
    'vms_recipes': [{k: v for k, v in vr.items() if k != 'words'} for vr in vms_recipes],
    'aurea_sig': {k: v for k, v in aurea_sig.items() if k != 'tokens'},
    'matches': all_matches,
    'best_matches_under_015': [
        {'distance': d, 'vms_id': vid, 'an_id': aid, 'an_name': aname}
        for d, vid, aid, aname, _, _ in best[:20]
    ],
    'aurea_ranking': [
        {'distance': d, 'vms_id': vid} for d, vid, _ in aurea_matches
    ],
}

with open(os.path.join(RESULTS, 'crib_signature_match.json'), 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print('\nSaved crib_signature_match.json')
