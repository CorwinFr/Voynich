"""
SESSION 16 — Update hypothesis_registry.json with all findings.

New findings:
  Frappe 1: seees=lens, ykeed=nitrum, kald=ovum, ypch=aqua (candidate)
  Frappe 2: ch/ot/sh too ubiquitous for specific mapping, qot=acetum? (conflict)
  Frappe 3: 7 balnea-exclusive roots, ol-compounds dominant
  Frappe 4: k/t galenic WEAKENED (wrong direction)
  Frappe 5: sh=51% before dose, ch=functional confirmed
  Frappe 6: 62 functional roots classified (terminators, openers, connectors)
"""
import json, sys, io, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.dirname(__file__)
REG_PATH = os.path.join(BASE, '..', 'hypothesis_registry.json')

with open(REG_PATH, encoding='utf-8') as f:
    registry = json.load(f)

# ================================================================
# UPDATE META
# ================================================================
registry['_meta']['sessions'] = '10-16'
registry['_meta']['last_updated'] = '2026-04-12'

# ================================================================
# NEW PROBABLE INGREDIENTS (Frappe 1)
# ================================================================
new_probables = {
    'seees': {
        'latin': 'lens',
        'confidence': 0.75,
        'evidence_for': [
            'frappe1_positional_f3v_elleborus',
            'frappe1_crossfolio_PERFECT_TP1_FP0_FN0',
        ],
        'evidence_against': [],
        'session': 16,
    },
    'ykeed': {
        'latin': 'nitrum',
        'confidence': 0.70,
        'evidence_for': [
            'frappe1_positional_f48v_ruta',
            'frappe1_crossfolio_TP1_FP0_FN1',
        ],
        'evidence_against': [
            'only_1_folio_confirmed',
        ],
        'session': 16,
    },
    'kald': {
        'latin': 'ovum',
        'confidence': 0.65,
        'evidence_for': [
            'frappe1_positional_f66v_satureia',
            'frappe1_crossfolio_TP1_FP0_FN1',
        ],
        'evidence_against': [
            'only_1_folio_confirmed',
        ],
        'session': 16,
    },
}

for root, data in new_probables.items():
    if root not in registry.get('probable_ingredients', {}):
        if 'probable_ingredients' not in registry:
            registry['probable_ingredients'] = {}
        registry['probable_ingredients'][root] = data
        print(f'  NEW PROBABLE: {root} = {data["latin"]} (conf={data["confidence"]})')
    else:
        # Update existing
        existing = registry['probable_ingredients'][root]
        existing['evidence_for'].extend(data['evidence_for'])
        existing['confidence'] = max(existing['confidence'], data['confidence'])
        print(f'  UPDATED: {root} = {data["latin"]} (conf={existing["confidence"]})')

# ================================================================
# YPCH = AQUA (upgrade from allium → aqua, stronger evidence)
# ================================================================
if 'ypch' in registry.get('probable_ingredients', {}):
    old = registry['probable_ingredients']['ypch']
    old['evidence_for'].append('frappe1_fingerprint_J050_TP4_FP2_16anchors')
    old['evidence_against'] = old.get('evidence_against', [])
    old['evidence_against'].append('was_allium_ABENGUEFIT_single_source')
    old['latin'] = 'aqua'
    old['confidence'] = 0.70
    old['conflict'] = 'session15_said_allium(ABENGUEFIT), session16_says_aqua(Macer_fingerprint_J=0.50). Aqua has stronger evidence.'
    print(f'  CONFLICT RESOLVED: ypch = aqua (was allium, Macer fingerprint stronger)')
else:
    registry['probable_ingredients']['ypch'] = {
        'latin': 'aqua',
        'confidence': 0.70,
        'evidence_for': [
            'frappe1_fingerprint_J050_TP4_FP2_16anchors',
        ],
        'evidence_against': [
            'was_allium_ABENGUEFIT_single_source',
        ],
        'session': 16,
    }
    print(f'  NEW PROBABLE: ypch = aqua (conf=0.70)')

# ================================================================
# UPDATE UNKNOWN TARGETS
# ================================================================
# aqua now has a candidate
if 'aqua' in registry['unknown_targets']:
    registry['unknown_targets']['aqua']['attempts'].append({
        'candidate': 'ypch',
        'method': 'macer_fingerprint_16anchors',
        'result': 'J=0.50, TP=4/6, FP=2',
        'status': 'probable',
        'session': 16,
    })
    print(f'  UPDATED: aqua target → ypch candidate (J=0.50)')

# ================================================================
# k/t GALENIC — WEAKENED
# ================================================================
registry['structural_facts']['kt_hot_cold']['session_16'] = {
    'result': 'WRONG DIRECTION',
    'detail': 'hot_plant(origanum)_has_most_k=0.820, cold_mean=0.548',
    'n_hot': 1,
    'n_cold': 3,
    'verdict': 'INCONCLUSIVE — too few data points AND wrong direction',
}
registry['structural_facts']['kt_hot_cold']['p'] = 'N/A'
registry['structural_facts']['kt_hot_cold']['confirmed'] = False
print(f'  UPDATED: kt_hot_cold → WEAKENED (wrong direction)')

# ================================================================
# FUNCTIONAL WORDS (Frappe 6) — Mark in registry
# ================================================================
if 'functional_words' not in registry:
    registry['functional_words'] = {}

# Top functional words (>40% of folios)
functional_list = {
    'ch':   {'folio_pct': 97, 'category': 'CONNECTOR', 'total': 2290},
    'sh':   {'folio_pct': 89, 'category': 'FUNCTIONAL', 'total': 1476, 'note': '51% before dose in pharma'},
    'ot':   {'folio_pct': 85, 'category': 'CONNECTOR', 'total': 1291, 'note': '53% after ingredient in pharma'},
    'ok':   {'folio_pct': 84, 'category': 'CONNECTOR', 'total': 1415},
    'qok':  {'folio_pct': 77, 'category': 'FUNCTIONAL', 'total': 2247, 'note': 'balnea-heavy 40%'},
    'ol':   {'folio_pct': 66, 'category': 'FUNCTIONAL', 'total': 737, 'note': 'balnea-heavy 40%'},
    'or':   {'folio_pct': 64, 'category': 'CONNECTOR', 'total': 491},
    'qot':  {'folio_pct': 62, 'category': 'CONNECTOR', 'total': 676},
    'dy':   {'folio_pct': 62, 'category': 'TERMINATOR', 'total': 282, 'note': 'end-heavy pos=0.72'},
    'aiin': {'folio_pct': 57, 'category': 'CONNECTOR', 'total': 504},
    'ar':   {'folio_pct': 54, 'category': 'CONNECTOR', 'total': 462},
    'dch':  {'folio_pct': 43, 'category': 'OPENER', 'total': 148, 'note': 'start-heavy'},
    'tch':  {'folio_pct': 38, 'category': 'OPENER', 'total': 132, 'note': 'start-heavy'},
    'ych':  {'folio_pct': 29, 'category': 'OPENER', 'total': 99, 'note': 'very start-heavy pos=0.13'},
    'am':   {'folio_pct': 24, 'category': 'TERMINATOR', 'total': 90, 'note': 'confirmed -am=72% sentence end'},
    'oty':  {'folio_pct': 35, 'category': 'TERMINATOR', 'total': 121, 'note': 'end-heavy pos=0.68'},
}

registry['functional_words'] = functional_list
print(f'  ADDED: {len(functional_list)} functional words classified')

# ================================================================
# BALNEA VOCABULARY (Frappe 3)
# ================================================================
if 'balnea_vocabulary' not in registry:
    registry['balnea_vocabulary'] = {}

registry['balnea_vocabulary'] = {
    'exclusive_roots': ['qolsh', 'qoly', 'loly', 'salch', 'qolky', 'lcheckhy', 'olksh'],
    'enriched_roots': ['rsh', 'solch', 'qolch', 'solsh', 'sheckh', 'qolk', 'olsh', 'qol'],
    'pattern': 'Most balnea roots contain ol/l as substring → ol may be body/bath concept',
    'n_balnea_folios': 20,
    'session': 16,
}
print(f'  ADDED: balnea vocabulary (7 exclusive, 8 enriched)')

# ================================================================
# VMS SECTIONS (corrected from Frappe 3)
# ================================================================
registry['structural_facts']['vms_sections'] = {
    'herbal_a': 111,
    'herbal_b': 32,
    'pharma': 24,
    'balnea': 20,
    'cosmo': 22,
    'astro': 10,
    'bio': 6,
    'volvelle': 1,
    'total': 226,
    'confirmed': True,
}
print(f'  ADDED: VMS section counts')

# ================================================================
# UPDATE NEXT_ACTIONS
# ================================================================
registry['next_actions'] = {
    'priority_HIGH': [
        'Verify ypch=aqua in pharma recipes (does it behave like a liquid?)',
        'Test seees=lens in Plantago/Elleborus folios (both chapters mention lens)',
        'Deep balnea analysis: match ol-compounds to body parts',
    ],
    'priority_MEDIUM': [
        'Search for vinum/succus among non-functional roots (not in top 62)',
        'Use ykeed=nitrum to constrain recipes containing it',
        'Look for verb patterns: which roots always follow logos r(recipe) or m(misce)?',
    ],
    'priority_LOW': [
        'Extended Macer with ALL 77 chapters (not just anchor plants)',
        'k/t needs 10+ quality-confirmed plants to test properly',
        'Cross-validate functional words against logogram behavior',
    ],
}
print(f'  UPDATED: next_actions')

# ================================================================
# SAVE
# ================================================================
with open(REG_PATH, 'w', encoding='utf-8') as f:
    json.dump(registry, f, indent=2, ensure_ascii=False)

print(f'\n  Registry saved. Totals:')
print(f'    Confirmed ingredients: {len(registry["confirmed_ingredients"])}')
print(f'    Probable ingredients: {len(registry.get("probable_ingredients", {}))}')
print(f'    Plant names: {len(registry["plant_names"])}')
print(f'    Functional words: {len(registry["functional_words"])}')
print(f'    Balnea exclusive: {len(registry["balnea_vocabulary"]["exclusive_roots"])}')
print(f'    Eliminated global: {len(registry["eliminated_global"])}')
