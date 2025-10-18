# Heurystyki i koszt – skrót

## Problem (VRPTW)
Klienci z oknami czasowymi: generujemy tylko trasy spełniające okna (praktycznie hard – naruszenia są odrzucane podczas konstrukcji / SA), ale w funkcji kosztu pozostawiono pola kar L,H (soft design) które przy pełnej wykonalności = 0.

## Heurystyki
- Savings (Clarke–Wright) – deterministyczny baseline.
- Greedy Insertion – wielokrotne losowe permutacje klientów, wybór najlepszego.

## Funkcja kosztu
C = c_km * D + c_vehicle * K + p_late * L + p_horizon * H (+ opcjonalnie w_time * sum_route_time_E jeśli aktywne)
- D dystans; K pojazdy; L spóźnienia; H przekroczenia horyzontu.
- waiting_total NIE wchodzi do kosztu.

(W aktualnych wynikach L=0 i H=0 bo naruszenia nie przechodzą do finalnych tras.)

## Kluczowe metryki
total_cost, vehicles_used, total_distance_km, lateness_P_sum, horizon_excess_E, waiting_total (diagnostycznie).

## Dane
Rozmiary: 20,40,80,120,200 × okna: tight/medium/loose/very_loose.

## Procedura
1× Savings, R× Insertion → najlepszy zapis. Wyniki: CSV + JSON z trasami.

## Decyzje
- Brak kary za waiting.
- Multi-start tylko dla Insertion.

## Rozszerzenia (plan)
Lokalne ulepszenia (2-opt, relocate, swap), merge tras, operatory redukcji, dodatkowe wagi (waiting, time load), seed.

## Synteza
Porównujemy Savings vs multi-start Insertion pod względem kosztu, liczby pojazdów i kar czasu; oczekiwanie raportowane pomocniczo.
