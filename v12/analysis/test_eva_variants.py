"""
TEST EVA VARIANTS — Impact on decoding quality.

For each word with variants, decode ALL variants and compare:
- Does any variant produce a better Perseus match?
- Does any variant produce a known ingredient?
- What's the overall improvement?
"""
import sys, os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from v12.config import Config
from v12.pipeline import VoynichPipeline
from v12.stages.hmm_decoder import decode_root
from v12.loaders.eva_variants import get_word_variants, parse_folio_with_variants

# Known pharmaceutical ingredients (extended with Italian names)
KNOWN_INGREDIENTS = {
    'aloe', 'apium', 'asarum', 'rosa', 'crocus', 'piper', 'mastix',
    'myrrha', 'nardus', 'costus', 'sal', 'mel', 'cera', 'oleum',
    'aqua', 'aquam', 'vinum', 'acetum', 'thus', 'camphora', 'opium',
    'cassia', 'cinnamomum', 'galanga', 'cubeba', 'senna', 'ruta',
    'salvia', 'plantago', 'absinthium', 'artemisia', 'cuminum',
    'foeniculum', 'petroselinum', 'glycyrrhiza', 'viola', 'papaver',
    'santalum', 'storax', 'euphorbium', 'aristolochia', 'olibanum',
    'ferrum', 'cuprum', 'argentum', 'sulfur', 'resina', 'gummi',
    # Italian vernacular
    'pepe', 'lilie', 'sapa', 'sapam',
}


def decode_best(word, pipeline, beam=20):
    """Decode a word and return best result."""
    if len(word) < 2:
        result = pipeline.decode_word(word)
        return result.latin, 0, False, ''

    paths = decode_root(word, pipeline.hmm, top_k=beam)
    best_latin = '?'
    best_freq = 0
    best_perseus = False

    for vp in paths:
        if not vp.latin:
            continue
        clean = vp.latin.replace(' ', '').lower()
        freq = pipeline.corpus.freq(clean)
        perseus = pipeline.dictionary.is_valid(clean)

        if perseus and (not best_perseus or freq > best_freq):
            best_latin = vp.latin
            best_freq = freq
            best_perseus = True
        elif not best_perseus and freq > best_freq:
            best_latin = vp.latin
            best_freq = freq

    is_ingredient = best_latin.lower().replace(' ', '') in KNOWN_INGREDIENTS
    return best_latin, best_freq, best_perseus, 'ingredient' if is_ingredient else ''


def main():
    config = Config()
    pipeline = VoynichPipeline(config)
    pipeline.load()

    print("=" * 90)
    print("TEST EVA VARIANTS — Impact on pharmaceutical ingredient detection")
    print("=" * 90)
    print()

    # Test on f103r (best pharma page)
    zl_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'transcriptions', 'ZL.txt')
    folio_data = parse_folio_with_variants(zl_path, 'f103r', include_confusions=True)

    total_words = 0
    improved_words = 0
    new_ingredients = 0
    new_perseus = 0

    print(f"Folio f103r: {len(folio_data)} lines")
    print()

    improvements = []

    for lnum in sorted(folio_data.keys()):
        word_list = folio_data[lnum]
        for primary, variants in word_list:
            if len(primary) < 2:
                continue
            total_words += 1

            # Decode primary
            p_latin, p_freq, p_perseus, p_ingr = decode_best(primary, pipeline)

            # Decode all variants
            best_var = None
            best_var_latin = p_latin
            best_var_freq = p_freq
            best_var_perseus = p_perseus
            best_var_ingr = p_ingr

            for variant in variants:
                if variant.eva == primary:
                    continue
                v_latin, v_freq, v_perseus, v_ingr = decode_best(variant.eva, pipeline)

                # Is this variant BETTER?
                better = False
                if v_ingr and not p_ingr:
                    better = True  # Found an ingredient!
                elif v_perseus and not p_perseus:
                    better = True  # Found a Perseus word
                elif v_perseus and p_perseus and v_freq > p_freq * 2:
                    better = True  # Much higher frequency

                if better:
                    best_var = variant
                    best_var_latin = v_latin
                    best_var_freq = v_freq
                    best_var_perseus = v_perseus
                    best_var_ingr = v_ingr

            if best_var and best_var.eva != primary:
                improved_words += 1
                if best_var_ingr and not p_ingr:
                    new_ingredients += 1
                if best_var_perseus and not p_perseus:
                    new_perseus += 1

                improvements.append({
                    'line': lnum,
                    'primary': primary,
                    'primary_decode': p_latin,
                    'primary_perseus': p_perseus,
                    'variant': best_var.eva,
                    'variant_decode': best_var_latin,
                    'variant_freq': best_var_freq,
                    'variant_perseus': best_var_perseus,
                    'variant_source': best_var.source,
                    'is_ingredient': best_var_ingr,
                })

    # Report
    print(f"Total content words: {total_words}")
    print(f"Words improved by variants: {improved_words} ({improved_words*100//max(total_words,1)}%)")
    print(f"New ingredients found: {new_ingredients}")
    print(f"New Perseus words: {new_perseus}")
    print()

    if improvements:
        print("IMPROVEMENTS FOUND:")
        print()
        print(f"{'Line':>5} {'Primary':>12} {'Decode':>15} {'P?':>3} → {'Variant':>12} {'Decode':>15} {'Freq':>6} {'P?':>3} {'Source':>20} {'Ingr':>5}")
        print("-" * 120)
        for imp in improvements:
            p_mark = 'P' if imp['primary_perseus'] else '-'
            v_mark = 'P' if imp['variant_perseus'] else '-'
            i_mark = '***' if imp['is_ingredient'] else ''
            print(f"{imp['line']:>5} {imp['primary']:>12} {imp['primary_decode']:>15} {p_mark:>3} → "
                  f"{imp['variant']:>12} {imp['variant_decode']:>15} {imp['variant_freq']:>6} {v_mark:>3} "
                  f"{imp['variant_source']:>20} {i_mark:>5}")

    # Also test on L04 variants
    print()
    print("=" * 90)
    print("L04 VARIANT TEST")
    print("=" * 90)
    print()

    l04_words = ['daiin','otey','ofeeey','shes','okeeod','lkeeol','dkedar',
                 'yf','aros','chedaiin','eeety','deeodal','vo','tchor',
                 'kedar','dal','aiin','otal','daro']

    for word in l04_words:
        variants = get_word_variants(word, include_confusions=True)
        p_latin, p_freq, p_perseus, p_ingr = decode_best(word, pipeline)

        found_better = False
        for v in variants:
            if v.eva == word:
                continue
            v_latin, v_freq, v_perseus, v_ingr = decode_best(v.eva, pipeline)
            if (v_ingr and not p_ingr) or (v_perseus and not p_perseus) or (v_freq > p_freq * 3):
                print(f"  {word:12s} ({p_latin:12s} f={p_freq:4d}) → {v.eva:12s} ({v_latin:12s} f={v_freq:4d}) [{v.source}] {'INGREDIENT' if v_ingr else ''}")
                found_better = True

        if not found_better and len(word) >= 3:
            # Show anyway for context
            pass


if __name__ == '__main__':
    main()
