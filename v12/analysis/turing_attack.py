#!/usr/bin/env python3
"""
TURING ATTACK: Find ONE phrase in the Voynich that matches a known medieval text.

Strategy:
1. Find all lines containing 'recipe' (r) or starting recipe patterns
2. For each, generate multiple decode paths (top-5 per word)
3. Lemmatize via Collatinus
4. Search every 3/4/5-gram in the sectorial corpora
5. ONE match of 4+ non-generic words = the judge of peace
"""
import sys, os, re, math, json
from collections import Counter, defaultdict
from itertools import product
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from v12.config import Config
from v12.pipeline import VoynichPipeline
from v12.loaders.transcription import parse_folio, list_folios
from v12.models.sectorial_lm import lemmatize_collatinus, SectorialLM

GENERIC_LEMMAS = {'et', 'in', 'cum_2', 'per', 'ex', 'de', 'ad', 'is', 'qui_2',
                   'hic', 'sum', 'non', 'que', 'vel', 'aut', 'si', 'sed', 'ut',
                   'idem', 'ille', 'edo', 'do', 'fio', 'habeo', 'dico_2'}

SECTION_LM = {'H': 'herbal', 'P': 'pharma', 'S': 'pharma', 'B': 'balnea',
              'Z': 'pharma', 'C': 'pharma', 'A': 'herbal', 'T': 'pharma'}


def build_corpus_ngrams(corpus_path, cache, max_n=5):
    """Build n-gram indices from a corpus (lemmatized)."""
    with open(corpus_path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read().lower()
    words = [w for w in re.findall(r'[a-z]+', text) if 2 <= len(w) <= 25]

    print(f'  Lemmatizing {len(words)} words...', file=sys.stderr)
    lemmas = []
    for i, w in enumerate(words):
        if i % 20000 == 0 and i > 0:
            print(f'    {i}/{len(words)}...', file=sys.stderr)
        lemmas.append(lemmatize_collatinus(w, cache))

    ngrams = {}
    for n in range(3, max_n + 1):
        ng = Counter()
        for i in range(len(lemmas) - n + 1):
            gram = tuple(lemmas[i:i+n])
            ng[gram] += 1
        ngrams[n] = ng
        print(f'  {n}-grams: {len(ng)} unique', file=sys.stderr)

    return ngrams, lemmas


def beam_decode_line(pipeline, eva_words, beam_width=30):
    """Decode a line keeping top candidates per word, return beam of sequences."""
    # Get top-5 candidates per position
    candidates_per_pos = []
    for eva in eva_words:
        result = pipeline.decode_word(eva)
        cands = [result.latin]
        if result.alternatives:
            cands.extend([a[0] for a in result.alternatives[:4]])
        # Deduplicate
        seen = set()
        unique = []
        for c in cands:
            if c.lower() not in seen:
                seen.add(c.lower())
                unique.append(c)
        candidates_per_pos.append(unique[:5])

    # Beam search: generate top sequences
    # Start with single-word beams
    if not candidates_per_pos:
        return []

    beam = [(0.0, [c]) for c in candidates_per_pos[0]]

    for pos in range(1, len(candidates_per_pos)):
        new_beam = []
        for score, seq in beam:
            for cand in candidates_per_pos[pos]:
                new_beam.append((score, seq + [cand]))
        # Prune to beam_width (just keep first N for now — simple)
        new_beam = new_beam[:beam_width]
        beam = new_beam

    return [seq for _, seq in beam]


def main():
    config = Config()
    pipeline = VoynichPipeline(config)
    pipeline.load()

    cache = {}  # shared lemma cache

    # Build corpus ngrams
    print('=== BUILDING CORPUS N-GRAMS (lemmatized) ===')
    corpus_ngrams = {}
    for name, path in [('pharma', 'CORPORA_FINAL/corpus_pharma.txt'),
                       ('herbal', 'CORPORA_FINAL/corpus_herbal.txt'),
                       ('balnea', 'CORPORA_FINAL/corpus_balnea.txt')]:
        print(f'\n  {name}:')
        if os.path.exists(path):
            corpus_ngrams[name], _ = build_corpus_ngrams(path, cache, max_n=5)

    # Find ALL recipe lines in VMS
    print('\n=== SCANNING VMS FOR RECIPE LINES ===')
    folios = list_folios('data/transcriptions/ZL.txt')

    recipe_lines = []  # (folio, section, line_num, eva_words)

    for fid, sec in folios:
        lines, _ = parse_folio('data/transcriptions/ZL.txt', fid)
        if not lines:
            continue
        for lnum, words in lines.items():
            # Lines containing 'r' (recipe logogram) or starting with recipe patterns
            has_recipe = 'r' in words
            # Also lines with coque/misce patterns (recipe instructions)
            has_instruction = any(w in ('qoky', 'qok', 'm') for w in words)
            # Also lines with known ingredient logograms
            has_ingredient = any(w in ('oteeos', 'shkaiin', 'opcheol') for w in words)

            if has_recipe or has_ingredient:
                recipe_lines.append((fid, sec, lnum, words))

    print(f'  Found {len(recipe_lines)} recipe-like lines across {len(set(r[0] for r in recipe_lines))} folios')

    # For each recipe line: decode, lemmatize, search in corpora
    print('\n=== TURING ATTACK: SEARCHING FOR CRIB MATCHES ===')
    print('=' * 120)

    all_matches = []

    for idx, (fid, sec, lnum, eva_words) in enumerate(recipe_lines):
        if idx % 20 == 0:
            print(f'  Processing {idx}/{len(recipe_lines)}...', file=sys.stderr)

        # Get the right corpus
        lm_name = SECTION_LM.get(sec, 'pharma')
        if lm_name not in corpus_ngrams:
            continue

        # Beam decode this line
        sequences = beam_decode_line(pipeline, eva_words, beam_width=20)

        for seq in sequences:
            # Lemmatize the sequence
            lemmas = []
            for word in seq:
                main_w = word.split()[0].lower() if word else ''
                lemma = lemmatize_collatinus(main_w, cache)
                lemmas.append(lemma)

            # Search n-grams (3, 4, 5) in corpus
            for n in [5, 4, 3]:
                if n not in corpus_ngrams[lm_name]:
                    continue
                ng_index = corpus_ngrams[lm_name][n]

                for i in range(len(lemmas) - n + 1):
                    gram = tuple(lemmas[i:i+n])
                    if gram in ng_index:
                        non_generic = sum(1 for l in gram if l not in GENERIC_LEMMAS)
                        corpus_count = ng_index[gram]
                        orig_words = seq[i:i+n]

                        all_matches.append({
                            'folio': fid,
                            'section': sec,
                            'line': lnum,
                            'n': n,
                            'lemma_gram': gram,
                            'decoded_words': orig_words,
                            'corpus_count': corpus_count,
                            'non_generic': non_generic,
                            'lm': lm_name,
                        })

    # Sort by specificity then by n-gram length then by corpus count
    all_matches.sort(key=lambda m: (-m['non_generic'], -m['n'], -m['corpus_count']))

    # Deduplicate
    seen = set()
    unique_matches = []
    for m in all_matches:
        key = ' '.join(m['lemma_gram'])
        if key not in seen:
            seen.add(key)
            unique_matches.append(m)

    # Report
    print(f'\n{"="*120}')
    print(f'RESULTS: {len(unique_matches)} unique n-gram matches found')

    specific = [m for m in unique_matches if m['non_generic'] >= 2]
    very_specific = [m for m in unique_matches if m['non_generic'] >= 3]

    print(f'  Specific (>=2 non-generic): {len(specific)}')
    print(f'  Very specific (>=3 non-generic): {len(very_specific)}')
    print(f'{"="*120}')

    if unique_matches:
        print(f'\n{"FOLIO":8s} {"SEC":4s} {"L":>3s} {"N":>2s} {"SPEC":>4s} {"#":>5s} {"LEMMA N-GRAM":50s} {"DECODED":50s}')
        print('-' * 130)

        for m in unique_matches[:80]:
            gram_str = ' '.join(m['lemma_gram'])
            dec_str = ' | '.join(m['decoded_words'])[:50]
            spec_tag = '*' * m['non_generic']
            print(f'{m["folio"]:8s} {m["section"]:4s} {m["line"]:3d} {m["n"]:2d} {spec_tag:>4s} {m["corpus_count"]:5d} {gram_str:50s} {dec_str:50s}')

    # Save results
    output_path = 'v12/output/TURING_ATTACK_RESULTS.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump([{**m, 'lemma_gram': list(m['lemma_gram'])} for m in unique_matches[:200]], f, indent=2, ensure_ascii=False)
    print(f'\nResults saved to {output_path}')


if __name__ == '__main__':
    main()
