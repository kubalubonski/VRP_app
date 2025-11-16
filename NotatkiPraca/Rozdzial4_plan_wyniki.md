# Rozdział 4. Eksperymenty i wyniki (wersja skrócona)

## 4.1. Cel
Porównać dwie heurystyki konstrukcyjne (Savings, Insertion) na zestawie profilowanych instancji VRPTW oraz pokazać jak metaheurystyka Symulowane Wyżarzanie (SA) dalej obniża koszt. Skupienie: koszt całkowity, liczba pojazdów, wpływ szerokości okien, slack czasowy.

## 4.2. Dane
Instancje: rozmiary 20, 40, 80, 120, 200; profile okien: tight, medium, loose, very_loose. Każdy profil to inna szerokość okna (tight najwęższe). Czasy przejazdu: punkty w kwadracie 120×120 km, prędkości 55–75 km/h, E = dystans / v (kap 160 min), O = E * f_O (0.88–0.95), P = E * f_P (1.08–1.30). Okna wyznaczane od przybliżonego czasu dojazdu z depotu i zwężane/poszerzane wg profilu. Brak spóźnień (twarde okna E/P).

## 4.3. Metryki heurystyk (minimum)
- total_cost – główna miara jakości.
- vehicles_used – kompresja klientów.
- cost_pct_gain_insertion = (cost_S − cost_I)/cost_S.
- avg_wait_per_client – wykorzystanie okien (niższy slack = lepsze dopasowanie).
- makespan_E – kontrola czy redukcja pojazdów nie przeciąga końca dnia.

## 4.4. Metryki SA (minimum)
- start_cost, best_cost, improvement_pct.
- epochs, iters_per_T (parametry intensywności).
- accepted_moves vs improving_moves → acceptance_ratio_worse.
- trace (epoka, T, best_cost) do wykresu konwergencji.

## 4.5. Procedura (heurystyki)
1. Uruchom Savings i Insertion na każdej instancji.
2. Zapis tras do JSON; wyliczenie metryk → CSV `heurystyki_batch.csv`.
3. Wybór rozwiązania startowego dla SA: zawsze Insertion (niższy koszt / mniej pojazdów), chyba że koszty identyczne.

## 4.6. Podział tabel (Word)
- Tab. 4.1: Rozmiary 20–40 (profil, cost_S, cost_I, % gain, veh_S, veh_I).
- Tab. 4.2: Rozmiary 80–120 (jak wyżej).
- Tab. 4.3: Rozmiar 200 (dodaj avg_wait_per_client).
- Tab. 4.4: Średni % gain i średni veh_diff per profil.
- Tab. 4.5: Średni % gain i średni veh_diff per rozmiar.

## 4.7. Wykresy (minimalny zestaw)
- Fig. 4.1: vehicles_used vs size (Savings vs Insertion).
- Fig. 4.2: Heatmapa % gain (profil × rozmiar).
- Fig. 4.3: Boxplot avg_wait_per_client (profil × heurystyka).
- Fig. 4.4: SA – best_cost vs epoka (różne alpha).

## 4.8. Kolejność narracji
1. Koszt i pojazdy (Tab. 4.1–4.3): Insertion przeważnie lepszy.
2. Skalowanie (Fig. 4.1 + Tab. 4.5): rosnąca trudność → więcej pojazdów dla Savings.
3. Wpływ profilu (Heatmapa + Tab. 4.4): przewaga Insertion rośnie przy węższych oknach.
4. Slack (Boxplot): Savings ma większy średni slack → przestrzeń dla SA.
5. Wybór bazowego rozwiązania: Insertion.
6. Zapowiedź SA i parametrów.

## 4.9. Plan testów SA
Parametry siatki: t_max ∈ {500,1000}, alpha ∈ {0.90,0.95,0.98}, iters_per_T ∈ {200,500}, neighborhood ∈ {mixed, two_opt}. Najpierw instancja 80_medium → wybór najlepszej pary (alpha, iters_per_T) → przeniesienie na 120 i 200 (profil tight i loose). Chłodzenie: T_{k+1} = alpha * T_k.

## 4.10. Raportowanie SA
Tabela: (t_max, alpha, iters_per_T, best_cost, improvement_pct, accepted_moves, improving_moves). Wykres Fig. 4.4 (krzywe konwergencji). Jedno zdanie interpretujące acceptance_ratio_worse (spadek wraz z chłodzeniem).

## 4.11. Kluczowe zdania do wniosków
- „Insertion redukuje koszt względem Savings we wszystkich rozmiarach; największy zysk przy profilu tight.”
- „Przewaga Insertion koreluje z zawężaniem okien – im mniej luzu czasowego, tym większa różnica.”
- „Savings generuje większy slack, co potwierdza sens dalszej optymalizacji metaheurystycznej.”
- „SA z alpha=0.95 szybciej przechodzi z fazy eksploracji do ulepszania niż alpha=0.98.”

## 4.12. Skrót implementacyjny (Excel)
Filtry: (20–40), (80–120), (200). Formuła % gain: =(cost_S - cost_I)/cost_S. Heatmapa z pivotem (Rows=size, Columns=profile). Kopiuj jako obraz.

## 4.13. Najważniejsza teza rozdziału
Heurystyka wstawiania daje lepszą i bardziej zwartą bazę niż Savings, a kontrolowane chłodzenie w SA pozwala tę bazę jeszcze obniżyć kosztowo bez zwiększania liczby pojazdów.

---
Notatka: Źródło metryk wyłącznie `heurystyki_batch.csv`.
