"""
LOADER — Load all referentiels (R01-R08) and sources (S01-S10) from RECIPE_DATASET.

Usage:
    from lib.loader import load_all, load_referentiels, load_sources

    data = load_all()
    verbs = data['R01']          # dict of V_xxx entries
    ingredients = data['R02']    # dict of I_xxx entries
    recipes_an = data['S01']     # list of AN recipe entries
    aurea = data['S03']          # list with 1 Aurea entry
"""
import json
import os
from pathlib import Path

# Base path to RECIPE_DATASET
DATASET_DIR = Path(__file__).parent.parent.parent / 'attacks' / 'RECIPE_DATASET'

# Fallback: try the datasets/ directory (old location)
if not DATASET_DIR.exists():
    DATASET_DIR = Path(__file__).parent.parent.parent / 'RECIPE_DATASET'
if not DATASET_DIR.exists():
    DATASET_DIR = Path(__file__).parent.parent.parent / 'datasets'

REFERENTIEL_FILES = {
    'R01': 'R01_verbs.json',
    'R02': 'R02_ingredients.json',
    'R03': 'R03_units.json',
    'R04': 'R04_forms.json',
    'R05': 'R05_tools.json',
    'R06': 'R06_qualities.json',
    'R07': 'R07_plant_parts.json',
    'R08': 'R08_indications.json',
}

SOURCE_FILES = {
    'S01': 'S01_AN.json',
    'S02': 'S02_CI.json',
    'S03': 'S03_AUREA.json',
    'S05': 'S05_MACER.json',
    'S06': 'S06_REGIMEN.json',
    'S07': 'S07_DALME.json',
    'S09': 'S09_COLLECTIO.json',
    'S10': 'S10_ALPHITA.json',
}


def _load_json(filepath):
    """Load a JSON file with UTF-8 encoding."""
    with open(filepath, encoding='utf-8') as f:
        return json.load(f)


def load_referentiel(code):
    """Load a single referentiel (R01-R08).

    Returns dict of entries (excluding _meta).
    Each entry is keyed by ref_id (V_recipe, I_myrrha, etc.)
    """
    filename = REFERENTIEL_FILES.get(code)
    if not filename:
        raise ValueError(f"Unknown referentiel: {code}")

    filepath = DATASET_DIR / filename
    if not filepath.exists():
        print(f"WARNING: {filepath} not found")
        return {}

    data = _load_json(filepath)
    # Remove _meta, return only entries
    return {k: v for k, v in data.items() if k != '_meta'}


def load_referentiel_with_meta(code):
    """Load a referentiel with its _meta field."""
    filename = REFERENTIEL_FILES.get(code)
    if not filename:
        raise ValueError(f"Unknown referentiel: {code}")
    filepath = DATASET_DIR / filename
    if not filepath.exists():
        return {'_meta': {}, 'entries': {}}
    data = _load_json(filepath)
    meta = data.pop('_meta', {})
    return {'_meta': meta, 'entries': data}


def load_source(code):
    """Load a single source (S01-S10).

    Returns list of entries (each entry has id, raw_text, tokens, etc.)
    """
    filename = SOURCE_FILES.get(code)
    if not filename:
        raise ValueError(f"Unknown source: {code}")

    filepath = DATASET_DIR / filename
    if not filepath.exists():
        # Try alternate names
        for alt in [filename.replace('.json', '_final.json'), filename.replace('.json', '_new.json')]:
            alt_path = DATASET_DIR / alt
            if alt_path.exists():
                filepath = alt_path
                break
        else:
            print(f"WARNING: {filepath} not found")
            return []

    data = _load_json(filepath)
    return data.get('entries', [])


def load_source_with_meta(code):
    """Load a source with its _meta field."""
    filename = SOURCE_FILES.get(code)
    if not filename:
        raise ValueError(f"Unknown source: {code}")
    filepath = DATASET_DIR / filename
    if not filepath.exists():
        return {'_meta': {}, 'entries': []}
    data = _load_json(filepath)
    return {'_meta': data.get('_meta', {}), 'entries': data.get('entries', [])}


def load_referentiels():
    """Load all referentiels. Returns dict keyed by R01-R08."""
    result = {}
    for code in REFERENTIEL_FILES:
        result[code] = load_referentiel(code)
    return result


def load_sources():
    """Load all sources. Returns dict keyed by S01-S10."""
    result = {}
    for code in SOURCE_FILES:
        entries = load_source(code)
        if entries:
            result[code] = entries
    return result


def load_all():
    """Load everything. Returns merged dict R01-R08 + S01-S10."""
    result = load_referentiels()
    result.update(load_sources())
    return result


# ================================================================
# LOOKUP HELPERS
# ================================================================

class FormLookup:
    """Reverse lookup: given any inflected form, find the ref_id.

    Usage:
        lookup = FormLookup(verbs_dict, ingredients_dict)
        lookup.find("myrrham")  # -> ("I_myrrha", "R02")
        lookup.find("coquatur") # -> ("V_coque", "R01")
        lookup.find("unknown")  # -> (None, None)
    """
    def __init__(self, *referentiel_dicts):
        self._index = {}  # form -> (ref_id, source_code)

        code_map = {
            'V_': 'R01', 'I_': 'R02', 'D_': 'R03', 'U_': 'R03',
            'F_': 'R04', 'T_': 'R05', 'Q_': 'R06', 'COMBO_Q_': 'R06',
            'P_': 'R07', 'M_': 'R08',
        }

        for ref_dict in referentiel_dicts:
            for ref_id, entry in ref_dict.items():
                # Determine source code from prefix
                source = 'UNKNOWN'
                for prefix, code in code_map.items():
                    if ref_id.startswith(prefix):
                        source = code
                        break

                # Index canonical form
                canonical = entry.get('canonical', '')
                if canonical:
                    self._index[canonical.lower()] = (ref_id, source)

                # Index all forms
                forms = entry.get('forms', {})
                for lang, form_list in forms.items():
                    if isinstance(form_list, list):
                        for form in form_list:
                            self._index[form.lower()] = (ref_id, source)
                    elif isinstance(form_list, str):
                        self._index[form_list.lower()] = (ref_id, source)

    def find(self, word):
        """Find ref_id for a word form. Returns (ref_id, source_code) or (None, None)."""
        return self._index.get(word.lower(), (None, None))

    def find_ref(self, word):
        """Find just the ref_id. Returns ref_id or None."""
        return self._index.get(word.lower(), (None, None))[0]

    def __contains__(self, word):
        return word.lower() in self._index

    def __len__(self):
        return len(self._index)


def build_form_lookup(referentiels=None):
    """Build a FormLookup from all referentiels.

    Usage:
        lookup = build_form_lookup()
        ref_id = lookup.find_ref("myrrham")  # -> "I_myrrha"
    """
    if referentiels is None:
        referentiels = load_referentiels()
    return FormLookup(*referentiels.values())


# ================================================================
# STATISTICS
# ================================================================

def print_stats(data=None):
    """Print summary statistics of loaded data."""
    if data is None:
        data = load_all()

    print("=" * 60)
    print("RECIPE_DATASET STATISTICS")
    print("=" * 60)
    print(f"Dataset directory: {DATASET_DIR}")
    print()

    print("REFERENTIELS:")
    total_ref = 0
    for code in sorted(REFERENTIEL_FILES.keys()):
        if code in data:
            n = len(data[code])
            total_ref += n
            print(f"  {code}: {n:>5d} entries")
    print(f"  TOTAL: {total_ref:>5d} concepts")
    print()

    print("SOURCES:")
    total_entries = 0
    total_tokens = 0
    total_refs = 0
    for code in sorted(SOURCE_FILES.keys()):
        if code in data:
            entries = data[code]
            n = len(entries)
            tokens = sum(len(e.get('tokens', [])) for e in entries)
            refs = sum(1 for e in entries for t in e.get('tokens', []) if t.get('ref'))
            total_entries += n
            total_tokens += tokens
            total_refs += refs
            pct = refs * 100 // tokens if tokens > 0 else 0
            print(f"  {code}: {n:>5d} entries, {tokens:>7d} tokens, {refs:>6d} with ref ({pct}%)")
    print(f"  TOTAL: {total_entries:>5d} entries, {total_tokens:>7d} tokens, {total_refs:>6d} refs")
    print()

    # Form lookup stats
    lookup = build_form_lookup({k: v for k, v in data.items() if k.startswith('R')})
    print(f"FORM LOOKUP: {len(lookup)} indexed forms across all languages")


if __name__ == '__main__':
    data = load_all()
    print_stats(data)
