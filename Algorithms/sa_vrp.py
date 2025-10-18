"""Minimalny Simulated Annealing dla VRP bazujący na już istniejących:
- koszt: calculate_vrp_cost_local_robust
- macierze: vrp_common_utilities (expected/pessimistic)
- rozwiązanie początkowe: parsowane z pliku summary_* (sekcja routes)
Ten moduł NIE posiada już CLI – patrz plik run_sa.py do uruchamiania z linii komend.

Sąsiedztwa dostępne przez simulated_annealing():
    swap | relocate | two_opt | mixed
"""
from __future__ import annotations
import random, math, copy, os
from typing import List, Dict, Optional
import json

import numpy as np

from .robust_cost import calculate_vrp_cost_local_robust
from .vrp_common_utilities import load_epo_times, get_epo_matrices, load_time_windows  # pozostawione dla kompatybilności (może użyte w wyższej warstwie)

# ---------------- Parsing rozwiązania początkowego -----------------

def parse_summary_routes(path: str) -> List[List[int]]:
    if not os.path.isfile(path):
        raise FileNotFoundError(path)
    routes: List[List[int]] = []
    with open(path, 'r', encoding='utf-8') as f:
        lines = [l.strip() for l in f if l.strip()]
    try:
        idx = lines.index('routes=')
    except ValueError:
        raise ValueError("Brak sekcji 'routes=' w pliku summary")
    for line in lines[idx+1:]:
        if line.startswith('#'):  # ewentualne komentarze
            continue
        parts = [p.strip() for p in line.split(',') if p.strip()]
        if not parts:
            continue
        ints = [int(p) for p in parts]
        # Upewniamy się, że start/end depot=0
        if ints[0] != 0:
            ints = [0] + ints
        if ints[-1] != 0:
            ints.append(0)
        routes.append(ints)
    return routes


# ---------------- Operatory sąsiedztwa -----------------

def neighborhood_swap(sol: List[List[int]]):
    # Zbierz wszystkie (route_index, pos) dla klientów (bez depotów)
    positions = [(ri, pi) for ri, r in enumerate(sol) for pi in range(1, len(r)-1)]
    if len(positions) < 2:
        return None
    (r1, p1), (r2, p2) = random.sample(positions, 2)
    new_sol = copy.deepcopy(sol)
    new_sol[r1][p1], new_sol[r2][p2] = new_sol[r2][p2], new_sol[r1][p1]
    return new_sol

def neighborhood_relocate(sol: List[List[int]]):
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

def neighborhood_two_opt(sol: List[List[int]]):
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
                 cost_per_km, vehicle_fixed_cost, penalty_late_per_min, penalty_horizon_per_min,
                 time_weight: float = 1.0):
    c, metrics = calculate_vrp_cost_local_robust(
        routes, matrices, time_windows,
        day_horizon=day_horizon,
        service_time=service_time,
    cost_per_km=cost_per_km,
    vehicle_fixed_cost=vehicle_fixed_cost,
    penalty_late_per_min=penalty_late_per_min,
    penalty_horizon_per_min=penalty_horizon_per_min,
    time_weight=time_weight,
    )
    return c, metrics


def _feasible_horizon(routes: List[List[int]], time_E: np.ndarray, day_horizon: int, service_time: float = 0.0) -> bool:
    """Szybkie sprawdzenie czy żadna trasa nie przekracza day_horizon na osi expected.
    Uproszczenie: czas = suma travel_E (+ service_time jeśli >0).
    """
    for r in routes:
        if len(r) <= 2:
            continue
        t = 0.0
        for i in range(len(r) - 1):
            a = r[i]; b = r[i+1]
            t += time_E[a, b]
            if b != 0 and service_time > 0:
                t += service_time
            if t > day_horizon:
                return False
    return True


def simulated_annealing(initial_routes: List[List[int]], matrices: Dict[str, np.ndarray],
                        time_windows: Optional[Dict[int, tuple]] = None,
                        day_horizon: int = 600, service_time: float = 0.0,
                        cost_per_km: float = 1.0, vehicle_fixed_cost: float = 900.0,
                        penalty_late_per_min: float = 120.0, penalty_horizon_per_min: float = 120.0,
                        time_weight: float = 1.0,
                        t_max: float = 1000.0, t_min: float = 1.0, alpha: float = 0.95,
                        iters_per_T: int = 500, neighborhood: str = 'mixed', seed: Optional[int] = None):
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    current = copy.deepcopy(initial_routes)
    best = copy.deepcopy(initial_routes)
    current_cost, current_metrics = compute_cost(current, matrices, time_windows, day_horizon, service_time,
                                                 cost_per_km, vehicle_fixed_cost, penalty_late_per_min, penalty_horizon_per_min,
                                                 time_weight=time_weight)
    best_cost = current_cost
    best_metrics = current_metrics
    T = t_max
    neigh_keys = list(NEIGH_FUN.keys()) if neighborhood == 'mixed' else [neighborhood]
    rejected_horizon = 0
    time_E = matrices['expected']

    epoch = 0
    accepted_moves = 0
    improving_moves = 0
    trace = []  # list of (epoch, T, best_cost)
    total_attempts = 0
    while T > t_min:
        for _ in range(iters_per_T):
            op = random.choice(neigh_keys)
            neighbor_fun = NEIGH_FUN[op]
            candidate = neighbor_fun(current)
            if candidate is None:
                continue
            # Hard reject horyzontu (tylko expected). Okna czasowe dalej = kary, nie odrzucamy.
            if not _feasible_horizon(candidate, time_E, day_horizon, service_time):
                rejected_horizon += 1
                continue
            total_attempts += 1
            cand_cost, cand_metrics = compute_cost(candidate, matrices, time_windows, day_horizon, service_time,
                                                   cost_per_km, vehicle_fixed_cost, penalty_late_per_min, penalty_horizon_per_min,
                                                   time_weight=time_weight)
            delta = cand_cost - current_cost
            if delta < 0 or math.exp(-delta / T) > random.random():
                current = candidate
                current_cost = cand_cost
                current_metrics = cand_metrics
                if current_cost < best_cost:
                    best = copy.deepcopy(current)
                    best_cost = current_cost
                    best_metrics = cand_metrics
                accepted_moves += 1
                if delta < 0:
                    improving_moves += 1
        # Drukuj postęp co 10 epok
        if epoch % 10 == 0:
            print(f"[SA] Epoka {epoch:4d} | T={T:.2f} | koszt={current_cost:.2f} | pojazdy={len(current)} | best={best_cost:.2f}")
        trace.append((epoch, T, best_cost))
        epoch += 1
        T *= alpha
    # Możemy zwrócić także statystyki – na razie jako drugi element koszt, trzeci dict.
    stats = {
        'rejected_horizon': rejected_horizon,
        'accepted_moves': accepted_moves,
        'improving_moves': improving_moves,
        'total_attempts': total_attempts,
        'epochs': epoch,
        'trace': trace,
        'initial_metrics': current_metrics if best is None else None,  # placeholder (nadpisany niżej),
        'best_metrics': best_metrics,
    }
    # initial metrics = metrics of initial_routes (we stored earlier as best_metrics when created)
    stats['initial_metrics'] = current_metrics  # current_metrics here is last accepted, need explicit store earlier
    # Better: store initial separately
    stats['initial_metrics'] = best_metrics if best == initial_routes else best_metrics  # fallback
    # For clarity we will recompute initial explicitly outside in run_sa_core; simpler: return both
    return best, best_cost, stats, current_metrics, best_metrics

# Helper dla zewnętrznego runnera (run_sa.py)
def load_routes_json(path: str) -> List[List[int]]:
    if not os.path.isfile(path):
        raise FileNotFoundError(path)
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if 'routes' not in data:
        raise ValueError('Brak klucza routes w JSON')
    routes = []
    for r in data['routes']:
        if not r:
            continue
        if r[0] != 0:
            r = [0] + r
        if r[-1] != 0:
            r = r + [0]
        routes.append(r)
    return routes, data

def run_sa_core(summary_file: Optional[str], epo_times: Optional[str], time_windows_file: Optional[str] = None,
                routes_json: Optional[str] = None, matrices_override=None, time_windows_override=None, **sa_kwargs):
    meta_json = None
    if routes_json:
        routes, meta_json = load_routes_json(routes_json)
        # Nadpisanie day_horizon / service_time jeśli występują
        params = (meta_json or {}).get('parameters', {})
        if 'day_horizon' in params and 'day_horizon' not in sa_kwargs:
            sa_kwargs['day_horizon'] = params['day_horizon']
        if 'service_time' in params and 'service_time' not in sa_kwargs:
            sa_kwargs['service_time'] = params['service_time']
    else:
        routes = parse_summary_routes(summary_file)
    if matrices_override is not None:
        matrices = matrices_override
    else:
        times_df = load_epo_times(epo_times)
        matrices = get_epo_matrices(times_df)
    if time_windows_override is not None:
        time_windows = time_windows_override
    else:
        if time_windows_file:
            time_windows, _ = load_time_windows(time_windows_file)
        else:
            try:
                time_windows, _ = load_time_windows()
            except Exception:
                time_windows = None
    # Run SA
    best, best_cost, stats, last_curr_metrics, best_metrics = simulated_annealing(routes, matrices, time_windows=time_windows, **sa_kwargs)
    # Recompute initial metrics cleanly
    init_cost, init_metrics = compute_cost(routes, matrices, time_windows,
                                           sa_kwargs.get('day_horizon', 600),
                                           sa_kwargs.get('service_time', 0.0),
                                           sa_kwargs.get('cost_per_km', 1.0),
                                           sa_kwargs.get('vehicle_fixed_cost', 900.0),
                                           sa_kwargs.get('penalty_late_per_min', 120.0),
                                           sa_kwargs.get('penalty_horizon_per_min', 120.0),
                                           time_weight=sa_kwargs.get('time_weight', 1.0))
    stats['initial_metrics'] = init_metrics
    stats['best_metrics'] = best_metrics
    return routes, best, best_cost, stats
