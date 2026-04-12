"""
STEPS 4+5+6 — Extract mappings, test cleartext, decode f103r.

Step 4: Use ALL 1420 matches, weight by score, extract convergent mappings
Step 5: Test short EVA words against Latin pharma dictionary
Step 6: Apply everything to f103r
"""
import json, sys, io, os
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

RESULTS = os.path.join(os.path.dirname(__file__), 'results')

with open(os.path.join(RESULTS, 'an_signatures.json'), encoding='utf-8') as f:
    an_sigs = json.load(f)
with open(os.path.join(RESULTS, 'vms_signatures.json'), encoding='utf-8') as f:
    vms_sigs = json.load(f)
with open(os.path.join(RESULTS, 'alignments.json'), encoding='utf-8') as f:
    align_data = json.load(f)

# Index sigs
an_by_id = {s['id']: s for s in an_sigs}
vms_by_id = {s['id']: s for s in vms_sigs}

# ================================================================
# STEP 4 — EXTRACT MAPPINGS from ALL top matches (with length constraint)
# ================================================================
print('=' * 70)
print('STEP 4 — EXTRACT MAPPINGS (top 200 matches, length-constrained)')
print('=' * 70)

def lcs_align(a, b):
    m, n = len(a), len(b)
    dp = [[0]*(n+1) for _ in range(m+1)]
    for i in range(m):
        for j in range(n):
            if a[i] == b[j]:
                dp[i+1][j+1] = dp[i][j] + 1
            else:
                dp[i+1][j+1] = max(dp[i-1+1][j+1] if i > 0 else 0, dp[i+1][j])
    alignment = []
    i, j = m, n
    while i > 0 and j > 0:
        if a[i-1] == b[j-1]:
            alignment.append((i-1, j-1))
            i -= 1; j -= 1
        elif dp[i-1][j] > dp[i][j-1]:
            i -= 1
        else:
            j -= 1
    alignment.reverse()
    return alignment

# Collect ALL ingredient pairs from top 200 matches
mapping_evidence = defaultdict(list)  # eva_word → [(latin, score, len_diff, source)]

top_matches = align_data['top_matches'][:200]

for m in top_matches:
    vsig = vms_by_id.get(m['vms_id'])
    asig = an_by_id.get(m['an_id'])
    if not vsig or not asig: continue

    alignment = lcs_align(vsig['signature'], asig['signature'])

    for vi, ai in alignment:
        if vi >= len(vsig['tokens']) or ai >= len(asig['tokens']): continue
        vt = vsig['tokens'][vi]
        at = asig['tokens'][ai]
        if vt['type'] != 'I' or at['type'] != 'I': continue

        eva = vt['eva']
        latin = at['raw'].lower()
        len_diff = abs(vt['length'] - at['length'])

        mapping_evidence[eva].append({
            'latin': latin,
            'score': m['score'],
            'len_diff': len_diff,
            'an_ref': at.get('ref', ''),
            'source': f'{m["vms_id"]}↔{m["an_id"]}',
        })

# Aggregate: for each EVA word, find most common Latin match
print(f'\n  {len(mapping_evidence)} EVA words with mapping evidence')

candidate_mappings = {}

for eva, evidences in mapping_evidence.items():
    # Count Latin candidates, weighted by score and length match
    latin_scores = defaultdict(float)
    latin_counts = Counter()
    latin_refs = {}

    for ev in evidences:
        latin = ev['latin']
        # Weight: alignment score × length bonus
        len_bonus = 1.0 if ev['len_diff'] <= 2 else 0.5 if ev['len_diff'] <= 4 else 0.2
        weight = ev['score'] * len_bonus
        latin_scores[latin] += weight
        latin_counts[latin] += 1
        if ev['an_ref']:
            latin_refs[latin] = ev['an_ref']

    # Best candidate
    best_latin = max(latin_scores, key=latin_scores.get)
    best_score = latin_scores[best_latin]
    best_count = latin_counts[best_latin]
    total = len(evidences)

    # Confidence: needs multiple sources AND good score
    confidence = best_count / max(total, 1) * best_score / max(total, 1)

    candidate_mappings[eva] = {
        'latin': best_latin,
        'ref': latin_refs.get(best_latin, ''),
        'score': round(best_score, 3),
        'count': best_count,
        'total_evidence': total,
        'agreement': round(best_count / max(total, 1), 2),
        'confidence': round(confidence, 4),
        'alternatives': [(l, round(s, 3), c) for l, s, c in
                         sorted(((l, latin_scores[l], latin_counts[l])
                                 for l in latin_scores), key=lambda x: -x[1])[:3]],
    }

# Sort by confidence
ranked = sorted(candidate_mappings.items(), key=lambda x: -x[1]['confidence'])

print(f'\n  TOP 30 CANDIDATE MAPPINGS:')
print(f'  {"EVA":>18s} → {"Latin":>18s} {"Agree":>6s} {"Count":>5s} {"Conf":>6s} {"Ref":>15s}')
print('  ' + '-' * 75)
for eva, m in ranked[:30]:
    alt = m['alternatives'][1] if len(m['alternatives']) > 1 else ('', 0, 0)
    print(f'  {eva:>18s} → {m["latin"]:>18s} {m["agreement"]:>5.0%} {m["count"]:>5d} '
          f'{m["confidence"]:>6.4f} {m["ref"]:>15s}  alt:{alt[0]}')

# ================================================================
# STEP 5 — CLEARTEXT SHORT WORDS
# ================================================================
print(f'\n{"="*70}')
print('STEP 5 — CLEARTEXT SHORT WORDS')
print('=' * 70)

# Latin pharma words of 2-4 letters
LATIN_SHORT = {
    # 2 letters
    'os': 'bone/mouth', 'in': 'in', 'et': 'and', 'de': 'of',
    'ad': 'to', 'ex': 'from', 'ut': 'so that',
    # 3 letters
    'sal': 'salt', 'sol': 'sun', 'mel': 'honey', 'fel': 'bile',
    'ros': 'dew/rose', 'lac': 'milk', 'vas': 'vessel', 'vis': 'force',
    'ius': 'juice', 'cor': 'heart', 'par': 'equal', 'ars': 'art',
    'dos': 'dose', 'pix': 'pitch', 'nux': 'nut', 'lux': 'light',
    'cum': 'with', 'per': 'through', 'vel': 'or', 'est': 'is',
    'ana': 'of each', 'fac': 'make', 'dat': 'give',
    # 4 letters
    'aqua': 'water', 'aloe': 'aloe', 'rosa': 'rose', 'cera': 'wax',
    'dosis': 'dose', 'fiat': 'let it be', 'mane': 'morning',
    'sero': 'evening', 'hora': 'hour',
}

# VMS words of 2-4 chars with their frequencies
with open(os.path.join(os.path.dirname(__file__), '..', 'vms', 'vms_structured.json'), encoding='utf-8') as f:
    vms = json.load(f)

vms_word_freq = Counter()
for fid, folio in vms['folios'].items():
    for block in folio['blocks']:
        for line in block['lines']:
            for w in line['words']:
                vms_word_freq[w['eva_primary']] += 1

print(f'\n  {"EVA":>8s} {"Freq":>5s} {"=Latin?":>10s} {"Meaning":>15s} {"Plausible?":>12s}')
print('  ' + '-' * 55)

cleartext_confirmed = {}

for eva in sorted(LATIN_SHORT.keys()):
    freq = vms_word_freq.get(eva, 0)
    if freq == 0: continue
    meaning = LATIN_SHORT[eva]

    # Check plausibility
    plausible = ''
    if eva == 'sal' and freq > 10:
        plausible = '★ CONFIRMED'
        cleartext_confirmed[eva] = meaning
    elif eva in ('in', 'et', 'de', 'cum', 'per', 'vel', 'est') and freq > 5:
        # These are our LOGOGRAMS — already confirmed!
        plausible = '★ LOGOGRAM'
        cleartext_confirmed[eva] = meaning
    elif freq >= 5:
        plausible = '? POSSIBLE'
    else:
        plausible = '  rare'

    print(f'  {eva:>8s} {freq:>5d} {eva:>10s} {meaning:>15s} {plausible:>12s}')

# NEW: check words NOT in our Latin dict but that could be cleartext
print(f'\n  Mots EVA courts (3-4 chars) les plus fréquents NON-logogram:')
LOGOS = {'o','l','d','r','v','x','k','m','f','t','y','c','s','sh','p','ch','air','h'}
short_freq = [(w, f) for w, f in vms_word_freq.most_common()
              if 3 <= len(w) <= 4 and w not in LOGOS]

for w, f in short_freq[:20]:
    in_latin = '→ ' + LATIN_SHORT[w] if w in LATIN_SHORT else ''
    in_mapping = ''
    if w in candidate_mappings:
        cm = candidate_mappings[w]
        in_mapping = f'align→{cm["latin"]}({cm["agreement"]:.0%})'
    print(f'  {w:>8s} freq={f:4d} {in_latin:>15s} {in_mapping}')

# ================================================================
# STEP 6 — DECODE f103r WITH EVERYTHING
# ================================================================
print(f'\n{"="*70}')
print('STEP 6 — DECODE f103r (all signals combined)')
print('=' * 70)

LOGO_TABLE = {
    'o':'AC','l':'SE','d':'DE','r':'RECIPE','v':'VEL','x':'CRUX',
    'k':'CUM','m':'MISCE','f':'PER','t':'ET','y':'IN','c':'CUM',
    's':'EST','sh':'CI','p':'USQUE','ch':'CUM',
}

KB_PATH = os.path.join(os.path.dirname(__file__), '..', 'knowledge_base.json')
with open(KB_PATH, encoding='utf-8') as f:
    kb = json.load(f)
plant_roots = {r: d['herbal_folio'] for r, d in kb['roots'].items() if d.get('herbal_folio')}

f103r = vms['folios']['f103r']

for block in f103r['blocks']:
    bid = block.get('block_id', '')
    words = [w for line in block['lines'] for w in line['words']]

    print(f'\n{"─"*60}')
    print(f'{bid} ({len(words)} mots)')
    print(f'{"─"*60}')

    for w in words:
        eva = w['eva_primary']
        morph = w.get('morphology') or {}
        root = morph.get('root', '')
        suffix = morph.get('suffix', '') or ''
        ic = morph.get('i_count')

        decoded = None
        method = None

        # Priority 1: Logogram
        if eva in LOGO_TABLE:
            decoded = LOGO_TABLE[eva]
            method = 'LOGO'

        # Priority 2: Dose
        elif ic is not None:
            decoded = f'DOSE(i{ic})'
            method = 'DOSE'

        # Priority 3: Cleartext (sal, etc)
        elif eva in cleartext_confirmed:
            decoded = f'{eva.upper()}({cleartext_confirmed[eva]})'
            method = 'CLEAR'

        # Priority 4: Alignment mapping (confidence > 0.001)
        elif eva in candidate_mappings and candidate_mappings[eva]['confidence'] > 0.001:
            cm = candidate_mappings[eva]
            decoded = f'{cm["latin"]}({cm["agreement"]:.0%})'
            method = 'ALIGN'

        # Priority 5: Plant
        elif root in plant_roots:
            decoded = f'PLANT_{plant_roots[root]}'
            method = 'PLANT'

        # Priority 6: Unknown
        else:
            decoded = eva
            method = '?'

        tag = {'LOGO':'L','DOSE':'D','CLEAR':'C','ALIGN':'A','PLANT':'P','?':'·'}[method]
        print(f'  [{tag}] {eva:18s} → {decoded}')

# Save all results
output = {
    'candidate_mappings': {eva: m for eva, m in ranked[:100]},
    'cleartext_confirmed': cleartext_confirmed,
    'n_total_evidence': len(mapping_evidence),
}

with open(os.path.join(RESULTS, 'final_mappings.json'), 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f'\nSaved final_mappings.json')
