"""
S4/S5: Scoring and ranking — calibrated direct scoring.
Replaces Borda rank consensus with proportional signal scoring
from VSV12 calibrated pipeline (2026-04-08).

7 signals combined:
1. PERSEUS: +3000/+5000 for dictionary-attested words
2. CORPUS FREQUENCY: log(freq+1) * 300 per word
3. MORPHOLOGY: +500 per word with valid Latin ending
4. FUSION BONUS: single-word fusions get proportional bonus
5. SPLIT PENALTY: "X et" splits penalized (et is over-frequent)
6. MONOLITHIC PRIORITY: log(freq+1) * 1200, proportional not flat
7. SHORT FRAGMENT PENALTY: all-short multi-word = debris
"""
import math
from dataclasses import dataclass
from v12.loaders.corpus import CorpusModel
from v12.loaders.dictionary import LatinDictionary
from v12.validation.morphology import is_valid_latin_ending


@dataclass
class ScoredCandidate:
    latin: str
    confidence: str     # CONFIRMED, HIGH, MEDIUM, LOW, OPAQUE
    layer: str          # L1_LOGO, L2_AGG, L3_KA, EXCEPTION
    rule: str           # provenance
    raw_score: float    # combined score (higher = better)
    signals: dict       # individual signal values


def rank_candidates(
    candidates: list[tuple[str, float, str]],   # (latin, raw_score, rule)
    corpus: CorpusModel,
    dictionary: LatinDictionary,
    layer: str = 'L3_KA',
    collision_latin: str = '',
) -> list[ScoredCandidate]:
    """
    Rank candidates using calibrated direct scoring.

    Each candidate gets a total score = sum of 9 weighted signals.
    Higher score = better candidate.
    collision_latin: if set, a candidate matching this string gets penalized.
                     Only set when prev EVA != current EVA (collision, not repeat).
    """
    if not candidates:
        return []

    # Deduplicate by latin text (keep highest raw_score)
    seen = {}
    for latin, score, rule in candidates:
        clean = latin.lower().strip()
        if clean not in seen or score > seen[clean][1]:
            seen[clean] = (latin, score, rule)
    unique = list(seen.values())

    if not unique:
        return []

    scored = []
    for latin, raw_score, rule in unique:
        words = latin.split()

        # === SIGNAL 1: PERSEUS ===
        perseus_score = 0
        perseus_valid_count = 0
        for w in words:
            if len(w) >= 2 and dictionary.is_valid(w):
                perseus_score += 3000
                perseus_valid_count += 1
                if len(w) >= 4:
                    perseus_score += 2000

        perseus_ratio = perseus_valid_count / max(len(words), 1)

        # === SIGNAL 2: CORPUS FREQUENCY ===
        corpus_score = 0
        total_freq = 0
        for w in words:
            freq = corpus.freq(w)
            if freq > 0:
                corpus_score += int(math.log(freq + 1) * 300)
                total_freq += freq

        # === SIGNAL 3: MORPHOLOGY ===
        morpho_score = 0
        morpho_count = 0
        for w in words:
            if len(w) >= 3 and is_valid_latin_ending(w):
                morpho_score += 500
                morpho_count += 1
        morpho_ratio = morpho_count / max(len(words), 1)

        # === SIGNAL 4: FUSION BONUS ===
        fusion_bonus = 0
        if len(words) == 1 and len(words[0]) >= 4:
            fused_word = words[0]
            fused_freq = corpus.freq(fused_word)
            if fused_freq >= 5:
                fusion_bonus = 2000 + int(math.log(fused_freq + 1) * 400)
            elif dictionary.is_valid(fused_word):
                fusion_bonus = 1000

        # === SIGNAL 5: SPLIT PENALTY for -dy → "X et" ===
        split_penalty = 0
        if len(words) >= 2 and words[-1] == 'et':
            pre_et = words[-2] if len(words) >= 2 else ''
            et_freq = corpus.freq('et')
            et_discount = min(int(math.log(et_freq + 1) * 100), 1000) if et_freq > 0 else 0
            split_penalty = -et_discount - 2000
            if pre_et and corpus.freq(pre_et) == 0:
                split_penalty -= 1500

        # === SIGNAL 6: MONOLITHIC PRIORITY (calibrated) ===
        mono_bonus = 0
        is_mono = 'MONO' in rule
        if is_mono and len(words) == 1 and len(words[0]) >= 4:
            mono_word = words[0]
            mono_freq = corpus.freq(mono_word)
            mono_in_perseus = dictionary.is_valid(mono_word)
            if mono_freq > 0 and mono_in_perseus:
                # Proportional: log(freq+1) * 1200
                # tere(514) → 7500, coquo(2) → 1320, coques(58) → 4870
                mono_bonus = int(math.log(mono_freq + 1) * 1200)
                if len(mono_word) >= 6:
                    mono_bonus += 2000
            elif mono_in_perseus and len(mono_word) >= 6:
                mono_bonus = 2000

        # === SIGNAL 7: SHORT FRAGMENT PENALTY ===
        short_penalty = 0
        if len(words) >= 2:
            short_count = sum(1 for w in words if len(w) <= 3)
            if short_count == len(words):
                short_penalty = -3000
            elif short_count >= len(words) - 1:
                short_penalty = -1500

        # === SIGNAL 8: MEDICAL BONUS ===
        medical_score = 0
        for w in words:
            if dictionary.is_medical(w):
                medical_score += 500

        # === SIGNAL 9: COLLISION PENALTY ===
        # Only applied when different EVA words produce the same Latin.
        # Same EVA → same Latin is a genuine repeat (scribe repeated himself).
        # Different EVA → same Latin is a decoder collision (K&A losing info).
        collision_penalty = 0
        if collision_latin and latin.lower().strip() == collision_latin.lower().strip():
            collision_penalty = -8000

        # === COMBINE ===
        total_score = (raw_score + perseus_score + corpus_score +
                       morpho_score + fusion_bonus + split_penalty +
                       mono_bonus + short_penalty + medical_score +
                       collision_penalty)

        signals = {
            'perseus': perseus_score,
            'corpus': corpus_score,
            'morpho': morpho_score,
            'fusion': fusion_bonus,
            'split': split_penalty,
            'mono': mono_bonus,
            'short': short_penalty,
            'medical': medical_score,
            'collision': collision_penalty,
            'raw': raw_score,
        }

        # === CONFIDENCE ===
        perseus_ok = perseus_ratio >= 0.5
        corpus_ok = total_freq > 0

        if perseus_ok and corpus_ok:
            confidence = 'HIGH'
        elif perseus_ok or (corpus_ok and morpho_ratio >= 0.5):
            confidence = 'MEDIUM'
        elif morpho_ratio >= 0.5 or corpus_ok:
            confidence = 'LOW'
        else:
            confidence = 'OPAQUE'

        scored.append(ScoredCandidate(
            latin=latin,
            confidence=confidence,
            layer=layer,
            rule=rule,
            raw_score=total_score,
            signals=signals,
        ))

    # Sort by total score (higher = better)
    scored.sort(key=lambda sc: -sc.raw_score)

    # Boost winner if it clearly dominates
    if len(scored) >= 2:
        margin = scored[0].raw_score - scored[1].raw_score
        if margin >= 5000 and scored[0].confidence == 'MEDIUM':
            scored[0].confidence = 'HIGH'

    return scored
