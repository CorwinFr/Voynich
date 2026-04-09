"""
ZODIAC CRIB ATTACK — Use known zodiac sign identifications from illustrations
to create a crib (known plaintext) and crack the cipher.

Known mapping (from illustrations, widely accepted):
  f70v1 = PISCES (Mars)
  f70v2 = ARIES (dark, Mars/Avril)
  f71r  = ARIES (light, Avril)
  f71v  = TAURUS (dark, Avril/Mai)
  f72r1 = TAURUS (light, Mai)
  f72r2 = GEMINI (Mai/Juin)
  f72r3 = GEMINI (Juin)
  f72v1 = CANCER (Juin/Juillet)
  f72v2 = LEO (Juillet/Août)
  f72v3 = VIRGO (Août/Septembre)
  f73r  = LIBRA (Septembre/Octobre)
  f73v  = SCORPIO (Octobre/Novembre)
  (missing: SAGITTARIUS, CAPRICORNUS, AQUARIUS)

Month names are written in the margins in Latin-like script.
The FIRST WORD of each zodiac page may be the sign name in EVA cipher.

Strategy:
1. Extract the first few words of each zodiac page
2. Decode them through ALL K&A paths (not just the best)
3. Check if ANY path produces the expected zodiac sign name
4. If match found → we have a CONFIRMED K&A path for that word
5. Use confirmed paths to improve the entire manuscript decode
"""
import sys, os, socket, re
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from v12.config import Config
from v12.pipeline import VoynichPipeline
from v12.loaders.transcription import list_folios, parse_folio
from v12.stages.hmm_decoder import decode_root
from v12.stages.tokenizer import tokenize, preprocess_triples


# Known zodiac assignments from illustrations
ZODIAC_PAGES = {
    'f70v1': {'sign': 'pisces', 'month': 'martius', 'latin_sign': 'pisces'},
    'f70v2': {'sign': 'aries', 'month': 'martius', 'latin_sign': 'aries'},
    'f71r':  {'sign': 'aries', 'month': 'aprilis', 'latin_sign': 'aries'},
    'f71v':  {'sign': 'taurus', 'month': 'aprilis', 'latin_sign': 'taurus'},
    'f72r1': {'sign': 'taurus', 'month': 'maius', 'latin_sign': 'taurus'},
    'f72r2': {'sign': 'gemini', 'month': 'maius', 'latin_sign': 'gemini'},
    'f72r3': {'sign': 'gemini', 'month': 'iunius', 'latin_sign': 'gemini'},
    'f72v1': {'sign': 'cancer', 'month': 'iunius', 'latin_sign': 'cancer'},
    'f72v2': {'sign': 'leo', 'month': 'iulius', 'latin_sign': 'leo'},
    'f72v3': {'sign': 'virgo', 'month': 'augustus', 'latin_sign': 'virgo'},
    'f73r':  {'sign': 'libra', 'month': 'september', 'latin_sign': 'libra'},
    'f73v':  {'sign': 'scorpio', 'month': 'october', 'latin_sign': 'scorpius'},
}

# Also try medieval Latin variants
SIGN_VARIANTS = {
    'pisces': ['pisces', 'piscis', 'pisc'],
    'aries': ['aries', 'aris', 'aros', 'ariet'],
    'taurus': ['taurus', 'taur', 'torus'],
    'gemini': ['gemini', 'gemin'],
    'cancer': ['cancer', 'cancr'],
    'leo': ['leo', 'leon', 'leoni'],
    'virgo': ['virgo', 'virgini', 'virg'],
    'libra': ['libra', 'libre', 'libr'],
    'scorpio': ['scorpio', 'scorpius', 'scorp'],
    'sagittarius': ['sagittarius', 'sagitt'],
    'capricornus': ['capricornus', 'capric'],
    'aquarius': ['aquarius', 'aquari'],
}

MONTH_VARIANTS = {
    'martius': ['martius', 'mars', 'marc', 'marti'],
    'aprilis': ['aprilis', 'april', 'apri'],
    'maius': ['maius', 'mai', 'maij'],
    'iunius': ['iunius', 'iuni', 'juni'],
    'iulius': ['iulius', 'iuli', 'juli'],
    'augustus': ['augustus', 'augst', 'augu'],
    'september': ['september', 'septemb', 'sept'],
    'october': ['october', 'octob', 'octo'],
    'november': ['november', 'novemb'],
    'december': ['december', 'decemb'],
}


def fuzzy_match(candidate, targets, threshold=0.6):
    """Check if candidate matches any target (fuzzy)."""
    c = candidate.lower().strip()
    if len(c) < 3:
        return []
    matches = []
    for target in targets:
        t = target.lower()
        # Exact
        if c == t:
            matches.append((t, 1.0))
            continue
        # Prefix match
        min_len = min(len(c), len(t))
        if min_len >= 3:
            matching = sum(1 for a, b in zip(c, t) if a == b)
            sim = matching / max(len(c), len(t))
            if sim >= threshold:
                matches.append((t, sim))
        # Subsequence
        if len(c) >= 4 and len(t) >= 4:
            i = j = match = 0
            while i < len(c) and j < len(t):
                if c[i] == t[j]:
                    match += 1
                    i += 1
                    j += 1
                else:
                    i += 1
                    j += 1
            sub_sim = match / max(len(c), len(t))
            if sub_sim >= threshold and (t, sub_sim) not in matches:
                matches.append((t, sub_sim))

    matches.sort(key=lambda x: -x[1])
    return matches[:3]


def main():
    config = Config()
    pipeline = VoynichPipeline(config)
    pipeline.load()

    out = []
    out.append("# ZODIAC CRIB ATTACK")
    out.append("## Utiliser les illustrations connues pour craquer le chiffre")
    out.append("")

    all_confirmed = []  # (eva, latin, sign/month, folio, similarity)

    for fid, info in ZODIAC_PAGES.items():
        sign = info['sign']
        month = info['month']
        latin_sign = info['latin_sign']

        lines, sec = parse_folio(config.transcription_path, fid)
        if not lines:
            continue

        out.append(f"---")
        out.append(f"## {fid} — Signe attendu: **{sign.upper()}** / Mois: **{month}**")
        out.append("")

        # Get first 8 words of the page
        first_line = min(lines.keys())
        first_words = lines[first_line][:8]

        out.append(f"Premiers mots EVA: `{' '.join(first_words)}`")
        out.append("")

        # For each word, try ALL K&A decodings and check against sign/month
        sign_targets = SIGN_VARIANTS.get(sign, [sign])
        month_targets = MONTH_VARIANTS.get(month, [month])
        all_targets = sign_targets + month_targets

        out.append(f"| EVA | Top decode | Alternatives K&A | Match zodiaque? |")
        out.append(f"|-----|-----------|-----------------|----------------|")

        for eva_word in first_words:
            if len(eva_word) < 3:
                continue

            # Standard decode
            std = pipeline.decode_word(eva_word)

            # ALL HMM paths
            hmm_paths = decode_root(eva_word, pipeline.hmm, top_k=30)

            best_match = None
            best_sim = 0
            all_alts = []

            for vp in hmm_paths:
                if not vp.latin:
                    continue
                clean = vp.latin.replace(' ', '').lower()
                all_alts.append(clean)

                # Check against zodiac targets
                matches = fuzzy_match(clean, all_targets, threshold=0.55)
                if matches and matches[0][1] > best_sim:
                    best_match = (clean, matches[0][0], matches[0][1])
                    best_sim = matches[0][1]

            # Also try monolithic decode
            mono_paths = decode_root(eva_word, pipeline.hmm, top_k=30)
            for vp in mono_paths:
                if not vp.latin:
                    continue
                clean = vp.latin.replace(' ', '').lower()
                matches = fuzzy_match(clean, all_targets, threshold=0.55)
                if matches and matches[0][1] > best_sim:
                    best_match = (clean, matches[0][0], matches[0][1])
                    best_sim = matches[0][1]

            # Show top 5 alternatives
            alts_str = ', '.join(all_alts[:5])

            if best_match:
                marker = f"**{best_match[1].upper()}** ({best_match[2]:.0%}) via '{best_match[0]}'"
                if best_match[2] >= 0.7:
                    all_confirmed.append((eva_word, best_match[0], best_match[1], fid, best_match[2]))
            else:
                marker = '-'

            out.append(f"| {eva_word:15s} | {std.latin:20s} | {alts_str:40s} | {marker} |")

        out.append("")

    # ============================================================
    # CONFIRMED MATCHES SUMMARY
    # ============================================================
    out.append("")
    out.append("---")
    out.append("# CONFIRMED MATCHES")
    out.append("")

    if all_confirmed:
        all_confirmed.sort(key=lambda x: -x[4])
        out.append("| EVA | K&A decode | Zodiac match | Folio | Similarity |")
        out.append("|-----|-----------|-------------|-------|-----------|")
        for eva, decode, target, fid, sim in all_confirmed:
            stars = '***' if sim >= 0.8 else '**' if sim >= 0.7 else '*'
            out.append(f"| {eva} | {decode} | {target} | {fid} | {sim:.0%} {stars} |")
    else:
        out.append("Aucun match confirme.")

    # ============================================================
    # SEARCH CONFIRMED WORDS ACROSS MANUSCRIPT
    # ============================================================
    out.append("")
    out.append("---")
    out.append("# RECHERCHE DES MOTS CONFIRMES DANS TOUT LE MANUSCRIT")
    out.append("")

    # Get all confirmed EVA words
    confirmed_eva = set(eva for eva, _, _, _, sim in all_confirmed if sim >= 0.6)

    if confirmed_eva:
        folios = list_folios(config.transcription_path)
        word_locations = defaultdict(list)

        for fid, section in folios:
            flines, sec = parse_folio(config.transcription_path, fid)
            if not flines:
                continue
            for lnum, words in flines.items():
                for w in words:
                    if w.lower() in confirmed_eva:
                        word_locations[w.lower()].append((fid, section, lnum))

        for eva_word in sorted(confirmed_eva):
            locs = word_locations.get(eva_word, [])
            match_info = next((t for e, d, t, f, s in all_confirmed if e == eva_word), '?')
            out.append(f"### `{eva_word}` (= {match_info}): {len(locs)} occurrences")
            sec_dist = Counter(s for _, s, _ in locs)
            out.append(f"  Sections: {dict(sec_dist)}")
            for fid, sec, lnum in locs[:10]:
                out.append(f"  - {fid} [{sec}] L{lnum:02d}")
            out.append("")

    # ============================================================
    # MONTH NAMES IN MARGINS
    # ============================================================
    out.append("")
    out.append("---")
    out.append("# NOMS DE MOIS (marges des pages zodiacales)")
    out.append("")
    out.append("Les noms de mois sont ecrits dans les marges en ecriture latine lisible.")
    out.append("D'apres la litterature, les mois identifiables sont:")
    out.append("  Mars, Avril, Mai, Juin, Juillet, Aout, Septembre, Octobre")
    out.append("  (Novembre, Decembre, Janvier, Fevrier sont sur les pages manquantes)")
    out.append("")
    out.append("Ces noms de mois en clair CONFIRMENT l'interpretation zodiacale")
    out.append("et fournissent un ancrage chronologique pour le volvelle de f57v.")

    # Write
    report = '\n'.join(out)
    out_path = os.path.join(os.path.dirname(__file__), '..', 'output', 'ZODIAC_CRIB_ATTACK.md')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"Report: {out_path}")
    print(f"Confirmed matches: {len(all_confirmed)}")
    for eva, decode, target, fid, sim in all_confirmed:
        print(f"  {eva} -> {decode} = {target} ({sim:.0%}) on {fid}")


if __name__ == '__main__':
    main()
