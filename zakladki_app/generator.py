"""Cienka warstwa orkiestracji: Excel -> PDF lub Word.

Jedyny punkt wejscia uzywany przez GUI (FEAT-002).
"""

from typing import List

from .excel_reader import Entry, read_entries

SUPPORTED_FORMATS = ("pdf", "docx")


def generate(excel_path, out_path, fmt: str) -> str:
    """Generuje plik wyjsciowy z pliku Excel.

    Args:
        excel_path: sciezka do pliku .xlsx ze zestawieniem.
        out_path: sciezka docelowa pliku wynikowego.
        fmt: format wyjsciowy, 'pdf' lub 'docx'.

    Returns:
        Sciezka zapisanego pliku wynikowego.

    Raises:
        ValueError: gdy format jest nieobslugiwany lub brak danych/naglowkow.
    """
    normalized = (fmt or "").strip().lower().lstrip(".")
    if normalized not in SUPPORTED_FORMATS:
        raise ValueError(
            "Nieobslugiwany format: {!r}. Dozwolone: 'pdf', 'docx'.".format(fmt)
        )

    entries: List[Entry] = read_entries(excel_path)
    if not entries:
        raise ValueError("Plik Excel nie zawiera zadnych wierszy danych.")

    if normalized == "pdf":
        from .pdf_builder import build_pdf

        return build_pdf(entries, out_path)

    from .word_builder import build_docx

    return build_docx(entries, out_path)
