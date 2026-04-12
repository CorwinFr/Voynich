"""
PHASE 4+5 — Multi-signal Crack + Decode f103r Recipe 1

Combine ALL signals to produce best-effort decoding.
For each word in f103r B01:
1. Logogram? → direct table lookup
2. Dose? → mark as DOSE
3. Root identified by botanical anchor? → use that
4. Root has w2v candidate? → use highest scoring
5. Otherwise → UNKNOWN

Output: annotated recipe with confidence levels.
"""
import json, sys, io, os
import numpy as np
from collections import Counter
from gensim.models import Word2Vec
from scipy.linalg import orthogonal_procrustes

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

KB_PATH = os.path.join(os.path.dirname(__file__), '..', 'knowledge_base.json')
VMS_PATH = os.path.join(os.path.dirname(__file__), '..', 'vms', 'vms_structured.json')
LATIN_MODEL = os.path.join(os.path.dirname(__file__), '..', 'session_10', 'B_gpu_embeddings', 'results', 'latin_w2v.model')
VMS_MODEL = os.path.join(os.path.dirname(__file__), '..', 'session_10', 'B_gpu_embeddings', 'results', 'vms_w2v.model')

with open(KB_PATH, encoding='utf-8') as f:
    kb = json.load(f)
with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)

# Load w2v for on-the-fly lookup
latin_model = Word2Vec.load(LATIN_MODEL)
vms_model = Word2Vec.load(VMS_MODEL)

LOGOS = {'o':'ac','l':'se','d':'de','r':'recipe','v':'vel','k':'cum','m':'misce',
         'f':'per','t':'et','y':'in','s':'est','sh':'ci','p':'usque','ch':'cum',
         'x':'crux','air':'air','h':'(h)','c':'cum'}
avms, alat = [], []
for e, l in {'o':'ac','l':'se','d':'de','r':'recipe','v':'vel','k':'cum',
             'm':'misce','f':'per','t':'et','y':'in','s':'est','p':'usque'}.items():
    if e in vms_model.wv and l in latin_model.wv:
        avms.append(vms_model.wv[e]); alat.append(latin_model.wv[l])
R, _ = orthogonal_procrustes(np.array(avms), np.array(alat))

# Build w2v lookup function
latin_words = list(latin_model.wv.index_to_key)
latin_vecs = np.array([latin_model.wv[w] for w in latin_words])
latin_norms = np.linalg.norm(latin_vecs, axis=1, keepdims=True) + 1e-10
latin_normed = latin_vecs / latin_norms

# Ingredient-only Latin words (filter from AN)
AN_INGREDIENTS = set()
for entry in kb['an_constraints'].get('top_ingredients', []):
    AN_INGREDIENTS.add(entry['latin'])

def w2v_nearest(eva, top_k=5, ingr_only=False):
    if eva not in vms_model.wv:
        return []
    vec = vms_model.wv[eva] @ R
    vec_norm = vec / (np.linalg.norm(vec) + 1e-10)
    sims = latin_normed @ vec_norm
    top_idx = np.argsort(-sims)[:50]
    results = []
    for i in top_idx:
        w = latin_words[i]
        if ingr_only and w not in AN_INGREDIENTS:
            continue
        results.append((w, float(sims[i])))
        if len(results) >= top_k:
            break
    return results

# ================================================================
# DECODE ALL PHARMA BLOCKS (f103r to f116r)
# ================================================================
print('=' * 70)
print('FULL PHARMA DECODE — f103r to f116r')
print('=' * 70)

LOGOGRAM_SET = set(LOGOS.keys())
GALLOWS_VERBS = {'p': 'RECIPE', 't': 'ACCIPE', 'k': 'MISCE', 'f': 'FIAT'}

total_decoded = 0
total_words = 0
decoded_by_method = Counter()

all_decoded_blocks = []

for fid in sorted(vms['folios'].keys()):
    folio = vms['folios'][fid]
    if folio['metadata']['section'] != 'pharma': continue

    for block in folio['blocks']:
        if not block.get('separator'): continue
        words = [w for line in block['lines'] for w in line['words']]
        if not words: continue

        decoded_words = []
        for i, w in enumerate(words):
            eva = w['eva_primary']
            morph = w.get('morphology') or {}
            root = morph.get('root', '')
            suffix = morph.get('suffix', '') or ''
            ic = morph.get('i_count')

            latin = None
            method = None
            confidence = 0

            # 1. LOGOGRAM
            if eva in LOGOGRAM_SET:
                latin = LOGOS[eva].upper()
                method = 'logogram'
                confidence = 1.0

            # 2. DOSE
            elif ic is not None:
                latin = f'DOSE(i{ic})'
                method = 'morphology'
                confidence = 0.9

            # 3. GALLOWS INITIAL (first word of block)
            elif i == 0 and eva[0] in 'ptkf' and eva not in LOGOGRAM_SET:
                gal = eva[0]
                verb = GALLOWS_VERBS.get(gal, '?')
                latin = f'{verb}({eva})'
                method = 'gallows_verb'
                confidence = 0.7

            # 4. BOTANICAL ANCHOR
            elif root in kb['roots'] and kb['roots'][root].get('cracked_latin'):
                cracked = kb['roots'][root]['cracked_latin']
                status = kb['roots'][root].get('crack_status', '')
                latin = cracked
                if suffix:
                    latin += f'.{suffix}'
                method = f'botanical({status})'
                confidence = 0.6 if status == 'probable' else 0.4

            # 5. W2V NEAREST (ingredient-filtered)
            else:
                nn = w2v_nearest(eva, top_k=3, ingr_only=True)
                if nn:
                    latin = nn[0][0]
                    if suffix:
                        latin += f'.{suffix}'
                    confidence = nn[0][1] * 0.5  # discount w2v
                    method = 'w2v_ingr'
                else:
                    nn_all = w2v_nearest(eva, top_k=1)
                    if nn_all:
                        latin = f'?{nn_all[0][0]}'
                        method = 'w2v_any'
                        confidence = nn_all[0][1] * 0.3

            if latin:
                total_decoded += 1
                decoded_by_method[method] += 1

            total_words += 1
            decoded_words.append({
                'pos': i,
                'eva': eva,
                'latin': latin or '???',
                'method': method or 'unknown',
                'confidence': round(confidence, 2),
                'suffix': suffix,
            })

        all_decoded_blocks.append({
            'block_id': block['block_id'],
            'folio': fid,
            'words': decoded_words,
        })

# ================================================================
# PRINT f103r blocks
# ================================================================
print('\n' + '=' * 70)
print('f103r — DECODED RECIPES')
print('=' * 70)

for db in all_decoded_blocks:
    if not db['folio'].startswith('f103r'): continue

    print(f'\n{"─"*70}')
    print(f'{db["block_id"]}')
    print(f'{"─"*70}')

    for dw in db['words']:
        conf_bar = '█' * int(dw['confidence'] * 5)
        method_short = dw['method'][:8] if dw['method'] else '?'
        print(f'  {dw["eva"]:18s} → {dw["latin"]:25s} [{method_short:8s}] {conf_bar}')

# ================================================================
# SUMMARY
# ================================================================
print('\n' + '=' * 70)
print('DECODE SUMMARY')
print('=' * 70)
print(f'  Total words:    {total_words}')
print(f'  Decoded:        {total_decoded} ({total_decoded*100//total_words}%)')
print(f'  Unknown:        {total_words - total_decoded}')
print(f'\n  By method:')
for method, count in decoded_by_method.most_common():
    print(f'    {method:20s}: {count:5d} ({count*100//total_words}%)')

# ================================================================
# SAVE DECODED OUTPUT
# ================================================================
output = {
    'total_words': total_words,
    'total_decoded': total_decoded,
    'decode_rate': round(total_decoded / total_words, 3),
    'by_method': dict(decoded_by_method),
    'blocks': all_decoded_blocks,
}

out_path = os.path.join(os.path.dirname(__file__), 'F103R_DECODED.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

# Human-readable output for f103r
md_path = os.path.join(os.path.dirname(__file__), 'F103R_DECODED.md')
with open(md_path, 'w', encoding='utf-8') as f:
    f.write('# f103r — DECODED (Phase 5)\n\n')
    f.write(f'Decode rate: {total_decoded*100//total_words}% ({total_decoded}/{total_words})\n\n')
    f.write('Legend: [L]=logogram [D]=dose [G]=gallows [B]=botanical [W]=w2v [?]=unknown\n\n')

    for db in all_decoded_blocks:
        if not db['folio'].startswith('f103r'): continue
        f.write(f'## {db["block_id"]}\n\n')
        f.write('```\n')
        for dw in db['words']:
            tag = {'logogram':'L','morphology':'D','gallows_verb':'G',
                   'botanical(probable)':'B','botanical(weak)':'b',
                   'w2v_ingr':'W','w2v_any':'?'}.get(dw['method'], '?')
            f.write(f'[{tag}] {dw["eva"]:18s} → {dw["latin"]}\n')
        f.write('```\n\n')

print(f'\nSaved F103R_DECODED.json and F103R_DECODED.md')
