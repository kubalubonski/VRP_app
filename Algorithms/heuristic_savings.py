"""Clarke-Wright Savings Heuristic (separate module)
Prosty algorytm zachłanny łączący trasy na podstawie oszczędności czasu."""

from datetime import datetime
from typing import Dict, List, Optional, Tuple
import numpy as np


def clarke_wright_savings(
    matrices: Dict[str, np.ndarray],
    time_windows: Optional[Dict[int, Optional[Tuple[datetime.time, datetime.time]]]] = None,
    day_horizon: int = 600,
    service_time: float = 0.0,
    ignore_p_constraints: bool = False,
    ignore_all_constraints: bool = False,
) -> List[List[int]]:
    time_E = matrices['expected']
    time_P = matrices['pessimistic']
    n_locations = time_E.shape[0]
    if n_locations <= 1:
        return [[0, 0]]

    customers = [i for i in range(1, n_locations)]
    routes = {c: [0, c, 0] for c in customers}

    savings = []
    for i in customers:
        for j in customers:
            if i != j:
                sij = time_E[0, i] + time_E[0, j] - time_E[i, j]
                savings.append((sij, i, j))
    savings.sort(reverse=True)

    base_dt = datetime.strptime("08:00", "%H:%M")

    def feasible_p(route: List[int]) -> bool:
        if ignore_all_constraints:
            return True
        timeline_P = 0.0
        for k in range(len(route) - 1):
            a = route[k]; b = route[k+1]
            travel_P = time_P[a, b]
            arrival_P = timeline_P + travel_P
            if not ignore_p_constraints and time_windows and b in time_windows and time_windows[b]:
                ws, we = time_windows[b]
                ws_min = (datetime.combine(base_dt.date(), ws) - base_dt).seconds / 60
                we_min = (datetime.combine(base_dt.date(), we) - base_dt).seconds / 60
                if arrival_P > we_min:
                    return False
                if arrival_P < ws_min:
                    arrival_P = ws_min
                timeline_P = arrival_P
            else:
                timeline_P = arrival_P
            if not ignore_all_constraints and timeline_P > day_horizon:
                return False
        return True

    def find_route_end(node):
        for key, r in routes.items():
            if len(r) > 2 and r[-2] == node:
                return key
        return None

    def find_route_start(node):
        for key, r in routes.items():
            if len(r) > 2 and r[1] == node:
                return key
        return None

    for s, i, j in savings:
        rid_i = find_route_end(i)
        rid_j = find_route_start(j)
        if rid_i is None or rid_j is None or rid_i == rid_j:
            continue
        r_i = routes[rid_i]
        r_j = routes[rid_j]
        merged = r_i[:-1] + r_j[1:]
        if feasible_p(merged):
            del routes[rid_i]; del routes[rid_j]
            routes[merged[1]] = merged

    return list(routes.values())
