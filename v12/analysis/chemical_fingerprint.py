#!/usr/bin/env python3
"""
CHEMICAL FINGERPRINTING: The Turing Attack on the Voynich.

Instead of matching word sequences (which fails because the scribe reformulates),
match SETS OF INGREDIENTS across a passage. If f103r contains {aloes, asarum,
apium, thus, oleum, cicura} — 6 specific ingredients — the probability of
random co-occurrence in a 20000-word lexicon is ~10^-18.

Strategy:
1. Extract ALL ingredients from VSV12 decode of f103r (and other pharma folios)
2. Build a "chemical fingerprint" for each folio passage
3. Build fingerprints for each recipe in the Antidotarium corpus
4. Jaccard similarity: identify which recipe matches which folio
"""
import sys, os, re
from collections import Counter, defaultdict
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Pharmaceutical ingredient lexicon (lemma -> canonical name)
# These are the substances we can identify in decoded text
INGREDIENT_LEXICON = {
    # Confirmed by pipeline (HIGH confidence)
    'aloes': 'ALOES', 'aloe': 'ALOES',
    'ture': 'THUS', 'tura': 'THUS', 'turis': 'THUS', 'thus': 'THUS',
    'asara': 'ASARUM', 'asari': 'ASARUM', 'asarum': 'ASARUM',
    'apio': 'APIUM', 'apii': 'APIUM', 'apium': 'APIUM',
    'olen': 'OLEUM', 'olei': 'OLEUM', 'oleum': 'OLEUM', 'oleo': 'OLEUM',
    'cicura': 'CICHORIUM', 'cichorium': 'CICHORIUM',
    'aperiens': 'APERIENS',
    'hiera': 'HIERA', 'iera': 'HIERA',
    'coquendo': 'COQUO', 'coque': 'COQUO', 'coquentis': 'COQUO',
    'recipe': 'RECIPE',
    'dolor': 'DOLOR', 'dolorem': 'DOLOR',
    'iecur': 'IECUR',
    'rens': 'RENES', 'renes': 'RENES', 'renum': 'RENES',
    'cooperiens': 'COOPERIENS',
    'equaliter': 'EQUALITER',
    'cibum': 'CIBUS', 'cibo': 'CIBUS', 'cibus': 'CIBUS',
    'aquam': 'AQUA', 'aqua': 'AQUA',
    'mel': 'MEL', 'melle': 'MEL', 'mellis': 'MEL',
    'vinum': 'VINUM', 'vini': 'VINUM', 'uinum': 'VINUM',
    'cera': 'CERA',
    'libra': 'LIBRA',
    # Additional pharma ingredients from Antidotarium
    'crocus': 'CROCUS', 'croci': 'CROCUS',
    'mastix': 'MASTIX', 'masticis': 'MASTIX',
    'nardus': 'NARDUS', 'nardi': 'NARDUS', 'spica': 'NARDUS',
    'piper': 'PIPER', 'piperis': 'PIPER',
    'zingiber': 'ZINGIBER', 'zinziberis': 'ZINGIBER',
    'myrrha': 'MYRRHA', 'mirre': 'MYRRHA',
    'camphora': 'CAMPHORA', 'camphore': 'CAMPHORA',
    'opium': 'OPIUM', 'opii': 'OPIUM',
    'cassia': 'CASSIA', 'cassie': 'CASSIA', 'casie': 'CASSIA',
    'cinamomum': 'CINNAMOMUM', 'cinamomi': 'CINNAMOMUM', 'cinnamomi': 'CINNAMOMUM',
    'storax': 'STORAX', 'storacis': 'STORAX',
    'galbanum': 'GALBANUM', 'galbani': 'GALBANUM',
    'rosa': 'ROSA', 'rosarum': 'ROSA',
    'absinthium': 'ABSINTHIUM', 'absinthii': 'ABSINTHIUM',
    'salvia': 'SALVIA', 'salvie': 'SALVIA',
    'ruta': 'RUTA', 'rutae': 'RUTA',
    'menta': 'MENTHA', 'mentha': 'MENTHA', 'mente': 'MENTHA',
    'origanum': 'ORIGANUM', 'origani': 'ORIGANUM',
    'artemisia': 'ARTEMISIA', 'artemisiae': 'ARTEMISIA',
    'viola': 'VIOLA', 'viole': 'VIOLA',
    'helleborus': 'HELLEBORUS', 'ellebori': 'HELLEBORUS',
    'mandragora': 'MANDRAGORA',
    'papaver': 'PAPAVER',
    'euphorbium': 'EUPHORBIUM', 'euphorbii': 'EUPHORBIUM',
    'bdellium': 'BDELLIUM',
    'scammonea': 'SCAMMONEA', 'scammonii': 'SCAMMONEA',
    'agaricum': 'AGARICUM', 'agarici': 'AGARICUM',
    'costus': 'COSTUS', 'costi': 'COSTUS',
    'myristica': 'NUX_MUSCATA', 'muscata': 'NUX_MUSCATA',
}

# Known Antidotarium Nicolai recipes with their key ingredients
ANTIDOTARIUM_RECIPES = {
    'Aurea Alexandrina': {'ASARUM', 'THUS', 'ALOES', 'APIUM', 'CINNAMOMUM', 'ZINGIBER',
                          'CROCUS', 'MASTIX', 'NARDUS', 'MYRRHA', 'EUPHORBIUM', 'COSTUS'},
    'Metridatum': {'ASARUM', 'APIUM', 'THUS', 'MYRRHA', 'CROCUS', 'NARDUS',
                   'PIPER', 'ZINGIBER', 'OPIUM', 'ROSA', 'CASSIA', 'CINNAMOMUM', 'STORAX'},
    'Hiera Picra': {'ALOES', 'ASARUM', 'MASTIX', 'CROCUS', 'NARDUS', 'CINNAMOMUM'},
    'Theriac': {'OPIUM', 'MYRRHA', 'CROCUS', 'PIPER', 'ZINGIBER', 'NARDUS',
                'CINNAMOMUM', 'ROSA', 'THUS', 'CASSIA', 'STORAX'},
    'Diascordium': {'OPIUM', 'ROSA', 'CINNAMOMUM', 'PIPER', 'ASARUM', 'CROCUS', 'CASSIA'},
    'Electuarium de succo rosarum': {'ROSA', 'ALOES', 'CROCUS', 'MASTIX'},
    'Hiera logadii': {'ALOES', 'ASARUM', 'NARDUS', 'CROCUS', 'MASTIX', 'CINNAMOMUM', 'CASSIA'},
    'Pillulae aureae': {'ALOES', 'CROCUS', 'MYRRHA', 'MASTIX'},
    'Requies magna': {'OPIUM', 'ROSA', 'CAMPHORA', 'NARDUS', 'CINNAMOMUM'},
    'Oleum benedictum': {'OLEUM', 'APIUM', 'ASARUM'},
}


def extract_ingredients_from_text(text):
    """Extract pharmaceutical ingredients from decoded Latin text."""
    words = re.findall(r'[a-z]+', text.lower())
    found = set()
    for w in words:
        if w in INGREDIENT_LEXICON:
            found.add(INGREDIENT_LEXICON[w])
    return found


def extract_ingredients_from_corpus_windows(corpus_path, window_size=100):
    """Extract ingredient sets from sliding windows in the corpus."""
    with open(corpus_path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read().lower()
    words = re.findall(r'[a-z]+', text)

    windows = []
    for i in range(0, len(words) - window_size, window_size // 2):
        window_words = words[i:i+window_size]
        window_text = ' '.join(window_words)
        ingredients = extract_ingredients_from_text(window_text)
        if len(ingredients) >= 3:  # Only interesting windows
            context = ' '.join(window_words[:20]) + '...'
            windows.append((i, ingredients, context))
    return windows


def jaccard(set_a, set_b):
    """Jaccard similarity between two sets."""
    if not set_a or not set_b:
        return 0.0
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union)


def main():
    print('=' * 120)
    print('CHEMICAL FINGERPRINTING: TURING ATTACK ON THE VOYNICH')
    print('=' * 120)

    # Step 1: Extract ingredients from VSV12 decode of f103r
    vsv12_path = 'VSV12/v12/output/f103r.txt'
    if not os.path.exists(vsv12_path):
        # Fall back to our v12
        vsv12_path = 'v12/output/f103r_v12.txt'

    print(f'\n--- STEP 1: Extract ingredients from {vsv12_path} ---')
    with open(vsv12_path, 'r', encoding='utf-8') as f:
        f103r_text = f.read()

    f103r_ingredients = extract_ingredients_from_text(f103r_text)
    # Remove ultra-generic (AQUA, CIBUS are in every recipe)
    GENERIC_INGREDIENTS = {'AQUA', 'CIBUS', 'COQUO', 'RECIPE', 'HIERA', 'MEL', 'EQUALITER', 'VINUM'}
    f103r_specific = f103r_ingredients - GENERIC_INGREDIENTS

    print(f'  ALL ingredients found: {f103r_ingredients}')
    print(f'  SPECIFIC ingredients (excl. generic): {f103r_specific}')
    print(f'  Count: {len(f103r_specific)} specific + {len(f103r_ingredients & GENERIC_INGREDIENTS)} generic')

    # Also extract per-line for cluster analysis
    print('\n  Per-line ingredient distribution:')
    for line in f103r_text.split('\n'):
        if line.strip().startswith('L'):
            lnum = line.strip()[:4]
            ings = extract_ingredients_from_text(line)
            specific = ings - GENERIC_INGREDIENTS
            if specific:
                print(f'    {lnum}: {specific}')

    # Step 2: Match against known Antidotarium recipes
    print(f'\n--- STEP 2: Match f103r fingerprint against Antidotarium recipes ---')
    print(f'\n  f103r specific fingerprint: {f103r_specific}')
    print(f'\n  {"RECIPE":30s} {"OVERLAP":>8s} {"JACCARD":>8s} {"SHARED":40s} {"MISSING FROM VMS":30s}')
    print('-' * 130)

    results = []
    for recipe_name, recipe_ings in ANTIDOTARIUM_RECIPES.items():
        recipe_specific = recipe_ings - GENERIC_INGREDIENTS
        overlap = f103r_specific & recipe_specific
        missing_from_vms = recipe_specific - f103r_specific
        missing_from_recipe = f103r_specific - recipe_specific
        j = jaccard(f103r_specific, recipe_specific)

        results.append((recipe_name, len(overlap), j, overlap, missing_from_vms))
        print(f'  {recipe_name:30s} {len(overlap):4d}/{len(recipe_specific):2d}  {j:8.3f}  {str(overlap):40s} miss: {missing_from_vms}')

    results.sort(key=lambda x: (-x[1], -x[2]))
    print(f'\n  BEST MATCH: {results[0][0]} with {results[0][1]} shared ingredients, Jaccard={results[0][2]:.3f}')

    # Step 3: Search for ingredient clusters in the corpus
    print(f'\n--- STEP 3: Search for matching clusters in corpus_pharma ---')
    corpus_path = 'CORPORA_FINAL/corpus_pharma.txt'
    if os.path.exists(corpus_path):
        windows = extract_ingredients_from_corpus_windows(corpus_path, window_size=150)
        print(f'  Found {len(windows)} windows with 3+ ingredients')

        # Match windows against f103r fingerprint
        best_windows = []
        for pos, window_ings, context in windows:
            window_specific = window_ings - GENERIC_INGREDIENTS
            overlap = f103r_specific & window_specific
            if len(overlap) >= 3:
                j = jaccard(f103r_specific, window_specific)
                best_windows.append((pos, j, len(overlap), overlap, context))

        best_windows.sort(key=lambda x: (-x[2], -x[1]))

        print(f'  Windows with 3+ shared specific ingredients: {len(best_windows)}')
        print(f'\n  {"POS":>8s} {"OVERLAP":>8s} {"JACCARD":>8s} {"SHARED":40s} {"CONTEXT":50s}')
        print('-' * 120)
        for pos, j, n_overlap, overlap, context in best_windows[:20]:
            print(f'  {pos:8d} {n_overlap:4d}     {j:8.3f}  {str(overlap):40s} {context[:50]}')

    # Step 4: Do the same for other pharma folios
    print(f'\n--- STEP 4: Fingerprint other pharma folios ---')
    pharma_folios = ['f88r', 'f99r', 'f101r', 'f108r', 'f111r', 'f75r']
    for fid in pharma_folios:
        path = f'VSV12/v12/output/{fid}.txt'
        if not os.path.exists(path):
            path = f'v12/output/{fid}_v12.txt'
        if not os.path.exists(path):
            continue
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
        ings = extract_ingredients_from_text(text)
        specific = ings - GENERIC_INGREDIENTS
        if specific:
            # Find best matching recipe
            best_recipe = None
            best_overlap = 0
            for rname, rings in ANTIDOTARIUM_RECIPES.items():
                rspec = rings - GENERIC_INGREDIENTS
                overlap = len(specific & rspec)
                if overlap > best_overlap:
                    best_overlap = overlap
                    best_recipe = rname
            print(f'  {fid:8s}: {specific} -> best: {best_recipe} ({best_overlap} shared)')


if __name__ == '__main__':
    main()
