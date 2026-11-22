---
name: rozpoznanie-dzialki
description: Zbiera dane o miejscu, zanim powstanie model czy wizualizacja — od adresu nieruchomości granice i wymiary działki (ULDK), sąsiednie działki i budynki z ewidencji, ortofotomapę (geoportal), widok z Map Google / Street View, plan miejscowy, zdjęcia elewacji od użytkownika — i zapisuje kartę działki z oceną pewności. Używaj zaraz po założeniu projektu, gdy pada „adres”, „działka”, „otoczenie”, „sąsiedzi”, „mapa”, „geoportal”, albo gdy ktoś prosi o model/wizualizację, a w projekcie nie ma `otoczenie/karta_dzialki.md`. / EN — Gathers site data before any model or render: from the property address, plot boundaries and dimensions (ULDK), neighbouring plots and buildings from the land register, orthophoto (geoportal), Google Maps / Street View, local zoning plan and the user's elevation photos; writes a site card with a confidence rating. Use right after project setup, or when a model/render is requested and `otoczenie/karta_dzialki.md` is missing.
---

# Rozpoznanie działki

Skany mówią, jak budynek był zaprojektowany; nie mówią, jak dziś stoi w otoczeniu. Koncepcja i wizualizacje muszą pokazywać ten budynek na tej działce, z tymi sąsiadami. Dlatego to drugi krok projektu, zaraz po `nowy-projekt`, przed `spis-arkuszy`. **Model terenu i wizualizacja nie startują bez karty działki** (sekcja „Bramka”).

Python z `~/.architekt/config.json` (klucz `python`). Skrypt `scripts/pobierz_dzialke.py` w folderze tego skilla (tylko biblioteka standardowa + Pillow).

## 1. Pierwsze pytanie: adres, zdjęcia, projekt

Powiedz użytkownikowi wprost, po co: z tymi danymi pierwsze wizualizacje od razu pokazują prawdziwy budynek w prawdziwym otoczeniu; bez nich kończy się na wielu rundach poprawek.

W pierwszej wiadomości proś o wszystko naraz (pomiń to, co już jest w projekcie): **adres nieruchomości**, **zdjęcia nieruchomości** (każda elewacja, otoczenie, sąsiedzi) i **projekt / dokumentację budynku** (skany, PDF), bo każdy je ma.

Bez **adresu nieruchomości** nie idź dalej. Przyjmij też numer działki z obrębem, link z Map Google (współrzędne `@50.77,15.73` w linku) albo GPS z EXIF zdjęcia. Zapytaj od razu, czy nieruchomość to jedna działka czy kilka.

## 2. Mapy i ewidencja (automatycznie)

```
"<python>" "<skill>/scripts/pobierz_dzialke.py" --adres "Karpacz, ul. Przykładowa 1" --folder otoczenie
#   albo --dzialka "<obręb> <nr>" | --xy <dł>,<szer> (WGS84) | --xy2180 <E>,<N>
```

Wynik w `otoczenie/`: `dzialka.json` (numer, powierzchnia, boki, wierzchołki w EPSG:2180 i w metrach lokalnych, sąsiednie działki, budynki z ewidencji na działce i u sąsiadów z obrysami), `orto.jpg`, `ewidencja.png`, `podglad.png`. Trwa 1–3 min.

- Obejrzyj `podglad.png` i pokaż użytkownikowi: czy to właściwa działka, czy obrys budynku z ewidencji zgadza się z dachem na ortofoto (rozjazd > 1 m zapisz w karcie).
- „UWAGA: budynek wychodzi na działkę …” → nieruchomość to prawdopodobnie kilka działek; ustal zasięg i uruchom skrypt dla pozostałych.
- Obrys z ewidencji jest pierwszym sprawdzeniem przerysowanych rzutów: wymiary bryły z `dzialka.json` porównaj z rzutem parteru (różnice > 20 cm wypisz).
- Ewidencja nie zna wysokości budynków; ortofoto bywa sprzed 2–3 lat.
- Sieć: `services.gugik.gov.pl`, `uldk.gugik.gov.pl`, `mapy.geoportal.gov.pl`, `integracja.gugik.gov.pl` + serwer WMS powiatu (przekierowanie).

## 3. Mapy Google / Street View i plan miejscowy

- Poproś użytkownika o link do Street View lub zrzuty: budynek od ulicy, budynki sąsiednie, widok z działki. Street View Static API wymaga klucza Google; przeglądarki użyj tylko za wyraźną zgodą użytkownika.
- Plan miejscowy (MPZP) lub decyzja WZ: przy koncepcji przebudowy (wysokość, linie zabudowy, dachy, intensywność). Poproś o wypis albo sprawdźcie warstwę MPZP na geoportal.gov.pl. Zapisz w karcie ustalenia dotyczące tej działki.

## 4. Od użytkownika: uzupełnienie

Zdjęcia i dokumentacja przyszły w kroku 1; sprawdź je według listy i dopytaj jednym pytaniem o brakujące: Zdjęcia każdej elewacji (na wprost, cały budynek w kadrze), dachu, widoki na sąsiadów z działki, detale do wizualizacji (kolor tynku, stolarka, pokrycie dachu); mapa do celów projektowych lub pomiar geodety (rzędne terenu, uzbrojenie); zdjęcie z drona, jeśli jest.

## 5. Karta działki

`otoczenie/karta_dzialki.md`: tabela `dana | wartość | źródło | pewność (pewne / szacowane / brak)`: adres i działki · obrys budynku z ewidencji vs rzut · kierunek północy · teren (spadki, rzędne) · sąsiednie budynki w zasięgu kadrów (odległość, wysokość, wygląd) · drzewa · ustalenia MPZP/WZ · materiały elewacji i dachu dziś · lista zdjęć z opisem. Pod tabelą: czego brakuje (jedno zbiorcze pytanie) i co jest szacowane. Uzupełnij sekcję „Projekt” i „Kierunki świata” w `CLAUDE.md`. `HANDOFF.md` + `PROGRESS.md`.

## Bramka

`wizualizacja` (scena z terenem i otoczeniem) i warianty koncepcji startują dopiero, gdy karta ma: adres i granice działki potwierdzone przez użytkownika, kierunek północy, sąsiednie budynki w zasięgu kadrów, zdjęcia elewacji. Brak danych → tylko za zgodą użytkownika, a brakujące elementy opisz jako szacowane w podpisie renderu. Nie dodawaj sąsiadów ani terenu, których nie widziałeś.
