"""
L04 CRACK V2 — With proper EVA GLYPH tokenization.

In Voynich script, 'ch', 'sh', 'ee', 'ii', 'ain/aiin' are SINGLE glyphs,
not sequences of letters. This changes word lengths dramatically.

Also tries: bigram/trigram analysis, reverse crib (Latin→EVA mapping tables),
and brute-force with constraint propagation.
"""
import sys, os, re
from collections import Counter, defaultdict
from itertools import combinations

# ── EVA TOKENIZER ─────────────────────────────────────────────────
# Voynich glyphs that are written as multiple EVA characters

EVA_DIGRAPHS = ['sh', 'ch', 'ee', 'ii', 'in', 'ai']  # ordered longest first
EVA_TRIGRAPHS = ['iin', 'ain', 'eee']
EVA_QUADGRAPHS = ['aiin', 'dain', 'oiin']

def tokenize_eva(word):
    """Split EVA word into actual Voynich glyph tokens."""
    tokens = []
    i = 0
    while i < len(word):
        matched = False
        # Try longest first
        for length in [4, 3, 2]:
            if i + length <= len(word):
                chunk = word[i:i+length]
                if length == 4 and chunk in EVA_QUADGRAPHS:
                    tokens.append(chunk)
                    i += length
                    matched = True
                    break
                elif length == 3 and chunk in EVA_TRIGRAPHS:
                    tokens.append(chunk)
                    i += length
                    matched = True
                    break
                elif length == 2 and chunk in EVA_DIGRAPHS:
                    tokens.append(chunk)
                    i += length
                    matched = True
                    break
        if not matched:
            tokens.append(word[i])
            i += 1
    return tokens


# ── L04 DATA ──────────────────────────────────────────────────────

L04_WORDS = [
    (1,  'daiin'),    (2,  'otey'),     (3,  'ofeeey'),   (4,  'shes'),
    (5,  'o'),        (6,  'd'),        (7,  'okeeod'),    (8,  'l'),
    (9,  'o'),        (10, 'lkeeol'),   (11, 'dkedar'),    (12, 'yf'),
    (13, 'aros'),     (14, 's'),        (15, 'y'),         (16, 'chedaiin'),
    (17, 'k'),        (18, 'eeety'),    (19, 'x'),         (20, 'deeodal'),
    (21, 'vo'),       (22, 'tchor'),    (23, 'kedar'),     (24, 'dal'),
    (25, 'daiin'),    (26, 'aiin'),     (27, 'otal'),      (28, 'daro'),
    (29, 'v'),
]

# Mansion data (names, herbs, stones, body parts, Latin names)
MANSIONS = {
    1:  {'names': ['alnath','alnach','alvach','horns','cornua'], 'herb': 'plantago', 'stone': 'cristallus', 'body': 'caput', 'latin': 'cornua arietis'},
    2:  {'names': ['albotain','albotayn','ventris','venter'], 'herb': 'ruta', 'stone': 'rubinus', 'body': 'venter', 'latin': 'venter arietis'},
    3:  {'names': ['azoraya','athorayya','pluviae','soraya'], 'herb': 'mastix', 'stone': 'corallus', 'body': 'stomachus', 'latin': 'pluviae'},
    4:  {'names': ['aldebaran','oculus','aldebara'], 'herb': 'absinthium', 'stone': 'rubinus', 'body': 'oculus', 'latin': 'oculus tauri'},
    5:  {'names': ['almices','almites','almutzen'], 'herb': 'cuminum', 'stone': 'agatha', 'body': 'pes', 'latin': 'signum'},
    6:  {'names': ['athaya','athanna','athena','hanna'], 'herb': 'mastix', 'stone': 'corneolus', 'body': 'stomachus', 'latin': 'stella lucida'},
    7:  {'names': ['aldirah','aldira','brachium','dirah'], 'herb': 'camphora', 'stone': 'chalcedonius', 'body': 'brachium', 'latin': 'brachium'},
    8:  {'names': ['annathra','nathra','nebula'], 'herb': 'costus', 'stone': 'berillus', 'body': 'oculus', 'latin': 'nebula'},
    9:  {'names': ['atarf','atarfe','tartf'], 'herb': 'nardus', 'stone': 'granatus', 'body': 'stomachus', 'latin': 'oculus leonis'},
    10: {'names': ['algebha','algebhe','frons'], 'herb': 'aloe', 'stone': 'diamans', 'body': 'stomachus', 'latin': 'frons leonis'},
    11: {'names': ['azobra','azobre','cauda'], 'herb': 'olibanum', 'stone': 'granatus', 'body': 'costa', 'latin': 'cauda leonis'},
    12: {'names': ['acarfa','asarpha','latrantes'], 'herb': 'cicoria', 'stone': 'topazius', 'body': 'venter', 'latin': 'cauda'},
    13: {'names': ['alhayra','alawe','spica','alhaire'], 'herb': 'plantago', 'stone': 'smaragdus', 'body': 'venter', 'latin': 'spica virginis'},
    14: {'names': ['azimech','alcimech','simak','inerme'], 'herb': 'salvia', 'stone': 'smaragdus', 'body': 'dorsum', 'latin': 'inerme'},
    15: {'names': ['algafra','argafra','tecta','cooperta'], 'herb': 'armoniacum', 'stone': 'smaragdus', 'body': 'anus', 'latin': 'tecta cooperta'},
    16: {'names': ['azubene','acubene','chelae','cornua'], 'herb': 'rosa', 'stone': 'corallus', 'body': 'renes', 'latin': 'cornua scorpionis'},
    17: {'names': ['alichil','alichel','corona'], 'herb': 'crocus', 'stone': 'ferrum', 'body': 'nates', 'latin': 'corona scorpionis'},
    18: {'names': ['alcalb','alcakl','cor'], 'herb': 'piper', 'stone': 'sardonix', 'body': 'cor', 'latin': 'cor scorpionis'},
    19: {'names': ['exaula','axaulah','cauda'], 'herb': 'aristolochia', 'stone': 'topazius', 'body': 'crus', 'latin': 'cauda scorpionis'},
    20: {'names': ['nahaym','naayim','abnahaya'], 'herb': 'castoreum', 'stone': 'cristallus', 'body': 'femur', 'latin': 'desertum'},
    21: {'names': ['elbelda','albelda','desertum'], 'herb': 'tus', 'stone': 'calcedonia', 'body': 'dorsum', 'latin': 'desertum'},
    22: {'names': ['caadaldeba','acadaldeba','pastor'], 'herb': 'nardus', 'stone': 'corneolus', 'body': 'genu', 'latin': 'pastor'},
    23: {'names': ['caadachbia','deglutiens','sadachbia'], 'herb': 'sanguis draconis', 'stone': 'ferrum', 'body': 'tibia', 'latin': 'deglutiens'},
    24: {'names': ['caadbolaha','felicitas','sadalsuud'], 'herb': 'euphorbium', 'stone': 'lazulus', 'body': 'tibia', 'latin': 'felicitas'},
    25: {'names': ['caadaladbia','algadbia','tentoria'], 'herb': 'staphisagria', 'stone': 'lazulus', 'body': 'pes', 'latin': 'tentoria'},
    26: {'names': ['almisdam','almiquedam','prior'], 'herb': 'asarum', 'stone': 'jaspis', 'body': 'dorsum', 'latin': 'prior'},
    27: {'names': ['algarf','posterior','mucaddim'], 'herb': 'aristolochia', 'stone': 'ferrum', 'body': 'pes', 'latin': 'posterior'},
    28: {'names': ['arrexhe','arcexe','piscis','batn'], 'herb': 'euphorbium', 'stone': 'corallus', 'body': 'pes', 'latin': 'piscis'},
}


def get_all_targets():
    """Get ALL target words with their token length."""
    targets = {}
    for num, data in MANSIONS.items():
        for name in data['names']:
            targets[name.lower()] = ('name', num)
        targets[data['herb'].lower()] = ('herb', num)
        targets[data['stone'].lower()] = ('stone', num)
        targets[data['body'].lower()] = ('body', num)
        # Also add Latin descriptive names
        for part in data['latin'].lower().split():
            if len(part) >= 3:
                targets[part] = ('latin_desc', num)
    return targets


def main():
    out = []
    out.append("# L04 CRACK V2 — Tokenisation EVA correcte")
    out.append("")

    # ── Tokenize all L04 words ────────────────────────────────────
    out.append("## 1. TOKENISATION — Longueurs reelles des mots")
    out.append("")
    out.append("| Pos | EVA | Chars | Tokens | Tokenized |")
    out.append("|-----|-----|-------|--------|-----------|")

    for day, word in L04_WORDS:
        tokens = tokenize_eva(word)
        out.append(f"| {day:2d} | {word:10s} | {len(word):5d} | {len(tokens):6d} | {' '.join(tokens)} |")

    out.append("")

    # ── Unique tokens ─────────────────────────────────────────────
    all_tokens = []
    for _, word in L04_WORDS:
        all_tokens.extend(tokenize_eva(word))

    token_freq = Counter(all_tokens)
    unique_tokens = sorted(token_freq.keys(), key=lambda x: -token_freq[x])
    out.append(f"**Tokens uniques : {len(unique_tokens)}**")
    out.append(f"Token list: {unique_tokens}")
    out.append(f"Total tokens: {sum(token_freq.values())}")
    out.append("")
    out.append("| Token | Count | % |")
    out.append("|-------|-------|---|")
    total = sum(token_freq.values())
    for tok in unique_tokens:
        out.append(f"| {tok:5s} | {token_freq[tok]:5d} | {token_freq[tok]*100/total:.1f}% |")
    out.append("")

    # ── Length-based matching with tokens ──────────────────────────
    out.append("## 2. CORRESPONDANCES PAR LONGUEUR (tokens)")
    out.append("")

    targets = get_all_targets()
    content_words = [(d, w) for d, w in L04_WORDS if len(w) > 1]

    out.append("| Pos | EVA | Tok | Targets meme longueur |")
    out.append("|-----|-----|-----|----------------------|")

    for day, word in content_words:
        tok_len = len(tokenize_eva(word))
        same_len = [(t, typ, num) for t, (typ, num) in targets.items() if len(t) == tok_len]
        targets_str = ', '.join(f'{t}({typ[0]}M{num})' for t, typ, num in same_len[:10])
        out.append(f"| {day:2d} | {word:10s} | {tok_len:3d} | {targets_str} |")

    out.append("")

    # ── Substitution with token→letter mapping ────────────────────
    out.append("## 3. CRIB DRAG — Substitution token→lettre")
    out.append("")

    best_results = []

    for day, word in content_words:
        tokens = tokenize_eva(word)
        tok_len = len(tokens)

        for target, (typ, mnum) in targets.items():
            if len(target) != tok_len:
                continue

            # Try mapping each token to each letter
            mapping = {}
            reverse_map = {}
            consistent = True
            for tok, letter in zip(tokens, target):
                if tok in mapping:
                    if mapping[tok] != letter:
                        consistent = False
                        break
                else:
                    if letter in reverse_map and reverse_map[letter] != tok:
                        consistent = False
                        break
                    mapping[tok] = letter
                    reverse_map[letter] = tok
            if not consistent:
                continue

            # Apply this mapping to ALL other content words
            cascade = 0
            decoded_all = []
            for d2, w2 in content_words:
                tok2 = tokenize_eva(w2)
                decoded = ''
                complete = True
                for t in tok2:
                    if t in mapping:
                        decoded += mapping[t]
                    else:
                        decoded += '?'
                        complete = False
                if complete and decoded in targets:
                    cascade += 1
                decoded_all.append((d2, w2, decoded, complete))

            if cascade > 0 or len(mapping) >= 4:
                best_results.append({
                    'pos': day,
                    'eva': word,
                    'target': target,
                    'type': typ,
                    'mansion': mnum,
                    'mapping': dict(mapping),
                    'n_mapped': len(mapping),
                    'cascade': cascade,
                    'decoded': decoded_all,
                })

    best_results.sort(key=lambda x: (x['cascade'], x['n_mapped']), reverse=True)

    out.append(f"Total cribs testes: {sum(1 for _ in best_results)}")
    cascaded = [r for r in best_results if r['cascade'] > 0]
    out.append(f"**Cribs avec cascade > 0: {len(cascaded)}**")
    out.append("")

    for r in best_results[:40]:
        marker = " *** CASCADE ***" if r['cascade'] > 0 else ""
        out.append(f"### j{r['pos']} `{r['eva']}` = `{r['target']}` ({r['type']} M{r['mansion']}){marker}")
        out.append(f"  Mapping: {r['mapping']}")
        out.append(f"  Cascade: {r['cascade']}")
        if r['cascade'] > 0:
            for d2, w2, dec, complete in r['decoded']:
                if dec in targets or complete:
                    hit = " <<<" if dec in targets else ""
                    out.append(f"  j{d2:2d} {w2:10s} -> {dec}{hit}")
        out.append("")

    # ── Cross-word pattern constraints ────────────────────────────
    out.append("## 4. CONTRAINTES CROISEES — Memes tokens dans differents mots")
    out.append("")

    # Find tokens shared between words
    word_tokens = {}
    for day, word in content_words:
        word_tokens[day] = tokenize_eva(word)

    # For each token, which words contain it?
    token_to_words = defaultdict(list)
    for day, tokens in word_tokens.items():
        for i, tok in enumerate(tokens):
            token_to_words[tok].append((day, i))

    out.append("| Token | Occurrences | Mots | Position dans mot |")
    out.append("|-------|-------------|------|-------------------|")
    for tok in unique_tokens:
        if token_freq[tok] >= 2 and len(tok) >= 1:
            words_with = [(d, i) for d, i in token_to_words[tok] if d in [x[0] for x in content_words]]
            if len(words_with) >= 2:
                words_str = ', '.join(f'j{d}[{i}]' for d, i in words_with)
                out.append(f"| {tok:5s} | {len(words_with):11d} | {words_str} |  |")

    out.append("")

    # ── Frequency-based token mapping ─────────────────────────────
    out.append("## 5. MAPPING PAR FREQUENCE (tokens)")
    out.append("")

    # Target corpus: all mansion names concatenated, then frequency of letters
    target_corpus = ''
    for num, data in MANSIONS.items():
        target_corpus += data['names'][0]  # use primary name

    target_freq = Counter(target_corpus)
    target_ranked = [l for l, c in target_freq.most_common()]
    token_ranked = [t for t, c in token_freq.most_common()]

    freq_map = {}
    for i in range(min(len(token_ranked), len(target_ranked))):
        freq_map[token_ranked[i]] = target_ranked[i]

    out.append(f"Frequency mapping: {freq_map}")
    out.append("")
    out.append("| Pos | EVA | Tokens | Freq-decoded |")
    out.append("|-----|-----|--------|-------------|")
    for day, word in L04_WORDS:
        tokens = tokenize_eva(word)
        decoded = ''.join(freq_map.get(t, '?') for t in tokens)
        out.append(f"| {day:2d} | {word:10s} | {' '.join(tokens):15s} | {decoded} |")

    out.append("")

    # ── Also try herb corpus frequency ────────────────────────────
    out.append("## 6. MAPPING PAR FREQUENCE (herbes)")
    out.append("")
    herb_corpus = ''.join(data['herb'] for data in MANSIONS.values())
    herb_freq_c = Counter(herb_corpus)
    herb_ranked = [l for l, c in herb_freq_c.most_common()]

    freq_map_herb = {}
    for i in range(min(len(token_ranked), len(herb_ranked))):
        freq_map_herb[token_ranked[i]] = herb_ranked[i]

    out.append(f"Herb frequency mapping: {freq_map_herb}")
    out.append("")
    out.append("| Pos | EVA | Freq-decoded (herbs) |")
    out.append("|-----|-----|---------------------|")
    for day, word in L04_WORDS:
        tokens = tokenize_eva(word)
        decoded = ''.join(freq_map_herb.get(t, '?') for t in tokens)
        out.append(f"| {day:2d} | {word:10s} | {decoded} |")

    out.append("")

    # ── Try daiin = specific crib and propagate ───────────────────
    out.append("## 7. CRIB SPECIFIQUE — `daiin` (j1, j25) = ?")
    out.append("")
    out.append("`daiin` apparait 2 fois (j1, j25). Tokens: " + str(tokenize_eva('daiin')))
    out.append("")

    daiin_tokens = tokenize_eva('daiin')
    # Try all targets of same token length
    for target, (typ, mnum) in sorted(targets.items()):
        if len(target) != len(daiin_tokens):
            continue
        mapping = {}
        reverse_map = {}
        ok = True
        for tok, letter in zip(daiin_tokens, target):
            if tok in mapping:
                if mapping[tok] != letter:
                    ok = False; break
            else:
                if letter in reverse_map and reverse_map[letter] != tok:
                    ok = False; break
                mapping[tok] = letter
                reverse_map[letter] = tok
        if not ok:
            continue

        # Apply to key words and see what we get
        decoded_words = []
        for day, word in content_words:
            tok = tokenize_eva(word)
            dec = ''.join(mapping.get(t, '?') for t in tok)
            decoded_words.append((day, word, dec))

        # Count how many decoded words have no '?'
        complete = sum(1 for _, _, d in decoded_words if '?' not in d)
        known = sum(1 for _, _, d in decoded_words if d in targets)

        if known > 0 or complete >= 3:
            out.append(f"### `daiin` = `{target}` ({typ} M{mnum})")
            out.append(f"  Mapping: {mapping}")
            out.append(f"  Complete words: {complete}, Known targets: {known}")
            for day, word, dec in decoded_words:
                hit = " <<<" if dec in targets else ""
                out.append(f"  j{day:2d} {word:10s} -> {dec}{hit}")
            out.append("")

    # ── Summary ───────────────────────────────────────────────────
    out.append("---")
    out.append("## BILAN")
    out.append("")
    if cascaded:
        out.append(f"**{len(cascaded)} CRIBS AVEC CASCADE TROUVEES !**")
        for r in cascaded:
            out.append(f"- j{r['pos']} `{r['eva']}` = `{r['target']}` (cascade={r['cascade']})")
    else:
        out.append("**Aucune cascade trouvee avec substitution simple token→lettre.**")
        out.append("")
        out.append("Implications :")
        out.append("1. L04 n'est PAS un chiffre monoalphabetique simple")
        out.append("2. OU les noms de mansions ne sont pas la cible")
        out.append("3. OU les tokens EVA ne correspondent pas 1:1 a des lettres")
        out.append("4. OU l'encodage utilise des ABBREVIATIONS (comme le reste du VMS)")
        out.append("5. Piste a explorer : nomenclateur (chaque mot = code arbitraire)")

    report = '\n'.join(out)
    out_path = os.path.join(os.path.dirname(__file__), '..', 'output', 'L04_CRACK_V2.md')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"Report: {out_path}")
    # Print key results
    for line in report.split('\n'):
        if '<<<' in line or 'CASCADE' in line or line.startswith('##') or 'cascade' in line.lower() or 'Implications' in line or line.startswith('**'):
            print(line)


if __name__ == '__main__':
    main()
