"""
Collatinus Validator — Pass the top 200 LOW-confidence decoded words
through Collatinus to check if they are valid medieval Latin.
If recognized → promote to HIGH.
"""
import sys, os, socket, re
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from v12.config import Config
from v12.pipeline import VoynichPipeline
from v12.loaders.transcription import list_folios, parse_folio


def lemmatize_collatinus(word):
    """Query Collatinus daemon for lemma + morphology."""
    w = word.lower().strip()
    if len(w) < 3 or not w.isalpha():
        return None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect(('127.0.0.1', 5555))
        s.sendall(f'-lfr {w}\n'.encode('utf-8'))
        data = s.recv(4096).decode('utf-8', errors='replace').strip()
        s.close()
        if data.startswith('*'):
            return data
        return None
    except Exception:
        return None


def main():
    config = Config()
    pipeline = VoynichPipeline(config)
    pipeline.load()
    folios = list_folios(config.transcription_path)

    # Collect all LOW words
    low_words = Counter()  # latin -> count
    low_examples = {}  # latin -> (fid, lnum, eva)

    for fid, section in folios:
        lines, sec = parse_folio(config.transcription_path, fid)
        if not lines:
            continue
        decoded = pipeline.decode_folio(lines)
        for lnum, words in sorted(decoded.items()):
            for dw in words:
                if dw.confidence == 'LOW':
                    clean = dw.latin.lower().strip('_[]()? ')
                    # Split compound words and check each part
                    for part in clean.split():
                        if len(part) >= 3 and part.isalpha():
                            low_words[part] += 1
                            if part not in low_examples:
                                low_examples[part] = (fid, lnum, dw.eva, dw.latin)

    print(f"Unique LOW word forms: {len(low_words)}")
    print(f"Total LOW occurrences: {sum(low_words.values())}")

    # Test top 200 through Collatinus
    out = []
    out.append("# Validation Collatinus des mots LOW")
    out.append("")
    out.append(f"**Mots LOW uniques**: {len(low_words)}")
    out.append(f"**Occurrences totales**: {sum(low_words.values())}")
    out.append("")

    recognized = []
    unrecognized = []
    errors = []

    tested = 0
    for word, count in low_words.most_common(200):
        result = lemmatize_collatinus(word)
        tested += 1

        if result:
            # Parse lemma
            lemma_line = result.split('\n')[0]
            recognized.append((word, count, lemma_line))
        else:
            unrecognized.append((word, count))

        if tested % 50 == 0:
            print(f"  Tested {tested}/200...")

    # Report
    out.append("---")
    out.append("## Mots reconnus par Collatinus (PROMOTABLES en HIGH)")
    out.append("")
    out.append(f"**{len(recognized)} mots reconnus** sur {tested} testes")
    out.append("")

    total_promotable = sum(c for _, c, _ in recognized)
    out.append(f"**{total_promotable} occurrences** pourraient passer de LOW a HIGH")
    out.append("")

    out.append("| Mot | Occurrences | Lemme Collatinus | EVA source |")
    out.append("|-----|------------|-----------------|------------|")
    for word, count, lemma in recognized:
        ex = low_examples.get(word, ('?', 0, '?', '?'))
        # Clean lemma for display
        lemma_clean = lemma.replace('|', '/').strip()[:60]
        out.append(f"| {word} | {count} | {lemma_clean} | {ex[2]} |")

    out.append("")
    out.append("---")
    out.append("## Mots NON reconnus par Collatinus")
    out.append("")
    out.append(f"**{len(unrecognized)} mots non reconnus** sur {tested} testes")
    out.append("")

    total_unknown = sum(c for _, c in unrecognized)
    out.append(f"**{total_unknown} occurrences** restent LOW/OPAQUE")
    out.append("")

    out.append("| Mot | Occurrences | Pourquoi opaque? |")
    out.append("|-----|------------|-----------------|")
    for word, count in unrecognized[:50]:
        # Try to categorize
        if len(word) >= 8:
            reason = "Mot long (agglutination probable)"
        elif not any(c in 'aeiou' for c in word):
            reason = "Pas de voyelles"
        elif word.endswith('ece') or word.endswith('ace') or word.endswith('oece'):
            reason = "Suffixe K&A non latin (-ece, -ace)"
        else:
            reason = "Combinaison K&A inconnue"
        out.append(f"| {word} | {count} | {reason} |")

    # Summary
    out.append("")
    out.append("---")
    out.append("## Synthese")
    out.append("")
    pct_recognized = len(recognized) * 100 // max(tested, 1)
    out.append(f"- **Taux de reconnaissance**: {pct_recognized}% ({len(recognized)}/{tested})")
    out.append(f"- **Occurrences promotables**: {total_promotable} (de LOW a HIGH)")
    out.append(f"- **Impact potentiel**: {total_promotable} mots supplementaires lisibles")
    out.append(f"  soit {total_promotable * 100 // 38442}% du manuscrit total")

    # Write
    report = '\n'.join(out)
    out_path = os.path.join(os.path.dirname(__file__), '..', 'output', 'COLLATINUS_VALIDATION.md')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\nReport: {out_path}")
    print(f"Recognized: {len(recognized)}/{tested} ({pct_recognized}%)")
    print(f"Promotable occurrences: {total_promotable}")


if __name__ == '__main__':
    main()
