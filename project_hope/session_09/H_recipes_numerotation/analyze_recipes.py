"""
Analyze star-delimited pharma recipes: structure, doses, numbering.
"""
import json, sys, io, os
from collections import Counter, defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

VMS_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'vms', 'vms_structured.json')
RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')

LOGOGRAMS = {'o','l','d','r','v','x','k','m','f','t','y','c','s','sh','p','air'}

with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)

# ================================================================
# Extract ALL star-delimited recipes
# ================================================================
recipes = []
for fid, folio in vms['folios'].items():
    if folio['metadata']['section'] != 'pharma':
        continue
    for block in folio['blocks']:
        if not block.get('separator'):
            continue

        words = []
        for line in block['lines']:
            for w in line['words']:
                eva = w['eva_primary']
                morph = w.get('morphology', {})

                if eva in LOGOGRAMS:
                    tag = 'LOGO'
                elif morph.get('is_dose_candidate'):
                    ic = morph.get('i_count', 0)
                    tag = 'D%d' % ic if ic else 'D?'
                elif morph.get('suffix') in ('am', 'om'):
                    tag = 'END'
                elif morph.get('n_glyphs', 0) >= 5:
                    tag = 'LONG'
                elif len(eva) >= 4:
                    tag = 'MED'
                else:
                    tag = 'SHORT'

                words.append({
                    'eva': eva, 'tag': tag,
                    'suffix': morph.get('suffix', ''),
                    'root': morph.get('root', ''),
                    'i_count': morph.get('i_count'),
                })

        recipes.append({
            'block_id': block['block_id'],
            'folio': fid,
            'n_words': len(words),
            'words': words,
        })

print('=' * 70)
print('RECETTES PHARMA (etoiles uniquement): %d' % len(recipes))
print('=' * 70)

lens = [r['n_words'] for r in recipes]
doses_per = [sum(1 for w in r['words'] if w['tag'].startswith('D')) for r in recipes]
logos_per = [sum(1 for w in r['words'] if w['tag'] == 'LOGO') for r in recipes]

print('Tokens/recette: min=%d max=%d avg=%.1f median=%d' % (
    min(lens), max(lens), sum(lens)/len(lens), sorted(lens)[len(lens)//2]))
print('Doses/recette:  min=%d max=%d avg=%.1f' % (
    min(doses_per), max(doses_per), sum(doses_per)/len(doses_per)))
print('Logos/recette:  min=%d max=%d avg=%.1f' % (
    min(logos_per), max(logos_per), sum(logos_per)/len(logos_per)))

# ================================================================
# STRUCTURE: tag sequences
# ================================================================
print()
print('=' * 70)
print('ECHANTILLON: 20 premieres recettes')
print('=' * 70)

for r in recipes[:20]:
    tag_seq = ' '.join(w['tag'] for w in r['words'])
    n_d = sum(1 for w in r['words'] if w['tag'].startswith('D'))
    n_l = sum(1 for w in r['words'] if w['tag'] == 'LONG')
    dose_words = [w['eva'] for w in r['words'] if w['tag'].startswith('D')]
    print('%s [%2dw %2dL %2dD] %s' % (
        r['block_id'], r['n_words'], n_l, n_d, ' '.join(dose_words) if dose_words else '-'))
    print('  %s' % tag_seq)
    print()

# ================================================================
# CONTEXTE des doses
# ================================================================
print('=' * 70)
print('CONTEXTE DES DOSES')
print('=' * 70)

before = Counter()
after = Counter()
d1_pos = []
d2_pos = []
d1_before_word = Counter()
d2_before_word = Counter()
d1_after_word = Counter()
d2_after_word = Counter()

for r in recipes:
    words = r['words']
    n = len(words)
    for i, w in enumerate(words):
        if not w['tag'].startswith('D'):
            continue
        pos = i / max(n-1, 1)

        if i > 0: before[words[i-1]['tag']] += 1
        if i < n-1: after[words[i+1]['tag']] += 1

        if w['tag'] == 'D1':
            d1_pos.append(pos)
            if i > 0: d1_before_word[words[i-1]['eva']] += 1
            if i < n-1: d1_after_word[words[i+1]['eva']] += 1
        elif w['tag'] == 'D2':
            d2_pos.append(pos)
            if i > 0: d2_before_word[words[i-1]['eva']] += 1
            if i < n-1: d2_after_word[words[i+1]['eva']] += 1

print()
print('Avant dose: %s' % before.most_common(6))
print('Apres dose: %s' % after.most_common(6))
print()
print('D1 (-ain): n=%d pos=%.3f' % (len(d1_pos), sum(d1_pos)/len(d1_pos) if d1_pos else 0))
print('D2 (-aiin): n=%d pos=%.3f' % (len(d2_pos), sum(d2_pos)/len(d2_pos) if d2_pos else 0))
print()
print('Mots AVANT D1: %s' % d1_before_word.most_common(8))
print('Mots AVANT D2: %s' % d2_before_word.most_common(8))
print('Mots APRES D1: %s' % d1_after_word.most_common(8))
print('Mots APRES D2: %s' % d2_after_word.most_common(8))

# ================================================================
# D1 vs D2: same ROOT + different i_count on SAME recipe?
# ================================================================
print()
print('=' * 70)
print('MEME RACINE + D1 ET D2 DANS LA MEME RECETTE')
print('=' * 70)

same_root_both = 0
examples = []
for r in recipes:
    roots_d1 = set(w['root'] for w in r['words'] if w['tag'] == 'D1')
    roots_d2 = set(w['root'] for w in r['words'] if w['tag'] == 'D2')
    shared = roots_d1 & roots_d2
    if shared:
        same_root_both += 1
        if len(examples) < 10:
            d1_words = [w['eva'] for w in r['words'] if w['tag'] == 'D1' and w['root'] in shared]
            d2_words = [w['eva'] for w in r['words'] if w['tag'] == 'D2' and w['root'] in shared]
            examples.append((r['block_id'], shared, d1_words, d2_words))

print('Recettes avec meme racine en D1 ET D2: %d / %d (%.0f%%)' % (
    same_root_both, len(recipes), same_root_both*100/len(recipes)))
print()
for bid, shared, d1w, d2w in examples:
    print('  %s: root=%s  D1=%s  D2=%s' % (bid, shared, d1w[:3], d2w[:3]))

# ================================================================
# RATIO D1:D2 par recette (varie-t-il?)
# ================================================================
print()
print('=' * 70)
print('RATIO D1:D2 PAR RECETTE')
print('=' * 70)

ratios = []
for r in recipes:
    nd1 = sum(1 for w in r['words'] if w['tag'] == 'D1')
    nd2 = sum(1 for w in r['words'] if w['tag'] == 'D2')
    if nd1 + nd2 >= 3:
        ratio = nd2 / max(nd1, 0.5)
        ratios.append((r['block_id'], nd1, nd2, ratio))

ratios.sort(key=lambda x: x[3])
print('Recettes avec 3+ doses, triees par ratio D2/D1:')
print('%-15s %4s %4s %8s' % ('Recipe', 'D1', 'D2', 'ratio'))
for bid, d1, d2, rat in ratios:
    bar = '#' * min(int(rat * 5), 40)
    print('%-15s %4d %4d %8.1f  %s' % (bid, d1, d2, rat, bar))

print()
print('Ratio min=%.1f max=%.1f' % (ratios[0][3] if ratios else 0, ratios[-1][3] if ratios else 0))
print('Recettes D1-dominantes (ratio<1): %d' % sum(1 for _,_,_,r in ratios if r < 1))
print('Recettes D2-dominantes (ratio>1): %d' % sum(1 for _,_,_,r in ratios if r > 1))
print('Recettes equilibrees (ratio~1):   %d' % sum(1 for _,_,_,r in ratios if 0.8 <= r <= 1.2))

# Save
json.dump({
    'n_recipes': len(recipes),
    'avg_tokens': sum(lens)/len(lens),
    'avg_doses': sum(doses_per)/len(doses_per),
    'same_root_both_d1_d2': same_root_both,
    'ratio_distribution': [(b,d1,d2,r) for b,d1,d2,r in ratios],
}, open(os.path.join(RESULTS_DIR, 'recipe_analysis.json'), 'w'), indent=2)
print('\nSaved recipe_analysis.json')
