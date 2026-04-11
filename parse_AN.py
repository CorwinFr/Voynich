"""
Parse Antidotarium Nicolai recipes from the cleaned van den Berg text.
The text mixes Latin recipes with Dutch translation and critical apparatus.
Strategy: extract Latin blocks between "Recipe" keywords.
"""
import json, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load the clean AN text
with open('data/raw_corpus_9a/cleaned/clean_antidotarium_nicolai_1917.txt', encoding='utf-8') as f:
    raw = f.read()

# Also load the raw van den Berg for cross-reference
with open('BruteForce/Plants/Corpus_Pharmaceutique/sources_brutes/van_den_berg_full_text.txt', encoding='utf-8') as f:
    vdb = f.read()

# Load verbs and ingredients for tokenization
with open('datasets/R01_verbs.json', encoding='utf-8') as f:
    verbs_db = json.load(f)
with open('datasets/R02_ingredients.json', encoding='utf-8') as f:
    ingr_db = json.load(f)

# Build lookup tables
verb_forms = {}  # form -> ref_id
for key, v in verbs_db.items():
    if key == '_meta': continue
    for lang_forms in v.get('forms', {}).values():
        if isinstance(lang_forms, list):
            for form in lang_forms:
                verb_forms[form.lower()] = key

ingr_forms = {}  # form -> ref_id
for key, v in ingr_db.items():
    if key == '_meta': continue
    for lang_forms in v.get('forms', {}).values():
        if isinstance(lang_forms, list):
            for form in lang_forms:
                ingr_forms[form.lower()] = key

# Known dose/unit/prep patterns
DOSE_WORDS = {'ana', 'an', 'aa'}
UNIT_PATTERNS = re.compile(r'\.z\.|\.lb\.|\.O\.|\.S\.|drachm|unci|libr|scrupul|grana')
QTY_PATTERN = re.compile(r'^[ivxlc]+$|^\d+$')
PREPS = {'cum', 'in', 'per', 'de', 'ad', 'contra', 'super', 'sine', 'ante', 'post', 'sub', 'ubi', 'ex', 'ab', 'pro', 'supra'}
CONJS = {'et', 'vel', 'sive', 'aut', 'seu', 'nec', 'neque', 'atque'}
COPS = {'est', 'sunt', 'sit', 'fuerit'}
GRAM_WORDS = {'non', 'sed', 'que', 'qui', 'quod', 'hoc', 'hec', 'tamen', 'enim',
              'eius', 'eo', 'ea', 'suo', 'sua', 'omne', 'omnem', 'omni',
              'modo', 'modum', 'dicta', 'dictum', 'dictus', 'bene', 'satis',
              'primo', 'secundo', 'tertio', 'quarto', 'gradu',
              'maxime', 'proprie', 'precipue', 'mirabiliter',
              'a', 'e', 'o', 'u', 'ii', 'ij', 'iij', 'iiii', 'viii'}
FORM_WORDS = {'electuarium', 'electuarii', 'unguentum', 'unguenti', 'emplastrum',
              'syrupus', 'syrupi', 'pilulae', 'pilularum', 'trochisci', 'trochiscorum',
              'pulvis', 'pulveris', 'oleum', 'olei', 'confectio', 'confectionis',
              'potio', 'potionis', 'ceratum', 'cerati', 'collyrium', 'collyrii'}

def tokenize_word(word):
    """Classify a single word into token type."""
    w = word.lower().strip('.,;:)(')
    if not w or len(w) < 2:
        return None

    if w in verb_forms:
        return {'raw': word, 'type': 'VERB', 'ref': verb_forms[w], 'normalized': w}
    if w in DOSE_WORDS:
        return {'raw': word, 'type': 'DOSE', 'ref': 'D_ana', 'normalized': w}
    if w in PREPS:
        return {'raw': word, 'type': 'PREP', 'normalized': w}
    if w in CONJS:
        return {'raw': word, 'type': 'CONJ', 'normalized': w}
    if w in COPS:
        return {'raw': word, 'type': 'COP', 'normalized': w}
    if w in FORM_WORDS:
        return {'raw': word, 'type': 'FORM', 'normalized': w}
    if w in GRAM_WORDS:
        return {'raw': word, 'type': 'GRAM', 'normalized': w}
    if UNIT_PATTERNS.search(w):
        return {'raw': word, 'type': 'UNIT', 'normalized': w}
    if QTY_PATTERN.match(w):
        return {'raw': word, 'type': 'QTY', 'normalized': w}

    # Check ingredients
    if w in ingr_forms:
        return {'raw': word, 'type': 'INGR', 'ref': ingr_forms[w], 'normalized': w}

    # Genitive/accusative forms: try stripping Latin endings
    for ending in ['ae', 'arum', 'orum', 'ium', 'um', 'am', 'is', 'i', 'o', 'em']:
        stem = w[:-len(ending)] if w.endswith(ending) and len(w) > len(ending) + 2 else None
        if stem:
            for check in [stem, stem + 'a', stem + 'us', stem + 'um', stem + 'is']:
                if check in ingr_forms:
                    return {'raw': word, 'type': 'INGR', 'ref': ingr_forms[check], 'normalized': check}

    # Dutch/editorial words to skip
    if any(c in w for c in ['\\', ';', '«', '»', '—']) or w.startswith('fol'):
        return None

    # Default: unknown ingredient candidate
    if len(w) >= 3 and w.isalpha():
        return {'raw': word, 'type': 'INGR', 'normalized': w}

    return None


def extract_latin_recipes(text):
    """Extract Latin recipe blocks from the mixed text."""
    recipes = []

    # Strategy: find all "Recipe" occurrences in text that are followed by ingredient lists
    # Split text into paragraphs
    paragraphs = text.split('\n\n')

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # Find Recipe keyword
        recipe_matches = list(re.finditer(r'\bRecipe\b', para, re.I))
        if not recipe_matches:
            continue

        for match in recipe_matches:
            # Extract from Recipe to the next sentence boundary or end
            start = match.start()
            # Find recipe end: next Dutch block, or next numbered entry, or end of paragraph
            rest = para[start:]

            # Remove Dutch text (characterized by specific patterns)
            # Dutch has: «, ;, ende, elcs, dats, saelt, gnouch, etc.
            # Keep only Latin-looking text
            latin_words = []
            for word in rest.split():
                # Skip clearly Dutch words
                if any(dutch in word.lower() for dutch in ['ende', 'elcs', 'dats', 'saelt', 'gnouch',
                    'geve', 'grot', 'wine', 'mede', 'sode', 'comt', 'iege', 'saet',
                    'nuchtren', 'houde', 'smorg', 'middage']):
                    continue
                # Skip editorial markers
                if re.match(r'^\d+\)', word) or re.match(r'^fol\.', word, re.I):
                    continue
                if '«' in word or '»' in word or ';' in word:
                    continue
                latin_words.append(word)

            latin_text = ' '.join(latin_words)

            # Clean up
            latin_text = re.sub(r'\([^)]*\)', '', latin_text)  # remove parenthetical notes
            latin_text = re.sub(r'\s+', ' ', latin_text).strip()

            if len(latin_text) > 30:  # Minimum viable recipe
                recipes.append(latin_text)

    return recipes


# Extract recipes
raw_recipes = extract_latin_recipes(raw)

# Also extract from van den Berg (may catch more)
vdb_recipes = extract_latin_recipes(vdb)

print('Recipes from clean AN: %d' % len(raw_recipes))
print('Recipes from van den Berg: %d' % len(vdb_recipes))

# Combine and deduplicate (by first 50 chars)
all_recipes = {}
for r in raw_recipes + vdb_recipes:
    key = r[:50].lower()
    if key not in all_recipes or len(r) > len(all_recipes[key]):
        all_recipes[key] = r

recipes = list(all_recipes.values())
print('Combined unique: %d' % len(recipes))

# Try to extract recipe names from context
# AN recipes have names like "Aurea Alexandrina", "Dialacca", "Diaciminum"
name_pattern = re.compile(r'([A-Z][a-z]+(?:\s+[a-z]+)?)\s+(?:valet|dicitur|dictum|utilis|optimum)', re.I)

# Tokenize each recipe
entries = []
all_verbs_found = set()
all_ingr_found = set()

for i, raw_text in enumerate(recipes):
    tokens = []
    words = raw_text.split()

    for word in words:
        tok = tokenize_word(word)
        if tok:
            tok['pos'] = len(tokens) + 1
            tokens.append(tok)
            if tok['type'] == 'VERB':
                all_verbs_found.add(tok['normalized'])
            elif tok['type'] == 'INGR':
                all_ingr_found.add(tok['normalized'])

    if len(tokens) < 3:
        continue

    # Extract name if possible
    name_match = name_pattern.search(raw_text[:200])
    recipe_name = name_match.group(1) if name_match else 'AN_%03d' % (i + 1)

    # Build summary
    ingr_list = [t.get('ref', t['normalized']) for t in tokens if t['type'] == 'INGR']
    verb_list = [t.get('ref', t['normalized']) for t in tokens if t['type'] == 'VERB']
    n_ingr = len(ingr_list)
    n_verbs = len(verb_list)
    pattern = ' '.join(t['type'] for t in tokens)

    entries.append({
        'id': 'AN_%03d' % (i + 1),
        'name': recipe_name,
        'raw_text': raw_text[:500],
        'tokens': tokens,
        'pattern': pattern,
        'summary': {
            'n_tokens': len(tokens),
            'n_ingredients': n_ingr,
            'n_verbs': n_verbs,
            'ingredients': list(set(ingr_list))[:30],
            'verbs': list(set(verb_list)),
            'ratio_verb_ingr': '1:%.1f' % (n_ingr / max(n_verbs, 1)),
        }
    })

# Write output
output = {
    '_meta': {
        'source_text': 'Antidotarium Nicolai',
        'edition': 'van den Berg 1917 (editio princeps 1471)',
        'files': [
            'data/raw_corpus_9a/cleaned/clean_antidotarium_nicolai_1917.txt',
            'BruteForce/Plants/Corpus_Pharmaceutique/sources_brutes/van_den_berg_full_text.txt'
        ],
        'language': 'latin (mixed with Dutch critical apparatus)',
        'period': '~1150, Salerno',
        'count': len(entries),
        'note': 'Parsed from mixed Latin/Dutch text. Some recipes may be incomplete or merged.',
    },
    'entries': entries
}

with open('datasets/S01_AN.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print('\nS01_AN.json: %d recipes' % len(entries))
print('Unique verbs found: %d' % len(all_verbs_found))
print('Unique ingredients found: %d' % len(all_ingr_found))
print('\nTop patterns:')
from collections import Counter
patterns = Counter()
for e in entries:
    # Simplified pattern: just token types in order
    simplified = re.sub(r'(INGR )+', 'INGR+ ', e['pattern'])
    patterns[simplified] += 1
for p, c in patterns.most_common(10):
    print('  [%dx] %s' % (c, p[:80]))

# Show sample
if entries:
    print('\nSample recipe:')
    e = entries[0]
    print('  Name: %s' % e['name'])
    print('  Tokens: %d (ingr=%d, verbs=%d)' % (e['summary']['n_tokens'], e['summary']['n_ingredients'], e['summary']['n_verbs']))
    print('  Ratio: %s' % e['summary']['ratio_verb_ingr'])
    print('  Pattern: %s' % e['pattern'][:100])
