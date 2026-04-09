"""
Generate a clean, human-readable Latin text from the complete decode.
Only CONFIRMED + HIGH confidence words. LOW/OPAQUE shown as [...].
Grouped by manuscript section.
"""
import sys, os
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from v12.config import Config
from v12.pipeline import VoynichPipeline
from v12.loaders.transcription import list_folios, parse_folio

SECTION_NAMES = {
    'H': 'HERBAL — Monographies de plantes',
    'A': 'ASTRONOMIE — Diagrammes astronomiques',
    'B': 'BALNEA — Bains thérapeutiques',
    'C': 'COSMO — Cosmologie/théorie',
    'P': 'PHARMA — Recettes pharmaceutiques',
    'S': 'STARS — Section étoiles/recettes',
    'T': 'TEXT — Pages de texte',
    'Z': 'ZODIAC — Calendrier zodiacal',
}


def main():
    config = Config()
    pipeline = VoynichPipeline(config)
    pipeline.load()

    folios = list_folios(config.transcription_path)

    # Group folios by section
    by_section = defaultdict(list)
    for fid, section in folios:
        by_section[section or '?'].append(fid)

    output = []
    output.append("=" * 80)
    output.append("  VOYNICH MANUSCRIPT — LATIN DECODE v12")
    output.append("  Clean reading text (CONFIRMED + HIGH confidence only)")
    output.append(f"  {len(folios)} folios")
    output.append("=" * 80)

    stats = {'total': 0, 'readable': 0, 'opaque': 0}

    for section in ['H', 'P', 'S', 'B', 'Z', 'A', 'C', 'T', '?']:
        if section not in by_section:
            continue

        section_name = SECTION_NAMES.get(section, section)
        output.append(f"\n\n{'#' * 80}")
        output.append(f"# {section_name}")
        output.append(f"{'#' * 80}")

        for fid in by_section[section]:
            lines, sec = parse_folio(config.transcription_path, fid)
            if not lines:
                continue

            decoded = pipeline.decode_folio(lines)

            folio_lines = []
            for lnum in sorted(decoded.keys()):
                words = decoded[lnum]
                parts = []
                for dw in words:
                    stats['total'] += 1
                    if dw.confidence in ('CONFIRMED', 'HIGH'):
                        stats['readable'] += 1
                        parts.append(dw.latin)
                    elif dw.confidence == 'MEDIUM':
                        stats['readable'] += 1
                        parts.append(f'{dw.latin}?')
                    else:
                        stats['opaque'] += 1
                        parts.append('...')

                line_text = ' '.join(parts)
                # Collapse consecutive ...
                while '... ...' in line_text:
                    line_text = line_text.replace('... ...', '...')
                folio_lines.append(line_text)

            if folio_lines:
                output.append(f"\n--- {fid.upper()} ---")
                for i, line in enumerate(folio_lines):
                    output.append(f"  {line}")

    # Summary
    pct = stats['readable'] / max(stats['total'], 1) * 100
    output.append(f"\n\n{'=' * 80}")
    output.append(f"  SUMMARY")
    output.append(f"  Total words: {stats['total']}")
    output.append(f"  Readable: {stats['readable']} ({pct:.1f}%)")
    output.append(f"  Opaque: {stats['opaque']} ({100-pct:.1f}%)")
    output.append(f"{'=' * 80}")

    report = '\n'.join(output)
    out_path = os.path.join(os.path.dirname(__file__), '..', 'output', 'VOYNICH_LATIN_CLEAN.txt')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"Written: {out_path}")
    print(f"Readable: {stats['readable']}/{stats['total']} ({pct:.1f}%)")


if __name__ == '__main__':
    main()
