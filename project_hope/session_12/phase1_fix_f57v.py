"""
PHASE 1 — Fix f57v in vms_structured.json using ZL3b.

The old parser stripped @-symbols. We need to:
1. Re-parse f57v from ZL3b-n.txt with @169-@172 preserved
2. Update vms_structured.json
3. Update knowledge_base.json with corrected volvelle data
"""
import json, sys, io, os, re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ZL3B_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'transcriptions', 'ZL3b-n.txt')
VMS_PATH = os.path.join(os.path.dirname(__file__), '..', 'vms', 'vms_structured.json')
KB_PATH = os.path.join(os.path.dirname(__file__), '..', 'knowledge_base.json')
RESULTS = os.path.dirname(__file__)

# ================================================================
# 1. Parse f57v from ZL3b properly
# ================================================================
print('Parsing f57v from ZL3b...')

f57v_lines = []
in_f57v = False
with open(ZL3B_PATH, encoding='utf-8') as f:
    for line in f:
        if '<f57v>' in line:
            in_f57v = True
            continue
        if in_f57v and line.startswith('<f') and 'f57v' not in line:
            break
        if in_f57v and 'f57v' in line and not line.startswith('#'):
            f57v_lines.append(line.rstrip())

print(f'  {len(f57v_lines)} lines found')

# Parse each line
def parse_zl3b_line(raw):
    """Parse a ZL3b line, preserving @NNN; symbols."""
    # Extract line ID
    m = re.match(r'<(f57v\.\d+)[^>]*>', raw)
    if not m:
        return None, []
    line_id = m.group(1)

    # Get text after last >
    text = raw.split('>')[-1].strip()

    # Remove comments <!...>
    text = re.sub(r'<!.*?>', '', text)

    # Remove <$>
    text = text.replace('<$>', '')

    # Handle variants [x:y] → take first
    text = re.sub(r'\[(\w+):(\w+)\]', r'\1', text)

    # Handle ligatures {xxx} → xxx
    text = re.sub(r'\{([^}]+)\}', r'\1', text)

    # Now split by dots and commas, but preserve @NNN;x patterns
    # First: normalize @NNN;x → @NNN;x (keep as-is)
    # Split by . and ,
    tokens = re.split(r'[.,]', text)

    words = []
    for tok in tokens:
        tok = tok.strip()
        if not tok:
            continue
        # Handle @NNN;x composite tokens
        # @169;v means @169 followed by v = one glyph
        tok = re.sub(r'@(\d+);(\w?)', r'@\1\2', tok)  # @169;v → @169v
        if tok.startswith('<%>'):
            tok = tok[3:]
        if tok:
            words.append(tok)

    return line_id, words

parsed_lines = []
for raw in f57v_lines:
    lid, words = parse_zl3b_line(raw)
    if lid:
        parsed_lines.append((lid, words))
        print(f'  {lid}: {" ".join(words[:20])}{"..." if len(words) > 20 else ""}')

# ================================================================
# 2. Analyze the corrected f57v.3 sequence
# ================================================================
print('\n' + '=' * 70)
print('CORRECTED f57v.3 SEQUENCE')
print('=' * 70)

for lid, words in parsed_lines:
    if lid == 'f57v.3':
        print(f'\n  Total tokens: {len(words)}')

        # Split into 4 repetitions
        # Each rep should be ~17 tokens
        # Look for the pattern: ends with @172
        reps = []
        current = []
        for w in words:
            current.append(w)
            if '@172' in w:
                reps.append(current)
                current = []
        if current:
            reps.append(current)

        for i, rep in enumerate(reps):
            print(f'  Rep {i+1} ({len(rep)} tokens): {" ".join(rep)}')

        # Alignment
        print(f'\n  ALIGNMENT:')
        max_len = max(len(r) for r in reps)
        for pos in range(max_len):
            vals = []
            for r in reps:
                vals.append(r[pos] if pos < len(r) else '-')
            stable = 'STABLE' if len(set(vals)) == 1 else 'CHANGE'
            print(f'    pos {pos+1:2d}: {" | ".join(f"{v:>6s}" for v in vals)}  [{stable}]')

# ================================================================
# 3. Corrected permutation line (f57v.5)
# ================================================================
print(f'\n{"="*70}')
print('CORRECTED f57v.5 PERMUTATION')
print('=' * 70)

for lid, words in parsed_lines:
    if lid == 'f57v.5':
        print(f'  {len(words)} tokens: {" ".join(words)}')

        # Separate logograms from @-symbols from words
        print('\n  Token analysis:')
        LOGOS = {'o','l','d','r','v','x','k','m','f','t','y','c','s','p','a','i'}
        for i, w in enumerate(words):
            if '@' in w:
                kind = '@SYMBOL'
            elif w in LOGOS or len(w) == 1:
                kind = 'LOGO'
            else:
                kind = 'WORD'
            print(f'    {i+1:2d} {w:12s} [{kind}]')

# ================================================================
# 4. Build corrected L3→L5 substitution table
# ================================================================
print(f'\n{"="*70}')
print('CORRECTED SUBSTITUTION TABLE L3→L5')
print('=' * 70)

# L3 (first rep of f57v.3)
l3 = None
l5 = None
for lid, words in parsed_lines:
    if lid == 'f57v.3':
        # First 17 tokens
        reps_list = []
        current = []
        for w in words:
            current.append(w)
            if '@172' in w:
                reps_list.append(current)
                current = []
        l3 = reps_list[0] if reps_list else []
    if lid == 'f57v.5':
        l5 = words

if l3 and l5:
    print(f'\n  L3 ({len(l3)} tokens): {" ".join(l3)}')
    print(f'  L5 ({len(l5)} tokens): {" ".join(l5)}')

    # Build mapping (position-by-position)
    n = min(len(l3), len(l5))
    print(f'\n  Mapping ({n} positions):')
    sub_table = {}
    for i in range(n):
        src = l3[i]
        dst = l5[i]
        change = '' if src == dst else ' ◄ CHANGE'
        print(f'    L3[{i+1:2d}]={src:>8s}  →  L5[{i+1:2d}]={dst:>8s}{change}')
        if src != dst:
            sub_table[src] = dst

    print(f'\n  Effective substitutions ({len(sub_table)}):')
    for src, dst in sub_table.items():
        print(f'    {src:>8s} → {dst}')

# ================================================================
# 5. Update vms_structured.json
# ================================================================
print(f'\n{"="*70}')
print('Updating vms_structured.json...')

with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)

# Rebuild f57v blocks
new_lines = []
for lid, words in parsed_lines:
    word_objs = []
    for w in words:
        word_objs.append({
            'eva_primary': w,
            'morphology': {
                'n_glyphs': len(w),
                'is_logogram': w in LOGOS and len(w) <= 2,
                'root': w,
                'suffix': '',
                'i_count': None,
                'e_count': None,
            }
        })
    new_lines.append({
        'line_id': lid,
        'words': word_objs,
    })

# Replace f57v
vms['folios']['f57v']['blocks'] = [{
    'block_id': 'f57v_B01',
    'separator': None,
    'lines': new_lines,
}]

# Count words
total_f57v = sum(len(l['words']) for l in new_lines)
print(f'  f57v now has {total_f57v} words (was 179)')

# Count @-symbols
at_count = sum(1 for l in new_lines for w in l['words'] if '@' in w['eva_primary'])
print(f'  @-symbols preserved: {at_count}')

with open(VMS_PATH, 'w', encoding='utf-8') as f:
    json.dump(vms, f, indent=2, ensure_ascii=False)
print('  Saved vms_structured.json')

# ================================================================
# 6. Update knowledge_base.json
# ================================================================
print(f'\nUpdating knowledge_base.json...')

with open(KB_PATH, encoding='utf-8') as f:
    kb = json.load(f)

kb['volvelle'] = {
    'sequence_l3': l3,
    'permutation_l5': l5[:n] if l5 else [],
    'substitution_table': sub_table,
    'labels': [w for lid, words in parsed_lines for w in words
               if lid in ('f57v.6','f57v.7','f57v.8','f57v.9',
                          'f57v.10','f57v.11','f57v.12','f57v.13')],
    'title': parsed_lines[0][1][0] if parsed_lines else '',
    'variants': {
        'pos_9': 'f→p (reps 1-2 vs 3-4)',
        'pos_16': 'I→c (rep 1 vs 2-4)',
    },
    'at_symbols': {
        '@169v': {'position': 10, 'occurrences': 5, 'also_on': ['f66r.24']},
        '@170': {'position': 13, 'occurrences': 5, 'also_on': ['f57v.5']},
        '@171': {'position': 14, 'occurrences': 5, 'also_on': ['f57v.5']},
        '@172': {'position': 17, 'occurrences': 6, 'also_on': ['f57v.4', 'f66r.38']},
    },
    'zl_version': 'ZL3b-n.txt v3b (13/05/2025)',
}

with open(KB_PATH, 'w', encoding='utf-8') as f:
    json.dump(kb, f, indent=2, ensure_ascii=False)
print('  Saved knowledge_base.json')

# Save results
results = {
    'l3_sequence': l3,
    'l5_permutation': l5,
    'substitution_table': sub_table,
    'corrected_lines': {lid: words for lid, words in parsed_lines},
}
with open(os.path.join(RESULTS, 'phase1_results.json'), 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print('\nPhase 1 complete.')
