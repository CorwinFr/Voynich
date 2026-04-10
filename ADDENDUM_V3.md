# Addendum V3 — Correction and Update

*Guillaume Clement, April 2026*
*Following Addendum V2 (DOI: 10.5281/zenodo.19477552)*

---

## Summary

Addendum V2 identified architectural flaws in our initial pipeline that inflated results from 36.7% (real signal) to 89.3% (artifact). Since then, we rebuilt the analysis from scratch (V19 through V40). This short update corrects the record and confirms which findings hold.

## What was wrong (corrected)

An architectural error in the multi-candidate scorer amplified a modest signal (+18 pp above random) into a misleading headline (89.3%). The scorer was searching the entire Latin dictionary for the best match, not decoding the actual text. This was identified in V13-V14 and documented honestly in Addendum V2. The scorer has been removed. All subsequent work uses direct structural analysis of the EVA transcription without optimization.

## What was right (confirmed with stronger evidence)

The core findings from the initial publication have been independently retested and hold:

**The PREFIX + ROOT morphological system** is real. 36,983 tokens decompose into a structured system of prefixes, state markers, quantity indicators, and base suffixes. A falsification test on random EVA-like text produces 3.6% structural match vs 64.5% on the real corpus. The structure is not an artifact.

**The Tironian Notes connection** holds. Z-score of 9.4 on 500 random trials (V20). The manuscript's notation system shares statistical properties with the medieval Latin shorthand tradition.

**The pharmaceutical interpretation** is supported. Four recipe patterns from the Antidotarium Nicolai (Salerno, 12th c.) match decoded lines: ointment base (oleum + cera), filtered vinegar preparation (acetum + cola), saline wash (aqua + sal), and compound formulation with equal parts (ana). The verb-to-ingredient ratio in decoded recipe sections is 6:1 to 8:1, consistent with real pharmaceutical Latin (target: 3-8:1).

**The sh/ch binary** is the strongest single finding. Two sets of tokens sharing the same suffix but differing only in their sh- or ch- prefix show a sectorial correlation of r = 0.956. This means sh-X and ch-X refer to the same substance in two different states. Random token pairs show r = 0.031. This cannot be explained by chance.

## What remains uncertain

The specific identity of most substances is not proven. We have proposed mappings (ol = oleum, ar = aqua, al = sal, etc.) with a permutation z-score of 2.09, which is statistically significant but not overwhelming. These are our best hypotheses, not established facts.

No complete Latin sentence has been reconstructed. The decoded output reads as compact pharmaceutical notation, not as continuous prose. This is consistent with our model (a notation system, not a ciphered language) but it means the manuscript cannot yet be "read" in the traditional sense.

## What we can say with confidence

The Voynich Manuscript encodes a structured, non-random system with pharmaceutical vocabulary, a productive morphological grammar, and statistical properties consistent with medieval Latin shorthand. It is not a hoax, not a random cipher, and not a natural language in simple substitution. It is most likely a professional notation system created by a single author for his own use.

The complete test code (V13-V40), decoded manuscripts, and all raw results are available in `v12/validation_v2/` on github.com/CorwinFr/Voynich.

---
---

# Addendum V3 — Correction et mise a jour

*Guillaume Clement, avril 2026*
*Suite a l'Addendum V2 (DOI: 10.5281/zenodo.19477552)*

---

## Resume

L'Addendum V2 avait identifie des defauts architecturaux dans notre pipeline initial, qui gonflaient les resultats de 36,7% (signal reel) a 89,3% (artefact). Depuis, nous avons reconstruit l'analyse de zero (V19 a V40). Cette courte mise a jour corrige le bilan et confirme ce qui tient.

## Ce qui etait faux (corrige)

Une erreur d'architecture dans le scorer multi-candidats amplifiait un signal modeste (+18 pp au-dessus du hasard) en un chiffre trompeur (89,3%). Le scorer cherchait le meilleur match dans tout le dictionnaire latin, au lieu de decoder le texte reel. Cela a ete identifie en V13-V14 et documente honnetement dans l'Addendum V2. Le scorer a ete supprime. Tout le travail ulterieur utilise l'analyse structurelle directe de la transcription EVA, sans optimisation.

## Ce qui etait juste (confirme avec des preuves plus solides)

Les resultats fondamentaux de la publication initiale ont ete retestes independamment et tiennent :

**Le systeme morphologique PREFIXE + RACINE** est reel. 36 983 tokens se decomposent en un systeme structure de prefixes, marqueurs d'etat, indicateurs de quantite et suffixes de base. Un test de falsification sur du texte EVA aleatoire produit 3,6% de correspondance structurelle contre 64,5% sur le vrai corpus. La structure n'est pas un artefact.

**La connexion aux Notes Tironiennes** tient. Z-score de 9,4 sur 500 essais aleatoires (V20). Le systeme de notation du manuscrit partage des proprietes statistiques avec la tradition de stenographie latine medievale.

**L'interpretation pharmaceutique** est etayee. Quatre motifs de recettes de l'Antidotarium Nicolai (Salerne, XIIe s.) correspondent a des lignes decodees : base d'onguent (oleum + cera), preparation vinaigree filtree (acetum + cola), lavage salin (aqua + sal), et formulation composee a parts egales (ana). Le ratio verbes/ingredients dans les sections de recettes decodees est de 6:1 a 8:1, coherent avec le latin pharmaceutique reel (cible : 3-8:1).

**Le binaire sh/ch** est le resultat individuel le plus solide. Deux ensembles de tokens partageant le meme suffixe mais ne differant que par leur prefixe sh- ou ch- montrent une correlation sectorielle de r = 0,956. Cela signifie que sh-X et ch-X designent la meme substance dans deux etats differents. Des paires aleatoires montrent r = 0,031. Cela ne peut pas s'expliquer par le hasard.

## Ce qui reste incertain

L'identite specifique de la plupart des substances n'est pas prouvee. Nous avons propose des mappings (ol = oleum, ar = aqua, al = sal, etc.) avec un z-score de permutation de 2,09, ce qui est statistiquement significatif mais pas ecrasant. Ce sont nos meilleures hypotheses, pas des faits etablis.

Aucune phrase latine complete n'a ete reconstituee. Le resultat decode se lit comme de la notation pharmaceutique compacte, pas comme de la prose continue. C'est coherent avec notre modele (un systeme notationnel, pas une langue chiffree), mais cela signifie que le manuscrit ne peut pas encore etre "lu" au sens traditionnel.

## Ce que nous pouvons affirmer avec confiance

Le Manuscrit de Voynich encode un systeme structure, non aleatoire, avec un vocabulaire pharmaceutique, une grammaire morphologique productive, et des proprietes statistiques coherentes avec la stenographie latine medievale. Ce n'est pas un canular, pas un chiffre aleatoire, et pas une langue naturelle en substitution simple. C'est tres probablement un systeme de notation professionnel cree par un auteur unique pour son propre usage.

Le code complet des tests (V13-V40), les manuscrits decodes et tous les resultats bruts sont disponibles dans `v12/validation_v2/` sur github.com/CorwinFr/Voynich.
