"""Generator danych w formacie aplikacji (długi format czasy_scenariusze.csv).

Kolumny:
StartIdx,EndIdx,StartTyp,EndTyp,StartUlica,StartMiasto,EndUlica,EndMiasto,DeliveryTimeWindow,Distance_km,Duration_time_expected,Duration_time_pessimistic,Duration_time_optimistic

Założenia:
- Pełny graf skierowany (bez łuków i==j) między depotem (0) i klientami (1..n)
- DeliveryTimeWindow przypisane do węzła docelowego (EndIdx); puste jeśli EndIdx==0 (powrót do magazynu)
- Okna czasowe generowane jak wcześniej (param --windows) w minutach względem 08:00
- Odległości w km: bazowo euklides 2D + szum (±5%)
- Czas expected = distance_km / speed * 60; speed losowa 65–85 km/h + szum ±5%
- Pessimistic/Optimistic zgodnie z wariantem wariancji

Użycie:
 python generate_app_style_data.py --sizes small medium large --variance mixed --windows medium --output-dir test_data --prefix app

Wynikowe pliki: <output_dir>/<prefix>_small.csv itd.
"""
from __future__ import annotations
import argparse
import os
import random as rd
import csv
from math import sqrt
from datetime import datetime, timedelta
from typing import List, Tuple

SIZE_MAP = {
    'small': 10,
    'medium': 25,
    'large': 50,
}

STREETS = [
    'Floriańska','Święty Marcin','Długa','Kościuszki','Lipowa','Polna','Słoneczna',
    'Kwiatowa','Krótka','Sportowa','Szkolna','Leśna','Ogrodowa','Widokowa','Spacerowa'
]
CITIES = [
    'Warszawa','Kraków','Poznań','Gdańsk','Łódź','Wrocław','Katowice','Lublin','Szczecin','Bydgoszcz'
]


def pick_variance_factor(variance_mode: str):
    """Wybór mnożnika wariancji (pessimistic) wg finalnej specyfikacji.
    low: 1.08–1.15, high: 1.20–1.30, mixed: 30% high.
    """
    def low():
        return rd.uniform(1.08, 1.15)
    def high():
        return rd.uniform(1.20, 1.30)
    if variance_mode == 'low':
        return low
    if variance_mode == 'high':
        return high
    # mixed – 30% szansa na wyższy mnożnik
    def mixed():
        if rd.random() < 0.3:
            return high()
        return low()
    return mixed


def choose_window(width_mode: str) -> float:
    """Losowa szerokość okna (min) dla profilu: tight, medium, loose, very_loose."""
    if width_mode == 'tight':
        return rd.uniform(70, 90)
    if width_mode == 'medium':
        return rd.uniform(150, 180)
    if width_mode == 'loose':
        return rd.uniform(240, 300)
    if width_mode == 'very_loose':
        return rd.uniform(330, 380)
    # Domyślne bezpieczeństwo – medium
    return rd.uniform(150, 180)


def assign_windows(n_clients: int, mode: str) -> List[Tuple[int,int]]:
    windows = [(0,0)]
    for _ in range(n_clients):
        width = choose_window(mode)
        center = rd.uniform(60, 540)
        start = max(0, center - width/2)
        end = min(600, start + width)
        windows.append((int(start), int(end)))
    return windows


def minutes_to_range(start: int, end: int) -> str:
    base = datetime(2024,1,1,8,0,0)
    s = (base + timedelta(minutes=start)).strftime('%H:%M')
    e = (base + timedelta(minutes=end)).strftime('%H:%M')
    return f"{s}-{e}"


def generate_coordinates(n_nodes: int):
    """Finalna skala przestrzeni: kwadrat 0..120 km.
    Średni dystans ~ 0.52 * 120 ≈ 62 km → expected ok. 50–60 min przy prędkościach 55–75 km/h.
    """
    max_coord = 120
    coords = []
    for _ in range(n_nodes):
        coords.append((rd.uniform(0, max_coord), rd.uniform(0, max_coord)))
    return coords


def distance(a, b):
    return sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)


def generate_instance(size_label: str, n_clients: int, variance: str, windows_mode: str, out_dir: str, prefix: str):
    n_nodes = n_clients + 1
    variance_picker = pick_variance_factor(variance)
    windows = assign_windows(n_clients, windows_mode)
    coords = generate_coordinates(n_nodes)

    # Przydział ulic/miast dla węzłów (0 = depot)
    node_streets = ['Puławska']
    node_cities = ['Warszawa']
    for i in range(1, n_nodes):
        node_streets.append(STREETS[(i-1) % len(STREETS)])
        node_cities.append(CITIES[(i-1) % len(CITIES)])

    rows = []
    for i in range(n_nodes):
        for j in range(n_nodes):
            if i == j:
                continue
            dist = distance(coords[i], coords[j])
            # dodajemy ±5% szumu odległości i zaokrąglamy do 2 miejsc
            dist *= rd.uniform(0.95, 1.05)
            distance_km = round(dist, 2)
            # prędkość km/h
            # Prędkość wg specyfikacji: 55–75 km/h (różnicowanie losowe)
            speed = rd.uniform(55, 75)
            exp_minutes = (distance_km / speed) * 60.0
            exp_minutes *= rd.uniform(0.95, 1.05)
            exp_val = round(exp_minutes, 2)
            pess_mult = variance_picker()
            pess_val = round(exp_val * pess_mult, 2)
            # Optymistyczny zakres: 0.88–0.95
            opt_val = round(exp_val * rd.uniform(0.88, 0.95), 2)

            # typy
            start_typ = 'Magazyn' if i == 0 else 'PunktDostawy'
            end_typ = 'Magazyn' if j == 0 else 'PunktDostawy'
            if j == 0:
                window = ''
            else:
                wstart, wend = windows[j]
                window = minutes_to_range(wstart, wend)

            rows.append({
                'StartIdx': i,
                'EndIdx': j,
                'StartTyp': start_typ,
                'EndTyp': end_typ,
                'StartUlica': node_streets[i],
                'StartMiasto': node_cities[i],
                'EndUlica': node_streets[j],
                'EndMiasto': node_cities[j],
                'DeliveryTimeWindow': window,
                'Distance_km': distance_km,
                'Duration_time_expected': exp_val,
                'Duration_time_pessimistic': pess_val,
                'Duration_time_optimistic': opt_val,
            })

    return rows


def enforce_max_duration(rows, max_duration: float):
    """Jeśli podano limit, skaluje wszystkie czasy (E/P/O) globalnie tak, aby
    maksymalny expected <= max_duration. Skalowanie zachowuje proporcje.
    """
    if max_duration is None:
        return rows
    current_max = max(r['Duration_time_expected'] for r in rows)
    if current_max <= max_duration:
        return rows
    factor = max_duration / current_max
    for r in rows:
        r['Duration_time_expected'] = min(max_duration, round(r['Duration_time_expected'] * factor, 2))
        r['Duration_time_pessimistic'] = round(r['Duration_time_pessimistic'] * factor, 2)
        r['Duration_time_optimistic'] = round(r['Duration_time_optimistic'] * factor, 2)
    return rows

# Stały limit maksymalnego expected travel (min). Jeśli użytkownik poda --max-duration niższy – użyj jego.
HARDCODED_MAX_EXPECTED = 160.0


def write_rows(rows, out_dir: str, prefix: str, size_label: str):
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, f"{prefix}_{size_label}.csv")
    with open(out_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'StartIdx','EndIdx','StartTyp','EndTyp','StartUlica','StartMiasto','EndUlica','EndMiasto',
            'DeliveryTimeWindow','Distance_km','Duration_time_expected','Duration_time_pessimistic','Duration_time_optimistic'
        ]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    return out_file


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sizes', nargs='*', default=['small','medium','large'])
    ap.add_argument('--variance', choices=['low','high','mixed'], default='mixed')
    ap.add_argument('--windows', choices=['tight','medium','loose','very_loose'], default='medium')
    ap.add_argument('--all-basic-windows', action='store_true', help='Wygeneruj 4 warianty okien (tight, medium, loose, very_loose) dla każdej wielkości.')
    ap.add_argument('--output-dir', default='test_data')
    ap.add_argument('--prefix', default='app')
    ap.add_argument('--seed', type=int, default=None)
    ap.add_argument('--max-duration', type=float, default=None, help='Globalny limit (minuty) na najdłuższy expected travel time; skaluje wszystkie czasy jeśli potrzeba')
    args = ap.parse_args()

    if args.seed is not None:
        rd.seed(args.seed)

    window_profiles = [args.windows]
    if args.all_basic_windows:
        window_profiles = ['tight','medium','loose','very_loose']

    for size_label in args.sizes:
        if size_label in SIZE_MAP:
            n_clients = SIZE_MAP[size_label]
        else:
            try:
                n_clients = int(size_label)
                if n_clients <= 0:
                    print(f"[WARN] Pomijam nielogiczną wartość: {size_label}")
                    continue
            except ValueError:
                print(f"[WARN] Pomijam nieznany rozmiar: {size_label}")
                continue
        for win_mode in window_profiles:
            tag = f"{size_label}_{win_mode}" if args.all_basic_windows else size_label
            print(f"Generuję: size={size_label} ({n_clients} klientów) windows={win_mode}")
            rows = generate_instance(size_label, n_clients, args.variance, win_mode, args.output_dir, args.prefix)
            # Jeśli użytkownik nie podał max-duration, stosujemy twardy limit HARDCODED_MAX_EXPECTED
            effective_limit = args.max_duration if args.max_duration is not None else HARDCODED_MAX_EXPECTED
            rows = enforce_max_duration(rows, effective_limit)
            path = write_rows(rows, args.output_dir, args.prefix, tag)
            max_exp = max(r['Duration_time_expected'] for r in rows)
            print(f"  Zapisano: {path} (max expected = {max_exp} min)")

    print('Gotowe (format aplikacji).')

if __name__ == '__main__':
    main()
