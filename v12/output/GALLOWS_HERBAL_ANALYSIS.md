# GALLOWS ANALYSIS — Premiers mots des pages herbal

## Decouverte : le gallows est une PREPOSITION, pas un classificateur

108 pages herbal analysees. Le PREMIER MOT commence presque toujours par un gallows :

| Gallows | Pages | % | Decode | Sens |
|---------|-------|---|--------|------|
| p | 50 | 45% | per- | pour/par |
| k | 21 | 19% | cum- | avec |
| t | 20 | 18% | el- | le |
| f | 8 | 7% | per- | = p (homophonie) |
| aucun | 9 | 8% | - | debut atypique |

p et f sont SYNONYMES (homophonie f/p). Le gallows introduit le sujet :
"Pour [plante]", "Avec [plante]", "Le [plante]"

## Le nom de la plante est APRES le gallows

Le vrai nom est dans le RESTE du mot, pas dans le gallows :
- pchor = p(per) + chor(iera/cola) → la plante est "chor"
- kchsy = k(cum) + chsy → la plante est "chsy"  
- tshol = t(el) + shol(ciens) → la plante est "shol"

## Implications pour le decodage

Le pipeline doit STRIPPER le gallows pour decoder le nom de plante.
Ensuite matcher le reste contre le nomenclator italien.
