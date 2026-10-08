"""Przyjazny dla uzytkownika interfejs graficzny (Tkinter) generatora zakladek.

Program pozwala wskazac plik Excel, PYTA o format (Word lub PDF),
pozwala wybrac miejsce zapisu i tworzy gotowy plik.

WAZNE: tkinter jest importowany dopiero w momencie uruchomienia GUI
(wewnatrz funkcji), dzieki czemu `import zakladki_app` oraz testy
dzialaja takze w srodowiskach bez tkinter (np. serwer CI bez ekranu).
"""

import os

from .generator import generate

# Tytul okna oraz etykiety przyciskow (po polsku dla uzytkownika).
APP_TITLE = "Generator zakładek"

# Mapowanie wyboru formatu -> (fmt dla generatora, rozszerzenie pliku, opis).
FORMAT_PDF = "pdf"
FORMAT_DOCX = "docx"

_FORMAT_META = {
    FORMAT_PDF: {
        "fmt": "pdf",
        "extension": ".pdf",
        "label": "PDF (*.pdf)",
    },
    FORMAT_DOCX: {
        "fmt": "docx",
        "extension": ".docx",
        "label": "Word (*.docx)",
    },
}


def format_meta(choice):
    """Zwraca metadane dla wybranego formatu.

    Logika wydzielona z GUI, aby mozna ja bylo testowac bez tkinter.

    Args:
        choice: 'pdf' lub 'docx'.

    Returns:
        Slownik z kluczami: 'fmt', 'extension', 'label'.

    Raises:
        ValueError: gdy format jest nieznany.
    """
    key = (choice or "").strip().lower().lstrip(".")
    if key not in _FORMAT_META:
        raise ValueError(
            "Nieznany format: {!r}. Dozwolone: 'pdf', 'docx'.".format(choice)
        )
    return dict(_FORMAT_META[key])


def default_output_name(excel_path, choice):
    """Proponuje nazwe pliku wyjsciowego na podstawie pliku Excel i formatu.

    Args:
        excel_path: sciezka do wskazanego pliku Excel.
        choice: 'pdf' lub 'docx'.

    Returns:
        Proponowana nazwa pliku (bez katalogu), np. 'zestawienie.pdf'.
    """
    meta = format_meta(choice)
    base = os.path.splitext(os.path.basename(str(excel_path)))[0] or "zakladki"
    return base + meta["extension"]


def run_generation(excel_path, out_path, choice):
    """Uruchamia generowanie dla wybranego formatu.

    Cienki, testowalny bez GUI wrapper na generate().

    Args:
        excel_path: sciezka do pliku Excel.
        out_path: sciezka docelowa.
        choice: 'pdf' lub 'docx'.

    Returns:
        Sciezka zapisanego pliku wynikowego.
    """
    meta = format_meta(choice)
    return generate(excel_path, out_path, meta["fmt"])


def _friendly_error(exc):
    """Buduje przyjazny, polski komunikat o bledzie dla uzytkownika."""
    if isinstance(exc, ValueError):
        # Bledy walidacji (brak kolumn, brak danych) juz sa po polsku.
        return str(exc)
    if isinstance(exc, PermissionError):
        return (
            "Nie udalo sie zapisac pliku. Upewnij sie, ze plik wynikowy "
            "nie jest otwarty w innym programie (np. w Wordzie), i sprobuj ponownie."
        )
    if isinstance(exc, FileNotFoundError):
        return (
            "Nie znaleziono pliku. Sprawdz, czy wskazany plik Excel istnieje "
            "i nie zostal przeniesiony."
        )
    return "Wystapil nieoczekiwany blad:\n{}".format(exc)


def main():
    """Uruchamia okno aplikacji. Importuje tkinter dopiero tutaj."""
    import tkinter as tk
    from tkinter import filedialog, messagebox

    root = tk.Tk()
    root.title(APP_TITLE)
    root.geometry("460x260")
    root.minsize(420, 240)

    # Przechowuje sciezke wybranego pliku Excel.
    state = {"excel_path": None}

    container = tk.Frame(root, padx=20, pady=20)
    container.pack(fill="both", expand=True)

    header = tk.Label(
        container,
        text="Generator zakładek",
        font=("Arial", 16, "bold"),
    )
    header.pack(pady=(0, 4))

    hint = tk.Label(
        container,
        text=(
            "1) Wskaż plik Excel  2) Wybierz format (Word lub PDF)  "
            "3) Zapisz gotowy plik"
        ),
        wraplength=400,
        justify="center",
    )
    hint.pack(pady=(0, 12))

    selected_label = tk.Label(
        container,
        text="Nie wybrano pliku Excel.",
        fg="#555555",
        wraplength=400,
        justify="center",
    )
    selected_label.pack(pady=(0, 12))

    # Ramka z przyciskami wyboru formatu (poczatkowo nieaktywne).
    format_frame = tk.Frame(container)
    format_frame.pack(pady=(0, 6))

    prompt_label = tk.Label(
        format_frame,
        text="W jakim formacie zapisać zakładki?",
        font=("Arial", 10, "bold"),
    )
    prompt_label.grid(row=0, column=0, columnspan=2, pady=(0, 6))

    def save_as(choice):
        """Pyta o miejsce zapisu i generuje plik w wybranym formacie."""
        excel_path = state["excel_path"]
        if not excel_path:
            messagebox.showwarning(
                APP_TITLE, "Najpierw wybierz plik Excel.", parent=root
            )
            return

        meta = format_meta(choice)
        out_path = filedialog.asksaveasfilename(
            parent=root,
            title="Zapisz jako",
            defaultextension=meta["extension"],
            initialfile=default_output_name(excel_path, choice),
            filetypes=[(meta["label"], "*" + meta["extension"]),
                       ("Wszystkie pliki", "*.*")],
        )
        if not out_path:
            return  # Uzytkownik anulowal.

        try:
            saved = run_generation(excel_path, out_path, choice)
        except Exception as exc:  # noqa: BLE001 - pokazujemy przyjazny komunikat
            messagebox.showerror(APP_TITLE, _friendly_error(exc), parent=root)
            return

        messagebox.showinfo(
            APP_TITLE,
            "Gotowe! Plik zapisano w:\n{}".format(saved),
            parent=root,
        )

    btn_word = tk.Button(
        format_frame,
        text="Word (.docx)",
        width=16,
        state="disabled",
        command=lambda: save_as(FORMAT_DOCX),
    )
    btn_word.grid(row=1, column=0, padx=6)

    btn_pdf = tk.Button(
        format_frame,
        text="PDF",
        width=16,
        state="disabled",
        command=lambda: save_as(FORMAT_PDF),
    )
    btn_pdf.grid(row=1, column=1, padx=6)

    def choose_excel():
        """Otwiera okno wyboru pliku Excel i aktywuje przyciski formatu."""
        path = filedialog.askopenfilename(
            parent=root,
            title="Wybierz plik Excel",
            filetypes=[("Pliki Excel", "*.xlsx *.xls"),
                       ("Wszystkie pliki", "*.*")],
        )
        if not path:
            return
        state["excel_path"] = path
        selected_label.config(
            text="Wybrany plik:\n{}".format(os.path.basename(path)),
            fg="#1a7f1a",
        )
        btn_word.config(state="normal")
        btn_pdf.config(state="normal")

    choose_btn = tk.Button(
        container,
        text="Wybierz plik Excel...",
        font=("Arial", 11),
        command=choose_excel,
    )
    choose_btn.pack(before=selected_label, pady=(0, 10))

    root.mainloop()


if __name__ == "__main__":
    main()
