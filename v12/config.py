"""
Configuration loader: reads all rules from JSON files into typed dataclasses.
Single source of truth for all mappings, thresholds, and parameters.
"""
import json
import os
from dataclasses import dataclass, field
from typing import Optional

RULES_DIR = os.path.join(os.path.dirname(__file__), 'rules')
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')


@dataclass(frozen=True)
class GlyphRule:
    glyph: str
    phonemes: list[str]
    weights: list[float]
    locked: bool = False
    context_overrides: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Logogram:
    eva: str
    latin: str
    confidence: str   # 'confirmed', 'proposed', 'statistical'
    freq: int = 0
    source: str = ''


@dataclass(frozen=True)
class PrefixRule:
    eva: str
    latin: str
    tier: str         # '1', '1b', '2'
    probability: float
    blacklist: tuple[str, ...] = ()


@dataclass(frozen=True)
class SuffixRule:
    eva: str
    latin: str
    suffix_type: str  # 'truncation', 'accusative', 'conjunction', etc.


@dataclass(frozen=True)
class ConfirmedRoot:
    eva: str
    latin: str
    score: int


class Config:
    """Loads and provides access to all decoder rules."""

    def __init__(self, rules_dir: str = RULES_DIR, data_dir: str = DATA_DIR):
        self.rules_dir = rules_dir
        self.data_dir = data_dir

        self.glyphs: dict[str, GlyphRule] = {}
        self.logograms: dict[str, Logogram] = {}
        self.prefixes: list[PrefixRule] = []
        self.suffixes: dict[str, SuffixRule] = {}
        self.confirmed_roots: dict[str, ConfirmedRoot] = {}
        self.hmm_params: dict = {}
        self.exceptions: dict[str, str] = {}
        self.not_prefixes: set[str] = set()

        self._load_all()

    def _load_json(self, filename: str) -> dict:
        path = os.path.join(self.rules_dir, filename)
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _load_all(self):
        self._load_glyphs()
        self._load_logograms()
        self._load_prefixes()
        self._load_suffixes()
        self._load_confirmed_roots()
        self._load_hmm_params()
        self._load_exceptions()

    def _load_glyphs(self):
        raw = self._load_json('glyphs.json')
        for glyph, data in raw.items():
            if glyph.startswith('_'):
                continue
            self.glyphs[glyph] = GlyphRule(
                glyph=glyph,
                phonemes=data['phonemes'],
                weights=data['weights'],
                locked=data.get('locked', False),
                context_overrides=data.get('context_overrides', {}),
            )

    def _load_logograms(self):
        raw = self._load_json('logograms.json')
        for eva, data in raw.items():
            if eva.startswith('_'):
                continue
            self.logograms[eva] = Logogram(
                eva=eva,
                latin=data['latin'],
                confidence=data['confidence'],
                freq=data.get('freq', 0),
                source=data.get('source', ''),
            )

    def _load_prefixes(self):
        raw = self._load_json('prefixes.json')
        self.not_prefixes = set(raw.get('_not_prefixes', []))
        for eva, data in raw.items():
            if eva.startswith('_'):
                continue
            self.prefixes.append(PrefixRule(
                eva=eva,
                latin=data['latin'],
                tier=str(data['tier']),
                probability=data['probability'],
                blacklist=tuple(data.get('blacklist', [])),
            ))
        # Sort: longest prefix first, then by tier
        tier_order = {'1': 0, '1b': 1, '2': 2}
        self.prefixes.sort(key=lambda p: (-len(p.eva), tier_order.get(p.tier, 3)))

    def _load_suffixes(self):
        raw = self._load_json('suffixes.json')
        for eva, data in raw.items():
            if eva.startswith('_'):
                continue
            self.suffixes[eva] = SuffixRule(
                eva=eva,
                latin=data['latin'],
                suffix_type=data['type'],
            )

    def _load_confirmed_roots(self):
        raw = self._load_json('confirmed_roots.json')
        for eva, data in raw.items():
            if eva.startswith('_'):
                continue
            self.confirmed_roots[eva] = ConfirmedRoot(
                eva=eva,
                latin=data['latin'],
                score=data['score'],
            )

    def _load_hmm_params(self):
        self.hmm_params = self._load_json('hmm_params.json')

    def _load_exceptions(self):
        raw = self._load_json('exceptions.json')
        self.exceptions = raw.get('_entries', {})

    # Glyph ordering for tokenization (longest first for compound glyphs)
    GLYPH_ORDER = [
        'aiin', 'cth', 'ckh', 'cfh', 'cph',
        'iin', 'iir',
        'sh', 'ch',
        'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'k', 'l',
        'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'v', 'x', 'y',
    ]

    # Data file paths
    @property
    def transcription_path(self) -> str:
        return os.path.join(self.data_dir, 'transcriptions', 'ZL.txt')

    @property
    def corpus_path(self) -> str:
        return os.path.join(self.data_dir, 'corpus_latin_medical_extended.txt')

    @property
    def perseus_path(self) -> str:
        return os.path.join(self.data_dir, 'latin_valid_wordset.json')

    @property
    def bigram_path(self) -> str:
        return os.path.join(self.data_dir, 'latin_word_bigrams.json')
