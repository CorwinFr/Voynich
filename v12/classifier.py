"""
WORD CLASSIFIER — Determine word type BEFORE decoding.

Types:
  LOGOGRAM   → decode by TABLE (fixed Latin word)
  DOSAGE     → decode by QUANTITY system (ana, numbers, drachmes)
  INGREDIENT → decode by K&A (phonetic, name of substance)
  VERB_LOGO  → logogram that is a pharmaceutical verb (recipe, misce, coque)
  FUNCTION   → logogram that is a function word (ac, de, in, cum, vel)

The classification drives WHICH decoder to use.
"""
import json
import os
from pathlib import Path


# ── Load logogram table ──────────────────────────────────────────

_RULES_DIR = Path(__file__).parent / 'rules'

def _load_logograms():
    """Load confirmed logograms from rules/logograms.json."""
    path = _RULES_DIR / 'logograms.json'
    if not path.exists():
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if isinstance(data, dict):
        return {k: v.get('latin', v) if isinstance(v, dict) else v
                for k, v in data.items() if k != '_comment'}
    return {entry['eva']: entry['latin'] for entry in data}

LOGOGRAMS = _load_logograms()

# ── The glyph table (from bifolio cross-validation) ──────────────

GLYPH_TABLE = {
    'o': 'ac', 'l': 'se', 'd': 'de', 'r': 'recipe', 'v': 'vel',
    'x': 'crux', 'k': 'cum', 'm': 'misce', 'f': 'per', 't': 'el',
    'y': 'in', 'c': 'cum', 's': 'est', 'p': 'usque',
    'sh': 'ci', 'ch': 'cum',
}

# Pharmaceutical verbs (as logograms)
VERB_LOGOGRAMS = {
    'qoky': 'coque', 'r': 'recipe', 'm': 'misce',
    'chor': 'cola', 'otedy': 'tere et',
}

# Known dosage patterns
DOSAGE_SUFFIXES = ['aiin', 'ain', 'aii', 'ai']

# ── Classifier ───────────────────────────────────────────────────

class WordType:
    LOGOGRAM = 'LOGO'      # single glyph or confirmed logogram → TABLE
    VERB = 'VERB'          # pharmaceutical verb logogram
    FUNCTION = 'FUNC'      # function word (preposition, conjunction)
    DOSAGE = 'DOSE'        # quantity expression (ana X drachmes)
    INGREDIENT = 'INGR'    # compound word → K&A decode
    MIXED = 'MIXED'        # prefix logogram + ingredient root


def classify_word(word, prev_type=None, prev_word=None):
    """Classify an EVA word into its type.

    Args:
        word: EVA word string
        prev_type: type of previous word (for context)
        prev_word: previous EVA word (for context)

    Returns:
        (WordType, details_dict)
    """
    # ── Rule 1: Single glyph → always LOGOGRAM ──
    if len(word) <= 2 and word in GLYPH_TABLE:
        value = GLYPH_TABLE[word]
        if value in ('recipe', 'misce'):
            return WordType.VERB, {'table_value': value}
        elif value in ('ac', 'de', 'in', 'cum', 'vel', 'per', 'el', 'est', 'se', 'ci', 'usque', 'crux'):
            return WordType.FUNCTION, {'table_value': value}
        else:
            return WordType.LOGOGRAM, {'table_value': value}

    # ── Rule 2: Known verb logogram → VERB ──
    if word in VERB_LOGOGRAMS:
        return WordType.VERB, {'table_value': VERB_LOGOGRAMS[word]}

    # ── Rule 3: Known logogram → LOGOGRAM/FUNCTION ──
    if word in LOGOGRAMS:
        value = LOGOGRAMS[word]
        return WordType.LOGOGRAM, {'table_value': value}

    # ── Rule 4: Pure dosage (standalone aiin/ain/ai) ──
    if word in ('aiin', 'ain', 'aii', 'ai'):
        return WordType.DOSAGE, {'dosage': _parse_dosage(word)}

    # ── Rule 5: Prefix + dosage suffix ──
    # e.g., okaiin = ok + aiin, where ok is short (1-3 chars)
    for suffix in DOSAGE_SUFFIXES:
        if word.endswith(suffix) and len(word) > len(suffix):
            prefix = word[:-len(suffix)]
            # Short prefix (1-3 chars) = preposition + dosage
            if len(prefix) <= 3 and _is_prefix_sequence(prefix):
                return WordType.DOSAGE, {
                    'prefix': prefix,
                    'dosage': _parse_dosage(suffix),
                    'prefix_meaning': _decode_prefix(prefix),
                }
            # Long prefix (4+ chars) = ingredient with dosage attached
            else:
                return WordType.MIXED, {
                    'ingredient_part': prefix,
                    'dosage_part': suffix,
                    'dosage': _parse_dosage(suffix),
                }

    # ── Rule 6: Short word after verb → likely INGREDIENT ──
    if prev_type == WordType.VERB:
        return WordType.INGREDIENT, {}

    # ── Rule 7: Word after dosage → likely next INGREDIENT ──
    if prev_type == WordType.DOSAGE:
        return WordType.INGREDIENT, {}

    # ── Rule 8: Compound word (4+ chars, no dosage suffix) ──
    if len(word) >= 4:
        # Check if it starts with a known prefix (deagglutination)
        for prefix in ['qo', 'da', 'ot', 'ol', 'ok', 'ch', 'sh']:
            if word.startswith(prefix) and len(word) > len(prefix) + 2:
                return WordType.INGREDIENT, {'prefix': prefix}
        return WordType.INGREDIENT, {}

    # ── Rule 9: Short unknown → FUNCTION by default ──
    if len(word) <= 3:
        return WordType.FUNCTION, {}

    return WordType.INGREDIENT, {}


def _is_prefix_sequence(prefix):
    """Check if prefix is a sequence of known logogram glyphs."""
    known_prefixes = {'d', 'y', 'o', 'l', 's', 'ok', 'qo', 'ot', 'ol',
                      'da', 'sa', 'ra', 'la', 'ch', 'sh', 'qok', 'qot'}
    return prefix in known_prefixes


def _decode_prefix(prefix):
    """Decode a short prefix using the table."""
    parts = []
    i = 0
    while i < len(prefix):
        for length in [2, 1]:
            if i + length <= len(prefix):
                chunk = prefix[i:i+length]
                if chunk in GLYPH_TABLE:
                    parts.append(GLYPH_TABLE[chunk])
                    i += length
                    break
        else:
            parts.append(f'[{prefix[i]}]')
            i += 1
    return ' '.join(parts)


def _parse_dosage(dosage_str):
    """Parse a dosage suffix into structured form."""
    dosage_map = {
        'aiin': 'ana II dr.',
        'ain':  'ana I dr.',
        'aii':  'ana II',
        'ai':   'ana I',
    }
    return dosage_map.get(dosage_str, dosage_str)


def classify_line(words):
    """Classify all words in a line with context."""
    results = []
    prev_type = None
    prev_word = None

    for w in words:
        wtype, details = classify_word(w, prev_type, prev_word)
        results.append((w, wtype, details))
        prev_type = wtype
        prev_word = w

    return results


# ══════════════════════════════════════════════════════════════════
# TEST
# ══════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    # Test on L04
    l04 = ['daiin','otey','ofeeey','shes','o','d','okeeod','l','o','lkeeol',
           'dkedar','yf','aros','s','y','chedaiin','k','eeety','x','deeodal',
           'vo','tchor','kedar','dal','daiin','aiin','otal','daro','v']

    print("=== L04 CLASSIFICATION ===\n")
    results = classify_line(l04)
    for w, wtype, details in results:
        det = details.get('table_value', details.get('dosage', details.get('prefix', '')))
        print(f"  {w:>12} → {wtype:5s}  {det}")

    print()

    # Test on f103r first line
    f103r_l1 = ['pchedal','shdy','ytechypchy','otey','lshey','qoteey',
                'qotal','shedy','yshdal','dain','okal','dald']

    print("=== F103R LINE 1 CLASSIFICATION ===\n")
    results = classify_line(f103r_l1)
    for w, wtype, details in results:
        det = details.get('table_value', details.get('dosage',
              details.get('prefix_meaning', details.get('prefix', ''))))
        print(f"  {w:>12} → {wtype:5s}  {det}")
