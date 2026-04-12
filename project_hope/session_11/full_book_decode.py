"""
FULL BOOK STRUCTURAL DECODE — All sections, all folios.

Apply the structural decoder to the ENTIRE VMS:
- herbal_a, herbal_b, pharma, balnea, astro, cosmo, bio, volvelle

Analyze per section, per folio:
- Type distributions
- Anomalies (folios that don't fit their section)
- Cross-section comparisons
- Distribution errors (folios misclassified by ZL?)
"""
import json, sys, io, os
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

KB_PATH = os.path.join(os.path.dirname(__file__), '..', 'knowledge_base.json')
VMS_PATH = os.path.join(os.path.dirname(__file__), '..', 'vms', 'vms_structured.json')
RESULTS = os.path.dirname(__file__)

with open(KB_PATH, encoding='utf-8') as f:
    kb = json.load(f)
with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)

LOGOS = {eva: data['latin'] for eva, data in kb['logograms'].items()}
LOGOGRAM_SET = set(LOGOS.keys())

# Rebuild root codes from KB
plant_roots = {}
for root, data in kb['roots'].items():
    if data.get('herbal_folio'):
        plant_roots[root] = data['herbal_folio']

# Dose-adjacency reclassification (from previous analysis)
with open(os.path.join(RESULTS, 'reclassified_analysis.json'), encoding='utf-8') as f:
    reclass = json.load(f)
reclassified = reclass.get('reclassified_codes', {})

# Root classification
root_codes = {}
for root, data in kb['roots'].items():
    if root in plant_roots:
        root_codes[root] = f'PLANT_{plant_roots[root]}'
    elif data.get('block_initial_pct', 0) > 30:
        root_codes[root] = f'VERB_{root}'
    elif data.get('total_freq', 0) >= 3:
        # Check if reclassified
        for fc, new_type in reclassified.items():
            func_info = kb.get('roots', {}).get(root, {})
            # Match by checking func registry
        root_codes[root] = f'INGR_{root}'

GALLOWS = {'p': 'Rp', 't': 'Ac', 'k': 'Mi', 'f': 'Fi'}

# ================================================================
# DECODE EVERY WORD IN THE MANUSCRIPT
# ================================================================
print('Decoding entire manuscript...')

all_folios = {}

for fid in sorted(vms['folios'].keys()):
    folio = vms['folios'][fid]
    section = folio['metadata']['section']

    folio_words = []
    for block in folio['blocks']:
        words = [w for line in block['lines'] for w in line['words']]
        has_star = block.get('separator') is not None

        for i, w in enumerate(words):
            eva = w['eva_primary']
            morph = w.get('morphology') or {}
            root = morph.get('root', '')
            suffix = morph.get('suffix', '') or ''
            ic = morph.get('i_count')

            if eva in LOGOGRAM_SET:
                wtype = 'LOGO'
            elif ic is not None:
                wtype = 'DOSE'
            elif i == 0 and has_star and eva[0] in 'ptkf' and eva not in LOGOGRAM_SET:
                wtype = 'VERB'
            elif root in plant_roots:
                wtype = 'PLANT'
            elif root and len(root) >= 2:
                # Check if this root is very frequent across all sections = functional
                rd = kb['roots'].get(root, {})
                total = rd.get('total_freq', 0)
                pharma = rd.get('pharma_freq', 0)
                herbal = rd.get('herbal_freq', 0)

                # Simple heuristic: if appears in 50%+ of all sections equally = FUNC
                # Otherwise = INGR
                if total >= 50 and pharma * 100 // max(total, 1) < 40 and herbal * 100 // max(total, 1) < 40:
                    wtype = 'FUNC'
                else:
                    wtype = 'INGR'
            else:
                wtype = 'UNK'

            folio_words.append(wtype)

    if folio_words:
        tc = Counter(folio_words)
        n = len(folio_words)
        all_folios[fid] = {
            'section': section,
            'n_words': n,
            'n_blocks': len(folio['blocks']),
            'counts': dict(tc),
            'pcts': {t: tc[t] * 100 // n for t in tc},
        }

# ================================================================
# 1. PER-SECTION AGGREGATE
# ================================================================
print('\n' + '=' * 70)
print('1. DISTRIBUTION PAR SECTION')
print('=' * 70)

section_agg = defaultdict(lambda: Counter())
section_words = defaultdict(int)
section_folios = defaultdict(int)

for fid, info in all_folios.items():
    section = info['section']
    section_folios[section] += 1
    section_words[section] += info['n_words']
    for t, c in info['counts'].items():
        section_agg[section][t] += c

print(f'\n{"Section":>12s} {"Folios":>6s} {"Words":>6s} '
      f'{"INGR%":>6s} {"DOSE%":>6s} {"PLANT%":>6s} {"FUNC%":>6s} '
      f'{"LOGO%":>6s} {"VERB%":>6s} {"UNK%":>5s}')
print('-' * 75)

for section in ['herbal_a', 'herbal_b', 'pharma', 'balnea', 'astro', 'cosmo', 'bio', 'volvelle']:
    if section not in section_agg: continue
    n = section_words[section]
    s = section_agg[section]
    print(f'{section:>12s} {section_folios[section]:>6d} {n:>6d} '
          f'{s["INGR"]*100//n:>5d}% {s["DOSE"]*100//n:>5d}% {s["PLANT"]*100//n:>5d}% '
          f'{s["FUNC"]*100//n:>5d}% {s["LOGO"]*100//n:>5d}% {s["VERB"]*100//n:>5d}% '
          f'{s["UNK"]*100//n:>4d}%')

# ================================================================
# 2. PER-FOLIO DETAIL WITH ANOMALY DETECTION
# ================================================================
print(f'\n{"="*70}')
print('2. TOUS LES FOLIOS — avec détection d\'anomalies')
print('=' * 70)

# Compute section averages for anomaly detection
section_avg = {}
for section in section_agg:
    n = section_words[section]
    s = section_agg[section]
    section_avg[section] = {t: s[t] * 100 // max(n, 1) for t in s}

anomalies = []

print(f'\n{"Folio":>8s} {"Section":>10s} {"Words":>5s} '
      f'{"INGR":>5s} {"DOSE":>5s} {"PLANT":>5s} {"FUNC":>5s} '
      f'{"LOGO":>5s} {"VERB":>5s} {"UNK":>4s} {"Signal":>20s}')
print('-' * 90)

for fid in sorted(all_folios.keys()):
    info = all_folios[fid]
    section = info['section']
    n = info['n_words']
    p = info['pcts']
    avg = section_avg.get(section, {})

    # Anomaly detection: >2x or <0.5x section average for key types
    signals = []

    ingr = p.get('INGR', 0)
    dose = p.get('DOSE', 0)
    plant = p.get('PLANT', 0)
    func = p.get('FUNC', 0)
    logo = p.get('LOGO', 0)
    verb = p.get('VERB', 0)
    unk = p.get('UNK', 0)

    avg_ingr = avg.get('INGR', 1)
    avg_dose = avg.get('DOSE', 1)
    avg_plant = avg.get('PLANT', 1)

    if avg_dose > 0 and dose > avg_dose * 2:
        signals.append('HIGH_DOSE')
    if avg_dose > 0 and dose < avg_dose * 0.3 and dose < 5:
        signals.append('LOW_DOSE')
    if avg_plant > 0 and plant > avg_plant * 2:
        signals.append('HIGH_PLANT')
    if unk > 20:
        signals.append('HIGH_UNK')
    if logo > 10:
        signals.append('HIGH_LOGO')
    if n < 20:
        signals.append('VERY_SHORT')
    if func > 30:
        signals.append('HIGH_FUNC')

    # Cross-section anomaly: looks like a different section
    if section in ('herbal_a', 'herbal_b') and dose > 15:
        signals.append('PHARMA_LIKE?')
    if section == 'pharma' and dose < 5 and plant > 10:
        signals.append('HERBAL_LIKE?')
    if section == 'balnea' and ingr < 10:
        signals.append('NON_RECIPE?')

    signal_str = ' '.join(signals) if signals else ''
    if signals:
        anomalies.append((fid, section, n, signals))

    print(f'{fid:>8s} {section:>10s} {n:>5d} '
          f'{ingr:>4d}% {dose:>4d}% {plant:>4d}% {func:>4d}% '
          f'{logo:>4d}% {verb:>4d}% {unk:>3d}% {signal_str:>20s}')

# ================================================================
# 3. ANOMALIES SUMMARY
# ================================================================
print(f'\n{"="*70}')
print(f'3. ANOMALIES ({len(anomalies)} folios)')
print('=' * 70)

for fid, section, n, signals in anomalies:
    print(f'  {fid:8s} ({section:10s}, {n:3d}w) : {", ".join(signals)}')

# ================================================================
# 4. SECTION SIGNATURES — what makes each section unique?
# ================================================================
print(f'\n{"="*70}')
print('4. SIGNATURES DE SECTION')
print('=' * 70)

for section in ['herbal_a', 'herbal_b', 'pharma', 'balnea', 'astro', 'cosmo', 'bio']:
    if section not in section_avg: continue
    avg = section_avg[section]
    n = section_words[section]

    # What's distinctive about this section?
    distinctive = []
    for t in ['INGR', 'DOSE', 'PLANT', 'FUNC', 'LOGO', 'VERB', 'UNK']:
        val = avg.get(t, 0)
        # Compare to global average
        global_avg = sum(section_agg[s].get(t, 0) for s in section_agg) * 100 // max(sum(section_words.values()), 1)
        if val > global_avg * 1.5:
            distinctive.append(f'{t}={val}%(+)')
        elif val < global_avg * 0.5 and global_avg > 2:
            distinctive.append(f'{t}={val}%(-)')

    print(f'\n  {section:>12s} ({section_folios[section]}f, {n}w):')
    print(f'    INGR={avg.get("INGR",0)}% DOSE={avg.get("DOSE",0)}% PLANT={avg.get("PLANT",0)}% '
          f'FUNC={avg.get("FUNC",0)}% LOGO={avg.get("LOGO",0)}%')
    if distinctive:
        print(f'    Distinctive: {", ".join(distinctive)}')

# ================================================================
# 5. HERBAL vs PHARMA — same system?
# ================================================================
print(f'\n{"="*70}')
print('5. HERBAL vs PHARMA — même système?')
print('=' * 70)

ha = section_avg.get('herbal_a', {})
hb = section_avg.get('herbal_b', {})
ph = section_avg.get('pharma', {})
ba = section_avg.get('balnea', {})

print(f'\n{"Type":>8s} {"Herbal_A":>10s} {"Herbal_B":>10s} {"Pharma":>10s} {"Balnea":>10s}')
print('-' * 50)
for t in ['INGR', 'DOSE', 'PLANT', 'FUNC', 'LOGO', 'VERB', 'UNK']:
    print(f'{t:>8s} {ha.get(t,0):>9d}% {hb.get(t,0):>9d}% {ph.get(t,0):>9d}% {ba.get(t,0):>9d}%')

# ================================================================
# 6. FOLIO CLUSTERING — which folios are most similar?
# ================================================================
print(f'\n{"="*70}')
print('6. FOLIOS QUI NE RESSEMBLENT PAS À LEUR SECTION')
print('=' * 70)

# For each folio, compute distance to its section average
for fid, info in sorted(all_folios.items()):
    section = info['section']
    avg = section_avg.get(section, {})
    n = info['n_words']
    if n < 10: continue

    # Euclidean distance in type-percentage space
    dist = 0
    for t in ['INGR', 'DOSE', 'PLANT', 'FUNC', 'LOGO', 'VERB']:
        diff = info['pcts'].get(t, 0) - avg.get(t, 0)
        dist += diff ** 2
    dist = dist ** 0.5

    # Also compute distance to OTHER sections
    best_other = None
    best_other_dist = 999
    for other_sec in section_avg:
        if other_sec == section: continue
        d2 = sum((info['pcts'].get(t, 0) - section_avg[other_sec].get(t, 0)) ** 2
                 for t in ['INGR', 'DOSE', 'PLANT', 'FUNC', 'LOGO', 'VERB']) ** 0.5
        if d2 < best_other_dist:
            best_other_dist = d2
            best_other = other_sec

    if best_other_dist < dist * 0.8:  # closer to another section
        print(f'  {fid:8s} ({section:10s}) → closer to {best_other:10s} '
              f'(own={dist:.1f}, other={best_other_dist:.1f})')

# ================================================================
# SAVE FULL RESULTS
# ================================================================
output = {
    'section_aggregates': {
        section: {
            'n_folios': section_folios[section],
            'n_words': section_words[section],
            'type_pcts': dict(section_avg.get(section, {})),
        }
        for section in section_agg
    },
    'folio_details': all_folios,
    'anomalies': [
        {'folio': fid, 'section': sec, 'n_words': n, 'signals': sigs}
        for fid, sec, n, sigs in anomalies
    ],
}

out_path = os.path.join(RESULTS, 'full_book_analysis.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f'\n\nSaved full_book_analysis.json')
print(f'Total: {len(all_folios)} folios, {sum(f["n_words"] for f in all_folios.values())} words')
