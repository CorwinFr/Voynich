"""
REVERSE K&A HUNT — Find ingredients by going backwards:
Latin ingredient → K&A inverse → expected EVA pattern → search manuscript.

This is the Turing approach: start from known plaintext, find the cipher.
"""
import sys, os, re
from collections import Counter, defaultdict
from pathlib import Path
from itertools import product

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from v12.config import Config
from v12.pipeline import VoynichPipeline
from v12.loaders.transcription import list_folios, parse_folio
from v12.stages.hmm_decoder import decode_root


# REVERSE K&A MAPPING: Latin letter → possible EVA glyphs
# Each Latin letter can be encoded by one or more EVA glyphs
LATIN_TO_EVA = {
    'a': ['a', 'o'],          # a→a (minority), o→a (via o=e/a)
    'b': [],                   # b not in K&A (confirmed)
    'c': ['k'],                # k→c/qu
    'd': ['d'],                # d→d
    'e': ['o', 'ee', 'e'],     # o→e (majority), ee→oe/e
    'f': [],                   # f not directly mapped
    'g': ['g'],                # rare
    'h': [],                   # h silent (confirmed)
    'i': ['ch', 'y'],          # ch→i, y→i (minority)
    'l': ['l', 't'],           # l→l, t→l/el
    'k': ['k'],                # k→c/qu → could also be k
    'm': ['m'],                # m→m
    'n': ['n'],                # n→n
    'o': ['o', 'ee'],          # o→o, ee→oe/o
    'p': ['p', 'f'],           # p→per, f→par → p consonant
    'q': ['k'],                # qu→k
    'r': ['r'],                # r→r
    's': ['s', 'sh'],          # s→s/us, sh→ci/s?
    't': ['t', 'd'],           # t→t (via T-trigger or minority)
    'u': ['a', 'o'],           # u→u/a
    'v': ['v'],                # v→vel
    'x': ['x'],                # x→crux
    'y': ['y'],                # y→i/in
    'z': [],                   # not in EVA
}

# Missing ingredients from Aurea Alexandrina + other key Antidotarium ingredients
TARGET_INGREDIENTS = {
    # Aurea Alexandrina missing
    'croci': 'saffron',
    'piperis': 'pepper',
    'cinamomi': 'cinnamon',
    'mellis': 'honey',
    'masticis': 'mastic',
    'petrosellini': 'parsley',
    # Other important ingredients
    'galangae': 'galangal',
    'nardi': 'nard',
    'cassiae': 'cassia',
    'myrrhae': 'myrrh',
    'zingiber': 'ginger',
    'cumini': 'cumin',
    'costi': 'costus',
    'feniculi': 'fennel',
    'absinthii': 'wormwood',
    'rosae': 'rose',
    'salviae': 'sage',
    'mentae': 'mint',
    'rutae': 'rue',
    'violae': 'violet',
    'lilii': 'lily',
    'opii': 'opium',
    'succum': 'juice',
    'sapam': 'must-syrup',
    'butyri': 'butter',
    # Shorter forms
    'crocus': 'saffron',
    'piper': 'pepper',
    'cassia': 'cassia',
    'myrrha': 'myrrh',
    'nardus': 'nard',
    'costus': 'costus',
    'rosa': 'rose',
    'salvia': 'sage',
    'menta': 'mint',
    'ruta': 'rue',
    'viola': 'violet',
}


def latin_to_eva_patterns(latin_word, max_patterns=200):
    """
    Convert a Latin word to all possible EVA patterns via reverse K&A.
    Returns list of EVA strings.
    """
    options_per_char = []
    i = 0
    word = latin_word.lower()

    while i < len(word):
        ch = word[i]
        # Handle digraphs
        if ch == 'q' and i+1 < len(word) and word[i+1] == 'u':
            options_per_char.append(['k'])
            i += 2
            continue

        opts = LATIN_TO_EVA.get(ch, [])
        if not opts:
            # Skip unmappable letters (h, b, f, z)
            i += 1
            continue

        options_per_char.append(opts)
        i += 1

    if not options_per_char:
        return []

    # Generate all combinations (limited)
    patterns = []
    count = 1
    for opts in options_per_char:
        count *= len(opts)
    if count > max_patterns:
        # Too many — use only first option per position
        patterns.append(''.join(opts[0] for opts in options_per_char))
        # And try swapping one position at a time
        base = [opts[0] for opts in options_per_char]
        for i, opts in enumerate(options_per_char):
            for opt in opts[1:]:
                variant = base.copy()
                variant[i] = opt
                patterns.append(''.join(variant))
    else:
        for combo in product(*options_per_char):
            patterns.append(''.join(combo))

    return list(set(patterns))


def search_patterns_in_manuscript(patterns, folios_data):
    """Search for EVA patterns across the entire manuscript."""
    matches = []
    pattern_set = set(patterns)

    for fid, section, lines in folios_data:
        for lnum, words in lines.items():
            for i, w in enumerate(words):
                w_lower = w.lower()
                # Exact match
                if w_lower in pattern_set:
                    ctx_b = words[i-1] if i > 0 else '-'
                    ctx_a = words[i+1] if i < len(words)-1 else '-'
                    matches.append((fid, section, lnum, i, w, ctx_b, ctx_a, 'EXACT'))
                # Substring match (pattern is contained in word)
                else:
                    for pat in patterns:
                        if len(pat) >= 3 and pat in w_lower and len(w_lower) - len(pat) <= 3:
                            ctx_b = words[i-1] if i > 0 else '-'
                            ctx_a = words[i+1] if i < len(words)-1 else '-'
                            matches.append((fid, section, lnum, i, w, ctx_b, ctx_a, f'CONTAINS({pat})'))
                            break

    return matches


def main():
    config = Config()
    pipeline = VoynichPipeline(config)
    pipeline.load()

    # Load all folios
    folios = list_folios(config.transcription_path)
    folios_data = []
    for fid, section in folios:
        lines, sec = parse_folio(config.transcription_path, fid)
        if lines:
            folios_data.append((fid, section or '?', lines))

    total_words = sum(sum(len(ws) for ws in lines.values()) for _, _, lines in folios_data)
    print(f"Manuscript: {len(folios_data)} folios, {total_words} words")

    out = []
    out.append("# REVERSE K&A INGREDIENT HUNT")
    out.append(f"## {len(TARGET_INGREDIENTS)} target ingredients x {len(folios_data)} folios")
    out.append("")

    all_results = []

    for ingredient, english in sorted(TARGET_INGREDIENTS.items()):
        # Generate EVA patterns
        patterns = latin_to_eva_patterns(ingredient)

        if not patterns:
            out.append(f"### {ingredient} ({english}) — SKIPPED (unmappable letters)")
            out.append("")
            continue

        # Search in manuscript
        matches = search_patterns_in_manuscript(patterns, folios_data)

        if matches:
            out.append(f"### {ingredient} ({english}) — {len(matches)} MATCHES")
            out.append(f"  EVA patterns tested: {patterns[:10]}{'...' if len(patterns) > 10 else ''}")
            out.append("")

            # Verify: decode each match and check if K&A produces the ingredient
            verified = []
            for fid, sec, lnum, pos, eva_word, ctx_b, ctx_a, match_type in matches[:20]:
                # Try to decode this EVA word
                hmm_paths = decode_root(eva_word, pipeline.hmm, top_k=50)
                found_ingr = False
                for vp in hmm_paths:
                    if not vp.latin:
                        continue
                    clean = vp.latin.replace(' ', '').lower()
                    if clean == ingredient or clean.startswith(ingredient[:4]):
                        found_ingr = True
                        verified.append((fid, sec, lnum, eva_word, clean, ctx_b, ctx_a))
                        break

                std_decode = pipeline.decode_word(eva_word)
                out.append(f"  {fid:8s} [{sec}] L{lnum:02d}: `{eva_word}` std={std_decode.latin:20s} "
                          f"match={match_type:15s} verified={'YES' if found_ingr else 'no':4s} "
                          f"ctx: {ctx_b}/{ctx_a}")

            if verified:
                all_results.append((ingredient, english, verified))
                out.append(f"  **VERIFIED: {len(verified)} occurrences**")
            out.append("")
        else:
            out.append(f"### {ingredient} ({english}) — 0 matches")
            out.append(f"  EVA patterns: {patterns[:5]}")
            out.append("")

    # Summary
    out.append("---")
    out.append("# SUMMARY")
    out.append("")
    out.append(f"Total ingredients searched: {len(TARGET_INGREDIENTS)}")
    out.append(f"Ingredients with verified matches: {len(all_results)}")
    out.append("")

    if all_results:
        out.append("| Ingredient | English | Verified occurrences | Top folio |")
        out.append("|-----------|---------|---------------------|-----------|")
        for ingr, eng, verified in sorted(all_results, key=lambda x: -len(x[2])):
            top_fid = verified[0][0]
            out.append(f"| {ingr} | {eng} | {len(verified)} | {top_fid} |")

    # Combined with previous session results
    out.append("")
    out.append("## COMPLETE INGREDIENT LIST (all methods combined)")
    out.append("")
    all_ingr = {'aloe', 'aloes', 'ture', 'turis', 'sal', 'olei', 'oleo',
                'aceto', 'cerae', 'cera', 'asari', 'iecur', 'succi',
                'hiera', 'cicura', 'rens', 'aquam', 'equaliter'}
    for ingr, eng, verified in all_results:
        all_ingr.add(ingr)

    out.append(f"Total unique ingredients identified: {len(all_ingr)}")
    for ingr in sorted(all_ingr):
        out.append(f"  - {ingr}")

    # Write
    report = '\n'.join(out)
    out_path = os.path.join(os.path.dirname(__file__), '..', 'output', 'REVERSE_KA_HUNT.md')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\nReport: {out_path}")
    print(f"Verified ingredients: {len(all_results)}")
    for ingr, eng, verified in all_results:
        print(f"  {ingr} ({eng}): {len(verified)} occurrences")


if __name__ == '__main__':
    main()
