"""
CLI entry point: python -m v12 --folio f88r
"""
import argparse
import sys
import os

# Add parent directory to path so we can import v12
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from v12.config import Config
from v12.pipeline import VoynichPipeline
from v12.folio_reader import read_folio


def main():
    parser = argparse.ArgumentParser(description='Voynich Decoder v12')
    parser.add_argument('--folio', '-f', type=str, help='Folio ID to decode (e.g., f88r)')
    parser.add_argument('--word', '-w', type=str, help='Single EVA word to decode')
    parser.add_argument('--no-english', action='store_true', help='Omit English translation')
    parser.add_argument('--audit', action='store_true', help='Show audit trail for OPAQUE/LOW words')
    parser.add_argument('--all-folios', action='store_true', help='Decode all folios')
    args = parser.parse_args()

    # Initialize
    config = Config()
    pipeline = VoynichPipeline(config)
    pipeline.load()

    if args.word:
        # Decode single word
        result = pipeline.decode_word(args.word)
        print(f"\n  {result.eva} → {result.latin}")
        print(f"  Confidence: {result.confidence}")
        print(f"  Layer: {result.layer}")
        print(f"  Rule: {result.rule}")
        if result.alternatives:
            print(f"  Alternatives:")
            for alt_lat, alt_rule in result.alternatives:
                print(f"    {alt_lat} ({alt_rule})")
        return

    if args.folio:
        # Decode folio
        output = read_folio(
            pipeline, config.transcription_path, args.folio,
            show_english=not args.no_english,
            show_audit=args.audit,
        )
        print(output)
        return

    if args.all_folios:
        from v12.loaders.transcription import list_folios
        folios = list_folios(config.transcription_path)
        for fid, section in folios:
            output = read_folio(
                pipeline, config.transcription_path, fid,
                show_english=not args.no_english,
            )
            print(output)
        return

    # Default: show help
    parser.print_help()


if __name__ == '__main__':
    main()
