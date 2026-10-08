# Generator zakładek

Prosty, przyjazny program dla systemu **Windows**, który na podstawie pliku
**Excel** tworzy gotowe do druku **zakładki** w formacie **Word (.docx)** lub
**PDF**. Program sam **pyta**, w jakim formacie chcesz zapisać plik.

Przykłady znajdują się w repozytorium:

- `zestawienie zakladki.xlsx` – przykładowy plik **wejściowy** (Excel),
- `zakladki.pdf` – przykładowy plik **wyjściowy** (tak wygląda efekt).

## Jak to działa

1. Wskazujesz plik Excel z zestawieniem.
2. Program pyta, czy zapisać wynik jako **Word** czy **PDF**.
3. Wybierasz, gdzie zapisać plik.
4. Program tworzy dokument – każda zakładka to osobna strona.

### Co musi zawierać plik Excel

W **pierwszym wierszu** arkusza muszą znaleźć się nagłówki kolumn o nazwach
(wielkość liter nie ma znaczenia, kolejność dowolna):

| Nagłówek w Excelu | Co oznacza                         | Jak trafia na zakładkę              |
|-------------------|------------------------------------|-------------------------------------|
| `trafo`           | numer transformatora, np. 05-0112  | pierwsza linia: `ST ` + wartość (np. `ST 05-0112`) |
| `miejscowosc`     | nazwa miejscowości                 | druga linia                         |
| `wt`              | numer / oznaczenie, np. 71/RE-5/KŚ/2026 | trzecia linia                   |

Uwaga: dopuszczalne są puste kolumny pomiędzy nagłówkami – program odnajduje
kolumny po **nazwie**, a nie po pozycji. Polskie znaki (ą, ę, ś, ź, ...) są
w pełni obsługiwane.

Każdy wiersz danych tworzy jedną zakładkę o trzech wyśrodkowanych, pogrubionych
liniach:

```
ST 05-0112
Kiczki Pierwsze
71/RE-5/KŚ/2026
```

## Szybki start w Windows (dla osób nietechnicznych)

1. **Zainstaluj Pythona.** Wejdź na [python.org](https://www.python.org/downloads/),
   pobierz instalator i podczas instalacji **zaznacz opcję „Add Python to PATH”**.
   (Biblioteka `tkinter`, potrzebna do okna programu, instaluje się razem
   z Pythonem z python.org – nie trzeba jej dodatkowo instalować.)
2. **Pobierz ten program** (np. przyciskiem „Code → Download ZIP” na GitHubie)
   i rozpakuj do wybranego folderu.
3. **Zainstaluj wymagane biblioteki.** W folderze z programem otwórz wiersz
   poleceń (w pasku adresu Eksploratora wpisz `cmd` i naciśnij Enter), a następnie
   wpisz:

   ```
   pip install -r requirements.txt
   ```

4. **Uruchom program:**

   ```
   python run.py
   ```

   Jeśli pliki `.py` są skojarzone z Pythonem, możesz też po prostu
   **kliknąć dwukrotnie** plik `run.py`.

Otworzy się okno „Generator zakładek”. Kliknij **„Wybierz plik Excel...”**,
następnie wybierz **Word (.docx)** albo **PDF**, wskaż miejsce zapisu – gotowe.

## Budowanie samodzielnego pliku .exe (Windows)

Aby rozdać program osobom bez zainstalowanego Pythona, możesz zbudować
pojedynczy plik wykonywalny `.exe` za pomocą **PyInstaller**.

> **Uwaga:** plik `.exe` dla Windows da się zbudować **tylko na Windows**.
> Nie można go utworzyć na Linux/macOS.

W folderze z programem (w Windows):

```
pip install pyinstaller
pyinstaller --noconfirm zakladki.spec
```

Albo bez pliku `.spec`:

```
pyinstaller --noconfirm --windowed --onefile --name Zakladki ^
    --add-data "zakladki_app/fonts/DejaVuSans-Bold.ttf;zakladki_app/fonts" run.py
```

Gotowy plik `Zakladki.exe` pojawi się w folderze `dist`. Dołączona czcionka
`DejaVuSans-Bold.ttf` jest **obowiązkowa** – zapewnia poprawne wyświetlanie
polskich znaków w plikach PDF.

## Dla programistów

- Kod silnika (odczyt Excela, budowanie PDF/Word) znajduje się w pakiecie
  `zakladki_app/` i jest **niezależny od GUI**, dzięki czemu można go testować
  bez ekranu.
- Testy uruchamiasz poleceniem:

  ```
  pip install -r requirements-dev.txt
  python -m pytest -q
  ```

  Test GUI jest automatycznie pomijany, gdy `tkinter` nie jest dostępny.
