"""
F57V CROSS-RING ANALYSIS — Compare ALL rings of f57v.

Ring 1 (L01): 1 word (center label) = dairal
Ring 2 (L02): ~54 words (outer ring, calendar/zodiac)
Ring 3 (L03): 4x17 = 68 individual glyphs (cipher key)
Ring 4 (L04): 29 words (our target)
Ring 5 (L05): ~35 individual glyphs + words (inner ring)
Rings 6-13: Center labels (8 words)

GOAL: Find which rings share glyph profiles, shared vocabulary,
and structural patterns. Determine if L04 is in a different
system from L02/L05 or the same.
"""
import re
from collections import Counter

# ── RAW DATA FROM ZL.txt ─────────────────────────────────────────

L01 = 'dairal'

L02_RAW = 'v.saly.soeos.vs.ar.okees.o.d.soefchees.lg.sos.okey.defo.f.o.rkedam.sh.ofol.sar.ddal.yty.s.y.daiir.otey.dshdy.dkalr.oty.pchchy.a.r.opaiin.dal.karody.vr.okeey.daram.qokar.okal.okal.d.o.l.shkeal.dydas.o.k.sher.saiin'
L02_WORDS = [w for w in L02_RAW.replace(',', '.').split('.') if w.strip()]

L03_RAW = 'o.l.j.r.v.x.k.m.f.t.r.y.I.o.l.d.r.v.x.k.m.f.t.r.y.c.o.l.d.r.v.x.k.m.p.t.r.y.c.o.l.d.r.v.x.k.m.p.t.r.y.c'
# Remove special glyphs @169-172 — keep the pattern
L03_ELEMENTS = [e for e in L03_RAW.split('.') if e.strip() and e != 'I']

L04_RAW = 'daiin.otey.ofeeey.shes.o.d.okeeod.l.o.lkeeol.dkedar.yf.aros.s.y.chedaiin.k.eeety.x.deeodal.vo.tchor.kedar.dal.daiin.aiin.otal.daro.v'
L04_WORDS = [w for w in L04_RAW.split('.') if w.strip()]

L05_RAW = 'o.a.l.r.m.aiin.d.c.f.r.y.l.k.x.l.r.ar.o.r.t.l.r.d.y.dar.teodar.otodal.sheky.oteeody.x.r.l'
L05_ELEMENTS = [e for e in L05_RAW.split('.') if e.strip() and e != '?']

CENTER_LABELS = ['otodaram', 'oparairdly', 'olkeedal', 'otardaly',
                 'arkoldy', 'araarar', 'okeely', 'ocfhor.okear']

def glyph_profile(text):
    """Get glyph frequency profile of a text."""
    clean = re.sub(r'[^a-z]', '', text.lower())
    freq = Counter(clean)
    total = sum(freq.values())
    if total == 0:
        return {}
    return {g: count/total for g, count in freq.items()}

def profile_distance(p1, p2):
    """Manhattan distance between two glyph profiles."""
    all_glyphs = set(list(p1.keys()) + list(p2.keys()))
    return sum(abs(p1.get(g, 0) - p2.get(g, 0)) for g in all_glyphs)

def main():
    out = []
    out.append("# F57V CROSS-RING ANALYSIS")
    out.append("")

    # ── Ring inventory ────────────────────────────────────────────
    out.append("## 1. INVENTAIRE DES ANNEAUX")
    out.append("")
    out.append(f"- L01 (centre): 1 mot = `{L01}`")
    out.append(f"- L02 (exterieur): {len(L02_WORDS)} mots")
    out.append(f"- L03 (cle): {len(L03_ELEMENTS)} elements (4 quadrants x ~17)")
    out.append(f"- L04 (cible): {len(L04_WORDS)} mots")
    out.append(f"- L05 (interieur): {len(L05_ELEMENTS)} elements")
    out.append(f"- Centre (L06-L13): {len(CENTER_LABELS)} labels")
    out.append("")

    # ── L03 cipher key analysis ───────────────────────────────────
    out.append("## 2. L03 — LA CLE DE CHIFFRE (4x17)")
    out.append("")

    # Split into 4 quadrants (each ends with @172)
    # Pattern: o.l.[d:j].r.v.x.k.m.f.@169.t.r.@170.@171.y.[I:c].@172
    # = 17 elements per quadrant
    q1 = ['o','l','d','r','v','x','k','m','f','?','t','r','?','?','y','I','@172']
    q2 = ['o','l','d','r','v','x','k','m','f','?','t','r','?','?','y','c','@172']
    q3 = ['o','l','d','r','v','x','k','m','p','?','t','r','?','?','y','c','@172']
    q4 = ['o','l','d','r','v','x','k','m','p','?','t','r','?','?','y','c','@172']

    out.append("### Structure des 4 quadrants")
    out.append("```")
    out.append("Pos:  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17")
    out.append(f"Q1:   o  l  d  r  v  x  k  m  f  ?  t  r  ?  ?  y  I  @")
    out.append(f"Q2:   o  l  d  r  v  x  k  m  f  ?  t  r  ?  ?  y  c  @")
    out.append(f"Q3:   o  l  d  r  v  x  k  m  p  ?  t  r  ?  ?  y  c  @")
    out.append(f"Q4:   o  l  d  r  v  x  k  m  p  ?  t  r  ?  ?  y  c  @")
    out.append("```")
    out.append("")
    out.append("### DIFFERENCES entre quadrants")
    out.append("- Position 3 : Q1=**d**/Q1alt=**j**, Q2-Q4=d")
    out.append("- Position 9 : Q1-Q2=**f**, Q3-Q4=**p** ← HOMOPHONIE f/p !")
    out.append("- Position 16: Q1=**I**, Q2-Q4=**c** ← I vs c")
    out.append("- Positions 10,13,14: glyphes speciaux (@169, @170, @171)")
    out.append("")

    out.append("### Elements de L03 vs glyphes de L04")
    out.append("")
    l03_glyphs = set(['o','l','d','r','v','x','k','m','f','t','y','c','p','I'])
    l04_glyphs = set(''.join(L04_WORDS))
    shared = l03_glyphs & l04_glyphs
    l03_only = l03_glyphs - l04_glyphs
    l04_only = l04_glyphs - l03_glyphs

    out.append(f"Glyphes L03: {sorted(l03_glyphs)} ({len(l03_glyphs)})")
    out.append(f"Glyphes L04: {sorted(l04_glyphs)} ({len(l04_glyphs)})")
    out.append(f"**Partages**: {sorted(shared)} ({len(shared)})")
    out.append(f"L03 seulement: {sorted(l03_only)} ({len(l03_only)})")
    out.append(f"L04 seulement: {sorted(l04_only)} ({len(l04_only)})")
    out.append("")

    out.append("### L03 COMME ALPHABET DE REFERENCE")
    out.append("")
    out.append("L03 contient 14 glyphes distincts (en excluant les speciaux).")
    out.append("L04 contient 17 caracteres distincts.")
    out.append(f"Intersection: {len(shared)}/14 L03 glyphs appear in L04 ({len(shared)*100//14}%)")
    out.append("")
    out.append("Les 3 glyphes de L03 ABSENTS de L04: m, p, I")
    out.append("Les 6 glyphes de L04 ABSENTS de L03: a, e, h, i, n, s")
    out.append("")
    out.append("**OBSERVATION CRUCIALE**: Les glyphes de L03 sont presque")
    out.append("tous des CONSONNES dans le systeme K&A (o,l,d,r,v,x,k,m,f,t,y,c,p).")
    out.append("Les glyphes de L04 absents de L03 sont presque tous des VOYELLES")
    out.append("ou des elements vocaliques (a, e, i) plus h, n, s.")
    out.append("")
    out.append("**HYPOTHESE**: L03 fournit les CONSONNES, L04 les VOYELLES+CONSONNES")
    out.append("= L03 est une cle de selection/permutation, pas un texte.")
    out.append("")

    # ── L05 analysis ──────────────────────────────────────────────
    out.append("## 3. L05 — ANNEAU INTERIEUR")
    out.append("")
    out.append(f"Elements: {L05_ELEMENTS}")
    out.append(f"Total: {len(L05_ELEMENTS)}")
    out.append("")

    l05_glyphs = set(''.join(L05_ELEMENTS))
    shared_45 = l04_glyphs & l05_glyphs
    out.append(f"Glyphes L05: {sorted(l05_glyphs)} ({len(l05_glyphs)})")
    out.append(f"Partages L04-L05: {sorted(shared_45)} ({len(shared_45)})")
    out.append("")

    # Check for shared words between L04 and L05
    l04_set = set(L04_WORDS)
    l05_set = set(L05_ELEMENTS)
    shared_words_45 = l04_set & l05_set
    out.append(f"**Mots partages L04-L05**: {shared_words_45}")
    out.append("")

    # Check shared with L02
    l02_set = set(L02_WORDS)
    shared_words_24 = l02_set & l04_set
    shared_words_25 = l02_set & l05_set
    out.append(f"**Mots partages L02-L04**: {shared_words_24}")
    out.append(f"**Mots partages L02-L05**: {shared_words_25}")
    out.append("")

    # ── Glyph frequency comparison across ALL rings ───────────────
    out.append("## 4. PROFILS DE FREQUENCE — TOUS LES ANNEAUX")
    out.append("")

    profiles = {
        'L02': glyph_profile('.'.join(L02_WORDS)),
        'L03': glyph_profile('.'.join(L03_ELEMENTS)),
        'L04': glyph_profile('.'.join(L04_WORDS)),
        'L05': glyph_profile('.'.join(L05_ELEMENTS)),
        'Centre': glyph_profile('.'.join(CENTER_LABELS)),
    }

    all_g = sorted(set(g for p in profiles.values() for g in p.keys()))

    out.append(f"| Glyph | L02% | L03% | L04% | L05% | Centre% |")
    out.append(f"|-------|------|------|------|------|---------|")
    for g in all_g:
        vals = [f"{profiles[ring].get(g, 0)*100:5.1f}" for ring in ['L02', 'L03', 'L04', 'L05', 'Centre']]
        out.append(f"| {g:5s} | {'% | '.join(vals)}% |")

    out.append("")

    # Distance matrix
    out.append("### Matrice de distance (Manhattan)")
    out.append("")
    rings = ['L02', 'L03', 'L04', 'L05', 'Centre']
    out.append("| | " + " | ".join(rings) + " |")
    out.append("|---|" + "|".join(["---"] * len(rings)) + "|")
    for r1 in rings:
        row = []
        for r2 in rings:
            d = profile_distance(profiles[r1], profiles[r2])
            row.append(f"{d:.2f}")
        out.append(f"| {r1:7s} | " + " | ".join(row) + " |")

    out.append("")
    out.append("### Interpretation")
    out.append("")

    # Find closest/farthest pairs
    min_d = 99
    max_d = 0
    min_pair = ""
    max_pair = ""
    for i, r1 in enumerate(rings):
        for r2 in rings[i+1:]:
            d = profile_distance(profiles[r1], profiles[r2])
            if d < min_d:
                min_d = d
                min_pair = f"{r1}-{r2}"
            if d > max_d:
                max_d = d
                max_pair = f"{r1}-{r2}"

    out.append(f"Paire la plus PROCHE: **{min_pair}** (distance={min_d:.2f})")
    out.append(f"Paire la plus ELOIGNEE: **{max_pair}** (distance={max_d:.2f})")
    out.append("")

    # Specifically compare L04 to each other ring
    out.append("### Distance de L04 a chaque anneau")
    for r in rings:
        if r != 'L04':
            d = profile_distance(profiles['L04'], profiles[r])
            out.append(f"  L04 ↔ {r}: {d:.2f}")
    out.append("")

    # ── L03 as potential cipher key ───────────────────────────────
    out.append("## 5. L03 COMME CLE — TEST")
    out.append("")
    out.append("Si L03 est un alphabet de substitution (14 glyphes = 14 lettres),")
    out.append("et L04 utilise ces glyphes + des voyelles supplementaires,")
    out.append("alors L04 pourrait etre lu DIRECTEMENT en remplacant chaque")
    out.append("glyphe L03 par sa position dans la sequence.")
    out.append("")

    # Map L03 positions to glyphs
    l03_sequence = ['o','l','d','r','v','x','k','m','f','?1','t','r2','?2','?3','y','c/I','@172']
    # Unique glyphs in order of first appearance
    l03_unique = []
    seen = set()
    for g in ['o','l','d','r','v','x','k','m','f','t','y','c','p','I']:
        if g not in seen:
            l03_unique.append(g)
            seen.add(g)

    out.append(f"L03 unique sequence: {l03_unique}")
    out.append(f"= {len(l03_unique)} unique values")
    out.append("")

    # Map each L03 glyph to its position number (1-14)
    l03_to_num = {g: i+1 for i, g in enumerate(l03_unique)}
    out.append(f"L03 → number mapping: {l03_to_num}")
    out.append("")

    # Apply to L04 words
    out.append("### L04 words as L03-position numbers")
    out.append("")
    out.append("| Pos | EVA | As L03 positions |")
    out.append("|-----|-----|-----------------|")
    for i, word in enumerate(L04_WORDS):
        nums = []
        for ch in word:
            if ch in l03_to_num:
                nums.append(str(l03_to_num[ch]))
            else:
                nums.append(f'({ch})')  # not in L03
        out.append(f"| {i+1:2d} | {word:10s} | {' '.join(nums)} |")

    out.append("")

    report = '\n'.join(out)
    out_path = 'v12/output/F57V_CROSS_RING.md'
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"Report: {out_path}")
    for line in report.split('\n'):
        if line.startswith('#') or 'CRUCIALE' in line or 'HYPOTHESE' in line or 'partag' in line.lower() or 'distance' in line.lower() or 'PROCHE' in line or 'ELOIGN' in line:
            print(line)


if __name__ == '__main__':
    main()
