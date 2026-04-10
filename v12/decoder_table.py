"""
TABLE-BASED DECODER — No HMM, no probabilities, no beam search.

The Voynich cipher is a LOOKUP TABLE, not a phonetic cipher.
Each glyph (or glyph group) maps to ONE fixed Latin word.
The apothecary read it at a glance, like Tironian notes.

The table is derived from cross-validation of f57v L03 and f66r L16-L49
(bifolio bH1, same physical sheet — 9/9 glyphs match perfectly).

KNOWN (18 glyphs, 100% stable cross-validated):
  o→ac  l→se  d→de  r→recipe  v→vel  x→crux
  k→cum  m→misce  f→per  t→el  y→in  c→cum
  s→est  sh→ci  p→usque  air→aier

UNKNOWN (vowel/filler glyphs):
  a→?  e→?  i→?  n→?  h→?

COMPOUND GLYPHS (digraphs treated as single units):
  ch→?  ee→?  aiin→?  ii→?  in→?
"""

# ══════════════════════════════════════════════════════════════════
# THE TABLE — The only source of truth
# ══════════════════════════════════════════════════════════════════

# Confirmed by bifolio cross-validation (f57v L03 ↔ f66r L16-L49)
GLYPH_TABLE = {
    # CONSONANT-LOGOGRAMS (fixed Latin word per glyph)
    'o':   'ac',       # et/and (conjunction)
    'l':   'se',       # soi/self
    'd':   'de',       # de/from (preposition)
    'r':   'recipe',   # prends/take (pharmaceutical verb)
    'v':   'vel',      # ou/or (conjunction)
    'x':   'crux',     # croix/cross (marker)
    'k':   'cum',      # avec/with (preposition)
    'm':   'misce',    # melange/mix (pharmaceutical verb)
    'f':   'per',      # par/through (preposition)
    't':   'el',       # le/the? or 'l' value
    'y':   'in',       # dans/in (preposition)
    'c':   'cum',      # avec/with (= k)
    's':   'est',      # est/is (copula)
    'p':   'usque',    # jusque/until

    # DIGRAPH-LOGOGRAMS
    'sh':  'ci',       # ci/here
    # 'ch': unknown — most problematic glyph
    # 'ee': unknown
    # 'ph': unknown (related to p=usque + h?)
}

# VOWEL GLYPHS — meaning unknown, probably grammatical
# These appear inside "words" as FILLERS between consonant-logograms
VOWEL_GLYPHS = {
    'a':   '?a',    # unknown — possibly a case marker
    'e':   '?e',    # unknown — possibly a vowel connector
    'i':   '?i',    # unknown — possibly a modifier
    'n':   '?n',    # unknown — possibly a case ending
    'h':   '?h',    # unknown — possibly silent or modifier
}

# COMPOUND SEQUENCES (known multi-glyph units)
COMPOUNDS = {
    'aiin':  '?aiin',   # UNKNOWN — was forced as "aquam", now freed
    'ain':   '?ain',    # shortened form of aiin
    'air':   'aier',    # confirmed on f66r
    'ch':    '?ch',     # the BIG unknown
    'ee':    '?ee',     # double-e, unknown
    'ii':    '?ii',     # double-i, unknown
    'in':    '?in',     # could be y(in) or i+n
}


# ══════════════════════════════════════════════════════════════════
# THE TOKENIZER — Split EVA word into glyph units
# ══════════════════════════════════════════════════════════════════

# Ordered longest-first for greedy matching
GLYPH_UNITS = sorted(
    list(GLYPH_TABLE.keys()) + list(COMPOUNDS.keys()) + list(VOWEL_GLYPHS.keys()),
    key=len, reverse=True
)
# Remove duplicates (single chars that are also in compounds)
# Priority: compounds > table > vowels

def tokenize_to_glyphs(word):
    """Split an EVA word into its constituent glyph units.

    Returns list of (glyph, source) tuples.
    Source = 'TABLE', 'COMPOUND', 'VOWEL', 'UNKNOWN'
    """
    tokens = []
    i = 0
    while i < len(word):
        matched = False

        # Try longest match first
        for length in [4, 3, 2]:
            if i + length <= len(word):
                chunk = word[i:i+length]
                if chunk in COMPOUNDS:
                    tokens.append((chunk, 'COMPOUND'))
                    i += length
                    matched = True
                    break
                elif chunk in GLYPH_TABLE:
                    tokens.append((chunk, 'TABLE'))
                    i += length
                    matched = True
                    break

        if not matched:
            ch = word[i]
            if ch in GLYPH_TABLE:
                tokens.append((ch, 'TABLE'))
            elif ch in VOWEL_GLYPHS:
                tokens.append((ch, 'VOWEL'))
            else:
                tokens.append((ch, 'UNKNOWN'))
            i += 1

    return tokens


# ══════════════════════════════════════════════════════════════════
# THE DECODER — Apply table to produce Latin
# ══════════════════════════════════════════════════════════════════

def decode_word_table(word):
    """Decode an EVA word using the lookup table.

    Returns:
        latin: the decoded Latin string
        known_pct: percentage of glyphs that have known values
        breakdown: list of (glyph, latin_value, source) tuples
    """
    tokens = tokenize_to_glyphs(word)

    breakdown = []
    latin_parts = []
    known = 0
    total = 0

    for glyph, source in tokens:
        total += 1
        if source == 'TABLE':
            value = GLYPH_TABLE[glyph]
            latin_parts.append(value)
            breakdown.append((glyph, value, 'KNOWN'))
            known += 1
        elif source == 'COMPOUND':
            value = COMPOUNDS[glyph]
            latin_parts.append(value)
            breakdown.append((glyph, value, 'COMPOUND'))
            if not value.startswith('?'):
                known += 1
        elif source == 'VOWEL':
            value = VOWEL_GLYPHS[glyph]
            latin_parts.append(value)
            breakdown.append((glyph, value, 'VOWEL'))
        else:
            latin_parts.append(f'[{glyph}]')
            breakdown.append((glyph, f'[{glyph}]', 'UNKNOWN'))

    latin = ' '.join(latin_parts)
    known_pct = known / total * 100 if total > 0 else 0

    return latin, known_pct, breakdown


def decode_line_table(words):
    """Decode a list of EVA words using the table."""
    results = []
    for w in words:
        latin, pct, breakdown = decode_word_table(w)
        results.append((w, latin, pct, breakdown))
    return results


# ══════════════════════════════════════════════════════════════════
# MAIN — Test the table decoder
# ══════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    import sys

    # Test on L03 (the key/formula)
    l03_q1 = ['o','l','d','r','v','x','k','m','f','t','r','y','c']
    print("=== L03 QUADRANT 1 — The pharmaceutical formula ===")
    print()
    for w in l03_q1:
        latin, pct, bd = decode_word_table(w)
        print(f"  {w:3s} → {latin}")
    print()
    formula = ' '.join(GLYPH_TABLE.get(w, f'[{w}]') for w in l03_q1)
    print(f"  FORMULA: {formula}")
    print()

    # Test on L04 (the 29 volvelle labels)
    l04 = ['daiin','otey','ofeeey','shes','o','d','okeeod','l','o','lkeeol',
           'dkedar','yf','aros','s','y','chedaiin','k','eeety','x','deeodal',
           'vo','tchor','kedar','dal','daiin','aiin','otal','daro','v']

    print("=== L04 — 29 volvelle labels (TABLE decode) ===")
    print()
    print(f"{'Pos':>3} {'EVA':>12} {'TABLE decode':>40} {'Known%':>6}")
    print("-" * 65)
    for i, w in enumerate(l04):
        latin, pct, bd = decode_word_table(w)
        print(f"{i+1:>3} {w:>12} {latin:>40} {pct:>5.0f}%")

    print()

    # Test on f103r first 5 lines
    print("=== F103R first lines — TABLE decode ===")
    print()

    import re
    with open('data/transcriptions/ZL.txt', encoding='utf-8') as f:
        raw = f.read()

    for line in raw.split('\n'):
        m = re.match(r'<(f103r\.(\d+))', line.strip())
        if not m: continue
        lnum = int(m.group(2))
        if lnum > 5: break

        text = re.sub(r'<[^>]*>', '', line.strip())
        text = re.sub(r'<!.*?>', '', text)
        text = re.sub(r'<%>|<\$>|\{[^}]*\}|@\d+;?', '', text)
        text = re.sub(r'\[[^\]]*:([^\]]*)\]', r'\1', text)
        text = re.sub(r'\?', '', text).replace(',', '.')
        words = [w.strip() for w in re.findall(r'[a-z]+', text) if w.strip()]

        print(f"L{lnum}: ", end='')
        for w in words:
            latin, pct, bd = decode_word_table(w)
            # Compact: just show the known parts
            compact = []
            for g, v, src in bd:
                if src == 'KNOWN':
                    compact.append(v.upper())
                else:
                    compact.append(v)
            print(f"[{'.'.join(compact)}]", end=' ')
        print()

    # Global stats
    print()
    print("=== COVERAGE STATS ===")
    all_words = []
    for line in raw.split('\n'):
        m = re.match(r'<f\d+[rv]\d?\.\d+', line.strip())
        if not m: continue
        text = re.sub(r'<[^>]*>', '', line.strip())
        text = re.sub(r'<!.*?>', '', text)
        text = re.sub(r'<%>|<\$>|\{[^}]*\}|@\d+;?', '', text)
        text = re.sub(r'\[[^\]]*:([^\]]*)\]', r'\1', text)
        text = re.sub(r'\?', '', text).replace(',', '.')
        words = [w.strip() for w in re.findall(r'[a-z]+', text) if w.strip()]
        all_words.extend(words)

    total_known = 0
    total_glyphs = 0
    for w in all_words:
        latin, pct, bd = decode_word_table(w)
        for g, v, src in bd:
            total_glyphs += 1
            if src == 'KNOWN':
                total_known += 1

    print(f"Total glyphs in VMS: {total_glyphs}")
    print(f"Known (table lookup): {total_known} ({total_known*100//total_glyphs}%)")
    print(f"Unknown: {total_glyphs - total_known} ({(total_glyphs-total_known)*100//total_glyphs}%)")
