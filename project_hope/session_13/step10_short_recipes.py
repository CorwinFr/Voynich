"""
STEP 10 — Align SHORT VMS recipes with AN.

Short recipes have less ambiguity → stronger signal.
For each VMS block with 5-15 words:
  1. Count unique PREFIXES (= distinct concepts)
  2. Count DOSE markers
  3. Count FUNC words
  4. Find AN recipes with EXACT same profile
  5. Word-by-word alignment with LENGTH constraint
"""
import json, sys, io, os
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

VMS_PATH = os.path.join(os.path.dirname(__file__), '..', 'vms', 'vms_structured.json')
AN_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'attacks', 'RECIPE_DATASET', 'S01_AN.json')
RESULTS = os.path.join(os.path.dirname(__file__), 'results')

with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)
with open(AN_PATH, encoding='utf-8') as f:
    an = json.load(f)

LOGOS = {'o','l','d','r','v','x','k','m','f','t','y','c','s','sh','p','ch','air','h'}

# ================================================================
# 1. Find SHORT VMS pharma blocks
# ================================================================
print('=' * 70)
print('SHORT VMS RECIPES (5-20 words)')
print('=' * 70)

short_vms = []

for fid, folio in vms['folios'].items():
    if folio['metadata']['section'] != 'pharma': continue
    for block in folio['blocks']:
        if not block.get('separator'): continue
        words = []
        for line in block['lines']:
            for w in line['words']:
                eva = w['eva_primary']
                morph = w.get('morphology') or {}
                root = morph.get('root', '')
                suffix = morph.get('suffix', '') or ''
                ic = morph.get('i_count')
                is_logo = eva in LOGOS

                if is_logo:
                    wtype = 'L'
                elif ic is not None:
                    wtype = 'D'
                else:
                    wtype = 'W'

                words.append({
                    'eva': eva, 'root': root, 'suffix': suffix,
                    'type': wtype, 'length': len(eva), 'i_count': ic,
                })

        n = len(words)
        if 5 <= n <= 20:
            n_dose = sum(1 for w in words if w['type'] == 'D')
            n_logo = sum(1 for w in words if w['type'] == 'L')
            n_content = n - n_dose - n_logo
            unique_roots = len(set(w['root'] for w in words if w['type'] == 'W'))
            sig = ''.join(w['type'] for w in words)

            short_vms.append({
                'id': block.get('block_id', ''),
                'folio': fid,
                'n': n,
                'n_dose': n_dose,
                'n_content': n_content,
                'n_logo': n_logo,
                'unique_roots': unique_roots,
                'signature': sig,
                'words': words,
            })

short_vms.sort(key=lambda x: x['n'])
print(f'\n  {len(short_vms)} short recipes found')

for sv in short_vms[:20]:
    evas = ' '.join(w['eva'] for w in sv['words'])
    print(f'\n  {sv["id"]} ({sv["n"]}w, {sv["n_dose"]}D, {sv["n_content"]}W, {sv["n_logo"]}L)')
    print(f'    sig: {sv["signature"]}')
    print(f'    {evas}')

# ================================================================
# 2. Build AN profiles for SHORT recipes
# ================================================================
print(f'\n{"="*70}')
print('AN SHORT RECIPES')
print('=' * 70)

short_an = []

for entry in an['entries']:
    # Build simplified profile
    tokens = []
    for tok in entry['tokens']:
        if tok['type'] in ('GRAM','CONJ','PREP','COP'):
            continue
        if tok['type'] == 'INGR':
            tt = 'W'
        elif tok['type'] in ('DOSE','QTY','UNIT'):
            tt = 'D'
        elif tok['type'] == 'VERB':
            tt = 'V'
        else:
            tt = 'W'
        tokens.append({
            'raw': tok['raw'],
            'type': tt,
            'ref': tok.get('ref', ''),
            'length': len(tok['raw']),
        })

    n = len(tokens)
    if n < 5: continue

    n_dose = sum(1 for t in tokens if t['type'] == 'D')
    n_content = sum(1 for t in tokens if t['type'] == 'W')

    short_an.append({
        'id': entry['id'],
        'name': entry.get('name', ''),
        'n': n,
        'n_dose': n_dose,
        'n_content': n_content,
        'signature': ''.join(t['type'] for t in tokens),
        'tokens': tokens,
    })

short_an.sort(key=lambda x: x['n'])
print(f'\n  {len(short_an)} AN recipes with 5+ content tokens')

# ================================================================
# 3. PROFILE MATCHING — exact structural match
# ================================================================
print(f'\n{"="*70}')
print('PROFILE MATCHING')
print('=' * 70)

matches = []

for sv in short_vms:
    for sa in short_an:
        # Match criteria:
        # 1. Same number of content words (±2)
        # 2. Same number of doses (±1)
        # 3. Similar total length (±30%)
        if abs(sv['n_content'] - sa['n_content']) > 2: continue
        if abs(sv['n_dose'] - sa['n_dose']) > 1: continue
        if max(sv['n'], sa['n']) > min(sv['n'], sa['n']) * 1.5: continue

        # Compute signature similarity
        v_sig = sv['signature'].replace('L', '')  # ignore logos
        a_sig = sa['signature']

        # LCS
        m_len, n_len = len(v_sig), len(a_sig)
        if m_len == 0 or n_len == 0: continue
        prev = [0] * (n_len + 1)
        for i in range(m_len):
            curr = [0] * (n_len + 1)
            for j in range(n_len):
                if v_sig[i] == a_sig[j]:
                    curr[j+1] = prev[j] + 1
                else:
                    curr[j+1] = max(curr[j], prev[j+1])
            prev = curr
        lcs = prev[n_len]
        score = lcs / max(m_len, n_len)

        if score < 0.6: continue

        # Word-level alignment by type
        v_content = [w for w in sv['words'] if w['type'] == 'W']
        a_content = [t for t in sa['tokens'] if t['type'] == 'W']

        # Align by position and LENGTH
        pairs = []
        for k in range(min(len(v_content), len(a_content))):
            vw = v_content[k]
            aw = a_content[k]
            len_diff = abs(vw['length'] - aw['length'])
            pairs.append({
                'vms_eva': vw['eva'],
                'an_raw': aw['raw'],
                'an_ref': aw.get('ref', ''),
                'vms_len': vw['length'],
                'an_len': aw['length'],
                'len_diff': len_diff,
                'len_match': len_diff <= 2,
            })

        n_len_match = sum(1 for p in pairs if p['len_match'])
        len_match_pct = n_len_match * 100 // max(len(pairs), 1)

        matches.append({
            'vms_id': sv['id'],
            'an_id': sa['id'],
            'an_name': sa['name'],
            'score': round(score, 3),
            'n_pairs': len(pairs),
            'len_match_pct': len_match_pct,
            'combined': round(score * 0.6 + len_match_pct / 100 * 0.4, 3),
            'pairs': pairs,
            'vms_n': sv['n'],
            'an_n': sa['n'],
        })

matches.sort(key=lambda x: -x['combined'])

print(f'\n  {len(matches)} matches found')

# ================================================================
# 4. TOP MATCHES — detailed
# ================================================================
print(f'\n{"="*70}')
print('TOP 15 SHORT RECIPE MATCHES')
print('=' * 70)

for m in matches[:15]:
    print(f'\n  {"─"*60}')
    print(f'  {m["vms_id"]} ({m["vms_n"]}w) ↔ {m["an_id"]} ({m["an_n"]}w) '
          f'"{m["an_name"][:35]}"')
    print(f'  Score={m["score"]:.3f} LenMatch={m["len_match_pct"]}% '
          f'Combined={m["combined"]:.3f}')

    for p in m['pairs']:
        marker = '✓' if p['len_match'] else '✗'
        print(f'    {marker} {p["vms_eva"]:18s} ({p["vms_len"]}) ↔ '
              f'{p["an_raw"]:18s} ({p["an_len"]}) {p["an_ref"]}')

# ================================================================
# 5. CONVERGENT MAPPINGS from short recipes
# ================================================================
print(f'\n{"="*70}')
print('CONVERGENT MAPPINGS (short recipes, len_match only)')
print('=' * 70)

short_mappings = defaultdict(Counter)

for m in matches[:30]:
    for p in m['pairs']:
        if p['len_match']:
            short_mappings[p['vms_eva']][p['an_raw'].lower()] += 1

convergent = []
for eva, latins in short_mappings.items():
    best, count = latins.most_common(1)[0]
    if count >= 2:
        total = sum(latins.values())
        convergent.append((eva, best, count, total))

convergent.sort(key=lambda x: -x[2])

if convergent:
    print(f'\n  {len(convergent)} convergent (len-matched, 2+ occurrences):')
    for eva, latin, count, total in convergent:
        print(f'    {eva:18s} → {latin:18s} ({count}/{total})')
else:
    print(f'\n  No convergent mappings with length constraint.')
    print(f'  Relaxing to all pairs (not just len-matched)...')

    for m in matches[:50]:
        for p in m['pairs']:
            short_mappings[p['vms_eva']][p['an_raw'].lower()] += 1

    for eva, latins in short_mappings.items():
        best, count = latins.most_common(1)[0]
        if count >= 2:
            total = sum(latins.values())
            convergent.append((eva, best, count, total))

    convergent = list(set(convergent))
    convergent.sort(key=lambda x: -x[2])
    print(f'\n  {len(convergent)} convergent (relaxed, top 50):')
    for eva, latin, count, total in convergent[:20]:
        agr = count * 100 // total
        print(f'    {eva:18s} → {latin:18s} ({count}/{total} = {agr}%)')

# Save
results = {
    'n_short_vms': len(short_vms),
    'n_matches': len(matches),
    'top_matches': matches[:30],
    'convergent': [{'eva': e, 'latin': l, 'count': c, 'total': t}
                   for e, l, c, t in convergent],
}

with open(os.path.join(RESULTS, 'short_recipe_matches.json'), 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print('\nSaved short_recipe_matches.json')
