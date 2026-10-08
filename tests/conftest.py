"""Wspolne sciezki/narzedzia dla testow."""

import os

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE_XLSX = os.path.join(REPO_ROOT, "zestawienie zakladki.xlsx")


@pytest.fixture
def sample_xlsx():
    """Sciezka do wzorcowego pliku Excel w repo."""
    assert os.path.exists(SAMPLE_XLSX), "Brak pliku wzorcowego: " + SAMPLE_XLSX
    return SAMPLE_XLSX
