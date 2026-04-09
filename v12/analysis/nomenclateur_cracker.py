"""
NOMENCLATEUR CRACKER — Find hidden ingredient names in f103r.

Strategy:
1. Extract EVA words at INGREDIENT POSITIONS (after verbs, before prepositions)
2. For each, try ALL K&A paths (beam=50)
3. For each path, try:
   a. Direct match against Antidotarium ingredient list
   b. Fuzzy match (75%+ similarity)
   c. Reversed K&A (read EVA backwards)
   d. Anagram of K&A output
4. Report all matches

The Antidotarium Nicolai contains ~110 ingredients. If we match even 5-10,
that's a breakthrough.
"""
import sys, os, re, socket
from collections import Counter, defaultdict
from pathlib import Path
from itertools import permutations

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from v12.config import Config
from v12.pipeline import VoynichPipeline
from v12.loaders.transcription import parse_folio
from v12.stages.hmm_decoder import decode_root
from v12.stages.tokenizer import tokenize, preprocess_triples


# Complete Antidotarium Nicolai ingredient list
# (Latin names as they appear in medieval pharmacopeia)
ANTIDOTARIUM_INGREDIENTS = {
    # Plantes
    'asarum', 'asari', 'aloe', 'aloes', 'apio', 'apium', 'apii',
    'absinthium', 'absinthii', 'anetum', 'aneti', 'anisum', 'anisi',
    'amomum', 'amomi', 'aristolochia', 'artemisia',
    'bdellium', 'bdellii', 'borago', 'boraginis',
    'calamus', 'calami', 'camphora', 'camphorae', 'cannabis',
    'capparis', 'cardamomum', 'cardamomi', 'cassia', 'cassiae',
    'castoreum', 'castorei', 'centaurea', 'cepa', 'cera', 'cerae',
    'cinnamomum', 'cinamomi', 'cinnamomi', 'coloquintida',
    'consolida', 'coriandrum', 'coriandri', 'costus', 'costi',
    'crocus', 'croci', 'cubeba', 'cubebae', 'cuminum', 'cumini',
    'curcuma', 'curcumae',
    'dictamnus', 'dictamni', 'dragantum',
    'elleborus', 'ellebori', 'enula', 'enulae', 'eupatorium', 'eupatorii',
    'feniculum', 'feniculi', 'foeniculum',
    'galanga', 'galangae', 'galbanum', 'galbani', 'gentiana', 'gentianae',
    'glycyrrhiza',
    'hypericum', 'hyperici', 'hyssopus', 'hyssopi',
    'iris', 'iridis',
    'juniperus', 'juniperi',
    'laureola', 'laurus', 'lauri', 'lavandula', 'lavandulae',
    'lilium', 'lilii', 'linum', 'lini', 'liquiritia', 'liquiritiae',
    'majorana', 'majoranae', 'malva', 'malvae', 'mandragora', 'mandragorae',
    'mastix', 'masticis', 'matricaria', 'mel', 'mellis',
    'mentha', 'menthae', 'menta', 'myrrha', 'myrrhae', 'myrtus', 'myrti',
    'muscus', 'musci',
    'nardus', 'nardi', 'nasturtium', 'nasturtii', 'nigella', 'nigellae',
    'nux', 'nucis',
    'oleum', 'olei', 'oleo', 'olibanum', 'olibani', 'opium', 'opii',
    'origanum', 'origani',
    'paeonia', 'paeoniae', 'papaver', 'papaveris',
    'petroselinum', 'petrosellini', 'petroselini',
    'piper', 'piperis', 'plantago', 'plantaginis',
    'polium', 'polii', 'polypodium', 'polypodii',
    'prunus', 'pruni', 'psyllium', 'psyllii', 'pulegium', 'pulegii',
    'pyrethrum', 'pyrethri',
    'rhabarbarum', 'rhabarbari', 'rheum', 'rosa', 'rosae',
    'rosmarinus', 'rosmarini', 'ruta', 'rutae',
    'sabina', 'sabinae', 'salvia', 'salviae', 'sambucus', 'sambuci',
    'sandalum', 'sandali', 'satureia', 'saxifraga', 'saxifragae',
    'scammonia', 'scammoniae', 'senna', 'sennae',
    'serpyllum', 'serpylli', 'sinapis', 'sinapis',
    'spica', 'spicae', 'spicanardi', 'squilla', 'squillae',
    'stoechas', 'stoechadis', 'styrax', 'styracis',
    'thus', 'turis', 'ture',
    'terebinthina', 'terebinthinae',
    'valeriana', 'valerianae', 'verbena', 'verbenae',
    'viola', 'violae', 'zingiber', 'zingiberis',
    # Mineraux/animaux
    'sulphur', 'sulfuris', 'sal', 'salis', 'argentum', 'aurum',
    'cerusa', 'cerusae', 'lithargyrum', 'lithargyri',
    'vitriolum', 'vitrioli', 'alumen', 'aluminis',
    'axungia', 'butyrum', 'butyri',
    # Preparations
    'sapa', 'sapam', 'acetum', 'aceti', 'aceto',
    'succus', 'succi', 'succo',
    'vinum', 'vini', 'vino',
    'lac', 'lactis', 'lacte',
    'aqua', 'aquam', 'aquae',
    # Termes speciaux Aurea Alexandrina
    'lignum', 'ligni', 'folium', 'folii', 'folia',
    'radix', 'radicis', 'semen', 'seminis',
    'cortex', 'corticis', 'flos', 'floris', 'flores',
}


def fuzzy_match_ingredient(candidate, threshold=0.65):
    """Check if candidate matches any ingredient (fuzzy)."""
    c = candidate.lower().strip()
    if len(c) < 3:
        return []
    matches = []
    for ingr in ANTIDOTARIUM_INGREDIENTS:
        if len(ingr) < 3:
            continue
        # Exact
        if c == ingr:
            matches.append((ingr, 1.0, 'EXACT'))
            continue
        # Prefix
        min_len = min(len(c), len(ingr))
        if min_len >= 3:
            matching = sum(1 for a, b in zip(c, ingr) if a == b)
            sim = matching / max(len(c), len(ingr))
            if sim >= threshold:
                matches.append((ingr, sim, 'FUZZY'))
        # Subsequence
        if len(c) >= 4 and len(ingr) >= 4:
            i = j = m = 0
            while i < len(c) and j < len(ingr):
                if c[i] == ingr[j]:
                    m += 1; i += 1; j += 1
                else:
                    i += 1; j += 1
            sub_sim = m / max(len(c), len(ingr))
            if sub_sim >= threshold:
                matches.append((ingr, sub_sim, 'SUBSEQ'))

    # Deduplicate
    seen = set()
    result = []
    for ingr, sim, method in sorted(matches, key=lambda x: -x[1]):
        if ingr not in seen:
            seen.add(ingr)
            result.append((ingr, sim, method))
    return result[:5]


def try_anagram(word, max_len=8):
    """Check if any permutation of word matches an ingredient."""
    if len(word) > max_len or len(word) < 4:
        return []
    # Only try partial anagrams (too many permutations for full)
    word_sorted = ''.join(sorted(word))
    matches = []
    for ingr in ANTIDOTARIUM_INGREDIENTS:
        if len(ingr) != len(word):
            continue
        if ''.join(sorted(ingr)) == word_sorted:
            matches.append((ingr, 1.0, 'ANAGRAM'))
    return matches


def main():
    config = Config()
    pipeline = VoynichPipeline(config)
    pipeline.load()

    lines, sec = parse_folio(config.transcription_path, 'f103r')
    decoded = pipeline.decode_folio(lines)

    VERBS = {'coque', 'coques', 'coquas', 'coquere', 'coqui', 'tere', 'misce', 'cola', 'colo', 'recipe'}
    PREPS = {'in', 'cum', 'per', 'de', 'ex', 'et', 'ac'}
    KNOWN = {'aquam', 'aqua', 'iure', 'eius', 'cum', 'in', 'et', 'de', 'per', 'ex', 'ac',
             'es', 'est', 'alo', 'cibo', 'cibum', 'ciboque', 'hiera', 'aloes', 'curam',
             'curas', 'cura', 'ede', 'vel', 'eo', 'ce', 'el', 'eli', 'code', 'quas',
             'cicura', 'dolor', 'rens'}

    out = []
    out.append("# NOMENCLATEUR CRACKER — f103r Ingredients")
    out.append("## Matching EVA words at ingredient positions against Antidotarium Nicolai")
    out.append("")

    # Find ingredient positions: words between VERB and PREP/VERB
    ingredient_candidates = []  # (lnum, eva, position_context)

    for lnum in sorted(decoded.keys()):
        words = decoded[lnum]
        for i, dw in enumerate(words):
            clean = dw.latin.lower().strip('_[]()? ')
            main = clean.split()[0] if clean else ''

            # Is this an "unknown" word near a verb?
            if main in KNOWN or main in VERBS or main in PREPS:
                continue
            if len(dw.eva) < 3:
                continue

            # Check if near a verb
            near_verb = False
            for j in range(max(0, i-2), min(len(words), i+3)):
                vw = words[j].latin.lower().strip('_[]()? ').split()[0]
                if vw in VERBS:
                    near_verb = True
                    break

            if near_verb:
                ctx_before = words[i-1].latin if i > 0 else '-'
                ctx_after = words[i+1].latin if i < len(words)-1 else '-'
                ingredient_candidates.append((lnum, dw.eva, dw.latin, ctx_before, ctx_after))

    out.append(f"Total ingredient-position candidates: {len(ingredient_candidates)}")
    out.append("")

    # For each candidate, try all K&A alternatives + fuzzy match
    all_hits = []

    for lnum, eva, current_latin, ctx_b, ctx_a in ingredient_candidates:
        # Get ALL K&A decodings
        hmm_paths = decode_root(eva, pipeline.hmm, top_k=50)

        best_match = None
        best_sim = 0

        for vp in hmm_paths:
            if not vp.latin:
                continue
            clean = vp.latin.replace(' ', '').lower()

            # Test 1: Direct/fuzzy match
            matches = fuzzy_match_ingredient(clean, threshold=0.60)
            for ingr, sim, method in matches:
                if sim > best_sim:
                    best_match = (clean, ingr, sim, method)
                    best_sim = sim

            # Test 2: Anagram
            anagrams = try_anagram(clean)
            for ingr, sim, method in anagrams:
                if sim > best_sim:
                    best_match = (clean, ingr, sim, method)
                    best_sim = sim

        # Test 3: Reversed EVA
        reversed_eva = eva[::-1]
        rev_paths = decode_root(reversed_eva, pipeline.hmm, top_k=10)
        for vp in rev_paths:
            if not vp.latin:
                continue
            clean = vp.latin.replace(' ', '').lower()
            matches = fuzzy_match_ingredient(clean, threshold=0.60)
            for ingr, sim, method in matches:
                if sim > best_sim:
                    best_match = (clean, ingr, sim, f'REVERSED_{method}')
                    best_sim = sim

        if best_match:
            all_hits.append((lnum, eva, current_latin, best_match, ctx_b, ctx_a))

    # Report
    out.append("## MATCHES FOUND")
    out.append("")

    if all_hits:
        all_hits.sort(key=lambda x: -x[3][2])
        out.append(f"| Line | EVA | Current decode | K&A path | INGREDIENT | Sim | Method | Context |")
        out.append(f"|------|-----|---------------|----------|------------|-----|--------|---------|")
        for lnum, eva, current, (ka_path, ingredient, sim, method), ctx_b, ctx_a in all_hits:
            out.append(f"| L{lnum:02d} | {eva} | {current} | {ka_path} | **{ingredient}** | {sim:.0%} | {method} | {ctx_b} / {ctx_a} |")
    else:
        out.append("No matches found.")

    # Also test ALL unique EVA words from f103r (not just verb-adjacent)
    out.append("")
    out.append("## EXHAUSTIVE SEARCH — All unique EVA words on f103r")
    out.append("")

    all_eva = set()
    for lnum in sorted(decoded.keys()):
        for dw in decoded[lnum]:
            if len(dw.eva) >= 4:
                all_eva.add(dw.eva)

    exhaustive_hits = []
    for eva in sorted(all_eva):
        hmm_paths = decode_root(eva, pipeline.hmm, top_k=30)
        for vp in hmm_paths:
            if not vp.latin:
                continue
            clean = vp.latin.replace(' ', '').lower()
            matches = fuzzy_match_ingredient(clean, threshold=0.70)
            for ingr, sim, method in matches:
                if sim >= 0.70:
                    exhaustive_hits.append((eva, clean, ingr, sim, method))

    # Deduplicate
    seen = set()
    for eva, ka, ingr, sim, method in sorted(exhaustive_hits, key=lambda x: -x[3]):
        key = f"{eva}_{ingr}"
        if key in seen:
            continue
        seen.add(key)
        out.append(f"  {eva:18s} -> {ka:20s} ~ **{ingr}** ({sim:.0%} {method})")

    out.append(f"\nTotal exhaustive hits: {len(seen)}")

    # Write
    report = '\n'.join(out)
    out_path = os.path.join(os.path.dirname(__file__), '..', 'output', 'NOMENCLATEUR_CRACKER.md')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"Report: {out_path}")
    print(f"Ingredient matches: {len(all_hits)}")
    print(f"Exhaustive hits: {len(seen)}")
    if all_hits:
        for _, eva, _, (ka, ingr, sim, method), _, _ in all_hits[:10]:
            print(f"  {eva} -> {ka} = {ingr} ({sim:.0%})")


if __name__ == '__main__':
    main()
