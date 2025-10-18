"""Demo uruchomienia heurystyk startowych (bez SA)

Możliwe dwa źródła danych:
1) Domyślnie: pliki w stylu poprzedniego pipeline (wwwroot/czasy_scenariusze.csv + dane_wejsciowe_geocoded.csv)
2) Edge-list w formacie aplikacji (app_*), podaj argument --app-csv test_data/app_small.csv

Porównywane heurystyki:
- Clarke–Wright Savings
- Greedy Insertion

Wypisywane są metryki funkcji local_robust.
"""
import os, sys, argparse
import re
import pandas as pd
import numpy as np

# Zapewnij działający import gdy uruchomisz poza katalogiem Algorithms
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if THIS_DIR not in sys.path:
    sys.path.append(THIS_DIR)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
ALG_DIR = os.path.join(ROOT_DIR, 'Algorithms')
if ALG_DIR not in sys.path:
    sys.path.append(ALG_DIR)

from Algorithms.vrp_common_utilities import (
    load_epo_times, load_time_windows, get_epo_matrices
)
from Algorithms.robust_cost import calculate_vrp_cost_local_robust
from Algorithms.heuristic_savings import clarke_wright_savings
from Algorithms.heuristic_insertion import greedy_insertion

# Stałe kosztowe (upraszczamy interfejs – brak już flag ich zmiany)
DAY_HORIZON = 600  # domyślny horyzont – nadpisywalny przez --day-horizon
COST_PER_KM = 1.0
VEHICLE_FIXED_COST = 900.0
PENALTY_LATE_PER_MIN = 120.0
PENALTY_HORIZON_PER_MIN = 120.0
# Waga składnika czasowego (cost_time = TIME_WEIGHT * sum_route_time_E)
TIME_WEIGHT = 1.0  # można łatwo zmienić w jednym miejscu

def load_app_edge_list(path: str):
    df = pd.read_csv(path)
    max_idx = int(max(df['StartIdx'].max(), df['EndIdx'].max()))
    n = max_idx + 1
    mats = {
        'expected': np.zeros((n, n)),
        'pessimistic': np.zeros((n, n)),
        'optimistic': np.zeros((n, n)),
        # Dodatkowa macierz dystansów fizycznych (km) do kosztu odległości
        'distance_km': np.zeros((n, n)),
    }
    time_windows = {}
    def parse_window(s):
        if not isinstance(s, str) or s.strip() == '' or '-' not in s:
            return None
        a, b = s.split('-')
        try:
            from datetime import datetime
            return datetime.strptime(a.strip(), '%H:%M').time(), datetime.strptime(b.strip(), '%H:%M').time()
        except Exception:
            return None
    for _, row in df.iterrows():
        i = int(row['StartIdx']); j = int(row['EndIdx'])
        if i == j:
            continue
        mats['expected'][i, j] = float(row['Duration_time_expected'])
        mats['pessimistic'][i, j] = float(row['Duration_time_pessimistic'])
        mats['optimistic'][i, j] = float(row['Duration_time_optimistic'])
        # Dystans fizyczny (km) – jeśli kolumna istnieje
        if 'Distance_km' in row and not pd.isna(row['Distance_km']):
            try:
                mats['distance_km'][i, j] = float(row['Distance_km'])
            except Exception:
                mats['distance_km'][i, j] = 0.0
        if j not in time_windows:
            time_windows[j] = parse_window(row.get('DeliveryTimeWindow', ''))
    if 0 not in time_windows:
        time_windows[0] = None
    return mats, time_windows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--app-csv', help='Ścieżka do pliku edge-list (app_*). Jeśli brak – użyje wwwroot/.')
    parser.add_argument('--day-horizon', type=int, default=600)
    parser.add_argument('--service-time', type=float, default=0.0, help='Stały czas obsługi (minuty) na każdą wizytę klienta (0 = brak).')
    # Usuwamy seed i dynamiczne modyfikacje kosztów – spójność eksperymentów
    parser.add_argument('--append-csv', help='Ścieżka do pliku CSV – dopisz wyniki (Savings & Insertion). Tworzy nagłówek jeśli brak pliku. (stały kompaktowy zestaw kolumn)')
    parser.add_argument('--repeat', type=int, default=1, help='Ile razy powtórzyć uruchomienie (losowość w insertion).')
    parser.add_argument('--ignore-p', action='store_true', help='Ignoruj okna czasowe na osi pesymistycznej (dalej pilnuj horyzontu dnia). Eksperymentalne.')
    parser.add_argument('--ignore-all', action='store_true', help='Ignoruj okna pesymistyczne i horyzont dnia podczas konstrukcji (pełna swoboda) – eksperyment.')
    parser.add_argument('--best-only', action='store_true', help='Jeśli podano --repeat>1: do CSV zapisz tylko najlepszy (minimalny total_cost) wariant dla każdego algorytmu.')
    parser.add_argument('--save-routes', action='store_true', help='Zapisz trasy i metryki do plików (routes_*.txt) obok danych wejściowych')
    parser.add_argument('--export-routes-json', action='store_true', help='Jeśli podano: zapisz minimalne pliki routes_<dataset>_<alg>.json (interfejs wejścia dla SA).')
    parser.add_argument('--no-summary', action='store_true', help='Nie twórz plików summary_*.txt (szybszy batch, mniej plików).')
    # Usunięto --diagnostics aby uprościć interfejs; zawsze zapisujemy podstawowy zestaw, szczegóły w plikach summary
    args = parser.parse_args()

    global DAY_HORIZON
    DAY_HORIZON = args.day_horizon  # jedyna dynamiczna zmiana

    if args.app_csv:
        print(f"Ładowanie edge-list z {args.app_csv} ...")
        matrices, time_windows = load_app_edge_list(args.app_csv)
        input_dir = os.path.dirname(args.app_csv)
    else:
        print("Ładowanie danych (format bazowy wwwroot)...")
        matrices = get_epo_matrices(load_epo_times())
        time_windows, _ = load_time_windows()
        input_dir = '.'

    # Multi-run handling
    runs_s = []  # list of (cost, solution, metrics)
    runs_i = []
    import random as _rd  # zachowujemy losowość dla insertion (bez seeda)
    for r_idx in range(1, args.repeat + 1):
        # Savings (deterministyczny - ale zachowujemy dla symetrii)
        sol_s = clarke_wright_savings(
            matrices, time_windows,
            day_horizon=DAY_HORIZON,
            service_time=args.service_time,
            ignore_p_constraints=args.ignore_p,
            ignore_all_constraints=args.ignore_all,
        )
        cs, ms = calculate_vrp_cost_local_robust(
            sol_s, matrices, time_windows,
            day_horizon=DAY_HORIZON,
            service_time=args.service_time,
            cost_per_km=COST_PER_KM,
            vehicle_fixed_cost=VEHICLE_FIXED_COST,
            penalty_late_per_min=PENALTY_LATE_PER_MIN,
            penalty_horizon_per_min=PENALTY_HORIZON_PER_MIN,
            time_weight=TIME_WEIGHT,
        )
        runs_s.append((cs, sol_s, ms))

        # Insertion (losowość przez shuffle)
        sol_i = greedy_insertion(
            matrices, time_windows,
            day_horizon=DAY_HORIZON,
            service_time=args.service_time,
            cost_per_km=COST_PER_KM,
            vehicle_fixed_cost=VEHICLE_FIXED_COST,
            penalty_late_per_min=PENALTY_LATE_PER_MIN,
            penalty_horizon_per_min=PENALTY_HORIZON_PER_MIN,
            ignore_p_constraints=args.ignore_p,
            ignore_all_constraints=args.ignore_all,
        )
        ci, mi = calculate_vrp_cost_local_robust(
            sol_i, matrices, time_windows,
            day_horizon=DAY_HORIZON,
            service_time=args.service_time,
            cost_per_km=COST_PER_KM,
            vehicle_fixed_cost=VEHICLE_FIXED_COST,
            penalty_late_per_min=PENALTY_LATE_PER_MIN,
            penalty_horizon_per_min=PENALTY_HORIZON_PER_MIN,
            time_weight=TIME_WEIGHT,
        )
        runs_i.append((ci, sol_i, mi))

    # Wybór do prezentacji
    def pick(runs):
        if args.best_only:
            return min(runs, key=lambda x: x[0]), runs.index(min(runs, key=lambda x: x[0]))+1
        return runs[-1], len(runs)  # ostatni run jeśli nie best_only

    (cs, sol_s, ms), idx_s = pick(runs_s)
    (ci, sol_i, mi), idx_i = pick(runs_i)

    print(f"\nHeurystyka: Clarke–Wright Savings (run_index={idx_s}/{args.repeat})")
    print("Routes:", sol_s)
    print("Cost:", cs)
    ms_print = {k:v for k,v in ms.items() if not k.startswith('route_') and k not in ('max_route_end_P',)}
    print("Metrics:", ms_print)

    print(f"\nHeurystyka: Greedy Insertion (run_index={idx_i}/{args.repeat})")
    print("Routes:", sol_i)
    print("Cost:", ci)
    mi_print = {k:v for k,v in mi.items() if not k.startswith('route_') and k not in ('max_route_end_P',)}
    print("Metrics:", mi_print)

    print("\nPorównanie podsumowanie:")
    def short(m):
        return {k: round(v,2) for k,v in m.items() if k in ('total_distance_km','vehicle_cost','vehicles_used','lateness_P_sum','horizon_excess_E','cost_distance','cost_penalty_late','cost_penalty_horizon')}
    print("Savings:", short(ms))
    print("Insertion:", short(mi))
    print("Lepszy koszt:", 'Savings' if cs < ci else 'Insertion')
    print("Gotowe.")

    def export_routes_json(path, dataset_tag, algorithm_label, cost, routes, metrics):
        import json, datetime
        core_metric_keys = [
            'vehicles_used','total_distance_km','waiting_total','lateness_P_sum','horizon_excess_E',
            'vehicle_cost','cost_distance','cost_penalty_late','cost_penalty_horizon','makespan_E',
            'sum_route_time_E','avg_route_time_E','total_service_time','cost_time'
        ]
        # Wyciągnij size/profile dla dokumentacji w JSON
        m = re.match(r'app_final_(\\d+)_(tight|medium|loose|very_loose)$', dataset_tag)
        ds_size = int(m.group(1)) if m else None
        ds_profile = m.group(2) if m else None
        payload = {
            'version': 1,
            'dataset': dataset_tag,
            'dataset_size': ds_size,
            'window_profile': ds_profile,
            'algorithm': algorithm_label,
            'generated_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'parameters': {
                'day_horizon': DAY_HORIZON,
                'service_time': args.service_time,
                'cost_model': {
                    'cost_per_km': COST_PER_KM,
                    'vehicle_fixed_cost': VEHICLE_FIXED_COST,
                    'penalty_late_per_min': PENALTY_LATE_PER_MIN,
                    'penalty_horizon_per_min': PENALTY_HORIZON_PER_MIN,
                    'time_weight': TIME_WEIGHT,
                }
            },
            'routes': routes,
            'metrics': {
                'total_cost': cost,
                **{k: metrics[k] for k in core_metric_keys if k in metrics}
            }
        }
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print(f"[JSON] Zapisano {path}")

    if args.export_routes_json:
        dataset_tag = os.path.splitext(os.path.basename(args.app_csv))[0] if args.app_csv else 'base'
        base_dir = os.path.dirname(args.append_csv) if args.append_csv else (os.path.dirname(args.app_csv) if args.app_csv else '.')
        json_s = os.path.join(base_dir, f"routes_{dataset_tag}_savings.json")
        json_i = os.path.join(base_dir, f"routes_{dataset_tag}_insertion.json")
        export_routes_json(json_s, dataset_tag, 'Savings', cs, sol_s, ms)
        export_routes_json(json_i, dataset_tag, 'Insertion', ci, sol_i, mi)
        # Plik best (wybór niższego total_cost); tie-breaker: mniej pojazdów, potem mniejszy dystans
        if cs < ci:
            best_alg, best_cost, best_routes, best_metrics = 'Savings', cs, sol_s, ms
        elif ci < cs:
            best_alg, best_cost, best_routes, best_metrics = 'Insertion', ci, sol_i, mi
        else:
            # Koszty równe – tie-break
            if ms['vehicles_used'] != mi['vehicles_used']:
                choose_insertion = mi['vehicles_used'] < ms['vehicles_used']
            elif ms['total_distance_km'] != mi['total_distance_km']:
                choose_insertion = mi['total_distance_km'] < ms['total_distance_km']
            else:
                # Ostatecznie preferuj Insertion (zwykle bardziej kosztowa konstrukcja)
                choose_insertion = True
            if choose_insertion:
                best_alg, best_cost, best_routes, best_metrics = 'Insertion', ci, sol_i, mi
            else:
                best_alg, best_cost, best_routes, best_metrics = 'Savings', cs, sol_s, ms
        best_path = os.path.join(base_dir, f"routes_{dataset_tag}_best.json")
        export_routes_json(best_path, dataset_tag, f"BEST({best_alg})", best_cost, best_routes, best_metrics)

    if args.save_routes:
        from datetime import datetime
        dataset_tag = 'base'
        if args.app_csv:
            dataset_tag = os.path.splitext(os.path.basename(args.app_csv))[0]
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        suffix = f"_{dataset_tag}_{ts}"
        def write_routes(path, routes, cost, metrics):
            with open(path, 'w', encoding='utf-8') as f:
                f.write(f"cost={cost}\n")
                for k,v in metrics.items():
                    if k.startswith('route_') or k in ('max_route_end_P',):
                        continue
                    f.write(f"{k}={v}\n")
                f.write("routes=\n")
                for r in routes:
                    f.write(','.join(map(str,r)) + '\n')
        base = os.path.join(input_dir, f'routes_savings{suffix}.txt')
        write_routes(base, sol_s, cs, ms)
        base2 = os.path.join(input_dir, f'routes_insertion{suffix}.txt')
        write_routes(base2, sol_i, ci, mi)
        print(f"Zapisano trasy: {base}, {base2}")

    # CSV append (wybrany podzbiór metryk)
    if args.append_csv:
        import csv as _csv, os as _os
        # Kompaktowy stały zestaw kolumn
        def parse_dataset(ds_name: str):
            m = re.match(r'app_final_(\d+)_(tight|medium|loose|very_loose)\.csv$', os.path.basename(ds_name)) if ds_name else None
            if m:
                return int(m.group(1)), m.group(2)
            return None, None
        ds_size, ds_profile = parse_dataset(args.app_csv) if args.app_csv else (None, None)

        def extract_row(label, cost, metrics, run_index):
            solution = sol_s if label=='Savings' else sol_i
            visits = sum(max(len(r)-2, 0) for r in solution)
            # Preferuj alias waiting_total jeśli istnieje
            waiting_total_val = metrics.get('waiting_total', metrics.get('waiting_E', 0.0))
            avg_wait = waiting_total_val / visits if visits>0 else 0.0
            avg_distance_per_route = metrics['total_distance_km'] / metrics['vehicles_used'] if metrics['vehicles_used']>0 else 0.0
            cost_time_val = metrics.get('cost_time')
            w_time_val = metrics.get('w_time')
            return {
                'dataset': os.path.splitext(os.path.basename(args.app_csv))[0] if args.app_csv else 'base',
                'size': ds_size,
                'window_profile': ds_profile,
                'algorithm': label,
                'total_cost': cost,
                'vehicles_used': metrics['vehicles_used'],
                'total_distance_km': metrics['total_distance_km'],
                'waiting_total': waiting_total_val,
                'avg_distance_per_route': avg_distance_per_route,
                'avg_wait_per_client': avg_wait,
                'lateness_P_sum': metrics['lateness_P_sum'],
                'horizon_excess_E': metrics['horizon_excess_E'],
                'makespan_E': metrics.get('makespan_E', metrics.get('max_route_end_E', 0.0)),
                'sum_route_time_E': metrics.get('sum_route_time_E', 0.0),
                'avg_route_time_E': metrics.get('avg_route_time_E', 0.0),
                'cost_time': cost_time_val,
                'w_time': w_time_val,
            }
        rows = [
            extract_row('Savings', cs, ms, idx_s),
            extract_row('Insertion', ci, mi, idx_i)
        ]
        file_exists = _os.path.exists(args.append_csv)
        with open(args.append_csv, 'a', newline='', encoding='utf-8') as f:
            fieldnames = list(rows[0].keys())
            writer = _csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            else:
                # ostrzeżenie jeśli nagłówek nie pasuje
                try:
                    with open(args.append_csv, 'r', encoding='utf-8') as fr:
                        first_line = fr.readline().strip().split(',')
                    if first_line != fieldnames:
                        print('[UWAGA] Istniejący plik ma inny układ kolumn – zalecane użycie nowego pliku.')
                except Exception:
                    pass
            for r in rows:
                writer.writerow(r)
        print(f"Dopisano wyniki do CSV: {args.append_csv}")

        # Tworzymy dodatkowe pliki podsumowań (summary_*.txt) w tym samym katalogu co CSV
        summary_dir = os.path.dirname(os.path.abspath(args.append_csv)) or '.'
        dataset_tag = os.path.splitext(os.path.basename(args.app_csv))[0] if args.app_csv else 'base'
        def write_summary(alg_label, cost, metrics, run_index, routes):
            fname = f"summary_{dataset_tag}_{alg_label.lower()}_run{run_index}.txt"
            path = os.path.join(summary_dir, fname)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(f"dataset={dataset_tag}\n")
                if ds_size is not None:
                    f.write(f"size={ds_size}\n")
                if ds_profile is not None:
                    f.write(f"window_profile={ds_profile}\n")
                f.write(f"algorithm={alg_label}\n")
                f.write(f"run_index={run_index}\n")
                f.write(f"total_cost={cost}\n")
                core_keys = [
                    'vehicles_used','total_distance_km','waiting_total','lateness_P_sum','horizon_excess_E',
                    'makespan_E','sum_route_time_E','avg_route_time_E','cost_time','w_time','cost_distance','cost_penalty_late','cost_penalty_horizon','vehicle_cost'
                ]
                waiting_total_val = metrics.get('waiting_total', metrics.get('waiting_E',0.0))
                    # Wpisz kluczowe metryki (w tym nowe czasowe sum/avg route time)
                for k in core_keys:
                    if k == 'waiting_total':
                        f.write(f"waiting_total={waiting_total_val}\n")
                        continue
                    if k in metrics:
                        f.write(f"{k}={metrics[k]}\n")
                # Lista długości tras
                if 'route_distance_list' in metrics:
                    f.write("route_distances="+','.join(str(x) for x in metrics['route_distance_list'])+"\n")
                if 'route_waiting_E_list' in metrics:
                    f.write("route_waiting="+','.join(str(x) for x in metrics['route_waiting_E_list'])+"\n")
                # Pełne trasy (opcjonalnie w pracy można cytować fragmenty)
                f.write("routes=\n")
                for r in routes:
                    f.write(','.join(map(str, r)) + '\n')
            return path
        if not args.no_summary:
            p1 = write_summary('Savings', cs, ms, idx_s, sol_s)
            p2 = write_summary('Insertion', ci, mi, idx_i, sol_i)
            print(f"Zapisano podsumowania: {p1}, {p2}")
        else:
            print("(Pomijam pliki summary – --no-summary)")

if __name__ == '__main__':
    main()
