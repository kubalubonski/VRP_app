import csv
import sys
import time
import requests  # wymagane dla zapytań TomTom
from datetime import datetime, date
try:
    from zoneinfo import ZoneInfo
except ImportError:
    ZoneInfo = None

# Kody błędów
EXIT_SUCCESS = 0
EXIT_ERROR = 1  
EXIT_API_LIMIT = 2

INPUT_CSV = 'wwwroot/czasy_przejazdu.csv'        # Plik z czasami bazowymi (ORS)
GEOCODE_CSV = 'wwwroot/dane_wejsciowe_geocoded.csv'  # Potrzebne do współrzędnych dla TOM TOM
OUTPUT_CSV = 'wwwroot/czasy_scenariusze.csv'     # Plik wynikowy scenariuszy
LOG_FILE = 'Logs/log_python.txt'
PESSIMISTIC_MULTIPLIER = 1.3   # Fallback jeśli brak HERE lub brak danych godzinowych
OPTIMISTIC_MULTIPLIER = 0.85   # Optymistyczny (noc, brak ruchu)
TOMTOM_API_KEY = '05YMFFwR3seQqEUT3dZN2YqhaMPxotjN'  # Wklej tutaj swój klucz TomTom (placeholder jeśli pusty)
TOMTOM_API_URL_BASE = 'https://api.tomtom.com/routing/1/calculateRoute'
HOUR_START = 8
HOUR_END = 18
SLEEP_BETWEEN_HOURS = 0.15

def _log_tomtom(msg):
    log(f"[TOMTOM] {msg}")

def _missing_tomtom_key():
    return (not TOMTOM_API_KEY) or TOMTOM_API_KEY.startswith('WPISZ_TUTAJ') or len(TOMTOM_API_KEY.strip()) < 20

def tomtom_duration_for_hour(lat1, lon1, lat2, lon2, hour_local):
    """Zwraca czas przejazdu w minutach dla danej godziny wykorzystując TomTom Routing API z ruchem (traffic)."""
    if _missing_tomtom_key():
        return None
    try:
        today = date.today()
        if ZoneInfo is not None:
            tz = ZoneInfo('Europe/Warsaw')
            dt_local = datetime(today.year, today.month, today.day, hour_local, 0, 0, tzinfo=tz)
            dt_utc = dt_local.astimezone(ZoneInfo('UTC'))
            depart_iso = dt_utc.isoformat().replace('+00:00', 'Z')
        else:
            dt_local = datetime(today.year, today.month, today.day, hour_local, 0, 0)
            depart_iso = dt_local.isoformat() + 'Z'
        # Endpoint: /routing/1/calculateRoute/{start}:{end}/json
        # Parametry: traffic=true&departAt=...&key=...
        coord_path = f"{lat1},{lon1}:{lat2},{lon2}"
        url = f"{TOMTOM_API_URL_BASE}/{coord_path}/json"
        params = {
            'traffic': 'true',
            'departAt': depart_iso,
            'key': TOMTOM_API_KEY
        }
        r = requests.get(url, params=params, timeout=15)
        if r.status_code == 429:
            _log_tomtom('Limit 429 – przerywam dla tej pary.')
            return None
        if r.status_code != 200:
            _log_tomtom(f"Status {r.status_code} pomijam h={hour_local}")
            return None
        data = r.json()
        routes = data.get('routes') or []
        if not routes:
            _log_tomtom(f"Brak routes h={hour_local}")
            return None
        summary = routes[0].get('summary', {})
        travel_sec = summary.get('travelTimeInSeconds')
        if travel_sec is None:
            _log_tomtom(f"Brak travelTimeInSeconds h={hour_local}")
            return None
        return travel_sec / 60.0
    except Exception as e:
        _log_tomtom(f"Wyjątek h={hour_local}: {e}")
        return None

def compute_pessimistic(lat1, lon1, lat2, lon2, base):
    """Zwraca pesymistyczny czas: max z godzin (TomTom) lub fallback * multiplier."""
    if _missing_tomtom_key():
        return base * PESSIMISTIC_MULTIPLIER
    max_dur = None
    for h in range(HOUR_START, HOUR_END + 1):
        d_h = tomtom_duration_for_hour(lat1, lon1, lat2, lon2, h)
        if d_h is not None:
            max_dur = d_h if max_dur is None else max(max_dur, d_h)
        time.sleep(SLEEP_BETWEEN_HOURS)
    if max_dur is None:
        return base * PESSIMISTIC_MULTIPLIER
    return max_dur

def log(msg):
    print(msg)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

log(f"[PYTHON][SCENARIOS][START] Generowanie scenariuszy czasowych: {INPUT_CSV} -> {OUTPUT_CSV}")

log("[INFO] Wczytuję punkty geocoded...")
points = []
try:
    with open(GEOCODE_CSV, newline='', encoding='utf-8') as gfile:
        greader = csv.DictReader(gfile)
        for row in greader:
            if row.get('Lat') and row.get('Lon'):
                points.append({'Lat': row['Lat'], 'Lon': row['Lon']})
    log(f"[INFO] Załadowano {len(points)} punktów do mapowania współrzędnych.")
except Exception as e:
    log(f"[ERROR] Nie udało się wczytać geocoded: {e}")

log("[INFO] Wczytuję czasy bazowe i generuję scenariusze...")
real_pess_computed = 0
fallback_used = 0
error_rows = 0
cache_pess = {}
with open(INPUT_CSV, newline='', encoding='utf-8') as infile, open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as outfile:
    reader = csv.DictReader(infile)
    fieldnames = ['StartIdx','EndIdx','StartTyp','EndTyp','StartUlica','StartMiasto','EndUlica','EndMiasto','DeliveryTimeWindow','Distance_km','Duration_time_expected','Duration_time_pessimistic','Duration_time_optimistic']
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in reader:
        try:
            base_raw = row.get('Duration_time') or row.get('Duration_time_expected')
            duration_min = float(base_raw)
            i = int(row.get('StartIdx','-1'))
            j = int(row.get('EndIdx','-1'))
            pess_val = None
            key = (i,j)
            if key in cache_pess:
                pess_val = cache_pess[key]
            else:
                lat1 = points[i]['Lat'] if 0 <= i < len(points) else None
                lon1 = points[i]['Lon'] if 0 <= i < len(points) else None
                lat2 = points[j]['Lat'] if 0 <= j < len(points) else None
                lon2 = points[j]['Lon'] if 0 <= j < len(points) else None
                if lat1 and lon1 and lat2 and lon2:
                    pess_val = compute_pessimistic(lat1, lon1, lat2, lon2, duration_min)
                else:
                    pess_val = duration_min * PESSIMISTIC_MULTIPLIER
                cache_pess[key] = pess_val
            if (not _missing_tomtom_key()) and pess_val != duration_min * PESSIMISTIC_MULTIPLIER:
                real_pess_computed += 1
                src = 'tomtom'
            else:
                fallback_used += 1
                src = 'fallback'
            optim_val = duration_min * OPTIMISTIC_MULTIPLIER
            writer.writerow({
                'StartIdx': row.get('StartIdx',''),
                'EndIdx': row.get('EndIdx',''),
                'StartTyp': row.get('StartTyp',''),
                'EndTyp': row.get('EndTyp',''),
                'StartUlica': row.get('StartUlica',''),
                'StartMiasto': row.get('StartMiasto',''),
                'EndUlica': row.get('EndUlica',''),
                'EndMiasto': row.get('EndMiasto',''),
                'DeliveryTimeWindow': row.get('DeliveryTimeWindow',''),
                'Distance_km': row.get('Distance_km',''),
                'Duration_time_expected': round(duration_min, 2),
                'Duration_time_pessimistic': round(pess_val, 2),
                'Duration_time_optimistic': round(optim_val, 2)
            })
            log(f"[OK] {i}->{j} base={duration_min:.2f} pess={pess_val:.2f} opt={optim_val:.2f} [SRC={src}]")
        except Exception as e:
            error_rows += 1
            writer.writerow({
                'StartIdx': row.get('StartIdx',''),
                'EndIdx': row.get('EndIdx',''),
                'StartTyp': row.get('StartTyp',''),
                'EndTyp': row.get('EndTyp',''),
                'StartUlica': row.get('StartUlica',''),
                'StartMiasto': row.get('StartMiasto',''),
                'EndUlica': row.get('EndUlica',''),
                'EndMiasto': row.get('EndMiasto',''),
                'DeliveryTimeWindow': row.get('DeliveryTimeWindow',''),
                'Distance_km': row.get('Distance_km',''),
                'Duration_time_expected': '',
                'Duration_time_pessimistic': '',
                'Duration_time_optimistic': ''
            })
            log(f"[ERROR] Błąd scenariusza: {e}")
    if _missing_tomtom_key():
        log('[INFO] Brak prawdziwego TOMTOM_API_KEY – wszystkie pesymistyczne czasy to fallback multiplier.')
    log(f"[END] Scenariusze (TomTom): real pess={real_pess_computed} fallback={fallback_used} errors={error_rows}. Zapisano do {OUTPUT_CSV}")
sys.exit(EXIT_SUCCESS)
