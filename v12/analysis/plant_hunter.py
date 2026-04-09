"""
Plant Hunter — Search for hidden plant names in OPAQUE/LOW words.
Strategy: decode opaque EVA words monolithically and compare against
known medieval plant names from Circa Instans and botanical anchors.
"""
import sys, os, json, re
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from v12.config import Config
from v12.pipeline import VoynichPipeline
from v12.loaders.transcription import list_folios, parse_folio
from v12.stages.tokenizer import tokenize, preprocess_triples
from v12.stages.hmm_decoder import decode_root

# Medieval Latin plant names (Circa Instans + Antidotarium + common pharmacopeia)
# Source: standard medieval materia medica
PLANT_NAMES = {
    # A
    'absinthium', 'acacia', 'aconitum', 'acorus', 'agrimonia', 'aloe', 'aloes',
    'althaea', 'ambrosia', 'amomum', 'amygdalum', 'anchusa', 'anetum', 'angelica',
    'anisium', 'anisum', 'apium', 'aristolochia', 'artemisia', 'asarum', 'asparagus',
    'atriplex', 'auripigmentum',
    # B
    'balsamum', 'bdellium', 'betonica', 'borago', 'brassica', 'bryonia', 'buglossa',
    # C
    'calamus', 'camomilla', 'camphora', 'cannabis', 'capparis', 'cardamomum',
    'carduus', 'carum', 'cassia', 'castoreum', 'centaurea', 'cepa', 'cera',
    'cerasa', 'cichorium', 'cicuta', 'cinnamomum', 'citrullus', 'colchicum',
    'colocynthis', 'consolida', 'coriandrum', 'costus', 'crocus', 'cucumis',
    'cuminum', 'curcuma', 'cynoglossa',
    # D
    'daucus', 'dictamnus', 'digitalis', 'dragantum',
    # E
    'ebulus', 'elaterium', 'electuarium', 'elleborus', 'endivia', 'enula',
    'epithimum', 'eruca', 'eupatorium', 'euphorbia',
    # F
    'feniculum', 'foeniculum', 'fenugraecum', 'filix', 'fragaria', 'fraxinus',
    # G
    'galanga', 'galbanum', 'gentiana', 'gingidium', 'gladiolus', 'glycyrrhiza',
    # H
    'helleborus', 'helenium', 'hermodactylus', 'hiera', 'hypericum', 'hyssopus',
    # I-J
    'iris', 'isatis', 'iva', 'juniperus',
    # L
    'lactuca', 'lapathum', 'laureola', 'laurus', 'lavandula', 'lens', 'levisticum',
    'lilium', 'linum', 'liquiritia', 'lolium', 'lupinus',
    # M
    'majorana', 'malva', 'mandragora', 'marrubium', 'mastix', 'matricaria',
    'melilotum', 'melissa', 'menta', 'millefolium', 'morus', 'muscus', 'myrrha',
    'myrtus',
    # N
    'narcissus', 'nardus', 'nasturtium', 'nepeta', 'nigella', 'nux',
    # O
    'ocimum', 'oleum', 'olibanum', 'opium', 'origanum', 'orobus',
    # P
    'paeonia', 'papaver', 'pastinaca', 'peonia', 'petroselinum', 'piper',
    'plantago', 'polium', 'polygonatum', 'polypodium', 'portulaca', 'prunus',
    'psyllium', 'pulegium', 'pyrethrum',
    # Q-R
    'raphanus', 'rhabarbarum', 'rheum', 'rosa', 'rosmarinus', 'ruta',
    # S
    'sabina', 'sagapenum', 'salvia', 'sambucus', 'sandalum', 'saponaria',
    'satureia', 'saxifraga', 'scabiosa', 'scammonia', 'scilla', 'senecio',
    'senna', 'serpyllum', 'sinapis', 'solanum', 'spica', 'spicanardi',
    'squilla', 'staphisagria', 'stoechas', 'styrax', 'succinum',
    # T
    'tamarindus', 'tanacetum', 'terebinthina', 'thapsia', 'thus', 'thymum',
    'tormentilla', 'tragacanthum', 'trifolium', 'turbith',
    # U-V
    'urtica', 'valeriana', 'verbascum', 'verbena', 'veronica', 'viola',
    'viscum', 'vitex', 'vitis',
    # Z
    'zedoaria', 'zingiber', 'zizyphus',
    # Common medieval forms
    'enula', 'inula', 'eneliode', 'ineliode', 'cicura', 'ture', 'asara',
    'apio', 'olen', 'oleo', 'aceto', 'melle', 'butyro', 'axungia',
    'lithargiro', 'cerusa', 'tutia', 'vitriolum', 'alumen', 'arsenicum',
    'sulphur', 'argentum', 'aurum', 'ferrum', 'plumbum', 'stannum',
}

# Also add oblique cases
PLANT_FORMS = set()
for p in PLANT_NAMES:
    PLANT_FORMS.add(p)
    # Common Latin endings
    if p.endswith('um'):
        PLANT_FORMS.add(p[:-2] + 'i')   # gen sing
        PLANT_FORMS.add(p[:-2] + 'o')   # dat/abl
        PLANT_FORMS.add(p[:-2] + 'a')   # nom pl neut
    elif p.endswith('a'):
        PLANT_FORMS.add(p[:-1] + 'ae')  # gen/dat/nom pl
        PLANT_FORMS.add(p[:-1] + 'am')  # acc sing
    elif p.endswith('is'):
        PLANT_FORMS.add(p[:-2] + 'em')  # acc sing
        PLANT_FORMS.add(p[:-2] + 'i')   # dat sing
        PLANT_FORMS.add(p[:-2] + 'e')   # abl sing
    elif p.endswith('us'):
        PLANT_FORMS.add(p[:-2] + 'i')   # gen sing
        PLANT_FORMS.add(p[:-2] + 'o')   # dat/abl
        PLANT_FORMS.add(p[:-2] + 'um')  # acc sing


def fuzzy_match(decoded: str, threshold: float = 0.75) -> list[tuple[str, float]]:
    """Find plant names that are similar to decoded word (Levenshtein-based)."""
    matches = []
    d = decoded.lower().strip()
    if len(d) < 4:
        return matches

    for plant in PLANT_FORMS:
        if len(plant) < 4:
            continue
        # Quick length filter
        if abs(len(d) - len(plant)) > 3:
            continue

        # Calculate similarity
        # Simple: count matching characters in order (LCS-like)
        i = j = matching = 0
        while i < len(d) and j < len(plant):
            if d[i] == plant[j]:
                matching += 1
                i += 1
                j += 1
            elif i + 1 < len(d) and d[i+1] == plant[j]:
                i += 1  # skip one in decoded
            else:
                j += 1  # skip one in plant
                i += 1

        sim = matching / max(len(d), len(plant))
        if sim >= threshold:
            matches.append((plant, sim))

    matches.sort(key=lambda x: -x[1])
    return matches[:5]


def main():
    print("=" * 80)
    print("  PLANT HUNTER — Searching for hidden plant names")
    print("=" * 80)

    config = Config()
    pipeline = VoynichPipeline(config)
    pipeline.load()

    folios = list_folios(config.transcription_path)

    # Focus on herbal folios but scan all
    output = []
    output.append("=" * 80)
    output.append("  PLANT HUNTER REPORT")
    output.append("=" * 80)

    # Collect all opaque/low words with their contexts
    opaque_words = []  # (folio, section, line, eva, decoded, context_before, context_after)

    for fid, section in folios:
        lines, sec = parse_folio(config.transcription_path, fid)
        if not lines:
            continue
        decoded = pipeline.decode_folio(lines)

        for lnum, words in sorted(decoded.items()):
            for i, dw in enumerate(words):
                if dw.confidence in ('LOW', 'OPAQUE') and len(dw.eva) >= 4:
                    ctx_before = words[i-1].latin if i > 0 else '-'
                    ctx_after = words[i+1].latin if i < len(words)-1 else '-'
                    opaque_words.append((fid, section, lnum, dw.eva, dw.latin, ctx_before, ctx_after))

    print(f"\nFound {len(opaque_words)} opaque/low words (len>=4)")

    # === STRATEGY 1: Direct match against plant names ===
    output.append("\n\n## 1. DIRECT MATCHES — Decoded words matching plant names")
    output.append("-" * 60)

    direct_matches = []
    for fid, sec, lnum, eva, latin, ctx_b, ctx_a in opaque_words:
        clean = latin.lower().strip('_[]()? ')
        if clean in PLANT_FORMS:
            direct_matches.append((fid, sec, lnum, eva, clean, ctx_b, ctx_a))

    if direct_matches:
        for fid, sec, lnum, eva, plant, ctx_b, ctx_a in direct_matches:
            output.append(f"  {fid:8s} [{sec}] L{lnum:02d}: {eva:20s} -> {plant:20s}  context: {ctx_b} | {ctx_a}")
    else:
        output.append("  No direct matches found.")

    # === STRATEGY 2: Fuzzy match ===
    output.append("\n\n## 2. FUZZY MATCHES — Decoded words similar to plant names (>75%)")
    output.append("-" * 60)

    fuzzy_results = []
    seen_eva = set()
    for fid, sec, lnum, eva, latin, ctx_b, ctx_a in opaque_words:
        if eva in seen_eva:
            continue
        seen_eva.add(eva)
        clean = latin.lower().strip('_[]()? ')
        if len(clean) < 5:
            continue
        matches = fuzzy_match(clean, threshold=0.70)
        if matches:
            fuzzy_results.append((fid, sec, lnum, eva, clean, matches, ctx_b, ctx_a))

    fuzzy_results.sort(key=lambda x: -x[5][0][1])
    for fid, sec, lnum, eva, decoded, matches, ctx_b, ctx_a in fuzzy_results[:60]:
        best = matches[0]
        others = ', '.join(f'{m[0]}({m[1]:.0%})' for m in matches[1:3])
        output.append(f"  {fid:8s} [{sec}] L{lnum:02d}: {eva:18s} -> {decoded:20s} ~ {best[0]:20s} ({best[1]:.0%})  {others}")
        output.append(f"    context: ...{ctx_b} [{decoded}] {ctx_a}...")

    # === STRATEGY 3: HMM alternative decodings for top opaques ===
    output.append("\n\n## 3. ALTERNATIVE DECODINGS — Top 50 frequent opaques re-decoded")
    output.append("-" * 60)

    # Count opaque EVA words
    eva_counts = Counter()
    for fid, sec, lnum, eva, latin, ctx_b, ctx_a in opaque_words:
        eva_counts[eva] += 1

    for eva, count in eva_counts.most_common(50):
        if len(eva) < 3:
            continue
        # Try all HMM paths
        hmm_paths = decode_root(eva, pipeline.hmm, top_k=15)
        candidates = []
        for vp in hmm_paths:
            if not vp.latin:
                continue
            clean = vp.latin.replace(' ', '')
            is_plant = clean.lower() in PLANT_FORMS
            is_perseus = pipeline.dictionary.is_valid(clean)
            freq = pipeline.corpus.freq(clean)
            candidates.append((clean, vp.log_prob, is_plant, is_perseus, freq))

        # Check for plant matches in alternatives
        plant_hits = [c for c in candidates if c[2]]
        perseus_hits = [c for c in candidates if c[3]]

        output.append(f"\n  {eva:18s} ({count}x)")
        if plant_hits:
            output.append(f"    *** PLANT MATCH: {', '.join(f'{c[0]}' for c in plant_hits)}")
        for c in candidates[:8]:
            markers = []
            if c[2]: markers.append('PLANT')
            if c[3]: markers.append('PERSEUS')
            if c[4] > 0: markers.append(f'freq={c[4]}')
            m = ' '.join(markers)
            output.append(f"    {c[0]:25s} logP={c[1]:7.2f}  {m}")

    # === STRATEGY 4: Herbal folio focus ===
    output.append("\n\n## 4. HERBAL FOLIO OPAQUE CONCENTRATION")
    output.append("-" * 60)

    herbal_opaques = [x for x in opaque_words if x[1] == 'H']
    output.append(f"  Herbal section: {len(herbal_opaques)} opaque words (total herbal folios)")

    # Group by folio
    by_folio = defaultdict(list)
    for fid, sec, lnum, eva, latin, ctx_b, ctx_a in herbal_opaques:
        by_folio[fid].append((lnum, eva, latin, ctx_b, ctx_a))

    for fid in sorted(by_folio.keys()):
        words = by_folio[fid]
        if len(words) >= 3:
            output.append(f"\n  {fid} ({len(words)} opaque words):")
            for lnum, eva, latin, ctx_b, ctx_a in words[:10]:
                output.append(f"    L{lnum:02d}: {eva:18s} → {latin:20s}  [{ctx_b} | {ctx_a}]")

    # Write report
    report = '\n'.join(output)
    out_path = os.path.join(os.path.dirname(__file__), '..', 'output', 'PLANT_HUNTER_REPORT.txt')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\nReport: {out_path}")
    print(report[:4000].encode('ascii', 'replace').decode())


if __name__ == '__main__':
    main()
