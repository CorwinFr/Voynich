"""
HMM Viterbi decoder for glyph→phoneme mapping.

3 states: STANDARD, VOWEL_CLUSTER, GAP_CONSONANT
Context-conditioned emissions for 'o' based on next glyph (lookahead-1).
"""
import math
from dataclasses import dataclass
from v12.config import Config, GlyphRule
from v12.stages.tokenizer import GlyphToken

# States
STANDARD = 'STANDARD'
VOWEL_CLUSTER = 'VOWEL_CLUSTER'
GAP_CONSONANT = 'GAP_CONSONANT'
STATES = [STANDARD, VOWEL_CLUSTER, GAP_CONSONANT]

VOWEL_GLYPHS = {'a', 'e', 'o', 'i'}
CONSONANT_GLYPHS = {'k', 't', 'd', 'l', 'r', 's', 'p', 'f', 'n', 'm', 'q',
                     'ch', 'sh', 'cth', 'ckh', 'cfh', 'cph'}


@dataclass
class ViterbiPath:
    """One decoded path through the HMM."""
    phonemes: list[str]     # phoneme per token
    states: list[str]       # state per token
    log_prob: float         # total log probability
    latin: str              # assembled Latin string

    @property
    def confidence(self) -> float:
        """Normalized confidence [0,1] based on log probability."""
        if not self.phonemes:
            return 0.0
        return math.exp(self.log_prob / max(len(self.phonemes), 1))


class GlyphHMM:
    """
    Hidden Markov Model for Voynich glyph → Latin phoneme decoding.
    Uses Viterbi algorithm to find optimal state/emission path.
    """

    def __init__(self, config: Config):
        self.config = config
        self.hmm_params = config.hmm_params
        self._build_tables()

    def _build_tables(self):
        """Build emission and transition tables from config."""
        # Transition probabilities P(next_state | current_state)
        self.transitions: dict[str, dict[str, float]] = {}
        trans_raw = self.hmm_params.get('transitions', {})
        for state in STATES:
            state_trans = trans_raw.get(state, {})
            default = state_trans.get('_default', {STANDARD: 1.0})
            self.transitions[state] = {s: default.get(s, 0.0) for s in STATES}

        # Context-conditioned emissions for 'o'
        self.context_emissions = self.hmm_params.get('context_emissions', {})

        # State-specific emission overrides
        self.state_emissions = self.hmm_params.get('emissions', {})

    def get_emissions(self, glyph: str, state: str, next_glyph: str | None,
                      prev_glyph: str | None, is_initial: bool, is_final: bool
                      ) -> list[tuple[str, float]]:
        """
        Get emission probabilities P(phoneme | glyph, state, context).

        Returns list of (phoneme, probability) pairs.
        """
        # Special: dy → et (logographic, handled at word level)
        if glyph == 'y' and prev_glyph == 'd' and is_final:
            return [('__DY_ET__', 1.0)]

        # Special: final y
        if glyph == 'y' and is_final:
            return [('__Y_FINAL__', 1.0)]

        # Context-conditioned 'o': different behavior based on next glyph
        if glyph == 'o' and state == STANDARD:
            if next_glyph == 't':
                ctx = self.context_emissions.get('o_before_t', {})
                return self._make_pairs(ctx)
            elif next_glyph == 'k':
                ctx = self.context_emissions.get('o_before_k', {})
                return self._make_pairs(ctx)
            elif next_glyph in VOWEL_GLYPHS or next_glyph in ('iin',):
                ctx = self.context_emissions.get('o_before_vowel', {})
                return self._make_pairs(ctx)

        # State-specific overrides (VOWEL_CLUSTER, GAP_CONSONANT)
        if state != STANDARD and state in self.state_emissions:
            state_em = self.state_emissions[state]
            if glyph in state_em:
                return self._make_pairs(state_em[glyph])

        # Standard emissions from glyph rules
        if glyph in self.config.glyphs:
            rule = self.config.glyphs[glyph]

            # Apply context overrides from glyph rules
            if rule.context_overrides:
                override = self._match_context_override(
                    rule, prev_glyph, next_glyph, is_initial, is_final
                )
                if override:
                    return override

            return list(zip(rule.phonemes, rule.weights))

        # Unknown glyph: emit as-is with low confidence
        return [(glyph, 0.1)]

    def _match_context_override(self, rule: GlyphRule,
                                 prev_glyph: str | None, next_glyph: str | None,
                                 is_initial: bool, is_final: bool
                                 ) -> list[tuple[str, float]] | None:
        """Try to match context overrides for a glyph rule."""
        overrides = rule.context_overrides

        # k: prev in vowel set
        if rule.glyph == 'k':
            vowel_set = {'a', 'o', 'e', 'y', 'q'}
            if prev_glyph in vowel_set and 'prev_in_vowel' in overrides:
                return self._make_pairs(overrides['prev_in_vowel'])
            if next_glyph in ('a', 'o', 'e', 'iin', 'aiin') and 'next_in_vowel_or_iin' in overrides:
                return self._make_pairs(overrides['next_in_vowel_or_iin'])

        # d: context-dependent
        if rule.glyph == 'd':
            if next_glyph == 'a' and 'next=a' in overrides:
                return self._make_pairs(overrides['next=a'])
            if next_glyph == 'ch' and is_initial and 'next=ch_AND_initial' in overrides:
                return self._make_pairs(overrides['next=ch_AND_initial'])
            if next_glyph == 'o' and is_initial and 'next=o_AND_initial' in overrides:
                return self._make_pairs(overrides['next=o_AND_initial'])
            if prev_glyph in VOWEL_GLYPHS and 'prev_in_vowel' in overrides:
                return self._make_pairs(overrides['prev_in_vowel'])

        # l: context-dependent
        if rule.glyph == 'l':
            if (next_glyph == 'y' or is_final) and 'next=y_OR_final_after_cth' in overrides:
                return self._make_pairs(overrides['next=y_OR_final_after_cth'])
            if is_initial and 'initial' in overrides:
                return self._make_pairs(overrides['initial'])

        # r: prev=a and final
        if rule.glyph == 'r':
            if prev_glyph == 'a' and is_final and 'prev=a_AND_final' in overrides:
                return self._make_pairs(overrides['prev=a_AND_final'])

        # y: initial
        if rule.glyph == 'y':
            if is_initial and 'initial' in overrides:
                return self._make_pairs(overrides['initial'])

        # a: prev=k
        if rule.glyph == 'a':
            if prev_glyph == 'k' and 'prev=k' in overrides:
                return self._make_pairs(overrides['prev=k'])

        # cth: context
        if rule.glyph == 'cth':
            if next_glyph == 'y' and 'next=y' in overrides:
                return self._make_pairs(overrides['next=y'])
            if is_initial and next_glyph == 'o' and 'initial_AND_next=o' in overrides:
                return self._make_pairs(overrides['initial_AND_next=o'])

        return None

    def _make_pairs(self, data: dict) -> list[tuple[str, float]]:
        """Convert {phonemes: [...], weights: [...]} to list of (phoneme, weight)."""
        if not data or 'phonemes' not in data:
            return []
        phonemes = data['phonemes']
        weights = data.get('weights', [1.0 / len(phonemes)] * len(phonemes))
        return list(zip(phonemes, weights))

    def viterbi(self, tokens: list[GlyphToken], top_k: int = 5) -> list[ViterbiPath]:
        """
        Find top-k most probable state/emission paths through the HMM.

        Uses beam search Viterbi for efficiency.
        """
        if not tokens:
            return [ViterbiPath([], [], 0.0, '')]

        n = len(tokens)
        beam_width = max(top_k * 3, 15)  # keep more paths during search

        # Each beam entry: (log_prob, states, phonemes)
        beam: list[tuple[float, list[str], list[str]]] = [(0.0, [], [])]

        for i, tok in enumerate(tokens):
            next_glyph = tokens[i+1].glyph if i+1 < n else None
            prev_glyph = tokens[i-1].glyph if i > 0 else None

            new_beam: list[tuple[float, list[str], list[str]]] = []

            for log_prob, states, phonemes in beam:
                current_state = states[-1] if states else STANDARD

                # Get emissions for this glyph in current state
                emissions = self.get_emissions(
                    tok.glyph, current_state, next_glyph, prev_glyph,
                    tok.is_initial, tok.is_final,
                )

                for phoneme, emit_prob in emissions:
                    if emit_prob <= 0:
                        continue

                    # Transition to next state
                    for next_state, trans_prob in self.transitions[current_state].items():
                        if trans_prob <= 0:
                            continue

                        # Special: transition to VOWEL_CLUSTER if emitting vowel
                        if tok.glyph in VOWEL_GLYPHS and next_state == VOWEL_CLUSTER:
                            pass  # allow
                        elif tok.glyph not in VOWEL_GLYPHS and next_state == VOWEL_CLUSTER:
                            continue  # can't enter vowel cluster on non-vowel

                        new_lp = log_prob + math.log(emit_prob + 1e-10) + math.log(trans_prob + 1e-10)
                        new_beam.append((
                            new_lp,
                            states + [next_state],
                            phonemes + [phoneme],
                        ))

            # Prune beam
            new_beam.sort(key=lambda x: -x[0])
            beam = new_beam[:beam_width]

        # Convert beam entries to ViterbiPaths
        results = []
        seen_latin = set()
        for log_prob, states, phonemes in beam:
            latin = self._assemble_latin(phonemes)
            if latin in seen_latin:
                continue
            seen_latin.add(latin)
            results.append(ViterbiPath(
                phonemes=phonemes,
                states=states,
                log_prob=log_prob,
                latin=latin,
            ))
            if len(results) >= top_k:
                break

        return results if results else [ViterbiPath([], [], -100.0, tokens_to_eva(tokens))]

    def _assemble_latin(self, phonemes: list[str]) -> str:
        """Assemble phoneme list into a Latin string, handling special markers."""
        parts = []
        has_dy = False
        y_final = False

        for ph in phonemes:
            if ph == '__DY_ET__':
                has_dy = True
            elif ph == '__Y_FINAL__':
                y_final = True
            elif ph:  # skip empty emissions
                parts.append(ph)

        base = ''.join(parts)

        # Deduplicate adjacent identical vowels (scribal artifact)
        base = self._dedup_vowels(base)

        if has_dy:
            base = f"{base} et"

        return base

    def _dedup_vowels(self, word: str) -> str:
        """Remove adjacent duplicate vowels (ee→e, aa→a, etc.)."""
        if not word:
            return word
        vowels = set('aeiou')
        result = [word[0]]
        for i in range(1, len(word)):
            if word[i] in vowels and word[i] == word[i-1]:
                continue  # skip duplicate
            result.append(word[i])
        return ''.join(result)
