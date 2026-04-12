"""
FULL MACER ATTACK — All steps combined.

1. Profile every Macer chapter (plant, ingredients, qualities)
2. Profile every VMS herbal folio (roots, k/t ratio, suffixes)
3. Extract galenic qualities from Tacuinum (hot/cold/wet/dry + degree)
4. Test k/t vs galenic qualities
5. Cross-match Macer chapters ↔ VMS folios
6. Cross-validate with Sherwood botanical IDs
"""
import json, sys, io, os
import numpy as np
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

VMS_PATH = os.path.join(os.path.dirname(__file__), '..', 'vms', 'vms_structured.json')
MACER_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'attacks', 'RECIPE_DATASET', 'S05_MACER.json')
TAC_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'attacks', 'RECIPE_DATASET', 'S12_TACUINUM.json')
BOT_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'botanical_anchors.json')
RESULTS = os.path.join(os.path.dirname(__file__), 'results')

with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)
with open(MACER_PATH, encoding='utf-8') as f:
    macer = json.load(f)
with open(TAC_PATH, encoding='utf-8') as f:
    tac = json.load(f)

# Load botanical IDs
try:
    with open(BOT_PATH, encoding='utf-8') as f:
        bot_data = json.load(f)
    bot_anchors = {e['folio']: e for e in bot_data.get('anchors', [])}
except:
    bot_anchors = {}

LOGOS = {'o','l','d','r','v','x','k','m','f','t','y','c','s','sh','p','ch','air','h'}

# ================================================================
# 1. PROFILE MACER CHAPTERS
# ================================================================
print('=' * 70)
print('1. MACER CHAPTER PROFILES')
print('=' * 70)

macer_profiles = []
for entry in macer['entries']:
    ingredients = set()
    for tok in entry['tokens']:
        if tok['type'] == 'INGR' and tok.get('ref'):
            ingredients.add(tok['ref'])

    macer_profiles.append({
        'id': entry['id'],
        'plant': entry['name'],
        'n_tokens': len(entry['tokens']),
        'n_ingredients': len(ingredients),
        'ingredients': sorted(ingredients),
    })
    print(f'  {entry["name"]:20s}: {len(entry["tokens"]):4d} tok, {len(ingredients):3d} ingr')

# ================================================================
# 2. EXTRACT GALENIC QUALITIES FROM TACUINUM
# ================================================================
print(f'\n{"="*70}')
print('2. GALENIC QUALITIES (Tacuinum)')
print('=' * 70)

galenic = {}  # plant_name → {hot/cold/wet/dry, degree}

for entry in tac['entries']:
    name = entry['name'].lower().strip('.')

    hot = cold = wet = dry = 0
    for tok in entry['tokens']:
        raw = tok.get('raw', '').lower().strip('.,:;')
        if 'calid' in raw: hot += 1
        elif 'frigid' in raw or 'infrigid' in raw: cold += 1
        if 'humid' in raw: wet += 1
        elif 'sicc' in raw: dry += 1

    # Determine primary quality
    if hot + cold + wet + dry == 0:
        continue

    primary = 'HOT' if hot > cold else 'COLD' if cold > hot else 'NEUTRAL'
    moisture = 'WET' if wet > dry else 'DRY' if dry > wet else 'NEUTRAL'

    galenic[name] = {
        'primary': primary,
        'moisture': moisture,
        'hot': hot, 'cold': cold, 'wet': wet, 'dry': dry,
        'total_qual': hot + cold + wet + dry,
    }

print(f'  {len(galenic)} plants with galenic qualities')

# Distribution
qual_dist = Counter(g['primary'] for g in galenic.values())
moist_dist = Counter(g['moisture'] for g in galenic.values())
print(f'  Primary: {dict(qual_dist)}')
print(f'  Moisture: {dict(moist_dist)}')

# Show some examples
print(f'\n  Examples:')
for name in list(galenic.keys())[:10]:
    g = galenic[name]
    print(f'    {name:20s}: {g["primary"]:7s} {g["moisture"]:7s} (h={g["hot"]} c={g["cold"]} w={g["wet"]} d={g["dry"]})')

# ================================================================
# 3. PROFILE VMS HERBAL FOLIOS
# ================================================================
print(f'\n{"="*70}')
print('3. VMS HERBAL FOLIO PROFILES')
print('=' * 70)

herbal_profiles = []

for fid, folio in sorted(vms['folios'].items()):
    if 'herbal' not in folio['metadata']['section']: continue

    k_count = 0
    t_count = 0
    n_words = 0
    roots = set()
    suffixes = Counter()
    first_word = ''

    for block in folio['blocks']:
        words = [w for line in block['lines'] for w in line['words']]
        if not first_word and words:
            first_word = words[0]['eva_primary']

        for w in words:
            eva = w['eva_primary']
            n_words += 1
            if eva in LOGOS: continue

            morph = w.get('morphology') or {}
            root = morph.get('root', '')
            suffix = morph.get('suffix', '') or ''

            if root: roots.add(root)
            if suffix: suffixes[suffix] += 1

            # Count k and t (in ALL positions within words)
            for ch in eva:
                if ch == 'k': k_count += 1
                elif ch == 't': t_count += 1

    total_kt = k_count + t_count
    kt_ratio = k_count / max(total_kt, 1)

    # Botanical ID
    bot = bot_anchors.get(fid, {})
    species = bot.get('proposed_species', '')
    sherwood = bot.get('common_name', '')

    herbal_profiles.append({
        'folio': fid,
        'n_words': n_words,
        'n_roots': len(roots),
        'kt_ratio': round(kt_ratio, 3),
        'k_count': k_count,
        't_count': t_count,
        'top_suffixes': dict(suffixes.most_common(5)),
        'first_word': first_word,
        'species': species,
        'common_name': sherwood,
    })

print(f'  {len(herbal_profiles)} herbal folios profiled')

# ================================================================
# 4. TEST k/t vs GALENIC QUALITIES
# ================================================================
print(f'\n{"="*70}')
print('4. k/t RATIO vs GALENIC QUALITIES')
print('=' * 70)

# For each herbal folio with a botanical ID, find its galenic quality in Tacuinum
matched_kt_galenic = []

for hp in herbal_profiles:
    species = hp['species'].lower() if hp['species'] else ''
    if not species: continue
    if hp['k_count'] + hp['t_count'] < 5: continue

    # Try to match species name with Tacuinum entries
    species_parts = species.replace('/', ' ').split()
    matched_galenic = None

    for tac_name, qual in galenic.items():
        tac_lower = tac_name.lower()
        for part in species_parts:
            part_clean = part.strip().lower()
            if len(part_clean) >= 4 and part_clean in tac_lower:
                matched_galenic = qual
                matched_galenic['tac_name'] = tac_name
                break
        if matched_galenic:
            break

    if matched_galenic:
        matched_kt_galenic.append({
            'folio': hp['folio'],
            'species': hp['species'],
            'kt_ratio': hp['kt_ratio'],
            'primary': matched_galenic['primary'],
            'moisture': matched_galenic['moisture'],
            'tac_name': matched_galenic['tac_name'],
        })

print(f'\n  {len(matched_kt_galenic)} folios matched with Tacuinum qualities')

if matched_kt_galenic:
    print(f'\n  {"Folio":>8s} {"kt":>5s} {"Quality":>8s} {"Moist":>8s} {"Species":>25s} {"Tac":>15s}')
    print('  ' + '-' * 75)

    hot_kts = []
    cold_kts = []

    for m in sorted(matched_kt_galenic, key=lambda x: x['kt_ratio']):
        print(f'  {m["folio"]:>8s} {m["kt_ratio"]:>5.2f} {m["primary"]:>8s} {m["moisture"]:>8s} '
              f'{m["species"][:25]:>25s} {m["tac_name"][:15]:>15s}')

        if m['primary'] == 'HOT':
            hot_kts.append(m['kt_ratio'])
        elif m['primary'] == 'COLD':
            cold_kts.append(m['kt_ratio'])

    # Statistical test
    if hot_kts and cold_kts:
        hot_mean = np.mean(hot_kts)
        cold_mean = np.mean(cold_kts)

        print(f'\n  HOT plants: mean k/t = {hot_mean:.3f} (n={len(hot_kts)})')
        print(f'  COLD plants: mean k/t = {cold_mean:.3f} (n={len(cold_kts)})')
        print(f'  Difference: {abs(hot_mean - cold_mean):.3f}')

        if hot_mean > cold_mean:
            print(f'  → k-dominant = HOT, t-dominant = COLD')
        else:
            print(f'  → k-dominant = COLD, t-dominant = HOT')

        # Permutation test
        import random
        random.seed(42)
        all_kts = hot_kts + cold_kts
        observed_diff = abs(hot_mean - cold_mean)
        n_exceed = 0
        for _ in range(10000):
            random.shuffle(all_kts)
            perm_hot = all_kts[:len(hot_kts)]
            perm_cold = all_kts[len(hot_kts):]
            perm_diff = abs(np.mean(perm_hot) - np.mean(perm_cold))
            if perm_diff >= observed_diff:
                n_exceed += 1

        p_value = n_exceed / 10000
        print(f'  Permutation p-value: {p_value:.4f}')
        print(f'  VERDICT: {"✓ SIGNIFICANT (p<0.05)" if p_value < 0.05 else "✗ NOT SIGNIFICANT"}')
    else:
        print(f'\n  Not enough matched plants for statistical test')

# ================================================================
# 5. CROSS-MATCH MACER CHAPTERS ↔ VMS FOLIOS
# ================================================================
print(f'\n{"="*70}')
print('5. MACER ↔ VMS FOLIO MATCHING')
print('=' * 70)

# For each Macer chapter, find VMS folios with similar profile
# Criteria: similar number of unique roots, similar k/t profile

for mp in macer_profiles[:10]:
    print(f'\n  Macer: {mp["plant"]:20s} ({mp["n_tokens"]}tok, {mp["n_ingredients"]}ingr)')

    # Find VMS folios with similar size
    candidates = []
    for hp in herbal_profiles:
        if hp['n_words'] < 10: continue

        # Size similarity (within 2x)
        size_ratio = hp['n_words'] / max(mp['n_tokens'], 1)
        if size_ratio > 2 or size_ratio < 0.5: continue

        # Root count similarity
        root_ratio = hp['n_roots'] / max(mp['n_ingredients'], 1)

        score = 1.0 - abs(1.0 - size_ratio) * 0.5 - abs(1.0 - root_ratio) * 0.5

        # Check if Sherwood ID matches
        sherwood_match = False
        if hp['species']:
            for part in mp['plant'].lower().split():
                if len(part) >= 4 and part in hp['species'].lower():
                    sherwood_match = True

        if sherwood_match:
            score += 0.5

        candidates.append({
            'folio': hp['folio'],
            'n_words': hp['n_words'],
            'n_roots': hp['n_roots'],
            'kt_ratio': hp['kt_ratio'],
            'species': hp['species'],
            'score': round(score, 3),
            'sherwood_match': sherwood_match,
        })

    candidates.sort(key=lambda x: -x['score'])

    for c in candidates[:3]:
        match_marker = ' ★ SHERWOOD MATCH' if c['sherwood_match'] else ''
        print(f'    → {c["folio"]:8s} ({c["n_words"]}w, {c["n_roots"]}r, kt={c["kt_ratio"]:.2f}) '
              f'score={c["score"]:.3f} {c["species"][:25]}{match_marker}')

# ================================================================
# 6. FULL k/t DISTRIBUTION — all herbal folios
# ================================================================
print(f'\n{"="*70}')
print('6. k/t DISTRIBUTION COMPLÈTE')
print('=' * 70)

kts = [(hp['kt_ratio'], hp['folio'], hp['species'][:30])
       for hp in herbal_profiles if hp['k_count'] + hp['t_count'] >= 10]
kts.sort()

print(f'\n  k-dominant (>0.6):')
for kt, fid, sp in kts:
    if kt > 0.6:
        print(f'    {fid:8s} kt={kt:.2f} {sp}')

print(f'\n  t-dominant (<0.4):')
for kt, fid, sp in kts:
    if kt < 0.4:
        print(f'    {fid:8s} kt={kt:.2f} {sp}')

print(f'\n  Balanced (0.4-0.6):')
n_balanced = sum(1 for kt, _, _ in kts if 0.4 <= kt <= 0.6)
print(f'    {n_balanced} folios')

# Save
results = {
    'macer_profiles': macer_profiles,
    'herbal_profiles': herbal_profiles,
    'galenic_matches': matched_kt_galenic,
    'n_herbal': len(herbal_profiles),
    'n_galenic_matched': len(matched_kt_galenic),
}

with open(os.path.join(RESULTS, 'macer_attack.json'), 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print('\nSaved macer_attack.json')
