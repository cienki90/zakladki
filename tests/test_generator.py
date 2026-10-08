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


def test_generate_unsupported_format(sample_xlsx, tmp_path):
    with pytest.raises(ValueError):
        generate(sample_xlsx, str(tmp_path / "x.txt"), "txt")
