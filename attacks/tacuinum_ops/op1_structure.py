"""
OP-1: COMPTAGE STRUCTUREL
Combien d'elements par page dans la section astro/cosmo du VMS?
Compare avec 7 (Tacuinum), 12 (zodiac), 28-30 (calendrier lunaire).
"""
import re, json, sys, os
from collections import Counter, defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from lib.vms_parser import VMSCorpus

def main():
    print("=" * 60)
    print("OP-1: COMPTAGE STRUCTUREL — Section Astro/Cosmo")
    print("=" * 60)

    vms = VMSCorpus()
    vms.load()

    # Section astro/cosmo: f58-f73
    astro_folios = sorted(set(
        w.folio for w in vms.words
        if 58 <= w.folio_num <= 73
    ), key=lambda f: (int(re.search(r'\d+', f).group()), f))

    print(f"\nFolios astro/cosmo: {len(astro_folios)}")
    print()

    # For each folio: count lines, words, labels, structural markers
    folio_data = []
    for folio in astro_folios:
        words = vms.get_folio(folio)
        n_words = len(words)
        lines = set(w.line for w in words)
        n_lines = len(lines)

        # Count words that look like "labels" (short, near figures)
        # Labels in ZL.txt are typically on their own lines with few words
        short_lines = 0
        label_candidates = 0
        words_per_line = defaultdict(list)
        for w in words:
            words_per_line[w.line].append(w)

        for line_num, line_words in words_per_line.items():
            if len(line_words) <= 3:
                short_lines += 1
                label_candidates += len(line_words)

        # Count -am terminators (potential entry separators)
        am_count = sum(1 for w in words if w.eva.endswith('am') and len(w.eva) > 2)

        # Count logogram 'r' (recipe = potential entry start)
        recipe_count = sum(1 for w in words if w.eva == 'r')

        folio_data.append({
            'folio': folio,
            'n_words': n_words,
            'n_lines': n_lines,
            'short_lines': short_lines,
            'label_candidates': label_candidates,
            'am_terminators': am_count,
            'recipe_markers': recipe_count,
        })

        print(f"  {folio:8s}  words={n_words:4d}  lines={n_lines:2d}  "
              f"short_lines={short_lines:2d}  -am={am_count:2d}  r={recipe_count:d}")

    # Summary stats
    total_words = sum(f['n_words'] for f in folio_data)
    total_lines = sum(f['n_lines'] for f in folio_data)
    total_short = sum(f['short_lines'] for f in folio_data)
    total_am = sum(f['am_terminators'] for f in folio_data)

    print()
    print("=" * 60)
    print("SUMMARY")
    print(f"  Total folios: {len(folio_data)}")
    print(f"  Total words: {total_words}")
    print(f"  Total lines: {total_lines}")
    print(f"  Total short lines (<=3 words): {total_short}")
    print(f"  Total -am terminators: {total_am}")
    print()

    # Key question: how many "entries" per folio?
    # Hypothesis 1: entries separated by -am
    if total_am > 0:
        entries_per_folio_am = total_am / len(folio_data)
        tokens_per_entry_am = total_words / total_am
        print(f"  If -am = entry separator:")
        print(f"    Entries per folio: {entries_per_folio_am:.1f}")
        print(f"    Tokens per entry: {tokens_per_entry_am:.1f}")

    # Hypothesis 2: entries = short lines (labels near figures)
    if total_short > 0:
        entries_per_folio_short = total_short / len(folio_data)
        print(f"  If short lines = labels/entries:")
        print(f"    Labels per folio: {entries_per_folio_short:.1f}")

    # Hypothesis 3: entries = lines
    entries_per_folio_lines = total_lines / len(folio_data)
    tokens_per_line = total_words / total_lines
    print(f"  If each line = 1 entry:")
    print(f"    Lines per folio: {entries_per_folio_lines:.1f}")
    print(f"    Tokens per line: {tokens_per_line:.1f}")

    # Compare with reference
    print()
    print("COMPARISON WITH REFERENCE STRUCTURES:")
    print(f"  Tacuinum Sanitatis: 7 entries per table, ~15 tokens per entry")
    print(f"  Zodiac calendar:   12 entries per sign (months)")
    print(f"  Lunar calendar:    28-30 entries per cycle")
    print()

    # Check zodiac pages specifically (f70-f73 have zodiac signs)
    print("ZODIAC PAGES (f67-f73, with sub-folios):")
    zodiac_folios = [f for f in folio_data if int(re.search(r'\d+', f['folio']).group()) >= 67]
    for f in zodiac_folios:
        print(f"  {f['folio']:8s}  words={f['n_words']:4d}  lines={f['n_lines']:2d}  "
              f"-am={f['am_terminators']:2d}  tokens/line={f['n_words']/max(f['n_lines'],1):.1f}")

    # Nymph count from ZL.txt annotations
    print()
    print("CHECKING ZL.txt FOR NYMPH/FIGURE ANNOTATIONS...")
    with open('data/transcriptions/ZL.txt', encoding='utf-8') as f:
        zl = f.read()

    nymph_count = Counter()
    for line in zl.split('\n'):
        m = re.match(r'<f(\d+)([rv])(\d?)', line.strip())
        if not m: continue
        fnum = int(m.group(1))
        if not (58 <= fnum <= 73): continue
        folio = f"f{fnum}{m.group(2)}{m.group(3)}"

        # Count figure/star annotations
        stars = len(re.findall(r'<!star>', line, re.I))
        nymphs = len(re.findall(r'<!nymph|<!figure|<!person|<!nude', line, re.I))
        labels = len(re.findall(r'<!label', line, re.I))
        plants = len(re.findall(r'<!plant', line, re.I))

        if stars or nymphs or labels or plants:
            nymph_count[folio] += stars + nymphs + labels + plants

    if nymph_count:
        print("Figure/annotation counts:")
        for f in sorted(nymph_count, key=lambda x: (int(re.search(r'\d+', x).group()), x)):
            print(f"  {f:8s}  {nymph_count[f]:3d} annotations")
    else:
        print("  No figure annotations found in ZL.txt markup")
        print("  (Figure counts may need to be checked from Yale Beinecke images)")

    # Save results
    results = {
        'folio_data': folio_data,
        'summary': {
            'total_folios': len(folio_data),
            'total_words': total_words,
            'total_lines': total_lines,
            'total_short_lines': total_short,
            'total_am_terminators': total_am,
            'entries_per_folio_by_am': round(total_am / len(folio_data), 1) if total_am else 0,
            'tokens_per_entry_by_am': round(total_words / total_am, 1) if total_am else 0,
            'lines_per_folio': round(total_lines / len(folio_data), 1),
            'tokens_per_line': round(total_words / total_lines, 1),
        },
        'nymph_annotations': dict(nymph_count),
    }

    os.makedirs('attacks/tacuinum_ops/results', exist_ok=True)
    with open('attacks/tacuinum_ops/results/op1_structure.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to attacks/tacuinum_ops/results/op1_structure.json")


if __name__ == '__main__':
    main()
