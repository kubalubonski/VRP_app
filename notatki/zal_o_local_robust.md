# Założenia – Local Robust + Heurystyki

## 1. Model (local robust)
- Dwie osie czasu: Expected (E) – liczenie kosztu; Pessimistic (P) – kontrola wykonalności (okna + horyzont).
- Local feasibility: każdy krok A→B musi mieć arrival_P ≤ window_end_B; koniec trasy w P przed horyzontem.
- Start dnia 08:00; wszystkie czasy w minutach od startu.
- Okno czasowe HH:MM-HH:MM; brak poprawnego okna => brak ograniczenia.
- `service_time` (stały na klienta) doliczany po rozpoczęciu obsługi (domyślnie 0).

## 2. Dane wejściowe
- `matrices`: numpy: `expected`, `pessimistic` (opcjonalnie `optimistic`).
- `time_windows`: dict node -> (start,end) lub None.
- `routes`: lista tras [[0,...,0], ...].
- Parametry: `day_horizon`, `service_time`, `w_wait`, `w_penalty_P`, `base_vehicle_cost`, `vehicle_growth_factor`.

## 3. Funkcja kosztu
```
Cost = travel_E
     + w_wait * waiting_E
     + w_penalty_P * (lateness_P_sum + horizon_excess_E)
     + vehicle_cost
```
Składniki: travel_E (suma przejazdów E), waiting_E (czekanie do okna), lateness_P_sum (spóźnienia w P), horizon_excess_E (przekroczenia horyzontu w E), vehicle_cost = base * growth^(k-1). `service_time` wpływa na timeline.

## 4. Wyjścia funkcji kosztu
- `total_cost`
- `metrics`: travel_E, waiting_E, lateness_P_sum, horizon_excess_E, vehicle_cost, vehicles_used, route_end_times_E/P, route_waiting_E_list, route_travel_E_list, max_route_end_E/P, service_time_per_visit, total_service_time.

## 5. Heurystyki
**Clarke–Wright Savings**: scala pojedyncze trasy na podstawie oszczędności `s(i,j)`; akceptuje tylko P-feasible; zwykle mniej pojazdów.

**Greedy Insertion**: iteracyjne wstawianie klienta w miejsce o minimalnym przyroście kosztu (pełna wycena); jeśli brak feasible pozycji → nowa trasa; zwykle niższy koszt końcowy.

**Best-of**: wybór niższego kosztu z dwóch powyższych.

## 6. Interpretacja metryk
- Duże `waiting_E` – wiele wczesnych przyjazdów / krótkie trasy.
- `lateness_P_sum` > 0 – spóźnienia względem okien (niepożądane).
- `horizon_excess_E` > 0 – przekroczenia dnia.
- `vehicles_used` vs `vehicle_cost` – kompromis konsolidacja vs koszt.

## 7. Propozycje rozwoju (skrót)
- Uwzględnić `service_time` w feasibility heurystyk.
- Prosty test regresyjny (insertion ≤ savings cost na małym zbiorze).
- Eksport CSV metryk per trasa.
- Parametryzacja godziny startu.
