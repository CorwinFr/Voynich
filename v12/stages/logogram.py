"""
S1: Logogram resolution.
Looks up whole EVA words in the logogram table.
"""
from dataclasses import dataclass
from typing import Optional
from v12.config import Config, Logogram


@dataclass
class DecodedWord:
    eva: str
    latin: str
    confidence: str    # CONFIRMED, HIGH, MEDIUM, LOW, OPAQUE
    layer: str         # L1_LOGO, L2_AGG, L3_KA, EXCEPTION
    rule: str          # specific rule that produced this decode
    alternatives: list[tuple[str, str]] | None = None  # [(latin, rule), ...]


def resolve_logogram(eva_word: str, config: Config) -> Optional[DecodedWord]:
    """
    Check if the EVA word is a known logogram.

    Returns DecodedWord if matched, None otherwise.
    """
    word = eva_word.lower().strip()

    # Check exception registry first (highest priority)
    if word in config.exceptions:
        return DecodedWord(
            eva=word,
            latin=config.exceptions[word],
            confidence='CONFIRMED',
            layer='EXCEPTION',
            rule='exception_registry',
        )

    # Check logogram table
    if word in config.logograms:
        logo = config.logograms[word]
        confidence = 'CONFIRMED' if logo.confidence == 'confirmed' else 'HIGH'
        return DecodedWord(
            eva=word,
            latin=logo.latin,
            confidence=confidence,
            layer='L1_LOGO',
            rule=f'logo_{logo.source}',
        )

    # Check confirmed roots as standalone words
    if word in config.confirmed_roots:
        root = config.confirmed_roots[word]
        return DecodedWord(
            eva=word,
            latin=root.latin,
            confidence='CONFIRMED',
            layer='L2_ROOT_STANDALONE',
            rule='confirmed_root',
        )

    return None
