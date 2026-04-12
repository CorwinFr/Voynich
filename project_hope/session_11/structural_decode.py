"""
STRUCTURAL DECODE — Generic decoding without guessing ingredients.

Each word gets a STRUCTURAL CODE:
  PLANT_fXXx   = root identified in herbal section (IS a plant)
  INGR_N       = pharma root NOT in herbal (mineral? animal? compound?)
  VERB(p/t/k/f)= gallows-initial word at block start
  LOGO(xxx)    = logogram (confirmed Latin word)
  DOSE(iN)     = dosage marker (-ain/-aiin)
  FUNC_N       = functional/grammatical word (high freq, no herbal folio)
  UNK          = too rare to classify

Suffixes appended: .edy .ain .ol .ar etc.

Output: every pharma block decoded structurally.
"""
import json, sys, io, os
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

KB_PATH = os.path.join(os.path.dirname(__file__), '..', 'knowledge_base.json')
VMS_PATH = os.path.join(os.path.dirname(__file__), '..', 'vms', 'vms_structured.json')
RESULTS = os.path.dirname(__file__)

with open(KB_PATH, encoding='utf-8') as f:
    kb = json.load(f)
with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)

LOGOS = {eva: data['latin'] for eva, data in kb['logograms'].items()}
LOGOGRAM_SET = set(LOGOS.keys())

# ================================================================
# 1. CLASSIFY EVERY ROOT
# ================================================================

# Roots with herbal folio = PLANT
plant_roots = {}
for root, data in kb['roots'].items():
    if data.get('herbal_folio'):
        plant_roots[root] = data['herbal_folio']

# Remaining frequent pharma roots = INGR or FUNC
# FUNC = appears in ALL sections roughly equally (grammatical)
# INGR = concentrated in pharma/herbal (content word)

ingr_counter = 0
func_counter = 0
root_codes = {}  # root -> code
ingr_registry = {}  # code -> root
func_registry = {}

for root, data in sorted(kb['roots'].items(), key=lambda x: -x[1]['total_freq']):
    if root in plant_roots:
        root_codes[root] = f'PLANT_{plant_roots[root]}'
        continue

    pharma = data.get('pharma_freq', 0)
    herbal = data.get('herbal_freq', 0)
    total = data.get('total_freq', 0)
    if total < 3:
        continue

    # Heuristic: is this a functional word or a content word?
    # Functional: appears broadly across all sections
    # Content: concentrated in specific sections
    pharma_pct = pharma * 100 // max(total, 1)
    herbal_pct = herbal * 100 // max(total, 1)

    # High block-initial = probably a verb/title root
    block_init = data.get('block_initial_pct', 0)

    if block_init > 30:
        # Probably a recipe opener / verb
        root_codes[root] = f'VERB_{root}'
    elif pharma_pct > 60 or herbal_pct > 60:
        # Concentrated in one section = content word (ingredient)
        ingr_counter += 1
        code = f'INGR_{ingr_counter:03d}'
        root_codes[root] = code
        ingr_registry[code] = {'root': root, 'pharma': pharma, 'herbal': herbal, 'total': total}
    elif total > 50:
        # Very frequent + spread across sections = functional
        func_counter += 1
        code = f'FUNC_{func_counter:03d}'
        root_codes[root] = code
        func_registry[code] = {'root': root, 'pharma': pharma, 'herbal': herbal, 'total': total}
    else:
        # Low frequency, section-mixed = ingredient (probably rare)
        ingr_counter += 1
        code = f'INGR_{ingr_counter:03d}'
        root_codes[root] = code
        ingr_registry[code] = {'root': root, 'pharma': pharma, 'herbal': herbal, 'total': total}

print(f'Root classification:')
print(f'  PLANT:  {len(plant_roots)}')
print(f'  INGR:   {ingr_counter}')
print(f'  FUNC:   {func_counter}')
print(f'  VERB:   {sum(1 for c in root_codes.values() if c.startswith("VERB_"))}')

# ================================================================
# 2. DECODE ALL PHARMA BLOCKS
# ================================================================
print('\nDecoding pharma...')

GALLOWS = {'p': 'Rp', 't': 'Ac', 'k': 'Mi', 'f': 'Fi'}

all_blocks = []
type_counts = Counter()

for fid in sorted(vms['folios'].keys()):
    folio = vms['folios'][fid]
    if folio['metadata']['section'] != 'pharma': continue

    for block in folio['blocks']:
        if not block.get('separator'): continue
        words = [w for line in block['lines'] for w in line['words']]
        if not words: continue

        decoded = []
        for i, w in enumerate(words):
            eva = w['eva_primary']
            morph = w.get('morphology') or {}
            root = morph.get('root', '')
            suffix = morph.get('suffix', '') or ''
            ic = morph.get('i_count')

            # Classify
            if eva in LOGOGRAM_SET:
                code = f'LOGO({LOGOS[eva]})'
                wtype = 'LOGO'
            elif ic is not None:
                code = f'DOSE(i{ic})'
                wtype = 'DOSE'
            elif i == 0 and eva[0] in 'ptkf' and eva not in LOGOGRAM_SET:
                gal = GALLOWS.get(eva[0], '?')
                code = f'VERB({gal})'
                wtype = 'VERB'
            elif root in root_codes:
                code = root_codes[root]
                if suffix:
                    code += f'.{suffix}'
                wtype = code.split('_')[0].split('(')[0]
            else:
                code = f'UNK({eva})'
                wtype = 'UNK'

            type_counts[wtype] += 1
            decoded.append({
                'eva': eva,
                'code': code,
                'type': wtype,
                'suffix': suffix,
            })

        all_blocks.append({
            'block_id': block['block_id'],
            'folio': fid,
            'decoded': decoded,
        })

# ================================================================
# 3. PRINT f103r
# ================================================================
print('\n' + '=' * 70)
print('f103r — STRUCTURAL DECODE')
print('=' * 70)

for db in all_blocks:
    if not db['folio'] == 'f103r': continue

    print(f'\n{"─"*60}')
    print(f'{db["block_id"]}')
    print(f'{"─"*60}')

    # Compact line: just the codes
    codes = [dw['code'] for dw in db['decoded']]
    # Print in lines of ~6 codes
    for start in range(0, len(codes), 6):
        chunk = codes[start:start+6]
        evas = [dw['eva'] for dw in db['decoded'][start:start+6]]
        # Align
        for j in range(len(chunk)):
            width = max(len(chunk[j]), len(evas[j])) + 1
            chunk[j] = chunk[j].ljust(width)
            evas[j] = evas[j].ljust(width)
        print('  ' + ' '.join(evas))
        print('  ' + ' '.join(chunk))
        print()

# ================================================================
# 4. STATISTICS
# ================================================================
print('=' * 70)
print('TYPE DISTRIBUTION')
print('=' * 70)

total = sum(type_counts.values())
for t, n in type_counts.most_common():
    pct = n * 100 // total
    bar = '█' * (pct // 2)
    print(f'  {t:8s}: {n:5d} ({pct:2d}%) {bar}')

# ================================================================
# 5. REGISTRY — what is each code?
# ================================================================

# Save registries
registry = {
    'plants': {code: {'root': root, 'folio': folio}
               for root, folio in plant_roots.items()
               for code in [f'PLANT_{folio}']},
    'ingredients': ingr_registry,
    'functions': func_registry,
    'logograms': {f'LOGO({lat})': {'eva': eva, 'latin': lat}
                  for eva, lat in LOGOS.items()},
    'verbs': {code: {'root': root} for root, code in root_codes.items()
              if code.startswith('VERB_')},
}

# Save everything
output = {
    'type_counts': dict(type_counts),
    'total_words': total,
    'registry': registry,
    'blocks': all_blocks,
}

out_path = os.path.join(RESULTS, 'structural_decode.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

# Human-readable f103r
md_path = os.path.join(RESULTS, 'F103R_STRUCTURAL.md')
with open(md_path, 'w', encoding='utf-8') as f:
    f.write('# f103r — Structural Decode\n\n')
    f.write('```\n')
    f.write('PLANT_fXXx = plant from herbal folio XXx\n')
    f.write('INGR_NNN   = unidentified ingredient #NNN\n')
    f.write('VERB(Xx)   = recipe opener (Rp=Recipe, Ac=Accipe, Mi=Misce, Fi=Fiat)\n')
    f.write('LOGO(xxx)  = logogram (Latin word)\n')
    f.write('DOSE(iN)   = dosage marker\n')
    f.write('FUNC_NNN   = functional/grammatical word\n')
    f.write('.suffix    = grammatical suffix\n')
    f.write('```\n\n')

    for db in all_blocks:
        if db['folio'] != 'f103r': continue
        f.write(f'## {db["block_id"]}\n\n')
        for dw in db['decoded']:
            f.write(f'{dw["eva"]:18s} → {dw["code"]}\n')
        f.write('\n')

print(f'\nSaved structural_decode.json')
print(f'Saved F103R_STRUCTURAL.md')

# Print plant registry
print('\n' + '=' * 70)
print('PLANT REGISTRY')
print('=' * 70)
for root in sorted(plant_roots.keys(), key=lambda r: -kb['roots'].get(r, {}).get('pharma_freq', 0)):
    folio = plant_roots[root]
    pharma = kb['roots'].get(root, {}).get('pharma_freq', 0)
    bot = kb['roots'].get(root, {}).get('botanical_id')
    species = bot.get('species', '?') if bot else '?'
    print(f'  PLANT_{folio:6s} root={root:12s} pharma:x{pharma:3d} → {species}')

print(f'\n  {len(plant_roots)} plants identified by folio')
print(f'  {ingr_counter} unidentified ingredients')
print(f'  {func_counter} functional words')
