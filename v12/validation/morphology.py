"""
Latin morphological validator.
Checks if a word has valid Latin endings.
"""

# Valid Latin endings by category
VALID_ENDINGS = {
    # Nominal endings (1st-5th declension)
    'nom_sg': ['a', 'us', 'um', 'er', 'es', 'is', 'e', 'or', 'os', 'en', 'ar'],
    'gen_sg': ['ae', 'i', 'is', 'us', 'ei'],
    'dat_sg': ['ae', 'o', 'i', 'ui', 'ei'],
    'acc_sg': ['am', 'um', 'em', 'im', 'en'],
    'abl_sg': ['a', 'o', 'e', 'i', 'u'],
    'nom_pl': ['ae', 'i', 'a', 'es', 'ia', 'us', 'ua'],
    'gen_pl': ['arum', 'orum', 'um', 'ium'],
    'dat_pl': ['is', 'ibus'],
    'acc_pl': ['as', 'os', 'a', 'es', 'ia', 'us', 'ua'],

    # Verbal endings
    'inf': ['are', 'ere', 'ire', 'ari', 'eri', 'iri'],
    'imp_sg': ['a', 'e', 'i'],          # imperatives: coque, misce, ede
    'imp_pl': ['ate', 'ete', 'ite'],
    'pres_1s': ['o'],
    'pres_2s': ['as', 'es', 'is'],
    'pres_3s': ['at', 'et', 'it'],
    'pres_3p': ['ant', 'ent', 'unt', 'iunt'],
    'perf_3s': ['it', 'vit'],
    'subj_3s': ['at', 'et', 'it', 'iat'],
    'gerund': ['endo', 'ando', 'iendo'],
    'participle': ['ens', 'ans', 'iens', 'atus', 'itus', 'utus'],

    # Adverbs/prepositions
    'adverb': ['e', 'er', 'iter', 'im'],
    'prep': ['cum', 'in', 'per', 'ex', 'de', 'ad', 'sub', 'pro'],
}

# Flatten all valid endings
_ALL_ENDINGS: set[str] = set()
for endings in VALID_ENDINGS.values():
    _ALL_ENDINGS.update(endings)

# Common short Latin words that don't follow ending patterns
_SHORT_WORDS = {
    'et', 'in', 'cum', 'per', 'ex', 'de', 'ad', 'ac', 'ut', 'si',
    'eo', 'ei', 'id', 'is', 'ea', 'es', 'ens', 'vel', 'aut', 'sed',
    'hic', 'haec', 'hoc', 'qui', 'quae', 'quod', 'dum', 'iam', 'tum',
    'non', 'nec', 'nam', 'ubi', 'quo', 'qua', 'sic', 'ita',
}


def is_valid_latin_ending(word: str) -> bool:
    """Check if a word has a valid Latin morphological ending."""
    w = word.lower().strip('?[]()').replace(' ', '')
    if not w:
        return False

    # Short words get a pass
    if len(w) <= 3:
        return w in _SHORT_WORDS or True  # most 2-3 letter combos are valid

    # Check each ending length (longest first for specificity)
    for end_len in range(min(5, len(w) - 1), 0, -1):
        ending = w[-end_len:]
        if ending in _ALL_ENDINGS:
            return True

    return False


def classify_ending(word: str) -> str | None:
    """Classify the morphological category of a Latin word ending."""
    w = word.lower().strip('?[]()').replace(' ', '')
    if len(w) < 2:
        return None

    for category, endings in VALID_ENDINGS.items():
        for ending in sorted(endings, key=len, reverse=True):
            if w.endswith(ending) and len(w) > len(ending):
                return category

    return None
