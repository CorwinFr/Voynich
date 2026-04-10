"""
L04 TRANSPOSITION CRACK — Test ALL anagrams/permutations/shifts.

DISCOVERY: `aros` (j13) is an anagram of `rosa` (herb of mansion 16).
If L04 uses a transposition cipher (rearrangement of letters/tokens),
we can crack it by testing all permutations against a dictionary.

With tokens of length 3-6, permutations range from 6 to 720 — tractable.
"""
import sys, os
from itertools import permutations
from collections import Counter, defaultdict

# ── EVA TOKENIZER ─────────────────────────────────────────────────
EVA_MULTI = ['aiin','eee','ain','iin','sh','ch','ee','ai','in','ii']

def tokenize(word):
    tokens = []
    i = 0
    while i < len(word):
        matched = False
        for length in [4,3,2]:
            if i + length <= len(word):
                chunk = word[i:i+length]
                if chunk in EVA_MULTI:
                    tokens.append(chunk)
                    i += length
                    matched = True
                    break
        if not matched:
            tokens.append(word[i])
            i += 1
    return tokens

# ── L04 ───────────────────────────────────────────────────────────
L04 = [
    (1,'daiin'),(2,'otey'),(3,'ofeeey'),(4,'shes'),(5,'o'),(6,'d'),
    (7,'okeeod'),(8,'l'),(9,'o'),(10,'lkeeol'),(11,'dkedar'),(12,'yf'),
    (13,'aros'),(14,'s'),(15,'y'),(16,'chedaiin'),(17,'k'),(18,'eeety'),
    (19,'x'),(20,'deeodal'),(21,'vo'),(22,'tchor'),(23,'kedar'),(24,'dal'),
    (25,'daiin'),(26,'aiin'),(27,'otal'),(28,'daro'),(29,'v'),
]

# ── TARGET DICTIONARY (pharmaceutical + astronomical + mansion) ──
TARGETS = set()

# Pharmaceutical terms (Latin)
pharma = [
    'aloe','rosa','crocus','nardus','costus','piper','mastix','ruta',
    'salvia','myrrha','ambra','sulfur','storax','camphora','tus',
    'oleum','aqua','sal','mel','vinum','cera','ferrum','plumbum',
    'aurum','argentum','cuprum','stannum','resina','gummi','opium',
    'cassia','casia','senna','galanga','cubeba','zedoaria','zingiber',
    'muscus','lignum','cornu','ficus','piscis','asarum','cicuta',
    'aconitum','mandragora','papaver','cannabis','absinthium',
    'artemisia','plantago','verbena','betonica','centaurea',
    'euphorbium','aristolochia','staphisagria','olibanum','thus',
    'coque','tere','misce','cola','recipe','fiat','detur',
    'herba','radix','folia','semen','cortex','flores','succus',
    'pulvis','extractum','infusum','decoctum','unguentum',
    'emplastrum','pilula','electuarium','sirupus','potio',
    'drachma','uncia','libra','grana','scrupulum',
    'acre','acris','dulce','dulcis','amara','amarus',
    'calida','frigida','humida','sicca','calidus','frigidus',
    'alba','rubra','nigra','viridis','flava',
    'maior','minor','vera','vulgaris','silvestris',
    'sapa','sapo','cera','pix','butyrum','adeps',
    'renes','costa','dorsum','caput','venter','stomachus',
    'oculus','cor','pes','genu','tibia','femur','nates',
    'brachium','anus','ruta','menta','salvia',
    # Star names
    'aldebaran','sirius','vega','altair','arcturus','spica',
    'regulus','antares','capella','procyon','deneb','canopus',
    'polaris','rigel','betelgeuse','fomalhaut','alpheratz',
    'markab','denebola','algol','alnath','alnair','alphard',
    'alphecca','dubhe','menkar','alioth','alkaid','bellatrix',
    'scheat','alhena','almach','algenib','algorab','alnilam','alnitak',
    # Mansion names (Latin/Arabic)
    'alnath','alvach','albotain','azoraya','aldebaran','almices',
    'athaya','aldirah','nathra','atarf','algebha','azobra',
    'acarfa','alhayra','spica','azimech','algafra','azubene',
    'alichil','alcalb','exaula','nahaym','elbelda','pastor',
    'arcexe','almisdam','algarf','cornua','venter','oculus',
    'corona','chelae','cauda','frons','nebula','desertum',
    'felicitas','tentoria','prior','posterior','deglutiens',
    # Suffumigations
    'storax','lignum','muscus','santalum','sulfur','resina',
    'olibanum','species','pilus','argentum','asafoetida',
    # Medical terms
    'morbus','febris','dolor','cura','sanare','languere',
    'mori','vivere','sanus','infirmus','aegrotus',
    # Elements
    'aqua','terra','ignis','aer','luna','sol',
    # Numbers
    'unus','duo','tres','quatuor','quinque','sex','septem',
    'octo','novem','decem','primus','secundus','tertius',
    # Zodiac
    'aries','taurus','gemini','cancer','leo','virgo',
    'libra','scorpio','sagittarius','capricornus','aquarius','pisces',
    # Common short Latin
    'dies','hora','lux','nox','rex','pax','vox','lex','dux',
    'ars','mors','sors','flos','bos','mus','rus','ius',
    'est','vel','sed','per','pro','sub','cum','sine',
    'ante','post','inter','supra','infra','extra','ultra',
]
TARGETS = set(t.lower() for t in pharma)

# Also add reversed versions to catch mirror ciphers
TARGETS_REV = {t[::-1]: t for t in TARGETS if len(t) >= 3}


def test_all_permutations(tokens, max_perms=5000):
    """Generate all permutations of tokens, join, check against targets."""
    hits = []
    n = len(tokens)
    if n > 7:
        return hits  # too many permutations

    seen = set()
    for perm in permutations(range(n)):
        reordered = ''.join(tokens[i] for i in perm)
        if reordered in seen:
            continue
        seen.add(reordered)

        if reordered in TARGETS:
            hits.append(('EXACT', reordered, list(perm)))
        if reordered in TARGETS_REV:
            hits.append(('REVERSE_OF', TARGETS_REV[reordered], list(perm)))

        # Also check if it's a known word with different tokenization
        # (treat as raw characters)
        if len(seen) > max_perms:
            break

    return hits


def test_systematic_shifts(tokens):
    """Test cyclic shifts: rotate left by 1, 2, ..., n-1."""
    hits = []
    n = len(tokens)
    for shift in range(1, n):
        shifted = tokens[shift:] + tokens[:shift]
        word = ''.join(shifted)
        if word in TARGETS:
            hits.append(('SHIFT_L', shift, word))
        rev = word[::-1]
        if rev in TARGETS:
            hits.append(('SHIFT_L_REV', shift, rev))
    return hits


def test_char_level_anagram(word):
    """Test all character-level permutations (not token-level)."""
    if len(word) > 8:
        return []
    hits = []
    seen = set()
    for perm in permutations(word):
        reordered = ''.join(perm)
        if reordered in seen:
            continue
        seen.add(reordered)
        if reordered in TARGETS:
            hits.append(('CHAR_ANAGRAM', reordered))
        if len(seen) > 50000:
            break
    return hits


def test_pair_swaps(tokens):
    """Test swapping adjacent pairs."""
    hits = []
    n = len(tokens)
    for i in range(n - 1):
        swapped = list(tokens)
        swapped[i], swapped[i+1] = swapped[i+1], swapped[i]
        word = ''.join(swapped)
        if word in TARGETS:
            hits.append(('SWAP', i, i+1, word))
    return hits


def test_reverse(tokens):
    """Test simple reversal."""
    rev = ''.join(tokens[::-1])
    if rev in TARGETS:
        return [('REVERSE', rev)]
    return []


def main():
    out = []
    out.append("# L04 TRANSPOSITION CRACK — Anagrammes et permutations")
    out.append("")
    out.append("Pour chaque mot L04, on teste :")
    out.append("1. TOUTES les permutations de tokens (token-level)")
    out.append("2. TOUTES les permutations de caracteres (char-level)")
    out.append("3. Rotations cycliques (shift left/right)")
    out.append("4. Echanges de paires adjacentes")
    out.append("5. Inversion (miroir)")
    out.append("")
    out.append(f"Dictionnaire : {len(TARGETS)} termes cibles")
    out.append("")

    total_hits = 0
    all_results = []

    for day, word in L04:
        if len(word) <= 1:
            continue

        tokens = tokenize(word)
        hits = []

        # Token-level permutations
        token_hits = test_all_permutations(tokens)
        hits.extend([(h[0], h[1], f"tokens:{h[2]}") for h in token_hits])

        # Systematic shifts
        shift_hits = test_systematic_shifts(tokens)
        hits.extend([(h[0], h[2], f"shift={h[1]}") for h in shift_hits])

        # Reverse
        rev_hits = test_reverse(tokens)
        hits.extend([(h[0], h[1], "reversed") for h in rev_hits])

        # Pair swaps
        swap_hits = test_pair_swaps(tokens)
        hits.extend([(h[0], h[3], f"swap({h[1]},{h[2]})") for h in swap_hits])

        # Character-level anagram
        char_hits = test_char_level_anagram(word)
        hits.extend([(h[0], h[1], "char-level") for h in char_hits])

        if hits:
            total_hits += len(hits)
            out.append(f"## j{day} `{word}` → tokens: {tokens}")
            for htype, result, detail in hits:
                marker = " *** STRONG ***" if htype in ('EXACT', 'CHAR_ANAGRAM') else ""
                out.append(f"  **{htype}**: `{result}` ({detail}){marker}")
                all_results.append((day, word, htype, result, detail))
            out.append("")
        else:
            out.append(f"j{day} `{word}` → no matches")

    out.append("")
    out.append("---")
    out.append(f"## BILAN: {total_hits} hits sur {sum(1 for d,w in L04 if len(w)>1)} mots-contenu")
    out.append("")

    if all_results:
        out.append("### TOUS LES HITS")
        out.append("| Jour | EVA | Type | Resultat | Detail |")
        out.append("|------|-----|------|----------|--------|")
        for day, word, htype, result, detail in all_results:
            out.append(f"| {day:2d} | {word:10s} | {htype:15s} | {result:15s} | {detail} |")

    out.append("")

    # Check consistency of character-level anagram mappings
    if all_results:
        out.append("### ANALYSE DE COHERENCE DES ANAGRAMMES")
        out.append("")
        char_anagrams = [(d, w, r) for d, w, t, r, det in all_results
                         if t == 'CHAR_ANAGRAM']
        if char_anagrams:
            out.append("Paires EVA → Latin (anagrammes confirmes) :")
            for day, eva, latin in char_anagrams:
                # Derive letter mapping
                out.append(f"  j{day}: `{eva}` → `{latin}`")
                out.append(f"    Letters EVA: {sorted(eva)}")
                out.append(f"    Letters Latin: {sorted(latin)}")
                if sorted(eva) == sorted(latin):
                    out.append(f"    *** ANAGRAMME PARFAIT (memes lettres) ***")
                else:
                    out.append(f"    Lettres differentes — substitution + transposition")
            out.append("")

    report = '\n'.join(out)
    out_path = os.path.join(os.path.dirname(__file__), '..', 'output', 'L04_TRANSPOSITION.md')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"Report: {out_path}")
    for line in report.split('\n'):
        if '***' in line or line.startswith('##') or 'BILAN' in line or 'EXACT' in line or 'ANAGRAM' in line:
            print(line)


if __name__ == '__main__':
    main()
