"""
PHASE 1A — Extend anchors from 6 to maximum.

Cross-reference ALL 106 botanical anchors with ALL 4 corpus:
- S05_MACER (25 chapters)
- S02_CI / Circa Instans (141 entries)
- S12_TACUINUM (358 entries)
- S10_ALPHITA (1714 entries)

Accept confidence >= 0.3 (tolerate error).
"""
import json, sys, io, os, re
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BOT_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'botanical_anchors.json')
VMS_PATH = os.path.join(os.path.dirname(__file__), '..', 'vms', 'vms_structured.json')
RECIPE_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'attacks', 'RECIPE_DATASET')
RESULTS = os.path.dirname(__file__)

with open(BOT_PATH, encoding='utf-8') as f:
    bot_data = json.load(f)
with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)

bot_anchors = bot_data.get('anchors', [])
print(f'Botanical anchors: {len(bot_anchors)}')

# Load all corpus entry names
def load_corpus_names(fname):
    """Load all plant/entry names from a corpus."""
    path = os.path.join(RECIPE_DIR, fname)
    if not os.path.exists(path): return {}
    with open(path, encoding='utf-8') as f:
        data = json.load(f)

    names = {}
    for entry in data.get('entries', []):
        name = entry.get('name', '').lower().strip()
        if name:
            # Extract ingredients too
            ingrs = set()
            for tok in entry.get('tokens', []):
                if tok.get('type') == 'INGR' and tok.get('ref'):
                    ingrs.add(tok['ref'])
                elif tok.get('type') == 'INGR':
                    raw = tok.get('raw', '').lower().strip('.,;: ')
                    if len(raw) >= 3:
                        ingrs.add(raw)
            names[name] = {
                'id': entry.get('id', ''),
                'name': entry.get('name', ''),
                'ingredients': ingrs,
                'n_tokens': len(entry.get('tokens', [])),
            }
    return names

corpora = {
    'MACER': load_corpus_names('S05_MACER.json'),
    'TACUINUM': load_corpus_names('S12_TACUINUM.json'),
    'ALPHITA': load_corpus_names('S10_ALPHITA.json'),
}

print(f'Corpora: MACER={len(corpora["MACER"])}, TAC={len(corpora["TACUINUM"])}, ALPH={len(corpora["ALPHITA"])}')

# ================================================================
# Match each botanical anchor with corpus entries
# ================================================================
def match_name(species, common, medieval, corpus_names):
    """Try to match a botanical ID with corpus entry names."""
    matches = []
    species_parts = set(p.lower().strip() for p in re.split(r'[/\s,]', species) if len(p) >= 4)
    common_parts = set(p.lower().strip() for p in re.split(r'[/\s,]', common) if len(p) >= 4)
    medieval_parts = set(p.lower().strip() for p in re.split(r'[/\s,;]', medieval) if len(p) >= 3)

    all_parts = species_parts | common_parts | medieval_parts

    for corpus_name, entry in corpus_names.items():
        corpus_lower = corpus_name.lower()
        for part in all_parts:
            if part in corpus_lower or corpus_lower in part:
                matches.append((corpus_name, entry))
                break
            # Also try genus name only
            genus = part.split()[0] if ' ' in part else part
            if len(genus) >= 4 and genus in corpus_lower:
                matches.append((corpus_name, entry))
                break

    return matches

extended_anchors = []

for anchor in bot_anchors:
    fid = anchor.get('folio', '')
    species = anchor.get('proposed_species', '') or ''
    common = anchor.get('common_name', '') or ''
    medieval = anchor.get('medieval_latin_name', '') or ''
    conf = anchor.get('confidence_score', 0)

    if conf < 0.3:
        continue
    if fid not in vms['folios']:
        continue

    corpus_matches = {}
    for corpus_name, corpus_entries in corpora.items():
        m = match_name(species, common, medieval, corpus_entries)
        if m:
            corpus_matches[corpus_name] = m[0]  # best match

    if corpus_matches:
        # Collect all ingredients from ALL matched corpus entries
        all_ingr = set()
        matched_names = {}
        for cn, (entry_name, entry_data) in corpus_matches.items():
            all_ingr.update(entry_data['ingredients'])
            matched_names[cn] = entry_name

        extended_anchors.append({
            'folio': fid,
            'species': species,
            'common': common,
            'medieval': medieval,
            'confidence': conf,
            'corpus_matches': matched_names,
            'n_corpus': len(corpus_matches),
            'ingredients': sorted(all_ingr),
            'n_ingredients': len(all_ingr),
        })

# Sort by number of corpus matches, then confidence
extended_anchors.sort(key=lambda x: (-x['n_corpus'], -x['confidence']))

print(f'\n{"="*70}')
print(f'EXTENDED ANCHORS: {len(extended_anchors)} folios')
print('=' * 70)

for a in extended_anchors:
    corps = ', '.join(f'{k}:{v}' for k, v in a['corpus_matches'].items())
    print(f'  {a["folio"]:8s} conf={a["confidence"]:.2f} {a["n_corpus"]}corpus {a["n_ingredients"]:3d}ingr | '
          f'{a["species"][:25]:25s} | {corps}')

# ================================================================
# Quick win: Phase 3B — first word = plant name
# ================================================================
print(f'\n{"="*70}')
print('PHASE 3B — FIRST WORD = PLANT NAME')
print('=' * 70)

LOGOS = {'o','l','d','r','v','x','k','m','f','t','y','c','s','sh','p','ch','air','h'}

first_words = {}
for a in extended_anchors:
    fid = a['folio']
    folio = vms['folios'][fid]
    for block in folio['blocks']:
        words = [w for line in block['lines'] for w in line['words']]
        if not words: continue
        # First non-logogram word (skip gallows opener, take the root)
        first_content = None
        for w in words:
            eva = w['eva_primary']
            if eva in LOGOS: continue
            morph = w.get('morphology') or {}
            root = morph.get('root', '')
            if root and len(root) >= 2:
                first_content = {'eva': eva, 'root': root}
                break

        if first_content:
            first_words[fid] = first_content
            break

print(f'\n  {"Folio":>8s} {"1st word":>15s} {"Root":>10s} → {"Plant":>25s}')
print('  ' + '-' * 65)

plant_name_mappings = {}
for a in extended_anchors:
    fid = a['folio']
    if fid not in first_words: continue
    fw = first_words[fid]

    # The plant's Latin name
    # Use medieval name if available, else genus from species
    latin_name = a['medieval'].split(',')[0].split(';')[0].strip().lower() if a['medieval'] else ''
    if not latin_name:
        latin_name = a['species'].split('/')[0].split(' ')[0].strip().lower()

    plant_name_mappings[fw['root']] = {
        'latin': latin_name,
        'folio': fid,
        'species': a['species'],
        'eva': fw['eva'],
    }

    print(f'  {fid:>8s} {fw["eva"]:>15s} {fw["root"]:>10s} → {latin_name:>25s}')

# ================================================================
# Save
# ================================================================
output = {
    'n_anchors': len(extended_anchors),
    'anchors': extended_anchors,
    'plant_name_mappings': plant_name_mappings,
    'first_words': first_words,
}

os.makedirs(RESULTS, exist_ok=True)
with open(os.path.join(RESULTS, 'extended_anchors.json'), 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f'\n  Saved extended_anchors.json')
print(f'  {len(extended_anchors)} anchors (was 6)')
print(f'  {len(plant_name_mappings)} plant name mappings from first words')
