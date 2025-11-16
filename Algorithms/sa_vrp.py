"""Simulated Annealing dla VRP
Minimalna implementacja:
 - Propagacja tylko expected (E), arrival_P punktowo.
 - Twarde okna dla E i P; horyzont dnia na osi E.
 - Koszt: dystans + koszt pojazdów + kara horyzontu + (opcjonalnie) komponent czasu.
 - Sąsiedztwa: swap | relocate | two_opt | mixed.
"""
from __future__ import annotations
import random, math, copy, os, json
from typing import List, Dict, Optional, Tuple

import numpy as np

from .robust_cost import calculate_vrp_cost_local_robust
from .vrp_common_utilities import load_epo_times, get_epo_matrices, load_time_windows
from .common_feasibility import route_feasible_ep_classified

# ---------------- Parsowanie tras (unifikacja JSON / summary) -----------------

def load_routes_generic(path: str) -> Tuple[List[List[int]], Optional[Dict]]:
    """Załaduj trasy z pliku summary_*.txt (sekcja routes=) lub z pliku JSON.

    Zwraca tuple (routes, meta_dict). Dla pliku summary meta_dict == None.
    Normalizuje każdą trasę tak, aby zaczynała i kończyła się 0 (depot).
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(path)
    _, ext = os.path.splitext(path.lower())
    routes: List[List[int]] = []
    meta: Optional[Dict] = None
    if ext == '.json':
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        meta = data
        if 'routes' not in data:
            raise ValueError('Brak klucza routes w JSON')
        for r in data['routes']:
            if not r:
                continue
            if r[0] != 0:
                r = [0] + r
            if r[-1] != 0:
                r = r + [0]
            routes.append(r)
    else:
        with open(path, 'r', encoding='utf-8') as f:
            lines = [l.strip() for l in f if l.strip()]
        if 'routes=' not in lines:
            raise ValueError("Brak sekcji 'routes=' w pliku summary")
        start = lines.index('routes=') + 1
        for line in lines[start:]:
            if line.startswith('#'):
                continue
            parts = [p for p in line.split(',') if p.strip()]
            if not parts:
                continue
            ints = [int(p) for p in parts]
            if ints[0] != 0:
                ints.insert(0, 0)
            if ints[-1] != 0:
                ints.append(0)
            routes.append(ints)
    return routes, meta


# ---------------- Operatory sąsiedztwa -----------------

def neighborhood_swap(sol: List[List[int]]) -> Optional[List[List[int]]]:
    # Zbierz wszystkie (route_index, pos) dla klientów (bez depotów)
    positions = [(ri, pi) for ri, r in enumerate(sol) for pi in range(1, len(r)-1)]
    if len(positions) < 2:
        return None
    (r1, p1), (r2, p2) = random.sample(positions, 2)
    new_sol = copy.deepcopy(sol)
    new_sol[r1][p1], new_sol[r2][p2] = new_sol[r2][p2], new_sol[r1][p1]
    return new_sol

def neighborhood_relocate(sol: List[List[int]]) -> Optional[List[List[int]]]:
    routes_non_empty = [ri for ri, r in enumerate(sol) if len(r) > 2]
    if not routes_non_empty:
        return None
    src = random.choice(routes_non_empty)
    r_src = sol[src]
    if len(r_src) <= 3:  # tylko jeden klient – możemy potem usunąć trasę
        pos_client = 1
    else:
        pos_client = random.randint(1, len(r_src)-2)
    client = r_src[pos_client]
    dest = random.randrange(len(sol))
    if dest == src and len(r_src) <= 3:
        # nic sensownego – spróbuj innej trasy docelowej jeśli istnieje
        if len(sol) > 1:
            dest = (dest + 1) % len(sol)
    new_sol = copy.deepcopy(sol)
    new_sol[src].pop(pos_client)
    if len(new_sol[src]) == 2:  # stała się pusta
        del new_sol[src]
        if dest > src:
            dest -= 1
    # jeśli po usunięciu nie ma tras, dodaj nową
    if not new_sol:
        new_sol.append([0, client, 0])
        return new_sol
    if dest >= len(new_sol):
        dest = len(new_sol)-1
    insert_route = new_sol[dest]
    insert_pos = random.randint(1, len(insert_route)-1)
    insert_route.insert(insert_pos, client)
    return new_sol

def neighborhood_two_opt(sol: List[List[int]]) -> Optional[List[List[int]]]:
    candidate_routes = [ri for ri, r in enumerate(sol) if len(r) > 4]
    if not candidate_routes:
        return None
    ri = random.choice(candidate_routes)
    r = sol[ri]
    i = random.randint(1, len(r)-3)
    j = random.randint(i+1, len(r)-2)
    new_r = r[:i] + list(reversed(r[i:j])) + r[j:]
    new_sol = copy.deepcopy(sol)
    new_sol[ri] = new_r
    return new_sol

NEIGH_FUN = {
    'swap': neighborhood_swap,
    'relocate': neighborhood_relocate,
    'two_opt': neighborhood_two_opt,
}


# ---------------- SA core -----------------

def compute_cost(routes: List[List[int]], matrices, time_windows, day_horizon, service_time,
                 cost_per_km, vehicle_fixed_cost, penalty_horizon_per_min,
                 time_weight: float = 1.0) -> Tuple[float, Dict]:
    """Wrapper dla `calculate_vrp_cost_local_robust`.
    
    `penalty_late_per_min` jest celowo pominięty i zerowany w SA, ponieważ
    filtr E/P (twarde okna) eliminuje spóźnienia.
    """
    cost, metrics = calculate_vrp_cost_local_robust(
        routes, matrices, time_windows,
        day_horizon=day_horizon,
        service_time=service_time,
        cost_per_km=cost_per_km,
        vehicle_fixed_cost=vehicle_fixed_cost,
        penalty_horizon_per_min=penalty_horizon_per_min,
        time_weight=time_weight,
    )
    return cost, metrics


def simulated_annealing(initial_routes: List[List[int]], matrices: Dict[str, np.ndarray],
                        time_windows: Optional[Dict[int, tuple]] = None,
                        day_horizon: int = 600, service_time: float = 0.0,
                        cost_per_km: float = 1.0, vehicle_fixed_cost: float = 900.0,
                        penalty_horizon_per_min: float = 120.0,
                        time_weight: float = 1.0,
                        t_max: float = 1000.0, t_min: float = 1.0, alpha: float = 0.95,
                        iters_per_T: int = 500, neighborhood: str = 'mixed', seed: Optional[int] = None):
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    current = copy.deepcopy(initial_routes)
    best = copy.deepcopy(initial_routes)
    # Kara za spóźnienia (lateness) jest zerowana, ponieważ filtr E/P i twarde okna
    # uniemożliwiają generowanie niedopuszczalnych (spóźnionych) rozwiązań.
    current_cost, current_metrics = compute_cost(current, matrices, time_windows, day_horizon, service_time,
                                                 cost_per_km, vehicle_fixed_cost, penalty_horizon_per_min,
                                                 time_weight=time_weight)
    # Zachowaj koszt startowy przed jakąkolwiek poprawą – potrzebny do poprawnego wyliczenia improvement_pct
    initial_cost = current_cost
    best_cost = current_cost
    best_metrics = current_metrics

    T = t_max
    neigh_keys = list(NEIGH_FUN.keys()) if neighborhood == 'mixed' else [neighborhood]
    
    # Statystyki odrzuceń
    rejected_horizon = 0
    rejected_window_E = 0
    rejected_window_P = 0
    rejected_window_both = 0
    
    time_E = matrices['expected']
    time_P = matrices['pessimistic']

    epoch = 0
    accepted_moves = 0
    improving_moves = 0
    trace: List[Tuple[int, float, float]] = []
    total_attempts = 0

    while T > t_min:
        for _ in range(iters_per_T):
            total_attempts += 1
            neigh_key = random.choice(neigh_keys)
            candidate = NEIGH_FUN[neigh_key](current)
            if candidate is None:
                continue

            # Weryfikacja dopuszczalności – wszystkie trasy muszą być OK
            is_feasible = True
            cand_vio_E, cand_vio_P, cand_vio_both = False, False, False
            
            for r in candidate:
                ok, vio_E, vio_P, vio_both = route_feasible_ep_classified(
                    r, time_E, time_P, time_windows, day_horizon, service_time
                )
                if not ok:
                    is_feasible = False
                    # Agreguj flagi naruszeń z poszczególnych tras
                    if vio_E: cand_vio_E = True
                    if vio_P: cand_vio_P = True
                    if vio_both: cand_vio_both = True
            
            if not is_feasible:
                # Zliczanie typów naruszeń dla celów analitycznych
                if cand_vio_E: rejected_window_E += 1
                if cand_vio_P: rejected_window_P += 1
                if cand_vio_both: rejected_window_both += 1
                # Horyzont jest sprawdzany wewnątrz `route_feasible_ep_classified`,
                # więc jego naruszenie również ustawi `cand_vio_E` na True.
                # Dla uproszczenia nie tworzymy osobnego licznika, gdyż jest to podkategoria `vio_E`.
                continue

            cand_cost, _ = compute_cost(candidate, matrices, time_windows, day_horizon, service_time,
                                        cost_per_km, vehicle_fixed_cost, penalty_horizon_per_min,
                                        time_weight=time_weight)
            
            delta = cand_cost - current_cost
            if delta < 0:
                current = candidate
                current_cost = cand_cost
                improving_moves += 1
                accepted_moves += 1
                if cand_cost < best_cost:
                    best = candidate
                    best_cost = cand_cost
                    # Metryki liczymy tylko dla najlepszego rozwiązania, aby oszczędzić czas
                    _, best_metrics = compute_cost(best, matrices, time_windows, day_horizon, service_time,
                                                   cost_per_km, vehicle_fixed_cost, penalty_horizon_per_min,
                                                   time_weight=time_weight)
            elif math.exp(-delta / T) > random.random():
                current = candidate
                current_cost = cand_cost
                accepted_moves += 1
        
        trace.append((epoch, T, best_cost))
        T *= alpha
        epoch += 1

    stats = {
        'initial_cost': initial_cost,
        'initial_metrics': current_metrics,  # Metryki startowe
        'rejected_horizon': rejected_horizon, # Ten licznik jest już nieużywany, ale zostaje dla API
        'accepted_moves': accepted_moves,
        'improving_moves': improving_moves,
        'total_attempts': total_attempts,
        'epochs': epoch,
        'trace': trace,
        'best_metrics': best_metrics,
        'rejected_window_E': rejected_window_E,
        'rejected_window_P': rejected_window_P,
        'rejected_window_both': rejected_window_both,
    }
    return best, best_cost, stats

# Helper dla zewnętrznego runnera (run_sa.py)
def load_routes_json(path: str) -> List[List[int]]:  # zachowujemy dla kompatybilności zewnętrznych importów
    routes, meta = load_routes_generic(path)
    return routes, (meta or {})

def run_sa_core(summary_file: Optional[str], epo_times: Optional[str], time_windows_file: Optional[str] = None,
                routes_json: Optional[str] = None, matrices_override=None, time_windows_override=None, **sa_kwargs):
    meta_json = None
    if routes_json:
        # 1. Preferuj plik JSON z trasami (wynik heurystyki)
        routes, meta_json = load_routes_generic(routes_json)
        if not routes:
            raise SystemExit(f"Błąd: Plik JSON '{routes_json}' nie zawiera tras lub jest pusty.")
    elif summary_file:
        # 2. Alternatywnie, użyj pliku summary (starszy format)
        routes, _ = load_routes_generic(summary_file)
        if not routes:
            raise SystemExit(f"Błąd: Plik summary '{summary_file}' nie zawiera tras.")
    else:
        raise SystemExit("Błąd: Nie podano źródła tras (ani --routes-json, ani --summary).")

    if matrices_override is not None:
        matrices = matrices_override
    else:
        # Jeśli nie ma nadpisania, buduj z EPO
        epo_df = load_epo_times(epo_times)
        matrices = get_epo_matrices(epo_df)

    if time_windows_override is not None:
        time_windows = time_windows_override
    else:
        # Jeśli nie ma nadpisania, buduj z pliku (wymaga `time_windows_file`)
        if not time_windows_file:
            # Domyślnie brak okien, jeśli nie podano pliku
            time_windows = {}
        else:
            time_windows, _ = load_time_windows(time_windows_file)

    # Uruchomienie SA z przekazaniem wszystkich pozostałych argumentów
    best, best_cost, stats = simulated_annealing(routes, matrices, time_windows=time_windows, **sa_kwargs)

    # Zwróć komplet wyników, w tym trasy początkowe dla porównania
    return routes, best, best_cost, stats
