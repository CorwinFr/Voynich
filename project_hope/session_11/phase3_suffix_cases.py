"""
PHASE 3 — Suffix → Latin Case Verification

Test: do EVA suffixes correlate with positional/functional roles
that match Latin grammatical cases?

Latin case usage in pharma recipes:
- GENITIVE (-is, -ae, -orum): ingredient lists ("recipe rosae piperis croci")
- ABLATIVE (-o, -a, -e): with prepositions ("cum aqua", "in vino")
- ACCUSATIVE (-am, -um): direct objects ("accipe rosam")
- NOMINATIVE (-a, -us, -um): subjects/titles
"""
import json, sys, io, os
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

KB_PATH = os.path.join(os.path.dirname(__file__), '..', 'knowledge_base.json')
VMS_PATH = os.path.join(os.path.dirname(__file__), '..', 'vms', 'vms_structured.json')

with open(KB_PATH, encoding='utf-8') as f:
    kb = json.load(f)
with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)

LOGOGRAM_SET = set(kb['logograms'].keys())
LOGO_LATIN = {eva: data['latin'] for eva, data in kb['logograms'].items()}

# ================================================================
# 1. For each suffix, measure: position, what precedes, what follows
# ================================================================
print('Analyzing suffix contexts in pharma...')

suffix_context = defaultdict(lambda: {
    'count': 0,
    'positions': [],          # relative position in block
    'after_logo': Counter(),  # which logogram precedes
    'after_dose': 0,          # preceded by dose
    'after_same_suffix': 0,   # preceded by word with same suffix
    'before_logo': Counter(), # which logogram follows
    'before_dose': 0,         # followed by dose
    'at_block_start': 0,      # first 2 words of block
    'at_block_end': 0,        # last 2 words of block
    'after_gallows_word': 0,  # after a gallows-initial word
})

for fid, folio in vms['folios'].items():
    if folio['metadata']['section'] != 'pharma': continue
    for block in folio['blocks']:
        words = [w for line in block['lines'] for w in line['words']]
        n = len(words)
        if n < 3: continue

        for i, w in enumerate(words):
            eva = w['eva_primary']
            if eva in LOGOGRAM_SET: continue
            morph = w.get('morphology') or {}
            suffix = morph.get('suffix', '') or ''
            if not suffix: continue

            sc = suffix_context[suffix]
            sc['count'] += 1
            sc['positions'].append(i / max(n - 1, 1))

            # Block edges
            if i < 2: sc['at_block_start'] += 1
            if i >= n - 2: sc['at_block_end'] += 1

            # Previous word context
            if i > 0:
                prev = words[i-1]
                prev_eva = prev['eva_primary']
                if prev_eva in LOGOGRAM_SET:
                    sc['after_logo'][LOGO_LATIN.get(prev_eva, prev_eva)] += 1
                if (prev.get('morphology') or {}).get('i_count') is not None:
                    sc['after_dose'] += 1
                if prev_eva[0] in 'ptkf' and prev_eva not in LOGOGRAM_SET:
                    sc['after_gallows_word'] += 1
                prev_suf = (prev.get('morphology') or {}).get('suffix', '') or ''
                if prev_suf == suffix:
                    sc['after_same_suffix'] += 1

            # Next word context
            if i < n - 1:
                nxt = words[i+1]
                nxt_eva = nxt['eva_primary']
                if nxt_eva in LOGOGRAM_SET:
                    sc['before_logo'][LOGO_LATIN.get(nxt_eva, nxt_eva)] += 1
                if (nxt.get('morphology') or {}).get('i_count') is not None:
                    sc['before_dose'] += 1

# ================================================================
# 2. Analyze and assign Latin case hypotheses
# ================================================================
print('\n' + '=' * 70)
print('SUFFIX ANALYSIS — Position & Context')
print('=' * 70)

case_hypotheses = {}

for suffix in sorted(suffix_context.keys(), key=lambda s: -suffix_context[s]['count']):
    sc = suffix_context[suffix]
    n = sc['count']
    if n < 20: continue

    avg_pos = sum(sc['positions']) / len(sc['positions'])
    start_pct = sc['at_block_start'] * 100 // n
    end_pct = sc['at_block_end'] * 100 // n
    after_dose_pct = sc['after_dose'] * 100 // n
    before_dose_pct = sc['before_dose'] * 100 // n
    after_same_pct = sc['after_same_suffix'] * 100 // n
    after_gal_pct = sc['after_gallows_word'] * 100 // n

    # Top preceding logograms
    top_after_logo = sc['after_logo'].most_common(3)
    top_before_logo = sc['before_logo'].most_common(3)

    # Case hypothesis based on patterns
    hypothesis = '?'
    evidence = []

    if end_pct > 30:
        hypothesis = 'TERMINATEUR'
        evidence.append(f'end={end_pct}%')
    elif start_pct > 15:
        hypothesis = 'NOMINATIF/TITRE'
        evidence.append(f'start={start_pct}%')
    elif after_dose_pct > 25:
        hypothesis = 'POST-DOSE (nouveau ingrédient)'
        evidence.append(f'after_dose={after_dose_pct}%')
    elif before_dose_pct > 25:
        hypothesis = 'GÉNITIF (ingr avant dose)'
        evidence.append(f'before_dose={before_dose_pct}%')
    elif after_same_pct > 30:
        hypothesis = 'LISTE (séquence d\'ingrédients)'
        evidence.append(f'after_same={after_same_pct}%')

    # Logogram context
    if top_after_logo:
        for logo, cnt in top_after_logo:
            if cnt > n * 0.05:
                evidence.append(f'after_{logo}={cnt}')

    case_hypotheses[suffix] = hypothesis

    print(f'\n  -{suffix:6s} (n={n:4d}) avg_pos={avg_pos:.2f}')
    print(f'    start={start_pct:2d}% end={end_pct:2d}% '
          f'after_dose={after_dose_pct:2d}% before_dose={before_dose_pct:2d}% '
          f'after_same={after_same_pct:2d}% after_gallow={after_gal_pct:2d}%')
    if top_after_logo:
        print(f'    After logo: {", ".join(f"{l}({c})" for l,c in top_after_logo)}')
    if top_before_logo:
        print(f'    Before logo: {", ".join(f"{l}({c})" for l,c in top_before_logo)}')
    print(f'    → HYPOTHESIS: {hypothesis} [{", ".join(evidence)}]')

# ================================================================
# 3. Summary table
# ================================================================
print('\n' + '=' * 70)
print('SUFFIX → LATIN CASE MAPPING')
print('=' * 70)

print(f'\n{"Suffix":>8s} {"Count":>6s} {"AvgPos":>7s} {"Start%":>7s} {"End%":>6s} '
      f'{"AfDose":>7s} {"BfDose":>7s} {"Hypothesis":>25s}')
print('-' * 85)

for suffix in sorted(suffix_context.keys(), key=lambda s: -suffix_context[s]['count']):
    sc = suffix_context[suffix]
    n = sc['count']
    if n < 20: continue
    avg_pos = sum(sc['positions']) / len(sc['positions'])
    start_pct = sc['at_block_start'] * 100 // n
    end_pct = sc['at_block_end'] * 100 // n
    ad = sc['after_dose'] * 100 // n
    bd = sc['before_dose'] * 100 // n
    hyp = case_hypotheses.get(suffix, '?')

    print(f'{suffix:>8s} {n:>6d} {avg_pos:>7.2f} {start_pct:>6d}% {end_pct:>5d}% '
          f'{ad:>6d}% {bd:>6d}% {hyp:>25s}')

# Update KB
for suffix, hyp in case_hypotheses.items():
    if suffix in kb['suffixes']:
        kb['suffixes'][suffix]['latin_case'] = hyp

with open(KB_PATH, 'w', encoding='utf-8') as f:
    json.dump(kb, f, indent=2, ensure_ascii=False)

print(f'\nUpdated knowledge_base.json with suffix hypotheses')
