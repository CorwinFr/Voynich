"""
L04 FULL DECODE — All 29 words, beam=50, ALL transcription variants.

Outputs a comprehensive table with:
- EVA word (ZL consensus + Takahashi/Grove/Stolfi variants)
- Top 10 K&A paths per word
- Perseus validation
- Corpus frequency
"""
import sys, os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from v12.config import Config
from v12.pipeline import VoynichPipeline
from v12.stages.hmm_decoder import decode_root

# ── ZL consensus transcription ────────────────────────────────────
# From ZL.txt line 2527: <f57v.4,+Cc>
# Bracket notation [che:eee] means "che OR eee" — ZL prefers eee

L04_ZL = [
    (1,  'daiin'),
    (2,  'otey'),
    (3,  'ofeeey'),     # ZL: of[che:eee]y → ofeeey; H/V/U: ofchey
    (4,  'shes'),
    (5,  'o'),
    (6,  'd'),
    (7,  'okeeod'),     # ZL: okeeod; H: okchod; V/U: okchod
    (8,  'l'),
    (9,  'o'),
    (10, 'lkeeol'),     # ZL: lkeeol; V/U: l!!keeol (uncertain)
    (11, 'dkedar'),
    (12, 'yf'),         # ZL: yf; H: o!f; V/U: o!f / o,f
    (13, 'aros'),
    (14, 's'),          # ZL: s; V/U: r  *** CRITICAL VARIANT ***
    (15, 'y'),
    (16, 'chedaiin'),
    (17, 'k'),
    (18, 'eeety'),      # ZL: eeety; H: echty; V/U: chety *** CRITICAL ***
    (19, 'x'),
    (20, 'deeodal'),    # ZL: deeodal; H: doe!dal; V/U: docodal *** CRITICAL ***
    (21, 'vo'),
    (22, 'tchor'),      # ZL: tchor; All agree
    (23, 'kedar'),      # ZL: kedar; H: cs.tedas; V/U: sh.tedar *** MASSIVE ***
    (24, 'dal'),        # ZL: dal; H: dal; V/U: dal
    # @172 marker here (upside-down lambda)
    (25, 'daiin'),
    (26, 'aiin'),
    (27, 'otal'),       # ZL: otal; H: otyl *** VARIANT ***
    (28, 'daro'),
    (29, 'v'),
]

# ── Variant readings from LSI.txt ─────────────────────────────────
# H = Takahashi, V = Grove, U = Stolfi

VARIANTS = {
    3:  {'ZL': 'ofeeey',   'H': 'ofchey',   'V': 'ofchey',   'note': 'ch vs eee'},
    7:  {'ZL': 'okeeod',   'H': 'okchod',   'V': 'okchod',   'note': 'ch vs ee'},
    12: {'ZL': 'yf',       'H': 'of',       'V': 'of',       'note': 'y vs o initial'},
    14: {'ZL': 's',        'H': 's',        'V': 'r',        'note': 's vs r CRITICAL'},
    18: {'ZL': 'eeety',    'H': 'echty',    'V': 'chety',    'note': '3 readings!'},
    20: {'ZL': 'deeodal',  'H': 'doedal',   'V': 'docodal',  'note': 'ee vs o vs oco'},
    22: {'ZL': 'tchor',    'H': 'tchor',    'V': 'tchor',    'note': 'All agree'},
    23: {'ZL': 'kedar',    'H': 'tedas',    'V': 'tedar',    'note': 'COMPLETELY different! + H has cs/V has sh before'},
    27: {'ZL': 'otal',     'H': 'otyl',     'V': 'otal',     'note': 'a vs y'},
}

# Words 22-23 in Takahashi: "cs.tedas" (2 words)
# Words 22-23 in Grove/Stolfi: "sh.tedar" (2 words)
# ZL: "tchor.kedar" (2 words)
# This means the WORD BOUNDARIES differ between transcribers!


def decode_all_variants(eva_word, pipeline, beam=50):
    """Decode one EVA word with beam K&A paths."""
    if len(eva_word) < 2:
        # Single glyph — use pipeline standard decode
        std = pipeline.decode_word(eva_word)
        return [{'latin': std.latin, 'logp': 0.0, 'freq': 0, 'perseus': False, 'rule': 'logogram'}]

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
        results.append({
            'latin': vp.latin,
            'logp': vp.log_prob,
            'freq': freq,
            'perseus': perseus,
            'rule': '|'.join(vp.states[:3]) if hasattr(vp, 'states') and vp.states else 'hmm'
        })

    # Sort by: Perseus first, then frequency, then log_prob
    results.sort(key=lambda x: (x['perseus'], x['freq'], x['logp']), reverse=True)
    return results[:15]  # Top 15


def main():
    config = Config()
    pipeline = VoynichPipeline(config)
    pipeline.load()

    out = []
    out.append("# L04 FULL DECODE — 29 mots, beam=50, toutes variantes")
    out.append("")
    out.append("Pipeline K&A v12. Toutes les alternatives de decodage.")
    out.append("Variantes de transcription : ZL (Zandbergen-Landini), H (Takahashi), V (Grove), U (Stolfi)")
    out.append("")

    for day, eva_zl in L04_ZL:
        out.append(f"---")
        out.append(f"## Jour {day} : `{eva_zl}` (len={len(eva_zl)})")
        out.append("")

        # Check for variants
        if day in VARIANTS:
            v = VARIANTS[day]
            out.append(f"### Variantes de transcription")
            out.append(f"- ZL : `{v['ZL']}`")
            out.append(f"- H (Takahashi) : `{v['H']}`")
            out.append(f"- V (Grove) : `{v['V']}`")
            out.append(f"- Note : {v['note']}")
            out.append("")

        # Decode ZL version
        out.append(f"### Decodage ZL : `{eva_zl}`")
        paths_zl = decode_all_variants(eva_zl, pipeline)
        if paths_zl:
            out.append("| # | Latin | logP | Freq | Perseus | Notes |")
            out.append("|---|-------|------|------|---------|-------|")
            for i, p in enumerate(paths_zl):
                pers = "OUI" if p['perseus'] else "-"
                out.append(f"| {i+1} | {p['latin']:20s} | {p['logp']:.1f} | {p['freq']:5d} | {pers} | |")
        else:
            out.append("*Aucun chemin K&A*")
        out.append("")

        # Decode variants if different from ZL
        if day in VARIANTS:
            v = VARIANTS[day]
            variant_words = set()
            for key in ['H', 'V']:
                vw = v[key]
                if vw != v['ZL'] and vw not in variant_words:
                    variant_words.add(vw)

            for vw in sorted(variant_words):
                out.append(f"### Decodage variante : `{vw}`")
                paths_v = decode_all_variants(vw, pipeline)
                if paths_v:
                    out.append("| # | Latin | logP | Freq | Perseus | Notes |")
                    out.append("|---|-------|------|------|---------|-------|")
                    for i, p in enumerate(paths_v[:10]):
                        pers = "OUI" if p['perseus'] else "-"
                        out.append(f"| {i+1} | {p['latin']:20s} | {p['logp']:.1f} | {p['freq']:5d} | {pers} | |")
                else:
                    out.append("*Aucun chemin K&A*")
                out.append("")

        # Special case: words 22-23 have completely different readings
        if day == 22:
            out.append("### ALERTE : Mots 22-23 — frontieres de mots differentes !")
            out.append("- ZL lit : `tchor` (j22) + `kedar` (j23)")
            out.append("- H lit : `cs` (?) + `tedas` (?)")
            out.append("- V/U lit : `sh` (?) + `tedar` (?)")
            out.append("")
            for alt in ['tedas', 'tedar']:
                out.append(f"### Decodage alt j23 : `{alt}`")
                paths_alt = decode_all_variants(alt, pipeline)
                if paths_alt:
                    out.append("| # | Latin | logP | Freq | Perseus | Notes |")
                    out.append("|---|-------|------|------|---------|-------|")
                    for i, p in enumerate(paths_alt[:10]):
                        pers = "OUI" if p['perseus'] else "-"
                        out.append(f"| {i+1} | {p['latin']:20s} | {p['logp']:.1f} | {p['freq']:5d} | {pers} | |")
                out.append("")

    # ── Summary table ─────────────────────────────────────────────

    out.append("---")
    out.append("## TABLEAU RECAPITULATIF — Meilleur decode par jour")
    out.append("")
    out.append("| Jour | EVA (ZL) | Variantes | Best Latin | Perseus | Freq | Alternatives notables |")
    out.append("|------|----------|-----------|-----------|---------|------|-----------------------|")

    for day, eva_zl in L04_ZL:
        paths = decode_all_variants(eva_zl, pipeline)
        best = paths[0] if paths else {'latin': '?', 'perseus': False, 'freq': 0}
        pers = "OUI" if best['perseus'] else "-"
        var_str = ""
        if day in VARIANTS:
            v = VARIANTS[day]
            diffs = [f"{k}:{v[k]}" for k in ['H', 'V'] if v[k] != v['ZL']]
            var_str = ', '.join(diffs)

        # Notable alternatives (Perseus=True, different from best)
        alts = [p['latin'] for p in paths[1:4] if p['perseus'] and p['latin'] != best['latin']]
        alt_str = ', '.join(alts) if alts else '-'

        out.append(f"| {day:2d} | {eva_zl:10s} | {var_str:20s} | {best['latin']:15s} | {pers} | {best['freq']:5d} | {alt_str} |")

    out.append("")

    # ── Glyph ambiguity summary ───────────────────────────────────

    out.append("---")
    out.append("## AMBIGUITES DE GLYPHES")
    out.append("")
    out.append("### Positions a 3 lectures differentes")
    out.append("- **Jour 18** : ZL=`eeety`, H=`echty`, V=`chety` — 3 lectures completement differentes")
    out.append("- **Jour 20** : ZL=`deeodal`, H=`doedal`, V=`docodal` — milieu du mot ambigu")
    out.append("")
    out.append("### Positions a 2 lectures")
    out.append("- **Jour 3** : ZL=`ofeeey`, H/V=`ofchey` — `eee` vs `che`")
    out.append("- **Jour 7** : ZL=`okeeod`, H/V=`okchod` — `ee` vs `ch`")
    out.append("- **Jour 12** : ZL=`yf`, H/V=`of` — initiale `y` vs `o`")
    out.append("- **Jour 14** : ZL/H=`s`, V/U=`r` — **glyphe s/r souvent confondus**")
    out.append("- **Jour 27** : ZL/V=`otal`, H=`otyl` — `a` vs `y`")
    out.append("")
    out.append("### Frontieres de mots differentes")
    out.append("- **Jours 22-23** : ZL=`tchor.kedar`, H=`cs.tedas`, V=`sh.tedar`")
    out.append("  Les 3 transcripteurs voient des MOTS DIFFERENTS aux memes positions !")
    out.append("")
    out.append("### Symbole special")
    out.append("- **@172** (upside-down lambda) entre jours 24 et 25")
    out.append("  Pourrait etre un separateur, un numero, ou un marqueur de section")
    out.append("")

    report = '\n'.join(out)
    out_path = os.path.join(os.path.dirname(__file__), '..', 'output', 'L04_FULL_DECODE.md')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"Report: {out_path}")
    # Print summary to stdout
    for line in out[-35:]:
        print(line)


if __name__ == '__main__':
    main()
