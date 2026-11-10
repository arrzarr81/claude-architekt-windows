#!/usr/bin/env bash
# SessionStart (plugin architekt): wypisuje stan projektu z HANDOFF.md, żeby nowa rozmowa zaczynała z wiedzą o projekcie.
# Wyjście trafia do kontekstu Claude. W folderze bez HANDOFF.md nic nie wypisuje.
dir="${CLAUDE_PROJECT_DIR:-$PWD}"
f="$dir/HANDOFF.md"
if [ -f "$f" ]; then
  echo "=== Stan projektu z HANDOFF.md (wczytany automatycznie przez plugin architekt) ==="
  head -c 8000 "$f"
  echo
  echo "=== koniec HANDOFF.md; pełna historia w PROGRESS.md ==="
elif [ ! -f "$HOME/.architekt/config.json" ]; then
  echo "Plugin architekt: komputer nie jest jeszcze przygotowany (brak ~/.architekt/config.json). Gdy użytkownik zacznie pracę, zaproponuj skill przygotuj-komputer."
fi
exit 0
