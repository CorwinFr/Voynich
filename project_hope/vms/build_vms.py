"""
BUILD vms_structured.json — Single source of truth.
ZL.txt = primary text (Zandbergen 2022 consensus)
LSI.txt = variants (5 independent transcribers)
Alignment: LINE by LINE (not word by word — ZL has +1416 words vs LSI)
"""
import re, json, sys, io
from collections import OrderedDict, Counter, defaultdict
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DATA_DIR = Path(__file__).parent.parent / 'data'
ZL_PATH = DATA_DIR / 'ZL.txt'
LSI_PATH = DATA_DIR / 'LSI_ivtff_0d.txt'
OUT_PATH = Path(__file__).parent / 'vms_structured.json'
STATS_PATH = Path(__file__).parent / 'vms_stats.json'

# ================================================================
# CONSTANTS
# ================================================================
LOGOGRAMS = {
    'o': 'ac', 'l': 'se', 'd': 'de', 'r': 'recipe', 'v': 'vel',
    'x': 'crux', 'k': 'cum', 'm': 'misce', 'f': 'per', 't': 'el',
    'y': 'in', 'c': 'cum', 's': 'est', 'sh': 'ci', 'p': 'usque',
    'air': 'aier',
}

SUFFIXES = [
    'aiiin', 'aiin', 'ain',
    'eeey', 'eey', 'ey',
    'eedy', 'edy',
    'eol', 'ol', 'or', 'ar', 'al',
    'dy', 'am', 'om',
    'chy', 'shy', 'air',
]

def get_section(fnum, rv='r'):
    if fnum <= 56: return 'herbal_a'
    elif fnum == 57 and rv == 'v': return 'volvelle'
    elif fnum == 57: return 'herbal_a'
    elif 58 <= fnum <= 67: return 'astro'
    elif 68 <= fnum <= 73: return 'cosmo'
    elif 75 <= fnum <= 84: return 'balnea'
    elif 85 <= fnum <= 86: return 'bio'
    elif 87 <= fnum <= 102: return 'herbal_b'
    elif 103 <= fnum <= 116: return 'pharma'
    return 'other'

def count_glyphs(w):
    digraphs = ['cth','ckh','cph','cfh','sh','ch','ee','ii','ai','oi','ph']
    i = 0; n = 0
    while i < len(w):
        matched = False
        for dg in sorted(digraphs, key=len, reverse=True):
            if w[i:i+len(dg)] == dg:
                n += 1; i += len(dg); matched = True; break
        if not matched:
            n += 1; i += 1
    return n

def get_suffix(w):
    if w in LOGOGRAMS: return '', None, None, None
    for sfx in SUFFIXES:
        if w.endswith(sfx) and len(w) > len(sfx):
            root = w[:-len(sfx)]
            # i_count
            ic = None
            if sfx in ('ain',): ic = 1
            elif sfx in ('aiin',): ic = 2
            elif sfx in ('aiiin',): ic = 3
            # e_count
            ec = None
            if sfx in ('ey','edy'): ec = 1
            elif sfx in ('eey','eedy','eol'): ec = 2
            elif sfx in ('eeey',): ec = 3
            return root, sfx, ic, ec
    return w, '', None, None

def parse_zl_word(raw):
    """Parse a ZL token: extract primary EVA, variants, uncertainty."""
    variants = []
    uncertain = False
    specials = []
    parts = []
    i = 0
    while i < len(raw):
        if raw[i] == '[':
            j = raw.find(']', i)
            if j < 0: j = len(raw)
            content = raw[i+1:j]
            options = content.split(':')
            parts.append(options[0])
            for opt in options[1:]:
                if opt and opt != '?':
                    variants.append(opt)
            i = j + 1
        elif raw[i] == '{':
            j = raw.find('}', i)
            if j < 0: j = len(raw)
            content = raw[i+1:j]
            specials.append(content)
            parts.append(content)
            i = j + 1
        elif raw[i] == '@':
            m = re.match(r'@(\d+);', raw[i:])
            if m:
                specials.append('@%s;' % m.group(1))
                parts.append('@%s;' % m.group(1))
                i += len(m.group(0))
            else:
                parts.append(raw[i]); i += 1
        elif raw[i] == '?':
            uncertain = True; i += 1
        else:
            parts.append(raw[i]); i += 1

    primary = ''.join(parts).strip('.,;:')
    eva_clean = re.sub(r'[^a-z]', '', primary.lower())
    return eva_clean, variants, uncertain, specials

# ================================================================
# PARSE ZL.txt
# ================================================================
def parse_zl():
    print('Parsing ZL.txt...')
    with open(ZL_PATH, encoding='utf-8') as f:
        zl_raw = f.read()

    folios = OrderedDict()
    folio_meta = {}
    current_fid = None
    current_folio = None
    current_block = None
    block_num = 0

    # Pass 1: metadata
    for line in zl_raw.split('\n'):
        m = re.match(r'<(f\d+[rv]\d?)>\s+<!\s*(.+?)>', line.strip())
        if m:
            fid = m.group(1)
            meta = {}
            for mm in re.finditer(r'\$(\w+)=(\w+)', m.group(2)):
                meta[mm.group(1)] = mm.group(2)
            folio_meta[fid] = meta

    # Pass 2: text
    for line in zl_raw.split('\n'):
        line = line.strip()
        if not line or line.startswith('#'): continue

        m = re.match(r'<(f(\d+)([rv])(\d?))\.(\d+),([^>]*)>', line)
        if not m: continue

        fid = m.group(1)
        fnum = int(m.group(2))
        rv = m.group(3)
        sub = m.group(4)
        lnum = int(m.group(5))
        ltype = m.group(6)

        text_part = line[m.end():].strip()
        has_star = '<%>' in text_part
        has_end = '<$>' in text_part
        has_break = '<->' in text_part

        # Annotations
        annotations = [a.group(1) for a in re.finditer(r'<!([^>]+)>', text_part)
                       if not a.group(1).startswith('$')]

        # Clean text
        clean = re.sub(r'<[^>]*>', '', text_part)
        clean = clean.replace(',', '.').strip()
        raw_tokens = [t.strip() for t in clean.split('.') if t.strip()]

        # New folio?
        if fid != current_fid:
            current_fid = fid
            meta = folio_meta.get(fid, {})
            current_folio = {
                'folio_id': fid, 'folio_num': fnum, 'rv': rv, 'sub': sub,
                'metadata': {
                    'section': get_section(fnum, rv),
                    'quire': meta.get('Q', ''),
                    'illustration': meta.get('I', ''),
                    'language': meta.get('L', ''),
                    'hand': meta.get('H', ''),
                    'n_lines': 0, 'n_words': 0, 'n_blocks': 0,
                    'has_stars': False,
                },
                'blocks': [],
            }
            folios[fid] = current_folio
            current_block = None
            block_num = 0

        # New block?
        if has_star or current_block is None:
            block_num += 1
            sec = current_folio['metadata']['section']
            current_block = {
                'block_id': '%s_B%02d' % (fid, block_num),
                'block_type': 'recipe' if sec == 'pharma' else 'paragraph',
                'block_num': block_num,
                'separator': {'type': 'star'} if has_star else None,
                'n_lines': 0, 'n_words': 0, 'lines': [],
            }
            current_folio['blocks'].append(current_block)
            current_folio['metadata']['n_blocks'] = block_num
            if has_star:
                current_folio['metadata']['has_stars'] = True

        # Parse words
        words = []
        for wi, raw in enumerate(raw_tokens):
            eva, variants, uncertain, specials = parse_zl_word(raw)
            if not eva: continue

            root, suffix, ic, ec = get_suffix(eva)
            morph = {
                'n_glyphs': count_glyphs(eva),
                'is_logogram': eva in LOGOGRAMS,
                'root': root, 'suffix': suffix,
            }
            if LOGOGRAMS.get(eva): morph['logogram_latin'] = LOGOGRAMS[eva]
            if ic is not None: morph['i_count'] = ic
            if ec is not None: morph['e_count'] = ec
            if suffix: morph['suffix_type'] = suffix.upper().replace('AIIN','AIN_DOUBLE').replace('AIN','AIN_SINGLE').replace('AIIIN','AIN_TRIPLE') if 'ain' in suffix else suffix.upper()
            # Fix suffix_type
            if suffix == 'ain': morph['suffix_type'] = 'AIN_SINGLE'
            elif suffix == 'aiin': morph['suffix_type'] = 'AIN_DOUBLE'
            elif suffix == 'aiiin': morph['suffix_type'] = 'AIN_TRIPLE'
            elif suffix == 'ey': morph['suffix_type'] = 'EY_SINGLE'
            elif suffix == 'eey': morph['suffix_type'] = 'EEY_DOUBLE'
            elif suffix == 'eeey': morph['suffix_type'] = 'EEY_TRIPLE'
            elif suffix == 'edy': morph['suffix_type'] = 'EDY_SINGLE'
            elif suffix == 'eedy': morph['suffix_type'] = 'EDY_DOUBLE'
            elif suffix: morph['suffix_type'] = suffix.upper()

            morph['is_dose_candidate'] = ic is not None
            morph['has_gallows'] = bool(re.match(r'^[pkft]', eva)) and len(eva) > 1

            word = {
                'word_id': '%s.%d.%d' % (fid, lnum, wi),
                'position': wi,
                'eva_primary': eva,
                'morphology': morph,
            }
            if variants: word['eva_variants_zl'] = variants
            if uncertain: word['uncertain'] = True
            if specials: word['special_glyphs'] = specials
            words.append(word)

        line_data = {
            'line_id': '%s.%d' % (fid, lnum),
            'line_num': lnum, 'line_type': ltype,
            'n_words': len(words), 'words': words,
        }
        if has_star: line_data['has_star'] = True
        if has_end: line_data['has_end'] = True
        if annotations: line_data['annotations'] = annotations

        current_block['lines'].append(line_data)
        current_block['n_lines'] += 1
        current_block['n_words'] += len(words)
        current_folio['metadata']['n_lines'] += 1
        current_folio['metadata']['n_words'] += len(words)

    return folios

# ================================================================
# PARSE LSI.txt — extract variants per line
# ================================================================
def parse_lsi():
    print('Parsing LSI.txt for variants...')
    with open(LSI_PATH, encoding='latin-1') as f:
        lsi_raw = f.read()

    # Structure: each line has <folio.linenum,...;TRANSCRIBER> text
    # We collect readings per (folio, linenum, transcriber)
    readings = defaultdict(lambda: defaultdict(list))  # (folio,lnum) -> transcriber -> [words]

    for line in lsi_raw.split('\n'):
        line = line.strip()
        if not line or line.startswith('#'): continue

        m = re.match(r'<(f\d+[rv]\d?)\.(\d+),[^;]*;(\w+)>\s*(.*)', line)
        if not m: continue

        fid = m.group(1)
        lnum = int(m.group(2))
        transcriber = m.group(3)
        text = m.group(4)

        # Clean
        text = re.sub(r'<[^>]*>', '', text)
        text = re.sub(r'[!?\*\'"{}]', '', text)
        text = text.replace(',', '.').strip()
        words = [w.strip().lower() for w in re.split(r'[.\s]+', text) if w.strip() and re.match(r'^[a-z]+$', w.strip().lower())]

        readings[(fid, lnum)][transcriber] = words

    print('  LSI: %d unique (folio,line) positions' % len(readings))
    return readings

# ================================================================
# MERGE: add LSI variants to ZL-based JSON
# ================================================================
def merge_lsi_variants(folios, lsi_readings):
    print('Merging LSI variants...')
    n_enriched = 0
    n_total = 0

    for fid, folio in folios.items():
        for block in folio['blocks']:
            for line in block['lines']:
                lnum = line['line_num']
                key = (fid, lnum)

                if key not in lsi_readings:
                    continue

                transcribers = lsi_readings[key]
                # Skip H (composite) for consensus — use independent transcribers
                independent = {t: w for t, w in transcribers.items() if t != 'H'}

                zl_words = line['words']

                for wi, word in enumerate(zl_words):
                    n_total += 1
                    eva_zl = word['eva_primary']
                    variants = []
                    agree = 0
                    total_indep = 0

                    for transcriber, t_words in independent.items():
                        if wi < len(t_words):
                            t_eva = t_words[wi]
                            total_indep += 1
                            if t_eva == eva_zl:
                                agree += 1
                            else:
                                variants.append({'source': 'LSI_%s' % transcriber, 'eva': t_eva})

                    if variants:
                        existing = word.get('eva_variants_zl', [])
                        word['eva_variants'] = [{'source': 'ZL', 'eva': v} for v in existing] + variants
                        if 'eva_variants_zl' in word:
                            del word['eva_variants_zl']
                        n_enriched += 1

                    if total_indep > 0:
                        word['consensus'] = agree
                        word['consensus_total'] = total_indep

    print('  Enriched %d / %d words with LSI variants (%.1f%%)' % (n_enriched, n_total, n_enriched*100/max(n_total,1)))
    return n_enriched

# ================================================================
# STATS
# ================================================================
def compute_stats(folios):
    stats = {
        'total_folios': len(folios), 'total_lines': 0, 'total_words': 0,
        'total_blocks': 0, 'total_variants': 0, 'total_uncertain': 0,
        'total_logograms': 0, 'total_dose_candidates': 0,
        'sections': Counter(), 'words_by_section': Counter(),
        'blocks_by_section': Counter(), 'suffix_types': Counter(),
        'consensus_dist': Counter(),
    }
    for fid, folio in folios.items():
        sec = folio['metadata']['section']
        stats['sections'][sec] += 1
        for block in folio['blocks']:
            stats['total_blocks'] += 1
            stats['blocks_by_section'][sec] += 1
            for line in block['lines']:
                stats['total_lines'] += 1
                for w in line['words']:
                    stats['total_words'] += 1
                    stats['words_by_section'][sec] += 1
                    if w.get('eva_variants'): stats['total_variants'] += 1
                    if w.get('uncertain'): stats['total_uncertain'] += 1
                    m = w.get('morphology', {})
                    if m.get('is_logogram'): stats['total_logograms'] += 1
                    if m.get('is_dose_candidate'): stats['total_dose_candidates'] += 1
                    st = m.get('suffix_type')
                    if st: stats['suffix_types'][st] += 1
                    c = w.get('consensus')
                    if c is not None: stats['consensus_dist'][str(c)] += 1
    return stats

# ================================================================
# MAIN
# ================================================================
def main():
    folios = parse_zl()
    lsi = parse_lsi()
    n_enriched = merge_lsi_variants(folios, lsi)

    stats = compute_stats(folios)

    output = {
        '_meta': {
            'source_primary': 'ZL.txt (Zandbergen-Landini v2b, 2022)',
            'source_variants': 'LSI_ivtff_0d.txt (Stolfi/Takahashi interlinear)',
            'version': '1.0',
            'date': '2026-04-12',
            'total_folios': stats['total_folios'],
            'total_lines': stats['total_lines'],
            'total_words': stats['total_words'],
            'total_blocks': stats['total_blocks'],
            'total_with_variants': stats['total_variants'],
            'total_logograms': stats['total_logograms'],
            'total_dose_candidates': stats['total_dose_candidates'],
            'note': 'TEXT ONLY. ZL=primary, LSI=variants. No K&A, no candidates.',
        },
        'folios': folios,
    }

    print('Writing %s...' % OUT_PATH)
    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False)

    stats_json = {k: (dict(v) if isinstance(v, Counter) else v) for k, v in stats.items()}
    with open(STATS_PATH, 'w', encoding='utf-8') as f:
        json.dump(stats_json, f, indent=2, ensure_ascii=False)

    # Print summary
    print()
    print('=' * 60)
    print('PROJECT_HOPE — vms_structured.json BUILT')
    print('=' * 60)
    print('Primary: ZL.txt | Variants: LSI.txt')
    print()
    print('Folios:       %6d' % stats['total_folios'])
    print('Lines:        %6d' % stats['total_lines'])
    print('Words:        %6d' % stats['total_words'])
    print('Blocks:       %6d' % stats['total_blocks'])
    print('With variants:%6d (%.1f%%)' % (stats['total_variants'], stats['total_variants']*100/max(stats['total_words'],1)))
    print('Logograms:    %6d (%.1f%%)' % (stats['total_logograms'], stats['total_logograms']*100/max(stats['total_words'],1)))
    print('Dose cands:   %6d (%.1f%%)' % (stats['total_dose_candidates'], stats['total_dose_candidates']*100/max(stats['total_words'],1)))
    print()
    print('Sections:')
    for sec in sorted(stats['sections']):
        print('  %-12s %3d fol  %6d words  %4d blocks' % (sec, stats['sections'][sec], stats['words_by_section'][sec], stats['blocks_by_section'][sec]))
    print()
    print('Consensus (independent transcribers agreeing with ZL):')
    for c in sorted(stats['consensus_dist']):
        print('  %s agree: %6d words' % (c, stats['consensus_dist'][c]))
    print()

    # Validate f103r
    f103r = folios.get('f103r')
    if f103r:
        print('f103r: %d blocks, %d words, %d lines' % (len(f103r['blocks']), f103r['metadata']['n_words'], f103r['metadata']['n_lines']))
        doses = sum(1 for b in f103r['blocks'] for l in b['lines'] for w in l['words'] if w.get('morphology',{}).get('is_dose_candidate'))
        print('f103r doses: %d (%.1f per recipe)' % (doses, doses/len(f103r['blocks'])))
    print()
    print('Size: %.1f MB' % (OUT_PATH.stat().st_size / 1e6))

if __name__ == '__main__':
    main()
