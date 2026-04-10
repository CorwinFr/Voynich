"""
DUAL DECODER — Routes each word to the right decoding system.

LOGOGRAM/FUNCTION → Table lookup (instant, 100% reliable)
DOSAGE → Quantity parser (ana X drachmes)
INGREDIENT → K&A pipeline (HMM beam=30, monolithic)
                → then match against ingredient corpora

This is the MASTER decoder that replaces direct pipeline usage.
"""
import sys
import os
import re
import json
import csv
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from v12.classifier import classify_line, WordType, GLYPH_TABLE
from v12.decoder_table import decode_word_table, COMPOUNDS


class DualDecoder:
    """Decodes VMS text using the dual system."""

    def __init__(self):
        self._pipeline = None
        self._ingredients_db = None

    def _ensure_pipeline(self):
        if self._pipeline is None:
            from v12.config import Config
            from v12.pipeline import VoynichPipeline
            config = Config()
            self._pipeline = VoynichPipeline(config)
            self._pipeline.load()

    def _ensure_ingredients(self):
        if self._ingredients_db is not None:
            return
        self._ingredients_db = set()

        # Load Antidotarium
        an_path = Path(__file__).parent.parent / 'BruteForce' / 'Plants' / \
                  'Corpus_Pharmaceutique' / 'datasets' / 'antidotarium_nicolai_ingredients.csv'
        if an_path.exists():
            with open(an_path, 'r', encoding='utf-8') as f:
                for row in csv.DictReader(f):
                    self._ingredients_db.add(row['Ingredient_Latin'].strip().lower())

        # Load validation matrix
        matrix_path = Path(__file__).parent / 'data' / 'pharma_validation_matrix.json'
        if matrix_path.exists():
            with open(matrix_path, 'r') as f:
                matrix = json.load(f)
                for name in matrix:
                    self._ingredients_db.add(name.lower())

        # Load Italian nomenclator (multi-attested only)
        nom_path = Path(__file__).parent.parent / 'BruteForce' / 'Italien plant names' / \
                   'nomenclator_multi_attested.csv'
        if nom_path.exists():
            with open(nom_path, 'r', encoding='utf-8') as f:
                for row in csv.DictReader(f):
                    self._ingredients_db.add(row['italian_name'].strip().lower())

    def decode_word(self, word, word_type, details):
        """Decode a single word given its classification.

        Returns:
            {
                'eva': str,
                'type': str,
                'latin': str,
                'confidence': str,  # HIGH, MEDIUM, LOW, TABLE, DOSAGE
                'ingredient': str or None,  # matched ingredient name
                'source': str,  # TABLE, DOSAGE, KA, LOGOGRAM
            }
        """
        result = {
            'eva': word,
            'type': word_type,
            'latin': '',
            'confidence': '',
            'ingredient': None,
            'source': '',
        }

        if word_type in (WordType.FUNCTION, WordType.LOGOGRAM, WordType.VERB):
            # TABLE LOOKUP
            value = details.get('table_value', '')
            if not value and word in GLYPH_TABLE:
                value = GLYPH_TABLE[word]
            result['latin'] = value
            result['confidence'] = 'TABLE'
            result['source'] = 'TABLE'

        elif word_type == WordType.DOSAGE:
            # QUANTITY SYSTEM
            prefix_meaning = details.get('prefix_meaning', '')
            dosage = details.get('dosage', '')
            if prefix_meaning:
                result['latin'] = f"{prefix_meaning} {dosage}"
            else:
                result['latin'] = dosage
            result['confidence'] = 'DOSAGE'
            result['source'] = 'DOSAGE'

        elif word_type == WordType.MIXED:
            # PREFIX (logogram) + INGREDIENT root + DOSAGE suffix
            ingr_part = details.get('ingredient_part', '')
            dosage = details.get('dosage', '')
            # Decode ingredient part by K&A
            self._ensure_pipeline()
            from v12.stages.hmm_decoder import decode_root
            paths = decode_root(ingr_part, self._pipeline.hmm, top_k=15)
            best_ingr = self._pick_best_ingredient(paths)
            result['latin'] = f"{best_ingr} {dosage}"
            result['confidence'] = 'MEDIUM'
            result['source'] = 'KA+DOSAGE'
            result['ingredient'] = self._match_ingredient(best_ingr)

        elif word_type == WordType.INGREDIENT:
            # K&A DECODE (full word)
            self._ensure_pipeline()
            from v12.stages.hmm_decoder import decode_root
            paths = decode_root(word, self._pipeline.hmm, top_k=30)
            best = self._pick_best_ingredient(paths)
            result['latin'] = best
            result['ingredient'] = self._match_ingredient(best)
            if result['ingredient']:
                result['confidence'] = 'HIGH'
            else:
                result['confidence'] = 'MEDIUM'
            result['source'] = 'KA'

        else:
            result['latin'] = f'[{word}]'
            result['confidence'] = 'LOW'
            result['source'] = 'UNKNOWN'

        return result

    def _pick_best_ingredient(self, hmm_paths):
        """From HMM paths, pick the best one that matches a known ingredient."""
        self._ensure_pipeline()
        self._ensure_ingredients()

        candidates = []
        seen = set()
        for vp in hmm_paths:
            if not vp.latin:
                continue
            clean = vp.latin.replace(' ', '').lower()
            if clean in seen:
                continue
            seen.add(clean)

            freq = self._pipeline.corpus.freq(clean)
            perseus = self._pipeline.dictionary.is_valid(clean)
            is_ingredient = self._match_ingredient(clean) is not None

            # Score: ingredient match > perseus+freq > perseus > freq
            score = 0
            if is_ingredient:
                score += 10000
            if perseus:
                score += 2000
            if freq > 0:
                score += freq

            candidates.append((vp.latin, score))

        if candidates:
            candidates.sort(key=lambda x: -x[1])
            return candidates[0][0]
        return '?'

    def _match_ingredient(self, latin_decode):
        """Check if a decoded Latin string matches a known ingredient."""
        self._ensure_ingredients()
        clean = latin_decode.replace(' ', '').lower()

        # Exact match
        if clean in self._ingredients_db:
            return clean

        # Stem match (4+ chars)
        if len(clean) >= 4:
            for ingr in self._ingredients_db:
                if len(ingr) >= 4 and clean[:4] == ingr[:4]:
                    return ingr

        return None

    def decode_line(self, words):
        """Decode a full line of EVA words.

        Returns list of result dicts.
        """
        classified = classify_line(words)
        results = []
        for word, wtype, details in classified:
            result = self.decode_word(word, wtype, details)
            results.append(result)
        return results

    def decode_line_formatted(self, words):
        """Decode and format a line for human reading."""
        results = self.decode_line(words)
        parts = []
        for r in results:
            if r['type'] == WordType.VERB:
                parts.append(f"**{r['latin'].upper()}**")
            elif r['type'] == WordType.FUNCTION:
                parts.append(r['latin'])
            elif r['type'] == WordType.DOSAGE:
                parts.append(f"[{r['latin']}]")
            elif r['ingredient']:
                parts.append(f"*{r['latin']}*({r['ingredient']})")
            elif r['type'] == WordType.INGREDIENT:
                parts.append(f"_{r['latin']}_")
            elif r['type'] == WordType.MIXED:
                parts.append(f"_{r['latin']}_")
            else:
                parts.append(r['latin'])
        return ' '.join(parts)


# ══════════════════════════════════════════════════════════════════
# MAIN — Decode f103r with the dual system
# ══════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    decoder = DualDecoder()

    zl_path = Path(__file__).parent.parent / 'data' / 'transcriptions' / 'ZL.txt'
    with open(zl_path, 'r', encoding='utf-8') as f:
        raw = f.read()

    print("=" * 80)
    print("F103R — DUAL SYSTEM DECODE")
    print("VERBS in **BOLD**, ingredients in _italic_, dosages in [brackets]")
    print("Known ingredients marked with (name)")
    print("=" * 80)
    print()

    total_words = 0
    total_ingredients = 0
    identified_ingredients = set()
    total_dosages = 0
    total_verbs = 0

    for line in raw.split('\n'):
        m = re.match(r'<(f103r\.(\d+)),([^>]+)>', line.strip())
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

        formatted = decoder.decode_line_formatted(words)
        results = decoder.decode_line(words)

        # Stats
        for r in results:
            total_words += 1
            if r['type'] == WordType.INGREDIENT or r['type'] == WordType.MIXED:
                total_ingredients += 1
                if r['ingredient']:
                    identified_ingredients.add(r['ingredient'])
            elif r['type'] == WordType.DOSAGE:
                total_dosages += 1
            elif r['type'] == WordType.VERB:
                total_verbs += 1

        print(f"L{lnum:2d}: {formatted[:100]}")

    print()
    print("=" * 80)
    print("STATISTICS")
    print("=" * 80)
    print(f"Total words: {total_words}")
    print(f"Verbs: {total_verbs}")
    print(f"Ingredients (total): {total_ingredients}")
    print(f"Ingredients (identified): {len(identified_ingredients)}")
    print(f"Dosages: {total_dosages}")
    print(f"Verb:Ingredient ratio: 1:{total_ingredients/max(total_verbs,1):.1f}")
    print()
    print(f"IDENTIFIED INGREDIENTS:")
    for ingr in sorted(identified_ingredients):
        print(f"  - {ingr}")
