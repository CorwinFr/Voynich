"""
LUNAIRE LATIN CRIB — Align L04 with reconstructed Latin lunaire.

Uses LUNAIRE_LATIN_RECONSTRUCTION.md (attested Latin vocabulary)
for LEXICAL matching, not just semantic.

For each of the 29 L04 words, check if ANY K&A path (beam=50)
produces a term from the lunaire Latin vocabulary.
"""
import sys, os, re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from v12.config import Config
from v12.pipeline import VoynichPipeline
from v12.stages.hmm_decoder import decode_root


L04 = [
    (1,  'daiin'),    (2,  'otey'),     (3,  'ofeeey'),   (4,  'shes'),
    (5,  'o'),        (6,  'd'),        (7,  'okeeod'),    (8,  'l'),
    (9,  'o'),        (10, 'lkeeol'),   (11, 'dkedar'),    (12, 'yf'),
    (13, 'aros'),     (14, 's'),        (15, 'y'),         (16, 'chedaiin'),
    (17, 'k'),        (18, 'eeety'),    (19, 'x'),         (20, 'deeodal'),
    (21, 'vo'),       (22, 'tchor'),    (23, 'kedar'),     (24, 'dal'),
    (25, 'daiin'),    (26, 'aiin'),     (27, 'otal'),      (28, 'daro'),
    (29, 'v'),
]

# Lunaire Latin vocabulary — all attested terms from reconstruction
LUNAIRE_VOCAB = {
    # Medical outcomes
    'sanabitur': ('guerira', 'GUERISON'),
    'sanus': ('sain', 'GUERISON'),
    'sanare': ('guerir', 'GUERISON'),
    'sanitas': ('sante', 'GUERISON'),
    'salus': ('salut', 'GUERISON'),
    'morietur': ('mourra', 'MORT'),
    'mori': ('mourir', 'MORT'),
    'mors': ('mort', 'MORT'),
    'languebit': ('languira', 'LANGUEUR'),
    'languere': ('languir', 'LANGUEUR'),
    'diu': ('longtemps', 'DUREE'),
    'cito': ('vite', 'VITESSE'),
    'tarde': ('tard/finalement', 'DUREE'),
    'periculum': ('danger', 'DANGER'),
    'periculo': ('danger', 'DANGER'),
    'sine': ('sans', 'ABSENCE'),
    'cum': ('avec', 'PRESENCE'),
    'vincetur': ('sera vaincu', 'DEFAITE'),
    'confortabitur': ('sera conforte', 'CONFORT'),
    'confortare': ('conforter', 'CONFORT'),
    'allevabit': ('se levera', 'GUERISON'),
    'alleviare': ('soulager', 'GUERISON'),
    'surgere': ('se lever', 'GUERISON'),
    'surget': ('se levera', 'GUERISON'),
    'decumbere': ('tomber malade', 'MALADIE'),
    'decubuerit': ('tombe malade', 'MALADIE'),
    'desperabitur': ('desesperera', 'DESESPOIR'),
    'medicina': ('medecine', 'REMEDE'),
    'medicamen': ('remede', 'REMEDE'),
    'medicare': ('soigner', 'REMEDE'),
    'auxiliabitur': ('aidera', 'AIDE'),
    'timor': ('crainte', 'PEUR'),
    'infirmitas': ('maladie', 'MALADIE'),
    'morbus': ('maladie', 'MALADIE'),
    'dolor': ('douleur', 'DOULEUR'),
    'febris': ('fievre', 'MALADIE'),
    'cura': ('soin', 'REMEDE'),
    'remedium': ('remede', 'REMEDE'),
    'potio': ('potion', 'REMEDE'),

    # Bloodletting
    'sanguinem': ('sang', 'SAIGNEE'),
    'sanguis': ('sang', 'SAIGNEE'),
    'minuere': ('diminuer/saigner', 'SAIGNEE'),
    'vena': ('veine', 'SAIGNEE'),
    'purgare': ('purger', 'PURGE'),
    'balneari': ('baigner', 'BAIN'),
    'balneum': ('bain', 'BAIN'),

    # Activities
    'bonum': ('bon', 'QUALITE'),
    'malum': ('mauvais', 'QUALITE'),
    'optimum': ('excellent', 'QUALITE'),
    'pessimum': ('le pire', 'QUALITE'),
    'nihil': ('rien', 'INTERDICTION'),
    'incipere': ('commencer', 'ACTION'),
    'emere': ('acheter', 'COMMERCE'),
    'vendere': ('vendre', 'COMMERCE'),
    'seminare': ('semer', 'AGRICULTURE'),
    'plantare': ('planter', 'AGRICULTURE'),
    'nuptiae': ('noces', 'MARIAGE'),
    'matrimonium': ('mariage', 'MARIAGE'),
    'navigare': ('naviguer', 'VOYAGE'),
    'iter': ('voyage', 'VOYAGE'),
    'aedificare': ('construire', 'CONSTRUCTION'),
    'domus': ('maison', 'MAISON'),
    'intrare': ('entrer', 'ACTION'),
    'venari': ('chasser', 'CHASSE'),
    'reconciliare': ('reconcilier', 'PAIX'),
    'similiter': ('pareillement', 'COMPARAISON'),
    'vivere': ('vivre', 'VIE'),
    'vivet': ('vivra', 'VIE'),

    # Time/lunar
    'luna': ('lune', 'ASTRE'),
    'dies': ('jour', 'TEMPS'),
    'hora': ('heure', 'TEMPS'),
    'noctem': ('nuit', 'TEMPS'),
    'aqua': ('eau', 'ELEMENT'),
    'aquam': ('eau', 'ELEMENT'),
    'lux': ('lumiere', 'LUMIERE'),
    'luce': ('lumiere', 'LUMIERE'),

    # Evaluative
    'leviter': ('legerement', 'INTENSITE'),
    'graviter': ('gravement', 'INTENSITE'),
    'longum': ('long', 'DUREE'),
    'breve': ('court', 'DUREE'),
    'semper': ('toujours', 'FREQUENCE'),
    'transierit': ('passera', 'TRANSITION'),

    # Phase specific
    'crux': ('croix/marque', 'MARQUEUR'),
    'signum': ('signe', 'MARQUEUR'),
}


def check_lunaire_match(eva_word, pipeline, beam=50):
    """Check if any K&A path produces a lunaire Latin term."""
    matches = []

    if len(eva_word) < 2:
        # Single glyph — check logogram
        std = pipeline.decode_word(eva_word)
        decoded = std.latin.lower().strip('_[]()? ')
        for term, (fr, cat) in LUNAIRE_VOCAB.items():
            if decoded == term or term.startswith(decoded) or decoded.startswith(term[:3]):
                matches.append((decoded, term, fr, cat, 'LOGOGRAM'))
        return matches

    # HMM beam search
    paths = decode_root(eva_word, pipeline.hmm, top_k=beam)
    for vp in paths:
        if not vp.latin:
            continue
        clean = vp.latin.replace(' ', '').lower()

        for term, (fr, cat) in LUNAIRE_VOCAB.items():
            # Exact match
            if clean == term:
                matches.append((clean, term, fr, cat, 'EXACT'))
            # Prefix match (4+ chars)
            elif len(clean) >= 4 and len(term) >= 4:
                if clean[:4] == term[:4]:
                    matches.append((clean, term, fr, cat, 'PREFIX'))
            # Close match (3 chars)
            elif len(clean) >= 3 and len(term) >= 3:
                if clean[:3] == term[:3] and abs(len(clean) - len(term)) <= 2:
                    matches.append((clean, term, fr, cat, 'CLOSE'))

    # Deduplicate by term
    seen = set()
    unique = []
    for m in matches:
        if m[1] not in seen:
            seen.add(m[1])
            unique.append(m)

    return unique


def main():
    config = Config()
    pipeline = VoynichPipeline(config)
    pipeline.load()

    # Lunaire consensus for context
    DAY_QUALITY = {
        1: 'BON', 2: 'BON', 3: 'MAUVAIS', 4: 'BON (mourra)', 5: 'MAUVAIS',
        6: 'MOYEN', 7: 'BON (medecine)', 8: 'MOYEN', 9: 'BON', 10: 'MIXTE',
        11: 'BON', 12: 'MIXTE (mourra/languira)', 13: 'TRES MAUVAIS (pire jour)',
        14: 'TRES BON (optimum)', 15: 'MAUVAIS (pres de la mort)',
        16: 'MIXTE', 17: 'BON (vivra)', 18: 'TRES BON',
        19: 'MAUVAIS (medecine aidera)', 20: 'BON', 21: 'MOYEN (conforte)',
        22: 'BON (gueri)', 23: 'MIXTE', 24: 'MOYEN (mourra)',
        25: 'TRES MAUVAIS (pire jour)', 26: 'MOYEN (mourra vite)',
        27: 'BON (vivra)', 28: 'MIXTE (conforte)', 29: 'TRES BON',
    }

    LUNAIRE_LATIN = {
        1: 'diu languebit sed sanabitur',
        2: 'cito sanabitur',
        3: 'languebit et in periculo erit',
        4: 'morietur',
        5: 'morietur',
        6: 'leviter languebit',
        7: 'per medicinam sanabitur',
        8: 'non diu languebit',
        9: 'cito se allevabit',
        10: 'sine periculo erit',
        11: 'cito se allevabit',
        12: 'cito morietur',
        13: 'vincetur a morbo',
        14: 'morietur',
        15: 'prope mortem languebit',
        16: 'languebit similiter',
        17: 'tarde vivet',
        18: 'tarde sanabitur',
        19: 'medicina ei auxiliabitur',
        20: 'cito sanabitur',
        21: 'cito confortabitur',
        22: 'similiter',
        23: 'non languebit',
        24: 'morietur',
        25: 'si diem transierit sanabitur',
        26: 'cito morietur',
        27: 'vivet',
        28: 'cito confortabitur',
        29: 'per medicinam sanabitur',
    }

    out = []
    out.append("# LUNAIRE LATIN CRIB — L04 vs Lunarium de Aegrotis reconstruit")
    out.append("")
    out.append("## Methode : crib LEXICAL (beam K&A = 50) contre vocabulaire latin atteste")
    out.append("")

    out.append("| Jour | EVA | Std decode | Lunaire latin | K&A match? | Terme | Cat | Score |")
    out.append("|------|-----|-----------|---------------|-----------|-------|-----|-------|")

    total_score = 0
    strong = 0
    coherent = 0

    for day, eva in L04:
        std = pipeline.decode_word(eva)
        std_latin = std.latin.lower().strip('_[]()? ')

        lunaire_text = LUNAIRE_LATIN.get(day, '?')
        quality = DAY_QUALITY.get(day, '?')

        matches = check_lunaire_match(eva, pipeline)

        if matches:
            best = matches[0]
            ka_path, term, fr, cat, method = best

            # Score based on quality of match + day coherence
            score = 0
            if method == 'EXACT':
                score = 3
                strong += 1
            elif method == 'PREFIX':
                score = 2
                coherent += 1
            elif method == 'CLOSE':
                score = 1
            elif method == 'LOGOGRAM':
                # Check if logogram matches day theme
                if cat in ('ELEMENT',) and day in (1, 25):
                    score = 3
                    strong += 1
                elif cat == 'MARQUEUR' and day == 19:
                    score = 3
                    strong += 1
                else:
                    score = 1

            total_score += score
            stars = '***' if score == 3 else '**' if score == 2 else '*'
            all_matches = ', '.join(f'{m[1]}({m[3]})' for m in matches[:3])
            out.append(f"| {day:2d} | {eva:10s} | {std_latin:18s} | {lunaire_text:35s} | {method:8s} | {all_matches:40s} | {cat:10s} | {score} {stars} |")
        else:
            out.append(f"| {day:2d} | {eva:10s} | {std_latin:18s} | {lunaire_text:35s} | -        | -                                        | -          | 0    |")

    out.append("")
    out.append("## SCORE GLOBAL")
    out.append("")
    out.append(f"- Total score: **{total_score}** / {29*3} ({total_score*100//(29*3)}%)")
    out.append(f"- Matches FORTS (score 3): **{strong}** / 29 ({strong*100//29}%)")
    out.append(f"- Matches coherents (score 2): **{coherent}** / 29 ({coherent*100//29}%)")
    out.append(f"- Matches totaux (score 1+): **{strong+coherent}** / 29")
    out.append("")

    thresh = total_score * 100 // (29*3)
    if thresh >= 40:
        out.append("**VERDICT: L'hypothese lunaire est SOUTENUE.** Correspondances lexicales significatives.")
    elif thresh >= 25:
        out.append("**VERDICT: Signaux ENCOURAGEANTS.** Coherence partielle avec le vocabulaire lunaire.")
    else:
        out.append("**VERDICT: L'hypothese lunaire reste FRAGILE.** Peu de correspondances lexicales directes.")

    # Write
    report = '\n'.join(out)
    out_path = os.path.join(os.path.dirname(__file__), '..', 'output', 'LUNAIRE_LATIN_CRIB.md')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(report)

    # Also copy to hypothesis dir
    hyp_path = os.path.join(os.path.dirname(__file__), '..', '..', 'hypotheses', 'H04_lunaire_L04', 'LUNAIRE_LATIN_CRIB.md')
    with open(hyp_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"Report: {out_path}")
    print(f"Score: {total_score}/{29*3} ({thresh}%)")
    print(f"Strong: {strong}, Coherent: {coherent}")


if __name__ == '__main__':
    main()
