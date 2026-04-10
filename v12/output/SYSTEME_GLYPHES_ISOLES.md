# SYSTEME DES GLYPHES ISOLES — Synthese multi-folios

## DECOUVERTE : Un systeme VMS-wide de glyphes isoles

Les glyphes isoles (un seul caractere par position) ne sont PAS des mots.
Ils apparaissent dans au moins 6 folios du VMS avec la MEME fonction :
marqueurs structurels, separateurs de sections, ou elements d'un alphabet/repertoire.

## Les folios qui utilisent ce systeme

| Folio | Nb isoles | Glyphes | Fonction | Note |
|-------|-----------|---------|----------|------|
| **f66r** | **34** | y,o,s,sh,d,f,x,c,t,l,r,p + @172,@195 | REPERTOIRE/ALPHABET | ZL note "cf f57v seq." |
| **f57v L04** | **9** | o,d,l,s,y,k,x,v + @172 | Separateurs de secteur | Notre cible |
| **f57v L03** | **68** | o,l,d,r,v,x,k,m,f,t,y,c,p + @169-172 | CLE (4x17 pattern) | Cipher key |
| **f69r** | **6** | y,d,o,l,s,e[d:g] | Branches d'etoile | Labels de secteur |
| **f49v** | ~20 | divers | INDEXATION | Alternance label/texte |
| **f76r** | ~9 | divers | INDEXATION | Partage 7 mots avec L04 |
| **f75v** | ~6 | divers | INDEXATION | Structure similaire |

## Le PONT critique : f66r ↔ f57v

Le transcripteur ZL a note DEUX references croisees explicites :
- f66r.37 (`c`) : `<!cf f57v seq.>` = "comparer avec la sequence de f57v"
- f66r.38 (`@172`) : `<!cf f57v?>` = "comparer avec f57v ?"

Le symbole @172 (lambda inverse) apparait dans :
- f57v L03 : 4 fois (fin de chaque quadrant de la cle)
- f57v L04 : 1 fois (entre j24 et j25)
- f66r : 1 fois (position 38 dans la sequence d'isoles)

## Le repertoire de f66r : un ALPHABET de 14-17 glyphes

f66r lignes 16-49 contiennent 34 glyphes isoles consecutifs.
C'est 2 × 17, la meme taille qu'un quadrant de L03.

**Les 13 glyphes uniques de f66r** : y, o, s, sh, d, f, x, c, t, l, r, p, air
**Les 13 glyphes uniques de L03** : o, l, d, r, v, x, k, m, f, t, y, c, p, I

**9 sont partages** (c, d, f, l, o, r, t, x, y).
**f66r ajoute** : s, sh, air, p
**L03 ajoute** : k, m, v, I

Ensemble, les deux repertoires couvrent **17 glyphes** + les symboles speciaux.
C'est exactement le nombre de glyphes uniques dans L04 (17) !

## Interpretation : f66r = table de correspondance

f66r pourrait etre une TABLE DE REFERENCE montrant l'alphabet
complet utilise dans les instruments (f57v, f69r, etc.).

La structure de f66r :
1. Lignes 1-15 : 15 MOTS courts (rary, sals, qon, dary, ykeol, saly, salf,
   fary, qotesy, ykaly, doly, saiin, qokal, qolsa, raral)
2. Lignes 16-49 : 34 GLYPHES ISOLES (le repertoire)
3. Lignes 50-56 : Texte paragraphe (contenu)
4. Lignes 57+ : Suite du texte

Les 15 mots courts (lignes 1-15) pourraient etre les NOMS ou
VALEURS des 15 premiers glyphes du repertoire. C'est-a-dire :
- rary = nom/valeur du glyphe 1
- sals = nom/valeur du glyphe 2
- etc.

## Ce que ca implique pour L04

1. Les 9 glyphes isoles de L04 sont des elements du REPERTOIRE f66r/L03
2. Ils fonctionnent comme des SEPARATEURS ou INDEX, pas comme des mots
3. Leur "signification" est POSITIONNELLE (ils indiquent un secteur,
   une categorie, ou un numero) pas LINGUISTIQUE
4. Le @172 est un marqueur special = FIN DE SECTION / RETOUR

## Questions ouvertes

1. Les 15 mots courts de f66r (lignes 1-15) sont-ils les DEFINITIONS
   des 15 premiers glyphes du repertoire ?
2. Les lignes 1-15 de f66r suivent-elles le meme ORDRE que les glyphes
   de f66r lignes 16-49 ? (rary = y ? sals = o ? etc.)
3. Le @195 (f66r.42) est-il un autre symbole special comme le @172 ?
4. Pourquoi f66r a 34 isoles (2×17) et pas 17 (1 quadrant) ou 68 (4 quadrants) ?
