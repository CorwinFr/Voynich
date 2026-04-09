"""
Stage S5: Sectorial reranker (raw-form LMs).
Uses raw-form bigram Language Models (no Collatinus needed)
to choose between candidates based on context.
Key insight: 'coque coque' has score 0 in corpus -> forces alternatives.
"""
import json
import math
import os
from v12.stages.logogram import DecodedWord


SECTION_LM_MAP = {
    'H': 'herbal', 'S': 'pharma', 'P': 'pharma',
    'B': 'balnea', 'T': 'pharma', 'Z': 'pharma',
    'C': 'pharma', 'A': 'herbal',
}


class RawLM:
    """Simple bigram LM on raw word forms."""

    def __init__(self, path: str):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.unigrams = data.get('unigrams', {})
        self.bigrams = data.get('bigrams', {})
        self.total = sum(self.unigrams.values())

    def bigram_score(self, w1: str, w2: str) -> float:
        """Log probability of w2 given w1."""
        key = f"{w1}|{w2}"
        bg = self.bigrams.get(key, 0)
        u1 = self.unigrams.get(w1, 0)

        if bg > 0 and u1 > 0:
            return math.log(bg / u1)
        elif u1 > 0:
            u2 = self.unigrams.get(w2, 0)
            if u2 > 0:
                return math.log(u2 / self.total) - 2.0
            return -12.0
        return -12.0


class SectorialReranker:
    """Reranks decoded words using raw-form bigram LMs."""

    def __init__(self, lm_dir: str):
        self.lms = {}
        for name in ['herbal', 'pharma', 'balnea']:
            path = os.path.join(lm_dir, f'lm_{name}_raw.json')
            if os.path.exists(path):
                self.lms[name] = RawLM(path)

    def get_lm(self, section: str):
        name = SECTION_LM_MAP.get(section, 'pharma')
        return self.lms.get(name)

    def rerank_line(self, decoded_words: list[DecodedWord], section: str) -> list[DecodedWord]:
        """
        Rerank a line using bigram context from raw-form LMs.
        CONFIRMED words are never touched.
        """
        lm = self.get_lm(section)
        if not lm or len(decoded_words) < 2:
            return decoded_words

        # Pharma words that must NEVER be replaced by reranking
        PROTECTED_WORDS = {'coque', 'coques', 'coquas', 'coquere', 'coqui', 'coquo',
                           'tere', 'misce', 'cola', 'colo', 'recipe', 'collige',
                           'cole', 'collige',
                           'hiera', 'aloes', 'cicura', 'dolor', 'rens', 'iecur',
                           'equaliter', 'aquam', 'iure', 'curam', 'curas'}

        # Build candidate lists
        cands_per_pos = []
        for dw in decoded_words:
            latin_main = dw.latin.split()[0].lower() if dw.latin else ''
            is_protected = dw.confidence == 'CONFIRMED' or latin_main in PROTECTED_WORDS
            if is_protected:
                cands_per_pos.append([(dw.latin, dw.confidence, dw.rule)])
            else:
                cands = [(dw.latin, dw.confidence, dw.rule)]
                if dw.alternatives:
                    for alt_latin, alt_rule in dw.alternatives[:3]:
                        cands.append((alt_latin, dw.confidence, alt_rule))
                cands_per_pos.append(cands)

        # Greedy left-to-right with lookahead
        result = []
        prev_word = None

        for i, dw in enumerate(decoded_words):
            cands = cands_per_pos[i]

            if len(cands) == 1:
                # Only one option (CONFIRMED or no alternatives)
                result.append(dw)
                prev_word = cands[0][0].split()[0]
                continue

            # Score each candidate
            best_latin = cands[0][0]
            best_score = -999
            best_conf = cands[0][1]
            best_rule = cands[0][2]

            # Get next word for lookahead
            next_word = None
            if i + 1 < len(decoded_words):
                next_word = decoded_words[i+1].latin.split()[0]

            for latin, conf, rule in cands:
                # Split compound words and take first
                main = latin.split()[0] if latin else ''

                score = 0.0
                # Bigram with previous word
                if prev_word and main:
                    score += lm.bigram_score(prev_word, main) * 100
                # Bigram with next word (lookahead)
                if next_word and main:
                    score += lm.bigram_score(main, next_word) * 50

                if score > best_score:
                    best_score = score
                    best_latin = latin
                    best_conf = conf
                    best_rule = rule

            if best_latin != dw.latin:
                result.append(DecodedWord(
                    eva=dw.eva, latin=best_latin,
                    confidence=best_conf,
                    layer=dw.layer + '_RR',
                    rule=best_rule + '_reranked',
                    alternatives=dw.alternatives,
                ))
            else:
                result.append(dw)

            prev_word = best_latin.split()[0] if best_latin else None

        return result
