# Szkic spisu treści (wariant A, Wstęp nienumerowany)

Wstęp (nienumerowany) ............................................. 3–5
   A.1 Kontekst i motywacja ........................................ 3
   A.2 Cel i zakres pracy .......................................... 3–4
   A.3 Zakres niepewności (E/P – EPO) .............................. 4
   A.4 Wkłady i struktura .......................................... 5

1. Problem i model ................................................ 6–14
   1.1 Definicja VRP / VRPTW ....................................... 6–7
   1.2 Reprezentacja i notacja ..................................... 7
   1.3 Okna czasowe E i P (warunek podwójny) ...................... 8–9
   1.4 Horyzont dnia i filtr ruchów ................................ 9
   1.5 Funkcja kosztu (distance, vehicle, time) ................... 10–11
   1.6 Profile okien (tight/medium/loose/very_loose) .............. 12
   1.7 Uproszczenia i konsekwencje ................................ 13
   1.8 Relacja do literatury / most do metod ...................... 14

2. Aplikacja i przygotowanie danych .............................. 15–22
   2.1 Rola prototypu i zakres implementacji ...................... 15
   2.2 Pipeline danych (diagram) .................................. 16
   2.3 Integracje API (OSM, ORS, pogoda) .......................... 17
   2.4 Generowanie syntetycznych instancji ........................ 18
   2.5 Format wejść/wyjść (CSV/JSON slim) ......................... 19–20
   2.6 Ograniczenia stanu bieżącego ............................... 21–22

3. Metody optymalizacji .......................................... 23–33
   3.1 Heurystyki konstrukcyjne (Savings, Insertion) .............. 23–24
   3.2 Symulowane wyżarzanie – zasada ............................. 25–26
   3.3 Sąsiedztwa (swap, relocate, 2-opt) ......................... 27
   3.4 Harmonogram temperatury (geometric) ........................ 28
   3.5 Parametry i statystyki (accepted/improving/rejected) ....... 29–30
   3.6 Metryki oceny .............................................. 31
   3.7 Rozszerzenia potencjalne ................................... 32–33

4. Eksperymenty i wyniki ......................................... 34–48
   4.1 Plan eksperymentalny ....................................... 34–35
   4.2 Procedura i narzędzia ...................................... 36
   4.3 Jakość heurystyk (tabela) ................................. 37–38
   4.4 Efekt SA (wykresy, tabele) ................................. 39–43
   4.5 Wpływ parametrów (alpha, iters) ............................ 44–45
   4.6 Trade-off distance vs waiting .............................. 46
   4.7 Dyskusja i ograniczenia .................................... 47–48

5. Wnioski ....................................................... 49–52
   5.1 Podsumowanie osiągnięć ..................................... 49–50
   5.2 Rekomendacje parametrów .................................... 50
   5.3 Kierunki dalszych prac ..................................... 51
   5.4 Wartość praktyczna ......................................... 52

Bibliografia ..................................................... 53–??
Załączniki ....................................................... ??–??

(Uwagi: zakres stron orientacyjny; faktyczna objętość zależy od szczegółowości opisów i liczby tabel/rysunków.)