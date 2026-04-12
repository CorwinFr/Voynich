"""
PHASE 1 — Botanical Anchors
For each EVA root with a herbal folio, find the botanical identification.
Root EVA → herbal folio → plant drawing → species → medieval Latin name.
Update knowledge_base.json with cracked roots.
"""
import json, sys, io, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

KB_PATH = os.path.join(os.path.dirname(__file__), '..', 'knowledge_base.json')

with open(KB_PATH, encoding='utf-8') as f:
    kb = json.load(f)

print('=' * 70)
print('PHASE 1 — BOTANICAL ANCHORS')
print('=' * 70)

# For each root with a botanical ID, check confidence
cracked = 0
probable = 0
weak = 0

results = []

for root, data in sorted(kb['roots'].items(), key=lambda x: -x[1]['total_freq']):
    bot = data.get('botanical_id')
    if not bot:
        continue

    folio = data['herbal_folio']
    species = bot.get('species', '')
    common = bot.get('common_name', '')
    medieval = bot.get('medieval_latin', '')
    conf = bot.get('confidence', 0)
    proposers = bot.get('proposers', '')

    # Determine crack quality
    if conf >= 0.75 and medieval:
        status = 'CRACKED'
        cracked += 1
        data['crack_status'] = 'cracked'
        data['cracked_latin'] = medieval.lower()
    elif conf >= 0.5:
        status = 'PROBABLE'
        probable += 1
        data['crack_status'] = 'probable'
        data['cracked_latin'] = medieval.lower() if medieval else species.split('/')[0].strip().lower()
    else:
        status = 'weak'
        weak += 1
        data['crack_status'] = 'weak'
        data['cracked_latin'] = None

    results.append({
        'root': root,
        'folio': folio,
        'species': species,
        'medieval_latin': medieval,
        'confidence': conf,
        'status': status,
        'pharma_freq': data['pharma_freq'],
    })

    print(f'  {root:12s} ({folio}) → {medieval or species:30s} conf={conf:.2f} '
          f'pharma:x{data["pharma_freq"]:3d} [{status}]')

print(f'\n  CRACKED:  {cracked}')
print(f'  PROBABLE: {probable}')
print(f'  Weak:     {weak}')

# Save updated KB
with open(KB_PATH, 'w', encoding='utf-8') as f:
    json.dump(kb, f, indent=2, ensure_ascii=False)

print(f'\nUpdated knowledge_base.json')
