"""
Build the HYPOTHESIS REGISTRY — persistent, versioned, nothing deleted.
"""
import json, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

registry = {
    '_meta': {
        'description': 'Hypothesis registry for VMS decoding',
        'principle': 'Accumulate evidence FOR and AGAINST. Nothing deleted.',
        'sessions': '10-14',
        'last_updated': '2026-04-12',
    },
    'confirmed_ingredients': {
        'cth': {'latin': 'acetum', 'english': 'vinegar', 'confidence': 0.9,
                'evidence_for': ['fingerprint_unique_6anchors', 'found_on_f48v_Ruta', 'daly_fuzzy_support'],
                'evidence_against': [], 'session_confirmed': 13},
        'yk': {'latin': 'mel', 'english': 'honey', 'confidence': 0.9,
               'evidence_for': ['fingerprint_unique_6anchors', 'found_on_f48v_Ruta'],
               'evidence_against': ['was_candidate_for_aqua_15pct'], 'session_confirmed': 13},
        'cht': {'latin': 'piper', 'english': 'pepper', 'confidence': 0.9,
                'evidence_for': ['fingerprint_unique_macer77_f48v+f28r'],
                'evidence_against': ['was_plantaginis_with_6anchors'], 'session_confirmed': 14},
        'shocthy': {'latin': 'mastix', 'english': 'mastic', 'confidence': 0.9,
                    'evidence_for': ['fingerprint_unique_100anchors_f29r+f25r'],
                    'evidence_against': [], 'session_confirmed': 14},
        'shotch': {'latin': 'nigella', 'english': 'black cumin', 'confidence': 0.9,
                   'evidence_for': ['fingerprint_unique_100anchors_f29v+f50v'],
                   'evidence_against': [], 'session_confirmed': 14},
        'chk': {'latin': 'oleum', 'english': 'oil', 'confidence': 0.8,
                'evidence_for': ['triangulation_exclusive_f48v+f9v+f41r'],
                'evidence_against': [], 'session_confirmed': 14},
        'otoly': {'latin': 'sal', 'english': 'salt', 'confidence': 0.7,
                  'evidence_for': ['triangulation_exclusive_f48v+f37r'],
                  'evidence_against': [], 'session_confirmed': 14},
    },
    'plant_names': {
        'pcheod': {'latin': 'ruta', 'folio': 'f48v', 'confidence': 0.6, 'method': 'first_word_sherwood_macer'},
        'foch': {'latin': 'viola', 'folio': 'f9v', 'confidence': 0.6, 'method': 'first_word_sherwood_macer'},
        'pos': {'latin': 'lactuca', 'folio': 'f29r', 'confidence': 0.6, 'method': 'first_word_sherwood_macer'},
        'tsho': {'latin': 'apium', 'folio': 'f44v', 'confidence': 0.6, 'method': 'first_word_sherwood_macer'},
        'posho': {'latin': 'salvia', 'folio': 'f51v', 'confidence': 0.6, 'method': 'first_word_sherwood_macer'},
        'tedo': {'latin': 'crocus', 'folio': 'f39r', 'confidence': 0.6, 'method': 'first_word_sherwood'},
        'tocph': {'latin': 'mentha', 'folio': 'f37r', 'confidence': 0.6, 'method': 'first_word_sherwood_macer'},
        'keered': {'latin': 'coriandrum', 'folio': 'f41v', 'confidence': 0.6, 'method': 'first_word_sherwood_macer'},
        'pchod': {'latin': 'aristolochia', 'folio': 'f28r', 'confidence': 0.6, 'method': 'first_word_sherwood_macer'},
        'pched': {'latin': 'lens', 'folio': 'f26v', 'confidence': 0.6, 'method': 'first_word_sherwood'},
        'do': {'latin': 'gentiana', 'folio': 'f50v', 'confidence': 0.6, 'method': 'first_word_sherwood'},
        'chod': {'latin': 'symphytum', 'folio': 'f8v', 'confidence': 0.6, 'method': 'first_word_sherwood'},
        'keed': {'latin': 'erigeron', 'folio': 'f31r', 'confidence': 0.6, 'method': 'first_word_sherwood'},
        'fch': {'latin': 'veronica', 'folio': 'f32r', 'confidence': 0.6, 'method': 'first_word_sherwood'},
        'ko': {'latin': 'lonicera', 'folio': 'f13v', 'confidence': 0.6, 'method': 'first_word_sherwood'},
        'ksh': {'latin': 'rhododendron', 'folio': 'f28v', 'confidence': 0.6, 'method': 'first_word_sherwood'},
        'told': {'latin': 'dictamnus', 'folio': 'f21v', 'confidence': 0.6, 'method': 'first_word_sherwood'},
        'och': {'latin': 'drosera', 'folio': 'f56r', 'confidence': 0.6, 'method': 'first_word_sherwood'},
        'tsh': {'latin': 'sonchus', 'folio': 'f15r', 'confidence': 0.6, 'method': 'first_word_sherwood'},
        'pcho': {'latin': 'scorzonera', 'folio': 'f14r', 'confidence': 0.6, 'method': 'first_word_sherwood'},
        'pod': {'latin': 'valeriana', 'folio': 'f31v', 'confidence': 0.6, 'method': 'first_word_sherwood'},
        'po': {'latin': 'inula', 'folio': 'f46v', 'confidence': 0.6, 'method': 'first_word_sherwood'},
        'kcho': {'latin': 'arnica', 'folio': 'f5r', 'confidence': 0.6, 'method': 'first_word_sherwood'},
    },
    'unknown_targets': {
        'aqua': {'attempts': [
            {'candidate': 'aiin', 'method': 'alignment', 'result': '15%', 'status': 'eliminated', 'session': 13},
            {'candidate': 'qok', 'method': 'co_occurrence', 'result': 'Zipf p=0.92', 'status': 'eliminated', 'session': 13},
            {'candidate': None, 'method': 'triangulation', 'result': '6/10 folios=too ubiquitous', 'status': 'no_candidate', 'session': 14},
        ]},
        'succus': {'attempts': [
            {'candidate': None, 'method': 'triangulation', 'result': '8/10 folios', 'status': 'no_candidate', 'session': 14},
        ]},
        'vinum': {'attempts': [
            {'candidate': None, 'method': 'triangulation', 'result': '8/10 folios', 'status': 'no_candidate', 'session': 14},
        ]},
        'lac': {'attempts': []},
        'rosa': {'attempts': []},
        'faba': {'attempts': []},
        'ovum': {'attempts': []},
    },
    'eliminated_global': [
        {'hypothesis': 'letter_substitution', 'reason': 'volvelle score=0.00', 'session': 12},
        {'hypothesis': 'f_p_variants', 'reason': 'permutation p=1.0', 'session': 13},
        {'hypothesis': 'AN_recodification', 'reason': 'Zipf artifact p=0.92', 'session': 13},
        {'hypothesis': 'icount_doses', 'reason': 'i2=81% herbal, ratio inversé', 'session': 14},
        {'hypothesis': 'encoding_has_phonetic_logic', 'reason': '0-12% match on all tests', 'session': 14},
    ],
    'structural_facts': {
        'gallows_88pct_initial': {'p': 0.000, 'confirmed': True},
        'am_terminator_72pct': {'enrichment': 5.3, 'confirmed': True},
        'n_end_98pct': {'confirmed': True},
        'q_start_99pct': {'confirmed': True},
        'volvelle_alphabet': {'p': 0.00016, 'confirmed': True},
        'macer_best_match': {'score': 1.61, 'confirmed': True},
        'pharma_compounds': {'description': 'prefix+root+suffix', 'confirmed': True},
        'kt_hot_cold': {'p': 0.13, 'confirmed': False, 'trend': 'k=cold t=hot'},
    },
    'next_actions': {
        'priority_HIGH': [
            'Run triangulation with S08_AVICENNA (28 plant matches)',
            'Run triangulation with S15_ABENGUEFIT (22 plant matches)',
        ],
        'priority_MEDIUM': [
            'Use Tacuinum galenic qualities to validate k/t',
            'Decompose more pharma words with Avicenna ingredients',
            'Find aqua/succus/vinum by exclusion (large corpus needed)',
        ],
        'priority_LOW': [
            'Parse full Macer from Wikisource with better ingredient extraction',
            'Cross-validate plant names against multiple Sherwood alternatives',
        ],
    },
}

out_path = 'd:/Github/Voynich/project_hope/hypothesis_registry.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(registry, f, indent=2, ensure_ascii=False)

print(f'HYPOTHESIS REGISTRY SAVED: {out_path}')
print(f'  {len(registry["confirmed_ingredients"])} confirmed ingredients')
print(f'  {len(registry["plant_names"])} plant names')
print(f'  {len(registry["unknown_targets"])} unknown targets with {sum(len(u["attempts"]) for u in registry["unknown_targets"].values())} attempts')
print(f'  {len(registry["eliminated_global"])} globally eliminated hypotheses')
print(f'  {len(registry["structural_facts"])} structural facts')
