---
name: zestawienie-pdf
description: Składa arkusze i wizualizacje w jeden PDF do wydruku lub wysłania (A3 poziomo, strona tytułowa, rzuty, elewacje, rendery z podpisami). Używaj, gdy użytkownik mówi „zestawienie”, „PDF do wydruku”, „pakiet dla inwestora”, „złóż w jeden plik”, „A3”.
---

# Zestawienie PDF

Python z `~/.architekt/config.json` (klucz `python`). Biblioteki są już w środowisku: matplotlib (strony), PyMuPDF (`import pymupdf`, łączenie PDF-ów).

## Kroki

1. Ustal z użytkownikiem zawartość i kolejność (domyślnie: strona tytułowa → rzuty od najniższej kondygnacji → przekroje → elewacje → wizualizacje) i format (domyślnie A3 poziomo).
2. Napisz `tools/zestawienie.py`:
   - strona tytułowa (matplotlib, A3 = 16,54 × 11,69 cala): tytuł, adres, data, spis zawartości,
   - arkusze DXF: dołącz gotowe `rysunki/<arkusz>.pdf` (już A3) przez `pymupdf` — nie rasteryzuj ich,
   - rendery PNG: strona A3 z obrazem dopasowanym do strony i podpisem (ujęcie, wariant, data),
   - łączenie: `pymupdf.open()` + `insert_pdf()`, zapis do `<nazwa>_<data>.pdf` w głównym folderze projektu.
3. Sprawdź: liczba stron, rozmiar pliku (do maila do ok. 20 MB — w razie potrzeby zmniejsz rendery do 2000 px i JPEG 85%), obejrzyj pierwszą stronę i jedną z renderem w małej rozdzielczości.
4. Podaj użytkownikowi pełną ścieżkę pliku. `HANDOFF.md` + `PROGRESS.md`.
