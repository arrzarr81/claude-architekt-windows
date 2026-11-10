---
name: model-ifc
description: Buduje model 3D budynku w IFC4 (ifcopenshell) z danych przerysowanych rzutów — kondygnacje, ściany, otwory, okna, drzwi, stropy, dach — oraz warianty koncepcji (winda, balkony, nowe otwory) jako parametry. Używaj, gdy użytkownik mówi „model IFC”, „model 3D”, „BIM”, „wariant”, „dodaj windę / balkon / okno w modelu”, „policz powierzchnie”. / EN — Builds a 3D IFC4 building model (ifcopenshell) from traced floor plans — storeys, walls, openings, windows, doors, slabs, roof — with design variants (lift, balconies, new openings) as parameters. Use when the user says “IFC model”, “3D model”, “BIM”, “variant”, “add a lift / balcony / window to the model”, “calculate floor areas”.
---

# Model IFC

Wzorzec: `scripts/prosty_model_ifc.py` w folderze tego skilla — działający kod w aktualnym API ifcopenshell (0.8+). API zmieniało się między wersjami, więc **pisz według wzorca, nie z pamięci**. Python z `~/.architekt/config.json` (klucz `python`).

## Budowa modelu

1. Sprawdź, czy są przerysowane rzuty wszystkich kondygnacji (`tools/*.py`) i rzędne z przekroju (sekcja „Układ i jednostki” w `CLAUDE.md`). Brakuje rzędnych → zapytaj albo odczytaj z przekroju (skill `skan-do-dxf`, krok „najpierw odczyt”).
2. Napisz `tools/model_ifc.py`, który **importuje dane arkuszy** (słowniki z `tools/<arkusz>.py`), a nie kopiuje liczb. Zamiana: cm → m, Y = −y.
   - kondygnacje: nazwa, rzędna, wysokość,
   - ściany z prostokątów `sciany` (IfcWall, grubość = krótszy bok),
   - otwory: IfcOpeningElement + IfcWindow / IfcDoor o wymiarach z opisu (np. „150/150”); parapet 90 cm, jeśli nie podano — i zapisz to w UWAGACH,
   - stropy z obrysu kondygnacji, dach wg opisu użytkownika lub przekroju,
   - style powierzchni o nazwach: `sciany`, `okna`, `szklo`, `dach`, `strop`, `teren` — scena Blendera dobiera po nich materiały.
3. Zapisz do `model/<nazwa>.ifc`.
4. **Sprawdź** (pokaż użytkownikowi): liczba elementów każdej klasy, czy każdy element ma geometrię i kondygnację, podgląd rzutów wyciętych z IFC (matplotlib, PNG) obok rzutów DXF. Rozbieżności > 5 cm wypisz.
5. `HANDOFF.md` + `PROGRESS.md`.

## Warianty

Dodaj parametr `--wariant <nazwa>`; wariant bazowy (stan istniejący) zostaje bez zmian. Każdy wariant = osobny plik `model/<nazwa>_<wariant>.ifc` i tabela różnic: elementy dodane/usunięte, powierzchnie. Nie kopiuj całego skryptu na wariant.

## Podgląd dla użytkownika

Autodesk Viewer (viewer.autodesk.com): darmowe konto, wgrywa się plik `.ifc`, działa w przeglądarce; plik jest dostępny 30 dni, potem trzeba wgrać ponownie. Offline: BIM Vision (Windows, darmowy), Bonsai w Blenderze. Do renderów — skill `wizualizacja`.
