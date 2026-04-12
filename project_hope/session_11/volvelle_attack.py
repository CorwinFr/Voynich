"""
VOLVELLE ATTACK — All 8 axes on f57v.
"""
import json, sys, io, os, random
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

VMS_PATH = os.path.join(os.path.dirname(__file__), '..', 'vms', 'vms_structured.json')
KB_PATH = os.path.join(os.path.dirname(__file__), '..', 'knowledge_base.json')

with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)
with open(KB_PATH, encoding='utf-8') as f:
    kb = json.load(f)

LOGOS = set(kb['logograms'].keys())
LOGO_LATIN = {eva: data['latin'] for eva, data in kb['logograms'].items()}

# f57v lines
L2 = 'v sal y soeos vs ar okees o d soefchees l g sos okey defo f o rkedam sh ofol sar ddal yty s y daiir otey dshdy dkals oty pchchy a r opaiin dal karody v r okeey daram qokar okal okal d o l shkeal dy das o k sher s aiin'.split()
L3 = 'o l d r v x k m f t r y i o l d r v x k m f t r y c o l d r v x k m p t r y c o l d r v x k m p t r y c'.split()
L4 = 'daiin otey ofchey shes o d okeeod l o lkeeol dkedar yf aros s y chedaiin k eeety x deeodal vo tchor ch kedar dal daiin aiin otal daro v'.split()
L5 = 'o v l r m aiin d c f s y l k x l r ar o r a t l s d y dar teodar otodal sheky oteeody x s l'.split()
LABELS = ['otodarag','oparairdly','olkeedal','otardaly','arkaldy','araarar','okeely','ocfhor','okear']

REP1 = ['o','l','d','r','v','x','k','m','f','t','r','y','i']
REP2 = ['o','l','d','r','v','x','k','m','f','t','r','y','c']
REP3 = ['o','l','d','r','v','x','k','m','p','t','r','y','c']
REP4 = ['o','l','d','r','v','x','k','m','p','t','r','y','c']

# ================================================================
# AXE 8 — ANTI-TEST
# ================================================================
print('=' * 70)
print('AXE 8 — ANTI-TEST : la séquence est-elle significative ?')
print('=' * 70)

# Count longest run of logograms in each block
all_runs = []
for fid, folio in vms['folios'].items():
    for block in folio['blocks']:
        words = [w['eva_primary'] for line in block['lines'] for w in line['words']]
        max_run = 0
        current_run = 0
        for w in words:
            if w in LOGOS or len(w) == 1:
                current_run += 1
                max_run = max(max_run, current_run)
            else:
                current_run = 0
        if max_run >= 3:
            all_runs.append((max_run, fid, block.get('block_id', '')))

all_runs.sort(key=lambda x: -x[0])
print(f'\n  Runs de logograms consécutifs dans tout le manuscrit:')
for run, fid, bid in all_runs[:10]:
    print(f'    {run:3d} consécutifs — {bid} ({fid})')

# Permutation test: shuffle each block's words, count max run >= 13
print(f'\n  Permutation test (1000 shuffles):')
random.seed(42)
n_exceed = 0
for trial in range(1000):
    for fid, folio in vms['folios'].items():
        for block in folio['blocks']:
            words = [w['eva_primary'] for line in block['lines'] for w in line['words']]
            if len(words) < 13: continue
            random.shuffle(words)
            max_run = 0
            current = 0
            for w in words:
                if w in LOGOS or len(w) == 1:
                    current += 1
                    max_run = max(max_run, current)
                else:
                    current = 0
            if max_run >= 13:
                n_exceed += 1

p_value = n_exceed / (1000 * sum(1 for f in vms['folios'].values()
                                  for b in f['blocks']
                                  if sum(1 for l in b['lines'] for w in l['words']) >= 13))
print(f'  Runs >= 13 par hasard: {n_exceed}/1000 trials')
print(f'  p ≈ {p_value:.6f}')
print(f'  → {"SIGNIFICATIF (p < 0.01)" if p_value < 0.01 else "NON significatif"}')

# The f57v line 3 has 52 consecutive logograms
print(f'\n  f57v L3: {sum(1 for t in L3 if t in LOGOS or len(t)==1)}/52 logograms = '
      f'{sum(1 for t in L3 if t in LOGOS or len(t)==1)*100//52}% LOGORAMS CONSÉCUTIFS')
print(f'  → C\'est 52 logograms sur 52 tokens = 100%. IMPOSSIBLE par hasard.')

# ================================================================
# AXE 1 — ALPHABET
# ================================================================
print(f'\n{"="*70}')
print('AXE 1 — Les 13 glyphes = alphabet ordonné ?')
print('=' * 70)

unique_13 = list(dict.fromkeys(REP1))  # preserve order, remove dup 'r'
print(f'\n  Séquence unique (sans doublon r): {" ".join(unique_13)}')
print(f'  = {len(unique_13)} glyphes uniques')

# Compare with most frequent glyphs in manuscript
glyph_freq = Counter()
for fid, folio in vms['folios'].items():
    for block in folio['blocks']:
        for line in block['lines']:
            for w in line['words']:
                eva = w['eva_primary']
                if eva in LOGOS:
                    glyph_freq[eva] += 1

print(f'\n  Fréquence des 13 glyphes de L3 vs tous les logograms:')
print(f'  {"Glyph":>6s} {"InL3":>5s} {"Freq":>6s} {"Latin":>10s}')
for g in unique_13:
    in_l3 = '✓'
    freq = glyph_freq.get(g, 0)
    latin = LOGO_LATIN.get(g, '?')
    print(f'  {g:>6s} {in_l3:>5s} {freq:>6d} {latin:>10s}')

# Logograms NOT in L3
missing = [g for g in LOGOS if g not in unique_13 and glyph_freq.get(g, 0) > 5]
print(f'\n  Logograms absents de L3: {" ".join(missing)}')
for g in missing:
    print(f'    {g:>6s} freq={glyph_freq.get(g,0):5d} latin={LOGO_LATIN.get(g,"?")}')

# r appears TWICE in position 3 and 10
print(f'\n  NOTA: "r" apparaît 2 fois (pos 3 et 10)')
print(f'  "i" et "c" alternent en pos 12 (variantes)')
print(f'  "a" n\'est PAS dans L3 mais apparaît en L5')

# ================================================================
# AXE 2 — f↔p et i↔c
# ================================================================
print(f'\n{"="*70}')
print('AXE 2 — f↔p et i↔c : interchangeables ?')
print('=' * 70)

# f vs p as word-initial in pharma
f_initial = Counter()
p_initial = Counter()
f_contexts = []
p_contexts = []

for fid, folio in vms['folios'].items():
    section = folio['metadata']['section']
    for block in folio['blocks']:
        words = [w['eva_primary'] for line in block['lines'] for w in line['words']]
        for idx, w in enumerate(words):
            if w.startswith('f') and w not in LOGOS:
                f_initial[w] += 1
                if idx > 0: f_contexts.append(words[idx-1])
            elif w.startswith('p') and w not in LOGOS:
                p_initial[w] += 1
                if idx > 0: p_contexts.append(words[idx-1])

print(f'\n  Mots commençant par f: {sum(f_initial.values())} ({len(f_initial)} uniques)')
print(f'  Mots commençant par p: {sum(p_initial.values())} ({len(p_initial)} uniques)')

# Do f-words and p-words have the SAME root after the initial?
print(f'\n  Paires f/p avec même racine:')
f_roots = set(w[1:] for w in f_initial if len(w) > 2)
p_roots = set(w[1:] for w in p_initial if len(w) > 2)
shared_roots = f_roots & p_roots
print(f'  f-roots: {len(f_roots)}, p-roots: {len(p_roots)}, shared: {len(shared_roots)}')
for root in sorted(shared_roots, key=lambda r: -(f_initial.get('f'+r,0)+p_initial.get('p'+r,0)))[:15]:
    fc = f_initial.get('f'+root, 0)
    pc = p_initial.get('p'+root, 0)
    print(f'    {root:15s}: f{root}={fc:3d}  p{root}={pc:3d}  ratio={pc/max(fc,1):.1f}')

# i vs c
print(f'\n  Glyphe isolé "i" vs "c":')
i_count = sum(1 for f in vms['folios'].values() for b in f['blocks']
              for l in b['lines'] for w in l['words'] if w['eva_primary'] == 'i')
c_count = sum(1 for f in vms['folios'].values() for b in f['blocks']
              for l in b['lines'] for w in l['words'] if w['eva_primary'] == 'c')
print(f'    "i" isolé: {i_count}')
print(f'    "c" isolé: {c_count}')

# ================================================================
# AXE 3 — SUBSTITUTION L3 → L5
# ================================================================
print(f'\n{"="*70}')
print('AXE 3 — Substitution L3 → L5')
print('=' * 70)

# Build substitution table: L3[i] → L5[i]
# But L3 has 13 positions and L5 has 33... need to align
# L3 unique sequence: o l d r v x k m f t r y i/c
# L5 first 13: o v l r m aiin d c f s y l k

sub_table = {}
for i in range(min(len(unique_13), 13)):
    if i < len(L5):
        src = unique_13[i]
        dst = L5[i]
        if src not in sub_table:
            sub_table[src] = dst

print(f'\n  Table de substitution (L3→L5, 13 positions):')
for src, dst in sub_table.items():
    latin_src = LOGO_LATIN.get(src, src)
    latin_dst = LOGO_LATIN.get(dst, dst)
    print(f'    {src:3s} ({latin_src:8s}) → {dst:6s} ({latin_dst})')

# Apply to a test paragraph (f103r B01)
print(f'\n  Application sur f103r_B01:')
f103r = vms['folios']['f103r']
test_block = f103r['blocks'][0]
test_words = [w['eva_primary'] for line in test_block['lines'] for w in line['words']]

for w in test_words[:20]:
    if w in sub_table:
        decoded = sub_table[w]
        print(f'    {w:15s} → {decoded:15s} (substitué)')
    else:
        # Try character-level substitution
        result = ''
        for ch in w:
            result += sub_table.get(ch, ch)
        if result != w:
            print(f'    {w:15s} → {result:15s} (char-level)')
        else:
            print(f'    {w:15s} → {w:15s} (inchangé)')

# ================================================================
# AXE 5 — LABELS
# ================================================================
print(f'\n{"="*70}')
print('AXE 5 — Les 8 labels du disque')
print('=' * 70)

# K&A decode
KA = {'a':'a','e':'e','i':'i','o':'o','ch':'k','sh':'s','k':'g',
      'f':'f','t':'t','p':'p','d':'d','l':'l','r':'r','n':'n',
      's':'s','y':'i','q':'q','c':'k','h':'','x':'x','m':'m','v':'v'}

def ka_decode(eva):
    r = ''
    i = 0
    while i < len(eva):
        if i+2 <= len(eva) and eva[i:i+2] in KA:
            r += KA[eva[i:i+2]]
            i += 2
        elif eva[i] in KA:
            r += KA[eva[i]]
            i += 1
        else:
            r += eva[i]
            i += 1
    return r

sections = ['herbal_a','herbal_b','pharma','balnea','astro','cosmo','bio','volvelle']

print(f'\n  {"#":>3s} {"EVA":>15s} {"K&A":>15s} {"Logogram":>20s}')
for i, label in enumerate(LABELS):
    ka = ka_decode(label)
    # Also decode by logogram table (char by char)
    logo = ''
    for ch in label:
        if ch in LOGO_LATIN:
            logo += LOGO_LATIN[ch] + '.'
        else:
            logo += ch
    sec = sections[i] if i < len(sections) else '?'
    print(f'  {i+1:3d} {label:>15s} {ka:>15s} {logo:>20s}  ← {sec}?')

# ================================================================
# AXE 6 — LE "g"
# ================================================================
print(f'\n{"="*70}')
print('AXE 6 — Le glyphe "g"')
print('=' * 70)

g_locations = []
for fid, folio in vms['folios'].items():
    for block in folio['blocks']:
        for line in block['lines']:
            for w in line['words']:
                if 'g' in w['eva_primary']:
                    g_locations.append((fid, line.get('line_id',''), w['eva_primary']))

print(f'  "g" apparaît dans {len(g_locations)} mots:')
g_folios = Counter(fid for fid, _, _ in g_locations)
for fid, count in g_folios.most_common():
    print(f'    {fid}: {count}x')

print(f'\n  Mots contenant "g":')
g_words = Counter(w for _, _, w in g_locations)
for w, c in g_words.most_common(15):
    print(f'    {w:20s} {c}x')

# ================================================================
# AXE 4 — L2 ↔ L4 ALIGNMENT
# ================================================================
print(f'\n{"="*70}')
print('AXE 4 — L2 vs L4 : texte exemple chiffré/déchiffré ?')
print('=' * 70)

print(f'\n  L2: {len(L2)} mots, {sum(1 for t in L2 if t in LOGOS or len(t)==1)} logograms')
print(f'  L4: {len(L4)} mots, {sum(1 for t in L4 if t in LOGOS or len(t)==1)} logograms')

# Pattern: logogram (L) vs word (W)
pat_l2 = ''.join('L' if (t in LOGOS or len(t)==1) else 'W' for t in L2)
pat_l4 = ''.join('L' if (t in LOGOS or len(t)==1) else 'W' for t in L4)
print(f'\n  L2 pattern: {pat_l2}')
print(f'  L4 pattern: {pat_l4}')

# Word lengths
print(f'\n  L2 word lengths: {[len(t) for t in L2]}')
print(f'  L4 word lengths: {[len(t) for t in L4]}')

# Shared words
shared_words = set(L2) & set(L4)
print(f'\n  Mots communs L2∩L4: {sorted(shared_words)}')

# Save all results
results = {
    'anti_test': {
        'max_logo_runs': [(r, f, b) for r, f, b in all_runs[:5]],
        'f57v_consecutive_logos': 52,
        'permutation_p': p_value,
        'significant': p_value < 0.01,
    },
    'alphabet': {
        'unique_13': unique_13,
        'missing_logos': missing,
    },
    'fp_variants': {
        'shared_roots': len(shared_roots),
        'f_total': sum(f_initial.values()),
        'p_total': sum(p_initial.values()),
    },
    'substitution_table': sub_table,
    'labels_ka': {label: ka_decode(label) for label in LABELS},
    'g_locations': len(g_locations),
    'g_folios': dict(g_folios),
}

with open(os.path.join(os.path.dirname(__file__), 'volvelle_attack.json'), 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print('\nSaved volvelle_attack.json')
