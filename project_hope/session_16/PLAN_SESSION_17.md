# PLAN SESSION 17 — Évaluation ROI par attaque

## Diagnostic (session 16)

- Décodage réel : ~5% (3-4 ingrédients fiables)
- 8 faits structurels prouvés
- 62 mots fonctionnels identifiés (32% du texte = grammaire)
- Principale découverte : les openers pharma CONTIENNENT les noms de plantes
  (pchedal = p+pched(lens)+al, 27% vérifiés, probablement plus)

## ATTAQUES CLASSÉES PAR ROI (retour sur investissement)

### ATTAQUE 1 — Openers pharma = noms de recettes (ROI: ★★★★★)
**Potentiel** : Décoder TOUTES les recettes par leur plante.
**Méthode** : Chaque opener pharma = gallows + racine_plante + suffixe.
On connaît 23 racines de plantes. Matcher les 286 openers.
- 27% matchent déjà avec des racines ≥3 chars
- Beaucoup d'autres matcheront si on inclut les racines 2 chars
- Pour chaque match : la recette EST pour cette plante → contrainte forte

**Ce que ça apporte** :
- Identification de la plante-cible de 50-100 recettes pharma
- Si on sait que recette X = "pour la ruta", alors ses ingrédients
  DOIVENT être dans le chapitre Ruta du Macer
- Crée un pont direct herbal↔pharma pour le fingerprinting

**Risque** : faux positifs des racines courtes (2 chars)
**Temps** : 2h

---

### ATTAQUE 2 — Valider oty=froid sur herbal_b (ROI: ★★★★)
**Potentiel** : Étendre un résultat p=0.023 à p<<<0.001.
**Méthode** : 32 folios herbal_b. Identifier leurs plantes (Sherwood/Scott).
Vérifier si oty en L1-3 corrèle avec froid sur cet ensemble indépendant.

**Ce que ça apporte** :
- Si confirmé : premier mot décodé comme CONCEPT grammatical
  (pas un ingrédient, mais un marqueur de qualité)
- Ouvre la porte à : chckhy/chckh = marqueur HOT ?
- Progrès sur la structure des 3 premières lignes de chaque folio

**Risque** : pas assez de plantes identifiées dans herbal_b
**Temps** : 1h

---

### ATTAQUE 3 — UNE recette lisible (ROI: ★★★★)
**Potentiel** : Première preuve de concept — du latin lisible.
**Méthode** :
1. Prendre les recettes dont on connaît la plante (Attaque 1)
2. Ne garder que les mots à conf ≥ 0.8 (cth, yk, cht, chk)
3. Chercher dans Macer le chapitre correspondant
4. Vérifier si les ingrédients matchent

**Ce que ça apporte** :
- Si réussi : 5+ mots latins dans le bon ordre = preuve de décodage
- Publication possible (même partielle)

**Risque** : les 4 ingrédients fiables sont peut-être trop peu
**Dépend de** : Attaque 1
**Temps** : 2h

---

### ATTAQUE 4 — Prouver ypch=aqua indépendamment (ROI: ★★★)
**Potentiel** : +1 ingrédient universel fiable (aqua = très fréquent).
**Méthode** :
1. Dans les recettes identifiées par plante (Attaque 1), vérifier
   si ypch apparaît quand Macer mentionne aqua
2. Test distributionnel : ypch suit-il des doses ?
3. Cross-folio fingerprint étendu au-delà des 16 ancres

**Ce que ça apporte** :
- Si confirmé : aqua décodé = progression massive (6/16 folios l'ont)
- Contrainte forte pour les recettes pharma

**Risque** : aqua est trop ubiquitaire (même problème que session 14)
**Dépend de** : Attaque 1 (partiellement)
**Temps** : 1.5h

---

### ATTAQUE 5 — Réduire les faux positifs (ROI: ★★★)
**Potentiel** : Passer de 42% apparent à un % réel fiable.
**Méthode** :
1. Exclure les racines ≤3 chars des matchs globaux
2. Ne les accepter que si le contexte confirme (bonne position, bon folio)
3. Recalculer les % de décodage avec seuil strict

**Ce que ça apporte** :
- Chiffres honnêtes pour chaque folio
- Identifier les vrais "meilleurs" folios (pas ceux gonflés)
- Base propre pour Attaque 3

**Risque** : aucun, c'est du nettoyage
**Temps** : 1h

---

### ATTAQUE 6 — Cosmo/Astro labels (ROI: ★★)
**Potentiel** : 372 labels = vocabulaire indépendant.
**Méthode** : Analyser les patterns. Sont-ce des noms de mois,
signes du zodiaque, étoiles ? Comparer avec les labels connus
des diagrammes de calendrier médiévaux.

**Ce que ça apporte** :
- Vocabulaire potentiellement plus facile (labels courts, contexte visuel)
- Mais peu de lien avec le décodage pharma/herbal

**Risque** : vocabulaire complètement séparé
**Temps** : 2h

---

### ATTAQUE 7 — Vinum/succus par exclusion (ROI: ★★)
**Potentiel** : +2 ingrédients universels.
**Méthode** : Si ypch=aqua, chercher les 2 prochains véhicules
parmi les racines NON fonctionnelles, présentes en pharma, rares en herbal.
Profil attendu : suit dose, précède ingrédient.

**Ce que ça apporte** :
- Si réussi : les 3 véhicules = progression significative
- Mais dépend fortement du succès de ypch=aqua

**Dépend de** : Attaque 4
**Temps** : 1.5h

---

## ORDRE RECOMMANDÉ

```
Attaque 5 (nettoyage FP)     ← 1h, base propre
    ↓
Attaque 1 (openers pharma)   ← 2h, DÉCOUVERTE CLEF potentielle
    ↓
Attaque 3 (1 recette)        ← 2h, PREUVE DE CONCEPT
    ↓
Attaque 2 (oty=froid)        ← 1h, confirmation structurelle
    ↓
Attaque 4 (ypch=aqua)        ← 1.5h, si besoin
    ↓
Attaque 7 (vinum/succus)     ← 1.5h, si aqua confirmé
```

## CRITÈRE DE SUCCÈS

- [ ] % de décodage RÉEL calculé (sans faux positifs)
- [ ] 50+ recettes pharma identifiées par plante-cible
- [ ] 1 recette avec 5+ mots latins dans le bon ordre
- [ ] oty=froid confirmé sur herbal_b (p < 0.01)
- [ ] ypch=aqua confirmé ou éliminé
