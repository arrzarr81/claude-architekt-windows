---
name: spis-arkuszy
description: Przegląda skany dokumentacji (PDF, JPG ze zdjęć teczek urzędowych) i robi spis arkuszy z numerem strony, tytułem, skalą i czytelnością. Używaj, gdy użytkownik mówi „spis arkuszy”, „co jest w teczce”, „przejrzyj skany”, „znajdź rzut / przekrój / elewację”, albo przed pierwszym przerysowaniem w nowym projekcie. / EN — Reviews documentation scans (PDF, JPG photos of permit files) and lists the sheets with page number, title, scale and legibility. Use when the user says “sheet list”, “what is in the file”, “go through the scans”, “find the plan / section / elevation”, or before the first tracing in a new project.
---

# Spis arkuszy ze skanów

Cel: tabela `spis_arkuszy.md`, z której później wybiera się strony do przerysowania. Nic jeszcze nie przerysowujesz.

Python bierz z `~/.architekt/config.json` (klucz `python`; Windows: `%USERPROFILE%\.architekt\config.json`). Skrypt `strony_pdf.py` leży w folderze `scripts/` tego skilla.

## Kroki

1. Lista plików w `skany/` (lub w folderze wskazanym przez użytkownika): nazwa, typ, rozmiar. Dla każdego PDF: `"<python>" "<skill>/scripts/strony_pdf.py" plik.pdf` — liczba stron i czy mają warstwę tekstu.
2. PDF-y z tekstem: `--tekst` do `skany/_tekst/`, potem szukaj w tekście (tytuły, „rzut”, „przekrój”, „skala”, numery rysunków) zamiast oglądać każdą stronę.
3. Skany bez tekstu: podglądy `--dpi 50` do `skany/_podglad/` i oglądaj je partiami po kilka stron. Nie otwieraj pełnych rozdzielczości na tym etapie.
4. Zdjęcia JPG/HEIC: oglądaj zmniejszone (do ok. 1200 px). Jeśli zdjęcie jest obrócone lub pod kątem — zanotuj to w kolumnie uwag.
5. Zapisz `spis_arkuszy.md` z tabelą:

   | plik | strona | nr rysunku | tytuł | skala | data | rodzaj (rysunek / opis / decyzja) | czytelność (dobra / słaba / nieczytelna) | uwagi |

6. Pod tabelą krótko: które arkusze są podstawą (rzuty wszystkich kondygnacji, przekrój z rzędnymi, elewacje, sytuacja), czego brakuje, które są nieczytelne i trzeba je zeskanować lub sfotografować jeszcze raz.
7. Zaktualizuj `HANDOFF.md` (spis gotowy, proponowana kolejność przerysowania) i powiedz użytkownikowi jednym akapitem, co znalazłeś i od którego arkusza proponujesz zacząć.

Podglądy w `skany/_podglad/` zostaw — przydadzą się przy przerysowaniu.
