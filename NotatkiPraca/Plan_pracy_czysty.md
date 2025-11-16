# Plan pracy (wariant A – Wstęp nienumerowany)

Wstęp (nienumerowany)
   A.1 Kontekst i motywacja
   A.2 Cel i zakres pracy
   A.3 Zakres niepewności (scenariusze E / P – podejście EPO)
   A.4 Wkłady pracy i struktura

1. Problem i model
   1.1 Definicja wariantu VRP / VRPTW
   1.2 Reprezentacja rozwiązania i notacja
   1.3 Okna czasowe: Expected (E) i Pesymistyczne (P)
   1.4 Horyzont dnia i filtr ruchów
   1.5 Funkcja kosztu i komponenty
   1.6 Profile okien (tight / medium / loose / very_loose)
   1.7 Uproszczenia i konsekwencje
   1.8 Relacja do literatury (quasi‑robust EPO)
   1.9 Most do metod

2. Aplikacja i przygotowanie danych
   2.1 Rola prototypu i zakres implementacji
   2.2 Pipeline danych (wejście → geokodowanie → macierz → pliki)
   2.3 Integracje z API (OSM, ORS, pogodowe – stan / plan)
   2.4 Generowanie syntetycznych instancji
   2.5 Format wejść dla heurystyk i SA
   2.6 Output slim (JSON / CSV) – uzasadnienie
   2.7 Ograniczenia aktualnego stanu

3. Metody optymalizacji
   3.1 Heurystyki konstrukcyjne (Savings, Insertion)
   3.2 Symulowane wyżarzanie – zasada działania
   3.3 Sąsiedztwa (swap, relocate, 2-opt)
   3.4 Harmonogram temperatury (geometric)
   3.5 Parametry i statystyki procesu
   3.6 Metryki oceny (vehicles, distance, makespan, waiting, runtime)
   3.7 (Opc.) kierunki rozszerzeń (or-opt, cross-exchange, tuning)

4. Eksperymenty i wyniki
   4.1 Hipotezy badawcze (H1 redukcja floty, H2 dystans vs waiting, H3 stabilność parametrów)
   4.2 Generowanie i selekcja instancji (profile, losowość, seed, katalog)
   4.3 Plan eksperymentalny (siatka: size × profile × param grid SA)
   4.4 Procedura (konstrukcja → SA → zapis slim → agregacja CSV)
   4.5 Jakość startowych heurystyk (baseline vehicles / distance)
   4.6 Efekt SA (redukcje cost, distance, vehicles, makespan)
   4.7 Wpływ parametrów (alpha, iters, T0) + dynamika trace
   4.8 Trade-off distance vs waiting i struktura kosztu
   4.9 Stabilność i wariancja (powtórzenia, seed sensitivity)
   4.10 Dyskusja i ograniczenia (syntetyczność, brak capacity, dwa scenariusze)

5. Wnioski
   5.1 Podsumowanie osiągnięć
   5.2 Rekomendacje parametrów
   5.3 Kierunki dalszych prac
   5.4 Wartość praktyczna rozwiązania

Bibliografia
Załączniki