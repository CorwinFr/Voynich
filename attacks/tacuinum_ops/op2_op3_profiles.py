"""
OP-2 + OP-3 COMBINED: Profile VMS astro vs Tacuinum
Side-by-side comparison of statistical signatures.
"""
import re, json, sys, os, math
from collections import Counter, defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from lib.vms_parser import VMSCorpus, get_suffix, LOGOGRAMS

def entropy(counter):
    total = sum(counter.values())
    if total == 0: return 0
    return -sum((c/total) * math.log2(c/total) for c in counter.values() if c > 0)

def ttr(words):
    """Type-Token Ratio"""
    if not words: return 0
    return len(set(words)) / len(words)

def profile_vms_section(vms, section_name, folio_range):
    """Build statistical profile of a VMS section."""
    words = [w for w in vms.words if folio_range[0] <= w.folio_num <= folio_range[1]]
    if not words:
        return None

    eva_words = [w.eva for w in words]
    freq = Counter(eva_words)

    # Separate labels (short lines) from prose (long lines)
    lines = defaultdict(list)
    for w in words:
        lines[(w.folio, w.line)].append(w)

    label_words = []  # from lines with <=3 words
    prose_words = []  # from lines with >3 words
    for key, line_words in lines.items():
        if len(line_words) <= 3:
            label_words.extend([w.eva for w in line_words])
        else:
            prose_words.extend([w.eva for w in line_words])

    # Suffix distribution
    sfx_dist = Counter()
    root_dist = Counter()
    for w in words:
        if w.suffix:
            sfx_dist[w.suffix] += 1
            root_dist[w.root] += 1

    # Logogram ratio
    n_logos = sum(1 for w in words if w.is_logogram)

    # Word length distribution
    len_dist = Counter(len(w.eva) for w in words)

    # Position distribution
    pos_start = sum(1 for w in words if w.is_line_start)
    pos_end = sum(1 for w in words if w.is_line_end)

    # Bigrams (same line only)
    bigrams = Counter()
    sorted_words = sorted(words, key=lambda w: (w.folio, w.line, w.position))
    for i in range(len(sorted_words) - 1):
        if sorted_words[i].folio == sorted_words[i+1].folio and sorted_words[i].line == sorted_words[i+1].line:
            bigrams[(sorted_words[i].eva, sorted_words[i+1].eva)] += 1

    return {
        'section': section_name,
        'n_tokens': len(eva_words),
        'n_unique': len(set(eva_words)),
        'ttr': round(ttr(eva_words), 4),
        'entropy': round(entropy(freq), 2),
        'n_logos': n_logos,
        'logo_pct': round(n_logos * 100 / len(eva_words), 1),
        'n_label_tokens': len(label_words),
        'n_prose_tokens': len(prose_words),
        'label_pct': round(len(label_words) * 100 / len(eva_words), 1) if eva_words else 0,
        'top20_words': [(w, c) for w, c in freq.most_common(20)],
        'top20_non_logo': [(w, c) for w, c in freq.most_common(50) if w not in LOGOGRAMS][:20],
        'suffix_dist': dict(sfx_dist.most_common()),
        'top10_roots': [(r, c) for r, c in root_dist.most_common(10)],
        'word_length_dist': dict(sorted(len_dist.items())),
        'avg_word_length': round(sum(len(w.eva) for w in words) / len(words), 2),
        'top10_bigrams': [{'bg': list(bg), 'count': c} for bg, c in bigrams.most_common(10)],
    }


def profile_tacuinum():
    """Build statistical profile of Tacuinum text."""
    with open('attacks/RECIPE_DATASET/S12_TACUINUM.json', encoding='utf-8') as f:
        tac = json.load(f)

    entries = tac['entries']

    # Collect all text by column
    col_words = defaultdict(list)
    all_words = []
    for e in entries:
        for col in ['natura', 'gradus', 'melius', 'iuvamentum', 'nocumentum', 'remotio']:
            text = e.get(col, '').lower()
            words = re.findall(r'[a-z]+', text)
            col_words[col].extend(words)
            all_words.extend(words)

        # Name is special
        name = e.get('name', '').lower()
        name_words = re.findall(r'[a-z]+', name)
        col_words['nomina'].extend(name_words)
        all_words.extend(name_words)

    freq = Counter(all_words)

    # Per-column stats
    col_stats = {}
    for col, words in col_words.items():
        col_freq = Counter(words)
        col_stats[col] = {
            'n_tokens': len(words),
            'n_unique': len(set(words)),
            'ttr': round(ttr(words), 4),
            'entropy': round(entropy(col_freq), 2),
            'top10': [(w, c) for w, c in col_freq.most_common(10)],
        }

    # Galenic distribution
    thermal = Counter()
    moisture = Counter()
    for e in entries:
        t = e.get('thermal', '')
        m = e.get('moisture', '')
        if t: thermal[t] += 1
        if m: moisture[m] += 1

    return {
        'n_entries': len(entries),
        'n_tokens_total': len(all_words),
        'n_unique_total': len(set(all_words)),
        'ttr_total': round(ttr(all_words), 4),
        'entropy_total': round(entropy(freq), 2),
        'tokens_per_entry': round(len(all_words) / len(entries), 1),
        'top20_words': [(w, c) for w, c in freq.most_common(20)],
        'col_stats': col_stats,
        'thermal': dict(thermal),
        'moisture': dict(moisture),
        'galenic_ratio': {
            'calidum_pct': round(thermal.get('calidum', 0) * 100 / sum(thermal.values()), 1) if thermal else 0,
            'frigidum_pct': round(thermal.get('frigidum', 0) * 100 / sum(thermal.values()), 1) if thermal else 0,
            'siccum_pct': round(moisture.get('siccum', 0) * 100 / sum(moisture.values()), 1) if moisture else 0,
            'humidum_pct': round(moisture.get('humidum', 0) * 100 / sum(moisture.values()), 1) if moisture else 0,
        },
    }


def main():
    print("=" * 70)
    print("OP-2 + OP-3: PROFILS COMPARES VMS ASTRO vs TACUINUM")
    print("=" * 70)

    # Load VMS
    vms = VMSCorpus()
    vms.load()

    # Profile 4 sections for comparison
    sections = {
        'ASTRO (f58-f73)': (58, 73),
        'HERBAL_A (f1-f56)': (1, 56),
        'BALNEA (f75-f84)': (75, 84),
        'PHARMA (f103-f116)': (103, 116),
    }

    profiles = {}
    for name, (lo, hi) in sections.items():
        p = profile_vms_section(vms, name, (lo, hi))
        if p:
            profiles[name] = p

    # Profile Tacuinum
    tac_profile = profile_tacuinum()

    # ====== DISPLAY ======
    print()
    print("=" * 70)
    print("GLOBAL COMPARISON")
    print("=" * 70)
    print(f"{'Metric':<25s}", end='')
    for name in profiles:
        print(f" {name[:12]:>12s}", end='')
    print(f" {'TACUINUM':>12s}")
    print("-" * 85)

    for metric in ['n_tokens', 'n_unique', 'ttr', 'entropy', 'logo_pct', 'label_pct', 'avg_word_length']:
        print(f"{metric:<25s}", end='')
        for name in profiles:
            v = profiles[name].get(metric, '-')
            if isinstance(v, float):
                print(f" {v:>12.3f}", end='')
            else:
                print(f" {str(v):>12s}", end='')
        # Tacuinum equivalent
        tac_val = {
            'n_tokens': tac_profile['n_tokens_total'],
            'n_unique': tac_profile['n_unique_total'],
            'ttr': tac_profile['ttr_total'],
            'entropy': tac_profile['entropy_total'],
            'logo_pct': 0,
            'label_pct': 0,
            'avg_word_length': '-',
        }.get(metric, '-')
        if isinstance(tac_val, float):
            print(f" {tac_val:>12.3f}")
        else:
            print(f" {str(tac_val):>12s}")

    # Suffix comparison
    print()
    print("=" * 70)
    print("SUFFIX DISTRIBUTION (top 8)")
    print("=" * 70)
    all_suffixes = set()
    for p in profiles.values():
        all_suffixes.update(p['suffix_dist'].keys())

    print(f"{'Suffix':<8s}", end='')
    for name in profiles:
        print(f" {name[:12]:>12s}", end='')
    print()

    for sfx in sorted(all_suffixes, key=lambda s: -max(p['suffix_dist'].get(s, 0) for p in profiles.values()))[:10]:
        print(f"-{sfx:<7s}", end='')
        for name in profiles:
            c = profiles[name]['suffix_dist'].get(sfx, 0)
            total = profiles[name]['n_tokens']
            pct = c * 100 // total if total else 0
            print(f" {c:>5d}({pct:>2d}%)", end='')
        print()

    # Top words astro vs Tacuinum
    print()
    print("=" * 70)
    print("TOP 20 WORDS: VMS ASTRO (non-logogram) vs TACUINUM")
    print("=" * 70)
    astro = profiles.get('ASTRO (f58-f73)', {})
    print(f"{'VMS ASTRO':<25s} {'count':>5s}  |  {'TACUINUM':<25s} {'count':>5s}")
    print("-" * 70)
    astro_top = astro.get('top20_non_logo', [])
    tac_top = tac_profile.get('top20_words', [])
    for i in range(20):
        a_word = astro_top[i][0] if i < len(astro_top) else ''
        a_count = astro_top[i][1] if i < len(astro_top) else 0
        t_word = tac_top[i][0] if i < len(tac_top) else ''
        t_count = tac_top[i][1] if i < len(tac_top) else 0
        print(f"{a_word:<25s} {a_count:>5d}  |  {t_word:<25s} {t_count:>5d}")

    # Tacuinum column vocabulary sizes
    print()
    print("=" * 70)
    print("TACUINUM COLUMN VOCABULARY SIZES (target for OP-5)")
    print("=" * 70)
    for col, stats in tac_profile['col_stats'].items():
        print(f"  {col:<15s}  tokens={stats['n_tokens']:>5d}  unique={stats['n_unique']:>4d}  "
              f"TTR={stats['ttr']:.3f}  entropy={stats['entropy']:.2f}")

    # Galenic distribution
    print()
    print("=" * 70)
    print("TACUINUM GALENIC DISTRIBUTION")
    print("=" * 70)
    gr = tac_profile['galenic_ratio']
    print(f"  calidum:  {tac_profile['thermal'].get('calidum', 0):>3d}  ({gr['calidum_pct']}%)")
    print(f"  frigidum: {tac_profile['thermal'].get('frigidum', 0):>3d}  ({gr['frigidum_pct']}%)")
    print(f"  siccum:   {tac_profile['moisture'].get('siccum', 0):>3d}  ({gr['siccum_pct']}%)")
    print(f"  humidum:  {tac_profile['moisture'].get('humidum', 0):>3d}  ({gr['humidum_pct']}%)")
    print(f"  Ratio cal:fri = {tac_profile['thermal'].get('calidum',1)/max(tac_profile['thermal'].get('frigidum',1),1):.2f}:1")

    # KEY COMPARISON: repetitivity
    print()
    print("=" * 70)
    print("REPETITIVITY COMPARISON (TTR = Type/Token, lower = more repetitive)")
    print("=" * 70)
    for name, p in profiles.items():
        print(f"  VMS {name[:20]:<20s}  TTR={p['ttr']:.4f}  entropy={p['entropy']:.2f}")
    print(f"  TACUINUM total        TTR={tac_profile['ttr_total']:.4f}  entropy={tac_profile['entropy_total']:.2f}")
    print(f"  TACUINUM gradus       TTR={tac_profile['col_stats']['gradus']['ttr']:.4f}  entropy={tac_profile['col_stats']['gradus']['entropy']:.2f}")
    print(f"  TACUINUM natura       TTR={tac_profile['col_stats']['natura']['ttr']:.4f}  entropy={tac_profile['col_stats']['natura']['entropy']:.2f}")

    # ASTRO sub-analysis: dense pages vs label pages
    print()
    print("=" * 70)
    print("ASTRO SUB-ANALYSIS: DENSE vs LABEL PAGES")
    print("=" * 70)

    dense_words = [w for w in vms.words if 58 <= w.folio_num <= 73 and w.total_in_line > 3]
    label_words_list = [w for w in vms.words if 58 <= w.folio_num <= 73 and w.total_in_line <= 3]

    dense_freq = Counter(w.eva for w in dense_words)
    label_freq = Counter(w.eva for w in label_words_list)

    print(f"  Dense (lines >3 words):  {len(dense_words)} tokens, {len(dense_freq)} unique, TTR={ttr([w.eva for w in dense_words]):.4f}")
    print(f"  Labels (lines <=3 words): {len(label_words_list)} tokens, {len(label_freq)} unique, TTR={ttr([w.eva for w in label_words_list]):.4f}")

    print()
    print("  Dense top 10 (non-logo):")
    for w, c in dense_freq.most_common(30):
        if w not in LOGOGRAMS:
            print(f"    {w:<15s} {c:>4d}x")
            if sum(1 for ww, _ in dense_freq.most_common(30) if ww not in LOGOGRAMS and dense_freq[ww] >= c) >= 10:
                break

    print()
    print("  Label top 10 (non-logo):")
    for w, c in label_freq.most_common(30):
        if w not in LOGOGRAMS:
            print(f"    {w:<15s} {c:>4d}x")
            if sum(1 for ww, _ in label_freq.most_common(30) if ww not in LOGOGRAMS and label_freq[ww] >= c) >= 10:
                break

    # Save results
    results = {
        'vms_profiles': {k: {kk: vv for kk, vv in v.items()} for k, v in profiles.items()},
        'tacuinum_profile': tac_profile,
        'astro_dense_tokens': len(dense_words),
        'astro_label_tokens': len(label_words_list),
    }

    with open('attacks/tacuinum_ops/results/op2_op3_profiles.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to attacks/tacuinum_ops/results/op2_op3_profiles.json")


if __name__ == '__main__':
    main()
