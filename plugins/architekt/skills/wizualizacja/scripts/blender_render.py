"""blender_render.py — uniwersalna scena i render budynku z pliku OBJ (eksport z IFC: ifc_do_obj.py).

Robi: import OBJ, materiały PBR po nazwie materiału (sciany, dach, okna, szklo, strop, teren ...),
teren, niebo fizyczne + słońce, kamera ustawiona automatycznie na bryłę, render Cycles na GPU
(wybiera sama: OptiX / CUDA / HIP / oneAPI / Metal, inaczej CPU), odszumianie, AgX.

Użycie (bez okna Blendera):
  Windows:  "C:\\Program Files\\Blender Foundation\\Blender 4.2\\blender.exe" -b -P blender_render.py -- model.obj render.png
  macOS:    /Applications/Blender.app/Contents/MacOS/Blender -b -P blender_render.py -- model.obj render.png
Parametry opcjonalne (po kolei): próbki=64  szerokość=1600  azymut_kamery=215  wysokość_kamery_st=18
  słońce_azymut=150  słońce_wysokość=35
Przykład podglądu: ... -- model.obj podglad.png 16 800      finał: ... -- model.obj final.png 256 2400
Działa w Blenderze 4.x i 5.x.
"""
import math
import os
import sys

import bpy
from mathutils import Vector

# słowo w nazwie materiału -> (kolor RGB jak w sRGB 0–1, chropowatość, metaliczność, przezroczystość szkła)
MATERIALY = [
    (("szkl", "glass", "szyb"), ((0.75, 0.82, 0.85), 0.02, 0.0, True)),
    (("okn", "window", "ram", "drzw", "door"), ((0.18, 0.18, 0.19), 0.4, 0.0, False)),
    (("dach", "roof", "dachow"), ((0.20, 0.20, 0.22), 0.6, 0.0, False)),
    (("strop", "slab", "beton", "concrete"), ((0.55, 0.55, 0.53), 0.8, 0.0, False)),
    (("balustr", "railing", "stal", "steel"), ((0.30, 0.30, 0.32), 0.35, 0.8, False)),
    (("drew", "wood", "deska"), ((0.45, 0.30, 0.18), 0.6, 0.0, False)),
    (("scian", "wall", "tynk", "elew"), ((0.86, 0.84, 0.80), 0.85, 0.0, False)),
]


def argumenty():
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if len(a) < 2:
        raise SystemExit(__doc__)
    liczby = [float(x) for x in a[2:]]
    dom = [64, 1600, 215, 18, 150, 35]
    p = liczby + dom[len(liczby):]
    return a[0], a[1], int(p[0]), int(p[1]), p[2], p[3], p[4], p[5]


def lin(c):
    """Kolor podany jak w programach graficznych (sRGB 0–1) -> wartość liniowa, której używa Blender."""
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)


def material(nazwa, kolor, chrop, metal, szklo):
    kolor = lin(kolor)
    m = bpy.data.materials.new(nazwa)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*kolor, 1)
    b.inputs["Roughness"].default_value = chrop
    b.inputs["Metallic"].default_value = metal
    if szklo:
        for k in ("Transmission Weight", "Transmission"):        # nazwa zależy od wersji Blendera
            if k in b.inputs:
                b.inputs[k].default_value = 1.0
        b.inputs["IOR"].default_value = 1.45
    return m


def podmien_materialy(obiekty):
    cache = {}
    for o in obiekty:
        for slot in o.material_slots:
            if not slot.material:
                continue
            n = slot.material.name.lower()
            for slowa, par in MATERIALY:
                if any(s in n for s in slowa):
                    key = slowa[0]
                    if key not in cache:
                        cache[key] = material("PBR_" + key, *par)
                    slot.material = cache[key]
                    break


def gpu(scena):
    scena.render.engine = "CYCLES"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    for typ in ("OPTIX", "CUDA", "HIP", "ONEAPI", "METAL"):
        try:
            prefs.compute_device_type = typ
            prefs.get_devices()
            urz = [d for d in prefs.devices if d.type == typ]
            if urz:
                for d in prefs.devices:
                    d.use = d.type == typ
                scena.cycles.device = "GPU"
                print("GPU:", typ, [d.name for d in urz])
                return
        except TypeError:
            continue
    scena.cycles.device = "CPU"
    print("GPU niedostępne — render na CPU")


def niebo(scena, az, el):
    w = bpy.data.worlds.new("niebo")
    scena.world = w
    w.use_nodes = True
    nt = w.node_tree
    sky = nt.nodes.new("ShaderNodeTexSky")
    for typ in ("MULTIPLE_SCATTERING", "NISHITA", "HOSEK_WILKIE"):
        try:
            sky.sky_type = typ
            break
        except TypeError:
            continue
    if hasattr(sky, "sun_elevation"):
        sky.sun_elevation = math.radians(el)
        sky.sun_rotation = math.radians(90 - az)
        sky.sun_disc = False
    bg = nt.nodes["Background"]
    bg.inputs["Strength"].default_value = 0.4
    nt.links.new(sky.outputs["Color"], bg.inputs["Color"])
    s = bpy.data.objects.new("slonce", bpy.data.lights.new("slonce", "SUN"))
    s.data.energy = 4.0
    s.data.angle = math.radians(0.8)
    s.data.color = (1.0, 0.93, 0.85)
    # kierunek światła: azymut od północy (+Y) zgodnie z ruchem wskazówek, wysokość nad horyzontem
    s.rotation_euler = (math.radians(90 - el), 0, math.radians(180 - az))
    scena.collection.objects.link(s)


def main():
    obj, out, probki, szer, az_k, el_k, az_s, el_s = argumenty()
    obj = os.path.abspath(obj)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    bpy.ops.wm.obj_import(filepath=obj, forward_axis="Y", up_axis="Z")
    budynek = [o for o in sc.objects if o.type == "MESH"]
    podmien_materialy(budynek)
    print("materiały:", sorted({s.material.name for o in budynek for s in o.material_slots if s.material}))

    pkt = [o.matrix_world @ Vector(c) for o in budynek for c in o.bound_box]
    mn = Vector((min(p.x for p in pkt), min(p.y for p in pkt), min(p.z for p in pkt)))
    mx = Vector((max(p.x for p in pkt), max(p.y for p in pkt), max(p.z for p in pkt)))
    srodek, rozm = (mn + mx) / 2, (mx - mn)

    bpy.ops.mesh.primitive_plane_add(size=max(rozm.x, rozm.y) * 80, location=(srodek.x, srodek.y, mn.z - 0.02))
    sc.objects[-1].data.materials.append(material("teren", (0.30, 0.40, 0.22), 0.9, 0.0, False))

    niebo(sc, az_s, el_s)

    cam = bpy.data.objects.new("kamera", bpy.data.cameras.new("kamera"))
    cam.data.lens = 30
    sc.collection.objects.link(cam)
    odl = max(rozm.x, rozm.y, rozm.z) * 2.2
    a, e = math.radians(az_k), math.radians(el_k)
    cam.location = srodek + Vector((math.sin(a) * math.cos(e), math.cos(a) * math.cos(e), math.sin(e))) * odl
    cam.rotation_euler = (srodek - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.camera = cam

    gpu(sc)
    sc.cycles.samples = probki
    sc.cycles.use_denoising = True
    sc.render.resolution_x = szer
    sc.render.resolution_y = int(szer * 2 / 3)
    try:
        sc.view_settings.view_transform = "AgX"
        sc.view_settings.look = "AgX - Medium High Contrast"
    except TypeError:
        sc.view_settings.view_transform = "Filmic"
    sc.view_settings.exposure = -0.3
    sc.render.filepath = os.path.abspath(out)   # Blender wymaga ścieżki bezwzględnej
    bpy.ops.render.render(write_still=True)
    print("zapisano", out)


main()
