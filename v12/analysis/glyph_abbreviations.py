"""
Glyph Abbreviations Cracker — Analyze isolated glyphs (l, a, sh, f, k, t, ch)
in context to determine their meaning as pharmaceutical abbreviations.

For each glyph: position in line, what precedes/follows, section distribution,
and test specific hypotheses (l=libra, a=ana, sh=signa, f=fiat, k=calefac, t=tere).
"""
import sys, os
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from v12.config import Config
from v12.pipeline import VoynichPipeline
from v12.loaders.transcription import list_folios, parse_folio


GLYPHS_TO_TEST = ['l', 'a', 'sh', 'f', 'k', 't', 'ch', 'e']

HYPOTHESES = {
    'l':  {'hyp': 'libra (poids)', 'test': 'entre quantite et ingredient?'},
    'a':  {'hyp': 'ana (a parts egales)', 'test': 'dans listes d\'ingredients?'},
    'sh': {'hyp': 'signa (etiquetez)', 'test': 'fin de recette/paragraphe?'},
    'f':  {'hyp': 'fiat (que cela soit fait)', 'test': 'position finale?'},
    'k':  {'hyp': 'calefac (chauffe)', 'test': 'entre deux ingredients?'},
    't':  {'hyp': 'tere (broie)', 'test': 'entre deux ingredients?'},
    'ch': {'hyp': 'i/id (cela)', 'test': 'pronom demonstratif?'},
    'e':  {'hyp': 'e/ex (de/hors de)', 'test': 'preposition?'},
}

PHARMA_WORDS = {'coquo', 'coque', 'coques', 'coquere', 'coquas', 'tere',
                'recipe', 'misce', 'hiera', 'aloes', 'aquam', 'aqua',
                'rens', 'cura', 'curam', 'dolor', 'alo', 'iure',
                'cibo', 'cibus', 'equaliter', 'libra'}

INGREDIENTS = {'hiera', 'aloes', 'alo', 'cura', 'curam', 'rens',
               'cibo', 'cibus', 'iure', 'aquam', 'aqua'}

VERBS = {'coquo', 'coque', 'coques', 'coquere', 'coquas', 'tere',
         'recipe', 'misce', 'ciere', 'ciens', 'collige'}


def main():
    config = Config()
    pipeline = VoynichPipeline(config)
    pipeline.load()
    folios = list_folios(config.transcription_path)

    out = []
    out.append("# Analyse des Glyphes Isoles — Abbreviations Pharmaceutiques")
    out.append("")

    for glyph in GLYPHS_TO_TEST:
        hyp = HYPOTHESES.get(glyph, {})
        out.append(f"---")
        out.append(f"## Glyphe `{glyph}` — Hypothese: **{hyp.get('hyp', '?')}**")
        out.append("")

        # Collect all occurrences with full context
        occurrences = []
        for fid, section in folios:
            lines_data, sec = parse_folio(config.transcription_path, fid)
            if not lines_data:
                continue
            decoded = pipeline.decode_folio(lines_data)
            for lnum, words in sorted(decoded.items()):
                for i, dw in enumerate(words):
                    if dw.eva != glyph:
                        continue
                    before_2 = words[i-2] if i >= 2 else None
                    before_1 = words[i-1] if i >= 1 else None
                    after_1 = words[i+1] if i < len(words)-1 else None
                    after_2 = words[i+2] if i < len(words)-2 else None
                    pos = 'FIRST' if i == 0 else ('LAST' if i == len(words)-1 else 'MIDDLE')
                    is_near_end = i >= len(words) - 3
                    occurrences.append({
                        'fid': fid, 'sec': section or '?', 'lnum': lnum, 'pos': pos,
                        'i': i, 'total': len(words), 'near_end': is_near_end,
                        'b2': before_2, 'b1': before_1,
                        'a1': after_1, 'a2': after_2,
                    })

        total = len(occurrences)
        out.append(f"**Occurrences**: {total}")
        out.append("")

        if total == 0:
            out.append("Aucune occurrence trouvee.")
            out.append("")
            continue

        # Section distribution
        sec_dist = Counter(o['sec'] for o in occurrences)
        out.append(f"### Distribution par section")
        out.append("")
        out.append("| Section | Count | % |")
        out.append("|---------|-------|---|")
        for sec, count in sec_dist.most_common():
            out.append(f"| {sec} | {count} | {count*100//total}% |")
        out.append("")

        # Position in line
        pos_dist = Counter(o['pos'] for o in occurrences)
        out.append(f"### Position dans la ligne")
        out.append("")
        for p, c in pos_dist.most_common():
            out.append(f"- **{p}**: {c} ({c*100//total}%)")
        near_end = sum(1 for o in occurrences if o['near_end'])
        out.append(f"- Pres de la fin (3 derniers mots): {near_end} ({near_end*100//total}%)")
        out.append("")

        # Word before
        before_latin = Counter()
        before_eva = Counter()
        for o in occurrences:
            if o['b1']:
                before_latin[o['b1'].latin] += 1
                before_eva[o['b1'].eva] += 1

        out.append(f"### Mot AVANT `{glyph}` (top 10)")
        out.append("")
        out.append("| Latin | Count | EVA |")
        out.append("|-------|-------|-----|")
        for w, c in before_latin.most_common(10):
            out.append(f"| {w} | {c} | |")
        out.append("")

        # Word after
        after_latin = Counter()
        for o in occurrences:
            if o['a1']:
                after_latin[o['a1'].latin] += 1

        out.append(f"### Mot APRES `{glyph}` (top 10)")
        out.append("")
        out.append("| Latin | Count |")
        out.append("|-------|-------|")
        for w, c in after_latin.most_common(10):
            out.append(f"| {w} | {c} |")
        out.append("")

        # Pharma context
        near_pharma = 0
        near_ingredient = 0
        near_verb = 0
        for o in occurrences:
            context_words = set()
            for pos_key in ['b2', 'b1', 'a1', 'a2']:
                dw = o[pos_key]
                if dw:
                    context_words.add(dw.latin.lower().strip('_[]()? '))
            if context_words & PHARMA_WORDS:
                near_pharma += 1
            if context_words & INGREDIENTS:
                near_ingredient += 1
            if context_words & VERBS:
                near_verb += 1

        out.append(f"### Contexte pharmaceutique")
        out.append("")
        out.append(f"- Pres d'un mot pharma: {near_pharma}/{total} ({near_pharma*100//total}%)")
        out.append(f"- Pres d'un ingredient: {near_ingredient}/{total} ({near_ingredient*100//total}%)")
        out.append(f"- Pres d'un verbe: {near_verb}/{total} ({near_verb*100//total}%)")
        out.append("")

        # Examples
        out.append(f"### Exemples (20 premiers)")
        out.append("")
        for o in occurrences[:20]:
            b = f"{o['b1'].latin}" if o['b1'] else '-'
            a = f"{o['a1'].latin}" if o['a1'] else '-'
            out.append(f"- {o['fid']} L{o['lnum']:02d} [{o['sec']}]: ...{b} **[{glyph}]** {a}...")
        out.append("")

        # Hypothesis test
        out.append(f"### Verdict")
        out.append("")

        if glyph == 'l':
            # Test LIBRA: between quantity-like word and ingredient
            ingr_after = sum(1 for o in occurrences if o['a1'] and o['a1'].latin.lower() in INGREDIENTS)
            ac_before = sum(1 for o in occurrences if o['b1'] and o['b1'].latin.lower() == 'ac')
            out.append(f"- `ac` precede `l`: {ac_before}/{total} ({ac_before*100//total}%)")
            out.append(f"- Ingredient suit `l`: {ingr_after}/{total} ({ingr_after*100//total}%)")
            if ac_before > total * 0.1:
                out.append(f"- **COMPATIBLE avec LIBRA** (ac libra = 'et une livre de')")
            else:
                out.append(f"- Faible support pour LIBRA")

        elif glyph == 'a':
            # Test ANA: in ingredient lists (multiple ingredients around it)
            multi_ingr = sum(1 for o in occurrences
                           if (o['b1'] and o['b1'].latin.lower() in INGREDIENTS) and
                              (o['a1'] and o['a1'].latin.lower() in INGREDIENTS))
            out.append(f"- Ingredient avant ET apres: {multi_ingr}/{total}")
            if multi_ingr > total * 0.2:
                out.append(f"- **COMPATIBLE avec ANA** (a parts egales)")

        elif glyph == 'sh':
            # Test SIGNA: near end of recipe/paragraph
            end_pos = sum(1 for o in occurrences if o['near_end'])
            out.append(f"- Pres de la fin: {end_pos}/{total} ({end_pos*100//total}%)")
            if end_pos > total * 0.4:
                out.append(f"- **COMPATIBLE avec SIGNA** (instruction finale)")
            else:
                out.append(f"- Faible support pour SIGNA, plutot milieu de texte")

        elif glyph == 'f':
            # Test FIAT: at end of recipe
            end_pos = sum(1 for o in occurrences if o['pos'] == 'LAST' or o['near_end'])
            out.append(f"- Position finale/pres fin: {end_pos}/{total} ({end_pos*100//total}%)")

        elif glyph in ('k', 't'):
            # Test imperative verbs: between ingredients
            between_ingr = sum(1 for o in occurrences
                             if (o['b1'] and o['b1'].latin.lower() in INGREDIENTS) or
                                (o['a1'] and o['a1'].latin.lower() in INGREDIENTS))
            out.append(f"- Adjacent a un ingredient: {between_ingr}/{total} ({between_ingr*100//total}%)")

        out.append("")

    # Write
    report = '\n'.join(out)
    out_path = os.path.join(os.path.dirname(__file__), '..', 'output', 'GLYPH_ABBREVIATIONS.md')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"Report: {out_path}")
    print(f"Analyzed {len(GLYPHS_TO_TEST)} glyphs")


if __name__ == '__main__':
    main()
