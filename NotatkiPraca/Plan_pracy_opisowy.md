# Plan pracy – opisowy (wariant A, Wstęp nienumerowany)

## Wstęp (nienumerowany)
A.1 Kontekst i motywacja – wyzwania logistyki ostatniej mili; potrzeba redukcji dystansu, liczby pojazdów i czasu operacyjnego.
A.2 Cel i zakres – zaprojektowanie i ocena metaheurystycznego podejścia (SA) do VRPTW z elementem niepewności czasów; stworzenie prototypu pipeline’u danych.
A.3 Zakres niepewności – dwa scenariusze: Expected (E) i Pesymistyczny (P); filtr EPO: ruch musi spełniać okna w obu scenariuszach; brak kar → hard filtering.
A.4 Wkłady i struktura – zarys rozdziałów oraz wkłady (slim output, quasi‑robust filtr, param study SA).

## 1. Problem i model
1.1 Definicja VRP/VRPTW – pojedynczy depot, zbiór klientów z oknami czasowymi.
1.2 Notacja – indeksy klientów, czasy przejazdu (macierze), czasy rozpoczęcia obsługi, kolejność w trasie.
1.3 Okna czasowe E / P – dwa scenariusze; warunek podwójny \(S_i^E, S_i^P \le b_i\).
1.4 Horyzont dnia – maksymalny czas zakończenia trasy; naruszenia odrzucane.
1.5 Funkcja kosztu – \(c_d Dist + c_v Vehicles + w_t TimeSum\); brak kar za spóźnienia.
1.6 Profile okien – tight/medium/loose/very_loose; szerokość okna a waiting i eksploracja.
1.7 Uproszczenia – brak pojemności, \(s_i=0\), dwa scenariusze, pojedynczy depot.
1.8 Relacja do literatury – quasi‑robust vs klasyczny robust; brak penalizacji.
1.9 Most do metod – przejście do heurystyk i SA.

## 2. Aplikacja i przygotowanie danych
2.1 Rola prototypu – UI do wprowadzania danych, generowanie wejść dla algorytmów.
2.2 Pipeline – wejście → geokodowanie (OSM) → macierz (ORS) → profile okien → pliki CSV/JSON.
2.3 Integracje API – stan (geokodowanie + czasy), plan (pogoda / dynamiczne modyfikatory).
2.4 Generowanie syntetyczne – seria instancji (rozmiary, profile okien) dla eksperymentów parametrycznych.
2.5 Format wejść – macierz czasów, definicje okien E/P, parametry SA.
2.6 Output slim – motywacja minimalności (łatwa analiza batch, mniejsza objętość).
2.7 Ograniczenia – brak jeszcze wywołań SA z UI; brak dynamicznej pogody.
2.8 Eksport i katalog instancji – konwencja nazw: dataset_size_profile_seed; mapowanie do kolumn CSV (dataset,size,window_profile); struktura folderów i możliwość re-use.

## 3. Metody optymalizacji
3.1 Inicjalizacja – wybór heurystyki startowej vs kilka startów i selekcja (najniższy cost / najmniej pojazdów).
3.2 Reprezentacja – struktury do szybkiej aktualizacji: listy tras, pre‑sumy dystansu/czasu.
3.3 Walidacja E/P – procedura sprawdzania okien w obu scenariuszach po kandydacie ruchu (early reject).
3.4 Operatory – opis działania, złożoność: swap O(k), relocate O(k), 2-opt O(k) z pruningiem.
3.5 Harmonogram SA – dobór T0 (target acceptance), alpha; warunki stopu: max_iter, stagnacja.
3.6 Akceptacja i statystyki – rejestrowanie accepted/improving, rejected_horizon; wskaźniki eksploracji.
3.7 Trace_improvements – struktura zapisu (iter, cost, vehicles) i wykorzystanie w analizie konwergencji.
3.8 Złożoność – szacunkowy koszt jednej iteracji vs wielkość instancji; profil czasu (parsowanie ruchów vs walidacja E/P).
3.9 Rozszerzenia – or-opt, cross-exchange, adaptive cooling / reheating, wielostart.

## 4. Eksperymenty i wyniki
4.1 Hipotezy – H1: SA redukuje liczbę pojazdów ≥ X% na profilach loose; H2: alpha wpływa na trade-off distance/waiting; H3: stabilność wyników przy powtórzeniach.
4.2 Instancje – sposób generacji, seed control, rozkład profili okien, liczba instancji per kombinacja.
4.3 Plan – siatka size × profile × (alpha, iters, T0); liczba powtórzeń dla stabilności.
4.4 Procedura – konstrukcja (Savings/Insertion) → wybór startu → SA → eksport slim.
4.5 Baseline heurystyk – tabela startowych vehicles/distance vs profile.
4.6 Efekt SA – średnie i najlepsze delty cost/vehicles/distance/makespan.
4.7 Parametry – krzywe konwergencji i acceptance rate vs temperatura.
4.8 Trade-off – analiza udziału waiting w koszcie czasu vs distance.
4.9 Stabilność – wariancja wyników; boxploty; wpływ seed.
4.10 Dyskusja – interpretacja ograniczeń (syntetyczne dane, brak capacity) i implikacje.

## 5. Wnioski
5.1 Osiągnięcia – pipeline + heurystyki + SA + slim.
5.2 Rekomendacje – sugerowane zakresy alpha/iters.
5.3 Kierunki dalsze – robust wieloscenariuszowe, capacity, multi-depot, adaptacja.
5.4 Wartość praktyczna – szybka kalibracja.

## Bibliografia
Lista pozycji cytowanych wpleciona w rozdziały 1–4.

## Załączniki (opc.)
Przykładowy slim JSON, konfiguracja SA, przykładowa linia CSV.
