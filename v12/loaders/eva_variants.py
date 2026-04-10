"""
EVA VARIANT GENERATOR — Unified transcription with glyph doubts.

Instead of picking ONE reading per word, generates ALL plausible
readings with confidence weights. The pipeline then decodes EACH
variant and keeps the best-scoring result.

Sources of variants:
1. ZL bracket notation [alt1:alt2] — both alternatives
2. LSI multi-transcriber (H, V, U) — disagreements
3. Known EVA confusions (ch↔ee, s↔r, a↔o, p↔f, t↔k)
"""
import re
from typing import NamedTuple
from itertools import product


class EVAVariant(NamedTuple):
    """A word reading with confidence weight."""
    eva: str
    weight: float  # 1.0 = consensus, 0.7 = primary alt, 0.4 = secondary alt
    source: str    # 'ZL', 'H', 'V', 'U', 'confusion_rule'


# ── Known EVA glyph confusions ───────────────────────────────────
# Each tuple: (glyph_a, glyph_b, confusion_probability)
# Based on documented transcription errors across H/V/U

GLYPH_CONFUSIONS = [
    ('ch', 'ee', 0.3),   # Most common: bench vs double-e
    ('s', 'r', 0.2),     # Similar shape
    ('a', 'o', 0.15),    # Bowl shape confusion
    ('p', 'f', 0.15),    # Gallows variants (confirmed by L03 Q1/Q3)
    ('t', 'k', 0.1),     # Gallows confusion
    ('y', 'a', 0.1),     # Final position
    ('d', 'j', 0.05),    # Rare (seen in L03)
]


def parse_zl_variants(raw_text: str) -> list[tuple[str, list[EVAVariant]]]:
    """Parse a ZL text line and extract words with bracket variants.

    Input: 'daiin.of[che:eee]y.shes'
    Output: [
        ('daiin', [EVAVariant('daiin', 1.0, 'ZL')]),
        ('ofchey', [EVAVariant('ofchey', 0.7, 'ZL_alt1'),
                     EVAVariant('ofeeey', 1.0, 'ZL_alt2')]),
        ('shes', [EVAVariant('shes', 1.0, 'ZL')]),
    ]
    """
    # Remove non-word markup but KEEP brackets
    text = re.sub(r'<[^>]*>', '', raw_text)
    text = re.sub(r'<!.*?>', '', text)
    text = re.sub(r'<%>|<\$>', '', text)
    text = re.sub(r'\{[^}]*\}', '', text)
    text = re.sub(r'@\d+;?', '', text)
    text = re.sub(r'\?', '', text)
    text = text.replace(',', '.')

    results = []
    for token in text.split('.'):
        token = token.strip()
        if not token:
            continue

        # Check for bracket alternatives [alt1:alt2]
        bracket_match = re.search(r'\[([^\]]*):([^\]]*)\]', token)
        if bracket_match:
            alt1_insert = bracket_match.group(1)
            alt2_insert = bracket_match.group(2)
            prefix = token[:bracket_match.start()]
            suffix = token[bracket_match.end():]

            word_alt1 = prefix + alt1_insert + suffix
            word_alt2 = prefix + alt2_insert + suffix

            # Clean
            word_alt1 = re.sub(r'[^a-z]', '', word_alt1)
            word_alt2 = re.sub(r'[^a-z]', '', word_alt2)

            if word_alt1 and word_alt2:
                variants = [
                    EVAVariant(word_alt2, 1.0, 'ZL_preferred'),  # ZL takes alt2
                    EVAVariant(word_alt1, 0.7, 'ZL_alt1'),
                ]
                # Use the ZL-preferred form as the display word
                results.append((word_alt2, variants))
            elif word_alt1:
                results.append((word_alt1, [EVAVariant(word_alt1, 1.0, 'ZL')]))
            elif word_alt2:
                results.append((word_alt2, [EVAVariant(word_alt2, 1.0, 'ZL')]))
        else:
            clean = re.sub(r'[^a-z]', '', token)
            if clean:
                results.append((clean, [EVAVariant(clean, 1.0, 'ZL')]))

    return results


def generate_confusion_variants(word: str, max_variants: int = 8) -> list[EVAVariant]:
    """Generate variants from known glyph confusions.

    For each confusion pair (a↔b), if the word contains 'a',
    generate a variant with 'b' substituted (and vice versa).
    Only generates single-substitution variants (not combinations).
    """
    variants = []

    for glyph_a, glyph_b, prob in GLYPH_CONFUSIONS:
        # Check a→b substitution
        if glyph_a in word:
            # Replace first occurrence only (to limit explosion)
            new_word = word.replace(glyph_a, glyph_b, 1)
            if new_word != word:
                variants.append(EVAVariant(new_word, prob, f'confusion_{glyph_a}>{glyph_b}'))

        # Check b→a substitution
        if glyph_b in word:
            new_word = word.replace(glyph_b, glyph_a, 1)
            if new_word != word:
                variants.append(EVAVariant(new_word, prob, f'confusion_{glyph_b}>{glyph_a}'))

    # Sort by weight descending, limit
    variants.sort(key=lambda v: -v.weight)
    return variants[:max_variants]


def merge_variants(zl_variants: list[EVAVariant],
                   confusion_variants: list[EVAVariant],
                   lsi_variants: list[EVAVariant] | None = None) -> list[EVAVariant]:
    """Merge all variant sources, deduplicate, sort by weight."""
    all_vars = {}

    for v in zl_variants:
        if v.eva not in all_vars or v.weight > all_vars[v.eva].weight:
            all_vars[v.eva] = v

    if lsi_variants:
        for v in lsi_variants:
            if v.eva not in all_vars or v.weight > all_vars[v.eva].weight:
                all_vars[v.eva] = v

    for v in confusion_variants:
        if v.eva not in all_vars:
            all_vars[v.eva] = v

    result = sorted(all_vars.values(), key=lambda v: -v.weight)
    return result


def get_word_variants(word: str, zl_variants: list[EVAVariant] | None = None,
                      include_confusions: bool = True,
                      max_total: int = 12) -> list[EVAVariant]:
    """Get all variants for a word, from all sources.

    Args:
        word: The primary EVA reading
        zl_variants: Pre-parsed ZL bracket variants (if any)
        include_confusions: Whether to generate confusion variants
        max_total: Maximum number of variants to return

    Returns:
        List of EVAVariant, sorted by weight (highest first)
    """
    if zl_variants is None:
        zl_variants = [EVAVariant(word, 1.0, 'ZL')]

    confusion = generate_confusion_variants(word) if include_confusions else []

    merged = merge_variants(zl_variants, confusion)
    return merged[:max_total]


def parse_folio_with_variants(zl_path: str, target_folio: str,
                               include_confusions: bool = True
                               ) -> dict[int, list[tuple[str, list[EVAVariant]]]]:
    """Parse a folio and return words with ALL variants.

    Returns: {line_num: [(primary_word, [variants]), ...]}
    """
    lines = {}

    with open(zl_path, 'r', encoding='utf-8') as f:
        for raw_line in f:
            line_match = re.match(r'<(f\d+[rv]\d?)\.(\d+)', raw_line.strip())
            if not line_match:
                continue

            folio = line_match.group(1)
            if folio != target_folio:
                continue

            lnum = int(line_match.group(2))
            text = raw_line.strip()

            # Parse ZL variants (keeping brackets)
            word_variants = parse_zl_variants(text)

            # For each word, add confusion variants
            enriched = []
            for primary, zl_vars in word_variants:
                if include_confusions and len(primary) >= 2:
                    all_vars = get_word_variants(primary, zl_vars, True)
                else:
                    all_vars = zl_vars
                enriched.append((primary, all_vars))

            if enriched:
                lines[lnum] = enriched

    return lines


# ── Quick test ────────────────────────────────────────────────────

if __name__ == '__main__':
    # Test with L04 words
    test_words = [
        ('ofeeey', '[che:eee]'),  # ZL has bracket
        ('shes', None),
        ('okeeod', None),
        ('aros', None),
        ('tchor', None),
    ]

    print("EVA VARIANT GENERATOR — Test")
    print()

    for word, bracket_info in test_words:
        variants = get_word_variants(word)
        print(f"  {word:12s} → {len(variants)} variants:")
        for v in variants:
            print(f"    {v.eva:15s} (w={v.weight:.2f}, {v.source})")
        print()

    # Test ZL parsing
    print("ZL bracket parsing test:")
    test_line = '<f57v.4,+Cc> daiin.otey.of[che:eee]y.shes.o.d'
    parsed = parse_zl_variants(test_line)
    for primary, variants in parsed:
        print(f"  {primary:12s} → {[(v.eva, v.weight) for v in variants]}")
