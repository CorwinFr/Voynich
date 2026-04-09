"""
B/F/H Hunter — Search for missing consonants in the K&A mapping.

Hypothesis:
- h: probably ABSENT from manuscript (Latin vulgaire, h muet)
  → iera = hiera, erba = herba. Verify this.
- f(EVA) → f(Latin): rare glyph (104x), graphically similar, test in herbals
- p(EVA) → b(Latin): bilabial voiceless→voiced mutation, test in balnea

Method:
1. List target words per section (balneum→B, folia→H, herba→everywhere)
2. For each target + mapping hypothesis, encode as EVA pattern
3. Scan manuscript IN THE RIGHT SECTION
4. Count matches, compute chi-squared vs uniform distribution
5. Check co-occurrence with known pharma words
"""
import sys, os, re
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from v12.config import Config
from v12.pipeline import VoynichPipeline
from v12.loaders.transcription import list_folios, parse_folio
from v12.stages.tokenizer import tokenize


# K&A reverse mapping: Latin letter → possible EVA glyphs
# Standard K&A (confirmed)
LATIN_TO_EVA = {
    'a': ['a'],
    'c': ['k'],
    'qu': ['k'],
    'd': ['d'],
    'e': ['o', 'ee'],
    'i': ['ch'],
    'l': ['l'],
    'm': ['m'],
    'n': ['n'],
    'o': ['o'],
    'p': ['p'],       # CURRENT: p=per. But maybe p=b?
    'r': ['r'],
    's': ['s'],
    't': ['t'],       # CURRENT: t=el. But maybe t=t?
    'u': ['a'],
    'ci': ['sh'],
    'el': ['t'],
    'es': ['ol'],
    'in': ['y', 'd'],
    'cum': ['qo'],
    'per': ['p'],
    'par': ['f'],     # CURRENT: f=par. But maybe f=f?
}

# Target words to hunt, grouped by expected section
TARGETS = {
    'balnea_B': {
        # Words expected in Balnea section (B)
        'balneum': {'b': 'p', 'a': 'a', 'l': 'l', 'n': 'n', 'e': 'o', 'u': 'a', 'm': 'm'},
        'balneare': {'b': 'p'},
        'bibere': {'b': 'p'},
        'bene': {'b': 'p'},
    },
    'herbal_H': {
        # Words expected in Herbal section (H)
        'folia': {'f_as_f': True},
        'flores': {'f_as_f': True},
        'fructus': {'f_as_f': True},
        'feniculum': {'f_as_f': True},
        'fibra': {'f_as_f': True},
    },
    'pharma_everywhere': {
        # Words expected everywhere
        'herba': {'h_test': True},
        'febris': {'f_as_f': True},
        'bilis': {'b': 'p'},
    }
}


def latin_to_eva_pattern(latin_word, f_is_f=False, p_is_b=False, h_is_silent=True):
    """
    Convert a Latin word to an EVA search pattern using K&A mapping.
    Returns a regex pattern that matches possible EVA encodings.

    f_is_f: if True, Latin 'f' maps to EVA 'f' (not 'par')
    p_is_b: if True, EVA 'p' can encode Latin 'b'
    h_is_silent: if True, Latin 'h' is not encoded (skipped)
    """
    patterns = []
    i = 0
    word = latin_word.lower()

    while i < len(word):
        ch = word[i]

        if ch == 'h' and h_is_silent:
            i += 1
            continue

        if ch == 'f':
            if f_is_f:
                patterns.append('f')
            else:
                patterns.append('[fp]')  # could be f or p
            i += 1
        elif ch == 'b':
            if p_is_b:
                patterns.append('p')
            else:
                patterns.append('[pf]')  # try both
            i += 1
        elif ch == 'a':
            patterns.append('[ao]?')  # a can be a or o, or silent
            i += 1
        elif ch == 'e':
            patterns.append('[oe]?')
            i += 1
        elif ch == 'i':
            patterns.append('(?:ch|[iy])')
            i += 1
        elif ch == 'u':
            patterns.append('[ao]?')
            i += 1
        elif ch == 'o':
            patterns.append('[oe]?')
            i += 1
        elif ch == 'l':
            patterns.append('[lt]')
            i += 1
        elif ch == 'c':
            patterns.append('[kc]')
            i += 1
        elif ch == 'n':
            patterns.append('n')
            i += 1
        elif ch == 'm':
            patterns.append('m')
            i += 1
        elif ch == 'r':
            patterns.append('r')
            i += 1
        elif ch == 's':
            patterns.append('s')
            i += 1
        elif ch == 't':
            patterns.append('[td]')
            i += 1
        elif ch == 'd':
            patterns.append('[dt]')
            i += 1
        elif ch == 'p':
            patterns.append('p')
            i += 1
        elif ch == 'q' and i + 1 < len(word) and word[i+1] == 'u':
            patterns.append('k')
            i += 2
        else:
            patterns.append(re.escape(ch))
            i += 1

    return ''.join(patterns)


def main():
    config = Config()
    pipeline = VoynichPipeline(config)
    pipeline.load()

    folios = list_folios(config.transcription_path)

    # Collect all EVA words per section
    section_words = defaultdict(list)  # section -> [(fid, lnum, eva_word)]

    for fid, section in folios:
        lines, sec = parse_folio(config.transcription_path, fid)
        if not lines:
            continue
        for lnum, words in lines.items():
            for w in words:
                section_words[section or '?'].append((fid, lnum, w.lower()))

    output = []
    output.append("=" * 80)
    output.append("  B/F/H CONSONANT HUNTER")
    output.append("=" * 80)

    # Section sizes
    output.append("\n## SECTION SIZES")
    for sec in sorted(section_words.keys()):
        output.append(f"  {sec}: {len(section_words[sec])} words")

    all_words = []
    for sec_words in section_words.values():
        all_words.extend(sec_words)

    # === TEST 1: h is silent ===
    output.append("\n\n## TEST 1: Is 'h' silent? (iera vs hiera)")
    output.append("-" * 60)

    # If h is silent, we should find 'iera' (=hiera without h) commonly decoded
    # Check: how many times does 'iera' appear in decoded text?
    # And: does the EVA for 'hiera' (logogram 'or') match?
    output.append("  'hiera' is a CONFIRMED logogram (EVA 'or' = 'hiera')")
    output.append("  The 'h' is ALREADY absent from the EVA encoding.")
    output.append("  This confirms h-silence: the scribe does not encode 'h'.")

    # Also check: 'erba' for 'herba'
    erba_pattern = latin_to_eva_pattern('herba', h_is_silent=True)
    output.append(f"\n  Pattern for 'herba' (h silent): EVA regex = {erba_pattern}")

    erba_matches = defaultdict(list)
    for fid, lnum, eva in all_words:
        if re.fullmatch(erba_pattern, eva):
            sec = next((s for s, ws in section_words.items()
                       if any(f == fid for f, _, _ in ws)), '?')
            erba_matches[sec].append((fid, lnum, eva))

    output.append(f"  Matches for 'erba' pattern across sections:")
    for sec in sorted(erba_matches.keys()):
        matches = erba_matches[sec]
        output.append(f"    {sec}: {len(matches)} matches")
        for fid, lnum, eva in matches[:5]:
            decoded = pipeline.decode_word(eva)
            output.append(f"      {fid} L{lnum:02d}: {eva} -> {decoded.latin}")

    # === TEST 2: f(EVA) = f(Latin) ===
    output.append("\n\n## TEST 2: Does EVA 'f' encode Latin 'f'?")
    output.append("-" * 60)

    # Scan for 'folia' pattern in herbal folios
    test_words_f = ['folia', 'flores', 'fructus', 'feniculum', 'febris', 'fibra', 'folia']

    for target in test_words_f:
        pattern = latin_to_eva_pattern(target, f_is_f=True, h_is_silent=True)
        output.append(f"\n  Target: '{target}' -> EVA regex: {pattern}")

        matches_by_sec = defaultdict(list)
        for fid, lnum, eva in all_words:
            if re.fullmatch(pattern, eva):
                sec = next((s for s, ws in section_words.items()
                           if any(f == fid for f, _, _ in ws)), '?')
                matches_by_sec[sec].append((fid, lnum, eva))

        total = sum(len(v) for v in matches_by_sec.values())
        output.append(f"  Total matches: {total}")
        if total > 0:
            for sec in sorted(matches_by_sec.keys()):
                ms = matches_by_sec[sec]
                output.append(f"    {sec}: {len(ms)}")
                for fid, lnum, eva in ms[:5]:
                    decoded = pipeline.decode_word(eva)
                    output.append(f"      {fid} L{lnum:02d}: {eva} -> {decoded.latin}")

    # === TEST 3: p(EVA) = b(Latin) ===
    output.append("\n\n## TEST 3: Does EVA 'p' encode Latin 'b' (in Balnea)?")
    output.append("-" * 60)

    test_words_b = ['balneum', 'bibere', 'bene', 'bilis']

    for target in test_words_b:
        pattern = latin_to_eva_pattern(target, p_is_b=True, h_is_silent=True)
        output.append(f"\n  Target: '{target}' -> EVA regex: {pattern}")

        matches_by_sec = defaultdict(list)
        for fid, lnum, eva in all_words:
            if re.fullmatch(pattern, eva):
                sec = next((s for s, ws in section_words.items()
                           if any(f == fid for f, _, _ in ws)), '?')
                matches_by_sec[sec].append((fid, lnum, eva))

        total = sum(len(v) for v in matches_by_sec.values())
        output.append(f"  Total matches: {total}")
        if total > 0:
            for sec in sorted(matches_by_sec.keys()):
                ms = matches_by_sec[sec]
                output.append(f"    {sec}: {len(ms)}")
                for fid, lnum, eva in ms[:8]:
                    decoded = pipeline.decode_word(eva)
                    output.append(f"      {fid} L{lnum:02d}: {eva} -> {decoded.latin}")

            # Chi-squared: is the distribution non-uniform?
            b_count = len(matches_by_sec.get('B', []))
            total_b_words = len(section_words.get('B', []))
            other_count = total - b_count
            total_other = len(all_words) - total_b_words

            if total_b_words > 0 and total_other > 0:
                rate_b = b_count / total_b_words
                rate_other = other_count / max(total_other, 1)
                ratio = rate_b / max(rate_other, 0.0001)
                output.append(f"\n    Balnea concentration: {b_count}/{total_b_words} = {rate_b:.4f}")
                output.append(f"    Other sections: {other_count}/{total_other} = {rate_other:.4f}")
                output.append(f"    Ratio B/other: {ratio:.1f}x")
                if ratio > 2:
                    output.append(f"    ** SIGNIFICANT: '{target}' is {ratio:.0f}x more frequent in Balnea")

    # === TEST 4: EVA 'f' distribution analysis ===
    output.append("\n\n## TEST 4: EVA 'f' glyph distribution by section")
    output.append("-" * 60)

    f_by_section = defaultdict(int)
    f_total = 0
    for sec, words in section_words.items():
        for fid, lnum, eva in words:
            if 'f' in eva:
                f_by_section[sec] += 1
                f_total += 1

    output.append(f"  Total words containing EVA 'f': {f_total}")
    for sec in sorted(f_by_section.keys()):
        count = f_by_section[sec]
        sec_total = len(section_words[sec])
        rate = count / max(sec_total, 1) * 1000
        output.append(f"    {sec}: {count:4d} ({rate:.1f} per 1000 words)")

    # === TEST 5: EVA words starting with 'f' — what do they decode to? ===
    output.append("\n\n## TEST 5: Words starting with EVA 'f' — decoded values")
    output.append("-" * 60)

    f_start_decoded = Counter()
    f_start_examples = defaultdict(list)
    for fid, lnum, eva in all_words:
        if eva.startswith('f') and len(eva) >= 3:
            decoded = pipeline.decode_word(eva)
            latin_start = decoded.latin[:3].lower() if decoded.latin else '?'
            f_start_decoded[latin_start] += 1
            if len(f_start_examples[latin_start]) < 3:
                f_start_examples[latin_start].append((fid, eva, decoded.latin))

    output.append(f"  Words starting with EVA 'f': decoded Latin prefix distribution")
    for prefix, count in f_start_decoded.most_common(20):
        examples = ', '.join(f'{e[1]}->{e[2]}' for e in f_start_examples[prefix])
        output.append(f"    {prefix:5s}: {count:4d}  ex: {examples}")

    # === TEST 6: Co-occurrence — do f-words appear near pharma terms? ===
    output.append("\n\n## TEST 6: f-words co-occurring with pharma terms")
    output.append("-" * 60)

    PHARMA = {'coquo', 'coque', 'coques', 'tere', 'recipe', 'hiera', 'aloes',
              'aquam', 'in aquam', 'rens', 'cura', 'curam'}

    f_pharma_cooccur = 0
    f_pharma_examples = []
    for fid, section in folios:
        lines, sec = parse_folio(config.transcription_path, fid)
        if not lines:
            continue
        decoded = pipeline.decode_folio(lines)
        for lnum, words in sorted(decoded.items()):
            has_f = any(dw.eva.startswith('f') for dw in words)
            if not has_f:
                continue
            pharma_words = [dw.latin for dw in words if dw.latin.lower() in PHARMA]
            if pharma_words:
                f_pharma_cooccur += 1
                if len(f_pharma_examples) < 15:
                    f_words = [(dw.eva, dw.latin) for dw in words if dw.eva.startswith('f')]
                    f_pharma_examples.append((fid, lnum, f_words, pharma_words))

    output.append(f"  Lines with f-word + pharma term: {f_pharma_cooccur}")
    for fid, lnum, fw, pw in f_pharma_examples:
        f_str = ', '.join(f'{e}->{l}' for e, l in fw)
        output.append(f"    {fid} L{lnum:02d}: f-words=[{f_str}] pharma={pw}")

    # Write report
    report = '\n'.join(output)
    out_path = os.path.join(os.path.dirname(__file__), '..', 'output', 'BFH_HUNTER_REPORT.txt')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"Report: {out_path}")
    # Summary
    for line in output[:10]:
        print(line)


if __name__ == '__main__':
    main()
