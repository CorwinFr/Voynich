"""
SECTION VOCABULARY — Which roots are SPECIFIC to each section?

For each root, compute its section profile.
A root that appears 80%+ in balnea and nowhere else = balnea-specific vocabulary.
"""
import json, sys, io, os
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

VMS_PATH = os.path.join(os.path.dirname(__file__), '..', 'vms', 'vms_structured.json')
KB_PATH = os.path.join(os.path.dirname(__file__), '..', 'knowledge_base.json')

with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)
with open(KB_PATH, encoding='utf-8') as f:
    kb = json.load(f)

LOGOGRAM_SET = set(kb['logograms'].keys())

# ================================================================
# 1. Count every root by section
# ================================================================
root_section = defaultdict(Counter)  # root → {section: count}
root_total = Counter()

SECTIONS = ['herbal', 'pharma', 'balnea', 'astro', 'cosmo', 'bio']

for fid, folio in vms['folios'].items():
    section = folio['metadata']['section']
    sec = 'herbal' if 'herbal' in section else section

    for block in folio['blocks']:
        for line in block['lines']:
            for w in line['words']:
                eva = w['eva_primary']
                if eva in LOGOGRAM_SET: continue
                root = (w.get('morphology') or {}).get('root', '')
                if not root or len(root) < 2: continue
                root_section[root][sec] += 1
                root_total[root] += 1

# ================================================================
# 2. For each section, find EXCLUSIVE and ENRICHED roots
# ================================================================
print('=' * 70)
print('VOCABULAIRE SPÉCIFIQUE PAR SECTION')
print('=' * 70)

for target_sec in SECTIONS:
    exclusive = []    # >=80% in this section
    enriched = []     # >=50% in this section
    absent = []       # 0% in this section but common elsewhere

    for root, counts in root_section.items():
        total = root_total[root]
        if total < 5: continue
        in_target = counts.get(target_sec, 0)
        pct = in_target * 100 // total

        if pct >= 80:
            exclusive.append((root, total, in_target, pct))
        elif pct >= 50:
            enriched.append((root, total, in_target, pct))

    # Sort by frequency
    exclusive.sort(key=lambda x: -x[1])
    enriched.sort(key=lambda x: -x[1])

    print(f'\n{"─"*70}')
    print(f'{target_sec.upper()} — {len(exclusive)} exclusifs, {len(enriched)} enrichis')
    print(f'{"─"*70}')

    if exclusive:
        print(f'\n  EXCLUSIFS (≥80% dans {target_sec}):')
        for root, total, in_t, pct in exclusive[:20]:
            other_secs = ', '.join(f'{s}:{c}' for s, c in root_section[root].most_common()
                                   if s != target_sec and c > 0)
            print(f'    {root:15s} total={total:4d} {target_sec}={in_t:3d}({pct}%) | {other_secs}')

    if enriched:
        print(f'\n  ENRICHIS (50-79% dans {target_sec}):')
        for root, total, in_t, pct in enriched[:15]:
            print(f'    {root:15s} total={total:4d} {target_sec}={in_t:3d}({pct}%)')

# ================================================================
# 3. SHARED VOCABULARY — roots common across ALL sections
# ================================================================
print(f'\n{"="*70}')
print('VOCABULAIRE PARTAGÉ (présent dans 4+ sections)')
print('=' * 70)

shared = []
for root, counts in root_section.items():
    total = root_total[root]
    if total < 10: continue
    n_sections = sum(1 for s in SECTIONS if counts.get(s, 0) > 0)
    if n_sections >= 4:
        max_pct = max(counts.get(s, 0) * 100 // total for s in SECTIONS)
        shared.append((root, total, n_sections, max_pct))

shared.sort(key=lambda x: -x[1])
print(f'\n  {len(shared)} roots partagés')
print(f'\n  {"Root":>12s} {"Total":>6s} {"Sects":>5s} {"MaxPct":>6s} {"Profile":>40s}')
print('  ' + '-' * 75)
for root, total, n_sec, max_pct in shared[:30]:
    profile = ' '.join(f'{s[:3]}:{root_section[root].get(s,0):3d}'
                       for s in SECTIONS if root_section[root].get(s, 0) > 0)
    label = 'GRAMMATICAL' if max_pct < 40 else 'CONTENT' if max_pct > 60 else 'MIXED'
    print(f'  {root:>12s} {total:>6d} {n_sec:>5d} {max_pct:>5d}% {profile:>40s} [{label}]')

# ================================================================
# 4. BALNEA deep dive — what ARE those FUNC-like words?
# ================================================================
print(f'\n{"="*70}')
print('BALNEA DEEP DIVE — les mots fréquents')
print('=' * 70)

balnea_roots = [(root, counts['balnea'], root_total[root])
                for root, counts in root_section.items()
                if counts.get('balnea', 0) >= 3]
balnea_roots.sort(key=lambda x: -x[1])

print(f'\n  {"Root":>12s} {"Balnea":>7s} {"Total":>6s} {"Bal%":>5s} {"Profile":>45s}')
print('  ' + '-' * 80)
for root, bal, total in balnea_roots[:40]:
    bal_pct = bal * 100 // total
    profile = ' '.join(f'{s[:3]}:{root_section[root].get(s,0):3d}'
                       for s in SECTIONS if root_section[root].get(s, 0) > 0)
    marker = ' ★EXCL' if bal_pct >= 80 else ' ●ENRICH' if bal_pct >= 50 else ''
    print(f'  {root:>12s} {bal:>7d} {total:>6d} {bal_pct:>4d}% {profile:>45s}{marker}')

# ================================================================
# 5. CROSS-SECTION: are PLANT roots used differently?
# ================================================================
print(f'\n{"="*70}')
print('PLANT ROOTS PAR SECTION — même plante, même usage?')
print('=' * 70)

plant_roots = {root: data['herbal_folio'] for root, data in kb['roots'].items()
               if data.get('herbal_folio')}

for root in sorted(plant_roots.keys(), key=lambda r: -root_total.get(r, 0)):
    total = root_total.get(root, 0)
    if total < 5: continue
    counts = root_section.get(root, Counter())
    folio = plant_roots[root]
    profile = ' '.join(f'{s[:3]}:{counts.get(s,0):3d}' for s in SECTIONS if counts.get(s, 0) > 0)
    print(f'  PLANT_{folio:6s} root={root:10s} total={total:4d} | {profile}')

# ================================================================
# 6. SUMMARY TABLE
# ================================================================
print(f'\n{"="*70}')
print('RÉSUMÉ — vocabulaire par section')
print('=' * 70)

for sec in SECTIONS:
    excl = sum(1 for r, c in root_section.items()
               if root_total[r] >= 5 and c.get(sec, 0) * 100 // root_total[r] >= 80)
    enri = sum(1 for r, c in root_section.items()
               if root_total[r] >= 5 and 50 <= c.get(sec, 0) * 100 // root_total[r] < 80)
    total_roots = sum(1 for r, c in root_section.items()
                      if root_total[r] >= 5 and c.get(sec, 0) > 0)
    print(f'  {sec:>10s}: {total_roots:3d} roots used, {excl:3d} exclusifs, {enri:3d} enrichis')

# Save
out = {sec: {
    'exclusive': [(r, root_total[r]) for r, c in root_section.items()
                  if root_total[r] >= 5 and c.get(sec, 0) * 100 // root_total[r] >= 80],
    'enriched': [(r, root_total[r]) for r, c in root_section.items()
                 if root_total[r] >= 5 and 50 <= c.get(sec, 0) * 100 // root_total[r] < 80],
} for sec in SECTIONS}

with open(os.path.join(os.path.dirname(__file__), 'section_vocabulary.json'), 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=2, ensure_ascii=False)

print('\nSaved section_vocabulary.json')
