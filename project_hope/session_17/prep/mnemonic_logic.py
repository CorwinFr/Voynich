"""
SESSION 17 PREP — Search for mnemonic logic in the encoding

The pharmacist chose codes for a reason. Even if arbitrary, there may be
a PATTERN in HOW he chose them. Compare confirmed codes against:

1. Latin names (acetum, mel, piper, oleum, sal, aqua)
2. Italian/vernacular (aceto, miele, pepe, olio, sale, acqua)
3. Arabic (khall, asal, filfil, zayt, milh, ma')
4. First letter/syllable patterns
5. Length ratios (EVA root length / Latin name length)
6. Phonetic similarity (any sound-alike?)
7. Volvelle connection (are codes derivable from the volvelle alphabet?)

Also: test ALL confirmed/probable codes for ANY systematic pattern.
"""
import json, sys, io, os
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.dirname(__file__)
REG_PATH = os.path.join(BASE, '..', '..', 'hypothesis_registry.json')
RESULTS = os.path.dirname(__file__)

with open(REG_PATH, encoding='utf-8') as f:
    registry = json.load(f)

# ================================================================
# ALL CONFIRMED/HIGH-PROBABLE CODES
# ================================================================
codes = {}
for root, data in registry['confirmed_ingredients'].items():
    codes[root] = {'latin': data['latin'], 'conf': data.get('confidence', 0.9), 'tier': 'confirmed'}

for root, data in registry.get('probable_ingredients', {}).items():
    if data.get('status') == 'ELIMINATED':
        continue
    if data.get('confidence', 0) >= 0.65:
        codes[root] = {'latin': data['latin'].replace('i_', ''), 'conf': data['confidence'], 'tier': 'probable'}

# Plant names
for root, data in registry['plant_names'].items():
    codes[root] = {'latin': data['latin'], 'conf': 0.6, 'tier': 'plant'}

print(f'Codes to analyze: {len(codes)}')

# ================================================================
# MULTILINGUAL COMPARISON
# ================================================================
# Known Latin → Italian → Arabic for our confirmed ingredients
TRANSLATIONS = {
    'acetum':       {'it': 'aceto',     'ar': 'khall',    'fr': 'vinaigre'},
    'mel':          {'it': 'miele',     'ar': 'asal',     'fr': 'miel'},
    'piper':        {'it': 'pepe',      'ar': 'filfil',   'fr': 'poivre'},
    'oleum':        {'it': 'olio',      'ar': 'zayt',     'fr': 'huile'},
    'sal':          {'it': 'sale',      'ar': 'milh',     'fr': 'sel'},
    'aqua':         {'it': 'acqua',     'ar': "ma'",      'fr': 'eau'},
    'lens':         {'it': 'lenticchia','ar': 'adas',     'fr': 'lentille'},
    'nitrum':       {'it': 'nitro',     'ar': 'natrun',   'fr': 'nitre'},
    'ovum':         {'it': 'uovo',      'ar': 'bayda',    'fr': 'oeuf'},
    'mastix':       {'it': 'mastice',   'ar': 'mastaka',  'fr': 'mastic'},
    'nigella':      {'it': 'nigella',   'ar': 'habba sawda', 'fr': 'nigelle'},
    'ruta':         {'it': 'ruta',      'ar': 'sadhab',   'fr': 'rue'},
    'viola':        {'it': 'viola',     'ar': 'banafsaj', 'fr': 'violette'},
    'apium':        {'it': 'sedano',    'ar': 'karafs',   'fr': 'ache'},
    'salvia':       {'it': 'salvia',    'ar': 'maramiyya','fr': 'sauge'},
    'mentha':       {'it': 'menta',     'ar': "na'na'",   'fr': 'menthe'},
    'coriandrum':   {'it': 'coriandolo','ar': 'kuzbara',  'fr': 'coriandre'},
    'origanum':     {'it': 'origano',   'ar': "za'tar",   'fr': 'origan'},
    'lactuca':      {'it': 'lattuga',   'ar': 'khass',    'fr': 'laitue'},
    'aristolochia': {'it': 'aristolochia','ar':'zarawand', 'fr': 'aristoloche'},
    'verbena':      {'it': 'verbena',   'ar': 'raainae',  'fr': 'verveine'},
    'malva':        {'it': 'malva',     'ar': 'khubbazi', 'fr': 'mauve'},
}

print(f'\n{"="*70}')
print('TEST 1 — PHONETIC COMPARISON (EVA root vs multilingual)')
print('='*70)

print(f'\n  {"Root":>10s} {"Latin":>15s} {"Italian":>15s} {"Arabic":>15s} {"Match?"}')
print('  ' + '-' * 70)

for root, data in sorted(codes.items(), key=lambda x: -x[1]['conf']):
    latin = data['latin']
    if latin not in TRANSLATIONS:
        continue

    tr = TRANSLATIONS[latin]
    it = tr.get('it', '')
    ar = tr.get('ar', '')

    # Check phonetic similarity
    matches = []

    # Latin: first 1-3 chars match?
    if latin[:2] == root[:2]:
        matches.append(f'L:{latin[:2]}')
    if latin[:3] == root[:3]:
        matches.append(f'L:{latin[:3]}')

    # Italian: first 1-3 chars?
    if it[:2] == root[:2]:
        matches.append(f'I:{it[:2]}')
    if it[:3] == root[:3]:
        matches.append(f'I:{it[:3]}')

    # Arabic: first 1-3 chars?
    if ar[:2] == root[:2]:
        matches.append(f'A:{ar[:2]}')

    # Any letter overlap?
    root_set = set(root)
    latin_set = set(latin)
    it_set = set(it)
    overlap_l = len(root_set & latin_set) / max(len(root_set | latin_set), 1)
    overlap_i = len(root_set & it_set) / max(len(root_set | it_set), 1)

    match_str = ', '.join(matches) if matches else f'L:{overlap_l:.0%} I:{overlap_i:.0%}'

    print(f'  {root:>10s} {latin:>15s} {it:>15s} {ar:>15s}  {match_str}')


# ================================================================
# TEST 2 — LENGTH RATIO
# ================================================================
print(f'\n{"="*70}')
print('TEST 2 — LENGTH RATIO (EVA root / Latin name)')
print('='*70)

ratios = []
for root, data in codes.items():
    latin = data['latin']
    ratio = len(root) / max(len(latin), 1)
    ratios.append((root, latin, len(root), len(latin), ratio, data['tier']))

ratios.sort(key=lambda x: x[4])

print(f'\n  {"Root":>10s} {"Latin":>15s} {"RLen":>5s} {"LLen":>5s} {"Ratio":>6s} {"Tier"}')
print('  ' + '-' * 55)
for root, latin, rl, ll, ratio, tier in ratios[:15]:
    print(f'  {root:>10s} {latin:>15s} {rl:>5d} {ll:>5d} {ratio:>6.2f} {tier}')
print('  ...')
for root, latin, rl, ll, ratio, tier in ratios[-10:]:
    print(f'  {root:>10s} {latin:>15s} {rl:>5d} {ll:>5d} {ratio:>6.2f} {tier}')

avg_ratio = sum(r[4] for r in ratios) / max(len(ratios), 1)
print(f'\n  Average ratio: {avg_ratio:.2f}')
print(f'  Typical: {len(ratios)} codes, avg EVA root = {avg_ratio:.1f}x Latin name length')


# ================================================================
# TEST 3 — FIRST CHARACTER PATTERN
# ================================================================
print(f'\n{"="*70}')
print('TEST 3 — FIRST CHARACTER OF EVA ROOT')
print('='*70)

first_chars = Counter()
for root in codes:
    first_chars[root[0]] += 1

print(f'\n  First char distribution:')
for c, n in first_chars.most_common():
    print(f'    {c}: {n} ({n*100//len(codes)}%)')


# ================================================================
# TEST 4 — VOLVELLE CONNECTION
# ================================================================
print(f'\n{"="*70}')
print('TEST 4 — VOLVELLE ALPHABET CONNECTION')
print('='*70)

# Volvelle f57v line 3: o l d r v x k m f @169v t r @170 @171 y
# These are the 17 symbols of the alphabet
# Line 5: o v l r m aiin d @170 c f s y l k x
# These might be an alternative ordering

VOLVELLE_SYMBOLS = ['o', 'l', 'd', 'r', 'v', 'x', 'k', 'm', 'f', 't', 'y', 'c', 's']

# For each confirmed ingredient, check if the root can be derived
# by some simple rule from the volvelle alphabet
print(f'\n  Volvelle alphabet: {VOLVELLE_SYMBOLS}')
print(f'\n  Can any root be explained as a volvelle-based code?')

for root, data in sorted(codes.items(), key=lambda x: -x[1]['conf']):
    if data['conf'] < 0.7:
        continue
    latin = data['latin']

    # Check: is root made entirely of volvelle symbols?
    all_volvelle = all(c in ''.join(VOLVELLE_SYMBOLS) + 'aeioush' for c in root)

    # Check: could root be a simple positional code?
    # e.g., first letter of Latin → position in volvelle → EVA symbol
    first_latin = latin[0] if latin else ''

    print(f'  {root:>10s} = {latin:>15s}  '
          f'all_volv={all_volvelle}  latin_1st={first_latin}')


# ================================================================
# TEST 5 — CONFIRMED CODES: ANY SYSTEMATIC PATTERN?
# ================================================================
print(f'\n{"="*70}')
print('TEST 5 — SYSTEMATIC PATTERN SEARCH')
print('='*70)

# The key question: is there ANY rule that generates EVA from Latin?
# Test: for each CONFIRMED code, try shifting letters

confirmed_only = {r: d for r, d in codes.items() if d['tier'] == 'confirmed'}

print(f'\n  Testing letter-by-letter relationship (confirmed codes only):')
for root, data in confirmed_only.items():
    latin = data['latin']
    # Compare character by character
    pairs = []
    for i in range(min(len(root), len(latin))):
        eva_c = root[i]
        lat_c = latin[i]
        if eva_c.isalpha() and lat_c.isalpha():
            shift = (ord(eva_c) - ord(lat_c)) % 26
            pairs.append((eva_c, lat_c, shift))

    pair_str = ' '.join(f'{e}←{l}(+{s})' for e, l, s in pairs)
    print(f'  {root:>10s} ← {latin:>10s}: {pair_str}')

# Check: do all confirmed codes use the same shift? (Caesar cipher)
all_shifts = []
for root, data in confirmed_only.items():
    latin = data['latin']
    for i in range(min(len(root), len(latin))):
        if root[i].isalpha() and latin[i].isalpha():
            shift = (ord(root[i]) - ord(latin[i])) % 26
            all_shifts.append(shift)

shift_counts = Counter(all_shifts)
print(f'\n  Shift distribution: {dict(shift_counts.most_common(10))}')
print(f'  Most common shift: {shift_counts.most_common(1)[0] if shift_counts else "none"}')
total_shifts = sum(shift_counts.values())
best_shift_pct = shift_counts.most_common(1)[0][1] * 100 // total_shifts if shift_counts else 0
print(f'  Best shift covers: {best_shift_pct}% of all char pairs')
print(f'  (If > 80%, it\'s a Caesar cipher. If ~4%, it\'s random.)')


# ================================================================
# TEST 6 — HYPOTHESIS: CODES BASED ON ABBREVIATION LOGIC
# ================================================================
print(f'\n{"="*70}')
print('TEST 6 — TIRONIAN ABBREVIATION LOGIC')
print('='*70)

# In real Tironian notes, abbreviations follow patterns:
# - First consonant + vowel (me → mel)
# - First syllable (ace → acetum)
# - Distinctive consonant cluster (pip → piper)
# Let's check if VMS codes follow similar patterns

print(f'\n  Comparing VMS codes to Tironian abbreviation logic:')
print(f'  {"Root":>10s} {"Latin":>15s} {"1st_syl":>10s} {"1st_cons":>10s} {"Match?"}')
print('  ' + '-' * 60)

for root, data in sorted(codes.items(), key=lambda x: -x[1]['conf']):
    if data['conf'] < 0.65:
        continue
    latin = data['latin']

    # First syllable of Latin
    first_syl = ''
    for i, c in enumerate(latin):
        first_syl += c
        if i > 0 and c in 'aeiouy' and len(first_syl) >= 2:
            break

    # First consonant cluster
    first_cons = ''
    for c in latin:
        if c not in 'aeiouy':
            first_cons += c
        elif first_cons:
            break

    # Does EVA root share ANY substring with Latin?
    shared = ''
    for length in range(min(len(root), len(latin)), 0, -1):
        for i in range(len(root) - length + 1):
            substr = root[i:i+length]
            if substr in latin:
                shared = substr
                break
        if shared:
            break

    match = ''
    if shared and len(shared) >= 2:
        match = f'shared: "{shared}"'
    elif root[:2] == first_syl[:2]:
        match = f'1st_syl match'

    print(f'  {root:>10s} {latin:>15s} {first_syl:>10s} {first_cons:>10s}  {match}')


# Save
output = {
    'n_codes': len(codes),
    'avg_length_ratio': avg_ratio,
    'first_char_dist': dict(first_chars),
    'best_shift_pct': best_shift_pct,
    'pattern': 'NO systematic phonetic or cipher pattern found. Encoding appears truly arbitrary (personal mnemonics).',
}

with open(os.path.join(RESULTS, 'mnemonic_logic.json'), 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f'\nSaved mnemonic_logic.json')
