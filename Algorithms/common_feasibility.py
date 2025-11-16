"""Wspólne funkcje sprawdzania wykonalności tras (dual E/P) – wersja odchudzona.

Semantyka:
 - Propagujemy tylko expected.
 - arrival_P = timeline_E + t_P (punktowa kontrola końca okna).
 - Naruszenie okna jeśli arrival_E > end lub arrival_P > end.
 - timeline_E = max(arrival_E, window_start) + service_time (dla klienta != depot).
 - Kontrola horyzontu: timeline_E <= day_horizon.

Udostępniamy tylko:
 - route_feasible_ep_classified (pełna klasyfikacja E/P/both dla jednej trasy).
 - route_feasible_ep (bool wrapper).
Nic więcej – brak nieużywanych wariantów solution_*.
"""
from __future__ import annotations
from datetime import datetime
from typing import List, Optional, Tuple, Dict
import numpy as np


def route_feasible_ep_classified(
    route: List[int],
    time_E: np.ndarray,
    time_P: np.ndarray,
    time_windows: Optional[Dict[int, Optional[Tuple[datetime.time, datetime.time]]]],
    day_horizon: int,
    service_time: float = 0.0,
) -> Tuple[bool, bool, bool, bool]:
    """Zwraca krotkę:
    (ok, violation_E, violation_P, violation_both)
    violation_both == True gdy przynajmniej jeden klient narusza okno jednocześnie dla E i P.
    """
    if not route or len(route) < 2:
        return True, False, False, False
    base_dt = datetime.strptime("08:00", "%H:%M")
    timeline_E = 0.0
    vio_E = False
    vio_P = False
    vio_both = False
    for i in range(len(route) - 1):
        a = route[i]; b = route[i+1]
        arrival_E = timeline_E + time_E[a, b]
        arrival_P = timeline_E + time_P[a, b]
        if time_windows and b in time_windows and time_windows[b]:
            ws, we = time_windows[b]
            ws_min = (datetime.combine(base_dt.date(), ws) - base_dt).seconds / 60
            we_min = (datetime.combine(base_dt.date(), we) - base_dt).seconds / 60
            if arrival_E > we_min:
                vio_E = True
            if arrival_P > we_min:
                vio_P = True
            if arrival_E > we_min and arrival_P > we_min:
                vio_both = True
            if arrival_E > we_min or arrival_P > we_min:
                # mimo naruszenia kontynuujemy dla pełnej klasyfikacji (nie early-exit)
                pass
            start_E = max(arrival_E, ws_min)
        else:
            start_E = arrival_E
        if b != 0 and service_time > 0:
            start_E += service_time
        timeline_E = start_E
        if timeline_E > day_horizon:
            # przekroczenie horyzontu interpretujemy jako naruszenie expected
            vio_E = True
            break
    ok = not (vio_E or vio_P)
    return ok, vio_E, vio_P, vio_both


def route_feasible_ep(
    route: List[int],
    time_E: np.ndarray,
    time_P: np.ndarray,
    time_windows: Optional[Dict[int, Optional[Tuple[datetime.time, datetime.time]]]],
    day_horizon: int,
    service_time: float = 0.0,
) -> bool:
    ok, _, _, _ = route_feasible_ep_classified(route, time_E, time_P, time_windows, day_horizon, service_time)
    return ok



