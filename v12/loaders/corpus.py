"""
Latin corpus loader: builds word frequency model from medical Latin corpus.
"""
import re
from collections import Counter


class CorpusModel:
    """Word frequency model from Latin medical corpus."""

    def __init__(self):
        self.word_freq: Counter = Counter()
        self._prefix_index: dict[str, tuple[str, int]] = {}

    def load(self, corpus_path: str):
        """Load corpus and build frequency table."""
        with open(corpus_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                for w in re.findall(r'[a-zA-Z]+', line.lower()):
                    if 2 <= len(w) <= 25:
                        self.word_freq[w] += 1

        # Build prefix index for truncation lookup (top 12K words)
        for w, freq in self.word_freq.most_common(12000):
            for plen in range(2, min(len(w), 14)):
                prefix = w[:plen]
                if prefix not in self._prefix_index:
                    self._prefix_index[prefix] = (w, freq)

    def freq(self, word: str) -> int:
        """Get frequency of a word."""
        return self.word_freq.get(word.lower(), 0)

    def truncation_lookup(self, stem: str) -> tuple[str, int] | None:
        """Find the most likely full word for a truncated stem."""
        result = self._prefix_index.get(stem.lower())
        if result and len(result[0]) > len(stem):
            return result
        return None

    @property
    def size(self) -> int:
        return len(self.word_freq)
