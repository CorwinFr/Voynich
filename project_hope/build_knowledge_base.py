"""
BUILD KNOWLEDGE BASE — Consolidate ALL decoding discoveries into one JSON.

Sources:
- Logograms: confirmed session 6 + w2v session 10
- Roots: plant_crossref (session 9) + w2v candidates (session 10)
- Suffixes: datasets/03_suffixes.json (session 7)
- Botanical IDs: data/botanical_anchors.json + datasets/10_botanical_ids.json
- AN constraints: attacks/RECIPE_DATASET/S01_AN.json + R01-R08
- Gallows: session 10 block-initial analysis
- Star colors: session 10 visual observation
"""
import json, sys, io, os
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.dirname(__file__)
VMS_PATH = os.path.join(BASE, 'vms', 'vms_structured.json')
CROSSREF_PATH = os.path.join(BASE, 'session_09', 'results', 'plant_crossref_complete.json')
W2V_PATH = os.path.join(BASE, 'session_10', 'B_gpu_embeddings', 'results', 'w2v_procrustes.json')
CRACK_PATH = os.path.join(BASE, 'session_10', 'F_crack', 'results', 'crack_roots.json')
SUFFIXES_PATH = os.path.join(BASE, '..', 'datasets', '03_suffixes.json')
BOTANICAL_PATH = os.path.join(BASE, '..', 'data', 'botanical_anchors.json')
BOTANICAL_IDS_PATH = os.path.join(BASE, '..', 'datasets', '10_botanical_ids.json')
AN_PATH = os.path.join(BASE, '..', 'attacks', 'RECIPE_DATASET', 'S01_AN.json')

LOGOGRAMS_TABLE = {
    'o': 'ac', 'l': 'se', 'd': 'de', 'r': 'recipe', 'v': 'vel',
    'x': 'crux', 'k': 'cum', 'm': 'misce', 'f': 'per', 't': 'et',
    'y': 'in', 'c': 'cum', 's': 'est', 'sh': 'ci', 'p': 'usque',
    'ch': 'cum', 'air': 'air', 'h': '(muet)',
}
LOGOGRAM_SET = set(LOGOGRAMS_TABLE.keys())

kb = {}

# ================================================================
# 1. LOGOGRAMS
# ================================================================
print('1. Logograms...')
kb['logograms'] = {
    eva: {'latin': lat, 'confidence': 'confirmed', 'source': 'bifolio+w2v'}
    for eva, lat in LOGOGRAMS_TABLE.items()
}
print(f'   {len(kb["logograms"])} logograms')

# ================================================================
# 2. VMS DATA — root frequencies by section
# ================================================================
print('2. VMS root profiles...')
with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)

root_data = defaultdict(lambda: {
    'pharma': 0, 'herbal': 0, 'balnea': 0, 'astro': 0, 'other': 0,
    'total': 0, 'words': set(), 'suffixes': Counter(),
    'block_initial': 0, 'block_other': 0,
})

for fid, folio in vms['folios'].items():
    section = folio['metadata']['section']
    sec_key = section if section in ('pharma', 'balnea', 'astro') else \
              'herbal' if 'herbal' in section else 'other'

    for block in folio['blocks']:
        words = [w for line in block['lines'] for w in line['words']]
        for i, w in enumerate(words):
            eva = w['eva_primary']
            if eva in LOGOGRAM_SET: continue
            morph = w.get('morphology') or {}
            root = morph.get('root', '')
            suffix = morph.get('suffix', '') or ''
            if not root: continue

            rd = root_data[root]
            rd[sec_key] += 1
            rd['total'] += 1
            rd['words'].add(eva)
            if suffix: rd['suffixes'][suffix] += 1
            if i == 0:
                rd['block_initial'] += 1
            else:
                rd['block_other'] += 1

# Convert sets/counters to serializable
roots = {}
for root, rd in root_data.items():
    if rd['total'] < 3: continue  # skip very rare
    roots[root] = {
        'pharma_freq': rd['pharma'],
        'herbal_freq': rd['herbal'],
        'balnea_freq': rd['balnea'],
        'total_freq': rd['total'],
        'words': sorted(rd['words']),
        'suffixes': dict(rd['suffixes'].most_common(5)),
        'block_initial_pct': round(rd['block_initial'] * 100 / max(rd['total'], 1)),
        'herbal_folio': None,
        'botanical_id': None,
        'w2v_candidates': [],
        'crack_status': 'unknown',
        'cracked_latin': None,
    }

print(f'   {len(roots)} roots (freq >= 3)')

# ================================================================
# 3. HERBAL CROSSREF — root → folio mapping
# ================================================================
print('3. Herbal crossref...')
with open(CROSSREF_PATH, encoding='utf-8') as f:
    crossref = json.load(f)

for entry in crossref['crossref']:
    root = entry['root']
    if root in roots:
        roots[root]['herbal_folio'] = entry['folio']

n_with_folio = sum(1 for r in roots.values() if r['herbal_folio'])
print(f'   {n_with_folio} roots with herbal folio')

# ================================================================
# 4. BOTANICAL IDS — folio → species
# ================================================================
print('4. Botanical IDs...')
botanical = {}

if os.path.exists(BOTANICAL_PATH):
    with open(BOTANICAL_PATH, encoding='utf-8') as f:
        anchors_data = json.load(f)
    anchor_list = anchors_data.get('anchors', anchors_data) if isinstance(anchors_data, dict) else anchors_data
    for entry in anchor_list:
        fid = entry.get('folio', '')
        botanical[fid] = {
            'species': entry.get('proposed_species', ''),
            'common_name': entry.get('common_name', ''),
            'confidence': entry.get('confidence_score', 0),
            'proposers': entry.get('proposers', ''),
            'medieval_latin': entry.get('medieval_latin_name', ''),
        }

if os.path.exists(BOTANICAL_IDS_PATH):
    with open(BOTANICAL_IDS_PATH, encoding='utf-8') as f:
        bot_ids_data = json.load(f)
    bot_entries = bot_ids_data.get('entries', []) if isinstance(bot_ids_data, dict) else bot_ids_data
    for entry in bot_entries:
        fid = entry.get('folio', '')
        if fid not in botanical:
            botanical[fid] = {
                'species': entry.get('species', ''),
                'common_name': entry.get('common_name', ''),
                'confidence': {'high': 0.9, 'medium-high': 0.75, 'medium': 0.6,
                              'low-medium': 0.4, 'low': 0.2}.get(entry.get('confidence', ''), 0.3),
                'proposers': entry.get('proposer', ''),
                'medieval_latin': entry.get('medieval_latin', ''),
            }

# Link botanical to roots
for root, data in roots.items():
    folio = data.get('herbal_folio')
    if folio and folio in botanical:
        data['botanical_id'] = botanical[folio]

n_with_bot = sum(1 for r in roots.values() if r['botanical_id'])
print(f'   {len(botanical)} folios with botanical IDs')
print(f'   {n_with_bot} roots with botanical identification')

# ================================================================
# 5. W2V CANDIDATES
# ================================================================
print('5. W2V candidates...')
if os.path.exists(W2V_PATH):
    with open(W2V_PATH, encoding='utf-8') as f:
        w2v = json.load(f)
    nn = w2v.get('nn_results', {})
    for eva_word, data in nn.items():
        # Find which root this word belongs to
        for root, rd in roots.items():
            if eva_word in rd['words']:
                top3 = data.get('neighbors', [])[:3]
                rd['w2v_candidates'] = [
                    {'latin': n['latin'], 'cosine': n['cosine']}
                    for n in top3
                ]
                break
    n_with_w2v = sum(1 for r in roots.values() if r['w2v_candidates'])
    print(f'   {n_with_w2v} roots with w2v candidates')

# Crack candidates
if os.path.exists(CRACK_PATH):
    with open(CRACK_PATH, encoding='utf-8') as f:
        crack = json.load(f)
    for entry in crack.get('best_per_root', []):
        root = entry['root']
        if root in roots:
            roots[root]['crack_candidates'] = [{
                'latin': entry['latin'],
                'score': entry['score'],
                'w2v': entry['w2v'],
            }]

# ================================================================
# 6. SUFFIXES
# ================================================================
print('6. Suffixes...')
suffixes = {}
if os.path.exists(SUFFIXES_PATH):
    with open(SUFFIXES_PATH, encoding='utf-8') as f:
        suf_data = json.load(f)
    # Handle dict with 'entries' key
    suf_list = suf_data.get('entries', suf_data) if isinstance(suf_data, dict) else suf_data
    if isinstance(suf_list, list):
        for entry in suf_list:
            name = entry.get('suffix', entry.get('name', ''))
            suffixes[name] = {
                'count': entry.get('total_count', entry.get('count', 0)),
                'avg_position': entry.get('avg_line_position', entry.get('avg_position', 0)),
                'pct_line_start': entry.get('pct_line_start', 0),
                'pct_line_end': entry.get('pct_line_end', 0),
                'pct_herbal': entry.get('pct_herbal', 0),
                'pct_pharma': entry.get('pct_pharma', 0),
                'pct_balnea': entry.get('pct_balnea', 0),
                'hypothesis': entry.get('hypothesized_role', ''),
                'latin_case': None,
            }

if not suffixes:
    # Build from VMS data
    for root, rd in roots.items():
        for suf, count in rd.get('suffixes', {}).items():
            if suf not in suffixes:
                suffixes[suf] = {'count': 0, 'latin_case': None}
            suffixes[suf]['count'] += count

print(f'   {len(suffixes)} suffixes')

# ================================================================
# 7. GALLOWS
# ================================================================
print('7. Gallows...')
gallows = {}
for g in ['p', 't', 'k', 'f']:
    initial = sum(1 for r, rd in roots.items()
                  if any(w.startswith(g) for w in rd['words']) and rd['block_initial_pct'] > 50)
    total_initial = sum(rd['block_initial'] for r, rd in root_data.items()
                       if any(w.startswith(g) for w in rd['words']))
    total_other = sum(rd['block_other'] for r, rd in root_data.items()
                      if any(w.startswith(g) for w in rd['words']))
    gallows[g] = {
        'freq_initial': total_initial,
        'freq_other': total_other,
        'hypothesis': {'p': 'Recipe', 't': 'Accipe', 'k': 'Misce', 'f': 'Fiat'}.get(g, '?'),
    }

# ================================================================
# 8. STAR COLORS
# ================================================================
print('8. Star colors...')
star_colors = {
    'f103r': ['R','V','V','R','V','R','V','V','R','V','V','R','V','R','V','V','R','V','V'],
    'f103v': ['R','V','R','V','R','V','R','V','R','V','R','V','R','V'],
}

# ================================================================
# 9. AN CONSTRAINTS
# ================================================================
print('9. AN constraints...')
an_constraints = {}
if os.path.exists(AN_PATH):
    with open(AN_PATH, encoding='utf-8') as f:
        an = json.load(f)

    # Top ingredients
    ingr_freq = Counter()
    ingr_pairs = Counter()
    for entry in an['entries']:
        ingr_in_recipe = []
        for tok in entry['tokens']:
            if tok['type'] == 'INGR':
                name = tok['raw'].lower()
                ingr_freq[name] += 1
                ingr_in_recipe.append(name)
        for i, a in enumerate(sorted(set(ingr_in_recipe))):
            for b in sorted(set(ingr_in_recipe)):
                if a < b:
                    ingr_pairs[(a, b)] += 1

    an_constraints = {
        'n_recipes': len(an['entries']),
        'top_ingredients': [
            {'latin': name, 'freq': freq}
            for name, freq in ingr_freq.most_common(50)
        ],
        'common_pairs': [
            {'pair': list(pair), 'freq': freq}
            for pair, freq in ingr_pairs.most_common(30)
        ],
        'binding_agents': ['mel', 'aqua', 'vinum', 'manna', 'succus'],
    }

print(f'   {an_constraints.get("n_recipes", 0)} AN recipes')
print(f'   {len(an_constraints.get("top_ingredients", []))} top ingredients')

# ================================================================
# ASSEMBLE AND SAVE
# ================================================================
kb['roots'] = roots
kb['suffixes'] = suffixes
kb['gallows'] = gallows
kb['star_colors'] = star_colors
kb['an_constraints'] = an_constraints
kb['metadata'] = {
    'version': '1.0',
    'built': '2026-04-12',
    'sessions': '1-10',
    'hypothesis': 'Personal Tironian notes system',
    'n_roots': len(roots),
    'n_roots_with_folio': n_with_folio,
    'n_roots_with_botanical': n_with_bot,
    'n_logograms': len(kb['logograms']),
    'n_suffixes': len(suffixes),
}

out_path = os.path.join(BASE, 'knowledge_base.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(kb, f, indent=2, ensure_ascii=False)

# Summary
print('\n' + '=' * 70)
print('KNOWLEDGE BASE BUILT')
print('=' * 70)
print(f'  Logograms:    {len(kb["logograms"])}')
print(f'  Roots:        {len(roots)}')
print(f'    with folio: {n_with_folio}')
print(f'    with bot ID:{n_with_bot}')
print(f'  Suffixes:     {len(suffixes)}')
print(f'  Gallows:      {len(gallows)}')
print(f'  AN recipes:   {an_constraints.get("n_recipes", 0)}')
print(f'  Star colors:  {len(star_colors)} folios')
print(f'\nSaved: {out_path}')
