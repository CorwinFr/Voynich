"""
Lemmatized Crib Matching — Search for n-gram matches between
decoded Voynich text and medieval Latin corpora, using Collatinus
lemmatization to match across morphological variants.

coquas/coques/coquere → COQUO
aquam/aqua/aquae → AQUA
tere → TERO

This dramatically increases match probability.
"""
import sys, os, re, json, socket
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from v12.config import Config
from v12.pipeline import VoynichPipeline
from v12.loaders.transcription import list_folios, parse_folio


# ─── Collatinus lemmatizer ───
LEMMA_CACHE = {}

def lemmatize(word):
    """Lemmatize a Latin word via Collatinus daemon (localhost:5555)."""
    w = word.lower().strip()
    if w in LEMMA_CACHE:
        return LEMMA_CACHE[w]
    if len(w) < 2 or not w.isalpha():
        LEMMA_CACHE[w] = w
        return w
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect(('127.0.0.1', 5555))
        s.sendall(f'-lfr {w}\n'.encode('utf-8'))
        data = s.recv(4096).decode('utf-8', errors='replace').strip()
        s.close()
        if data.startswith('*'):
            # Extract lemma: "* lĕmma, ae, f. : definition"
            parts = data.split(',')
            lemma = parts[0].replace('*', '').strip()
            # Remove macrons/breves for clean matching
            clean = ''
            for ch in lemma:
                if ch in 'āăâ': clean += 'a'
                elif ch in 'ēĕê': clean += 'e'
                elif ch in 'īĭî': clean += 'i'
                elif ch in 'ōŏô': clean += 'o'
                elif ch in 'ūŭû': clean += 'u'
                else: clean += ch
            LEMMA_CACHE[w] = clean
            return clean
        LEMMA_CACHE[w] = w
        return w
    except Exception:
        LEMMA_CACHE[w] = w
        return w


def lemmatize_sequence(words):
    """Lemmatize a list of words, skip function words."""
    SKIP = {'et', 'in', 'cum', 'de', 'per', 'ad', 'ex', 'ac', 'es', 'est',
            'eius', 'eo', 'ea', 'id', 'qui', 'quae', 'quod', 'hic', 'haec',
            'ille', 'illa', 'se', 'sui', 'sibi'}
    result = []
    for w in words:
        clean = w.lower().strip('_[]()? ')
        if not clean or not clean.isalpha():
            continue
        if clean in SKIP:
            result.append(clean)  # keep function words as-is
        else:
            result.append(lemmatize(clean))
    return result


def extract_ngrams(lemmas, n):
    """Extract n-grams from lemmatized sequence."""
    grams = []
    for i in range(len(lemmas) - n + 1):
        gram = tuple(lemmas[i:i+n])
        # Skip if all function words
        FUNC = {'et', 'in', 'cum', 'de', 'per', 'ad', 'ex', 'ac', 'es', 'est', 'eius'}
        if all(w in FUNC for w in gram):
            continue
        grams.append(gram)
    return grams


def load_corpus_lemmatized(corpus_path):
    """Load and lemmatize a corpus file, return n-gram index."""
    print(f"  Loading corpus: {corpus_path}")
    with open(corpus_path, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read().lower()

    # Split into words
    words = re.findall(r'[a-z]+', text)
    print(f"    Raw words: {len(words)}")

    # Lemmatize (batch — cache makes this fast after first pass)
    lemmas = []
    batch_size = 500
    for i in range(0, len(words), batch_size):
        batch = words[i:i+batch_size]
        for w in batch:
            lemmas.append(lemmatize(w))
        if (i // batch_size) % 20 == 0:
            print(f"    Lemmatized {min(i+batch_size, len(words))}/{len(words)}...")

    # Build n-gram indices
    bigrams = Counter(extract_ngrams(lemmas, 2))
    trigrams = Counter(extract_ngrams(lemmas, 3))
    quadgrams = Counter(extract_ngrams(lemmas, 4))
    pentagrams = Counter(extract_ngrams(lemmas, 5))

    print(f"    Bigrams: {len(bigrams)}, Trigrams: {len(trigrams)}, "
          f"Quadgrams: {len(quadgrams)}, Pentagrams: {len(pentagrams)}")

    return {'bi': bigrams, 'tri': trigrams, 'quad': quadgrams, 'penta': pentagrams}


def main():
    print("=" * 80)
    print("  LEMMATIZED CRIB MATCHING — Collatinus + Full Manuscript")
    print("=" * 80)

    config = Config()
    pipeline = VoynichPipeline(config)
    pipeline.load()

    # Load and lemmatize corpora
    corpus_dir = Path('CORPORA_FINAL')
    corpus_indices = {}
    for name in ['corpus_herbal', 'corpus_pharma', 'corpus_balnea']:
        path = corpus_dir / f'{name}.txt'
        if path.exists():
            corpus_indices[name] = load_corpus_lemmatized(str(path))

    # Decode and lemmatize the Voynich manuscript
    print("\nDecoding and lemmatizing Voynich manuscript...")
    folios = list_folios(config.transcription_path)

    vms_lines = []  # (folio, line, lemmatized_words, raw_words)
    vms_bigrams = Counter()
    vms_trigrams = Counter()
    vms_quadgrams = Counter()
    vms_pentagrams = Counter()

    for i, (fid, section) in enumerate(folios):
        lines, sec = parse_folio(config.transcription_path, fid)
        if not lines:
            continue
        decoded = pipeline.decode_folio(lines)

        for lnum, words in sorted(decoded.items()):
            # Only use CONFIRMED + HIGH words for matching
            raw = []
            for dw in words:
                if dw.confidence in ('CONFIRMED', 'HIGH', 'MEDIUM'):
                    clean = dw.latin.lower().strip('_[]()? ')
                    # Split compound decodings (e.g., "in aquam" → ["in", "aquam"])
                    for part in clean.split():
                        if part.isalpha() and len(part) >= 2:
                            raw.append(part)

            if len(raw) < 2:
                continue

            lemmas = lemmatize_sequence(raw)
            vms_lines.append((fid, lnum, lemmas, raw))

            for gram in extract_ngrams(lemmas, 2):
                vms_bigrams[gram] += 1
            for gram in extract_ngrams(lemmas, 3):
                vms_trigrams[gram] += 1
            for gram in extract_ngrams(lemmas, 4):
                vms_quadgrams[gram] += 1
            for gram in extract_ngrams(lemmas, 5):
                vms_pentagrams[gram] += 1

        if (i + 1) % 30 == 0:
            print(f"  {i+1}/{len(folios)} folios...")

    print(f"\nVMS n-grams: bi={len(vms_bigrams)}, tri={len(vms_trigrams)}, "
          f"quad={len(vms_quadgrams)}, penta={len(vms_pentagrams)}")

    # === MATCH ===
    output = []
    output.append("=" * 80)
    output.append("  LEMMATIZED CRIB MATCHING RESULTS")
    output.append(f"  VMS: {len(vms_lines)} lines lemmatized")
    output.append("=" * 80)

    all_corpus_bi = Counter()
    all_corpus_tri = Counter()
    all_corpus_quad = Counter()
    all_corpus_penta = Counter()

    for name, idx in corpus_indices.items():
        all_corpus_bi += idx['bi']
        all_corpus_tri += idx['tri']
        all_corpus_quad += idx['quad']
        all_corpus_penta += idx['penta']

    # Find matches
    for n, vms_grams, corpus_grams, label in [
        (2, vms_bigrams, all_corpus_bi, 'BIGRAM'),
        (3, vms_trigrams, all_corpus_tri, 'TRIGRAM'),
        (4, vms_quadgrams, all_corpus_quad, 'QUADRIGRAM'),
        (5, vms_pentagrams, all_corpus_penta, 'PENTAGRAM'),
    ]:
        matches = []
        for gram, vms_count in vms_grams.items():
            corpus_count = corpus_grams.get(gram, 0)
            if corpus_count > 0:
                matches.append((gram, vms_count, corpus_count))

        matches.sort(key=lambda x: -(x[1] * x[2]))

        output.append(f"\n\n## {label} MATCHES ({len(matches)} found)")
        output.append("-" * 60)

        # Filter: at least one non-function word
        FUNC = {'et', 'in', 'cum', 'de', 'per', 'ad', 'ex', 'ac', 'es', 'est', 'eius'}
        specific = [m for m in matches if any(w not in FUNC for w in m[0])]
        generic = [m for m in matches if all(w in FUNC for w in m[0])]

        output.append(f"  Specific (content words): {len(specific)}")
        output.append(f"  Generic (function words only): {len(generic)}")

        # Show top specific matches
        for gram, vc, cc in specific[:50]:
            gram_str = ' '.join(gram)
            output.append(f"  {gram_str:40s}  VMS={vc:4d}  CORPUS={cc:4d}")

    # === Find which VMS lines contain the best matches ===
    output.append("\n\n## BEST MATCHING LINES (quad/penta matches in context)")
    output.append("-" * 60)

    quad_set = {gram for gram, vc, cc in
                [(g, v, all_corpus_quad.get(g, 0)) for g, v in vms_quadgrams.items()]
                if cc > 0}
    penta_set = {gram for gram, vc, cc in
                 [(g, v, all_corpus_penta.get(g, 0)) for g, v in vms_pentagrams.items()]
                 if cc > 0}

    for fid, lnum, lemmas, raw in vms_lines:
        line_quads = [g for g in extract_ngrams(lemmas, 4) if g in quad_set]
        line_pentas = [g for g in extract_ngrams(lemmas, 5) if g in penta_set]

        if line_pentas:
            output.append(f"\n  *** PENTAGRAM *** {fid} L{lnum:02d}")
            output.append(f"    Raw: {' '.join(raw)}")
            output.append(f"    Lemmatized: {' '.join(lemmas)}")
            for g in line_pentas:
                output.append(f"    MATCH: {' '.join(g)}")
        elif line_quads:
            output.append(f"\n  QUADRIGRAM {fid} L{lnum:02d}")
            output.append(f"    Raw: {' '.join(raw)}")
            output.append(f"    Lemmatized: {' '.join(lemmas)}")
            for g in line_quads[:3]:
                output.append(f"    MATCH: {' '.join(g)}")

    # Write report
    report = '\n'.join(output)
    out_path = os.path.join(os.path.dirname(__file__), '..', 'output', 'CRIB_LEMMATIZED_REPORT.txt')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(report)

    # Save cache
    cache_path = os.path.join(os.path.dirname(__file__), '..', 'output', 'lemma_cache.json')
    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump(LEMMA_CACHE, f, ensure_ascii=False, indent=1)

    print(f"\nReport: {out_path}")
    print(f"Lemma cache: {cache_path} ({len(LEMMA_CACHE)} entries)")

    # Print summary
    for line in output[:30]:
        print(line)


if __name__ == '__main__':
    main()
