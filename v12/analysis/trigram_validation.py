#!/usr/bin/env python3
"""
COUP 4: Trigram validation.
Decode VMS with sectorial reranker and measure trigram matches against corpora.
This is the verdict: do decoded word sequences exist in real medical Latin?
"""
import sys, os, re, json
from collections import Counter, defaultdict
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from v12.config import Config
from v12.pipeline import VoynichPipeline
from v12.loaders.transcription import parse_folio, list_folios
from v12.stages.reranker import SectorialReranker
from v12.models.sectorial_lm import lemmatize_collatinus, SectorialLM

SECTION_NAMES = {
    'H': 'Herbal', 'P': 'Pharma', 'B': 'Balnea', 'S': 'Recipes',
    'A': 'Astro', 'Z': 'Zodiac', 'C': 'Cosmo', 'T': 'Text',
}

GENERIC_LEMMAS = {'et', 'in', 'cum', 'per', 'ex', 'de', 'ad', 'is', 'qui',
                   'hic', 'sum', 'non', 'que', 'vel', 'aut', 'si', 'sed'}


def main():
    config = Config()
    pipeline = VoynichPipeline(config)
    pipeline.load()

    # Load reranker
    lm_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
    reranker = SectorialReranker(lm_dir)

    # Load corpus trigrams for validation
    print('Building corpus trigrams for validation...')
    corpus_trigrams = {}
    for name, path in [('herbal', 'CORPORA_FINAL/corpus_herbal.txt'),
                       ('pharma', 'CORPORA_FINAL/corpus_pharma.txt'),
                       ('balnea', 'CORPORA_FINAL/corpus_balnea.txt')]:
        if not os.path.exists(path):
            continue
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read().lower()
        words = [w for w in re.findall(r'[a-z]+', text) if len(w) >= 2]

        # Lemmatize corpus words (use cache for speed)
        cache = {}
        lemmas = []
        for w in words:
            lemmas.append(lemmatize_collatinus(w, cache))

        # Build trigrams
        tris = Counter()
        for i in range(len(lemmas) - 2):
            tris[(lemmas[i], lemmas[i+1], lemmas[i+2])] += 1
        corpus_trigrams[name] = tris
        print(f'  {name}: {len(tris)} unique trigrams from {len(words)} words')

    # Select test folios across sections
    test_folios = {
        'H': ['f9v', 'f15r', 'f34r'],
        'P': ['f88r', 'f99r'],
        'S': ['f103r', 'f108r', 'f111r'],
        'B': ['f75r', 'f76r'],
        'Z': ['f72r'],
    }

    section_lm_map = {'H': 'herbal', 'P': 'pharma', 'S': 'pharma',
                      'B': 'balnea', 'Z': 'pharma'}

    print('\n' + '=' * 120)
    print('TRIGRAM VALIDATION: decoded VMS vs sectorial corpora')
    print('=' * 120)

    total_matches = 0
    total_specific_matches = 0
    all_match_details = []

    for sec, fids in test_folios.items():
        lm_name = section_lm_map.get(sec, 'pharma')
        tris = corpus_trigrams.get(lm_name)
        if not tris:
            continue

        for fid in fids:
            lines, _ = parse_folio('data/transcriptions/ZL.txt', fid)
            if not lines:
                for s in ['1', '2']:
                    lines, _ = parse_folio('data/transcriptions/ZL.txt', fid + s)
                    if lines:
                        fid = fid + s
                        break
            if not lines:
                continue

            decoded = pipeline.decode_folio(lines)

            # Apply reranker
            for lnum in decoded:
                decoded[lnum] = reranker.rerank_line(decoded[lnum], sec)

            # Build lemmatized sequences per line and check trigrams
            folio_matches = 0
            folio_specific = 0

            for lnum in sorted(decoded.keys()):
                words = decoded[lnum]
                # Lemmatize decoded words
                lemmas = []
                originals = []
                for dw in words:
                    main_w = dw.latin.split()[0] if dw.latin else ''
                    lemma = lemmatize_collatinus(main_w.lower(), reranker._lemma_cache)
                    lemmas.append(lemma)
                    originals.append(dw.latin)

                # Check trigrams
                for i in range(len(lemmas) - 2):
                    tri = (lemmas[i], lemmas[i+1], lemmas[i+2])
                    if tri in tris:
                        total_matches += 1
                        folio_matches += 1
                        # Is it specific (not all generic)?
                        non_generic = sum(1 for l in tri if l not in GENERIC_LEMMAS)
                        if non_generic >= 2:
                            total_specific_matches += 1
                            folio_specific += 1
                            orig_tri = (originals[i], originals[i+1], originals[i+2])
                            all_match_details.append((fid, lnum, tri, orig_tri, tris[tri], non_generic))

            if folio_matches > 0:
                print(f'  {fid:8s} [{sec}]: {folio_matches} trigram matches ({folio_specific} specific)')

    print(f'\n{"="*80}')
    print(f'TOTAL TRIGRAM MATCHES: {total_matches}')
    print(f'SPECIFIC MATCHES (>=2 non-generic lemmas): {total_specific_matches}')
    print(f'{"="*80}')

    if all_match_details:
        print('\nDETAIL: Specific trigram matches')
        print(f'{"FOLIO":8s} {"L":>3s} {"LEMMA TRIGRAM":45s} {"ORIGINAL":45s} {"CORPUS#":>7s} {"SPEC":>4s}')
        print('-' * 120)
        # Sort by corpus frequency (most significant first)
        all_match_details.sort(key=lambda x: -x[4])
        seen = set()
        for fid, lnum, tri, orig_tri, count, spec in all_match_details[:100]:
            tri_str = ' '.join(tri)
            if tri_str in seen:
                continue
            seen.add(tri_str)
            orig_str = ' '.join(orig_tri)
            print(f'{fid:8s} {lnum:3d} {tri_str:45s} {orig_str:45s} {count:7d} {"*"*spec}')
    else:
        print('\nNO SPECIFIC TRIGRAM MATCHES FOUND')


if __name__ == '__main__':
    main()
