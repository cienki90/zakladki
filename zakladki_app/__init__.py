"""zakladki_app - core engine for generating 'zakladki' (label cards) from an Excel sheet.

GUI-free package: reading Excel and building PDF/Word documents live here so they can
be unit-tested headlessly. The Tkinter GUI (if any) imports from this package.
"""

from .generator import generate
from .excel_reader import read_entries, Entry

__all__ = ["generate", "read_entries", "Entry"]
