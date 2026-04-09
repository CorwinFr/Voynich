"""
Opaque Words Deep Dive — Comprehensive analysis of LOW/OPAQUE words.
What are they? Where are they? What patterns do they follow?
What do they look like? What surrounds them?
"""
import sys, os, re
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from v12.config import Config
from v12.pipeline import VoynichPipeline
from v12.loaders.transcription import list_folios, parse_folio


def main():
    config = Config()
    pipeline = VoynichPipeline(config)
    pipeline.load()

    folios = list_folios(config.transcription_path)

    # Collect ALL decoded words with context
    all_decoded = []  # (fid, section, lnum, pos, dw, ctx_before, ctx_after, eva_before, eva_after)

    for fid, section in folios:
        lines, sec = parse_folio(config.transcription_path, fid)
        if not lines:
            continue
        decoded = pipeline.decode_folio(lines)
        for lnum, words in sorted(decoded.items()):
            for i, dw in enumerate(words):
                ctx_b = words[i-1] if i > 0 else None
                ctx_a = words[i+1] if i < len(words)-1 else None
                all_decoded.append((fid, section or '?', lnum, i, dw,
                                    ctx_b, ctx_a))

    total = len(all_decoded)
    opaques = [(fid, sec, ln, pos, dw, cb, ca)
               for fid, sec, ln, pos, dw, cb, ca in all_decoded
               if dw.confidence in ('LOW', 'OPAQUE')]

    print(f"Total words: {total}, Opaque/Low: {len(opaques)} ({len(opaques)*100//total}%)")

    out = []
    out.append("# Rapport : Mots Opaques du Manuscrit de Voynich")
    out.append(f"## Pipeline v12 + deagg + scoring calibre + collision penalty")
    out.append(f"## Date : 2026-04-08")
    out.append("")
    out.append(f"**Total mots** : {total}")
    out.append(f"**Opaques (LOW + OPAQUE)** : {len(opaques)} ({len(opaques)*100//total}%)")
    out.append("")

    # === 1. Distribution par section ===
    out.append("---")
    out.append("## 1. Distribution par section")
    out.append("")

    sec_total = Counter()
    sec_opaque = Counter()
    for fid, sec, ln, pos, dw, cb, ca in all_decoded:
        sec_total[sec] += 1
        if dw.confidence in ('LOW', 'OPAQUE'):
            sec_opaque[sec] += 1

    out.append("| Section | Total mots | Opaques | Taux | Commentaire |")
    out.append("|---------|-----------|---------|------|-------------|")
    for sec in ['H', 'S', 'B', 'P', 'T', 'Z', 'A', 'C']:
        t = sec_total.get(sec, 0)
        o = sec_opaque.get(sec, 0)
        pct = o * 100 // max(t, 1)
        names = {'H': 'Herbal', 'S': 'Stars/Recettes', 'B': 'Balnea',
                 'P': 'Pharma', 'T': 'Texte', 'Z': 'Zodiac',
                 'A': 'Astro', 'C': 'Cosmo'}
        out.append(f"| {sec} ({names.get(sec, sec)}) | {t} | {o} | {pct}% | |")

    # === 2. Mots opaques les plus frequents ===
    out.append("")
    out.append("---")
    out.append("## 2. Mots opaques les plus frequents (EVA)")
    out.append("")

    eva_counts = Counter()
    eva_decoded = {}
    eva_sections = defaultdict(Counter)
    for fid, sec, ln, pos, dw, cb, ca in opaques:
        eva_counts[dw.eva] += 1
        eva_decoded[dw.eva] = dw.latin
        eva_sections[dw.eva][sec] += 1

    out.append("| EVA | Occurrences | Decode actuel | Sections | Confidence |")
    out.append("|-----|------------|---------------|----------|------------|")
    for eva, count in eva_counts.most_common(50):
        dec = eva_decoded.get(eva, '?')
        secs = ', '.join(f'{s}:{c}' for s, c in eva_sections[eva].most_common(3))
        conf = 'LOW'
        for fid, sec, ln, pos, dw, cb, ca in opaques:
            if dw.eva == eva:
                conf = dw.confidence
                break
        out.append(f"| {eva} | {count} | {dec} | {secs} | {conf} |")

    # === 3. Longueur des mots opaques ===
    out.append("")
    out.append("---")
    out.append("## 3. Longueur des mots opaques vs lisibles")
    out.append("")

    len_opaque = Counter()
    len_readable = Counter()
    for fid, sec, ln, pos, dw, cb, ca in all_decoded:
        l = len(dw.eva)
        if dw.confidence in ('LOW', 'OPAQUE'):
            len_opaque[l] += 1
        else:
            len_readable[l] += 1

    out.append("| Longueur EVA | Lisibles | Opaques | % opaque |")
    out.append("|-------------|----------|---------|----------|")
    for length in range(1, 15):
        r = len_readable.get(length, 0)
        o = len_opaque.get(length, 0)
        t = r + o
        pct = o * 100 // max(t, 1)
        out.append(f"| {length} | {r} | {o} | {pct}% |")

    # === 4. Patterns EVA des opaques ===
    out.append("")
    out.append("---")
    out.append("## 4. Patterns structurels des mots opaques")
    out.append("")
    out.append("Classification par structure EVA (debut, fin, composition):")
    out.append("")

    # Prefix patterns
    prefix_counts = Counter()
    suffix_counts = Counter()
    for fid, sec, ln, pos, dw, cb, ca in opaques:
        eva = dw.eva
        if len(eva) >= 3:
            # First 2 chars
            p = eva[:2]
            if eva[:2] in ('ch', 'sh', 'ck', 'ct', 'cf', 'cp'):
                p = eva[:2]
            else:
                p = eva[0]
            prefix_counts[p] += 1

            # Last 2-3 chars
            for suf in ['dy', 'ey', 'ol', 'or', 'ar', 'al', 'am', 'aiin', 'ain',
                         'iin', 'chy', 'shy', 'oly', 'ory']:
                if eva.endswith(suf):
                    suffix_counts[suf] += 1
                    break
            else:
                suffix_counts[eva[-2:]] += 1

    out.append("### Prefixes EVA des opaques (debut du mot)")
    out.append("")
    out.append("| Prefixe | Count | Latin attendu |")
    out.append("|---------|-------|---------------|")
    for p, c in prefix_counts.most_common(20):
        latin_map = {'y': 'in', 'd': 'in', 'o': 'e/a', 'q': 'co/cum', 's': 'us',
                     'ch': 'i', 'sh': 'ci', 'k': 'c/qu', 't': 'el', 'l': 'es/ex',
                     'p': 'per', 'f': 'par', 'r': 're', 'a': 'u'}
        out.append(f"| {p} | {c} | {latin_map.get(p, '?')} |")

    out.append("")
    out.append("### Suffixes EVA des opaques (fin du mot)")
    out.append("")
    out.append("| Suffixe | Count |")
    out.append("|---------|-------|")
    for s, c in suffix_counts.most_common(20):
        out.append(f"| -{s} | {c} |")

    # === 5. Contexte : quel mot PRECEDE et SUIT un opaque ===
    out.append("")
    out.append("---")
    out.append("## 5. Contexte des mots opaques")
    out.append("")

    before_word = Counter()
    after_word = Counter()
    before_conf = Counter()
    after_conf = Counter()

    for fid, sec, ln, pos, dw, cb, ca in opaques:
        if cb:
            before_word[cb.latin] += 1
            before_conf[cb.confidence] += 1
        if ca:
            after_word[ca.latin] += 1
            after_conf[ca.confidence] += 1

    out.append("### Mot AVANT un opaque (top 20)")
    out.append("")
    out.append("| Mot precedent | Count | Interpretation |")
    out.append("|--------------|-------|----------------|")
    for w, c in before_word.most_common(20):
        out.append(f"| {w} | {c} | |")

    out.append("")
    out.append("### Mot APRES un opaque (top 20)")
    out.append("")
    out.append("| Mot suivant | Count | Interpretation |")
    out.append("|------------|-------|----------------|")
    for w, c in after_word.most_common(20):
        out.append(f"| {w} | {c} | |")

    out.append("")
    out.append("### Confidence du contexte")
    out.append("")
    out.append("| Mot avant (conf) | Count | Mot apres (conf) | Count |")
    out.append("|-----------------|-------|------------------|-------|")
    for conf in ['CONFIRMED', 'HIGH', 'MEDIUM', 'LOW', 'OPAQUE']:
        bc = before_conf.get(conf, 0)
        ac = after_conf.get(conf, 0)
        out.append(f"| {conf} | {bc} | {conf} | {ac} |")

    # === 6. Position dans la ligne ===
    out.append("")
    out.append("---")
    out.append("## 6. Position des opaques dans la ligne")
    out.append("")

    pos_counts = Counter()
    for fid, sec, ln, pos, dw, cb, ca in opaques:
        if pos == 0:
            pos_counts['Premier mot'] += 1
        elif pos <= 2:
            pos_counts['Mots 2-3'] += 1
        elif ca is None:
            pos_counts['Dernier mot'] += 1
        else:
            pos_counts['Milieu'] += 1

    out.append("| Position | Count | % |")
    out.append("|----------|-------|---|")
    for p, c in pos_counts.most_common():
        pct = c * 100 // len(opaques)
        out.append(f"| {p} | {c} | {pct}% |")

    # === 7. Exemples detailles par section ===
    out.append("")
    out.append("---")
    out.append("## 7. Exemples detailles par section")
    out.append("")

    for sec_code in ['H', 'S', 'B', 'P']:
        sec_opaques = [(fid, sec, ln, pos, dw, cb, ca)
                       for fid, sec, ln, pos, dw, cb, ca in opaques
                       if sec == sec_code]
        if not sec_opaques:
            continue

        names = {'H': 'Herbal', 'S': 'Stars/Recettes', 'B': 'Balnea', 'P': 'Pharma'}
        out.append(f"### Section {sec_code} ({names.get(sec_code, sec_code)}) — {len(sec_opaques)} opaques")
        out.append("")

        # Show 15 examples with context
        shown = set()
        count = 0
        for fid, sec, ln, pos, dw, cb, ca in sec_opaques:
            key = f"{fid}_{ln}_{dw.eva}"
            if key in shown:
                continue
            shown.add(key)
            cb_str = f"{cb.latin}" if cb else '-'
            ca_str = f"{ca.latin}" if ca else '-'
            out.append(f"- **{fid} L{ln:02d}**: `{dw.eva}` -> `{dw.latin}` [{dw.confidence}]")
            out.append(f"  - Contexte: ...{cb_str} **[{dw.latin}]** {ca_str}...")
            if dw.alternatives:
                alts = ', '.join(f'{a[0]}' for a in dw.alternatives[:3])
                out.append(f"  - Alternatives: {alts}")
            count += 1
            if count >= 15:
                break
        out.append("")

    # === 8. Categories hypothetiques ===
    out.append("---")
    out.append("## 8. Hypotheses sur la nature des mots opaques")
    out.append("")

    # Categorize opaques
    cat_counts = Counter()
    for fid, sec, ln, pos, dw, cb, ca in opaques:
        eva = dw.eva
        latin = dw.latin.lower().strip('_[]()? ')

        if len(eva) <= 2:
            cat_counts['Glyphes isoles (1-2 chars)'] += 1
        elif eva.startswith('y') or eva.startswith('d'):
            cat_counts['Prefixe IN + mot inconnu'] += 1
        elif eva.startswith('qo'):
            cat_counts['Prefixe CUM + mot inconnu'] += 1
        elif eva.startswith('ot'):
            cat_counts['T-trigger + mot inconnu'] += 1
        elif not any(c.isalpha() for c in latin if c not in 'aeiou'):
            cat_counts['Voyelles seules (pas de consonnes)'] += 1
        elif len(latin) >= 8:
            cat_counts['Mots longs non attestes'] += 1
        elif 'et' in latin:
            cat_counts['Splits -dy non resolus'] += 1
        else:
            cat_counts['Combinaisons K&A inconnues'] += 1

    out.append("| Categorie | Count | % des opaques |")
    out.append("|-----------|-------|---------------|")
    for cat, c in cat_counts.most_common():
        pct = c * 100 // max(len(opaques), 1)
        out.append(f"| {cat} | {c} | {pct}% |")

    # === 9. Les opaques qui pourraient etre des noms propres/plantes ===
    out.append("")
    out.append("---")
    out.append("## 9. Candidats noms de plantes / termes techniques")
    out.append("")
    out.append("Mots opaques en premiere position de ligne dans les folios Herbal :")
    out.append("")

    first_word_opaques = []
    for fid, sec, ln, pos, dw, cb, ca in opaques:
        if pos == 0 and sec == 'H' and len(dw.eva) >= 4:
            ca_str = ca.latin if ca else '-'
            first_word_opaques.append((fid, ln, dw.eva, dw.latin, ca_str))

    out.append("| Folio | Ligne | EVA | Decode | Mot suivant |")
    out.append("|-------|-------|-----|--------|-------------|")
    for fid, ln, eva, latin, ca in first_word_opaques[:30]:
        out.append(f"| {fid} | L{ln:02d} | {eva} | {latin} | {ca} |")

    # Write
    report = '\n'.join(out)
    out_path = os.path.join(os.path.dirname(__file__), '..', 'output', 'OPAQUE_DEEP_DIVE.md')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"Report: {out_path}")
    print(f"Total: {total}, Opaques: {len(opaques)} ({len(opaques)*100//total}%)")


if __name__ == '__main__':
    main()
