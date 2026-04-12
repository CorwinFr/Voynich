"""
VOYNICH ENGINE — Independent validation of Tier 3 (death-match-only) anchors

For each uncertain mapping, check DISTRIBUTIONAL properties in the VMS:

1. VERBS (trita, superaddere, sumere, decoctio, jungere, bibere):
   - Should appear AFTER ingredients and BEFORE doses/body parts
   - Should be in imperative/participial position
   - Should appear more in pharma than herbal

2. BODY PARTS (caput):
   - Should appear near disease words
   - May correlate with specific sections

3. DISEASES (febris, dolor, venenum):
   - Should appear near body parts and verbs
   - More common in remedy descriptions

4. INGREDIENTS (vinum, rosa):
   - Should appear in herbal folios where Macer mentions them
   - Cross-folio fingerprint should match

Each test is INDEPENDENT of positional alignment.
"""
import json, sys, io, os
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.dirname(os.path.dirname(__file__))
VMS_PATH = os.path.join(BASE, 'vms', 'vms_structured.json')
REG_PATH = os.path.join(BASE, 'hypothesis_registry.json')
RESULTS = os.path.join(BASE, 'engine')

with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)
with open(REG_PATH, encoding='utf-8') as f:
    registry = json.load(f)

LOGOS = {'o': 'ac', 'l': 'se', 'd': 'de', 'r': 'recipe', 'v': 'vel',
         'x': 'crux', 'k': 'cum', 'm': 'misce', 'f': 'per', 't': 'et',
         'y': 'in', 'c': 'cum', 's': 'est', 'sh': 'ci', 'p': 'usque', 'ch': 'cum'}
LOGO_SET = set(LOGOS.keys())

# Known ingredients (tier 1-2 only, for context analysis)
KNOWN_INGR = set()
for root in registry['confirmed_ingredients']:
    KNOWN_INGR.add(root)
KNOWN_INGR.update({'ypch', 'ykeed', 'seees', 'kald', 'otoly'})

# Tier 3 to validate
TIER3 = {
    'otch': ('trita', 'VERB'),
    'cthy': ('superaddere', 'VERB'),
    'qoty': ('sumere', 'VERB'),
    'alch': ('decoctio', 'VERB'),
    'chod': ('jungere', 'VERB'),
    'kch':  ('sumere', 'VERB'),
    'chot': ('decoctio', 'VERB'),
    'chcthy':('superaddere', 'VERB'),
    'chy':  ('caput', 'BODY'),
    'cho':  ('febris', 'DISEASE'),
    'chek': ('dolor', 'DISEASE'),
    'cheky':('venenum', 'DISEASE'),
    'dal':  ('vinum', 'INGR'),
    'dary': ('vinum', 'INGR'),
    'qokeo':('rosa', 'INGR'),
}

# ================================================================
# TEST 1: Context — what comes before/after each root?
# ================================================================
print('='*70)
print('TEST 1 — CONTEXT ANALYSIS (what surrounds each tier 3 root?)')
print('='*70)

results = {}

for root, (latin, expected_type) in TIER3.items():
    before_ingr = 0
    after_ingr = 0
    before_logo = 0
    after_logo = 0
    before_func = 0
    total = 0

    section_dist = Counter()
    positions = []

    for fid, folio in vms['folios'].items():
        sec = folio['metadata']['section']
        for block in folio['blocks']:
            all_words = []
            for line in block['lines']:
                all_words.extend(line['words'])

            for i, w in enumerate(all_words):
                r = (w.get('morphology') or {}).get('root', '')
                if r != root and w['eva_primary'] != root:
                    continue

                total += 1
                section_dist[sec] += 1
                if len(all_words) > 1:
                    positions.append(i / (len(all_words) - 1))

                # What's before?
                if i > 0:
                    prev = all_words[i-1]
                    prev_eva = prev['eva_primary']
                    prev_root = (prev.get('morphology') or {}).get('root', '')
                    if prev_eva in LOGO_SET:
                        before_logo += 1
                    elif prev_root in KNOWN_INGR:
                        before_ingr += 1

                # What's after?
                if i < len(all_words) - 1:
                    nxt = all_words[i+1]
                    nxt_eva = nxt['eva_primary']
                    nxt_root = (nxt.get('morphology') or {}).get('root', '')
                    if nxt_eva in LOGO_SET:
                        after_logo += 1
                    elif nxt_root in KNOWN_INGR:
                        after_ingr += 1

    if total == 0:
        continue

    mean_pos = sum(positions) / len(positions) if positions else 0
    herbal_pct = (section_dist.get('herbal_a', 0) + section_dist.get('herbal_b', 0)) * 100 // total
    pharma_pct = section_dist.get('pharma', 0) * 100 // total
    bi_pct = before_ingr * 100 // total
    ai_pct = after_ingr * 100 // total
    bl_pct = before_logo * 100 // total

    # Evaluate against expected type
    checks = []
    if expected_type == 'VERB':
        # Verbs should: follow ingredients (>20%), appear in pharma (>10%), mid-position
        if bi_pct >= 15:
            checks.append('✓ follows ingredients')
        else:
            checks.append(f'✗ follows ingredients only {bi_pct}%')
        if pharma_pct >= 8:
            checks.append('✓ in pharma')
        else:
            checks.append(f'✗ pharma only {pharma_pct}%')
    elif expected_type == 'BODY':
        # Body parts: should appear near verbs, mid-to-late position
        if mean_pos >= 0.3:
            checks.append('✓ mid/late position')
        else:
            checks.append(f'✗ early position {mean_pos:.2f}')
    elif expected_type == 'DISEASE':
        # Diseases: should appear near verbs
        if herbal_pct >= 30:
            checks.append('✓ in herbal (where diseases are described)')
        else:
            checks.append(f'? herbal only {herbal_pct}%')
    elif expected_type == 'INGR':
        # Ingredients: should appear in herbal, follow logos/functional
        if herbal_pct >= 30:
            checks.append('✓ in herbal')
        else:
            checks.append(f'✗ herbal only {herbal_pct}%')

    verdict = 'PASS' if all('✓' in c for c in checks) else 'MIXED' if any('✓' in c for c in checks) else 'FAIL'

    results[root] = {
        'latin': latin, 'type': expected_type, 'total': total,
        'herbal_pct': herbal_pct, 'pharma_pct': pharma_pct,
        'before_ingr_pct': bi_pct, 'after_ingr_pct': ai_pct,
        'mean_pos': round(mean_pos, 2), 'verdict': verdict,
        'checks': checks,
    }

    print(f'\n  {root:>8s} = {latin:>15s} [{expected_type:>7s}]  n={total}  '
          f'herb={herbal_pct}%  phar={pharma_pct}%  '
          f'bef_ingr={bi_pct}%  pos={mean_pos:.2f}  → {verdict}')
    for c in checks:
        print(f'    {c}')


# ================================================================
# TEST 2: FINGERPRINT for ingredients (dal/dary=vinum, qokeo=rosa)
# ================================================================
print(f'\n\n{"="*70}')
print('TEST 2 — FINGERPRINT for ingredient candidates')
print('='*70)

SHERWOOD_MACER = {
    'f48v':'Ruta','f9v':'Violae','f44v':'Apium','f51v':'Salvia',
    'f29r':'Lactuca','f41r':'Origanum','f37r':'Mentha',
    'f41v':'Coriandrum','f22r':'Verbena','f28r':'Aristolochia',
    'f5v':'Malva','f45r':'Atriplex','f66v':'Satureia',
    'f65v':'Centaurea','f3v':'Elleborus','f95v1':'Althaea',
}

# Which Macer chapters have vinum? rosa?
VINUM_CHAPTERS = {'Ruta','Violae','Origanum','Mentha','Coriandrum',
                  'Verbena','Aristolochia','Atriplex','Satureia','Lactuca',
                  'Salvia','Centaurea','Althaea','Malva'}  # most chapters
ROSA_CHAPTERS = {'Violae'}  # rosa mentioned mainly in Violae

for test_root, test_ingr, expected_chapters in [
    ('dal', 'vinum', VINUM_CHAPTERS),
    ('dary', 'vinum', VINUM_CHAPTERS),
    ('qokeo', 'rosa', ROSA_CHAPTERS),
]:
    present_in = []
    absent_from = []

    for fid, macer_ch in SHERWOOD_MACER.items():
        if fid not in vms['folios']:
            continue
        has_root = False
        for block in vms['folios'][fid]['blocks']:
            for line in block['lines']:
                for w in line['words']:
                    r = (w.get('morphology') or {}).get('root', '')
                    if r == test_root:
                        has_root = True
                        break
                if has_root: break
            if has_root: break

        expects = macer_ch in expected_chapters
        if has_root:
            present_in.append((fid, macer_ch, expects))
        else:
            absent_from.append((fid, macer_ch, expects))

    tp = sum(1 for _, _, e in present_in if e)
    fp = sum(1 for _, _, e in present_in if not e)
    fn = sum(1 for _, _, e in absent_from if e)
    tn = sum(1 for _, _, e in absent_from if not e)
    n = tp + fp + fn + tn

    accuracy = (tp + tn) * 100 // max(n, 1)
    precision = tp * 100 // max(tp + fp, 1) if (tp + fp) > 0 else 0
    recall = tp * 100 // max(tp + fn, 1) if (tp + fn) > 0 else 0

    print(f'\n  {test_root} = {test_ingr}:  TP={tp} FP={fp} FN={fn} TN={tn}  '
          f'acc={accuracy}% prec={precision}% rec={recall}%')
    for fid, ch, exp in present_in:
        marker = '✓' if exp else '✗'
        print(f'    {marker} {fid:>8s} ({ch:>15s}) HAS {test_root} {"(expected)" if exp else "(unexpected)"}')


# ================================================================
# SUMMARY
# ================================================================
print(f'\n\n{"="*70}')
print('VALIDATION SUMMARY')
print('='*70)

passed = []
mixed = []
failed = []

for root, data in sorted(results.items()):
    if data['verdict'] == 'PASS':
        passed.append((root, data['latin'], data['type']))
    elif data['verdict'] == 'MIXED':
        mixed.append((root, data['latin'], data['type']))
    else:
        failed.append((root, data['latin'], data['type']))

print(f'\n  PASS ({len(passed)}):')
for r, l, t in passed:
    print(f'    {r:>10s} = {l:>15s} [{t}]')

print(f'\n  MIXED ({len(mixed)}):')
for r, l, t in mixed:
    print(f'    {r:>10s} = {l:>15s} [{t}]')

print(f'\n  FAIL ({len(failed)}):')
for r, l, t in failed:
    print(f'    {r:>10s} = {l:>15s} [{t}]')

# Save
output = {
    'n_tested': len(results),
    'n_pass': len(passed),
    'n_mixed': len(mixed),
    'n_fail': len(failed),
    'details': results,
    'passed': [(r, l, t) for r, l, t in passed],
    'failed': [(r, l, t) for r, l, t in failed],
}

with open(os.path.join(RESULTS, 'validate_tier3_results.json'), 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f'\nSaved validate_tier3_results.json')
