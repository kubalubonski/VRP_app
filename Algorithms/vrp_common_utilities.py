from typing import Dict, Tuple, Optional
from datetime import datetime
import pandas as pd
import numpy as np

__all__ = [
    "load_epo_times",
    "load_time_windows",
    "get_epo_matrix",
    "get_epo_matrices",
]

def load_epo_times(epo_path="../wwwroot/czasy_scenariusze.csv"):
    return pd.read_csv(epo_path, header=0)

def load_time_windows(data_path="../wwwroot/dane_wejsciowe_geocoded.csv"):
    data_df = pd.read_csv(data_path, header=0)
    time_windows: Dict[int, Optional[Tuple[datetime.time, datetime.time]]] = {}
    for idx, row in data_df.iterrows():
        location_id = idx
        if 'OknoCzasoweOd' in data_df.columns and 'OknoCzasoweDo' in data_df.columns:
            start_col = 'OknoCzasoweOd'; end_col = 'OknoCzasoweDo'
        elif 'time_window_start' in data_df.columns and 'time_window_end' in data_df.columns:
            start_col = 'time_window_start'; end_col = 'time_window_end'
        else:
            start_col = end_col = None
        if start_col and end_col and pd.notna(row[start_col]) and pd.notna(row[end_col]):
            start_time = datetime.strptime(str(row[start_col]), '%H:%M').time()
            end_time = datetime.strptime(str(row[end_col]), '%H:%M').time()
            time_windows[location_id] = (start_time, end_time)
        else:
            time_windows[location_id] = None
    return time_windows, data_df

def get_epo_matrix(times_df, scenario='expected'):
    cols = {
        'expected': 'Duration_time_expected',
        'pessimistic': 'Duration_time_pessimistic',
        'optimistic': 'Duration_time_optimistic'
    }
    if scenario not in cols:
        raise ValueError("Bad scenario")
    start_locs = set(times_df['StartIdx'].unique())
    end_locs = set(times_df['EndIdx'].unique())
    all_locs = sorted(start_locs.union(end_locs))
    n = len(all_locs)
    m = np.zeros((n, n))
    col = cols[scenario]
    for _, r in times_df.iterrows():
        i = int(r['StartIdx']); j = int(r['EndIdx'])
        if i < n and j < n:
            m[i, j] = float(r[col])
    return m

def get_epo_matrices(times_df):
    return {
        'expected': get_epo_matrix(times_df, 'expected'),
        'pessimistic': get_epo_matrix(times_df, 'pessimistic'),
        'optimistic': get_epo_matrix(times_df, 'optimistic')
    }
