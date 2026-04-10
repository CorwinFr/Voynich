#!/usr/bin/env python3
"""
9A Corpus Cleaner — Medieval Medical Latin
Cleans OCR text from Archive.org and other sources, isolates Latin from
Italian/Dutch/English/German commentary, and assembles the final corpus.
"""

import re
import os
import json
from pathlib import Path
from collections import Counter

RAW_DIR = Path(__file__).parent
OUT_DIR = RAW_DIR.parent  # data/
CLEAN_DIR = RAW_DIR / "cleaned"
CLEAN_DIR.mkdir(exist_ok=True)

# ── Language detection word lists ──

LATIN_FUNCTION_WORDS = {
    'et', 'in', 'cum', 'per', 'ad', 'est', 'sunt', 'quod', 'sed', 'non',
    'de', 'ut', 'si', 'ex', 'ab', 'vel', 'aut', 'quae', 'qui', 'esse',
    'hoc', 'hic', 'enim', 'nam', 'nec', 'quia', 'autem', 'tamen', 'sic',
    'item', 'ideo', 'idem', 'eius', 'quo', 'sive', 'atque', 'quam',
    'etiam', 'ille', 'illa', 'illud', 'ergo', 'ita', 'vero', 'ante',
    'post', 'inter', 'super', 'sub', 'pro', 'contra', 'sine', 'circa',
    'apud', 'secundum', 'propter', 'omnibus', 'omnis', 'omnia',
    'potest', 'debet', 'habet', 'facit', 'dicit', 'fuit', 'sit',
    'fiat', 'fit', 'eum', 'eam', 'eos', 'qua', 'quid',
    # Medical Latin high-freq
    'recipe', 'virtus', 'calida', 'frigida', 'humida', 'sicca',
    'herba', 'radix', 'folium', 'folia', 'semen', 'aqua', 'vinum',
    'oleum', 'mel', 'pulvis', 'decoctum', 'stomachum', 'corpus',
    'dolor', 'febris', 'morbus', 'sanguis', 'calidum', 'frigidum',
    'humidum', 'siccum', 'medicina', 'medicus', 'natura', 'valet',
}

ITALIAN_FUNCTION_WORDS = {
    'il', 'la', 'di', 'che', 'del', 'nel', 'con', 'una', 'un', 'le',
    'lo', 'gli', 'dei', 'della', 'delle', 'dello', 'degli', 'alla',
    'allo', 'alle', 'dal', 'dalla', 'dalle', 'dallo', 'dagli',
    'sul', 'sulla', 'sulle', 'sullo', 'questo', 'questa', 'questi',
    'quello', 'quella', 'quelli', 'quelle', 'anche', 'sono', 'era',
    'essere', 'stato', 'stata', 'come', 'perche', 'quando', 'dove',
    'chi', 'cui', 'suo', 'sua', 'suoi', 'loro', 'ogni', 'fra',
    'tra', 'ancora', 'dopo', 'prima', 'sempre', 'molto', 'poco',
    'tutto', 'tutti', 'noi', 'voi', 'hanno', 'aveva', 'fatto',
    'parte', 'tempo', 'stesso', 'modo', 'altro', 'altri', 'quale',
    'quali', 'pero', 'cioe', 'dunque', 'quindi', 'mentre', 'perch',
    'percbe', 'poiche', 'giacche', 'senza', 'verso', 'sotto', 'sopra',
    'fuori', 'dentro', 'accanto', 'insieme', 'cosa', 'cose', 'anno',
    'anni', 'secolo', 'secoli', 'storia', 'capitolo',
    # OCR variants common in De Renzi
    'alia', 'delia', 'nella', 'dalle',
}

DUTCH_FUNCTION_WORDS = {
    'de', 'het', 'een', 'van', 'en', 'dat', 'die', 'bij', 'voor',
    'met', 'niet', 'ook', 'als', 'aan', 'maar', 'nog', 'wel', 'dan',
    'wat', 'naar', 'uit', 'tot', 'hun', 'hem', 'zij', 'haar', 'ons',
    'werd', 'worden', 'heeft', 'hebben', 'zijn', 'was', 'waren',
    'deze', 'dit', 'door', 'kan', 'zou', 'meer', 'veel', 'geen',
    'onder', 'over', 'tussen', 'omdat', 'wanneer', 'echter', 'reeds',
    'volgens', 'waarin', 'waarvan', 'waarbij', 'waardoor',
    'men', 'zich', 'hier', 'daar', 'waar', 'hoe', 'wie',
    'andere', 'anderen', 'eerste', 'nieuwe', 'jaar', 'jaren',
    'zooals', 'doch', 'immers', 'behalve', 'slechts', 'thans',
}

ENGLISH_FUNCTION_WORDS = {
    'the', 'of', 'and', 'to', 'in', 'is', 'that', 'it', 'for', 'was',
    'on', 'are', 'as', 'with', 'his', 'they', 'be', 'at', 'one',
    'have', 'this', 'from', 'or', 'had', 'by', 'but', 'not', 'what',
    'all', 'were', 'we', 'when', 'your', 'can', 'said', 'there',
    'each', 'which', 'their', 'will', 'other', 'about', 'many',
    'then', 'them', 'these', 'some', 'her', 'would', 'been', 'has',
    'its', 'who', 'did', 'than', 'been', 'could', 'may', 'after',
    'should', 'into', 'such', 'only', 'also',
    # Archive.org boilerplate
    'book', 'library', 'copyright', 'digital', 'google', 'page',
    'project', 'public', 'domain', 'preserved', 'scanned',
}

GERMAN_FUNCTION_WORDS = {
    'der', 'die', 'das', 'und', 'ist', 'von', 'zu', 'den', 'mit',
    'auf', 'fur', 'ein', 'eine', 'dem', 'des', 'sich', 'nicht',
    'auch', 'als', 'noch', 'nach', 'aber', 'bei', 'uber', 'wie',
    'nur', 'oder', 'sehr', 'kann', 'hat', 'sind', 'wird', 'war',
    'aus', 'wenn', 'man', 'ich', 'schon', 'durch', 'dieser',
    'diese', 'dieses', 'einem', 'einer', 'worden', 'haben',
    'zwischen', 'welche', 'welcher', 'welches',
}


def tokenize(text):
    """Simple word tokenizer."""
    return re.findall(r'[a-zA-Zàáâãäåæçèéêëìíîïðñòóôõöùúûüýþÿ]+', text.lower())


def detect_language(text, min_words=5):
    """
    Score a text block for language dominance.
    Returns (lang, confidence) where lang is 'latin', 'italian', 'dutch',
    'english', 'german', or 'noise'.
    """
    words = tokenize(text)
    if len(words) < min_words:
        return 'noise', 0.0

    word_set = set(words)
    total = len(words)

    scores = {
        'latin': len([w for w in words if w in LATIN_FUNCTION_WORDS]) / total,
        'italian': len([w for w in words if w in ITALIAN_FUNCTION_WORDS]) / total,
        'dutch': len([w for w in words if w in DUTCH_FUNCTION_WORDS]) / total,
        'english': len([w for w in words if w in ENGLISH_FUNCTION_WORDS]) / total,
        'german': len([w for w in words if w in GERMAN_FUNCTION_WORDS]) / total,
    }

    # Disambiguate: some words overlap (de, in, etc.)
    # Boost Latin if medical terms present
    medical_terms = {'recipe', 'herba', 'radix', 'calida', 'frigida', 'humida',
                     'sicca', 'stomachum', 'decoctum', 'pulvis', 'febribus',
                     'virtus', 'sanguis', 'medicina', 'morbus', 'dolor'}
    if word_set & medical_terms:
        scores['latin'] += 0.05

    # Latin endings boost
    latin_endings = sum(1 for w in words if len(w) > 3 and
                       w.endswith(('tur', 'ibus', 'orum', 'arum', 'ium',
                                   'atis', 'onis', 'alis', 'aris', 'inem',
                                   'unt', 'ant', 'ent', 'ere', 'ire')))
    scores['latin'] += (latin_endings / total) * 0.3

    best_lang = max(scores, key=scores.get)
    best_score = scores[best_lang]

    if best_score < 0.05:
        return 'noise', best_score

    return best_lang, best_score


def clean_ocr_artifacts(text):
    """Remove common OCR artifacts."""
    # Remove page numbers (standalone numbers on a line)
    text = re.sub(r'^\s*\d{1,4}\s*$', '', text, flags=re.MULTILINE)
    # Remove Roman numeral page headers
    text = re.sub(r'^\s*[IVXLCDM]{1,8}\s*$', '', text, flags=re.MULTILINE)
    # Remove common Archive.org boilerplate
    boilerplate_patterns = [
        r'(?i)this is a digital copy.*?(?=\n\n)',
        r'(?i)generated (?:by|at|on).*?(?=\n)',
        r'(?i)digitized by google.*?(?=\n)',
        r'(?i)original from.*?(?=\n)',
        r'(?i)public domain.*?(?=\n)',
        r'(?i)uploaded by.*?(?=\n)',
        r'(?i)internet archive.*?(?=\n)',
        r'(?i)book contributor.*?(?=\n)',
        r'(?i)copyright.*?(?=\n)',
    ]
    for pat in boilerplate_patterns:
        text = re.sub(pat, '', text)

    # Remove lines that are mostly non-alpha (OCR noise)
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            cleaned_lines.append('')
            continue
        alpha_chars = sum(1 for c in stripped if c.isalpha())
        if len(stripped) > 0 and alpha_chars / len(stripped) < 0.4:
            continue  # Skip noisy lines
        cleaned_lines.append(line)

    text = '\n'.join(cleaned_lines)

    # Collapse multiple blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Remove OCR-typical artifacts
    text = re.sub(r'[|{}\[\]@#$%^&*_<>~`]', '', text)
    # Fix common OCR substitutions in Latin
    text = re.sub(r'\bqu\s*;', 'que', text)  # q; -> que
    text = re.sub(r'\bp\s*;', 'per', text)   # p; -> per

    return text.strip()


def split_into_paragraphs(text):
    """Split text into paragraph-like blocks."""
    # Split on double newlines or significant gaps
    blocks = re.split(r'\n\s*\n', text)
    return [b.strip() for b in blocks if b.strip()]


def extract_latin_blocks(text, source_name=""):
    """
    Extract Latin-dominant paragraphs from mixed-language text.
    Returns (latin_text, stats_dict).
    """
    paragraphs = split_into_paragraphs(text)
    latin_blocks = []
    stats = Counter()

    for para in paragraphs:
        lang, score = detect_language(para)
        stats[lang] += 1
        if lang == 'latin':
            latin_blocks.append(para)

    latin_text = '\n\n'.join(latin_blocks)
    return latin_text, dict(stats)


def normalize_latin(text):
    """Light normalization for medieval Latin."""
    # Don't force u/v or i/j normalization — preserve medieval spelling
    # But fix OCR-specific issues

    # Fix split words at line breaks (hyphenation)
    text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
    # Fix excessive spacing (OCR artifact from De Renzi)
    text = re.sub(r'  +', ' ', text)
    # Fix common OCR misreads in Latin
    text = re.sub(r'\brn\b', 'm', text)  # Only standalone 'rn' -> 'm'
    # Collapse line breaks within paragraphs (keep paragraph structure)
    # A paragraph break is a blank line; within paragraphs, join lines
    paragraphs = text.split('\n\n')
    normalized = []
    for para in paragraphs:
        # Join lines within paragraph
        joined = ' '.join(line.strip() for line in para.split('\n') if line.strip())
        if joined:
            normalized.append(joined)
    return '\n\n'.join(normalized)


def process_file(filename, special_handling=None):
    """
    Process a single raw file.
    special_handling: None, 'bilingual_it', 'bilingual_nl', 'noisy_ocr', 'clean_latin'
    """
    filepath = RAW_DIR / filename
    if not filepath.exists():
        print(f"  SKIP: {filename} not found")
        return None, {}

    text = filepath.read_text(encoding='utf-8', errors='replace')
    original_words = len(tokenize(text))

    # Step 1: Clean OCR artifacts
    text = clean_ocr_artifacts(text)

    if special_handling == 'clean_latin':
        # Already clean Latin (e.g., Bibliotheca Augustana)
        result = normalize_latin(text)
        clean_words = len(tokenize(result))
        stats = {'type': 'clean_latin', 'original_words': original_words,
                 'clean_words': clean_words}
        return result, stats

    if special_handling == 'noisy_ocr':
        # Aggressive cleaning for Circa Instans
        latin_text, lang_stats = extract_latin_blocks(text)
        latin_text = normalize_latin(latin_text)
        clean_words = len(tokenize(latin_text))
        non_latin_ratio = 1.0 - (clean_words / max(original_words, 1))
        stats = {'type': 'noisy_ocr', 'original_words': original_words,
                 'clean_words': clean_words, 'lang_blocks': lang_stats,
                 'non_latin_ratio_after_clean': non_latin_ratio}
        return latin_text, stats

    # Default: bilingual or mixed — extract Latin blocks
    latin_text, lang_stats = extract_latin_blocks(text, filename)
    latin_text = normalize_latin(latin_text)
    clean_words = len(tokenize(latin_text))
    stats = {'type': special_handling or 'mixed', 'original_words': original_words,
             'clean_words': clean_words, 'lang_blocks': lang_stats}
    return latin_text, stats


def main():
    # ── File configurations ──
    files_config = [
        # (filename, label, special_handling)
        ('regimen_sanitatis.txt', 'Regimen Sanitatis (Augustana)', 'clean_latin'),
        ('regimen_sanitatis_croke_1830.txt', 'Regimen Sanitatis (Croke 1830)', 'bilingual_en'),
        ('alphita_mowat_1887.txt', 'Alphita (Mowat 1887)', 'bilingual_en'),
        ('macer_floridus_choulant_1832.txt', 'Macer Floridus (Choulant 1832)', 'bilingual_de'),
        ('antidotarium_nicolai_1917.txt', 'Antidotarium Nicolai (1917)', 'bilingual_nl'),
        ('clavis_sanationis_biusante.txt', 'Clavis Sanationis (BIU Santé)', None),
        ('circa_instans_ms_ocr.txt', 'Circa Instans (MS OCR)', 'noisy_ocr'),
        ('collectio_salernitana_v1.txt', 'Collectio Salernitana I', 'bilingual_it'),
        ('collectio_salernitana_v2.txt', 'Collectio Salernitana II', 'bilingual_it'),
        ('collectio_salernitana_v3.txt', 'Collectio Salernitana III', 'bilingual_it'),
        ('collectio_salernitana_v4.txt', 'Collectio Salernitana IV', 'bilingual_it'),
        ('collectio_salernitana_v5.txt', 'Collectio Salernitana V', 'bilingual_it'),
        ('canon_medicinae_1507.txt', 'Canon Medicinae (1507)', None),
        ('canon_medicinae_1522.txt', 'Canon Medicinae (1522)', None),
    ]

    all_stats = {}
    corpus_parts = []
    circa_instans_text = None

    print("=" * 70)
    print("CORPUS 9A — Medieval Medical Latin Cleaner")
    print("=" * 70)

    for filename, label, handling in files_config:
        print(f"\n>>> Processing: {label}")
        cleaned, stats = process_file(filename, handling)

        if cleaned is None:
            print(f"    SKIPPED")
            continue

        # Save individual cleaned file
        clean_path = CLEAN_DIR / f"clean_{filename}"
        clean_path.write_text(cleaned, encoding='utf-8')

        orig = stats.get('original_words', 0)
        clean = stats.get('clean_words', 0)
        retention = (clean / orig * 100) if orig > 0 else 0
        print(f"    {orig:>10,} words raw -> {clean:>10,} words clean ({retention:.1f}% retained)")
        if 'lang_blocks' in stats:
            print(f"    Language blocks: {stats['lang_blocks']}")

        all_stats[label] = stats

        # Special handling for Circa Instans
        if filename == 'circa_instans_ms_ocr.txt':
            clean_words = stats.get('clean_words', 0)
            # Check non-latin ratio by re-analyzing cleaned text
            words = tokenize(cleaned)
            if words:
                latin_count = sum(1 for w in words if w in LATIN_FUNCTION_WORDS or
                                 (len(w) > 3 and w.endswith(('tur', 'ibus', 'orum', 'arum',
                                  'ium', 'atis', 'onis', 'alis', 'aris'))))
                non_latin_pct = 1.0 - (latin_count / len(words))
                if non_latin_pct > 0.70:
                    print(f"    WARNING: High noise ratio ({non_latin_pct:.0%}) -- routing to noisy subcorpus")
                    circa_instans_text = cleaned
                    continue
                else:
                    print(f"    OK: Noise ratio acceptable ({non_latin_pct:.0%}) -- including in main corpus")

        # Don't include both Canon editions — use 1507 (more words), skip 1522
        if filename == 'canon_medicinae_1522.txt':
            print(f"    (Skipping 1522 edition — using 1507 as primary)")
            continue

        corpus_parts.append(f"### {label} ###\n\n{cleaned}")

    # ── Assemble final corpus ──
    print("\n" + "=" * 70)
    print("ASSEMBLING FINAL CORPUS")
    print("=" * 70)

    final_corpus = '\n\n\n'.join(corpus_parts)
    final_path = OUT_DIR / 'corpus_latin_medical_extended.txt'
    final_path.write_text(final_corpus, encoding='utf-8')
    final_words = len(tokenize(final_corpus))
    print(f"\n  corpus_latin_medical_extended.txt: {final_words:,} words")

    # Save noisy Circa Instans separately if needed
    if circa_instans_text:
        noisy_path = OUT_DIR / 'corpus_circa_instans_noisy.txt'
        noisy_path.write_text(circa_instans_text, encoding='utf-8')
        noisy_words = len(tokenize(circa_instans_text))
        print(f"  corpus_circa_instans_noisy.txt: {noisy_words:,} words (noisy subcorpus)")

    # ── Generate medical suffix dictionary ──
    print("\n" + "=" * 70)
    print("GENERATING MEDICAL LATIN SUFFIX DICTIONARY")
    print("=" * 70)

    words = tokenize(final_corpus)
    suffix_dict = generate_suffix_dictionary(words)
    suffix_path = OUT_DIR / 'dict_latin_medical_suffixes.json'
    suffix_path.write_text(json.dumps(suffix_dict, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"  dict_latin_medical_suffixes.json: {sum(len(v) for v in suffix_dict.values())} entries across {len(suffix_dict)} suffix categories")

    # ── Save stats ──
    stats_path = RAW_DIR / 'cleaning_stats.json'
    stats_path.write_text(json.dumps(all_stats, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"\n  Detailed stats: raw_corpus_9a/cleaning_stats.json")

    # ── Summary ──
    total_raw = sum(s.get('original_words', 0) for s in all_stats.values())
    total_clean = final_words
    print(f"\n{'=' * 70}")
    print(f"SUMMARY")
    print(f"  Total raw words:   {total_raw:>12,}")
    print(f"  Total clean words: {total_clean:>12,}")
    print(f"  Retention rate:    {total_clean/total_raw*100:>11.1f}%")
    print(f"  Target was:        50,000-200,000 words")
    print(f"  {'TARGET EXCEEDED!' if total_clean >= 50000 else 'Below target'}")
    print(f"{'=' * 70}")


def generate_suffix_dictionary(words):
    """
    Extract medical Latin suffixes with example words.
    Groups by suffix category (declension, conjugation, technical).
    """
    # Define suffix categories
    suffix_categories = {
        # Nominal suffixes (medical terminology)
        '-atio / -ationis (action nouns)': ['atio', 'ationis', 'atione', 'ationem', 'ationes', 'ationibus'],
        '-tio / -tionis (action nouns)': ['tio', 'tionis', 'tione', 'tionem', 'tiones'],
        '-entia / -entiae (quality)': ['entia', 'entiae', 'entiam', 'entias'],
        '-antia / -antiae (quality)': ['antia', 'antiae', 'antiam'],
        '-alis / -ale (adjective)': ['alis', 'ale', 'alem', 'ali', 'ales', 'alium', 'alibus'],
        '-aris / -are (adjective)': ['aris', 'are', 'arem', 'ari', 'ares', 'arium', 'aribus'],
        '-tura / -turae (process)': ['tura', 'turae', 'turam', 'turis'],
        '-mentum / -menti (instrument)': ['mentum', 'menti', 'mento', 'mentis'],
        '-icum / -ica (adjective)': ['icum', 'ica', 'icam', 'ico', 'ici', 'icis'],
        '-osus / -osa (abundance)': ['osus', 'osa', 'osum', 'osi', 'osae', 'osis'],
        '-ivus / -iva (tendency)': ['ivus', 'iva', 'ivum', 'ivi', 'ivae', 'ivis'],
        '-bilis / -bile (capability)': ['bilis', 'bile', 'bilem', 'bili', 'biles', 'bilium'],
        # 1st declension (feminine, herbs/plants)
        '-a / -ae (1st decl.)': ['ae', 'am', 'arum'],
        # 2nd declension (neuter, remedies)
        '-um / -i (2nd decl. neut.)': ['orum'],
        # 3rd declension (medical terms)
        '-is / -is (3rd decl.)': ['ibus'],
        # Verbal suffixes (medical procedures)
        '-are (1st conj. inf.)': ['are', 'atur', 'antur', 'anda', 'andum'],
        '-ere (2nd/3rd conj. inf.)': ['ere', 'etur', 'entur', 'enda', 'endum'],
        '-ire (4th conj. inf.)': ['ire', 'itur', 'iuntur'],
        # Participles (common in recipes)
        '-tus / -ta / -tum (past part.)': ['tus', 'tum', 'tis'],
        '-ns / -ntis (pres. part.)': ['ens', 'ans', 'entis', 'antis', 'entes', 'antes'],
    }

    # Count words by suffix
    word_counter = Counter(words)
    result = {}

    for category, suffixes in suffix_categories.items():
        examples = {}
        for suffix in suffixes:
            matching = [(w, c) for w, c in word_counter.items()
                       if w.endswith(suffix) and len(w) > len(suffix) + 2]
            # Top 20 by frequency
            top = sorted(matching, key=lambda x: -x[1])[:20]
            if top:
                examples[f'-{suffix}'] = {w: c for w, c in top}

        if examples:
            result[category] = examples

    return result


if __name__ == '__main__':
    main()
