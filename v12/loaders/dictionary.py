"""
Latin dictionary loader: Perseus wordset + medical vocabulary.
"""
import json
from typing import Optional


class LatinDictionary:
    """Perseus dictionary + medical vocabulary for validation."""

    def __init__(self):
        self._perseus: set[str] = set()
        self._medical: set[str] = set()

    def load_perseus(self, path: str):
        """Load Perseus Latin wordset (265K forms)."""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if isinstance(data, list):
            self._perseus = set(w.lower() for w in data)
        elif isinstance(data, dict):
            self._perseus = set(k.lower() for k in data.keys())
        self._build_medical_subset()

    def _build_medical_subset(self):
        """Build medical vocabulary subset from Perseus."""
        # Core medical/pharmaceutical Latin vocabulary
        medical_stems = {
            'aqua', 'cura', 'dolor', 'morbus', 'febris', 'tumor',
            'coque', 'misce', 'recipe', 'seca', 'ede', 'da',
            'ciere', 'aperiens', 'dolens', 'hiera', 'aloe',
            'cibus', 'cibo', 'cibum', 'potio', 'electuarium',
            'herba', 'radix', 'folia', 'semen', 'cortex',
            'succus', 'pulvis', 'unguentum', 'emplastrum',
            'balneum', 'lavare', 'fovere', 'calor', 'sudor',
            'ren', 'renes', 'iecur', 'ilia', 'dolor',
            'purgare', 'mundare', 'sanare', 'curare',
            'dulcis', 'amarus', 'calidus', 'frigidus',
            'libra', 'uncia', 'drachma', 'scrupulus',
            'decoctio', 'infusio', 'tinctura', 'mixtura',
        }
        self._medical = medical_stems & self._perseus
        # Also add any Perseus word containing medical stems
        for w in self._perseus:
            for stem in medical_stems:
                if stem in w and len(w) <= len(stem) + 6:
                    self._medical.add(w)
                    break

    def is_valid(self, word: str) -> bool:
        """Check if word is in Perseus dictionary."""
        return word.lower().strip('?[]()') in self._perseus

    def is_medical(self, word: str) -> bool:
        """Check if word is medical/pharmaceutical Latin."""
        return word.lower().strip('?[]()') in self._medical

    def add_medical_terms(self, terms: list[str]):
        """Add additional medical terms."""
        for t in terms:
            self._medical.add(t.lower())

    def add_vulgar_forms(self):
        """Add medieval vulgar Latin pharmaceutical forms not in Perseus.

        These are ablative/vernacular forms found in Antidotarium Nicolai,
        Circa Instans, and similar XIIe-XVe century pharmaceutical texts.
        They are valid medical Latin but not in the classical Perseus dictionary.
        """
        vulgar_pharma = [
            # Ingredients (ablative/vulgar forms)
            'ture', 'turis', 'tura',           # thus/thuris (frankincense)
            'asara', 'asaro', 'asari',          # asarum (wild ginger)
            'apio', 'apii',                     # apium (celery/parsley)
            'olen', 'oleo', 'olei',             # oleum (oil)
            'croci', 'croco',                   # crocus (saffron)
            'masticis', 'mastice',              # mastix (mastic)
            'nardi', 'nardo',                   # nardus (spikenard)
            'mirre', 'mirra',                   # myrrha (myrrh)
            'cinamomi', 'cinnamomi',            # cinnamomum (cinnamon)
            'zinziberis', 'zedoarie',           # zingiber (ginger)
            'camphore', 'camphora',             # camphora (camphor)
            'storacis', 'storace',              # storax (styrax resin)
            'casie', 'cassie',                  # cassia (cinnamon bark)
            'galbani', 'galbano',               # galbanum (resin)
            'opii', 'opio',                     # opium
            'piperis', 'pipere',                # piper (pepper)
            # Preparation terms
            'elixatura', 'elixatura',           # elixir preparation
            'colatura', 'colaturae',            # filtration
            'coctura', 'cocturae',              # cooking product
            'decoctura',                        # decoction product
            'coquendo', 'miscendo',             # gerunds
            'equaliter',                        # equal parts
            'ciboque',                          # food-and (agglutinated)
            # Compound medicine names
            'ierapigra', 'hierapicra',          # hiera picra
            'diascordium',                      # diascordium
            'metridatum', 'mithridatium',       # mithridate
            'electuarium', 'electuarii',        # electuary
            'theriac', 'theriaca',              # theriac
            # Vulgar forms of common words
            'codura', 'codure',                 # to harden (vulgar)
            'usure', 'usura',                   # use/practice
        ]
        for w in vulgar_pharma:
            self._perseus.add(w)
            self._medical.add(w)

    @property
    def size(self) -> int:
        return len(self._perseus)

    @property
    def medical_size(self) -> int:
        return len(self._medical)
