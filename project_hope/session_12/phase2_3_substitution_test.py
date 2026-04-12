"""
PHASE 2+3 — Re-tokenize with composite glyphs + Test L3→L5 substitution.

1. Fuse ch/sh/th/kh/ph into single tokens
2. Count the effective alphabet size
3. Apply L3→L5 substitution at glyph level
4. Apply INVERSE substitution
5. Measure: which direction makes the text more "Latin-like"?
"""
import json, sys, io, os, re
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

VMS_PATH = os.path.join(os.path.dirname(__file__), '..', 'vms', 'vms_structured.json')
KB_PATH = os.path.join(os.path.dirname(__file__), '..', 'knowledge_base.json')
RESULTS = os.path.dirname(__file__)

with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)
with open(KB_PATH, encoding='utf-8') as f:
    kb = json.load(f)

# ================================================================
# 1. RE-TOKENIZE — composite glyphs
# ================================================================
print('=' * 70)
print('PHASE 2: RE-TOKENIZATION')
print('=' * 70)

# Count glyph-level characters in all EVA words
COMPOSITES = {'ch', 'sh', 'th', 'kh', 'ph', 'ck', 'ct', 'cf', 'cp'}

def tokenize_glyphs(eva):
    """Split EVA word into individual visual glyphs."""
    glyphs = []
    i = 0
    while i < len(eva):
        # Try 2-char composites first
        if i + 1 < len(eva) and eva[i:i+2] in COMPOSITES:
            glyphs.append(eva[i:i+2])
            i += 2
        else:
            glyphs.append(eva[i])
            i += 1
    return glyphs

# Count all glyphs across manuscript
glyph_freq = Counter()
word_count = 0

for fid, folio in vms['folios'].items():
    for block in folio['blocks']:
        for line in block['lines']:
            for w in line['words']:
                eva = w['eva_primary']
                if '@' in eva: continue  # skip special symbols
                glyphs = tokenize_glyphs(eva)
                glyph_freq.update(glyphs)
                word_count += 1

print(f'\n  Total words: {word_count}')
print(f'  Unique glyphs (with composites): {len(glyph_freq)}')
print(f'\n  Glyph frequencies:')
total_glyphs = sum(glyph_freq.values())
for g, n in glyph_freq.most_common(30):
    pct = n * 100 // total_glyphs
    bar = '█' * (pct // 2)
    print(f'    {g:4s}: {n:6d} ({pct:2d}%) {bar}')

# Compare with volvelle alphabet
volvelle_glyphs = set(['o','l','d','r','v','x','k','m','f','p','t','y','c','I',
                       '@169v','@170','@171','@172'])
text_glyphs = set(glyph_freq.keys())

print(f'\n  Volvelle glyphs: {len(volvelle_glyphs)}')
print(f'  Text glyphs (>10 occ): {sum(1 for g,n in glyph_freq.items() if n > 10)}')

in_both = volvelle_glyphs & text_glyphs
only_volvelle = volvelle_glyphs - text_glyphs
only_text = {g for g, n in glyph_freq.items() if n > 100} - volvelle_glyphs

print(f'\n  In both: {sorted(in_both)}')
print(f'  Only on volvelle: {sorted(only_volvelle)}')
print(f'  Only in text (freq>100): {sorted(only_text)}')

# ================================================================
# 2. THE KEY INSIGHT — two-layer alphabet
# ================================================================
print(f'\n{"="*70}')
print('TWO-LAYER ALPHABET')
print('=' * 70)

layer1 = set(['o','l','d','r','v','x','k','m','f','p','t','y','c'])
layer2 = set(['a','e','h','i','n','q','s'])  # h only in composites

layer1_count = sum(glyph_freq.get(g, 0) for g in layer1)
layer2_count = sum(glyph_freq.get(g, 0) for g in layer2)
composite_count = sum(glyph_freq.get(g, 0) for g in COMPOSITES)

print(f'  Layer 1 (volvelle): {layer1_count} ({layer1_count*100//total_glyphs}%)')
print(f'  Layer 2 (structural): {layer2_count} ({layer2_count*100//total_glyphs}%)')
print(f'  Composites (ch/sh/etc): {composite_count} ({composite_count*100//total_glyphs}%)')

# Position analysis for layer 2
print(f'\n  Layer 2 positional rigidity:')
for g in ['a', 'e', 'h', 'i', 'n', 'q', 's']:
    starts = 0
    middles = 0
    ends = 0
    total_g = 0
    for fid, folio in vms['folios'].items():
        for block in folio['blocks']:
            for line in block['lines']:
                for w in line['words']:
                    eva = w['eva_primary']
                    if '@' in eva: continue
                    glyphs = tokenize_glyphs(eva)
                    for pos, gl in enumerate(glyphs):
                        if gl == g:
                            total_g += 1
                            if pos == 0: starts += 1
                            elif pos == len(glyphs)-1: ends += 1
                            else: middles += 1
    if total_g > 0:
        print(f'    {g}: start={starts*100//total_g:2d}% mid={middles*100//total_g:2d}% '
              f'end={ends*100//total_g:2d}% (n={total_g})')

# ================================================================
# 3. APPLY L3→L5 SUBSTITUTION
# ================================================================
print(f'\n{"="*70}')
print('PHASE 3: SUBSTITUTION TEST')
print('=' * 70)

sub_forward = kb['volvelle']['substitution_table']
sub_inverse = {v: k for k, v in sub_forward.items()}

def apply_sub(eva, table):
    """Apply glyph-level substitution."""
    glyphs = tokenize_glyphs(eva)
    result = []
    for g in glyphs:
        result.append(table.get(g, g))
    return ''.join(result)

# Test on pharma words — measure which direction produces better bigram stats
print('\n  Testing forward (L3→L5) and inverse (L5→L3) on pharma...')

original_bigrams = Counter()
forward_bigrams = Counter()
inverse_bigrams = Counter()

test_words = []
for fid, folio in vms['folios'].items():
    if folio['metadata']['section'] != 'pharma': continue
    for block in folio['blocks']:
        for line in block['lines']:
            for w in line['words']:
                eva = w['eva_primary']
                if '@' in eva or len(eva) < 3: continue
                test_words.append(eva)

                # Original bigrams
                for i in range(len(eva)-1):
                    original_bigrams[eva[i:i+2]] += 1

                # Forward substitution
                fwd = apply_sub(eva, sub_forward)
                for i in range(len(fwd)-1):
                    forward_bigrams[fwd[i:i+2]] += 1

                # Inverse substitution
                inv = apply_sub(eva, sub_inverse)
                for i in range(len(inv)-1):
                    inverse_bigrams[inv[i:i+2]] += 1

# Latin bigram reference frequencies (top 20)
LATIN_BIGRAMS = {
    'er': 3.2, 'in': 3.0, 'um': 2.8, 'is': 2.7, 'us': 2.5,
    'et': 2.4, 'an': 2.3, 'ar': 2.2, 'es': 2.1, 'ti': 2.0,
    'at': 1.9, 'en': 1.8, 'or': 1.7, 'on': 1.6, 'de': 1.5,
    'em': 1.4, 'am': 1.3, 'it': 1.2, 'ra': 1.1, 're': 1.0,
}

def latin_score(bigrams):
    """Score how Latin-like the bigram distribution is."""
    total = sum(bigrams.values())
    if total == 0: return 0
    score = 0
    for bi, expected_pct in LATIN_BIGRAMS.items():
        actual_pct = bigrams.get(bi, 0) * 100 / total
        # Reward proximity to expected
        score += max(0, 1.0 - abs(actual_pct - expected_pct))
    return score

orig_score = latin_score(original_bigrams)
fwd_score = latin_score(forward_bigrams)
inv_score = latin_score(inverse_bigrams)

print(f'\n  Latin-likeness scores:')
print(f'    Original:  {orig_score:.2f}')
print(f'    Forward:   {fwd_score:.2f} ({"+"+str(round(fwd_score-orig_score,2)) if fwd_score>orig_score else round(fwd_score-orig_score,2)})')
print(f'    Inverse:   {inv_score:.2f} ({"+"+str(round(inv_score-orig_score,2)) if inv_score>orig_score else round(inv_score-orig_score,2)})')

best = 'FORWARD' if fwd_score > inv_score else 'INVERSE' if inv_score > fwd_score else 'TIE'
print(f'\n  → Best direction: {best}')

# Show examples
print(f'\n  Examples (first 20 pharma words):')
print(f'  {"Original":>18s} {"Forward":>18s} {"Inverse":>18s}')
print('  ' + '-' * 56)
for eva in test_words[:20]:
    fwd = apply_sub(eva, sub_forward)
    inv = apply_sub(eva, sub_inverse)
    print(f'  {eva:>18s} {fwd:>18s} {inv:>18s}')

# ================================================================
# 4. FREQUENCY COMPARISON
# ================================================================
print(f'\n{"="*70}')
print('LETTER FREQUENCY COMPARISON')
print('=' * 70)

# Latin letter frequencies
LATIN_FREQ = {
    'e': 12.5, 'i': 11.0, 'a': 9.0, 'u': 8.5, 't': 7.5,
    's': 7.0, 'r': 6.5, 'n': 6.5, 'o': 5.5, 'l': 3.5,
    'c': 3.5, 'm': 3.0, 'd': 3.0, 'p': 2.5, 'b': 2.0,
}

# VMS letter frequencies (original, forward, inverse)
def char_freq(words, table=None):
    counts = Counter()
    for w in words:
        if table:
            w = apply_sub(w, table)
        for ch in w:
            counts[ch] += 1
    return counts

orig_chars = char_freq(test_words)
fwd_chars = char_freq(test_words, sub_forward)
inv_chars = char_freq(test_words, sub_inverse)

total_orig = sum(orig_chars.values())
total_fwd = sum(fwd_chars.values())
total_inv = sum(inv_chars.values())

print(f'\n  {"Char":>5s} {"Latin%":>7s} {"Orig%":>7s} {"Fwd%":>7s} {"Inv%":>7s}')
print('  ' + '-' * 35)
all_chars = sorted(set(list(LATIN_FREQ.keys()) + [c for c in orig_chars if orig_chars[c] > 100]),
                   key=lambda c: -LATIN_FREQ.get(c, 0))
for ch in all_chars[:15]:
    lat = LATIN_FREQ.get(ch, 0)
    orig = orig_chars.get(ch, 0) * 100 / max(total_orig, 1)
    fwd = fwd_chars.get(ch, 0) * 100 / max(total_fwd, 1)
    inv = inv_chars.get(ch, 0) * 100 / max(total_inv, 1)
    print(f'  {ch:>5s} {lat:>6.1f}% {orig:>6.1f}% {fwd:>6.1f}% {inv:>6.1f}%')

# Save
results = {
    'glyph_count': len(glyph_freq),
    'layer1_pct': layer1_count * 100 // total_glyphs,
    'layer2_pct': layer2_count * 100 // total_glyphs,
    'latin_scores': {
        'original': round(orig_score, 3),
        'forward': round(fwd_score, 3),
        'inverse': round(inv_score, 3),
        'best': best,
    },
    'substitution_table': sub_forward,
}
with open(os.path.join(RESULTS, 'phase2_3_results.json'), 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print('\nSaved phase2_3_results.json')
