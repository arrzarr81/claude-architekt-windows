"""sprawdz_projekt.py — kontrola wyników projektu (rysunki DXF, model IFC, eksport OBJ, rendery), zanim uznasz etap za gotowy.
Użycie (z głównego folderu projektu, Pythonem z ~/.architekt/config.json):
  python sprawdz_projekt.py .                     → sprawdza wszystko, raport w weryfikacja/raport_<data>.md
  python sprawdz_projekt.py . --zapisz-wzorce     → zapamiętuje obecne liczby (ściany, kondygnacje, obiekty DXF)
                                                    jako wzorzec; tylko po zamierzonej zmianie i zgodzie użytkownika
Kod wyjścia 0 = PASS, 1 = FAIL. Ostatnia linia: WERYFIKACJA: PASS|FAIL (n/m).
Sprawdza:
  rysunki/*.dxf  otwiera się, ma obiekty; rzut: ściany w cm (1–200 m), narożnik NW bryły w 0,0; jest PDF i PNG obok
  model/*.ifc    jednostka metr, kondygnacje z rosnącą rzędną, ściany, każda ściana/płyta ze stylem (materiał renderu),
                 wymiary bryły 1–200 m (pomyłka cm/m), zgodność szerokości z rzutem DXF (±10 cm)
  render/*.obj   obiekty, każdy materiał opisany w .mtl, brak „bez_stylu”
  render/*.png   obraz nie jest czarny ani jednolity
  weryfikacja/wzorce.json  te same liczby co we wzorcu (zmiana = FAIL, dopóki użytkownik jej nie zatwierdzi)
Wymaga: ezdxf, ifcopenshell, pillow, pymupdf (instaluje je skill przygotuj-komputer).
"""
import datetime
import json
import sys
from pathlib import Path


class Wyniki:
    def __init__(self):
        self.w = []          # (obszar, plik, opis, status: ok|fail|uwaga, szczegóły)

    def ok(self, obszar, plik, opis, warunek, sz=""):
        self.w.append((obszar, plik, opis, "ok" if warunek else "fail", str(sz)))
        return bool(warunek)

    def uwaga(self, obszar, plik, opis, sz=""):
        self.w.append((obszar, plik, opis, "uwaga", str(sz)))


def obraz_niepusty(p):
    from PIL import Image, ImageStat
    im = Image.open(p).convert("L")
    im.thumbnail((400, 400))
    s = ImageStat.Stat(im)
    return 8 < s.mean[0] < 247 and s.stddev[0] > 6, f"jasność {s.mean[0]:.0f}, odchylenie {s.stddev[0]:.1f}"


def rysunek_niepusty(p):
    """Rysunek kreskowy na białym tle: wystarczy, że ma ciemne linie (≥ 0,3% pikseli)."""
    from PIL import Image
    im = Image.open(p).convert("L")
    im.thumbnail((1200, 1200))
    h = im.histogram()
    ciemne = sum(h[:160]) / max(1, sum(h))
    return ciemne >= 0.003, f"{ciemne * 100:.1f}% pikseli z linią"


def sprawdz_dxf(proj, R, liczby):
    import ezdxf
    from ezdxf import bbox
    try:
        import pymupdf
    except ImportError:
        pymupdf = None
    szer_rzutow = {}
    for p in sorted((proj / "rysunki").glob("*.dxf")):
        n = p.name
        try:
            doc = ezdxf.readfile(p)
        except Exception as e:
            R.ok("DXF", n, "plik się otwiera", False, e)
            continue
        msp = doc.modelspace()
        warstwy = {}
        for e in msp:
            warstwy[e.dxf.layer] = warstwy.get(e.dxf.layer, 0) + 1
        liczby[n] = {"obiekty": len(msp), **{f"warstwa {k}": v for k, v in sorted(warstwy.items())}}
        R.ok("DXF", n, "ma obiekty", len(msp) > 0, f"{len(msp)} obiektów, {len(warstwy)} warstw")
        sc = msp.query('*[layer=="SCIANY"]')
        if len(sc) and "rzut" in n.lower():
            ex = bbox.extents(sc)
            w, h = ex.size.x, ex.size.y
            R.ok("DXF", n, "ściany w centymetrach (bryła 1–200 m)", 100 <= max(w, h) <= 20000, f"{w:.0f} × {h:.0f} cm")
            R.ok("DXF", n, "narożnik NW bryły w punkcie 0,0", abs(ex.extmin.x) <= 5 and abs(ex.extmax.y) <= 5,
                 f"min x {ex.extmin.x:.1f}, max y {ex.extmax.y:.1f} cm")
            szer_rzutow[n] = (w, h)
        for rozsz in (".pdf", ".png"):
            q = p.with_suffix(rozsz)
            if not q.exists():
                R.uwaga("DXF", n, f"brak {q.name} (podgląd z cad_dxf.zapisz)")
            elif rozsz == ".pdf" and pymupdf is None:
                R.ok("DXF", q.name, "PDF ma nagłówek %PDF (bez pymupdf)", q.read_bytes()[:5] == b"%PDF-")
            elif rozsz == ".pdf":
                d = pymupdf.open(q)
                R.ok("DXF", q.name, "PDF się otwiera", len(d) >= 1, f"{len(d)} str.")
            else:
                ok, sz = rysunek_niepusty(q)
                R.ok("DXF", q.name, "podgląd PNG ma rysunek", ok, sz)
    return szer_rzutow


def sprawdz_ifc(proj, R, liczby, szer_rzutow):
    import ifcopenshell
    import ifcopenshell.geom
    for p in sorted((proj / "model").glob("*.ifc")):
        n = p.name
        try:
            f = ifcopenshell.open(str(p))
        except Exception as e:
            R.ok("IFC", n, "plik się otwiera", False, e)
            continue
        import ifcopenshell.util.element
        import ifcopenshell.util.unit
        skala = ifcopenshell.util.unit.calculate_unit_scale(f)          # jednostka pliku → metry
        kond = sorted(f.by_type("IfcBuildingStorey"), key=lambda k: k.Elevation or 0)
        rz = [k.Elevation or 0 for k in kond]
        R.ok("IFC", n, "kondygnacje z różnymi rzędnymi", len(kond) >= 1 and len(set(rz)) == len(rz),
             ", ".join(f"{k.Name} {k.Elevation or 0:+.2f}" for k in kond))
        sciany, plyty = f.by_type("IfcWall"), f.by_type("IfcSlab")
        R.ok("IFC", n, "są ściany", len(sciany) > 0, f"{len(sciany)} ścian, {len(plyty)} płyt")
        liczby[n] = {"kondygnacje": len(kond), "sciany": len(sciany), "plyty": len(plyty),
                     "style": sorted({s.Name for s in f.by_type("IfcSurfaceStyle") if s.Name})}
        styl_rep = set()
        for si in f.by_type("IfcStyledItem"):
            if si.Item:
                styl_rep.add(si.Item.id())
        bez = []
        for e in sciany + plyty:
            rep = e.Representation
            items = [it for r in (rep.Representations if rep else []) for it in r.Items]
            if items and not any(it.id() in styl_rep for it in items):
                bez.append(e.Name or e.GlobalId)
        R.ok("IFC", n, "każda ściana i płyta ma styl (materiał w renderze)", not bez, bez[:3])
        s = ifcopenshell.geom.settings()
        s.set("use-world-coords", True)
        zle_rz, inne = [], []
        for k in kond:      # rzędna kondygnacji (w jednostkach pliku) = spód większości jej ścian (geometria w metrach)
            rz_m = (k.Elevation or 0) * skala
            spody = []
            for e in ifcopenshell.util.element.get_decomposition(k):
                if e.is_a("IfcWall"):
                    try:
                        spody.append((min(ifcopenshell.geom.create_shape(s, e).geometry.verts[2::3]), e.Name))
                    except Exception:
                        pass
            if not spody:
                continue
            odst = [(z, nm) for z, nm in spody if abs(z - rz_m) > 0.05]
            if len(odst) * 2 > len(spody):      # szyb windy, ściana oporowa mogą odstawać; większość nie
                zle_rz.append(f"{k.Name}: rzędna {rz_m:+.3f} m, ściany od {min(z for z, _ in spody):+.2f} m")
            inne += [f"{k.Name}/{nm} {z:+.2f}" for z, nm in odst]
        R.ok("IFC", n, "rzędne kondygnacji zgodne ze ścianami (jednostki pliku)", not zle_rz,
             "; ".join(zle_rz[:2]) or f"jednostka pliku = {skala:g} m" +
             (f"; ściany poza rzędną swojej kondygnacji: {', '.join(inne[:3])}" if inne else ""))
        mn, mx = [1e9] * 3, [-1e9] * 3
        it = ifcopenshell.geom.iterator(s, f, include=sciany or None)
        if sciany and it.initialize():
            while True:
                v = it.get().geometry.verts
                for i in range(3):
                    mn[i] = min(mn[i], min(v[i::3]))
                    mx[i] = max(mx[i], max(v[i::3]))
                if not it.next():
                    break
            w, h, z = (mx[i] - mn[i] for i in range(3))
            R.ok("IFC", n, "bryła 1–200 m (nie cm wpisane jako m)", 1 <= max(w, h) <= 200, f"{w:.2f} × {h:.2f} × {z:.2f} m")
            if szer_rzutow:
                rz_n, (dw, dh) = max(szer_rzutow.items(), key=lambda kv: kv[1][0] * kv[1][1])
                opis = f"obrys ścian zgodny z {rz_n} (±10 cm)"
                sz = f"IFC {w:.2f} × {h:.2f} m, DXF {dw / 100:.2f} × {dh / 100:.2f} m"
                if abs(w - dw / 100) <= 0.10 and abs(h - dh / 100) <= 0.10:
                    R.ok("IFC", n, opis, True, sz)
                else:   # model może obejmować więcej niż największy rzut (przybudówki) → tylko uwaga
                    R.uwaga("IFC", n, opis, sz)


def sprawdz_render(proj, R, liczby):
    for p in sorted((proj / "render").glob("*.obj")):
        n = p.name
        t = p.read_text(encoding="utf-8", errors="replace").splitlines()
        obiekty = sum(1 for l in t if l.startswith("o "))
        uzyte = {l.split(None, 1)[1] for l in t if l.startswith("usemtl ")}
        mtl = p.with_suffix(".mtl")
        opisane = {l.split(None, 1)[1] for l in mtl.read_text().splitlines() if l.startswith("newmtl ")} if mtl.exists() else set()
        liczby[n] = {"obiekty": obiekty, "materialy": sorted(uzyte)}
        R.ok("OBJ", n, "ma obiekty", obiekty > 0, f"{obiekty} obiektów")
        R.ok("OBJ", n, "każdy materiał opisany w .mtl", uzyte <= opisane, sorted(uzyte - opisane)[:3])
        if "bez_stylu" in uzyte:
            R.uwaga("OBJ", n, "elementy bez stylu w IFC → szary materiał w renderze")
    for p in sorted((proj / "render").glob("*.png")):
        ok, sz = obraz_niepusty(p)
        R.ok("render", p.name, "obraz nie jest czarny ani jednolity", ok, sz)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    proj = Path(sys.argv[1]).resolve()
    zapisz = "--zapisz-wzorce" in sys.argv
    R, liczby = Wyniki(), {}
    szer = sprawdz_dxf(proj, R, liczby) if (proj / "rysunki").is_dir() else {}
    if (proj / "model").is_dir():
        sprawdz_ifc(proj, R, liczby, szer)
    if (proj / "render").is_dir():
        sprawdz_render(proj, R, liczby)
    if not R.w:
        R.ok("projekt", str(proj), "są wyniki do sprawdzenia (rysunki/, model/, render/)", False)
    wz_p = proj / "weryfikacja" / "wzorce.json"
    if zapisz:
        wz_p.parent.mkdir(exist_ok=True)
        wz_p.write_text(json.dumps(liczby, ensure_ascii=False, indent=1), encoding="utf-8")
        print("zapisano wzorce:", wz_p)
    elif wz_p.exists():
        wz = json.loads(wz_p.read_text(encoding="utf-8"))
        for plik, war in wz.items():
            if plik not in liczby:
                R.ok("wzorzec", plik, "plik ze wzorca istnieje", False, "brak pliku")
                continue
            rozne = [f"{k}: {v} → {liczby[plik].get(k)}" for k, v in war.items() if liczby[plik].get(k) != v]
            R.ok("wzorzec", plik, "liczby jak we wzorcu", not rozne, "; ".join(rozne[:4]))
    lin = [f"# Weryfikacja projektu — {datetime.datetime.now():%Y-%m-%d %H:%M}", "",
           "| obszar | plik | sprawdzenie | wynik | szczegóły |", "|---|---|---|---|---|"]
    ikona = {"ok": "✅", "fail": "❌", "uwaga": "⚠️"}
    for ob, pl, op, st, sz in R.w:
        lin.append(f"| {ob} | {pl} | {op} | {ikona[st]} | {sz.replace('|', '/')} |")
        if st != "ok":
            print(f"{'FAIL ' if st == 'fail' else 'UWAGA'} {ob} {pl}: {op} — {sz}")
    rap = proj / "weryfikacja" / f"raport_{datetime.datetime.now():%Y%m%d_%H%M%S}.md"
    rap.parent.mkdir(exist_ok=True)
    rap.write_text("\n".join(lin) + "\n", encoding="utf-8")
    sprawdzenia = [r for r in R.w if r[3] != "uwaga"]
    n = sum(r[3] == "ok" for r in sprawdzenia)
    print("raport:", rap)
    print(f"WERYFIKACJA: {'PASS' if n == len(sprawdzenia) else 'FAIL'} ({n}/{len(sprawdzenia)})")
    sys.exit(0 if n == len(sprawdzenia) else 1)


if __name__ == "__main__":
    main()
