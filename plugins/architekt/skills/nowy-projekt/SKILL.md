---
name: nowy-projekt
description: Zakłada nowy projekt przerysowania dokumentacji budynku w bieżącym folderze — CLAUDE.md z zasadami, foldery, HANDOFF.md, PROGRESS.md, git. Używaj, gdy użytkownik mówi „nowy projekt”, „zaczynamy”, „załóż projekt”, „mam skany domu / teczki”, albo gdy w folderze są skany, a nie ma jeszcze CLAUDE.md z zasadami projektu.
---

# Nowy projekt

Projekt = jeden budynek = bieżący folder (ten, w którym uruchomiono Claude Code). Nie zakładaj podfolderu na projekt, chyba że użytkownik o to prosi.

## Kroki

1. Sprawdź `~/.architekt/config.json` (Windows: `%USERPROFILE%\.architekt\config.json`). Brak pliku → najpierw skill `przygotuj-komputer`.
2. Zapytaj krótko (jedno pytanie, wszystko naraz) tylko o to, czego nie widać w plikach: adres lub nazwę budynku i co jest celem (inwentaryzacja, koncepcja przebudowy, wizualizacje). Jeśli użytkownik już to podał — nie pytaj.
3. Utwórz foldery: `skany/`, `tools/`, `rysunki/`, `model/`, `render/`. Pliki skanów leżące luzem w folderze przenieś do `skany/` (pokaż listę przed przeniesieniem). Nazwy plików zostaw.
4. Skopiuj `szablon_CLAUDE.md` z folderu tego skilla jako `CLAUDE.md` i uzupełnij sekcję „Projekt”. Jeśli `CLAUDE.md` już istnieje — dopisz tylko brakujące sekcje, nie nadpisuj.
5. Skopiuj `cad_dxf.py` i `przyklad_rzut.py` ze skilla `skan-do-dxf` (folder `scripts/` obok tego skilla: `../skan-do-dxf/scripts/`) do `tools/`. Arkusze importują `cad_dxf` z `tools/`, więc wersja modułu jest zamrożona w projekcie.
6. Utwórz `HANDOFF.md` (nagłówek z datą, „Stan: projekt założony”, „Dalej: spis arkuszy”) i `PROGRESS.md` (pierwszy wpis z datą). Utwórz `.gitignore` z liniami: `__pycache__/`, `*.blend1`, `render/podglad*`.
7. `git init` i pierwszy commit (jeśli jest git). Brak gita → powiedz, że commity w `/handoff` nie zadziałają, i idź dalej.
8. Uruchom z głównego folderu projektu: `"<python>" tools/przyklad_rzut.py` (Python z config.json) — powstaje `rysunki/przyklad_rzut.png`. Obejrzyj go (mała rozdzielczość) i potwierdź użytkownikowi, że rysowanie działa.
9. Zaproponuj następny krok jednym zdaniem: spis arkuszy ze skanów (skill `spis-arkuszy`).
