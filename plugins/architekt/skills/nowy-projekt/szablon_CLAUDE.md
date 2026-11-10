# CLAUDE.md — zasady projektu

## Projekt
- Budynek: <adres / nazwa>
- Cel: <inwentaryzacja / koncepcja przebudowy / wizualizacje>
- Źródła: skany w `skany/` (spis w `spis_arkuszy.md`)

## Układ i jednostki
- Rysunki 2D: centymetry. Układ arkusza: x w prawo od zewnętrznego lica lewej ściany bryły, y w dół od zewnętrznego lica górnej ściany; punkt 0,0 = narożnik lewy-górny bryły. Wszystkie kondygnacje w tym samym układzie, więc nakładają się 1:1.
- Model IFC: metry (cm / 100), Z w górę, X = x arkusza, Y = −y arkusza.
- Kierunki świata: <np. góra arkusza = północ; uzupełnić po spisie arkuszy>.
- Rzędne kondygnacji: <nazwa, rzędna posadzki, wysokość — uzupełnić z przekroju>.

## Jak powstają rysunki
- Każdy arkusz = skrypt `tools/<arkusz>.py` z danymi w słowniku (wzór: `tools/przyklad_rzut.py`), rysunek generuje `cad_dxf.zapisz()` → `rysunki/<arkusz>.dxf/.png/.pdf`.
- Poprawki tylko w danych skryptu, nigdy ręcznie w DXF.
- Przy każdym elemencie komentarz ze źródłem: plik skanu, strona, wymiar.
- Model IFC: `tools/model_ifc.py` czyta dane arkuszy; warianty jako parametr `--wariant`, nie kopie plików.

## Stan prac w plikach, nie w rozmowie
- Długie rozmowy są automatycznie skracane, a użytkownik robi /clear, więc pliki muszą mieć aktualny stan.
- Po każdym etapie (arkusz przerysowany, model zbudowany, decyzja, przed serią renderów) zaktualizuj `HANDOFF.md` bez pytania: co gotowe, co dalej, pułapki, polecenia do uruchomienia.
- Historię dopisuj na końcu `PROGRESS.md` (data + krótko). Nigdy jej nie nadpisuj.
- Gdy rozmowa jest długa, a kolejne zadanie niezależne, napisz jednym zdaniem: „stan zapisany, to dobry moment na /handoff i /clear”.

## Oszczędzanie kontekstu
- Dużych PDF-ów nie czytaj w całości: `strony_pdf.py` (skill spis-arkuszy) — podgląd 60 dpi, odczyt wymiarów 150–200 dpi tylko potrzebnych stron lub wycinków.
- Obrazy oglądaj do ok. 1600 px; pełną rozdzielczość tylko dla wyciętego fragmentu.
- Rendery: najpierw podgląd 16 próbek / 800 px, finał dopiero po akceptacji kadru.
- Wyniki długich poleceń streszczaj, nie wklejaj całych logów.

## Sprawdzanie
- Zanim uznasz coś za gotowe, pokaż dowód: podgląd PNG, tabelę różnic wymiarów, liczbę elementów w IFC. Jeśli nie dało się sprawdzić — powiedz to wprost.
- Elementów niewidocznych na skanie nie zgaduj — wpisz je do UWAGI na arkuszu i do `HANDOFF.md`.

## Komunikacja
- Użytkownik jest architektem, nie programistą: pisz o rysunkach i wymiarach, nie o kodzie. Nie pokazuj kodu, jeśli nie prosi.
- Pliki wynikowe wskazuj pełną ścieżką.
