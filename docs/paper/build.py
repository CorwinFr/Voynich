#!/usr/bin/env python3
"""
Build the paper PDF.
Usage: python build.py [output_path]
"""
import sys, os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from config import GOLD, WARM_GRAY, BORDER, MARGIN_L, MARGIN_R, W, H
from content import build_story
from appendix_catalogue import build_folio_appendix
from reportlab.platypus import SimpleDocTemplate


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for i, state in enumerate(self._saved_page_states):
            self.__dict__.update(state)
            self._draw_page_extras(i + 1, num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def _draw_page_extras(self, page_num, total):
        self.saveState()
        # Gold footer line
        self.setStrokeColor(GOLD)
        self.setLineWidth(0.5)
        self.line(MARGIN_L, 14 * mm, W - MARGIN_R, 14 * mm)
        # Page number
        self.setFont('Helvetica', 8)
        self.setFillColor(WARM_GRAY)
        self.drawCentredString(W / 2, 10 * mm, f"{page_num}")
        # Header (skip page 1)
        if page_num > 1:
            self.setStrokeColor(BORDER)
            self.setLineWidth(0.3)
            self.line(MARGIN_L, H - 16 * mm, W - MARGIN_R, H - 16 * mm)
            self.setFont('Helvetica', 7)
            self.setFillColor(WARM_GRAY)
            self.drawString(MARGIN_L, H - 14.5 * mm, "Clement, G. (2026)")
            self.drawRightString(W - MARGIN_R, H - 14.5 * mm,
                "Toward a Phonetic Decryption of the Voynich Manuscript")
        self.restoreState()


def main():
    output = sys.argv[1] if len(sys.argv) > 1 else "Voynich_Decryption_Clement_Claude_2026.pdf"

    doc = SimpleDocTemplate(output, pagesize=A4,
        leftMargin=MARGIN_L, rightMargin=MARGIN_R,
        topMargin=22 * mm, bottomMargin=22 * mm)

    story = build_story()
    story.extend(build_folio_appendix())
    doc.build(story, canvasmaker=NumberedCanvas)

    size_kb = os.path.getsize(output) / 1024
    print(f"PDF generated: {output}")
    print(f"Size: {size_kb:.1f} KB")


if __name__ == "__main__":
    main()
