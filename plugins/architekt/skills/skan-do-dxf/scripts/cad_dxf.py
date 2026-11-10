"""cad_dxf.py — przerysowanie rzutów ze skanów do DXF (ezdxf). Uniwersalne narzędzie.

Użycie: w skrypcie arkusza zbuduj słownik rzutu `r` (opis kluczy niżej) i wywołaj `zapisz(r, "nazwa")`
→ rysunki/nazwa.dxf + .png + .pdf (A3). Przykład: przyklad_rzut.py. Wymaga: pip install ezdxf shapely matplotlib
(opencv-python tylko dla funkcji nakladka).

Jednostka: cm. Dane rysunków podaje się w układzie arkusza: x w prawo od zewnętrznego lica
ściany lewej (zachodniej) bryły, y w dół od zewnętrznego lica ściany górnej (północnej). W DXF oś Y
jest odwrócona (Y = -y), więc północ arkusza jest u góry, a punkt (0, 0) to narożnik NW bryły.
Dzięki temu wszystkie kondygnacje nakładają się w jednym układzie współrzędnych.

Rzut opisuje słownik z kluczami (wszystkie opcjonalne poza 'tytul'):
  sciany      [(x0, y0, x1, y1)]           prostokąty ścian
  sciany_poly [[(x, y), ...]]              ściany o dowolnym kształcie (np. skośne)
  okna        [(x0, y0, x1, y1, opis)]     otwór okienny wycinany ze ściany
  drzwi       [(os, c, a0, a1, zawias, strona, grubosc, opis)]  patrz rysuj_drzwi
  otwory      [(x0, y0, x1, y1)]           otwory bez stolarki
  schody      [(x0, x1, y0, n, s, 'y'|'x')] biegi: n stopni po s cm od y0 (lub x0)
  kreskowane  [(x0, y0, x1, y1)]           pola kreskowane z oryginału
  linie       [(warstwa, [(x, y), ...], zamknieta)]  dodatkowe linie (obrysy, granice)
  pomieszczenia [(nr, x, y, podpis)]       opisy pomieszczeń
  teksty      [(tekst, x, y, wysokosc, rot)]
  wymiary     [(punkty, stala, os, odstep)]  łańcuchy wymiarowe
  tabliczka   [linie tekstu]
"""
import math
from pathlib import Path

import ezdxf
from ezdxf.enums import TextEntityAlignment
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

KATALOG = Path.cwd() / "rysunki"   # wyniki w podfolderze rysunki/ bieżącego folderu

WARSTWY = [
    ("SCIANY", 7), ("SCIANY_KRESKOWANIE", 8), ("OKNA", 4), ("DRZWI", 2), ("SCHODY", 6),
    ("KRESKOWANE_ORYG", 1), ("WYMIARY", 3), ("OPISY", 7), ("TABLICZKA", 7),
    ("OBRYS_INNE_KONDYGNACJE", 9), ("GRANICA_DZIALKI", 1), ("UWAGI", 1), ("ELEWACJA", 7),
    ("TEREN", 3), ("OSIE", 8),
]


def pt(x, y):
    return (x, -y)


def _poly_sciany(r):
    ksztalty = [box(*s) for s in r.get("sciany", [])]
    ksztalty += [Polygon(p) for p in r.get("sciany_poly", [])]
    return unary_union(ksztalty) if ksztalty else Polygon()


def otwor_drzwi(d):
    o, c, a0, a1, _, _, t, _ = d
    return box(a0, c, a1, c + t) if o == "y" else box(c, a0, c + t, a1)


def geometria_scian(r):
    otwory = [box(*o[:4]) for o in r.get("okna", [])]
    otwory += [otwor_drzwi(d) for d in r.get("drzwi", [])]
    otwory += [box(*o) for o in r.get("otwory", [])]
    g = _poly_sciany(r)
    return g.difference(unary_union(otwory)) if otwory else g


def _polys(g):
    if g.is_empty:
        return []
    return [g] if isinstance(g, Polygon) else [p for p in g.geoms if isinstance(p, Polygon)]


def dodaj_sciany(msp, g):
    for p in _polys(g):
        for ring in [p.exterior, *p.interiors]:
            msp.add_lwpolyline([pt(x, y) for x, y in ring.coords], close=True,
                               dxfattribs={"layer": "SCIANY"})
        h = msp.add_hatch(dxfattribs={"layer": "SCIANY_KRESKOWANIE"})
        h.set_pattern_fill("ANSI31", scale=8)
        h.paths.add_polyline_path([pt(x, y) for x, y in p.exterior.coords], is_closed=True)
        for ring in p.interiors:
            h.paths.add_polyline_path([pt(x, y) for x, y in ring.coords], is_closed=True)


def tekst(msp, t, x, y, h=10, rot=0, warstwa="OPISY", align=TextEntityAlignment.MIDDLE_CENTER):
    msp.add_text(t, height=h, rotation=rot, dxfattribs={"layer": warstwa}).set_placement(
        pt(x, y), align=align)


def rysuj_drzwi(msp, d):
    """d = (os, c, a0, a1, zawias, strona, grubosc, opis)
    os 'y': ściana pozioma, lico górne na y=c, otwór a0..a1 w x; strona +1 = skrzydło w stronę +y.
    os 'x': ściana pionowa, lico lewe na x=c, otwór a0..a1 w y; strona +1 = w stronę +x.
    zawias 0 przy a0, 1 przy a1, 2 = dwuskrzydłowe."""
    o, c, a0, a1, zaw, strona, t, opis = d
    lico = c if strona < 0 else c + t

    def skrzydlo(z, szer, kier):
        if o == "y":
            hx, hy = z, lico
            koniec = (hx, hy + strona * szer)
            ang_leaf = 90 if strona < 0 else -90
            ang_close = 0 if kier > 0 else 180
        else:
            hx, hy = lico, z
            koniec = (hx + strona * szer, hy)
            ang_leaf = 0 if strona > 0 else 180
            ang_close = -90 if kier > 0 else 90
        msp.add_line(pt(hx, hy), pt(*koniec), dxfattribs={"layer": "DRZWI"})
        a, b = sorted([ang_leaf, ang_close])
        if b - a > 180:
            a, b = b, a + 360
        msp.add_arc(pt(hx, hy), szer, a, b, dxfattribs={"layer": "DRZWI"})

    szer = a1 - a0
    if zaw == 2:
        skrzydlo(a0, szer / 2, +1)
        skrzydlo(a1, szer / 2, -1)
    elif zaw == 0:
        skrzydlo(a0, szer, +1)
    else:
        skrzydlo(a1, szer, -1)
    if o == "y":
        tekst(msp, opis, (a0 + a1) / 2, c + t / 2 + strona * 45, 9)
    else:
        tekst(msp, opis, c + t / 2 + strona * 45, (a0 + a1) / 2, 9, 90)


def rysuj_okno(msp, ok, zewn=None):
    x0, y0, x1, y1, opis = ok
    msp.add_lwpolyline([pt(x0, y0), pt(x1, y0), pt(x1, y1), pt(x0, y1)], close=True,
                       dxfattribs={"layer": "OKNA"})
    if x1 - x0 >= y1 - y0:
        ym = (y0 + y1) / 2
        for dy in (-3, 3):
            msp.add_line(pt(x0, ym + dy), pt(x1, ym + dy), dxfattribs={"layer": "OKNA"})
        s = zewn if zewn is not None else (-1 if y0 <= 0 else 1)
        tekst(msp, opis, (x0 + x1) / 2, (y0 if s < 0 else y1) + s * 25, 10)
    else:
        xm = (x0 + x1) / 2
        for dx in (-3, 3):
            msp.add_line(pt(xm + dx, y0), pt(xm + dx, y1), dxfattribs={"layer": "OKNA"})
        s = zewn if zewn is not None else (-1 if x0 <= 0 else 1)
        tekst(msp, opis, (x0 if s < 0 else x1) + s * 25, (y0 + y1) / 2, 10, 90)


def rysuj_schody(msp, b):
    a0, a1, s0, n, s, kier = b
    for i in range(n + 1):
        v = s0 + i * s
        p, q = ((a0, v), (a1, v)) if kier == "y" else ((v, a0), (v, a1))
        msp.add_line(pt(*p), pt(*q), dxfattribs={"layer": "SCHODY"})
    m = (a0 + a1) / 2
    p, q = ((m, s0 + n * s), (m, s0 + 5)) if kier == "y" else ((s0 + n * s, m), (s0 + 5, m))
    msp.add_line(pt(*p), pt(*q), dxfattribs={"layer": "SCHODY"})


def lancuch(msp, punkty, stala, os, odst):
    ds = {"dimtxt": 11, "dimasz": 0, "dimtsz": 4, "dimexe": 4, "dimexo": 6, "dimdec": 0,
          "dimclrd": 3, "dimclre": 3, "dimlfac": 1}  # EZDXF domyślnie ma dimlfac=100
    for a, b in zip(punkty, punkty[1:]):
        if os == "x":
            p1, p2, base, ang = pt(a, stala), pt(b, stala), pt(a, stala + odst), 0
        else:
            p1, p2, base, ang = pt(stala, a), pt(stala, b), pt(stala + odst, a), 90
        msp.add_linear_dim(base=base, p1=p1, p2=p2, angle=ang, dimstyle="EZDXF", override=ds,
                           dxfattribs={"layer": "WYMIARY"}).render()


def zbuduj(r):
    doc = ezdxf.new("R2010", setup=True)
    doc.header["$INSUNITS"] = 5  # cm
    for n, c in WARSTWY:
        lt = "DASHED" if n in ("OBRYS_INNE_KONDYGNACJE", "GRANICA_DZIALKI") else "Continuous"
        doc.layers.add(n, color=c, linetype=lt)
    msp = doc.modelspace()
    dodaj_sciany(msp, geometria_scian(r))
    for ok in r.get("okna", []):
        rysuj_okno(msp, ok)
    for d in r.get("drzwi", []):
        rysuj_drzwi(msp, d)
    for b in r.get("schody", []):
        rysuj_schody(msp, b)
    for x0, y0, x1, y1 in r.get("kreskowane", []):
        h = msp.add_hatch(color=1, dxfattribs={"layer": "KRESKOWANE_ORYG"})
        h.set_pattern_fill("ANSI37", scale=4)
        h.paths.add_polyline_path([pt(x0, y0), pt(x1, y0), pt(x1, y1), pt(x0, y1)], is_closed=True)
    for warstwa, pts, zamk in r.get("linie", []):
        msp.add_lwpolyline([pt(*p) for p in pts], close=zamk, dxfattribs={"layer": warstwa})
    for nr, x, y, *podpis in r.get("pomieszczenia", []):
        msp.add_circle(pt(x, y), 22, dxfattribs={"layer": "OPISY"})
        tekst(msp, nr, x, y, 14)
        if podpis and podpis[0]:
            tekst(msp, podpis[0], x, y + 38, 10)
    k = r.get("skala_tekstu", 1)
    for t, x, y, h, rot in r.get("teksty", []):
        tekst(msp, t, x, y, h * k, rot)
    for w in r.get("wymiary", []):
        lancuch(msp, *w)
    if r.get("obrot"):  # obrót całego rysunku (stopnie, przeciwnie do wskazówek zegara)
        from ezdxf.math import Matrix44
        m = Matrix44.z_rotate(math.radians(r["obrot"]))
        for e in list(msp):
            e.transform(m)
    tx, ty = r.get("tabliczka_xy", (0, -700))
    h1, h2 = r.get("tabliczka_h", (20, 11))
    for i, t in enumerate([r["tytul"], *r.get("tabliczka", [])]):
        tekst(msp, t, tx, ty + i * h2 * 2.4 + (h1 - h2) * (i > 0), h1 if i == 0 else h2,
              warstwa="TABLICZKA", align=TextEntityAlignment.LEFT)
    return doc


def podglad_png(doc, path, dpi=150):
    import os
    import tempfile
    os.environ.setdefault("MPLCONFIGDIR", tempfile.gettempdir())
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from ezdxf.addons.drawing import Frontend, RenderContext
    from ezdxf.addons.drawing.config import BackgroundPolicy, ColorPolicy, Configuration
    from ezdxf.addons.drawing.matplotlib import MatplotlibBackend

    fig = plt.figure(figsize=(16, 11))
    ax = fig.add_axes([0, 0, 1, 1])
    cfg = Configuration(background_policy=BackgroundPolicy.WHITE, color_policy=ColorPolicy.BLACK)
    Frontend(RenderContext(doc), MatplotlibBackend(ax), config=cfg).draw_layout(doc.modelspace())
    fig.savefig(path, dpi=dpi)
    plt.close(fig)


def eksport(doc, path, dpi=300, margines=0.04):
    """Czytelny eksport: PNG w wysokiej rozdzielczości i wektorowy PDF, kadr dopasowany do rysunku,
    arkusz A3 (poziomo lub pionowo, wg proporcji rysunku)."""
    import os
    import tempfile
    os.environ.setdefault("MPLCONFIGDIR", tempfile.gettempdir())
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from ezdxf import bbox
    from ezdxf.addons.drawing import Frontend, RenderContext
    from ezdxf.addons.drawing.config import (BackgroundPolicy, ColorPolicy, Configuration,
                                             LineweightPolicy)
    from ezdxf.addons.drawing.matplotlib import MatplotlibBackend

    ext = bbox.extents(doc.modelspace())
    w, h = ext.size.x, ext.size.y
    rozm = (16.54, 11.69) if w >= h else (11.69, 16.54)          # A3 w calach
    fig = plt.figure(figsize=rozm)
    ax = fig.add_axes([margines, margines, 1 - 2 * margines, 1 - 2 * margines])
    cfg = Configuration(background_policy=BackgroundPolicy.WHITE, color_policy=ColorPolicy.BLACK,
                        lineweight_policy=LineweightPolicy.RELATIVE, lineweight_scaling=1.6)
    Frontend(RenderContext(doc), MatplotlibBackend(ax), config=cfg).draw_layout(doc.modelspace())
    ax.set_aspect("equal")
    ax.set_xlim(ext.extmin.x, ext.extmax.x)
    ax.set_ylim(ext.extmin.y, ext.extmax.y)
    ax.axis("off")
    fig.set_size_inches(*rozm)
    path = Path(path)
    fig.savefig(path.with_suffix(".png"), dpi=dpi)
    fig.savefig(path.with_suffix(".pdf"))
    plt.close(fig)


def nakladka(r, zdjecie, src_px, dst_cm, path, zakres=(-200, -600, 2300, 1700), s=1.0):
    """Rektyfikacja zdjęcia arkusza (4 punkty src_px ↔ dst_cm) i nałożenie ścian rzutu."""
    import cv2
    import numpy as np
    x0, y0, x1, y1 = zakres
    dst = (np.float32(dst_cm) - [x0, y0]) * s
    hm = cv2.getPerspectiveTransform(np.float32(src_px), dst.astype(np.float32))
    img = cv2.imread(str(zdjecie))
    out = cv2.warpPerspective(img, hm, (int((x1 - x0) * s), int((y1 - y0) * s)))
    out = cv2.addWeighted(out, 0.6, np.full_like(out, 255), 0.4, 0)
    for p in _polys(geometria_scian(r)):
        for ring in [p.exterior, *p.interiors]:
            pts = ((np.array(ring.coords) - [x0, y0]) * s).astype(np.int32)
            cv2.polylines(out, [pts], True, (0, 0, 255), 2)
    for ok in r.get("okna", []):
        a = ((np.array(ok[:4]) - [x0, y0, x0, y0]) * s).astype(int)
        cv2.rectangle(out, (a[0], a[1]), (a[2], a[3]), (255, 128, 0), 2)
    for _, pts, zamk in r.get("linie", []):
        a = ((np.array(pts) - [x0, y0]) * s).astype(np.int32)
        cv2.polylines(out, [a], zamk, (0, 160, 0), 2)
    cv2.imwrite(str(path), out)


def zapisz(r, nazwa):
    KATALOG.mkdir(parents=True, exist_ok=True)
    doc = zbuduj(r)
    dxf = KATALOG / f"{nazwa}.dxf"
    doc.saveas(dxf)
    eksport(doc, dxf)
    print("zapisano", dxf)
    return dxf
