"""
ATTACK C part 2 — Word-by-word alignment of best VMS↔AN signature matches.

For each strong match (d < 0.10), align VMS words with AN tokens by:
1. Position (relative position in recipe)
2. Type inference (VMS dose → AN DOSE, VMS logogram → AN VERB/CONJ)
3. Pattern matching (word length, suffix, root)

Goal: produce candidate mappings EVA_word → Latin_word for convergence testing.
"""
import json, sys, io, os
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.dirname(__file__)
VMS_PATH = os.path.join(BASE, '..', '..', 'vms', 'vms_structured.json')
AN_PATH = os.path.join(BASE, '..', '..', '..', 'attacks', 'RECIPE_DATASET', 'S01_AN.json')
RESULTS = os.path.join(BASE, 'results')

LOGOGRAMS = {'o','l','d','r','v','x','k','m','f','t','y','c','s','sh','p','air','ch'}
LOGO_MAP = {
    'o': 'ac', 'l': 'se', 'd': 'de', 'r': 'recipe', 'v': 'vel',
    'x': 'crux', 'k': 'cum', 'm': 'misce', 'f': 'per', 't': 'el',
    'y': 'in', 'c': 'cum', 's': 'est', 'sh': 'ci', 'p': 'usque',
    'ch': 'cum', 'air': 'air',
}

# ================================================================
# Load data
# ================================================================
with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)
with open(AN_PATH, encoding='utf-8') as f:
    an_data = json.load(f)

# Index AN recipes by id
an_by_id = {e['id']: e for e in an_data['entries']}

# Build VMS recipe word lists
f103r = vms['folios']['f103r']
vms_blocks = {}
for b in f103r['blocks']:
    words = []
    for line in b['lines']:
        for w in line['words']:
            morph = w.get('morphology', {})
            words.append({
                'eva': w['eva_primary'],
                'root': morph.get('root', ''),
                'suffix': morph.get('suffix', ''),
                'i_count': morph.get('i_count'),
                'is_logo': w['eva_primary'] in LOGOGRAMS,
                'type_guess': 'LOGO' if w['eva_primary'] in LOGOGRAMS
                              else 'DOSE' if morph.get('i_count') is not None
                              else 'CONTENT',
            })
    vms_blocks[b['block_id']] = words

# ================================================================
# Best matches from signature analysis
# ================================================================
BEST_PAIRS = [
    ('f103r_B01', 'AN_012', 0.029),
    ('f103r_B02', 'AN_011', 0.028),
    ('f103r_B03', 'AN_041', 0.042),
    ('f103r_B03', 'AN_148', 0.082),
    ('f103r_B04', 'AN_095', 0.076),
    ('f103r_B07', 'AN_097', 0.034),
    ('f103r_B08', 'AN_028', 0.090),
    ('f103r_B09', 'AN_095', 0.056),
    ('f103r_B10', 'AN_095', 0.067),
    ('f103r_B16', 'AN_097', 0.052),
    ('f103r_B17', 'AN_090', 0.081),
    ('f103r_B18', 'AN_024', 0.057),
]

print('=' * 70)
print('WORD-BY-WORD ALIGNMENT: VMS f103r vs AN recipes')
print('=' * 70)

all_alignments = []
all_candidates = defaultdict(list)  # eva_word → [(latin_word, type, context, confidence)]

for vms_id, an_id, dist in BEST_PAIRS:
    vms_words = vms_blocks[vms_id]
    an_entry = an_by_id[an_id]
    an_tokens = an_entry['tokens']

    print(f'\n{"="*70}')
    print(f'{vms_id} ↔ {an_id} "{an_entry["name"][:50]}" (d={dist:.3f})')
    print(f'VMS: {len(vms_words)} words | AN: {len(an_tokens)} tokens')
    print('-' * 70)

    # ================================================================
    # Strategy 1: Positional alignment
    # Map relative positions: VMS word i/N → AN token j/M
    # ================================================================
    n_vms = len(vms_words)
    n_an = len(an_tokens)

    print('\nPOSITIONAL ALIGNMENT:')
    alignment = []
    for i, vw in enumerate(vms_words):
        rel_pos = i / max(n_vms - 1, 1)
        j = int(rel_pos * (n_an - 1))
        j = min(j, n_an - 1)
        at = an_tokens[j]

        # Check type compatibility
        type_match = '?'
        if vw['is_logo']:
            latin = LOGO_MAP.get(vw['eva'], '?')
            type_match = f'LOGO→{latin}'
        elif vw['type_guess'] == 'DOSE' and at['type'] in ('DOSE', 'QTY', 'UNIT'):
            type_match = 'DOSE✓'
        elif vw['type_guess'] == 'CONTENT' and at['type'] == 'INGR':
            type_match = 'INGR?'
        elif vw['type_guess'] == 'CONTENT' and at['type'] in ('VERB', 'GRAM', 'PREP', 'CONJ'):
            type_match = f'FUNC({at["type"]})'

        alignment.append({
            'vms_pos': i,
            'vms_eva': vw['eva'],
            'vms_type': vw['type_guess'],
            'an_pos': j,
            'an_raw': at['raw'],
            'an_type': at['type'],
            'an_ref': at.get('ref', ''),
            'type_match': type_match,
        })

        # Show first 15 alignments
        if i < 15 or i >= n_vms - 3:
            print(f'  [{i:2d}] {vw["eva"]:15s} ({vw["type_guess"]:7s}) '
                  f'↔ [{j:2d}] {at["raw"]:15s} ({at["type"]:5s}) {type_match}')
        elif i == 15:
            print(f'  ... ({n_vms - 18} more) ...')

    # ================================================================
    # Strategy 2: Type-based alignment
    # Align DOSE↔DOSE, then fill INGR in between
    # ================================================================
    vms_doses = [(i, w) for i, w in enumerate(vms_words) if w['type_guess'] == 'DOSE']
    an_doses = [(i, t) for i, t in enumerate(an_tokens) if t['type'] in ('DOSE', 'QTY')]

    print(f'\nTYPE-BASED: {len(vms_doses)} VMS doses vs {len(an_doses)} AN doses')

    # Align doses by relative position
    dose_pairs = []
    for vi, (vpos, vw) in enumerate(vms_doses):
        if not an_doses:
            break
        v_rel = vpos / max(n_vms - 1, 1)
        best_j = min(range(len(an_doses)),
                     key=lambda j: abs(an_doses[j][0] / max(n_an - 1, 1) - v_rel))
        apos, at = an_doses[best_j]
        dose_pairs.append((vpos, vw, apos, at))
        print(f'  DOSE: [{vpos}] {vw["eva"]:15s} ↔ [{apos}] {at["raw"]:10s} ({at.get("ref","")})')

    # ================================================================
    # Strategy 3: Ingredient segments between doses
    # ================================================================
    print(f'\nINGREDIENT SEGMENTS:')

    # Get AN ingredient blocks (between doses)
    an_segments = []
    prev_dose = 0
    for apos, at in an_doses + [(n_an, None)]:
        segment = [(i, t) for i, t in enumerate(an_tokens[prev_dose:apos], prev_dose)
                   if t['type'] == 'INGR']
        if segment:
            an_segments.append(segment)
        prev_dose = apos + 1

    # Get VMS content blocks (between doses)
    vms_segments = []
    prev_dose = 0
    dose_positions = [vpos for vpos, _ in vms_doses] + [n_vms]
    for vpos in dose_positions:
        segment = [(i, w) for i, w in enumerate(vms_words[prev_dose:vpos], prev_dose)
                   if w['type_guess'] == 'CONTENT']
        if segment:
            vms_segments.append(segment)
        prev_dose = vpos + 1

    n_seg = min(len(vms_segments), len(an_segments))
    for s in range(n_seg):
        vs = vms_segments[s]
        ans = an_segments[s]
        print(f'\n  Segment {s}: {len(vs)} VMS content ↔ {len(ans)} AN ingredients')
        for k in range(min(len(vs), len(ans))):
            vpos, vw = vs[k]
            apos, at = ans[k]
            confidence = 0.3  # base positional
            if len(vs) == len(ans):
                confidence += 0.2  # same segment size
            if k == 0:
                confidence += 0.1  # first in segment
            print(f'    {vw["eva"]:18s} → {at["raw"]:18s} ({at.get("ref",""):15s}) conf={confidence:.1f}')

            all_candidates[vw['eva']].append({
                'latin': at['raw'],
                'ref': at.get('ref', ''),
                'type': at['type'],
                'source': f'{vms_id}↔{an_id}',
                'strategy': 'segment_positional',
                'confidence': confidence,
            })

    all_alignments.append({
        'vms_id': vms_id,
        'an_id': an_id,
        'distance': dist,
        'n_vms': n_vms,
        'n_an': n_an,
        'n_dose_pairs': len(dose_pairs),
        'n_segments_aligned': n_seg,
        'alignment': alignment,
    })

# ================================================================
# CONVERGENCE: which EVA words get the SAME Latin mapping from multiple pairs?
# ================================================================
print('\n\n' + '=' * 70)
print('CONVERGENCE ANALYSIS: EVA words with multiple candidate mappings')
print('=' * 70)

convergent = []
for eva, candidates in sorted(all_candidates.items(), key=lambda x: -len(x[1])):
    if len(candidates) < 2:
        continue

    # Count latin candidates
    latin_counts = Counter(c['latin'] for c in candidates)
    top_latin, top_count = latin_counts.most_common(1)[0]
    total = len(candidates)
    agreement = top_count / total

    refs = set(c['ref'] for c in candidates if c['ref'])

    convergent.append({
        'eva': eva,
        'n_sources': total,
        'top_latin': top_latin,
        'agreement': agreement,
        'all_candidates': dict(latin_counts),
        'refs': list(refs),
    })

    if total >= 2:
        print(f'\n  {eva:18s} → {top_latin:15s} '
              f'({top_count}/{total} = {agreement:.0%} agreement)')
        for latin, count in latin_counts.most_common(5):
            ref = next((c['ref'] for c in candidates if c['latin'] == latin and c['ref']), '')
            print(f'    {latin:15s} x{count}  {ref}')

convergent.sort(key=lambda x: (-x['agreement'], -x['n_sources']))

print(f'\n\nTotal EVA words with 2+ candidate mappings: {len(convergent)}')
print(f'With >50% agreement: {sum(1 for c in convergent if c["agreement"] > 0.5)}')
print(f'With 100% agreement: {sum(1 for c in convergent if c["agreement"] == 1.0)}')

# ================================================================
# Save
# ================================================================
results = {
    'pairs_analyzed': len(BEST_PAIRS),
    'alignments': [{k: v for k, v in a.items() if k != 'alignment'} for a in all_alignments],
    'convergent_candidates': convergent,
    'all_candidates': {eva: cands for eva, cands in all_candidates.items()},
    'summary': {
        'total_eva_with_candidates': len(all_candidates),
        'total_convergent': len(convergent),
        'high_agreement': sum(1 for c in convergent if c['agreement'] > 0.5),
        'perfect_agreement': sum(1 for c in convergent if c['agreement'] == 1.0),
    }
}

with open(os.path.join(RESULTS, 'crib_word_alignment.json'), 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print('\nSaved crib_word_alignment.json')
