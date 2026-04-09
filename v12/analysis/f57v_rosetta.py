"""
f57v ROSETTA STONE ANALYSIS

If f57v is a pharmaceutical volvelle (like Ashmole 370), then:
- L02 (outer ring, 54 words) = calendar/zodiac labels
- L03 (middle ring, 4x12) = cipher key / quadrant markers
- L04 (29 words) = lunar cycle (29.5 days)
- L05 (inner ring, 75%) = hour markers / alphabet
- L06-L13 (center) = pivot labels

We KNOW what should be on each ring. This is a CRIB ATTACK.
"""
import sys, os, re, socket
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from v12.config import Config
from v12.pipeline import VoynichPipeline
from v12.loaders.transcription import list_folios, parse_folio
from v12.stages.tokenizer import tokenize
from v12.stages.hmm_decoder import decode_root


def lemmatize(word):
    """Quick Collatinus lemma check."""
    w = word.lower().strip()
    if len(w) < 3: return w
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect(('127.0.0.1', 5555))
        s.sendall(f'-lfr {w}\n'.encode('utf-8'))
        data = s.recv(4096).decode('utf-8', errors='replace').strip()
        s.close()
        if data.startswith('*'):
            return data.split('\n')[0][:80]
        return f"[not found: {w}]"
    except:
        return f"[error: {w}]"


# Expected content for a medical volvelle
ZODIAC_SIGNS = ['aries', 'taurus', 'gemini', 'cancer', 'leo', 'virgo',
                'libra', 'scorpio', 'sagittarius', 'capricornus', 'aquarius', 'pisces']
MONTHS_LATIN = ['ianuarius', 'februarius', 'martius', 'aprilis', 'maius', 'iunius',
                'iulius', 'augustus', 'september', 'october', 'november', 'december']
PLANETS = ['saturnus', 'iupiter', 'mars', 'sol', 'venus', 'mercurius', 'luna']
HUMORS = ['sanguineus', 'cholericus', 'melancholicus', 'phlegmaticus']
QUALITIES = ['calidus', 'frigidus', 'humidus', 'siccus']
LUNAR_TERMS = ['novilunium', 'crescens', 'plenilunium', 'decrescens',
               'prima', 'secunda', 'tertia', 'quarta',
               'coniunctio', 'oppositio', 'quadratura', 'sextilis', 'trinus']
HOUR_TERMS = ['hora', 'prima', 'tertia', 'sexta', 'nona', 'vesper', 'completorium',
              'matutina', 'meridies', 'nox', 'dies']


def try_all_decodings(eva_word, pipeline, top_k=15):
    """Get ALL possible K&A decodings for a word."""
    results = []
    # HMM paths
    paths = decode_root(eva_word, pipeline.hmm, top_k=top_k)
    for vp in paths:
        if vp.latin:
            clean = vp.latin.replace(' ', '')
            freq = pipeline.corpus.freq(clean)
            perseus = pipeline.dictionary.is_valid(clean)
            results.append({
                'latin': vp.latin,
                'clean': clean,
                'logp': vp.log_prob,
                'freq': freq,
                'perseus': perseus,
            })
    return results


def check_zodiac_match(decoded_options, sign_list):
    """Check if any decoding matches a zodiac sign (fuzzy)."""
    matches = []
    for opt in decoded_options:
        clean = opt['clean'].lower()
        for sign in sign_list:
            # Exact match
            if clean == sign:
                matches.append((sign, 1.0, opt['latin']))
            # Prefix match (first 3-4 chars)
            elif len(clean) >= 3 and sign.startswith(clean[:3]):
                sim = len(clean) / len(sign)
                matches.append((sign, sim, opt['latin']))
            elif len(clean) >= 3 and clean.startswith(sign[:3]):
                sim = min(len(sign), len(clean)) / max(len(sign), len(clean))
                matches.append((sign, sim, opt['latin']))
    matches.sort(key=lambda x: -x[1])
    return matches[:3]


def main():
    config = Config()
    pipeline = VoynichPipeline(config)
    pipeline.load()

    lines, sec = parse_folio(config.transcription_path, 'f57v')
    decoded = pipeline.decode_folio(lines)

    out = []
    out.append("# f57v ROSETTA STONE ANALYSIS")
    out.append("## Volvelle medico-astrologique — Attaque par crib")
    out.append("")

    # ============================================================
    # ANALYSIS 1: L03 — THE CIPHER KEY (4 quadrants x 12 positions)
    # ============================================================
    out.append("---")
    out.append("## 1. L03 — LA CLE DU CHIFFRE (4 quadrants)")
    out.append("")

    l03_words = [dw.eva for dw in decoded[3]]
    out.append(f"Total glyphes: {len(l03_words)}")
    out.append("")

    # Split into 4 blocks by 'y' delimiter
    blocks = []
    current = []
    for g in l03_words:
        current.append(g)
        if g == 'y':
            blocks.append(current)
            current = []
    if current:
        blocks.append(current)

    out.append(f"Blocs (separes par y): {len(blocks)}")
    out.append("")

    # Alignment table
    out.append("| Position | Bloc 1 | Bloc 2 | Bloc 3 | Bloc 4 | Constant? | Logogram |")
    out.append("|----------|--------|--------|--------|--------|-----------|----------|")

    max_len = max(len(b) for b in blocks[:4])
    for pos in range(max_len):
        vals = []
        for b in blocks[:4]:
            vals.append(b[pos] if pos < len(b) else '-')
        is_const = len(set(v for v in vals if v != '-')) == 1
        const_str = "OUI" if is_const else "**VARIABLE**"
        # Check logogram
        logo = ''
        if is_const:
            test_val = vals[0]
            logo_map = {'r': 'recipe', 'v': 'vel', 'x': 'crux', 'm': 'misce',
                        'y': 'in', 'l': '?', 'k': '?', 't': '?', 'o': 'ac'}
            logo = logo_map.get(test_val, '?')
        out.append(f"| {pos:2d} | {vals[0]:6s} | {vals[1]:6s} | {vals[2]:6s} | {vals[3]:6s} | {const_str:9s} | {logo} |")

    out.append("")
    out.append("### Interpretation de la sequence fixe")
    out.append("")
    out.append("La sequence fixe de chaque quadrant est:")
    out.append("```")
    fixed = blocks[1] if len(blocks) > 1 else blocks[0]  # bloc 2 is representative
    out.append(f"  {' '.join(fixed)}")
    out.append("```")
    out.append("")

    # Try to read the fixed sequence as an instruction
    fixed_decoded = []
    for g in fixed:
        dw = pipeline.decode_word(g)
        fixed_decoded.append((g, dw.latin, dw.confidence))
    out.append("| Glyph | Decode | Conf | Interpretation possible |")
    out.append("|-------|--------|------|----------------------|")
    interpretations = {
        'o': 'ac (et/aussi) ou SEPARATEUR',
        'l': 'MARQUEUR/CHIFFRE — position fixe dans tous les quadrants',
        'r': 'RECIPE (prends) — instruction pharmaceutique',
        'v': 'VEL (ou) — alternative',
        'x': 'CRUX (marque) — symbole de reference',
        'k': 'MARQUEUR/CHIFFRE — position fixe',
        'm': 'MISCE (melange) — instruction pharmaceutique',
        'f': 'VARIABLE: f dans Q1-Q2, p dans Q3-Q4',
        'p': 'VARIABLE: remplace f dans Q3-Q4',
        't': 'MARQUEUR/CHIFFRE — position fixe',
        'y': 'IN (dans) — fin de sequence',
        'd': 'VARIABLE: remplace j dans Q2-Q4',
        'j': 'VARIABLE: uniquement Q1',
        'c': 'PREFIXE de Q3-Q4 (absent de Q1-Q2)',
    }
    for g, lat, conf in fixed_decoded:
        interp = interpretations.get(g, '?')
        out.append(f"| {g} | {lat} | {conf} | {interp} |")

    # ============================================================
    # ANALYSIS 2: L04 — LUNAR CYCLE (29 words)
    # ============================================================
    out.append("")
    out.append("---")
    out.append("## 2. L04 — CYCLE LUNAIRE (29 mots = 29 jours)")
    out.append("")

    l04_words = decoded[4]
    out.append(f"Total mots: {len(l04_words)}")
    out.append("")

    # Analyze each word for astronomical/medical content
    out.append("| Jour | EVA | Decode v12 | Collatinus | Match astro? |")
    out.append("|------|-----|-----------|------------|-------------|")

    for i, dw in enumerate(l04_words):
        day = i + 1
        # Collatinus check
        clean = dw.latin.lower().strip('_[]()? ')
        col_result = ''
        if len(clean) >= 3 and clean.isalpha():
            col_result = lemmatize(clean)

        # Check astronomical matches
        astro = ''
        clean_lower = clean.lower()
        # Special checks
        if clean_lower in ('aries', 'aros', 'ares'):
            astro = '*** ARIES? ***'
        elif clean_lower in ('luce', 'lux', 'luna'):
            astro = '*** LUX/LUNA ***'
        elif clean_lower in ('crux', 'signum'):
            astro = 'CRUX (marque)'
        elif clean_lower in ('aquam', 'aqua'):
            astro = 'AQUA'
        elif clean_lower in ('vel', 'aut'):
            astro = 'VEL (ou)'
        elif clean_lower.startswith('dur'):
            astro = 'DURUS (dur/fort)?'
        elif clean_lower.startswith('cod'):
            astro = 'CODE?'
        elif 'sol' in clean_lower:
            astro = '*** SOL? ***'
        elif clean_lower == 'te':
            astro = 'TU/TERE?'
        elif day == 15:
            astro = '(JOUR 15 = pleine lune?)'
        elif day == 1:
            astro = '(JOUR 1 = nouvelle lune?)'
        elif day == 8:
            astro = '(JOUR 8 = premier quartier?)'
        elif day == 22:
            astro = '(JOUR 22 = dernier quartier?)'

        col_short = col_result[:50] if col_result else ''
        out.append(f"| {day:2d} | {dw.eva:15s} | {dw.latin:20s} | {col_short:50s} | {astro} |")

    # ============================================================
    # ANALYSIS 3: L05 — THE INNER RING (alphabet/hours)
    # ============================================================
    out.append("")
    out.append("---")
    out.append("## 3. L05 — ANNEAU INTERIEUR (alphabet/heures)")
    out.append("")

    l05_words = decoded[5]
    out.append(f"Total elements: {len(l05_words)}")
    out.append("")

    # Separate single glyphs from multi-glyph words
    singles = [(i, dw) for i, dw in enumerate(l05_words) if len(dw.eva) <= 2]
    multis = [(i, dw) for i, dw in enumerate(l05_words) if len(dw.eva) > 2]

    out.append(f"Glyphes isoles (1-2 chars): {len(singles)}")
    out.append(f"Mots multi-glyphes: {len(multis)}")
    out.append("")

    # The single glyphs in order
    out.append("### Sequence des glyphes isoles (potentiel alphabet)")
    out.append("")
    out.append("| # | Position | EVA | K&A actuel | Hypothese heure |")
    out.append("|---|----------|-----|-----------|----------------|")

    hour_labels_24 = ['I (1h)', 'II (2h)', 'III (3h)', 'IV (4h)', 'V (5h)', 'VI (6h)',
                      'VII (7h)', 'VIII (8h)', 'IX (9h)', 'X (10h)', 'XI (11h)', 'XII (12h)',
                      'XIII (13h)', 'XIV (14h)', 'XV (15h)', 'XVI (16h)', 'XVII (17h)', 'XVIII (18h)',
                      'XIX (19h)', 'XX (20h)', 'XXI (21h)', 'XXII (22h)', 'XXIII (23h)', 'XXIV (24h)']

    for idx, (pos, dw) in enumerate(singles):
        hour = hour_labels_24[idx] if idx < len(hour_labels_24) else '?'
        ka = {'o': 'e/a/ac', 'a': 'u/a', 'l': 'es/t', 'r': 'recipe/re',
              'm': 'misce/m', 'd': 'de/in', 'c': '?', 'f': 'par/f',
              'y': 'in', 'k': 'c/qu', 'x': 'crux', 't': 'el/t',
              'ar': 'iure/ure'}.get(dw.eva, '?')
        out.append(f"| {idx+1:2d} | {pos:2d} | {dw.eva:3s} | {ka:12s} | {hour} |")

    # Check if the sequence has structure
    glyph_seq = [dw.eva for _, dw in singles]
    out.append("")
    out.append(f"Sequence complete: {' '.join(glyph_seq)}")
    out.append("")

    # Check for repeating sub-patterns
    out.append("### Sous-patterns repetes")
    out.append("")
    for n in [3, 4, 5, 6]:
        for i in range(len(glyph_seq) - n):
            sub = tuple(glyph_seq[i:i+n])
            # Count occurrences
            count = 0
            for j in range(len(glyph_seq) - n + 1):
                if tuple(glyph_seq[j:j+n]) == sub:
                    count += 1
            if count >= 2:
                out.append(f"  {n}-gram '{' '.join(sub)}' appears {count}x (at pos {i})")

    # ============================================================
    # ANALYSIS 4: L02 — OUTER RING (zodiac/months)
    # ============================================================
    out.append("")
    out.append("---")
    out.append("## 4. L02 — ANNEAU EXTERIEUR (zodiaque/mois?)")
    out.append("")

    l02_words = decoded[2]
    out.append(f"Total mots: {len(l02_words)}")
    out.append("")

    # Try to find zodiac sign names via alternative decodings
    out.append("### Recherche de noms zodiacaux dans les decodages alternatifs")
    out.append("")

    all_targets = ZODIAC_SIGNS + MONTHS_LATIN + PLANETS + LUNAR_TERMS
    for i, dw in enumerate(l02_words):
        if len(dw.eva) < 3:
            continue
        # Get all possible decodings
        alts = try_all_decodings(dw.eva, pipeline, top_k=20)
        # Check against zodiac/month/planet names
        matches = check_zodiac_match(alts, all_targets)
        if matches:
            best = matches[0]
            out.append(f"  L02 mot {i+1:2d}: `{dw.eva}` -> possible **{best[0]}** "
                       f"(sim={best[1]:.0%}, via '{best[2]}')")

    # ============================================================
    # ANALYSIS 5: Cross-reference with actual zodiac pages
    # ============================================================
    out.append("")
    out.append("---")
    out.append("## 5. CROSS-REFERENCE: Pages zodiaque (f70v-f73v)")
    out.append("")
    out.append("Les pages zodiacales montrent les 12 signes ILLUSTRES.")
    out.append("Si f57v est un volvelle, ses labels devraient matcher ceux des pages Z.")
    out.append("")

    zodiac_folios = ['f70v1','f70v2','f71r','f71v','f72r1','f72r2','f72r3',
                     'f72v1','f72v2','f72v3','f73r','f73v']
    zodiac_first_words = []

    for fid in zodiac_folios:
        zlines, zsec = parse_folio(config.transcription_path, fid)
        if not zlines:
            continue
        first_line = min(zlines.keys())
        first_words_eva = zlines[first_line][:3]
        zdecoded = pipeline.decode_folio(zlines)
        first_decoded = zdecoded[first_line][:3]

        out.append(f"  **{fid}**: {' '.join(w for w in first_words_eva)}")
        for dw in first_decoded:
            out.append(f"    {dw.eva:15s} -> {dw.latin:20s} [{dw.confidence}]")
        zodiac_first_words.append((fid, first_words_eva, first_decoded))

    # Check if zodiac page words appear in f57v
    out.append("")
    out.append("### Mots communs entre f57v L02 et pages zodiaque")
    out.append("")

    f57v_eva_set = set(dw.eva for dw in l02_words)
    for fid, first_eva, first_dec in zodiac_first_words:
        common = set(first_eva) & f57v_eva_set
        if common:
            out.append(f"  {fid} partage avec f57v: {common}")

    # ============================================================
    # ANALYSIS 6: Center labels (L06-L13)
    # ============================================================
    out.append("")
    out.append("---")
    out.append("## 6. CENTRE DU VOLVELLE (L06-L13)")
    out.append("")

    for lnum in range(6, 14):
        if lnum not in decoded:
            continue
        for dw in decoded[lnum]:
            col = lemmatize(dw.latin.strip('_[]()? ')) if len(dw.latin) >= 3 else ''
            out.append(f"  L{lnum:02d}: `{dw.eva}` -> `{dw.latin}` [{dw.confidence}] {col[:60]}")

    # ============================================================
    # SYNTHESIS
    # ============================================================
    out.append("")
    out.append("---")
    out.append("## 7. SYNTHESE — f57v comme cle de dechiffrement")
    out.append("")
    out.append("### Structure du volvelle")
    out.append("")
    out.append("| Anneau | Contenu | Elements | Parallele Ashmole 370 |")
    out.append("|--------|---------|----------|----------------------|")
    out.append(f"| L02 (ext) | Calendrier/Zodiaque | {len(l02_words)} mots | Disque 1: mois + signes |")
    out.append(f"| L03 (mid) | Cle du chiffre | 4x12+3 glyphes | Marqueurs de quadrant |")
    out.append(f"| L04 (int-mid) | Cycle lunaire | {len(l04_words)} mots | Disque 2: age lunaire |")
    out.append(f"| L05 (int) | Heures/alphabet | {len(l05_words)} elements | Disque 3: cadran horaire |")
    out.append(f"| L06-13 (centre) | Labels pivot | 8 mots | Pivot central |")

    # Write
    report = '\n'.join(out)
    out_path = os.path.join(os.path.dirname(__file__), '..', 'output', 'F57V_ROSETTA.md')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"Report: {out_path}")
    print(f"Analyzed {sum(len(decoded[l]) for l in decoded)} words across {len(decoded)} rings")


if __name__ == '__main__':
    main()
