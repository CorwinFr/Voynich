# L04 TRANSPOSITION CRACK — Anagrammes et permutations

Pour chaque mot L04, on teste :
1. TOUTES les permutations de tokens (token-level)
2. TOUTES les permutations de caracteres (char-level)
3. Rotations cycliques (shift left/right)
4. Echanges de paires adjacentes
5. Inversion (miroir)

Dictionnaire : 279 termes cibles

j1 `daiin` → no matches
j2 `otey` → no matches
j3 `ofeeey` → no matches
j4 `shes` → no matches
j7 `okeeod` → no matches
j10 `lkeeol` → no matches
j11 `dkedar` → no matches
j12 `yf` → no matches
## j13 `aros` → tokens: ['a', 'r', 'o', 's']
  **REVERSE_OF**: `rosa` (tokens:[0, 3, 2, 1])
  **EXACT**: `rosa` (tokens:[1, 2, 3, 0]) *** STRONG ***
  **SHIFT_L**: `rosa` (shift=1)
  **CHAR_ANAGRAM**: `rosa` (char-level) *** STRONG ***

j16 `chedaiin` → no matches
j18 `eeety` → no matches
j20 `deeodal` → no matches
j21 `vo` → no matches
j22 `tchor` → no matches
j23 `kedar` → no matches
j24 `dal` → no matches
j25 `daiin` → no matches
j26 `aiin` → no matches
j27 `otal` → no matches
j28 `daro` → no matches

---
## BILAN: 4 hits sur 20 mots-contenu

### TOUS LES HITS
| Jour | EVA | Type | Resultat | Detail |
|------|-----|------|----------|--------|
| 13 | aros       | REVERSE_OF      | rosa            | tokens:[0, 3, 2, 1] |
| 13 | aros       | EXACT           | rosa            | tokens:[1, 2, 3, 0] |
| 13 | aros       | SHIFT_L         | rosa            | shift=1 |
| 13 | aros       | CHAR_ANAGRAM    | rosa            | char-level |

### ANALYSE DE COHERENCE DES ANAGRAMMES

Paires EVA → Latin (anagrammes confirmes) :
  j13: `aros` → `rosa`
    Letters EVA: ['a', 'o', 'r', 's']
    Letters Latin: ['a', 'o', 'r', 's']
    *** ANAGRAMME PARFAIT (memes lettres) ***
