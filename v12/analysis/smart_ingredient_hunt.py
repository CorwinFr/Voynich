"""
SMART INGREDIENT HUNT — Find ingredients using medieval apothecary logic:
1. Synonyms and abbreviations (canella for cinnamomum, petro for petroselinum)
2. Consonant substitution (b→p, f→p, g→k)
3. Drop double consonants (myrrha→myra, mellis→melis)
4. Arabic/Italian names (za'faran, pepe, cannella)
5. Already-decoded words that might be misread ingredients
"""
import sys, os, re
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from v12.config import Config
from v12.pipeline import VoynichPipeline
from v12.loaders.transcription import list_folios, parse_folio
from v12.stages.hmm_decoder import decode_root


# EXPANDED ingredient list with synonyms, abbreviations, Arabic names
# Format: search_term -> (real_ingredient, language, notes)
SMART_TARGETS = {
    # CROCUS/SAFFRON — the hardest one
    'croco': ('crocus', 'Latin ablative', 'most common recipe form'),
    'croci': ('crocus', 'Latin genitive', 'Aurea Alexandrina form'),
    'crocum': ('crocus', 'Latin accusative', ''),
    'karkom': ('crocus', 'Arabic/Hebrew', 'karkom = saffron'),

    # PIPER/PEPPER
    'piper': ('piper', 'Latin', 'standard'),
    'pipere': ('piper', 'Latin ablative', 'in recipes'),
    'pepe': ('piper', 'Italian', 'vernacular'),
    'pilpil': ('piper', 'Arabic', 'filfil without f'),

    # CINNAMOMUM/CINNAMON
    'canela': ('cinnamomum', 'Italian/Spanish', 'common vernacular'),
    'canella': ('cinnamomum', 'Italian', 'with double-l simplified'),
    'cinamo': ('cinnamomum', 'Latin abbreviated', 'short form'),
    'casia': ('cassia', 'Latin simplified', 'drop double-s'),
    'kirpa': ('cinnamomum', 'Arabic qirfa', 'b→p substitution'),

    # MELLIS/HONEY
    'mel': ('mel', 'Latin', 'nominative, 3 letters'),
    'mele': ('mel', 'Latin ablative', ''),
    'meli': ('mel', 'Latin dative', ''),
    'melis': ('mel', 'Latin simplified', 'drop double-l'),
    'asal': ('mel', 'Arabic', 'asal = honey'),

    # MASTICIS/MASTIC
    'mastic': ('mastix', 'Latin stem', ''),
    'mastice': ('mastix', 'Latin ablative', ''),
    'mastica': ('mastix', 'Latin', ''),

    # MYRRHA
    'myra': ('myrrha', 'Latin simplified', 'drop double-r'),
    'mira': ('myrrha', 'Latin variant', 'common medieval'),
    'mura': ('myrrha', 'Arabic murr', 'simplified'),
    'mure': ('myrrha', 'Latin/Arabic', ''),

    # GALANGA
    'kalanka': ('galanga', 'Arabic', 'g→k substitution'),
    'kalanga': ('galanga', 'Arabic/Latin', 'g→k'),

    # NARDUS/NARD — should be encodable
    'nardo': ('nardus', 'Latin ablative', ''),
    'nardi': ('nardus', 'Latin genitive', 'Antidotarium form'),

    # ZINGIBER/GINGER
    'kinkiper': ('zingiber', 'Arabic', 'g→k, z→k substitution'),

    # FENICULUM/FENNEL
    'penicolo': ('feniculum', 'Italian', 'f→p substitution'),
    'penucolo': ('feniculum', 'Latin/Italian', 'f→p'),

    # ROSA/ROSE — simple
    'rosa': ('rosa', 'Latin', ''),
    'rose': ('rosa', 'Latin', ''),
    'rosarum': ('rosa', 'Latin genitive plural', ''),

    # VIOLA/VIOLET
    'viola': ('viola', 'Latin', ''),
    'viole': ('viola', 'Latin', ''),

    # COSTUS
    'costo': ('costus', 'Latin ablative', ''),
    'costi': ('costus', 'Latin genitive', ''),

    # CUMINUM/CUMIN
    'cumino': ('cuminum', 'Latin ablative', ''),
    'kamun': ('cuminum', 'Arabic', ''),

    # ALUMEN
    'alumen': ('alumen', 'Latin', 'alum'),
    'alumine': ('alumen', 'Latin ablative', ''),

    # ADDITIONAL from Antidotarium
    'elleporo': ('elleborus', 'Latin simplified', 'hellebore, h silent, b→p'),
    'ellepori': ('elleborus', 'Latin gen.', 'h silent, b→p'),
    'purekio': ('pulegium', 'Latin', 'pennyroyal, g→k'),
    'mentam': ('menta', 'Latin acc.', 'mint'),
    'apsintion': ('absinthium', 'Greek/Latin', 'b→p'),
    'opium': ('opium', 'Latin', ''),
    'opio': ('opium', 'Latin ablative', ''),

    # LIQUIDS and bases
    'aceto': ('acetum', 'Latin ablative', 'vinegar'),
    'lactis': ('lac', 'Latin genitive', 'milk'),
    'lacte': ('lac', 'Latin ablative', 'milk'),
    'sapa': ('sapa', 'Latin', 'must syrup'),
}


def latin_to_eva_simple(latin_word):
    """Convert Latin to EVA using simple reverse K&A. Returns list of patterns."""
    REVERSE = {
        'a': ['a', 'o'], 'b': ['p'], 'c': ['k'], 'd': ['d'],
        'e': ['o', 'ee'], 'f': ['p', 'f'], 'g': ['k'],
        'h': [], 'i': ['ch', 'y'], 'k': ['k'],
        'l': ['l', 't'], 'm': ['m'], 'n': ['n'],
        'o': ['o', 'ee'], 'p': ['p', 'f'], 'q': ['k'],
        'r': ['r'], 's': ['s', 'sh'], 't': ['t', 'd'],
        'u': ['a', 'o'], 'v': ['v'], 'x': ['x'],
        'y': ['y'], 'z': ['k', 's'],
    }

    options = []
    i = 0
    word = latin_word.lower()
    while i < len(word):
        ch = word[i]
        if ch == 'q' and i+1 < len(word) and word[i+1] == 'u':
            options.append(['k'])
            i += 2
            continue
        # Skip doubled consonants (use single)
        if i+1 < len(word) and word[i] == word[i+1] and word[i] not in 'aeiou':
            i += 1
            continue
        opts = REVERSE.get(ch, [ch])
        if opts:
            options.append(opts)
        i += 1

    if not options:
        return []

    # Generate patterns (limit combinations)
    from itertools import product
    count = 1
    for o in options:
        count *= len(o)

    if count <= 100:
        return [''.join(combo) for combo in product(*options)]
    else:
        # Just use first option + single swaps
        base = [o[0] for o in options]
        patterns = [''.join(base)]
        for i, opts in enumerate(options):
            for opt in opts[1:]:
                v = base.copy()
                v[i] = opt
                patterns.append(''.join(v))
        return list(set(patterns))


def main():
    config = Config()
    pipeline = VoynichPipeline(config)
    pipeline.load()

    folios = list_folios(config.transcription_path)

    # Build word index for fast searching
    word_index = defaultdict(list)  # eva_word -> [(fid, sec, lnum, pos)]
    for fid, section in folios:
        lines, sec = parse_folio(config.transcription_path, fid)
        if not lines:
            continue
        for lnum, words in lines.items():
            for i, w in enumerate(words):
                word_index[w.lower()].append((fid, section or '?', lnum, i))

    print(f"Word index: {len(word_index)} unique EVA words")

    out = []
    out.append("# SMART INGREDIENT HUNT")
    out.append(f"## {len(SMART_TARGETS)} targets (synonyms, Arabic, abbreviations)")
    out.append("")

    all_hits = []

    for search_term, (real_ingr, language, notes) in sorted(SMART_TARGETS.items()):
        # Generate EVA patterns
        patterns = latin_to_eva_simple(search_term)
        if not patterns:
            continue

        # Search in word index
        matches = []
        for pat in patterns:
            # Exact match
            if pat in word_index:
                for fid, sec, lnum, pos in word_index[pat]:
                    matches.append((fid, sec, lnum, pos, pat, 'EXACT'))
            # Also check if pattern is contained in longer words
            for eva_word, locs in word_index.items():
                if len(eva_word) >= len(pat) + 1 and len(eva_word) <= len(pat) + 4:
                    if pat in eva_word:
                        for fid, sec, lnum, pos in locs[:3]:  # limit
                            matches.append((fid, sec, lnum, pos, eva_word, f'IN({pat})'))

        if not matches:
            continue

        # Verify: does HMM produce the ingredient from this EVA?
        verified = []
        unverified = []
        seen_eva = set()

        for fid, sec, lnum, pos, eva_word, match_type in matches[:30]:
            if eva_word in seen_eva:
                continue
            seen_eva.add(eva_word)

            hmm_paths = decode_root(eva_word, pipeline.hmm, top_k=50)
            found = False
            for vp in hmm_paths:
                if not vp.latin:
                    continue
                clean = vp.latin.replace(' ', '').lower()
                # Check if any K&A path produces the search term or real ingredient
                if (clean == search_term or clean == real_ingr or
                    clean.startswith(search_term[:4]) or
                    clean.startswith(real_ingr[:4])):
                    verified.append((fid, sec, lnum, eva_word, clean, match_type))
                    found = True
                    break

            if not found:
                # Also check standard decode
                std = pipeline.decode_word(eva_word)
                unverified.append((fid, sec, lnum, eva_word, std.latin, match_type))

        if verified:
            all_hits.append((search_term, real_ingr, language, notes, verified))
            out.append(f"### {search_term} = {real_ingr} ({language}) — **{len(verified)} VERIFIED**")
            for fid, sec, lnum, eva, ka, mt in verified[:10]:
                out.append(f"  {fid:8s} [{sec}] L{lnum:02d}: `{eva}` -> `{ka}` ({mt})")
            out.append("")
        elif unverified and len(matches) >= 2:
            out.append(f"### {search_term} = {real_ingr} ({language}) — {len(matches)} pattern matches, 0 verified")
            for fid, sec, lnum, eva, std, mt in unverified[:5]:
                out.append(f"  {fid:8s} [{sec}] L{lnum:02d}: `{eva}` std=`{std}` ({mt})")
            out.append("")

    # Summary
    out.append("---")
    out.append("# SUMMARY")
    out.append("")
    out.append(f"Targets searched: {len(SMART_TARGETS)}")
    out.append(f"**Verified ingredient matches: {len(all_hits)}**")
    out.append("")

    if all_hits:
        out.append("| Search term | Real ingredient | Language | Verified | Notes |")
        out.append("|------------|----------------|----------|----------|-------|")
        for term, ingr, lang, notes, verified in all_hits:
            out.append(f"| {term} | {ingr} | {lang} | {len(verified)}x | {notes} |")

    # Complete ingredient list
    out.append("")
    out.append("## MASTER INGREDIENT LIST (all sessions combined)")
    out.append("")
    all_ingr = {'aloe', 'aloes', 'ture', 'turis', 'sal', 'olei', 'oleo',
                'aceto', 'cerae', 'cera', 'asari', 'iecur', 'succi', 'sapam',
                'hiera', 'cicura', 'rens', 'aquam', 'equaliter',
                'coquo', 'coque', 'tere', 'recipe', 'misce', 'cola'}
    for term, ingr, lang, notes, verified in all_hits:
        all_ingr.add(ingr)
        all_ingr.add(term)

    out.append(f"**Total unique terms: {len(all_ingr)}**")
    for ingr in sorted(all_ingr):
        out.append(f"  - {ingr}")

    # Write
    report = '\n'.join(out)
    out_path = os.path.join(os.path.dirname(__file__), '..', 'output', 'SMART_INGREDIENT_HUNT.md')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\nReport: {out_path}")
    print(f"Verified hits: {len(all_hits)}")
    for term, ingr, lang, notes, verified in all_hits:
        print(f"  {term} = {ingr} ({lang}): {len(verified)}x")


if __name__ == '__main__':
    main()
