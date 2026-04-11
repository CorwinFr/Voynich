#!/usr/bin/env python3
"""
Rebuild all 3 corpora integrating:
  1. NEW sources: Dispensarium 1582 (Circa Instans + pharma), Collectio V, Collectio alt
  2. u/v normalization (medieval convention: u medial, v initial)
  3. Improved OCR correction for BALNEA
  4. All existing sources from the first build
"""
import re
import os
import unicodedata
from collections import Counter

RAW_DIR = "/sessions/laughing-jolly-bell/raw_texts"
OUT_DIR = "/sessions/laughing-jolly-bell/corpora_v2"
FINAL_DIR = "/sessions/laughing-jolly-bell/mnt/Voynich FINAL/corpora"
os.makedirs(OUT_DIR, exist_ok=True)

# ============================================================
# LATIN DETECTION
# ============================================================

LATIN_WORDS = set("""
et in de ad est non cum per que sunt si quod sed ut
hoc ex ab vel pro quae enim aut eius ante post inter
haec nam hic nec quam ita quia sic quo atque etiam tamen
super omni omnia esse potest qua ipse autem item contra
suo sua suam suae fuit ubi sive huius eorum ipsa ipsius
idem ideo ergo vero quidem tandem ac ne an num quoque
inde unde hinc illic illo illa qui cuius cui quem quam
quibus hunc hanc huic hos has horum harum
ille illud illius illi illum illam nisi tam iam
nihil semper saepe numquam postea deinde prius
magis minus maxime minime bene male facile
aqua aquae calida calidae virtus virtute herba herbae radix
medicina medicinae morbus morbi febris febre corpus corporis
sanguis sanguinis humor humores calidum frigidum siccum humidum
vinum oleum mel lac succus folia flores semen cortex
libra dragma uncia scrupulus recipe fiat confectio syrupus
stomachus caput oculi dolor capitis ventris pectoris
purgat curat sanat iuvat confert prodest nocet purgatio
matricem renum vesicae epilepsiam paralysim tussim
potio decoctio emplastrum unguentum pillulae electuarium
coque cola distilla tere misce adde pone solve
dosis quantitas temperamentum complexio qualitas gradus
calor frigus humiditas siccitas febres apostema ulcus
plantago artemisia absinthium rosmarinus salvia mentha
aloe mirra cassia cinamomum galanga zedoaria piper
opium balsamum thus camphora mastix gummi
balneum balnea therma thermae fons fontis sudor lavacrum
""".split())

NON_LATIN_STOPS = set("""
the and of to in is that for it this with from are was on but not they all
be at have had has his her she which their there been one our who how what
where when why would could should into more some than other been about also
over such through most then these those between each during above below
een het van de die en in dat met voor dit uit zijn was op den der aan nog
ook als maar wel niet zo dan nu door hij zij naar toe mee zou zal bij tot
haar hem meer werd worden men hun kan over had onder nog zoals alle geen
deze ons wordt maar ook reeds echter altijd hierin hierbij hierna waarna
terwijl omdat wanneer ontbreekt voegt vergeten zooals blijkt volgens wellicht
worden noemd lees woorden aldus doch indien evenwel welke zulk beide niets
veel weinig ander andere hebben hadden heeft hebt zouden kunnen moeten willen
weten noemen doen gaan staan goed groot klein lang dit dat die het twee drie
il la le lo gli una dei delle del nella nel della dello sul sono stato stata
era erano questo questa questi queste anche come dove quando perche molto
tutto tutti tutta tutte altra quello quelli quelle essere avere fare dire
chi che cosa come dove quanto quando quale quali cui tra fra cioe cosi
ancora sempre ogni invece pero quindi della delle degli nelle negli sulle
ossia quindi perciò siccome sebbene affinché benché autore scrittore medico
le la les de du des un une en dans par pour est ce que qui et mais ou donc
car ni avec sur son ses leur leurs nous vous ils elles cette cet dans entre
sous sans après avant depuis pendant tout toute toutes même bien fait dire
der die das ein eine einer eines einem einen von zu und ist den dem des
im am auf an in mit bei aus nach für um aber auch als dann denn noch wenn
sich oder wie so wird wurde wir sie wer was ihr man hab hat sein kann will
nicht nur doch schon mehr alle dem zum zur botan vgl pflanzen pflanze
edition volume page chapter book text manuscript library published printed
édition publié imprimé tome chapitre bibliothèque médecine
""".split())

NOISE_WORDS = set("""
i p c x v ii iii iv vi vii viii ix xi xii xiii xiv xv xvi xx
l m n o s t b d f g h j k r u w y z
bg yy dd bb cc nn mm gg ee ff ll ss rr
silv matth diosc bart plin gal avic nic sim plat
see vgl cfr ed ibid op cit vol tom cap lib
bd bd nr fol ms mss cod codd typ sig
""".split())

VALID_LATIN_ENDINGS = (
    'us', 'um', 'em', 'is', 'es', 'ae', 'am', 'os', 'as', 'a', 'o', 'e', 'i',
    'ium', 'ibus', 'orum', 'arum', 'atur', 'itur', 'etur', 'untur', 'antur',
    'unt', 'ant', 'ent', 'at', 'it', 'et', 'ens', 'ans',
    'ione', 'iones', 'alis', 'ilis', 'ando', 'endo',
    'mus', 'tis', 'atis', 'itis', 'utis',
    'ax', 'ex', 'ix', 'ox', 'ux',
    'men', 'ter', 'ior', 'ius',
    'lis', 'tus', 'tum', 'tor', 'rix',
    'ere', 'ire', 'are',
)


# ============================================================
# TEXT PROCESSING UTILITIES
# ============================================================

def is_likely_latin_line(line, threshold=0.3):
    words = re.findall(r'[a-z]+', line.lower())
    if len(words) < 3:
        return False
    latin_count = sum(1 for w in words if w in LATIN_WORDS)
    non_latin_count = sum(1 for w in words if w in NON_LATIN_STOPS)
    if non_latin_count > latin_count and non_latin_count >= 2:
        return False
    if latin_count / len(words) >= threshold:
        return True
    latin_endings = sum(1 for w in words if len(w) > 3 and
                       w.endswith(('um', 'us', 'is', 'em', 'ae', 'am', 'ium',
                                   'ibus', 'orum', 'arum', 'atur', 'itur',
                                   'unt', 'ant', 'ens', 'ent', 'ione',
                                   'alis', 'ilis', 'ando', 'endo')))
    if latin_endings / len(words) >= 0.25:
        return True
    return False


def clean_text(text, remove_apparatus=True):
    text = unicodedata.normalize('NFC', text)
    text = text.replace('æ', 'ae').replace('œ', 'oe')
    text = text.replace('Æ', 'ae').replace('Œ', 'oe')
    text = text.replace('ſ', 's')
    if remove_apparatus:
        lines = text.split('\n')
        cleaned = []
        for line in lines:
            line = line.strip()
            if re.match(r'^\d+\)\s', line):
                continue
            if re.match(r'^[\*†‡§]\s', line):
                continue
            if re.match(r'^\d+\s*$', line):
                continue
            cleaned.append(line)
        text = '\n'.join(cleaned)
    return text


def normalize_latin(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def uv_normalize(text):
    """Medieval u/v normalization: v initial, u medial.
    In medieval Latin manuscripts: 'v' was used at the start of words,
    'u' was used in the middle of words, regardless of consonant/vowel value.
    """
    words = text.split()
    normalized = []
    for w in words:
        if len(w) < 2:
            normalized.append(w)
            continue
        # Initial position: u -> v if followed by a vowel (vinum, virtus, vel)
        # But keep 'u' if followed by consonant and it's clearly a vowel (ut, ubi, unde)
        # Medial position: v -> u (always)
        chars = list(w)
        for i in range(1, len(chars)):
            if chars[i] == 'v':
                chars[i] = 'u'
        # Initial v stays v, initial u stays u for common words
        # Actually, the simplest medieval convention: medial v -> u only
        normalized.append(''.join(chars))
    return ' '.join(normalized)


def fix_16c_ocr(text):
    """Fix systematic OCR errors from 16th century typefaces"""
    ocr_fixes = [
        (r'\beft\b', 'est'), (r'\bcft\b', 'est'),
        (r'\bfi\b', 'si'), (r'\bfed\b', 'sed'), (r'\bfic\b', 'sic'),
        (r'\bfine\b', 'sine'), (r'\bfunt\b', 'sunt'), (r'\bfub\b', 'sub'),
        (r'\bfuper\b', 'super'), (r'\bfupra\b', 'supra'),
        (r'\bfatis\b', 'satis'), (r'\bfecundum\b', 'secundum'),
        (r'\bfimilis\b', 'similis'), (r'\bfimiliter\b', 'similiter'),
        (r'\bfpecies\b', 'species'), (r'\bfpiritus\b', 'spiritus'),
        (r'\bftomachus\b', 'stomachus'), (r'\bfanguinis\b', 'sanguinis'),
        (r'\bfanguis\b', 'sanguis'), (r'\bfoluit\b', 'soluit'),
        (r'\bfuccus\b', 'succus'), (r'\bfalutem\b', 'salutem'),
        (r'\bfalubris\b', 'salubris'), (r'\bfanitas\b', 'sanitas'),
        (r'\bfanitatis\b', 'sanitatis'), (r'\bfciendum\b', 'sciendum'),
        (r'\bfcribit\b', 'scribit'), (r'\bfemper\b', 'semper'),
        (r'\bfenfu\b', 'sensu'), (r'\bfenfus\b', 'sensus'),
        (r'\bfubtilis\b', 'subtilis'), (r'\bfubftantia\b', 'substantia'),
        (r'\bvt\b', 'ut'), (r'\bdc\b', 'de'), (r'\bcx\b', 'ex'),
        (r'\bpcr\b', 'per'),
        (r'\bficcum\b', 'siccum'), (r'\bficcitas\b', 'siccitas'),
        (r'\bfulphur\b', 'sulphur'), (r'\bfal\b', 'sal'), (r'\bfalis\b', 'salis'),
        # Additional patterns identified
        (r'\bfolent\b', 'solent'), (r'\bfolutio\b', 'solutio'),
        (r'\bfudor\b', 'sudor'), (r'\bfudoris\b', 'sudoris'),
        (r'\bfulphureum\b', 'sulphureum'), (r'\bfulfur\b', 'sulfur'),
        (r'\bfufficiens\b', 'sufficiens'), (r'\bfufficit\b', 'sufficit'),
        (r'\bfubmergi\b', 'submergi'), (r'\bfucceffiue\b', 'successive'),
        (r'\bfapientia\b', 'sapientia'), (r'\bfapor\b', 'sapor'),
        (r'\bfaporis\b', 'saporis'), (r'\bfolida\b', 'solida'),
        (r'\bfolidus\b', 'solidus'),
        (r'\bftagnum\b', 'stagnum'), (r'\bftare\b', 'stare'),
        (r'\bftomachi\b', 'stomachi'), (r'\bftudium\b', 'studium'),
    ]
    for pattern, replacement in ocr_fixes:
        text = re.sub(pattern, replacement, text)
    return text


def is_valid_latin_window(words, strict=False):
    if len(words) < 3:
        return False
    latin_count = 0
    non_latin_count = 0
    for w in words:
        if w in LATIN_WORDS:
            latin_count += 2
        elif w in NON_LATIN_STOPS:
            non_latin_count += 3
        elif len(w) > 3:
            if w.endswith(VALID_LATIN_ENDINGS):
                latin_count += 1
        elif len(w) <= 2:
            pass
    total = latin_count + non_latin_count + 1
    score = latin_count / total
    if strict:
        return score > 0.5 and non_latin_count < 2
    else:
        return score > 0.35 and non_latin_count <= 2


def window_filter(text, strict=False, apply_ocr_fix=False):
    """Apply sliding window Latin validation"""
    if apply_ocr_fix:
        text = fix_16c_ocr(text)
    words = text.split()
    window_size = 15
    step = 15
    good_words = []
    i = 0
    while i < len(words):
        window = words[i:i + window_size]
        if is_valid_latin_window(window, strict=strict):
            good_words.extend(window)
        i += step
    return ' '.join(good_words)


def quality_clean(text):
    """Remove noise words, abbreviations, non-Latin remnants"""
    words = text.split()
    cleaned = []
    for w in words:
        if w in NOISE_WORDS:
            continue
        if len(w) < 2:
            continue
        if re.search(r'\d', w):
            continue
        if len(w) > 3 and not re.search(r'[aeiou]', w):
            continue
        cleaned.append(w)
    result = ' '.join(cleaned)
    result = re.sub(r'\b(\w+)\s+\1\b', r'\1', result)
    result = re.sub(r'\s+', ' ', result).strip()
    return result


def extract_latin_from_raw(filepath, threshold=0.25, min_line_len=5):
    """Generic Latin extraction from a raw text file"""
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()
    lines = text.split('\n')
    latin_lines = []
    for line in lines:
        line = line.strip()
        if not line or len(line) < min_line_len:
            continue
        if is_likely_latin_line(line, threshold=threshold):
            latin_lines.append(line)
    text = '\n'.join(latin_lines)
    text = clean_text(text)
    return normalize_latin(text)


# ============================================================
# SOURCE PROCESSORS (existing + new)
# ============================================================

def process_macer_floridus():
    print("  [HERBAL] Macer Floridus...")
    filepath = os.path.join(RAW_DIR, 'macer_floridus_raw.txt')
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()
    start_marker = "Herbarum quasdam dicturus carmine vires"
    start_idx = text.find(start_marker)
    if start_idx == -1:
        print("    ERROR: Cannot find start marker")
        return ""
    text = text[start_idx:]
    lines = text.split('\n')
    verse_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if re.match(r'^\d+\s+(Herbar|[A-Z][a-z]*\.|cfr\.|Cfr\.)', line):
            continue
        if re.match(r'^\d+\s+\w+\s+codd\.|vett\.\s+editt', line):
            continue
        lower = line.lower()
        german_markers = ['botan.', 'cfr.', 'diosc.', 'plin.', 'vgl.', 'vid.', 'ed.']
        if any(m in lower for m in german_markers) and not any(w in lower for w in ['herba', 'radix', 'folia']):
            continue
        if any(ord(c) > 0x0370 and ord(c) < 0x0400 for c in line):
            continue
        if re.match(r'^[IVXLC]+\.\s*[A-Z]+\.?\s*$', line):
            continue
        if len(line) > 10:
            verse_lines.append(line)
    text = '\n'.join(verse_lines)
    text = clean_text(text)
    return normalize_latin(text)


def process_alphita():
    print("  [HERBAL] Alphita glossary...")
    filepath = os.path.join(RAW_DIR, 'alphita_raw.txt')
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()
    lines = text.split('\n')
    glossary_lines = []
    in_glossary = False
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if 'ABSINTHIUM' in line or 'Absinthium' in line:
            in_glossary = True
        if not in_glossary:
            continue
        words = line.lower().split()
        eng_count = sum(1 for w in words if w in NON_LATIN_STOPS)
        if eng_count > len(words) * 0.4:
            continue
        glossary_lines.append(line)
    text = '\n'.join(glossary_lines)
    text = clean_text(text)
    return normalize_latin(text)


def process_flos_medicinae():
    print("  [HERBAL] Flos Medicinae...")
    flos_path = "/sessions/laughing-jolly-bell/mnt/Voynich FINAL/Flos medicinae Scholae Salerni.txt"
    if not os.path.exists(flos_path):
        print("    File not found")
        return ""
    with open(flos_path, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()
    lines = text.split('\n')
    latin_lines = [l.strip() for l in lines if l.strip() and len(l.strip()) > 10 and is_likely_latin_line(l)]
    text = '\n'.join(latin_lines)
    text = clean_text(text)
    return normalize_latin(text)


def process_dispensarium_herbal():
    """NEW: Extract Circa Instans section from Dispensarium 1582 (lines 44000+)"""
    print("  [HERBAL] Dispensarium 1582 -> Circa Instans (De Simplici Medicina)...")
    filepath = os.path.join(RAW_DIR, 'dispensarium_1582_raw.txt')
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        all_lines = f.readlines()

    # The Circa Instans / De Simplici Medicina section starts around line 44000
    # Take everything from line 44000 onwards
    ci_lines = all_lines[43999:]  # 0-indexed
    print(f"    Circa Instans section: {len(ci_lines)} lines from line 44000")

    latin_lines = []
    for line in ci_lines:
        line = line.strip()
        if not line or len(line) < 5:
            continue
        if is_likely_latin_line(line, threshold=0.2):
            latin_lines.append(line)

    text = '\n'.join(latin_lines)
    text = clean_text(text)
    result = normalize_latin(text)
    print(f"    Extracted: {len(result.split())} words")
    return result


def process_antidotarium_nicolai():
    print("  [PHARMA] Antidotarium Nicolai...")
    filepath = os.path.join(RAW_DIR, 'antidotarium_nicolai_raw.txt')
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()
    lines = text.split('\n')
    latin_lines = []
    for line in lines:
        line = line.strip()
        if not line or len(line) < 5:
            continue
        dutch_markers = ['ontbreekt', 'voegt', 'hiervan', 'wordt', 'hierna',
                        'volgens', 'vergeten', 'zooals', 'blijkt', 'staat',
                        'lees', 'wellicht']
        if any(m in line.lower() for m in dutch_markers):
            continue
        if re.match(r'^\d+\)\s*(zie|tot|deze|er\s+staat|ontbreekt|hiervan)', line, re.I):
            continue
        if re.match(r'^fol\.\s*\d', line):
            continue
        if is_likely_latin_line(line, threshold=0.2):
            latin_lines.append(line)
        elif any(term in line.lower() for term in ['recipe', 'confectio', 'libr',
                'dragma', 'uncia', 'electuarium', 'syrupus', 'pillulae',
                'dosis', 'fiat', 'coque', 'cole', 'dissolve']):
            latin_lines.append(line)
    text = '\n'.join(latin_lines)
    text = clean_text(text)
    return normalize_latin(text)


def process_collectio_salernitana(vol_num):
    print(f"  [PHARMA] Collectio Salernitana Vol. {vol_num}...")
    filepath = os.path.join(RAW_DIR, f'collectio_sal_v{vol_num}_raw.txt')
    if not os.path.exists(filepath):
        print(f"    File not found: {filepath}")
        return ""
    return extract_latin_from_raw(filepath, threshold=0.25)


def process_collectio_alt():
    """NEW: Process alternative Collectio Salernitana digitization"""
    print("  [PHARMA] Collectio Salernitana (alt digitization)...")
    filepath = os.path.join(RAW_DIR, 'collectio_sal_alt_raw.txt')
    if not os.path.exists(filepath):
        print("    File not found")
        return ""
    return extract_latin_from_raw(filepath, threshold=0.25)


def process_dispensarium_pharma():
    """NEW: Extract pharma section from Dispensarium 1582 (lines 1-44000)"""
    print("  [PHARMA] Dispensarium 1582 -> Pharma section (Dispensarium proper)...")
    filepath = os.path.join(RAW_DIR, 'dispensarium_1582_raw.txt')
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        all_lines = f.readlines()

    # Pharma section is the first ~44000 lines (Dispensarium proper)
    pharma_lines = all_lines[:44000]
    print(f"    Pharma section: {len(pharma_lines)} lines")

    latin_lines = []
    for line in pharma_lines:
        line = line.strip()
        if not line or len(line) < 5:
            continue
        if is_likely_latin_line(line, threshold=0.2):
            latin_lines.append(line)

    text = '\n'.join(latin_lines)
    text = clean_text(text)
    result = normalize_latin(text)
    print(f"    Extracted: {len(result.split())} words")
    return result


def process_de_balneis_1553():
    print("  [BALNEA] De Balneis 1553...")
    filepath = os.path.join(RAW_DIR, 'de_balneis_1553_raw.txt')
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()
    lines = text.split('\n')
    latin_lines = []
    for line in lines:
        line = line.strip()
        if not line or len(line) < 5:
            continue
        if is_likely_latin_line(line, threshold=0.2):
            latin_lines.append(line)
    text = '\n'.join(latin_lines)
    text = clean_text(text)
    return normalize_latin(text)


def process_guaineri():
    print("  [BALNEA] Guaineri De Balneis...")
    from bs4 import BeautifulSoup
    filepath = os.path.join(RAW_DIR, 'guaineri_de_balneis.html')
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        html = f.read()
    soup = BeautifulSoup(html, 'html.parser')
    content = soup.find('div', class_='entry-content') or soup.find('article') or soup.find('body')
    text = content.get_text(separator='\n') if content else soup.get_text(separator='\n')
    lines = text.split('\n')
    latin_lines = []
    for line in lines:
        line = line.strip()
        if not line or len(line) < 5:
            continue
        if any(eng in line.lower() for eng in ['click here', 'posted', 'comment', 'share', 'menu', 'search', 'home', 'about', 'contact']):
            continue
        if is_likely_latin_line(line, threshold=0.2):
            latin_lines.append(line)
    text = '\n'.join(latin_lines)
    text = clean_text(text)
    return normalize_latin(text)


def process_regimen_sanitatis():
    print("  [BALNEA] Regimen Sanitatis Salernitanum...")
    texts = []
    for fname in ['regimen_sanitatis_raw.txt', 'regimen_sanitatis_croke_raw.txt']:
        filepath = os.path.join(RAW_DIR, fname)
        if not os.path.exists(filepath):
            continue
        texts.append(extract_latin_from_raw(filepath, threshold=0.25))
    return ' '.join(texts)


# ============================================================
# FULL PIPELINE
# ============================================================

def build_and_clean(name, raw_texts, strict=False, apply_ocr_fix=False):
    """Combine raw extractions, apply window filter, quality clean, uv normalize"""
    # Combine
    combined = ' '.join(t for t in raw_texts if t)
    combined = re.sub(r'\s+', ' ', combined).strip()
    raw_wc = len(combined.split())
    print(f"\n  {name} - Raw combined: {raw_wc:,} words")

    # Window filter
    filtered = window_filter(combined, strict=strict, apply_ocr_fix=apply_ocr_fix)
    filt_wc = len(filtered.split())
    print(f"  {name} - After window filter: {filt_wc:,} words ({filt_wc/raw_wc*100:.1f}% kept)")

    # Quality clean
    cleaned = quality_clean(filtered)
    clean_wc = len(cleaned.split())
    print(f"  {name} - After quality clean: {clean_wc:,} words")

    # u/v normalization
    normalized = uv_normalize(cleaned)
    final_wc = len(normalized.split())
    print(f"  {name} - After u/v normalization: {final_wc:,} words")

    return normalized, final_wc


def show_quality(text, name):
    words = text.split()
    wc = len(words)
    freq = Counter(words)
    unique = len(freq)

    print(f"\n  === {name} QUALITY ===")
    print(f"  Words: {wc:,} | Unique: {unique:,} | Ratio: {unique/wc:.3f}")

    top20 = ', '.join(f'{w}({c})' for w, c in freq.most_common(20))
    print(f"  Top 20: {top20}")

    # Samples at various positions
    positions = [0, 500, 5000, 20000, 50000, 100000, wc - 50]
    for pos in positions:
        if 0 <= pos < wc - 20:
            sample = ' '.join(words[pos:pos+25])
            print(f"  [{pos:>7}] {sample}")

    # Medical vocabulary check
    med_vocab = {
        'HERBAL': ['herba', 'herbae', 'radix', 'folia', 'succus', 'semen', 'flores', 'cortex', 'calida', 'frigida'],
        'PHARMA': ['recipe', 'coque', 'confectio', 'electuarium', 'syrupus', 'dragma', 'uncia', 'pillulae', 'fiat', 'dissolue'],
        'BALNEA': ['aqua', 'balneum', 'balnea', 'calida', 'therma', 'sudor', 'lauacrum', 'frigida', 'fontis', 'fons'],
    }
    vocab = med_vocab.get(name, [])
    found = [(w, freq.get(w, 0)) for w in vocab if freq.get(w, 0) > 0]
    found.sort(key=lambda x: -x[1])
    if found:
        print(f"  Key vocab: {', '.join(f'{w}({c})' for w, c in found)}")


if __name__ == '__main__':
    print("=" * 65)
    print("CORPUS REBUILD v2 - WITH NEW SOURCES + U/V NORMALIZATION")
    print("=" * 65)

    # ============================================================
    # HERBAL: existing (Macer, Alphita, Flos) + NEW (Circa Instans from Dispensarium)
    # ============================================================
    print("\n--- HERBAL CORPUS ---")
    herbal_texts = [
        process_macer_floridus(),
        process_alphita(),
        process_flos_medicinae(),
        process_dispensarium_herbal(),  # NEW
    ]
    herbal_text, herbal_wc = build_and_clean("HERBAL", herbal_texts, strict=False)

    # ============================================================
    # PHARMA: existing (Antidotarium, Collectio I-IV) + NEW (Dispensarium pharma, Collectio V, Collectio alt)
    # ============================================================
    print("\n--- PHARMA CORPUS ---")
    pharma_texts = [
        process_antidotarium_nicolai(),
        process_collectio_salernitana(1),
        process_collectio_salernitana(2),
        process_collectio_salernitana(3),
        process_collectio_salernitana(4),
        process_dispensarium_pharma(),   # NEW
        process_collectio_salernitana(5),  # NEW
        process_collectio_alt(),          # NEW
    ]
    pharma_text, pharma_wc = build_and_clean("PHARMA", pharma_texts, strict=True)

    # ============================================================
    # BALNEA: existing (De Balneis 1553, Guaineri, Regimen Sanitatis) - with OCR fix
    # ============================================================
    print("\n--- BALNEA CORPUS ---")
    balnea_texts = [
        process_de_balneis_1553(),
        process_guaineri(),
        process_regimen_sanitatis(),
    ]
    balnea_text, balnea_wc = build_and_clean("BALNEA", balnea_texts, strict=False, apply_ocr_fix=True)

    # ============================================================
    # SAVE AND REPORT
    # ============================================================
    print("\n" + "=" * 65)
    print("SAVING CORPORA")
    print("=" * 65)

    for name, text in [('herbal', herbal_text), ('pharma', pharma_text), ('balnea', balnea_text)]:
        out_path = os.path.join(FINAL_DIR, f'corpus_{name}.txt')
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"  Saved: {out_path}")

    # Quality reports
    print("\n" + "=" * 65)
    print("QUALITY ANALYSIS")
    print("=" * 65)
    show_quality(herbal_text, "HERBAL")
    show_quality(pharma_text, "PHARMA")
    show_quality(balnea_text, "BALNEA")

    # Final summary
    print("\n" + "=" * 65)
    print("FINAL RESULTS")
    print("=" * 65)
    total = herbal_wc + pharma_wc + balnea_wc
    targets = {'HERBAL': '200K-500K', 'PHARMA': '200K-500K', 'BALNEA': '50K-200K'}
    for name, wc in [('HERBAL', herbal_wc), ('PHARMA', pharma_wc), ('BALNEA', balnea_wc)]:
        tgt = targets[name]
        if name == 'BALNEA':
            status = 'OK' if wc >= 50000 else 'BELOW TARGET'
        else:
            status = 'OK' if wc >= 200000 else 'BELOW TARGET'
        print(f"  {name:8s}: {wc:>10,} words  (target: {tgt})  [{status}]")
    print(f"  {'TOTAL':8s}: {total:>10,} words")
    print(f"\n  u/v normalization: APPLIED (medial v -> u)")
