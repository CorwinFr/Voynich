#!/usr/bin/env python3
"""
AXE 2: Recipe fingerprint matching.
Cross-matches decoded folio ingredients against known medieval recipes.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from v12.config import Config
from v12.pipeline import VoynichPipeline
from v12.loaders.transcription import parse_folio

# Pharmaceutical ingredients (standardized name -> latin forms)
INGREDIENTS = {
    'aloe':     ['aloes', 'aloe', 'aloem', 'aloet'],
    'asarum':   ['asari', 'asarum', 'asaro', 'asara'],
    'apium':    ['apii', 'apium', 'apio', 'petroselini'],
    'thus':     ['turis', 'thus', 'ture', 'thuris', 'libani'],
    'crocus':   ['croci', 'crocus', 'croco'],
    'mastix':   ['masticis', 'mastix', 'mastice'],
    'nardus':   ['nardi', 'nardus', 'nardo', 'spica'],
    'oleum':    ['olei', 'oleum', 'oleo', 'olen'],
    'mel':      ['mellis', 'mel', 'melle'],
    'vinum':    ['vini', 'vinum', 'vino', 'uin'],
    'aqua':     ['aqua', 'aquam', 'aquae', 'aquis'],
    'piper':    ['piperis', 'piper', 'pipere'],
    'cinnamon': ['cinamomi', 'cinnamomi', 'casie', 'cassie'],
    'zingiber': ['zinziberis', 'zingiber', 'zedoarie'],
    'opium':    ['opii', 'opium', 'opio'],
    'rosa':     ['rosarum', 'rosa', 'rose', 'rosaceum'],
    'myrrha':   ['mirre', 'myrrha', 'myrrhae', 'mirra'],
    'camphora': ['camphore', 'camphora'],
    'hiera':    ['hiera', 'ierapigra', 'hierae', 'iera'],
    'cicuta':   ['cicura', 'cichorium', 'cichorea'],
    'dolor':    ['dolor', 'dolorem', 'dolore', 'dolens'],
    'aperiens': ['aperiens', 'aperientem', 'aperiendi'],
    'cibus':    ['cibus', 'cibo', 'cibum', 'ciboque', 'cibolis'],
}

PREP_VERBS = {
    'recipe':   ['recipe', 'recipiat'],
    'coque':    ['coque', 'coquendo', 'coquas', 'coquant', 'coquam', 'coquens'],
    'misce':    ['misce', 'miscendo'],
    'ciere':    ['ciere', 'cies', 'ciens', 'cieo'],
    'ede':      ['ede', 'edere', 'edens'],
    'da':       ['da', 'detur', 'dare'],
}

KNOWN_RECIPES = {
    'Aurea Alexandrina': {
        'ingredients': {'asarum', 'thus', 'aloe', 'apium', 'cinnamon', 'zingiber',
                        'crocus', 'mastix', 'nardus', 'myrrha'},
    },
    'Metridatum': {
        'ingredients': {'asarum', 'apium', 'thus', 'myrrha', 'crocus', 'nardus',
                        'piper', 'zingiber', 'opium', 'rosa'},
    },
    'Hiera Picra': {
        'ingredients': {'aloe', 'asarum', 'mastix', 'crocus', 'nardus', 'cinnamon'},
    },
    'Theriac': {
        'ingredients': {'opium', 'myrrha', 'crocus', 'piper', 'zingiber', 'nardus',
                        'cinnamon', 'rosa', 'thus'},
    },
    'Circa Instans decoction': {
        'ingredients': {'aqua', 'hiera', 'cibus'},
    },
    'Hiera + Aloes compound': {
        'ingredients': {'hiera', 'aloe', 'aqua', 'cibus'},
    },
}

def main():
    config = Config()
    pipeline = VoynichPipeline(config)
    pipeline.load()

    pharma_folios = ['f103r', 'f108r', 'f88r', 'f75r', 'f111r', 'f1r',
                     'f9v', 'f15r', 'f41r', 'f37r']

    folio_ingredients = {}
    folio_verbs = {}
    folio_total_words = {}

    for fid in pharma_folios:
        lines, sec = parse_folio('data/transcriptions/ZL.txt', fid)
        if not lines:
            for s in ['1', '2']:
                lines, sec = parse_folio('data/transcriptions/ZL.txt', fid + s)
                if lines:
                    break
        if not lines:
            continue

        decoded = pipeline.decode_folio(lines)
        total = sum(len(w) for w in decoded.values())
        folio_total_words[fid] = total

        ing_counts = {}
        verb_counts = {}

        for lnum, words in decoded.items():
            for dw in words:
                lat = dw.latin.lower().strip('?[]()_')
                for name, forms in INGREDIENTS.items():
                    for form in forms:
                        if form in lat:
                            ing_counts[name] = ing_counts.get(name, 0) + 1
                            break
                for name, forms in PREP_VERBS.items():
                    for form in forms:
                        if form in lat:
                            verb_counts[name] = verb_counts.get(name, 0) + 1
                            break

        folio_ingredients[fid] = ing_counts
        folio_verbs[fid] = verb_counts

    # Print ingredient matrix
    print('=' * 100)
    print('AXE 2 : RECIPE FINGERPRINT MATCHING')
    print('=' * 100)

    all_ings = sorted(set(i for d in folio_ingredients.values() for i in d.keys()))

    print('\n--- INGREDIENT MATRIX (counts) ---')
    header = f'{"Folio":10s} {"Words":>5s}' + ''.join(f' {i:>7s}' for i in all_ings)
    print(header)
    print('-' * len(header))
    for fid in pharma_folios:
        if fid not in folio_ingredients:
            continue
        ings = folio_ingredients[fid]
        total = folio_total_words.get(fid, 0)
        row = f'{fid:10s} {total:5d}' + ''.join(f' {ings.get(i,0):7d}' for i in all_ings)
        print(row)

    # Print verb matrix
    all_verbs = sorted(set(v for d in folio_verbs.values() for v in d.keys()))
    print('\n--- PREPARATION VERB MATRIX ---')
    header = f'{"Folio":10s} {"Words":>5s}' + ''.join(f' {v:>8s}' for v in all_verbs)
    print(header)
    print('-' * len(header))
    for fid in pharma_folios:
        if fid not in folio_verbs:
            continue
        verbs = folio_verbs[fid]
        total = folio_total_words.get(fid, 0)
        row = f'{fid:10s} {total:5d}' + ''.join(f' {verbs.get(v,0):8d}' for v in all_verbs)
        print(row)

    # Recipe matching
    print('\n--- RECIPE MATCHING (overlap score) ---')
    print(f'{"Recipe":30s} {"Needs":>5s}', end='')
    for fid in pharma_folios:
        if fid in folio_ingredients:
            print(f' {fid:>8s}', end='')
    print()
    print('-' * 120)

    for recipe_name, recipe in KNOWN_RECIPES.items():
        needed = recipe['ingredients']
        print(f'{recipe_name:30s} {len(needed):5d}', end='')
        for fid in pharma_folios:
            if fid not in folio_ingredients:
                continue
            ings = set(folio_ingredients[fid].keys())
            overlap = ings & needed
            score = len(overlap)
            pct = score * 100 // len(needed) if needed else 0
            print(f' {score:2d}/{len(needed):2d} {pct:3d}%', end='')
        print()

    # Detail best matches
    print('\n--- BEST MATCHES (detail) ---')
    for recipe_name, recipe in KNOWN_RECIPES.items():
        needed = recipe['ingredients']
        for fid in pharma_folios:
            if fid not in folio_ingredients:
                continue
            ings = set(folio_ingredients[fid].keys())
            overlap = ings & needed
            missing = needed - ings
            score = len(overlap)
            if score >= 3:
                print(f'\n  {recipe_name} x {fid}: {score}/{len(needed)}')
                print(f'    FOUND:   {overlap}')
                print(f'    MISSING: {missing}')
                # Show counts of found ingredients
                for ing in sorted(overlap):
                    count = folio_ingredients[fid][ing]
                    print(f'      {ing:15s} x{count}')


if __name__ == '__main__':
    main()
