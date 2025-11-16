"""Clarke-Wright Savings Heuristic
Łączenie tras na podstawie oszczędności: sij = t_{0,i}^E + t_{0,j}^E - t_{i,j}^E.

Dualny filtr okien (E/P): propagujemy tylko expected.
    A_b^E = B_a^E + t_{ab}^E
    A_b^P = B_a^E + t_{ab}^P
Akceptacja merge gdy dla każdego b: B_b^E ≤ b_b oraz (jeśli kontrolujemy P) B_b^P ≤ b_b.
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple
import numpy as np
from .common_feasibility import route_feasible_ep


def clarke_wright_savings(
    matrices: Dict[str, np.ndarray],
    time_windows: Optional[Dict[int, Optional[Tuple[datetime.time, datetime.time]]]] = None,
    day_horizon: int = 600,
    service_time: float = 0.0,
    ignore_all_constraints: bool = False,
) -> List[List[int]]:
    """Implementacja heurystyki oszczędności Clarke'a-Wrighta.

    Algorytm startuje z trywialnego rozwiązania (każdy klient ma osobną trasę),
    a następnie iteracyjnie łączy trasy na podstawie "oszczędności" w koszcie,
    pod warunkiem zachowania dopuszczalności czasowej.
    """
    time_E = matrices['expected']
    time_P = matrices['pessimistic']
    n_locations = time_E.shape[0]
    if n_locations <= 1:
        return [[0, 0]]

    customers = list(range(1, n_locations))
    # Inicjalizacja: każdemu klientowi przypisana jest osobna trasa [0, klient, 0]
    routes = {c: [0, c, 0] for c in customers}

    # Oblicz oszczędności dla wszystkich par klientów (i, j)
    # Oszczędność sij = d(0,i) + d(0,j) - d(i,j)
    savings = []
    for i in customers:
        for j in customers:
            if i != j:
                # Używamy czasu oczekiwanego (E) jako metryki do obliczania oszczędności
                s_ij = time_E[0, i] + time_E[0, j] - time_E[i, j]
                if s_ij > 0:
                    savings.append((s_ij, i, j))
    
    # Sortuj oszczędności malejąco, aby najpierw rozważać najbardziej obiecujące połączenia
    savings.sort(reverse=True)

    def find_route_with_endpoint(node: int, start_of_route: bool) -> Optional[int]:
        """Znajdź klucz trasy, która zaczyna/kończy się danym węzłem."""
        for key, r in routes.items():
            if len(r) > 2:
                if start_of_route and r[1] == node:
                    return key
                if not start_of_route and r[-2] == node:
                    return key
        return None

    for s, i, j in savings:
        # Warunek 1: i musi być ostatnim klientem na swojej trasie
        route_i_key = find_route_with_endpoint(i, start_of_route=False)
        # Warunek 2: j musi być pierwszym klientem na swojej trasie
        route_j_key = find_route_with_endpoint(j, start_of_route=True)

        # Jeśli oba warunki są spełnione i trasy są różne, można je połączyć
        if route_i_key is not None and route_j_key is not None and route_i_key != route_j_key:
            route_i = routes[route_i_key]
            route_j = routes[route_j_key]
            
            # Utwórz nową, połączoną trasę
            merged_route = route_i[:-1] + route_j[1:]

            # Sprawdź, czy połączona trasa jest dopuszczalna
            if ignore_all_constraints or route_feasible_ep(merged_route, time_E, time_P, time_windows, day_horizon, service_time):
                # Jeśli tak, zaktualizuj zbiór tras
                routes[route_i_key] = merged_route
                del routes[route_j_key]

    return list(routes.values())
