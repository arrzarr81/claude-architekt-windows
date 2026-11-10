---
name: przygotuj-komputer
description: Przygotowuje komputer z Windows do pracy z pluginem architekt — sam instaluje przez winget Pythona 3.12, biblioteki (ezdxf, ifcopenshell, shapely, matplotlib, opencv, pymupdf) i Blendera, sprawdza kartę graficzną i zapisuje ścieżki w %USERPROFILE%\.architekt\config.json. Używaj, gdy użytkownik mówi „przygotuj komputer”, „zainstaluj”, „nie działa Blender / Python”, albo gdy innemu skillowi brakuje config.json.
---

# Przygotowanie komputera (Windows)

Użytkownik nie jest programistą: instalujesz wszystko sam, poleceniami. Nie każ mu pobierać plików ze stron ani klikać instalatorów. Przed każdym poleceniem, które wywoła okno zgody administratora (Python, Blender), uprzedź go jednym zdaniem: „Windows zapyta o zgodę — kliknij Tak”.

Polecenia poniżej są w składni PowerShell. Jeśli Twoje narzędzie powłoki to Git Bash, uruchamiaj je przez `powershell.exe -NoProfile -Command "..."` albo przepisz ścieżki (`$env:USERPROFILE` → `$USERPROFILE`). `V` = `$env:USERPROFILE\.architekt\venv`.

## 0. Czy już jest gotowe?

Jeśli istnieje `$env:USERPROFILE\.architekt\config.json` i `V\Scripts\python.exe`: uruchom krok 5. Wynik „WSZYSTKO DZIAŁA” → powiedz to użytkownikowi i zakończ.

## 1. winget

`winget --version`. Brak → poproś użytkownika o instalację „Instalator aplikacji” (App Installer) z Microsoft Store i zakończ do tego czasu. Błąd „No package found” w kolejnych krokach → `winget source update` i ponów.

## 2. Python 3.12

- Sprawdź: `py -3.12 --version` (launcher `py`). Uwaga: `python.exe` z `WindowsApps` to tylko skrót do sklepu — nie licz go jako zainstalowanego Pythona.
- Brak: `winget install --id Python.Python.3.12 -e --source winget --accept-source-agreements --accept-package-agreements`
- Po instalacji bieżąca sesja nie widzi nowej ścieżki PATH. Używaj `py -3.12` albo pełnej ścieżki `$env:LOCALAPPDATA\Programs\Python\Python312\python.exe`. Nie każ użytkownikowi restartować, dopóki to działa.

## 3. Środowisko i biblioteki

```
py -3.12 -m venv "$env:USERPROFILE\.architekt\venv"
& "$env:USERPROFILE\.architekt\venv\Scripts\python.exe" -m pip install --upgrade pip
& "$env:USERPROFILE\.architekt\venv\Scripts\python.exe" -m pip install ezdxf shapely matplotlib opencv-python-headless ifcopenshell pymupdf
```

Jedno środowisko dla wszystkich projektów — nie twórz `.venv` w folderach projektów.

## 4. Blender

- Najpierw krok 5 — `sprawdz.py` sam szuka Blendera w `C:\Program Files\Blender Foundation\Blender *\blender.exe`. Jest → pomiń instalację.
- Brak: `winget install --id BlenderFoundation.Blender -e --source winget --accept-source-agreements --accept-package-agreements` (ok. 400 MB, kilka minut — powiedz o tym).
- Brak uprawnień administratora (komputer firmowy): wersja przenośna ZIP z `https://download.blender.org/release/` (najnowszy folder `BlenderX.Y/`, plik `*-windows-x64.zip`), rozpakuj do `$env:LOCALAPPDATA\Programs\Blender Foundation\Blender X.Y\` tak, żeby `blender.exe` leżał bezpośrednio w tym folderze.
- Blender nie trafia do PATH — zawsze pełna ścieżka z config.json.
- Kartę graficzną wybiera sam `blender_render.py` (OptiX/CUDA/HIP); w Blenderze nic nie trzeba ustawiać.

## 5. Kontrola

```
& "$env:USERPROFILE\.architekt\venv\Scripts\python.exe" "<folder tego skilla>\scripts\sprawdz.py"
```

(opcjonalnie `--blender "<ścieżka do blender.exe>"`, jeśli jest w nietypowym miejscu). Skrypt zapisuje `config.json` i kończy się „WSZYSTKO DZIAŁA” albo listą braków — braki uzupełnij i uruchom ponownie.

## 6. Git

`git --version`. Brak → `winget install --id Git.Git -e --source winget --accept-source-agreements --accept-package-agreements` (potrzebny do commitów w `/handoff`).

## Raport dla użytkownika

Krótko, bez kodu: „Gotowe: Python 3.12, biblioteki, Blender 5.x. Render na karcie <nazwa> (albo: na procesorze — będzie wolniej). Możesz zacząć: załóż folder projektu ze skanami i napisz »nowy projekt«.”
