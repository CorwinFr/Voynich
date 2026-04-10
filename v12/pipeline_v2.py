"""
PIPELINE V2 — Exhaustive decode with glyph variants + dual system + rule scoring.

For each word:
  1. Generate ALL EVA variant readings
  2. For EACH variant: classify (LOGO/INGR/DOSE/FUNC) + decode (table/K&A)
  3. Score ALL combinations by simple RULES
  4. Pick the best-scoring combination PER LINE

No logarithms. No HMM probabilities for scoring. Just lookup tables and rules.
"""
import sys
import re
import json
import csv
import os
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent.parent))

from v12.loaders.eva_variants import get_word_variants, EVAVariant
from v12.classifier import classify_word, classify_line, WordType, GLYPH_TABLE, LOGOGRAMS
from v12.decoder_table import COMPOUNDS


# ══════════════════════════════════════════════════════════════════
# INGREDIENT DATABASE (loaded once)
# ══════════════════════════════════════════════════════════════════

class IngredientDB:
    """All known ingredients from all sources."""

    def __init__(self):
        self.antidotarium = set()     # 114 AN ingredients
        self.corpora_multi = set()    # 2+ corpora
        self.nomenclator_it = set()   # 4466 Italian names
        self.nomenclator_hi = set()   # 86 high-confidence Italian
        self.all_names = set()
        self._loaded = False

    def load(self):
        if self._loaded:
            return
        base = Path(__file__).parent.parent

        # Antidotarium
        p = base / 'BruteForce/Plants/Corpus_Pharmaceutique/datasets/antidotarium_nicolai_ingredients.csv'
        if p.exists():
            with open(p, 'r', encoding='utf-8') as f:
                for row in csv.DictReader(f):
                    name = row['Ingredient_Latin'].strip().lower()
                    self.antidotarium.add(name)
                    self.all_names.add(name)

        # Validation matrix (2+ corpora)
        p = base / 'v12/data/pharma_validation_matrix.json'
        if p.exists():
            with open(p, 'r') as f:
                matrix = json.load(f)
                for name, data in matrix.items():
                    self.all_names.add(name.lower())
                    if data['count'] >= 2:
                        self.corpora_multi.add(name.lower())

        # Italian nomenclator
        for fname, target in [('nomenclator_multi_attested.csv', self.nomenclator_hi),
                               ('nomenclator_unified.csv', self.nomenclator_it)]:
            p = base / 'BruteForce/Italien plant names' / fname
            if p.exists():
                with open(p, 'r', encoding='utf-8') as f:
                    for row in csv.DictReader(f):
                        name = row['italian_name'].strip().lower()
                        target.add(name)
                        self.all_names.add(name)

        self._loaded = True

    def match(self, latin_word):
        """Match a decoded Latin word against all databases.
        Returns (name, score, source) or None.
        """
        clean = latin_word.replace(' ', '').lower()

        # Exact matches
        if clean in self.antidotarium:
            return (clean, 90, 'AN')
        if clean in self.nomenclator_hi:
            return (clean, 85, 'IT_HI')
        if clean in self.corpora_multi:
            return (clean, 70, 'MULTI')
        if clean in self.nomenclator_it:
            return (clean, 60, 'IT')
        if clean in self.all_names:
            return (clean, 50, 'CORPUS')

        # Stem match (4+ chars)
        if len(clean) >= 4:
            for db, score, src in [(self.antidotarium, 80, 'AN~'),
                                    (self.nomenclator_hi, 75, 'IT_HI~'),
                                    (self.corpora_multi, 60, 'MULTI~'),
                                    (self.nomenclator_it, 50, 'IT~')]:
                for name in db:
                    if len(name) >= 4 and clean[:4] == name[:4]:
                        return (name, score, src)

        return None


# ══════════════════════════════════════════════════════════════════
# RULE-BASED SCORER
# ══════════════════════════════════════════════════════════════════

SCORE_TABLE_MATCH = 100
SCORE_LOGOGRAM = 80
SCORE_INGREDIENT_AN = 90
SCORE_INGREDIENT_IT_HI = 85
SCORE_INGREDIENT_MULTI = 70
SCORE_DOSAGE_PATTERN = 60
SCORE_STRUCTURE_COHERENT = 50
SCORE_KA_PERSEUS = 30
SCORE_KA_CORPUS = 20
SCORE_VARIANT_ZL = 10
SCORE_VARIANT_ALT = 5
SCORE_VARIANT_CONFUSION = 2


def score_decode(word_type, decoded_latin, ingredient_match, variant_weight,
                 prev_type=None, next_type=None):
    """Score a single word decode by simple rules."""
    score = 0

    # Source weight
    if variant_weight >= 1.0:
        score += SCORE_VARIANT_ZL
    elif variant_weight >= 0.5:
        score += SCORE_VARIANT_ALT
    else:
        score += SCORE_VARIANT_CONFUSION

    # Type-specific scoring
    if word_type in (WordType.LOGOGRAM, WordType.FUNCTION, WordType.VERB):
        score += SCORE_TABLE_MATCH
    elif word_type == WordType.DOSAGE:
        score += SCORE_DOSAGE_PATTERN
    elif word_type == WordType.INGREDIENT:
        if ingredient_match:
            score += ingredient_match[1]  # score from DB match
        else:
            score += SCORE_KA_CORPUS  # generic decode

    # Structural coherence bonus
    if word_type == WordType.INGREDIENT and prev_type in (WordType.VERB, WordType.DOSAGE):
        score += SCORE_STRUCTURE_COHERENT
    if word_type == WordType.DOSAGE and prev_type == WordType.INGREDIENT:
        score += SCORE_STRUCTURE_COHERENT
    if word_type == WordType.VERB and prev_type in (WordType.DOSAGE, WordType.FUNCTION, None):
        score += SCORE_STRUCTURE_COHERENT

    # Structural PENALTY
    if word_type == WordType.INGREDIENT and prev_type == WordType.INGREDIENT:
        score -= 20  # consecutive ingredients = suspect

    return score


# ══════════════════════════════════════════════════════════════════
# THE PIPELINE
# ══════════════════════════════════════════════════════════════════

class PipelineV2:
    def __init__(self):
        self.ingredient_db = IngredientDB()
        self._ka_pipeline = None

    def _ensure_ka(self):
        if self._ka_pipeline is None:
            from v12.config import Config
            from v12.pipeline import VoynichPipeline
            config = Config()
            self._ka_pipeline = VoynichPipeline(config)
            self._ka_pipeline.load()

    def decode_word_variant(self, word, variant_weight=1.0):
        """Decode a single word with classification + appropriate decoder.
        Returns dict with all info.
        """
        self.ingredient_db.load()

        result = {
            'eva': word,
            'variant_weight': variant_weight,
            'type': None,
            'latin': '',
            'ingredient': None,
            'score': 0,
        }

        # Classify
        wtype, details = classify_word(word)
        result['type'] = wtype

        if wtype in (WordType.FUNCTION, WordType.LOGOGRAM, WordType.VERB):
            result['latin'] = details.get('table_value', GLYPH_TABLE.get(word, word))
            result['score'] = score_decode(wtype, result['latin'], None, variant_weight)

        elif wtype == WordType.DOSAGE:
            prefix_meaning = details.get('prefix_meaning', '')
            dosage = details.get('dosage', word)
            result['latin'] = f"{prefix_meaning} {dosage}".strip()
            result['score'] = score_decode(wtype, result['latin'], None, variant_weight)

        elif wtype in (WordType.INGREDIENT, WordType.MIXED):
            self._ensure_ka()
            from v12.stages.hmm_decoder import decode_root

            decode_part = details.get('ingredient_part', word)
            paths = decode_root(decode_part, self._ka_pipeline.hmm, top_k=20)

            best_latin = '?'
            best_match = None
            best_score = 0

            for vp in paths:
                if not vp.latin:
                    continue
                clean = vp.latin.replace(' ', '').lower()
                match = self.ingredient_db.match(clean)

                freq = self._ka_pipeline.corpus.freq(clean)
                perseus = self._ka_pipeline.dictionary.is_valid(clean)

                s = 0
                if match:
                    s = match[1]
                elif perseus:
                    s = SCORE_KA_PERSEUS
                elif freq > 0:
                    s = SCORE_KA_CORPUS

                if s > best_score:
                    best_score = s
                    best_latin = vp.latin
                    best_match = match

            if wtype == WordType.MIXED:
                dosage = details.get('dosage', '')
                result['latin'] = f"{best_latin} {dosage}".strip()
            else:
                result['latin'] = best_latin

            result['ingredient'] = best_match[0] if best_match else None
            result['score'] = score_decode(wtype, result['latin'], best_match, variant_weight)

        else:
            result['latin'] = f'[{word}]'

        return result

    def decode_line(self, words):
        """Decode a line: for each word, try ALL variants, keep best."""
        self.ingredient_db.load()
        line_results = []

        prev_type = None
        for word in words:
            variants = get_word_variants(word, include_confusions=True, max_total=8)

            best_result = None
            best_total = -1

            for v in variants:
                r = self.decode_word_variant(v.eva, v.weight)
                # Add structural coherence with previous word
                struct_bonus = 0
                if r['type'] == WordType.INGREDIENT and prev_type in (WordType.VERB, WordType.DOSAGE):
                    struct_bonus = SCORE_STRUCTURE_COHERENT
                if r['type'] == WordType.DOSAGE and prev_type == WordType.INGREDIENT:
                    struct_bonus = SCORE_STRUCTURE_COHERENT

                total = r['score'] + struct_bonus

                if total > best_total:
                    best_total = total
                    best_result = r
                    best_result['chosen_variant'] = v.eva
                    best_result['original_eva'] = word

            if best_result:
                line_results.append(best_result)
                prev_type = best_result['type']
            else:
                line_results.append({
                    'eva': word, 'type': WordType.FUNCTION,
                    'latin': word, 'ingredient': None, 'score': 0,
                    'chosen_variant': word, 'original_eva': word,
                })
                prev_type = WordType.FUNCTION

        return line_results

    def format_3lines(self, words, lnum):
        """Produce the 3-line format: EVA / TYPE / LAT"""
        results = self.decode_line(words)

        TYPE_SHORT = {
            WordType.VERB: 'VERB', WordType.FUNCTION: 'func',
            WordType.DOSAGE: 'DOSE', WordType.INGREDIENT: 'INGR',
            WordType.MIXED: 'MIX', WordType.LOGOGRAM: 'logo',
        }

        eva_parts = []
        type_parts = []
        lat_parts = []
        var_notes = []

        for r in results:
            w = r['original_eva']
            t = TYPE_SHORT.get(r['type'], '????')

            # Latin formatting
            if r['ingredient']:
                lat = r['ingredient'].upper()
            elif r['type'] == WordType.VERB:
                lat = r['latin'].upper()
            elif r['type'] == WordType.DOSAGE:
                lat = f"[{r['latin']}]"
            else:
                lat = r['latin']

            # Variant note
            variant_used = r.get('chosen_variant', w)
            var = f"({variant_used})" if variant_used != w else ''

            width = max(len(w), len(t), len(lat), 4) + 1
            eva_parts.append(f'{w:>{width}}')
            type_parts.append(f'{t:>{width}}')
            lat_parts.append(f'{lat:>{width}}')
            if var:
                var_notes.append(f'{w}→{variant_used}')

        lines = []
        lines.append(f'L{lnum:02d} EVA:  {" ".join(eva_parts)}')
        lines.append(f'    TYPE: {" ".join(type_parts)}')
        lines.append(f'    LAT:  {" ".join(lat_parts)}')
        if var_notes:
            lines.append(f'    VAR:  {", ".join(var_notes)}')

        return lines, results


# ══════════════════════════════════════════════════════════════════
# ANOMALY DETECTOR
# ══════════════════════════════════════════════════════════════════

def detect_anomalies(results):
    """Detect structural anomalies in a decoded line."""
    anomalies = []

    types = [r['type'] for r in results]

    # 3+ consecutive INGR
    run = 0
    for i, t in enumerate(types):
        if t == WordType.INGREDIENT:
            run += 1
            if run >= 3:
                anomalies.append(('INGR_RUN', i, f'{run} consecutive INGR'))
        else:
            run = 0

    # DOSE without preceding INGR
    for i, t in enumerate(types):
        if t == WordType.DOSAGE and i > 0:
            if types[i-1] not in (WordType.INGREDIENT, WordType.MIXED, WordType.LOGOGRAM):
                anomalies.append(('ORPHAN_DOSE', i, f'DOSE after {TYPE_SHORT.get(types[i-1],"?")}'))

    # func chain 4+
    run = 0
    for i, t in enumerate(types):
        if t == WordType.FUNCTION:
            run += 1
            if run >= 4:
                anomalies.append(('FUNC_CHAIN', i, f'{run} consecutive func'))
        else:
            run = 0

    # No INGR in line
    if WordType.INGREDIENT not in types and len(types) >= 5:
        anomalies.append(('NO_INGR', 0, 'No ingredient in line'))

    return anomalies

TYPE_SHORT = {
    WordType.VERB: 'VERB', WordType.FUNCTION: 'func',
    WordType.DOSAGE: 'DOSE', WordType.INGREDIENT: 'INGR',
    WordType.MIXED: 'MIX', WordType.LOGOGRAM: 'logo',
}


# ══════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    pipeline = PipelineV2()

    zl_path = Path(__file__).parent.parent / 'data' / 'transcriptions' / 'ZL.txt'
    with open(zl_path, 'r', encoding='utf-8') as f:
        raw = f.read()

    print("=" * 90)
    print("F103R — PIPELINE V2 (variants + dual + rules + anomalies)")
    print("=" * 90)
    print()

    total_words = 0
    total_anomalies = 0
    all_ingredients = set()
    all_variants_used = 0
    stats = Counter()

    for line in raw.split('\n'):
        m = re.match(r'<(f103r\.(\d+)),', line.strip())
        if not m:
            continue
        lnum = int(m.group(2))

        text = re.sub(r'<[^>]*>', '', line.strip())
        text = re.sub(r'<!.*?>', '', text)
        text = re.sub(r'<%>|<\$>|\{[^}]*\}|@\d+;?', '', text)
        text = re.sub(r'\[[^\]]*:([^\]]*)\]', r'\1', text)
        text = re.sub(r'\?', '', text).replace(',', '.')
        words = [w.strip() for w in re.findall(r'[a-z]+', text) if w.strip()]
        if not words:
            continue

        lines, results = pipeline.format_3lines(words, lnum)

        # Stats
        for r in results:
            total_words += 1
            stats[TYPE_SHORT.get(r['type'], '?')] += 1
            if r['ingredient']:
                all_ingredients.add(r['ingredient'])
            if r.get('chosen_variant', r['eva']) != r['original_eva']:
                all_variants_used += 1

        # Anomalies
        anomalies = detect_anomalies(results)
        total_anomalies += len(anomalies)

        for l in lines:
            print(l)
        if anomalies:
            print(f'    *** ANOMALIES: {[(a[0], a[2]) for a in anomalies]}')
        print()

    print("=" * 90)
    print("STATISTIQUES")
    print("=" * 90)
    print(f"Total words: {total_words}")
    print(f"Types: {dict(stats.most_common())}")
    print(f"Ratio VERB:INGR = 1:{stats['INGR']/max(stats['VERB'],1):.1f}")
    print(f"Anomalies: {total_anomalies}")
    print(f"Variants used (≠ ZL): {all_variants_used}")
    print(f"Ingredients identified: {len(all_ingredients)}")
    for i in sorted(all_ingredients):
        print(f"  - {i}")
