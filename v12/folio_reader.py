"""
High-level folio reader: parse + decode + format.
"""
from v12.pipeline import VoynichPipeline
from v12.loaders.transcription import parse_folio
from v12.stages.logogram import DecodedWord
from v12.registry.audit import AuditTrail
from v12.translate import translate
from v12.validation.entropy import entropy_report


def read_folio(pipeline: VoynichPipeline, zl_path: str, folio_id: str,
               show_english: bool = True, show_audit: bool = False) -> str:
    """
    Decode and format a complete folio.

    Returns formatted string with EVA, Latin, English, and statistics.
    """
    # Parse folio
    lines, section = parse_folio(zl_path, folio_id)
    if not lines:
        # Try with suffix variants
        for suffix in ['1', '2']:
            lines, section = parse_folio(zl_path, folio_id + suffix)
            if lines:
                folio_id = folio_id + suffix
                break
    if not lines:
        return f"  Folio {folio_id} not found in transcription."

    # Decode
    decoded = pipeline.decode_folio(lines)

    # Build audit trail
    audit = AuditTrail()
    for lnum, words in decoded.items():
        for i, dw in enumerate(words):
            audit.log(dw, folio_id, lnum, i)

    # Format output
    output = []
    output.append(f"\n{'='*100}")
    output.append(f"  FOLIO {folio_id.upper()} | Section: {section or '?'}")
    output.append(f"{'='*100}")

    decoded_texts = []

    for lnum in sorted(decoded.keys()):
        words = decoded[lnum]
        eva_parts = [dw.eva for dw in words]
        latin_parts = []
        english_parts = []

        for dw in words:
            # Format Latin with confidence markers
            if dw.confidence in ('CONFIRMED', 'HIGH'):
                latin_parts.append(dw.latin)
            elif dw.confidence == 'MEDIUM':
                latin_parts.append(f'{dw.latin}(?)')
            elif dw.confidence == 'LOW':
                latin_parts.append(f'_{dw.latin}_')
            else:
                latin_parts.append(f'[{dw.latin}]')

            english_parts.append(translate(dw.latin))

        latin_line = ' '.join(latin_parts)
        decoded_texts.append(latin_line)

        output.append(f"\n  L{lnum:02d} EVA  : {' '.join(eva_parts)}")
        output.append(f"      LATIN: {latin_line}")
        if show_english:
            output.append(f"      EN   : {' '.join(english_parts)}")

    # Statistics
    stats = pipeline.stats(decoded)
    output.append(f"\n  {'='*70}")
    output.append(f"  STATISTICS v12")
    output.append(f"  Total words: {stats['total']}")
    output.append(f"  CONFIRMED: {stats['CONFIRMED']}")
    output.append(f"  HIGH:      {stats['HIGH']}")
    output.append(f"  MEDIUM:    {stats['MEDIUM']}")
    output.append(f"  LOW:       {stats['LOW']}")
    output.append(f"  OPAQUE:    {stats['OPAQUE']}")
    output.append(f"  Perseus:   {stats['perseus_valid']}")
    output.append(f"  Medical:   {stats['medical']}")

    # Entropy
    ent = entropy_report(decoded_texts)
    output.append(f"  H1 entropy: {ent['h1']} bits (ref Latin: ~4.0)")
    output.append(f"  H2 entropy: {ent['h2']} bits (ref Latin: ~3.5, ref EVA: ~2.1)")
    output.append(f"  Quality:    {ent['quality']}")
    output.append(f"  {'='*70}")

    # Audit trail (OPAQUE and LOW words for review)
    if show_audit:
        opaque = audit.opaque_words()
        low = audit.low_words()
        if opaque or low:
            output.append(f"\n  --- WORDS NEEDING REVIEW ---")
            for e in opaque:
                alts = ', '.join(f'{a[0]}' for a in e.alternatives[:3])
                output.append(f"  OPAQUE: {e.eva_word:15s} -> {e.final_latin:20s} (L{e.line:02d}) alts: {alts}")
            for e in low[:10]:
                alts = ', '.join(f'{a[0]}' for a in e.alternatives[:3])
                output.append(f"  LOW:    {e.eva_word:15s} -> {e.final_latin:20s} (L{e.line:02d}) alts: {alts}")

    return '\n'.join(output)
