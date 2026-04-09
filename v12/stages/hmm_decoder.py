"""
S3: HMM Viterbi decoder stage.
For each segmentation path's ROOT, run HMM to produce Latin candidates.
"""
from v12.config import Config
from v12.stages.tokenizer import GlyphToken, tokenize, preprocess_triples
from v12.models.hmm import GlyphHMM, ViterbiPath
from v12.models.lattice import SegmentPath


def decode_root(root_eva: str, hmm: GlyphHMM, top_k: int = 5) -> list[ViterbiPath]:
    """Decode a root EVA string using the HMM Viterbi algorithm."""
    tokens = tokenize(root_eva)
    tokens = preprocess_triples(tokens)
    if not tokens:
        return []
    return hmm.viterbi(tokens, top_k=top_k)


def decode_segmentation(path: SegmentPath, hmm: GlyphHMM, config: Config,
                         top_k: int = 5) -> list[tuple[str, float, str]]:
    """
    Decode a segmentation path: prefix_latin + HMM(root) + suffix_latin.

    Returns list of (assembled_latin, score, rule_description).
    """
    results = []

    # Check if root is a confirmed root first
    root_eva = path.root_eva
    if root_eva in config.confirmed_roots:
        confirmed = config.confirmed_roots[root_eva]
        latin = _assemble(path.prefix_latin, confirmed.latin, path.suffix_latin)
        score = confirmed.score * path.total_weight
        rule = f'confirmed_root_{root_eva}'
        results.append((latin, score, rule))

    # Also try HMM decode on the root
    hmm_paths = decode_root(root_eva, hmm, top_k=top_k)
    for vp in hmm_paths:
        if not vp.latin:
            continue
        latin = _assemble(path.prefix_latin, vp.latin, path.suffix_latin)
        score = math.exp(vp.log_prob) * path.total_weight * 1000  # scale for comparison
        rule = f'hmm_{"|".join(vp.states[:3])}'
        results.append((latin, score, rule))

    return results


def _assemble(prefix: str, root: str, suffix: str) -> str:
    """Assemble prefix + root + suffix into Latin text."""
    parts = []
    if prefix and prefix != '?':
        parts.append(prefix)
    if root:
        # Apply suffix to root
        if suffix:
            # Handle space-separated suffixes like " et"
            if suffix.startswith(' '):
                parts.append(root + suffix.lstrip())
            else:
                parts.append(root + suffix)
        else:
            parts.append(root)
    return ' '.join(parts)


import math  # noqa: E402
