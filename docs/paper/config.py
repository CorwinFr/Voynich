"""
Configuration: colors, styles, page layout, corrected statistics.
All numbers verified against VOYNICH_DECODE_V12_INGREDIENTS.txt (2026-04-09).
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import HRFlowable, Table, TableStyle, Paragraph

# ══════════════════════════════════════════
# COLORS
# ══════════════════════════════════════════
DARK_NAVY   = HexColor("#0d1b2a")
NAVY        = HexColor("#1b2838")
DEEP_BLUE   = HexColor("#1a3a5c")
MEDIUM_BLUE = HexColor("#2c5f8a")
ACCENT_BLUE = HexColor("#3a7cbf")
LIGHT_BLUE  = HexColor("#e3edf7")
PALE_BLUE   = HexColor("#f4f8fc")
GOLD        = HexColor("#c9a84c")
DARK_GOLD   = HexColor("#a07d2e")
LIGHT_GOLD  = HexColor("#f5ecd0")
WARM_GRAY   = HexColor("#6b7280")
LIGHT_GRAY  = HexColor("#f3f4f6")
MED_GRAY    = HexColor("#9ca3af")
BORDER      = HexColor("#d1d5db")
TABLE_HEAD  = HexColor("#1a3a5c")
TABLE_ALT   = HexColor("#f0f5fa")
RED_SOFT     = HexColor("#dc6b5a")
GREEN_SOFT   = HexColor("#4a9d6e")
PURPLE_SOFT  = HexColor("#7c5cbf")
ORANGE_SOFT  = HexColor("#d4883a")

# ══════════════════════════════════════════
# PAGE LAYOUT
# ══════════════════════════════════════════
W, H = A4
MARGIN_L = 22 * mm
MARGIN_R = 22 * mm
TEXT_W = W - MARGIN_L - MARGIN_R

# ══════════════════════════════════════════
# CORRECTED STATISTICS (from v12 final output)
# ══════════════════════════════════════════
STATS = {
    "total_words":   38_442,
    "total_folios":  226,        # folio sides
    "folio_ids":     184,        # unique EVA folio identifiers
    "confirmed":     8_543,
    "high":         26_277,
    "medium":          346,
    "low":           2_799,
    "opaque":          477,
    "perseus":      34_342,
    "medical":       6_509,
    "conf_high_pct":  90.6,
    "perseus_pct":    89.3,
    "medical_pct":    16.9,
    "opaque_pct":      1.2,
    "h1_entropy":     3.65,      # approximate global
    # Per-folio (v12 actual)
    "f103r": {"words": 532, "conf_high": 93, "perseus": 91, "medical": 26},
    "f75r":  {"words": 417, "conf_high": 96, "perseus": 95, "medical": 19},
    "f88r":  {"words": 150, "conf_high": 94, "perseus": 93, "medical": 13},
    "f1v":   {"words":  92, "conf_high": 90, "perseus": 90, "medical":  8},
    "f57v":  {"words": 176, "conf_high": 70, "perseus": 70, "medical": 16},
    "f33r":  {"words":  74, "conf_high": 95, "perseus": 95, "medical": 28},
}

# Section breakdown (from v12 output)
SECTIONS = {
    "H": {"name": "Herbal",          "folios": 129, "desc": "Plant monographs with pharmaceutical properties"},
    "S": {"name": "Pharmaceutical",   "folios":  25, "desc": "Recipe-dense pharmaceutical section"},
    "P": {"name": "Pharma (cont.)",   "folios":  16, "desc": "Additional pharmaceutical pages"},
    "B": {"name": "Balneological",    "folios":  19, "desc": "Hydrotherapy treatises (human figures in baths)"},
    "C": {"name": "Cosmological",     "folios":  10, "desc": "Multi-page diagrams, volvelle (f57v)"},
    "A": {"name": "Astronomical",     "folios":   8, "desc": "Additional astrological content"},
    "Z": {"name": "Zodiac",           "folios":  12, "desc": "Circular zodiac diagrams with star labels"},
    "T": {"name": "Transitional",     "folios":   7, "desc": "Title/boundary pages (f1r, f116v)"},
}

# ══════════════════════════════════════════
# STYLES
# ══════════════════════════════════════════
s_title_main = ParagraphStyle('TitleMain', fontSize=22, leading=27,
    textColor=DARK_NAVY, alignment=TA_CENTER, fontName='Helvetica-Bold',
    spaceAfter=4*mm)

s_title_sub = ParagraphStyle('TitleSub', fontSize=13, leading=17,
    textColor=MEDIUM_BLUE, alignment=TA_CENTER, fontName='Helvetica',
    spaceAfter=3*mm)

s_author = ParagraphStyle('Author', fontSize=11, leading=14,
    textColor=DARK_NAVY, alignment=TA_CENTER, fontName='Helvetica-Bold',
    spaceAfter=1.5*mm)

s_affil = ParagraphStyle('Affil', fontSize=9, leading=12,
    textColor=WARM_GRAY, alignment=TA_CENTER, fontName='Helvetica',
    spaceAfter=1.5*mm)

s_abstract_title = ParagraphStyle('AbsTitle', fontSize=11, leading=14,
    textColor=DARK_NAVY, fontName='Helvetica-Bold', spaceBefore=5*mm,
    spaceAfter=2*mm, alignment=TA_CENTER)

s_abstract = ParagraphStyle('Abstract', fontSize=9.5, leading=13.5,
    textColor=HexColor("#333333"), alignment=TA_JUSTIFY,
    fontName='Helvetica', leftIndent=12*mm, rightIndent=12*mm,
    spaceAfter=3*mm)

s_keywords = ParagraphStyle('Keywords', fontSize=8.5, leading=11,
    textColor=WARM_GRAY, fontName='Helvetica', leftIndent=12*mm,
    rightIndent=12*mm, spaceAfter=5*mm)

s_h1 = ParagraphStyle('H1', fontSize=16, leading=20, textColor=DARK_NAVY,
    spaceBefore=9*mm, spaceAfter=4*mm, fontName='Helvetica-Bold')

s_h2 = ParagraphStyle('H2', fontSize=12, leading=15, textColor=DEEP_BLUE,
    spaceBefore=6*mm, spaceAfter=3*mm, fontName='Helvetica-Bold')

s_h3 = ParagraphStyle('H3', fontSize=10, leading=13, textColor=MEDIUM_BLUE,
    spaceBefore=4*mm, spaceAfter=2*mm, fontName='Helvetica-Bold')

s_body = ParagraphStyle('Body', fontSize=10, leading=14,
    textColor=HexColor("#1a1a1a"), alignment=TA_JUSTIFY,
    fontName='Helvetica', spaceAfter=3*mm)

s_body_indent = ParagraphStyle('BodyIndent', parent=s_body,
    leftIndent=8*mm, rightIndent=5*mm, fontSize=9.5, leading=13)

s_caption = ParagraphStyle('Caption', fontSize=8.5, leading=11,
    textColor=WARM_GRAY, alignment=TA_CENTER, fontName='Helvetica-Oblique',
    spaceBefore=2*mm, spaceAfter=6*mm)

s_table_h = ParagraphStyle('TH', fontSize=8.5, leading=11,
    textColor=white, fontName='Helvetica-Bold', alignment=TA_CENTER)

s_table_c = ParagraphStyle('TC', fontSize=8.5, leading=11,
    textColor=black, fontName='Helvetica')

s_table_cc = ParagraphStyle('TCC', parent=s_table_c, alignment=TA_CENTER)

s_ref = ParagraphStyle('Ref', fontSize=8.5, leading=11.5,
    textColor=HexColor("#333333"), fontName='Helvetica',
    leftIndent=10*mm, firstLineIndent=-10*mm, spaceAfter=1.5*mm)

s_ack = ParagraphStyle('Ack', fontSize=9.5, leading=13.5,
    textColor=HexColor("#333333"), alignment=TA_JUSTIFY,
    fontName='Helvetica', spaceAfter=3*mm)

s_decode_line = ParagraphStyle('DecodeLine', fontSize=8, leading=11,
    textColor=DEEP_BLUE, fontName='Courier', leftIndent=5*mm,
    spaceAfter=0.5*mm)

s_fig_title = ParagraphStyle('FigTitle', fontSize=9, leading=12,
    textColor=DARK_NAVY, fontName='Helvetica-Bold', alignment=TA_CENTER,
    spaceBefore=3*mm, spaceAfter=1*mm)


# ══════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════
def gold_rule(width_pct=100, thickness=1):
    return HRFlowable(width=f"{width_pct}%", thickness=thickness,
        color=GOLD, spaceBefore=2*mm, spaceAfter=2*mm)

def blue_rule(width_pct=100, thickness=0.5):
    return HRFlowable(width=f"{width_pct}%", thickness=thickness,
        color=ACCENT_BLUE, spaceBefore=1*mm, spaceAfter=1*mm)

def make_table(headers, rows, col_widths=None):
    hdr = [Paragraph(h, s_table_h) for h in headers]
    data = [hdr]
    for row in rows:
        data.append([Paragraph(str(c), s_table_c) for c in row])
    t = Table(data, colWidths=col_widths, repeatRows=1)
    cmds = [
        ('BACKGROUND', (0,0), (-1,0), TABLE_HEAD),
        ('TEXTCOLOR', (0,0), (-1,0), white),
        ('GRID', (0,0), (-1,-1), 0.4, BORDER),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            cmds.append(('BACKGROUND', (0,i), (-1,i), TABLE_ALT))
    t.setStyle(TableStyle(cmds))
    return t
