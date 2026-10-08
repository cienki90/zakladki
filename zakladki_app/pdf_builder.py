"""Budowanie pliku PDF z zakladkami (reportlab).

Kazdy wpis to jedna strona o rozmiarze dokladnie 297 x 684 pkt (portret),
z trzema pogrubionymi, wysrodkowanymi liniami przy gornej krawedzi.
Uzywamy wbudowanej w reportlab czcionki Unicode (DejaVuSans-Bold),
aby polskie znaki (ł, ś, ż, ę, ą, ó) renderowaly sie poprawnie.
"""

import glob
import os
from typing import List

import reportlab
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from .excel_reader import Entry

# Rozmiar strony dokladnie jak we wzorcu zakladki.pdf.
PAGE_WIDTH = 297.0
PAGE_HEIGHT = 684.0

FONT_SIZE = 12.0
LINE_LEADING = 15.8
# Odleglosc bazy pierwszej linii od gornej krawedzi (~5 mm = ~14 pkt + wysokosc fontu).
TOP_OFFSET = 14.0

_FONT_NAME = "DejaVuSans-Bold"
_font_registered = False


def _font_candidates():
    """Zwraca liste potencjalnych sciezek do pogrubionej czcionki Unicode.

    Priorytet ma czcionka dolaczona do pakietu (zakladki_app/fonts), dzieki czemu
    polskie znaki renderuja sie tak samo na kazdym systemie (w tym Windows),
    niezaleznie od czcionek zainstalowanych w systemie.
    """
    pkg_fonts = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
    candidates = [
        os.path.join(pkg_fonts, "DejaVuSans-Bold.ttf"),
    ]
    # Czcionki dolaczone do reportlab (starsze wersje maja Vera, bez pelnej polszczyzny).
    rl_fonts = os.path.join(os.path.dirname(reportlab.__file__), "fonts")
    candidates += glob.glob(os.path.join(rl_fonts, "*DejaVuSans*Bold*.ttf"))
    return candidates


def _register_font() -> str:
    """Rejestruje pogrubiona czcionke Unicode z pelnym zestawem polskich znakow.

    Returns:
        Nazwa zarejestrowanej czcionki, lub 'Helvetica-Bold' jako awaryjna.
    """
    global _font_registered
    if _font_registered:
        return _FONT_NAME

    for ttf in _font_candidates():
        if ttf and os.path.exists(ttf):
            pdfmetrics.registerFont(TTFont(_FONT_NAME, ttf))
            # Rejestrujemy rodzine, aby bold/normal wskazywaly ta sama czcionke.
            registerFontFamily(
                _FONT_NAME,
                normal=_FONT_NAME,
                bold=_FONT_NAME,
                italic=_FONT_NAME,
                boldItalic=_FONT_NAME,
            )
            _font_registered = True
            return _FONT_NAME

    # Ostatecznie wbudowany Helvetica-Bold (bez pelnych polskich znakow).
    return "Helvetica-Bold"


def build_pdf(entries: List[Entry], out_path) -> str:
    """Tworzy wielostronicowy PDF - jedna strona na wpis.

    Args:
        entries: lista wpisow Entry.
        out_path: sciezka docelowa pliku .pdf.

    Returns:
        Sciezka zapisanego pliku.
    """
    font_name = _register_font()

    c = canvas.Canvas(str(out_path), pagesize=(PAGE_WIDTH, PAGE_HEIGHT))
    center_x = PAGE_WIDTH / 2.0

    for entry in entries:
        lines = [
            "ST " + entry.trafo,
            entry.miejscowosc,
            entry.wt,
        ]
        c.setFont(font_name, FONT_SIZE)
        for i, text in enumerate(lines):
            y = PAGE_HEIGHT - TOP_OFFSET - (i * LINE_LEADING)
            c.drawCentredString(center_x, y, text)
        c.showPage()

    c.save()
    return str(out_path)
