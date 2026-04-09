#!/usr/bin/env python3
"""
AXE B: Sentinel word analysis.
Find rare, specific decoded words and analyze their distribution across
manuscript sections to confirm thematic mapping.
"""
import sys, os, re
from collections import Counter, defaultdict
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from v12.config import Config
from v12.pipeline import VoynichPipeline
from v12.loaders.transcription import parse_folio, list_folios

SECTION_NAMES = {
    'H': 'Herbal', 'P': 'Pharma', 'B': 'Balnea', 'S': 'Recipes',
    'A': 'Astro', 'Z': 'Zodiac', 'C': 'Cosmo', 'T': 'Text',
}

# Sentinel words: rare enough to be meaningful, specific enough to anchor
SENTINELS = [
    # From full survey reading
    'uinum', 'vinum',      # wine (vehicle for remedies)
    'rens', 'renes',       # kidneys (balnea target)
    'aloes',               # aloe (key ingredient)
    'compellens',          # forcing (medical term)
    'colligens',           # gathering (preparation)
    'cooperiens',          # covering (preparation)
    'aperiens',            # opening/laxative
    'eliciens',            # extracting
    'coquendo',            # by cooking
    'equaliter',           # equally (dosage)
    'cicura',              # chicory (plant)
    'dolor', 'dolorem',    # pain
    'iecur',               # liver
    'coquentes',           # cooking (participle)
    'libra',               # pound (weight)
    'coelas', 'coelis',    # heavens (cosmo?)
    'aratura',             # preparation
    'indura',              # to harden
    'dura',                # hard/hardness
    'recipe',              # take! (recipe opener)
]


def main():
    config = Config()
    pipeline = VoynichPipeline(config)
    pipeline.load()

    folios = list_folios('data/transcriptions/ZL.txt')

    # Decode ALL folios and track sentinel distribution
    sentinel_dist = defaultdict(lambda: defaultdict(int))  # word -> section -> count
    sentinel_folios = defaultdict(lambda: defaultdict(list))  # word -> section -> [folio_ids]
    section_word_totals = Counter()  # section -> total words

    total_folios = len(folios)
    for idx, (fid, sec) in enumerate(folios):
        if idx % 20 == 0:
            print(f'  Decoding {idx}/{total_folios}...', file=sys.stderr)

        lines, _ = parse_folio('data/transcriptions/ZL.txt', fid)
        if not lines:
            continue

        decoded = pipeline.decode_folio(lines)
        n_words = sum(len(ws) for ws in decoded.values())
        section_word_totals[sec] += n_words

        for lnum, words in decoded.items():
            for dw in words:
                lat = dw.latin.lower()
                for sentinel in SENTINELS:
                    if sentinel in lat:
                        sentinel_dist[sentinel][sec] += 1
                        if fid not in sentinel_folios[sentinel][sec]:
                            sentinel_folios[sentinel][sec].append(fid)

    # Report
    print('=' * 120)
    print('AXE B: SENTINEL WORD DISTRIBUTION ACROSS MANUSCRIPT SECTIONS')
    print('=' * 120)
    print()

    # Section totals
    print('Section word totals:')
    for sec in sorted(section_word_totals.keys()):
        name = SECTION_NAMES.get(sec, sec)
        print(f'  {sec} ({name:10s}): {section_word_totals[sec]:6d} words')
    print()

    # Sentinel distribution matrix
    sections = sorted(section_word_totals.keys())
    header = f'{"SENTINEL":15s}' + ''.join(f' {SECTION_NAMES.get(s,s):>10s}' for s in sections) + '  TOTAL  CONCENTRATED?'
    print(header)
    print('-' * len(header))

    for sentinel in SENTINELS:
        if sentinel not in sentinel_dist:
            continue
        dist = sentinel_dist[sentinel]
        total = sum(dist.values())
        if total == 0:
            continue

        # Concentration: what fraction is in the top section?
        top_sec = max(dist, key=dist.get)
        concentration = dist[top_sec] / total

        row = f'{sentinel:15s}'
        for sec in sections:
            count = dist.get(sec, 0)
            if count > 0:
                # Normalize per 1000 words
                rate = count * 1000 / max(section_word_totals[sec], 1)
                row += f' {count:5d}({rate:4.1f})'
            else:
                row += f'          -'
        row += f'  {total:5d}'

        if concentration > 0.6 and total >= 3:
            row += f'  ** {SECTION_NAMES.get(top_sec, top_sec)} ({concentration:.0%})'
        elif concentration > 0.4:
            row += f'  ~ {SECTION_NAMES.get(top_sec, top_sec)} ({concentration:.0%})'

        print(row)

    # Detail for key sentinels
    print()
    print('=' * 80)
    print('DETAIL: Key sentinel words')
    print('=' * 80)
    for sentinel in ['uinum', 'rens', 'aloes', 'compellens', 'aperiens', 'coelas',
                     'colligens', 'dolor', 'iecur', 'recipe', 'coquendo', 'dura']:
        if sentinel not in sentinel_dist:
            continue
        dist = sentinel_dist[sentinel]
        total = sum(dist.values())
        if total == 0:
            continue
        print(f'\n  {sentinel.upper()} ({total} total):')
        for sec in sections:
            if sec in dist:
                folio_list = sentinel_folios[sentinel][sec]
                rate = dist[sec] * 1000 / max(section_word_totals[sec], 1)
                print(f'    {SECTION_NAMES.get(sec,sec):10s}: {dist[sec]:3d} occ ({rate:.1f}/1000w) folios: {", ".join(folio_list[:8])}')


if __name__ == '__main__':
    main()
