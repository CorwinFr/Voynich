"""
BRUTE FORCE f1r — Try EVERYTHING to decode the first page.

Hypothesis: f1r is the author's draft/manual page, not herbal content.
Expected: liber, meus, secretum, hic, est, de, medicina, herba, nomen, etc.

Methods:
1. K&A phonetic
2. Reeds substitution (d->a, r->c, g->y) + K&A
3. Logogram table
4. Syllable concatenation (pairs of consecutive words)
5. Reverse reading
6. Skip patterns
"""
import json, sys, io, os
from collections import Counter
from itertools import combinations

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

RESULTS = os.path.join(os.path.dirname(__file__), 'results')
os.makedirs(RESULTS, exist_ok=True)

# K&A phonetic
KA = {
    'a':'a','e':'e','i':'i','o':'o',
    'ch':'k','sh':'s','k':'g','f':'f',
    't':'t','p':'p','d':'d','l':'l',
    'r':'r','n':'n','s':'s','y':'i',
    'q':'q','c':'k','h':'',
    'x':'x','m':'m','v':'v',
}

REEDS = {'d':'a','r':'c','g':'y'}

LOGOS = {
    'o':'ac','l':'se','d':'de','r':'recipe','v':'vel',
    'x':'crux','k':'cum','m':'misce','f':'per','t':'et',
    'y':'in','c':'cum','s':'est','sh':'ci','p':'usque',
    'ch':'cum','air':'air',
}

TARGETS = set([
    'liber','libri','meus','meum','mea','secretum','secretis','secreto',
    'hic','hoc','hec','est','de','in','et','cum','per',
    'medicina','medicinis','medicinarum','medicus',
    'herba','herbis','herbarum','herbe',
    'nomen','qui','quod','scripsit','fecit','feci',
    'anno','domini','deus','dei','deo',
    'opus','artis','ars','scientia',
    'codex','pharmacum','remedium','antidotarium',
    'ego','iste','ista','istud',
    'recipe','misce','cura','sana',
    'aqua','oleum','sal','rosa','piper',
    'primus','secundus','tertius',
    'caput','capitulum','finis',
    'alpha','beta','gamma',
    'lectio','lectiones','nota','notae',
    'clavis','clave','signum','signa',
])

# f1r lines
F1R_LINES = [
    ['fachys','ykal','ar','ataiin','shol','shory','cthres','y','kor','sholdy'],
    ['sory','ckhar','or','y','kair','chtaiin','shar','ase','cthar','cthar','dan'],
    ['syaiir','sheky','or','ykaiin','shod','cthoary','cthes','daraiin','sy'],
    ['soiin','oteey','oteos','roloty','cthiar','daiin','okaiin','or','okan'],
    ['sair','y','chear','cthaiin','cphar','cfhaiin'],
    ['ydaraishy'],
    ['odar','cy','shol','cphoy','oydar','sh','s','cfhoaiin','shodary'],
    ['yshey','shody','okchoy','otchol','chocthy','os','chy','dain','chor','kos'],
    ['daiin','shos','cfhol','shody'],
    ['dain','os','teody'],
    ['ydain','cphesaiin','ols','cphey','ytain','shoshy','cphodal','es'],
    ['oksho','kshoy','otairin','oteol','okan','shodain','sckhey','daiin'],
    ['shoy','ckhey','kodaiin','cphy','cphodaiils','cthey','sho','oldain','d'],
    ['dain','oiin','chol','odaiin','chodain','chdy','okain','dn','cthy','kod'],
    ['daiin','shckhey','ckeo','r','char','shey','kol','chol','chol','kor','chal'],
    ['sho','chol','shodan','kshy','kchy','d','or','chodaiin','sho','koeam'],
    ['ycho','tchey','chekain','sheo','pshol','dydyd','cthy','daictoy'],
    ['yto','shol','she','kodshey','cphealy','dar','ain','dain','ckhyds'],
    ['dchar','shcthaiin','okaiir','chey','chy','tol','cthols','dlocto'],
    ['shok','chor','chey','dain','ckhey'],
    ['otol','daiiin'],
]

ALL_WORDS = [w for line in F1R_LINES for w in line]

def decode_ka(eva):
    r = ''
    i = 0
    while i < len(eva):
        matched = False
        for dlen in [3,2]:
            if i+dlen <= len(eva) and eva[i:i+dlen] in KA:
                r += KA[eva[i:i+dlen]]
                i += dlen
                matched = True
                break
        if not matched:
            if eva[i] in KA:
                r += KA[eva[i]]
            else:
                r += eva[i]
            i += 1
    return r

def decode_reeds(eva):
    r = ''
    i = 0
    while i < len(eva):
        matched = False
        for dlen in [3,2]:
            if i+dlen <= len(eva) and eva[i:i+dlen] in KA:
                r += KA[eva[i:i+dlen]]
                i += dlen
                matched = True
                break
        if not matched:
            if eva[i] in REEDS:
                r += REEDS[eva[i]]
            elif eva[i] in KA:
                r += KA[eva[i]]
            else:
                r += eva[i]
            i += 1
    return r

def check_target(decoded):
    d = decoded.lower()
    hits = []
    for t in TARGETS:
        if d == t:
            hits.append(('EXACT', t))
        elif len(t) >= 4 and t[:4] in d:
            hits.append(('PREFIX', t))
        elif len(d) >= 4 and d[:4] in t:
            hits.append(('RPREFIX', t))
    return hits

# ================================================================
print('=' * 70)
print('f1r BRUTE FORCE DECODE')
print('=' * 70)

all_hits = []

# METHOD 1 & 2: K&A and Reeds on each word
print('\n--- MÉTHODE 1+2: K&A et Reeds mot par mot ---')
for w in sorted(set(ALL_WORDS), key=lambda x: ALL_WORDS.index(x)):
    ka = decode_ka(w)
    rd = decode_reeds(w)

    hits_ka = check_target(ka)
    hits_rd = check_target(rd)

    if hits_ka or hits_rd or len(w) <= 3:
        print(f'  {w:18s} K&A={ka:15s} Reeds={rd:15s}', end='')
        for typ, tgt in hits_ka:
            print(f' [{typ}:{tgt} via K&A]', end='')
            all_hits.append((w, ka, 'K&A', typ, tgt))
        for typ, tgt in hits_rd:
            print(f' [{typ}:{tgt} via Reeds]', end='')
            all_hits.append((w, rd, 'Reeds', typ, tgt))
        print()

# METHOD 3: Concatenate consecutive word pairs
print('\n--- MÉTHODE 3: Concaténation de paires consécutives ---')
for i in range(len(ALL_WORDS)-1):
    concat = ALL_WORDS[i] + ALL_WORDS[i+1]
    ka = decode_ka(concat)
    rd = decode_reeds(concat)

    hits_ka = check_target(ka)
    hits_rd = check_target(rd)

    if hits_ka or hits_rd:
        pair = f'{ALL_WORDS[i]}+{ALL_WORDS[i+1]}'
        print(f'  {pair:30s} K&A={ka:20s} Reeds={rd:20s}', end='')
        for typ, tgt in hits_ka + hits_rd:
            method = 'K&A' if (typ, tgt) in hits_ka else 'Reeds'
            print(f' [{typ}:{tgt}]', end='')
            all_hits.append((pair, ka if method=='K&A' else rd, f'concat_{method}', typ, tgt))
        print()

# METHOD 4: Triplets
print('\n--- MÉTHODE 4: Triplets consécutifs ---')
for i in range(len(ALL_WORDS)-2):
    concat = ALL_WORDS[i] + ALL_WORDS[i+1] + ALL_WORDS[i+2]
    ka = decode_ka(concat)
    rd = decode_reeds(concat)

    hits_ka = check_target(ka)
    hits_rd = check_target(rd)

    if hits_ka or hits_rd:
        trip = f'{ALL_WORDS[i]}+{ALL_WORDS[i+1]}+{ALL_WORDS[i+2]}'
        print(f'  {trip:40s}', end='')
        for typ, tgt in hits_ka + hits_rd:
            method = 'K&A' if (typ, tgt) in hits_ka else 'Reeds'
            decoded = ka if method == 'K&A' else rd
            print(f' [{typ}:{tgt}={decoded}]', end='')
            all_hits.append((trip, decoded, f'triplet_{method}', typ, tgt))
        print()

# METHOD 5: Reverse reading
print('\n--- MÉTHODE 5: Lecture inversée ---')
for w in sorted(set(ALL_WORDS), key=lambda x: ALL_WORDS.index(x)):
    rev = w[::-1]
    ka = decode_ka(rev)
    rd = decode_reeds(rev)

    hits = check_target(ka) + check_target(rd)
    if hits:
        print(f'  {w:18s} rev={rev:18s} K&A={ka:15s} Reeds={rd:15s}', end='')
        for typ, tgt in hits:
            print(f' [{typ}:{tgt}]', end='')
            all_hits.append((f'REV:{w}', ka, 'reverse', typ, tgt))
        print()

# METHOD 6: First letters of each word (acrostic)
print('\n--- MÉTHODE 6: Acrostiche (premières lettres) ---')
for line_num, line in enumerate(F1R_LINES):
    firsts = ''.join(w[0] for w in line)
    ka = decode_ka(firsts)
    rd = decode_reeds(firsts)
    print(f'  L{line_num+1:02d}: {firsts:20s} K&A={ka:15s} Reeds={rd:15s}')

    hits = check_target(ka) + check_target(rd)
    for typ, tgt in hits:
        all_hits.append((f'acrostic_L{line_num+1}', ka, 'acrostic', typ, tgt))

# METHOD 7: First letters of each LINE
print('\n--- MÉTHODE 7: Acrostiche par ligne ---')
line_firsts = ''.join(line[0][0] for line in F1R_LINES)
print(f'  Premières lettres: {line_firsts}')
print(f'  K&A:  {decode_ka(line_firsts)}')
print(f'  Reeds: {decode_reeds(line_firsts)}')

# Block acrostics
for block_start, block_end, block_name in [(0,6,'B1'),(6,10,'B2'),(10,21,'B3')]:
    block_firsts = ''.join(F1R_LINES[i][0][0] for i in range(block_start, min(block_end, len(F1R_LINES))))
    print(f'  {block_name}: {block_firsts} -> K&A={decode_ka(block_firsts)} Reeds={decode_reeds(block_firsts)}')

# ================================================================
# SUMMARY
# ================================================================
print('\n' + '=' * 70)
print(f'TOTAL HITS: {len(all_hits)}')
print('=' * 70)
for w, decoded, method, typ, tgt in sorted(all_hits, key=lambda x: x[4]):
    print(f'  {tgt:15s} <- {decoded:20s} ({method:15s}) [{typ}] source={w}')

# Save
results = {
    'total_hits': len(all_hits),
    'hits': [{'source': w, 'decoded': d, 'method': m, 'match_type': t, 'target': tgt}
             for w, d, m, t, tgt in all_hits],
}
with open(os.path.join(RESULTS, 'decode_f1r.json'), 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print('\nSaved decode_f1r.json')
