"""
H2 entropy calculator for decoded text.
Target: decoded Latin should have H2 ~3.0-3.5 bits (vs raw EVA ~2.1 bits).
"""
import math
from collections import Counter


def bigram_entropy(text: str) -> float:
    """
    Calculate conditional entropy H2 (second-order) of a text.

    H2 = -sum over all bigrams (c1,c2) of P(c1,c2) * log2(P(c2|c1))

    Returns bits per character.
    """
    text = text.lower().replace(' ', '')
    if len(text) < 2:
        return 0.0

    # Count bigrams and unigrams
    bigram_counts: Counter = Counter()
    unigram_counts: Counter = Counter()

    for i in range(len(text) - 1):
        bigram = text[i:i+2]
        bigram_counts[bigram] += 1
        unigram_counts[text[i]] += 1
    unigram_counts[text[-1]] += 1

    total_bigrams = sum(bigram_counts.values())
    if total_bigrams == 0:
        return 0.0

    # H2 = -sum P(bigram) * log2(P(c2|c1))
    h2 = 0.0
    for (c1, c2), count in bigram_counts.items():
        p_bigram = count / total_bigrams
        p_c2_given_c1 = count / unigram_counts[c1]
        h2 -= p_bigram * math.log2(p_c2_given_c1)

    return h2


def unigram_entropy(text: str) -> float:
    """Calculate first-order entropy H1."""
    text = text.lower().replace(' ', '')
    if not text:
        return 0.0

    counts = Counter(text)
    total = len(text)
    h1 = 0.0
    for count in counts.values():
        p = count / total
        h1 -= p * math.log2(p)
    return h1


def entropy_report(decoded_lines: list[str]) -> dict:
    """
    Generate entropy report for decoded text.

    Returns dict with h1, h2, and quality assessment.
    """
    full_text = ' '.join(decoded_lines)
    h1 = unigram_entropy(full_text)
    h2 = bigram_entropy(full_text)

    # Reference values
    # Latin medical text: H1 ~4.0, H2 ~3.5
    # Raw EVA: H1 ~3.5, H2 ~2.1
    # Good decode should increase H2 toward 3.0+

    quality = 'good' if h2 >= 2.8 else ('fair' if h2 >= 2.4 else 'poor')

    return {
        'h1': round(h1, 3),
        'h2': round(h2, 3),
        'quality': quality,
        'text_length': len(full_text.replace(' ', '')),
        'reference_latin_h2': 3.5,
        'reference_eva_h2': 2.1,
    }
