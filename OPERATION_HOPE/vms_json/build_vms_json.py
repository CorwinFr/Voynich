#!/usr/bin/env python3
"""
BUILD vms_structured.json - THE source of truth for all VMS analysis.

Source: LSI_ivtff_0d.txt (Stolfi/Takahashi interlinear archive)
Uses H (composite) as primary reading, other transcribers as variants.

Architecture:
  vms_structured.json  <- THE TEXT (stable, no K&A)
    word analysis: root, suffix, n_glyphs, is_logogram, i_count, e_count
    variants from multiple transcribers
    block segmentation by <$> markers
"""

import json, re, sys
from collections import defaultdict, Counter, OrderedDict

IVTFF = "/sessions/laughing-jolly-bell/mnt/Voynich FINAL/OPERATION_HOPE/data/LSI_ivtff_0d.txt"
OUTDIR = "/sessions/laughing-jolly-bell/mnt/Voynich FINAL/OPERATION_HOPE"

# ========================================================================
# KNOWN CONSTANTS
# ========================================================================

LOGOGRAMS = {
    'o': 'et/vel',
    'y': 'in/ad',
    's': 'est/sed',
    'd': 'de/cum',
    'r': 'recipe/per',
    'l': 'vel/ille',
    'k': 'cum/con',
    'm': 'nam/num',
    'f': None,
    't': None,
    'p': 'per/pro',
    'x': None,
    'v': None,
    'c': None,
}

SECTION_MAP = {
    # Ranges: (start_num, end_num, suffix_filter) -> section
    # suffix_filter: None = any, 'r' = recto only, etc.
}

def classify_section(folio_id):
    """Classify folio into VMS section."""
    m = re.match(r'f(\d+)([rv])(\d*)', folio_id)
    if not m:
        return 'unknown'
    num = int(m.group(1))
    if 1 <= num <= 56:
        return 'herbal_a'
    elif 57 <= num <= 66:
        return 'herbal_b'
    elif 67 <= num <= 73:
        return 'astro'
    elif num == 74:
        return 'astro'  # blank/missing?
    elif 75 <= num <= 84:
        return 'balnea'
    elif 85 <= num <= 86:
        return 'bio'
    elif 87 <= num <= 116:
        return 'pharma'
    return 'other'

def analyze_word(eva):
    """Morphological analysis of an EVA word."""
    result = {
        'n_glyphs': len(eva),
        'is_logogram': eva in LOGOGRAMS,
        'logogram_latin': LOGOGRAMS.get(eva),
    }

    # Root/suffix decomposition
    root = eva
    suffix = ''
    suffix_type = None

    # Check for known suffix patterns (longest match first)
    suffix_patterns = [
        (r'(aiiin)$', 'AIN_TRIPLE'),
        (r'(aiin)$', 'AIN_DOUBLE'),
        (r'(ain)$', 'AIN_SINGLE'),
        (r'(eeey)$', 'EEY_TRIPLE'),
        (r'(eey)$', 'EEY_DOUBLE'),
        (r'(ey)$', 'EY_SINGLE'),
        (r'(eedy)$', 'EDY_DOUBLE'),
        (r'(edy)$', 'EDY_SINGLE'),
        (r'(eol)$', 'EOL'),
        (r'(ol)$', 'OL'),
        (r'(or)$', 'OR'),
        (r'(al)$', 'AL'),
        (r'(ar)$', 'AR'),
        (r'(am)$', 'AM'),
        (r'(dy)$', 'DY'),
        (r'(chy)$', 'CHY'),
        (r'(shy)$', 'SHY'),
        (r'(hor)$', 'HOR'),
    ]

    for pattern, stype in suffix_patterns:
        m = re.search(pattern, eva)
        if m and len(eva) > len(m.group(1)):
            suffix = m.group(1)
            suffix_type = stype
            root = eva[:m.start()]
            break

    result['root'] = root if root else eva
    result['suffix'] = suffix
    result['suffix_type'] = suffix_type

    # i-count (number of consecutive 'i' in -a[i+]n pattern)
    i_match = re.search(r'a(i+)n$', eva)
    result['i_count'] = len(i_match.group(1)) if i_match else None

    # e-count (number of consecutive 'e' in -[e+]y or -[e+]dy pattern)
    e_match = re.search(r'(e+)(d?y)$', eva)
    result['e_count'] = len(e_match.group(1)) if e_match else None

    # Dose candidate: has -ain/-aiin/-aiiin suffix and word length > 3
    result['is_dose_candidate'] = bool(i_match and len(eva) > 3)

    # Has gallows
    gallows = ['cth', 'ckh', 'cph', 'cfh', 't', 'k', 'p', 'f']
    bench_gallows = ['cth', 'ckh', 'cph', 'cfh']
    has_bench = any(bg in eva for bg in bench_gallows)
    # Count single gallows (after removing bench)
    clean = eva
    for bg in bench_gallows:
        clean = clean.replace(bg, '___')
    has_single = any(g in clean for g in ['t', 'k', 'p', 'f'])
    result['has_gallows'] = has_bench or has_single
    result['has_bench_gallows'] = has_bench

    return result

def parse_eva_word(raw):
    """Clean a raw EVA word string, extracting uncertainties."""
    uncertain = '?' in raw or '!' in raw
    # Remove uncertainty markers
    clean = raw.replace('!', '').replace('?', '').replace("'", '')
    # Remove any remaining special chars
    clean = re.sub(r'[^a-zA-Z]', '', clean)
    return clean.lower(), uncertain

def parse_line_text(text):
    """Parse an IVTFF line text into words with their EVA forms."""
    has_star = '<$>' in text

    # Remove markup but track it
    annotations = re.findall(r'<!([^>]+)>', text)
    text_clean = re.sub(r'<[^>]*>', '', text)

    # Remove comments
    text_clean = re.sub(r'\{[^}]*\}', '', text_clean)
    # Remove remaining special chars but keep dots (word separator)
    text_clean = re.sub(r'[^\w\s.]', '', text_clean)
    text_clean = re.sub(r'\s+', ' ', text_clean).strip()

    # Split on dots and spaces
    raw_words = [w.strip() for w in text_clean.split('.') if w.strip()]
    expanded = []
    for w in raw_words:
        parts = w.split()
        for p in parts:
            if p:
                expanded.append(p)

    words = []
    for i, raw in enumerate(expanded):
        eva, uncertain = parse_eva_word(raw)
        if not eva:
            continue
        words.append({
            'position': i,
            'eva_raw': raw,
            'eva_primary': eva,
            'uncertain': uncertain,
        })

    return words, has_star, annotations


# ========================================================================
# MAIN PARSING
# ========================================================================
print("=" * 70)
print("BUILDING vms_structured.json")
print("=" * 70)

# Phase 1: Parse all folio headers for metadata
folio_meta = {}
# Phase 2: Parse all text lines
folio_lines = defaultdict(list)  # folio_id -> [(line_num, para, transcriber, text, words, has_star)]
# Phase 3: Multi-transcriber variants
folio_variants = defaultdict(lambda: defaultdict(dict))  # folio -> line_num -> transcriber -> words

line_re = re.compile(r'^<(f\d+\w?\d?)\.(\d+),([^;]*);(\w)>\s*(.*)')
header_re = re.compile(r'^<(f\d+\w?\d?)>\s+<!\s*(.*?)>\s*$')
meta_re = re.compile(r'\$(\w)=(\w+)')

with open(IVTFF, encoding='latin-1') as f:
    for raw_line in f:
        raw_line = raw_line.rstrip('\n')

        # Skip comments
        if raw_line.startswith('#'):
            continue

        # Folio header with metadata
        hm = header_re.match(raw_line)
        if hm:
            folio_id = hm.group(1)
            meta_str = hm.group(2)
            meta = {}
            for mk, mv in meta_re.findall(meta_str):
                meta[mk] = mv
            folio_meta[folio_id] = {
                'illustration': meta.get('I', ''),
                'quire': meta.get('Q', ''),
                'page_in_quire': meta.get('P', ''),
                'language': meta.get('L', ''),
                'hand': meta.get('H', ''),
                'extra': meta.get('X', ''),
            }
            continue

        # Text line
        lm = line_re.match(raw_line)
        if lm:
            folio_id = lm.group(1)
            line_num = int(lm.group(2))
            para_info = lm.group(3)
            transcriber = lm.group(4)
            text = lm.group(5).strip()

            # Extract paragraph indicator
            para_match = re.search(r'[+@=]P(\d+)', para_info)
            paragraph = f"P{para_match.group(1)}" if para_match else "P0"

            # Parse words
            words, has_star, annotations = parse_line_text(text)

            # Store for primary (H) and variants
            folio_variants[folio_id][line_num][transcriber] = {
                'words': words,
                'has_star': has_star,
                'paragraph': paragraph,
                'annotations': annotations,
                'raw': text,
            }

            continue

# ========================================================================
# ASSEMBLY
# ========================================================================
print(f"\nFolios with metadata: {len(folio_meta)}")
print(f"Folios with text lines: {len(folio_variants)}")

# Build the structured JSON
output = {
    '_meta': {
        'source': 'LSI_ivtff_0d.txt (Stolfi/Takahashi interlinear, 1998)',
        'version': '1.0',
        'date': '2026-04-11',
        'parser': 'build_vms_json.py',
        'primary_transcriber': 'H (composite)',
        'notes': 'Morphological analysis included. K&A decode is EXTERNAL (separate file).',
    },
    'folios': OrderedDict(),
}

total_words = 0
total_lines = 0
total_blocks = 0
total_folios = 0
folio_word_counts = Counter()

# Sort folios by number
def folio_sort_key(fid):
    m = re.match(r'f(\d+)(\w?)(\d*)', fid)
    if m:
        return (int(m.group(1)), m.group(2), int(m.group(3) or 0))
    return (999, fid, 0)

sorted_folios = sorted(folio_variants.keys(), key=folio_sort_key)

for folio_id in sorted_folios:
    lines_data = folio_variants[folio_id]
    section = classify_section(folio_id)
    meta = folio_meta.get(folio_id, {})

    # Parse folio number and recto/verso
    fm = re.match(r'f(\d+)([rv])(\d*)', folio_id)
    if not fm:
        continue

    folio_num = int(fm.group(1))
    rv = fm.group(2)
    sub = fm.group(3) or ''

    # Build lines from H transcriber (primary), with variants
    folio_lines_out = []
    sorted_line_nums = sorted(lines_data.keys())

    for line_num in sorted_line_nums:
        transcribers = lines_data[line_num]

        # Primary: H
        if 'H' not in transcribers:
            # Fall back to first available
            primary_t = sorted(transcribers.keys())[0]
        else:
            primary_t = 'H'

        primary = transcribers[primary_t]

        # Build word list with analysis
        word_list = []
        for w in primary['words']:
            eva = w['eva_primary']
            if not eva or not re.match(r'^[a-z]+$', eva):
                continue

            word_entry = {
                'word_id': f"{folio_id}.{line_num}.{w['position']}",
                'position': w['position'],
                'eva_primary': eva,
                'uncertain': w['uncertain'],
                'analysis': analyze_word(eva),
            }

            # Collect variants from other transcribers
            variants = []
            for t, t_data in sorted(transcribers.items()):
                if t == primary_t:
                    continue
                # Find same position word in this transcriber
                for tw in t_data['words']:
                    if tw['position'] == w['position']:
                        if tw['eva_primary'] != eva and tw['eva_primary']:
                            variants.append({
                                'transcriber': t,
                                'eva': tw['eva_primary'],
                            })
                        break

            if variants:
                word_entry['eva_variants'] = variants

            word_list.append(word_entry)

        line_entry = {
            'line_id': f"{folio_id}.{line_num}",
            'line_num': line_num,
            'paragraph': primary['paragraph'],
            'has_star': primary['has_star'],
            'n_words': len(word_list),
            'words': word_list,
        }

        if primary['annotations']:
            line_entry['annotations'] = primary['annotations']

        folio_lines_out.append(line_entry)
        total_lines += 1
        total_words += len(word_list)
        folio_word_counts[folio_id] += len(word_list)

    # Segment into blocks
    blocks = []
    current_block_lines = []
    block_num = 0
    has_any_star = any(line.get('has_star', False) for line in folio_lines_out)

    for line_entry in folio_lines_out:
        current_block_lines.append(line_entry)

        if line_entry.get('has_star', False):
            # End of block
            block_num += 1
            block_type = 'recipe' if section == 'pharma' else 'paragraph'
            block_words = sum(l['n_words'] for l in current_block_lines)
            block_doses = sum(
                1 for l in current_block_lines
                for w in l['words']
                if w['analysis'].get('is_dose_candidate', False)
            )
            block_units = sum(
                1 for l in current_block_lines
                for w in l['words']
                if (w['analysis'].get('suffix_type') or '').startswith('EEY') or
                   (w['analysis'].get('suffix_type') or '').startswith('EY')
            )

            blocks.append({
                'block_id': f"{folio_id}_B{block_num:02d}",
                'block_type': block_type,
                'block_num': block_num,
                'n_lines': len(current_block_lines),
                'n_words': block_words,
                'n_dose_candidates': block_doses,
                'n_unit_candidates': block_units,
                'lines': current_block_lines,
            })
            total_blocks += 1
            current_block_lines = []

    # Remaining lines after last star
    if current_block_lines:
        block_num += 1
        block_type = 'recipe' if section == 'pharma' and has_any_star else 'continuous'
        block_words = sum(l['n_words'] for l in current_block_lines)
        block_doses = sum(
            1 for l in current_block_lines
            for w in l['words']
            if w['analysis'].get('is_dose_candidate', False)
        )
        block_units = sum(
            1 for l in current_block_lines
            for w in l['words']
            if (w['analysis'].get('suffix_type') or '').startswith('EEY') or
               (w['analysis'].get('suffix_type') or '').startswith('EY')
        )
        blocks.append({
            'block_id': f"{folio_id}_B{block_num:02d}",
            'block_type': block_type,
            'block_num': block_num,
            'n_lines': len(current_block_lines),
            'n_words': block_words,
            'n_dose_candidates': block_doses,
            'n_unit_candidates': block_units,
            'lines': current_block_lines,
        })
        total_blocks += 1

    # Build folio entry
    folio_entry = {
        'folio_id': folio_id,
        'folio_num': folio_num,
        'rv': rv,
        'sub': sub,
        'metadata': {
            'section': section,
            'quire': meta.get('quire', ''),
            'illustration': meta.get('illustration', ''),
            'language': meta.get('language', ''),
            'hand': meta.get('hand', ''),
            'n_lines': len(folio_lines_out),
            'n_words': folio_word_counts[folio_id],
            'n_blocks': len(blocks),
            'has_stars': has_any_star,
        },
        'blocks': blocks,
    }

    output['folios'][folio_id] = folio_entry
    total_folios += 1

# Update meta
output['_meta']['total_folios'] = total_folios
output['_meta']['total_lines'] = total_lines
output['_meta']['total_words'] = total_words
output['_meta']['total_blocks'] = total_blocks

# ========================================================================
# SAVE
# ========================================================================
outpath = f"{OUTDIR}/vms_structured.json"
with open(outpath, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"\nSaved to {outpath}")
print(f"  Folios:  {total_folios}")
print(f"  Lines:   {total_lines}")
print(f"  Words:   {total_words}")
print(f"  Blocks:  {total_blocks}")

# File size
import os
size_mb = os.path.getsize(outpath) / 1024 / 1024
print(f"  Size:    {size_mb:.1f} MB")

# ========================================================================
# STATS
# ========================================================================
print("\n" + "=" * 70)
print("STATISTICS")
print("=" * 70)

# Section breakdown
section_stats = defaultdict(lambda: {'folios': 0, 'words': 0, 'blocks': 0, 'lines': 0})
for fid, fdata in output['folios'].items():
    sec = fdata['metadata']['section']
    section_stats[sec]['folios'] += 1
    section_stats[sec]['words'] += fdata['metadata']['n_words']
    section_stats[sec]['blocks'] += fdata['metadata']['n_blocks']
    section_stats[sec]['lines'] += fdata['metadata']['n_lines']

print(f"\n{'Section':12s} {'Folios':>7s} {'Lines':>7s} {'Words':>7s} {'Blocks':>7s}")
print("-" * 45)
for sec in sorted(section_stats.keys()):
    s = section_stats[sec]
    print(f"  {sec:10s} {s['folios']:7d} {s['lines']:7d} {s['words']:7d} {s['blocks']:7d}")

# Pharma recipe stats
pharma_recipes = []
for fid, fdata in output['folios'].items():
    if fdata['metadata']['section'] == 'pharma':
        for block in fdata['blocks']:
            if block['block_type'] == 'recipe':
                pharma_recipes.append(block)

if pharma_recipes:
    pr_lens = [r['n_words'] for r in pharma_recipes]
    pr_doses = [r['n_dose_candidates'] for r in pharma_recipes]
    print(f"\nPharma recipes: {len(pharma_recipes)}")
    print(f"  Tokens/recipe: min={min(pr_lens)}, max={max(pr_lens)}, "
          f"mean={sum(pr_lens)/len(pr_lens):.1f}, median={sorted(pr_lens)[len(pr_lens)//2]}")
    print(f"  Doses/recipe:  min={min(pr_doses)}, max={max(pr_doses)}, "
          f"mean={sum(pr_doses)/len(pr_doses):.1f}")

# Variant stats
words_with_variants = 0
total_variant_count = 0
for fid, fdata in output['folios'].items():
    for block in fdata['blocks']:
        for line in block['lines']:
            for w in line['words']:
                if 'eva_variants' in w:
                    words_with_variants += 1
                    total_variant_count += len(w['eva_variants'])

print(f"\nVariant coverage:")
print(f"  Words with variants: {words_with_variants} ({100*words_with_variants/max(total_words,1):.1f}%)")
print(f"  Total variant readings: {total_variant_count}")

# Morphological analysis coverage
suffix_dist = Counter()
for fid, fdata in output['folios'].items():
    for block in fdata['blocks']:
        for line in block['lines']:
            for w in line['words']:
                st = w['analysis'].get('suffix_type')
                if st:
                    suffix_dist[st] += 1

print(f"\nSuffix type distribution:")
for st, c in suffix_dist.most_common(20):
    print(f"  {st:20s}: {c:5d}")

# Logogram stats
n_logo = sum(
    1 for fid, fdata in output['folios'].items()
    for block in fdata['blocks']
    for line in block['lines']
    for w in line['words']
    if w['analysis']['is_logogram']
)
print(f"\nLogograms: {n_logo} ({100*n_logo/max(total_words,1):.1f}%)")

# f103r verification
f103r = output['folios'].get('f103r')
if f103r:
    print(f"\nf103r verification:")
    print(f"  Blocks: {f103r['metadata']['n_blocks']}")
    print(f"  Words:  {f103r['metadata']['n_words']}")
    for b in f103r['blocks']:
        print(f"    {b['block_id']}: {b['n_words']} words, {b['n_dose_candidates']} doses, type={b['block_type']}")

print("\n" + "=" * 70)
print("BUILD COMPLETE")
print("=" * 70)
