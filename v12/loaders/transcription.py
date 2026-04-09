"""
IVTFF/ZL transcription parser.
Reads Zandbergen-Landini v2b format and extracts folio text.
"""
import re
from typing import Optional


def parse_folio(zl_path: str, target_folio: str) -> tuple[dict[int, list[str]], Optional[str]]:
    """
    Parse a specific folio from ZL transcription.

    Returns:
        (lines, section) where lines = {line_num: [eva_word, ...]},
        section = illustration type (H=herbal, A=astro, B=bio, P=pharma, etc.)
    """
    lines: dict[int, list[str]] = {}
    current_section: Optional[str] = None

    with open(zl_path, 'r', encoding='utf-8') as f:
        for raw_line in f:
            stripped = raw_line.strip()

            # Folio header: <f1r> <! ...>
            header = re.match(r'<(f\d+[rv]\d?)>\s+<!\s*(.*?)>', stripped)
            if header:
                fid = header.group(1)
                meta = header.group(2)
                sec_match = re.search(r'\$I=(\w)', meta)
                if fid == target_folio or fid.startswith(target_folio):
                    current_section = sec_match.group(1) if sec_match else '?'
                continue

            # Text line: <f1r.1, ...> text
            line_match = re.match(r'<(f\d+[rv]\d?)\.(\d+)', stripped)
            if not line_match:
                continue

            folio = line_match.group(1)
            if folio != target_folio:
                continue

            # Clean the text: remove markup
            text = re.sub(r'<[^>]*>', '', stripped)
            text = re.sub(r'<!.*?>', '', text)
            text = re.sub(r'<%>|<\$>|\{[^}]*\}|@\d+;', '', text)
            # Resolve alternative readings: [alt1:alt2] → alt2
            text = re.sub(r'\[([^\]]*):([^\]]*)\]', r'\2', text)
            text = re.sub(r'\?', '', text)
            text = text.replace(',', '.')

            lnum = int(line_match.group(2))
            words = []
            for w in re.findall(r'[a-z.]+', text):
                for part in w.split('.'):
                    clean = part.strip()
                    if clean:
                        words.append(clean)

            if words:
                lines[lnum] = words

    return lines, current_section


def list_folios(zl_path: str) -> list[tuple[str, str]]:
    """List all folio IDs and their section types."""
    folios = []
    with open(zl_path, 'r', encoding='utf-8') as f:
        for raw_line in f:
            header = re.match(r'<(f\d+[rv]\d?)>\s+<!\s*(.*?)>', raw_line.strip())
            if header:
                fid = header.group(1)
                meta = header.group(2)
                sec_match = re.search(r'\$I=(\w)', meta)
                section = sec_match.group(1) if sec_match else '?'
                folios.append((fid, section))
    return folios


def parse_all_words(zl_path: str) -> list[str]:
    """Extract all EVA words from the entire manuscript."""
    all_words = []
    with open(zl_path, 'r', encoding='utf-8') as f:
        for raw_line in f:
            line_match = re.match(r'<f\d+[rv]\d?\.\d+', raw_line.strip())
            if not line_match:
                continue
            text = re.sub(r'<[^>]*>', '', raw_line.strip())
            text = re.sub(r'<!.*?>', '', text)
            text = re.sub(r'<%>|<\$>|\{[^}]*\}|@\d+;', '', text)
            text = re.sub(r'\[([^\]]*):([^\]]*)\]', r'\2', text)
            text = re.sub(r'\?', '', text).replace(',', '.')
            for w in re.findall(r'[a-z.]+', text):
                for part in w.split('.'):
                    clean = part.strip()
                    if clean:
                        all_words.append(clean)
    return all_words
