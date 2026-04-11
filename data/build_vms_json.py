"""
BUILD vms_structured.json from ZL.txt (Zandbergen-Landini v2b, 2022).

Source of truth for the ENTIRE Voynich manuscript.
TEXT ONLY — no K&A, no candidates, no interpretations.

Folio > Block > Line > Word structure.
Each word has: EVA primary, variants, morphology, uncertainty.
"""
import re
import json
import sys
import io
from collections import Counter, defaultdict, OrderedDict
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ZL_PATH = Path(__file__).parent / 'transcriptions' / 'ZL.txt'

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
    'aiiin', 'aiin', 'ain',     # i-count system
    'eeey', 'eey', 'ey',       # e-count system (single e)
    'eedy', 'edy',              # e-count + dy
    'eol',                      # e + ol
    'ol', 'or', 'ar', 'al',    # basic endings
    'dy', 'am', 'om',          # terminators
    'chy', 'shy',               # ch/sh + y
    'air',                      # special
]


def get_section(fnum, rv='r', sub=''):
    """Map folio number to section."""
    if fnum <= 56:
        return 'herbal_a'
    elif fnum == 57 and rv == 'v':
        return 'volvelle'
    elif fnum == 57:
        return 'herbal_a'
    elif 58 <= fnum <= 67:
        return 'astro'
    elif 68 <= fnum <= 73:
        return 'cosmo'
    elif 74 <= fnum <= 74:
        return 'other'  # f74 is missing/other
    elif 75 <= fnum <= 84:
        return 'balnea'
    elif 85 <= fnum <= 86:
        return 'bio'
    elif 87 <= fnum <= 102:
        return 'herbal_b'
    elif 103 <= fnum <= 116:
        return 'pharma'
    return 'other'


def count_glyphs(eva_word):
    """Count EVA glyph units (digraphs count as 1)."""
    digraphs = ['sh', 'ch', 'ee', 'ii', 'ai', 'oi', 'ph', 'ck', 'th', 'cth', 'ckh', 'cph', 'cfh']
    i = 0
    count = 0
    w = eva_word
    while i < len(w):
        matched = False
        for dg in sorted(digraphs, key=len, reverse=True):
            if w[i:i+len(dg)] == dg:
                count += 1
                i += len(dg)
                matched = True
                break
        if not matched:
            count += 1
            i += 1
    return count


def analyze_morphology(eva_word):
    """Analyze EVA word morphology: root, suffix, i_count, e_count."""
    result = {
        'n_glyphs': count_glyphs(eva_word),
        'is_logogram': eva_word in LOGOGRAMS,
        'logogram_latin': LOGOGRAMS.get(eva_word),
        'root': eva_word,
        'suffix': '',
        'suffix_type': None,
        'i_count': None,
        'e_count': None,
        'is_dose_candidate': False,
        'has_gallows': bool(re.match(r'^[pkft]', eva_word)) and len(eva_word) > 1,
    }

    if result['is_logogram']:
        return result

    # Find longest matching suffix
    for sfx in SUFFIXES:
        if eva_word.endswith(sfx) and len(eva_word) > len(sfx):
            result['root'] = eva_word[:-len(sfx)]
            result['suffix'] = sfx
            break

    # Classify suffix
    sfx = result['suffix']
    if sfx == 'ain':
        result['suffix_type'] = 'AIN_SINGLE'
        result['i_count'] = 1
        result['is_dose_candidate'] = True
    elif sfx == 'aiin':
        result['suffix_type'] = 'AIN_DOUBLE'
        result['i_count'] = 2
        result['is_dose_candidate'] = True
    elif sfx == 'aiiin':
        result['suffix_type'] = 'AIN_TRIPLE'
        result['i_count'] = 3
        result['is_dose_candidate'] = True
    elif sfx == 'ey':
        result['suffix_type'] = 'EY_SINGLE'
        result['e_count'] = 1
    elif sfx == 'eey':
        result['suffix_type'] = 'EEY_DOUBLE'
        result['e_count'] = 2
    elif sfx == 'eeey':
        result['suffix_type'] = 'EEY_TRIPLE'
        result['e_count'] = 3
    elif sfx == 'edy':
        result['suffix_type'] = 'EDY_SINGLE'
        result['e_count'] = 1
    elif sfx == 'eedy':
        result['suffix_type'] = 'EDY_DOUBLE'
        result['e_count'] = 2
    elif sfx == 'eol':
        result['suffix_type'] = 'EOL'
    elif sfx in ('ol', 'or', 'ar', 'al', 'dy', 'am', 'om', 'chy', 'shy', 'air'):
        result['suffix_type'] = sfx.upper()

    return result


def parse_eva_word(raw_token):
    """Parse a raw ZL token into primary EVA + variants + uncertainty.

    Handles:
    - [a:o] variants → primary=a, variants=[o]
    - [cth:oto] → primary=cth, variants=[oto]
    - ? uncertainty markers
    - @NNN; special glyphs
    - {xxx} ligatures/special
    """
    # Extract variants [x:y:z]
    variants = []
    primary_parts = []
    uncertain_positions = []
    special_glyphs = []

    i = 0
    raw = raw_token
    pos = 0

    while i < len(raw):
        if raw[i] == '[':
            # Find closing bracket
            j = raw.index(']', i) if ']' in raw[i:] else len(raw)
            content = raw[i+1:j]
            options = content.split(':')
            primary_parts.append(options[0])  # First option = primary
            for opt in options[1:]:
                if opt and opt != '?':
                    variants.append({'position': pos, 'alt': opt})
            i = j + 1
            pos += len(options[0])
        elif raw[i] == '{':
            # Special glyph/ligature
            j = raw.index('}', i) if '}' in raw[i:] else len(raw)
            content = raw[i+1:j]
            special_glyphs.append({'position': pos, 'glyph': content})
            primary_parts.append(content)
            i = j + 1
            pos += len(content)
        elif raw[i] == '?':
            uncertain_positions.append(pos)
            i += 1
        elif raw[i] == '@':
            # @NNN; special code
            m = re.match(r'@(\d+);', raw[i:])
            if m:
                code = m.group(1)
                special_glyphs.append({'position': pos, 'glyph': '@%s;' % code})
                primary_parts.append('@%s;' % code)
                i += len(m.group(0))
                pos += 1
            else:
                primary_parts.append(raw[i])
                i += 1
                pos += 1
        else:
            primary_parts.append(raw[i])
            i += 1
            pos += 1

    primary = ''.join(primary_parts)
    # Clean primary: remove remaining punctuation artifacts
    primary = primary.strip('.,;:')

    return primary, variants, uncertain_positions, special_glyphs


def parse_zl():
    """Parse the complete ZL.txt into structured data."""
    with open(ZL_PATH, encoding='utf-8') as f:
        raw_text = f.read()

    folios = OrderedDict()
    current_folio_id = None
    current_folio = None
    current_block = None
    current_block_num = 0
    folio_metadata = {}

    # First pass: collect folio metadata
    for line in raw_text.split('\n'):
        line = line.strip()
        if not line:
            continue

        # Folio metadata line: <f1r>  <! $Q=A $P=A $F=a $B=1 $I=T $L=A $H=1 $C=1 $X=V>
        meta_match = re.match(r'<(f\d+[rv]\d?)>\s+<!\s*(.+?)>', line)
        if meta_match:
            fid = meta_match.group(1)
            meta_str = meta_match.group(2)
            meta = {}
            for m in re.finditer(r'\$(\w+)=(\w+)', meta_str):
                meta[m.group(1)] = m.group(2)
            folio_metadata[fid] = meta
            continue

    # Second pass: parse text
    for line in raw_text.split('\n'):
        line = line.strip()
        if not line:
            continue

        # Skip comments and metadata-only lines
        if line.startswith('#'):
            continue
        if re.match(r'^<f\d+[rv]\d?>\s+<!', line) and '.' not in line.split('>')[0]:
            continue

        # Text line: <f103r.1,@P0>  <%>text.here
        text_match = re.match(r'<(f(\d+)([rv])(\d?))\.(\d+),([^>]*)>', line)
        if not text_match:
            continue

        folio_id = text_match.group(1)
        fnum = int(text_match.group(2))
        rv = text_match.group(3)
        sub = text_match.group(4)
        line_num = int(text_match.group(5))
        line_type = text_match.group(6)  # @P0, +P0, *P0, =P0, @Cc, etc.

        # Get the text part (after the header)
        text_part = line[text_match.end():].strip()

        # Check for star marker <%>
        has_star = '<%>' in text_part

        # Check for end marker <$>
        has_end = '<$>' in text_part

        # Check for line break <->
        has_break = '<->' in text_part

        # Extract annotations
        annotations = []
        for ann in re.finditer(r'<!([^>]+)>', text_part):
            ann_text = ann.group(1)
            if ann_text.startswith('$'):
                continue  # metadata, not annotation
            annotations.append(ann_text)

        # Clean text: remove markup, keep EVA
        clean = text_part
        clean = re.sub(r'<[^>]*>', '', clean)  # remove all tags
        clean = clean.replace(',', '.').strip()  # normalize separators

        # Split into raw tokens
        raw_tokens = [t.strip() for t in clean.split('.') if t.strip()]

        # New folio?
        if folio_id != current_folio_id:
            current_folio_id = folio_id
            meta = folio_metadata.get(folio_id, {})
            section = get_section(fnum, rv, sub)

            current_folio = {
                'folio_id': folio_id,
                'folio_num': fnum,
                'rv': rv,
                'sub': sub,
                'metadata': {
                    'section': section,
                    'quire': meta.get('Q', ''),
                    'bifolio': meta.get('B', ''),
                    'illustration': meta.get('I', ''),
                    'language': meta.get('L', ''),
                    'hand': meta.get('H', ''),
                    'currier': meta.get('C', ''),
                    'extra': meta.get('X', ''),
                    'n_lines': 0,
                    'n_words': 0,
                    'n_blocks': 0,
                    'has_stars': False,
                },
                'blocks': [],
            }
            folios[folio_id] = current_folio
            current_block = None
            current_block_num = 0

        # New block? (star marker or first line of folio)
        is_new_block = has_star or (line_type.startswith('@') and current_block is None)

        if is_new_block:
            current_block_num += 1
            section = current_folio['metadata']['section']
            block_type = 'recipe' if section == 'pharma' else 'paragraph'

            # Parse star info from annotations
            star_info = None
            if has_star:
                current_folio['metadata']['has_stars'] = True
                # Try to extract star details from ZL comments
                # (color and points are in comment lines BEFORE the text, not always available)
                star_info = {'type': 'star'}

            current_block = {
                'block_id': '%s_B%02d' % (folio_id, current_block_num),
                'block_type': block_type,
                'block_num': current_block_num,
                'separator': star_info,
                'n_lines': 0,
                'n_words': 0,
                'lines': [],
            }
            current_folio['blocks'].append(current_block)
            current_folio['metadata']['n_blocks'] = current_block_num

        # If no block yet (first line, no star), create default
        if current_block is None:
            current_block_num = 1
            current_block = {
                'block_id': '%s_B%02d' % (folio_id, current_block_num),
                'block_type': 'paragraph',
                'block_num': current_block_num,
                'separator': None,
                'n_lines': 0,
                'n_words': 0,
                'lines': [],
            }
            current_folio['blocks'].append(current_block)
            current_folio['metadata']['n_blocks'] = 1

        # Parse words
        words = []
        for w_idx, raw_token in enumerate(raw_tokens):
            if not raw_token or len(raw_token) == 0:
                continue

            primary, variants, uncertain, specials = parse_eva_word(raw_token)

            # Skip empty after cleaning
            if not primary or not re.search(r'[a-z]', primary):
                continue

            # Clean primary to just EVA letters
            eva_clean = re.sub(r'[^a-z]', '', primary.lower())
            if not eva_clean:
                continue

            morph = analyze_morphology(eva_clean)

            word = {
                'word_id': '%s.%d.%d' % (folio_id, line_num, w_idx),
                'position': w_idx,
                'eva_primary': eva_clean,
                'eva_raw': raw_token,
                'uncertain': len(uncertain) > 0,
                'uncertain_positions': uncertain if uncertain else None,
                'special_glyphs': specials if specials else None,
                'eva_variants': variants if variants else None,
                'morphology': morph,
            }

            # Remove None fields to save space
            word = {k: v for k, v in word.items() if v is not None}

            words.append(word)

        # Build line
        line_data = {
            'line_id': '%s.%d' % (folio_id, line_num),
            'line_num': line_num,
            'line_type': line_type,
            'has_star': has_star,
            'has_end': has_end,
            'has_break': has_break,
            'annotations': annotations if annotations else None,
            'n_words': len(words),
            'words': words,
        }
        line_data = {k: v for k, v in line_data.items() if v is not None}

        current_block['lines'].append(line_data)
        current_block['n_lines'] += 1
        current_block['n_words'] += len(words)
        current_folio['metadata']['n_lines'] += 1
        current_folio['metadata']['n_words'] += len(words)

    return folios


def build_stats(folios):
    """Compute global statistics."""
    stats = {
        'total_folios': len(folios),
        'total_lines': 0,
        'total_words': 0,
        'total_blocks': 0,
        'total_with_variants': 0,
        'total_uncertain': 0,
        'total_logograms': 0,
        'total_dose_candidates': 0,
        'sections': Counter(),
        'suffix_types': Counter(),
        'words_per_section': Counter(),
        'blocks_per_section': Counter(),
    }

    for fid, folio in folios.items():
        sec = folio['metadata']['section']
        stats['sections'][sec] += 1
        for block in folio['blocks']:
            stats['total_blocks'] += 1
            stats['blocks_per_section'][sec] += 1
            for line in block['lines']:
                stats['total_lines'] += 1
                for word in line['words']:
                    stats['total_words'] += 1
                    stats['words_per_section'][sec] += 1
                    if word.get('eva_variants'):
                        stats['total_with_variants'] += 1
                    if word.get('uncertain'):
                        stats['total_uncertain'] += 1
                    morph = word.get('morphology', {})
                    if morph.get('is_logogram'):
                        stats['total_logograms'] += 1
                    if morph.get('is_dose_candidate'):
                        stats['total_dose_candidates'] += 1
                    st = morph.get('suffix_type')
                    if st:
                        stats['suffix_types'][st] += 1

    return stats


def main():
    print('Parsing ZL.txt...')
    folios = parse_zl()

    print('Computing statistics...')
    stats = build_stats(folios)

    # Build output
    output = {
        '_meta': {
            'source': 'ZL.txt (Zandbergen-Landini v2b, 2022)',
            'version': '1.0',
            'date': '2026-04-12',
            'parser': 'build_vms_json.py (ZL-based)',
            'total_folios': stats['total_folios'],
            'total_lines': stats['total_lines'],
            'total_words': stats['total_words'],
            'total_blocks': stats['total_blocks'],
            'total_with_variants': stats['total_with_variants'],
            'total_uncertain': stats['total_uncertain'],
            'total_logograms': stats['total_logograms'],
            'total_dose_candidates': stats['total_dose_candidates'],
            'note': 'TEXT ONLY — no K&A, no candidates, no interpretations',
        },
        'folios': folios,
    }

    # Save
    out_path = Path(__file__).parent / 'vms_structured.json'
    print('Writing %s...' % out_path)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    # Save stats
    stats_path = Path(__file__).parent / 'vms_structured_stats.json'
    # Convert Counters to dicts for JSON
    stats_json = {k: (dict(v) if isinstance(v, Counter) else v) for k, v in stats.items()}
    with open(stats_path, 'w', encoding='utf-8') as f:
        json.dump(stats_json, f, indent=2, ensure_ascii=False)

    # Print summary
    print()
    print('=' * 60)
    print('VMS_STRUCTURED.JSON — BUILD COMPLETE')
    print('=' * 60)
    print('Source: ZL.txt (Zandbergen-Landini v2b)')
    print()
    print('Folios:          %d' % stats['total_folios'])
    print('Lines:           %d' % stats['total_lines'])
    print('Words:           %d' % stats['total_words'])
    print('Blocks:          %d' % stats['total_blocks'])
    print('With variants:   %d (%.1f%%)' % (stats['total_with_variants'], stats['total_with_variants']*100/max(stats['total_words'],1)))
    print('Uncertain:       %d (%.1f%%)' % (stats['total_uncertain'], stats['total_uncertain']*100/max(stats['total_words'],1)))
    print('Logograms:       %d (%.1f%%)' % (stats['total_logograms'], stats['total_logograms']*100/max(stats['total_words'],1)))
    print('Dose candidates: %d (%.1f%%)' % (stats['total_dose_candidates'], stats['total_dose_candidates']*100/max(stats['total_words'],1)))
    print()
    print('By section:')
    for sec in sorted(stats['sections']):
        nf = stats['sections'][sec]
        nw = stats['words_per_section'][sec]
        nb = stats['blocks_per_section'][sec]
        print('  %-12s %3d folios  %6d words  %4d blocks' % (sec, nf, nw, nb))
    print()
    print('Suffix types:')
    for st, c in stats['suffix_types'].most_common():
        print('  %-15s %5d' % (st, c))

    # Validate f103r
    print()
    print('=== VALIDATION f103r ===')
    f103r = folios.get('f103r')
    if f103r:
        print('Blocks: %d' % len(f103r['blocks']))
        print('Words:  %d' % f103r['metadata']['n_words'])
        print('Lines:  %d' % f103r['metadata']['n_lines'])
        for b in f103r['blocks'][:3]:
            print('  %s: %d lines, %d words' % (b['block_id'], b['n_lines'], b['n_words']))
    else:
        print('f103r NOT FOUND!')

    print()
    print('Files:')
    print('  %s (%.1f MB)' % (out_path, out_path.stat().st_size / 1e6))
    print('  %s' % stats_path)


if __name__ == '__main__':
    main()
