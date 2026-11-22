"""pobierz_dzialke.py — dane o nieruchomości z publicznych usług GUGiK, zanim cokolwiek zaprojektujemy.

Wejście (jedno z):  --adres "Jachranka, ul. X 12"   |  --dzialka "Jachranka 123" albo "140804_5.0010.123"
                    |  --xy 21.38,52.47 (WGS84 dł,szer, np. z linku Map Google)  |  --xy2180 638500,486500 (E,N)
Wynik w <folder>/ (domyślnie otoczenie/):
  dzialka.json   numer, TERYT, powierzchnia, długości boków, wierzchołki w EPSG:2180 i w metrach lokalnych
                 (x na wschód, y na południe, 0,0 = NW narożnik prostokąta otaczającego działkę; ten sam układ co ogrod.json),
                 sąsiednie działki (numery + obrysy), budynki z ewidencji na działce i u sąsiadów (obrysy, pow.)
  orto.jpg       ortofotomapa (geoportal, ok. 10 cm/px), działka + 25 m zapasu, góra = północ
  ewidencja.png  mapa ewidencyjna (granice, numery działek, budynki) w tym samym kadrze
  podglad.png    ortofoto z naniesioną granicą działki i numerami sąsiadów — do sprawdzenia przez użytkownika
Tylko biblioteka standardowa + Pillow. Sieć: services.gugik.gov.pl, uldk.gugik.gov.pl, mapy.geoportal.gov.pl,
integracja.gugik.gov.pl (przekierowuje na serwer WMS gminy/powiatu — jego host bywa inny w każdym powiecie).
"""
import argparse, json, math, ssl, sys, urllib.parse, urllib.request
from pathlib import Path

UA = {"User-Agent": "pobierz-dzialke/0.1"}
# Geoportal ma niepełny łańcuch certyfikatów (curl: kod 60). Mapy publiczne, tylko odczyt → bez weryfikacji, tylko ten host.
_BEZ_WERYFIKACJI = ssl._create_unverified_context()


def pobierz(url, binarnie=False, timeout=60):
    host = urllib.parse.urlparse(url).hostname or ""
    ctx = _BEZ_WERYFIKACJI if host == "mapy.geoportal.gov.pl" else None
    for proba in range(3):  # serwery GUGiK potrafią urwać odpowiedź (IncompleteRead) — ponów
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout, context=ctx) as r:
                dane = r.read()
            break
        except Exception:
            if proba == 2:
                raise
    return dane if binarnie else dane.decode("utf-8", "replace")


# ---------- lokalizacja ----------
def geokoduj(adres):
    j = json.loads(pobierz("https://services.gugik.gov.pl/uug/?request=GetAddress&address=" + urllib.parse.quote(adres)))
    wyn = list((j.get("results") or {}).values())
    if not wyn:
        sys.exit(f"Geokoder nie znalazł adresu: {adres!r}. Podaj numer działki albo punkt z mapy (--xy).")
    w = wyn[0]
    return float(w["x"]), float(w["y"]), f'{w.get("city")}, {w.get("street") or ""} {w.get("number")}'.strip()


def wgs84_do_2180(lon, lat):
    """Odwzorowanie Gaussa-Krügera PUWG 1992 (GRS80), dokładność ~cm."""
    a, f = 6378137.0, 1 / 298.257222101
    e2 = f * (2 - f); ep2 = e2 / (1 - e2)
    fi, la = math.radians(lat), math.radians(lon - 19.0)
    N = a / math.sqrt(1 - e2 * math.sin(fi) ** 2)
    t, c = math.tan(fi), ep2 * math.cos(fi) ** 2
    A = la * math.cos(fi)
    e4, e6 = e2 * e2, e2 ** 3
    M = a * ((1 - e2 / 4 - 3 * e4 / 64 - 5 * e6 / 256) * fi - (3 * e2 / 8 + 3 * e4 / 32 + 45 * e6 / 1024) * math.sin(2 * fi)
             + (15 * e4 / 256 + 45 * e6 / 1024) * math.sin(4 * fi) - (35 * e6 / 3072) * math.sin(6 * fi))
    x = M + N * t * (A ** 2 / 2 + (5 - t * t + 9 * c + 4 * c * c) * A ** 4 / 24 + (61 - 58 * t * t + t ** 4) * A ** 6 / 720)
    y = N * (A + (1 - t * t + c) * A ** 3 / 6 + (5 - 18 * t * t + t ** 4 + 72 * c - 58 * ep2) * A ** 5 / 120)
    m0 = 0.9993
    return y * m0 + 500000, x * m0 - 5300000  # E, N


# ---------- ULDK ----------
def _wkt_do_punktow(wkt):
    wkt = wkt.split(";", 1)[-1]
    srodek = wkt[wkt.index("((") + 2: wkt.index(")")].lstrip("(")  # POLYGON i MULTIPOLYGON: pierwszy pierścień
    pkt = [tuple(map(float, p.split())) for p in srodek.split(",")]
    return pkt[:-1] if pkt[0] == pkt[-1] else pkt


def uldk(zapytanie, wynik="id,voivodeship,county,commune,region,parcel,geom_wkt"):
    t = pobierz(f"https://uldk.gugik.gov.pl/?{zapytanie}&result={wynik}").strip().splitlines()
    if not t or t[0].strip() != "0" and not t[0].strip().isdigit():
        return []
    if t[0].strip() == "-1":
        return []
    out = []
    for linia in t[1:]:
        pola = linia.split("|")
        out.append(dict(zip(wynik.split(","), pola)))
    return out


def dzialka_po_xy(e, n):
    r = uldk(f"request=GetParcelByXY&xy={e},{n},2180")
    return r[0] if r else None


def budynek_po_xy(e, n):
    r = uldk(f"request=GetBuildingByXY&xy={e},{n},2180", "id,geom_wkt")
    return r[0] if r else None


# ---------- geometria ----------
def pole(p):
    return abs(sum(p[i][0] * p[i - 1][1] - p[i - 1][0] * p[i][1] for i in range(len(p)))) / 2


def w_wielokacie(x, y, p):
    w = False
    for i in range(len(p)):
        (x1, y1), (x2, y2) = p[i - 1], p[i]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            w = not w
    return w


def punkty_probne(p, odsuniecie=1.0, krok=4.0):
    """Punkty tuż za granicą działki, co ~krok m wzdłuż każdego boku — do znalezienia sąsiadów."""
    out = []
    for i in range(len(p)):
        (x1, y1), (x2, y2) = p[i - 1], p[i]
        dl = math.hypot(x2 - x1, y2 - y1)
        if dl < 0.5:
            continue
        nx, ny = (y2 - y1) / dl, -(x2 - x1) / dl
        k = max(1, int(dl // krok))
        for j in range(k):
            s = (j + 0.5) / k
            mx, my = x1 + (x2 - x1) * s, y1 + (y2 - y1) * s
            for zn in (1, -1):
                px, py = mx + zn * nx * odsuniecie, my + zn * ny * odsuniecie
                if not w_wielokacie(px, py, p):
                    out.append((px, py))
                    break
    return out


def siatka_wewnatrz(p, krok=4.0, maks=40):
    """Punkty wewnątrz obrysu co ~krok m; przy dużym obrysie krok rośnie, żeby nie przekroczyć ~maks zapytań do ULDK."""
    xs, ys = [q[0] for q in p], [q[1] for q in p]
    krok = max(krok, math.sqrt(pole(p) / maks))
    x = min(xs) + krok / 2
    while x < max(xs):
        y = min(ys) + krok / 2
        while y < max(ys):
            if w_wielokacie(x, y, p):
                yield x, y
            y += krok
        x += krok


# ---------- mapy ----------
def wms(url_baza, warstwy, bbox, szer, wys, fmt):
    q = dict(SERVICE="WMS", VERSION="1.1.1", REQUEST="GetMap", LAYERS=warstwy, STYLES="", SRS="EPSG:2180",
             BBOX=",".join(f"{v:.2f}" for v in bbox), WIDTH=szer, HEIGHT=wys, FORMAT=fmt, TRANSPARENT="TRUE")
    return pobierz(url_baza + "?" + urllib.parse.urlencode(q), binarnie=True, timeout=120)


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--adres"); g.add_argument("--dzialka"); g.add_argument("--xy"); g.add_argument("--xy2180")
    ap.add_argument("--folder", default="otoczenie")
    ap.add_argument("--zapas", type=float, default=25.0, help="m wokół działki na mapach")
    ap.add_argument("--px", type=float, default=0.10, help="m na piksel ortofoto")
    a = ap.parse_args()
    out = Path(a.folder); out.mkdir(parents=True, exist_ok=True)

    adres = None
    if a.dzialka:
        r = uldk("request=GetParcelByIdOrNr&id=" + urllib.parse.quote(a.dzialka))
        if not r:
            sys.exit(f"ULDK nie zna działki {a.dzialka!r} (format: 'Obręb 123' albo '140804_5.0010.123').")
        if len(r) > 1:
            print("UWAGA: kilka działek pasuje, biorę pierwszą:", ", ".join(x["id"] for x in r))
        dz = r[0]
    else:
        if a.adres:
            e, n, adres = geokoduj(a.adres)
        elif a.xy:
            lon, lat = map(float, a.xy.split(","))
            e, n = wgs84_do_2180(lon, lat)
        else:
            e, n = map(float, a.xy2180.split(","))
        dz = dzialka_po_xy(e, n)
        if not dz:
            sys.exit("Brak działki w tym punkcie (ULDK).")

    P = _wkt_do_punktow(dz["geom_wkt"])
    minE, maxE = min(p[0] for p in P), max(p[0] for p in P)
    minN, maxN = min(p[1] for p in P), max(p[1] for p in P)
    lok = lambda p: (round(p[0] - minE, 2), round(maxN - p[1], 2))
    boki = [round(math.hypot(P[i][0] - P[i - 1][0], P[i][1] - P[i - 1][1]), 2) for i in range(len(P))]

    sasiedzi = {}
    for x, y in punkty_probne(P):
        s = dzialka_po_xy(x, y)
        if s and s["id"] != dz["id"] and s["id"] not in sasiedzi:
            sasiedzi[s["id"]] = s

    budynki = {}
    for x, y in list(siatka_wewnatrz(P)):
        b = budynek_po_xy(x, y)
        if b and b["id"] not in budynki:
            budynki[b["id"]] = dict(b, gdzie="na działce")
    for sid, s in sasiedzi.items():
        for x, y in siatka_wewnatrz(_wkt_do_punktow(s["geom_wkt"]), krok=5.0, maks=25):
            if not (minE - a.zapas < x < maxE + a.zapas and minN - a.zapas < y < maxN + a.zapas):
                continue
            b = budynek_po_xy(x, y)
            if b and b["id"] not in budynki:
                budynki[b["id"]] = dict(b, gdzie=f"u sąsiada {s.get('parcel', sid)}")

    # Budynek „na działce” wychodzący na sąsiednią → nieruchomość to zwykle kilka działek jednego właściciela.
    wspolne = set()
    for b in budynki.values():
        if b["gdzie"] != "na działce":
            continue
        for x, y in _wkt_do_punktow(b["geom_wkt"]):
            if not w_wielokacie(x, y, P):
                for v in sasiedzi.values():
                    if w_wielokacie(x, y, _wkt_do_punktow(v["geom_wkt"])):
                        wspolne.add(v.get("parcel"))

    def opis_obrysu(pkt):
        return dict(wierzcholki_2180=[[round(x, 2), round(y, 2)] for x, y in pkt],
                    wierzcholki_lokalne=[list(lok(p)) for p in pkt], powierzchnia_m2=round(pole(pkt), 1))

    wynik = dict(
        zrodlo="GUGiK: ULDK (granice, budynki ewidencyjne), geokoder UUG; dokładność granic zależy od ewidencji gminy",
        adres_z_geokodera=adres,
        dzialka=dict(id=dz["id"], numer=dz.get("parcel"), obreb=dz.get("region"), gmina=dz.get("commune"),
                     powiat=dz.get("county"), dlugosci_bokow_m=boki,
                     prostokat_otaczajacy_m=[round(maxE - minE, 2), round(maxN - minN, 2)], **opis_obrysu(P)),
        uklad_lokalny="x na wschód, y na południe [m], 0,0 = E %.2f N %.2f (EPSG:2180)" % (minE, maxN),
        sasiednie_dzialki=[dict(id=k, numer=v.get("parcel"), **opis_obrysu(_wkt_do_punktow(v["geom_wkt"])))
                           for k, v in sasiedzi.items()],
        budynki_ewidencyjne=[dict(id=k, gdzie=v["gdzie"], **opis_obrysu(_wkt_do_punktow(v["geom_wkt"])))
                             for k, v in budynki.items()],
        budynek_wychodzi_na_dzialki=sorted(wspolne),
        uwaga="Ewidencja nie podaje wysokości budynków ani drzew — te bierzemy z projektu domu, zdjęć, Street View lub drona.",
    )
    (out / "dzialka.json").write_text(json.dumps(wynik, ensure_ascii=False, indent=1))

    # mapy
    bbox = (minE - a.zapas, minN - a.zapas, maxE + a.zapas, maxN + a.zapas)
    szer = min(4000, int((bbox[2] - bbox[0]) / a.px)); wys = int(szer * (bbox[3] - bbox[1]) / (bbox[2] - bbox[0]))
    bledy = []
    # HighResolution (≤10 cm) nie wszędzie ma pokrycie — wtedy zwraca białą kartkę; StandardResolution (25 cm) jest wszędzie.
    for warstwa in ("HighResolution", "StandardResolution"):
        try:
            jpg = wms(f"https://mapy.geoportal.gov.pl/wss/service/PZGIK/ORTO/WMS/{warstwa}", "Raster", bbox, szer, wys, "image/jpeg")
            from PIL import Image
            import io
            if min(lo for lo, hi in Image.open(io.BytesIO(jpg)).convert("RGB").getextrema()) > 240:
                bledy.append(f"ortofoto {warstwa}: brak pokrycia (pusty obraz)")
                continue
            (out / "orto.jpg").write_bytes(jpg)
            wynik["ortofoto"] = f"geoportal ORTO {warstwa}"
            (out / "dzialka.json").write_text(json.dumps(wynik, ensure_ascii=False, indent=1))
            break
        except Exception as ex:
            bledy.append(f"ortofoto {warstwa}: {ex}")
    try:
        (out / "ewidencja.png").write_bytes(wms("https://integracja.gugik.gov.pl/cgi-bin/KrajowaIntegracjaEwidencjiGruntow",
                                                "dzialki,numery_dzialek,budynki", bbox, szer, wys, "image/png"))
    except Exception as ex:
        bledy.append(f"mapa ewidencyjna: {ex}")

    try:
        from PIL import Image, ImageDraw
        img = Image.open(out / "orto.jpg").convert("RGB")
        s = img.width / (bbox[2] - bbox[0])
        px = lambda p: ((p[0] - bbox[0]) * s, (bbox[3] - p[1]) * s)
        d = ImageDraw.Draw(img)
        for b in budynki.values():
            d.polygon([px(p) for p in _wkt_do_punktow(b["geom_wkt"])], outline=(255, 140, 0), width=3)
        for v in sasiedzi.values():
            q = _wkt_do_punktow(v["geom_wkt"])
            d.line([px(p) for p in q + q[:1]], fill=(80, 200, 255), width=2)
        d.line([px(p) for p in P + P[:1]], fill=(255, 40, 40), width=5)
        for v in sasiedzi.values():
            q = [p for p in _wkt_do_punktow(v["geom_wkt"]) if bbox[0] < p[0] < bbox[2] and bbox[1] < p[1] < bbox[3]]
            if q:
                cx, cy = px((sum(p[0] for p in q) / len(q), sum(p[1] for p in q) / len(q)))
                d.text((cx, cy), str(v.get("parcel")), fill=(255, 255, 255))
        img.save(out / "podglad.png")
    except Exception as ex:
        bledy.append(f"podgląd: {ex}")

    print(f"Działka {dz.get('parcel')} (obręb {dz.get('region')}, {dz['id']}): {pole(P):.0f} m², "
          f"prostokąt {maxE - minE:.1f} × {maxN - minN:.1f} m, boki {boki}")
    print(f"Sąsiednie działki: {len(sasiedzi)} ({', '.join(str(v.get('parcel')) for v in sasiedzi.values())})")
    print(f"Budynki z ewidencji: {len(budynki)} (" + "; ".join(f"{v['gdzie']} {pole(_wkt_do_punktow(v['geom_wkt'])):.0f} m²" for v in budynki.values()) + ")")
    print(f"Pliki: {out.resolve()}/ dzialka.json orto.jpg ewidencja.png podglad.png")
    if wspolne:
        print(f"UWAGA: budynek z tej działki wychodzi na działkę/i {', '.join(sorted(wspolne))} — nieruchomość "
              "prawdopodobnie obejmuje kilka działek. Zapytaj użytkownika i porównaj z ogrodzeniem na ortofoto.")
    for b in bledy:
        print("BŁĄD", b)


if __name__ == "__main__":
    main()
