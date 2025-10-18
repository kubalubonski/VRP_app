# METRYKI – WERSJA KRÓTKA

## JSON (metrics + cost_model)
total_cost – suma wszystkich składników kosztu.
cost_distance – koszt dystansu (km * stawka).
vehicle_cost – koszt uruchomionych pojazdów.
cost_penalty_late – kara za spóźnienia (lateness_P_sum * kara).
cost_penalty_horizon – kara za przekroczenie horyzontu.
cost_time – time_weight * sum_route_time_E (akumulacja końców tras = obciążenie floty).
w_time / time_weight – waga składnika czasowego.
vehicles_used – liczba tras z klientami.
total_distance_km – łączny km.
waiting_total (waiting_E) – suma czekania przed oknami.
lateness_P_sum – suma spóźnień (pessimistic); 0 = wszystko na czas.
horizon_excess_E – nadwyżka ponad day_horizon (expected).
makespan_E – najpóźniejszy koniec trasy (expected).
sum_route_time_E – suma czasów zakończenia tras (expected).
avg_route_time_E – średnia z czasów zakończeń tras.
route_distance_list – dystanse poszczególnych tras.
route_waiting_E_list – oczekiwanie per trasa.
route_end_times_E / P – czasy zakończeń tras (expected / pessimistic).
max_route_end_E / P – maksymalne zakończenie (expected / pessimistic).
service_time_per_visit – stały czas obsługi jednego klienta.
total_service_time – łączny czas obsługi.

Krótki wzór: total_cost = cost_distance + vehicle_cost + cost_penalty_late + cost_penalty_horizon + cost_time.

## CSV (heuristics_all.csv)
dataset – nazwa zestawu.
size – liczba klientów.
window_profile – tight / medium / loose / very_loose.
algorithm – Savings / Insertion.
total_cost – jak w JSON.
vehicles_used – jak w JSON.
total_distance_km – jak w JSON.
waiting_total – jak w JSON.
avg_distance_per_route – total_distance_km / vehicles_used.
avg_wait_per_client – waiting_total / liczba odwiedzin.
lateness_P_sum – jak w JSON.
horizon_excess_E – jak w JSON.
makespan_E – jak w JSON.
sum_route_time_E – jak w JSON.
avg_route_time_E – jak w JSON.
cost_time – jak w JSON.
w_time – jak w JSON.

Różnice: CSV nie ma list per trasę (route_*) ani dekompozycji kosztu na osobne pola typu cost_penalty_late (poza tym co wymienione), JSON jest pełny – CSV to skrót do analiz pivot.
