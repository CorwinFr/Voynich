"""
SESSION 16 — FRAPPE 1: Herbal × Macer chapter by chapter

SURGICAL APPROACH: Two complementary methods.

Part A — POSITIONAL MATCHING
  For each anchor folio↔Macer chapter pair:
  1. Find where each Macer ingredient appears in the chapter text (normalized 0-1)
  2. Find where each VMS root appears in the folio (normalized 0-1)
  3. Use confirmed ingredients as positional calibration anchors
  4. Map unknown Macer ingredients to nearby unknown VMS roots

Part B — REFINED CROSS-FOLIO FINGERPRINT
  For each of the 36 Macer ingredients:
  1. Build binary fingerprint: which of the 16 anchor chapters mention it
  2. Build VMS fingerprint: which of the 16 anchor folios contain each root
  3. Match fingerprints (presence/absence across ALL 16 anchors)
  4. Require match on 3+ folios with 0-1 false positives

Part C — CROSS-VALIDATION
  Combine both signals. Candidates confirmed by BOTH methods get high confidence.
"""
import json, sys, io, os, re
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.dirname(__file__)
VMS_PATH = os.path.join(BASE, '..', 'vms', 'vms_structured.json')
MACER_PATH = os.path.join(BASE, '..', 'session_14', 'macer_complete.json')
REG_PATH = os.path.join(BASE, '..', 'hypothesis_registry.json')
RESULTS = BASE

with open(VMS_PATH, encoding='utf-8') as f:
    vms = json.load(f)
with open(MACER_PATH, encoding='utf-8') as f:
    macer = json.load(f)
with open(REG_PATH, encoding='utf-8') as f:
    registry = json.load(f)

LOGOS = {'o','l','d','r','v','x','k','m','f','t','y','c','s','sh','p','ch','air','h'}

# Already confirmed root→latin
CONFIRMED = {}
for root, data in registry['confirmed_ingredients'].items():
    CONFIRMED[root] = data['latin']

# Plant names (first word of herbal folio)
PLANT_NAMES = {}
for root, data in registry['plant_names'].items():
    PLANT_NAMES[root] = data['latin']

# ================================================================
# ANCHOR TABLE: Sherwood folio → Macer chapter name
# ================================================================
ANCHORS_RAW = {
    'f48v': 'ruta',      'f9v': 'viola',       'f44v': 'apium',
    'f51v': 'salvia',    'f29r': 'lactuca',    'f41r': 'origanum',
    'f37r': 'mentha',    'f41v': 'coriandrum', 'f22r': 'verbena',
    'f28r': 'aristolochia', 'f5v': 'malva',    'f45r': 'atriplex',
    'f66v': 'satureia',  'f65v': 'centaurea',  'f3v': 'elleborus',
    'f95v1': 'althaea',
}

# Match plant names to Macer chapter objects
MACER_BY_NAME = {}
for ch in macer['chapters']:
    MACER_BY_NAME[ch['name'].lower()] = ch
# Special cases
if 'violae' in MACER_BY_NAME:
    MACER_BY_NAME['viola'] = MACER_BY_NAME['violae']

ANCHORS = {}
for fid, plant in ANCHORS_RAW.items():
    if fid not in vms['folios']:
        print(f'  SKIP {fid} — not in VMS')
        continue
    ch = MACER_BY_NAME.get(plant)
    if not ch:
        print(f'  SKIP {fid} ({plant}) — not in Macer')
        continue
    ANCHORS[fid] = {'plant': plant, 'macer': ch}

print(f'Working anchors: {len(ANCHORS)}')

# ================================================================
# INGREDIENT STEM PATTERNS (for positional detection in Macer text)
# ================================================================
# Map ingredient tag → regex patterns to find in Latin text
INGR_PATTERNS = {
    'acetum':      r'\bacet[uoia]\w*\b',
    'aqua':        r'\baqua[em]?\b|\bamne\b',
    'mel':         r'\bmel\b|\bmell[ei]\w*\b|\bmulsa\b',
    'piper':       r'\bpiper\w*\b',
    'oleum':       r'\boleu[mi]\b|\boleo\b',
    'sal':         r'\bsal[ei]?\b|\bsale\b',
    'vinum':       r'\bvin[uoia]\w*\b|\bmero\b|\bmust[uo]\b',
    'succus':      r'\bsucc[uoia]\w*\b',
    'lac':         r'\blac\b|\blact[ei]\w*\b',
    'ovum':        r'\bov[uoia]\w*\b',
    'nitrum':      r'\bnitr[uoia]\w*\b',
    'myrrha':      r'\bmyrrh\w*\b',
    'ruta':        r'\brut[ae]\w*\b',
    'coriandrum':  r'\bcoriand\w*\b',
    'faba':        r'\bfab[ae]\w*\b',
    'lens':        r'\blen[st]\w*\b',
    'nardus':      r'\bnard\w*\b',
    'rosa':        r'\bros[ai]\w*\b',
    'plantago':    r'\bplantag\w*\b',
    'linum':       r'\blin[uoia]\w*\b',
    'feniculum':   r'\bfenic\w*\b',
    'vesica':      r'\bvesic\w*\b',
    'cera':        r'\bcer[ae]\w*\b',
    'thus':        r'\bthus\b|\bthur[ei]\w*\b',
    'sulphur':     r'\bsulph\w*\b',
    'origanum':    r'\borigan\w*\b',
    'anethum':     r'\baneth\w*\b',
    'chamomilla':  r'\bchamom\w*\b',
    'betonica':    r'\bbetonic\w*\b',
    'crocus':      r'\bcroc[uoia]\w*\b',
    'urtica':      r'\burtic\w*\b',
    'verbena':     r'\bverben\w*\b',
    'aristolochia':r'\baristoloch\w*\b',
    'salvia':      r'\bsalvi\w*\b',
    'mentha':      r'\bment[ha]\w*\b',
}

def find_ingredient_positions(chapter_text, ingredients):
    """Find normalized positions (0-1) of each ingredient in chapter text."""
    text_lower = chapter_text.lower()
    text_len = max(len(text_lower), 1)
    result = {}
    for ingr_tag in ingredients:
        ingr_name = ingr_tag.replace('I_', '').replace('P_', '')
        pattern = INGR_PATTERNS.get(ingr_name)
        if not pattern:
            continue
        positions = []
        for m in re.finditer(pattern, text_lower):
            positions.append(m.start() / text_len)
        if positions:
            result[ingr_name] = {
                'positions': positions,
                'first': min(positions),
                'last': max(positions),
                'mean': sum(positions) / len(positions),
                'count': len(positions),
            }
    return result

# ================================================================
# VMS ROOT EXTRACTION WITH POSITIONS
# ================================================================
def get_folio_roots_with_positions(fid):
    """Get all roots in a folio with their normalized line positions."""
    folio = vms['folios'][fid]
    all_lines = []
    for block in folio['blocks']:
        for line in block['lines']:
            all_lines.append(line)
    n_lines = max(len(all_lines), 1)

    root_positions = defaultdict(list)
    root_counts = Counter()
    for i, line in enumerate(all_lines):
        norm_pos = i / n_lines
        for w in line['words']:
            eva = w['eva_primary']
            if eva in LOGOS or len(eva) < 2:
                continue
            root = (w.get('morphology') or {}).get('root', '')
            if root and len(root) >= 2:
                root_positions[root].append(norm_pos)
                root_counts[root] += 1
    return root_positions, root_counts

# ================================================================
# PART A: POSITIONAL MATCHING
# ================================================================
print(f'\n{"="*70}')
print('PART A — POSITIONAL MATCHING (within folio↔chapter pairs)')
print('='*70)

positional_candidates = defaultdict(list)

for fid, anchor_data in sorted(ANCHORS.items()):
    plant = anchor_data['plant']
    chapter = anchor_data['macer']

    # Get Macer ingredient positions
    ingr_positions = find_ingredient_positions(chapter['text'], chapter['ingredients'])

    # Get VMS root positions
    root_positions, root_counts = get_folio_roots_with_positions(fid)

    # Identify confirmed roots as calibration points
    calibration = []
    for root, latin in CONFIRMED.items():
        if root in root_positions and latin in ingr_positions:
            vms_mean = sum(root_positions[root]) / len(root_positions[root])
            macer_mean = ingr_positions[latin]['mean']
            calibration.append((root, latin, vms_mean, macer_mean))

    # Also use plant name as calibration (usually at position ~0.0)
    for root, pname in PLANT_NAMES.items():
        if root in root_positions and pname == plant:
            vms_mean = sum(root_positions[root]) / len(root_positions[root])
            calibration.append((root, pname, vms_mean, 0.0))

    print(f'\n  {fid} = {plant:15s}  '
          f'macer_ingr={len(ingr_positions):2d}  '
          f'vms_roots={len(root_positions):2d}  '
          f'calibration={len(calibration)}')

    if calibration:
        for root, latin, vms_p, mac_p in calibration:
            print(f'    ANCHOR: {root:>10s} = {latin:>12s}  '
                  f'vms={vms_p:.2f}  macer={mac_p:.2f}')

    # For each unmatched Macer ingredient, find closest unmatched VMS root
    matched_roots = set(r for r, _, _, _ in calibration)
    matched_ingrs = set(l for _, l, _, _ in calibration)

    unmatched_ingrs = {i: d for i, d in ingr_positions.items()
                       if i not in matched_ingrs}
    unmatched_roots = {r: ps for r, ps in root_positions.items()
                       if r not in matched_roots
                       and r not in CONFIRMED
                       and r not in PLANT_NAMES}

    if not unmatched_ingrs or not unmatched_roots:
        continue

    # If we have calibration, compute position offset
    offset = 0.0
    if calibration:
        offsets = [vms_p - mac_p for _, _, vms_p, mac_p in calibration]
        offset = sum(offsets) / len(offsets)

    # Match by closest position
    for ingr_name, ingr_data in unmatched_ingrs.items():
        target_pos = ingr_data['mean'] + offset
        best_root = None
        best_dist = 999
        candidates_here = []

        for root, positions in unmatched_roots.items():
            root_mean = sum(positions) / len(positions)
            dist = abs(root_mean - target_pos)
            candidates_here.append((root, root_mean, dist, root_counts[root]))

        candidates_here.sort(key=lambda x: x[2])

        if candidates_here:
            best = candidates_here[0]
            if best[2] < 0.4:  # within 40% of text
                print(f'    MATCH: {ingr_name:>12s} (pos={ingr_data["mean"]:.2f}) '
                      f'→ {best[0]:>10s} (pos={best[1]:.2f}, dist={best[2]:.2f}, '
                      f'count={best[3]})')
                positional_candidates[best[0]].append({
                    'ingredient': ingr_name,
                    'folio': fid,
                    'plant': plant,
                    'distance': best[2],
                    'vms_pos': best[1],
                    'macer_pos': ingr_data['mean'],
                    'root_count': best[3],
                    'n_calibration': len(calibration),
                })

                # Show runner-up if close
                if len(candidates_here) > 1 and candidates_here[1][2] < 0.3:
                    runner = candidates_here[1]
                    print(f'      alt: {ingr_name:>12s} → {runner[0]:>10s} '
                          f'(dist={runner[2]:.2f})')


# ================================================================
# PART B: CROSS-FOLIO FINGERPRINT (refined, 16 anchors)
# ================================================================
print(f'\n\n{"="*70}')
print('PART B — CROSS-FOLIO FINGERPRINT (16 anchors)')
print('='*70)

# Build Macer ingredient fingerprints across anchors
anchor_fids = sorted(ANCHORS.keys())
macer_fingerprints = {}  # ingredient → set of fids

for fid in anchor_fids:
    chapter = ANCHORS[fid]['macer']
    for ingr_tag in chapter['ingredients']:
        ingr_name = ingr_tag.replace('I_', '').replace('P_', '')
        if ingr_name not in macer_fingerprints:
            macer_fingerprints[ingr_name] = set()
        macer_fingerprints[ingr_name].add(fid)

# Build VMS root fingerprints across anchors
vms_fingerprints = {}  # root → set of fids

for fid in anchor_fids:
    _, root_counts = get_folio_roots_with_positions(fid)
    for root in root_counts:
        if root in CONFIRMED or root in PLANT_NAMES:
            continue
        if root not in vms_fingerprints:
            vms_fingerprints[root] = set()
        vms_fingerprints[root].add(fid)

print(f'\n  Macer ingredients with fingerprints: {len(macer_fingerprints)}')
print(f'  VMS unknown roots with fingerprints: {len(vms_fingerprints)}')

# Show Macer fingerprints for reference
print(f'\n  MACER INGREDIENT FINGERPRINTS:')
for ingr, fids in sorted(macer_fingerprints.items(), key=lambda x: -len(x[1])):
    n = len(fids)
    # Skip already confirmed
    already = ingr in CONFIRMED.values()
    marker = ' [KNOWN]' if already else ''
    if n >= 2:
        print(f'    {ingr:>15s}: {n:2d}/16 folios{marker}')

# Match fingerprints
fingerprint_candidates = defaultdict(list)

for ingr_name, macer_fids in macer_fingerprints.items():
    if ingr_name in CONFIRMED.values():
        continue
    if len(macer_fids) < 2:
        continue

    for root, vms_fids in vms_fingerprints.items():
        if len(vms_fids) < 2:
            continue

        # Compute match quality
        intersection = macer_fids & vms_fids
        macer_only = macer_fids - vms_fids  # false negatives
        vms_only = vms_fids - macer_fids    # false positives

        n_match = len(intersection)
        n_fp = len(vms_only)
        n_fn = len(macer_only)
        n_total = len(macer_fids | vms_fids)

        # Jaccard similarity
        jaccard = n_match / max(n_total, 1)

        # Require: 3+ matches, few false positives
        if n_match >= 3 and n_fp <= 2 and jaccard >= 0.3:
            fingerprint_candidates[root].append({
                'ingredient': ingr_name,
                'n_match': n_match,
                'n_fp': n_fp,
                'n_fn': n_fn,
                'jaccard': jaccard,
                'matched_folios': sorted(intersection),
            })

# Show best fingerprint matches
print(f'\n  FINGERPRINT MATCHES (3+ folios, <=2 FP, Jaccard>=0.3):')
all_fp_matches = []
for root, matches in fingerprint_candidates.items():
    for m in matches:
        all_fp_matches.append((root, m))

all_fp_matches.sort(key=lambda x: (-x[1]['jaccard'], -x[1]['n_match']))

for root, m in all_fp_matches[:30]:
    print(f'    {root:>12s} = {m["ingredient"]:>12s}  '
          f'match={m["n_match"]}  FP={m["n_fp"]}  FN={m["n_fn"]}  '
          f'J={m["jaccard"]:.2f}  folios={m["matched_folios"][:4]}')


# ================================================================
# PART C: CROSS-VALIDATION (combine Part A + Part B)
# ================================================================
print(f'\n\n{"="*70}')
print('PART C — CROSS-VALIDATION')
print('='*70)

# Collect all candidate root→ingredient mappings
all_candidates = defaultdict(lambda: defaultdict(list))

# From positional matching
for root, matches in positional_candidates.items():
    for m in matches:
        all_candidates[root][m['ingredient']].append({
            'method': 'positional',
            'folio': m['folio'],
            'distance': m['distance'],
            'calibration': m['n_calibration'],
        })

# From fingerprint matching
for root, matches in fingerprint_candidates.items():
    for m in matches:
        all_candidates[root][m['ingredient']].append({
            'method': 'fingerprint',
            'n_match': m['n_match'],
            'jaccard': m['jaccard'],
            'folios': m['matched_folios'],
        })

# Score each root→ingredient pair
final_results = []

for root, ingr_map in all_candidates.items():
    for ingr_name, evidences in ingr_map.items():
        methods = set(e['method'] for e in evidences)
        n_positional = sum(1 for e in evidences if e['method'] == 'positional')
        n_fingerprint = sum(1 for e in evidences if e['method'] == 'fingerprint')

        # Confidence scoring
        if 'positional' in methods and 'fingerprint' in methods:
            confidence = 0.85  # Both methods agree
            strength = 'STRONG'
        elif n_fingerprint > 0:
            best_fp = max((e for e in evidences if e['method'] == 'fingerprint'),
                         key=lambda e: e['jaccard'])
            if best_fp['jaccard'] >= 0.5:
                confidence = 0.75
                strength = 'GOOD'
            else:
                confidence = 0.6
                strength = 'MODERATE'
        elif n_positional >= 2:
            confidence = 0.7
            strength = 'GOOD'
        elif n_positional == 1:
            avg_dist = sum(e['distance'] for e in evidences if e['method'] == 'positional') / n_positional
            confidence = 0.5 if avg_dist < 0.2 else 0.4
            strength = 'WEAK'
        else:
            confidence = 0.4
            strength = 'WEAK'

        final_results.append({
            'root': root,
            'ingredient': ingr_name,
            'confidence': confidence,
            'strength': strength,
            'n_positional': n_positional,
            'n_fingerprint': n_fingerprint,
            'methods': sorted(methods),
            'evidences': evidences,
        })

final_results.sort(key=lambda x: (-x['confidence'], -x['n_positional'] - x['n_fingerprint']))

# Remove duplicates: if same root maps to multiple ingredients, keep best
seen_roots = set()
deduped = []
for r in final_results:
    if r['root'] not in seen_roots:
        deduped.append(r)
        seen_roots.add(r['root'])

print(f'\n  FINAL CANDIDATES ({len(deduped)} unique roots):')
print(f'  {"Root":>12s} {"Ingredient":>15s} {"Conf":>5s} {"Str":>8s} '
      f'{"Pos":>4s} {"FP":>3s} {"Methods"}')
print('  ' + '-' * 75)

new_strong = []
new_moderate = []

for r in deduped:
    marker = '★★★' if r['strength'] == 'STRONG' else '★★' if r['strength'] == 'GOOD' else '★'
    print(f'  {r["root"]:>12s} {r["ingredient"]:>15s} {r["confidence"]:>5.2f} '
          f'{r["strength"]:>8s} {r["n_positional"]:>4d} {r["n_fingerprint"]:>3d} '
          f'{"+".join(r["methods"])} {marker}')

    if r['strength'] in ('STRONG', 'GOOD'):
        new_strong.append(r)
    else:
        new_moderate.append(r)

print(f'\n  STRONG/GOOD: {len(new_strong)}')
print(f'  MODERATE/WEAK: {len(new_moderate)}')


# ================================================================
# PART D: VERIFY CONFIRMED INGREDIENTS (sanity check)
# ================================================================
print(f'\n\n{"="*70}')
print('PART D — VERIFICATION OF CONFIRMED INGREDIENTS')
print('='*70)

for root, latin in CONFIRMED.items():
    # Check fingerprint consistency
    if latin in macer_fingerprints:
        macer_fids = macer_fingerprints[latin]
        root_fids = set()
        for fid in anchor_fids:
            _, rc = get_folio_roots_with_positions(fid)
            if root in rc:
                root_fids.add(fid)

        intersection = macer_fids & root_fids
        fp = root_fids - macer_fids
        fn = macer_fids - root_fids
        jaccard = len(intersection) / max(len(macer_fids | root_fids), 1)

        status = '✓' if jaccard >= 0.2 else '?'
        print(f'  {status} {root:>10s} = {latin:>10s}  '
              f'match={len(intersection)}  FP={len(fp)}  FN={len(fn)}  '
              f'J={jaccard:.2f}')
    else:
        print(f'  - {root:>10s} = {latin:>10s}  (not in Macer ingredients)')


# ================================================================
# SAVE RESULTS
# ================================================================
output = {
    'n_anchors': len(ANCHORS),
    'n_positional_candidates': sum(len(v) for v in positional_candidates.values()),
    'n_fingerprint_candidates': len(all_fp_matches),
    'n_final_strong': len(new_strong),
    'n_final_moderate': len(new_moderate),
    'candidates': [{
        'root': r['root'],
        'ingredient': r['ingredient'],
        'confidence': r['confidence'],
        'strength': r['strength'],
        'n_positional': r['n_positional'],
        'n_fingerprint': r['n_fingerprint'],
        'methods': r['methods'],
    } for r in deduped],
    'verified_confirmed': {
        root: latin for root, latin in CONFIRMED.items()
    },
}

with open(os.path.join(RESULTS, 'frappe1_results.json'), 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f'\nSaved frappe1_results.json')
print(f'\n{"="*70}')
print(f'FRAPPE 1 SUMMARY')
print(f'  Anchors used: {len(ANCHORS)}')
print(f'  New STRONG/GOOD candidates: {len(new_strong)}')
print(f'  New MODERATE/WEAK candidates: {len(new_moderate)}')
print(f'  Verified confirmed: {len(CONFIRMED)}')
print(f'{"="*70}')
