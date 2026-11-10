"""strony_pdf.py — strony PDF jako obrazy PNG i tekst (PyMuPDF), do przeglądania skanów bez czytania całego pliku.

Użycie:
  python strony_pdf.py plik.pdf                      → liczba stron, wymiary, czy strona ma tekst
  python strony_pdf.py plik.pdf wyj/ --dpi 60        → wszystkie strony jako wyj/<plik>_s001.png (podgląd)
  python strony_pdf.py plik.pdf wyj/ --strony 12,15-18 --dpi 200   → wybrane strony do odczytu wymiarów
  python strony_pdf.py plik.pdf wyj/ --tekst         → warstwa tekstu każdej strony do wyj/<plik>.txt (do grep)
Numery stron od 1. Wymaga: pip install pymupdf
"""
import sys
from pathlib import Path

import pymupdf as fitz  # PyMuPDF (import fitz jest przestarzały)


def zakres(opis, n):
    strony = []
    for czesc in opis.split(","):
        czesc = czesc.strip()
        if "-" in czesc:
            a, b = czesc.split("-")
            strony += range(int(a), int(b) + 1)
        elif czesc:
            strony.append(int(czesc))
    return [s for s in strony if 1 <= s <= n]


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)
    pdf = Path(args[0])
    wyj = Path(args[1]) if len(args) > 1 and not args[1].startswith("--") else None
    dpi = int(args[args.index("--dpi") + 1]) if "--dpi" in args else 60
    doc = fitz.open(pdf)
    strony = zakres(args[args.index("--strony") + 1], len(doc)) if "--strony" in args else list(range(1, len(doc) + 1))

    if wyj is None:
        print(f"{pdf.name}: {len(doc)} stron")
        for s in strony:
            p = doc[s - 1]
            tekst = len(p.get_text().strip())
            print(f"  s.{s:>3}  {p.rect.width / 72 * 25.4:.0f}×{p.rect.height / 72 * 25.4:.0f} mm  "
                  f"tekst: {'tak' if tekst > 20 else 'nie (skan)'}")
        return

    wyj.mkdir(parents=True, exist_ok=True)
    if "--tekst" in args:
        plik = wyj / f"{pdf.stem}.txt"
        with open(plik, "w", encoding="utf-8") as f:
            for s in strony:
                f.write(f"\n===== strona {s} =====\n{doc[s - 1].get_text()}")
        print(f"Tekst: {plik}")
        return
    for s in strony:
        plik = wyj / f"{pdf.stem}_s{s:03d}.png"
        doc[s - 1].get_pixmap(dpi=dpi).save(plik)
        print(plik)


if __name__ == "__main__":
    main()
