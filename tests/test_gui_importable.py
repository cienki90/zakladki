"""Testy modulu GUI.

Testy importu sa pomijane, gdy tkinter jest niedostepny (np. sandbox/CI bez
ekranu). Logika niezalezna od tkinter (wybor formatu, nazwa pliku) jest
testowana zawsze - bez uruchamiania okna.
"""

import pytest

from zakladki_app import gui


def test_format_meta_pdf():
    meta = gui.format_meta("pdf")
    assert meta["fmt"] == "pdf"
    assert meta["extension"] == ".pdf"


def test_format_meta_docx_is_case_insensitive():
    meta = gui.format_meta("DOCX")
    assert meta["fmt"] == "docx"
    assert meta["extension"] == ".docx"


def test_format_meta_rejects_unknown():
    with pytest.raises(ValueError):
        gui.format_meta("txt")


def test_default_output_name_uses_excel_basename():
    name = gui.default_output_name("/sciezka/zestawienie.xlsx", "pdf")
    assert name == "zestawienie.pdf"
    name2 = gui.default_output_name("C:/dane/wykaz.xlsx", "docx")
    assert name2 == "wykaz.docx"


def test_run_generation_dispatches_fmt(monkeypatch):
    """run_generation musi wywolac generate z wlasciwym formatem."""
    calls = {}

    def fake_generate(excel_path, out_path, fmt):
        calls["args"] = (excel_path, out_path, fmt)
        return out_path

    monkeypatch.setattr(gui, "generate", fake_generate)

    result = gui.run_generation("in.xlsx", "out.docx", "docx")
    assert result == "out.docx"
    assert calls["args"] == ("in.xlsx", "out.docx", "docx")

    gui.run_generation("in.xlsx", "out.pdf", "PDF")
    assert calls["args"] == ("in.xlsx", "out.pdf", "pdf")


def test_gui_module_importable_when_tkinter_available():
    """Sprawdza importowalnosc GUI tam, gdzie tkinter istnieje."""
    pytest.importorskip("tkinter")
    import importlib

    import zakladki_app.gui as gui_mod

    importlib.reload(gui_mod)
    assert hasattr(gui_mod, "main")
    assert callable(gui_mod.main)
