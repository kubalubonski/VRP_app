"""Greedy Insertion Heuristic
Buduje rozwiązanie iteracyjnie: start od jednego klienta i kolejne wstawki
minimalizujące przyrost kosztu globalnego.

Model dualny okien (E/P): dla kroku i->j bazujemy na osi expected (E):
    A_j^E = B_i^E + t_{ij}^E
    A_j^P = B_i^E + t_{ij}^P
    B_j^S = max(A_j^S, a_j)
Akceptacja gdy B_j^E ≤ b_j oraz (o ile kontrolujemy P) B_j^P ≤ b_j.
Propagujemy wyłącznie B_j^E. P jest używany punktowo do weryfikacji okna.
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import random as rd
import numpy as np

from .robust_cost import calculate_vrp_cost_local_robust
from .common_feasibility import route_feasible_ep


def _local_feasible(route: List[int], time_E, time_P, time_windows, day_horizon, service_time, ignore_all_constraints):
    if ignore_all_constraints:
        return True
    return route_feasible_ep(route, time_E, time_P, time_windows, day_horizon, service_time)


def greedy_insertion(
    matrices: Dict[str, np.ndarray],
    time_windows: Optional[Dict[int, Optional[Tuple[datetime.time, datetime.time]]]] = None,
    day_horizon: int = 600,
    service_time: float = 0.0,
    cost_per_km: float = 1.0,
    vehicle_fixed_cost: float = 900.0,
    penalty_horizon_per_min: float = 120.0,
    ignore_all_constraints: bool = False,
        ) -> List[List[int]]:

    time_E = matrices['expected']
    time_P = matrices['pessimistic']
    n = time_E.shape[0]
    customers = list(range(1, n))
    if not customers:
        return [[0,0]]

    # Losowa kolejność klientów wprowadza element stochastyczny
    rd.shuffle(customers)
    
    # Inicjalizacja: pierwsza trasa z losowym klientem
    first_customer = customers.pop()
    routes: List[List[int]] = [[0, first_customer, 0]]

    def evaluate(solution: List[List[int]]) -> float:
        """Funkcja pomocnicza do oceny kosztu danego rozwiązania."""
        cost, _ = calculate_vrp_cost_local_robust(
            solution, matrices, time_windows,
            day_horizon=day_horizon,
            service_time=service_time,
            cost_per_km=cost_per_km,
            vehicle_fixed_cost=vehicle_fixed_cost,
            penalty_horizon_per_min=penalty_horizon_per_min,
        )
        return cost

    while customers:
        client_to_insert = customers.pop()
        best_insertion_cost = float('inf')
        best_solution_after_insertion = None
        
        # Krok 1: Znajdź najlepsze miejsce wstawienia w istniejących trasach
        for r_idx, route in enumerate(routes):
            for pos in range(1, len(route)):
                # Utwórz kandydacką trasę przez wstawienie klienta
                new_route = route[:pos] + [client_to_insert] + route[pos:]
                
                # Sprawdź dopuszczalność tylko zmodyfikowanej trasy
                if not route_feasible_ep(new_route, time_E, time_P, time_windows, day_horizon, service_time):
                    continue
                
                # Oceń koszt całego nowego rozwiązania
                candidate_solution = routes[:r_idx] + [new_route] + routes[r_idx+1:]
                new_cost = evaluate(candidate_solution)

                if new_cost < best_insertion_cost:
                    best_insertion_cost = new_cost
                    best_solution_after_insertion = candidate_solution

        # Krok 2: Rozważ utworzenie nowej trasy dla klienta
        new_route_for_client = [0, client_to_insert, 0]
        if route_feasible_ep(new_route_for_client, time_E, time_P, time_windows, day_horizon, service_time):
            candidate_solution = routes + [new_route_for_client]
            new_cost = evaluate(candidate_solution)
            
            if new_cost < best_insertion_cost:
                best_insertion_cost = new_cost
                best_solution_after_insertion = candidate_solution

        # Krok 3: Zaktualizuj rozwiązanie
        if best_solution_after_insertion is not None:
            routes = best_solution_after_insertion
        else:
            # Jeśli nigdzie nie dało się wstawić klienta (bardzo restrykcyjne okna),
            # dodaj go w osobnej, potencjalnie niedopuszczalnej trasie.
            # Taki przypadek jest mało prawdopodobny przy poprawnych danych.
            routes.append([0, client_to_insert, 0])

    return routes
