"""
DEEP PATTERN SEARCH — Find ANY recurring pattern in the VMS.

1. N-grams de mots EVA (bigrams, trigrams, 4-grams)
2. N-grams de TYPES structurels
3. Blocs identiques ou quasi-identiques
4. Lignes qui se répètent entre folios
5. Séquences de suffixes récurrentes
6. Premiers/derniers mots de blocs — formules d'ouverture/fermeture
7. Mots qui apparaissent TOUJOURS ensemble (collocations)
8. Blocs anormalement courts ou longs
9. Hapax par section (mots uniques à UN seul folio)
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

# Build flat word stream per section
sections_words = defaultdict(list)  # section → [(folio, block, [eva_words])]

for fid, folio in vms['folios'].items():
    section = folio['metadata']['section']
    sec = 'herbal' if 'herbal' in section else section
    for block in folio['blocks']:
        words = [w['eva_primary'] for line in block['lines'] for w in line['words']]
        if words:
            sections_words[sec].append((fid, block.get('block_id', ''), words))

all_words_flat = []
for fid, folio in vms['folios'].items():
    for block in folio['blocks']:
        for line in block['lines']:
            for w in line['words']:
                all_words_flat.append(w['eva_primary'])

# ================================================================
# 1. WORD N-GRAMS — most frequent bigrams/trigrams/4-grams
# ================================================================
print('=' * 70)
print('1. N-GRAMS DE MOTS (tout le manuscrit)')
print('=' * 70)

for n, label in [(2, 'BIGRAMS'), (3, 'TRIGRAMS'), (4, '4-GRAMS')]:
    ngrams = Counter()
    for i in range(len(all_words_flat) - n + 1):
        gram = tuple(all_words_flat[i:i+n])
        ngrams[gram] += 1

    print(f'\n  TOP 20 {label}:')
    for gram, count in ngrams.most_common(20):
        print(f'    {count:4d}x  {" ".join(gram)}')

# ================================================================
# 2. TYPE SEQUENCE N-GRAMS
# ================================================================
print(f'\n{"="*70}')
print('2. SÉQUENCES DE TYPES STRUCTURELS')
print('=' * 70)

# Build type stream
def get_type(w_dict):
    eva = w_dict['eva_primary']
    if eva in LOGOGRAM_SET: return 'L'
    morph = w_dict.get('morphology') or {}
    if morph.get('i_count') is not None: return 'D'
    root = morph.get('root', '')
    if root in {r for r, d in kb['roots'].items() if d.get('herbal_folio')}: return 'P'
    return 'W'  # word (content)

type_stream = []
for fid, folio in vms['folios'].items():
    for block in folio['blocks']:
        for line in block['lines']:
            for w in line['words']:
                type_stream.append(get_type(w))

for n in [3, 4, 5]:
    tgrams = Counter()
    for i in range(len(type_stream) - n + 1):
        gram = ''.join(type_stream[i:i+n])
        tgrams[gram] += 1
    print(f'\n  TOP 10 type-{n}-grams:')
    for gram, count in tgrams.most_common(10):
        print(f'    {count:5d}x  {gram}')

# ================================================================
# 3. BLOCS IDENTIQUES OU QUASI-IDENTIQUES
# ================================================================
print(f'\n{"="*70}')
print('3. BLOCS SIMILAIRES (Jaccard > 0.5)')
print('=' * 70)

block_sets = []
for fid, folio in vms['folios'].items():
    for block in folio['blocks']:
        words = [w['eva_primary'] for line in block['lines'] for w in line['words']]
        if len(words) >= 5:
            block_sets.append((fid, block.get('block_id', ''), set(words), words))

similar_pairs = []
for i in range(len(block_sets)):
    for j in range(i+1, min(i+50, len(block_sets))):  # limit search window
        fid_i, bid_i, set_i, _ = block_sets[i]
        fid_j, bid_j, set_j, _ = block_sets[j]
        if fid_i == fid_j: continue
        inter = len(set_i & set_j)
        union = len(set_i | set_j)
        jacc = inter / max(union, 1)
        if jacc > 0.5:
            similar_pairs.append((jacc, fid_i, bid_i, fid_j, bid_j, inter, union))

similar_pairs.sort(key=lambda x: -x[0])
for jacc, fi, bi, fj, bj, inter, union in similar_pairs[:15]:
    print(f'  Jaccard={jacc:.2f} {bi}({fi}) ↔ {bj}({fj}) [{inter}/{union}]')

if not similar_pairs:
    # Broader search: across all blocks
    all_block_words = []
    for fid, folio in vms['folios'].items():
        for block in folio['blocks']:
            words = tuple(w['eva_primary'] for line in block['lines'] for w in line['words'])
            if len(words) >= 3:
                all_block_words.append((fid, block.get('block_id',''), words))

    # Find repeated subsequences of length 5+
    subseq5 = Counter()
    for _, _, words in all_block_words:
        for i in range(len(words) - 4):
            subseq5[words[i:i+5]] += 1

    repeated = [(seq, c) for seq, c in subseq5.items() if c >= 2]
    repeated.sort(key=lambda x: -x[1])
    print(f'\n  Repeated 5-word subsequences: {len(repeated)}')
    for seq, c in repeated[:15]:
        print(f'    {c}x: {" ".join(seq)}')

# ================================================================
# 4. LIGNES RÉPÉTÉES entre folios
# ================================================================
print(f'\n{"="*70}')
print('4. LIGNES QUI SE RÉPÈTENT')
print('=' * 70)

line_texts = defaultdict(list)
for fid, folio in vms['folios'].items():
    for block in folio['blocks']:
        for line in block['lines']:
            words = tuple(w['eva_primary'] for w in line['words'])
            if len(words) >= 4:
                line_texts[words].append((fid, line.get('line_id', '')))

repeated_lines = [(words, locs) for words, locs in line_texts.items() if len(locs) >= 2]
repeated_lines.sort(key=lambda x: -len(x[1]))

print(f'  {len(repeated_lines)} lignes qui apparaissent 2+ fois')
for words, locs in repeated_lines[:15]:
    loc_str = ', '.join(f'{fid}:{lid}' for fid, lid in locs[:4])
    print(f'  {len(locs)}x: {" ".join(words[:8])}{"..." if len(words)>8 else ""} [{loc_str}]')

# ================================================================
# 5. SUFFIX SEQUENCES
# ================================================================
print(f'\n{"="*70}')
print('5. SÉQUENCES DE SUFFIXES')
print('=' * 70)

suffix_stream = []
for fid, folio in vms['folios'].items():
    if folio['metadata']['section'] != 'pharma': continue
    for block in folio['blocks']:
        for line in block['lines']:
            for w in line['words']:
                suf = (w.get('morphology') or {}).get('suffix', '') or ''
                if suf:
                    suffix_stream.append(suf)

for n in [2, 3, 4]:
    sgrams = Counter()
    for i in range(len(suffix_stream) - n + 1):
        gram = tuple(suffix_stream[i:i+n])
        sgrams[gram] += 1
    print(f'\n  TOP 10 suffix-{n}-grams (pharma):')
    for gram, count in sgrams.most_common(10):
        print(f'    {count:4d}x  {" → ".join(gram)}')

# ================================================================
# 6. FORMULES D'OUVERTURE / FERMETURE
# ================================================================
print(f'\n{"="*70}')
print('6. FORMULES D\'OUVERTURE ET FERMETURE')
print('=' * 70)

openers = Counter()  # first 3 words of star-blocks
closers = Counter()  # last 3 words of star-blocks

for fid, folio in vms['folios'].items():
    for block in folio['blocks']:
        if not block.get('separator'): continue
        words = [w['eva_primary'] for line in block['lines'] for w in line['words']]
        if len(words) >= 3:
            openers[tuple(words[:3])] += 1
            closers[tuple(words[-3:])] += 1

print('\n  TOP 15 OUVERTURES (3 premiers mots):')
for gram, count in openers.most_common(15):
    print(f'    {count:3d}x  {" ".join(gram)}')

print('\n  TOP 15 FERMETURES (3 derniers mots):')
for gram, count in closers.most_common(15):
    print(f'    {count:3d}x  {" ".join(gram)}')

# ================================================================
# 7. COLLOCATIONS — mots qui apparaissent TOUJOURS ensemble
# ================================================================
print(f'\n{"="*70}')
print('7. COLLOCATIONS (mots toujours ensemble)')
print('=' * 70)

# For words with freq >= 20, check: when word A appears in a block,
# does word B always appear too?
word_blocks = defaultdict(set)  # word → set of block_ids
block_id_counter = 0

for fid, folio in vms['folios'].items():
    for block in folio['blocks']:
        block_id_counter += 1
        for line in block['lines']:
            for w in line['words']:
                word_blocks[w['eva_primary']].add(block_id_counter)

# Find strong collocations
freq_words = [w for w, blocks in word_blocks.items()
              if len(blocks) >= 15 and w not in LOGOGRAM_SET]

print(f'\n  Checking {len(freq_words)} frequent words...')
collocations = []
for i, w1 in enumerate(freq_words):
    b1 = word_blocks[w1]
    for w2 in freq_words[i+1:]:
        b2 = word_blocks[w2]
        # Jaccard of block co-occurrence
        inter = len(b1 & b2)
        union = len(b1 | b2)
        jacc = inter / max(union, 1)
        # Conditional: P(w2|w1) and P(w1|w2)
        p_w2_given_w1 = inter / max(len(b1), 1)
        p_w1_given_w2 = inter / max(len(b2), 1)
        mutual = min(p_w2_given_w1, p_w1_given_w2)
        if mutual > 0.5 and inter >= 10:
            collocations.append((mutual, w1, w2, len(b1), len(b2), inter))

collocations.sort(key=lambda x: -x[0])
print(f'  {len(collocations)} strong collocations found')
for mutual, w1, w2, n1, n2, inter in collocations[:20]:
    print(f'    {mutual:.2f} {w1:15s}({n1:3d}) ↔ {w2:15s}({n2:3d}) [{inter} shared blocks]')

# ================================================================
# 8. BLOCS ANORMAUX (très courts ou très longs)
# ================================================================
print(f'\n{"="*70}')
print('8. BLOCS ANORMAUX')
print('=' * 70)

block_sizes = []
for fid, folio in vms['folios'].items():
    section = folio['metadata']['section']
    for block in folio['blocks']:
        words = [w for line in block['lines'] for w in line['words']]
        block_sizes.append((len(words), fid, block.get('block_id', ''), section))

block_sizes.sort()

print('\n  5 PLUS COURTS:')
for n, fid, bid, sec in block_sizes[:5]:
    print(f'    {n:3d}w  {bid:20s} ({fid}, {sec})')

print('\n  5 PLUS LONGS:')
for n, fid, bid, sec in block_sizes[-5:]:
    print(f'    {n:3d}w  {bid:20s} ({fid}, {sec})')

# ================================================================
# 9. MOTS UNIQUES à un seul folio
# ================================================================
print(f'\n{"="*70}')
print('9. FOLIOS AVEC BEAUCOUP DE HAPAX')
print('=' * 70)

word_folios = defaultdict(set)
folio_vocab = defaultdict(set)
for fid, folio in vms['folios'].items():
    for block in folio['blocks']:
        for line in block['lines']:
            for w in line['words']:
                eva = w['eva_primary']
                word_folios[eva].add(fid)
                folio_vocab[fid].add(eva)

folio_hapax = {}
for fid in sorted(folio_vocab.keys()):
    hapax = [w for w in folio_vocab[fid] if len(word_folios[w]) == 1]
    total = len(folio_vocab[fid])
    if total >= 10:
        folio_hapax[fid] = (len(hapax), total, len(hapax)*100//total)

# Sort by hapax percentage
top_hapax = sorted(folio_hapax.items(), key=lambda x: -x[1][2])
print(f'\n  TOP 15 folios par % de mots uniques:')
for fid, (n_hapax, n_total, pct) in top_hapax[:15]:
    section = vms['folios'][fid]['metadata']['section']
    print(f'    {fid:8s} ({section:10s}): {n_hapax:3d}/{n_total:3d} hapax ({pct}%)')

# Save key findings
results = {
    'repeated_lines': len(repeated_lines),
    'strong_collocations': len(collocations),
    'top_hapax_folios': [(fid, n, t, p) for fid, (n, t, p) in top_hapax[:20]],
}
with open(os.path.join(os.path.dirname(__file__), 'deep_patterns.json'), 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print('\nSaved deep_patterns.json')
