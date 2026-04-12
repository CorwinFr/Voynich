"""
SESSION 17 PREP — Full structural audit

Check EVERY structural rule against EVERY folio.
Flag anomalies. Understand what breaks and why.

Rules to test:
1. Gallows 88% block-initial → which folios/blocks violate?
2. n=98% word-end → which words have n NOT at end?
3. q=99% word-start → which words have q NOT at start?
4. -am = sentence terminator → where does it appear mid-sentence?
5. First word = plant name (herbal) → which folios break this?
6. Pharma opener = gallows-initial → which don't?
7. Morphology: prefix+root+suffix → words that don't decompose?
8. Section coherence → any folio misclassified?
"""
import json, sys, io, os
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.dirname(__file__)
VMS_PATH = os.path.join(BASE, '..', '..', 'vms', 'vms_structured.json')
RESULTS = os.path.dirname(__file__)

with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)

GALLOWS = set('ptkf')
LOGOS = {'o','l','d','r','v','x','k','m','f','t','y','c','s','sh','p','ch','air','h'}

anomalies = defaultdict(list)

# ================================================================
# RULE 1: Gallows 88% block-initial
# ================================================================
print('='*70)
print('RULE 1 — Gallows block-initial (expect 88%)')
print('='*70)

gallows_initial = 0
gallows_other = 0
gallows_per_section = defaultdict(lambda: {'initial': 0, 'other': 0, 'total_blocks': 0})

for fid, folio in vms['folios'].items():
    sec = folio['metadata']['section']
    for block in folio['blocks']:
        gallows_per_section[sec]['total_blocks'] += 1
        first_word_is_gallows = False
        for li, line in enumerate(block['lines']):
            for wi, w in enumerate(line['words']):
                eva = w['eva_primary']
                has_gallows = any(c in GALLOWS for c in eva if len(eva) > 1)
                if not has_gallows:
                    continue
                if li == 0 and wi == 0:
                    gallows_initial += 1
                    first_word_is_gallows = True
                else:
                    gallows_other += 1

        if not first_word_is_gallows:
            lines = block['lines']
            if lines and lines[0]['words']:
                first = lines[0]['words'][0]['eva_primary']
                if first[0] not in GALLOWS and first not in LOGOS:
                    gallows_per_section[sec]['other'] += 1
                else:
                    gallows_per_section[sec]['initial'] += 1
            else:
                gallows_per_section[sec]['other'] += 1

total_g = gallows_initial + gallows_other
pct = gallows_initial * 100 // max(total_g, 1)
print(f'  Gallows initial: {gallows_initial} ({pct}%)')
print(f'  Gallows other: {gallows_other}')

# Non-gallows-initial blocks by section
print(f'\n  Blocks NOT starting with gallows, by section:')
for sec in sorted(gallows_per_section.keys()):
    s = gallows_per_section[sec]
    n_other = s['other']
    n_total = s['total_blocks']
    if n_other > 0:
        print(f'    {sec:>12s}: {n_other}/{n_total} blocks')


# ================================================================
# RULE 2: n = 98% word-end
# ================================================================
print(f'\n{"="*70}')
print('RULE 2 — n at word-end (expect 98%)')
print('='*70)

n_at_end = 0
n_not_at_end = 0
n_violations = []

for fid, folio in vms['folios'].items():
    for block in folio['blocks']:
        for line in block['lines']:
            for w in line['words']:
                eva = w['eva_primary']
                if 'n' not in eva:
                    continue
                # Check if n is at the end (last char or part of 'ain', 'aiin' etc)
                if eva.endswith('n') or eva.endswith('in') or eva.endswith('iin'):
                    n_at_end += 1
                else:
                    n_not_at_end += 1
                    if len(n_violations) < 20:
                        n_violations.append((fid, eva))

total_n = n_at_end + n_not_at_end
pct_n = n_at_end * 100 // max(total_n, 1)
print(f'  n at end: {n_at_end} ({pct_n}%)')
print(f'  n NOT at end: {n_not_at_end}')
if n_violations:
    print(f'  Sample violations: {n_violations[:10]}')


# ================================================================
# RULE 3: q = 99% word-start
# ================================================================
print(f'\n{"="*70}')
print('RULE 3 — q at word-start (expect 99%)')
print('='*70)

q_at_start = 0
q_not_at_start = 0
q_violations = []

for fid, folio in vms['folios'].items():
    for block in folio['blocks']:
        for line in block['lines']:
            for w in line['words']:
                eva = w['eva_primary']
                if 'q' not in eva:
                    continue
                if eva.startswith('q'):
                    q_at_start += 1
                else:
                    q_not_at_start += 1
                    if len(q_violations) < 20:
                        q_violations.append((fid, eva))

total_q = q_at_start + q_not_at_start
pct_q = q_at_start * 100 // max(total_q, 1)
print(f'  q at start: {q_at_start} ({pct_q}%)')
print(f'  q NOT at start: {q_not_at_start}')
if q_violations:
    print(f'  Sample violations: {q_violations[:10]}')


# ================================================================
# RULE 4: -am sentence terminator
# ================================================================
print(f'\n{"="*70}')
print('RULE 4 — Words ending in -am (position analysis)')
print('='*70)

am_positions = Counter()  # 'last', 'near_last', 'other'
am_total = 0

for fid, folio in vms['folios'].items():
    for block in folio['blocks']:
        all_words = []
        for line in block['lines']:
            for w in line['words']:
                all_words.append(w['eva_primary'])

        for i, eva in enumerate(all_words):
            if eva.endswith('am') and len(eva) >= 2:
                am_total += 1
                pos = i / max(len(all_words) - 1, 1)
                if i >= len(all_words) - 2:
                    am_positions['last_2'] += 1
                elif pos > 0.7:
                    am_positions['late'] += 1
                else:
                    am_positions['early'] += 1

print(f'  Total -am words: {am_total}')
for pos, n in am_positions.most_common():
    print(f'    {pos:>10s}: {n} ({n*100//max(am_total,1)}%)')


# ================================================================
# RULE 5: Unexplained words (not logo, not decomposable)
# ================================================================
print(f'\n{"="*70}')
print('RULE 5 — Words that don\'t fit the structure')
print('='*70)

# Words with unusual characters or patterns
unusual = Counter()
very_long = []
very_short_nonlogo = Counter()
contains_numbers = []

for fid, folio in vms['folios'].items():
    for block in folio['blocks']:
        for line in block['lines']:
            for w in line['words']:
                eva = w['eva_primary']

                # Very long words (>12 chars)
                if len(eva) > 12:
                    very_long.append((fid, eva, len(eva)))

                # Contains @ (special symbols)
                if '@' in eva:
                    unusual[eva] += 1

                # Contains ? (uncertain readings)
                if '?' in eva:
                    unusual[eva] += 1

                # Contains digits or unusual chars
                if any(c.isdigit() for c in eva):
                    contains_numbers.append((fid, eva))

if very_long:
    very_long.sort(key=lambda x: -x[2])
    print(f'\n  Very long words (>12 chars): {len(very_long)}')
    for fid, eva, length in very_long[:15]:
        print(f'    {fid:>8s}: {eva} ({length} chars)')

if unusual:
    print(f'\n  Words with special characters (@, ?): {len(unusual)}')
    for w, n in unusual.most_common(10):
        print(f'    {w}: {n}x')

# Words that have NO morphology at all
no_morph = Counter()
has_morph = 0
for fid, folio in vms['folios'].items():
    for block in folio['blocks']:
        for line in block['lines']:
            for w in line['words']:
                eva = w['eva_primary']
                if eva in LOGOS:
                    continue
                morph = w.get('morphology') or {}
                if not morph.get('root'):
                    no_morph[eva] += 1
                else:
                    has_morph += 1

print(f'\n  Words with morphology: {has_morph}')
print(f'  Words WITHOUT morphology (non-logo): {sum(no_morph.values())}')
print(f'  Unique words without morphology: {len(no_morph)}')
print(f'  Most common unmorphed:')
for w, n in no_morph.most_common(15):
    print(f'    {w:>15s}: {n:>4d}x')


# ================================================================
# RULE 6: Section coherence (words exclusive to sections)
# ================================================================
print(f'\n{"="*70}')
print('RULE 6 — Cross-section word leakage')
print('='*70)

# Find words that appear in ONLY one section
word_sections = defaultdict(set)
for fid, folio in vms['folios'].items():
    sec = folio['metadata']['section']
    for block in folio['blocks']:
        for line in block['lines']:
            for w in line['words']:
                eva = w['eva_primary']
                if len(eva) >= 4:
                    word_sections[eva].add(sec)

single_section = Counter()
multi_section = 0
for w, secs in word_sections.items():
    if len(secs) == 1:
        single_section[list(secs)[0]] += 1
    else:
        multi_section += 1

print(f'  Words in exactly 1 section: {sum(single_section.values())}')
print(f'  Words in 2+ sections: {multi_section}')
print(f'  By section:')
for sec, n in single_section.most_common():
    total_sec = sum(1 for w, s in word_sections.items() if sec in s)
    pct = n * 100 // max(total_sec, 1)
    print(f'    {sec:>12s}: {n} exclusive ({pct}% of its vocabulary)')

# ================================================================
# SAVE anomalies
# ================================================================
output = {
    'gallows_initial_pct': pct,
    'n_at_end_pct': pct_n,
    'q_at_start_pct': pct_q,
    'am_positions': dict(am_positions),
    'very_long_words': [(f, e, l) for f, e, l in very_long[:20]],
    'no_morph_top': dict(no_morph.most_common(20)),
    'section_exclusivity': dict(single_section),
}

with open(os.path.join(RESULTS, 'audit_structural.json'), 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f'\nSaved audit_structural.json')
