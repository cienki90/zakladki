"""Testy odczytu pliku Excel."""

import openpyxl
import pytest

from zakladki_app.excel_reader import read_entries


def test_read_entries_count(sample_xlsx):
    entries = read_entries(sample_xlsx)
    assert len(entries) == 14


def test_read_entries_first_row(sample_xlsx):
    entries = read_entries(sample_xlsx)
    first = entries[0]
    assert first.trafo == "05-0112"
    assert first.miejscowosc == "Kiczki Pierwsze"
    assert first.wt == "71/RE-5/KŚ/2026"


def test_read_entries_polish_diacritics(sample_xlsx):
    entries = read_entries(sample_xlsx)
    by_trafo = {e.trafo: e for e in entries}
    assert "05-0885" in by_trafo
    assert by_trafo["05-0885"].miejscowosc == "Woźbin"


def test_read_entries_all_trafo_values(sample_xlsx):
    entries = read_entries(sample_xlsx)
    expected = [
        "05-0112", "05-0115", "05-0181", "05-0191", "05-0195", "05-0346",
        "05-0355", "05-0398", "05-0739", "05-0885", "05-0917", "05-0918",
        "05-1067", "05-1069",
    ]
    assert [e.trafo for e in entries] == expected


def test_read_entries_wt_constant(sample_xlsx):
    entries = read_entries(sample_xlsx)
    assert all(e.wt == "71/RE-5/KŚ/2026" for e in entries)


def test_missing_trafo_header_raises(tmp_path):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Arkusz1"
    ws.append(["Plik", "miejscowosc", None, "wt"])
    ws.append([112, "Kiczki Pierwsze", None, "71/RE-5/KŚ/2026"])
    path = tmp_path / "broken.xlsx"
    wb.save(str(path))

    with pytest.raises(ValueError):
        read_entries(str(path))


def test_header_located_by_name_not_index(tmp_path):
    """Kolumny lokalizowane po nazwie, nie po indeksie (pusta kolumna D)."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Arkusz1"
    ws.append(["Plik", "trafo", "miejscowosc", None, "wt"])
    ws.append([112, "05-0112", "Woźbin", None, "71/RE-5/KŚ/2026"])
    path = tmp_path / "ok.xlsx"
    wb.save(str(path))

    entries = read_entries(str(path))
    assert len(entries) == 1
    assert entries[0].trafo == "05-0112"
    assert entries[0].miejscowosc == "Woźbin"
    assert entries[0].wt == "71/RE-5/KŚ/2026"
