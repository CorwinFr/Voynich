"""
DEAGGLUTINATOR — Discover the author's agglutination system.

The Voynich author GLUES prepositions/particles to the following word:
  y + taiin = IN + elura (not "inelura" as one word)
  d + aiin  = IN + aquam (already known!)
  o + keey  = E + quo   (not "equo" as one word)

This script:
1. Tests EVERY initial EVA glyph as a potential prefix
2. For each prefix, checks if stripping it produces better Latin
3. Maps the full prefix system
4. Re-decodes the manuscript with deagglutination
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


def decode_bare(word, pipeline, top_k=5):
    """Decode a word through HMM only, return top candidates with Perseus/corpus info."""
    results = []
    hmm_paths = decode_root(word, pipeline.hmm, top_k=top_k)
    for vp in hmm_paths:
        if not vp.latin:
            continue
        clean = vp.latin.replace(' ', '')
        is_perseus = pipeline.dictionary.is_valid(clean)
        freq = pipeline.corpus.freq(clean)
        results.append((clean, vp.log_prob, is_perseus, freq))
    return results


def test_prefix(prefix_eva, prefix_latin, pipeline, folios, config, sample_size=200):
    """
    Test if a given EVA glyph acts as a prefix (preposition glued to next word).

    Returns stats on how often stripping the prefix produces better Latin.
    """
    from v12.loaders.transcription import parse_folio

    words_with_prefix = []  # (eva, full_decode, remainder, rem_decode, rem_perseus, rem_freq)

    count = 0
    for fid, section in folios:
        if count >= sample_size:
            break
        lines, sec = parse_folio(config.transcription_path, fid)
        if not lines:
            continue
        decoded = pipeline.decode_folio(lines)

        for lnum, dw_list in sorted(decoded.items()):
            for dw in dw_list:
                if count >= sample_size:
                    break
                if not dw.eva.startswith(prefix_eva) or len(dw.eva) < 4:
                    continue

                remainder = dw.eva[len(prefix_eva):]
                if len(remainder) < 2:
                    continue

                # Decode remainder
                rem_dw = pipeline.decode_word(remainder)
                rem_perseus = pipeline.dictionary.is_valid(rem_dw.latin.strip('_[]()? '))
                rem_freq = pipeline.corpus.freq(rem_dw.latin.strip('_[]()? '))

                # Also check full word Perseus status
                full_perseus = pipeline.dictionary.is_valid(dw.latin.strip('_[]()? '))

                words_with_prefix.append({
                    'eva': dw.eva,
                    'full_latin': dw.latin,
                    'full_conf': dw.confidence,
                    'full_perseus': full_perseus,
                    'remainder': remainder,
                    'rem_latin': rem_dw.latin,
                    'rem_conf': rem_dw.confidence,
                    'rem_perseus': rem_perseus,
                    'rem_freq': rem_freq,
                    'fid': fid,
                })
                count += 1

    # Compute improvement stats
    total = len(words_with_prefix)
    if total == 0:
        return None

    # How often does remainder decode BETTER than full word?
    rem_better = sum(1 for w in words_with_prefix
                     if w['rem_perseus'] and not w['full_perseus'])
    full_better = sum(1 for w in words_with_prefix
                      if w['full_perseus'] and not w['rem_perseus'])
    both_good = sum(1 for w in words_with_prefix
                    if w['full_perseus'] and w['rem_perseus'])
    neither = sum(1 for w in words_with_prefix
                  if not w['full_perseus'] and not w['rem_perseus'])

    # Confidence improvement
    conf_order = {'CONFIRMED': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1, 'OPAQUE': 0}
    conf_improved = sum(1 for w in words_with_prefix
                        if conf_order.get(w['rem_conf'], 0) > conf_order.get(w['full_conf'], 0))

    return {
        'prefix_eva': prefix_eva,
        'prefix_latin': prefix_latin,
        'total': total,
        'rem_better': rem_better,
        'full_better': full_better,
        'both_good': both_good,
        'neither': neither,
        'conf_improved': conf_improved,
        'improvement_rate': rem_better / max(total, 1),
        'examples': words_with_prefix[:30],
    }


def main():
    config = Config()
    pipeline = VoynichPipeline(config)
    pipeline.load()

    folios = list_folios(config.transcription_path)

    output = []
    output.append("=" * 90)
    output.append("  DEAGGLUTINATOR — Mapping the Voynich prefix/agglutination system")
    output.append("=" * 90)

    # === Test each initial glyph as a potential prefix ===
    # Known from K&A and our analysis:
    PREFIX_CANDIDATES = [
        ('y', 'in'),       # y = IN (preposition "in/into")
        ('o', 'e'),        # o = E/A (prothetic vowel or EX)
        ('d', 'in'),       # d = IN/D (variant of "in" or consonant D)
        ('s', 'us'),       # s = US (suffix? or S consonant)
        ('q', 'co'),       # q = CO/CUM (with)
        ('l', 'es'),       # l = ES/EX (out of)
        ('r', 're'),       # r = RE (again/back)
        ('a', 'u'),        # a = U/A (vowel)
        ('ch', 'i'),       # ch = I (vowel)
        ('sh', 'ci'),      # sh = CI (this/these)
        ('k', 'c'),        # k = C/QU (consonant)
        ('t', 'el'),       # t = EL/L (article?)
        ('p', 'pe'),       # p = PE/PER
        ('f', 'pa'),       # f = PA
        ('ot', 'T-'),      # ot = T-trigger (known)
        ('qo', 'cum'),     # qo = CUM/CO (with)
        ('ok', 'qu'),      # ok = QU
        ('da', 'in a'),    # da = IN A- (in the)
        ('ol', 'es'),      # ol = ES (known suffix pattern)
    ]

    output.append("\n\n## 1. PREFIX VALIDITY TEST")
    output.append("-" * 70)
    output.append(f"  Testing {len(PREFIX_CANDIDATES)} prefix candidates...")
    output.append(f"  For each: strip prefix, decode remainder, check if Latin improves")
    output.append(f"")
    output.append(f"  {'EVA':6s} {'Latin':6s} {'N':>5s} {'Rem>Full':>9s} {'Full>Rem':>9s} {'Both OK':>8s} {'Neither':>8s} {'Improv%':>8s}")

    all_results = []
    for prefix_eva, prefix_latin in PREFIX_CANDIDATES:
        print(f"  Testing prefix: {prefix_eva} = {prefix_latin}...")
        result = test_prefix(prefix_eva, prefix_latin, pipeline, folios, config, sample_size=150)
        if result:
            all_results.append(result)
            r = result
            output.append(f"  {r['prefix_eva']:6s} {r['prefix_latin']:6s} {r['total']:5d} "
                         f"{r['rem_better']:9d} {r['full_better']:9d} {r['both_good']:8d} "
                         f"{r['neither']:8d} {r['improvement_rate']:8.1%}")

    # Sort by improvement rate
    all_results.sort(key=lambda x: -x['improvement_rate'])

    # === Best prefixes with examples ===
    output.append("\n\n## 2. BEST PREFIX CANDIDATES (ranked by improvement rate)")
    output.append("-" * 70)

    for result in all_results:
        r = result
        if r['improvement_rate'] < 0.02:
            continue

        output.append(f"\n  ### EVA '{r['prefix_eva']}' = Latin '{r['prefix_latin']}' "
                     f"({r['total']} words, {r['improvement_rate']:.0%} improvement)")
        output.append(f"  Remainder better: {r['rem_better']}, Full better: {r['full_better']}, "
                     f"Both: {r['both_good']}, Neither: {r['neither']}")

        # Show examples where remainder is BETTER
        output.append(f"  Examples where DEAGGLUTINATION helps:")
        shown = 0
        for w in r['examples']:
            if w['rem_perseus'] and not w['full_perseus'] and shown < 10:
                output.append(f"    {w['eva']:18s} full={w['full_latin']:20s} [{w['full_conf']:5s}] "
                             f"-> {r['prefix_latin']} + {w['rem_latin']:20s} [{w['rem_conf']:5s}] IMPROVED")
                shown += 1

        # Show examples where full word is BETTER (prefix stripping hurts)
        output.append(f"  Examples where keeping full word is better:")
        shown = 0
        for w in r['examples']:
            if w['full_perseus'] and not w['rem_perseus'] and shown < 5:
                output.append(f"    {w['eva']:18s} full={w['full_latin']:20s} [{w['full_conf']:5s}] "
                             f"-> {r['prefix_latin']} + {w['rem_latin']:20s} [{w['rem_conf']:5s}] WORSE")
                shown += 1

    # === SECTION 3: The complete agglutination map ===
    output.append("\n\n## 3. THE AGGLUTINATION MAP")
    output.append("=" * 70)
    output.append("  How the Voynich author compresses Latin:")
    output.append("")

    confirmed_prefixes = []
    for r in all_results:
        if r['improvement_rate'] > 0.05 and r['rem_better'] > r['full_better']:
            confirmed_prefixes.append((r['prefix_eva'], r['prefix_latin'],
                                       r['improvement_rate'], r['total']))

    confirmed_prefixes.sort(key=lambda x: -x[2])

    output.append(f"  CONFIRMED PREFIXES (improvement > 5%, remainder beats full):")
    for eva, latin, rate, total in confirmed_prefixes:
        output.append(f"    EVA '{eva}' = '{latin}' ({rate:.0%} improvement, {total} words)")

    output.append(f"\n  AGGLUTINATION RULE:")
    output.append(f"  The scribe writes: PREFIX + WORD as a SINGLE EVA token")
    output.append(f"  Example: y+taiin = IN + [word decoded from taiin]")
    output.append(f"  Example: d+aiin = IN + AQUAM (already in logogram table!)")
    output.append(f"  Example: qo+keey = CUM + [word decoded from keey]")

    # === SECTION 4: Sample deagglutinated text ===
    output.append("\n\n## 4. SAMPLE DEAGGLUTINATED TEXT — f33r")
    output.append("-" * 70)

    # Build prefix map for deagglutination
    prefix_map = {}
    for r in all_results:
        if r['improvement_rate'] > 0.03 or r['prefix_eva'] in ('y', 'd', 'qo', 'ot'):
            prefix_map[r['prefix_eva']] = r['prefix_latin']

    # Decode f33r with deagglutination
    sample_folios = ['f33r', 'f103r', 'f88r', 'f76r', 'f101r']
    for sample_fid in sample_folios:
        lines, sec = parse_folio(config.transcription_path, sample_fid)
        if not lines:
            continue
        decoded = pipeline.decode_folio(lines)

        output.append(f"\n  --- {sample_fid.upper()} (deagglutinated) ---")
        for lnum in sorted(decoded.keys()):
            words = decoded[lnum]
            deagg_parts = []

            for dw in words:
                # Try deagglutination for each confirmed prefix
                deagg = None
                # Sort prefixes by length (longest first to avoid partial matches)
                for peva in sorted(prefix_map.keys(), key=len, reverse=True):
                    if dw.eva.startswith(peva) and len(dw.eva) > len(peva) + 1:
                        remainder = dw.eva[len(peva):]
                        rem_dw = pipeline.decode_word(remainder)
                        rem_clean = rem_dw.latin.strip('_[]()? ')

                        # Only deagglutinate if remainder is valid
                        if rem_dw.confidence in ('CONFIRMED', 'HIGH', 'MEDIUM'):
                            platin = prefix_map[peva]
                            deagg = f"{platin} {rem_dw.latin}"
                            break

                if deagg and dw.confidence in ('LOW', 'OPAQUE'):
                    deagg_parts.append(f"[{deagg}]")
                elif dw.confidence in ('CONFIRMED', 'HIGH'):
                    deagg_parts.append(dw.latin)
                elif dw.confidence == 'MEDIUM':
                    deagg_parts.append(f"{dw.latin}?")
                else:
                    deagg_parts.append(f"_{dw.latin}_")

            line_text = ' '.join(deagg_parts)
            output.append(f"  L{lnum:02d}: {line_text}")

    # Write report
    report = '\n'.join(output)
    out_path = os.path.join(os.path.dirname(__file__), '..', 'output', 'DEAGGLUTINATOR_REPORT.txt')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\nReport: {out_path}")
    print(f"Confirmed prefixes: {len(confirmed_prefixes)}")
    for eva, latin, rate, total in confirmed_prefixes:
        print(f"  {eva} = {latin} ({rate:.0%})")


if __name__ == '__main__':
    main()
