"""
Build structured reference datasets for Voynich manuscript analysis.
Each dataset is self-contained with source references and confidence levels.
"""
import json, csv, re, math
from collections import Counter, defaultdict

OUTDIR = 'datasets'

# ================================================================
# PARSE VMS TRANSCRIPTION
# ================================================================
with open('data/transcriptions/ZL.txt', encoding='utf-8') as f:
    zl_raw = f.read()

word_freq = Counter()
word_sections = defaultdict(Counter)
word_folios = defaultdict(set)

SUFFIXES = ['aiin','ain','eedy','edy','eey','ey','dy','ol','or','ar','al','am','om','air']

def get_section(fnum, rv):
    if fnum <= 56: return 'herbal_A'
    elif fnum == 57 and rv == 'v': return 'volvelle'
    elif 58 <= fnum <= 67: return 'astro'
    elif 68 <= fnum <= 73: return 'cosmo'
    elif 75 <= fnum <= 84: return 'balnea'
    elif 85 <= fnum <= 102: return 'herbal_B'
    elif 103 <= fnum <= 116: return 'pharma'
    return 'other'

def clean_line(line):
    text = re.sub(r'<[^>]*>', '', line.strip())
    text = re.sub(r'<!.*?>', '', text)
    text = text.replace(',', '.').replace('?', '')
    text = re.sub(r'\[[^\]]*:([^\]]*)\]', r'\1', text)
    return [w for w in re.findall(r'[a-z]+', text) if w]

def get_suffix(word):
    for s in SUFFIXES:
        if word.endswith(s) and len(word) > len(s):
            return s
    return None

# Parse all lines
all_parsed = []  # (fnum, rv, sub, lnum, sec, words)
for line in zl_raw.split('\n'):
    m = re.match(r'<f(\d+)([rv])(\d?)\.(\d+)', line.strip())
    if not m: continue
    fnum = int(m.group(1))
    rv = m.group(2)
    sub = m.group(3)
    lnum = int(m.group(4))
    sec = get_section(fnum, rv)
    folio = 'f%s%s%s' % (fnum, rv, sub)
    words = clean_line(line)
    all_parsed.append((fnum, rv, sub, lnum, sec, folio, words))
    for w in words:
        word_freq[w] += 1
        word_sections[w][sec] += 1
        word_folios[w].add(folio)

print('Parsed %d unique words, %d total tokens' % (len(word_freq), sum(word_freq.values())))

# ================================================================
# DATASET 1: LOGOGRAMS
# ================================================================
logograms = [
    {'eva':'o','latin':'ac','gloss':'and/also','pos':'conjunction','confidence':'CONFIRMED','source':'bifolio_bH1_f57v_f66r'},
    {'eva':'l','latin':'se','gloss':'self/itself','pos':'pronoun','confidence':'CONFIRMED','source':'bifolio_bH1'},
    {'eva':'d','latin':'de','gloss':'of/from','pos':'preposition','confidence':'CONFIRMED','source':'bifolio_bH1'},
    {'eva':'r','latin':'recipe','gloss':'take/prepare','pos':'verb_imperative','confidence':'CONFIRMED','source':'bifolio_bH1'},
    {'eva':'v','latin':'vel','gloss':'or','pos':'conjunction','confidence':'CONFIRMED','source':'bifolio_bH1'},
    {'eva':'x','latin':'crux','gloss':'cross/mark','pos':'noun_marker','confidence':'CONFIRMED','source':'bifolio_bH1'},
    {'eva':'k','latin':'cum','gloss':'with','pos':'preposition','confidence':'CONFIRMED','source':'bifolio_bH1'},
    {'eva':'m','latin':'misce','gloss':'mix','pos':'verb_imperative','confidence':'CONFIRMED','source':'bifolio_bH1'},
    {'eva':'f','latin':'per','gloss':'through/by','pos':'preposition','confidence':'CONFIRMED','source':'bifolio_bH1'},
    {'eva':'t','latin':'el','gloss':'the(?)','pos':'article_uncertain','confidence':'CONFIRMED','source':'bifolio_bH1'},
    {'eva':'y','latin':'in','gloss':'in/into','pos':'preposition','confidence':'CONFIRMED','source':'bifolio_bH1'},
    {'eva':'c','latin':'cum','gloss':'with','pos':'preposition','confidence':'CONFIRMED','source':'bifolio_bH1'},
    {'eva':'s','latin':'est','gloss':'is','pos':'copula','confidence':'CONFIRMED','source':'bifolio_bH1'},
    {'eva':'sh','latin':'ci','gloss':'here','pos':'adverb','confidence':'CONFIRMED','source':'bifolio_bH1'},
    {'eva':'p','latin':'usque','gloss':'until','pos':'preposition','confidence':'PROBABLE','source':'bifolio_bH1'},
    {'eva':'air','latin':'aier','gloss':'air','pos':'noun','confidence':'CONFIRMED','source':'f66r_cross_validation'},
]
for lg in logograms:
    lg['vms_freq'] = word_freq.get(lg['eva'], 0)

with open('%s/01_logograms.json' % OUTDIR, 'w', encoding='utf-8') as f:
    json.dump({
        'description': 'Single-glyph logograms confirmed by bifolio bH1 (f57v/f66r) cross-validation. 9/9 glyphs match, 0 exceptions.',
        'proof_file': 'v12/analysis/BIFOLIO_bH1_SYNTHESE_COMPLETE.md',
        'confidence_scale': {'CONFIRMED': 'bifolio cross-validated, no exceptions', 'PROBABLE': 'consistent evidence but not fully proven'},
        'count': len(logograms),
        'entries': logograms
    }, f, indent=2, ensure_ascii=False)
print('01_logograms.json: %d entries' % len(logograms))

# ================================================================
# DATASET 2: VERBS
# ================================================================
verbs = [
    {'eva_form':'r','latin':'recipe','gloss':'take/prepare','detection':'logogram','confidence':'CONFIRMED','source':'bifolio_bH1','vms_freq':word_freq.get('r',0),'reference':'Standard pharma abbreviation Rp. Universal in AN/CI/Grabadin'},
    {'eva_form':'m','latin':'misce','gloss':'mix/blend','detection':'logogram','confidence':'CONFIRMED','source':'bifolio_bH1','vms_freq':word_freq.get('m',0),'reference':'Standard pharma M. In AN 72/137 recipes'},
    {'eva_form':'?','latin':'coque','gloss':'cook/boil','detection':'ka_decode','confidence':'PROBABLE','source':'ka_pipeline_v12','vms_freq_est':50,'reference':'AN: 45/137 recipes. CI: in most plant entries. Grabadin: core verb'},
    {'eva_form':'?','latin':'tere','gloss':'grind/crush','detection':'ka_decode','confidence':'PROBABLE','source':'ka_pipeline_v12','vms_freq_est':30,'reference':'AN: 89/137 recipes (terantur). CI: preparation step'},
    {'eva_form':'?','latin':'cola','gloss':'strain/filter','detection':'ka_decode','confidence':'PROBABLE','source':'ka_pipeline_v12','vms_freq_est':20,'reference':'AN: 31/137. Grabadin: per pannum'},
    {'eva_form':'?','latin':'solve','gloss':'dissolve','detection':'ka_decode','confidence':'SPECULATIVE','source':'ka_pipeline_v12','vms_freq_est':15,'reference':'AN: solve in aqua/vino'},
    {'eva_form':'?','latin':'funde','gloss':'pour','detection':'ka_decode','confidence':'SPECULATIVE','source':'ka_pipeline_v12','vms_freq_est':10,'reference':'Grabadin: funde in vas'},
    {'eva_form':'?','latin':'pone','gloss':'place/put','detection':'ka_decode','confidence':'SPECULATIVE','source':'ka_pipeline_v12','vms_freq_est':10,'reference':'AN: pone in vase'},
    {'eva_form':'?','latin':'liquefac','gloss':'melt/liquefy','detection':'NOT_FOUND','confidence':'REFERENCE','source':'AN/Grabadin expected verb','vms_freq_est':0,'reference':'Grabadin: liquefac super ignem lentum'},
    {'eva_form':'?','latin':'distilla','gloss':'distill','detection':'NOT_FOUND','confidence':'REFERENCE','source':'AN/Grabadin expected verb','vms_freq_est':0,'reference':'Late medieval technique'},
    {'eva_form':'?','latin':'adde','gloss':'add','detection':'NOT_FOUND','confidence':'REFERENCE','source':'AN expected verb','vms_freq_est':0,'reference':'AN: adde X ad Y'},
    {'eva_form':'?','latin':'incorpora','gloss':'incorporate','detection':'NOT_FOUND','confidence':'REFERENCE','source':'AN expected verb','vms_freq_est':0,'reference':'AN: incorpora cum melle'},
    {'eva_form':'?','latin':'bullia','gloss':'boil','detection':'NOT_FOUND','confidence':'REFERENCE','source':'AN expected verb','vms_freq_est':0,'reference':'AN: fac bullire'},
    {'eva_form':'?','latin':'ablue','gloss':'wash','detection':'NOT_FOUND','confidence':'REFERENCE','source':'CI expected verb','vms_freq_est':0,'reference':'CI: ablue cum aqua'},
]

with open('%s/02_verbs.json' % OUTDIR, 'w', encoding='utf-8') as f:
    json.dump({
        'description': 'Pharmaceutical verbs: confirmed (logogram) + decoded (K&A) + expected (reference texts, not yet found in VMS)',
        'reference_texts': {
            'AN': 'Antidotarium Nicolai (van den Berg 1917) - data/raw_corpus_9a/antidotarium_nicolai_1917.txt',
            'CI': 'Circa Instans (Platearius/Dorveaux 1913) - BruteForce/Plants/Corpus_Pharmaceutique/sources_brutes/circa_instans_full_text.txt',
            'Grabadin': 'Liber Servitoris (Al-Zahrawi, Latin translation)'
        },
        'confidence_scale': {
            'CONFIRMED': 'logogram table, bifolio cross-validated',
            'PROBABLE': 'K&A decode + matches corpus verb',
            'SPECULATIVE': 'K&A decode, weak corpus evidence',
            'REFERENCE': 'Expected from reference texts, NOT YET found in VMS'
        },
        'count': len(verbs),
        'entries': verbs
    }, f, indent=2, ensure_ascii=False)
print('02_verbs.json: %d entries' % len(verbs))

# ================================================================
# DATASET 3: SUFFIXES
# ================================================================
suffix_entries = []
role_map = {
    'or': 'OPENER - 22% at line start, 64% herbal, subject/descriptor',
    'ol': 'DESCRIPTOR - herbal dominant, property/quality',
    'eey': 'MODIFIER - pharma+herbal mix, degree/detail',
    'ey': 'LIGHT_MODIFIER - mixed distribution',
    'eedy': 'PROCEDURAL_EXTENDED - balnea+pharma 84%',
    'aiin': 'CONNECTOR - middle position, links syntagms',
    'edy': 'PROCEDURAL_ITEM - balnea+pharma 78%, list element',
    'ain': 'SHORT_CONNECTOR - pharma+balnea 72%',
    'ar': 'PURPOSE/RESULT - mixed distribution',
    'dy': 'INSTRUCTION_MARKER - functional roots cho/sho concentrate here',
    'al': 'MEASURE/LOCATION - pharma+balnea 52%',
    'am': 'SENTENCE_TERMINATOR - 71% at line end, proven',
    'om': 'PARAGRAPH_SEPARATOR - 56% at line end, herbal 72%',
    'air': 'RARE_MODIFIER - pharma 43%',
}

for sfx in SUFFIXES:
    positions = []
    sections = Counter()
    at_end = at_start = total = 0
    roots = Counter()

    for fnum, rv, sub, lnum, sec, folio, words in all_parsed:
        for i, w in enumerate(words):
            if w.endswith(sfx) and len(w) > len(sfx):
                total += 1
                roots[w[:-len(sfx)]] += 1
                sections[sec] += 1
                if len(words) > 1:
                    positions.append(i / (len(words) - 1))
                if i == 0: at_start += 1
                if i == len(words) - 1: at_end += 1

    if total < 10: continue
    avg_pos = sum(positions) / len(positions) if positions else 0
    herbal_pct = round((sections.get('herbal_A', 0) + sections.get('herbal_B', 0)) * 100 / total, 1)
    balnea_pct = round(sections.get('balnea', 0) * 100 / total, 1)
    pharma_pct = round(sections.get('pharma', 0) * 100 / total, 1)

    suffix_entries.append({
        'suffix': sfx,
        'total_count': total,
        'avg_line_position': round(avg_pos, 3),
        'pct_line_start': round(at_start * 100 / total, 1),
        'pct_line_end': round(at_end * 100 / total, 1),
        'pct_herbal': herbal_pct,
        'pct_balnea': balnea_pct,
        'pct_pharma': pharma_pct,
        'n_unique_roots': len(roots),
        'top5_words': ['%s%s(%d)' % (r, sfx, c) for r, c in roots.most_common(5)],
        'hypothesized_role': role_map.get(sfx, ''),
    })

with open('%s/03_suffixes.json' % OUTDIR, 'w', encoding='utf-8') as f:
    json.dump({
        'description': '14 EVA suffixes forming a flexional grammar system. Same roots take all suffixes.',
        'key_findings': [
            '-am is SENTENCE TERMINATOR (71% at line end) - PROVEN',
            '-or is OPENER (22% at line start) - PROVEN',
            '-ol/-or dominant in HERBAL (descriptive register)',
            '-edy/-eedy dominant in BALNEA/PHARMA (procedural register)',
            'Anti-correlation: pages with chol.daiin (31 folios) have -edy ratio 0.17',
            'daiin bridges 80% DIFFERENT suffix types => not simply "et"',
        ],
        'source_analysis': 'docs/SESSION7_SUFFIX_PARADIGMS.md',
        'confidence': 'STATISTICAL_FACT for distributions; HYPOTHESIS for role interpretations',
        'count': len(suffix_entries),
        'entries': suffix_entries
    }, f, indent=2, ensure_ascii=False)
print('03_suffixes.json: %d entries' % len(suffix_entries))

# ================================================================
# DATASET 4: ROOT PARADIGM TABLE
# ================================================================
root_sfx = defaultdict(Counter)
for fnum, rv, sub, lnum, sec, folio, words in all_parsed:
    for w in words:
        s = get_suffix(w)
        if s:
            root_sfx[w[:-len(s)]][s] += 1

root_entries = []
for root, sfx_counts in sorted(root_sfx.items(), key=lambda x: -sum(x[1].values())):
    total = sum(sfx_counts.values())
    if total < 20: continue
    n_sfx = len(sfx_counts)
    probs = [c / total for c in sfx_counts.values()]
    entropy = -sum(p * math.log2(p) for p in probs if p > 0)
    dominant = sfx_counts.most_common(1)[0]
    rtype = 'LEXICAL' if entropy >= 2.5 else ('FUNCTIONAL' if entropy < 2.0 else 'MIXED')

    root_entries.append({
        'root': root,
        'total_freq': total,
        'n_suffixes_attested': n_sfx,
        'entropy': round(entropy, 2),
        'type': rtype,
        'dominant_suffix': dominant[0],
        'dominant_pct': round(dominant[1] * 100 / total, 1),
        'suffix_counts': dict(sfx_counts.most_common()),
    })

with open('%s/04_roots.json' % OUTDIR, 'w', encoding='utf-8') as f:
    json.dump({
        'description': 'EVA root morphemes with suffix paradigm. LEXICAL roots (high entropy) take all suffixes evenly. FUNCTIONAL roots concentrate on 1-2.',
        'key_findings': [
            'Root "d" is FUNCTIONAL: 48% -aiin, 0% -edy. Probably a grammatical particle.',
            'Roots "cho","sho","cheo" are FUNCTIONAL: 87-98% -dy. Probably markers.',
            'Roots "ch","sh","ok","qok","ot" are LEXICAL: 10-14 suffixes each.',
        ],
        'classification': {'LEXICAL': 'entropy >= 2.5', 'MIXED': '2.0 - 2.5', 'FUNCTIONAL': 'entropy < 2.0'},
        'count': len(root_entries),
        'entries': root_entries
    }, f, indent=2, ensure_ascii=False)
print('04_roots.json: %d entries' % len(root_entries))

# ================================================================
# DATASET 5: INGREDIENTS (from dictionary + nomenclator)
# ================================================================
with open('v12/data/vms_dictionary.json', encoding='utf-8') as f:
    vms_dict = json.load(f)

ingredients = []
for eva, entry in vms_dict.items():
    if entry.get('type') in ('INGR', 'DOSE_COMPOUND') or entry.get('ingredient'):
        ingredients.append({
            'eva': eva,
            'latin_decode': entry.get('latin', ''),
            'type': entry.get('type', ''),
            'confidence': entry.get('confidence', ''),
            'ingredient_match': entry.get('ingredient', ''),
            'frequency': entry.get('freq', 0),
            'source': entry.get('source', ''),
        })

with open('%s/05_ingredients.json' % OUTDIR, 'w', encoding='utf-8') as f:
    json.dump({
        'description': 'Ingredients identified in VMS via K&A decode + nomenclator/corpus matching',
        'reference_data': {
            'nomenclator': 'BruteForce/Italien plant names/nomenclator_unified.csv (4466 Italian plant names)',
            'AN_ingredients': 'BruteForce/Plants/Corpus_Pharmaceutique/datasets/antidotarium_nicolai_ingredients.csv (114 entries)',
            'CI_galenic': 'BruteForce/Plants/Corpus_Pharmaceutique/datasets/circa_instans_galenic_degrees.csv (207 entries)',
            'DALME': 'BruteForce/Plants/Corpus_Pharmaceutique/datasets/dalme_mathieu_roux_1488.csv (459 entries)',
            'Lylye': 'BruteForce/Plants/Corpus_Pharmaceutique/datasets/lylye_medicynes_ingredients.csv (715 entries)',
            'pharma_matrix': 'v12/data/pharma_validation_matrix.json (230 ingredients x 4 corpora)',
        },
        'warnings': [
            'K&A decode is FRAGILE for high-frequency words (13 suspect words = 11% of text)',
            'Ingredient identifications depend on K&A being correct for that specific word',
            'Only 37% of dictionary entries are confidence=SUR',
        ],
        'count': len(ingredients),
        'entries': ingredients
    }, f, indent=2, ensure_ascii=False)
print('05_ingredients.json: %d entries' % len(ingredients))

# ================================================================
# DATASET 6: GALENIC QUALITIES (from Circa Instans)
# ================================================================
galenic = []
with open('BruteForce/Plants/Corpus_Pharmaceutique/datasets/circa_instans_galenic_degrees.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        galenic.append({
            'entry_num': row.get('Entry#', ''),
            'old_french': row.get('OldFrench', ''),
            'latin': row.get('Latin', ''),
            'french': row.get('French', ''),
            'thermal': row.get('Thermal', ''),
            'thermal_degree': row.get('ThermalDeg', ''),
            'moisture': row.get('Moisture', ''),
            'moisture_degree': row.get('MoistureDeg', ''),
        })

with open('%s/06_galenic_qualities.json' % OUTDIR, 'w', encoding='utf-8') as f:
    json.dump({
        'description': 'Galenic qualities (thermal + moisture) for 207 simples from Circa Instans (Platearius, ~1166)',
        'source_file': 'BruteForce/Plants/Corpus_Pharmaceutique/datasets/circa_instans_galenic_degrees.csv',
        'source_text': 'Le Livre des Simples Medecines, ed. Dorveaux 1913',
        'system': {
            'thermal': ['calidum (hot)', 'frigidum (cold)'],
            'moisture': ['siccum (dry)', 'humidum (wet)'],
            'degrees': ['1 (mild)', '2 (moderate)', '3 (strong)', '4 (extreme)'],
            'note': 'Each simple has 2 qualities (thermal + moisture), each with a degree 1-4',
        },
        'relevance': 'If chol.daiin encodes Galenic formula, these are the expected values. Pattern: X est CALIDUM in N gradu ET SICCUM in N gradu.',
        'count': len(galenic),
        'entries': galenic
    }, f, indent=2, ensure_ascii=False)
print('06_galenic_qualities.json: %d entries' % len(galenic))

# ================================================================
# DATASET 7: DOSAGES (quantity notation system)
# ================================================================
dosages = {
    'description': 'Quantity/dosage notation system (SPECULATIVE - probably partially wrong)',
    'source': 'Session 6 analysis, docs/SESSION6_BILAN_COMPLET.md',
    'warnings': [
        'System produces 72 dosages on f103r where Aurea has only 7 => TOO MANY',
        'Suffix -aiin was originally decoded as "aquam" (WRONG, fixed session 6)',
        'Suffix -aiin was then hypothesized as dosage marker (PROBABLY WRONG)',
        'The quantity notation needs complete rethinking',
    ],
    'current_hypothesis': {
        'a': {'value': 'ana', 'meaning': 'of each (equal parts)', 'confidence': 'SPECULATIVE'},
        'i': {'value': '1', 'meaning': 'one unit', 'confidence': 'SPECULATIVE'},
        'ii': {'value': '2', 'meaning': 'two units', 'confidence': 'SPECULATIVE'},
        'n': {'value': 'drachma', 'meaning': '1 drachm (~3.4g)', 'confidence': 'SPECULATIVE'},
        'e': {'value': 'et', 'meaning': 'and (connector)', 'confidence': 'SPECULATIVE'},
        'h': {'value': '(silent)', 'meaning': 'mute/modifier', 'confidence': 'SPECULATIVE'},
    },
    'standard_medieval_units': [
        {'latin': 'granum', 'abbrev': 'gr.', 'weight_g': 0.065, 'source': 'AN/Compendium'},
        {'latin': 'scrupulum', 'abbrev': 'scr.', 'weight_g': 1.3, 'grains': 20, 'source': 'AN'},
        {'latin': 'drachma', 'abbrev': 'dr. / z.', 'weight_g': 3.9, 'scrupuli': 3, 'source': 'AN'},
        {'latin': 'uncia', 'abbrev': 'oz. / j.', 'weight_g': 31.1, 'drachmae': 8, 'source': 'AN'},
        {'latin': 'libra', 'abbrev': 'lb.', 'weight_g': 373.2, 'unciae': 12, 'source': 'AN'},
        {'latin': 'manipulus', 'abbrev': 'M.', 'meaning': 'handful', 'source': 'CI'},
        {'latin': 'pugillus', 'abbrev': '', 'meaning': 'pinch', 'source': 'CI'},
        {'latin': 'cochlear', 'abbrev': '', 'meaning': 'spoonful', 'source': 'CI'},
    ],
    'standard_abbreviations': [
        {'abbrev': 'ana', 'meaning': 'of each, equal parts', 'source': 'AN universal'},
        {'abbrev': 'q.s.', 'latin': 'quantum sufficit', 'meaning': 'as much as needed', 'source': 'AN'},
        {'abbrev': 'ss.', 'latin': 'semis', 'meaning': 'half', 'source': 'AN'},
        {'abbrev': 'Rp.', 'latin': 'recipe', 'meaning': 'take', 'source': 'AN universal'},
        {'abbrev': 'M.', 'latin': 'misce', 'meaning': 'mix', 'source': 'AN'},
        {'abbrev': 'ft.', 'latin': 'fiat', 'meaning': 'let it be made', 'source': 'AN'},
    ],
}

with open('%s/07_dosages.json' % OUTDIR, 'w', encoding='utf-8') as f:
    json.dump(dosages, f, indent=2, ensure_ascii=False)
print('07_dosages.json: written')

# ================================================================
# DATASET 8: RECIPE STRUCTURE TEMPLATES
# ================================================================
recipes = {
    'description': 'Recipe structure templates from reference texts, for comparison with VMS decode',
    'templates': [
        {
            'name': 'Antidotarium Nicolai format',
            'source': 'data/raw_corpus_9a/antidotarium_nicolai_1917.txt',
            'source_ref': 'van den Berg 1917 edition',
            'structure': 'Recipe [INGREDIENT_LIST] ana [DOSAGE]. [SINGLE_INSTRUCTION].',
            'pattern': ['VERB:recipe', 'INGR', 'INGR', 'INGR', '...', 'DOSE:ana Z.ii', 'VERB:terantur', 'PREP:cum', 'INGR:melle', 'RESULT:fiat electuarium'],
            'characteristics': {
                'n_recipes': 137,
                'avg_ingredients_per_recipe': '8-15',
                'verb_to_ingredient_ratio': '1:30',
                'ingredient_format': 'pure list, no verbs between',
                'dosage_position': 'at END of ingredient list',
                'instruction_count': '1-2 per recipe (at very end)',
                'organization': 'alphabetical by recipe name',
            },
            'example_latin': 'Recipe aloem epaticam, mirram, crocus, xilobalsami, ana drachmam unam; masticis, rose, spice, seminis apii, ana scrupulos duos. Terantur et cum melle rosato dispensentur.',
            'match_vms': 'POOR - VMS alternates verb-ingredient, AN lists ingredients in block',
        },
        {
            'name': 'Circa Instans format (monograph)',
            'source': 'BruteForce/Plants/Corpus_Pharmaceutique/sources_brutes/circa_instans_full_text.txt',
            'source_ref': 'Dorveaux 1913 edition (Old French)',
            'structure': '[PLANT_NAME] est [QUALITY1] et [QUALITY2]. [PROPERTIES]. [USAGE_RECIPES].',
            'pattern': ['NOUN:plant', 'COPULA:est', 'QUALITY:calidum/frigidum', 'DEGREE:in N gradu', 'CONJ:et', 'QUALITY:siccum/humidum', 'DEGREE:in N gradu', '.', 'PROPERTY:valet contra...', '.', 'VERB:recipe/prenez', 'INGR', 'VERB:coque', 'PREP:cum', 'INGR', '.'],
            'characteristics': {
                'n_entries': '~270 simples',
                'format': 'monograph per plant',
                'verb_to_ingredient_ratio': '1:3-5',
                'galenic_formula': 'ALWAYS present, first sentence',
                'usage_recipes': '1-5 short recipes per plant',
                'organization': 'roughly alphabetical',
            },
            'example_latin': 'Absinthium est calidum in primo gradu et siccum in eodem. Valet contra dolorem stomachi. Recipe succum absinthii et da cum vino.',
            'example_old_french': 'Aluisne est chauz el permer degre et ses el segont. Le jus vaut contre dolor del ventre. Prenez le jus et le donez ovec vin.',
            'match_vms': 'BEST MATCH for herbal section - 1 plant per page, descriptions then usage',
        },
        {
            'name': 'Grabadin / Liber Servitoris format',
            'source': 'Reference (no full text in repo)',
            'source_ref': 'Al-Zahrawi, Latin translations 12th century',
            'structure': 'Accipe [INGR], [VERB] [TOOL], [VERB], [VERB], [RESULT].',
            'pattern': ['VERB:accipe', 'INGR', 'CONJ:et', 'INGR', 'CONJ:et', 'VERB:liquefac', 'PREP:super', 'TOOL:ignem lentum', 'CONJ:et', 'VERB:misce', 'ADV:bene', 'CONJ:et', 'VERB:cola', 'PREP:per', 'TOOL:pannum', 'CONJ:et', 'VERB:pone', 'PREP:in', 'CONTAINER:vase'],
            'characteristics': {
                'format': 'step-by-step procedures',
                'verb_to_ingredient_ratio': '1:1-2 (very verb-heavy)',
                'organization': 'by preparation type (oils, ointments, syrups, electuaries, pills)',
                'tools_mentioned': 'mortar, fire, cloth, vessel',
            },
            'example_latin': 'Accipe oleum rosaceum et ceram albam et liquefac super ignem lentum et misce bene et cola per pannum et pone in vase.',
            'match_vms': 'POSSIBLE MATCH for balnea/pharma sections (-edy register)',
        },
        {
            'name': 'Tacuinum Sanitatis format',
            'source': 'Reference (no full text in repo)',
            'source_ref': 'Ibn Butlan, Latin translation 13th century',
            'structure': '[ITEM]. Natura: [QUALITY]. Optimum: [BEST_TYPE]. Iuvamentum: [BENEFIT]. Nocumentum: [HARM]. Remotio nocumenti: [REMEDY].',
            'pattern': ['NOUN:item', 'LABEL:Natura', 'QUALITY', 'LABEL:Optimum', 'DESCRIPTOR', 'LABEL:Iuvamentum', 'BENEFIT', 'LABEL:Nocumentum', 'HARM', 'LABEL:Remotio', 'REMEDY'],
            'characteristics': {
                'format': 'standardized 6-field entries',
                'very_structured': True,
                'illustrated': True,
                'organization': 'by category (plants, animals, activities, states)',
            },
            'match_vms': 'POSSIBLE for astro/cosmo sections (structured, illustrated, calendar-linked)',
        },
    ],
    'vms_observed_structure': {
        'herbal_section': {
            'folios': 'f1r-f57r, f85r-f102v',
            'suffix_register': '-ol, -or dominant',
            'structure_observed': '[gallows_prefix] [description_words] [chol.daiin on 31/148 pages] [more_words] [word-am = sentence end]',
            'verb_to_content_ratio': '~1:10-13 (between AN and CI)',
            'organization': '1 plant per page (recto+verso = same plant)',
        },
        'balnea_section': {
            'folios': 'f75r-f84v',
            'suffix_register': '-edy, -eedy dominant',
            'structure_observed': 'Long chains of -edy words (lists/procedures)',
        },
        'pharma_section': {
            'folios': 'f103r-f116r',
            'suffix_register': '-edy, -ain dominant',
            'structure_observed': 'Alternating ingredient-verb pattern (NOT pure list like AN)',
        },
    },
}

with open('%s/08_recipe_structures.json' % OUTDIR, 'w', encoding='utf-8') as f:
    json.dump(recipes, f, indent=2, ensure_ascii=False)
print('08_recipe_structures.json: %d templates' % len(recipes['templates']))

# ================================================================
# DATASET 9: VMS WORD FREQUENCY + SECTION DISTRIBUTION
# ================================================================
word_entries = []
for w, freq in word_freq.most_common(500):  # Top 500 words
    secs = word_sections[w]
    total_sec = sum(secs.values())
    sfx = get_suffix(w)
    root = w[:-len(sfx)] if sfx else ''

    word_entries.append({
        'eva': w,
        'frequency': freq,
        'n_folios': len(word_folios[w]),
        'suffix': sfx or '',
        'root': root,
        'pct_herbal': round((secs.get('herbal_A', 0) + secs.get('herbal_B', 0)) * 100 / total_sec, 1) if total_sec > 0 else 0,
        'pct_balnea': round(secs.get('balnea', 0) * 100 / total_sec, 1) if total_sec > 0 else 0,
        'pct_pharma': round(secs.get('pharma', 0) * 100 / total_sec, 1) if total_sec > 0 else 0,
        'pct_astro': round((secs.get('astro', 0) + secs.get('cosmo', 0)) * 100 / total_sec, 1) if total_sec > 0 else 0,
        'dict_latin': vms_dict.get(w, {}).get('latin', ''),
        'dict_confidence': vms_dict.get(w, {}).get('confidence', ''),
        'is_suspect': w in {'chedy','shedy','chol','chey','ol','dal','chor','daiin','dar','cheey','cheol','shol','shy'},
    })

with open('%s/09_top500_words.json' % OUTDIR, 'w', encoding='utf-8') as f:
    json.dump({
        'description': 'Top 500 VMS words with frequency, section distribution, suffix analysis, and dictionary decode',
        'source_transcription': 'data/transcriptions/ZL.txt (Zandbergen-Landini v2b)',
        'source_dictionary': 'v12/data/vms_dictionary.json',
        'warnings': [
            '13 suspect words flagged (is_suspect=true): their K&A decodes are PROBABLY WRONG',
            'Dictionary confidence: SUR=37%, PROBABLE=44%, DOUTE=11%, INCONNU=7%',
        ],
        'count': len(word_entries),
        'entries': word_entries
    }, f, indent=2, ensure_ascii=False)
print('09_top500_words.json: %d entries' % len(word_entries))

# ================================================================
# DATASET 10: BOTANICAL IDENTIFICATIONS
# ================================================================
bot_ids = []
with open('data/botanical_identifications.tsv', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        bot_ids.append({
            'folio': row.get('folio', ''),
            'section': row.get('section', ''),
            'species': row.get('proposed_species', ''),
            'common_name': row.get('common_name', ''),
            'proposer': row.get('proposer', ''),
            'confidence': row.get('confidence', ''),
            'notes': row.get('notes', ''),
        })

with open('%s/10_botanical_ids.json' % OUTDIR, 'w', encoding='utf-8') as f:
    json.dump({
        'description': 'Botanical identifications for herbal folios from multiple researchers',
        'source_file': 'data/botanical_identifications.tsv',
        'proposers': ['Dana Scott', 'Sherwood', 'Ethel Voynich', 'Tucker & Talbert', 'Tucker & Janick', 'Stephen Bax', 'Steve D'],
        'warnings': [
            'Most IDs have low-medium confidence',
            'Different proposers often disagree on species',
            'New World species (Tucker) are controversial',
            'Plant names are NOT directly encoded in K&A text (session 3 finding)',
        ],
        'count': len(bot_ids),
        'entries': bot_ids
    }, f, indent=2, ensure_ascii=False)
print('10_botanical_ids.json: %d entries' % len(bot_ids))

# ================================================================
# SUMMARY
# ================================================================
print('\n=== ALL DATASETS WRITTEN TO datasets/ ===')
print('01_logograms.json      - %d confirmed glyph-to-word mappings' % len(logograms))
print('02_verbs.json          - %d pharmaceutical verbs (confirmed + expected)' % len(verbs))
print('03_suffixes.json       - %d suffix paradigm entries with stats' % len(suffix_entries))
print('04_roots.json          - %d root morphemes classified LEX/FUNC' % len(root_entries))
print('05_ingredients.json    - %d ingredient identifications from dictionary' % len(ingredients))
print('06_galenic_qualities   - %d Circa Instans plant qualities' % len(galenic))
print('07_dosages.json        - medieval dosage system + VMS hypothesis')
print('08_recipe_structures   - %d reference text templates' % len(recipes['templates']))
print('09_top500_words.json   - 500 most frequent VMS words with full analysis')
print('10_botanical_ids.json  - %d plant identifications per folio' % len(bot_ids))
