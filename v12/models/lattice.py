"""
Segmentation lattice: DAG of all possible PREFIX + ROOT + SUFFIX splits.
MorphAGram-inspired: considers ALL segmentations, not greedy matching.
"""
from dataclasses import dataclass, field
from v12.config import Config, PrefixRule, SuffixRule
from v12.stages.tokenizer import GlyphToken, tokens_to_eva


@dataclass
class SegmentArc:
    """One possible segment in the lattice."""
    start: int          # start position in token sequence
    end: int            # end position (exclusive)
    segment_type: str   # 'prefix', 'root', 'suffix', 'whole'
    eva_form: str       # EVA substring
    latin_value: str    # Latin value (for affixes; empty for roots)
    weight: float       # statistical weight (higher = more likely)
    rule: str           # which rule produced this arc


@dataclass
class SegmentPath:
    """One complete segmentation: prefix + root + suffix."""
    prefix: SegmentArc | None
    root: SegmentArc
    suffix: SegmentArc | None
    total_weight: float

    @property
    def root_eva(self) -> str:
        return self.root.eva_form

    @property
    def prefix_latin(self) -> str:
        return self.prefix.latin_value if self.prefix else ''

    @property
    def suffix_latin(self) -> str:
        return self.suffix.latin_value if self.suffix else ''


class SegmentLattice:
    """
    Build and enumerate all valid segmentations of an EVA word.

    Strategy:
    - For each possible prefix (including empty prefix):
      - For each possible suffix (including empty suffix):
        - The middle portion is the root
        - Score the triple and add to the lattice
    """

    def __init__(self, tokens: list[GlyphToken], config: Config):
        self.tokens = tokens
        self.config = config
        self.paths: list[SegmentPath] = []
        self._build()

    def _build(self):
        eva_full = tokens_to_eva(self.tokens)
        n = len(self.tokens)
        if n == 0:
            return

        # Enumerate all valid prefix lengths
        prefix_options = self._find_prefixes(eva_full)

        # For each prefix, enumerate suffix options and extract root
        for prefix_arc in prefix_options:
            remainder_start = prefix_arc.end if prefix_arc else 0
            remainder_eva = tokens_to_eva(self.tokens[remainder_start:])

            if not remainder_eva:
                continue

            suffix_options = self._find_suffixes(remainder_eva, remainder_start)

            for suffix_arc in suffix_options:
                suffix_start = suffix_arc.start if suffix_arc else n
                root_tokens = self.tokens[remainder_start:suffix_start]

                if not root_tokens:
                    continue

                root_eva = tokens_to_eva(root_tokens)
                root_weight = self._score_root(root_eva)

                root_arc = SegmentArc(
                    start=remainder_start,
                    end=suffix_start,
                    segment_type='root',
                    eva_form=root_eva,
                    latin_value='',  # to be decoded by HMM
                    weight=root_weight,
                    rule='root',
                )

                pfx_w = prefix_arc.weight if prefix_arc else 1.0
                sfx_w = suffix_arc.weight if suffix_arc else 1.0
                total = pfx_w * root_weight * sfx_w

                self.paths.append(SegmentPath(
                    prefix=prefix_arc if prefix_arc and prefix_arc.eva_form else None,
                    root=root_arc,
                    suffix=suffix_arc if suffix_arc and suffix_arc.eva_form else None,
                    total_weight=total,
                ))

        # Sort by total weight (best first)
        self.paths.sort(key=lambda p: -p.total_weight)

    def _find_prefixes(self, eva_full: str) -> list[SegmentArc | None]:
        """Find all valid prefix splits, including no-prefix option."""
        results: list[SegmentArc | None] = []

        # Option 0: no prefix (whole word is root)
        results.append(None)

        for rule in self.config.prefixes:
            if not eva_full.startswith(rule.eva):
                continue
            if len(eva_full) <= len(rule.eva):
                continue
            if rule.eva in self.config.not_prefixes:
                continue

            # Check blacklist for tier 1b
            if rule.blacklist and eva_full in rule.blacklist:
                continue

            # For tier 2, only allow if remainder starts with a confirmed root
            if rule.tier == '2':
                remainder = eva_full[len(rule.eva):]
                if not self._remainder_has_confirmed_root(remainder):
                    continue

            # Count tokens consumed by this prefix
            pfx_end = self._count_tokens_for(rule.eva)
            if pfx_end is None:
                continue

            results.append(SegmentArc(
                start=0,
                end=pfx_end,
                segment_type='prefix',
                eva_form=rule.eva,
                latin_value=rule.latin,
                weight=rule.probability,
                rule=f'pfx_t{rule.tier}_{rule.eva}',
            ))

        return results

    def _find_suffixes(self, remainder_eva: str, global_offset: int) -> list[SegmentArc | None]:
        """Find all valid suffix splits for the remainder."""
        results: list[SegmentArc | None] = []

        # Option 0: no suffix
        results.append(None)

        n = len(self.tokens)
        for sfx_eva, sfx_rule in self.config.suffixes.items():
            if not remainder_eva.endswith(sfx_eva):
                continue
            if len(remainder_eva) <= len(sfx_eva):
                continue

            # Count tokens consumed by this suffix (from end)
            sfx_token_count = self._count_tokens_for_suffix(sfx_eva, global_offset)
            if sfx_token_count is None:
                continue

            sfx_start = n - sfx_token_count

            results.append(SegmentArc(
                start=sfx_start,
                end=n,
                segment_type='suffix',
                eva_form=sfx_eva,
                latin_value=sfx_rule.latin,
                weight=0.8,  # default suffix weight
                rule=f'sfx_{sfx_rule.suffix_type}_{sfx_eva}',
            ))

        return results

    def _count_tokens_for(self, eva_str: str) -> int | None:
        """Count how many tokens from the start match this EVA string."""
        acc = ''
        for i, tok in enumerate(self.tokens):
            acc += tok.glyph
            if acc == eva_str:
                return i + 1
            if len(acc) > len(eva_str):
                return None
        return None

    def _count_tokens_for_suffix(self, sfx_eva: str, global_offset: int) -> int | None:
        """Count how many tokens from the end match this EVA suffix."""
        acc = ''
        for i in range(len(self.tokens) - 1, global_offset - 1, -1):
            acc = self.tokens[i].glyph + acc
            if acc == sfx_eva:
                return len(self.tokens) - i
            if len(acc) > len(sfx_eva):
                return None
        return None

    def _remainder_has_confirmed_root(self, remainder: str) -> bool:
        """Check if the remainder starts with a confirmed root."""
        for root_eva in self.config.confirmed_roots:
            if remainder.startswith(root_eva):
                return True
        return False

    def _score_root(self, root_eva: str) -> float:
        """Score a root segment. Confirmed roots get high weight."""
        if root_eva in self.config.confirmed_roots:
            return 2.0  # strong signal
        # Short roots are more likely to be valid
        if len(root_eva) <= 4:
            return 0.8
        if len(root_eva) <= 6:
            return 0.6
        return 0.4  # long roots are harder to decode

    def top_k(self, k: int = 20) -> list[SegmentPath]:
        """Return top-k segmentation paths by weight."""
        return self.paths[:k]
