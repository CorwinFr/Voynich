"""Deep analysis of -ain/-aiin/-aiiin as potential dosage system."""
import re, sys, io, json
from collections import Counter, defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('data/transcriptions/ZL.txt', encoding='utf-8') as f:
    zl = f.read()

LOGOGRAMS = {'o','l','d','r','v','x','k','m','f','t','y','c','s','sh','p','air'}
SUFFIXES = ['aiiin','aiin','ain','eedy','edy','eey','ey','dy','ol','or','ar','al','am','om']

def get_sfx(w):
    for s in SUFFIXES:
        if w.endswith(s) and len(w) > len(s):
            return s
    return None

# Parse
all_seq = []
for line in zl.split('\n'):
    mm = re.match(r'<f(\d+)([rv])(\d?)\.(\d+)', line.strip())
    if not mm: continue
    fn = int(mm.group(1))
    fo = 'f%d%s%s' % (fn, mm.group(2), mm.group(3))
    if fn <= 56: sec = 'herbal'
    elif 58 <= fn <= 73: sec = 'astro'
    elif 75 <= fn <= 84: sec = 'balnea'
    elif 85 <= fn <= 102: sec = 'herbal_B'
    elif 103 <= fn <= 116: sec = 'pharma'
    else: continue
    text = re.sub(r'<[^>]*>', '', line.strip())
    text = re.sub(r'<!.*?>', '', text).replace(',', '.').replace('?', '')
    text = re.sub(r'\[[^\]]*:([^\]]*)\]', r'\1', text)
    words = [w for w in re.findall(r'[a-z]+', text) if w]
    for i, w in enumerate(words):
        all_seq.append((w, fo, sec, i, len(words)))

# ================================================================
# TEST A: Same roots with -ain, -aiin, -aiiin
# ================================================================
print('=' * 70)
print('TEST A: MEMES RACINES avec -ain / -aiin / -aiiin')
print('=' * 70)

roots = defaultdict(lambda: {'ain': 0, 'aiin': 0, 'aiiin': 0})
for w, fo, sec, pos, total in all_seq:
    if w.endswith('aiiin') and len(w) > 5:
        roots[w[:-5]]['aiiin'] += 1
    elif w.endswith('aiin') and len(w) > 4:
        roots[w[:-4]]['aiin'] += 1
    elif w.endswith('ain') and len(w) > 3:
        roots[w[:-3]]['ain'] += 1

# Roots with 2+ forms
multi = [(r, d['ain'], d['aiin'], d['aiiin'])
         for r, d in roots.items()
         if sum(1 for v in d.values() if v > 0) >= 2 and sum(d.values()) >= 10]
multi.sort(key=lambda x: -(x[1]+x[2]+x[3]))

print('\nRacines avec 2+ formes (freq>=10):')
print('%-10s %6s %6s %7s  ratio aiin:ain' % ('Root', '-ain', '-aiin', '-aiiin'))
for root, a1, a2, a3 in multi[:20]:
    ratio = '%.1f:1' % (a2 / max(a1, 1))
    print('%-10s %6d %6d %7d  %s' % (root, a1, a2, a3, ratio))

# ================================================================
# TEST B: Context of d+ain / d+aiin / d+aiiin
# ================================================================
print('\n' + '=' * 70)
print('TEST B: CONTEXTE de dain / daiin / daiiin')
print('=' * 70)

for target in ['dain', 'daiin', 'daiiin']:
    before = Counter()
    after = Counter()
    before_sfx = Counter()
    after_sfx = Counter()

    for idx, (w, fo, sec, pos, total) in enumerate(all_seq):
        if w != target: continue
        if idx > 0 and all_seq[idx-1][1] == fo:
            bw = all_seq[idx-1][0]
            before[bw] += 1
            s = get_sfx(bw)
            if s: before_sfx[s] += 1
        if idx < len(all_seq)-1 and all_seq[idx+1][1] == fo:
            aw = all_seq[idx+1][0]
            after[aw] += 1
            s = get_sfx(aw)
            if s: after_sfx[s] += 1

    n = sum(before.values())
    print('\n--- %s (%dx) ---' % (target, n))
    print('  AVANT: %s' % ', '.join('%s(%d)' % (w,c) for w,c in before.most_common(8)))
    print('  APRES: %s' % ', '.join('%s(%d)' % (w,c) for w,c in after.most_common(8)))
    print('  Sfx avant: %s' % ', '.join('-%s(%d)' % (s,c) for s,c in before_sfx.most_common(5)))
    print('  Sfx apres: %s' % ', '.join('-%s(%d)' % (s,c) for s,c in after_sfx.most_common(5)))
    print('  TTR avant: %.2f (%d/%d)' % (len(before)/max(n,1), len(before), n))
    print('  TTR apres: %.2f (%d/%d)' % (len(after)/max(n,1), len(after), n))

# ================================================================
# TEST C: Alternation in pharma
# ================================================================
print('\n' + '=' * 70)
print('TEST C: ALTERNANCE ingredient-dose en pharma')
print('=' * 70)

pharma_tagged = []
for w, fo, sec, pos, total in all_seq:
    if sec != 'pharma': continue
    if w in LOGOGRAMS:
        tag = 'LOGO'
    elif w.endswith('aiiin') and len(w) > 5:
        tag = 'D3'
    elif w.endswith('aiin') and len(w) > 4:
        tag = 'D2'
    elif w.endswith('ain') and len(w) > 3:
        tag = 'D1'
    elif len(w) >= 5:
        tag = 'LONG'
    else:
        tag = 'SHORT'
    pharma_tagged.append((w, tag, fo))

# Tag bigrams
tag_bg = Counter()
for i in range(len(pharma_tagged)-1):
    if pharma_tagged[i][2] == pharma_tagged[i+1][2]:
        tag_bg[pharma_tagged[i][1] + '>' + pharma_tagged[i+1][1]] += 1

print('\nTag bigrams (pharma, top 20):')
for bg, c in tag_bg.most_common(20):
    print('  %-15s %5d' % (bg, c))

print('\nPatterns cles:')
for p in ['LONG>D1','LONG>D2','D1>LONG','D2>LONG','LONG>LONG',
          'D1>D1','D2>D2','D1>D2','D2>D1','SHORT>D1','SHORT>D2',
          'D1>SHORT','D2>SHORT','LOGO>D1','LOGO>D2']:
    print('  %-15s %5d' % (p, tag_bg.get(p, 0)))

# ================================================================
# TEST D: f103r tagged sequence
# ================================================================
print('\n' + '=' * 70)
print('TEST D: f103r SEQUENCE (premier 100 tokens)')
print('=' * 70)
f103r = [(w,tag) for w,tag,fo in pharma_tagged if fo == 'f103r']
for i in range(min(100, len(f103r))):
    w, tag = f103r[i]
    marker = ' <-- DOSE?' if tag in ('D1','D2','D3') else ''
    marker2 = ' <-- LOGO=%s' % LOGOGRAMS.get(w,'') if tag == 'LOGO' else ''
    print('  %3d %-18s [%-5s]%s%s' % (i+1, w, tag, marker, marker2))

# ================================================================
# TEST E: Ratio aiin:ain par FOLIO pharma (varie-t-il?)
# ================================================================
print('\n' + '=' * 70)
print('TEST E: RATIO aiin:ain PAR FOLIO PHARMA')
print('=' * 70)

folio_ain = Counter()
folio_aiin = Counter()
for w, fo, sec, pos, total in all_seq:
    if sec != 'pharma': continue
    if w.endswith('aiin') and not w.endswith('aiiin') and len(w) > 4:
        folio_aiin[fo] += 1
    elif w.endswith('ain') and not w.endswith('aiin') and len(w) > 3:
        folio_ain[fo] += 1

print('\n%-10s %5s %5s %8s' % ('Folio', '-ain', '-aiin', 'ratio'))
folios = sorted(set(list(folio_ain.keys()) + list(folio_aiin.keys())),
                key=lambda x: (int(re.search(r'\d+', x).group()), x))
for fo in folios:
    a1 = folio_ain.get(fo, 0)
    a2 = folio_aiin.get(fo, 0)
    if a1 + a2 < 5: continue
    ratio = a2 / max(a1, 1)
    bar = '#' * int(ratio * 5)
    print('%-10s %5d %5d %8.1f  %s' % (fo, a1, a2, ratio, bar))

# Save all results
json.dump({
    'multi_roots': [(r,a1,a2,a3) for r,a1,a2,a3 in multi[:20]],
    'tag_bigrams': dict(tag_bg.most_common(30)),
    'folio_ratios': {fo: {'ain': folio_ain.get(fo,0), 'aiin': folio_aiin.get(fo,0)} for fo in folios},
}, open('attacks/operation_hope/results/deep_ain_analysis.json', 'w'), indent=2)
print('\nSaved deep_ain_analysis.json')
