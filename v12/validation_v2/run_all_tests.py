#!/usr/bin/env python3
"""
V2 Validation Suite — 6 statistical tests on the v12 decoded output.
All results stored in validation_v2/results/ as JSON for the V2 report.
"""
import json, os, sys, math, re
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

BASE = Path("d:/Github/Voynich")
DECODED = BASE / "v12/output/VOYNICH_DECODE_V12_INGREDIENTS.txt"
CLEAN = BASE / "v12/output/VOYNICH_LATIN_CLEAN.txt"
RESULTS_DIR = BASE / "v12/validation_v2/results"
RESULTS_DIR.mkdir(exist_ok=True)

CORPORA = {
    "latin_medical": BASE / "data/corpus_latin_medical_extended.txt",
    "latin_classical": BASE / "data/corpus_ovid.txt",
    "italian": BASE / "data/corpus_italian.txt",
    "italian_medical": BASE / "data/corpus_italian_medical.txt",
    "latin_medieval": BASE / "data/corpus_latin_medieval.txt",
}

PERSEUS = BASE / "data/latin_valid_wordset.json"


def load_words(path, max_words=500000):
    """Load words from a text file."""
    words = []
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            for w in re.findall(r'[a-zA-Z]{2,}', line.lower()):
                words.append(w)
                if len(words) >= max_words:
                    return words
    return words


def load_decoded_words():
    """Extract decoded Latin words from the clean file."""
    words = []
    with open(CLEAN, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('=') or line.startswith('#') or line.startswith('---'):
                continue
            for w in re.findall(r'[a-zA-Z]{2,}', line.lower()):
                if not w.startswith('_'):
                    words.append(w)
    return words


def load_decoded_per_folio():
    """Parse INGREDIENTS file for per-folio data."""
    folios = {}
    with open(DECODED, 'r', encoding='utf-8') as f:
        content = f.read()

    folio_blocks = re.split(r'FOLIO (\S+) \| Section: (\S+)', content)
    i = 1
    while i < len(folio_blocks) - 2:
        fid = folio_blocks[i]
        sec = folio_blocks[i+1]
        block = folio_blocks[i+2]

        words = []
        for line in block.split('\n'):
            if 'LATIN:' in line:
                latin = line.split('LATIN:')[1]
                for w in re.findall(r'[a-zA-Z]{2,}', latin.lower()):
                    if not w.startswith('_'):
                        words.append(w)

        # Extract stats
        m = re.search(r'Total words: (\d+)', block)
        total = int(m.group(1)) if m else len(words)
        m = re.search(r'Perseus:\s*(\d+)', block)
        perseus = int(m.group(1)) if m else 0
        m = re.search(r'CONFIRMED:\s*(\d+)', block)
        confirmed = int(m.group(1)) if m else 0
        m = re.search(r'HIGH:\s*(\d+)', block)
        high = int(m.group(1)) if m else 0

        folios[fid] = {
            "section": sec, "words": words, "total": total,
            "perseus": perseus, "confirmed": confirmed, "high": high,
        }
        i += 3
    return folios


# ══════════════════════════════════════════
# TEST 1: ENTROPY
# ══════════════════════════════════════════
def test_entropy():
    print("TEST 1: Entropy comparison...")

    def char_entropy(words, order=1):
        """Shannon entropy at character level."""
        text = ' '.join(words)
        if order == 1:
            freq = Counter(text)
            total = sum(freq.values())
            return -sum((c/total) * math.log2(c/total) for c in freq.values() if c > 0)
        else:  # H2 bigram
            bigrams = [text[i:i+2] for i in range(len(text)-1)]
            freq = Counter(bigrams)
            total = sum(freq.values())
            return -sum((c/total) * math.log2(c/total) for c in freq.values() if c > 0) / 2

    def word_entropy(words):
        freq = Counter(words)
        total = sum(freq.values())
        return -sum((c/total) * math.log2(c/total) for c in freq.values() if c > 0)

    decoded = load_decoded_words()
    results = {"decoded": {
        "H1_char": round(char_entropy(decoded, 1), 3),
        "H2_char": round(char_entropy(decoded, 2), 3),
        "H_word": round(word_entropy(decoded), 3),
        "n_words": len(decoded),
        "n_types": len(set(decoded)),
    }}

    for name, path in CORPORA.items():
        if path.exists():
            words = load_words(path)
            results[name] = {
                "H1_char": round(char_entropy(words, 1), 3),
                "H2_char": round(char_entropy(words, 2), 3),
                "H_word": round(word_entropy(words), 3),
                "n_words": len(words),
                "n_types": len(set(words)),
            }
            print(f"  {name}: H1={results[name]['H1_char']}, H2={results[name]['H2_char']}, "
                  f"Hw={results[name]['H_word']}, types={results[name]['n_types']}")

    print(f"  DECODED: H1={results['decoded']['H1_char']}, H2={results['decoded']['H2_char']}, "
          f"Hw={results['decoded']['H_word']}, types={results['decoded']['n_types']}")

    with open(RESULTS_DIR / "test1_entropy.json", 'w') as f:
        json.dump(results, f, indent=2)
    print(f"  -> {RESULTS_DIR / 'test1_entropy.json'}")


# ══════════════════════════════════════════
# TEST 2: TRIGRAM VALIDATION
# ══════════════════════════════════════════
def test_trigrams():
    print("TEST 2: Trigram validation...")

    # Build trigram sets from corpora
    corpus_trigrams = {}
    for name, path in CORPORA.items():
        if path.exists():
            words = load_words(path)
            trigrams = set()
            for i in range(len(words) - 2):
                trigrams.add((words[i], words[i+1], words[i+2]))
            corpus_trigrams[name] = trigrams

    # Extract decoded trigrams per section
    folios = load_decoded_per_folio()
    sections = defaultdict(list)
    for fid, data in folios.items():
        sections[data["section"]].extend(data["words"])

    results = {}

    # Global decoded trigrams
    decoded = load_decoded_words()
    decoded_trigrams = set()
    for i in range(len(decoded) - 2):
        decoded_trigrams.add((decoded[i], decoded[i+1], decoded[i+2]))

    results["global"] = {
        "total_trigrams": len(decoded_trigrams),
        "matches": {}
    }
    for cname, ctri in corpus_trigrams.items():
        matches = decoded_trigrams & ctri
        results["global"]["matches"][cname] = {
            "count": len(matches),
            "examples": [' '.join(m) for m in list(matches)[:20]],
        }
        print(f"  Global vs {cname}: {len(matches)} matches")

    # Per section
    for sec, words in sections.items():
        sec_trigrams = set()
        for i in range(len(words) - 2):
            sec_trigrams.add((words[i], words[i+1], words[i+2]))

        results[f"section_{sec}"] = {"total_trigrams": len(sec_trigrams), "matches": {}}
        for cname, ctri in corpus_trigrams.items():
            matches = sec_trigrams & ctri
            results[f"section_{sec}"]["matches"][cname] = len(matches)

    with open(RESULTS_DIR / "test2_trigrams.json", 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"  -> {RESULTS_DIR / 'test2_trigrams.json'}")


# ══════════════════════════════════════════
# TEST 3: MORPHOLOGY VALIDATION
# ══════════════════════════════════════════
def test_morphology():
    print("TEST 3: Morphology validation...")

    VALID_ENDINGS = {
        # Noun declensions
        "nom_1": ["a", "ae"],
        "nom_2": ["us", "um", "i", "er"],
        "nom_3": ["is", "em", "es", "ium", "ibus"],
        "nom_4": ["us", "ui", "uum"],
        "nom_5": ["es", "ei"],
        # Verb conjugations
        "verb_pres": ["o", "as", "at", "amus", "atis", "ant",
                      "es", "et", "emus", "etis", "ent",
                      "is", "it", "imus", "itis", "unt"],
        "verb_imp": ["e", "a", "ite", "ate"],
        "verb_inf": ["are", "ere", "ire"],
        "verb_part": ["ans", "ens", "iens"],
        # Common endings
        "adverb": ["iter", "dum", "ter"],
        "prep": ["in", "cum", "per", "ex", "de"],
    }

    all_endings = set()
    for group in VALID_ENDINGS.values():
        all_endings.update(group)

    decoded = load_decoded_words()

    valid_count = 0
    invalid_words = []
    for w in decoded:
        matched = False
        for ending in sorted(all_endings, key=len, reverse=True):
            if w.endswith(ending) and len(w) > len(ending):
                valid_count += 1
                matched = True
                break
        if not matched:
            if w in {"et", "in", "ex", "de", "cum", "per", "es", "ac", "ad",
                     "ab", "ut", "si", "an", "vel", "eo", "ea", "id", "hic",
                     "sal", "mel", "cor", "ius", "os", "re"}:
                valid_count += 1
            else:
                invalid_words.append(w)

    # Same test on Italian corpus for comparison
    italian_words = load_words(CORPORA["italian"], 50000) if CORPORA["italian"].exists() else []
    italian_valid = sum(1 for w in italian_words
                       if any(w.endswith(e) and len(w) > len(e) for e in all_endings)
                       or w in {"et", "in", "ex", "de", "cum", "per"})

    results = {
        "decoded": {
            "total": len(decoded),
            "valid_endings": valid_count,
            "pct": round(100 * valid_count / len(decoded), 1),
            "top_invalid": Counter(invalid_words).most_common(30),
        },
        "italian_control": {
            "total": len(italian_words),
            "valid_endings": italian_valid,
            "pct": round(100 * italian_valid / max(len(italian_words), 1), 1),
        }
    }

    print(f"  Decoded: {results['decoded']['pct']}% valid Latin endings ({valid_count}/{len(decoded)})")
    print(f"  Italian control: {results['italian_control']['pct']}% ({italian_valid}/{len(italian_words)})")

    with open(RESULTS_DIR / "test3_morphology.json", 'w') as f:
        json.dump(results, f, indent=2)
    print(f"  -> {RESULTS_DIR / 'test3_morphology.json'}")


# ══════════════════════════════════════════
# TEST 4: WORD BIGRAM COHERENCE
# ══════════════════════════════════════════
def test_coherence():
    print("TEST 4: Word bigram coherence...")

    # Build bigram models from corpora
    def bigram_model(words):
        bigrams = Counter()
        unigrams = Counter(words)
        for i in range(len(words) - 1):
            bigrams[(words[i], words[i+1])] += 1
        return unigrams, bigrams

    def score_text(words, uni, bi, vocab_size):
        """Log-prob with Laplace smoothing."""
        score = 0.0
        n = 0
        for i in range(len(words) - 1):
            bg = (words[i], words[i+1])
            p = (bi.get(bg, 0) + 1) / (uni.get(words[i], 0) + vocab_size)
            score += math.log2(p)
            n += 1
        return score / max(n, 1)

    results = {}
    decoded = load_decoded_words()

    for name, path in CORPORA.items():
        if not path.exists():
            continue
        corpus_words = load_words(path)
        uni, bi = bigram_model(corpus_words)
        vocab = len(set(corpus_words))

        # Score decoded text against this corpus
        decoded_score = score_text(decoded, uni, bi, vocab)

        # Score corpus against itself (self-coherence baseline)
        half = len(corpus_words) // 2
        self_score = score_text(corpus_words[half:], *bigram_model(corpus_words[:half]), vocab)

        # Score shuffled decoded (control)
        import random
        shuffled = decoded.copy()
        random.shuffle(shuffled)
        shuffled_score = score_text(shuffled, uni, bi, vocab)

        results[name] = {
            "decoded_score": round(decoded_score, 3),
            "self_coherence": round(self_score, 3),
            "shuffled_control": round(shuffled_score, 3),
            "ratio_decoded_vs_self": round(decoded_score / min(self_score, -0.001), 3),
        }
        print(f"  vs {name}: decoded={decoded_score:.3f}, self={self_score:.3f}, "
              f"shuffled={shuffled_score:.3f}")

    with open(RESULTS_DIR / "test4_coherence.json", 'w') as f:
        json.dump(results, f, indent=2)
    print(f"  -> {RESULTS_DIR / 'test4_coherence.json'}")


# ══════════════════════════════════════════
# TEST 5: CHEMICAL FINGERPRINT
# ══════════════════════════════════════════
def test_chemical():
    print("TEST 5: Chemical fingerprint (Antidotarium)...")

    AUREA_ALEXANDRINA = {
        "asari", "aloes", "turis", "petrosellini", "cinamomi",
        "masticis", "croci", "piperis", "olei", "mellis", "coque", "cola"
    }

    METRIDATUM = {
        "apii", "asari", "turis", "petrosellini", "cinamomi",
        "croci", "piperis", "nardi", "cassia", "mellis"
    }

    HIERA_PICRA = {
        "aloes", "asari", "cinamomi", "masticis", "croci",
        "nardi", "mellis", "coque", "cola"
    }

    RECIPES = {
        "Aurea Alexandrina": AUREA_ALEXANDRINA,
        "Metridatum": METRIDATUM,
        "Hiera Picra": HIERA_PICRA,
    }

    # Expanded ingredient set (what v12 can decode)
    ALL_FOUND = {
        "aloe", "aloes", "ture", "turis", "sal", "olei", "oleo",
        "aceto", "aceti", "cerae", "cera", "mel", "mellis",
        "iecur", "asari", "asarum", "nardi", "cassiae", "cassia",
        "apii", "apium", "vini", "croci", "sapa", "succi",
        "hiera", "cicura", "enula", "inula", "pepe", "lilie",
        "cardamomi", "costi", "lauri", "piretri",
        "coque", "coquas", "coquere", "cola", "recipe", "misce",
        "tere", "ciere", "equaliter",
    }

    folios = load_decoded_per_folio()
    results = {"per_folio": {}, "recipes": {}}

    # Per-folio ingredient count
    for fid, data in folios.items():
        word_set = set(data["words"])
        found = word_set & ALL_FOUND
        if found:
            results["per_folio"][fid] = {
                "section": data["section"],
                "ingredients_found": sorted(found),
                "count": len(found),
                "total_words": data["total"],
            }

    # Recipe matching (top pharma folios)
    pharma_folios = {fid: data for fid, data in folios.items()
                     if data["section"] in ("S", "P")}

    for recipe_name, recipe_set in RECIPES.items():
        best_score = 0
        best_folio = None
        for fid, data in pharma_folios.items():
            word_set = set(data["words"])
            # Normalize: check stems
            found = set()
            for rw in recipe_set:
                for dw in word_set:
                    if dw.startswith(rw[:4]) or rw.startswith(dw[:4]):
                        found.add(rw)
            jaccard = len(found) / len(recipe_set) if recipe_set else 0
            if jaccard > best_score:
                best_score = jaccard
                best_folio = fid
                best_found = found

        results["recipes"][recipe_name] = {
            "canonical_ingredients": sorted(recipe_set),
            "best_folio": best_folio,
            "jaccard": round(best_score, 3),
            "found": sorted(best_found) if best_folio else [],
            "missing": sorted(recipe_set - best_found) if best_folio else [],
        }
        print(f"  {recipe_name}: best={best_folio}, Jaccard={best_score:.3f}, "
              f"found={len(best_found)}/{len(recipe_set)}")

    # Count folios with 3+ ingredients
    rich_folios = {k: v for k, v in results["per_folio"].items() if v["count"] >= 3}
    results["summary"] = {
        "folios_with_ingredients": len(results["per_folio"]),
        "folios_with_3plus": len(rich_folios),
        "total_unique_ingredients": len(ALL_FOUND),
    }
    print(f"  Folios with ingredients: {len(results['per_folio'])}, "
          f"3+ ingredients: {len(rich_folios)}")

    with open(RESULTS_DIR / "test5_chemical.json", 'w') as f:
        json.dump(results, f, indent=2)
    print(f"  -> {RESULTS_DIR / 'test5_chemical.json'}")


# ══════════════════════════════════════════
# TEST 6: WORD LENGTH DISTRIBUTION
# ══════════════════════════════════════════
def test_word_lengths():
    print("TEST 6: Word length distributions...")

    def length_dist(words):
        lengths = [len(w) for w in words]
        dist = Counter(lengths)
        total = len(lengths)
        return {
            "mean": round(sum(lengths) / max(total, 1), 2),
            "median": sorted(lengths)[total // 2] if lengths else 0,
            "distribution": {str(k): v for k, v in sorted(dist.items())},
            "total": total,
        }

    def ks_statistic(dist1, dist2):
        """Kolmogorov-Smirnov statistic between two length distributions."""
        all_lengths = sorted(set(list(dist1.keys()) + list(dist2.keys())))
        total1 = sum(dist1.values())
        total2 = sum(dist2.values())
        cdf1 = 0
        cdf2 = 0
        max_diff = 0
        for length in all_lengths:
            cdf1 += dist1.get(length, 0) / max(total1, 1)
            cdf2 += dist2.get(length, 0) / max(total2, 1)
            max_diff = max(max_diff, abs(cdf1 - cdf2))
        return round(max_diff, 4)

    decoded = load_decoded_words()
    results = {"decoded": length_dist(decoded)}

    # Load EVA words for comparison
    eva_words = []
    with open(DECODED, 'r', encoding='utf-8') as f:
        for line in f:
            if 'EVA' in line and ':' in line:
                eva_part = line.split(':')[1] if 'EVA' in line.split(':')[0] else ''
                for w in re.findall(r'[a-zA-Z]{2,}', eva_part):
                    eva_words.append(w.lower())
    results["eva_raw"] = length_dist(eva_words[:len(decoded)])

    for name, path in CORPORA.items():
        if path.exists():
            words = load_words(path, len(decoded))
            results[name] = length_dist(words)

    # KS statistics
    decoded_dist = Counter(len(w) for w in decoded)
    results["ks_tests"] = {}
    for name in list(CORPORA.keys()) + ["eva_raw"]:
        if name in results and "distribution" in results[name]:
            ref_dist = {int(k): v for k, v in results[name]["distribution"].items()}
            ks = ks_statistic(decoded_dist, ref_dist)
            results["ks_tests"][f"decoded_vs_{name}"] = ks
            print(f"  KS decoded vs {name}: {ks}")

    print(f"  Decoded mean length: {results['decoded']['mean']}")
    for name in CORPORA:
        if name in results:
            print(f"  {name} mean length: {results[name]['mean']}")

    with open(RESULTS_DIR / "test6_word_lengths.json", 'w') as f:
        json.dump(results, f, indent=2)
    print(f"  -> {RESULTS_DIR / 'test6_word_lengths.json'}")


# ══════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("V2 VALIDATION SUITE")
    print("=" * 60)

    test_entropy()
    print()
    test_trigrams()
    print()
    test_morphology()
    print()
    test_coherence()
    print()
    test_chemical()
    print()
    test_word_lengths()

    print()
    print("=" * 60)
    print(f"All results in {RESULTS_DIR}/")
    print("=" * 60)
