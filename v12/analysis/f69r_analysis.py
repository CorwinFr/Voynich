"""
F69R ANALYSIS — The Rosetta Stone?

f69r has EXACTLY the same structure as f57v:
- Paragraph text (lines 1-4, @P0)
- Labels on a circular diagram (lines 5-20, @L0/&L0)
- Labels on a ROTATING ring (lines 21-42, @Ro) with HOUR markers
- A concentric circle text (line 43, @Cc)
- ISOLATED GLYPHS (lines 44-49, @L0) = y, d, o, l, s, e[d:g]

The isolated glyphs y, d, o, l, s are the SAME as L04's isolated glyphs!
And dal.daiin appears at line 19 = same bigram as L04 j24-j25.
"""
import sys, re
from collections import Counter, defaultdict

sys.path.insert(0, '.')
from v12.config import Config
from v12.pipeline import VoynichPipeline

config = Config()
pipeline = VoynichPipeline(config)
pipeline.load()

# ── F69R structure ────────────────────────────────────────────────

# Paragraph (outer text)
P0 = {
    1: 'tcheeos.shey.opaiin.chey.shey.qokeeyshdy.ol.ot.otal.sar',
    2: 'daiin.shey.okaiin.shkechy.sheey.tey.chy.cthy.otol.cham',
    3: 'sheos.aiin.ar.choetey.okal.chy.ykar.ytchey.cheotam',
    4: 'ycheoraiin.ychey.otaiin.okchor.yty.chkal.shol',
}

# Sector labels (inner diagram, 16 labels)
SECTORS = {
    5:  'oteos.chop.otaeky',
    6:  'ar.odair.chtaly',
    7:  'oto.dar.archol',
    8:  'okeey.cheydy',
    9:  'dcho.char.ar',
    10: 'ytal.air.al',
    11: 'shy.chtairy',
    12: 'yt.oetear',
    13: 'ytey.cholam',
    14: 'dair.ar.yteey.chdy',
    15: 'okair.os.air',
    16: 'chytos.aly',
    17: 'chetar.araly',
    18: 'dair.alody',
    19: 'dal.daiin.otalam',
    20: 'ytcheodytor',
}

# Rotating ring with HOUR markers (22 positions)
HOURS = {
    21: ('09:15', 'chodchy.chotal'),
    22: ('10:00', 'okeo.sho.qotam'),
    23: ('10:30', 'okeodar.oteody'),
    24: ('11:00', 'ykeeos.al.dair.dar'),
    25: ('11:30', 'ykeey.dal.oky'),
    26: ('00:00', 'doly.dal.dar.chyky'),
    27: ('00:30', 'okchol.qokol.daly'),
    28: ('01:00', 'ykechody.otar'),
    29: ('01:30', 'dary.dar.aloly'),
    30: ('02:30', 'okeeocthy.okar.ar'),
    31: ('03:00', 'chey.ar.cthorary'),
    32: ('03:30', 'sair.chekey.sairam'),
    33: ('04:00', 'okeeo.dal.okar.ar'),
    34: ('05:00', 'sol.aiir.okeytam'),
    35: ('05:30', 'okeos.ar.ald'),
    36: ('05:45', 'docheeo.kody.sar'),
    37: ('06:15', 'dchokey.shkchodyal'),
    38: ('06:45', 'chor.al.alchy.ral'),
    39: ('07:00', 'sair.al.okody.otedy'),
    40: ('07:30', 'okody.cheody.sar'),
    41: ('08:00', 'chokeod.okeey'),
    42: ('08:45', 'dkochy.cthody.dy'),
}

# Concentric circle
CC = {43: 'okoeese.daiikey.oees.chear.yteey.oteeodar.cho.okeeos.alaiin'}

# ISOLATED GLYPHS (with position markers <!1> through <!6>)
ISOLATED = {
    44: ('1', 'y'),
    45: ('2', 'd'),
    46: ('3', 'o'),
    47: ('4', 'l'),
    48: ('5', 's'),
    49: ('6', 'ed'),  # e[d:g] in ZL
}

# ── L04 for comparison ────────────────────────────────────────────
L04_WORDS = ['daiin','otey','ofeeey','shes','o','d','okeeod','l','o','lkeeol',
             'dkedar','yf','aros','s','y','chedaiin','k','eeety','x','deeodal',
             'vo','tchor','kedar','dal','daiin','aiin','otal','daro','v']

L04_ISOLATED = {'o': 'ac', 'd': 'de', 'l': '[l]', 's': 'est', 'y': 'in',
                'k': '[k]', 'x': 'crux', 'v': 'vel'}


def main():
    out = []
    out.append("# F69R ANALYSIS — Structure parallele a f57v")
    out.append("")

    # ── Structure comparison ──────────────────────────────────────
    out.append("## 1. STRUCTURE COMPAREE f69r vs f57v")
    out.append("")
    out.append("| Element | f57v | f69r |")
    out.append("|---------|------|------|")
    out.append("| Texte paragraphe | L02 (54 mots, @Cc) | P0 (4 lignes, @P0) |")
    out.append("| Cle/pattern | L03 (4x17, +Cc) | - |")
    out.append("| Labels anneau | L04 (29 mots, +Cc) | Sectors (16 labels, &L0) |")
    out.append("| Anneau rotatif | - | Hours (22 positions, @Ro) |")
    out.append("| Cercle concentrique | - | CC (1 ligne, @Cc) |")
    out.append("| Centre/labels | L06-L13 (8 labels) | - |")
    out.append("| **Glyphes isoles** | **9 (o,d,l,o,s,y,k,x,v)** | **6 (y,d,o,l,s,ed)** |")
    out.append("")

    # ── Isolated glyphs comparison ────────────────────────────────
    out.append("## 2. GLYPHES ISOLES — COMPARAISON DIRECTE")
    out.append("")
    out.append("| Position f69r | Glyph | Aussi dans L04 ? | L04 decode |")
    out.append("|--------------|-------|-----------------|-----------|")
    for pos, (num, glyph) in sorted(ISOLATED.items()):
        in_l04 = "OUI" if glyph in L04_ISOLATED else "non"
        decode = L04_ISOLATED.get(glyph, '-')
        out.append(f"| {pos} (#{num}) | {glyph} | {in_l04} | {decode} |")

    out.append("")
    out.append("**5/6 glyphes isoles de f69r sont les MEMES que ceux de L04** (y, d, o, l, s)")
    out.append("Le 6e (ed/eg) n'apparait pas dans L04.")
    out.append("")
    out.append("**Les numeros <!1> a <!6> suggerent un ORDRE ou une NUMEROTATION.**")
    out.append("Si y=1, d=2, o=3, l=4, s=5, ed=6, alors les glyphes isoles")
    out.append("sont des CHIFFRES, pas des mots !")
    out.append("")

    # ── Shared vocabulary ─────────────────────────────────────────
    out.append("## 3. VOCABULAIRE PARTAGE f69r ↔ L04")
    out.append("")

    # Extract all f69r words
    all_f69r_words = set()
    for text in list(P0.values()) + list(SECTORS.values()) + [t for _, t in HOURS.values()] + list(CC.values()):
        words = [w.strip() for w in text.replace(',', '.').split('.') if w.strip()]
        all_f69r_words.update(words)

    l04_set = set(L04_WORDS)
    shared = l04_set & all_f69r_words
    out.append(f"Mots L04: {len(l04_set)} uniques")
    out.append(f"Mots f69r: {len(all_f69r_words)} uniques")
    out.append(f"**Partages: {sorted(shared)}** ({len(shared)} mots)")
    out.append("")

    # Check which shared words appear WHERE in f69r
    for word in sorted(shared):
        locations = []
        for pos, text in P0.items():
            if word in text.replace(',', '.').split('.'):
                locations.append(f'P0.{pos}')
        for pos, text in SECTORS.items():
            if word in text.replace(',', '.').split('.'):
                locations.append(f'Sector.{pos}')
        for pos, (hour, text) in HOURS.items():
            if word in text.replace(',', '.').split('.'):
                locations.append(f'Hour.{pos}({hour})')
        for pos, text in CC.items():
            if word in text.replace(',', '.').split('.'):
                locations.append(f'CC.{pos}')
        l04_pos = [i+1 for i, w in enumerate(L04_WORDS) if w == word]
        out.append(f"  `{word}`: L04 j{l04_pos} ↔ f69r {locations}")
    out.append("")

    # ── The hour ring — decode ────────────────────────────────────
    out.append("## 4. ANNEAU DES HEURES (f69r.21-42)")
    out.append("")
    out.append("f69r a un anneau avec des marqueurs d'HEURE (09:15 a 08:45).")
    out.append("C'est un CADRAN — probablement horaire.")
    out.append("")

    out.append("| Pos | Heure | Texte | Mots partages L04 |")
    out.append("|-----|-------|-------|-------------------|")
    for pos, (hour, text) in sorted(HOURS.items()):
        words = [w.strip() for w in text.replace(',', '.').split('.') if w.strip()]
        shared_w = [w for w in words if w in l04_set]
        shared_str = ', '.join(shared_w) if shared_w else '-'
        out.append(f"| {pos} | {hour} | {text[:35]:35s} | {shared_str} |")

    out.append("")

    # ── The sector labels — decode ────────────────────────────────
    out.append("## 5. LABELS DE SECTEUR (f69r.5-20) — Decode pipeline")
    out.append("")
    out.append("| Pos | Texte | Mots | Pipeline decode |")
    out.append("|-----|-------|------|----------------|")

    for pos, text in sorted(SECTORS.items()):
        words = [w.strip() for w in text.replace(',', '.').split('.') if w.strip()]
        decodes = []
        for w in words:
            result = pipeline.decode_word(w)
            decodes.append(result.latin)
        out.append(f"| {pos} | {text[:30]:30s} | {len(words)} | {' '.join(decodes)[:50]} |")

    out.append("")

    # ── KEY DISCOVERY: dal.daiin in both ──────────────────────────
    out.append("## 6. LE PONT : `dal.daiin` dans les deux")
    out.append("")
    out.append("f69r.19 = `dal.daiin.otalam`")
    out.append("L04 j24-j25 = `dal` + [@172] + `daiin`")
    out.append("")
    out.append("Le meme bigram `dal.daiin` apparait dans les DEUX instruments !")
    out.append("En K&A: `dal` = in alo (dans l'aloes) + `daiin` = in aquam (dans l'eau)")
    out.append("Suivi de `otalam`/`otal` qui decodent similairement (sal/tus)")
    out.append("")

    # ── Glyph frequency comparison ───────────────────────────────
    out.append("## 7. FREQUENCE DE GLYPHES f69r vs L04 vs VMS")
    out.append("")

    f69r_all_text = '.'.join(list(P0.values()) + list(SECTORS.values()) +
                             [t for _, t in HOURS.values()] + list(CC.values()))
    f69r_clean = re.sub(r'[^a-z]', '', f69r_all_text.lower())
    l04_clean = re.sub(r'[^a-z]', '', ''.join(L04_WORDS).lower())

    f69r_freq = Counter(f69r_clean)
    l04_freq = Counter(l04_clean)
    f69_total = sum(f69r_freq.values())
    l04_total = sum(l04_freq.values())

    out.append(f"| Glyph | f69r% | L04% | Diff | Note |")
    out.append(f"|-------|-------|------|------|------|")
    all_g = sorted(set(list(f69r_freq.keys()) + list(l04_freq.keys())))
    for g in all_g:
        f69p = f69r_freq.get(g, 0) / f69_total * 100
        l04p = l04_freq.get(g, 0) / l04_total * 100
        diff = l04p - f69p
        note = '***' if abs(diff) > 5 else ''
        out.append(f"| {g} | {f69p:.1f}% | {l04p:.1f}% | {diff:+.1f} | {note} |")

    out.append("")

    # Manhattan distance
    manhattan = sum(abs(f69r_freq.get(g, 0)/f69_total - l04_freq.get(g, 0)/l04_total)
                    for g in all_g)
    out.append(f"**Distance Manhattan f69r-L04: {manhattan:.3f}**")
    out.append("")

    # ── SYNTHESIS ─────────────────────────────────────────────────
    out.append("## 8. SYNTHESE")
    out.append("")
    out.append("### f69r et f57v sont des INSTRUMENTS PARALLELES")
    out.append("")
    out.append("Points communs :")
    out.append("1. Glyphes isoles IDENTIQUES (y, d, o, l, s)")
    out.append("2. Vocabulaire partage (dal, daiin, otal, etc.)")
    out.append("3. Structure circulaire/concentrique")
    out.append("4. Labels fonctionnels sur des anneaux")
    out.append("")
    out.append("Differences :")
    out.append("1. f69r a des marqueurs d'HEURE (cadran horaire)")
    out.append("2. f57v a la cle L03 (4x17 pattern)")
    out.append("3. f69r a 16 secteurs (pas 29)")
    out.append("4. f69r a 22 positions horaires (pas 29)")
    out.append("")
    out.append("### LES GLYPHES ISOLES SONT DES CHIFFRES")
    out.append("")
    out.append("Sur f69r, les glyphes isoles ont des NUMEROS explicites :")
    out.append("y=1, d=2, o=3, l=4, s=5, ed=6")
    out.append("")
    out.append("Si ce systeme s'applique aussi a L04 de f57v :")
    out.append("| Pos L04 | Glyph | = Chiffre | Ancien decode K&A |")
    out.append("|---------|-------|-----------|-------------------|")
    out.append("| 5 | o | **3** | ac |")
    out.append("| 6 | d | **2** | de |")
    out.append("| 8 | l | **4** | [l] |")
    out.append("| 9 | o | **3** | ac |")
    out.append("| 14 | s | **5** | est |")
    out.append("| 15 | y | **1** | in |")
    out.append("| 17 | k | **?** | [k] (pas dans f69r) |")
    out.append("| 19 | x | **?** | crux (pas dans f69r) |")
    out.append("| 29 | v | **?** | vel (pas dans f69r) |")
    out.append("")
    out.append("Les 6 premiers (y=1 a ed=6) couvrent 6 positions.")
    out.append("k, x, v pourraient etre 7, 8, 9 ou des valeurs speciales.")
    out.append("")

    report = '\n'.join(out)
    out_path = 'v12/output/F69R_ANALYSIS.md'
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"Report: {out_path}")
    for line in report.split('\n'):
        if line.startswith('#') or '***' in line or 'CHIFFRE' in line or 'Partag' in line or 'PONT' in line or 'IDENTIQUES' in line:
            print(line)


if __name__ == '__main__':
    main()
