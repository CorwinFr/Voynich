"""
ANTIDOTARIUM CRIB TEST — Align f103r decoded text with
Aurea Alexandrina / Metridatum recipes word-by-word.

The Aurea Alexandrina recipe from the Antidotarium Nicolai:
  Recipe asari, ligni aloes, turis, petrosellini, cinamomi,
  masticis, folii, spice nardi, croci, piperis longi,
  cassie fistule, carpobalsamum... ana drachmas duas.
  Coque in aqua mellis. Cola et recipe.

Key pharma verbs: recipe, coque, tere, misce, cola
Key ingredients: aloes, hiera, asari, turis, croci, piper, olei, mellis
Key prepositions: in, cum, per, et
"""
import sys, os, re, socket
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from v12.config import Config
from v12.pipeline import VoynichPipeline
from v12.loaders.transcription import parse_folio


# Pharma vocabulary from Antidotarium Nicolai
RECIPE_VERBS = {'recipe', 'coque', 'coques', 'coquas', 'coquere', 'coqui',
                'tere', 'misce', 'cola', 'colo', 'collige', 'solve',
                'distilla', 'fac', 'pone', 'adde', 'fiat'}
INGREDIENTS = {'aloes', 'aloe', 'hiera', 'asari', 'asarum', 'turis', 'ture',
               'croci', 'crocus', 'piper', 'piperis', 'olei', 'oleum', 'oleo',
               'mellis', 'mel', 'cera', 'cerae', 'mastix', 'nardi', 'nardus',
               'cassia', 'cinamomi', 'cinnamomum', 'myrrha', 'galanga',
               'folii', 'spica', 'cardamomum', 'zingiber', 'costus',
               'cicura', 'rens', 'iecur', 'sal', 'sulfur'}
PREPOSITIONS = {'in', 'cum', 'per', 'de', 'ex', 'ad', 'et', 'ac', 'vel'}
QUANTITIES = {'ana', 'equaliter', 'libra', 'librae', 'uncia', 'unciae',
              'drachma', 'scrupulus', 'partes'}
LIQUIDS = {'aquam', 'aqua', 'aquae', 'vinum', 'vino', 'iure', 'succo',
           'oleo', 'aceto', 'melle'}
BODY = {'dolor', 'cura', 'curam', 'curas', 'febris', 'morbus', 'rens'}

ALL_PHARMA = RECIPE_VERBS | INGREDIENTS | PREPOSITIONS | QUANTITIES | LIQUIDS | BODY


def lemmatize(word):
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
            parts = data.split(',')
            lemma = parts[0].replace('*', '').strip()
            clean = ''
            for ch in lemma:
                if ch in 'aeiou\u0101\u0103\u0113\u0115\u012b\u012d\u014d\u014f\u016b\u016d':
                    clean += ch.lower()
                    if ch in '\u0101\u0103': clean = clean[:-1] + 'a'
                    elif ch in '\u0113\u0115': clean = clean[:-1] + 'e'
                    elif ch in '\u012b\u012d': clean = clean[:-1] + 'i'
                    elif ch in '\u014d\u014f': clean = clean[:-1] + 'o'
                    elif ch in '\u016b\u016d': clean = clean[:-1] + 'u'
                else:
                    clean += ch.lower()
            return clean
        return w
    except:
        return w


def main():
    config = Config()
    pipeline = VoynichPipeline(config)
    pipeline.load()

    lines, sec = parse_folio(config.transcription_path, 'f103r')
    decoded = pipeline.decode_folio(lines)

    out = []
    out.append("# TEST CRIB ANTIDOTARIUM NICOLAI — f103r")
    out.append("## Alignement mot-a-mot avec l'Aurea Alexandrina et le Metridatum")
    out.append("")

    # Collect all decoded words
    all_words = []
    for lnum in sorted(decoded.keys()):
        line_words = []
        for dw in decoded[lnum]:
            clean = dw.latin.lower().strip('_[]()? ')
            for part in clean.split():
                if part.isalpha() and len(part) >= 2:
                    line_words.append((part, dw.confidence, dw.eva))
        all_words.append((lnum, line_words))

    # Count pharma matches
    total_words = sum(len(ws) for _, ws in all_words)
    pharma_matches = 0
    verb_matches = 0
    ingredient_matches = 0
    prep_matches = 0
    liquid_matches = 0
    quantity_matches = 0
    body_matches = 0
    non_pharma = 0

    word_categories = Counter()

    for lnum, words in all_words:
        for word, conf, eva in words:
            w = word.lower()
            if w in RECIPE_VERBS:
                pharma_matches += 1
                verb_matches += 1
                word_categories['VERB'] += 1
            elif w in INGREDIENTS:
                pharma_matches += 1
                ingredient_matches += 1
                word_categories['INGREDIENT'] += 1
            elif w in LIQUIDS:
                pharma_matches += 1
                liquid_matches += 1
                word_categories['LIQUID'] += 1
            elif w in QUANTITIES:
                pharma_matches += 1
                quantity_matches += 1
                word_categories['QUANTITY'] += 1
            elif w in BODY:
                pharma_matches += 1
                body_matches += 1
                word_categories['BODY'] += 1
            elif w in PREPOSITIONS:
                pharma_matches += 1
                prep_matches += 1
                word_categories['PREPOSITION'] += 1
            else:
                non_pharma += 1
                word_categories['OTHER'] += 1

    pct = pharma_matches * 100 // max(total_words, 1)

    out.append(f"## Resultats globaux")
    out.append("")
    out.append(f"| Metrique | Valeur |")
    out.append(f"|----------|--------|")
    out.append(f"| Total mots | {total_words} |")
    out.append(f"| **Match pharma** | **{pharma_matches} ({pct}%)** |")
    out.append(f"| Verbes (coque, tere, recipe...) | {verb_matches} |")
    out.append(f"| Ingredients (aloes, hiera...) | {ingredient_matches} |")
    out.append(f"| Liquides (aquam, iure...) | {liquid_matches} |")
    out.append(f"| Prepositions (in, cum, et...) | {prep_matches} |")
    out.append(f"| Quantites (equaliter...) | {quantity_matches} |")
    out.append(f"| Corps (dolor, cura...) | {body_matches} |")
    out.append(f"| Non-pharma | {non_pharma} ({non_pharma*100//max(total_words,1)}%) |")
    out.append("")

    # Show line by line with pharma highlighting
    out.append("## Alignement ligne par ligne")
    out.append("")

    for lnum, words in all_words:
        pharma_in_line = sum(1 for w, _, _ in words if w.lower() in ALL_PHARMA)
        total_in_line = len(words)
        pct_line = pharma_in_line * 100 // max(total_in_line, 1)

        parts = []
        for w, conf, eva in words:
            if w.lower() in RECIPE_VERBS:
                parts.append(f"**{w}**")
            elif w.lower() in INGREDIENTS:
                parts.append(f"*{w}*")
            elif w.lower() in LIQUIDS:
                parts.append(f"_{w}_")
            elif w.lower() in ALL_PHARMA:
                parts.append(w)
            else:
                parts.append(f"[{w}]")

        if pct_line >= 50:
            marker = "+++"
        elif pct_line >= 30:
            marker = "++"
        else:
            marker = "+"

        out.append(f"L{lnum:02d} ({pct_line}% {marker}): {' '.join(parts)}")

    # Specific recipe patterns
    out.append("")
    out.append("## Patterns de recettes identifies")
    out.append("")

    # Look for recipe-like sequences
    recipe_patterns = []
    for lnum, words in all_words:
        ws = [w.lower() for w, _, _ in words]
        for i in range(len(ws) - 2):
            # VERB + INGREDIENT/LIQUID
            if ws[i] in RECIPE_VERBS and (ws[i+1] in INGREDIENTS or ws[i+1] in LIQUIDS):
                recipe_patterns.append((lnum, f"{ws[i]} {ws[i+1]}", 'VERB+INGR'))
            # VERB + PREP + LIQUID
            if ws[i] in RECIPE_VERBS and i+2 < len(ws) and ws[i+1] in PREPOSITIONS and ws[i+2] in LIQUIDS:
                recipe_patterns.append((lnum, f"{ws[i]} {ws[i+1]} {ws[i+2]}", 'VERB+PREP+LIQ'))
            # INGREDIENT + in + LIQUID
            if ws[i] in INGREDIENTS and i+2 < len(ws) and ws[i+1] == 'in' and ws[i+2] in LIQUIDS:
                recipe_patterns.append((lnum, f"{ws[i]} in {ws[i+2]}", 'INGR+in+LIQ'))

    out.append(f"Total patterns de recette identifies: {len(recipe_patterns)}")
    out.append("")
    for lnum, pattern, ptype in recipe_patterns[:30]:
        out.append(f"  L{lnum:02d}: {pattern} ({ptype})")

    # Comparison with Aurea Alexandrina
    out.append("")
    out.append("## Comparaison avec l'Aurea Alexandrina")
    out.append("")
    out.append("Formule canonique: Recipe asari, ligni aloes, turis, petrosellini,")
    out.append("cinamomi, masticis... coque in aqua mellis. Cola et recipe.")
    out.append("")

    aurea_keywords = ['recipe', 'asari', 'aloes', 'turis', 'coque', 'aqua',
                      'mellis', 'cola', 'croci', 'piper', 'olei', 'misce']
    found = []
    not_found = []
    for kw in aurea_keywords:
        # Check if keyword appears in f103r decoded text
        all_decoded_words = set()
        for _, words in all_words:
            for w, _, _ in words:
                all_decoded_words.add(w.lower())
                # Also check lemmatized
                lem = lemmatize(w)
                if lem:
                    all_decoded_words.add(lem.lower())

        if kw in all_decoded_words:
            count = sum(1 for _, ws in all_words for w, _, _ in ws if w.lower() == kw)
            found.append((kw, count))
        else:
            not_found.append(kw)

    out.append(f"| Terme Aurea | Trouve? | Occurrences f103r |")
    out.append(f"|------------|---------|------------------|")
    for kw, count in found:
        out.append(f"| {kw} | OUI | {count} |")
    for kw in not_found:
        out.append(f"| {kw} | non | 0 |")

    out.append(f"")
    out.append(f"**Score Aurea: {len(found)}/{len(aurea_keywords)} termes retrouves ({len(found)*100//len(aurea_keywords)}%)**")

    # Write
    report = '\n'.join(out)
    out_path = os.path.join(os.path.dirname(__file__), '..', 'output', 'ANTIDOTARIUM_CRIB.md')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"Report: {out_path}")
    print(f"Pharma match: {pharma_matches}/{total_words} ({pct}%)")
    print(f"Aurea score: {len(found)}/{len(aurea_keywords)}")


if __name__ == '__main__':
    main()
