#!/usr/bin/env python3
"""
AXE A + AXE C: Regimen Sanitatis structural mapping + trigram crib search.
1. Parse Regimen Sanitatis into thematic chapters
2. Build vocabulary profiles per chapter
3. Correlate VMS section profiles with Regimen chapters
4. Extract trigrams from Regimen and search in decoded VMS
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

# Thematic vocabulary clusters derived from Regimen Sanitatis structure
# These are the KEY WORDS for each major theme of the Regimen
REGIMEN_THEMES = {
    'DIETA': {
        'name': 'Diet & Food',
        'keywords': ['cibus', 'cibo', 'cibum', 'edere', 'ede', 'potus', 'bibere',
                     'vinum', 'uinum', 'panis', 'carnes', 'lac', 'caseus',
                     'piscis', 'ovum', 'fructus', 'oleum', 'mel', 'sal',
                     'digestio', 'stomachus', 'coquere', 'coque', 'coquendo'],
    },
    'HERBAE': {
        'name': 'Herbs & Simples',
        'keywords': ['herba', 'radix', 'folia', 'semen', 'cortex', 'succus',
                     'flos', 'planta', 'alo', 'cicura', 'salvia', 'mentha',
                     'origanum', 'ruta', 'absinthium', 'aperiens', 'eliciens',
                     'purgare', 'mundare', 'libra', 'drachma', 'equaliter'],
    },
    'BALNEA': {
        'name': 'Baths & Hygiene',
        'keywords': ['balneum', 'balnea', 'lavare', 'aqua', 'aquam', 'calor',
                     'sudor', 'fovere', 'colligens', 'renes', 'rens', 'lotio',
                     'frigidus', 'calidus', 'temperatus', 'cutis', 'corpus'],
    },
    'PHARMACIA': {
        'name': 'Compound Medicine',
        'keywords': ['recipe', 'misce', 'coque', 'tere', 'cola', 'adde',
                     'electuarium', 'pilula', 'unguentum', 'emplastrum',
                     'sirupus', 'hiera', 'aloes', 'asarum', 'crocus',
                     'coquendo', 'cooperiens', 'aratura'],
    },
    'ASTROLOGIA': {
        'name': 'Astrology & Calendar',
        'keywords': ['luna', 'sol', 'stella', 'signum', 'aries', 'taurus',
                     'dies', 'hora', 'tempus', 'aloes', 'purgare',
                     'coelum', 'coelas', 'coelis', 'sidus'],
    },
    'MORBI': {
        'name': 'Diseases & Pain',
        'keywords': ['dolor', 'dolorem', 'morbus', 'febris', 'tumor',
                     'apostema', 'ulcus', 'vulnus', 'iecur', 'caput',
                     'pectus', 'ilia', 'renes', 'dura', 'indura',
                     'compellens', 'perciens'],
    },
    'HUMORES': {
        'name': 'Humoral Theory',
        'keywords': ['sanguis', 'colera', 'melancolica', 'flegma',
                     'calidus', 'frigidus', 'humidus', 'siccus',
                     'dura', 'cura', 'curam', 'purgare', 'aperiens'],
    },
}


def load_regimen_words(path):
    """Load and clean Regimen Sanitatis text."""
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read().lower()
    # Clean OCR artifacts
    text = re.sub(r'[^a-z\s]', ' ', text)
    words = [w for w in text.split() if len(w) >= 3]
    return words


def decode_all_vms(pipeline):
    """Decode entire VMS and return per-section word lists."""
    folios = list_folios('data/transcriptions/ZL.txt')
    section_words = defaultdict(list)  # section -> [decoded_latin_words]
    section_folios = defaultdict(list)

    for idx, (fid, sec) in enumerate(folios):
        if idx % 30 == 0:
            print(f'  Decoding {idx}/{len(folios)}...', file=sys.stderr)

        lines, _ = parse_folio('data/transcriptions/ZL.txt', fid)
        if not lines:
            continue

        decoded = pipeline.decode_folio(lines)
        section_folios[sec].append(fid)

        for lnum, words in decoded.items():
            for dw in words:
                if dw.confidence in ('CONFIRMED', 'HIGH', 'MEDIUM'):
                    for w in dw.latin.lower().split():
                        clean = re.sub(r'[^a-z]', '', w)
                        if len(clean) >= 2:
                            section_words[sec].append(clean)

    return section_words, section_folios


def build_trigrams(words):
    """Build trigram frequency from a word list."""
    trigrams = Counter()
    for i in range(len(words) - 2):
        tri = (words[i], words[i+1], words[i+2])
        trigrams[tri] += 1
    return trigrams


def main():
    config = Config()
    pipeline = VoynichPipeline(config)
    pipeline.load()

    # ========================================
    # AXE A: Regimen thematic correlation
    # ========================================
    print('=' * 120)
    print('AXE A: REGIMEN SANITATIS THEMATIC MAPPING')
    print('=' * 120)

    # Load Regimen
    regimen_path = 'Cowork/nlm_nlmuid-9414702-bk.txt'
    regimen_words = load_regimen_words(regimen_path)
    regimen_freq = Counter(regimen_words)
    print(f'Regimen Sanitatis: {len(regimen_words)} words, {len(regimen_freq)} unique')

    # Also load Flos Medicinae and Ortus Sanitatis for extra coverage
    extra_sources = {}
    for name, path in [('Flos', 'Cowork/Flos medicinae Scholae Salerni.txt'),
                       ('Ortus', 'Cowork/Ortus sanitatis.txt')]:
        if os.path.exists(path):
            words = load_regimen_words(path)
            extra_sources[name] = Counter(words)
            print(f'{name}: {len(words)} words')

    # Decode VMS
    print('\nDecoding VMS...')
    vms_sections, vms_folios = decode_all_vms(pipeline)

    # Build VMS section profiles
    vms_profiles = {}
    for sec, words in vms_sections.items():
        vms_profiles[sec] = Counter(words)

    # Correlate each VMS section with each Regimen theme
    print('\n--- CORRELATION MATRIX: VMS Section x Regimen Theme ---')

    themes = list(REGIMEN_THEMES.keys())
    sections = sorted(vms_profiles.keys())

    header = f'{"VMS Section":15s}' + ''.join(f' {t:>12s}' for t in themes)
    print(header)
    print('-' * len(header))

    correlations = {}  # (section, theme) -> score

    for sec in sections:
        profile = vms_profiles[sec]
        total_words = sum(profile.values())
        row = f'{sec} ({SECTION_NAMES.get(sec,"?"):8s})'

        best_theme = None
        best_score = 0

        for theme_key in themes:
            theme = REGIMEN_THEMES[theme_key]
            keywords = theme['keywords']

            # Count how many theme keywords appear in this section
            hits = 0
            for kw in keywords:
                hits += profile.get(kw, 0)

            # Normalize by section size
            score = hits / max(total_words, 1) * 1000  # per 1000 words

            correlations[(sec, theme_key)] = score

            if score > best_score:
                best_score = score
                best_theme = theme_key

            row += f' {score:12.1f}'

        row += f'  BEST: {best_theme}'
        print(row)

    # Show best match per section
    print('\n--- BEST MATCHES ---')
    for sec in sections:
        scores = [(t, correlations[(sec, t)]) for t in themes]
        scores.sort(key=lambda x: -x[1])
        top1, s1 = scores[0]
        top2, s2 = scores[1]
        name = SECTION_NAMES.get(sec, sec)
        ratio = s1 / s2 if s2 > 0 else 999
        strength = 'STRONG' if ratio > 1.5 else 'moderate' if ratio > 1.2 else 'weak'
        print(f'  {sec} ({name:10s}): {top1:12s} ({s1:.1f}/1000) >> {top2:12s} ({s2:.1f}/1000)  ratio={ratio:.1f} [{strength}]')

    # ========================================
    # AXE C: Trigram crib search
    # ========================================
    print('\n' + '=' * 120)
    print('AXE C: TRIGRAM CRIB SEARCH - Regimen phrases in VMS')
    print('=' * 120)

    # Build VMS trigrams per section
    vms_trigrams = {}
    for sec, words in vms_sections.items():
        vms_trigrams[sec] = build_trigrams(words)

    # Build Regimen trigrams (filter to medical/meaningful ones)
    regimen_trigrams = build_trigrams(regimen_words)

    # Generic words to exclude from trigram matching
    GENERIC = {'et', 'in', 'cum', 'de', 'per', 'ex', 'ad', 'est', 'non',
               'que', 'qui', 'quod', 'quia', 'sed', 'vel', 'aut', 'si',
               'hoc', 'hic', 'ille', 'eius', 'eo', 'ei', 'eum', 'eam'}

    # Find Regimen trigrams that also appear in VMS
    print('\nSearching for Regimen trigrams in decoded VMS...')
    matches = []

    for tri, reg_count in regimen_trigrams.most_common(500):
        w1, w2, w3 = tri
        # Skip if all 3 words are generic
        non_generic = sum(1 for w in tri if w not in GENERIC and len(w) >= 3)
        if non_generic < 1:
            continue

        for sec, sec_tris in vms_trigrams.items():
            vms_count = sec_tris.get(tri, 0)
            if vms_count > 0:
                matches.append((tri, reg_count, sec, vms_count, non_generic))

    # Sort by specificity (non-generic count) then by VMS frequency
    matches.sort(key=lambda x: (-x[4], -x[3]))

    print(f'\nFound {len(matches)} trigram matches')
    print()
    print(f'{"TRIGRAM":40s} {"REG":>4s} {"VMS_SEC":>10s} {"VMS#":>5s} {"SPEC":>4s}')
    print('-' * 75)

    seen = set()
    shown = 0
    for tri, reg_count, sec, vms_count, specificity in matches:
        tri_str = ' '.join(tri)
        if tri_str in seen:
            continue
        seen.add(tri_str)
        sec_name = SECTION_NAMES.get(sec, sec)
        spec_tag = '*' * specificity
        print(f'  {tri_str:38s} {reg_count:4d} {sec_name:>10s} {vms_count:5d} {spec_tag}')
        shown += 1
        if shown >= 60:
            break


if __name__ == '__main__':
    main()
