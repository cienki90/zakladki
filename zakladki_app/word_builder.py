"""Budowanie pliku Word (.docx) z zakladkami (python-docx).

Rozmiar strony dopasowany do wzorca (104.78 x 241.3 mm, portret).
Kazdy wpis to trzy wysrodkowane, pogrubione akapity (12 pkt) przy gornej krawedzi,
oddzielone podzialem strony. Domyslna czcionka Calibri obsluguje polskie znaki.
"""

from typing import List

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.shared import Mm, Pt

from .excel_reader import Entry

# Rozmiar strony jak we wzorcu (297 x 684 pkt).
PAGE_WIDTH_MM = 104.78
PAGE_HEIGHT_MM = 241.3

FONT_NAME = "Calibri"
FONT_SIZE_PT = 12
# Maly gorny margines, aby tekst byl przy gornej krawedzi.
TOP_MARGIN_MM = 4.0
SIDE_MARGIN_MM = 4.0


def _add_entry(document: Document, entry: Entry) -> None:
    """Dodaje trzy wysrodkowane, pogrubione akapity dla jednego wpisu."""
    lines = ["ST " + entry.trafo, entry.miejscowosc, entry.wt]
    for text in lines:
        p = document.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pf = p.paragraph_format
        pf.space_before = Pt(0)
        pf.space_after = Pt(0)
        run = p.add_run(text)
        run.bold = True
        run.font.name = FONT_NAME
        run.font.size = Pt(FONT_SIZE_PT)


def build_docx(entries: List[Entry], out_path) -> str:
    """Tworzy dokument Word - jedna sekcja/strona na wpis.

    Args:
        entries: lista wpisow Entry.
        out_path: sciezka docelowa pliku .docx.

    Returns:
        Sciezka zapisanego pliku.
    """
    document = Document()

    section = document.sections[0]
    section.orientation = WD_ORIENT.PORTRAIT
    section.page_width = Mm(PAGE_WIDTH_MM)
    section.page_height = Mm(PAGE_HEIGHT_MM)
    section.top_margin = Mm(TOP_MARGIN_MM)
    section.bottom_margin = Mm(TOP_MARGIN_MM)
    section.left_margin = Mm(SIDE_MARGIN_MM)
    section.right_margin = Mm(SIDE_MARGIN_MM)

    # Domyslna czcionka dokumentu.
    normal = document.styles["Normal"]
    normal.font.name = FONT_NAME
    normal.font.size = Pt(FONT_SIZE_PT)

    for idx, entry in enumerate(entries):
        if idx > 0:
            # Podzial strony przed kolejnym wpisem (nie po ostatnim).
            break_p = document.add_paragraph()
            break_p.add_run().add_break(WD_BREAK.PAGE)
        _add_entry(document, entry)

    document.save(str(out_path))
    return str(out_path)
