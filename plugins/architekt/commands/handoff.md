---
description: Handoff przed /clear — zapis stanu sesji do plików projektu (handoff / progress / lekcje / pamięć), commit bez pusha, gotowe do /clear / EN — Handoff before /clear — saves the session state to project files (handoff / progress / lessons / memory), commits without pushing, ready for /clear
argument-hint: "[opcjonalna notatka do handoffa]"
---

Zrób handoff tej sesji przed `/clear`. Cel: nowa sesja ma ruszyć z samych plików, bez zadawania pytań.

## 0. Rozpoznanie projektu
- Jeśli projekt ma własny skill domykania sesji (np. `koniec-sesji`, coś z „handoff”/„session” w nazwie) albo CLAUDE.md opisuje rytuał końca sesji — **wywołaj go / postępuj według niego**; on ma pierwszeństwo przed krokami poniżej w kwestii ścieżek i formatu.
- Ustal, gdzie projekt trzyma stan: `git ls-files | grep -iE 'handoff|progress|todo|lessons|STATE'` oraz katalogi `.planning/`, `tasks/`. Używaj istniejących plików, nie twórz równoległych.
- Brak czegokolwiek → utwórz `handoff.md` i `progress.md` w katalogu głównym repo.

## 1. Handoff (stan bieżący)
Nagłówek z dzisiejszą datą i jednym zdaniem stanu. Edytuj **w miejscu** — nie przebudowuj struktury pliku. Zawartość: co jest w toku, następny krok i kto go robi, terminy, ścieżki plików, otwarte decyzje, polecenia do uruchomienia. Zamknięte wątki usuń stąd (idą do progress).

## 2. Progress (historia)
Dopisz na końcu sekcję z datą: co zamknięto w tej sesji — krótko, fakty. Nigdy nie nadpisuj.

## 3. Reguła czy fakt
- Nowa reguła pracy (zwłaszcza po korekcie użytkownika) → `tasks/lessons.md` albo odpowiedni skill projektu.
- Ustalenie, decyzja, data, adres, kontakt → pamięć projektu (plik + linia w `MEMORY.md`), najpierw sprawdź, czy nie ma już pliku o tym samym.
- Nie dubluj jednego w drugim ani w handoffie.

## 4. Zadania w tle
Zatrzymaj wszystkie (TaskStop) — żadnych osieroconych monitorów i pętli.

## 5. Commit
`git add` tylko zmienionych plików projektu (bez śmieci, plików tymczasowych, sekretów, plików oznaczonych do skasowania). Komunikat `Handoff DD.MM: <stan w kilku słowach>` z wymaganą stopką. **Nie pushuj**, chyba że użytkownik prosi. Brak repo git → pomiń i powiedz o tym.

## 6. Weryfikacja
Sprawdź zapis (`head -3` pliku handoff, `git log -1 --stat`). Nie deklaruj sukcesu bez tego.

## 7. Komunikat końcowy
Jedna krótka wiadomość: co zapisano (ścieżki), co czeka na użytkownika i z jakim terminem, oraz „możesz wpisać /clear”. Nie streszczaj treści handoffa w czacie.

$ARGUMENTS
