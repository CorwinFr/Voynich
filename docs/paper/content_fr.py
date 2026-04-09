"""
PDF LinkedIn  - Version française narrative.
"Le Manuscrit de Voynich : Journal d'un Décryptage"
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

# Styles spécifiques au récit
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
        "Le Manuscrit de Voynich<br/>Journal d'un Décryptage", s_title_main))
    story.append(Spacer(1, 5*mm))
    story.append(Paragraph(
        "Comment un ingénieur IA et une intelligence artificielle<br/>"
        "ont lu le livre le plus mystérieux du monde", s_title_sub))
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
        "<i>« Pensez comme Turing  - trouvez UNE correspondance irréfutable<br/>"
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
        "le codex catalogué MS 408  - plus connu sous le nom de <b>Manuscrit de Voynich</b>  - "
        "résiste à toute tentative de déchiffrement.", s_narrative))
    story.append(Paragraph(
        "240 pages de vélin de veau, datées au carbone 14 entre 1404 et 1438. "
        "Des illustrations de plantes qu'aucun botaniste ne reconnaît. Des diagrammes "
        "astronomiques avec des femmes nues dans des bassins. Un système d'écriture "
        "qui ne ressemble à aucun alphabet connu. Et un texte dont les propriétés "
        "statistiques  - une entropie anormalement basse de 2,1 bits  - ont conduit "
        "certains chercheurs à conclure qu'il ne signifie tout simplement rien.", s_narrative))
    story.append(Paragraph(
        "Les théories ne manquent pas : canular élaboré par un faussaire génial, "
        "langue artificielle oubliée, code militaire d'une puissance disparue, "
        "ou  - hypothèse la plus audacieuse  - l'œuvre d'un esprit qui écrivait dans "
        "une langue réelle, mais la masquait derrière un chiffre que personne n'avait "
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
        "Tout commence en mars 2026, par un article que l'algorithme de recommandation "
        "d'Academia.edu glisse dans mon flux. Tim King, Alessandra Andrisani, Bryce Beasley "
        "et Julian Condo y proposent quelque chose de radical : les glyphes du Voynich "
        "seraient une forme modifiée de <b>notes tironiennes</b>  - le système de sténographie "
        "inventé par l'affranchi de Cicéron au premier siècle avant notre ère, et encore "
        "largement utilisé au Moyen Âge.", s_narrative))
    story.append(Paragraph(
        "Leur tableau de translitération attribue à chaque caractère EVA (le système de "
        "transcription standard du Voynich) une ou plusieurs valeurs phonétiques latines. "
        "C'est une hypothèse  - pas une preuve. Mais elle est testable.", s_narrative))
    story.append(Paragraph(
        "Ce soir-là, j'ouvre Claude Code et je tape : <i>« Prends le mot EVA 'daiin' "
        "et applique le mapping King-Andrisani. »</i>", s_narrative))
    story.append(Paragraph(
        "La réponse arrive en une seconde : <b>in aquam</b>  - « dans l'eau ».", s_narrative_bold))
    story.append(Paragraph(
        "Un mot qui apparaît plus de 2 700 fois dans le manuscrit. Le solvant universel "
        "de toute pharmacopée médiévale. Mon cœur s'accélère. Il est 23h et je sais que "
        "je ne dormirai pas cette nuit.", s_narrative))

    story.append(PageBreak())

    # ══════════════════════════════════════════
    # 3. LA MÉTHODE TURING
    # ══════════════════════════════════════════
    story.append(Paragraph("3. La Méthode Turing", s_h1))
    story.append(blue_rule())

    story.append(Paragraph(
        "Alan Turing n'a pas cassé Enigma par force brute. Il a cherché des <i>cribs</i>  - "
        "des fragments de texte clair dont il connaissait le contenu à l'avance. Les bulletins "
        "météo allemands commençaient toujours par « WETTER » ; les rapports du matin contenaient "
        "systématiquement « KEINE BESONDEREN VORKOMMNISSE » (rien à signaler). Ces certitudes "
        "lui donnaient un point d'ancrage pour remonter jusqu'à la clé.", s_narrative))
    story.append(Paragraph(
        "Notre crib à nous s'appelle l'<b>Antidotarium Nicolai</b>. Compilé à l'école de "
        "médecine de Salerne au XIIe siècle, c'est LE formulaire pharmaceutique standard de "
        "l'Europe médiévale  - entre 115 et 175 recettes de médicaments composés que TOUT "
        "apothicaire du XVe siècle devait connaître par cœur.", s_narrative))
    story.append(Paragraph(
        "Le raisonnement est simple : si le Voynich est un livre de recettes pharmaceutiques, "
        "alors on doit y trouver les mots que tout apothicaire utilise quotidiennement :", s_narrative))
    story.append(Paragraph(
        "<b>recipe</b> (prends), <b>coque</b> (cuis), <b>misce</b> (mélange), "
        "<b>tere</b> (broie), <b>cola</b> (filtre), <b>aquam</b> (eau), "
        "<b>oleo</b> (huile), <b>equaliter</b> (à parts égales)...", s_narrative_bold))
    story.append(Paragraph(
        "Nous les trouvons. Tous. Partout dans le manuscrit. Et pas distribués au hasard  - "
        "concentrés exactement là où les illustrations montrent des plantes, des jarres, "
        "des bassins de préparation.", s_narrative))

    story.append(PageBreak())

    # ══════════════════════════════════════════
    # 4. LE MUR DE L'AGGLUTINATION
    # ══════════════════════════════════════════
    story.append(Paragraph("4. Le Mur de l'Agglutination", s_h1))
    story.append(blue_rule())

    story.append(Paragraph(
        "Nous construisons un pipeline  - le K&A v12. Sept étapes automatisées : "
        "tokenisation, résolution des logogrammes, décodage monolithique, segmentation "
        "par HMM Viterbi, scoring multicritère, reranking, validation Perseus. "
        "Nous le lançons sur les 226 faces de folios.", s_narrative))
    story.append(Paragraph(
        "Résultat : <b>74% de mots reconnus</b> au dictionnaire latin Perseus "
        "(265 419 entrées). Encourageant  - mais insuffisant. Un quart du texte reste "
        "opaque. Des mots impossibles comme « ykeedy », « qokeey », « daiin » résistent "
        "à toute décomposition.", s_narrative))
    story.append(Paragraph(
        "C'est le moment où on a failli abandonner.", s_narrative))
    story.append(Paragraph(
        "Puis, un soir à 2h du matin, en fixant la liste des mots qui commencent par « y »  - "
        "et ils sont légion  - l'eureka arrive. Le scribe ne met pas d'espace entre la préposition "
        "et le mot qui suit. Il <b>colle</b> « in » au mot suivant. « ykeedy » n'est pas un mot "
        "inconnu  - c'est « <b>in</b> + <b>ciere</b> » (dans + remuer). « qokeey » est "
        "« <b>cum</b> + <b>eo</b> » (avec + lui). Comme les proclitiques arabes  - <i>bi-</i>, "
        "<i>wa-</i>, <i>li-</i>  - écrits sans espace devant le mot.", s_narrative))
    story.append(Paragraph(
        "Nous identifions <b>13 préfixes agglutinés</b>. Le pipeline passe de "
        "74% à <b>89,3%</b> en une nuit. Ce qui semblait du charabia devient du latin "
        "pharmaceutique lisible.", s_narrative_bold))

    story.append(PageBreak())

    # ══════════════════════════════════════════
    # 5. INELIODE
    # ══════════════════════════════════════════
    story.append(Paragraph("5. INELIODE  - La Preuve Botanique", s_h1))
    story.append(blue_rule())

    story.append(Paragraph(
        "Le folio f33r porte une grande illustration de plante : larges feuilles lobées vert foncé, "
        "deux fleurs composées à disque strié vert et blanc sur de longs pédoncules, racines "
        "pivotantes brun-orangé. Au-dessus, huit lignes de texte.", s_narrative))
    story.append(Paragraph(
        "Le pipeline décode le mot principal : <b>INELIODE</b>.", s_narrative_bold))
    story.append(Paragraph(
        "En latin pharmaceutique médiéval, c'est <b>Inula helenium</b>  - l'aunée officinale. "
        "Une plante de la famille des Astéracées, utilisée depuis l'Antiquité contre les "
        "affections respiratoires et digestives. Décrite dans le <i>Circa Instans</i> de "
        "Salerne, dans les recettes de Dioscoride, dans l'Antidotarium Nicolai.", s_narrative))
    story.append(Paragraph(
        "Triple convergence :", s_narrative))
    story.append(Paragraph(
        "1. Le texte décodé dit « aunée »<br/>"
        "2. L'illustration montre une Astéracée à grosses fleurs composées<br/>"
        "3. La tradition médicale médiévale confirme l'usage pharmaceutique", s_narrative))
    story.append(Paragraph(
        "Trois preuves indépendantes qui convergent sur la même plante. "
        "C'est le moment où l'hypothèse devient difficile à rejeter.", s_narrative_bold))

    story.append(PageBreak())

    # ══════════════════════════════════════════
    # 6. LA VOLVELLE
    # ══════════════════════════════════════════
    story.append(Paragraph("6. La Volvelle  - L'Instrument de l'Apothicaire", s_h1))
    story.append(blue_rule())

    story.append(Paragraph(
        "Le folio f57v est la page la plus célèbre du manuscrit  - et la plus "
        "incomprise. Un grand diagramme circulaire avec des anneaux concentriques "
        "de texte, un soleil au centre, quatre figures aux points cardinaux.", s_narrative))
    story.append(Paragraph(
        "Ce n'est pas un texte. C'est une <b>machine</b>.", s_narrative_bold))

    story.append(DrawingFlowable(make_volvelle_diagram()))
    story.append(Paragraph("Structure de la volvelle f57v  - reconstruction schématique.", s_caption))

    story.append(Paragraph(
        "L'anneau L04 contient exactement <b>29 mots</b>  - le mois lunaire synodique "
        "(29,5 jours). L'anneau L03 présente un motif 4×17 avec des variations systématiques "
        "aux positions 2 et 8 qui confirment l'homophonie f/p du chiffre. L'anneau L05 couvre "
        "75% du cercle  - un cadran de 18 heures avec un trou de 90° pour les heures de nuit.", s_narrative))
    story.append(Paragraph(
        "La structure est un isomorphisme quasi parfait avec le manuscrit <b>Ashmole 370</b> "
        "(Bibliothèque Bodléienne, Oxford, ~1424)  - le <i>Kalendarium</i> de Nicholas de Lynn, "
        "un instrument de calcul astronomique conçu pour les médecins.", s_narrative))

    story.append(DrawingFlowable(make_ashmole_comparison()))
    story.append(Paragraph("Correspondance structurelle entre l'Ashmole 370 et le folio f57v.", s_caption))

    story.append(Paragraph(
        "Ce n'est pas un horoscope. C'est un <b>calculateur de timing thérapeutique</b>  - "
        "un instrument qui indique à l'apothicaire quand saigner, quand purger, quand "
        "administrer tel ou tel remède en fonction de la position du soleil et de la phase "
        "de la lune, conformément à la médecine galénique.", s_narrative_bold))

    story.append(PageBreak())

    # ══════════════════════════════════════════
    # 7. f103r  - LA CONFIRMATION
    # ══════════════════════════════════════════
    story.append(Paragraph("7. f103r  - Le Folio qui a Tout Confirmé", s_h1))
    story.append(blue_rule())

    story.append(Paragraph(
        "Le folio 103r est une page de texte dense  - 54 lignes, pas d'illustration, "
        "juste du Voynichois serré avec de petites étoiles rouges en marge pour marquer "
        "les paragraphes. <b>532 mots, 91% validés au dictionnaire Perseus.</b>", s_narrative))
    story.append(Paragraph(
        "Le mot <b>coque</b> (cuis !) apparaît <b>17 fois</b> sur cette seule page. "
        "Pas la même forme  - coque, coquas, coquere, coquendo, coquant, coquentis  - "
        "une conjugaison latine complète. Impossible à produire par hasard.", s_narrative))
    story.append(Paragraph(
        "La liste d'ingrédients se lit comme une entrée de l'Antidotarium :", s_narrative))

    story.append(make_table(
        ["Latin", "Français", "Occurrences sur f103r"],
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
        col_widths=[30*mm, 40*mm, 40*mm]))
    story.append(Paragraph("Ingrédients identifiés sur le folio f103r.", s_caption))

    story.append(Paragraph(
        "Sur les 12 ingrédients canoniques de l'<b>Aurea Alexandrina</b>  - une des recettes "
        "les plus célèbres de l'Antidotarium  - nous en retrouvons <b>7</b> sur cette seule "
        "page. Les 4 manquants (cinnamomum, masticis, myrrha, galangal) ont des patterns "
        "consonantiques incompatibles avec le mapping K&A connu.", s_narrative))
    story.append(Paragraph(
        "Ce n'est plus une hypothèse. <b>C'est une recette que je peux lire.</b>", s_narrative_bold))

    story.append(PageBreak())

    # ══════════════════════════════════════════
    # 8. LES PAGES ASTRONOMIQUES
    # ══════════════════════════════════════════
    story.append(Paragraph("8. Les Pages Astronomiques  - La Surprise", s_h1))
    story.append(blue_rule())

    story.append(Paragraph(
        "On pensait avoir terminé le gros du travail quand l'analyse folio par folio "
        "des 226 pages a réservé une surprise majeure.", s_narrative))
    story.append(Paragraph(
        "Le folio f67r  - une magnifique rosette avec un visage solaire au centre, "
        "rayons bleus et rouges alternés  - semblait purement astronomique. Le décodage "
        "révèle : <b>aloe</b> (5 fois), <b>ture</b> (encens), <b>olei</b> (huile), "
        "<b>vini</b> (vin), <b>recipe</b> (prends). C'est une recette.", s_narrative))
    story.append(Paragraph(
        "Sur le folio adjacent f67r2 (la rosette lunaire, côté droit) apparaît "
        "<b>nardi</b>  - le nard, une des épices les plus précieuses de la pharmacopée "
        "antique. Sur le verso f67v1 : <b>cassiae</b>  - la cannelle.", s_narrative))
    story.append(Paragraph(
        "Ces ingrédients n'étaient pas dans notre liste initiale de 25 termes. "
        "Ils étaient cachés sur des pages que tout le monde considérait comme de "
        "simples diagrammes astronomiques.", s_narrative))
    story.append(Paragraph(
        "La conclusion s'impose : les diagrammes célestes ne sont pas décoratifs. "
        "Ils encodent des <b>recettes aromatiques liées aux positions stellaires</b>. "
        "Le manuscrit est un système unifié  - il dit non seulement <i>quoi</i> préparer, "
        "mais aussi <i>quand</i>.", s_narrative_bold))

    story.append(PageBreak())

    # ══════════════════════════════════════════
    # 9. LES DOUTES
    # ══════════════════════════════════════════
    story.append(Paragraph("9. Les Doutes  - Ce qui Reste", s_h1))
    story.append(blue_rule())

    story.append(Paragraph(
        "L'honnêteté intellectuelle exige de dire ce qui ne marche pas encore.", s_narrative))
    story.append(Paragraph(
        "<b>9% du texte reste opaque</b>  - des mots longs et composés que le pipeline ne "
        "sait pas décomposer, et des entrées de nomenclateur (noms propres, noms de plantes, "
        "entités astronomiques) qui utilisent un système de chiffrement différent du texte "
        "courant. Sur les folios zodiacaux (f70v-f73v), les noms des signes ne sont jamais "
        "produits par le décodage phonétique  - ils relèvent d'un livre de codes séparé.", s_narrative))
    story.append(Paragraph(
        "<b>4 ingrédients</b> de l'Aurea Alexandrina restent introuvables : cinnamomum "
        "(cannelle de Ceylan), masticis (mastic), myrrha (myrrhe), galangal. Leurs patterns "
        "consonantiques sont incompatibles avec les mappings K&A connus  - il existe peut-être "
        "une troisième méthode d'encodage, ou des équivalents en italien vernaculaire que "
        "nous n'avons pas encore identifiés.", s_narrative))
    story.append(Paragraph(
        "Le chiffre homophonique crée des <b>collisions</b> : les glyphes EVA 'f' et 'p' "
        "décodent tous deux vers « per », ce qui signifie que des mots EVA différents peuvent "
        "produire le même résultat latin. Une pénalité de collision (-8000 dans le scorer) "
        "atténue ce problème, mais ne l'élimine pas.", s_narrative))
    story.append(Paragraph(
        "Nous ne prétendons pas avoir résolu le Manuscrit de Voynich. Nous prétendons "
        "avoir lu  - pour la première fois  - <b>90,6%</b> de son texte en latin plausible, "
        "validé contre un dictionnaire externe que ni un humain ni une IA ne peut "
        "« halluciner ».", s_narrative_bold))

    story.append(PageBreak())

    # ══════════════════════════════════════════
    # 10. CE QUE CONTIENT LE LIVRE
    # ══════════════════════════════════════════
    story.append(Paragraph("10. Ce que Contient le Livre", s_h1))
    story.append(blue_rule())

    story.append(Paragraph(
        "Au terme de cette analyse, voici ce que nous pensons être le contenu du manuscrit "
        " - le <b>vade-mecum</b> d'un apothicaire itinérant du nord de l'Italie, "
        "début du XVe siècle :", s_narrative))

    story.append(make_table(
        ["Section", "Folios", "Contenu", "Tradition médicale"],
        [
            ["Herbes (H)", "129", "Monographies de plantes avec préparations", "Circa Instans"],
            ["Pharmaceutique (S+P)", "41", "Recettes composées, ingrédients multiples", "Antidotarium Nicolai"],
            ["Balnéologique (B)", "19", "Protocoles d'hydrothérapie", "De Balneis Puteolanis"],
            ["Zodiacale (Z)", "12", "Calendrier des purges et saignées", "Astrologie médicale"],
            ["Cosmologique (C)", "10", "Cadre théorique, volvelle f57v", "Théorie humorale galénique"],
            ["Astronomique (A)", "8", "Recettes liées aux positions stellaires", "Iatromathématique"],
            ["Transitoire (T)", "7", "Pages titre et frontières", " -"],
        ],
        col_widths=[30*mm, 14*mm, 55*mm, 40*mm]))
    story.append(Paragraph(f"Structure du manuscrit  - {S['total_folios']} faces de folios, "
        f"{S['total_words']:,} mots décodés.", s_caption))

    story.append(Paragraph(
        "Ce n'est pas une collection disparate de sections sans rapport. "
        "C'est un <b>système thérapeutique unifié</b> : les herbes fournissent "
        "la matière première, les recettes composent les remèdes, les bains "
        "traitent le corps, le zodiaque dicte le calendrier, et la volvelle "
        "calcule le timing optimal. Tout est lié.", s_narrative_bold))

    story.append(Paragraph(
        "Le chiffrement n'était pas destiné à cacher un secret d'État. Il servait "
        "trois fonctions pratiques : <b>compression</b> (gagner de la place sur un vélin "
        "coûteux par agglutination et abréviations), <b>efficacité</b> (notation rapide "
        "par sténographie), et <b>secret professionnel</b> (protéger des formulations "
        "propriétaires contre les concurrents)  - une pratique bien documentée dans la "
        "culture des guildes médiévales.", s_narrative))

    story.append(PageBreak())

    # ══════════════════════════════════════════
    # 11. L'AVENTURE HUMAIN-IA
    # ══════════════════════════════════════════
    story.append(Paragraph("11. L'Aventure Humain-IA", s_h1))
    story.append(blue_rule())

    story.append(Paragraph(
        "Ce projet raconte aussi quelque chose sur la façon dont on peut travailler "
        "avec l'intelligence artificielle.", s_narrative))
    story.append(Paragraph(
        "L'intuition a toujours été humaine. C'est un humain qui a reconnu le pattern "
        "d'agglutination à 2h du matin. C'est un humain qui a décidé d'utiliser "
        "l'Antidotarium Nicolai comme crib. C'est un humain qui a regardé l'illustration "
        "du folio f33r et s'est dit : « Cette plante ressemble à de l'aunée. »", s_narrative))
    story.append(Paragraph(
        "La puissance de calcul était machine. 265 419 entrées de dictionnaire à vérifier "
        "pour chaque mot décodé. 226 folios à analyser systématiquement. 13 règles de "
        "préfixe à tester en combinatoire sur 38 442 mots. Des modèles de langue sur "
        "800 000 mots de corpus pharmaceutique à interroger. Aucun humain ne peut faire "
        "cela seul en un temps raisonnable.", s_narrative))
    story.append(Paragraph(
        "Le garde-fou critique : le <b>dictionnaire Perseus</b>. Il est externe, objectif, "
        "vérifiable par quiconque. Une IA peut « halluciner » une traduction. Elle ne peut "
        "pas halluciner une entrée dans un dictionnaire de 265 419 formes attestées. "
        "Chaque mot que nous prétendons avoir décodé est vérifié contre cette référence. "
        "89,3% passent le test.", s_narrative))
    story.append(Paragraph(
        "Alan Turing rêvait que les machines nous aident un jour à voir ce que "
        "nous ne voyons pas seuls. Ce projet est, modestement, une réalisation "
        "de ce rêve.", s_narrative_bold))

    story.append(PageBreak())

    # ══════════════════════════════════════════
    # 12. REMERCIEMENTS + LIENS
    # ══════════════════════════════════════════
    story.append(Paragraph("12. Remerciements", s_h1))
    story.append(blue_rule())

    story.append(Paragraph(
        "À <b>Hélène</b>, ma femme, et à <b>Mathis</b> et <b>Margaux</b>, mes enfants  - "
        "pour leur patience devant les innombrables soirées et week-ends passés à déchiffrer "
        "du latin médiéval. Cette obsession n'aurait pas été possible sans leur amour.", s_ack))
    story.append(Paragraph(
        "À <b>Flow Line Integration</b> pour les ressources de calcul et l'infrastructure IA.", s_ack))
    story.append(Paragraph(
        "À <b>Tim King</b> et <b>Alessandra Andrisani</b>, Bryce Beasley et Julian Condo  - "
        "pour le tableau de translitération sans lequel rien de tout ceci n'existerait.", s_ack))
    story.append(Paragraph(
        "À <b>Nick Pelling</b> pour son analyse pionnière du folio f57v, "
        "à <b>René Zandbergen</b> et Gabriel Landini pour la transcription EVA, "
        "et à la communauté du forum Voynich Ninja.", s_ack))
    story.append(Paragraph(
        "Dédié à la mémoire d'<b>Alan Turing</b> (1912-1954).", s_ack))

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
