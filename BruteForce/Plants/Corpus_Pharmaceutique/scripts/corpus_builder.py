#!/usr/bin/env python3
"""
Medieval Medical Latin Corpus Builder
Downloads and processes texts from archive.org and other sources
for the Voynich Manuscript decoding project.
"""

import requests
import re
import os
import unicodedata
import time

WORK_DIR = "/sessions/laughing-jolly-bell/raw_texts"
os.makedirs(WORK_DIR, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Research Project - Medieval Latin Corpus)'
}

def download_text(url, filename, description=""):
    """Download text from URL and save to file"""
    filepath = os.path.join(WORK_DIR, filename)
    if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
        print(f"  [SKIP] {filename} already exists ({os.path.getsize(filepath)} bytes)")
        return filepath

    print(f"  [DOWNLOAD] {description or filename}...")
    try:
        resp = requests.get(url, headers=HEADERS, timeout=120)
        resp.raise_for_status()
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(resp.text)
        print(f"  [OK] {len(resp.text)} chars saved to {filename}")
        return filepath
    except Exception as e:
        print(f"  [ERROR] {e}")
        return None

def clean_latin_text(text):
    """
    Clean text to extract Latin content:
    - Remove page numbers and headers
    - Remove OCR artifacts
    - Normalize characters
    - Lowercase
    - Remove punctuation except spaces
    """
    # Normalize unicode
    text = unicodedata.normalize('NFC', text)

    # Remove common OCR artifacts and non-Latin characters
    # Remove lines that are just numbers (page numbers)
    lines = text.split('\n')
    cleaned_lines = []

    for line in lines:
        line = line.strip()

        # Skip empty lines
        if not line:
            continue

        # Skip lines that are just numbers (page numbers)
        if re.match(r'^\d+\s*$', line):
            continue

        # Skip lines that are just punctuation/symbols
        if re.match(r'^[\W\d]+$', line):
            continue

        # Skip very short lines (likely OCR noise)
        if len(line) < 3:
            continue

        cleaned_lines.append(line)

    text = ' '.join(cleaned_lines)

    # Remove common non-Latin elements
    # Remove text in brackets (editorial notes)
    text = re.sub(r'\[.*?\]', ' ', text)

    # Remove numbers
    text = re.sub(r'\d+', ' ', text)

    # Remove punctuation but keep spaces
    text = re.sub(r'[^\w\s]', ' ', text)

    # Lowercase
    text = text.lower()

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def is_latin_word(word):
    """Basic check if a word looks like it could be Latin"""
    # Must be at least 2 chars
    if len(word) < 2:
        return False
    # Must be alphabetic
    if not word.isalpha():
        return False
    # Common Latin letter patterns
    return True


def filter_latin_words(text):
    """Filter to keep only likely Latin words"""
    words = text.split()
    # Keep words that look Latin (basic ASCII letters, common Latin patterns)
    latin_words = []
    for w in words:
        # Remove any remaining non-alpha chars
        w = re.sub(r'[^a-z]', '', w)
        if len(w) >= 2 and w.isalpha():
            latin_words.append(w)
    return ' '.join(latin_words)


# ============================================================
# SOURCES TO DOWNLOAD
# ============================================================

SOURCES = {
    # HERBAL CORPUS
    'herbal': [
        {
            'name': 'Macer Floridus - De viribus herbarum (Choulant 1832)',
            'url': 'https://archive.org/stream/deviribusherbaru00mace/deviribusherbaru00mace_djvu.txt',
            'filename': 'macer_floridus_djvu.txt',
            'type': 'herbal',
            'date': 'XIe siecle (ed. 1832)',
        },
        {
            'name': 'Alphita - Glossaire medico-botanique (Mowat 1887)',
            'url': 'https://archive.org/stream/b21463955/b21463955_djvu.txt',
            'filename': 'alphita_mowat_djvu.txt',
            'type': 'herbal',
            'date': 'XIIIe siecle (ed. 1887)',
        },
    ],
    # PHARMA CORPUS
    'pharma': [
        {
            'name': 'Antidotarium Nicolai (van den Berg 1917)',
            'url': 'https://archive.org/stream/eenemiddelnederl00nicouoft/eenemiddelnederl00nicouoft_djvu.txt',
            'filename': 'antidotarium_nicolai_vdberg_djvu.txt',
            'type': 'pharma',
            'date': 'XIIe siecle (ed. 1917)',
        },
        {
            'name': 'Collectio Salernitana Vol. I (De Renzi)',
            'url': 'https://archive.org/stream/BIUSante_34887x01/BIUSante_34887x01_djvu.txt',
            'filename': 'collectio_salernitana_v1_djvu.txt',
            'type': 'pharma',
            'date': '1852',
        },
        {
            'name': 'Collectio Salernitana Vol. II (De Renzi)',
            'url': 'https://archive.org/stream/bub_gb_WSoEmOJJBUAC/bub_gb_WSoEmOJJBUAC_djvu.txt',
            'filename': 'collectio_salernitana_v2_djvu.txt',
            'type': 'pharma',
            'date': '1852-1859',
        },
        {
            'name': 'Collectio Salernitana Vol. III (De Renzi)',
            'url': 'https://archive.org/stream/collectiosalern04salegoog/collectiosalern04salegoog_djvu.txt',
            'filename': 'collectio_salernitana_v3_djvu.txt',
            'type': 'pharma',
            'date': '1854',
        },
        {
            'name': 'Collectio Salernitana Vol. IV (De Renzi)',
            'url': 'https://archive.org/stream/BIUSante_34887x04/BIUSante_34887x04_djvu.txt',
            'filename': 'collectio_salernitana_v4_djvu.txt',
            'type': 'pharma',
            'date': '1855',
        },
    ],
    # BALNEA CORPUS
    'balnea': [
        {
            'name': 'De Balneis omnia (Venice 1553)',
            'url': 'https://archive.org/stream/bub_gb_fhNVl_wrMh0C/bub_gb_fhNVl_wrMh0C_djvu.txt',
            'filename': 'de_balneis_1553_djvu.txt',
            'type': 'balnea',
            'date': '1553',
        },
        {
            'name': 'Regimen Sanitatis Salernitanum (Harington edition)',
            'url': 'https://archive.org/stream/schoolofsalernum00hariiala/schoolofsalernum00hariiala_djvu.txt',
            'filename': 'regimen_sanitatis_harington_djvu.txt',
            'type': 'balnea',
            'date': 'XIe-XIIe siecle',
        },
        {
            'name': 'Regimen Sanitatis (Croke edition)',
            'url': 'https://archive.org/stream/b29337446/b29337446_djvu.txt',
            'filename': 'regimen_sanitatis_croke_djvu.txt',
            'type': 'balnea',
            'date': 'XIe-XIIe siecle (ed. 1830)',
        },
        {
            'name': 'Guaineri De Balneis (transcription)',
            'url': 'http://cipherfoundation.org/older-ciphers/voynich-manuscript/antonio-guaineris-de-balneis/',
            'filename': 'guaineri_de_balneis.html',
            'type': 'balnea',
            'date': 'XVe siecle',
        },
    ],
}

if __name__ == '__main__':
    print("=" * 60)
    print("MEDIEVAL MEDICAL LATIN CORPUS BUILDER")
    print("=" * 60)

    for corpus_name, sources in SOURCES.items():
        print(f"\n--- {corpus_name.upper()} CORPUS ---")
        for src in sources:
            filepath = download_text(src['url'], src['filename'], src['name'])
            if filepath:
                size = os.path.getsize(filepath)
                print(f"  File size: {size:,} bytes")
            time.sleep(1)  # Be polite to servers

    print("\n\nAll downloads complete.")
    print(f"Files saved to: {WORK_DIR}")

    # List downloaded files
    print("\nDownloaded files:")
    for f in sorted(os.listdir(WORK_DIR)):
        size = os.path.getsize(os.path.join(WORK_DIR, f))
        print(f"  {f}: {size:,} bytes")
