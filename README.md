# Claude Code: skany → DXF → model IFC → wizualizacje (Windows)

Polski · [English](README.en.md)

Plugin do Claude Code dla architektów. Piszesz po polsku, co ma powstać, a Claude przerysowuje skany dokumentacji do DXF, buduje model IFC i robi wizualizacje w Blenderze. Skryptów nie trzeba znać — działają w tle.

Wersja dla Windows 10/11. Wersja dla macOS: [claude-architekt-mac](https://github.com/arrzarr81/claude-architekt-mac).

## Instalacja (raz, ok. 20 minut)

Potrzebne jest konto Claude **Pro** (na próbę) albo **Max** (do codziennej pracy). Karta NVIDIA przyspiesza rendery, ale nie jest konieczna.

**Jak otworzyć PowerShell:** naciśnij klawisz Windows, wpisz `powershell` i naciśnij Enter. Otworzy się okno, w które wpisuje się polecenia. Każde polecenie zatwierdzasz klawiszem Enter. Używaj PowerShell, nie „Wiersza polecenia” (cmd) — polecenia poniżej są dla PowerShell.

**Filmy** (po angielsku; można włączyć napisy z tłumaczeniem na polski: ikona ustawień → Napisy → Tłumacz automatycznie). Polecenia wpisuj według tej instrukcji, filmy pokazują, jak to wygląda na ekranie.

- **Najpierw obejrzyj ten** — prosto, krok po kroku, instalacja i pierwsze uruchomienie Claude Code w PowerShell: [youtube.com/watch?v=1R92BDfJ_s8](https://www.youtube.com/watch?v=1R92BDfJ_s8)
- **Gdy coś nie działa** — więcej szczegółów i rozwiązywanie problemów: [youtube.com/watch?v=jnaI83h7SM8](https://www.youtube.com/watch?v=jnaI83h7SM8)

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
4. **Pierwsze uruchomienie Claude Code i logowanie.** W tym samym oknie PowerShell wpisz `claude` i naciśnij Enter. Okno zmieni wygląd, bo zamiast PowerShell działa w nim teraz Claude Code. Przy pierwszym uruchomieniu pojawi się kilka pytań. Między opcjami przechodzisz strzałkami ↑ ↓, a wybór zatwierdzasz klawiszem Enter:
   - wygląd (kolory): zostaw podświetloną opcję i naciśnij Enter;
   - sposób logowania: wybierz opcję z **kontem Claude (subskrypcja Pro/Max)**. Otworzy się przeglądarka. Zaloguj się tam na swoje konto Claude i kliknij „Autoryzuj”, a potem wróć do okna PowerShell;
   - „Czy ufasz plikom w tym folderze?” (*Do you trust the files in this folder?*): wybierz „Tak” (*Yes, proceed*).

   **Jak poznać, gdzie jesteś:**
   - Jeśli linia zaczyna się od `PS D:\Projekty>`, to jest PowerShell. Tu wpisujesz `claude`, `cd`, `mkdir`.
   - Jeśli widzisz ramkę z `>` na dole okna, to jest Claude Code. Tu piszesz po polsku do Claude i wpisujesz polecenia zaczynające się od `/`.
   - Claude Code zamykasz poleceniem `/exit` (albo dwa razy Ctrl+C) i wracasz wtedy do PowerShell.

   Polecenia możesz przepisać ręcznie albo skopiować z tej instrukcji. Wkleja się je w okno klawiszami Ctrl+V albo prawym przyciskiem myszy.

5. **Instalacja pluginu (wpisujesz w Claude Code, w ramce z `>`).** Wpisz pierwsze polecenie i naciśnij Enter:

   ```
   /plugin marketplace add arrzarr81/claude-architekt-windows
   ```

   Gdy pojawi się potwierdzenie, wpisz drugie polecenie i naciśnij Enter:

   ```
   /plugin install architekt@claude-architekt-windows
   ```

   Jeśli Claude zapyta, dla kogo zainstalować plugin, wybierz pierwszą opcję (dla Ciebie, *user*) i naciśnij Enter. Jeśli poprosi o ponowne uruchomienie (*restart*), wpisz `/exit`, a potem w PowerShell znowu `claude`. Gdy po wpisaniu samego `/` na liście poleceń widać `/handoff`, plugin jest zainstalowany.

   **Jeśli coś nie działa:**
   - Komunikat „claude: The term 'claude' is not recognized”: zamknij PowerShell, otwórz go ponownie i przejdź do folderu (`cd D:\Projekty`).
   - Gdy nie pomaga, uruchom ponownie komputer.
   - Gdy polecenie `/plugin` zwróci błąd, zrób zrzut ekranu i wyślij go nam.

6. W Claude Code napisz: **„Przygotuj komputer do pracy.”** Claude sam zainstaluje Pythona, biblioteki i Blendera i sprawdzi, czy działają. Gdy Windows zapyta o zgodę administratora, kliknij „Tak”.

## Dobre praktyki: bezpieczeństwo plików

Claude Code pracuje na plikach w Twoim komputerze. Domyślnie **przed każdym poleceniem i każdą zmianą pliku pyta o zgodę**, i to wystarcza, jeśli zachowasz kilka nawyków (na Windows nie ma dodatkowej „piaskownicy”, więc to te zgody są zabezpieczeniem):

1. **Czytaj, o co pyta, zanim klikniesz „Tak”.** Jeśli w pytaniu jest usuwanie (`Remove-Item`, `rm`, `del`, „usuń”) albo folder spoza projektu, wybierz „Nie” i zapytaj Claude, po co mu to.
2. **Opcję „Tak, i nie pytaj więcej” (*Yes, and don't ask again*) wybieraj tylko przy poleceniach, które niczego nie usuwają** (np. rendery, eksport PDF). Nigdy przy usuwaniu.
3. **Nie uruchamiaj trybu bez pytań** (*bypass permissions*, `--dangerously-skip-permissions`), nawet jeśli ktoś to poleca w internecie.
4. **Uruchamiaj `claude` zawsze w folderze projektu** (`cd D:\Projekty\…`), nigdy w `C:\` ani w folderze użytkownika. Ważne pliki spoza projektu miej w kopii zapasowej (dysk zewnętrzny albo chmura).

Pliki samego projektu są dodatkowo chronione: przy każdym `/handoff` plugin zapisuje wersję w Git, więc zmienione lub usunięte rysunki da się przywrócić. Wystarczy napisać „przywróć wersję sprzed ostatniej zmiany”.

## Nowy projekt

Każdy budynek to osobny folder, bez spacji i polskich znaków w nazwie. Otwórz PowerShell i wpisz (`Projekt1` zamień na nazwę projektu, `D:` na `C:`, jeśli nie masz dysku D):

```
mkdir D:\Projekty\Projekt1
cd D:\Projekty\Projekt1
explorer .
```

Ostatnie polecenie otwiera ten folder w Eksploratorze: przeciągnij do niego skany lub projekt budynku (PDF, JPG) i zdjęcia nieruchomości (każda elewacja, otoczenie, sąsiedzi). Potem wróć do okna PowerShell, wpisz `claude` i napisz „nowy projekt” razem z **adresem nieruchomości**.

Claude najpierw zbiera dane o miejscu, a dopiero potem rysuje i renderuje: z adresu pobiera granice i wymiary działki, sąsiednie działki i budynki z ewidencji oraz ortofotomapę z geoportalu, poprosi o link do Street View i brakujące zdjęcia, a wynik zapisze w karcie działki (`otoczenie/karta_dzialki.md`). Dzięki temu wizualizacje pokazują budynek na prawdziwej działce, z prawdziwymi sąsiadami.

**Powrót do projektu następnego dnia:** otwórz PowerShell i wpisz `cd D:\Projekty\Projekt1`, a potem `claude`. Claude zawsze pracuje w folderze, w którym go uruchomiono, i widzi tylko jego zawartość.

## Praca

Przykłady poleceń:

- „Nowy projekt: Karpacz, ul. Przykładowa 1. Zdjęcia i skany są w folderze.”
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
| `nowy-projekt` | adres, zdjęcia i projekt na start; foldery, `CLAUDE.md` z zasadami, `HANDOFF.md`, git |
| `rozpoznanie-dzialki` | z adresu: granice i wymiary działki, sąsiedzi i budynki z ewidencji, ortofoto, Street View, karta działki; bez niej nie ma wizualizacji |
| `spis-arkuszy` | przegląd skanów, tabela arkuszy |
| `skan-do-dxf` | przerysowanie rzutu / przekroju / elewacji do DXF, porównanie ze skanem, DWG |
| `model-ifc` | model IFC4 z rzutów, warianty koncepcji |
| `wizualizacja` | IFC → OBJ → Blender (Cycles, OptiX/CUDA/HIP), podgląd i finał |
| `zestawienie-pdf` | PDF A3 z arkuszy i renderów |

Do tego komenda `/handoff` i hook, który po starcie, `/clear` i kompaktowaniu wczytuje `HANDOFF.md`.

Dokładność przerysowania ze skanu to zwykle ±10–20 cm: szkic roboczy i baza koncepcji, nie inwentaryzacja.

Licencja MIT.
