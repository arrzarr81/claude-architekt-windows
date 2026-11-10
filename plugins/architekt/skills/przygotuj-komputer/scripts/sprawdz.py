"""sprawdz.py — kontrola środowiska pluginu architekt (Windows i macOS).

Sprawdza biblioteki Pythona, znajduje Blendera, pyta go o wersję i kartę graficzną (Cycles),
a wynik zapisuje w ~/.architekt/config.json. Pozostałe skille biorą stamtąd ścieżki do Pythona i Blendera.

Użycie (Pythonem ze środowiska ~/.architekt/venv):
  Windows:  %USERPROFILE%\\.architekt\\venv\\Scripts\\python.exe sprawdz.py [--blender ŚCIEŻKA]
  macOS:    ~/.architekt/venv/bin/python sprawdz.py [--blender ŚCIEŻKA]
Kod wyjścia 0 = wszystko działa, 1 = czegoś brakuje (lista na końcu).
"""
import glob
import importlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path

KATALOG = Path.home() / ".architekt"
CONFIG = KATALOG / "config.json"

# moduł do importu -> pakiet pip
BIBLIOTEKI = {
    "ezdxf": "ezdxf",
    "shapely": "shapely",
    "matplotlib": "matplotlib",
    "cv2": "opencv-python-headless",
    "ifcopenshell": "ifcopenshell",
    "pymupdf": "pymupdf",
}

GPU_EXPR = """
import bpy
p = bpy.context.preferences.addons['cycles'].preferences
wynik = 'CPU'
for typ in ('OPTIX', 'CUDA', 'HIP', 'ONEAPI', 'METAL'):
    try:
        p.compute_device_type = typ
    except TypeError:
        continue
    p.get_devices()
    urz = [d.name for d in p.devices if d.type == typ]
    if urz:
        wynik = typ + ': ' + ', '.join(urz)
        break
print('ARCHITEKT_GPU=' + wynik)
"""


def klucz_wersji(sciezka):
    return [int(x) for x in re.findall(r"\d+", sciezka)] or [0]


def znajdz_blendera():
    system = platform.system()
    kandydaci = []
    if system == "Windows":
        for baza in (os.environ.get("ProgramFiles", r"C:\Program Files"),
                     os.environ.get("ProgramW6432", ""),
                     os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs")):
            if baza:
                kandydaci += glob.glob(os.path.join(baza, "Blender Foundation", "Blender*", "blender.exe"))
    elif system == "Darwin":
        for app in ("/Applications/Blender.app", str(Path.home() / "Applications" / "Blender.app")):
            kandydaci.append(os.path.join(app, "Contents", "MacOS", "Blender"))
    kandydaci = sorted({k for k in kandydaci if os.path.isfile(k)}, key=klucz_wersji)
    if kandydaci:
        return kandydaci[-1]
    return shutil.which("blender")  # np. Homebrew albo własna instalacja w PATH


def sprawdz_blendera(sciezka):
    wersja = gpu = None
    try:
        out = subprocess.run([sciezka, "--version"], capture_output=True, text=True, timeout=120).stdout
        m = re.search(r"Blender (\d+\.\d+(?:\.\d+)?)", out)
        wersja = m.group(1) if m else None
        out = subprocess.run([sciezka, "-b", "--factory-startup", "--python-expr", GPU_EXPR],
                             capture_output=True, text=True, timeout=300).stdout
        m = re.search(r"ARCHITEKT_GPU=(.*)", out)
        gpu = m.group(1).strip() if m else None
    except (OSError, subprocess.TimeoutExpired) as e:
        print("  błąd uruchomienia Blendera:", e)
    return wersja, gpu


def main():
    args = sys.argv[1:]
    blender = args[args.index("--blender") + 1] if "--blender" in args else None
    braki = []

    print(f"System: {platform.system()} {platform.release()} ({platform.machine()})")
    print(f"Python: {sys.version.split()[0]}  ({sys.executable})")
    if sys.version_info < (3, 10):
        braki.append("Python 3.10 lub nowszy")

    wersje = {}
    for modul, pakiet in BIBLIOTEKI.items():
        try:
            m = importlib.import_module(modul)
            wersje[pakiet] = str(getattr(m, "__version__", getattr(m, "version", "?")))
            print(f"  OK  {pakiet} {wersje[pakiet]}")
        except Exception as e:  # noqa: BLE001 — każda przyczyna = brak
            print(f"  BRAK {pakiet} ({e.__class__.__name__})")
            braki.append(f"biblioteka {pakiet}")

    blender = blender or znajdz_blendera()
    wersja_b = gpu = None
    if blender and os.path.isfile(blender):
        wersja_b, gpu = sprawdz_blendera(blender)
        print(f"Blender: {wersja_b or '?'}  ({blender})")
        print(f"Render:  {gpu or 'nie udało się sprawdzić karty (test GPU przerwany) — render może iść na procesorze'}")
        if not wersja_b:
            braki.append("Blender się nie uruchamia")
    else:
        print("Blender: nie znaleziono")
        braki.append("Blender")
        blender = None

    git = shutil.which("git")
    print(f"Git:     {'OK' if git else 'brak (commity w /handoff nie zadziałają)'}")

    KATALOG.mkdir(parents=True, exist_ok=True)
    CONFIG.write_text(json.dumps({
        "python": sys.executable,
        "blender": blender,
        "blender_wersja": wersja_b,
        "gpu": gpu,
        "biblioteki": wersje,
        "system": platform.system(),
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Zapisano: {CONFIG}")

    if braki:
        print("DO UZUPEŁNIENIA: " + "; ".join(braki))
        sys.exit(1)
    print("WSZYSTKO DZIAŁA")


if __name__ == "__main__":
    main()
