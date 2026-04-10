"""
L04 CRACK ENGINE — Brute-force substitution cipher attack.

PREMISE: L04 does NOT use K&A. The glyph frequency profile is
radically different from VMS global (v=33x, x=11x, h=0.34x, q/p/m=0).
L04 uses a DIRECT simple substitution or transliteration system.

STRATEGY:
1. Treat each EVA glyph as mapping to ONE Latin letter
2. Use known target vocabulary (mansion names, herbs, etc.) as cribs
3. Try all 28 rotations of mansion-to-position mapping
4. For each rotation, derive partial cipher and check consistency
5. Score by number of consistent mappings

With 17 unique glyphs and 104 total characters, this is tractable.
"""
import sys, os, re, math
from pathlib import Path
from collections import Counter, defaultdict
from itertools import permutations
import json

# ── L04 RAW DATA ──────────────────────────────────────────────────

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

# Content words only (excluding isolated glyphs)
CONTENT_WORDS = [(d, w) for d, w in L04_WORDS if len(w) > 1]
ISOLATED = [(d, w) for d, w in L04_WORDS if len(w) == 1]

# All unique glyphs in L04
ALL_GLYPHS = sorted(set(''.join(w for _, w in L04_WORDS)))
print(f"Unique glyphs in L04: {len(ALL_GLYPHS)} = {ALL_GLYPHS}")

# ── 28 LUNAR MANSIONS — All known name variants ──────────────────

# Multiple transliteration traditions: Picatrix Latin, Agrippa, Arabic
MANSIONS = {
    1:  {'names': ['alnath', 'alnach', 'horns'], 'star': 'beta Arietis',
         'herb': 'plantago', 'stone': 'cristallus', 'body': 'caput'},
    2:  {'names': ['albotain', 'albotayn', 'ventris'], 'star': 'Pleiades',
         'herb': 'ruta', 'stone': 'rubinus', 'body': 'venter'},
    3:  {'names': ['azoraya', 'athorayya', 'pluviae'], 'star': 'Aldebaran area',
         'herb': 'mastix', 'stone': 'corallus', 'body': 'stomachus'},
    4:  {'names': ['aldebaran', 'oculus'], 'star': 'Aldebaran',
         'herb': 'absinthium', 'stone': 'rubinus', 'body': 'oculus'},
    5:  {'names': ['almices', 'almites', 'almutzen'], 'star': 'Capella',
         'herb': 'cuminum', 'stone': 'agatha', 'body': 'pes'},
    6:  {'names': ['athaya', 'athanna', 'athena'], 'star': 'epsilon Geminorum',
         'herb': 'mastix', 'stone': 'corneolus', 'body': 'stomachus'},
    7:  {'names': ['aldirah', 'aldirain', 'aldira', 'brachium'], 'star': 'Castor/Pollux',
         'herb': 'camphora', 'stone': 'chalcedonius', 'body': 'brachium'},
    8:  {'names': ['annathra', 'anathra', 'nathra', 'nebula'], 'star': 'Praesepe',
         'herb': 'costus', 'stone': 'berillus', 'body': 'oculus'},
    9:  {'names': ['atarf', 'atarfe', 'oculus leonis'], 'star': 'Regulus area',
         'herb': 'nardus', 'stone': 'granatus', 'body': 'stomachus'},
    10: {'names': ['algebha', 'algebhal', 'algebhe', 'frons leonis'], 'star': 'Regulus',
         'herb': 'aloe', 'stone': 'diamans', 'body': 'stomachus'},
    11: {'names': ['azobra', 'azobre', 'cauda leonis'], 'star': 'Denebola',
         'herb': 'olibanum', 'stone': 'granatus', 'body': 'costa'},
    12: {'names': ['acarfa', 'asarpha', 'aserpha'], 'star': 'beta Virginis',
         'herb': 'cicoria', 'stone': 'topazius', 'body': 'venter'},
    13: {'names': ['alhayra', 'alahue', 'alawe', 'spica'], 'star': 'Spica',
         'herb': 'plantago', 'stone': 'smaragdus', 'body': 'venter'},
    14: {'names': ['azimech', 'alcimech', 'simak', 'inerme'], 'star': 'Arcturus',
         'herb': 'salvia', 'stone': 'smaragdus', 'body': 'dorsum'},
    15: {'names': ['algafra', 'argafra', 'tecta', 'cooperta'], 'star': 'iota Bootis',
         'herb': 'armoniacum', 'stone': 'smaragdus', 'body': 'anus'},
    16: {'names': ['azubene', 'acubene', 'chelae'], 'star': 'alpha Librae',
         'herb': 'rosa', 'stone': 'corallus', 'body': 'renes'},
    17: {'names': ['alichil', 'alichel', 'corona'], 'star': 'alpha Scorpii area',
         'herb': 'crocus', 'stone': 'ferrum', 'body': 'nates'},
    18: {'names': ['alcalb', 'alcakl', 'cor scorpionis'], 'star': 'Antares',
         'herb': 'piper', 'stone': 'sardonix', 'body': 'cor'},
    19: {'names': ['exaula', 'axaulah', 'cauda scorpionis'], 'star': 'Shaula',
         'herb': 'aristolochia', 'stone': 'topazius', 'body': 'crus'},
    20: {'names': ['nahaym', 'naayim', 'abnahaya'], 'star': 'Nunki area',
         'herb': 'castoreum', 'stone': 'cristallus', 'body': 'femur'},
    21: {'names': ['elbelda', 'albelda', 'desertum'], 'star': 'epsilon Sagittarii',
         'herb': 'tus', 'stone': 'calcedonia', 'body': 'dorsum'},
    22: {'names': ['caadaldeba', 'acadaldeba', 'pastor'], 'star': 'alpha Capricorni',
         'herb': 'nardus', 'stone': 'corneolus', 'body': 'genu'},
    23: {'names': ['caadachbia', 'caciddebolah', 'deglutiens'], 'star': 'Sadalachbia',
         'herb': 'sanguis draconis', 'stone': 'ferrum', 'body': 'tibia'},
    24: {'names': ['caadbolaha', 'caadachahot', 'felicitas'], 'star': 'Sadalsuud',
         'herb': 'euphorbium', 'stone': 'lazulus', 'body': 'tibia'},
    25: {'names': ['caadaladbia', 'algadbia', 'tentoria'], 'star': 'Fomalhaut area',
         'herb': 'staphisagria', 'stone': 'lazulus', 'body': 'pes'},
    26: {'names': ['almisdam', 'almiquedam', 'prior'], 'star': 'alpha Pegasi',
         'herb': 'asarum', 'stone': 'jaspis', 'body': 'dorsum'},
    27: {'names': ['algarf', 'algaafalmuehar', 'posterior'], 'star': 'Alpheratz',
         'herb': 'aristolochia', 'stone': 'ferrum', 'body': 'pes'},
    28: {'names': ['arrexhe', 'arcexe', 'piscis', 'batn'], 'star': 'Mirach',
         'herb': 'euphorbium', 'stone': 'corallus', 'body': 'pes'},
}


def get_all_target_words():
    """Get ALL possible target words from mansions (names, herbs, stones, body parts)."""
    targets = {}
    for num, data in MANSIONS.items():
        for name in data['names']:
            targets[name.lower()] = ('name', num)
        targets[data['herb'].lower()] = ('herb', num)
        targets[data['stone'].lower()] = ('stone', num)
        targets[data['body'].lower()] = ('body', num)
    return targets


def derive_mapping(eva_word, latin_word):
    """Try to derive a consistent glyph→letter mapping from an EVA↔Latin pair.
    Returns None if lengths don't match or mapping is inconsistent."""
    if len(eva_word) != len(latin_word):
        return None
    mapping = {}
    reverse = {}
    for e, l in zip(eva_word, latin_word):
        if e in mapping:
            if mapping[e] != l:
                return None  # inconsistent
        else:
            if l in reverse and reverse[l] != e:
                return None  # two EVA glyphs → same letter (not 1:1)
            mapping[e] = l
            reverse[l] = e
    return mapping


def check_mapping_consistency(mappings_list):
    """Check if multiple partial mappings are mutually consistent."""
    combined = {}
    reverse = {}
    for mapping in mappings_list:
        for e, l in mapping.items():
            if e in combined:
                if combined[e] != l:
                    return None, 0  # inconsistent
            else:
                if l in reverse and reverse[l] != e:
                    return None, 0
                combined[e] = l
                reverse[l] = e
    return combined, len(combined)


def score_rotation(rotation_offset, target_type='name'):
    """Score a specific rotation: mansion N maps to L04 position N+offset."""
    matches = []
    partial_mappings = []

    for mansion_num in range(1, 29):
        l04_pos = ((mansion_num - 1 + rotation_offset) % 29) + 1
        # Find the L04 word at this position
        eva_word = None
        for d, w in L04_WORDS:
            if d == l04_pos:
                eva_word = w
                break
        if eva_word is None or len(eva_word) <= 1:
            continue  # skip isolated glyphs

        # Get target words for this mansion
        data = MANSIONS[mansion_num]
        if target_type == 'name':
            targets = data['names']
        elif target_type == 'herb':
            targets = [data['herb']]
        elif target_type == 'stone':
            targets = [data['stone']]
        elif target_type == 'body':
            targets = [data['body']]
        else:
            targets = data['names'] + [data['herb'], data['stone'], data['body']]

        for target in targets:
            target = target.lower()
            m = derive_mapping(eva_word, target)
            if m is not None:
                matches.append((mansion_num, l04_pos, eva_word, target, m))
                partial_mappings.append(m)

    # Check consistency of all derived mappings
    if partial_mappings:
        combined, n_mapped = check_mapping_consistency(partial_mappings)
        if combined:
            return matches, combined, n_mapped
        else:
            # Find largest consistent subset
            best_subset = []
            best_combined = {}
            for i in range(len(partial_mappings)):
                subset = [partial_mappings[i]]
                for j in range(len(partial_mappings)):
                    if i != j:
                        test = subset + [partial_mappings[j]]
                        c, n = check_mapping_consistency(test)
                        if c is not None:
                            subset.append(partial_mappings[j])
                c, n = check_mapping_consistency(subset)
                if c and n > len(best_combined):
                    best_subset = [matches[k] for k in range(len(partial_mappings))
                                   if partial_mappings[k] in subset]
                    best_combined = c
            return best_subset, best_combined, len(best_combined)

    return matches, {}, 0


def try_length_match_all_targets():
    """For each content word, find ALL mansion attributes that match its length."""
    out = []
    targets = get_all_target_words()

    out.append("## LENGTH-BASED MATCHES — Quels mots cibles ont la meme longueur ?")
    out.append("")
    out.append("| Pos | EVA | Len | Targets de meme longueur | Type |")
    out.append("|-----|-----|-----|--------------------------|------|")

    for day, eva in CONTENT_WORDS:
        same_len = [(word, typ, num) for word, (typ, num) in targets.items()
                    if len(word) == len(eva)]
        if same_len:
            for word, typ, num in same_len[:8]:
                out.append(f"| {day:2d} | {eva:10s} | {len(eva)} | {word:20s} | {typ} M{num} |")
        else:
            out.append(f"| {day:2d} | {eva:10s} | {len(eva)} | - | - |")

    return '\n'.join(out)


def try_substitution_crib(eva_word, target_word):
    """Given an EVA word and a target, derive mapping and apply to ALL L04 words."""
    mapping = derive_mapping(eva_word, target_word)
    if mapping is None:
        return None

    decoded_words = []
    for day, word in L04_WORDS:
        decoded = ''
        unknown = False
        for g in word:
            if g in mapping:
                decoded += mapping[g]
            else:
                decoded += '?'
                unknown = True
        decoded_words.append((day, word, decoded, unknown))
    return mapping, decoded_words


def frequency_analysis():
    """Compare glyph frequencies in L04 with letter frequencies in mansion names."""
    out = []
    out.append("## FREQUENCY ANALYSIS")
    out.append("")

    # L04 glyph frequencies
    all_text = ''.join(w for _, w in L04_WORDS)
    l04_freq = Counter(all_text)
    l04_total = len(all_text)

    # Mansion name letter frequencies (all variants concatenated)
    mansion_text = ''
    for num, data in MANSIONS.items():
        mansion_text += data['names'][0]  # primary name
    man_freq = Counter(mansion_text)
    man_total = len(mansion_text)

    # Herb name frequencies
    herb_text = ''.join(data['herb'] for data in MANSIONS.values())
    herb_freq = Counter(herb_text)
    herb_total = len(herb_text)

    out.append("### L04 glyphs vs Mansion name letters vs Herb letters")
    out.append(f"| Rank | L04 glyph (%) | Mansion letter (%) | Herb letter (%) |")
    out.append(f"|------|---------------|-------------------|-----------------|")

    l04_ranked = l04_freq.most_common()
    man_ranked = man_freq.most_common()
    herb_ranked = herb_freq.most_common()

    for i in range(max(len(l04_ranked), len(man_ranked), len(herb_ranked))):
        l04_str = f"{l04_ranked[i][0]}={l04_ranked[i][1]*100/l04_total:.0f}%" if i < len(l04_ranked) else "-"
        man_str = f"{man_ranked[i][0]}={man_ranked[i][1]*100/man_total:.0f}%" if i < len(man_ranked) else "-"
        herb_str = f"{herb_ranked[i][0]}={herb_ranked[i][1]*100/herb_total:.0f}%" if i < len(herb_ranked) else "-"
        out.append(f"| {i+1:4d} | {l04_str:13s} | {man_str:17s} | {herb_str:15s} |")

    out.append("")

    # Suggest frequency-based mapping
    out.append("### Suggested frequency mapping (L04 → Mansion names)")
    out.append("")
    if len(l04_ranked) >= 5 and len(man_ranked) >= 5:
        freq_map = {}
        for i in range(min(len(l04_ranked), len(man_ranked))):
            freq_map[l04_ranked[i][0]] = man_ranked[i][0]
        out.append(f"Mapping: {freq_map}")
        out.append("")

        # Apply to all words
        out.append("| Pos | EVA | Freq-decoded | Known? |")
        out.append("|-----|-----|-------------|--------|")
        for day, word in L04_WORDS:
            decoded = ''.join(freq_map.get(g, '?') for g in word)
            out.append(f"| {day:2d} | {word:10s} | {decoded:15s} | |")

    return '\n'.join(out)


def exhaustive_crib_drag():
    """Try EVERY possible mansion attribute as a crib for EVERY L04 word.
    When lengths match, derive mapping and test consistency across words."""
    out = []
    out.append("## EXHAUSTIVE CRIB DRAG — Every target vs every position")
    out.append("")

    targets = get_all_target_words()
    best_results = []

    for day, eva in CONTENT_WORDS:
        for target_word, (target_type, mansion_num) in targets.items():
            if len(target_word) != len(eva):
                continue

            result = try_substitution_crib(eva, target_word)
            if result is None:
                continue

            mapping, decoded_words = result

            # Score: how many OTHER words decode to known targets?
            known_count = 0
            for d2, w2, dec2, unk in decoded_words:
                if d2 == day:
                    continue
                if not unk and dec2 in targets:
                    known_count += 1
                elif not unk and len(dec2) >= 3:
                    # Check partial matches
                    for t in targets:
                        if t.startswith(dec2) or dec2.startswith(t):
                            known_count += 0.5
                            break

            if known_count > 0 or len(mapping) >= 4:
                best_results.append({
                    'crib_pos': day,
                    'crib_eva': eva,
                    'crib_target': target_word,
                    'crib_type': target_type,
                    'mansion': mansion_num,
                    'mapping': dict(mapping),
                    'n_mapped': len(mapping),
                    'cascade_hits': known_count,
                    'decoded': [(d, w, dec) for d, w, dec, _ in decoded_words if len(w) > 1],
                })

    # Sort by cascade hits (most other words decoded)
    best_results.sort(key=lambda x: (x['cascade_hits'], x['n_mapped']), reverse=True)

    out.append(f"Total crib pairs tested: many")
    out.append(f"Results with cascade > 0: {sum(1 for r in best_results if r['cascade_hits'] > 0)}")
    out.append(f"Results with mapping >= 4: {len(best_results)}")
    out.append("")

    for r in best_results[:30]:
        out.append(f"### Crib: j{r['crib_pos']} `{r['crib_eva']}` = `{r['crib_target']}` ({r['crib_type']} M{r['mansion']})")
        out.append(f"  Mapping ({r['n_mapped']} glyphs): {r['mapping']}")
        out.append(f"  Cascade hits: {r['cascade_hits']}")
        for d, w, dec in r['decoded']:
            marker = " <<<" if dec in targets else ""
            out.append(f"    j{d:2d} {w:10s} -> {dec}{marker}")
        out.append("")

    return '\n'.join(out)


def rotation_test():
    """Try all 29 rotations of the mansion→position mapping."""
    out = []
    out.append("## ROTATION TEST — 29 decalages possibles")
    out.append("")

    best_rotations = []

    for offset in range(29):
        for target_type in ['name', 'herb', 'stone', 'body', 'all']:
            matches, combined, n_mapped = score_rotation(offset, target_type)
            if matches:
                best_rotations.append({
                    'offset': offset,
                    'type': target_type,
                    'n_matches': len(matches),
                    'n_mapped': n_mapped,
                    'matches': matches,
                    'combined': combined,
                })

    best_rotations.sort(key=lambda x: (x['n_matches'], x['n_mapped']), reverse=True)

    out.append(f"Rotations testees: 29 x 5 types = 145")
    out.append(f"Rotations avec matches: {len(best_rotations)}")
    out.append("")

    for r in best_rotations[:20]:
        out.append(f"### Offset={r['offset']}, Type={r['type']}: {r['n_matches']} matches, {r['n_mapped']} glyphs mappes")
        for mansion, pos, eva, target, mapping in r['matches']:
            out.append(f"  M{mansion:2d} -> j{pos:2d}: `{eva}` = `{target}` | {mapping}")
        if r['combined']:
            out.append(f"  Combined mapping: {r['combined']}")
        out.append("")

    return '\n'.join(out)


def pattern_analysis():
    """Analyze structural patterns independent of decoding."""
    out = []
    out.append("## PATTERN ANALYSIS — Structure des mots EVA")
    out.append("")

    # Vowel/consonant patterns (treating EVA glyphs by VMS frequency)
    # In VMS: o, e, a, i are most frequent = likely "vowels"
    # d, k, r, t, s, l, n, ch = likely "consonants"
    vowels = set('oeaiy')
    consonants = set('dkrtslnchfxvm')

    out.append("### CV patterns (o,e,a,i,y=V; rest=C)")
    out.append("")
    out.append("| Pos | EVA | CV pattern | Structure |")
    out.append("|-----|-----|-----------|-----------|")
    for day, word in L04_WORDS:
        cv = ''.join('V' if g in vowels else 'C' for g in word)
        out.append(f"| {day:2d} | {word:10s} | {cv:10s} | |")

    out.append("")

    # Repeated substrings
    out.append("### Sous-chaines communes")
    out.append("")
    words = [w for _, w in L04_WORDS if len(w) >= 3]
    substrings = Counter()
    for w in words:
        for i in range(len(w)):
            for j in range(i+2, len(w)+1):
                sub = w[i:j]
                if len(sub) >= 2:
                    substrings[sub] += 1

    for sub, count in substrings.most_common(20):
        if count >= 2:
            positions = [d for d, w in L04_WORDS if sub in w]
            out.append(f"  `{sub}` x{count}: jours {positions}")

    return '\n'.join(out)


def main():
    out = []
    out.append("# L04 CRACK ENGINE — Resultats")
    out.append("")
    out.append("## Premisse : K&A ne s'applique PAS a L04.")
    out.append("## On traite L04 comme un chiffre par substitution simple.")
    out.append(f"## 17 glyphes uniques, 104 caracteres totaux, 29 mots.")
    out.append("")

    # Test 1: Pattern analysis
    out.append(pattern_analysis())
    out.append("")

    # Test 2: Length matching
    out.append(try_length_match_all_targets())
    out.append("")

    # Test 3: Frequency analysis
    out.append(frequency_analysis())
    out.append("")

    # Test 4: Rotation test (28 offsets x 5 target types)
    out.append(rotation_test())
    out.append("")

    # Test 5: Exhaustive crib drag
    out.append(exhaustive_crib_drag())
    out.append("")

    report = '\n'.join(out)
    out_path = os.path.join(os.path.dirname(__file__), '..', 'output', 'L04_CRACK_RESULTS.md')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"Report written: {out_path}")

    # Print summary
    lines = report.split('\n')
    for line in lines:
        if line.startswith('#') or 'match' in line.lower() or 'cascade' in line.lower() or 'mapping' in line.lower() or '<<<' in line:
            print(line)


if __name__ == '__main__':
    main()
