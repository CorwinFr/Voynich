"""
SESSION 17 — ATTACK 3: Read ONE recipe using Macer bridge

Strategy:
1. Take the best-constrained recipes from Attack 2 (Macer bridge)
2. For each word, try to match ONLY ingredients from that specific Macer chapter
3. Use STRICT matching (roots >= 4 chars, or confirmed 3-char standalone)
4. Accept "unknown" honestly — don't force matches
5. Produce the best possible Latin reading

Best candidates:
  - aristolochia recipes (5 ingr in Macer = most constrained)
  - ruta recipes (10 ingr, but 6 already confirmed in our vocabulary)
  - lens/Plantago recipes (10 ingr, complex)
"""
import json, sys, io, os
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.dirname(__file__)
VMS_PATH = os.path.join(BASE, '..', 'vms', 'vms_structured.json')
REG_PATH = os.path.join(BASE, '..', 'hypothesis_registry.json')
MACER_PATH = os.path.join(BASE, '..', 'session_14', 'macer_complete.json')
ATK2_PATH = os.path.join(BASE, 'attack2_results.json')
RESULTS = BASE

with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)
with open(REG_PATH, encoding='utf-8') as f:
    registry = json.load(f)
with open(MACER_PATH, encoding='utf-8') as f:
    macer = json.load(f)
with open(ATK2_PATH, encoding='utf-8') as f:
    atk2 = json.load(f)

LOGOS = {'o': 'ac', 'l': 'se', 'd': 'de', 'r': 'recipe', 'v': 'vel',
         'x': 'crux', 'k': 'cum', 'm': 'misce', 'f': 'per', 't': 'et',
         'y': 'in', 'c': 'cum', 's': 'est', 'sh': 'ci', 'p': 'usque', 'ch': 'cum'}
LOGO_SET = set(LOGOS.keys())

# Build vocabulary — STRICT ONLY
# Only use roots that are either:
#   - >= 4 chars
#   - or 3 chars with >= 30% standalone (REAL from Attack 1)
REAL_SHORT = {'chk', 'cht', 'yk', 'dsh', 'olk', 'pod', 'ych'}  # from Attack 1

confirmed = {}
for root, data in registry['confirmed_ingredients'].items():
    if len(root) >= 4 or root in REAL_SHORT:
        confirmed[root] = data['latin']

probable_high = {}
for root, data in registry.get('probable_ingredients', {}).items():
    if data.get('status') == 'ELIMINATED':
        continue
    if data.get('confidence', 0) >= 0.65:
        if len(root) >= 4 or root in REAL_SHORT:
            probable_high[root] = data['latin']

all_vocab = {}
all_vocab.update(probable_high)
all_vocab.update(confirmed)  # confirmed overrides

sorted_vocab = sorted(all_vocab.keys(), key=len, reverse=True)

print(f'STRICT vocabulary: {len(all_vocab)} roots')
print(f'  Confirmed: {len(confirmed)}')
print(f'  Probable (>=0.65, real): {len(probable_high)}')

# ================================================================
# DECODE FUNCTION
# ================================================================
def decode_word(eva, macer_ingredients=None):
    """Decode a single EVA word. Returns (type, latin, confidence)."""
    # Logogram?
    if eva in LOGO_SET:
        return 'LOGO', LOGOS[eva], 1.0

    # Very short = functional (don't try to decode)
    if len(eva) <= 1:
        return 'SHORT', eva, 0.0

    # Try known vocabulary (strict)
    for root in sorted_vocab:
        idx = eva.find(root)
        if idx >= 0:
            prefix = eva[:idx]
            suffix = eva[idx+len(root):]
            if len(prefix) <= 4 and len(suffix) <= 6:
                latin = all_vocab[root]
                conf = 0.9 if root in confirmed else 0.7
                pfx_str = LOGOS.get(prefix, prefix) if prefix else ''
                sfx_str = suffix
                return 'VOCAB', f'{latin}', conf

    # Unknown
    return 'UNK', eva, 0.0


def decode_recipe(bid, macer_ingr=None):
    """Decode all words in a pharma block."""
    # Find the block
    for fid, folio in vms['folios'].items():
        for block in folio['blocks']:
            if block.get('block_id') == bid:
                words = []
                for line in block['lines']:
                    for w in line['words']:
                        eva = w['eva_primary']
                        wtype, latin, conf = decode_word(eva, macer_ingr)
                        words.append({
                            'eva': eva,
                            'type': wtype,
                            'latin': latin,
                            'conf': conf,
                        })
                return words, fid
    return [], ''


# ================================================================
# DECODE MACER-BRIDGED RECIPES
# ================================================================
print(f'\n{"="*70}')
print('DECODING MACER-BRIDGED RECIPES')
print('='*70)

best_readings = []

for bridge in atk2['macer_bridge']:
    plant = bridge['plant']
    macer_ch = bridge['macer_chapter']
    macer_ingr = set(bridge['macer_ingredients'])
    bids = bridge['recipe_bids']

    print(f'\n  === {plant.upper()} → Macer "{macer_ch}" ===')
    print(f'  Expected ingredients: {", ".join(sorted(macer_ingr))}')

    for bid in bids:
        words, fid = decode_recipe(bid, macer_ingr)
        if not words:
            continue

        n_total = len(words)
        n_decoded = sum(1 for w in words if w['conf'] > 0)
        n_high = sum(1 for w in words if w['conf'] >= 0.7)
        pct = n_decoded * 100 // max(n_total, 1)

        # Build reading
        parts = []
        decoded_ingredients = set()
        for w in words:
            if w['conf'] >= 0.7:
                parts.append(w['latin'].replace('i_', '').upper())
                if w['type'] == 'VOCAB':
                    decoded_ingredients.add(w['latin'].replace('i_', ''))
            elif w['conf'] > 0:
                parts.append(w['latin'].replace('i_', '').lower())
            else:
                parts.append(f'({w["eva"]})')

        # Check: how many decoded ingredients are in the Macer chapter?
        in_macer = decoded_ingredients & macer_ingr
        not_in_macer = decoded_ingredients - macer_ingr

        print(f'\n  {bid} ({n_total} words, {n_high} high-conf, {pct}% decoded):')
        print(f'    {" ".join(parts)}')
        if in_macer:
            print(f'    ✓ In Macer: {", ".join(sorted(in_macer))}')
        if not_in_macer:
            print(f'    ? Not in Macer: {", ".join(sorted(not_in_macer))}')

        best_readings.append({
            'bid': bid,
            'plant': plant,
            'macer_chapter': macer_ch,
            'n_total': n_total,
            'n_high_conf': n_high,
            'pct_decoded': pct,
            'reading': ' '.join(parts),
            'ingredients_found': sorted(decoded_ingredients),
            'in_macer': sorted(in_macer),
            'not_in_macer': sorted(not_in_macer),
        })

# ================================================================
# RANK: Which recipe has the most HIGH-CONFIDENCE words matching Macer?
# ================================================================
print(f'\n\n{"="*70}')
print('BEST RECIPE READINGS (ranked by high-conf words in Macer)')
print('='*70)

# Score = number of high-conf ingredient words that ARE in Macer
for br in best_readings:
    br['score'] = len(br['in_macer'])

best_readings.sort(key=lambda x: (-x['score'], -x['n_high_conf']))

print(f'\n  {"Block":>12s} {"Plant":>12s} {"Words":>5s} {"HiConf":>7s} '
      f'{"InMacer":>8s} {"NotInM":>7s} {"Reading (first 80 chars)"}')
print('  ' + '-' * 100)

for br in best_readings[:15]:
    reading_short = br['reading'][:80]
    print(f'  {br["bid"]:>12s} {br["plant"]:>12s} {br["n_total"]:>5d} '
          f'{br["n_high_conf"]:>7d} {br["score"]:>8d} {len(br["not_in_macer"]):>7d} '
          f'{reading_short}')

# ================================================================
# BEST READING — the ONE recipe
# ================================================================
if best_readings:
    best = best_readings[0]
    print(f'\n\n{"="*70}')
    print(f'THE BEST READING: {best["bid"]}')
    print(f'Plant: {best["plant"]} → Macer "{best["macer_chapter"]}"')
    print(f'='*70)
    print(f'\n  {best["reading"]}')
    print(f'\n  High-confidence words: {best["n_high_conf"]}')
    print(f'  Ingredients in Macer: {best["in_macer"]}')
    print(f'  Ingredients NOT in Macer: {best["not_in_macer"]}')
    print(f'\n  Macer chapter ingredients: '
          f'{", ".join(sorted(atk2["macer_bridge"][0]["macer_ingredients"]))}')

# ================================================================
# SAVE
# ================================================================
output = {
    'n_bridged_recipes': len(best_readings),
    'best_readings': best_readings[:20],
}

with open(os.path.join(RESULTS, 'attack3_results.json'), 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f'\nSaved attack3_results.json')
