"""Runner SA – analogiczny do run_heuristics_demo (minimalny).
Użycie:
python run_sa.py --summary summary_app_20_loose_insertion_run1.txt --epo wwwroot/czasy_scenariusze.csv \
    --t-max 1500 --t-min 1 --alpha 0.9 --iters 500 --neigh mixed --seed 42
"""
from __future__ import annotations
import argparse
import time
import os
from Algorithms.sa_vrp import run_sa_core


def build_parser():
    p = argparse.ArgumentParser(description="Run Simulated Annealing VRP")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument('--summary', help='Plik summary_* z sekcją routes=')
    group.add_argument('--routes-json', help='Plik routes_<dataset>_<alg>.json z trasami (eksport heurystyk).')
    p.add_argument('--epo', required=False, help='CSV z czasami (czasy scenariuszy) – wymagane jeśli nie podano --app-csv')
    p.add_argument('--app-csv', help='Edge-list (app_*.csv) – jeśli podane wraz z --routes-json, macierze zostaną odbudowane z tego pliku zamiast EPO.')
    # Minimalny zestaw parametrów dla użytkownika
    p.add_argument('--day-horizon', type=int, default=600)
    p.add_argument('--t-max', type=float, default=1000.0)
    p.add_argument('--alpha', type=float, default=0.95)
    p.add_argument('--iters', type=int, default=500, help='Iteracje na temperaturę (per T)')
    p.add_argument('--neigh', choices=['swap','relocate','two_opt','mixed'], default='mixed')
    p.add_argument('--t-min', type=float, default=1.0, help='Minimalna temperatura (stała wartość, można pominąć)')
    p.add_argument('--save-best', default=None, help='Zapisz najlepsze trasy do pliku (opcjonalnie)')
    p.add_argument('--time-weight', type=float, default=1.0, help='Waga składnika cost_time (sum_route_time_E).')
    p.add_argument('--save-csv', help='Opcjonalnie: zapis metryk do pliku CSV (append).')
    return p


def main():
    ap = build_parser(); args = ap.parse_args()
    # Stałe kosztowe – spójne z heurystykami
    service_time = 0.0
    cost_per_km = 1.0
    vehicle_fixed_cost = 900.0
    penalty_late = 120.0
    penalty_horizon = 120.0
    t_min = args.t_min

    summary_file = args.summary
    routes_json = args.routes_json
    matrices_override = None
    time_windows_override = None

    def load_app_edge_list(path: str):
        import pandas as pd, numpy as np, datetime
        df = pd.read_csv(path)
        max_idx = int(max(df['StartIdx'].max(), df['EndIdx'].max()))
        n = max_idx + 1
        mats = {
            'expected': np.zeros((n, n)),
            'pessimistic': np.zeros((n, n)),
            'optimistic': np.zeros((n, n)),
            'distance_km': np.zeros((n, n)),
        }
        time_windows = {}
        def parse_window(s):
            if not isinstance(s, str) or s.strip() == '' or '-' not in s:
                return None
            a, b = s.split('-')
            try:
                from datetime import datetime as _dt
                return _dt.strptime(a.strip(), '%H:%M').time(), _dt.strptime(b.strip(), '%H:%M').time()
            except Exception:
                return None
        for _, row in df.iterrows():
            i = int(row['StartIdx']); j = int(row['EndIdx'])
            if i == j:
                continue
            mats['expected'][i, j] = float(row['Duration_time_expected'])
            mats['pessimistic'][i, j] = float(row['Duration_time_pessimistic'])
            mats['optimistic'][i, j] = float(row['Duration_time_optimistic'])
            if 'Distance_km' in row and not pd.isna(row['Distance_km']):
                try:
                    mats['distance_km'][i, j] = float(row['Distance_km'])
                except Exception:
                    pass
            if j not in time_windows:
                time_windows[j] = parse_window(row.get('DeliveryTimeWindow', ''))
        if 0 not in time_windows:
            time_windows[0] = None
        return mats, time_windows

    if routes_json:
        summary_file = None
        if args.app_csv:
            matrices_override, time_windows_override = load_app_edge_list(args.app_csv)
        else:
            print('[INFO] Używasz --routes-json bez --app-csv: pozostaję przy macierzach z EPO (upewnij się, że zawierają pełny zakres indeksów).')
    if not args.app_csv and not args.epo:
        raise SystemExit('Musisz podać --epo jeśli nie ma --app-csv (brak źródła macierzy).')

    start_time = time.time()
    init_routes, best_routes, best_cost, stats = run_sa_core(
        summary_file=summary_file,
        routes_json=routes_json,
        epo_times=args.epo,
        time_windows_file=None,
        matrices_override=matrices_override,
        time_windows_override=time_windows_override,
        day_horizon=args.day_horizon,
        service_time=service_time,
        cost_per_km=cost_per_km,
        vehicle_fixed_cost=vehicle_fixed_cost,
        penalty_late_per_min=penalty_late,
        penalty_horizon_per_min=penalty_horizon,
        t_max=args.t_max,
        t_min=t_min,
        alpha=args.alpha,
        iters_per_T=args.iters,
        neighborhood=args.neigh,
        seed=None,
        time_weight=args.time_weight,
    )
    # Domyślnie nie drukujemy initial (minimalny interfejs)
    wall_time = time.time() - start_time
    print('Best cost:', best_cost)
    print('Best solution:')
    for r in best_routes:
        print('  ', r)
    print('Rejected (horizon) moves:', stats.get('rejected_horizon'))
    init_m = stats.get('initial_metrics') or {}
    best_m = stats.get('best_metrics') or {}
    # Podstawowy zestaw kluczy (minimalny do analizy i prezentacji)
    key_list = [
        'vehicles_used', 'total_distance_km', 'cost_distance', 'cost_time', 'vehicle_cost',
        'waiting_E', 'lateness_P_sum', 'horizon_excess_E', 'makespan_E', 'sum_route_time_E', 'avg_route_time_E'
    ]
    print('\nMetrics change (initial -> best | delta):')
    for k in key_list:
        if k in init_m and k in best_m:
            iv = init_m[k]; bv = best_m[k]; dv = bv - iv
            print(f"  {k}: {iv:.3f} -> {bv:.3f} | {dv:+.3f}")

    # Zapis pełnych wyników do JSON
    if args.save_best:
        import json, os
        # Redukcja metryk: wyciągamy tylko bazowe pola z initial/best
        def slim(m: dict):
            out = {k: m[k] for k in key_list if k in m}
            return out
        slim_init = slim(init_m)
        slim_best = slim(best_m)
        # Delta tylko dla wybranych kluczy
        delta = {k: (slim_best[k] - slim_init[k]) for k in slim_init.keys() if k in slim_best}
        # Trace: tylko momenty poprawy best_cost (epoch, cost)
        trace_full = stats.get('trace') or []
        improvement_trace = []
        last_cost = None
        for (ep, Tval, bc) in trace_full:
            if last_cost is None or bc < last_cost:
                improvement_trace.append([ep, bc])
                last_cost = bc
        # Podstawowe parametry (repro): ograniczamy zbiór do najważniejszych
        params = {
            't_max': args.t_max,
            'alpha': args.alpha,
            'iters_per_T': args.iters,
            'neighborhood': args.neigh,
            'day_horizon': args.day_horizon,
            'time_weight': args.time_weight,
            'routes_source': os.path.basename(routes_json) if routes_json else os.path.basename(summary_file) if summary_file else None,
            'matrices_source': os.path.basename(args.app_csv) if args.app_csv else os.path.basename(args.epo) if args.epo else None,
        }
        payload = {
            'parameters': params,
            'best_cost': best_cost,
            'best_routes': best_routes,
            'metrics_initial': slim_init,
            'metrics_best': slim_best,
            'metrics_delta': delta,
            'process': {
                'runtime_seconds': wall_time,
                'epochs': stats.get('epochs'),
                'accepted_moves': stats.get('accepted_moves'),
                'improving_moves': stats.get('improving_moves'),
                'rejected_horizon_moves': stats.get('rejected_horizon'),
                'rejected_horizon_rate': (stats.get('rejected_horizon')/stats.get('total_attempts')) if stats.get('total_attempts') else None,
            },
            'trace_improvements': improvement_trace,
        }
        with open(args.save_best, 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print('Saved results (slim JSON) ->', args.save_best)

    # Opcjonalny zapis do CSV (dodaj argument --save-csv <plik>)
    if hasattr(args, 'save_csv') and args.save_csv:
        import csv, os, re
        routes_source = os.path.basename(routes_json) if routes_json else os.path.basename(summary_file) if summary_file else ''
        # Parsowanie nazwy: routes_app_final_<size>_<window>_something.json
        dataset = None; size = None; window_profile = None
        m = re.match(r"routes_app_final_(\d+)_(very_loose|loose|medium|tight)_", routes_source)
        if m:
            size = int(m.group(1)); window_profile = m.group(2); dataset = f"app_final_{size}_{window_profile}"
        else:
            # fallback – spróbuj prostszego wzorca
            parts = routes_source.split('_')
            for w in ['very','loose','medium','tight']:
                if w in parts:
                    window_profile = 'very_loose' if w=='very' else w
            for p in parts:
                if p.isdigit():
                    size = int(p)
            dataset = routes_source.replace('routes_','').replace('.json','') if not dataset else dataset
        csv_keys = [
            'dataset','size','window_profile',
            'routes_source','t_max','alpha','iters_per_T','neighborhood','day_horizon','time_weight',
            'best_cost','vehicles_initial','vehicles_best','distance_initial','distance_best','makespan_initial','makespan_best',
            'sum_time_initial','sum_time_best','waiting_initial','waiting_best',
            'distance_delta','makespan_delta','sum_time_delta','waiting_delta','runtime_seconds'
        ]
        row = {
            'dataset': dataset,
            'size': size,
            'window_profile': window_profile,
            'routes_source': routes_source,
            't_max': args.t_max,
            'alpha': args.alpha,
            'iters_per_T': args.iters,
            'neighborhood': args.neigh,
            'day_horizon': args.day_horizon,
            'time_weight': args.time_weight,
            'best_cost': best_cost,
            'vehicles_initial': init_m.get('vehicles_used'),
            'vehicles_best': best_m.get('vehicles_used'),
            'distance_initial': init_m.get('total_distance_km'),
            'distance_best': best_m.get('total_distance_km'),
            'makespan_initial': init_m.get('makespan_E'),
            'makespan_best': best_m.get('makespan_E'),
            'sum_time_initial': init_m.get('sum_route_time_E'),
            'sum_time_best': best_m.get('sum_route_time_E'),
            'waiting_initial': init_m.get('waiting_E'),
            'waiting_best': best_m.get('waiting_E'),
            'distance_delta': (best_m.get('total_distance_km') - init_m.get('total_distance_km')) if init_m.get('total_distance_km') is not None and best_m.get('total_distance_km') is not None else None,
            'makespan_delta': (best_m.get('makespan_E') - init_m.get('makespan_E')) if init_m.get('makespan_E') is not None and best_m.get('makespan_E') is not None else None,
            'sum_time_delta': (best_m.get('sum_route_time_E') - init_m.get('sum_route_time_E')) if init_m.get('sum_route_time_E') is not None and best_m.get('sum_route_time_E') is not None else None,
            'waiting_delta': (best_m.get('waiting_E') - init_m.get('waiting_E')) if init_m.get('waiting_E') is not None and best_m.get('waiting_E') is not None else None,
            'runtime_seconds': wall_time,
        }
        write_header = not os.path.isfile(args.save_csv)
        with open(args.save_csv, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=csv_keys)
            if write_header:
                writer.writeheader()
            writer.writerow(row)
        print('Saved slim metrics to CSV ->', args.save_csv)

if __name__ == '__main__':
    main()
