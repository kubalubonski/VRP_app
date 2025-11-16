"""Batch runner dla Simulated Annealing na wszystkich plikach tras _best.json.

Użycie (przykład):
  python run_sa_batch.py --routes-dir test_data/Wyniki_json_heurystyki \
      --app-dir test_data \
      --t-max 800 1200 \
      --alpha 0.90 0.95 0.98 \
      --iters-per-T 300 500 \
      --neighborhood swap relocate two_opt mixed \
      --output sa_batch_results.csv

Opis:
- Szuka plików routes_app_final_*_best.json w katalogu --routes-dir.
- Do rekonstrukcji macierzy czasów używa odpowiadających im plików app_final_<size>_<profile>.csv z --app-dir.
- Uruchamia SA dla każdej kombinacji parametrów.
- Zapisuje wiersze do CSV (append) z kluczowymi metrykami i improvement_pct.

Aby ograniczyć czas, zmniejsz siatkę (np. tylko 2 wartości alpha i 1 iters-per-T).
"""
from __future__ import annotations
import argparse, os, re, csv, time
from Algorithms.sa_vrp import run_sa_core

# Parametry kosztowe zgodne z heurystykami
SERVICE_TIME = 0.0
COST_PER_KM = 1.0
VEHICLE_FIXED_COST = 900.0
PENALTY_HORIZON = 120.0
DAY_HORIZON_DEFAULT = 600

ROUTE_PATTERN = re.compile(r"routes_app_final_(\d+)_(very_loose|loose|medium|tight)_best\.json$")


def load_app_edge_list(path: str):
    import pandas as pd, numpy as np
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
        from datetime import datetime as _dt
        try:
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


def collect_route_files(routes_dir: str):
    out = []
    for name in os.listdir(routes_dir):
        m = ROUTE_PATTERN.match(name)
        if m:
            size = int(m.group(1)); profile = m.group(2)
            out.append((size, profile, os.path.join(routes_dir, name)))
    return sorted(out)


def build_parser():
    p = argparse.ArgumentParser(description='Batch SA over best heuristic solutions')
    p.add_argument('--routes-dir', required=True, help='Katalog z plikami routes_*_best.json')
    p.add_argument('--app-dir', required=True, help='Katalog z plikami app_final_<size>_<profile>.csv')
    p.add_argument('--t-max', nargs='+', type=float, default=[1000.0])
    p.add_argument('--t-min', type=float, default=1.0)
    p.add_argument('--alpha', nargs='+', type=float, default=[0.95])
    p.add_argument('--iters-per-T', nargs='+', type=int, default=[500])
    p.add_argument('--neighborhood', nargs='+', choices=['swap','relocate','two_opt','mixed'], default=['mixed'])
    p.add_argument('--day-horizon', type=int, default=DAY_HORIZON_DEFAULT)
    p.add_argument('--time-weight', type=float, default=1.0)
    p.add_argument('--output', required=True, help='CSV wynikowy (append lub tworzy)')
    p.add_argument('--limit', type=int, default=None, help='Opcjonalny limit liczby instancji do szybkiego testu')
    return p


def main():
    args = build_parser().parse_args()
    route_specs = collect_route_files(args.routes_dir)
    if not route_specs:
        raise SystemExit('Brak plików *_best.json w katalogu: ' + args.routes_dir)
    if args.limit:
        route_specs = route_specs[:args.limit]

    csv_cols = [
        'dataset','size','window_profile','t_max','t_min','alpha','iters_per_T','neighborhood',
        'day_horizon','time_weight','initial_cost','best_cost','improvement_pct',
        'vehicles_initial','vehicles_best','distance_initial','distance_best',
        'makespan_initial','makespan_best','waiting_initial','waiting_best',
        'accepted_moves','improving_moves','epochs','runtime_seconds'
    ]
    write_header = not os.path.isfile(args.output)

    with open(args.output, 'a', newline='', encoding='utf-8') as f_csv:
        writer = csv.DictWriter(f_csv, fieldnames=csv_cols)
        if write_header:
            writer.writeheader()

        total_jobs = 0
        for size, profile, route_path in route_specs:
            dataset_tag = f'app_final_{size}_{profile}'
            app_csv = os.path.join(args.app_dir, f'app_final_{size}_{profile}.csv')
            if not os.path.isfile(app_csv):
                print(f'[WARN] Brak pliku macierzy: {app_csv} – pomijam instancję {dataset_tag}')
                continue
            matrices, time_windows = load_app_edge_list(app_csv)

            for t_max in args.t_max:
                for alpha in args.alpha:
                    for iters in args.iters_per_T:
                        for neigh in args.neighborhood:
                            total_jobs += 1
                            start = time.time()
                            init_routes, best_routes, best_cost, stats = run_sa_core(
                                summary_file=None,
                                routes_json=route_path,
                                epo_times=None,  # korzystamy z override
                                time_windows_file=None,
                                matrices_override=matrices,
                                time_windows_override=time_windows,
                                day_horizon=args.day_horizon,
                                service_time=SERVICE_TIME,
                                cost_per_km=COST_PER_KM,
                                vehicle_fixed_cost=VEHICLE_FIXED_COST,
                                penalty_horizon_per_min=PENALTY_HORIZON,
                                t_max=t_max,
                                t_min=args.t_min,
                                alpha=alpha,
                                iters_per_T=iters,
                                neighborhood=neigh,
                                seed=None,
                                time_weight=args.time_weight,
                            )
                            wall = time.time() - start
                            init_m = stats.get('initial_metrics') or {}
                            best_m = stats.get('best_metrics') or {}
                            initial_cost = stats.get('initial_cost')
                            improvement_pct = (initial_cost - best_cost)/initial_cost if initial_cost else None
                            row = {
                                'dataset': dataset_tag,
                                'size': size,
                                'window_profile': profile,
                                't_max': t_max,
                                't_min': args.t_min,
                                'alpha': alpha,
                                'iters_per_T': iters,
                                'neighborhood': neigh,
                                'day_horizon': args.day_horizon,
                                'time_weight': args.time_weight,
                                'initial_cost': initial_cost,
                                'best_cost': best_cost,
                                'improvement_pct': improvement_pct,
                                'vehicles_initial': init_m.get('vehicles_used'),
                                'vehicles_best': best_m.get('vehicles_used'),
                                'distance_initial': init_m.get('total_distance_km'),
                                'distance_best': best_m.get('total_distance_km'),
                                'makespan_initial': init_m.get('makespan_E'),
                                'makespan_best': best_m.get('makespan_E'),
                                'waiting_initial': init_m.get('waiting_E'),
                                'waiting_best': best_m.get('waiting_E'),
                                'accepted_moves': stats.get('accepted_moves'),
                                'improving_moves': stats.get('improving_moves'),
                                'epochs': stats.get('epochs'),
                                'runtime_seconds': wall,
                            }
                            writer.writerow(row)
                            print(f"[OK] {dataset_tag} t_max={t_max} alpha={alpha} iters={iters} neigh={neigh} imp={improvement_pct:.4f if improvement_pct is not None else float('nan')} time={wall:.1f}s")
    print(f'Zakończono: {total_jobs} uruchomień SA.')

if __name__ == '__main__':
    main()
