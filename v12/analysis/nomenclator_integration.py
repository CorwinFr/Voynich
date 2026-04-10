"""
MARCHE 2: NOMENCLATOR INTEGRATION — Italian plant names into pipeline.

For each Italian plant name, compute what EVA form(s) would produce it
via K&A decoding. Then search the VMS for those EVA forms.

This is REVERSE K&A: Italian name → Latin equivalent → possible EVA forms.
"""
import sys, os, re, csv, json
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from v12.config import Config
from v12.pipeline import VoynichPipeline
from v12.stages.hmm_decoder import decode_root
from v12.loaders.eva_variants import get_word_variants


def load_nomenclator(csv_path):
    """Load Italian→Latin plant name mappings."""
    entries = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            italian = row['italian_name'].strip().lower()
            n_sources = int(row['n_sources'])
            latin_raw = row['latin_names'].strip()
            # Extract genus (first word of Latin name)
            latins = []
            for part in latin_raw.split(';'):
                genus = part.strip().split()[0].lower() if part.strip() else ''
                if genus and len(genus) >= 3:
                    latins.append(genus)
            if italian and latins:
                entries.append({
                    'italian': italian,
                    'n_sources': n_sources,
                    'latins': list(set(latins)),
                })
    return entries


def reverse_ka_simple(latin_word):
    """Reverse K&A: given a Latin word, what EVA forms could produce it?

    This is a SIMPLIFIED reverse — for each Latin letter, find possible EVA glyphs.
    K&A is not strictly invertible, but common mappings are:
    """
    # Simplified reverse K&A table (most common mappings)
    # Latin letter → possible EVA glyph(s)
    reverse = {
        'a': ['a', 'o'],       # a↔o confusion
        'b': ['v'],
        'c': ['k', 'ch'],     # c can come from k or ch
        'd': ['d', 't'],      # d↔t overlap
        'e': ['e', 'ee', 'ch'],  # e often from ee, ch produces i/e
        'f': ['f', 'p'],      # f↔p gallows
        'g': [],              # rare in K&A
        'h': [],              # usually silent
        'i': ['i', 'y', 'ch'],  # i from y or ch
        'j': ['d'],           # j←d
        'k': ['k'],
        'l': ['l'],
        'm': ['m'],
        'n': ['n', 'in'],     # n often from -in digraph
        'o': ['o', 'a'],      # o↔a confusion
        'p': ['p', 'f'],      # p↔f gallows
        'q': ['qo', 'ok'],    # q from qo- prefix
        'r': ['r', 's'],      # r↔s confusion
        's': ['s', 'r', 'sh'], # s from s, r, or sh
        't': ['t', 'k'],      # t↔k gallows
        'u': ['a', 'o', 'e'],  # u from various vowels
        'v': ['v'],
        'w': [],
        'x': ['x'],
        'y': ['y'],
        'z': [],
    }

    # For short words (3-6 letters), generate main EVA candidates
    if len(latin_word) > 8:
        return []  # too long, too many combinations

    # Simple: just use the primary mapping for each letter
    primary = {
        'a': 'a', 'b': 'v', 'c': 'k', 'd': 'd', 'e': 'e',
        'f': 'f', 'i': 'y', 'l': 'l', 'm': 'm', 'n': 'n',
        'o': 'o', 'p': 'p', 'r': 'r', 's': 's', 't': 't',
        'u': 'a', 'v': 'v', 'x': 'x', 'y': 'y',
    }

    eva_primary = ''
    for ch in latin_word.lower():
        if ch in primary:
            eva_primary += primary[ch]
        else:
            return []  # unmappable character

    return [eva_primary] if eva_primary else []


def search_vms_for_eva(eva_form, all_vms_words):
    """Search the entire VMS word list for an EVA form."""
    matches = []
    for folio, words in all_vms_words.items():
        for i, w in enumerate(words):
            if w == eva_form:
                matches.append((folio, i, w))
            # Also check if it appears as a substring (agglutinated)
            elif len(eva_form) >= 4 and eva_form in w:
                matches.append((folio, i, f'{w} (contains {eva_form})'))
    return matches


def main():
    config = Config()
    pipeline = VoynichPipeline(config)
    pipeline.load()

    # Load nomenclator
    nom_path = os.path.join(os.path.dirname(__file__), '..', '..',
                            'BruteForce', 'Italien plant names', 'nomenclator_multi_attested.csv')
    entries = load_nomenclator(nom_path)
    print(f"Loaded {len(entries)} multi-attested Italian plant names")

    # Load all VMS words
    zl_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'transcriptions', 'ZL.txt')

    all_vms_words = {}  # folio → [words]
    vms_word_set = set()
    with open(zl_path, 'r', encoding='utf-8') as f:
        for line in f:
            m = re.match(r'<(f\d+[rv]\d?)\.\d+', line.strip())
            if not m:
                continue
            folio = m.group(1)
            text = re.sub(r'<[^>]*>', '', line.strip())
            text = re.sub(r'<!.*?>', '', text)
            text = re.sub(r'<%>|<\$>|\{[^}]*\}|@\d+;?', '', text)
            text = re.sub(r'\[[^\]]*:([^\]]*)\]', r'\1', text)
            text = re.sub(r'\?', '', text).replace(',', '.')
            words = [w.strip() for w in re.findall(r'[a-z]+', text) if w.strip()]
            if words:
                all_vms_words.setdefault(folio, []).extend(words)
                vms_word_set.update(words)

    print(f"VMS: {len(vms_word_set)} unique words across {len(all_vms_words)} folios")
    print()

    # For each Italian name, try to find it in the VMS
    print("=" * 90)
    print("NOMENCLATOR SEARCH — Italian names → EVA → VMS")
    print("=" * 90)
    print()

    found = []
    not_found = []

    for entry in entries:
        italian = entry['italian']
        latins = entry['latins']

        # Strategy 1: Direct Italian name → EVA
        eva_forms_italian = reverse_ka_simple(italian)

        # Strategy 2: Latin genus → EVA
        eva_forms_latin = []
        for latin in latins:
            eva_forms_latin.extend(reverse_ka_simple(latin))

        # Strategy 3: Try K&A beam search in REVERSE
        # For each EVA word in VMS, decode and check if it matches
        # This is expensive, so we pre-filter by length
        all_eva_candidates = set(eva_forms_italian + eva_forms_latin)

        # Search VMS
        vms_matches = []
        for eva in all_eva_candidates:
            if eva in vms_word_set:
                vms_matches.append(('exact', eva))
            # Also search with variants
            variants = get_word_variants(eva, include_confusions=True)
            for v in variants:
                if v.eva in vms_word_set and v.eva != eva:
                    vms_matches.append(('variant', v.eva, v.source))

        # Also try: decode all VMS words of matching length and see if any decode to this name
        target_len = len(italian)
        for vms_word in vms_word_set:
            if abs(len(vms_word) - target_len) <= 1 and len(vms_word) >= 3:
                # Quick K&A decode
                paths = decode_root(vms_word, pipeline.hmm, top_k=5)
                for vp in paths:
                    if not vp.latin:
                        continue
                    clean = vp.latin.replace(' ', '').lower()
                    if clean == italian or clean in latins:
                        vms_matches.append(('decoded', vms_word, clean))
                    # Check genus only
                    for latin in latins:
                        if len(latin) >= 4 and clean.startswith(latin[:4]):
                            vms_matches.append(('prefix', vms_word, f'{clean}~{latin}'))

        if vms_matches:
            # Deduplicate
            unique_matches = list(set(str(m) for m in vms_matches))
            found.append((italian, latins, vms_matches[:5]))
            print(f"  FOUND: {italian:20s} ({','.join(latins):20s}) → {vms_matches[:3]}")
        else:
            not_found.append((italian, latins))

    print()
    print(f"RESULTS: {len(found)} found, {len(not_found)} not found out of {len(entries)}")
    print()

    if found:
        print("=== ALL MATCHES ===")
        print()
        for italian, latins, matches in found:
            print(f"  {italian:20s} ({','.join(latins):25s})")
            for m in matches[:5]:
                print(f"    {m}")
            print()

    # Save results
    results = {
        'found': [(it, lat, [str(m) for m in matches]) for it, lat, matches in found],
        'not_found': [(it, lat) for it, lat in not_found],
        'stats': {
            'total': len(entries),
            'found': len(found),
            'not_found': len(not_found),
            'rate': f"{len(found)*100//len(entries)}%",
        }
    }

    out_path = os.path.join(os.path.dirname(__file__), '..', 'output', 'NOMENCLATOR_SEARCH.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Results saved: {out_path}")


if __name__ == '__main__':
    main()
