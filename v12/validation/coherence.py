"""
Cross-word coherence metrics.
Measures how well decoded words fit together as Latin text.
"""
import json
from collections import defaultdict
from typing import Optional


class BigramLM:
    """Word-level bigram language model for Latin."""

    def __init__(self):
        self.bigrams: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.unigrams: dict[str, int] = defaultdict(int)
        self._total = 0

    def load(self, path: str):
        """Load pre-computed bigram model from JSON."""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if isinstance(data, dict):
            for key, count in data.items():
                parts = key.split('_') if '_' in key else key.split()
                if len(parts) == 2:
                    self.bigrams[parts[0]][parts[1]] = count
                    self.unigrams[parts[0]] += count
                    self._total += count

    def log_prob(self, w1: str, w2: str) -> float:
        """Log probability P(w2 | w1) with Laplace smoothing."""
        import math
        w1, w2 = w1.lower(), w2.lower()
        count_bigram = self.bigrams.get(w1, {}).get(w2, 0)
        count_unigram = self.unigrams.get(w1, 0)
        vocab_size = max(len(self.unigrams), 1)

        # Laplace smoothing
        prob = (count_bigram + 1) / (count_unigram + vocab_size)
        return math.log(prob)

    def score_sequence(self, words: list[str]) -> float:
        """Score a sequence of words using bigram log-probabilities."""
        if len(words) < 2:
            return 0.0
        total = 0.0
        for i in range(len(words) - 1):
            total += self.log_prob(words[i], words[i+1])
        return total / (len(words) - 1)  # normalize by length
