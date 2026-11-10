---
name: wizualizacja
description: Robi wizualizacje budynku w Blenderze bez otwierania okna programu — IFC → OBJ, scena z materiałami, terenem, niebem i słońcem, kamera, render Cycles na GPU (OptiX/CUDA/HIP/Metal); podgląd, potem finał. Używaj, gdy użytkownik mówi „wizualizacja”, „render”, „Blender”, „widok od ulicy”, „z lotu ptaka”, „wersja zimowa”, „złota godzina”. / EN — Renders the building in Blender without opening its window — IFC → OBJ, scene with materials, terrain, sky and sun, camera, Cycles render on the GPU (OptiX/CUDA/HIP/Metal); preview first, then final. Use when the user says “visualisation”, “render”, “Blender”, “street view”, “bird's-eye view”, “winter version”, “golden hour”.
---

# Wizualizacja w Blenderze

Skrypty w folderze `scripts/` tego skilla: `ifc_do_obj.py` (IFC → OBJ + MTL) i `blender_render.py` (scena i render). Skopiuj je do `tools/` projektu przy pierwszej wizualizacji — rozbudowy sceny robisz w kopii. Ścieżki z `~/.architekt/config.json`: `python`, `blender`, `gpu`. Brak Blendera → skill `przygotuj-komputer`.

## Kroki

1. **Eksport:** `"<python>" tools/ifc_do_obj.py model/<nazwa>.ifc render/<nazwa>.obj`.
2. **Podgląd** (zawsze najpierw): `"<blender>" -b -P tools/blender_render.py -- render/<nazwa>.obj render/podglad_<ujecie>.png 16 800 <azymut_kamery> <wysokosc_kamery_st> <slonce_azymut> <slonce_wysokosc>`. Domyślnie: kamera 215°, 18°; słońce 150°, 35°. Obejrzyj podgląd i pokaż użytkownikowi. Ustal z nim kadr, porę dnia, kierunek.
3. **Finał** dopiero po akceptacji kadru: 256 próbek, 2400 px → `render/<nazwa>_<ujecie>.png`. Powiedz, ile to potrwa (z czasu podglądu × ok. 16 × (2400/800)²) i uruchom w tle, jeśli > 2 min.
4. `HANDOFF.md`: lista ujęć z parametrami, żeby dało się je powtórzyć po zmianie modelu.

Render na CPU (brak GPU w config.json) jest wielokrotnie wolniejszy — przy finałach zaproponuj mniejszą rozdzielczość lub mniej próbek.

## Rozbudowa sceny

Teren z mapy, zieleń, ludzie, auta, śnieg, wnętrza: **osobne moduły** w `tools/scena_*.py` importowane przez `blender_render.py`, nie jeden wielki plik. Każdą zmianę sprawdzaj podglądem 16 próbek, zanim zrobisz finał.

- **Teren z mapy do celów projektowych** (DXF/DWG od geodety): wyciągnij punkty wysokościowe i granice działek z warstw (ezdxf), przelicz do układu budynku po 2 punktach kontrolnych (narożniki budynku na mapie), zapisz `model/teren.json`, w Blenderze zbuduj siatkę z triangulacji. Pokaż rzędne terenu przy narożnikach budynku do sprawdzenia.
- **Zima:** śnieg jako osobny materiał na powierzchniach o normalnej w górę (dach, teren), niebo zachmurzone, słońce nisko.
- **Ujęcie z wysokości oczu:** kamera 1,6 m nad terenem, ogniskowa 24–28 mm, pionowe linie pionowe (shift zamiast przechylania).

Wizualizacja koncepcji ma pokazywać projekt korzystnie, ale uczciwie: nie dodawaj elementów, których nie ma w modelu, bez zgody użytkownika.
