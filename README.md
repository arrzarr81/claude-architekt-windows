# Claude Code: skany → DXF → model IFC → wizualizacje (Windows)

Polski · [English](README.en.md)

Plugin do Claude Code dla architektów. Piszesz po polsku, co ma powstać, a Claude przerysowuje skany dokumentacji do DXF, buduje model IFC i robi wizualizacje w Blenderze. Skryptów nie trzeba znać — działają w tle.

Wersja dla Windows 10/11. Wersja dla macOS: [claude-architekt-mac](https://github.com/arrzarr81/claude-architekt-mac).

## Instalacja (raz, ok. 20 minut)

Potrzebne jest konto Claude **Pro** (na próbę) albo **Max** (do codziennej pracy). Karta NVIDIA przyspiesza rendery, ale nie jest konieczna.

**Jak otworzyć PowerShell:** naciśnij klawisz Windows, wpisz `powershell` i naciśnij Enter. Otworzy się okno, w które wpisuje się polecenia. Każde polecenie zatwierdzasz klawiszem Enter. Używaj PowerShell, nie „Wiersza polecenia” (cmd) — polecenia poniżej są dla PowerShell.

1. W PowerShell wpisz dwa polecenia:

   ```
   winget install --id Git.Git -e
   irm https://claude.ai/install.ps1 | iex
   ```

   Pierwsze polecenie instaluje **Git**. Jest potrzebny z dwóch powodów: Claude Code na Windows uruchamia przez niego swoje polecenia (wbudowany w Git program „Git Bash”), a plugin zapisuje w nim historię projektu po każdym etapie. Dzięki temu zawsze można wrócić do wcześniejszej wersji rysunków, jeśli poprawka pójdzie źle. Drugie polecenie instaluje **Claude Code**.

2. Zamknij okno PowerShell i otwórz je ponownie (tak jak wyżej).
3. Załóż folder na projekty i przejdź do niego. Jeśli masz dysk **D:** (Eksplorator plików → Ten komputer), użyj go:

   ```
   mkdir D:\Projekty
   cd D:\Projekty
   ```

   Bez dysku D: wpisz to samo z `C:` zamiast `D:`. Jeśli folder już istnieje, `mkdir` pokaże czerwony błąd, który możesz zignorować. Nie zakładaj projektów na Pulpicie ani w Dokumentach, jeśli synchronizuje je OneDrive.
4. Wpisz `claude` i zaloguj się kontem Claude. Potem wpisz w Claude Code:

   ```
   /plugin marketplace add arrzarr81/claude-architekt-windows
   /plugin install architekt@claude-architekt-windows
   ```

5. Napisz: **„Przygotuj komputer do pracy.”** Claude sam zainstaluje Pythona, biblioteki i Blendera i sprawdzi, czy działają. Gdy Windows zapyta o zgodę administratora, kliknij „Tak”.

## Nowy projekt

Każdy budynek to osobny folder, bez spacji i polskich znaków w nazwie. Otwórz PowerShell i wpisz (`Projekt1` zamień na nazwę projektu, `D:` na `C:`, jeśli nie masz dysku D):

```
mkdir D:\Projekty\Projekt1
cd D:\Projekty\Projekt1
explorer .
```

Ostatnie polecenie otwiera ten folder w Eksploratorze: przeciągnij do niego skany (PDF, JPG). Potem wróć do okna PowerShell, wpisz `claude` i napisz „nowy projekt”.

**Powrót do projektu następnego dnia:** otwórz PowerShell i wpisz `cd D:\Projekty\Projekt1`, a potem `claude`. Claude zawsze pracuje w folderze, w którym go uruchomiono, i widzi tylko jego zawartość.

## Praca

Przykłady poleceń:

- „Zrób spis arkuszy ze skanu `teczka.pdf`.”
- „Przerysuj rzut parteru ze strony 66 do DXF i porównaj ze skanem.”
- „Zbuduj model IFC z rzutów i przekroju.”
- „Zrób wizualizację od ulicy o złotej godzinie.”
- „Złóż rzuty i wizualizacje w PDF A3.”

Poprawki podawaj konkretnie: „ściana od ogrodu ma 38 cm, na skanie str. 66 jest 30 cm”. Claude pyta o zgodę przed uruchomieniem poleceń. Na początku zatwierdzaj je pojedynczo.

## Wyniki

- **DXF**: AutoCAD, BricsCAD albo LibreCAD (w AutoCAD zapisz jako DWG).
- **IFC**: Autodesk Viewer (viewer.autodesk.com), darmowe konto; wgrany plik jest dostępny 30 dni.
- **Rendery i zestawienia** (PNG, PDF): w folderze projektu.

## Długa praca

Przy zmianie tematu wpisz `/handoff`, a potem `/clear`. Stan prac zapisuje się w pliku `HANDOFF.md`, a nowa rozmowa wczytuje go sama.

## Aktualizacja pluginu

W Claude Code: `/plugin marketplace update claude-architekt-windows`.

## Co jest w środku

| Skill | Kiedy działa |
|---|---|
| `przygotuj-komputer` | instalacja Pythona, bibliotek i Blendera (winget), kontrola GPU |
| `nowy-projekt` | foldery, `CLAUDE.md` z zasadami, `HANDOFF.md`, git |
| `spis-arkuszy` | przegląd skanów, tabela arkuszy |
| `skan-do-dxf` | przerysowanie rzutu / przekroju / elewacji do DXF, porównanie ze skanem, DWG |
| `model-ifc` | model IFC4 z rzutów, warianty koncepcji |
| `wizualizacja` | IFC → OBJ → Blender (Cycles, OptiX/CUDA/HIP), podgląd i finał |
| `zestawienie-pdf` | PDF A3 z arkuszy i renderów |

Do tego komenda `/handoff` i hook, który po starcie, `/clear` i kompaktowaniu wczytuje `HANDOFF.md`.

Dokładność przerysowania ze skanu to zwykle ±10–20 cm: szkic roboczy i baza koncepcji, nie inwentaryzacja.

Licencja MIT.
