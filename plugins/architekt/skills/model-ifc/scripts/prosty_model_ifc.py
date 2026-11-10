"""prosty_model_ifc.py — wzorzec budowy modelu IFC4 z danych (ifcopenshell.api, wersja 0.8 lub nowsza).

Buduje: projekt → działka → budynek → kondygnacje; na każdej kondygnacji ściany z listy odcinków
i płytę stropu z obrysu; dach dwuspadowy jako dwie płyty. Każdy element ma styl powierzchni o nazwie
(sciany, strop, dach), po której scena Blendera (blender_render.py) dobiera materiał.

Użycie: python prosty_model_ifc.py model.ifc        (pip install ifcopenshell)
Podgląd: Autodesk Viewer (viewer.autodesk.com), BIM Vision, Bonsai w Blenderze.
Jednostki: metry. Dane kondygnacji i ścian zmień na swoje (np. z przerysowanego DXF; z cm dzielić przez 100).
"""
import math
import sys

import ifcopenshell
import ifcopenshell.api.aggregate
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcopenshell.api.style
import ifcopenshell.api.unit
import numpy as np

# --- dane (metry) ---
OBRYS = [(0, 0), (10, 0), (10, 8), (0, 8)]           # obrys zewnętrzny bryły
KONDYGNACJE = [("Parter", 0.00, 3.00), ("Piętro", 3.15, 3.00)]   # nazwa, rzędna, wysokość ścian
GRUBOSC = 0.30                                       # ściana zewnętrzna
STROP = 0.15
KALENICA = 3.0                                       # wysokość dachu ponad ostatni strop
KOLORY = {"sciany": (0.86, 0.84, 0.80), "strop": (0.6, 0.6, 0.6), "dach": (0.25, 0.25, 0.27)}


def macierz(x=0.0, y=0.0, z=0.0, kat=0.0):
    m = np.eye(4)
    c, s = math.cos(kat), math.sin(kat)
    m[:3, :3] = [[c, -s, 0], [s, c, 0], [0, 0, 1]]
    m[:3, 3] = [x, y, z]
    return m


def main(wyjscie):
    f = ifcopenshell.api.project.create_file(version="IFC4")
    projekt = ifcopenshell.api.root.create_entity(f, ifc_class="IfcProject", name="Projekt")
    ifcopenshell.api.unit.assign_unit(f)                       # metry
    model = ifcopenshell.api.context.add_context(f, context_type="Model")
    body = ifcopenshell.api.context.add_context(f, context_type="Model", context_identifier="Body",
                                                target_view="MODEL_VIEW", parent=model)
    dzialka = ifcopenshell.api.root.create_entity(f, ifc_class="IfcSite", name="Działka")
    budynek = ifcopenshell.api.root.create_entity(f, ifc_class="IfcBuilding", name="Budynek")
    ifcopenshell.api.aggregate.assign_object(f, products=[dzialka], relating_object=projekt)
    ifcopenshell.api.aggregate.assign_object(f, products=[budynek], relating_object=dzialka)

    style = {}
    for nazwa, rgb in KOLORY.items():
        st = ifcopenshell.api.style.add_style(f, name=nazwa)
        ifcopenshell.api.style.add_surface_style(
            f, style=st, ifc_class="IfcSurfaceStyleShading",
            attributes={"SurfaceColour": {"Name": None, "Red": rgb[0], "Green": rgb[1], "Blue": rgb[2]}})
        style[nazwa] = st

    def element(klasa, nazwa, rep, mac, kondygnacja, styl):
        e = ifcopenshell.api.root.create_entity(f, ifc_class=klasa, name=nazwa)
        ifcopenshell.api.geometry.edit_object_placement(f, product=e, matrix=mac)
        ifcopenshell.api.geometry.assign_representation(f, product=e, representation=rep)
        ifcopenshell.api.style.assign_representation_styles(f, shape_representation=rep, styles=[style[styl]])
        ifcopenshell.api.spatial.assign_container(f, products=[e], relating_structure=kondygnacja)
        return e

    for nazwa, z, h in KONDYGNACJE:
        kond = ifcopenshell.api.root.create_entity(f, ifc_class="IfcBuildingStorey", name=nazwa)
        kond.Elevation = z
        ifcopenshell.api.aggregate.assign_object(f, products=[kond], relating_object=budynek)
        # ściany: odcinki obrysu, oś przesunięta do środka o pół grubości
        for i, (a, b) in enumerate(zip(OBRYS, OBRYS[1:] + OBRYS[:1])):
            dl = math.dist(a, b)
            kat = math.atan2(b[1] - a[1], b[0] - a[0])
            rep = ifcopenshell.api.geometry.add_wall_representation(
                f, context=body, length=dl, height=h, thickness=GRUBOSC)
            element("IfcWall", f"{nazwa} ściana {i + 1}", rep, macierz(*a, z, kat), kond, "sciany")
        # strop nad kondygnacją z obrysu
        rep = ifcopenshell.api.geometry.add_slab_representation(
            f, context=body, depth=STROP, polyline=[(x, y) for x, y in OBRYS])
        element("IfcSlab", f"{nazwa} strop", rep, macierz(0, 0, z + h), kond, "strop")

    # dach dwuspadowy: dwie pochylone płyty nad ostatnią kondygnacją (kalenica wzdłuż osi x)
    nazwa, z, h = KONDYGNACJE[-1]
    z0 = z + h + STROP
    szer = OBRYS[2][1] - OBRYS[0][1]
    dl = OBRYS[1][0] - OBRYS[0][0]
    nachylenie = math.atan2(KALENICA, szer / 2)
    polaci = math.hypot(KALENICA, szer / 2)
    kond = budynek.IsDecomposedBy[0].RelatedObjects[-1]
    pochyl = np.eye(4)                                    # obrót wokół lokalnej osi x (spadek połaci)
    pochyl[:3, :3] = [[1, 0, 0], [0, math.cos(nachylenie), -math.sin(nachylenie)],
                      [0, math.sin(nachylenie), math.cos(nachylenie)]]
    okap = [macierz(OBRYS[0][0], OBRYS[0][1], z0, 0),     # połać od strony y = 0, wznosi się ku +y
            macierz(OBRYS[0][0] + dl, OBRYS[2][1], z0, math.pi)]   # połać przeciwna, obrócona o 180°
    for i, m in enumerate(okap):
        rep = ifcopenshell.api.geometry.add_slab_representation(
            f, context=body, depth=0.25, polyline=[(0, 0), (dl, 0), (dl, polaci), (0, polaci)])
        e = element("IfcSlab", f"dach połać {i + 1}", rep, m @ pochyl, kond, "dach")
        e.PredefinedType = "ROOF"

    f.write(wyjscie)
    print(wyjscie, "|", len(f.by_type("IfcWall")), "ścian,", len(f.by_type("IfcSlab")), "płyt")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "model.ifc")
