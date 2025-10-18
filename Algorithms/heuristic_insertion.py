"""Greedy Insertion Heuristic (separate module)
Buduje rozwiązanie iteracyjnie: losowy start => wstawki minimalizujące przyrost kosztu.
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import random as rd
import numpy as np

from .robust_cost import calculate_vrp_cost_local_robust


def _route_feasible_p(route: List[int], time_P: np.ndarray, time_windows, day_horizon: int) -> bool:
    base_dt = datetime.strptime("08:00", "%H:%M")
    timeline_P = 0.0
    for i in range(len(route) - 1):
        a = route[i]; b = route[i+1]
        travel_P = time_P[a, b]
        arrival_P = timeline_P + travel_P
        if time_windows and b in time_windows and time_windows[b]:
            ws, we = time_windows[b]
            ws_min = (datetime.combine(base_dt.date(), ws) - base_dt).seconds / 60
            we_min = (datetime.combine(base_dt.date(), we) - base_dt).seconds / 60
            if arrival_P > we_min:
                return False
            if arrival_P < ws_min:
                arrival_P = ws_min
        timeline_P = arrival_P  # service_time==0 (upraszczamy)
        if timeline_P > day_horizon:
            return False
    return True


def greedy_insertion(
    matrices: Dict[str, np.ndarray],
    time_windows: Optional[Dict[int, Optional[Tuple[datetime.time, datetime.time]]]] = None,
    day_horizon: int = 600,
    service_time: float = 0.0,
    cost_per_km: float = 1.0,
    vehicle_fixed_cost: float = 900.0,
    penalty_late_per_min: float = 120.0,
    penalty_horizon_per_min: float = 120.0,
    ignore_p_constraints: bool = False,
    ignore_all_constraints: bool = False,
) -> List[List[int]]:
    time_E = matrices['expected']
    time_P = matrices['pessimistic']
    n = time_E.shape[0]
    customers = list(range(1, n))
    if not customers:
        return [[0,0]]

    rd.shuffle(customers)
    # Start with single route with first customer
    first = customers.pop()
    routes: List[List[int]] = [[0, first, 0]]

    def evaluate(solution: List[List[int]]):
        c, _ = calculate_vrp_cost_local_robust(
            solution, matrices, time_windows,
            day_horizon=day_horizon,
            service_time=service_time,
            cost_per_km=cost_per_km,
            vehicle_fixed_cost=vehicle_fixed_cost,
            penalty_late_per_min=penalty_late_per_min,
            penalty_horizon_per_min=penalty_horizon_per_min,
        )
        return c

    while customers:
        client = customers.pop()
        best_delta = None
        best_solution = None
        baseline_cost = evaluate(routes)  # cache

        # Insert into existing routes
        for r_idx, route in enumerate(routes):
            for pos in range(1, len(route)):  # przed ostatnim depo
                new_route = route[:pos] + [client] + route[pos:]
                if ignore_all_constraints:
                    pass  # żadnych filtrów
                elif ignore_p_constraints:
                    if sum(time_P[new_route[i], new_route[i+1]] for i in range(len(new_route)-1)) > day_horizon:
                        continue
                else:
                    if not _route_feasible_p(new_route, time_P, time_windows, day_horizon):
                        continue
                candidate = routes.copy()
                candidate[r_idx] = new_route
                cost_new = evaluate(candidate)
                delta = cost_new - baseline_cost
                if best_delta is None or delta < best_delta:
                    best_delta = delta
                    best_solution = candidate

        # Nowa trasa jako fallback
        new_route = [0, client, 0]
        if ignore_all_constraints:
            candidate = routes + [new_route]
            cost_new = evaluate(candidate)
            delta = cost_new - baseline_cost
            if best_delta is None or delta < best_delta:
                best_delta = delta
                best_solution = candidate
        elif ignore_p_constraints:
            if sum(time_P[new_route[i], new_route[i+1]] for i in range(len(new_route)-1)) <= day_horizon:
                candidate = routes + [new_route]
                cost_new = evaluate(candidate)
                delta = cost_new - baseline_cost
                if best_delta is None or delta < best_delta:
                    best_delta = delta
                    best_solution = candidate
        elif _route_feasible_p(new_route, time_P, time_windows, day_horizon):
            candidate = routes + [new_route]
            cost_new = evaluate(candidate)
            delta = cost_new - baseline_cost
            if best_delta is None or delta < best_delta:
                best_delta = delta
                best_solution = candidate

        if best_solution is None:
            routes.append([0, client, 0])  # ostateczność
        else:
            routes = best_solution

    return routes
