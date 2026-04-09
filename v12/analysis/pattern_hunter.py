"""
Pattern Hunter — Analyse le décodage complet du manuscrit pour identifier :
1. Patterns syntaxiques récurrents (VERB + INGREDIENT + PREP + LIQUID)
2. Mots opaques groupés par pattern EVA
3. Suffixes (-dy, -dam, -dar, etc.) et leur distribution
4. Séquences prometteuses (3+ mots pharma consécutifs)
"""
import sys, os, re, json
from collections import Counter, defaultdict
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from v12.config import Config
from v12.pipeline import VoynichPipeline
from v12.loaders.transcription import list_folios, parse_folio
from v12.stages.logogram import DecodedWord


# ─── Vocabulary categories ───
VERBS = {'coquo', 'coques', 'coque', 'coqui', 'coquere', 'coquas', 'recipe', 'collige', 'colligens', 'misce', 'tere', 'fac', 'pone', 'adde', 'solve', 'distilla'}
INGREDIENTS = {'aloes', 'hiera', 'ture', 'asarum', 'apium', 'oleum', 'cicura', 'cera', 'mel', 'sal', 'piper', 'zingiber', 'crocus', 'myrrha', 'mastix', 'cassia', 'nardus', 'rens', 'iecur', 'libra'}
PREPS = {'in', 'cum', 'per', 'ex', 'de', 'ad', 'super', 'sub', 'pro'}
LIQUIDS = {'aquam', 'aqua', 'aquae', 'vinum', 'vino', 'oleum', 'oleo', 'succo', 'iure'}
CONJUNCTIONS = {'et', 'ac', 'vel', 'aut', 'sed', 'atque'}
MEASURE = {'libra', 'librae', 'uncia', 'unciae', 'drachma', 'equaliter', 'partes'}
BODY = {'rens', 'iecur', 'cor', 'caput', 'dolor', 'febris', 'morbus'}

ALL_PHARMA = VERBS | INGREDIENTS | LIQUIDS | MEASURE | BODY


def classify_word(latin: str) -> str:
    """Classify a decoded Latin word into a syntactic category."""
    w = latin.lower().strip('_[](?)')
    if w in VERBS: return 'V'      # Verb
    if w in INGREDIENTS: return 'I' # Ingredient
    if w in PREPS: return 'P'      # Preposition
    if w in LIQUIDS: return 'L'    # Liquid
    if w in CONJUNCTIONS: return 'C' # Conjunction
    if w in MEASURE: return 'M'    # Measure
    if w in BODY: return 'B'       # Body part
    if w == 'eius': return 'G'     # Genitive pronoun
    if w in ('es', 'est'): return 'X' # Copula
    return 'w'                     # Other word


def analyze_line(words: list[DecodedWord]) -> dict:
    """Analyze a single decoded line for patterns."""
    latins = [dw.latin.lower().strip('_[]()? ') for dw in words]
    cats = [classify_word(l) for l in latins]
    cat_str = ''.join(cats)

    # Count pharma words
    pharma_count = sum(1 for l in latins if l in ALL_PHARMA)

    # Find pharma runs (consecutive pharma words)
    max_run = 0
    current_run = 0
    runs = []
    run_start = -1
    for i, l in enumerate(latins):
        if l in ALL_PHARMA or l in PREPS or l in CONJUNCTIONS:
            if current_run == 0:
                run_start = i
            current_run += 1
        else:
            if current_run >= 3:
                runs.append((run_start, i, [latins[j] for j in range(run_start, i)]))
            max_run = max(max_run, current_run)
            current_run = 0
    if current_run >= 3:
        runs.append((run_start, len(latins), [latins[j] for j in range(run_start, len(latins))]))
        max_run = max(max_run, current_run)

    return {
        'latins': latins,
        'categories': cats,
        'cat_str': cat_str,
        'pharma_count': pharma_count,
        'pharma_density': pharma_count / max(len(latins), 1),
        'max_run': max_run,
        'runs': runs,
    }


def extract_suffix_patterns(eva_words: list[str]) -> Counter:
    """Extract EVA suffix patterns."""
    suffixes = Counter()
    for w in eva_words:
        # Check known suffixes
        for suf in ['dy', 'dam', 'dar', 'dal', 'daiin', 'dain', 'aiin', 'ain',
                     'ey', 'eey', 'ol', 'or', 'ar', 'al', 'am', 'chy', 'shy',
                     'iin', 'oly', 'ory', 'ary', 'aly']:
            if w.endswith(suf) and len(w) > len(suf):
                suffixes[f'-{suf}'] += 1
                break
    return suffixes


def group_opaque_words(decoded_all: list[tuple[str, DecodedWord]]) -> dict:
    """Group LOW/OPAQUE words by EVA glyph pattern."""
    opaque = defaultdict(list)
    for folio_id, dw in decoded_all:
        if dw.confidence in ('LOW', 'OPAQUE'):
            # Extract pattern: replace specific glyphs with categories
            pattern = dw.eva
            # Group by length and first/last glyph
            key = f"len={len(dw.eva)}_start={dw.eva[:2]}"
            opaque[key].append((folio_id, dw.eva, dw.latin))
    return opaque


def find_syntactic_templates(all_lines: list[dict]) -> Counter:
    """Find recurring syntactic templates (3-5 word category patterns)."""
    templates = Counter()
    for line in all_lines:
        cats = line['cat_str']
        # Extract all 3-grams, 4-grams, 5-grams
        for n in [3, 4, 5]:
            for i in range(len(cats) - n + 1):
                ngram = cats[i:i+n]
                # Only interesting if contains V or I
                if 'V' in ngram or 'I' in ngram:
                    templates[ngram] += 1
    return templates


def main():
    print("=" * 80)
    print("  PATTERN HUNTER — Full Manuscript Analysis")
    print("=" * 80)

    # Load pipeline
    config = Config()
    pipeline = VoynichPipeline(config)
    pipeline.load()

    folios = list_folios(config.transcription_path)
    print(f"\nScanning {len(folios)} folios...")

    all_lines = []
    all_eva_words = []
    all_decoded = []  # (folio_id, DecodedWord)
    suffix_counter = Counter()
    folio_scores = []
    best_runs = []  # (folio, line, run_words, run_len)

    for i, (fid, section) in enumerate(folios):
        lines, sec = parse_folio(config.transcription_path, fid)
        if not lines:
            continue

        decoded = pipeline.decode_folio(lines)

        for lnum, words in sorted(decoded.items()):
            # Collect EVA words
            eva_words = [dw.eva for dw in words]
            all_eva_words.extend(eva_words)

            # Collect decoded words
            for dw in words:
                all_decoded.append((fid, dw))

            # Suffix analysis
            suffix_counter += extract_suffix_patterns(eva_words)

            # Line analysis
            analysis = analyze_line(words)
            analysis['folio'] = fid
            analysis['section'] = section
            analysis['line'] = lnum
            all_lines.append(analysis)

            # Track best pharma runs
            for start, end, run_words in analysis['runs']:
                best_runs.append((fid, lnum, run_words, len(run_words)))

        if (i + 1) % 20 == 0:
            print(f"  ... {i+1}/{len(folios)} folios processed")

    print(f"\nTotal lines analyzed: {len(all_lines)}")
    print(f"Total words: {len(all_decoded)}")

    # ─── REPORT ───
    output = []
    output.append("=" * 80)
    output.append("  PATTERN HUNTER REPORT — Full Voynich Manuscript")
    output.append(f"  {len(folios)} folios, {len(all_lines)} lines, {len(all_decoded)} words")
    output.append("=" * 80)

    # 1. SUFFIX ANALYSIS
    output.append("\n\n## 1. EVA SUFFIX DISTRIBUTION (top 30)")
    output.append("-" * 50)
    for suf, count in suffix_counter.most_common(30):
        output.append(f"  {suf:10s} : {count:5d}")

    # 2. SYNTACTIC TEMPLATES
    output.append("\n\n## 2. SYNTACTIC TEMPLATES (V=verb, I=ingredient, P=prep, L=liquid, C=conj)")
    output.append("-" * 50)
    templates = find_syntactic_templates(all_lines)
    for tmpl, count in templates.most_common(40):
        if count >= 5:
            # Decode template
            legend = {'V': 'VERB', 'I': 'INGR', 'P': 'PREP', 'L': 'LIQ', 'C': 'CONJ',
                      'M': 'MEAS', 'B': 'BODY', 'G': 'eius', 'X': 'est', 'w': '...'}
            readable = ' + '.join(legend.get(c, c) for c in tmpl)
            output.append(f"  {tmpl:8s} ({readable:40s}) : {count:4d}x")

    # 3. BEST PHARMACEUTICAL RUNS (longest consecutive pharma sequences)
    output.append("\n\n## 3. BEST PHARMACEUTICAL SEQUENCES (3+ consecutive pharma terms)")
    output.append("-" * 50)
    best_runs.sort(key=lambda x: -x[3])
    seen = set()
    for fid, lnum, run_words, run_len in best_runs[:50]:
        key = f"{fid}_L{lnum:02d}"
        if key in seen:
            continue
        seen.add(key)
        output.append(f"  {fid:8s} L{lnum:02d} [{run_len} terms]: {' '.join(run_words)}")

    # 4. OPAQUE WORD CLUSTERS
    output.append("\n\n## 4. OPAQUE/LOW WORD CLUSTERS")
    output.append("-" * 50)
    opaque_groups = group_opaque_words(all_decoded)
    # Count total opaques
    total_opaque = sum(len(v) for v in opaque_groups.values())
    output.append(f"  Total LOW/OPAQUE words: {total_opaque}")

    # Group by EVA word (exact match)
    exact_opaque = Counter()
    for fid, dw in all_decoded:
        if dw.confidence in ('LOW', 'OPAQUE'):
            exact_opaque[dw.eva] += 1

    output.append(f"\n  Most frequent LOW/OPAQUE EVA words:")
    for eva, count in exact_opaque.most_common(40):
        output.append(f"    {eva:20s} : {count:4d}x")

    # 5. DENSITY MAP — which folios have highest pharma density
    output.append("\n\n## 5. FOLIO PHARMA DENSITY MAP")
    output.append("-" * 50)
    folio_pharma = defaultdict(lambda: {'pharma': 0, 'total': 0, 'section': ''})
    for line in all_lines:
        fp = folio_pharma[line['folio']]
        fp['pharma'] += line['pharma_count']
        fp['total'] += len(line['latins'])
        fp['section'] = line['section']

    ranked_folios = []
    for fid, data in folio_pharma.items():
        density = data['pharma'] / max(data['total'], 1)
        ranked_folios.append((fid, data['section'], data['pharma'], data['total'], density))
    ranked_folios.sort(key=lambda x: -x[4])

    output.append(f"  {'Folio':10s} {'Sec':4s} {'Pharma':>7s} {'Total':>7s} {'Density':>8s}")
    for fid, sec, pharma, total, density in ranked_folios[:30]:
        bar = '#' * int(density * 40)
        output.append(f"  {fid:10s} {sec:4s} {pharma:7d} {total:7d} {density:8.1%} {bar}")

    # 6. WORD FREQUENCY ANALYSIS (type-token)
    output.append("\n\n## 6. WORD FREQUENCY ANALYSIS")
    output.append("-" * 50)
    word_freq = Counter()
    for fid, dw in all_decoded:
        if dw.confidence not in ('OPAQUE',):
            word_freq[dw.latin.lower().strip('_[]()? ')] += 1

    total_tokens = sum(word_freq.values())
    total_types = len(word_freq)
    output.append(f"  Total tokens: {total_tokens}")
    output.append(f"  Unique types: {total_types}")
    output.append(f"  Type-token ratio: {total_types/max(total_tokens,1):.3f} (target: 0.34)")

    output.append(f"\n  Top 50 most frequent decoded words:")
    for word, count in word_freq.most_common(50):
        pct = count / total_tokens * 100
        output.append(f"    {word:25s} : {count:5d} ({pct:5.2f}%)")

    # 7. PROMISING LINES — high pharma density + low opaque
    output.append("\n\n## 7. MOST PROMISING LINES FOR READING")
    output.append("-" * 50)
    output.append("  Lines with pharma density > 30% and no OPAQUE words:")

    promising = []
    for line in all_lines:
        if line['pharma_density'] > 0.3 and line['pharma_count'] >= 3:
            # Check for opaques in this line
            promising.append(line)

    promising.sort(key=lambda x: (-x['pharma_density'], -x['pharma_count']))
    for line in promising[:30]:
        output.append(f"\n  {line['folio']:8s} L{line['line']:02d} [{line['section']}] "
                      f"density={line['pharma_density']:.0%} ({line['pharma_count']} terms)")
        output.append(f"    {' '.join(line['latins'])}")

    # Write report
    report = '\n'.join(output)
    out_path = os.path.join(os.path.dirname(__file__), '..', 'output', 'PATTERN_HUNTER_REPORT.txt')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\nReport written to {out_path}")
    print(report[:3000])


if __name__ == '__main__':
    main()
