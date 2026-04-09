"""
yt- Dissector — Is yt- always INULA, or is it IN + EL-word?

Strategy:
1. For every yt- word, strip the y (=in) and decode the remainder
2. Compare: does the remainder make sense as a standalone word?
3. Check context: what follows yt-words? (verb = it's a noun, noun = it's a prep)
4. Compare herbal folios (plant name position) vs other sections
5. Check if the SAME suffix patterns appear with OTHER prefixes
   (e.g., if -taiin exists both as y+taiin and o+taiin, then t+aiin is the root)
"""
import sys, os
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from v12.config import Config
from v12.pipeline import VoynichPipeline
from v12.loaders.transcription import list_folios, parse_folio
from v12.stages.tokenizer import tokenize, preprocess_triples
from v12.stages.hmm_decoder import decode_root


def main():
    config = Config()
    pipeline = VoynichPipeline(config)
    pipeline.load()

    folios = list_folios(config.transcription_path)

    output = []
    output.append("=" * 80)
    output.append("  yt- DISSECTOR: IN + EL-word vs INULA")
    output.append("=" * 80)

    # Collect ALL yt- words with full context
    yt_entries = []  # (fid, section, lnum, pos, eva, latin, conf, words_before, words_after)

    # Also collect words that share suffixes with yt- words
    # e.g. if ytaiin exists, check olaiin, daiin, etc.
    all_words_by_suffix = defaultdict(list)  # suffix -> [(prefix, eva, latin, fid)]

    for fid, section in folios:
        lines, sec = parse_folio(config.transcription_path, fid)
        if not lines:
            continue
        decoded = pipeline.decode_folio(lines)

        for lnum, words in sorted(decoded.items()):
            for i, dw in enumerate(words):
                # Track suffixes (last 3+ chars of EVA)
                if len(dw.eva) >= 4:
                    suffix = dw.eva[1:]  # everything after first glyph
                    all_words_by_suffix[suffix].append((dw.eva[0], dw.eva, dw.latin, fid))

                if not dw.eva.startswith('y'):
                    continue
                if len(dw.eva) < 3:
                    continue

                # Context: 2 words before/after
                before = [(words[j].latin, words[j].confidence) for j in range(max(0,i-2), i)]
                after = [(words[j].latin, words[j].confidence) for j in range(i+1, min(len(words), i+3))]

                yt_entries.append((fid, section, lnum, i, dw.eva, dw.latin, dw.confidence, before, after))

    output.append(f"\n  Total yt- words collected: {len(yt_entries)}")

    # === TEST 1: Decode remainder (strip y, decode rest) ===
    output.append("\n\n## 1. REMAINDER TEST: strip y- prefix, decode the rest")
    output.append("-" * 60)
    output.append("  If y=IN is a prefix, then the remainder should be a valid word.")

    # Group by EVA form
    yt_by_eva = defaultdict(list)
    for entry in yt_entries:
        yt_by_eva[entry[4]].append(entry)

    remainder_results = []
    for eva in sorted(yt_by_eva.keys(), key=lambda x: -len(yt_by_eva[x])):
        count = len(yt_by_eva[eva])
        if count < 3:
            continue

        remainder = eva[1:]  # strip 'y'
        full_decode = yt_by_eva[eva][0][5]  # current full decode

        # Decode remainder as standalone
        rem_result = pipeline.decode_word(remainder)
        rem_latin = rem_result.latin
        rem_conf = rem_result.confidence

        # Also try without y at all - decode the bare tokens
        hmm_paths = decode_root(remainder, pipeline.hmm, top_k=5)
        hmm_options = [(vp.latin.replace(' ', ''), vp.log_prob,
                        pipeline.dictionary.is_valid(vp.latin.replace(' ', '')),
                        pipeline.corpus.freq(vp.latin.replace(' ', '')))
                       for vp in hmm_paths if vp.latin]

        # Is remainder a known word?
        rem_perseus = any(h[2] for h in hmm_options)
        rem_corpus = any(h[3] > 0 for h in hmm_options)

        remainder_results.append((eva, count, full_decode, remainder, rem_latin, rem_conf,
                                  rem_perseus, rem_corpus, hmm_options[:5]))

    output.append(f"\n  {'EVA':18s} {'N':>4s} {'Full decode':25s} {'Remainder':10s} {'Rem decode':25s} {'Perseus':>7s} {'Corpus':>7s}")
    for eva, count, full, rem, rem_lat, rem_conf, rem_per, rem_corp, opts in remainder_results[:40]:
        p = 'YES' if rem_per else 'no'
        c = 'YES' if rem_corp else 'no'
        output.append(f"  {eva:18s} {count:4d} {full:25s} {rem:10s} {rem_lat:25s} {p:>7s} {c:>7s}")
        # Show HMM alternatives for remainder
        for lat, lp, is_per, freq in opts[:3]:
            markers = []
            if is_per: markers.append('PERSEUS')
            if freq > 0: markers.append(f'freq={freq}')
            m = ' '.join(markers) if markers else ''
            output.append(f"    {'':18s} {'':4s} {'':25s} {'':10s}   alt: {lat:20s} {m}")

    # === TEST 2: Context analysis — what follows yt- words? ===
    output.append("\n\n## 2. CONTEXT TEST: what word FOLLOWS yt- words?")
    output.append("-" * 60)
    output.append("  If yt- = noun (INULA), next word should be verb/prep/conj")
    output.append("  If yt- = IN+word, next word should be noun/adj")

    after_word = Counter()
    after_conf = Counter()
    after_category = Counter()

    VERBS = {'coquo', 'coques', 'coque', 'coqui', 'coquere', 'recipe', 'tere', 'misce'}
    PREPS = {'in', 'cum', 'per', 'ex', 'de', 'ad', 'super'}
    CONJS = {'et', 'ac', 'vel', 'sed'}
    NOUNS = {'aquam', 'aqua', 'hiera', 'aloes', 'eius', 'iure', 'cibo', 'tura'}

    for fid, sec, lnum, pos, eva, latin, conf, before, after in yt_entries:
        if after:
            next_word = after[0][0].lower().strip('_[]()? ')
            after_word[next_word] += 1
            after_conf[after[0][1]] += 1

            if next_word in VERBS:
                after_category['VERB'] += 1
            elif next_word in PREPS:
                after_category['PREP'] += 1
            elif next_word in CONJS:
                after_category['CONJ'] += 1
            elif next_word in NOUNS:
                after_category['NOUN'] += 1
            else:
                after_category['OTHER'] += 1

    output.append(f"\n  Category of word AFTER yt-:")
    for cat, count in after_category.most_common():
        pct = count / sum(after_category.values()) * 100
        output.append(f"    {cat:8s} : {count:4d} ({pct:5.1f}%)")

    output.append(f"\n  Top 20 words after yt-:")
    for word, count in after_word.most_common(20):
        cat = 'V' if word in VERBS else 'P' if word in PREPS else 'C' if word in CONJS else 'N' if word in NOUNS else '?'
        output.append(f"    {word:25s} : {count:4d}  [{cat}]")

    # === TEST 3: Section distribution ===
    output.append("\n\n## 3. SECTION DISTRIBUTION of yt- words")
    output.append("-" * 60)

    sec_dist = Counter()
    for entry in yt_entries:
        sec_dist[entry[1]] += 1

    total = sum(sec_dist.values())
    for sec, count in sec_dist.most_common():
        pct = count / total * 100
        output.append(f"    {sec:5s} : {count:4d} ({pct:5.1f}%)")

    # === TEST 4: Shared suffixes — does the same suffix appear with other prefixes? ===
    output.append("\n\n## 4. SHARED SUFFIX TEST")
    output.append("-" * 60)
    output.append("  If ytaiin and otaiin share suffix -taiin, the root is t+aiin, not y+taiin")
    output.append("  Checking: which yt- suffixes also appear with o-, d-, ch-, sh- prefixes")

    # Get yt- suffixes
    yt_suffixes = set()
    for eva in yt_by_eva:
        if len(eva) >= 4:
            yt_suffixes.add(eva[1:])  # suffix after y

    shared = []
    for suffix in sorted(yt_suffixes, key=lambda x: -len(yt_by_eva.get('y'+x, []))):
        yt_count = len(yt_by_eva.get('y' + suffix, []))
        if yt_count < 2:
            continue
        # Check other prefixes
        other_prefixes = []
        for entry_list in all_words_by_suffix.get(suffix, []):
            prefix = entry_list[0]
            if prefix != 'y':
                other_prefixes.append(prefix)

        if other_prefixes:
            prefix_counts = Counter(other_prefixes)
            others_str = ', '.join(f'{p}({c})' for p, c in prefix_counts.most_common(5))
            yt_decode = yt_by_eva['y' + suffix][0][5] if 'y' + suffix in yt_by_eva else '?'
            # Decode with each other prefix
            other_decodes = []
            for p, c in prefix_counts.most_common(3):
                other_eva = p + suffix
                other_result = pipeline.decode_word(other_eva)
                other_decodes.append(f"{p}+{suffix}={other_result.latin}")

            shared.append((suffix, yt_count, yt_decode, others_str, other_decodes))

    output.append(f"\n  {'Suffix':15s} {'yt-N':>5s} {'yt-decode':25s} {'Other prefixes':30s}")
    for suffix, yt_count, yt_decode, others, other_dec in shared[:40]:
        output.append(f"  {suffix:15s} {yt_count:5d} {yt_decode:25s} also: {others}")
        for od in other_dec[:3]:
            output.append(f"    {'':15s} {'':5s} {'':25s} {od}")

    # === TEST 5: Position in line ===
    output.append("\n\n## 5. POSITION IN LINE")
    output.append("-" * 60)
    output.append("  Plant names typically appear at LINE START (topic position)")

    pos_dist = Counter()
    for fid, sec, lnum, pos, eva, latin, conf, before, after in yt_entries:
        if pos == 0:
            pos_dist['FIRST'] += 1
        elif pos <= 2:
            pos_dist['EARLY (2-3)'] += 1
        else:
            pos_dist['MIDDLE/LATE'] += 1

    for p, count in pos_dist.most_common():
        pct = count / len(yt_entries) * 100
        output.append(f"    {p:15s} : {count:4d} ({pct:5.1f}%)")

    # === TEST 6: Herbal first-word analysis ===
    output.append("\n\n## 6. HERBAL FOLIOS: yt- as FIRST WORD of line")
    output.append("-" * 60)
    output.append("  In herbal monographs, the plant name is often the first word")

    first_word_yt = []
    for fid, sec, lnum, pos, eva, latin, conf, before, after in yt_entries:
        if pos == 0 and sec == 'H':
            after_str = ' '.join(a[0] for a in after[:3])
            first_word_yt.append((fid, lnum, eva, latin, after_str))

    for fid, lnum, eva, latin, after_str in first_word_yt:
        output.append(f"  {fid:8s} L{lnum:02d}: {eva:18s} -> {latin:25s} | next: {after_str}")

    # === VERDICT ===
    output.append("\n\n## VERDICT")
    output.append("=" * 60)

    noun_pct = after_category.get('NOUN', 0) / max(sum(after_category.values()), 1) * 100
    verb_pct = after_category.get('VERB', 0) / max(sum(after_category.values()), 1) * 100
    prep_pct = (after_category.get('PREP', 0) + after_category.get('CONJ', 0)) / max(sum(after_category.values()), 1) * 100

    if verb_pct + prep_pct > noun_pct:
        output.append("  EVIDENCE FAVORS: yt- = NOUN (followed by verbs/preps more than nouns)")
        output.append(f"  Verb/Prep after: {verb_pct + prep_pct:.1f}% vs Noun after: {noun_pct:.1f}%")
    else:
        output.append("  EVIDENCE FAVORS: yt- = IN + word (followed by nouns more than verbs)")
        output.append(f"  Noun after: {noun_pct:.1f}% vs Verb/Prep after: {verb_pct + prep_pct:.1f}%")

    herbal_pct = sec_dist.get('H', 0) / total * 100
    output.append(f"\n  Herbal concentration: {herbal_pct:.1f}% (if >50%, supports plant-name hypothesis)")
    output.append(f"  First-in-line (herbal): {len(first_word_yt)} instances")

    # Write
    report = '\n'.join(output)
    out_path = os.path.join(os.path.dirname(__file__), '..', 'output', 'YT_DISSECTOR_REPORT.txt')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"Report: {out_path}")
    print(f"Total yt- words: {len(yt_entries)}")
    for line in output[-10:]:
        print(line)


if __name__ == '__main__':
    main()
