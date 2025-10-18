"""Batch runner for all synthetic app_* datasets.

Usage examples:
  python batch_run_all.py --csv wyniki_compact.csv --repeat 20 --best-only
  python batch_run_all.py --csv wyniki_new.csv --repeat 10 --best-only --sizes 20 80 200 --window-variants tight loose
  python batch_run_all.py --csv wyniki_servicetime.csv --service-time 5 --clean-csv

Key options:
  --csv <path> (required) output CSV to append
  --repeat N (default=20) multi-run count for Insertion (Savings is deterministic)
  --best-only store only best-cost run per algorithm (strongly recommended when repeat>1)
  --clean-csv remove CSV before running (start fresh)
  --sizes filter sizes e.g. 20 40 80 120 200 (default: auto-detect all present)
  --window-variants filter window variants e.g. tight medium loose very_loose (default: all)
  --service-time minutes of service per visit (default 0)
  Cost overrides: --cost-per-km --vehicle-fixed-cost --penalty-late --penalty-horizon

Randomness description (short for thesis):
  Greedy Insertion introduces stochasticity by shuffling the customer order before successive greedy insertions.
  Each run with a different permutation can yield a different constructed solution. We perform R independent
  constructions (repeat=R) and keep only the best (lowest total cost) when --best-only is specified. Clarke–Wright
  Savings is deterministic here and serves as a stable baseline. This constitutes a simple multi-start constructive
  scheme improving robustness against unlucky insertion ordering.
"""
import argparse, os, sys, subprocess, shlex
from pathlib import Path

ROOT = Path(__file__).parent
TEST_DATA = ROOT / "test_data"

WINDOW_DEFAULT = ["tight","medium","loose","very_loose"]


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--csv', required=True, help='Ścieżka do pliku wynikowego CSV.')
    p.add_argument('--repeat', type=int, default=20, help='Liczba powtórzeń (multi-run) dla insertion.')
    p.add_argument('--best-only', action='store_true', help='Zapisz jedynie najlepszy run (Insertion).')
    p.add_argument('--clean-csv', action='store_true', help='Usuń istniejący plik CSV przed startem.')
    p.add_argument('--sizes', nargs='*', type=int, help='Filtr rozmiarów (np. 20 40 80). Domyślnie wszystkie wykryte.')
    p.add_argument('--window-variants', nargs='*', help='Filtr wariantów okien (tight medium loose very_loose).')
    p.add_argument('--service-time', type=float, default=0.0, help='Minuty obsługi per klient.')
    # Parametry kosztu
    p.add_argument('--cost-per-km', type=float, help='Nadpisz koszt za km.')
    p.add_argument('--vehicle-fixed-cost', type=float, help='Nadpisz stały koszt pojazdu.')
    p.add_argument('--penalty-late', type=float, help='Nadpisz karę za spóźnienie (min).')
    p.add_argument('--penalty-horizon', type=float, help='Nadpisz karę za przekroczenie horyzontu (min).')
    return p.parse_args()


def detect_datasets(sizes_filter, variants_filter):
    files = []
    for f in TEST_DATA.glob('app_*.csv'):
        name = f.stem  # app_XX_variant
        parts = name.split('_')
        if len(parts) < 3:
            continue
        try:
            size = int(parts[1])
        except ValueError:
            continue
        variant = '_'.join(parts[2:])
        if sizes_filter and size not in sizes_filter:
            continue
        if variants_filter and variant not in variants_filter:
            continue
        files.append((size, variant, f))
    # Sort by size then variant
    files.sort(key=lambda x: (x[0], WINDOW_DEFAULT.index(x[1]) if x[1] in WINDOW_DEFAULT else x[1]))
    return files


def build_base_cmd(args):
    base = [sys.executable, str(ROOT / 'run_heuristics_demo.py')]
    base += ['--repeat', str(args.repeat)]
    if args.best_only:
        base.append('--best-only')
    if args.service_time:
        base += ['--service-time', str(args.service_time)]
    if args.cost_per_km is not None:
        base += ['--cost-per-km', str(args.cost_per_km)]
    if args.vehicle_fixed_cost is not None:
        base += ['--vehicle-fixed-cost', str(args.vehicle_fixed_cost)]
    if args.penalty_late is not None:
        base += ['--penalty-late', str(args.penalty_late)]
    if args.penalty_horizon is not None:
        base += ['--penalty-horizon', str(args.penalty_horizon)]
    # append-csv will be added per call
    return base


def main():
    args = parse_args()
    if not TEST_DATA.exists():
        print(f"Brak folderu test_data: {TEST_DATA}")
        sys.exit(1)

    if args.clean_csv and os.path.exists(args.csv):
        os.remove(args.csv)
        print(f"[clean] Usunięto istniejący {args.csv}")

    variants_filter = args.window_variants or None
    sizes_filter = args.sizes or None

    datasets = detect_datasets(sizes_filter, variants_filter)
    if not datasets:
        print("Nie znaleziono datasetów (sprawdź filtry).")
        sys.exit(1)

    base_cmd = build_base_cmd(args)

    ok = 0
    failed = 0
    for size, variant, path in datasets:
        tag = f"app_{size}_{variant}"
        cmd = base_cmd + ['--app-csv', str(path), '--append-csv', args.csv]
        print(f"\n== RUN {tag} ==")
        print(' '.join(shlex.quote(c) for c in cmd))
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                ok += 1
                # Show only last 8 lines for brevity
                tail = '\n'.join(result.stdout.strip().splitlines()[-8:])
                print(tail)
            else:
                failed += 1
                print(f"[ERROR] returncode={result.returncode}")
                print(result.stderr or result.stdout)
        except Exception as e:
            failed += 1
            print(f"[EXCEPTION] {e}")

    print(f"\n=== PODSUMOWANIE ===")
    print(f"SUKCES: {ok} / {len(datasets)}  | NIEPOWODZENIA: {failed}")
    if failed:
        print("Sprawdź powyższe komunikaty błędów.")
    else:
        print("Wszystkie zakończone sukcesem.")

if __name__ == '__main__':
    main()
