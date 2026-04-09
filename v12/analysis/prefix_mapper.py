"""
Prefix Mapper — Map recurring EVA word-initial patterns to Latin roots.
Goal: discover the author's compression system by finding systematic
prefix -> meaning correspondences.

Strategy:
1. Extract all EVA word prefixes (2-3 glyphs)
2. For each prefix, collect all decoded Latin forms
3. Identify prefixes that consistently map to the same Latin root
4. Cross-reference with botanical/pharmaceutical terms
"""
import sys, os, json, re
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from v12.config import Config
from v12.pipeline import VoynichPipeline
from v12.loaders.transcription import list_folios, parse_folio


# Known botanical/pharma roots to watch for
ROOTS_OF_INTEREST = {
    'inel': 'INULA (Elecampane/Aunee)',
    'cic': 'CICHORIUM (Chicoree) or CICUTA (Cigue)',
    'coqu': 'COQUERE (cuire)',
    'hier': 'HIERA (remede sacre)',
    'alo': 'ALOES (aloes)',
    'rec': 'RECIPE (prends)',
    'aqu': 'AQUA (eau)',
    'tur': 'THUS/TURE (encens)',
    'cro': 'CROCUS (safran)',
    'cos': 'COSTUS (costus)',
    'sen': 'SENECIO (senecon)',
    'cur': 'CURA/CURCUMA',
    'pip': 'PIPER (poivre)',
    'sal': 'SALVIA (sauge)',
    'ros': 'ROSA/ROSMARINUS',
    'lil': 'LILIUM (lis)',
    'men': 'MENTHA (menthe)',
    'rut': 'RUTA (rue)',
    'mal': 'MALVA (mauve)',
    'art': 'ARTEMISIA (armoise)',
    'gen': 'GENTIANA (gentiane)',
    'lav': 'LAVANDULA (lavande)',
    'val': 'VALERIANA (valeriane)',
    'verb': 'VERBENA (verveine)',
    'viol': 'VIOLA (violette)',
    'mand': 'MANDRAGORA (mandragore)',
    'pap': 'PAPAVER (pavot)',
    'hell': 'HELLEBORUS (ellebore)',
    'eup': 'EUPATORIUM/EUPHORBIA',
    'orig': 'ORIGANUM (origan)',
    'cum': 'CUMINUM (cumin)',
    'fen': 'FENICULUM (fenouil)',
    'anis': 'ANISUM (anis)',
    'cinn': 'CINNAMOMUM (cannelle)',
    'myrrh': 'MYRRHA (myrrhe)',
    'mast': 'MASTIX (mastic)',
    'nard': 'NARDUS (nard)',
    'cam': 'CAMOMILLA (camomille)',
    'elect': 'ELECTUARIUM (electuaire)',
    'olib': 'OLIBANUM (encens)',
    'scam': 'SCAMMONIA',
    'aspar': 'ASPARAGUS',
    'beton': 'BETONICA',
    'borag': 'BORAGO',
    'pul': 'PULEGIUM (pouliot)',
    'absin': 'ABSINTHIUM (absinthe)',
    'plan': 'PLANTAGO (plantain)',
    'urtic': 'URTICA (ortie)',
    'sambuc': 'SAMBUCUS (sureau)',
    'opio': 'OPIUM (pavot)',
    'galang': 'GALANGA',
    'zingi': 'ZINGIBER (gingembre)',
    'aper': 'APERIENS (ouvrant)',
    'coll': 'COLLIGENS (cueillant)',
    'elic': 'ELICIENS (extrayant)',
    'dolor': 'DOLOR (douleur)',
    'febr': 'FEBRIS (fievre)',
    'morb': 'MORBUS (maladie)',
    'lib': 'LIBRA (livre/poids)',
    'unc': 'UNCIA (once)',
    'drach': 'DRACHMA',
    'equal': 'EQUALITER (egalement)',
    'balne': 'BALNEUM (bain)',
    'foli': 'FOLIA (feuilles)',
    'radic': 'RADIX (racine)',
    'sem': 'SEMEN (graine)',
    'flor': 'FLOS (fleur)',
    'cort': 'CORTEX (ecorce)',
    'succ': 'SUCCUS (jus)',
}


def extract_prefix(eva_word: str, length: int = 2) -> str:
    """Extract first N glyphs from EVA word."""
    # EVA multigraphs: ch, sh, ck, ct, cf, cp
    glyphs = []
    i = 0
    while i < len(eva_word) and len(glyphs) < length:
        if i + 1 < len(eva_word) and eva_word[i:i+2] in ('ch', 'sh', 'ck', 'ct', 'cf', 'cp'):
            glyphs.append(eva_word[i:i+2])
            i += 2
        else:
            glyphs.append(eva_word[i])
            i += 1
    return ''.join(glyphs)


def main():
    config = Config()
    pipeline = VoynichPipeline(config)
    pipeline.load()

    folios = list_folios(config.transcription_path)

    # Collect: for each EVA prefix, all (eva_word, latin, folio, section, confidence)
    prefix2_data = defaultdict(list)  # 2-glyph prefixes
    prefix3_data = defaultdict(list)  # 3-glyph prefixes

    # Also collect by EVA word start pattern
    word_starts = defaultdict(list)  # first 3 chars of EVA

    # Track which Latin roots appear for each prefix
    prefix2_latin_roots = defaultdict(Counter)
    prefix3_latin_roots = defaultdict(Counter)

    total = 0
    for fid, section in folios:
        lines, sec = parse_folio(config.transcription_path, fid)
        if not lines:
            continue
        decoded = pipeline.decode_folio(lines)

        for lnum, words in sorted(decoded.items()):
            for dw in words:
                if len(dw.eva) < 3:
                    continue
                total += 1

                latin_clean = dw.latin.lower().strip('_[]()? ')

                p2 = extract_prefix(dw.eva, 2)
                p3 = extract_prefix(dw.eva, 3)

                prefix2_data[p2].append((dw.eva, latin_clean, fid, section, dw.confidence))
                prefix3_data[p3].append((dw.eva, latin_clean, fid, section, dw.confidence))

                # Extract Latin root (first 3-4 chars)
                if len(latin_clean) >= 3:
                    lr3 = latin_clean[:3]
                    lr4 = latin_clean[:4] if len(latin_clean) >= 4 else latin_clean
                    prefix2_latin_roots[p2][lr4] += 1
                    prefix3_latin_roots[p3][lr4] += 1

    print(f"Processed {total} words across {len(folios)} folios")

    # Build report
    output = []
    output.append("=" * 80)
    output.append("  EVA PREFIX MAPPER — Systematic prefix-to-root analysis")
    output.append(f"  {total} words, {len(folios)} folios")
    output.append("=" * 80)

    # === SECTION 1: 2-glyph prefixes ranked by consistency ===
    output.append("\n\n## 1. TWO-GLYPH EVA PREFIXES (ranked by dominant Latin root %)")
    output.append("-" * 70)
    output.append(f"  {'EVA':8s} {'Count':>6s} {'Top Latin root':20s} {'%':>5s} {'Botanical match':30s}")

    prefix_scores = []
    for prefix, entries in prefix2_data.items():
        if len(entries) < 10:  # need enough data
            continue
        roots = prefix2_latin_roots[prefix]
        if not roots:
            continue
        top_root, top_count = roots.most_common(1)[0]
        consistency = top_count / len(entries) * 100

        # Check if top root matches a known botanical/pharma root
        botanical = ''
        for root_key, root_name in ROOTS_OF_INTEREST.items():
            if top_root.startswith(root_key[:3]) or root_key.startswith(top_root[:3]):
                botanical = root_name
                break

        prefix_scores.append((prefix, len(entries), top_root, consistency, botanical, roots))

    prefix_scores.sort(key=lambda x: (-x[3], -x[1]))

    for prefix, count, top_root, consistency, botanical, roots in prefix_scores[:50]:
        top3 = ', '.join(f'{r}({c})' for r, c in roots.most_common(3))
        output.append(f"  {prefix:8s} {count:6d} {top_root:20s} {consistency:5.1f}% {botanical:30s}")
        output.append(f"           roots: {top3}")

    # === SECTION 2: 3-glyph prefixes — more specific ===
    output.append("\n\n## 2. THREE-GLYPH EVA PREFIXES (high consistency)")
    output.append("-" * 70)

    prefix3_scores = []
    for prefix, entries in prefix3_data.items():
        if len(entries) < 5:
            continue
        roots = prefix3_latin_roots[prefix]
        if not roots:
            continue
        top_root, top_count = roots.most_common(1)[0]
        consistency = top_count / len(entries) * 100

        botanical = ''
        for root_key, root_name in ROOTS_OF_INTEREST.items():
            if top_root.startswith(root_key[:4]) or root_key.startswith(top_root[:4]):
                botanical = root_name
                break

        prefix3_scores.append((prefix, len(entries), top_root, consistency, botanical, roots))

    prefix3_scores.sort(key=lambda x: (-x[3], -x[1]))

    for prefix, count, top_root, consistency, botanical, roots in prefix3_scores[:60]:
        if consistency < 30:
            continue
        top3 = ', '.join(f'{r}({c})' for r, c in roots.most_common(3))
        marker = ' <<<' if botanical else ''
        output.append(f"  {prefix:10s} {count:5d} {top_root:20s} {consistency:5.1f}% {botanical:30s}{marker}")

    # === SECTION 3: Botanical prefix map ===
    output.append("\n\n## 3. BOTANICAL PREFIX MAP — EVA prefixes matching known plants")
    output.append("-" * 70)

    botanical_hits = []
    for prefix, count, top_root, consistency, botanical, roots in prefix_scores + prefix3_scores:
        if botanical and consistency > 30:
            botanical_hits.append((prefix, count, top_root, consistency, botanical))

    botanical_hits.sort(key=lambda x: (-x[3], -x[1]))
    seen_botanical = set()
    for prefix, count, top_root, consistency, botanical in botanical_hits:
        if botanical in seen_botanical:
            continue
        seen_botanical.add(botanical)
        output.append(f"  EVA {prefix:10s} ({count:4d}x) -> LAT {top_root:15s} = {botanical} ({consistency:.0f}%)")

    # === SECTION 4: Section-specific prefixes ===
    output.append("\n\n## 4. SECTION-SPECIFIC PREFIXES")
    output.append("-" * 70)
    output.append("  Prefixes that appear predominantly in one section:")

    for prefix, entries in sorted(prefix2_data.items(), key=lambda x: -len(x[1])):
        if len(entries) < 20:
            continue
        section_dist = Counter(e[3] for e in entries)
        top_sec, top_count = section_dist.most_common(1)[0]
        if top_count / len(entries) > 0.5:
            roots = prefix2_latin_roots[prefix]
            top_root = roots.most_common(1)[0][0] if roots else '?'
            output.append(f"  {prefix:8s} ({len(entries):4d}x) -> {top_sec:3s} {top_count/len(entries)*100:4.0f}%  root={top_root}")

    # === SECTION 5: The yt- family (INULA hypothesis) ===
    output.append("\n\n## 5. THE yt- FAMILY (INULA HYPOTHESIS)")
    output.append("-" * 70)

    yt_words = [(e[0], e[1], e[2], e[3], e[4]) for e in prefix2_data.get('yt', [])]
    output.append(f"  Total yt- words: {len(yt_words)}")

    # Group by EVA word
    yt_by_eva = defaultdict(list)
    for eva, latin, fid, sec, conf in yt_words:
        yt_by_eva[eva].append((latin, fid, sec, conf))

    output.append(f"  Unique yt- EVA forms: {len(yt_by_eva)}")
    for eva in sorted(yt_by_eva.keys(), key=lambda x: -len(yt_by_eva[x])):
        entries = yt_by_eva[eva]
        latins = Counter(e[0] for e in entries)
        folios = [e[1] for e in entries]
        sections = Counter(e[2] for e in entries)
        output.append(f"\n  {eva:20s} ({len(entries)}x) sections: {dict(sections)}")
        for latin, cnt in latins.most_common(5):
            output.append(f"    -> {latin:25s} ({cnt}x)")
        if len(folios) <= 10:
            output.append(f"    folios: {', '.join(folios)}")

    # === SECTION 6: The sh- family ===
    output.append("\n\n## 6. THE sh- FAMILY (CICURA/CI- HYPOTHESIS)")
    output.append("-" * 70)

    sh_roots = prefix2_latin_roots.get('sh', Counter())
    output.append(f"  Total sh- words: {len(prefix2_data.get('sh', []))}")
    output.append(f"  Top Latin roots:")
    for root, count in sh_roots.most_common(20):
        botanical = ''
        for rk, rn in ROOTS_OF_INTEREST.items():
            if root.startswith(rk[:3]):
                botanical = f' = {rn}'
                break
        output.append(f"    {root:15s} : {count:5d}{botanical}")

    # === SECTION 7: The qo- family ===
    output.append("\n\n## 7. THE qo- FAMILY (COQUERE HYPOTHESIS)")
    output.append("-" * 70)

    qo_roots = prefix2_latin_roots.get('qo', Counter())
    output.append(f"  Total qo- words: {len(prefix2_data.get('qo', []))}")
    for root, count in qo_roots.most_common(20):
        botanical = ''
        for rk, rn in ROOTS_OF_INTEREST.items():
            if root.startswith(rk[:3]):
                botanical = f' = {rn}'
                break
        output.append(f"    {root:15s} : {count:5d}{botanical}")

    # Write
    report = '\n'.join(output)
    out_path = os.path.join(os.path.dirname(__file__), '..', 'output', 'PREFIX_MAP_REPORT.txt')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\nReport: {out_path}")
    # Print summary only
    for line in output[:5] + output[-3:]:
        print(line)


if __name__ == '__main__':
    main()
