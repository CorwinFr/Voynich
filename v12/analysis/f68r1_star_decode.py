"""
F68R1 STAR LABELS — K&A decode + comparison with medieval star catalogues.

f68r1 has exactly 29 star labels. The al-Misri astrolabe (1227) has 29 star
pointers. Medieval astrolabes typically carry 20-30 named stars.

We decode via K&A (these labels ARE in VMS standard system) and compare
with known medieval star names (Arabic transliterations into Latin).
"""
import sys, os
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from v12.config import Config
from v12.pipeline import VoynichPipeline
from v12.stages.hmm_decoder import decode_root

# ── F68R1 STAR LABELS (ZL consensus) ─────────────────────────────

F68R1_STARS = [
    (8,  'okodaly'),
    (9,  'odchecthy'),
    (10, 'otcheody'),
    (11, 'okoaly'),
    (12, 'chocfhy'),
    (13, 'octhey'),
    (14, 'otshey'),
    (15, 'otydy'),
    (16, 'okear'),
    (17, 'cphocthy'),
    (18, 'ytchody'),
    (19, 'otys'),
    (20, 'olor'),
    (21, 'ockhy'),
    (22, 'ofcheor'),
    (23, 'otchdy'),
    (24, 'otykchs'),
    (25, 'otol'),
    (26, 'otor'),
    (27, 'oiinar'),
    (28, 'okoldy'),
    (29, 'ykchdy'),
    (30, 'toeeodcthy'),  # simplified from ZL markup
    (31, 'ocphy'),
    (32, 'okeeodal'),
    (33, 'okshor'),
    (34, 'osdaiin'),     # or: or.daiin (two words?)
    (35, 'otochedy'),
    (36, 'dolchedy'),
]

# ── F68R2 STAR LABELS ────────────────────────────────────────────

F68R2_STARS = [
    (7,  'oolchy'),      # cleaned from ZL markup
    (8,  'cheorol'),
    (9,  'odaiin'),
    (10, 'ochory'),
    (11, 'shdar'),
    (12, 'dchol'),
    (13, 'todaraiily'),
    (14, 'olcheesey'),
    (15, 'okchor'),
    (16, 'oteool'),
    (17, 'oydchy'),
    (18, 'okeeeody'),
    (19, 'cholar'),
    (20, 'dcheoldy'),
    (21, 'oteeear'),
    (22, 'otoeeo'),
    (23, 'ofcheody'),
    (24, 'otcheodar'),
    (25, 'odairchol'),   # odair.chol in ZL
    (26, 'opocphor'),
    (27, 'otoshol'),
    (28, 'chodar'),
    (29, 'sheey'),
    (30, 'okeeechor'),   # ok[eeee:eech]or
]

# ── MEDIEVAL STAR NAMES (29 most common on astrolabes) ────────────
# From standard medieval astrolabe star lists (Kunitzsch, al-Sufi tradition)
# Names as they appear in Latin/Arabic transliteration on European astrolabes

ASTROLABE_STARS = {
    # Arabic name → Latin form → Modern name
    'aldebaran': ('Aldebaran', 'alpha Tauri'),
    'algol': ('Caput Algol', 'beta Persei'),
    'algenib': ('Algenib', 'gamma Pegasi'),
    'algorab': ('Algorab', 'delta Corvi'),
    'alhena': ('Alhena', 'gamma Geminorum'),
    'alioth': ('Alioth', 'epsilon Ursae Majoris'),
    'alkaid': ('Alkaid', 'eta Ursae Majoris'),
    'almach': ('Almach', 'gamma Andromedae'),
    'alnair': ('Alnair', 'alpha Gruis'),
    'alnath': ('Alnath', 'beta Tauri'),
    'alnilam': ('Alnilam', 'epsilon Orionis'),
    'alnitak': ('Alnitak', 'zeta Orionis'),
    'alphard': ('Alphard', 'alpha Hydrae'),
    'alphecca': ('Alphecca', 'alpha Coronae Borealis'),
    'alpheratz': ('Alpheratz', 'alpha Andromedae'),
    'altair': ('Altair/Altayr', 'alpha Aquilae'),
    'antares': ('Antares/Cor Scorpionis', 'alpha Scorpii'),
    'arcturus': ('Arcturus', 'alpha Bootis'),
    'bellatrix': ('Bellatrix', 'gamma Orionis'),
    'betelgeuse': ('Betelgeuse', 'alpha Orionis'),
    'canopus': ('Canopus/Suhayl', 'alpha Carinae'),
    'capella': ('Capella', 'alpha Aurigae'),
    'deneb': ('Deneb/Dhanab', 'alpha Cygni'),
    'denebola': ('Denebola', 'beta Leonis'),
    'dubhe': ('Dubhe', 'alpha Ursae Majoris'),
    'fomalhaut': ('Fomalhaut', 'alpha Piscis Austrini'),
    'markab': ('Markab', 'alpha Pegasi'),
    'menkar': ('Menkar', 'alpha Ceti'),
    'polaris': ('Polaris/Alruccaba', 'alpha Ursae Minoris'),
    'procyon': ('Procyon', 'alpha Canis Minoris'),
    'regulus': ('Regulus/Cor Leonis', 'alpha Leonis'),
    'rigel': ('Rigel', 'beta Orionis'),
    'scheat': ('Scheat/Schedir', 'beta Pegasi'),
    'sirius': ('Sirius/Canis Major', 'alpha Canis Majoris'),
    'spica': ('Spica', 'alpha Virginis'),
    'vega': ('Vega/Waki', 'alpha Lyrae'),
}


def decode_star(eva_word, pipeline, beam=20):
    """Decode a star label via K&A."""
    if len(eva_word) < 2:
        std = pipeline.decode_word(eva_word)
        return [{'latin': std.latin, 'freq': 0, 'perseus': False}]

    paths = decode_root(eva_word, pipeline.hmm, top_k=beam)
    results = []
    seen = set()
    for vp in paths:
        if not vp.latin:
            continue
        clean = vp.latin.replace(' ', '').lower()
        if clean in seen:
            continue
        seen.add(clean)
        freq = pipeline.corpus.freq(clean)
        perseus = pipeline.dictionary.is_valid(clean)
        results.append({'latin': vp.latin, 'freq': freq, 'perseus': perseus})

    results.sort(key=lambda x: (x['perseus'], x['freq']), reverse=True)
    return results[:8]


def compare_with_star_names(decoded_options, star_dict):
    """Check if any K&A decode matches a known star name."""
    matches = []
    for opt in decoded_options:
        clean = opt['latin'].replace(' ', '').lower()
        for star_name, (latin, modern) in star_dict.items():
            # Exact match
            if clean == star_name or clean == latin.lower().replace(' ', ''):
                matches.append((star_name, modern, 1.0))
            # Prefix match (4+ chars)
            elif len(clean) >= 4 and star_name.startswith(clean[:4]):
                matches.append((star_name, modern, 0.7))
            elif len(clean) >= 4 and clean.startswith(star_name[:4]):
                matches.append((star_name, modern, 0.7))
            # 3-char prefix
            elif len(clean) >= 3 and len(star_name) >= 3 and clean[:3] == star_name[:3]:
                matches.append((star_name, modern, 0.4))
    return matches


def main():
    config = Config()
    pipeline = VoynichPipeline(config)
    pipeline.load()

    out = []
    out.append("# F68R1 STAR LABELS — K&A decode + comparaison astrolabe")
    out.append("")
    out.append("29 labels d'etoiles. K&A beam=20. Comparaison avec 36 etoiles d'astrolabe.")
    out.append("")

    # ── f68r1 ─────────────────────────────────────────────────────
    out.append("## F68R1 — 29 star labels")
    out.append("")
    out.append("| # | Pos | EVA | Best K&A | Perseus | Freq | Alt | Star match? |")
    out.append("|---|-----|-----|----------|---------|------|-----|-------------|")

    star_matches_total = 0
    for i, (pos, eva) in enumerate(F68R1_STARS):
        paths = decode_star(eva, pipeline)
        best = paths[0] if paths else {'latin': '?', 'perseus': False, 'freq': 0}
        pers = "OUI" if best['perseus'] else "-"
        alts = ', '.join(p['latin'] for p in paths[1:3])

        # Check ALL decode paths against star names
        star_hits = []
        for p in paths:
            hits = compare_with_star_names([p], ASTROLABE_STARS)
            star_hits.extend(hits)
        star_str = ', '.join(f'{s}({sc:.0f})' for s, m, sc in star_hits[:3]) if star_hits else '-'
        if star_hits:
            star_matches_total += 1

        out.append(f"| {i+1:2d} | {pos:2d} | {eva:15s} | {best['latin']:15s} | {pers} | {best['freq']:5d} | {alts:30s} | {star_str} |")

    out.append("")
    out.append(f"**Star name matches: {star_matches_total}/29**")
    out.append("")

    # ── f68r2 ─────────────────────────────────────────────────────
    out.append("## F68R2 — 24 star labels")
    out.append("")
    out.append("| # | Pos | EVA | Best K&A | Perseus | Freq | Star match? |")
    out.append("|---|-----|-----|----------|---------|------|-------------|")

    for i, (pos, eva) in enumerate(F68R2_STARS):
        paths = decode_star(eva, pipeline)
        best = paths[0] if paths else {'latin': '?', 'perseus': False, 'freq': 0}
        pers = "OUI" if best['perseus'] else "-"

        star_hits = []
        for p in paths:
            hits = compare_with_star_names([p], ASTROLABE_STARS)
            star_hits.extend(hits)
        star_str = ', '.join(f'{s}({sc:.0f})' for s, m, sc in star_hits[:3]) if star_hits else '-'

        out.append(f"| {i+1:2d} | {pos:2d} | {eva:15s} | {best['latin']:15s} | {pers} | {best['freq']:5d} | {star_str} |")

    out.append("")

    # ── Shared words between f68r1, f68r2, and L04 ───────────────
    out.append("## MOTS PARTAGES entre f68r1, f68r2, et L04")
    out.append("")

    f68r1_words = set(w for _, w in F68R1_STARS)
    f68r2_words = set(w for _, w in F68R2_STARS)
    l04_words = set(['daiin','otey','ofeeey','shes','o','d','okeeod','l',
                     'lkeeol','dkedar','yf','aros','s','y','chedaiin','k',
                     'eeety','x','deeodal','vo','tchor','kedar','dal',
                     'aiin','otal','daro','v'])

    # Check for shared words or substrings
    out.append("### Mots identiques")
    shared_12 = f68r1_words & f68r2_words
    if shared_12:
        out.append(f"f68r1 ∩ f68r2: {shared_12}")
    shared_1L = f68r1_words & l04_words
    if shared_1L:
        out.append(f"f68r1 ∩ L04: {shared_1L}")
    shared_2L = f68r2_words & l04_words
    if shared_2L:
        out.append(f"f68r2 ∩ L04: {shared_2L}")
    out.append("")

    # Check substrings
    out.append("### Sous-chaines partagees")
    for w1 in sorted(l04_words):
        if len(w1) < 3:
            continue
        for w2 in sorted(f68r1_words | f68r2_words):
            if w1 in w2 and w1 != w2:
                source = "f68r1" if w2 in f68r1_words else "f68r2"
                out.append(f"  L04:`{w1}` found in {source}:`{w2}`")
            elif w2 in w1 and w1 != w2 and len(w2) >= 3:
                source = "f68r1" if w2 in f68r1_words else "f68r2"
                out.append(f"  {source}:`{w2}` found in L04:`{w1}`")
    out.append("")

    # ── Pattern comparison ────────────────────────────────────────
    out.append("## COMPARAISON STRUCTURELLE")
    out.append("")

    # Word lengths
    f68r1_lens = [len(w) for _, w in F68R1_STARS]
    l04_lens = [len(w) for w in l04_words]
    out.append(f"f68r1 longueur moyenne: {sum(f68r1_lens)/len(f68r1_lens):.1f} (min={min(f68r1_lens)}, max={max(f68r1_lens)})")
    out.append(f"L04 longueur moyenne: {sum(l04_lens)/len(l04_lens):.1f} (min={min(l04_lens)}, max={max(l04_lens)})")
    out.append("")

    # Initial glyph
    f68_initials = Counter(w[0] for _, w in F68R1_STARS)
    l04_initials = Counter(w[0] for w in l04_words)
    out.append(f"f68r1 initiales: {dict(f68_initials.most_common())}")
    out.append(f"L04 initiales: {dict(l04_initials.most_common())}")
    out.append("")

    report = '\n'.join(out)
    out_path = os.path.join(os.path.dirname(__file__), '..', 'output', 'F68R1_STAR_DECODE.md')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"Report: {out_path}")
    for line in report.split('\n'):
        if 'match' in line.lower() or line.startswith('#') or '<<<' in line or 'partag' in line.lower() or 'found in' in line:
            print(line)


if __name__ == '__main__':
    main()
