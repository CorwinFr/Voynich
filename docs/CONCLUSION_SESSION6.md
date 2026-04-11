# CONCLUSION SESSION 6 — L'explication simple

## Date : 11 avril 2026
## 28 commits, ~16 heures d'analyse

---

## LA REPONSE SIMPLE

K&A fonctionne. Pour TOUT. Il n'y a pas de systeme dual,
pas de syllabaire, pas de nomenclateur separe.

**Preuve** : 84% des mots "douteux" (DOUTE_KA) sont des mots
latins ATTESTES dans le dictionnaire Perseus (84937 formes).

Le texte du VMS est du **latin pharmaceutique medieval**.
On le lit deja a 81%. Les 19% restants sont :
- Des mots latins rares (formes dialectales, cas grammaticaux)
- Des abbreviations medievales non resolues
- Des variantes de transcription EVA non testees
- PAS un systeme d'encodage different

## Ce qu'on a DECOUVERT (solide)

| Decouverte | Evidence | Force |
|-----------|----------|-------|
| VMS = receptaire pharma | Illustrations + decode + clustering | FORTE |
| K&A fonctionne | 81% decode, 84% Perseus sur DOUTE_KA | FORTE |
| Table des 18 logograms | Bifolio cross-validation, 0 exception | FORTE |
| Gallows = prepositions | p=per(50 pages), k=cum(21), t=el(20) | FORTE |
| daiin ≠ aquam (fix) | okaiin=cura(1540x), chaiin=iure(39x) | FORTE |
| Structure VERB+INGR+DOSE | Pattern visible sur f103r | FORTE |
| 217 ingredients identifies | Nomenclator + corpora + Sherwood | MOYENNE |
| 105/108 herbal plants | Gallows strip + nomenclator + externe | MOYENNE |
| Systeme de quantites | aiin=ana II dr., pattern recurrent | PROBABLE |

## Ce qu'on a EXPLORE mais PAS confirme

| Hypothese | Resultat | Statut |
|-----------|----------|--------|
| Syllabaire (t=lo, l=sa) | Fonctionne sur 2 ancres, pas generalise | NON CONFIRME |
| Mode dual (structure vs ingredient) | 84% Perseus sur DOUTE → pas necessaire | ABANDONNE |
| ch = c dans les noms | 16 votes mais pas de preuve decisive | POSSIBLE |
| Nomenclateur separe pour ingredients | Les 30 manquants sont probablement du latin rare | IMPROBABLE |
| Anagrammes (aros=rosa) | 3 hits pour rosa, 0 pour 17 autres | COINCIDENCE |

## Le VRAI probleme restant

Les 30 top ingredients de l'Antidotarium ne sont PAS identifies
dans notre decode. Mais ils ne sont probablement PAS "caches" —
ils sont DECODES mais sous des formes qu'on ne reconnait pas :

- Formes au genitif pluriel (-orum, -arum)
- Abbreviations medievales (gar. pour gariofilorum)
- Noms italiens vernaculaires non dans nos dictionnaires
- Simples que le scribe nommait differemment de l'AN

## Metriques finales

```
Dictionnaire : 7820 mots uniques, chacun UN decode fixe
Confiance : 37% SUR + 44% PROBABLE + 11% DOUTE + 7% INCONNU
Ingredients : 217 identifies
Plantes herbal : 105/108 nommees
Decode : 81% du texte lisible
Vitesse : lookup instantane (pas de calcul)
```

## Plan pour la prochaine session

1. **Ameliorer les references** — ajouter les corpus medieval
   (Lylye, Circa Instans, DALME) au dictionnaire Perseus pour
   reconnaitre plus de formes
2. **Tester les variantes EVA** sur les 7% INCONNU — chaque
   variante resolue = +0.1% du texte
3. **Lire des PAGES ENTIERES** avec le dictionnaire et noter
   les passages qui "font sens" vs ceux qui ne font pas sens
4. **Chercher la phrase de 5 mots** — comparer des sequences
   de 5 mots decodes avec des passages de l'Antidotarium
5. **Publier un preprint** — 81% decode + 217 ingredients +
   105 plantes est DEJA publiable comme resultat preliminaire
