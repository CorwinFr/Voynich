"""
ATTACK 04 — FUNDAMENTAL TEST: Word-level or syllable-level encoding?

THIS MUST RUN FIRST. If the VMS is logo-syllabic (like hieroglyphs),
the entire word-level candidate registry is biased and must be rethought.

Tests 3 hypotheses:
  H1: EVA glyph count ~ Latin letter count (alphabetic, K&A style)
  H2: EVA glyph count ~ Latin syllable count (syllabic)
  H3: No correlation (nomenclator / arbitrary code)

Uses the 16 known logograms as ground truth calibration,
plus any confirmed ingredients from the candidate store.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import math
from collections import Counter
from lib.loader import load_referentiels, build_form_lookup
from lib.vms_parser import VMSCorpus, LOGOGRAMS
from lib.scorer import count_syllables_latin


def count_eva_glyphs(eva_word):
    """Count the number of EVA glyph units in a word.

    EVA has digraphs: sh, ch, ee, ii, ai, oi, etc.
    We count GLYPH UNITS, not characters.
    """
    i = 0
    count = 0
    digraphs = ['sh', 'ch', 'ee', 'ii', 'ai', 'oi', 'ph', 'ck', 'th']

    while i < len(eva_word):
        if i + 1 < len(eva_word) and eva_word[i:i+2] in digraphs:
            count += 1
            i += 2
        else:
            count += 1
            i += 1
    return count


def pearson_correlation(x, y):
    """Compute Pearson correlation coefficient."""
    n = len(x)
    if n < 3:
        return 0.0

    mean_x = sum(x) / n
    mean_y = sum(y) / n

    cov = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
    var_x = sum((xi - mean_x) ** 2 for xi in x)
    var_y = sum((yi - mean_y) ** 2 for yi in y)

    if var_x == 0 or var_y == 0:
        return 0.0

    return cov / math.sqrt(var_x * var_y)


def run_test(anchors):
    """Run the word-vs-syllable test on a set of known anchors.

    Args:
        anchors: list of (eva_word, latin_word) pairs

    Returns:
        dict with correlation results
    """
    eva_lengths = []
    latin_letters = []
    latin_syllables = []
    details = []

    for eva, latin in anchors:
        n_eva = count_eva_glyphs(eva)
        n_letters = len(latin)
        n_syllables = count_syllables_latin(latin)

        eva_lengths.append(n_eva)
        latin_letters.append(n_letters)
        latin_syllables.append(n_syllables)
        details.append({
            'eva': eva,
            'latin': latin,
            'eva_glyphs': n_eva,
            'latin_letters': n_letters,
            'latin_syllables': n_syllables,
            'ratio_letters': round(n_letters / max(n_eva, 1), 2),
            'ratio_syllables': round(n_syllables / max(n_eva, 1), 2),
        })

    r_letters = pearson_correlation(eva_lengths, latin_letters)
    r_syllables = pearson_correlation(eva_lengths, latin_syllables)

    # Average ratios
    avg_ratio_letters = sum(d['ratio_letters'] for d in details) / len(details)
    avg_ratio_syllables = sum(d['ratio_syllables'] for d in details) / len(details)

    return {
        'n_anchors': len(anchors),
        'r_letters': round(r_letters, 4),
        'r_syllables': round(r_syllables, 4),
        'avg_ratio_letters_per_glyph': round(avg_ratio_letters, 2),
        'avg_ratio_syllables_per_glyph': round(avg_ratio_syllables, 2),
        'details': details,
    }


def interpret_results(results):
    """Interpret correlation results and determine encoding type."""
    r_let = results['r_letters']
    r_syl = results['r_syllables']

    print()
    print("=" * 60)
    print("ATTACK 04 — FUNDAMENTAL TEST: WORD vs SYLLABLE")
    print("=" * 60)
    print()
    print(f"Anchors tested: {results['n_anchors']}")
    print(f"Correlation EVA_glyphs ~ Latin_letters:   r = {r_let:+.4f}")
    print(f"Correlation EVA_glyphs ~ Latin_syllables: r = {r_syl:+.4f}")
    print(f"Average letters per EVA glyph:   {results['avg_ratio_letters_per_glyph']}")
    print(f"Average syllables per EVA glyph: {results['avg_ratio_syllables_per_glyph']}")
    print()

    # Print detail table
    print(f"{'EVA':<15s} {'Latin':<20s} {'Glyphs':>6s} {'Letters':>7s} {'Syllab':>6s} {'L/G':>5s} {'S/G':>5s}")
    print("-" * 70)
    for d in sorted(results['details'], key=lambda x: x['eva_glyphs']):
        print(f"{d['eva']:<15s} {d['latin']:<20s} {d['eva_glyphs']:>6d} {d['latin_letters']:>7d} {d['latin_syllables']:>6d} {d['ratio_letters']:>5.2f} {d['ratio_syllables']:>5.2f}")

    print()
    print("INTERPRETATION:")

    if r_let > 0.6:
        print(f"  H1 SUPPORTED (r={r_let:.3f}): Alphabetic encoding (K&A style)")
        print(f"  -> Each EVA glyph encodes ~{results['avg_ratio_letters_per_glyph']:.1f} Latin letters")
        print(f"  -> Word-level candidate registry is VALID")
        verdict = 'ALPHABETIC'
    elif r_syl > 0.6:
        print(f"  H2 SUPPORTED (r={r_syl:.3f}): Syllabic encoding")
        print(f"  -> Each EVA glyph encodes ~1 Latin syllable")
        print(f"  -> WARNING: Registry should work syllable-by-syllable")
        verdict = 'SYLLABIC'
    elif abs(r_let) < 0.3 and abs(r_syl) < 0.3:
        print(f"  H3 SUPPORTED: No length correlation -> Nomenclator (arbitrary code)")
        print(f"  -> Each EVA word = an arbitrary code for a Latin word")
        print(f"  -> Word-level candidate registry is VALID")
        print(f"  -> But K&A phonetic decoding is WRONG")
        verdict = 'NOMENCLATOR'
    else:
        print(f"  INCONCLUSIVE: r_letters={r_let:.3f}, r_syllables={r_syl:.3f}")
        print(f"  -> Need more anchors to distinguish")
        verdict = 'INCONCLUSIVE'

    results['verdict'] = verdict
    return results


def main():
    """Run the fundamental test."""
    print("Loading data...")

    # Test 1: Known logograms (most reliable anchors)
    logo_anchors = [(eva, latin) for eva, latin in LOGOGRAMS.items()]
    print(f"\nTest 1: {len(logo_anchors)} known logograms")
    results_logos = run_test(logo_anchors)
    interpret_results(results_logos)

    # Test 2: Load VMS corpus and check word length distribution
    vms = VMSCorpus()
    vms.load()

    # VMS word length distribution
    eva_length_dist = Counter()
    for word in vms.unique_words:
        n = count_eva_glyphs(word)
        eva_length_dist[n] += 1

    print()
    print("VMS word length distribution (EVA glyphs):")
    for n in sorted(eva_length_dist.keys()):
        c = eva_length_dist[n]
        bar = '#' * (c // 20)
        print(f"  {n:>2d} glyphs: {c:>5d} words  {bar}")

    # Latin ingredient length distribution
    refs = load_referentiels()
    ingredients = refs.get('R02', {})

    latin_letter_dist = Counter()
    latin_syllable_dist = Counter()
    for ref_id, entry in ingredients.items():
        canonical = entry.get('canonical', '')
        if canonical:
            latin_letter_dist[len(canonical)] += 1
            latin_syllable_dist[count_syllables_latin(canonical)] += 1

    print()
    print("Latin ingredient length distribution (letters):")
    for n in sorted(latin_letter_dist.keys()):
        c = latin_letter_dist[n]
        bar = '#' * (c // 5)
        print(f"  {n:>2d} letters: {c:>4d} ingredients  {bar}")

    print()
    print("Latin ingredient syllable distribution:")
    for n in sorted(latin_syllable_dist.keys()):
        c = latin_syllable_dist[n]
        bar = '#' * (c // 5)
        print(f"  {n:>2d} syllables: {c:>4d} ingredients  {bar}")

    # Compare distributions
    # If EVA glyph distribution peaks at 3-6 and Latin syllables at 2-4 -> syllabic
    # If EVA glyph distribution peaks at 3-6 and Latin letters at 6-12 -> alphabetic (~2x)
    eva_peak = max(eva_length_dist, key=eva_length_dist.get)
    latin_letter_peak = max(latin_letter_dist, key=latin_letter_dist.get) if latin_letter_dist else 0
    latin_syl_peak = max(latin_syllable_dist, key=latin_syllable_dist.get) if latin_syllable_dist else 0

    print()
    print(f"EVA word length peak: {eva_peak} glyphs")
    print(f"Latin letter length peak: {latin_letter_peak} letters")
    print(f"Latin syllable peak: {latin_syl_peak} syllables")
    print(f"Ratio letter_peak/eva_peak: {latin_letter_peak / max(eva_peak, 1):.2f}")
    print(f"Ratio syllable_peak/eva_peak: {latin_syl_peak / max(eva_peak, 1):.2f}")

    # Save results
    output = {
        'logograms_test': results_logos,
        'eva_length_distribution': dict(eva_length_dist),
        'latin_letter_distribution': dict(latin_letter_dist),
        'latin_syllable_distribution': dict(latin_syllable_dist),
        'peaks': {
            'eva_glyphs': eva_peak,
            'latin_letters': latin_letter_peak,
            'latin_syllables': latin_syl_peak,
        },
    }

    os.makedirs('attacks/results', exist_ok=True)
    with open('attacks/results/attack_04_results.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print()
    print("Results saved to attacks/results/attack_04_results.json")


if __name__ == '__main__':
    main()
