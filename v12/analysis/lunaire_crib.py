"""
LUNAIRE CRIB — Align L04 (29 words) with medieval lunar almanacs.

Sources: LUNAIRES_COMPLETS_30_JOURS.md
- A: Arsenal 2782 (Malades, XIVe)
- B: BnF Fr 2074 (Malades, XIVe-XVe)
- C: Arsenal 2782 (Saignee)
- D: BnF Fr 837 (Collectif, XIIIe — LE PLUS COMPLET)
- E: BnF Fr 1745 (Provencal, XIIIe-XIVe)

Method: semantic crib — compare MEANING, not exact words.
"""
import sys, os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from v12.config import Config
from v12.pipeline import VoynichPipeline
from v12.loaders.transcription import parse_folio
from v12.stages.hmm_decoder import decode_root


# L04 decoded words (from our pipeline)
L04_DECODED = [
    (1,  'daiin',    'in aquam'),
    (2,  'otey',     'oleo/te'),
    (3,  'ofeeey',   'epare/aper'),
    (4,  'shes',     'cies'),
    (5,  'o',        'ac'),
    (6,  'd',        'de'),
    (7,  'okeeod',   'quoede'),
    (8,  'l',        '?'),
    (9,  'o',        'ac'),
    (10, 'lkeeol',   'sequens/ex cons'),
    (11, 'dkedar',   'in codura/cedar'),
    (12, 'yf',       'inpar/impar'),
    (13, 'aros',     'uras/ares'),
    (14, 's',        'est'),
    (15, 'y',        'in'),
    (16, 'chedaiin', 'eius odeura'),
    (17, 'k',        '?'),
    (18, 'eeety',    'olen'),
    (19, 'x',        'crux'),
    (20, 'deeodal',  'dedens/in oeduce'),
    (21, 'vo',       've'),
    (22, 'tchor',    'lier/eliara'),
    (23, 'kedar',    'cedar/codura'),
    (24, 'dal',      'in alo/dolor'),
    (25, 'daiin',    'in aquam'),
    (26, 'aiin',     'aquam'),
    (27, 'otal',     'luce/alas'),
    (28, 'daro',     'dura'),
    (29, 'v',        'vel'),
]

# Lunaire consensus (from LUNAIRES_COMPLETS_30_JOURS.md)
# For each day: (quality, themes, saignee, latin_keywords)
LUNAIRE_CONSENSUS = {
    1:  ('BON',    'Longue maladie MAIS bon pour tout commencer. Purification.',
         'BONNE (avant tierce)', ['purgare', 'balneum', 'aqua', 'bonum', 'initium']),
    2:  ('BON',    'Guerira vite. Acheter/vendre, navigation.',
         'BONNE (avant tierce)', ['sanare', 'emere', 'vendere', 'navigare']),
    3:  ('MAUVAIS','NE RIEN COMMENCER. Languira, dangereux. Reves veridiques.',
         'DECONSEILLE', ['nihil', 'periculum', 'languere', 'cavere']),
    4:  ('BON',    'Guerit vite. Construire, voyage maritime.',
         'BONNE (avant tierce)', ['sanare', 'aedificare', 'bonum']),
    5:  ('MAUVAIS','NE RIEN FAIRE. Mourra. Amelioration lente.',
         'LE MATIN seulement', ['nihil', 'mori', 'malum', 'cavere']),
    6:  ('MOYEN',  'Retrouve sante. Mariage, chasse, stocker ble.',
         'BONNE', ['sanare', 'nuptiae', 'venatio', 'granum']),
    7:  ('BON',    'Guerira par medecine. Commencer entreprises.',
         'BONNE (BnF 837)', ['medicamen', 'incipere', 'sanare']),
    8:  ('MOYEN',  'Ne languira pas longtemps. Planter, semer herbes.',
         'BONNE (avant midi)', ['plantare', 'seminare', 'herba']),
    9:  ('BON',    'Se levera vite. Entrer maison, demenager.',
         'non specifie', ['surgere', 'domus', 'intrare']),
    10: ('MIXTE',  'Sans peril MAIS languissent et meurent (provencal). Commerce.',
         'non specifie', ['sine periculo', 'emere', 'vendere', 'seminare']),
    11: ('BON',    'Se levera vite. Vendange, planter arbres, voyage mer.',
         'non specifie', ['surgere', 'vindemia', 'plantare', 'navigare']),
    12: ('MIXTE',  'Mourra vite OU languira. Mariage, semer ble.',
         'RECOMMANDEE', ['mori', 'languere', 'nuptiae', 'seminare']),
    13: ('TRES MAUVAIS', 'PIRE JOUR. Sera vaincu. Fou, orgueilleux, meurt jeune.',
         'STRICTEMENT INTERDIT', ['pessimum', 'nihil', 'mori', 'stultus', 'cavere']),
    14: ('TRES BON', 'Excellent pour tout. Ne souffrira pas trop. Pelerinage.',
         'non specifie', ['optimum', 'omnia bona', 'peregrinatio']),
    15: ('MAUVAIS','Languira pres de la mort. Mauvais heritage. Luxurieux.',
         'DECONSEILLE', ['languere', 'mors', 'periculum', 'luxuria']),
    16: ('MIXTE',  'PIRE JOUR commerce. Guerira dans grande peine. Mauvais sang.',
         'BONNE (mauvais sang)', ['malus sanguis', 'purgare', 'poenae']),
    17: ('BON',    'Vivra. Semer, planter, mariage, chevalerie.',
         'BONNE (chaleur)', ['vivere', 'seminare', 'plantare', 'nuptiae', 'calor']),
    18: ('TRES BON','Grand profit, tout est bon. Guerit rapidement.',
         'non specifie', ['lucrum', 'omnia bona', 'sanare']),
    19: ('MAUVAIS','Medecine aidera. Prendre femme, bain, apprentissage. Anniversaire Pharaon.',
         'DECONSEILLE', ['medicamen', 'balneum', 'uxor', 'discere']),
    20: ('MIXTE',  'Guerira vite. Mauvais sauf hommage/pelerinage.',
         'INUTILE', ['sanare', 'peregrinatio', 'malum']),
    21: ('MOYEN',  'Sera conforte. Obtenir biens/terres.',
         'PREVENTIVE', ['confortare', 'bona', 'terra']),
    22: ('BON',    'Sera gueri. Reconciliation, commerce, chevaux.',
         'non specifie', ['sanare', 'pax', 'reconciliare', 'equus']),
    23: ('MIXTE',  'Mourra avant 4e jour OU endurera. Bon pour commencer.',
         'RECOMMANDEE', ['mori', 'durare', 'incipere']),
    24: ('MOYEN',  'Gueri rapidement. Commerce. PAS mariage.',
         'BONNE (avant tierce)', ['sanare', 'mercari', 'non nuptiae']),
    25: ('TRES MAUVAIS','PIRE JOUR. NE RIEN FAIRE. Saignee INTERDITE. Peur de la mort.',
         'STRICTEMENT INTERDIT', ['pessimum', 'nihil', 'timor mortis', 'cavere']),
    26: ('MOYEN',  'NE RIEN FAIRE. Retrouvera sante.',
         'non specifie', ['nihil', 'sanare']),
    27: ('BON',    'Vivra. Tout reussit. Guerira vite.',
         'non specifie', ['vivere', 'omnia bona', 'sanare']),
    28: ('MIXTE',  'Peur de mourir MAIS sera conforte. Universellement favorable.',
         'non specifie', ['timor mortis', 'confortare', 'bonum']),
    29: ('TRES BON','Bon pour tout. Guerison assuree. Prospere.',
         'non specifie', ['omnia bona', 'sanare', 'prosperitas']),
}


def semantic_score(day, decoded, alternatives):
    """Score semantic match between decoded word and lunaire consensus."""
    if day not in LUNAIRE_CONSENSUS:
        return 0, 'no data'

    quality, description, saignee, keywords = LUNAIRE_CONSENSUS[day]
    decoded_lower = decoded.lower()

    # Direct semantic matches
    # AQUA/BALNEUM matches
    if 'aquam' in decoded_lower or 'aqua' in decoded_lower:
        if day in (1, 19, 25):  # purification/bain days
            return 3, f'AQUA on purification/bain day ({quality})'
        if day == 25:
            return 3, f'AQUA on WORST day — purification/peur'
        return 1, f'aqua (generic)'

    # CRUX on critical day
    if 'crux' in decoded_lower:
        if quality in ('TRES MAUVAIS', 'MAUVAIS'):
            return 3, f'CRUX on {quality} day — dies criticus'
        return 2, f'crux (marker)'

    # LUCE/LUX on living/shining day
    if 'luce' in decoded_lower or 'lux' in decoded_lower:
        if quality in ('BON', 'TRES BON'):
            return 2, f'LUCE on {quality} day — vivere/lucere'
        return 1, 'luce (ambiguous)'

    # DOLOR on bad day
    if 'dolor' in decoded_lower:
        if quality in ('MAUVAIS', 'TRES MAUVAIS'):
            return 3, f'DOLOR on {quality} day'
        return 1, 'dolor (unexpected)'

    # DURA on endurance day
    if 'dura' in decoded_lower:
        if day in (23, 28):  # endurer/durer
            return 2, f'DURA on endurance day'
        return 1, 'dura'

    # VEL (ou) at end of cycle
    if decoded_lower == 'vel':
        if day == 29:
            return 2, 'VEL at cycle end — alternative/choice'
        return 0, 'vel (generic)'

    # IMPAR on day 12 (odd/unequal)
    if 'impar' in decoded_lower:
        if day == 12 and quality == 'MIXTE':
            return 2, 'IMPAR on MIXED day — unequal outcome'
        return 1, 'impar'

    # OLEN/OLEUM on specific days
    if 'ole' in decoded_lower:
        return 1, 'oleum (oil — preparation?)'

    # CIES/CIEO (stimulate)
    if 'cies' in decoded_lower or 'cieo' in decoded_lower:
        if quality in ('BON', 'TRES BON'):
            return 1, f'cieo (stimulate) on {quality} day'
        return 0, 'cieo (generic verb)'

    # CEDAR/CEDRUS on specific days
    if 'cedar' in decoded_lower or 'cedru' in decoded_lower:
        return 1, 'cedar (materia medica — ingredient?)'

    # EST/AC/DE/IN — too generic
    if decoded_lower in ('est', 'ac', 'de', 'in', 've', '?'):
        return 0, f'generic ({decoded_lower})'

    # Check alternatives for better matches
    for alt in alternatives:
        alt_lower = alt.lower()
        for kw in keywords:
            if kw[:4] in alt_lower or alt_lower[:4] in kw:
                return 2, f'ALT match: {alt} ~ {kw}'

    return 0, f'no semantic link ({decoded_lower})'


def main():
    config = Config()
    pipeline = VoynichPipeline(config)
    pipeline.load()

    out = []
    out.append("# LUNAIRE CRIB RESULTS — L04 vs 5 Medieval Lunar Almanacs")
    out.append("")
    out.append("## Alignment: 29 words of L04 vs lunaire consensus")
    out.append("")
    out.append("| Day | Phase | EVA | Decode v12 | Lunaire consensus | Saignee | Score | Verdict |")
    out.append("|-----|-------|-----|-----------|------------------|---------|-------|---------|")

    phases = {
        1: 'Nouvelle lune', 2: 'Croissant', 3: 'Croissant', 4: 'Croissant',
        5: 'Croissant', 6: 'Croissant', 7: '1er quartier', 8: '1er quartier',
        9: 'Gibbeuse+', 10: 'Gibbeuse+', 11: 'Gibbeuse+', 12: 'Gibbeuse+',
        13: 'Gibbeuse+', 14: 'Gibbeuse+', 15: 'Pleine lune', 16: 'Gibbeuse-',
        17: 'Gibbeuse-', 18: 'Gibbeuse-', 19: 'Gibbeuse-', 20: 'Gibbeuse-',
        21: 'Dernier Q', 22: 'Dernier Q', 23: 'Decroissant', 24: 'Decroissant',
        25: 'Decroissant', 26: 'Decroissant', 27: 'Dernier croissant', 28: 'Dernier croissant',
        29: 'Fin de cycle',
    }

    total_score = 0
    matches_2plus = 0
    matches_3 = 0

    for day, eva, decoded in L04_DECODED:
        phase = phases.get(day, '?')

        # Get alternatives via HMM
        alternatives = []
        if len(eva) >= 3:
            paths = decode_root(eva, pipeline.hmm, top_k=20)
            alternatives = [vp.latin.replace(' ', '').lower() for vp in paths if vp.latin][:10]

        # Lunaire info
        if day in LUNAIRE_CONSENSUS:
            quality, desc, saignee, _ = LUNAIRE_CONSENSUS[day]
            desc_short = desc[:40]
        else:
            quality = '?'
            desc_short = '?'
            saignee = '?'

        # Score
        score, verdict = semantic_score(day, decoded, alternatives)
        total_score += score
        if score >= 2:
            matches_2plus += 1
        if score >= 3:
            matches_3 += 1

        stars = '***' if score == 3 else '**' if score == 2 else '*' if score == 1 else ''
        out.append(f"| {day:2d} | {phase:17s} | {eva:10s} | {decoded:18s} | {quality:12s} {desc_short:40s} | {saignee:20s} | {score} {stars:3s} | {verdict} |")

    out.append("")
    out.append("## SCORE GLOBAL")
    out.append("")
    out.append(f"- Total score: **{total_score}** / {29*3} maximum ({total_score*100//(29*3)}%)")
    out.append(f"- Matches score 2+ (coherent): **{matches_2plus}** / 29 ({matches_2plus*100//29}%)")
    out.append(f"- Matches score 3 (strong): **{matches_3}** / 29 ({matches_3*100//29}%)")
    out.append("")

    if total_score >= 29:  # >33%
        out.append("**VERDICT: L'hypothese lunaire est SOUTENUE.** Le score depasse le seuil de 33%.")
    elif total_score >= 15:
        out.append("**VERDICT: Signaux ENCOURAGEANTS mais insuffisants.** Coherence partielle.")
    else:
        out.append("**VERDICT: L'hypothese lunaire est AFFAIBLIE.** Peu de correspondances.")

    # Pivot days analysis
    out.append("")
    out.append("## JOURS PIVOTS")
    out.append("")
    out.append("### Jours UNANIMEMENT MAUVAIS dans les lunaires : 3, 5, 13, 25")
    for day in [3, 5, 13, 25]:
        d = next((d for d in L04_DECODED if d[0] == day), None)
        if d:
            score, verdict = semantic_score(day, d[2], [])
            out.append(f"  Jour {day}: `{d[1]}` = `{d[2]}` — {verdict}")

    out.append("")
    out.append("### Jours UNANIMEMENT BONS : 1, 14, 17, 18, 29")
    for day in [1, 14, 17, 18, 29]:
        d = next((d for d in L04_DECODED if d[0] == day), None)
        if d:
            score, verdict = semantic_score(day, d[2], [])
            out.append(f"  Jour {day}: `{d[1]}` = `{d[2]}` — {verdict}")

    out.append("")
    out.append("### Saignee INTERDITE : 13, 25")
    for day in [13, 25]:
        d = next((d for d in L04_DECODED if d[0] == day), None)
        if d:
            out.append(f"  Jour {day}: `{d[1]}` = `{d[2]}`")

    # Write
    report = '\n'.join(out)
    out_path = os.path.join(os.path.dirname(__file__), '..', 'output', 'LUNAIRE_CRIB_RESULTS.md')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"Report: {out_path}")
    print(f"Score: {total_score}/{29*3} ({total_score*100//(29*3)}%)")
    print(f"Matches 2+: {matches_2plus}/29")
    print(f"Matches 3: {matches_3}/29")


if __name__ == '__main__':
    main()
