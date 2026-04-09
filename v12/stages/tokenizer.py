"""
S0: EVA word tokenizer.
Splits EVA text into typed glyph tokens using greedy left-to-right matching.
"""
from dataclasses import dataclass
from v12.config import Config


@dataclass
class GlyphToken:
    glyph: str
    position: int       # index in token sequence
    is_initial: bool
    is_final: bool
    raw_offset: int     # character offset in raw EVA string


def tokenize(eva_word: str, glyph_order: list[str] | None = None) -> list[GlyphToken]:
    """
    Tokenize an EVA word into compound glyph tokens.

    Uses greedy left-to-right matching with the glyph order table.
    Handles: aiin (4-char), iin/iir (3-char), ckh/cfh/cph/cth (3-char),
             ch/sh (2-char), single letters.

    Special: 'ain' not followed by 'i' is split as a+i+n (scribal abbreviation).
    Special: 'iiin' treated as 'iin' (triple reduction).
    """
    if glyph_order is None:
        glyph_order = Config.GLYPH_ORDER

    w = eva_word.lower().strip()
    tokens: list[GlyphToken] = []
    i = 0

    while i < len(w):
        # Special: 'ain' that is NOT part of 'aiin'
        if w[i:i+3] == 'ain' and w[i:i+4] != 'aiin':
            for ch in ['a', 'i', 'n']:
                tokens.append(GlyphToken(
                    glyph=ch, position=len(tokens),
                    is_initial=False, is_final=False, raw_offset=i,
                ))
                i += 1
            continue

        # Special: 'iiin' → treat as 'iin' (triple collapse)
        if w[i:i+4] == 'iiin':
            tokens.append(GlyphToken(
                glyph='iin', position=len(tokens),
                is_initial=False, is_final=False, raw_offset=i,
            ))
            i += 4
            continue

        # Greedy match from glyph order
        matched = False
        for g in glyph_order:
            if w[i:i+len(g)] == g:
                tokens.append(GlyphToken(
                    glyph=g, position=len(tokens),
                    is_initial=False, is_final=False, raw_offset=i,
                ))
                i += len(g)
                matched = True
                break

        if not matched:
            # Unknown character, keep as single token
            if w[i].isalpha():
                tokens.append(GlyphToken(
                    glyph=w[i], position=len(tokens),
                    is_initial=False, is_final=False, raw_offset=i,
                ))
            i += 1

    # Set initial/final flags
    if tokens:
        tokens[0].is_initial = True
        tokens[-1].is_final = True

    return tokens


def preprocess_triples(tokens: list[GlyphToken]) -> list[GlyphToken]:
    """
    Reduce triple-repeated glyphs to single (scribal artifact).
    eee → e, etc.
    """
    result: list[GlyphToken] = []
    i = 0
    while i < len(tokens):
        if (i + 2 < len(tokens)
                and tokens[i].glyph == tokens[i+1].glyph == tokens[i+2].glyph):
            # Keep only one
            tok = tokens[i]
            result.append(GlyphToken(
                glyph=tok.glyph, position=len(result),
                is_initial=tok.is_initial, is_final=tokens[i+2].is_final,
                raw_offset=tok.raw_offset,
            ))
            i += 3
        else:
            tok = tokens[i]
            result.append(GlyphToken(
                glyph=tok.glyph, position=len(result),
                is_initial=tok.is_initial, is_final=tok.is_final,
                raw_offset=tok.raw_offset,
            ))
            i += 1
    return result


def tokens_to_eva(tokens: list[GlyphToken]) -> str:
    """Reconstruct EVA string from tokens."""
    return ''.join(t.glyph for t in tokens)
