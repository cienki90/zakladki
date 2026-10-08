"""Testy generatora PDF/DOCX (odczyt wygenerowanych plikow)."""

import fitz  # pymupdf
import pytest
from docx import Document

from zakladki_app.generator import generate


def _page_text_lines(page):
    return [ln.strip() for ln in page.get_text().splitlines() if ln.strip()]


def test_generate_pdf_pages_and_content(sample_xlsx, tmp_path):
    out = tmp_path / "out.pdf"
    generate(sample_xlsx, str(out), "pdf")

    doc = fitz.open(str(out))
    try:
        assert doc.page_count == 14

        # Rozmiar strony dokladnie 297 x 684 pkt.
        rect = doc[0].rect
        assert round(rect.width) == 297
        assert round(rect.height) == 684

        page1 = _page_text_lines(doc[0])
        assert "ST 05-0112" in page1
        assert "Kiczki Pierwsze" in page1
        assert "71/RE-5/KŚ/2026" in page1

        # Strona z polskimi znakami diakrytycznymi.
        all_text = "\n".join(doc[i].get_text() for i in range(doc.page_count))
        assert "Woźbin" in all_text
        assert "Jędrzejów Nowy" in all_text
        assert "Leonów" in all_text
    finally:
        doc.close()


def test_generate_pdf_each_page_pattern(sample_xlsx, tmp_path):
    out = tmp_path / "out.pdf"
    generate(sample_xlsx, str(out), "pdf")

    doc = fitz.open(str(out))
    try:
        for i in range(doc.page_count):
            lines = _page_text_lines(doc[i])
            assert len(lines) == 3
            assert lines[0].startswith("ST ")
    finally:
        doc.close()


def test_generate_docx_content(sample_xlsx, tmp_path):
    out = tmp_path / "out.docx"
    generate(sample_xlsx, str(out), "docx")

    document = Document(str(out))
    texts = [p.text for p in document.paragraphs]
    joined = "\n".join(texts)

    assert "ST 05-0112" in texts
    assert "Kiczki Pierwsze" in texts
    assert "71/RE-5/KŚ/2026" in texts
    assert "Woźbin" in joined
    assert "Jędrzejów Nowy" in joined

    # 14 wpisow -> 13 podzialow stron (nie po ostatnim).
    xml = document.element.xml
    page_breaks = xml.count('w:type="page"')
    assert page_breaks == 13


def _page1_line_tops(path):
    """Zwraca liste gornych wspolrzednych (bbox top) linii tekstu na 1. stronie."""
    doc = fitz.open(str(path))
    try:
        tops = []
        for block in doc[0].get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                for span in line["spans"]:
                    if span["text"].strip():
                        tops.append(round(span["bbox"][1], 2))
        return tops
    finally:
        doc.close()


def test_generate_pdf_matches_sample_vertical_layout(sample_xlsx, sample_pdf, tmp_path):
    """Pozycja pionowa trzech linii musi odpowiadac wzorcowi zakladki.pdf.

    Chroni przed regresja z offsetem pionowym (tekst "wiszacy" przy gornej
    krawedzi), ktora wystepowala, gdy TOP_OFFSET nie uwzglednial nadlinii fontu.
    """
    out = tmp_path / "out.pdf"
    generate(sample_xlsx, str(out), "pdf")

    generated_tops = _page1_line_tops(out)
    sample_tops = _page1_line_tops(sample_pdf)

    assert len(generated_tops) == 3
    assert len(sample_tops) == 3

    # Wzorzec: ~14.2 / 30.0 / 45.9 pkt od gory. Dopuszczamy ~1.5 pkt roznicy.
    for got, expected in zip(generated_tops, sample_tops):
        assert abs(got - expected) <= 1.5, (
            "Linia na {} pkt odbiega od wzorca {} pkt".format(got, expected)
        )


def test_generate_unsupported_format(sample_xlsx, tmp_path):
    with pytest.raises(ValueError):
        generate(sample_xlsx, str(tmp_path / "x.txt"), "txt")
