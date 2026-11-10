"""Przykład arkusza: prosty rzut 10 × 8 m (ściany 30/12 cm, okna, drzwi, schody, wymiary) → rysunki/przyklad_rzut.dxf/.png/.pdf

Uruchom: python przyklad_rzut.py   (w folderze z cad_dxf.py)
Tak samo wygląda każdy przerysowany arkusz: dane w słowniku, rysunek generuje cad_dxf.zapisz().
Jednostka cm, x w prawo, y w dół od narożnika lewego-górnego bryły.
"""
from cad_dxf import zapisz

T = 30   # ściana zewnętrzna
W = 12   # ścianka działowa

r = {
    "tytul": "PRZYKŁAD — rzut parteru 1:100",
    "tabliczka": ["źródło: skan arkusza A-1, str. 12 (przykład)", "dokładność ±10 cm"],
    "sciany": [
        (0, 0, 1000, T), (0, 800 - T, 1000, 800),          # ściany górna i dolna
        (0, 0, T, 800), (1000 - T, 0, 1000, 800),          # lewa i prawa
        (600, T, 600 + W, 800 - T),                        # działowa pionowa
        (600 + W, 400, 1000 - T, 400 + W),                 # działowa pozioma
    ],
    # (x0, y0, x1, y1, opis) — otwór wycinany ze ściany
    "okna": [(150, 0, 300, T, "O1 150/150"), (400, 0, 520, T, "O2 120/150"),
             (1000 - T, 120, 1000, 300, "O3 180/150"), (150, 800 - T, 450, 800, "O4 300/220")],
    # (oś, lico ściany, od, do, zawias 0|1|2, strona ±1, grubość ściany, opis)
    "drzwi": [("x", 600, 550, 640, 0, +1, W, "D1 90"),
              ("y", 400, 700, 790, 1, -1, W, "D2 90"),
              ("x", 1000 - T, 600, 700, 0, -1, T, "D3 100 wejście")],
    # (x0, x1, y0, n stopni, szer. stopnia, kierunek)
    "schody": [(T, 130, 450, 11, 28, "y")],
    "pomieszczenia": [("1", 300, 300, "salon 26,4 m²"), ("2", 800, 200, "kuchnia 12,1 m²"),
                      ("3", 800, 600, "hol 10,8 m²")],
    # (punkty łańcucha, współrzędna stała, oś łańcucha, odsunięcie linii wymiarowej)
    "wymiary": [([0, 150, 300, 400, 520, 1000], 0, "x", -80),
                ([0, 400, 800], 0, "y", -80)],
    "tabliczka_xy": (0, 950),
}

if __name__ == "__main__":
    zapisz(r, "przyklad_rzut")
