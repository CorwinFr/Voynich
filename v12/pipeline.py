"""
Main pipeline orchestrator.
Wires S0→S6 together: tokenize → logogram → segment → HMM decode → score → output.
"""
from v12.config import Config
from v12.loaders.corpus import CorpusModel
from v12.loaders.dictionary import LatinDictionary
from v12.stages.logogram import resolve_logogram, DecodedWord
from v12.stages.tokenizer import tokenize, preprocess_triples
from v12.models.lattice import SegmentLattice
from v12.models.hmm import GlyphHMM
from v12.stages.hmm_decoder import decode_segmentation
from v12.stages.scorer import rank_candidates, ScoredCandidate


class VoynichPipeline:
    """
    Complete Voynich decoding pipeline.

    Usage:
        pipeline = VoynichPipeline()
        pipeline.load()
        result = pipeline.decode_word('daiin')
        results = pipeline.decode_line(['qoky', 'daiin', 'chor'])
    """

    # Pharma verbs — when the previous word is one of these,
    # the NEXT word gets ingredient-aware bonus scoring
    PHARMA_VERBS = {'coque', 'coques', 'coquas', 'coquere', 'coqui', 'coquo',
                    'tere', 'misce', 'cola', 'colo', 'collige', 'recipe',
                    'solve', 'distilla', 'fac', 'pone', 'adde'}

    # Antidotarium Nicolai ingredient list (for ingredient-position bonus)
    ANTIDOTARIUM = {
        'aloe', 'aloes', 'asarum', 'asari', 'apium', 'apii', 'apio',
        'ture', 'turis', 'thus', 'sal', 'salis', 'oleum', 'olei', 'oleo',
        'crocus', 'croci', 'piper', 'piperis', 'mel', 'mellis',
        'cera', 'cerae', 'mastix', 'masticis', 'nardus', 'nardi',
        'cassia', 'cassiae', 'cinnamomum', 'cinamomi',
        'myrrha', 'myrrhae', 'galanga', 'galangae',
        'costus', 'costi', 'cuminum', 'cumini',
        'hiera', 'cicura', 'rens', 'iecur',
        'succus', 'succi', 'succo', 'acetum', 'aceti', 'aceto',
        'vinum', 'vini', 'vino', 'lac', 'lactis', 'sapa', 'sapam',
        'rosa', 'rosae', 'viola', 'violae', 'enula', 'enulae',
        'feniculum', 'feniculi', 'absinthium', 'absinthii',
        'lilium', 'lilii', 'zingiber', 'zingiberis',
        'radix', 'radicis', 'semen', 'seminis',
        'folium', 'folii', 'folia', 'lignum', 'ligni',
        'pulvis', 'pulveris', 'libra', 'librae',
        'sulphur', 'sulfuris', 'alumen', 'aluminis',
    }

    # Agglutination prefixes: EVA prefix -> Latin equivalent
    # Discovered via deagglutinator analysis (2026-04-08).
    # The scribe glues prepositions/particles to the next word.
    # Only prefixes with >20% improvement AND remainder beats full.
    DEAGG_PREFIXES = [
        # (eva_prefix, latin_prefix, min_remainder_len)
        # Ordered longest-first to avoid partial matches
        ('da', 'in ', 3),    # 88% improvement — IN + A-word
        ('qo', 'cum ', 3),   # 34% improvement — CUM (with)
        ('ot', 't', 3),      # 27% improvement — T-trigger (already exists but this is fallback)
        ('ol', 'es ', 3),    # 47% improvement — ES/EX
        ('ok', 'qu', 3),     # 15% improvement — QU-
        ('y', 'in ', 3),     # 50% improvement — IN (preposition)
        ('d', 'in ', 3),     # 75% improvement — IN (variant)
        ('l', 'es ', 3),     # 37% improvement — ES/EX
        ('q', 'co', 3),      # 31% improvement — CO- (with)
        ('t', 'el ', 3),     # 28% improvement — EL (article?)
        ('r', 're', 3),      # 26% improvement — RE- (again)
        ('p', 'per ', 3),    # 17% improvement — PER (through)
        ('f', 'par ', 3),    # 18% improvement — PAR
    ]

    def __init__(self, config: Config | None = None):
        self.config = config or Config()
        self.corpus = CorpusModel()
        self.dictionary = LatinDictionary()
        self.hmm = GlyphHMM(self.config)
        self._loaded = False

    def load(self):
        """Load all data files (corpus, dictionary)."""
        print("Loading corpus...")
        self.corpus.load(self.config.corpus_path)
        print(f"  Corpus: {self.corpus.size} words")

        print("Loading dictionary...")
        self.dictionary.load_perseus(self.config.perseus_path)
        self.dictionary.add_vulgar_forms()
        print(f"  Perseus: {self.dictionary.size} forms, {self.dictionary.medical_size} medical (incl. vulgar pharma)")

        self._loaded = True
        print("Pipeline ready.")

    def decode_word(self, eva_word: str, prev_latin: str = '',
                    prev_eva: str = '', after_verb: bool = False) -> DecodedWord:
        """
        Decode a single EVA word through the full pipeline.

        S1: Logogram check
        S2: Segmentation lattice
        S3: HMM Viterbi on each segmentation's root
        S4: Score & rank candidates

        prev_latin: the decoded latin of the previous word in the line.
        prev_eva: the EVA of the previous word. Used together with prev_latin
                  for COLLISION detection (different EVA → same Latin = bad).
                  Same EVA → same Latin is a genuine repeat and is preserved.
        """
        word = eva_word.lower().strip()

        # S1: Logogram / exception / confirmed root
        logo = resolve_logogram(word, self.config)
        if logo:
            return logo

        # S0: Tokenize
        tokens = tokenize(word)
        tokens = preprocess_triples(tokens)

        if not tokens:
            return DecodedWord(
                eva=word, latin=f'[{word}]',
                confidence='OPAQUE', layer='ERROR', rule='empty_tokens',
            )

        # ==========================================================
        # S2 NEW: MONOLITHIC FIRST, SEGMENTATION AS FALLBACK
        # ==========================================================
        # The key insight: the segmentation was BREAKING real Latin
        # words into short fragments. E.g. qokeey -> "cum eo" (wrong)
        # instead of "coquo" (correct, a single conjugated verb).
        #
        # New priority:
        # 1. Try WHOLE-WORD K&A (monolithic) — produces long Latin words
        # 2. Try segmentation ONLY for short words or when monolithic fails
        # 3. The scorer picks the winner (long corpus-attested > short fragments)
        # ==========================================================

        from v12.stages.hmm_decoder import decode_root
        all_candidates: list[tuple[str, float, str]] = []

        # S2a: MONOLITHIC decode (whole word, no segmentation)
        # CHANGED: try for ALL words with 2+ chars (was 4+ tokens)
        # This is critical for -aiin words: okaiin=cura, not ok+aquam
        if len(word) >= 3:
            hmm_paths = decode_root(word, self.hmm, top_k=30)
            for vp in hmm_paths:
                if not vp.latin:
                    continue
                latin_clean = vp.latin.replace(' ', '')
                score = max(vp.log_prob * -100, 1)

                freq = self.corpus.freq(latin_clean)
                perseus = self.dictionary.is_valid(latin_clean)

                # BONUS: proportional to corpus frequency (log scale)
                # High-frequency words like cura(1540) get massive bonus
                if freq > 0:
                    import math
                    score += 2000 + math.log(freq + 1) * 1200
                if perseus:
                    score += 2000
                # Extra bonus for long valid words (they're more specific)
                if len(latin_clean) >= 5 and perseus:
                    score += 1500

                all_candidates.append((vp.latin, score, f'L3_MONO'))

        # S2b: SEGMENTATION decode (prefix+root+suffix)
        # Always try for words with 2+ tokens (covers d+aiin, qo+ky, etc.)
        if len(tokens) >= 2:
            lattice = SegmentLattice(tokens, self.config)
            paths = lattice.top_k(k=15)

            for path in paths:
                decoded = decode_segmentation(path, self.hmm, self.config, top_k=3)
                for latin, score, rule in decoded:
                    if latin:
                        layer_tag = 'L2_AGG' if path.prefix else 'L3_KA'
                        all_candidates.append((latin, score, f'{layer_tag}_{rule}'))

        # ==========================================================
        # S2c: DEAGGLUTINATION — strip prefixed prepositions
        # ==========================================================
        # The scribe glues prepositions to the next word:
        #   y+kaiin = IN + curam,  d+aiin = IN + aquam, etc.
        # Try each known prefix: strip it, decode remainder, add as candidate.
        # Only if remainder decodes with HIGH/CONFIRMED confidence.
        for peva, platin, min_rem in self.DEAGG_PREFIXES:
            if not word.startswith(peva):
                continue
            remainder = word[len(peva):]
            if len(remainder) < min_rem:
                continue
            # Avoid double-processing logograms (daiin already handled)
            if word in self.config.logograms:
                break

            # Decode remainder through the pipeline (recursion-safe: remainder won't re-deagg
            # because it's shorter and won't match the same prefix meaningfully)
            rem_logo = resolve_logogram(remainder, self.config)
            if rem_logo and rem_logo.confidence in ('CONFIRMED', 'HIGH'):
                combined = platin + rem_logo.latin
                all_candidates.append((combined, 4000, f'L3_DEAGG_{peva}={platin}+{rem_logo.latin}'))
                continue

            # Try HMM on remainder
            rem_paths = decode_root(remainder, self.hmm, top_k=5)
            for vp in rem_paths:
                if not vp.latin:
                    continue
                rem_clean = vp.latin.replace(' ', '')
                # Only accept if remainder is valid Latin
                rem_perseus = self.dictionary.is_valid(rem_clean)
                rem_corpus = self.corpus.freq(rem_clean)
                if rem_perseus or rem_corpus > 0:
                    combined = platin + vp.latin
                    # Score: proportional to remainder quality
                    score = 2000
                    if rem_corpus > 0:
                        score += 1000 + rem_corpus * 5
                    if rem_perseus:
                        score += 1500
                    all_candidates.append((combined, score, f'L3_DEAGG_{peva}={platin}+{vp.latin}'))
            # Only try best-matching prefix (longest first)
            break

        # S3b: ot→T trigger mechanism
        # When a word starts with 'ot', the 'o' disappears and 't' becomes
        # the Latin consonant T (not el/l/le). This is a proven mechanism:
        # otaiin = T + ure = TURE (incense), oteos = T + aloes? No, already logogram.
        # The T-trigger produces the Latin consonant that K&A 't' normally can't.
        if word.startswith('ot') and len(word) > 3:
            t_remainder = word[2:]  # strip 'ot'
            # Decode remainder with HMM
            from v12.stages.hmm_decoder import decode_root
            t_paths = decode_root(t_remainder, self.hmm, top_k=5)
            for vp in t_paths:
                if vp.latin:
                    t_latin = 't' + vp.latin  # prepend hard T
                    # Score proportional to corpus attestation
                    t_score = 3000
                    t_clean = t_latin.replace(' ', '')
                    t_freq = self.corpus.freq(t_clean)
                    if t_freq > 0:
                        t_score = 5000 + t_freq * 10
                    elif self.dictionary.is_valid(t_clean):
                        t_score = 4500
                    all_candidates.append((t_latin, t_score, f'L3_T_TRIGGER_{t_remainder}'))
            # Also try confirmed roots with T prefix
            if t_remainder in self.config.confirmed_roots:
                root = self.config.confirmed_roots[t_remainder]
                t_latin = 't' + root.latin
                all_candidates.append((t_latin, 5000, f'L3_T_TRIGGER_ROOT_{t_remainder}'))

        # S3c: ain→aiin normalization (scribal abbreviation)
        # Words containing 'ain' but not 'aiin' may be abbreviated forms
        if 'ain' in word and 'aiin' not in word:
            expanded = word.replace('ain', 'aiin', 1)
            exp_logo = resolve_logogram(expanded, self.config)
            if exp_logo:
                all_candidates.append((exp_logo.latin, 5000, f'ain_aiin_{exp_logo.rule}'))
            else:
                exp_tokens = tokenize(expanded)
                exp_tokens = preprocess_triples(exp_tokens)
                if exp_tokens:
                    exp_lattice = SegmentLattice(exp_tokens, self.config)
                    for path in exp_lattice.top_k(k=10):
                        decoded_exp = decode_segmentation(path, self.hmm, self.config, top_k=2)
                        for latin, score, rule in decoded_exp:
                            if latin:
                                layer_tag = 'L2_AGG' if path.prefix else 'L3_KA'
                                all_candidates.append((latin, score * 0.9, f'{layer_tag}_ain_norm_{rule}'))

        # ==========================================================
        # S2d: INGREDIENT-AWARE MODE
        # ==========================================================
        # When the previous word was a pharma verb (coque, tere, recipe...),
        # this word is likely an INGREDIENT. Explore more K&A paths
        # and give a massive bonus to any that match the Antidotarium.
        if len(tokens) >= 2:
            # Wider beam for ingredient search
            ingr_paths = decode_root(word, self.hmm, top_k=50)
            for vp in ingr_paths:
                if not vp.latin:
                    continue
                latin_clean = vp.latin.replace(' ', '').lower()
                # Check direct match against Antidotarium
                if latin_clean in self.ANTIDOTARIUM:
                    freq = self.corpus.freq(latin_clean)
                    # Score proportional to corpus attestation
                    # Must compete with standard K&A (typically 5000-9000)
                    score = 6000 + freq * 15
                    if freq > 10:
                        score += 3000  # well-attested ingredient
                    all_candidates.append((latin_clean, score,
                                          f'L3_INGREDIENT_{latin_clean}'))
                # Check anagram (same letters reordered)
                if len(latin_clean) >= 3:
                    sorted_chars = ''.join(sorted(latin_clean))
                    for ingr in self.ANTIDOTARIUM:
                        if len(ingr) == len(latin_clean) and ''.join(sorted(ingr)) == sorted_chars:
                            all_candidates.append((ingr, 12000,
                                                  f'L3_INGREDIENT_ANAGRAM_{latin_clean}->{ingr}'))

        # S4: Score and rank
        if not all_candidates:
            return DecodedWord(
                eva=word, latin=f'[{word}]',
                confidence='OPAQUE', layer='L3_KA', rule='no_candidates',
            )

        # Collision detection: only penalize if DIFFERENT EVA produces same Latin
        collision_latin = ''
        if prev_latin and prev_eva and word != prev_eva:
            collision_latin = prev_latin  # this is a collision target

        ranked = rank_candidates(all_candidates, self.corpus, self.dictionary,
                                  collision_latin=collision_latin)

        if not ranked:
            return DecodedWord(
                eva=word, latin=f'[{word}]',
                confidence='OPAQUE', layer='L3_KA', rule='ranking_failed',
            )

        best = ranked[0]
        alternatives = [(r.latin, r.rule) for r in ranked[1:4]]

        return DecodedWord(
            eva=word,
            latin=best.latin,
            confidence=best.confidence,
            layer=best.layer,
            rule=best.rule,
            alternatives=alternatives,
        )

    def decode_line(self, eva_words: list[str]) -> list[DecodedWord]:
        """Decode a line of EVA words with context-aware decoding."""
        results = []
        prev_latin = ''
        prev_eva = ''
        after_verb = False
        for w in eva_words:
            dw = self.decode_word(w, prev_latin=prev_latin, prev_eva=prev_eva,
                                 after_verb=after_verb)
            results.append(dw)
            # Check if this word is a pharma verb -> next word gets ingredient mode
            main_word = dw.latin.lower().split()[0] if dw.latin else ''
            after_verb = main_word in self.PHARMA_VERBS
            prev_latin = dw.latin
            prev_eva = w
        return results

    def decode_folio(self, folio_lines: dict[int, list[str]]) -> dict[int, list[DecodedWord]]:
        """Decode all lines of a folio."""
        results = {}
        for lnum in sorted(folio_lines.keys()):
            results[lnum] = self.decode_line(folio_lines[lnum])
        return results

    def stats(self, decoded: dict[int, list[DecodedWord]]) -> dict:
        """Compute statistics for a decoded folio."""
        total = 0
        counts = {'CONFIRMED': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'OPAQUE': 0}
        layers = {'L1_LOGO': 0, 'L2_AGG': 0, 'L2_ROOT_STANDALONE': 0,
                  'L3_KA': 0, 'EXCEPTION': 0, 'ERROR': 0}
        perseus_valid = 0
        medical = 0

        for lnum, words in decoded.items():
            for dw in words:
                total += 1
                counts[dw.confidence] = counts.get(dw.confidence, 0) + 1

                # Classify layer
                for key in layers:
                    if key in dw.layer:
                        layers[key] += 1
                        break

                # Check Perseus/medical
                for part in dw.latin.split():
                    if self.dictionary.is_valid(part):
                        perseus_valid += 1
                        if self.dictionary.is_medical(part):
                            medical += 1
                        break

        t = max(total, 1)
        return {
            'total': total,
            **{k: f"{v} ({v*100//t}%)" for k, v in counts.items()},
            'perseus_valid': f"{perseus_valid} ({perseus_valid*100//t}%)",
            'medical': f"{medical} ({medical*100//t}%)",
            'layers': layers,
        }
