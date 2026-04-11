"""
VMS_PARSER — Parse the Voynich manuscript transcription (ZL.txt) into structured data.

Usage:
    from lib.vms_parser import VMSCorpus

    vms = VMSCorpus()
    vms.load()

    # All words with metadata
    for word in vms.words:
        print(word.eva, word.folio, word.section, word.line, word.position)

    # Words on a specific folio
    f103r_words = vms.get_folio('f103r')

    # Word frequencies
    freq = vms.word_freq  # Counter

    # Words by section
    herbal_words = vms.get_section('herbal_A')
"""
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Set


# Find ZL.txt relative to repo root (works from any cwd)
_repo_root = Path(__file__).parent.parent.parent
TRANSCRIPTION_FILE = _repo_root / 'data' / 'transcriptions' / 'ZL.txt'
if not TRANSCRIPTION_FILE.exists():
    # Try from cwd
    TRANSCRIPTION_FILE = Path('data') / 'transcriptions' / 'ZL.txt'

# EVA suffix system (session 7 discovery)
SUFFIXES = ['aiin', 'ain', 'eedy', 'edy', 'eey', 'ey', 'dy', 'ol', 'or', 'ar', 'al', 'am', 'om', 'air']

# Known logograms (bifolio bH1 confirmed)
LOGOGRAMS = {
    'o': 'ac', 'l': 'se', 'd': 'de', 'r': 'recipe', 'v': 'vel',
    'x': 'crux', 'k': 'cum', 'm': 'misce', 'f': 'per', 't': 'el',
    'y': 'in', 'c': 'cum', 's': 'est', 'sh': 'ci', 'p': 'usque',
    'air': 'aier',
}


def get_section(fnum, rv):
    """Map folio number to section."""
    if fnum <= 56:
        return 'herbal_A'
    elif fnum == 57 and rv == 'v':
        return 'volvelle'
    elif 58 <= fnum <= 67:
        return 'astro'
    elif 68 <= fnum <= 73:
        return 'cosmo'
    elif 75 <= fnum <= 84:
        return 'balnea'
    elif 85 <= fnum <= 102:
        return 'herbal_B'
    elif 103 <= fnum <= 116:
        return 'pharma'
    return 'other'


def get_suffix(word):
    """Extract the EVA suffix from a word. Returns (root, suffix) or (word, None)."""
    if len(word) < 3:
        return word, None
    for s in SUFFIXES:
        if word.endswith(s) and len(word) > len(s):
            return word[:-len(s)], s
    return word, None


@dataclass
class VMSWord:
    """A single word from the VMS with all metadata."""
    eva: str                   # EVA transcription
    folio: str                 # e.g., 'f103r'
    folio_num: int             # e.g., 103
    rv: str                    # 'r' or 'v'
    sub: str                   # sub-folio (e.g., '2' in f85r2)
    section: str               # herbal_A, pharma, balnea, etc.
    line: int                  # line number within folio
    position: int              # word position within line
    total_in_line: int         # total words in this line

    # Derived
    root: str = ''             # root after suffix stripping
    suffix: Optional[str] = None  # EVA suffix (-ol, -edy, -aiin, etc.)
    is_logogram: bool = False  # single-glyph logogram?
    logogram_latin: Optional[str] = None  # Latin value if logogram

    def __post_init__(self):
        self.root, self.suffix = get_suffix(self.eva)
        if self.eva in LOGOGRAMS:
            self.is_logogram = True
            self.logogram_latin = LOGOGRAMS[self.eva]

    @property
    def relative_position(self):
        """Position as fraction of line (0.0=start, 1.0=end)."""
        if self.total_in_line <= 1:
            return 0.5
        return self.position / (self.total_in_line - 1)

    @property
    def is_line_start(self):
        return self.position == 0

    @property
    def is_line_end(self):
        return self.position == self.total_in_line - 1


class VMSCorpus:
    """The complete VMS text parsed into structured words."""

    def __init__(self, filepath=None):
        self.filepath = Path(filepath) if filepath else TRANSCRIPTION_FILE
        self.words: List[VMSWord] = []
        self.word_freq: Counter = Counter()
        self._by_folio: Dict[str, List[VMSWord]] = defaultdict(list)
        self._by_section: Dict[str, List[VMSWord]] = defaultdict(list)
        self._folios_order: List[str] = []

    def load(self):
        """Parse ZL.txt and populate all data structures."""
        with open(self.filepath, encoding='utf-8') as f:
            raw = f.read()

        seen_folios = set()
        for line in raw.split('\n'):
            m = re.match(r'<f(\d+)([rv])(\d?)\.(\d+)', line.strip())
            if not m:
                continue

            fnum = int(m.group(1))
            rv = m.group(2)
            sub = m.group(3)
            lnum = int(m.group(4))
            folio = f'f{fnum}{rv}{sub}'
            section = get_section(fnum, rv)

            # Track folio order
            if folio not in seen_folios:
                seen_folios.add(folio)
                self._folios_order.append(folio)

            # Clean text
            text = re.sub(r'<[^>]*>', '', line.strip())
            text = re.sub(r'<!.*?>', '', text)
            text = text.replace(',', '.').replace('?', '')
            text = re.sub(r'\[[^\]]*:([^\]]*)\]', r'\1', text)
            eva_words = [w for w in re.findall(r'[a-z]+', text) if w]

            for i, eva in enumerate(eva_words):
                word = VMSWord(
                    eva=eva,
                    folio=folio,
                    folio_num=fnum,
                    rv=rv,
                    sub=sub,
                    section=section,
                    line=lnum,
                    position=i,
                    total_in_line=len(eva_words),
                )
                self.words.append(word)
                self.word_freq[eva] += 1
                self._by_folio[folio].append(word)
                self._by_section[section].append(word)

        return self

    # ---- Accessors ----

    def get_folio(self, folio):
        """Get all words on a folio."""
        return self._by_folio.get(folio, [])

    def get_section(self, section):
        """Get all words in a section."""
        return self._by_section.get(section, [])

    def get_herbal(self):
        """Get all herbal words (A + B)."""
        return self._by_section.get('herbal_A', []) + self._by_section.get('herbal_B', [])

    @property
    def folios(self):
        """List of all folios in order."""
        return self._folios_order

    @property
    def sections(self):
        """List of all sections."""
        return list(self._by_section.keys())

    @property
    def unique_words(self):
        """Set of unique EVA words."""
        return set(self.word_freq.keys())

    # ---- Analysis helpers ----

    def word_folios(self, eva_word):
        """Which folios does this word appear on?"""
        return sorted(set(w.folio for w in self.words if w.eva == eva_word))

    def word_sections(self, eva_word):
        """Distribution of this word across sections."""
        c = Counter()
        for w in self.words:
            if w.eva == eva_word:
                c[w.section] += 1
        return c

    def word_context(self, eva_word, window=2):
        """Get context words around each occurrence."""
        contexts = []
        for i, w in enumerate(self.words):
            if w.eva == eva_word:
                before = [self.words[j].eva for j in range(max(0, i - window), i)
                          if self.words[j].folio == w.folio]
                after = [self.words[j].eva for j in range(i + 1, min(len(self.words), i + window + 1))
                         if self.words[j].folio == w.folio]
                contexts.append({'before': before, 'after': after, 'folio': w.folio, 'line': w.line})
        return contexts

    def suffix_distribution(self):
        """Count words by suffix type."""
        c = Counter()
        for w in self.words:
            if w.suffix:
                c[w.suffix] += 1
        return c

    def bigrams(self, section=None):
        """Count word bigrams, optionally filtered by section."""
        bg = Counter()
        words = self._by_section.get(section, self.words) if section else self.words
        for i in range(len(words) - 1):
            if words[i].folio == words[i + 1].folio and words[i].line == words[i + 1].line:
                bg[(words[i].eva, words[i + 1].eva)] += 1
        return bg

    def logogram_neighbors(self):
        """For each known logogram, what words follow/precede it?"""
        result = {}
        for logo in LOGOGRAMS:
            before = Counter()
            after = Counter()
            for i, w in enumerate(self.words):
                if w.eva == logo:
                    if i > 0 and self.words[i - 1].folio == w.folio:
                        before[self.words[i - 1].eva] += 1
                    if i < len(self.words) - 1 and self.words[i + 1].folio == w.folio:
                        after[self.words[i + 1].eva] += 1
            result[logo] = {'latin': LOGOGRAMS[logo], 'before': before.most_common(10), 'after': after.most_common(10)}
        return result

    # ---- Stats ----

    def print_stats(self):
        """Print summary statistics."""
        print("=" * 50)
        print("VMS CORPUS STATISTICS")
        print("=" * 50)
        print(f"Total tokens: {len(self.words)}")
        print(f"Unique words: {len(self.word_freq)}")
        print(f"Folios: {len(self._folios_order)}")
        print(f"Sections: {', '.join(sorted(self._by_section.keys()))}")
        print()
        print("By section:")
        for sec in sorted(self._by_section.keys()):
            n = len(self._by_section[sec])
            print(f"  {sec:12s}: {n:>6d} tokens")
        print()
        print("Logograms:")
        for logo, latin in sorted(LOGOGRAMS.items(), key=lambda x: -self.word_freq.get(x[0], 0)):
            freq = self.word_freq.get(logo, 0)
            if freq > 0:
                print(f"  {logo:>4s} = {latin:<10s} {freq:>5d}x")
        print()
        sfx = self.suffix_distribution()
        print("Suffixes:")
        for s, c in sfx.most_common():
            print(f"  -{s:<5s}: {c:>5d}")


if __name__ == '__main__':
    vms = VMSCorpus()
    vms.load()
    vms.print_stats()
