"""
SCORER — Scoring functions for candidate evaluation.

All functions return a float 0.0-1.0.
Higher = better match.
"""
import math
from collections import Counter
from typing import List, Dict, Counter as CounterType


def frequency_score(observed_folios: int, total_folios: int,
                    expected_pct: float) -> float:
    """Score based on folio frequency matching.

    Args:
        observed_folios: number of VMS folios the word appears on
        total_folios: total folios in the section
        expected_pct: expected percentage from reference (e.g., 52.6 for myrrha)

    Returns:
        0.0-1.0 score (1.0 = perfect match)
    """
    if total_folios == 0:
        return 0.0
    observed_pct = observed_folios * 100 / total_folios
    delta = abs(observed_pct - expected_pct)
    # Sigmoid-like scoring: delta=0 -> 1.0, delta=50 -> ~0.0
    return math.exp(-delta * delta / (2 * 15 * 15))


def cooccurrence_score(word_a_folios: set, word_b_folios: set,
                       expected_jaccard: float) -> float:
    """Score based on co-occurrence matching (Jaccard similarity).

    Args:
        word_a_folios: set of folios where word A appears
        word_b_folios: set of folios where word B appears
        expected_jaccard: expected Jaccard from reference co-occurrence

    Returns:
        0.0-1.0 score
    """
    if not word_a_folios or not word_b_folios:
        return 0.0
    intersection = len(word_a_folios & word_b_folios)
    union = len(word_a_folios | word_b_folios)
    observed_jaccard = intersection / union if union > 0 else 0.0
    delta = abs(observed_jaccard - expected_jaccard)
    return math.exp(-delta * delta / (2 * 0.2 * 0.2))


def word_length_score(eva_glyphs: int, latin_letters: int,
                      latin_syllables: int, mode='letter') -> float:
    """Score based on word length correlation.

    Args:
        eva_glyphs: number of EVA glyphs in the word
        latin_letters: number of letters in Latin candidate
        latin_syllables: number of syllables in Latin candidate
        mode: 'letter' or 'syllable' (which correlation to test)

    Returns:
        0.0-1.0 score
    """
    if mode == 'letter':
        # Expect ~2 letters per EVA glyph (K&A style)
        expected_glyphs = latin_letters / 2.0
    elif mode == 'syllable':
        # Expect 1 syllable per EVA glyph
        expected_glyphs = latin_syllables
    else:
        return 0.5  # unknown mode

    if expected_glyphs == 0:
        return 0.0
    ratio = eva_glyphs / expected_glyphs
    # Score peaks at ratio=1.0
    delta = abs(ratio - 1.0)
    return math.exp(-delta * delta / (2 * 0.3 * 0.3))


def context_score(observed_neighbors: CounterType,
                  expected_neighbors: set) -> float:
    """Score based on contextual neighbors.

    Args:
        observed_neighbors: Counter of VMS words appearing near target
        expected_neighbors: set of ref_ids expected to appear nearby

    Returns:
        0.0-1.0 score
    """
    if not observed_neighbors or not expected_neighbors:
        return 0.0
    # This needs the candidate mapping to translate VMS neighbors to ref_ids
    # For now, return a simple overlap ratio
    total = sum(observed_neighbors.values())
    if total == 0:
        return 0.0
    # Placeholder: will be refined when we have partial mappings
    return 0.5


def quadgram_score(decoded_text: str, quadgram_model: Dict[str, float]) -> float:
    """Score decoded text using quadgram language model.

    Args:
        decoded_text: the decoded Latin text
        quadgram_model: dict of quadgram -> log probability

    Returns:
        0.0-1.0 score (normalized perplexity)
    """
    text = decoded_text.lower()
    if len(text) < 4:
        return 0.0

    total_score = 0.0
    n_quadgrams = 0
    floor = min(quadgram_model.values()) if quadgram_model else -20.0

    for i in range(len(text) - 3):
        qg = text[i:i + 4]
        total_score += quadgram_model.get(qg, floor)
        n_quadgrams += 1

    if n_quadgrams == 0:
        return 0.0

    avg_score = total_score / n_quadgrams
    # Normalize: typical Latin is ~-8 to -10, random is ~-15 to -20
    # Map to 0-1 range
    normalized = max(0.0, min(1.0, (avg_score + 15) / 10))
    return normalized


def section_score(word_section_dist: Dict[str, int],
                  ingredient_section_expected: str) -> float:
    """Score based on section distribution.

    An ingredient that's mostly in herbal sections should match
    a VMS word that's mostly in herbal sections.

    Args:
        word_section_dist: Counter of sections for VMS word
        ingredient_section_expected: expected primary section

    Returns:
        0.0-1.0 score
    """
    total = sum(word_section_dist.values())
    if total == 0:
        return 0.0

    section_map = {
        'herbal': ['herbal_A', 'herbal_B'],
        'pharma': ['pharma'],
        'balnea': ['balnea'],
        'astro': ['astro', 'cosmo'],
    }

    expected_sections = section_map.get(ingredient_section_expected, [ingredient_section_expected])
    matched = sum(word_section_dist.get(s, 0) for s in expected_sections)
    return matched / total


def combine_scores(scores: Dict[str, float],
                   weights: Dict[str, float] = None) -> float:
    """Combine multiple scores with weights.

    Default weights favor multi-source convergence.
    """
    if not scores:
        return 0.0

    if weights is None:
        weights = {
            'frequency_match': 1.0,
            'cooccurrence': 1.0,
            'word_length': 0.8,
            'context_bigram': 1.0,
            'section_match': 0.7,
            'crib': 1.5,  # crib evidence is strong
            'quadgram': 0.5,
            'embedding': 1.2,
            'mcmc': 1.0,
            'neural': 1.0,
        }

    weighted_sum = 0.0
    total_weight = 0.0

    for key, score in scores.items():
        w = weights.get(key, 1.0)
        weighted_sum += score * w
        total_weight += w

    if total_weight == 0:
        return 0.0

    return weighted_sum / total_weight


def count_syllables_latin(word: str) -> int:
    """Estimate syllable count for a Latin word.

    Simple heuristic: count vowel groups.
    """
    word = word.lower()
    vowels = 'aeiouy'
    count = 0
    in_vowel = False
    for ch in word:
        if ch in vowels:
            if not in_vowel:
                count += 1
                in_vowel = True
        else:
            in_vowel = False
    return max(1, count)
