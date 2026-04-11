# OPERATION HOPE - VERDICT FINAL
## Date: 2026-04-11

---

## QUESTION POSEE

"Aucun systeme medical n'a pas de systeme de numeration. Soit on le trouve soit on arrete."

## REPONSE

Le VMS ne contient PAS de systeme de numeration explicite (pas de chiffres, pas de tally marks, pas de gallows-nombres).

Mais il contient un systeme morpho-suffixal ou le nombre de repetitions de caracteres (i dans -ain/-aiin/-aiiin, e dans -ey/-eey/-eeey) ENCODE DE L'INFORMATION qui varie massivement selon :
- La section (balnea vs pharma vs herbal : variation du ratio -aiin/-ain de 0.8 a 6.0)
- Le folio (variation de 0.16 a 42.0 entre folios pharma : 260x)
- Le prefixe (qok- ratio ~1:1, d- ratio ~4:1)

---

## FAITS ETABLIS (non contestables)

1. **Le ratio -aiin/-ain varie de 0.16 a 42.0 entre folios pharma.** Ce n'est pas grammatical.

2. **La famille qok- est massivement pharma-specifique** (P/H = 8 a 22 selon variante). 43.8% de tous les qok- sont en pharma.

3. **Les suffixes -eey/-edy distinguent les sections.** -eey: P/H = 3.87. -edy: P/H = 3.75.

4. **La distribution des gaps entre DOSE_CAND suit la meme forme exponentielle que l'AN.** Pic a gap=1 (22-26%), decroissance reguliere.

5. **f105r a 42 -aiin et ZERO -ain.** Aucune grammaire uniforme ne produit ca.

6. **Les systemes i-count et e-count sont independants** (r = 0.097). Ils encodent des choses differentes.

## HYPOTHESES REJETEES

- H1: Gallows = nombres -> REJETE (10.3% partout, structurel)
- H2: Tally marks (repetitions = comptage) -> REJETE (forme simple)
- a-i-n = 1, a-ii-n = 2, a-iii-n = 3 -> REJETE dans sa forme simple
  (distribution inversee vs AN : i=2 domine le VMS a 67%, i=1 domine l'AN a 36%)

## HYPOTHESES OUVERTES

- **Les suffixes -ain/-aiin encodent une distinction semantique liee au type de contenu** (listes vs prose, ou registre prescriptif vs descriptif). Le nombre de 'i' n'est pas un chiffre direct mais un marqueur morpho-semantique.

- **La famille qok- + suffixes variables pourrait encoder des unites de mesure** (qok-eey, qok-edy, qok-ain = 3 "unites" differentes). Non prouve.

- **Le pattern [mot long + mot en -ain/-aiin] reproduit la structure [ingredient + dose] de l'AN** avec la meme distribution de gaps. Compatible mais non discriminant (d'autres structures textuelles pourraient produire le meme pattern).

## DECISION

**ON CONTINUE LE PROJET.** Pas parce qu'on a trouve le systeme de numeration, mais parce que :

1. Le signal morpho-suffixal est REEL et INEXPLIQUE par une grammaire simple
2. La structure pharma du VMS est COMPATIBLE avec un texte pharmaceutique (distribution des gaps, densite des "marqueurs")
3. Les tests discriminants ultimes (co-occurrence structuree avec AN, decodage K&A des candidats) n'ont pas ete faits
4. L'hypothese "les nombres sont ecrits en toutes lettres" (comme dans un chiffrement a substitution d'un texte latin) reste viable : "duo drachmas" = 2 mots VMS, pas 1 symbole

Le systeme de numeration est probablement LEXICAL (mots entiers pour les nombres) et non SYMBOLIQUE (chiffres ou tally marks). C'est coherent avec un texte latin chiffre lettre par lettre ou "ii" dans ".ii." deviendrait un MOT EVA complet via la substitution.

## PROCHAINE ETAPE

Phase C : tester si K&A v12, applique aux candidats dose VMS, produit des mots latins de quantite/unite ou du bruit. C'est le test binaire final.

---

## FICHIERS PRODUITS (OPERATION_HOPE/)

### Scripts
- `parse_vms.py` : Parser IVTFF, segmentation, H1 gallows
- `analyze_hypotheses.py` : H2, H3, H8, H9, H10
- `analyze_deep.py` : Famille qok-, positions, suffixes
- `analyze_suffix_cross.py` : Prefixe x suffixe x section, co-occurrence
- `test_icount.py` : Distribution i-count, Benford, correlation
- `crib_aurea.py` : Alignement structurel AN vs VMS

### Donnees (data/)
- `LSI_ivtff_0d.txt` : Transcription IVTFF (38939 lignes)
- `vms_all_words.json`, `vms_pharma_words.json`, `vms_herbal_words.json`

### Resultats (results/)
- `freq_all.json`, `freq_pharma.json`, `freq_herbal.json`, `freq_astro.json`, `freq_balnea.json`
- `VERDICT.md` (v1), `VERDICT_v2.md`, `VERDICT_v3.md`, `VERDICT_FINAL.md`
