"""Budowanie pliku PDF z zakladkami (reportlab).

Kazdy wpis to jedna strona o rozmiarze dokladnie 297 x 684 pkt (portret),
z trzema pogrubionymi, wysrodkowanymi liniami przy gornej krawedzi.
Uzywamy wbudowanej w reportlab czcionki Unicode (DejaVuSans-Bold),
aby polskie znaki (ł, ś, ż, ę, ą, ó) renderowaly sie poprawnie.
"""

import glob
import os
import warnings
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
# Odleglosc GORY pierwszej linii tekstu od gornej krawedzi strony (jak we wzorcu
# zakladki.pdf: gorna krawedz pierwszej linii ~14.2 pkt od gory). Baza (linia
# bazowa) pierwszej linii jest nizej o wysokosc nadlinii (ascent) czcionki,
# dlatego dodajemy ascent podczas obliczania pozycji bazowej - inaczej tekst
# "wisialby" przy samej krawedzi (byl o ~ascent za wysoko wzgledem wzorca).
TOP_OFFSET = 14.2

_FONT_NAME = "DejaVuSans-Bold"
_FALLBACK_FONT = "Helvetica-Bold"
_font_registered = False

# Komunikat ostrzegawczy, gdy nie uda sie zarejestrowac czcionki Unicode i
# aplikacja musi uzyc czcionki awaryjnej bez pelnego zestawu polskich znakow.
FONT_FALLBACK_WARNING = (
    "Nie znaleziono czcionki Unicode (DejaVuSans-Bold) - uzyto czcionki awaryjnej "
    "'{fallback}'. Polskie znaki ( a, e, s, z, o...) moga wyswietlic sie "
    "nieprawidlowo. Upewnij sie, ze plik "
    "zakladki_app/fonts/DejaVuSans-Bold.ttf jest dostepny."
).format(fallback=_FALLBACK_FONT)


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
            # Rejestrujemy rodzine: uzywamy tej samej (pogrubionej) czcionki dla
            # wariantu normalnego i pogrubionego. Nie deklarujemy wariantow
            # kursywy, bo nie dysponujemy osobna czcionka italic/boldItalic, a
            # aplikacja i tak renderuje wylacznie tekst pogrubiony (bez kursywy).
            registerFontFamily(
                _FONT_NAME,
                normal=_FONT_NAME,
                bold=_FONT_NAME,
            )
            _font_registered = True
            return _FONT_NAME

    # Ostatecznie wbudowany Helvetica-Bold (bez pelnych polskich znakow).
    # Sygnalizujemy to glosno (ostrzezenie), aby problem nie przeszedl
    # niezauwazony - GUI przechwytuje to ostrzezenie i pokazuje je uzytkownikowi.
    warnings.warn(FONT_FALLBACK_WARNING, RuntimeWarning, stacklevel=2)
    return _FALLBACK_FONT


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

    # Linia bazowa pierwszego wiersza. TOP_OFFSET to odleglosc GORY tekstu od
    # gornej krawedzi; linia bazowa jest nizej o wysokosc nadlinii (ascent)
    # czcionki, dlatego ja dodajemy. Dzieki temu polozenie tekstu odpowiada
    # wzorcowi zakladki.pdf (gora pierwszej linii ~14.2 pkt od gory strony),
    # zamiast "wisiec" przy samej krawedzi.
    ascent = pdfmetrics.getAscentDescent(font_name, FONT_SIZE)[0]
    first_baseline = PAGE_HEIGHT - TOP_OFFSET - ascent

    for entry in entries:
        lines = [
            "ST " + entry.trafo,
            entry.miejscowosc,
            entry.wt,
        ]
        c.setFont(font_name, FONT_SIZE)
        for i, text in enumerate(lines):
            y = first_baseline - (i * LINE_LEADING)
            c.drawCentredString(center_x, y, text)
        c.showPage()

    c.save()
    return str(out_path)
