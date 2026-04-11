"""
Parse reference texts into universal recipe format.
Each recipe is tokenized into: VERB, INGR, DOSE, UNIT, QTY, PREP, ADJ, QUAL, TOOL, FORM, etc.
"""
import json, re
from collections import Counter

OUTDIR = 'datasets'

# ================================================================
# KNOWN PHARMACEUTICAL VOCABULARY (seed from Aurea + AN)
# ================================================================

VERBS_LATIN = {
    'recipe': 'take/prepare', 'misce': 'mix', 'tere': 'grind', 'terantur': 'grind(pass)',
    'coque': 'cook', 'coquatur': 'cook(pass)', 'cola': 'strain', 'coletur': 'strain(pass)',
    'solve': 'dissolve', 'funde': 'pour', 'pone': 'place', 'adde': 'add',
    'liquefac': 'melt', 'distilla': 'distill', 'incorpora': 'incorporate',
    'fiat': 'let-be-made', 'detur': 'let-be-given', 'datur': 'is-given',
    'dispensentur': 'dispense', 'conficiatur': 'prepare', 'bulliat': 'boil',
    'incidantur': 'cut', 'purgat': 'purge', 'mundificat': 'cleanse',
    'confortat': 'strengthen', 'valet': 'is-effective', 'operatur': 'works',
    'solvit': 'dissolves', 'provocat': 'provokes', 'sanat': 'heals',
    'infunde': 'infuse', 'commisce': 'mix-together', 'pulveriza': 'pulverize',
    'ablue': 'wash', 'decoque': 'decoct', 'exprime': 'press-out',
    'contere': 'grind-fine', 'contundantur': 'pound(pass)',
    'da': 'give', 'sumitur': 'is-taken', 'prenez': 'take(fr)',
    'faites': 'make(fr)', 'donez': 'give(fr)', 'metez': 'put(fr)',
    'lavez': 'wash(fr)', 'oigniez': 'anoint(fr)', 'cuire': 'cook(fr)',
}

UNITS = {
    'drachma': 'drachm(3.9g)', 'drachmam': 'drachm', 'drachmas': 'drachms',
    'uncia': 'ounce(31g)', 'unciam': 'ounce', 'uncias': 'ounces',
    'libra': 'pound(373g)', 'libram': 'pound', 'libras': 'pounds',
    'scrupulus': 'scruple(1.3g)', 'scrupulum': 'scruple',
    'granum': 'grain(0.065g)', 'grana': 'grains', 'grani': 'grain(gen)',
    'manipulus': 'handful', 'pugillus': 'pinch', 'cochlear': 'spoonful',
}

DOSE_MARKERS = {'ana', 'an', 'aa', 'quantum', 'sufficit', 'semis'}

PREPS = {
    'cum': 'with', 'in': 'in', 'per': 'through', 'de': 'of/from',
    'ad': 'for/to', 'contra': 'against', 'super': 'upon', 'sine': 'without',
    'ante': 'before', 'post': 'after', 'ubi': 'where', 'si': 'if',
    'ex': 'from', 'ab': 'from', 'pro': 'for', 'apud': 'at',
    'ovec': 'with(fr)', 'avec': 'with(fr)',
}

FORMS = {
    'electuarium': 'electuary', 'unguentum': 'ointment', 'emplastrum': 'plaster',
    'syrupus': 'syrup', 'pilulae': 'pills', 'trochisci': 'lozenges',
    'oleum': 'oil', 'pulvis': 'powder', 'confectio': 'confection',
    'potio': 'potion', 'decoctio': 'decoction', 'infusio': 'infusion',
    'cataplasma': 'poultice', 'collyrium': 'eye-wash', 'gargarisma': 'gargle',
    'suppositoria': 'suppository', 'ceratum': 'cerate', 'linimentum': 'liniment',
}

QUALITIES = {
    'calidum': 'hot', 'calida': 'hot(f)', 'calido': 'hot(abl)',
    'frigidum': 'cold', 'frigida': 'cold(f)', 'frigido': 'cold(abl)',
    'siccum': 'dry', 'sicca': 'dry(f)', 'sicco': 'dry(abl)',
    'humidum': 'wet', 'humida': 'wet(f)', 'humido': 'wet(abl)',
    'caliditatis': 'of-heat', 'frigiditatis': 'of-cold',
    'chauz': 'hot(fr)', 'chaude': 'hot(fr)', 'froide': 'cold(fr)',
    'froidure': 'coldness(fr)', 'seche': 'dry(fr)',
}

TOOLS = {
    'ignem': 'fire', 'ignis': 'fire', 'pannum': 'cloth', 'panno': 'cloth',
    'mortarium': 'mortar', 'pistillo': 'pestle', 'vas': 'vessel',
    'vase': 'vessel(abl)', 'aqua': 'water', 'vino': 'wine', 'vinum': 'wine',
    'melle': 'honey', 'mel': 'honey', 'oleo': 'oil', 'aceto': 'vinegar',
}

PARTS = {
    'radix': 'root', 'radicis': 'root(gen)', 'folia': 'leaves', 'folii': 'leaf(gen)',
    'semen': 'seed', 'seminis': 'seed(gen)', 'cortex': 'bark', 'corticis': 'bark(gen)',
    'succus': 'juice', 'succi': 'juice(gen)', 'flos': 'flower', 'floris': 'flower(gen)',
    'lignum': 'wood', 'ligni': 'wood(gen)', 'gummi': 'gum', 'resina': 'resin',
    'jus': 'juice(fr)', 'saet': 'seed(nl)',
}

# Stop words (grammar words that are NOT ingredients)
STOP_WORDS = {
    # Latin
    'non', 'sed', 'que', 'qui', 'quod', 'hoc', 'hec', 'illa', 'ille',
    'eius', 'ipsius', 'idem', 'tamen', 'enim', 'ergo', 'ita', 'sic',
    'tam', 'quam', 'quia', 'nam', 'nec', 'neque', 'atque', 'autem',
    'item', 'id', 'ea', 'eo', 'ei', 'ab', 'suo', 'sua', 'suum',
    'modum', 'modo', 'loco', 'parte', 'partem', 'omne', 'omnem', 'omni',
    'dicta', 'dictum', 'dictus', 'fit', 'facit', 'facta',
    'primo', 'secundo', 'tertio', 'quarto', 'gradu',
    'bene', 'parum', 'multum', 'satis', 'nimis',
    'maxime', 'proprie', 'eunti', 'dormitum',
    # Old French
    'la', 'le', 'les', 'un', 'une', 'des', 'du', 'au', 'en', 'de',
    'ce', 'ceste', 'cet', 'ces', 'li', 'el', 'al', 'del', 'nel',
    'qui', 'que', 'quant', 'quoi', 'ou', 'ne', 'pas', 'se', 'si',
    'par', 'por', 'sor', 'sus', 'desus', 'desoz', 'dedenz',
    'il', 'ele', 'on', 'lor', 'sa', 'son', 'ses', 'nos', 'vos',
    'est', 'es', 'sont', 'soit', 'estre', 'fu', 'fut',
    'bien', 'molt', 'tot', 'tote', 'toz', 'tel', 'tant',
    'puis', 'puet', 'doit', 'vaut', 'fait', 'mis', 'pris',
    'jor', 'nuit', 'fois', 'eure', 'tens', 'ausi', 'come',
    'car', 'mais', 'donc', 'lors', 'ains', 'onques',
    'feites', 'chose', 'choses', 'maniere', 'autre', 'autres',
    'bon', 'bonne', 'bons', 'mal', 'bon', 'mauvais',
    'grant', 'petit', 'gros', 'menu', 'fort',
    'home', 'feme', 'cors', 'leu', 'lieu', 'part',
    'dats', 'ende', 'die', 'dat', 'van', 'den', 'het', 'een',
    'ook', 'niet', 'voor', 'men', 'hem', 'haar', 'zijn',
    # Misc editorial
    'ms', 'ed', 'vol', 'pag', 'sup', 'fol', 'cap', 'lib',
}

# Build a combined lookup
ALL_VOCAB = {}
for word, gloss in VERBS_LATIN.items():
    ALL_VOCAB[word.lower()] = ('VERB', gloss)
for word, gloss in UNITS.items():
    ALL_VOCAB[word.lower()] = ('UNIT', gloss)
for word in DOSE_MARKERS:
    ALL_VOCAB[word.lower()] = ('DOSE', word)
for word, gloss in PREPS.items():
    ALL_VOCAB[word.lower()] = ('PREP', gloss)
for word, gloss in FORMS.items():
    ALL_VOCAB[word.lower()] = ('FORM', gloss)
for word, gloss in QUALITIES.items():
    ALL_VOCAB[word.lower()] = ('QUAL', gloss)
for word, gloss in TOOLS.items():
    ALL_VOCAB[word.lower()] = ('TOOL', gloss)
for word, gloss in PARTS.items():
    ALL_VOCAB[word.lower()] = ('PART', gloss)

def tokenize_recipe(text, recipe_id):
    """Tokenize a recipe text into typed tokens."""
    # Clean editorial marks
    text = re.sub(r'\^\)', '', text)
    text = re.sub(r'\d+\)', '', text)  # footnote refs
    text = re.sub(r'fol\.\s*\d+\s*[rv]\.?', '', text)  # folio refs
    text = re.sub(r'\([^)]*\)', '', text)  # parentheticals

    # Split into words
    raw_words = re.findall(r'[a-zA-Z]+|\.[\w]+\.', text)

    tokens = []
    all_verbs = set()
    all_ingr = set()
    all_doses = []

    for i, raw in enumerate(raw_words):
        word = raw.lower().strip('.')
        if not word or len(word) < 2:
            continue

        # Check known vocabulary
        if word in ALL_VOCAB:
            typ, gloss = ALL_VOCAB[word]
            tokens.append({'pos': len(tokens)+1, 'raw': raw, 'type': typ, 'normalized': word})
            if typ == 'VERB': all_verbs.add(word)
        # Check dosage numbers (.z.ii. = 2 drachms, .lb.ii. = 2 pounds)
        elif re.match(r'^[ivxlc]+$', word):
            tokens.append({'pos': len(tokens)+1, 'raw': raw, 'type': 'QTY', 'normalized': word})
        elif word in ('et', 'vel', 'sive', 'aut', 'ende', 'ou'):
            tokens.append({'pos': len(tokens)+1, 'raw': raw, 'type': 'CONJ', 'normalized': word})
        elif word in ('est', 'sunt', 'sit', 'es', 'sunt'):
            tokens.append({'pos': len(tokens)+1, 'raw': raw, 'type': 'COP', 'normalized': word})
        elif word in STOP_WORDS or len(word) < 3:
            tokens.append({'pos': len(tokens)+1, 'raw': raw, 'type': 'GRAM', 'normalized': word})
        else:
            # Default: assume INGREDIENT (most tokens in recipes are ingredients)
            tokens.append({'pos': len(tokens)+1, 'raw': raw, 'type': 'INGR', 'normalized': word})
            all_ingr.add(word)

    n_verbs = sum(1 for t in tokens if t['type'] == 'VERB')
    n_ingr = sum(1 for t in tokens if t['type'] == 'INGR')
    n_dose = sum(1 for t in tokens if t['type'] in ('DOSE', 'UNIT', 'QTY'))

    return tokens, {
        'n_tokens': len(tokens),
        'n_verbs': n_verbs,
        'n_ingredients': n_ingr,
        'n_dosages': n_dose,
        'verbs': sorted(all_verbs),
        'ingredients': sorted(all_ingr),
        'ratio_verb_ingr': '1:%.1f' % (n_ingr / max(n_verbs, 1)),
    }


# ================================================================
# PARSE AUREA ALEXANDRINA (our best crib)
# ================================================================
with open('BruteForce/Plants/AureaAlexandrina/aurea_alexandrina_crib_L1.txt', encoding='utf-8') as f:
    aurea_raw = f.read()

# Extract the clean recipe text
aurea_match = re.search(r'Recipe (.+?)detur in modum', aurea_raw, re.DOTALL)
if aurea_match:
    aurea_recipe_text = 'Recipe ' + aurea_match.group(1)
else:
    aurea_recipe_text = ''

aurea_tokens, aurea_summary = tokenize_recipe(aurea_recipe_text, 'AUREA_001')

aurea_entry = {
    'id': 'AUREA_001',
    'name': 'Aurea Alexandrina',
    'source': {
        'text': 'Antidotarium Nicolai',
        'edition': 'van den Berg 1917, pp.5-7',
        'file': 'BruteForce/Plants/AureaAlexandrina/aurea_alexandrina_crib_L1.txt',
        'language': 'latin',
    },
    'type': 'electuarium',
    'category': 'compound_recipe',
    'raw_text': aurea_recipe_text[:500],
    'tokens': aurea_tokens,
    'summary': aurea_summary,
}

with open('%s/13_recipes_AUREA.json' % OUTDIR, 'w', encoding='utf-8') as f:
    json.dump({
        'description': 'Aurea Alexandrina - Recipe #1 of Antidotarium Nicolai. PRIMARY CRIB for f103r.',
        'source': 'van den Berg 1917 edition, editio princeps 1471 (L1)',
        'note': '68 ingredients, largest recipe in AN. Used as crib for VMS folio f103r.',
        'count': 1,
        'entries': [aurea_entry]
    }, f, indent=2, ensure_ascii=False)
print('13_recipes_AUREA.json: 1 recipe, %d tokens, %d ingredients, %d verbs' % (
    aurea_summary['n_tokens'], aurea_summary['n_ingredients'], aurea_summary['n_verbs']))


# ================================================================
# PARSE CIRCA INSTANS (plant monographs)
# ================================================================
with open('BruteForce/Plants/Corpus_Pharmaceutique/sources_brutes/circa_instans_full_text.txt', encoding='utf-8') as f:
    ci_text = f.read()

# Split into entries by numbered sections
ci_entries = []
current_lines = []
current_num = None
for line in ci_text.split('\n'):
    line = line.strip()
    if not line:
        continue
    m = re.match(r'^(\d+)\.\s+(.+)', line)
    if m:
        if current_lines and current_num:
            ci_entries.append((current_num, ' '.join(current_lines)))
        current_num = m.group(1)
        current_lines = [m.group(2)]
    else:
        current_lines.append(line)
if current_lines and current_num:
    ci_entries.append((current_num, ' '.join(current_lines)))

ci_recipes = []
for num, text in ci_entries:
    if len(text) < 30:
        continue

    tokens, summary = tokenize_recipe(text, 'CI_%s' % num)

    # Try to extract plant name (usually first capitalized word or phrase)
    name_match = re.match(r'^([A-Z][A-Za-z\s]+?)(?:\s+est\s|\s+sunt\s|\s+es\b)', text)
    plant_name = name_match.group(1).strip() if name_match else text[:30].split('.')[0]

    # Try to extract Galenic qualities
    qual_match = re.search(r'(chau[dz]|froid|calid|frigid).{0,30}(se[cs]|humid|sicc)', text, re.I)
    has_galenic = qual_match is not None

    ci_recipes.append({
        'id': 'CI_%s' % num,
        'name': plant_name[:50],
        'source': {
            'text': 'Circa Instans (Le Livre des Simples Medecines)',
            'edition': 'Dorveaux 1913',
            'file': 'BruteForce/Plants/Corpus_Pharmaceutique/sources_brutes/circa_instans_full_text.txt',
            'entry_number': num,
            'language': 'old_french',
        },
        'type': 'simple_monograph',
        'category': 'plant_description',
        'has_galenic_formula': has_galenic,
        'raw_text': text[:300],
        'tokens': tokens[:100],  # Limit to avoid huge file
        'summary': summary,
    })

with open('%s/12_recipes_CI.json' % OUTDIR, 'w', encoding='utf-8') as f:
    json.dump({
        'description': 'Circa Instans plant monographs. Each entry = 1 plant with properties + usage recipes.',
        'source': 'Le Livre des Simples Medecines, ed. Dorveaux 1913 (Old French translation)',
        'original': 'Liber de simplici medicina dictus Circa instans, Matthaeus Platearius, ~1166 Salerno',
        'format': '[Plant name] est [quality1] et [quality2]. [Properties]. [Usage recipes].',
        'count': len(ci_recipes),
        'stats': {
            'with_galenic_formula': sum(1 for r in ci_recipes if r['has_galenic_formula']),
            'avg_tokens': sum(r['summary']['n_tokens'] for r in ci_recipes) // max(len(ci_recipes),1),
            'avg_ingredients': sum(r['summary']['n_ingredients'] for r in ci_recipes) // max(len(ci_recipes),1),
            'avg_verbs': sum(r['summary']['n_verbs'] for r in ci_recipes) // max(len(ci_recipes),1),
        },
        'entries': ci_recipes
    }, f, indent=2, ensure_ascii=False)
print('12_recipes_CI.json: %d entries, %d with Galenic formula' % (
    len(ci_recipes), sum(1 for r in ci_recipes if r['has_galenic_formula'])))


# ================================================================
# EXPORT MASTER VERB LIST (enriched from all parsing)
# ================================================================
# Collect all verbs found
all_found_verbs = Counter()
for r in ci_recipes:
    for v in r['summary']['verbs']:
        all_found_verbs[v] += 1
for v in aurea_summary['verbs']:
    all_found_verbs[v] += 1

print('\n=== ALL VERBS FOUND ===')
for v, c in all_found_verbs.most_common(30):
    known = 'KNOWN' if v in VERBS_LATIN else 'NEW'
    print('  %-20s %4dx  %s' % (v, c, known))

# Collect all ingredients found
all_found_ingr = Counter()
for r in ci_recipes:
    for ing in r['summary']['ingredients']:
        all_found_ingr[ing] += 1
for ing in aurea_summary['ingredients']:
    all_found_ingr[ing] += 1

print('\n=== TOP 30 INGREDIENTS ===')
for ing, c in all_found_ingr.most_common(30):
    print('  %-25s %4dx' % (ing, c))

# Write vocabulary enrichment file
vocab_enrich = {
    'description': 'All pharmaceutical vocabulary extracted from recipe parsing. Use to enrich master lists.',
    'verbs_found': {v: c for v, c in all_found_verbs.most_common()},
    'verbs_new': [v for v in all_found_verbs if v not in VERBS_LATIN],
    'ingredients_found': {i: c for i, c in all_found_ingr.most_common(200)},
    'total_unique_verbs': len(all_found_verbs),
    'total_unique_ingredients': len(all_found_ingr),
}
with open('%s/99_vocab_enrichment.json' % OUTDIR, 'w', encoding='utf-8') as f:
    json.dump(vocab_enrich, f, indent=2, ensure_ascii=False)

print('\n=== DONE ===')
print('12_recipes_CI.json: %d Circa Instans entries' % len(ci_recipes))
print('13_recipes_AUREA.json: 1 Aurea Alexandrina')
print('99_vocab_enrichment.json: %d verbs, %d ingredients' % (len(all_found_verbs), len(all_found_ingr)))
