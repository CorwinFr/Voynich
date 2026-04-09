"""
Latin → English/French translator for decoded text.
Simple dictionary-based lookup.
"""

EN_MAP = {
    # Prepositions/conjunctions
    'cum': 'with', 'in': 'in/into', 'et': 'and', 'per': 'through',
    'ex': 'out_of', 'de': 'of/from', 'ac': 'and_also', 'vel': 'or',
    'dum': 'while', 'seu': 'or_rather', 'contra': 'against',
    'usque': 'all_the_way', 'que': 'and(encl)',

    # Imperatives
    'coque': 'COOK!', 'coqui': 'to_cook', 'coquas': 'cook(subj)',
    'recipe': 'TAKE!', 'misce': 'MIX!',
    'ede': 'EAT!', 'seca': 'CUT!', 'da': 'GIVE!',
    'cies': 'STIR!', 'ciere': 'to_stir',
    'adure': 'BURN!', 'duce': 'LEAD!',

    # Nouns - substances
    'aquam': 'the_water', 'aqua': 'water', 'aquae': 'of_water',
    'curam': 'the_care', 'cura': 'care', 'curas': 'cares',
    'hiera': 'hiera[remedy]', 'aloes': 'aloe',
    'cicura': 'chicory', 'cibus': 'food', 'cibo': 'food(abl)',
    'cibum': 'food(acc)', 'dolor': 'pain', 'dolorem': 'pain(acc)',
    'aperiens': 'laxative', 'electuarium': 'electuary',

    # Body/medical
    'iecur': 'liver', 'rens': 'kidneys', 'ilia': 'flanks',
    'coda': 'tail',

    # Pronouns
    'eius': 'of_it/his', 'eo': 'by_it', 'ei': 'to_it',
    'eum': 'him(acc)', 'eam': 'her(acc)', 'eos': 'them(acc)',
    'est': 'is', 'es': 'you_are/eat',

    # Adjectives
    'dura': 'hard', 'dulcis': 'sweet', 'alia': 'other',

    # Pharmaceutical
    'libra': 'pound', 'equaliter': 'equally', 'cis': 'on_this_side',
    'coelas': 'of_the_heavens', 'coelis': 'in_the_heavens',
    'coquendo': 'by_cooking', 'coquam': 'I_cook(subj)',
    'coquant': 'let_them_cook', 'coquens': 'cooking',
    'deciere': 'shake_down', 'decie': 'ten_times',
    'colligens': 'gathering', 'cooperiens': 'covering',

    # Units
    'crux': '[mark]', '-que': 'and(encl)',

    # Function words
    'iure': 'by_right', 'aequ': 'equal',
    'alo': 'a_plant', 'ens': 'being',
    'aratura': 'preparation', 'ciboque': 'food_and',
    'cibolis': 'of_foods', 'cibos': 'foods(acc)',
    'inquam': 'I_say',
}


def translate(latin_word: str) -> str:
    """Translate a Latin word or phrase to English."""
    w = latin_word.lower().strip()

    # Exact match
    if w in EN_MAP:
        return EN_MAP[w]

    # Try compound match (longest first)
    for key in sorted(EN_MAP.keys(), key=len, reverse=True):
        if key in w:
            return EN_MAP[key]

    return f'<{latin_word}>'
