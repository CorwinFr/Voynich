"""
Parse the COMPLETE Macer Floridus (77 chapters, 5133 lines).
Extract: chapter name, text, all mentioned ingredients/substances.
"""
import json, sys, io, os, re
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

MACER_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'De_viribus_herbarum.txt')
RESULTS = os.path.dirname(__file__)

with open(MACER_PATH, encoding='utf-8') as f:
    text = f.read()

# ================================================================
# 1. Split into chapters
# ================================================================
# Pattern: Roman numeral + "." + Name + "."
# e.g. "I. Artemisia." or "LXXVII. Squilla."

chapters = []
# Split on chapter headers
parts = re.split(r'\n\s*((?:[IVXLC]+)\.\s+\w[^\n]*?\.)\s*\n', text)

current_name = None
current_text = []

for i, part in enumerate(parts):
    # Check if this is a header
    m = re.match(r'([IVXLC]+)\.\s+(\w+)', part.strip())
    if m:
        # Save previous chapter
        if current_name and current_text:
            chapters.append({
                'name': current_name,
                'text': '\n'.join(current_text),
            })
        current_name = m.group(2)
        current_text = []
    else:
        if current_name:
            current_text.append(part.strip())

# Save last
if current_name and current_text:
    chapters.append({'name': current_name, 'text': '\n'.join(current_text)})

print(f'Parsed {len(chapters)} chapters')

# ================================================================
# 2. Extract ingredients/substances from each chapter
# ================================================================

# Known pharma substances (Latin, genitive and nominative forms)
PHARMA_SUBSTANCES = {
    # Waters & liquids
    'aqua': 'I_aqua', 'aquae': 'I_aqua', 'aquam': 'I_aqua',
    'vinum': 'I_vinum', 'vino': 'I_vinum', 'vini': 'I_vinum',
    'aceto': 'I_acetum', 'acetum': 'I_acetum', 'aceti': 'I_acetum',
    'oleum': 'I_oleum', 'oleo': 'I_oleum', 'olei': 'I_oleum',
    'melle': 'I_mel', 'mel': 'I_mel', 'mellis': 'I_mel',
    'lacte': 'I_lac', 'lac': 'I_lac', 'lactis': 'I_lac',
    'succo': 'I_succus', 'succus': 'I_succus', 'succi': 'I_succus', 'succum': 'I_succus',
    # Minerals
    'sale': 'I_sal', 'sal': 'I_sal', 'salis': 'I_sal',
    'nitro': 'I_nitrum', 'nitrum': 'I_nitrum',
    'sulphur': 'I_sulphur', 'sulphure': 'I_sulphur',
    # Common ingredients
    'piper': 'I_piper', 'pipere': 'I_piper', 'piperis': 'I_piper',
    'croco': 'I_crocus', 'crocus': 'I_crocus', 'croci': 'I_crocus',
    'aloe': 'I_aloe', 'aloes': 'I_aloe',
    'myrrha': 'I_myrrha', 'myrrhae': 'I_myrrha', 'myrrham': 'I_myrrha',
    'thure': 'I_thus', 'thus': 'I_thus', 'thuris': 'I_thus',
    'cera': 'I_cera', 'cerae': 'I_cera', 'ceram': 'I_cera',
    'rosa': 'I_rosa', 'rosae': 'I_rosa', 'rosarum': 'I_rosa', 'rosis': 'I_rosa',
    'ova': 'I_ovum', 'ovum': 'I_ovum', 'ovi': 'I_ovum', 'ovo': 'I_ovum',
    'faba': 'I_faba', 'fabae': 'I_faba', 'fabam': 'I_faba',
    'lente': 'I_lens', 'lens': 'I_lens', 'lentis': 'I_lens',
    'allium': 'I_allium', 'allio': 'I_allium', 'allii': 'I_allium',
    'mastice': 'I_mastix', 'mastix': 'I_mastix',
    'cassia': 'I_cassia', 'cassiae': 'I_cassia', 'cassiam': 'I_cassia',
    'coriandro': 'I_coriandrum', 'coriandrum': 'I_coriandrum',
    'cumino': 'I_cuminum', 'cuminum': 'I_cuminum',
    'anetho': 'I_anethum', 'anethum': 'I_anethum',
    'feniculum': 'I_feniculum', 'feniculi': 'I_feniculum',
    'mentha': 'I_mentha', 'menthae': 'I_mentha', 'mentham': 'I_mentha',
    'origano': 'I_origanum', 'origanum': 'I_origanum',
    'cannabis': 'I_cannabis', 'cannabi': 'I_cannabis',
    'linum': 'I_linum', 'lini': 'I_linum', 'lino': 'I_linum',
    'nardo': 'I_nardus', 'nardus': 'I_nardus', 'nardi': 'I_nardus',
    'zingiber': 'I_zingiber', 'zingibere': 'I_zingiber',
    'cinnamomum': 'I_cinnamomum', 'cinnamomi': 'I_cinnamomum',
    'galbano': 'I_galbanum', 'galbanum': 'I_galbanum',
    # Plants used as ingredients
    'plantagine': 'I_plantago', 'plantago': 'I_plantago', 'plantaginis': 'I_plantago',
    'urtica': 'I_urtica', 'urticae': 'I_urtica',
    'ruta': 'I_ruta', 'rutae': 'I_ruta', 'rutam': 'I_ruta',
    'absinthio': 'I_absinthium', 'absinthium': 'I_absinthium',
    'betonica': 'I_betonica', 'betonicae': 'I_betonica',
    'chamomilla': 'I_chamomilla', 'chamomillae': 'I_chamomilla',
    'verbena': 'I_verbena', 'verbenae': 'I_verbena',
    'sambucus': 'I_sambucus', 'sambuci': 'I_sambucus',
    'gentiana': 'I_gentiana', 'gentianae': 'I_gentiana',
    'aristolochia': 'I_aristolochia', 'aristolochiae': 'I_aristolochia',
    'salviam': 'I_salvia', 'salvia': 'I_salvia', 'salviae': 'I_salvia',
    'hyssopo': 'I_hyssopus', 'hyssopus': 'I_hyssopus',
    # Body parts & preparations (as context)
    'adipem': 'P_adeps', 'adipe': 'P_adeps', 'adipi': 'P_adeps',
    'vesica': 'I_vesica', 'vesicae': 'I_vesica',
    # Galenic qualities
    'calida': 'Q_calidus', 'calidum': 'Q_calidus', 'caloris': 'Q_calidus',
    'frigida': 'Q_frigidus', 'frigidum': 'Q_frigidus',
    'sicca': 'Q_siccus', 'siccum': 'Q_siccus',
    'humida': 'Q_humidus', 'humidum': 'Q_humidus',
}

for ch in chapters:
    words = re.findall(r'[a-zA-Z]+', ch['text'].lower())
    found_ingr = set()
    found_qual = set()

    for word in words:
        if word in PHARMA_SUBSTANCES:
            ref = PHARMA_SUBSTANCES[word]
            if ref.startswith('Q_'):
                found_qual.add(ref)
            else:
                found_ingr.add(ref)

    ch['ingredients'] = sorted(found_ingr)
    ch['qualities'] = sorted(found_qual)
    ch['n_words'] = len(words)
    ch['n_ingredients'] = len(found_ingr)

# ================================================================
# 3. DISPLAY
# ================================================================
print(f'\n{"="*70}')
print(f'MACER FLORIDUS COMPLET — {len(chapters)} chapitres')
print('=' * 70)

total_ingr_types = set()
for ch in chapters:
    total_ingr_types.update(ch['ingredients'])
    qual_str = ','.join(q.replace('Q_','') for q in ch['qualities']) if ch['qualities'] else ''
    ingr_str = ','.join(i.replace('I_','').replace('P_','') for i in ch['ingredients'][:8])
    if len(ch['ingredients']) > 8:
        ingr_str += f'...+{len(ch["ingredients"])-8}'
    print(f'  {ch["name"]:15s} {ch["n_words"]:5d}w {ch["n_ingredients"]:3d}ingr [{qual_str:20s}] {ingr_str}')

print(f'\n  Total unique ingredient types: {len(total_ingr_types)}')
print(f'  Chapters with 5+ ingredients: {sum(1 for ch in chapters if ch["n_ingredients"] >= 5)}')
print(f'  Chapters with qualities: {sum(1 for ch in chapters if ch["qualities"])}')

# ================================================================
# 4. Compare old (25) vs new (77)
# ================================================================
print(f'\n{"="*70}')
print('OLD vs NEW Macer')
print('=' * 70)

old_names = {'Artemisia','Abrotanum','Absinthium','Urtica','Allium','Plantago',
             'Viola','Ruta','Apium','Althaea','Anethum','Betonica','Savina',
             'Porrum','Chamomilla','Nepeta','Pulegium','Foeniculum','Acidula',
             'Portulaca','Lactuca','Rosa','Lilium','Satureia','Salvia'}

new_names = set(ch['name'] for ch in chapters)
added = new_names - old_names

print(f'  Old: {len(old_names)} chapters')
print(f'  New: {len(new_names)} chapters')
print(f'  Added: {len(added)} chapters')

critical_added = []
for name in sorted(added):
    ch = next((c for c in chapters if c['name'] == name), None)
    if ch and ch['n_ingredients'] >= 3:
        critical_added.append((name, ch['n_ingredients']))

print(f'\n  NEW chapters with 3+ ingredients ({len(critical_added)}):')
for name, n in sorted(critical_added, key=lambda x: -x[1]):
    ch = next(c for c in chapters if c['name'] == name)
    ingr_str = ','.join(i.replace('I_','') for i in ch['ingredients'][:6])
    print(f'    {name:15s}: {n:3d} ingredients — {ingr_str}')

# Save
output = {
    'source': 'De viribus herbarum (Odo Magdunensis, 11th c.)',
    'file': 'data/De_viribus_herbarum.txt',
    'n_chapters': len(chapters),
    'n_unique_ingredients': len(total_ingr_types),
    'chapters': chapters,
}

with open(os.path.join(RESULTS, 'macer_complete.json'), 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f'\nSaved macer_complete.json ({len(chapters)} chapters)')
