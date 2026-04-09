"""
PDF LinkedIn, Version française narrative.
"Le Manuscrit de Voynich : Journal d'un Décryptage"
La VRAIE histoire, avec les galères, les doutes, les eurekas.
"""
from reportlab.platypus import Paragraph, Spacer, PageBreak
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

from config import (
    s_title_main, s_title_sub, s_author, s_affil,
    s_h1, s_h2, s_body, s_caption, s_ack, s_decode_line,
    gold_rule, blue_rule, make_table,
    WARM_GRAY, DARK_NAVY, MEDIUM_BLUE, DEEP_BLUE, STATS, SECTIONS
)
from diagrams import (
    DrawingFlowable,
    make_volvelle_diagram, make_pipeline_diagram,
    make_perseus_chart, make_ashmole_comparison, make_cipher_layers
)

S = STATS

s_epigraph = ParagraphStyle('Epigraph', fontSize=10, leading=14,
    textColor=MEDIUM_BLUE, alignment=TA_CENTER, fontName='Helvetica-Oblique',
    leftIndent=20*mm, rightIndent=20*mm, spaceBefore=5*mm, spaceAfter=5*mm)

s_narrative = ParagraphStyle('Narrative', fontSize=10.5, leading=15,
    textColor=DARK_NAVY, alignment=TA_JUSTIFY, fontName='Helvetica',
    spaceAfter=4*mm, firstLineIndent=5*mm)

s_narrative_bold = ParagraphStyle('NarrBold', parent=s_narrative,
    fontName='Helvetica-Bold', firstLineIndent=0)


def build_story_fr():
    story = []

    # ══════════════════════════════════════════
    # COUVERTURE
    # ══════════════════════════════════════════
    story.append(Spacer(1, 30*mm))
    story.append(gold_rule(50, 2))
    story.append(Spacer(1, 8*mm))
    story.append(Paragraph(
        "Le Manuscrit de Voynich<br/>Journal d'une Avancée", s_title_main))
    story.append(Spacer(1, 5*mm))
    story.append(Paragraph(
        "Quand un directeur IA et une intelligence artificielle<br/>"
        "s'attaquent au livre le plus mystérieux du monde", s_title_sub))
    story.append(Spacer(1, 8*mm))
    story.append(gold_rule(50, 2))
    story.append(Spacer(1, 12*mm))
    story.append(Paragraph("Guillaume Clement", s_author))
    story.append(Paragraph("Directeur IA, Flow Line Integration", s_affil))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph("assisté par Claude (Anthropic, Opus 4.6)", ParagraphStyle('collab',
        fontSize=9, leading=12, textColor=WARM_GRAY, alignment=TA_CENTER,
        fontName='Helvetica-Oblique')))
    story.append(Spacer(1, 12*mm))
    story.append(Paragraph("Avril 2026", ParagraphStyle('date',
        fontSize=10, leading=13, textColor=WARM_GRAY, alignment=TA_CENTER,
        fontName='Helvetica')))
    story.append(Paragraph("DOI: 10.5281/zenodo.19477552", ParagraphStyle('doi',
        fontSize=9, leading=12, textColor=WARM_GRAY, alignment=TA_CENTER,
        fontName='Helvetica')))
    story.append(Spacer(1, 15*mm))
    story.append(Paragraph(
        "<i>« Pensez comme Turing, trouvez UNE correspondance irréfutable<br/>"
        "plutôt que d'optimiser des statistiques globales. »</i>", s_epigraph))

    story.append(PageBreak())

    # ══════════════════════════════════════════
    # 1. LE MYSTÈRE
    # ══════════════════════════════════════════
    story.append(Paragraph("1. Le Mystère", s_h1))
    story.append(blue_rule())

    story.append(Paragraph(
        "Il existe, dans les caves climatisées de la Beinecke Rare Book Library "
        "à Yale, un manuscrit que personne ne peut lire. Depuis plus de six cents ans, "
        "le codex catalogué MS 408, plus connu sous le nom de <b>Manuscrit de Voynich</b>, "
        "résiste à toute tentative de déchiffrement.", s_narrative))
    story.append(Paragraph(
        "240 pages de vélin de veau, datées au carbone 14 entre 1404 et 1438. "
        "Des illustrations de plantes qu'aucun botaniste ne reconnaît. Des diagrammes "
        "astronomiques avec des femmes nues dans des bassins. Un système d'écriture "
        "qui ne ressemble à aucun alphabet connu. Et un texte dont les propriétés "
        "statistiques, une entropie anormalement basse de 2,1 bits, ont conduit "
        "certains chercheurs à conclure qu'il ne signifie tout simplement rien.", s_narrative))
    story.append(Paragraph(
        "Les théories ne manquent pas : canular élaboré par un faussaire génial, "
        "langue artificielle oubliée, code militaire d'une puissance disparue, "
        "ou, hypothèse la plus audacieuse, l'oeuvre d'un esprit qui écrivait dans "
        "une langue réelle mais la masquait derrière un chiffre que personne n'avait "
        "encore su reconnaître.", s_narrative))
    story.append(Paragraph(
        "<b>Et si c'était simplement du latin ?</b>", s_narrative_bold))

    story.append(PageBreak())

    # ══════════════════════════════════════════
    # 2. LA RENCONTRE
    # ══════════════════════════════════════════
    story.append(Paragraph("2. La Rencontre", s_h1))
    story.append(blue_rule())

    story.append(Paragraph(
        "Tout commence en mars 2026, par un rendez-vous client. On discute "
        "chiffrement de données, sécurité, cryptographie. En rentrant, l'algorithme "
        "d'Academia.edu me recommande un article de Tim King, Alessandra Andrisani, "
        "Bryce Beasley et Julian Condo. Ils proposent quelque chose de radical : "
        "les glyphes du Voynich seraient une forme modifiée de <b>notes tironiennes</b>, "
        "le système de sténographie inventé par l'affranchi de Cicéron au premier "
        "siècle avant notre ère.", s_narrative))
    story.append(Paragraph(
        "Leur tableau de translitération attribue à chaque caractère une ou plusieurs "
        "valeurs phonétiques latines. C'est une hypothèse, pas une preuve. "
        "Mais elle est testable. Et tester des hypothèses à grande échelle, "
        "c'est exactement ce que je fais dans mon métier.", s_narrative))
    story.append(Paragraph(
        "Ce soir-là, j'ouvre Claude Code et je tape : <i>« Prends le mot EVA 'daiin' "
        "et applique le mapping King-Andrisani. »</i>", s_narrative))
    story.append(Paragraph(
        "La réponse arrive en une seconde : <b>in aquam</b>, « dans l'eau ».", s_narrative_bold))
    story.append(Paragraph(
        "Un mot qui apparaît plus de 2 700 fois dans le manuscrit. Le solvant universel "
        "de toute pharmacopée médiévale. Il est 23h et je sais que "
        "je ne dormirai pas cette nuit.", s_narrative))

    story.append(PageBreak())

    # ══════════════════════════════════════════
    # 3. LE CAUCHEMAR DES PREMIÈRES VERSIONS
    # ══════════════════════════════════════════
    story.append(Paragraph("3. Le Cauchemar des Premières Versions", s_h1))
    story.append(blue_rule())

    story.append(Paragraph(
        "Ce qui suit est un enfer. Pas le genre romantique des films. "
        "Le genre où on code un pipeline à minuit, on le lance sur 226 pages, "
        "et au matin les résultats sont incohérents. Des faux positifs partout. "
        "Des mots latins qui n'existent pas. Des séquences absurdes.", s_narrative))
    story.append(Paragraph(
        "Version 10 : 55% de mots reconnus au dictionnaire. Catastrophique. "
        "On jette tout et on recommence.", s_narrative))
    story.append(Paragraph(
        "Version 11 : on ajoute un module de segmentation par chaînes de Markov. "
        "60%. Mieux, mais le module casse des vrais mots latins en les découpant "
        "n'importe comment. <i>Coquo</i> (je cuis) devient « co + quo », deux "
        "fragments sans sens.", s_narrative))
    story.append(Paragraph(
        "Version 11c : on ajoute une validation contre le dictionnaire Perseus de "
        "l'Université Tufts, 265 419 formes latines attestées. C'est notre garde-fou : "
        "un dictionnaire externe que ni un humain ni une IA ne peut halluciner. "
        "On monte à 70%. Mais un tiers du texte reste du bruit.", s_narrative))
    story.append(Paragraph(
        "À ce stade, la tentation d'abandonner est réelle. Trois versions jetées "
        "à la poubelle. Des nuits blanches pour rien. Sauf que...", s_narrative))
    story.append(Paragraph(
        "Au milieu du bruit, un signal persiste. Des mots médicaux. <i>Aquam</i> (eau), "
        "<i>olei</i> (huile), <i>cura</i> (soin), <i>hiera</i> (remède sacré composé). "
        "Ils reviennent, encore et encore, sur toutes les pages. Trop fréquents pour "
        "être du hasard.", s_narrative_bold))

    story.append(PageBreak())

    # ══════════════════════════════════════════
    # 4. ÉLIMINER L'IMPOSSIBLE
    # ══════════════════════════════════════════
    story.append(Paragraph("4. Éliminer l'Impossible", s_h1))
    story.append(blue_rule())

    story.append(Paragraph(
        "Avec Claude, on élimine les hypothèses une par une. Méthodiquement. "
        "Sans émotion.", s_narrative))
    story.append(Paragraph(
        "Langue inconnue ? On teste la rigidité du mapping : 0,79, au-dessus du seuil. "
        "Éliminée. Canular (hypothèse Rugg) ? La structure grammaticale est trop "
        "cohérente, Amancio et al. l'ont démontré en 2013. Code militaire ? Le vocabulaire "
        "est trop spécialisé dans le domaine médical. On vérifie chaque prédiction : "
        "« f » et « p » décodent tous les deux vers « per », confirmant l'homophonie "
        "du chiffre. « h » est muet, ce qui correspond au latin médiéval tardif. "
        "Les glyphes isolés sur f57v ne décodent vers rien, probablement des chiffres.", s_narrative))
    story.append(Paragraph(
        "Ce qui reste après avoir tout éliminé :", s_narrative))
    story.append(Paragraph(
        "L'hypothèse la plus compatible avec les données : <b>un livre d'apothicaire "
        "ou de médecin</b>, chiffré par un mélange de sténographie romaine (notes "
        "tironiennes), de substitution phonétique homophonique, et d'agglutination des "
        "prépositions. Possiblement pour économiser de l'espace sur un vélin hors de "
        "prix et protéger des formulations propriétaires. Un apothicaire italien, "
        "début du XVe siècle.", s_narrative_bold))
    story.append(Paragraph(
        "On reconstruit tout depuis zéro. Version 12. Sept étapes : tokenisation, "
        "logogrammes, décodage monolithique (essayer le mot entier AVANT de le découper), "
        "segmentation HMM, scoring multicritère à 9 signaux, reranking, validation Perseus.", s_narrative))
    story.append(Paragraph(
        "Premier lancement complet : <b>74%</b>. La piste est bonne. "
        "Mais un quart du texte résiste.", s_narrative))

    story.append(PageBreak())

    # ══════════════════════════════════════════
    # 5. L'EUREKA DE 2H DU MATIN
    # ══════════════════════════════════════════
    story.append(Paragraph("5. L'Eureka de 2h du Matin", s_h1))
    story.append(blue_rule())

    story.append(Paragraph(
        "Un soir, très tard, je fixe la liste des mots qui résistent. "
        "« ykeedy », « qokeey », « daiin ». Ils sont partout. Ils commencent "
        "tous par les mêmes lettres. Et soudain je vois.", s_narrative))
    story.append(Paragraph(
        "Le scribe ne met pas d'espace entre la préposition et le mot qui suit. "
        "Il <b>colle</b> « in » au mot suivant. « ykeedy » n'est pas un mot "
        "inconnu, c'est « <b>in</b> + <b>ciere</b> » (dans + remuer). "
        "« qokeey » est « <b>cum</b> + <b>eo</b> » (avec + cela). "
        "Comme les proclitiques en arabe, <i>bi-</i>, <i>wa-</i>, <i>li-</i>, "
        "écrits collés au mot suivant sans espace.", s_narrative))
    story.append(Paragraph(
        "On code 13 règles de préfixes. y = in, d = in, qo = cum, ol = ex, "
        "r = re, p = per... On relance le pipeline.", s_narrative))
    story.append(Paragraph(
        "Le résultat est immédiat. De 74% à <b>89%</b>. En une nuit.", s_narrative_bold))
    story.append(Paragraph(
        "Les quadrigrammes, ces séquences de quatre mots consécutifs qu'on retrouve "
        "mot pour mot dans des textes pharmaceutiques médiévaux, passent de 1 à <b>19</b>. "
        "Les trigrammes de 84 à 214. Les bigrammes de 793 à 1 069.", s_narrative))
    story.append(Paragraph(
        "Une seule découverte. Quinze points de pourcentage. Toute la structure "
        "du texte qui se révèle d'un coup.", s_narrative))

    story.append(PageBreak())

    # ══════════════════════════════════════════
    # 6. TURING ET L'ANTIDOTARIUM
    # ══════════════════════════════════════════
    story.append(Paragraph("6. Penser Comme Turing", s_h1))
    story.append(blue_rule())

    story.append(Paragraph(
        "Alan Turing n'a pas cassé Enigma par force brute. Il cherchait des "
        "<i>cribs</i>, des fragments de texte clair dont il connaissait le contenu "
        "à l'avance. Les bulletins météo allemands commençaient toujours par "
        "« WETTER ». Cette certitude lui servait de point d'ancrage quand tout "
        "le reste était flou.", s_narrative))
    story.append(Paragraph(
        "Notre crib s'appelle l'<b>Antidotarium Nicolai</b>. Compilé à l'école de "
        "médecine de Salerne au XIIe siècle, c'est le formulaire pharmaceutique que "
        "tout apothicaire du XVe siècle connaissait par coeur. Si notre décodage est "
        "correct, ses ingrédients et ses verbes de préparation doivent apparaître.", s_narrative))
    story.append(Paragraph(
        "On lance les attaques ciblées.", s_narrative))
    story.append(Paragraph(
        "Premier passage, recherche directe : on trouve 4 ingrédients. Décevant. "
        "Le score Aurea Alexandrina, une des recettes les plus célèbres, "
        "est de 4 sur 12. 33%.", s_narrative))
    story.append(Paragraph(
        "Mais en creusant, on comprend pourquoi. Les ingrédients n'utilisent pas "
        "le même chemin de décodage que les mots courants. Le scribe utilise des "
        "valeurs phonétiques <b>minoritaires</b> du mapping pour les noms d'ingrédients. "
        "C'est un niveau supplémentaire d'obscurcissement. Le « livre de codes » "
        "n'est pas caché, c'est l'Antidotarium lui-même : il faut être apothicaire "
        "pour reconnaître les noms.", s_narrative))
    story.append(Paragraph(
        "On code un explorateur qui teste 50 chemins phonétiques par mot. "
        "Deuxième passage : <b>25 ingrédients</b>. "
        "Troisième passage, folio par folio, 226 pages : <b>33</b>.", s_narrative_bold))

    story.append(PageBreak())

    # ══════════════════════════════════════════
    # 7. LES PREUVES
    # ══════════════════════════════════════════
    story.append(Paragraph("7. Les Résultats les plus Significatifs", s_h1))
    story.append(blue_rule())

    story.append(Paragraph("<b>f103r : la page pharmaceutique</b>", s_h2))
    story.append(Paragraph(
        "532 mots. 91% validés au dictionnaire. Le mot « coque » (cuis !) apparaît "
        "<b>17 fois en 5 formes conjuguées différentes</b> : coque, coquas, coquere, "
        "coquendo, coquant. Un paradigme morphologique latin complet. "
        "Statistiquement très difficile à produire par un mapping aléatoire.", s_narrative))

    story.append(make_table(
        ["Latin", "Français", "Occ."],
        [
            ["aloe / aloes", "aloès", "10+"],
            ["ture / turis", "encens", "2"],
            ["sal", "sel", "3"],
            ["olei", "huile", "4"],
            ["aceto", "vinaigre", "2"],
            ["cerae", "cire", "3"],
            ["iecur", "foie", "2"],
            ["hiera", "remède sacré composé", "8"],
            ["mel", "miel", "1"],
        ],
        col_widths=[30*mm, 50*mm, 20*mm]))
    story.append(Paragraph("Ingrédients trouvés sur le seul folio f103r.", s_caption))

    story.append(Paragraph(
        "7 des 12 ingrédients canoniques de l'Aurea Alexandrina semblent "
        "identifiables sur cette seule page.", s_narrative_bold))

    story.append(Paragraph("<b>f33r : la triple convergence</b>", s_h2))
    story.append(Paragraph(
        "Le pipeline décode <b>INELIODE</b>. En latin pharmaceutique médiéval : "
        "<i>Inula helenium</i>, l'aunée officinale. On regarde l'illustration sur "
        "la même page : une plante à grandes feuilles lobées, deux fleurs composées "
        "à disque strié, racines pivotantes. Famille des Astéracées. C'est exactement "
        "l'aunée.", s_narrative))
    story.append(Paragraph(
        "Le texte décodé suggère aunée. L'illustration ressemble à une aunée. La pharmacopée "
        "médiévale utilise l'aunée. <b>Trois indices indépendants pointent "
        "vers la même plante.</b> C'est le type de convergence qu'on ne peut pas "
        "fabriquer par accident.", s_narrative_bold))

    story.append(Paragraph("<b>L'italien caché</b>", s_h2))
    story.append(Paragraph(
        "Parmi les ingrédients, une surprise : <b>pepe</b>. Pas « piper » en latin. "
        "« Pepe » en italien. Et « lilie » au lieu de « lilium ». Le scribe ne maîtrise "
        "pas parfaitement son latin. Il laisse échapper sa langue maternelle. "
        "<b>C'est un Italien.</b> Cohérent avec la datation 1404-1438 et l'hypothèse "
        "d'un scripteur vénitien.", s_narrative))

    story.append(PageBreak())

    # ══════════════════════════════════════════
    # 8. LES ÉTOILES CACHENT DES ÉPICES
    # ══════════════════════════════════════════
    story.append(Paragraph("8. Les Étoiles Cachent des Épices", s_h1))
    story.append(blue_rule())

    story.append(Paragraph(
        "On pensait avoir terminé le gros du travail. Puis l'analyse des 226 pages, "
        "une par une, réserve la surprise la plus incroyable du projet.", s_narrative))
    story.append(Paragraph(
        "Le folio f67r : une magnifique rosette avec un visage solaire au centre, "
        "rayons bleus et rouges alternés. Tout le monde pensait que c'était un "
        "diagramme purement astronomique. Le décodage révèle : <b>aloe</b> (5 fois), "
        "<b>ture</b> (encens), <b>olei</b> (huile), <b>vini</b> (vin), "
        "<b>recipe</b> (prends).", s_narrative))
    story.append(Paragraph(
        "Ce qui ressemble à une recette, cachée dans un diagramme solaire.", s_narrative_bold))
    story.append(Paragraph(
        "Sur le folio adjacent f67r2, la rosette lunaire : <b>nardi</b>, le nard, "
        "une des épices les plus précieuses de l'Antiquité. Sur le verso f67v1 : "
        "<b>cassiae</b>, la cannelle. Puis f85r1, le grand foldout cosmologique : "
        "<b>apii</b> (céleri), <b>asari</b> (asaret), <b>aceti</b> (vinaigre), "
        "et encore <b>nardi</b>.", s_narrative))
    story.append(Paragraph(
        "Ces ingrédients n'étaient pas dans notre liste initiale. Ils étaient cachés "
        "sur des pages que tout le monde considérait comme décoratives depuis 600 ans.", s_narrative))
    story.append(Paragraph(
        "Si cette lecture est correcte, le manuscrit ne dit pas seulement "
        "<i>quoi</i> préparer. Il dit <i>quand</i>. Les diagrammes célestes "
        "semblent encoder des recettes aromatiques liées aux positions stellaires, "
        "ce qui serait compatible avec la tradition de la médecine iatromathématique "
        "médiévale.", s_narrative_bold))

    story.append(PageBreak())

    # ══════════════════════════════════════════
    # 9. LA VOLVELLE
    # ══════════════════════════════════════════
    story.append(Paragraph("9. La Volvelle : pas un Texte, une Machine", s_h1))
    story.append(blue_rule())

    story.append(Paragraph(
        "Le folio f57v est la page la plus célèbre du manuscrit, et la plus "
        "incomprise. Un grand diagramme circulaire avec des anneaux concentriques "
        "de texte, un soleil au centre, quatre figures aux points cardinaux.", s_narrative))

    story.append(DrawingFlowable(make_volvelle_diagram()))
    story.append(Paragraph("Structure de la volvelle f57v.", s_caption))

    story.append(Paragraph(
        "L'anneau L04 contient exactement <b>29 mots</b>. 29 jours. Le mois lunaire "
        "synodique. L'anneau L03 présente un motif 4x17 avec des variations "
        "systématiques qui confirment l'homophonie f/p du chiffre. L'anneau L05 "
        "couvre 75% du cercle, un cadran de 18 heures avec un trou de 90 degrés "
        "pour les heures de nuit.", s_narrative))
    story.append(Paragraph(
        "La structure est un isomorphisme quasi parfait avec le manuscrit "
        "<b>Ashmole 370</b> (Bibliothèque Bodléienne, Oxford, ~1424), le "
        "<i>Kalendarium</i> de Nicholas de Lynn, un instrument de calcul "
        "astronomique conçu pour les médecins.", s_narrative))

    story.append(DrawingFlowable(make_ashmole_comparison()))
    story.append(Paragraph("Correspondance structurelle Ashmole 370 / f57v.", s_caption))

    story.append(Paragraph(
        "Ce n'est probablement pas un horoscope. Les indices suggèrent un "
        "<b>calculateur de timing thérapeutique</b>, un instrument qui indiquerait "
        "quand saigner, quand purger, quand administrer tel remède en fonction "
        "des cycles célestes.", s_narrative_bold))
    story.append(Paragraph(
        "Mais soyons honnêtes : le centre de la volvelle reste obscur. Les 8 mots "
        "du pivot central sont tous classés LOW ou OPAQUE. On a trouvé la machine "
        "mais pas son mode d'emploi.", s_narrative))

    story.append(PageBreak())

    # ══════════════════════════════════════════
    # 10. CE QUI RÉSISTE
    # ══════════════════════════════════════════
    story.append(Paragraph("10. Ce qui Résiste Encore", s_h1))
    story.append(blue_rule())

    story.append(Paragraph(
        "L'honnêteté intellectuelle exige de raconter ce qui ne marche pas.", s_narrative))
    story.append(Paragraph(
        "3 421 mots résistent au décodage. Plus le mot est long, plus il résiste : "
        "29% d'échec au-delà de 8 caractères, 44% au-delà de 10. Ce sont probablement "
        "des composés que le pipeline ne sait pas décomposer, ou des entrées de "
        "nomenclateur, un livre de codes séparé pour les noms propres.", s_narrative))
    story.append(Paragraph(
        "Sur les folios zodiacaux (f70v à f73v), les noms des signes ne sont jamais "
        "produits par le décodage phonétique. Le scribe utilisait deux systèmes : "
        "un chiffre phonétique pour le texte courant, et un nomenclateur pour les "
        "noms propres et les entités astronomiques. Le nomenclateur, on ne l'a pas "
        "craqué.", s_narrative))
    story.append(Paragraph(
        "4 ingrédients de l'Aurea Alexandrina manquent : cinnamomum, masticis, "
        "myrrha, galangal. Leurs patterns consonantiques sont incompatibles "
        "avec les mappings connus. Il existe peut-être une troisième méthode "
        "d'encodage qu'on n'a pas trouvée.", s_narrative))
    story.append(Paragraph(
        "Et le test ultime : on n'a jamais trouvé une séquence de 5 mots "
        "consécutifs spécifiques dans un texte médiéval connu. 4 mots oui, "
        "19 fois. 5, jamais.", s_narrative))
    story.append(Paragraph(
        "89% de 38 442 mots validés contre un dictionnaire externe, c'est "
        "statistiquement très difficile à attribuer au hasard. Mais ce n'est pas "
        "100%. Et on ne sait pas si les 11% restants sont du bruit, un artefact "
        "du mapping, ou un deuxième chiffre qu'on n'a pas percé.", s_narrative))

    story.append(PageBreak())

    # ══════════════════════════════════════════
    # 11. CE QUE CONTIENT LE LIVRE
    # ══════════════════════════════════════════
    story.append(Paragraph("11. Ce que Contient le Livre", s_h1))
    story.append(blue_rule())

    story.append(Paragraph(
        "Au terme de cette aventure, voici ce que les résultats suggèrent : "
        "le manuscrit pourrait être le <b>vade-mecum</b> d'un apothicaire itinérant "
        "du nord de l'Italie, début du XVe siècle.", s_narrative))

    story.append(make_table(
        ["Section", "Folios", "Contenu", "Tradition"],
        [
            ["Herbes (H)", "129", "Monographies de plantes", "Circa Instans"],
            ["Pharmaceutique (S+P)", "41", "Recettes composées", "Antidotarium Nicolai"],
            ["Balnéologique (B)", "19", "Protocoles d'hydrothérapie", "De Balneis"],
            ["Zodiacale (Z)", "12", "Calendrier des purges", "Astrologie médicale"],
            ["Cosmologique (C)", "10", "Cadre théorique, volvelle f57v", "Médecine galénique"],
            ["Astronomique (A)", "8", "Recettes liées aux étoiles", "Iatromathématique"],
        ],
        col_widths=[32*mm, 14*mm, 46*mm, 40*mm]))
    story.append(Paragraph(f"{S['total_folios']} faces de folios, "
        f"{S['total_words']:,} mots décodés.", s_caption))

    story.append(Paragraph(
        "Ce qui frappe, c'est la cohérence. Si notre lecture est correcte, "
        "les sections forment un <b>système thérapeutique unifié</b> : les herbes "
        "fournissent la matière première, les recettes composent les remèdes, "
        "les bains traitent le corps, le zodiaque dicte le calendrier, la volvelle "
        "calcule le timing optimal. Tout semble lié.", s_narrative_bold))
    story.append(Paragraph(
        "Le chiffrement n'était pas destiné à cacher un secret d'État. "
        "Il servait trois fonctions pratiques : <b>compression</b> (économiser de la "
        "place par agglutination et abréviations), <b>efficacité</b> (notation rapide "
        "par sténographie), et <b>secret professionnel</b> (protéger des formulations "
        "contre les concurrents), une pratique documentée dans les guildes médiévales.", s_narrative))

    story.append(PageBreak())

    # ══════════════════════════════════════════
    # 12. L'AVENTURE HUMAIN-IA
    # ══════════════════════════════════════════
    story.append(Paragraph("12. Ce que j'ai Appris", s_h1))
    story.append(blue_rule())

    story.append(Paragraph(
        "Je ne suis pas chercheur, pas historien, pas cryptographe. Je suis un "
        "directeur IA qui a appliqué sa méthode métier, tester des hypothèses "
        "à grande échelle avec des données structurées, à un problème de "
        "cryptographie historique. Ce projet raconte quelque chose sur cette "
        "façon de travailler.", s_narrative))
    story.append(Paragraph(
        "L'intuition a toujours été humaine. C'est un humain qui a vu le pattern "
        "d'agglutination à 2h du matin. C'est un humain qui a décidé d'utiliser "
        "l'Antidotarium comme crib. C'est un humain qui a regardé l'illustration "
        "de f33r et s'est dit : « Cette plante ressemble à de l'aunée. »", s_narrative))
    story.append(Paragraph(
        "La puissance de calcul était machine. 265 419 entrées de dictionnaire à "
        "vérifier pour chaque mot. 226 folios à analyser. 13 règles de préfixe à "
        "tester en combinatoire sur 38 442 mots. 800 000 mots de corpus à croiser. "
        "Aucun humain ne fait cela seul.", s_narrative))
    story.append(Paragraph(
        "Le garde-fou : le <b>dictionnaire Perseus</b>. Externe, objectif, vérifiable "
        "par quiconque. Une IA peut halluciner une traduction. Elle ne peut pas "
        "halluciner une entrée dans un dictionnaire de 265 419 formes attestées.", s_narrative))
    story.append(Paragraph(
        "Et quand on doute de tout, à 3h du matin, quand les résultats ne bougent "
        "plus et qu'on se demande si on ne fait pas du <i>pattern matching</i> sur "
        "du bruit, se rappeler la méthode de <b>Turing</b> remet les idées en "
        "place. Pas la force brute. Un crib. Une seule certitude bien choisie "
        "suffit à faire basculer un chiffre entier.", s_narrative))
    story.append(Paragraph(
        "Ce projet est dédié à sa mémoire.", s_narrative))
    story.append(Paragraph(
        "Nous n'avons pas décrypté le Manuscrit de Voynich. Nous avons, peut-être, "
        "fait avancer significativement sa compréhension. La nuance est importante. "
        "J'ai tout publié en open source : le code, les 226 pages décodées, "
        "le pipeline complet. Pour que des médiévistes, des pharmacologues, des "
        "passionnés reprennent ce travail et aillent plus loin.", s_narrative))

    story.append(PageBreak())

    # ══════════════════════════════════════════
    # REMERCIEMENTS + LIENS
    # ══════════════════════════════════════════
    story.append(Paragraph("Remerciements", s_h1))
    story.append(blue_rule())

    story.append(Paragraph(
        "À <b>Hélène</b>, ma femme, et à <b>Mathis</b> et <b>Margaux</b>, mes "
        "enfants, pour leur patience devant les innombrables soirées et week-ends "
        "passés à déchiffrer du latin médiéval.", s_ack))
    story.append(Paragraph(
        "À <b>Flow Line Integration</b> pour les ressources de calcul et "
        "l'infrastructure IA.", s_ack))
    story.append(Paragraph(
        "À <b>Tim King</b> et <b>Alessandra Andrisani</b>, Bryce Beasley et "
        "Julian Condo pour le tableau de translitération sans lequel rien de "
        "tout ceci n'existerait.", s_ack))
    story.append(Paragraph(
        "À <b>Nick Pelling</b> pour f57v, à <b>René Zandbergen</b> et "
        "Gabriel Landini pour la transcription EVA, et à la communauté du "
        "forum Voynich Ninja.", s_ack))

    story.append(Spacer(1, 8*mm))
    story.append(gold_rule(60, 2))
    story.append(Spacer(1, 5*mm))

    s_link = ParagraphStyle('Link', fontSize=9, leading=13, textColor=WARM_GRAY,
        alignment=TA_CENTER, fontName='Helvetica')
    s_link_bold = ParagraphStyle('LinkBold', fontSize=9, leading=13, textColor=DARK_NAVY,
        alignment=TA_CENTER, fontName='Helvetica-Bold')

    story.append(Paragraph("<b>DOI: 10.5281/zenodo.19477552</b>", s_link_bold))
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph("Code source et texte décodé : <b>github.com/CorwinFr/Voynich</b>", s_link))
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph(
        "Article académique (en anglais, 52 pages) :", s_link))
    story.append(Paragraph(
        "<b>academia.edu/165576792</b>", s_link_bold))
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph(
        "Les travaux de recherche, les algorithmes de décryptage (pipeline K&amp;A v12) "
        "ainsi que les données présentées dans ce document ont fait l'objet d'un dépôt "
        "d'horodatage officiel (Enveloppe Soleau) auprès de l'INPI (France) en avril 2026.",
        ParagraphStyle('Legal', fontSize=7.5, leading=10, textColor=WARM_GRAY,
            alignment=TA_CENTER, fontName='Helvetica-Oblique')))

    return story
