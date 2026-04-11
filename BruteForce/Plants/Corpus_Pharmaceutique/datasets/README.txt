Tout est regroupe dans Voynich FINAL/Corpus_Pharmaceutique/. Voici la structure et les liens :

datasets/ - Les 4 corpus structures, prets a l'emploi :

matrice_croisee_4_corpora.xlsx - La matrice de concordance : 205 ingredients x 4 corpora, 4 onglets (matrice complete, top 50 AN, substances V39, statistiques)
antidotarium_nicolai_ingredients.csv - 114 ingredients, 137 recettes, frequences + degres galeniques CI
circa_instans_galenic_degrees.csv - 207 entrees avec degres galeniques complets
lylye_medicynes_ingredients.csv - 715 ingredients, 421 recettes (Ancientbiotics mBio 2020)

rapports/ - Toute l'analyse de recherche :

response_09 - Synthese croisement multi-corpus - Le rapport principal avec les 12 ingredients pan-corpus et les prochaines etapes
response_06 - Identification des plantes - Croisement CI / folios herbal VMS
response_05 - Codes d'ingredients - Systeme de notation pharmaceutique
response_01 a 04 - Antidotarium, zodiaque galenique, calendriers lunaires, notation
EXPERT_VALIDATION - Validation ligne par ligne du decodage

sources_brutes/ - Les textes extraits des XML/PDF originaux :

van_den_berg_full_text.txt - Antidotarium Nicolai latin (575K car., van den Berg 1917)
dorveaux_antidotaire_full_text.txt - Traductions francaises AN (273K car., Dorveaux 1896)
circa_instans_full_text.txt - Circa Instans complet (526K car., Dorveaux 1913)
mBio.03136-19-sd001.pdf - Dataset Ancientbiotics original (116 pages)

scripts/ - Les scripts Python de traitement :

build_cross_reference.py - Generation de la matrice croisee Excel
corpus_builder.py + rebuild_corpora.py - Extraction et lemmatisation des corpus

matrice_croisee_4_corpora.xlsx
Guillaume, les chiffres sont tres parlants :
459 items extraits de l'inventaire Mathieu Roux (Marseille, 1488), repartis en :

205 simples (matieres premieres)
50 eaux distillees
42 electuaires/opiats
29 poudres composees
27 sirops
21 confits, 21 huiles, 14 pilules, 13 pierres, 11 onguents, 11 troches, 4 emplatres

168 ingredients latins standardises identifies, et surtout : 34 des 40 top ingredients de l'Antidotarium Nicolai sont presents dans cette boutique marseillaise de 1488. Myrrha, Cinnamomum, Aloe, Anisum, Zingiber, Foeniculum, Rosa, Cardamomum, Caryophyllus, Olibanum, Piper, Galanga, Camphora, Rhabarbarum, Gentiana, Aristolochia, Mandragora, Hyoscyamus - tout y est.
C'est une confirmation massive que l'Antidotarium Nicolai n'est pas un texte theorique mais correspond exactement a ce qu'on trouvait dans une vraie boutique d'apothicaire provencal, a l'epoque du VMS.
Voir le CSV
Si tu arrives a extraire les 3 autres inventaires avec le meme script console (de Greoux serait le prochain avec ses 400+ items), je les parse immediatement et on aura un 5e corpus