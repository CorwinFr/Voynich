"""
ITERATION 1 — Decompose pharma words into prefix + plant-root + suffix.

For each pharma word, search if any known plant root is INSIDE it.
If found: extract prefix and suffix → decode the compound.
"""
import json, sys, io, os
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

VMS_PATH = os.path.join(os.path.dirname(__file__), '..', 'vms', 'vms_structured.json')
KB_PATH = os.path.join(os.path.dirname(__file__), '..', 'knowledge_base.json')
RESULTS = os.path.dirname(__file__)

with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)
with open(KB_PATH, encoding='utf-8') as f:
    kb = json.load(f)

LOGOS = set(kb['logograms'].keys())

# All known roots: confirmed + plant names
known_roots = {}
for root, data in kb.get('decoded_words', {}).get('confirmed', {}).items():
    known_roots[root] = data.get('latin', root)
for root, latin in kb.get('plant_names_corrected', {}).items():
    if root not in known_roots:
        known_roots[root] = latin

# Sort by length DESC so we match longest roots first
sorted_roots = sorted(known_roots.keys(), key=len, reverse=True)

print(f'Known roots: {len(known_roots)}')
print(f'  Confirmed: {len(kb.get("decoded_words",{}).get("confirmed",{}))}')
print(f'  Plant names: {len(kb.get("plant_names_corrected",{}))}')

# ================================================================
# For each pharma word, try to find a known root INSIDE it
# ================================================================
print(f'\n{"="*70}')
print('DECOMPOSING PHARMA WORDS')
print('=' * 70)

decomposed = []
prefix_counter = Counter()
suffix_counter = Counter()
root_in_pharma = Counter()
failed = []

for fid, folio in vms['folios'].items():
    if folio['metadata']['section'] != 'pharma': continue
    for block in folio['blocks']:
        for line in block['lines']:
            for w in line['words']:
                eva = w['eva_primary']
                if eva in LOGOS: continue
                if len(eva) < 3: continue

                # Try each known root
                found = None
                for root in sorted_roots:
                    if len(root) < 2: continue
                    idx = eva.find(root)
                    if idx >= 0:
                        prefix = eva[:idx]
                        suffix = eva[idx+len(root):]
                        # Sanity: prefix should be short (0-3 chars)
                        # and suffix should be a known suffix or short
                        if len(prefix) <= 4 and len(suffix) <= 5:
                            found = {
                                'eva': eva,
                                'prefix': prefix,
                                'root': root,
                                'latin': known_roots[root],
                                'suffix': suffix,
                                'folio': fid,
                            }
                            break

                if found:
                    decomposed.append(found)
                    prefix_counter[found['prefix']] += 1
                    suffix_counter[found['suffix']] += 1
                    root_in_pharma[found['root']] += 1
                else:
                    failed.append(eva)

total_pharma = len(decomposed) + len(failed)
print(f'\n  Total pharma words (3+ chars, non-logo): {total_pharma}')
print(f'  DECOMPOSED: {len(decomposed)} ({len(decomposed)*100//total_pharma}%)')
print(f'  Failed: {len(failed)} ({len(failed)*100//total_pharma}%)')

# ================================================================
# PREFIX ANALYSIS
# ================================================================
print(f'\n{"="*70}')
print('PREFIXES (what comes BEFORE the plant root)')
print('=' * 70)

print(f'\n  {len(prefix_counter)} unique prefixes')
print(f'\n  {"Prefix":>8s} {"Count":>6s} {"Pct":>5s} {"Logo?":>8s} {"Meaning":>10s}')
print('  ' + '-' * 45)

LOGO_MEANING = {'o':'ac','l':'se','d':'de','qo':'?cum?','op':'?ac+usque?',
                'ot':'?ac+et?','ok':'?ac+cum?','s':'est','sh':'ci',
                'y':'in','': '(none)'}

for pfx, count in prefix_counter.most_common(25):
    pct = count * 100 // len(decomposed)
    logo = LOGO_MEANING.get(pfx, '')
    print(f'  {repr(pfx):>8s} {count:>6d} {pct:>4d}% {logo:>10s}')

# ================================================================
# SUFFIX ANALYSIS
# ================================================================
print(f'\n{"="*70}')
print('SUFFIXES (what comes AFTER the plant root)')
print('=' * 70)

print(f'\n  {"Suffix":>8s} {"Count":>6s} {"Pct":>5s}')
print('  ' + '-' * 25)

for sfx, count in suffix_counter.most_common(25):
    pct = count * 100 // len(decomposed)
    print(f'  {repr(sfx):>8s} {count:>6d} {pct:>4d}%')

# ================================================================
# MOST FREQUENT PLANT ROOTS IN PHARMA
# ================================================================
print(f'\n{"="*70}')
print('PLANT ROOTS FOUND IN PHARMA COMPOUNDS')
print('=' * 70)

print(f'\n  {"Root":>12s} {"Latin":>15s} {"InPharma":>9s}')
print('  ' + '-' * 40)

for root, count in root_in_pharma.most_common(30):
    latin = known_roots.get(root, '?')
    print(f'  {root:>12s} {latin:>15s} {count:>9d}')

# ================================================================
# EXAMPLES — full decomposition
# ================================================================
print(f'\n{"="*70}')
print('EXAMPLES — decomposed pharma words')
print('=' * 70)

# Group by root, show top 3 per root
by_root = defaultdict(list)
for d in decomposed:
    by_root[d['root']].append(d)

for root in list(root_in_pharma.keys())[:15]:
    latin = known_roots.get(root, '?')
    examples = by_root[root][:5]
    print(f'\n  {root} = {latin}:')
    for ex in examples:
        meaning = f'{LOGO_MEANING.get(ex["prefix"], ex["prefix"])}+{latin}+{ex["suffix"]}'
        print(f'    {ex["eva"]:>18s} = {ex["prefix"]}|{root}|{ex["suffix"]:>5s} → {meaning}')

# ================================================================
# HYPOTHESIS: prefix = incorporated logogram/preposition
# ================================================================
print(f'\n{"="*70}')
print('HYPOTHESIS: prefix = incorporated preposition')
print('=' * 70)

# The most common prefixes and their logogram equivalents
print(f"""
  PREFIX  FREQ    LOGOGRAM    LATIN       INTERPRETATION
  (none)  {prefix_counter.get('',0):>5d}    -           -           bare root (nominative?)
  o       {prefix_counter.get('o',0):>5d}    o = ac      ac          "with/and [plant]"
  l       {prefix_counter.get('l',0):>5d}    l = se      se          "itself/own [plant]"
  d       {prefix_counter.get('d',0):>5d}    d = de      de          "of/from [plant]"
  qo      {prefix_counter.get('qo',0):>5d}    q+o = ?+ac  ?           compound prep
  op      {prefix_counter.get('op',0):>5d}    o+p = ac+usque          "with [plant] until"
  ot      {prefix_counter.get('ot',0):>5d}    o+t = ac+et             "with and [plant]"
  ok      {prefix_counter.get('ok',0):>5d}    o+k = ac+cum            "with together [plant]"
  s       {prefix_counter.get('s',0):>5d}    s = est     est         "[plant] is"
  y       {prefix_counter.get('y',0):>5d}    y = in      in          "in [plant]"
""")

# Save
output = {
    'total_pharma': total_pharma,
    'decomposed': len(decomposed),
    'failed': len(failed),
    'decompose_rate': round(len(decomposed)/total_pharma, 3),
    'top_prefixes': dict(prefix_counter.most_common(20)),
    'top_suffixes': dict(suffix_counter.most_common(20)),
    'top_roots_in_pharma': dict(root_in_pharma.most_common(30)),
    'examples': {root: [{'eva':d['eva'],'prefix':d['prefix'],'suffix':d['suffix']}
                        for d in by_root[root][:5]]
                 for root in list(root_in_pharma.keys())[:20]},
}

with open(os.path.join(RESULTS, 'iter1_decompose.json'), 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f'\nSaved iter1_decompose.json')
