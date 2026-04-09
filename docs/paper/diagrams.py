"""
All diagrams for the paper.
Fixed: volvelle labels on white background, pipeline text centered in boxes.
"""
import math
from reportlab.graphics.shapes import (
    Drawing, Circle, Line, String, Rect, Polygon, Group, Wedge
)
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics import renderPDF
from reportlab.platypus import Flowable

from config import (
    DARK_NAVY, DEEP_BLUE, MEDIUM_BLUE, ACCENT_BLUE, PALE_BLUE,
    GOLD, DARK_GOLD, LIGHT_GOLD, WARM_GRAY, BORDER,
    RED_SOFT, GREEN_SOFT, PURPLE_SOFT, ORANGE_SOFT,
    white, STATS
)


class DrawingFlowable(Flowable):
    def __init__(self, drawing):
        Flowable.__init__(self)
        self.drawing = drawing
        self.width = drawing.width
        self.height = drawing.height

    def draw(self):
        renderPDF.draw(self.drawing, self.canv, 0, 0)


# ══════════════════════════════════════════
# VOLVELLE f57v — FIXED LAYOUT
# Labels on white rectangles, positioned to avoid overlap
# ══════════════════════════════════════════
def make_volvelle_diagram():
    dw, dh = 480, 460
    d = Drawing(dw, dh)

    # Center the volvelle on the LEFT to leave space for labels on right
    cx, cy = 180, dh / 2 - 15

    # Background
    d.add(Rect(0, 0, dw, dh, fillColor=white, strokeColor=None))

    # Outer decorative border
    d.add(Circle(cx, cy, 170, fillColor=None, strokeColor=BORDER, strokeWidth=0.5))

    # Ring fills
    ring_fills = [
        HexColor("#c0d4e8"), HexColor("#cddcec"), HexColor("#dbe7f2"),
        HexColor("#e8f0f8"), HexColor("#f5ecd0"),
    ]

    ring_data = [
        (160, 130, ring_fills[0], MEDIUM_BLUE),   # L02
        (130, 100, ring_fills[1], MEDIUM_BLUE),    # L03
        (100,  72, ring_fills[2], MEDIUM_BLUE),    # L04
        ( 72,  45, ring_fills[3], ACCENT_BLUE),    # L05
        ( 45,   0, ring_fills[4], DARK_GOLD),      # Core
    ]

    # Draw rings as filled circles (outer first)
    for outer_r, inner_r, fill, stroke in ring_data:
        d.add(Circle(cx, cy, outer_r, fillColor=fill, strokeColor=stroke, strokeWidth=1.2))

    # Core circle on top
    d.add(Circle(cx, cy, 45, fillColor=ring_fills[4], strokeColor=DARK_GOLD, strokeWidth=1.5))

    # Tick marks on outer ring (54 elements for L02)
    for i in range(54):
        angle = math.radians(i * 360 / 54)
        x1 = cx + 158 * math.cos(angle)
        y1 = cy + 158 * math.sin(angle)
        x2 = cx + 163 * math.cos(angle)
        y2 = cy + 163 * math.sin(angle)
        d.add(Line(x1, y1, x2, y2, strokeColor=MEDIUM_BLUE, strokeWidth=0.4))

    # L03 quadrant dividers (4 seasons)
    quad_colors = [GREEN_SOFT, ORANGE_SOFT, RED_SOFT, PURPLE_SOFT]
    quad_labels = ["VER", "AES", "AVT", "HIE"]
    for i in range(4):
        angle = math.radians(i * 90 + 45)
        x1 = cx + 100 * math.cos(angle)
        y1 = cy + 100 * math.sin(angle)
        x2 = cx + 130 * math.cos(angle)
        y2 = cy + 130 * math.sin(angle)
        d.add(Line(x1, y1, x2, y2, strokeColor=DARK_NAVY, strokeWidth=1.0))
        mid_angle = math.radians(i * 90 + 90)
        lx = cx + 115 * math.cos(mid_angle)
        ly = cy + 115 * math.sin(mid_angle)
        d.add(String(lx - 6, ly - 4, quad_labels[i], fontSize=6,
                    fontName='Helvetica-Bold', fillColor=quad_colors[i]))

    # L04 tick marks (29 words for lunar cycle)
    for i in range(29):
        angle = math.radians(i * 360 / 29 - 90)
        x1 = cx + 98 * math.cos(angle)
        y1 = cy + 98 * math.sin(angle)
        x2 = cx + 101 * math.cos(angle)
        y2 = cy + 101 * math.sin(angle)
        d.add(Line(x1, y1, x2, y2, strokeColor=MEDIUM_BLUE, strokeWidth=0.5))
        if i in (0, 12, 18, 26):
            d.add(Circle(cx + 86 * math.cos(angle), cy + 86 * math.sin(angle),
                        2.5, fillColor=GOLD, strokeColor=DARK_GOLD, strokeWidth=0.5))

    # L05: 75% arc (gap from ~200 to ~290 deg)
    gap_start, gap_end = 200, 290
    for deg in range(0, 360, 2):
        if gap_start < deg < gap_end:
            continue
        angle = math.radians(deg)
        x1 = cx + 58 * math.cos(angle)
        y1 = cy + 58 * math.sin(angle)
        d.add(Circle(x1, y1, 1.0, fillColor=ACCENT_BLUE, strokeColor=None))

    # Gap annotation
    gap_mid = math.radians(245)
    gx = cx + 60 * math.cos(gap_mid)
    gy = cy + 60 * math.sin(gap_mid)
    d.add(String(gx - 18, gy - 2, "90° gap", fontSize=5.5,
                fontName='Helvetica-Oblique', fillColor=RED_SOFT))
    d.add(String(gx - 22, gy - 10, "(night hours)", fontSize=5,
                fontName='Helvetica-Oblique', fillColor=RED_SOFT))

    # Central sun with rays
    d.add(Circle(cx, cy, 18, fillColor=GOLD, strokeColor=DARK_GOLD, strokeWidth=2))
    d.add(Circle(cx, cy, 12, fillColor=HexColor("#e8c84c"), strokeColor=DARK_GOLD, strokeWidth=1))
    for angle_deg in range(0, 360, 20):
        angle = math.radians(angle_deg)
        x1 = cx + 18 * math.cos(angle)
        y1 = cy + 18 * math.sin(angle)
        x2 = cx + 25 * math.cos(angle)
        y2 = cy + 25 * math.sin(angle)
        d.add(Line(x1, y1, x2, y2, strokeColor=DARK_GOLD, strokeWidth=1.2))

    # Four cardinal figures
    for dx, dy in [(0, 32), (32, 0), (0, -32), (-32, 0)]:
        fx, fy = cx + dx, cy + dy
        d.add(Circle(fx, fy + 4, 3, fillColor=ORANGE_SOFT, strokeColor=DARK_GOLD, strokeWidth=0.8))
        d.add(Line(fx - 5, fy, fx + 5, fy, strokeColor=DARK_GOLD, strokeWidth=0.8))
        d.add(Line(fx, fy + 1, fx, fy - 3.5, strokeColor=DARK_GOLD, strokeWidth=0.8))

    # ── RIGHT-SIDE ANNOTATIONS on white backgrounds ──
    label_x = 360
    annotations = [
        (160, "L02: Pharmaceutical Index",  "54 logogram elements",      MEDIUM_BLUE, 390),
        (130, "L03: Astrological Aspects",  "4 × 17 repeating pattern",  MEDIUM_BLUE, 330),
        (100, "L04: Lunar Cycle",           "29 words = synodic month",  MEDIUM_BLUE, 270),
        ( 72, "L05: Solar Dial",            "18h arc (75% of circle)",   ACCENT_BLUE, 210),
        ( 45, "Core: Sighting Pivot",       "Sun + 4 cardinal figures",  DARK_GOLD,   150),
    ]

    for ring_r, title, subtitle, color, label_y in annotations:
        # Leader line from ring edge to label
        ring_angle = math.radians(10)  # slightly above horizontal
        ring_x = cx + ring_r * math.cos(ring_angle)
        ring_y = cy + ring_r * math.sin(ring_angle)

        d.add(Line(ring_x, ring_y, label_x - 8, label_y + 5,
                   strokeColor=color, strokeWidth=0.6, strokeDashArray=[2, 2]))
        d.add(Circle(ring_x, ring_y, 2, fillColor=color, strokeColor=None))

        # White background rectangle for label
        box_w = 118
        box_h = 26
        d.add(Rect(label_x - 4, label_y - 6, box_w, box_h,
                   fillColor=white, strokeColor=color, strokeWidth=0.6, rx=3, ry=3))

        d.add(String(label_x, label_y + 8, title, fontSize=7,
                    fontName='Helvetica-Bold', fillColor=DARK_NAVY))
        d.add(String(label_x, label_y - 2, subtitle, fontSize=6.5,
                    fontName='Helvetica', fillColor=WARM_GRAY))

    # Title
    d.add(String(50, dh - 12, "Figure 2. Folio f57v Volvelle Structure",
                fontSize=11, fontName='Helvetica-Bold', fillColor=DARK_NAVY))
    d.add(String(50, dh - 25, "Schematic reconstruction after Pelling (2017) and Ashmole 370 parallels",
                fontSize=7.5, fontName='Helvetica', fillColor=WARM_GRAY))

    # Bottom legend
    d.add(String(20, 12, "Beinecke MS 408, f57v. Vellum, compass-drawn. C14: 1404-1438. Section C (Cosmology).",
                fontSize=6.5, fontName='Helvetica-Oblique', fillColor=WARM_GRAY))

    return d


# ══════════════════════════════════════════
# PIPELINE FLOWCHART — FIXED text centering
# ══════════════════════════════════════════
def make_pipeline_diagram():
    dw, dh = 480, 200
    d = Drawing(dw, dh)
    d.add(Rect(0, 0, dw, dh, fillColor=PALE_BLUE, strokeColor=None))

    boxes = [
        ("T1\nNormalize",            10, MEDIUM_BLUE),
        ("T2a\nMonolithic\nDecode", 105, GREEN_SOFT),
        ("T2b\nSegment\n+ Prefixes",200, ACCENT_BLUE),
        ("T3\nGrade\n(H/M/L)",     295, ORANGE_SOFT),
        ("T4\nScore &\nSelect",     390, PURPLE_SOFT),
    ]

    bw, bh = 80, 70
    by = 90

    for label, bx, color in boxes:
        d.add(Rect(bx, by, bw, bh, fillColor=color, strokeColor=DARK_NAVY,
                   strokeWidth=1, rx=6, ry=6))
        lines = label.split('\n')
        n_lines = len(lines)
        # Vertically center the text block
        total_text_h = n_lines * 12
        start_y = by + (bh + total_text_h) / 2 - 6
        for i, line in enumerate(lines):
            ty = start_y - i * 12
            # Horizontally center using textAnchor
            tx = bx + bw / 2
            d.add(String(tx, ty, line,
                        fontSize=8, fontName='Helvetica-Bold', fillColor=white,
                        textAnchor='middle'))

    # Arrows
    for i in range(len(boxes) - 1):
        x1 = boxes[i][1] + bw
        x2 = boxes[i + 1][1]
        ymid = by + bh / 2
        d.add(Line(x1, ymid, x2, ymid, strokeColor=DARK_NAVY, strokeWidth=1.5))
        d.add(Polygon([x2, ymid, x2 - 6, ymid + 4, x2 - 6, ymid - 4],
                      fillColor=DARK_NAVY, strokeColor=DARK_NAVY))

    # Perseus DB annotation
    d.add(Rect(160, 15, 160, 35, fillColor=LIGHT_GOLD, strokeColor=DARK_GOLD,
               strokeWidth=0.8, rx=4, ry=4))
    d.add(String(240, 30, "Perseus Latin Dictionary", fontSize=8,
                fontName='Helvetica-Bold', fillColor=DARK_GOLD, textAnchor='middle'))
    d.add(String(240, 19, "(265,419 entries)", fontSize=7,
                fontName='Helvetica', fillColor=DARK_GOLD, textAnchor='middle'))

    # Dashed lines from Perseus to T2a and T3
    for tx in [145, 335]:
        d.add(Line(240, 50, tx, by, strokeColor=DARK_GOLD,
                   strokeWidth=0.8, strokeDashArray=[3, 3]))

    # Title
    d.add(String(dw / 2, dh - 15, "K&A v12 Pipeline Architecture",
                fontSize=11, fontName='Helvetica-Bold', fillColor=DARK_NAVY,
                textAnchor='middle'))

    # Input/output labels
    d.add(String(15, by + bh + 12, "EVA token", fontSize=7,
                fontName='Helvetica-Oblique', fillColor=WARM_GRAY))
    d.add(String(395, by + bh + 12, "Latin output", fontSize=7,
                fontName='Helvetica-Oblique', fillColor=WARM_GRAY))

    return d


# ══════════════════════════════════════════
# BAR CHART — CORRECTED with v12 stats
# ══════════════════════════════════════════
def make_perseus_chart():
    dw, dh = 440, 220
    d = Drawing(dw, dh)
    d.add(Rect(0, 0, dw, dh, fillColor=white, strokeColor=None))

    bc = VerticalBarChart()
    bc.x = 55
    bc.y = 35
    bc.height = 145
    bc.width = 360

    # CORRECTED values from v12 actual output
    bc.data = [
        (70, 91, 89.3, 90, 95, 93, 95),   # Perseus rates
        (70, 93, 90.6, 90, 96, 94, 95),    # CONF+HIGH rates
    ]
    bc.categoryAxis.categoryNames = [
        'f57v', 'f103r', 'Global', 'f1v', 'f75r', 'f88r', 'f33r'
    ]
    bc.categoryAxis.labels.fontSize = 7
    bc.categoryAxis.labels.fontName = 'Helvetica'
    bc.valueAxis.valueMin = 0
    bc.valueAxis.valueMax = 100
    bc.valueAxis.valueStep = 20
    bc.valueAxis.labels.fontSize = 7
    bc.valueAxis.labels.fontName = 'Helvetica'
    bc.bars[0].fillColor = ACCENT_BLUE
    bc.bars[1].fillColor = GOLD
    bc.bars[0].strokeColor = DEEP_BLUE
    bc.bars[1].strokeColor = DARK_GOLD
    bc.bars[0].strokeWidth = 0.5
    bc.bars[1].strokeWidth = 0.5
    bc.barWidth = 12
    bc.groupSpacing = 15
    d.add(bc)

    # Legend
    d.add(Rect(340, 185, 8, 8, fillColor=ACCENT_BLUE, strokeColor=None))
    d.add(String(352, 186, "Perseus %", fontSize=7, fontName='Helvetica', fillColor=DARK_NAVY))
    d.add(Rect(340, 172, 8, 8, fillColor=GOLD, strokeColor=None))
    d.add(String(352, 173, "CONF+HIGH %", fontSize=7, fontName='Helvetica', fillColor=DARK_NAVY))

    d.add(String(100, dh - 12, "Validation Rates Across Selected Folios",
                fontSize=10, fontName='Helvetica-Bold', fillColor=DARK_NAVY))

    return d


# ══════════════════════════════════════════
# ASHMOLE 370 COMPARISON
# ══════════════════════════════════════════
def make_ashmole_comparison():
    dw, dh = 460, 200
    d = Drawing(dw, dh)
    d.add(Rect(0, 0, dw, dh, fillColor=PALE_BLUE, strokeColor=None))

    # Left: Ashmole 370
    d.add(Rect(15, 25, 195, 155, fillColor=white, strokeColor=MEDIUM_BLUE,
               strokeWidth=1, rx=5, ry=5))
    d.add(String(45, 162, "Ashmole 370 (~1424)", fontSize=9,
                fontName='Helvetica-Bold', fillColor=DEEP_BLUE))

    for text, y in [("Base: 24h Scale", 142), ("Disc 1: Zodiac (12x30 deg)", 125),
                    ("Disc 2: Lunar Age (0-29.5d)", 108), ("Disc 3: Astrological Aspects", 91),
                    ("Pivot: Sighting Hole", 74)]:
        d.add(Circle(30, y + 3, 3, fillColor=MEDIUM_BLUE, strokeColor=None))
        d.add(String(38, y, text, fontSize=7.5, fontName='Helvetica', fillColor=DARK_NAVY))

    # Right: f57v
    d.add(Rect(250, 25, 195, 155, fillColor=white, strokeColor=GOLD,
               strokeWidth=1, rx=5, ry=5))
    d.add(String(295, 162, "Folio f57v (MS 408)", fontSize=9,
                fontName='Helvetica-Bold', fillColor=DARK_GOLD))

    for text, y in [("L05: 24 glyphs, 75% arc", 142), ("L02: 54 logogram elements", 125),
                    ("L04: Exactly 29 words", 108), ("L03: 4x17 repeating pattern", 91),
                    ("Core: Sun + 4 figures", 74)]:
        d.add(Circle(265, y + 3, 3, fillColor=GOLD, strokeColor=None))
        d.add(String(273, y, text, fontSize=7.5, fontName='Helvetica', fillColor=DARK_NAVY))

    # Connecting arrows
    for y in [145, 128, 111, 94, 77]:
        d.add(Line(210, y, 250, y, strokeColor=WARM_GRAY, strokeWidth=0.8,
                   strokeDashArray=[4, 2]))
        d.add(Polygon([250, y, 245, y + 3, 245, y - 3],
                      fillColor=WARM_GRAY, strokeColor=WARM_GRAY))

    d.add(String(215, 50, "1:1", fontSize=14, fontName='Helvetica-Bold', fillColor=GREEN_SOFT))
    d.add(String(205, 37, "structural", fontSize=7, fontName='Helvetica', fillColor=GREEN_SOFT))
    d.add(String(203, 28, "isomorphism", fontSize=7, fontName='Helvetica', fillColor=GREEN_SOFT))

    d.add(String(95, dh - 12, "Structural Correspondence: Ashmole 370 vs. f57v",
                fontSize=10, fontName='Helvetica-Bold', fillColor=DARK_NAVY))

    return d


# ══════════════════════════════════════════
# THREE-LAYER CIPHER MODEL
# ══════════════════════════════════════════
def make_cipher_layers():
    dw, dh = 440, 170
    d = Drawing(dw, dh)
    d.add(Rect(0, 0, dw, dh, fillColor=white, strokeColor=None))

    layers = [
        (120, 200, "Layer 1: Logograms",       "~10%", GREEN_SOFT,  "r=recipe, m=misce, x=crux"),
        ( 80, 280, "Layer 2: Agglutinated",    "~55%", ACCENT_BLUE, "y+keedy = in + ciere"),
        ( 40, 340, "Layer 3: Nomenclator",     "~28%", PURPLE_SOFT, "aros = Aries (codebook)"),
    ]

    for i, (x, w, title, pct, color, example) in enumerate(layers):
        y = 35 + i * 42
        d.add(Rect(x, y, w, 35, fillColor=color, strokeColor=DARK_NAVY,
                   strokeWidth=0.8, rx=5, ry=5))
        d.add(String(x + 8, y + 22, title, fontSize=8.5, fontName='Helvetica-Bold',
                    fillColor=white))
        d.add(String(x + 8, y + 10, f"{pct} -- {example}", fontSize=7,
                    fontName='Helvetica', fillColor=HexColor("#e8e8e8")))
        d.add(String(x + w - 35, y + 22, pct, fontSize=9,
                    fontName='Helvetica-Bold', fillColor=white))

    # Phonetic long words bar
    d.add(Rect(230, 35, 100, 20, fillColor=ORANGE_SOFT, strokeColor=DARK_NAVY,
               strokeWidth=0.5, rx=3, ry=3))
    d.add(String(280, 40, "Phonetic long ~7%", fontSize=7,
                fontName='Helvetica-Bold', fillColor=white, textAnchor='middle'))

    d.add(String(100, dh - 12, "Three-Layer Cipher Model",
                fontSize=10, fontName='Helvetica-Bold', fillColor=DARK_NAVY))

    return d


from reportlab.lib.colors import HexColor
