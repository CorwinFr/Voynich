"""
Analyze the mysterious 'l' glyph (191x occurrences) by examining its context.
What word appears before and after 'l' in every occurrence?
"""
import sys, os
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from v12.config import Config
from v12.pipeline import VoynichPipeline
from v12.loaders.transcription import list_folios, parse_folio


def main():
    print("=" * 80)
    print("  'l' LOGOGRAM ANALYSIS — 191 occurrences")
    print("=" * 80)

    config = Config()
    pipeline = VoynichPipeline(config)
    pipeline.load()

    folios = list_folios(config.transcription_path)

    before_word = Counter()
    after_word = Counter()
    before_eva = Counter()
    after_eva = Counter()
    sections = Counter()
    positions = Counter()  # position in line (start/middle/end)
    examples = []

    for fid, section in folios:
        lines, sec = parse_folio(config.transcription_path, fid)
        if not lines:
            continue
        decoded = pipeline.decode_folio(lines)

        for lnum, words in sorted(decoded.items()):
            for i, dw in enumerate(words):
                if dw.eva == 'l':
                    # Context
                    b_dw = words[i-1] if i > 0 else None
                    a_dw = words[i+1] if i < len(words)-1 else None

                    if b_dw:
                        before_word[b_dw.latin] += 1
                        before_eva[b_dw.eva] += 1
                    if a_dw:
                        after_word[a_dw.latin] += 1
                        after_eva[a_dw.eva] += 1

                    sections[section or '?'] += 1

                    # Position
                    if i == 0:
                        positions['START'] += 1
                    elif i == len(words) - 1:
                        positions['END'] += 1
                    else:
                        positions['MIDDLE'] += 1

                    # Example
                    ctx = []
                    for j in range(max(0,i-2), min(len(words), i+3)):
                        if j == i:
                            ctx.append(f"[l]")
                        else:
                            ctx.append(words[j].latin)
                    examples.append((fid, lnum, ' '.join(ctx)))

    # Report
    output = []
    output.append("=" * 80)
    output.append("  'l' LOGOGRAM ANALYSIS")
    output.append(f"  Total occurrences: {sum(sections.values())}")
    output.append("=" * 80)

    output.append("\n## SECTION DISTRIBUTION")
    for sec, count in sections.most_common():
        output.append(f"  {sec:5s} : {count:4d}")

    output.append("\n## POSITION IN LINE")
    for pos, count in positions.most_common():
        output.append(f"  {pos:8s} : {count:4d}")

    output.append("\n## WORD BEFORE 'l' (top 30)")
    for word, count in before_word.most_common(30):
        output.append(f"  {word:25s} : {count:4d}")

    output.append("\n## WORD AFTER 'l' (top 30)")
    for word, count in after_word.most_common(30):
        output.append(f"  {word:25s} : {count:4d}")

    output.append("\n## EVA BEFORE 'l' (top 20)")
    for eva, count in before_eva.most_common(20):
        output.append(f"  {eva:20s} : {count:4d}")

    output.append("\n## EVA AFTER 'l' (top 20)")
    for eva, count in after_eva.most_common(20):
        output.append(f"  {eva:20s} : {count:4d}")

    output.append("\n## EXAMPLES (first 40)")
    for fid, lnum, ctx in examples[:40]:
        output.append(f"  {fid:8s} L{lnum:02d}: {ctx}")

    # Hypothesis testing
    output.append("\n\n## HYPOTHESIS ANALYSIS")
    output.append("=" * 60)

    # H1: l = libra (weight unit)
    # If before ingredients or after numbers
    ingr_after = sum(1 for w in after_word if w in ('aloes','hiera','ture','cera','mel','oleum','aquam'))
    output.append(f"\n  H1: l = LIBRA (weight unit)")
    output.append(f"    Ingredient follows 'l': {ingr_after} times")
    output.append(f"    Mostly in MIDDLE of line: {positions.get('MIDDLE',0)}")

    # H2: l = vel (or)
    # If between two similar words
    output.append(f"\n  H2: l = VEL (or)")
    output.append(f"    Position distribution supports conjunction: {positions}")

    # H3: l = abbreviation marker (paragraph/section)
    output.append(f"\n  H3: l = paragraph/section marker")
    output.append(f"    At START of line: {positions.get('START',0)}")
    output.append(f"    At END of line: {positions.get('END',0)}")

    report = '\n'.join(output)
    out_path = os.path.join(os.path.dirname(__file__), '..', 'output', 'L_LOGOGRAM_ANALYSIS.txt')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\nReport: {out_path}")
    print(report)


if __name__ == '__main__':
    main()
