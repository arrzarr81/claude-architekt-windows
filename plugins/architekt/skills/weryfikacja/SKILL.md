---
name: weryfikacja
description: Sprawdza wyniki projektu, zanim etap zostanie uznany za gotowy — rysunki DXF (otwierają się, centymetry, narożnik bryły w 0,0, podgląd PDF/PNG), model IFC (rzędne kondygnacji zgodne ze ścianami, wymiary w metrach, style materiałów, zgodność z rzutem), eksport OBJ i rendery (nie czarne) — oraz porównuje liczby ze wzorcem projektu, żeby wyłapać przypadkowe zmiany. Używaj po każdym przerysowanym arkuszu, przebudowie modelu, eksporcie i renderze oraz gdy użytkownik mówi „sprawdź”, „czy wszystko się zgadza”, „zweryfikuj”, „przed wysłaniem”. / EN — Checks project outputs before a step is called done — DXF drawings (open, centimetres, building corner at 0,0, PDF/PNG preview), IFC model (storey levels match walls, metres, material styles, matches the plan), OBJ export and renders (not black) — and compares counts with the project baseline to catch accidental changes. Use after every redrawn sheet, model rebuild, export and render, and when the user says “check”, “verify”, “does everything match”, “before sending”.
---

# Weryfikacja wyników projektu

Etap (arkusz, model, render) nie jest gotowy, dopóki weryfikacja nie da PASS. Nie oceniasz „na oko”: skrypt otwiera pliki tak jak program architekta i sprawdza liczby.

Skrypt: `scripts/sprawdz_projekt.py` w folderze tego skilla (bez kopiowania do projektu). Python z `~/.architekt/config.json` (klucz `python`). Uruchamiaj z głównego folderu projektu:

```
"<python>" "<folder skilla>/scripts/sprawdz_projekt.py" .
```

Ostatnia linia: `WERYFIKACJA: PASS|FAIL (n/m)`. Raport z tabelą: `weryfikacja/raport_<data>.md`. Linie `FAIL` to błędy, `UWAGA` to rzeczy do przejrzenia (nie blokują).

## Kiedy uruchamiać
- po każdym `tools/<arkusz>.py` (nowy lub poprawiony rysunek),
- po przebudowie modelu IFC i po eksporcie do OBJ,
- po podglądzie i finale renderu,
- przed wysłaniem plików komukolwiek.

## Co sprawdza
- **DXF** (`rysunki/`): plik się otwiera i ma obiekty; w rzutach ściany w centymetrach (bryła 1–200 m) i narożnik NW bryły w punkcie 0,0 (wszystkie kondygnacje się nakładają); obok jest PDF i PNG z rysunkiem.
- **IFC** (`model/`): kondygnacje z różnymi rzędnymi; **rzędna kondygnacji zgadza się ze spodem większości jej ścian** (wyłapuje pomyłkę jednostek: rzędna w metrach w pliku w milimetrach); ściany są; każda ściana i płyta ma styl (inaczej w renderze jest szara); bryła 1–200 m (cm wpisane jako m); obrys zgodny z największym rzutem DXF (±10 cm, tylko UWAGA — model może mieć przybudówki).
- **OBJ / render** (`render/`): obiekty, materiały opisane w `.mtl`, obraz nie jest czarny ani jednolity. Podgląd i tak obejrzyj sam.
- **Wzorzec** (`weryfikacja/wzorce.json`): liczba ścian, płyt, kondygnacji, obiektów na warstwach DXF — każda zmiana to FAIL z listą różnic.

## Wzorzec projektu
- Pierwszy raz, gdy rysunki i model są zaakceptowane przez użytkownika: `... sprawdz_projekt.py . --zapisz-wzorce`.
- Gdy zmiana jest zamierzona (dorysowane okno, nowa ściana): pokaż użytkownikowi różnice z linii FAIL (po ludzku: „na rzucie parteru przybyły 2 okna, w modelu 1 ściana”), po jego zgodzie zapisz wzorzec ponownie.
- Gdy zmiany nikt nie planował: to błąd — wróć do danych arkusza/modelu.

## Przy FAIL
1. Przeczytaj linie FAIL i raport. Obejrzyj podgląd PNG rysunku lub renderu, którego dotyczą.
2. Popraw przyczynę w danych skryptu (`tools/<arkusz>.py`, `tools/model_ifc.py`), nigdy ręcznie w DXF/IFC i nigdy przez zmianę wzorca „żeby przeszło”.
3. Uruchom weryfikację ponownie. Użytkownikowi pokaż wynik: co było źle, co poprawione, PASS.

Użytkownik jest architektem: opisuj wynik rysunkami i wymiarami („rzędna piętra w modelu 0,003 m zamiast 3,15 m”), nie kodem.
