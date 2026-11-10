---
name: skan-do-dxf
description: Przerysowuje rzut, przekrój lub elewację ze skanu (PDF/zdjęcie) do DXF (+ podgląd PNG i PDF A3) skryptem z danymi w cm, porównuje wynik ze skanem i wypisuje różnice wymiarów; także zamiana DXF → DWG. Używaj, gdy użytkownik mówi „przerysuj”, „do DXF”, „do CAD”, „do DWG”, „rzut parteru ze strony…”, „popraw ścianę / okno na rysunku”. / EN — Traces a floor plan, section or elevation from a scan (PDF/photo) to DXF (+ PNG preview and A3 PDF) with a script holding dimensions in cm, compares the result with the scan and lists dimension differences; also converts DXF → DWG. Use when the user says “trace”, “redraw”, “to DXF”, “to CAD”, “to DWG”, “ground floor plan from page…”, “fix a wall / window in the drawing”.
---

# Skan → DXF

Wzorzec: `scripts/cad_dxf.py` (moduł) i `scripts/przyklad_rzut.py` (arkusz) w folderze tego skilla. W projekcie są ich kopie w `tools/` (skill `nowy-projekt`); jeśli ich nie ma — skopiuj. Opis kluczy słownika rzutu jest na początku `cad_dxf.py` — przeczytaj go przed pierwszym arkuszem. Python z `~/.architekt/config.json` (klucz `python`). Układ i jednostki: `CLAUDE.md` projektu.

## Przerysowanie arkusza

1. **Źródło.** Ustal plik i stronę (ze `spis_arkuszy.md`). Wyrenderuj stronę w 150–200 dpi skryptem `strony_pdf.py` (skill `spis-arkuszy`) i oglądaj ją we fragmentach, nie w całości w pełnej rozdzielczości.
2. **Najpierw odczyt, potem rysunek.** Wypisz użytkownikowi odczytane wymiary: łańcuchy zewnętrzne i wewnętrzne, grubości ścian, otwory (szerokość/wysokość, np. 150/150), biegi schodów. Każdy oznacz: **pewny** (opisany na rysunku) albo **szacowany** (z podziałki). Sprawdź, czy łańcuchy się sumują.
3. **Dane.** Utwórz `tools/<arkusz>.py` według `przyklad_rzut.py`: `sciany`, `okna`, `drzwi`, `otwory`, `schody`, `pomieszczenia`, `wymiary`, `tabliczka` (źródło: plik, strona, skala, dokładność). Wszystko w cm w układzie z `CLAUDE.md`. Przy każdym elemencie komentarz ze źródłem.
4. **Uruchom** z głównego folderu projektu (nie z `tools/`): `"<python>" tools/<arkusz>.py` → `rysunki/<arkusz>.dxf/.png/.pdf`. Folder `rysunki/` liczy się od miejsca uruchomienia.
5. **Porównaj ze skanem.** Obejrzyj PNG obok skanu. Jeśli na skanie da się wskazać 4 narożniki bryły (piksele), użyj `cad_dxf.nakladka()` i pokaż nakładkę. Wypisz tabelę: wymiar ze skanu / w rysunku / różnica. Popraw dane tam, gdzie różnica > 5 cm, i uruchom ponownie.
6. **Kolejne kondygnacje:** dodaj warstwę z obrysem kondygnacji niżej i wypisz miejsca, gdzie ściany nośne lub szachty nie leżą jedna nad drugą (> 5 cm).
7. **Zapis stanu:** `HANDOFF.md` (arkusz gotowy, niepewne miejsca, co dalej), wpis w `PROGRESS.md`.

Dokładność przerysowania ze skanu to zwykle ±10–20 cm — to szkic roboczy i baza koncepcji, nie inwentaryzacja. Mów to użytkownikowi przy pierwszym arkuszu. Elementów niewidocznych nie zgaduj — wpisz je do UWAGI na arkuszu.

## Poprawki

Użytkownik poda je jako „ściana X ma 38 cm, na skanie str. 66 jest 30 cm”. Poprawiasz dane w `tools/<arkusz>.py`, uruchamiasz skrypt, pokazujesz zmieniony fragment PNG. DXF nigdy nie poprawiasz ręcznie. Jeśli użytkownik poprawił DXF sam w CAD-zie, zapytaj, czy przenieść zmiany do danych skryptu (inaczej zostaną nadpisane).

## DXF → DWG

- AutoCAD / BricsCAD: otworzyć DXF i „Zapisz jako” DWG — najprościej.
- Wsadowo: ODA File Converter (bezpłatny, instaluje użytkownik ze strony ODA po rejestracji). Wywołanie: `ODAFileConverter <folder_dxf> <folder_dwg> ACAD2018 DWG 0 1 "*.DXF"`. Ścieżkę do programu ustal na komputerze użytkownika (Windows: `C:\Program Files\ODA\ODAFileConverter*\ODAFileConverter.exe`, macOS: `/Applications/ODAFileConverter.app/Contents/MacOS/ODAFileConverter`).
