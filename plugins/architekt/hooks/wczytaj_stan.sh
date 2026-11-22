#!/usr/bin/env bash
# SessionStart (plugin architekt):
#  - folder z HANDOFF.md: wypisuje stan projektu (trafia do kontekstu Claude) + przypomnienie o karcie działki, jeśli jej nie ma,
#  - nowy folder (bez HANDOFF.md): komunikat dla użytkownika (systemMessage), że dane na starcie = lepsze wizualizacje od razu,
#    i instrukcja dla Claude (additionalContext), żeby zaczął od pytania o adres, zdjęcia i projekt.
dir="${CLAUDE_PROJECT_DIR:-$PWD}"
f="$dir/HANDOFF.md"

if [ ! -f "$HOME/.architekt/config.json" ] && [ ! -f "$f" ]; then
  echo "Plugin architekt: komputer nie jest jeszcze przygotowany (brak ~/.architekt/config.json). Gdy użytkownik zacznie pracę, zaproponuj skill przygotuj-komputer, a po nim nowy-projekt (adres nieruchomości, zdjęcia, projekt)."
  exit 0
fi

if [ -f "$f" ]; then
  echo "=== Stan projektu z HANDOFF.md (wczytany automatycznie przez plugin architekt) ==="
  head -c 8000 "$f"
  echo
  echo "=== koniec HANDOFF.md; pełna historia w PROGRESS.md ==="
  if [ ! -f "$dir/otoczenie/karta_dzialki.md" ]; then
    echo "Plugin architekt: w projekcie nie ma jeszcze karty działki (otoczenie/karta_dzialki.md). Przy najbliższej okazji, a najpóźniej przed pierwszym renderem, powiedz użytkownikowi, że adres nieruchomości, zdjęcia (elewacje, otoczenie, sąsiedzi) i projekt dają od razu wizualizacje prawdziwego budynku na prawdziwej działce, bez późniejszych poprawek, i poproś o nie (skill rozpoznanie-dzialki)."
  fi
  exit 0
fi

# Nowy folder projektu
cat <<'EOF'
{"systemMessage": "Plugin architekt: nowy projekt. Najlepsze wizualizacje powstają od razu, gdy na starcie podasz: 1) adres nieruchomości, 2) zdjęcia nieruchomości (każda elewacja, otoczenie, sąsiedzi), 3) projekt lub skany dokumentacji budynku. Claude pobierze wtedy działkę, sąsiadów i ortofoto z geoportalu i odwzoruje prawdziwy budynek w prawdziwym miejscu, zamiast poprawiać rendery po kilka razy. Wrzuć pliki do tego folderu i napisz adres.",
 "hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "Plugin architekt: to nowy folder projektu (brak HANDOFF.md). Zanim zrobisz cokolwiek innego (także gdy użytkownik od razu prosi o rzut, model czy render), w pierwszej odpowiedzi wyjaśnij krótko po polsku, że adres nieruchomości, zdjęcia (elewacje, otoczenie, sąsiedzi) i projekt lub skany podane na starcie dają od razu trafne wizualizacje zamiast walki z poprawkami później, i poproś o to, czego nie widać w folderze. Potem skille nowy-projekt i rozpoznanie-dzialki. Jeśli użytkownik woli zacząć bez tych danych, uszanuj to, ale zapisz braki w HANDOFF.md i wróć do nich przed pierwszym renderem."}}
EOF
exit 0
