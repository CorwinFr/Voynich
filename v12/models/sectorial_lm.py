#!/usr/bin/env python3
"""
Sectorial Language Models built from lemmatized Latin medical corpora.
Uses Collatinus daemon (localhost:5555) for lemmatization.
"""
import json, os, re, socket, sys, time
from collections import Counter, defaultdict
from pathlib import Path

COLLATINUS_HOST = '127.0.0.1'
COLLATINUS_PORT = 5555
CACHE_DIR = Path(__file__).parent


def lemmatize_collatinus(word: str, cache: dict = {}) -> str:
    """Lemmatize a Latin word via Collatinus daemon. Returns lemma or original word."""
    w = word.lower().strip()
    if not w or len(w) < 2:
        return w

    if w in cache:
        return cache[w]

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((COLLATINUS_HOST, COLLATINUS_PORT))
        s.sendall(f'-lfr {w}'.encode('utf-8'))
        data = b''
        while True:
            try:
                chunk = s.recv(4096)
                if not chunk:
                    break
                data += chunk
            except:
                break
        s.close()

        response = data.decode('utf-8').strip()
        # Parse response: "* lemma, ..." -> extract lemma
        if response.startswith('*'):
            # Format: "* lĕmma, ae, f. : definition"
            parts = response.split(',')[0].replace('*', '').strip()
            # Remove diacritics for matching
            lemma = re.sub(r'[ăĕĭŏŭāēīōūȳ]', lambda m: {
                'ă':'a','ĕ':'e','ĭ':'i','ŏ':'o','ŭ':'u',
                'ā':'a','ē':'e','ī':'i','ō':'o','ū':'u','ȳ':'y'
            }.get(m.group(), m.group()), parts).lower().strip()
            cache[w] = lemma
            return lemma
    except Exception:
        pass

    cache[w] = w
    return w


def lemmatize_batch(words: list[str], progress_every: int = 5000) -> list[str]:
    """Lemmatize a list of words, with caching and progress."""
    cache = {}
    result = []
    total = len(words)
    for i, w in enumerate(words):
        if i > 0 and i % progress_every == 0:
            print(f'    Lemmatized {i}/{total} ({len(cache)} cached)...', file=sys.stderr)
        result.append(lemmatize_collatinus(w, cache))
    print(f'    Done: {total} words, {len(cache)} unique lemmas', file=sys.stderr)
    return result


def build_lm(corpus_path: str, output_path: str, name: str):
    """Build a bigram language model from a Latin corpus file."""
    print(f'\n=== Building LM: {name} from {corpus_path} ===')

    # Tokenize
    with open(corpus_path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read().lower()
    words = [w for w in re.findall(r'[a-z]+', text) if len(w) >= 2 and len(w) <= 25]
    print(f'  Tokens: {len(words)}')

    # Lemmatize via Collatinus
    print('  Lemmatizing via Collatinus...')
    lemmas = lemmatize_batch(words)

    # Build bigram counts
    bigrams = Counter()
    unigrams = Counter()
    for i in range(len(lemmas) - 1):
        bigrams[(lemmas[i], lemmas[i+1])] += 1
        unigrams[lemmas[i]] += 1
    if lemmas:
        unigrams[lemmas[-1]] += 1

    print(f'  Unigrams: {len(unigrams)}')
    print(f'  Bigrams: {len(bigrams)}')

    # Save as JSON
    data = {
        'name': name,
        'source': corpus_path,
        'total_tokens': len(words),
        'unique_lemmas': len(unigrams),
        'unique_bigrams': len(bigrams),
        'unigrams': dict(unigrams.most_common(10000)),
        'bigrams': {f'{a}|{b}': c for (a, b), c in bigrams.most_common(50000)},
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print(f'  Saved to {output_path}')
    print(f'  Top 20 bigrams:')
    for (a, b), c in bigrams.most_common(20):
        print(f'    {a:15s} {b:15s} {c:6d}')


class SectorialLM:
    """Load and query a sectorial language model."""

    def __init__(self, path: str):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.name = data['name']
        self.unigrams = data['unigrams']
        self.bigrams = {}
        for key, count in data['bigrams'].items():
            a, b = key.split('|')
            self.bigrams[(a, b)] = count
        self.total = data['total_tokens']
        self.vocab_size = data['unique_lemmas']

    def bigram_score(self, lemma1: str, lemma2: str) -> float:
        """Return log probability P(lemma2 | lemma1) with Laplace smoothing."""
        import math
        count_bg = self.bigrams.get((lemma1, lemma2), 0)
        count_ug = self.unigrams.get(lemma1, 0)
        prob = (count_bg + 1) / (count_ug + self.vocab_size)
        return math.log(prob)

    def score_sequence(self, lemmas: list[str]) -> float:
        """Score a sequence of lemmas using bigram log-probabilities."""
        if len(lemmas) < 2:
            return 0.0
        total = 0.0
        for i in range(len(lemmas) - 1):
            total += self.bigram_score(lemmas[i], lemmas[i+1])
        return total / (len(lemmas) - 1)

    def has_bigram(self, lemma1: str, lemma2: str) -> bool:
        """Check if a bigram exists in the LM."""
        return (lemma1, lemma2) in self.bigrams


def build_all():
    """Build all 3 sectorial LMs."""
    corpora = [
        ('D:/Github/Voynich/CORPORA_FINAL/corpus_herbal.txt',
         str(CACHE_DIR / 'lm_herbal.json'), 'LM_HERBAL'),
        ('D:/Github/Voynich/CORPORA_FINAL/corpus_pharma.txt',
         str(CACHE_DIR / 'lm_pharma.json'), 'LM_PHARMA'),
        ('D:/Github/Voynich/CORPORA_FINAL/corpus_balnea.txt',
         str(CACHE_DIR / 'lm_balnea.json'), 'LM_BALNEA'),
    ]
    for corpus_path, output_path, name in corpora:
        if not os.path.exists(corpus_path):
            print(f'  SKIP: {corpus_path} not found')
            continue
        build_lm(corpus_path, output_path, name)


if __name__ == '__main__':
    build_all()
