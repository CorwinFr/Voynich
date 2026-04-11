"""
CANDIDATE_STORE — Central registry of decoding candidates for every VMS word.

This is the HEART of the attack system.
Each VMS word has N candidates, each with scores from multiple attacks.
The store is persistent (JSON file) and accumulative (attacks ADD scores, never erase).

Usage:
    from lib.candidate_store import CandidateStore

    store = CandidateStore()
    store.load()  # or start fresh

    # Add a candidate from an attack
    store.add_candidate('chckhy', 'I_myrrha', 'attack_02',
                        score=0.92, detail='16 folios vs 12.6 expected')

    # Add another candidate from a different attack
    store.add_candidate('chckhy', 'I_mastix', 'attack_02',
                        score=0.42, detail='8 folios vs 7.2 expected')

    # Same word, same candidate, different attack
    store.add_candidate('chckhy', 'I_myrrha', 'attack_01',
                        score=0.85, detail='Position 5 on f103r matches Aurea')

    # Get best candidate
    best = store.get_best('chckhy')  # -> {'ref_id': 'I_myrrha', 'score_total': 0.88, ...}

    # Get all candidates for a word
    candidates = store.get_candidates('chckhy')  # -> list sorted by score

    # Save
    store.save()
"""
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Optional, Any

STORE_FILE = Path(__file__).parent.parent / 'results' / 'candidate_registry.json'

# Confidence thresholds
CONFIRMED = 0.95
PROBABLE = 0.75
POSSIBLE = 0.50


class CandidateStore:
    """Persistent registry of decoding candidates."""

    def __init__(self, filepath=None):
        self.filepath = Path(filepath) if filepath else STORE_FILE
        self._data: Dict[str, dict] = {}  # eva_word -> word_data
        self._version = 0

    def load(self):
        """Load existing registry from disk."""
        if self.filepath.exists():
            with open(self.filepath, encoding='utf-8') as f:
                raw = json.load(f)
            self._data = raw.get('words', {})
            self._version = raw.get('version', 0)
            print(f"Loaded {len(self._data)} words from {self.filepath}")
        else:
            self._data = {}
            self._version = 0
            print("Starting fresh candidate registry")
        return self

    def save(self):
        """Save registry to disk."""
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        self._version += 1
        output = {
            'version': self._version,
            'n_words': len(self._data),
            'n_confirmed': sum(1 for w in self._data.values() if w.get('confidence', 0) >= CONFIRMED),
            'n_probable': sum(1 for w in self._data.values() if PROBABLE <= w.get('confidence', 0) < CONFIRMED),
            'n_possible': sum(1 for w in self._data.values() if POSSIBLE <= w.get('confidence', 0) < PROBABLE),
            'words': self._data,
        }
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(self._data)} words (v{self._version}) to {self.filepath}")

    def _ensure_word(self, eva_word):
        """Ensure a word entry exists."""
        if eva_word not in self._data:
            self._data[eva_word] = {
                'eva': eva_word,
                'candidates': {},
                'best_candidate': None,
                'confidence': 0.0,
                'status': 'UNKNOWN',
            }
        return self._data[eva_word]

    def add_candidate(self, eva_word, ref_id, attack_name, score, detail='', **extra):
        """Add or update a candidate score from an attack.

        Args:
            eva_word: EVA word (e.g., 'chckhy')
            ref_id: reference ID (e.g., 'I_myrrha', 'V_coque')
            attack_name: which attack produced this (e.g., 'attack_02')
            score: float 0-1
            detail: human-readable explanation
            **extra: any additional fields
        """
        word_data = self._ensure_word(eva_word)
        candidates = word_data['candidates']

        if ref_id not in candidates:
            candidates[ref_id] = {
                'ref_id': ref_id,
                'scores': {},
                'evidence': [],
            }

        cand = candidates[ref_id]

        # Add score (never erase existing scores from other attacks)
        cand['scores'][attack_name] = score

        # Add evidence
        if detail:
            cand['evidence'].append({
                'source': attack_name,
                'detail': detail,
                'score': score,
            })

        # Add extra fields
        for k, v in extra.items():
            cand[k] = v

        # Recompute total score and best candidate
        self._recompute(eva_word)

    def add_counter_evidence(self, eva_word, ref_id, attack_name, detail):
        """Add evidence AGAINST a candidate."""
        word_data = self._ensure_word(eva_word)
        candidates = word_data['candidates']
        if ref_id in candidates:
            if 'counter_evidence' not in candidates[ref_id]:
                candidates[ref_id]['counter_evidence'] = []
            candidates[ref_id]['counter_evidence'].append({
                'source': attack_name,
                'detail': detail,
            })

    def set_confirmed(self, eva_word, ref_id, source='manual'):
        """Mark a mapping as CONFIRMED (score = 1.0)."""
        self.add_candidate(eva_word, ref_id, source, score=1.0, detail='Manually confirmed')

    def _recompute(self, eva_word):
        """Recompute total scores and best candidate for a word."""
        word_data = self._data[eva_word]
        candidates = word_data['candidates']

        best_ref = None
        best_score = 0.0

        for ref_id, cand in candidates.items():
            scores = cand['scores']
            if not scores:
                cand['score_total'] = 0.0
                continue

            # Combined score: weighted average favoring multi-source evidence
            values = list(scores.values())
            n_attacks = len(values)
            avg = sum(values) / n_attacks

            # Bonus for multi-source convergence (more attacks = more confident)
            convergence_bonus = min(0.1 * (n_attacks - 1), 0.3)  # max +0.3 for 4+ attacks

            # Penalty for counter-evidence
            n_counter = len(cand.get('counter_evidence', []))
            counter_penalty = min(0.05 * n_counter, 0.2)  # max -0.2

            total = min(1.0, max(0.0, avg + convergence_bonus - counter_penalty))
            cand['score_total'] = round(total, 4)
            cand['n_attacks'] = n_attacks

            if total > best_score:
                best_score = total
                best_ref = ref_id

        word_data['best_candidate'] = best_ref
        word_data['confidence'] = round(best_score, 4)

        if best_score >= CONFIRMED:
            word_data['status'] = 'CONFIRMED'
        elif best_score >= PROBABLE:
            word_data['status'] = 'PROBABLE'
        elif best_score >= POSSIBLE:
            word_data['status'] = 'POSSIBLE'
        else:
            word_data['status'] = 'DOUBTFUL'

    # ---- Getters ----

    def get_candidates(self, eva_word):
        """Get all candidates for a word, sorted by score descending."""
        word_data = self._data.get(eva_word, {})
        candidates = word_data.get('candidates', {})
        return sorted(candidates.values(), key=lambda c: -c.get('score_total', 0))

    def get_best(self, eva_word):
        """Get the best candidate for a word."""
        word_data = self._data.get(eva_word, {})
        best_ref = word_data.get('best_candidate')
        if best_ref:
            return word_data['candidates'].get(best_ref)
        return None

    def get_status(self, eva_word):
        """Get the status of a word (CONFIRMED/PROBABLE/POSSIBLE/DOUBTFUL/UNKNOWN)."""
        return self._data.get(eva_word, {}).get('status', 'UNKNOWN')

    def get_confidence(self, eva_word):
        """Get the confidence score of the best candidate."""
        return self._data.get(eva_word, {}).get('confidence', 0.0)

    def get_confirmed_words(self):
        """Get all words with CONFIRMED status."""
        return {w: d for w, d in self._data.items() if d.get('status') == 'CONFIRMED'}

    def get_probable_words(self):
        """Get all words with PROBABLE or better status."""
        return {w: d for w, d in self._data.items() if d.get('confidence', 0) >= PROBABLE}

    def get_all_words(self):
        """Get all words in the registry."""
        return dict(self._data)

    # ---- Seeding ----

    def seed_logograms(self):
        """Seed the registry with the 16 known logograms (CONFIRMED)."""
        from .vms_parser import LOGOGRAMS
        for eva, latin in LOGOGRAMS.items():
            # Map to ref_id format
            ref_map = {
                'ac': 'LOGO_ac', 'se': 'LOGO_se', 'de': 'PREP_de',
                'recipe': 'V_recipe', 'vel': 'CONJ_vel', 'crux': 'LOGO_crux',
                'cum': 'PREP_cum', 'misce': 'V_misce', 'per': 'PREP_per',
                'el': 'LOGO_el', 'in': 'PREP_in', 'est': 'COP_est',
                'ci': 'LOGO_ci', 'usque': 'PREP_usque', 'aier': 'LOGO_aier',
            }
            ref_id = ref_map.get(latin, f'LOGO_{latin}')
            self.set_confirmed(eva, ref_id, source='bifolio_bH1')
        print(f"Seeded {len(LOGOGRAMS)} confirmed logograms")

    # ---- Reporting ----

    def print_summary(self):
        """Print summary of registry state."""
        n_total = len(self._data)
        n_confirmed = sum(1 for d in self._data.values() if d.get('status') == 'CONFIRMED')
        n_probable = sum(1 for d in self._data.values() if d.get('status') == 'PROBABLE')
        n_possible = sum(1 for d in self._data.values() if d.get('status') == 'POSSIBLE')
        n_doubtful = sum(1 for d in self._data.values() if d.get('status') == 'DOUBTFUL')

        print("=" * 50)
        print("CANDIDATE REGISTRY")
        print("=" * 50)
        print(f"Total words: {n_total}")
        print(f"  CONFIRMED (>={CONFIRMED}): {n_confirmed}")
        print(f"  PROBABLE  (>={PROBABLE}):  {n_probable}")
        print(f"  POSSIBLE  (>={POSSIBLE}):  {n_possible}")
        print(f"  DOUBTFUL  (<{POSSIBLE}):   {n_doubtful}")
        print()

        if n_confirmed > 0:
            print("CONFIRMED mappings:")
            for eva, data in sorted(self._data.items()):
                if data.get('status') == 'CONFIRMED':
                    best = data.get('best_candidate', '?')
                    print(f"  {eva:>15s} = {best}")

    def export_mapping(self):
        """Export the current best mapping as a simple dict EVA -> ref_id."""
        return {
            eva: data['best_candidate']
            for eva, data in self._data.items()
            if data.get('best_candidate')
        }


if __name__ == '__main__':
    store = CandidateStore()
    store.load()
    store.seed_logograms()
    store.print_summary()
    store.save()
