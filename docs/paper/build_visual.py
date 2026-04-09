#!/usr/bin/env python3
"""
Voynich Visual Summary,8-page companion PDF for voynich.ninja.
No fluff, diagrams + tables + honest limitations.
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, HRFlowable
from reportlab.pdfgen import canvas

from config import (
    DARK_NAVY, DEEP_BLUE, MEDIUM_BLUE, ACCENT_BLUE, WARM_GRAY,
    GOLD, DARK_GOLD, BORDER, TABLE_HEAD, TABLE_ALT, PALE_BLUE,
    MARGIN_L, MARGIN_R, W, H, TEXT_W, STATS,
    s_h1, s_h2, s_body, s_caption,
    gold_rule, blue_rule, make_table,
)
from diagrams import (
    DrawingFlowable,
    make_volvelle_diagram, make_pipeline_diagram,
    make_perseus_chart, make_ashmole_comparison, make_cipher_layers
)

S = STATS

# Compact styles
s_vtitle = ParagraphStyle('VTitle', fontSize=20, leading=25,
    textColor=DARK_NAVY, alignment=TA_CENTER, fontName='Helvetica-Bold', spaceAfter=3*mm)
s_vsub = ParagraphStyle('VSub', fontSize=11, leading=14,
    textColor=MEDIUM_BLUE, alignment=TA_CENTER, fontName='Helvetica-Oblique', spaceAfter=6*mm)
s_vbody = ParagraphStyle('VBody', fontSize=10, leading=14,
    textColor=HexColor("#1a1a1a"), alignment=TA_JUSTIFY, fontName='Helvetica', spaceAfter=3*mm)
s_vbold = ParagraphStyle('VBold', parent=s_vbody, fontName='Helvetica-Bold')
s_vsmall = ParagraphStyle('VSmall', fontSize=8.5, leading=11,
    textColor=WARM_GRAY, fontName='Helvetica', spaceAfter=2*mm)
s_vwarn = ParagraphStyle('VWarn', fontSize=9.5, leading=13,
    textColor=HexColor("#8b4513"), alignment=TA_JUSTIFY, fontName='Helvetica',
    spaceAfter=3*mm, leftIndent=5*mm, rightIndent=5*mm)
s_vlink = ParagraphStyle('VLink', fontSize=9, leading=12, textColor=DARK_NAVY,
    alignment=TA_CENTER, fontName='Helvetica-Bold', spaceAfter=2*mm)


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved = []

    def showPage(self):
        self._saved.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        for i, state in enumerate(self._saved):
            self.__dict__.update(state)
            self.saveState()
            self.setFont('Helvetica', 7)
            self.setFillColor(WARM_GRAY)
            self.drawCentredString(W/2, 10*mm, f"{i+1}")
            self.setStrokeColor(GOLD)
            self.setLineWidth(0.4)
            self.line(MARGIN_L, 13*mm, W-MARGIN_R, 13*mm)
            self.restoreState()
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)


def build():
    output = "d:/Github/Voynich/docs/conference/Voynich_Visual_Summary.pdf"
    os.makedirs(os.path.dirname(output), exist_ok=True)
    doc = SimpleDocTemplate(output, pagesize=A4,
        leftMargin=MARGIN_L, rightMargin=MARGIN_R,
        topMargin=18*mm, bottomMargin=18*mm)
    story = []

    # ═══════════════════════════════════════
    # PAGE 1 : TITRE + RÉSUMÉ
    # ═══════════════════════════════════════
    story.append(Spacer(1, 15*mm))
    story.append(gold_rule(40, 2))
    story.append(Paragraph("K&amp;A v12 Pipeline: Voynich Manuscript", s_vtitle))
    story.append(Paragraph("Computational Latin Recovery,Visual Summary", s_vsub))
    story.append(gold_rule(40, 2))
    story.append(Spacer(1, 5*mm))

    story.append(Paragraph(
        "Guillaume Clement,CTO, Flow Line Integration<br/>"
        "Assisted by Claude (Anthropic, Opus 4.6),April 2026", s_vsmall))
    story.append(Spacer(1, 5*mm))

    story.append(Paragraph("<b>What this document is:</b> A visual summary of a computational "
        "pipeline that tests the King-Andrisani transliteration hypothesis (2021) at scale. "
        "The results are interesting but not definitive. My goal is to transmit this work "
        "to researchers with expertise in medieval Latin and pharmaceutical history.",
        s_vbody))
    story.append(Spacer(1, 3*mm))

    story.append(make_table(
        ["Metric", "Value"],
        [
            ["Words decoded", f"{S['total_words']:,} across {S['total_folios']} folio sides"],
            ["Perseus validation", f"{S['perseus_pct']}% (265,419 attested Latin forms)"],
            ["CONFIRMED + HIGH confidence", f"{S['conf_high_pct']}%"],
            ["Pharmaceutical terms found", "33 (23 ingredients, 6 verbs, 4 markers)"],
            ["f57v structure", "Compatible with medico-astrological volvelle (cf. Ashmole 370)"],
            ["Source code + decoded text", "github.com/CorwinFr/Voynich (open source)"],
        ],
        col_widths=[45*mm, 115*mm]))
    story.append(Paragraph("Table 1. Summary metrics.", s_caption))

    story.append(PageBreak())

    # ═══════════════════════════════════════
    # PAGE 2 : PIPELINE + EXAMPLE
    # ═══════════════════════════════════════
    story.append(Paragraph("How the Pipeline Works", s_h1))
    story.append(blue_rule())
    story.append(DrawingFlowable(make_pipeline_diagram()))
    story.append(Paragraph("Figure 1. K&amp;A v12 pipeline architecture.", s_caption))

    story.append(Paragraph("<b>Worked example:</b> EVA word <b>daiin</b>", s_vbold))
    story.append(make_table(
        ["Step", "Action", "Result"],
        [
            ["T1", "Normalize", "daiin"],
            ["T2a", "Monolithic K&A decode", "d→in, a→a, ii→ur, n→p → 'inaurp',not in Perseus"],
            ["T2b", "Try prefix d = 'in' + root 'aiin'", "aiin → aquam (Perseus: YES)"],
            ["T3", "Grade", "HIGH (prefix + Perseus match)"],
            ["T4", "Score", "Selected: in aquam ('into water')"],
        ],
        col_widths=[12*mm, 52*mm, 96*mm]))
    story.append(Paragraph("Table 2. Step-by-step decoding of 'daiin'.", s_caption))

    story.append(Paragraph("<b>Agglutinative Prefixes</b>,The scribe fuses prepositions "
        "to the following word (Arabic proclitic style):", s_vbold))
    story.append(make_table(
        ["EVA", "Latin", "Meaning", "Example"],
        [
            ["y",  "in",   "in/into",    "ykeedy → in + ciere (in + to stir)"],
            ["d",  "in",   "in/into",    "daiin → in + aquam (in + water)"],
            ["qo", "cum",  "with",       "qokeey → cum + eo (with + it)"],
            ["ol", "es/ex","from/out",   "olshedy → es + cibo et (from + food and)"],
            ["r",  "re-",  "again",      "rkar → re + cura (again + care)"],
            ["p",  "per",  "through",    "pchedy → per + eius et (through + his and)"],
            ["da", "in a", "in + article","daiin → in aquam"],
            ["l",  "es/ex","from",       "lchedy → es eius et"],
            ["t",  "el",   "the",        "tchoky → el iqu"],
            ["f",  "par",  "by/for",     "fchedy → par eius et"],
        ],
        col_widths=[12*mm, 14*mm, 18*mm, 90*mm]))
    story.append(Paragraph("Table 3. Agglutinative prefix rules (10 of 13 shown).", s_caption))

    story.append(PageBreak())

    # ═══════════════════════════════════════
    # PAGE 3 : GLYPH MAPPING + LOGOGRAMS
    # ═══════════════════════════════════════
    story.append(Paragraph("The K&amp;A Phonetic Mapping", s_h1))
    story.append(blue_rule())

    story.append(Paragraph("<b>Key EVA → Latin glyph values</b> (King-Andrisani 2021, "
        "probabilistic,multiple values per glyph):", s_vbold))
    story.append(make_table(
        ["EVA glyph", "Latin value(s)", "Weight", "Example word"],
        [
            ["k",  "c / qu",     "50/50", "kaiin → curam (care)"],
            ["o",  "e / a",      "50/50", "okeey → eo (by it)"],
            ["d",  "d / de / ed","40/30/30","dar → iure (by right)"],
            ["l",  "s / ce",     "60/40", "loty → sal (salt)"],
            ["a",  "u / a",      "60/40", "aiin → aquam (water)"],
            ["r",  "re / r / ra","50/30/20","rar → rure (in the country)"],
            ["t",  "el / l / le","50/30/20","teey → elo (from it)"],
            ["e",  "o / e",      "50/50", "eey → eo (by it)"],
            ["s",  "us / su / s","40/30/30","sar → iure (juice)"],
            ["ch", "i",          "100",   "chedy → eius et (his and)"],
            ["sh", "ci",         "100",   "shey → cies (you stir)"],
            ["cth","li / ili",   "50/50", "chcthy → ili (for the)"],
            ["ckh","qui / aqui", "70/30", "chckhy → iqui (indeed)"],
        ],
        col_widths=[20*mm, 26*mm, 18*mm, 70*mm]))
    story.append(Paragraph("Table 4. Principal K&A glyph mappings.", s_caption))

    story.append(Paragraph("<b>Top logograms</b> (whole-word mappings, confirmed):", s_vbold))
    story.append(make_table(
        ["EVA", "Latin", "Meaning", "Freq."],
        [
            ["dy",     "et",       "and",              "281"],
            ["y",      "in",       "in/into",          "338"],
            ["chedy",  "eius et",  "his/its and",      "504"],
            ["otedy",  "tere et",  "grind and",        "514"],
            ["r",      "recipe",   "take (Rx)",        "171"],
            ["qoky",   "coque",    "cook!",            "145"],
            ["sho",    "cibo",     "food (abl.)",      "93"],
            ["am",     "cum",      "with",             "86"],
            ["or",     "hiera",    "sacred compound",  "30"],
            ["oteos",  "aloes",    "aloe",             "25"],
            ["m",      "misce",    "mix!",             "13"],
            ["x",      "crux",     "cross/mark",       "10"],
        ],
        col_widths=[18*mm, 22*mm, 40*mm, 16*mm]))
    story.append(Paragraph("Table 5. Key logograms.", s_caption))

    story.append(Paragraph(
        "<i>Every decoded word is checked against the Perseus Digital Library (Tufts University), "
        "265,419 attested Latin forms. This is an external, verifiable criterion.</i>", s_vsmall))

    story.append(PageBreak())

    # ═══════════════════════════════════════
    # PAGE 4 : KEY FINDINGS
    # ═══════════════════════════════════════
    story.append(Paragraph("Key Findings", s_h1))
    story.append(blue_rule())

    story.append(Paragraph("<b>f103r,Pharmaceutical vocabulary density</b>", s_h2))
    story.append(Paragraph(
        "532 words, 91% Perseus match. The verb <i>coque</i> (cook) appears 17 times "
        "in 5 conjugated forms: coque, coquas, coquere, coquendo, coquant. This constitutes "
        "a Latin morphological paradigm that is statistically difficult to produce by chance.", s_vbody))
    story.append(make_table(
        ["Latin", "English", "Occ."],
        [
            ["aloe/aloes", "aloe", "10+"],
            ["ture/turis", "frankincense", "2"],
            ["sal", "salt", "3"],
            ["olei", "oil", "4"],
            ["aceto", "vinegar", "2"],
            ["cerae", "wax", "3"],
            ["iecur", "liver", "2"],
            ["hiera", "sacred compound", "8"],
            ["mel", "honey", "1"],
        ],
        col_widths=[28*mm, 40*mm, 16*mm]))
    story.append(Paragraph("Table 6. Ingredients found on f103r. Compatible with 7/12 Aurea Alexandrina.", s_caption))

    story.append(Paragraph("<b>f33r,INELIODE / Inula helenium</b>", s_h2))
    story.append(Paragraph(
        "Pipeline decodes INELIODE, compatible with <i>Inula helenium</i> (elecampane, "
        "Asteraceae). The botanical illustration on the same page shows composite flowers "
        "with striped disk patterns, morphologically consistent with Asteraceae. The accompanying "
        "text contains <i>equaliter</i> (equal parts), <i>tere</i> (grind), <i>ture</i> "
        "(frankincense). Three independent indicators on one page.", s_vbody))

    story.append(Paragraph("<b>Astronomical pages,hidden pharmaceutical vocabulary</b>", s_h2))
    story.append(Paragraph(
        "Folio-by-folio analysis found pharmaceutical terms on pages previously considered "
        "purely astronomical: <i>nardi</i> (spikenard, f67r2), <i>cassiae</i> (cinnamon, "
        "f67v1), <i>apii</i> (celery, f85r1), <i>vini</i> (wine, f67r1). These were not "
        "in the initial calibration set.", s_vbody))

    story.append(Paragraph("<b>Italian vernacular</b>", s_h2))
    story.append(Paragraph(
        "<i>Pepe</i> (Italian for <i>piper</i>) and <i>lilie</i> (Italian for <i>lilium</i>) "
        "suggest a native Italian speaker, consistent with C14 dating (1404-1438) and "
        "the Veneto hypothesis.", s_vbody))

    story.append(PageBreak())

    # ═══════════════════════════════════════
    # PAGE 5 : VOLVELLE
    # ═══════════════════════════════════════
    story.append(Paragraph("Folio f57v,Possible Volvelle", s_h1))
    story.append(blue_rule())
    story.append(DrawingFlowable(make_volvelle_diagram()))
    story.append(Paragraph("Figure 2. f57v volvelle structure (schematic).", s_caption))
    story.append(DrawingFlowable(make_ashmole_comparison()))
    story.append(Paragraph("Figure 3. Structural correspondence with Ashmole 370 (~1424). "
        "The 29-word ring L04 matches the synodic lunar month.", s_caption))

    story.append(PageBreak())

    # ═══════════════════════════════════════
    # PAGE 6 : CIPHER MODEL + CHART
    # ═══════════════════════════════════════
    story.append(Paragraph("Cipher Model and Validation", s_h1))
    story.append(blue_rule())
    story.append(DrawingFlowable(make_cipher_layers()))
    story.append(Paragraph("Figure 4. Three-layer cipher model.", s_caption))
    story.append(DrawingFlowable(make_perseus_chart()))
    story.append(Paragraph("Figure 5. Validation rates across selected folios.", s_caption))

    story.append(PageBreak())

    # ═══════════════════════════════════════
    # PAGE 7 : WHAT DOESN'T WORK
    # ═══════════════════════════════════════
    story.append(Paragraph("What Does Not Work,Known Limitations", s_h1))
    story.append(blue_rule())

    story.append(Paragraph(
        "This section is the most important in this document. These are the problems "
        "I cannot solve and the biases I cannot rule out.", s_vbody))

    story.append(make_table(
        ["Problem", "Detail", "Severity"],
        [
            ["Opaque words", "3,421 words (8.8%) undecoded. Failure rate: 29% at 8+ chars, 44% at 10+ chars.", "High"],
            ["Nomenclator", "Zodiac labels, star names, plant names use a separate code. Zodiac crib attacks = negative.", "High"],
            ["No 5-word match", "Never found 5 consecutive specific words in a known medieval text. Max = 4 words, 19 times.", "High"],
            ["Missing ingredients", "4/12 Aurea Alexandrina missing: cinamomi, masticis, myrrha, galangal. K&A-incompatible.", "Medium"],
            ["Homophonic collisions", "EVA 'f' and 'p' both decode to 'per'. Different EVA words can produce same Latin.", "Medium"],
            ["Short word bias", "2-3 letter Latin words (et, in, ex, es) match easily by chance. How much of 89% is artifact?", "Unknown"],
            ["Scoring circularity", "The scorer favors Perseus matches, so it selects Latin-looking output. Is this circular?", "Unknown"],
            ["Grammar untested", "I lack medieval Latin expertise to assess grammatical coherence of decoded output.", "Critical"],
            ["Volvelle center", "8 words in f57v central pivot are all LOW/OPAQUE. Found the machine, not the instructions.", "Medium"],
        ],
        col_widths=[30*mm, 98*mm, 18*mm]))
    story.append(Paragraph("Table 7. Known limitations and open questions.", s_caption))

    story.append(Paragraph(
        "89% is an interesting number. But I honestly do not know how much of it reflects "
        "genuine Latin structure in the manuscript versus artifacts of the scoring method. "
        "A medieval Latin specialist would see in five minutes what I cannot see in five weeks.",
        s_vwarn))

    story.append(PageBreak())

    # ═══════════════════════════════════════
    # PAGE 8 : CALL TO COMMUNITY
    # ═══════════════════════════════════════
    story.append(Paragraph("An Invitation", s_h1))
    story.append(blue_rule())

    story.append(Paragraph(
        "I am not the person who will solve the Voynich Manuscript. I'm a technologist "
        "who built a tool and obtained results that I find interesting but cannot fully "
        "evaluate myself.", s_vbody))
    story.append(Paragraph(
        "My purpose is to <b>transmit this work</b> to people who have the expertise "
        "I lack: medieval Latin, pharmaceutical history, Voynich paleography. "
        "If any of these results have value, it will be because someone with the "
        "right knowledge picked them up and pushed further.", s_vbody))
    story.append(Paragraph(
        "Everything is open source. The pipeline code is Python, the decoded text "
        "covers all 226 folio sides, and the folio-by-folio enriched catalogue is "
        "a structured JSON. Take it, break it, improve it.", s_vbody))

    story.append(Spacer(1, 8*mm))
    story.append(gold_rule(50, 2))
    story.append(Spacer(1, 5*mm))

    story.append(Paragraph("github.com/CorwinFr/Voynich", s_vlink))
    story.append(Paragraph("DOI: 10.5281/zenodo.19477552", s_vlink))
    story.append(Spacer(1, 5*mm))

    story.append(Paragraph(
        "Guillaume Clement,gcle1979@gmail.com<br/>"
        "Flow Line Integration", s_vsmall))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        "Registered via Enveloppe Soleau, INPI (France), April 2026.",
        ParagraphStyle('Legal', fontSize=7, leading=9, textColor=WARM_GRAY,
            alignment=TA_CENTER, fontName='Helvetica-Oblique')))

    # ═══════════════════════════════════════
    # APPENDIX: ALL DECODED FOLIOS (compact)
    # ═══════════════════════════════════════
    story.append(PageBreak())
    story.append(Paragraph("Appendix: Complete Decoded Text (226 Folio Sides)", s_h1))
    story.append(blue_rule())
    story.append(Paragraph(
        "CONFIRMED + HIGH confidence words only. '...' = undecoded (OPAQUE). "
        "Full decode with EVA alignment available at github.com/CorwinFr/Voynich", s_vsmall))
    story.append(Spacer(1, 2*mm))

    # Read clean Latin text
    clean_path = "d:/Github/Voynich/docs/decoded/VOYNICH_LATIN_CLEAN.txt"
    s_folio_hdr = ParagraphStyle('FolioHdr', fontSize=7.5, leading=9,
        fontName='Helvetica-Bold', textColor=DARK_NAVY, spaceBefore=2*mm, spaceAfter=0.5*mm)
    s_folio_txt = ParagraphStyle('FolioTxt', fontSize=6, leading=7.5,
        fontName='Courier', textColor=HexColor("#333333"), spaceAfter=0.5*mm,
        leftIndent=2*mm)

    with open(clean_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    current_folio = None
    folio_lines = []
    folio_count = 0

    def flush_folio():
        nonlocal current_folio, folio_lines, folio_count
        if current_folio and folio_lines:
            # Compact: max 3 lines per folio, join rest with spaces
            text_joined = ' '.join(l.strip() for l in folio_lines if l.strip())
            if len(text_joined) > 300:
                text_joined = text_joined[:297] + '...'
            story.append(Paragraph(f"<b>{current_folio}</b>", s_folio_hdr))
            story.append(Paragraph(text_joined.replace('&', '&amp;').replace('<', '&lt;'), s_folio_txt))
            folio_count += 1
        folio_lines = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith('---') and stripped.endswith('---'):
            flush_folio()
            current_folio = stripped.replace('---', '').strip()
        elif stripped.startswith('===') or stripped.startswith('#') or not stripped:
            continue
        else:
            folio_lines.append(stripped)
    flush_folio()

    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(f"{folio_count} folios decoded. Full text: github.com/CorwinFr/Voynich", s_vsmall))

    doc.build(story, canvasmaker=NumberedCanvas)
    size = os.path.getsize(output) / 1024
    print(f"PDF: {output} ({size:.0f} KB)")


if __name__ == "__main__":
    build()
