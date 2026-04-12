"""
LAST SEARCH — Find ANY crack in the armor.

Look for anomalies, outliers, anything that breaks the pattern:
1. Words that appear ONLY ONCE in the entire manuscript (+ are long)
2. Lines with abnormal character distributions
3. Folios where the system breaks down
4. Words that look like Latin/Italian despite encoding
5. Marginalia and non-Voynich text mixed with Voynich
6. f116v — German text mixed with Voynich words
7. f17r — Latin mixed with Voynich (UV)
8. Repeated exact phrases (cribs)
9. Words with 'g' (rare glyph, possibly different system)
10. The longest words — do they decode differently?
"""
import json, sys, io, os, re
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

VMS_PATH = os.path.join(os.path.dirname(__file__), '..', 'vms', 'vms_structured.json')
ZL_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'transcriptions', 'ZL3b-n.txt')

with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)

# ================================================================
# 1. LONGEST WORDS — unusual encoding?
# ================================================================
print('=' * 70)
print('1. LES 30 MOTS LES PLUS LONGS')
print('=' * 70)

all_words = []
for fid, folio in vms['folios'].items():
    for block in folio['blocks']:
        for line in block['lines']:
            for w in line['words']:
                eva = w['eva_primary']
                if '@' in eva: continue
                all_words.append((len(eva), eva, fid, folio['metadata']['section']))

all_words.sort(key=lambda x: -x[0])
seen = set()
count = 0
for length, word, fid, section in all_words:
    if word in seen: continue
    seen.add(word)
    count += 1
    if count > 30: break
    print(f'  {length:2d} chars: {word:25s} ({fid}, {section})')

# ================================================================
# 2. WORDS THAT LOOK LIKE LATIN/ITALIAN
# ================================================================
print(f'\n{"="*70}')
print('2. MOTS QUI RESSEMBLENT AU LATIN')
print('=' * 70)

LATIN_WORDS = {'rosa','aqua','sal','mel','oleum','vinum','recipe','misce',
               'cera','aloe','opium','ana','fiat','per','cum','est','vel',
               'dosis','herba','radix','folia','semen','cortex',
               'liber','meus','anno','deus','amen','sanctus',
               'maria','jesus','pater','noster','ars','opus'}

word_freq = Counter()
for _, _, _, _ in []:  pass  # reset
for fid, folio in vms['folios'].items():
    for block in folio['blocks']:
        for line in block['lines']:
            for w in line['words']:
                word_freq[w['eva_primary']] += 1

matches = []
for word, freq in word_freq.most_common():
    if word.lower() in LATIN_WORDS:
        matches.append((word, freq))

print(f'\n  Mots EVA identiques à du latin:')
for word, freq in matches:
    latin = word.lower()
    print(f'    {word:15s} freq={freq:4d} → latin: {latin}')

# Also check for near-matches
print(f'\n  Mots proches (edit distance 1):')
for latin in sorted(LATIN_WORDS):
    for word, freq in word_freq.most_common(500):
        if len(word) == len(latin) and sum(a != b for a, b in zip(word, latin)) == 1:
            print(f'    {word:15s} ≈ {latin:15s} (freq={freq})')

# ================================================================
# 3. f116v — GERMAN + VOYNICH (the Rosetta Stone?)
# ================================================================
print(f'\n{"="*70}')
print('3. f116v — TEXTE ALLEMAND + VOYNICH')
print('=' * 70)

f116v = vms['folios'].get('f116v')
if f116v:
    for block in f116v['blocks']:
        for line in block['lines']:
            words = [w['eva_primary'] for w in line['words']]
            print(f'  {line["line_id"]}: {" ".join(words)}')
else:
    print('  f116v not in structured JSON')

# Check ZL3b raw for f116v
print('\n  ZL3b raw:')
with open(ZL_PATH, encoding='utf-8') as f:
    in_f116v = False
    for line in f:
        if '<f116v>' in line:
            in_f116v = True
        if in_f116v and 'f116v' in line:
            print(f'  {line.rstrip()[:120]}')
        if in_f116v and line.startswith('<f') and 'f116v' not in line:
            break

# ================================================================
# 4. f66r — REFERENCE to f57v
# ================================================================
print(f'\n{"="*70}')
print('4. f66r — CROSS-REFERENCE avec f57v')
print('=' * 70)

with open(ZL_PATH, encoding='utf-8') as f:
    for line in f:
        if 'f66r' in line and ('f57v' in line or '@172' in line or '@169' in line):
            print(f'  {line.rstrip()[:120]}')

# ================================================================
# 5. MARGINALIA — all non-standard text
# ================================================================
print(f'\n{"="*70}')
print('5. MARGINALIA et texte non-Voynich')
print('=' * 70)

with open(ZL_PATH, encoding='utf-8') as f:
    for line in f:
        # Look for comments mentioning non-Voynich text
        if '<!doodle' in line.lower() or 'non-voynich' in line.lower() or \
           'latin' in line.lower() or 'german' in line.lower() or \
           'alphabet' in line.lower():
            line_clean = line.rstrip()[:120]
            print(f'  {line_clean}')

# ================================================================
# 6. WORDS WITH 'g' — different system?
# ================================================================
print(f'\n{"="*70}')
print('6. MOTS AVEC g — contexte complet')
print('=' * 70)

g_contexts = []
for fid, folio in vms['folios'].items():
    for block in folio['blocks']:
        for line in block['lines']:
            words = [w['eva_primary'] for w in line['words']]
            for i, w in enumerate(words):
                if 'g' in w:
                    before = words[max(0,i-2):i]
                    after = words[i+1:i+3]
                    g_contexts.append((fid, w, before, after))

print(f'  {len(g_contexts)} mots avec g')
# Group by the g-word itself
g_word_freq = Counter(w for _, w, _, _ in g_contexts)
print(f'\n  Top g-words:')
for w, n in g_word_freq.most_common(10):
    # Show contexts
    ctxs = [(b, a) for f, gw, b, a in g_contexts if gw == w][:3]
    ctx_str = ' | '.join(f'...{" ".join(b)} [{w}] {" ".join(a)}...' for b, a in ctxs)
    print(f'    {w:15s} ({n}x) {ctx_str}')

# ================================================================
# 7. LINES WITH UNUSUAL LOGOGRAM DENSITY
# ================================================================
print(f'\n{"="*70}')
print('7. LIGNES AVEC DENSITÉ INHABITUELLE DE LOGOGRAMS')
print('=' * 70)

LOGOS = {'o','l','d','r','v','x','k','m','f','t','y','c','s','sh','p','ch','air','h'}

unusual_lines = []
for fid, folio in vms['folios'].items():
    if fid == 'f57v': continue  # skip volvelle itself
    for block in folio['blocks']:
        for line in block['lines']:
            words = [w['eva_primary'] for w in line['words']]
            n = len(words)
            if n < 5: continue
            n_logo = sum(1 for w in words if w in LOGOS)
            pct = n_logo * 100 // n
            if pct > 40:
                unusual_lines.append((pct, fid, line.get('line_id',''),
                                     n, n_logo, ' '.join(words[:12])))

unusual_lines.sort(key=lambda x: -x[0])
print(f'\n  Lignes avec >40% logograms (hors f57v):')
for pct, fid, lid, n, nl, text in unusual_lines[:15]:
    section = vms['folios'][fid]['metadata']['section']
    print(f'    {pct:2d}% ({nl}/{n}) {fid:8s} {lid:12s} ({section:10s}) {text}...')

# ================================================================
# 8. HAPAX LEGOMENA — words appearing exactly ONCE
# ================================================================
print(f'\n{"="*70}')
print('8. HAPAX — mots les plus longs apparaissant 1 seule fois')
print('=' * 70)

hapax = [(w, fid) for w, freq in word_freq.items() if freq == 1
         for fid, folio in vms['folios'].items()
         for block in folio['blocks']
         for line in block['lines']
         for ww in line['words']
         if ww['eva_primary'] == w]

# Deduplicate
hapax_unique = {}
for w, fid in hapax:
    if w not in hapax_unique:
        hapax_unique[w] = fid

long_hapax = sorted(hapax_unique.items(), key=lambda x: -len(x[0]))
print(f'\n  Total hapax: {len(hapax_unique)}')
print(f'\n  20 plus longs hapax:')
for word, fid in long_hapax[:20]:
    section = vms['folios'][fid]['metadata']['section']
    print(f'    {len(word):2d} chars: {word:25s} ({fid}, {section})')

# ================================================================
# 9. f1r.6 — ydaraishy (isolated word = signature?)
# ================================================================
print(f'\n{"="*70}')
print('9. MOTS ISOLÉS SUR LEUR PROPRE LIGNE')
print('=' * 70)

for fid, folio in vms['folios'].items():
    for block in folio['blocks']:
        for line in block['lines']:
            words = [w['eva_primary'] for w in line['words']]
            if len(words) == 1 and len(words[0]) > 3:
                section = folio['metadata']['section']
                print(f'  {fid:8s} {line.get("line_id",""):12s} ({section:10s}): {words[0]}')

# Save
print(f'\nDone.')
