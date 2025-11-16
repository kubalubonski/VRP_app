from typing import Dict, List, Optional, Tuple
from datetime import datetime
import numpy as np

def count_used_vehicles(vrp_solution: List[List[int]]) -> int:
    return sum(1 for r in vrp_solution if len(r) > 2)

def calculate_vrp_cost_local_robust(
    vrp_solution: List[List[int]],
    matrices: Dict[str, np.ndarray],
    time_windows: Optional[Dict[int, Optional[Tuple[datetime.time, datetime.time]]]] = None,
    day_horizon: int = 600,
    service_time: float = 0.0,
    # Nowy model kosztu – parametry literaturowe
    cost_per_km: float = 1.0,
    vehicle_fixed_cost: float = 900.0,
    penalty_horizon_per_min: float = 120.0,
    time_weight: float = 1.0,
):
    """Nowa funkcja kosztu (literatura VRPTW).

    Całkowity koszt (bez komponentu spóźnień – okna twarde):
        C = cost_per_km * (suma_dystansu_km) + vehicle_fixed_cost * K
            + penalty_horizon_per_min * (suma przekroczeń horyzontu)

    Uwagi:
    - Zachowujemy obliczanie waiting time jako METRYKĘ diagnostyczną, ale nie wpływa ona na koszt.
    - Dystans: jeśli macierz 'distance_km' jest dostępna używamy jej; w przeciwnym razie aproksymujemy dystans czasem oczekiwanym (1:1) jako fallback.
    - Lateness liczone na osi pesymistycznej względem końca okna.
    - Przekroczenie horyzontu (horizon_excess) liczone na osi expected.
    - service_time doklejany po przybyciu (po ewentualnym czekaniu) jeśli b != 0.
    """
    time_E = matrices['expected']
    time_P = matrices['pessimistic']
    dist_matrix = matrices.get('distance_km', None)

    total_distance_km = 0.0
    total_wait_E = 0.0  # tylko diagnostyka
    # Lateness usunięte – okna P twarde, brak akumulacji
    total_lateness_P = 0.0
    horizon_excess = 0.0

    route_end_times_E: List[float] = []
    route_end_times_P: List[float] = []
    route_waiting_E_list: List[float] = []
    route_distance_list: List[float] = []

    base_dt = datetime.strptime("08:00", "%H:%M")

    for route in vrp_solution:
        if len(route) <= 2:
            continue
        timeline_E = 0.0
        timeline_P = 0.0
        route_wait_E = 0.0
        route_dist = 0.0

        for i in range(len(route) - 1):
            a = route[i]; b = route[i+1]
            travel_E = time_E[a, b]
            travel_P = time_P[a, b]
            if dist_matrix is not None:
                step_dist = dist_matrix[a, b]
            else:
                # fallback: przyjmij proporcję 1:1 do expected travel
                step_dist = travel_E
            total_distance_km += step_dist
            route_dist += step_dist

            arrival_E = timeline_E + travel_E
            arrival_P = timeline_P + travel_P

            if time_windows and b in time_windows and time_windows[b]:
                ws, we = time_windows[b]
                ws_minutes = (datetime.combine(base_dt.date(), ws) - base_dt).seconds / 60
                we_minutes = (datetime.combine(base_dt.date(), we) - base_dt).seconds / 60

                if arrival_E < ws_minutes:
                    wait_E = ws_minutes - arrival_E
                else:
                    wait_E = 0.0
                total_wait_E += wait_E
                route_wait_E += wait_E

                # Brak obliczania lateness – naruszenia P odrzucane wcześniej

                start_service_E = max(arrival_E, ws_minutes)
                start_service_P = max(arrival_P, ws_minutes)
                if b != 0 and service_time > 0:
                    start_service_E += service_time
                    start_service_P += service_time
                timeline_E = start_service_E
                timeline_P = start_service_P
            else:
                if b != 0 and service_time > 0:
                    arrival_E_with_service = arrival_E + service_time
                    arrival_P_with_service = arrival_P + service_time
                else:
                    arrival_E_with_service = arrival_E
                    arrival_P_with_service = arrival_P
                timeline_E = arrival_E_with_service
                timeline_P = arrival_P_with_service

        route_end_times_E.append(timeline_E)
        route_end_times_P.append(timeline_P)
        route_waiting_E_list.append(route_wait_E)
        route_distance_list.append(route_dist)
        if timeline_E > day_horizon:
            horizon_excess += (timeline_E - day_horizon)

    k_used = count_used_vehicles(vrp_solution)
    vehicle_cost = vehicle_fixed_cost * k_used

    cost_distance = cost_per_km * total_distance_km
    cost_horizon = penalty_horizon_per_min * horizon_excess
    # Suma czasów zakończenia tras (proxy wysiłku floty) jest obliczona poniżej jako sum_route_time_E.
    # Waga `time_weight` umożliwia włączenie/wyłączenie wpływu sumy czasów zakończenia tras
    # na funkcję celu. Domyślnie (1.0) jest to aktywny składnik kosztu.
    cost_time = time_weight * sum_route_time_E
    total_cost += cost_time
    metrics = {
        'total_distance_km': total_distance_km,
        'waiting_E': total_wait_E,
        # Alias bardziej intuicyjny dla zewnętrznych raportów / CSV
        'waiting_total': total_wait_E,
    'lateness_P_sum': 0.0,
        'horizon_excess_E': horizon_excess,
        'vehicle_cost': vehicle_cost,
        'vehicles_used': k_used,
        'cost_distance': cost_distance,
    'cost_penalty_late': 0.0,
        'cost_penalty_horizon': cost_horizon,
        'cost_time': cost_time,
        'w_time': time_weight,
        'route_end_times_E': route_end_times_E,
        'route_end_times_P': route_end_times_P,
        'route_waiting_E_list': route_waiting_E_list,
        'route_distance_list': route_distance_list,
        'max_route_end_E': max(route_end_times_E) if route_end_times_E else 0.0,
        'max_route_end_P': max(route_end_times_P) if route_end_times_P else 0.0,
        # Makespan w jednostkach minut (oś expected) – maksymalne zakończenie trasy
        'makespan_E': max(route_end_times_E) if route_end_times_E else 0.0,
        # Suma i średnia czasów zakończeń tras (proxy wysiłku floty na osi expected)
        'sum_route_time_E': sum_route_time_E,
        'avg_route_time_E': avg_route_time_E,
        'service_time_per_visit': service_time,
        'total_service_time': total_service_time,
    }
    return total_cost, metrics
