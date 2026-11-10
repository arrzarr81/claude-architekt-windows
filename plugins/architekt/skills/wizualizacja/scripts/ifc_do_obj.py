"""Eksport geometrii IFC do OBJ + MTL dla Blendera (wizualizacje 3D).

Obiekt OBJ = element IFC, nazwa "<klasa>|<nazwa>|<GlobalId>"; materiał = nazwa stylu IFC (sciany, okna, szklo...),
więc scena w Blenderze (blender_render.py) podmienia je na materiały PBR po nazwie. Współrzędne światowe IFC
w metrach, Z w górę (X = x domu, Y = -y). Pomijam strefy, otwory i adnotacje.

Użycie: python ifc_do_obj.py <plik.ifc> <plik.obj>    (pip install ifcopenshell)
"""
import sys
from pathlib import Path

import ifcopenshell
import ifcopenshell.geom

POMIN = ("IfcSpace", "IfcOpeningElement", "IfcAnnotation")


def eksport(ifc, obj):
    f = ifcopenshell.open(ifc)
    s = ifcopenshell.geom.settings()
    s.set("use-world-coords", True)
    obj = Path(obj)
    mtl = obj.with_suffix(".mtl")
    kolory, v0, linie = {}, 1, [f"mtllib {mtl.name}"]
    styl = {f"{c.is_a()}-{c.id()}": st.Name for st in f.by_type("IfcSurfaceStyle") for c in st.Styles}
    it = ifcopenshell.geom.iterator(s, f, include=[e for e in f.by_type("IfcProduct") if not any(e.is_a(c) for c in POMIN)])
    if not it.initialize():
        raise SystemExit("brak geometrii")
    n = 0
    while True:
        sh = it.get()
        e = f.by_id(sh.id)
        g = sh.geometry
        v, fa, mid = g.verts, g.faces, g.material_ids
        mats = [styl.get(m.name, m.name).replace(" ", "_") or "bez_stylu" for m in g.materials] or ["bez_stylu"]
        for m, mm in zip(mats, g.materials or []):
            kolory.setdefault(m, (tuple(mm.diffuse.components) if hasattr(mm.diffuse, "components")
                                  else tuple(mm.diffuse), getattr(mm, "transparency", 0.0) or 0.0))
        nazwa = f"{e.is_a()}|{(e.Name or '').replace(' ', '_')}|{e.GlobalId}"
        linie.append(f"o {nazwa}")
        linie += [f"v {v[i]:.4f} {v[i + 1]:.4f} {v[i + 2]:.4f}" for i in range(0, len(v), 3)]
        akt = None
        for k in range(0, len(fa), 3):
            m = mats[mid[k // 3]] if mid and mid[k // 3] >= 0 else mats[0]
            if m != akt:
                linie.append(f"usemtl {m}")
                akt = m
            linie.append(f"f {fa[k] + v0} {fa[k + 1] + v0} {fa[k + 2] + v0}")
        v0 += len(v) // 3
        n += 1
        if not it.next():
            break
    obj.write_text("\n".join(linie) + "\n")
    m = []
    for k, (c, t) in kolory.items():
        m += [f"newmtl {k}", f"Kd {c[0]:.3f} {c[1]:.3f} {c[2]:.3f}", f"d {1 - t:.3f}", ""]
    mtl.write_text("\n".join(m))
    print(obj, "|", n, "elementow,", len(kolory), "materialow:", ", ".join(sorted(kolory)))


if __name__ == "__main__":
    eksport(*sys.argv[1:3])
